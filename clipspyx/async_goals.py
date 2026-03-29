"""Async goal handler framework for CLIPS 7.0x backward chaining.

When rules generate goals via backward chaining, the async run loop dispatches
them to registered Python async handlers. Handlers fulfill goals by asserting
facts. Timers are the first built-in handler type.

"""

import asyncio
import inspect
import time as _time
import warnings
import weakref
from dataclasses import dataclass, field

from clipspyx.common import CLIPS_MAJOR
from clipspyx.values import Symbol
from clipspyx.dsl.timer import AFTER, AT, EVERY  # re-export


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class GoalHandlerError(Exception):
    """Raised when an async goal handler fails."""


# ---------------------------------------------------------------------------
# Per-environment state
# ---------------------------------------------------------------------------

@dataclass
class GoalHandlerState:
    handlers: dict = field(default_factory=dict)        # template_name -> async callable
    pending: dict = field(default_factory=dict)          # goal_index -> asyncio.Task
    halted: bool = False                                 # set by halt_async()


# ---------------------------------------------------------------------------
# Timer-event deftemplate
# ---------------------------------------------------------------------------

TIMER_EVENT_DEFTEMPLATE = """\
(deftemplate timer-event
  (slot kind (type SYMBOL))
  (slot name (type SYMBOL))
  (slot seconds (type FLOAT) (default 0.0))
  (slot time (type FLOAT) (default 0.0))
  (slot count (type INTEGER) (default 0))
  (slot fired_at (type FLOAT) (default 0.0)))"""


# ---------------------------------------------------------------------------
# Built-in timer handler
# ---------------------------------------------------------------------------

_EXHAUSTED = object()
"""Sentinel returned by _gen_step when an async generator is exhausted."""


async def _gen_step(agen):
    """Advance an async generator by one step.

    The ``sleep(0)`` after ``__anext__`` yields to the event loop before
    the task completes, ensuring that I/O callbacks for other handlers
    (HTTP responses, etc.) are processed even when the generator has
    buffered data and ``__anext__`` returns without suspending.
    """
    try:
        result = await agen.__anext__()
        await asyncio.sleep(0)
        return result
    except StopAsyncIteration:
        return _EXHAUSTED


def _timer_handler(goal, env):
    """Dispatch to one-shot or periodic timer handler.

    Returns a coroutine for ``at``/``after`` timers, or an async generator
    for ``every`` timers.
    """
    kind = str(goal['kind'])
    if kind == 'every':
        return _timer_every(goal, env)
    return _timer_oneshot(goal, env)


async def _timer_oneshot(goal, env):
    """Handle at/after timer-event goals (one-shot)."""
    kind = str(goal['kind'])
    name = str(goal['name'])

    seconds = 0.0
    target_time = 0.0

    if kind == 'at':
        target_time = float(goal['time'])
        sleep_for = max(0, target_time - _time.time())
    else:
        seconds = float(goal['seconds'])
        sleep_for = seconds

    await asyncio.sleep(sleep_for)

    tpl = env.find_template('timer-event')
    tpl.assert_fact(
        kind=Symbol(kind), name=Symbol(name),
        seconds=seconds, time=target_time,
        count=0, fired_at=_time.time())


async def _timer_every(goal, env):
    """Handle periodic timer-event goals (async generator).

    Each iteration sleeps, then retracts the previous fact (if any) and
    asserts a new one before yielding.  The fact persists until the next
    timer tick, ensuring ``env.run()`` sees it even when generator
    re-steps run between cycles (e.g. during an event-loop yield in
    ``_run_loop``).  On cancellation the ``finally`` block cleans up the
    last fact.
    """
    name = str(goal['name'])
    seconds = float(goal['seconds'])
    tpl = env.find_template('timer-event')

    count = 0
    fact = None
    try:
        while True:
            await asyncio.sleep(seconds)
            if fact is not None and fact.exists:
                fact.retract()
            fact = tpl.assert_fact(
                kind=Symbol('every'), name=Symbol(name),
                seconds=seconds, time=0.0,
                count=count, fired_at=_time.time())
            yield
            count += 1
    finally:
        if fact is not None and fact.exists:
            fact.retract()



# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def enable_goal_handlers(env):
    """Enable the async goal handler framework for the given environment.

    Registers the timer-event deftemplate and the built-in timer handler.
    Must be called before async_run() or register_goal_handler().

    Requires CLIPS 7.0x (goals are a 7.0x feature).
    """
    if CLIPS_MAJOR < 7:
        raise TypeError("Async goal handlers require CLIPS 7.0 or later")

    # Build the timer-event template
    env.build(TIMER_EVENT_DEFTEMPLATE)

    # Create and store state
    state = GoalHandlerState()
    state.handlers['timer-event'] = _timer_handler
    env._goal_handler_state = state


def disable_goal_handlers(env):
    """Disable the async goal handler framework and cancel pending tasks."""
    state = getattr(env, '_goal_handler_state', None)
    if state is None:
        return

    # Cancel all pending handler tasks
    for task in state.pending.values():
        task.cancel()
    state.pending.clear()

    env._goal_handler_state = None


def register_goal_handler(env, template, handler):
    """Register an async handler for goals matching a template.

    ``template`` can be a DSL Template class or a CLIPS template name string.

    The handler is an async callable with signature:
        async def handler(goal, env) -> None

    The handler receives the goal (a TemplateFact) and the Environment.
    It should assert facts to satisfy the goal.
    """
    state = env._goal_handler_state
    if state is None:
        raise RuntimeError("Call enable_goal_handlers(env) first")
    if isinstance(template, str):
        name = template
    else:
        name = template.__clipspyx_dsl__.name
    state.handlers[name] = handler




# ---------------------------------------------------------------------------
# AsyncRunner - resource context for async goal handling
# ---------------------------------------------------------------------------

class AsyncRunner:
    """Manages async goal handler lifecycle across multiple run() calls.

    Unlike the deprecated ``async_run()`` function, ``AsyncRunner`` owns the
    full goal handler lifecycle: it auto-enables on creation and disables on
    ``close()``.  Persistent handler tasks survive across ``run()`` calls
    and are only cancelled by ``close()``.

    Use :meth:`wake` to interrupt the handler wait and force the runner to
    cycle back to ``env.run()``, e.g. after injecting facts externally.

    Usage::

        async with AsyncRunner(env) as runner:
            runner.register_handler(MyTemplate, my_handler)
            while not done:
                # inject facts, then:
                runner.wake()
                result = await runner.run()
        # close() called automatically - all tasks cancelled, handlers disabled
    """

    def __init__(self, env):
        state = getattr(env, '_goal_handler_state', None)
        if state is None:
            enable_goal_handlers(env)
        self.env = env
        self._persistent_tasks = {}           # goal_index -> asyncio.Task
        self._generators = {}                 # task_id -> async generator
        self._closed = False
        self._skipped = set()                 # goal indices completed without satisfying
        self._orphaned_pending = set()        # detached tasks (goal retracted mid-flight)
        self._wake_event = asyncio.Event()
        self._in_env_run = False              # suppress notify during rule execution
        self._handler_tasks = set()           # tracked handler asyncio.Tasks

    def register_handler(self, template, handler):
        """Register an async handler for goals matching a template.

        Regular async handlers (coroutines) are tracked per-goal.
        Async generator handlers (functions with ``yield``) are tracked
        per-template and survive across ``run()`` calls -- ``yield``
        encodes persistence.
        """
        register_goal_handler(self.env, template, handler)

    def schedule(self, coro):
        """Schedule an external coroutine to run during ``run()``.

        Creates an ``asyncio.Task`` on the runner's event loop and adds
        it to the wait set so the run loop cycles when it completes.
        Safe to call from CLIPS rule actions (CFFI callbacks) -- avoids
        the ``asyncio.get_event_loop()`` ambiguity by using the loop
        that the runner is actually running on.

        The task is fire-and-forget: it is not tied to any goal and does
        not block completion.  Errors are logged as warnings.
        """
        task = asyncio.create_task(coro)
        self._orphaned_pending.add(task)
        self._handler_tasks.add(task)
        self._wake_event.set()
        return task

    def wake(self):
        """Signal the runner to cycle back to ``env.run()``.

        Safe to call from any coroutine while the runner is blocked in
        ``_wait_for_handlers``.  If called before the runner reaches the
        wait point, the signal is latched and consumed on the next wait.
        """
        self._wake_event.set()

    def _notify(self):
        """Auto-wake from working memory changes (fact assert/retract/modify).

        Suppressed during ``env.run()`` (rule-execution changes are already
        being processed) and from within handler tasks (handler completion
        already triggers cycling).
        """
        if self._in_env_run:
            return
        current = asyncio.current_task()
        if current is not None and current in self._handler_tasks:
            return
        self._wake_event.set()

    # -- run() and its cycle steps --

    async def run(self, limit=None, max_cycles=None):
        """Run the CLIPS engine with async goal handler processing.

        Raises ``RuntimeError`` if called after :meth:`close`.

        Returns a string indicating why the loop stopped:

        - ``"completed"``: no goals remain, no pending handlers
        - ``"max_cycles"``: reached the *max_cycles* limit
        - ``"halted"``: ``halt_async()`` was called (internal cancellation)
        """
        if self._closed:
            raise RuntimeError("AsyncRunner is closed")
        state = self.env._goal_handler_state
        if state is None:
            raise RuntimeError("Call enable_goal_handlers(env) first")

        self.env._runner_ref = weakref.ref(self)
        try:
            return await self._run_loop(state, limit, max_cycles)
        finally:
            self.env._runner_ref = None

    async def _run_loop(self, state, limit, max_cycles):
        """Core inference loop."""
        state.halted = False
        self._skipped.clear()
        cycle = 0
        while max_cycles is None or cycle < max_cycles:
            cycle += 1

            self._prune_done_persistent()
            self._prune_done_orphaned()

            if state.halted:
                return "halted"

            self._in_env_run = True
            try:
                self.env.run(limit)
            finally:
                self._in_env_run = False

            if state.halted:
                return "halted"

            self._dispatch_goals(state)
            self._detach_retracted_goals(state)

            if not state.pending and not self._has_active_persistent():
                return "completed"
            if max_cycles is not None and cycle >= max_cycles:
                return "max_cycles"

            reason = await self._wait_for_handlers(state)
            if reason is not None:
                return reason

            # Yield to the event loop between cycles so that external
            # async tasks (e.g. schedule_async coroutines created by
            # rule actions via asyncio.create_task) get a chance to
            # execute.  Safe for timer facts because _timer_every now
            # retracts the previous fact before asserting the next one
            # (not on re-step via finally).
            await asyncio.sleep(0)

        return "max_cycles"

    def _prune_done_persistent(self):
        """Remove completed persistent tasks from tracking."""
        for idx in [i for i, t in self._persistent_tasks.items()
                    if t.done()]:
            del self._persistent_tasks[idx]

    def _prune_done_orphaned(self):
        """Remove completed orphaned tasks, logging any errors."""
        for task in list(self._orphaned_pending):
            if task.done():
                self._orphaned_pending.discard(task)
                self._handler_tasks.discard(task)
                if not task.cancelled() and task.exception():
                    warnings.warn(
                        f"Orphaned handler failed: {task.exception()}",
                        stacklevel=1,
                    )

    def _has_active_persistent(self):
        """True if any persistent task is still running."""
        return any(not t.done() for t in self._persistent_tasks.values())

    def _create_handler_task(self, handler, goal):
        """Create a task from a handler invocation.

        Returns ``(task, is_generator)``.  If the handler returns a
        coroutine, wraps it in a task directly.  If it returns an async
        generator, creates a task for the first ``anext()`` step.
        """
        invocation = handler(goal, self.env)
        if inspect.isasyncgen(invocation):
            task = asyncio.create_task(_gen_step(invocation))
            self._generators[id(task)] = invocation
            self._handler_tasks.add(task)
            return task, True
        task = asyncio.create_task(invocation)
        self._handler_tasks.add(task)
        return task, False

    def _dispatch_goals(self, state):
        """Scan CLIPS goals and create handler tasks for new ones.

        Both generators and coroutines are tracked per-goal: generators in
        _persistent_tasks, coroutines in state.pending.
        """
        for goal in self.env.goals():
            tname = goal.template.name
            handler = state.handlers.get(tname)
            if handler is None:
                continue
            idx = goal.index
            # Already tracked?
            if idx in self._persistent_tasks \
                    and not self._persistent_tasks[idx].done():
                continue
            if idx in self._skipped or idx in state.pending:
                continue
            task, is_gen = self._create_handler_task(handler, goal)
            if is_gen:
                self._persistent_tasks[idx] = task
            else:
                state.pending[idx] = task

    def _detach_retracted_goals(self, state):
        """Detach non-persistent tasks whose goals no longer exist.

        Tasks are moved to ``_orphaned_pending`` instead of cancelled,
        allowing in-flight work (HTTP requests, etc.) to complete.
        Orphaned tasks do not block completion.

        Persistent tasks (_persistent_tasks) are intentionally NOT touched
        here.  In CLIPS backward chaining, a goal is retracted when satisfied
        (fact asserted), but the generator handler must keep running for
        subsequent iterations (e.g. every-timer ticks).
        """
        for idx in list(state.pending):
            try:
                self.env.find_goal(idx)
            except LookupError:
                task = state.pending.pop(idx)
                self._orphaned_pending.add(task)

        for idx in list(self._skipped):
            try:
                self.env.find_goal(idx)
            except LookupError:
                self._skipped.discard(idx)

    async def _wait_for_handlers(self, state):
        """Wait for at least one handler to complete, or a wake signal.

        Returns ``"completed"`` if no tasks remain (and no wake pending),
        or ``None`` to continue cycling.
        """
        # Yield to the event loop so external async tasks (e.g.
        # schedule_async coroutines created by rule actions) get a
        # chance to execute.  Placed here (after env.run()) rather
        # than at the end of the cycle to preserve fact visibility:
        # generator re-steps that retract scoped facts must not run
        # before the next env.run() sees those facts.
        await asyncio.sleep(0)

        wait_set = set(state.pending.values()) | {
            t for t in self._persistent_tasks.values() if not t.done()
        } | {
            t for t in self._orphaned_pending if not t.done()
        }

        # If nothing to wait on, check whether wake() was called.
        if not wait_set:
            if self._wake_event.is_set():
                self._wake_event.clear()
                return None          # continue cycling
            return "completed"

        # Create a task that completes when wake() is called.
        wake_task = asyncio.create_task(self._wake_event.wait())
        wait_set.add(wake_task)

        try:
            done, _ = await asyncio.wait(
                wait_set, return_when=asyncio.FIRST_COMPLETED)
        finally:
            wake_task.cancel()
            try:
                await wake_task
            except asyncio.CancelledError:
                pass

        # Consume the wake signal if it fired.
        woken = wake_task in done
        if woken:
            self._wake_event.clear()
            done.discard(wake_task)

        # Process any actual handler tasks that completed.
        if done:
            self._process_done(state, done)

        return None

    def _process_done(self, state, done):
        """Remove completed tasks from tracking and propagate errors.

        For generator-backed tasks, creates a replacement task for the
        next iteration instead of removing.
        """
        # Build reverse lookup: task id -> (owning dict, key)
        owners = {}
        for idx, t in state.pending.items():
            owners[id(t)] = (state.pending, idx)
        for idx, t in self._persistent_tasks.items():
            owners[id(t)] = (self._persistent_tasks, idx)

        for task in done:
            self._handler_tasks.discard(task)

            # Orphaned tasks: just clean up, don't propagate errors.
            if task in self._orphaned_pending:
                self._orphaned_pending.discard(task)
                if not task.cancelled() and task.exception():
                    warnings.warn(
                        f"Orphaned handler failed: {task.exception()}",
                        stacklevel=1,
                    )
                continue

            owner = owners.get(id(task))
            gen = self._generators.pop(id(task), None)

            if task.cancelled():
                if owner: del owner[0][owner[1]]
                if gen: asyncio.create_task(gen.aclose())
                continue

            if task.exception():
                if owner: del owner[0][owner[1]]
                if gen: asyncio.create_task(gen.aclose())
                raise GoalHandlerError(
                    f"Handler failed: {task.exception()}"
                ) from task.exception()

            if gen and task.result() is not _EXHAUSTED:
                new_task = asyncio.create_task(_gen_step(gen))
                self._generators[id(new_task)] = gen
                self._handler_tasks.add(new_task)
                if owner: owner[0][owner[1]] = new_task
            else:
                if owner:
                    if gen is None and owner[0] is state.pending:
                        idx = owner[1]
                        try:
                            self.env.find_goal(idx)
                            self._skipped.add(idx)
                        except LookupError:
                            pass
                    del owner[0][owner[1]]

    async def close(self):
        """Cancel all tasks (persistent and non-persistent) and disable
        goal handlers.
        """
        if self._closed:
            return
        self.env._runner_ref = None
        for task in self._persistent_tasks.values():
            task.cancel()
        self._persistent_tasks.clear()
        state = self.env._goal_handler_state
        if state is not None:
            for task in state.pending.values():
                task.cancel()
            state.pending.clear()
        for task in self._orphaned_pending:
            task.cancel()
        self._orphaned_pending.clear()
        # Generator cleanup happens via task cancellation above
        self._generators.clear()
        self._handler_tasks.clear()
        self._skipped.clear()
        self._wake_event.clear()
        disable_goal_handlers(self.env)
        self._closed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.close()
