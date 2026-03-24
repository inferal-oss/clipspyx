"""Hypothesis stateful tests for AsyncRunner state machine.

Exercises random sequences of operations (run, close, register_handler)
and verifies invariants hold after each step. Uses manual swarm testing:
each example randomly enables/disables a subset of operations, forcing
exploration of different feature combinations.

Requires CLIPS 7.0+ and hypothesis.
"""

import asyncio
import unittest

from hypothesis import settings, HealthCheck
from hypothesis.stateful import (
    RuleBasedStateMachine,
    initialize,
    invariant,
    rule,
    precondition,
)
from hypothesis import strategies as st

import clipspyx
from clipspyx import Environment, Symbol
from clipspyx.dsl import Template, Rule, TimerEvent
from clipspyx.async_goals import AsyncRunner, GoalHandlerError

CLIPS_70 = clipspyx.CLIPS_MAJOR >= 7


# ---------------------------------------------------------------------------
# DSL templates (Sm prefix avoids name collisions with test_async_goals.py)
# ---------------------------------------------------------------------------

class SmStreamA(Template):
    tag: Symbol

class SmStreamB(Template):
    tag: Symbol

class SmJob(Template):
    tag: Symbol

class SmStreamAResult(Template):
    tag: Symbol

class SmStreamBResult(Template):
    tag: Symbol

class SmJobResult(Template):
    tag: Symbol

class SmActive(Template):
    pass

class SmHaltTrigger(Template):
    pass


# Goal handler rules
def _make_stream_a_goal():
    class SmHandleStreamAGoal(Rule):
        goal(SmStreamA(tag=t))
    return SmHandleStreamAGoal

def _make_stream_b_goal():
    class SmHandleStreamBGoal(Rule):
        goal(SmStreamB(tag=t))
    return SmHandleStreamBGoal

def _make_job_goal():
    class SmHandleJobGoal(Rule):
        goal(SmJob(tag=t))
    return SmHandleJobGoal

# Consuming rules
def _make_stream_a_consumer():
    class SmOnStreamA(Rule):
        SmActive()
        s = SmStreamA(tag=t)
        retracts(s)
        asserts(SmStreamAResult(tag=t))
    return SmOnStreamA

def _make_stream_b_consumer():
    class SmOnStreamB(Rule):
        SmActive()
        s = SmStreamB(tag=t)
        retracts(s)
        asserts(SmStreamBResult(tag=t))
    return SmOnStreamB

def _make_job_consumer():
    class SmOnJob(Rule):
        SmActive()
        j = SmJob(tag=t)
        retracts(j)
        asserts(SmJobResult(tag=t))
    return SmOnJob

def _make_halt_rule():
    class SmHaltOnTrigger(Rule):
        h = SmHaltTrigger()
        def __action__(self):
            self.h.retract()
            self.__env__.halt_async()
    return SmHaltOnTrigger

def _make_timer_goal():
    class SmHandleTimerGoal(Rule):
        goal(TimerEvent(kind=k, name=n, seconds=s))
    return SmHandleTimerGoal


# ---------------------------------------------------------------------------
# Swarm features
# ---------------------------------------------------------------------------

SWARM_FEATURES = [
    "persistent_a",       # register persistent handler for SmStreamA
    "persistent_b",       # register persistent handler for SmStreamB
    "nonpersistent",      # register non-persistent handler for SmJob
    "halt",               # trigger halt_async via fact assertion
    "active_toggle",      # toggle the Active controlling fact
    "completing",         # persistent handlers complete quickly (vs loop forever)
    "wake",               # call runner.wake() at random times
]


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class AsyncRunnerStateMachine(RuleBasedStateMachine):
    """Property-based state machine test for AsyncRunner with swarm testing.

    Each example randomly selects a subset of features to enable, forcing
    exploration of feature combinations that uniform random misses.
    """

    def __init__(self):
        super().__init__()
        self._loop = asyncio.new_event_loop()

        # Model state
        self._is_closed = False
        self._persistent_templates = set()
        self._has_nonpersistent = False
        self._run_count = 0
        self._last_result = None
        self._active_fact_exists = False
        self._halt_pending = False
        self._swarm = set()

    def teardown(self):
        if not self._is_closed and hasattr(self, 'runner'):
            self._loop.run_until_complete(self.runner.close())
        self._loop.close()

    @initialize(
        swarm=st.frozensets(
            st.sampled_from(SWARM_FEATURES), min_size=1, max_size=6
        )
    )
    def init_runner(self, swarm):
        self._swarm = set(swarm)
        self.env = Environment()
        self.runner = AsyncRunner(self.env)

        self.env.define(SmStreamA)
        self.env.define(SmStreamB)
        self.env.define(SmJob)
        self.env.define(SmStreamAResult)
        self.env.define(SmStreamBResult)
        self.env.define(SmJobResult)
        self.env.define(SmActive)
        self.env.define(SmHaltTrigger)
        self.env.define(_make_stream_a_goal())
        self.env.define(_make_stream_b_goal())
        self.env.define(_make_job_goal())
        self.env.define(_make_stream_a_consumer())
        self.env.define(_make_stream_b_consumer())
        self.env.define(_make_job_consumer())
        self.env.define(_make_halt_rule())
        self.env.define(_make_timer_goal())
        self.env.reset()

        self._handler_calls = {}

    # -- Helpers --

    def _make_handler(self, template_cls, completing):
        tname = template_cls.__clipspyx_dsl__.name
        calls = self._handler_calls.setdefault(tname, [])

        if completing:
            async def handler(goal, env):
                calls.append(1)
                await asyncio.sleep(0.005)
                template_cls(__env__=env, tag=Symbol("data"))
                yield  # generator: persistent, completes after one yield
        else:
            async def handler(goal, env):
                calls.append(1)
                template_cls(__env__=env, tag=Symbol("data"))
                while True:
                    yield  # generator: persistent, runs forever
                    await asyncio.sleep(0.005)

        return handler

    # -- Rules --

    @precondition(lambda self: (
        not self._is_closed
        and "persistent_a" in self._swarm
        and SmStreamA.__clipspyx_dsl__.name not in self._persistent_templates
    ))
    @rule()
    def register_persistent_a(self):
        """Register persistent handler for SmStreamA."""
        completing = "completing" in self._swarm
        handler = self._make_handler(SmStreamA, completing)
        self.runner.register_handler(SmStreamA, handler)
        self._persistent_templates.add(SmStreamA.__clipspyx_dsl__.name)

    @precondition(lambda self: (
        not self._is_closed
        and "persistent_b" in self._swarm
        and SmStreamB.__clipspyx_dsl__.name not in self._persistent_templates
    ))
    @rule()
    def register_persistent_b(self):
        """Register persistent handler for SmStreamB."""
        completing = "completing" in self._swarm
        handler = self._make_handler(SmStreamB, completing)
        self.runner.register_handler(SmStreamB, handler)
        self._persistent_templates.add(SmStreamB.__clipspyx_dsl__.name)

    @precondition(lambda self: (
        not self._is_closed
        and "nonpersistent" in self._swarm
        and not self._has_nonpersistent
    ))
    @rule()
    def register_nonpersistent(self):
        """Register non-persistent handler for SmJob."""
        calls = self._handler_calls.setdefault("job", [])

        async def job_handler(goal, env):
            calls.append(1)
            await asyncio.sleep(0.005)
            SmJob(__env__=env, tag=Symbol("done"))

        self.runner.register_handler(SmJob, job_handler)
        self._has_nonpersistent = True

    @precondition(lambda self: (
        not self._is_closed
        and "active_toggle" in self._swarm
        and not self._active_fact_exists
    ))
    @rule()
    def assert_active(self):
        """Assert SmActive to enable goal generation."""
        SmActive(__env__=self.env)
        self._active_fact_exists = True

    @precondition(lambda self: (
        not self._is_closed
        and "active_toggle" in self._swarm
        and self._active_fact_exists
    ))
    @rule()
    def retract_active(self):
        """Retract SmActive to stop goal generation."""
        aname = SmActive.__clipspyx_dsl__.name
        for f in list(self.env.find_template(aname).facts()):
            f.retract()
        self._active_fact_exists = False

    @precondition(lambda self: (
        not self._is_closed
        and "halt" in self._swarm
        and not self._halt_pending
    ))
    @rule()
    def trigger_halt(self):
        """Assert SmHaltTrigger so the halt rule fires on next env.run()."""
        SmHaltTrigger(__env__=self.env)
        self._halt_pending = True

    @precondition(lambda self: (
        not self._is_closed
        and "wake" in self._swarm
    ))
    @rule()
    def wake_runner(self):
        """Call runner.wake() to interrupt blocked waits."""
        self.runner.wake()

    @precondition(lambda self: not self._is_closed)
    @rule(max_cyc=st.sampled_from([None, 1, 2, 3, 5, 10]))
    def do_run(self, max_cyc):
        """Execute runner.run() with random parameters."""
        # Without stop_event, max_cycles or halt_async is the only way
        # to bound a run. Force max_cycles unless halt is pending.
        if max_cyc is None and not self._halt_pending:
            max_cyc = 5

        async def _run():
            try:
                result = await asyncio.wait_for(
                    self.runner.run(
                        max_cycles=max_cyc,
                    ),
                    timeout=3.0,
                )
            except asyncio.TimeoutError:
                result = "timeout"
            return result

        result = self._loop.run_until_complete(_run())
        self._last_result = result
        self._run_count += 1

        if result == "halted":
            self._halt_pending = False

        assert result in ("completed", "halted", "max_cycles",
                          "timeout"), f"unexpected result: {result}"
        assert result != "timeout", \
            "run() timed out -- possible hang in the state machine"

    @precondition(lambda self: not self._is_closed)
    @rule()
    def do_close(self):
        """Close the runner."""
        self._loop.run_until_complete(self.runner.close())
        self._is_closed = True

    @precondition(lambda self: self._is_closed)
    @rule()
    def run_after_close_raises(self):
        """Verify run() after close() raises."""
        try:
            self._loop.run_until_complete(self.runner.run())
            assert False, "run() after close() should raise"
        except RuntimeError:
            pass

    @precondition(lambda self: self._is_closed)
    @rule()
    def close_is_idempotent(self):
        """Verify double close doesn't raise."""
        self._loop.run_until_complete(self.runner.close())

    # -- Invariants --

    @invariant()
    def persistent_tasks_bounded(self):
        """Persistent task count never exceeds registered generator templates."""
        if self._is_closed:
            assert len(self.runner._persistent_tasks) == 0, \
                f"persistent tasks after close: {list(self.runner._persistent_tasks)}"
        else:
            n_tasks = len(self.runner._persistent_tasks)
            # Model tracks which templates we registered as generators
            assert n_tasks <= len(self._persistent_templates), \
                f"persistent tasks ({n_tasks}) > registered ({len(self._persistent_templates)})"

    @invariant()
    def no_stale_completed_persistent_tasks(self):
        """Between run() calls, stale done tasks are bounded by the number
        of generator templates (top-of-loop prune handles them)."""
        if not self._is_closed:
            done_count = sum(1 for t in self.runner._persistent_tasks.values()
                            if t.done())
            assert done_count <= len(self._persistent_templates), \
                f"too many stale persistent tasks: {done_count} done " \
                f"out of {len(self.runner._persistent_tasks)} tracked"

    @invariant()
    def closed_state_consistent(self):
        """After close, all state is cleaned up."""
        if self._is_closed:
            assert self.runner._closed is True
            assert self.env._goal_handler_state is None
            assert len(self.runner._persistent_tasks) == 0

    @invariant()
    def completed_means_no_active_tasks(self):
        """After 'completed', no pending and no active persistent tasks."""
        if self._last_result == "completed" and not self._is_closed:
            state = self.env._goal_handler_state
            if state is not None:
                assert len(state.pending) == 0, \
                    f"pending not empty after completed: {len(state.pending)}"
            active = {n: t for n, t in self.runner._persistent_tasks.items()
                      if not t.done()}
            assert len(active) == 0, \
                f"active persistent after completed: {list(active)}"

    @invariant()
    def halted_preserves_persistent(self):
        """After 'halted', persistent tasks are not cancelled."""
        if self._last_result == "halted" and not self._is_closed:
            for name, task in self.runner._persistent_tasks.items():
                assert not task.cancelled(), \
                    f"persistent task {name!r} was cancelled by halt"

    @invariant()
    def max_cycles_preserves_persistent(self):
        """After 'max_cycles', persistent tasks are not cancelled."""
        if self._last_result == "max_cycles" and not self._is_closed:
            for name, task in self.runner._persistent_tasks.items():
                assert not task.cancelled(), \
                    f"persistent task {name!r} was cancelled by max_cycles"


# -- Test configuration --

if CLIPS_70:
    AsyncRunnerTest = AsyncRunnerStateMachine.TestCase
    AsyncRunnerTest.settings = settings(
        max_examples=200,
        stateful_step_count=30,
        deadline=15000,
        suppress_health_check=[HealthCheck.too_slow],
    )


if __name__ == '__main__':
    unittest.main()
