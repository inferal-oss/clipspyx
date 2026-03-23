"""Async goal handler framework for CLIPS 7.0x backward chaining.

When rules generate goals via backward chaining, the async run loop dispatches
them to registered Python async handlers. Handlers fulfill goals by asserting
facts. Timers are the first built-in handler type.

"""

import asyncio
import time as _time
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
    periodic_facts: dict = field(default_factory=dict)   # timer name -> (fact, count)
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

async def _timer_handler(goal, env):
    """Handle timer-event goals by sleeping and asserting the matching fact."""
    kind = str(goal['kind'])
    name = str(goal['name'])
    state = env._goal_handler_state

    # Read only the slots relevant to this kind.
    # Unspecified goal slots return UniversallyQuantifiedValue.
    seconds = 0.0
    target_time = 0.0

    if kind == 'at':
        target_time = float(goal['time'])
        sleep_for = max(0, target_time - _time.time())
    else:
        seconds = float(goal['seconds'])
        sleep_for = seconds

    await asyncio.sleep(sleep_for)

    # Determine count (increment for periodic)
    count = 0
    if kind == 'every' and name in state.periodic_facts:
        count = state.periodic_facts[name][1] + 1

    # Assert the timer-event fact
    tpl = env.find_template('timer-event')
    fact = tpl.assert_fact(
        kind=Symbol(kind), name=Symbol(name),
        seconds=seconds, time=target_time,
        count=count, fired_at=_time.time())

    # Track periodic facts for auto-retract
    if kind == 'every':
        state.periodic_facts[name] = (fact, count)


# ---------------------------------------------------------------------------
# Auto-retract helper for periodic timers
# ---------------------------------------------------------------------------

def _retract_periodic_facts(env, state):
    """Retract timer-event facts from periodic timers so goals regenerate."""
    for name, (fact, _count) in list(state.periodic_facts.items()):
        if fact.exists:
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
    state.periodic_facts.clear()

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


async def _wait_event(event):
    """Helper: await an asyncio.Event (used as a task in asyncio.wait)."""
    await event.wait()


async def async_run(env, limit=None, max_cycles=None, stop_event=None):
    """Run the CLIPS engine with async goal handler processing.

    .. deprecated::
        Use :class:`AsyncRunner` instead for better lifecycle management
        and persistent handler support.
    """
    import warnings
    warnings.warn(
        "async_run() is deprecated, use AsyncRunner instead",
        DeprecationWarning, stacklevel=2)
    runner = AsyncRunner(env)
    return await runner.run(limit=limit, max_cycles=max_cycles,
                            stop_event=stop_event)


# ---------------------------------------------------------------------------
# AsyncRunner - resource context for async goal handling
# ---------------------------------------------------------------------------

class AsyncRunner:
    """Manages async goal handler lifecycle across multiple run() calls.

    Unlike the deprecated ``async_run()`` function, ``AsyncRunner`` owns the
    full goal handler lifecycle: it auto-enables on creation and disables on
    ``close()``.  Persistent handler tasks survive when ``stop_event`` fires
    and are only cancelled by ``close()``.

    Usage::

        async with AsyncRunner(env) as runner:
            runner.register_handler(MyTemplate, my_handler, persistent=True)
            while not done:
                work_ready.clear()
                result = await runner.run(stop_event=work_ready)
        # close() called automatically - all tasks cancelled, handlers disabled
    """

    def __init__(self, env):
        state = getattr(env, '_goal_handler_state', None)
        if state is None:
            enable_goal_handlers(env)
        self.env = env
        self._persistent_templates = set()   # template names marked persistent
        self._persistent_tasks = {}          # template_name -> asyncio.Task
        self._closed = False

    def register_handler(self, template, handler, persistent=False):
        """Register an async handler for goals matching a template.

        If ``persistent=True``, the handler task survives across ``run()``
        calls when ``stop_event`` fires.  Only ``close()`` cancels it.
        Persistent tasks are keyed per-template (one task per template type).
        """
        register_goal_handler(self.env, template, handler)
        if persistent:
            name = template if isinstance(template, str) \
                else template.__clipspyx_dsl__.name
            self._persistent_templates.add(name)

    async def run(self, limit=None, max_cycles=None, stop_event=None):
        """Run the CLIPS engine with async goal handler processing.

        Returns a string indicating why the loop stopped:

        - ``"completed"``: no goals remain, no pending handlers
        - ``"max_cycles"``: reached the *max_cycles* limit
        - ``"halted"``: ``halt_async()`` was called (internal cancellation)
        - ``"stopped"``: *stop_event* was set (external cancellation)
        """
        state = self.env._goal_handler_state
        if state is None:
            raise RuntimeError("Call enable_goal_handlers(env) first")

        state.halted = False
        cycle = 0
        while max_cycles is None or cycle < max_cycles:
            cycle += 1

            # Check cancellation signals
            if state.halted:
                return "halted"
            if stop_event is not None and stop_event.is_set():
                return "stopped"

            # Run CLIPS synchronously (process agenda).
            self.env.run(limit)

            # Check halt after run (rules may have called halt_async)
            if state.halted:
                return "halted"

            # Auto-retract periodic timer-event facts AFTER run() processes
            # them, so goals regenerate for the next cycle.
            _retract_periodic_facts(self.env, state)

            # Scan goals for new dispatches
            for goal in self.env.goals():
                tname = goal.template.name
                if tname in self._persistent_templates:
                    # One task per persistent template
                    if (tname in self._persistent_tasks
                            and not self._persistent_tasks[tname].done()):
                        continue
                    handler = state.handlers.get(tname)
                    if handler is not None:
                        self._persistent_tasks[tname] = \
                            asyncio.create_task(handler(goal, self.env))
                else:
                    # Per-goal task (same as legacy async_run)
                    idx = goal.index
                    if idx in state.pending:
                        continue
                    handler = state.handlers.get(tname)
                    if handler is not None:
                        state.pending[idx] = \
                            asyncio.create_task(handler(goal, self.env))

            # Cancel tasks for retracted goals (non-persistent only)
            for idx in list(state.pending):
                try:
                    self.env.find_goal(idx)
                except LookupError:
                    state.pending.pop(idx).cancel()

            # Check completion
            active_persistent = {
                n: t for n, t in self._persistent_tasks.items()
                if not t.done()
            }
            if not state.pending and not active_persistent:
                return "completed"

            # Build wait set from both non-persistent and persistent tasks
            wait_set = set(state.pending.values()) | set(
                t for t in self._persistent_tasks.values() if not t.done()
            )
            if not wait_set:
                return "completed"

            # Wait for at least one handler to complete, or stop_event
            if stop_event is not None:
                stop_task = asyncio.create_task(_wait_event(stop_event))
                wait_set.add(stop_task)
                done, _ = await asyncio.wait(
                    wait_set, return_when=asyncio.FIRST_COMPLETED)
                stop_task.cancel()
                if stop_event.is_set():
                    # Cancel ONLY non-persistent tasks
                    for t in state.pending.values():
                        t.cancel()
                    state.pending.clear()
                    return "stopped"
            else:
                done, _ = await asyncio.wait(
                    wait_set, return_when=asyncio.FIRST_COMPLETED)

            # Process completed tasks
            for task in done:
                # Remove from non-persistent pending
                for idx, t in list(state.pending.items()):
                    if t is task:
                        del state.pending[idx]
                        break
                # Remove from persistent tasks
                for name, t in list(self._persistent_tasks.items()):
                    if t is task:
                        del self._persistent_tasks[name]
                        break
                if not task.cancelled() and task.exception():
                    raise GoalHandlerError(
                        f"Handler failed: {task.exception()}"
                    ) from task.exception()

        return "max_cycles"

    async def close(self):
        """Cancel all tasks (persistent and non-persistent) and disable
        goal handlers.
        """
        if self._closed:
            return
        for task in self._persistent_tasks.values():
            task.cancel()
        self._persistent_tasks.clear()
        state = self.env._goal_handler_state
        if state is not None:
            for task in state.pending.values():
                task.cancel()
            state.pending.clear()
        disable_goal_handlers(self.env)
        self._closed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.close()
