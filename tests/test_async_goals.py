"""Tests for the async goal handler framework.

All tests require CLIPS 7.0+ (backward chaining goals).
Uses the DSL for rule/template definitions.

"""

import asyncio
import time
import unittest

import clipspyx
from clipspyx import Environment, Symbol
from clipspyx.dsl import Template, Rule, TimerEvent, AFTER, AT, EVERY

CLIPS_70 = clipspyx.CLIPS_MAJOR >= 7


# ---------------------------------------------------------------------------
# Shared DSL templates
# ---------------------------------------------------------------------------

class TimerResult(Template):
    msg: Symbol


# Reusable goal handler rule factories
def _make_goal_handler():
    class HandleTimerGoal(Rule):
        goal(TimerEvent(kind=k, name=n, seconds=s))
    return HandleTimerGoal


def _make_at_goal_handler():
    class HandleTimerGoal(Rule):
        goal(TimerEvent(kind=k, name=n, time=t))
    return HandleTimerGoal


# ---------------------------------------------------------------------------
# Enable/Disable tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestEnableDisable(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_enable_goal_handlers(self):
        """enable_goal_handlers initializes state and registers timer template."""
        from clipspyx.async_goals import enable_goal_handlers
        enable_goal_handlers(self.env)

        self.assertIsNotNone(self.env._goal_handler_state)
        self.assertIn('timer-event', self.env._goal_handler_state.handlers)
        tpl = self.env.find_template('timer-event')
        self.assertEqual(tpl.name, 'timer-event')

    def test_disable_goal_handlers(self):
        """disable_goal_handlers clears state."""
        from clipspyx.async_goals import enable_goal_handlers, disable_goal_handlers
        enable_goal_handlers(self.env)
        disable_goal_handlers(self.env)
        self.assertIsNone(self.env._goal_handler_state)

    def test_register_custom_handler(self):
        """register_goal_handler stores handler in registry."""
        from clipspyx.async_goals import enable_goal_handlers
        enable_goal_handlers(self.env)

        async def my_handler(goal, env):
            pass

        self.env.register_goal_handler('my-template', my_handler)
        self.assertIs(
            self.env._goal_handler_state.handlers['my-template'], my_handler)

    def test_register_without_enable_raises(self):
        """register_goal_handler raises if enable not called."""
        async def h(goal, env):
            pass

        with self.assertRaises(RuntimeError):
            self.env.register_goal_handler('x', h)


@unittest.skipIf(CLIPS_70, "Test only for CLIPS 6.4x")
class TestGuard64x(unittest.TestCase):
    def test_enable_raises_on_64x(self):
        """enable_goal_handlers raises TypeError on CLIPS 6.4x."""
        from clipspyx.async_goals import enable_goal_handlers
        env = Environment()
        with self.assertRaises(TypeError):
            enable_goal_handlers(env)


# ---------------------------------------------------------------------------
# Basic async_run tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunBasic(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        from clipspyx.async_goals import enable_goal_handlers
        enable_goal_handlers(self.env)

    def test_async_run_no_goals(self):
        """async_run returns immediately when no goals exist."""
        self.env.reset()
        asyncio.run(self.env.async_run())

    def test_async_run_without_enable_raises(self):
        """async_run raises if enable not called."""
        env = Environment()
        with self.assertRaises(RuntimeError):
            asyncio.run(env.async_run())


# ---------------------------------------------------------------------------
# Timer AFTER tests (DSL)
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestTimerAfter(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        from clipspyx.async_goals import enable_goal_handlers
        enable_goal_handlers(self.env)

    def test_timer_after_fires(self):
        """One-shot timer asserts a fact after the delay."""

        class OnTimerFired(Rule):
            te = TimerEvent(
                kind=Symbol("after"), name=Symbol("test-timer"), seconds=0.05)
            asserts(TimerResult(msg=Symbol("done")))

        self.env.define(TimerResult)
        self.env.define(_make_goal_handler())
        self.env.define(OnTimerFired)
        self.env.reset()

        start = time.time()
        asyncio.run(self.env.async_run())
        elapsed = time.time() - start

        self.assertGreaterEqual(elapsed, 0.04)
        rname = TimerResult.__clipspyx_dsl__.name
        results = [f for f in self.env.find_template(rname).facts()]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['msg'], Symbol('done'))

    def test_timer_after_fact_has_fired_at(self):
        """Timer-event fact has a non-zero fired_at value."""

        class OnTimerFired(Rule):
            te = TimerEvent(
                kind=Symbol("after"), name=Symbol("test-timer"), seconds=0.01)

        self.env.define(_make_goal_handler())
        self.env.define(OnTimerFired)
        self.env.reset()

        asyncio.run(self.env.async_run())

        timer_facts = [f for f in self.env.find_template('timer-event').facts()]
        self.assertEqual(len(timer_facts), 1)
        self.assertGreater(float(timer_facts[0]['fired_at']), 0)


# ---------------------------------------------------------------------------
# Timer AT tests (DSL, dynamic epoch via fact binding)
# ---------------------------------------------------------------------------

class ScheduleConfig(Template):
    """Carries a dynamic epoch timestamp into rule matching."""
    target_time: float


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestTimerAt(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        from clipspyx.async_goals import enable_goal_handlers
        enable_goal_handlers(self.env)

    def test_timer_at_fires(self):
        """Absolute time timer fires at the target time."""
        target = time.time() + 0.05

        class OnAtFired(Rule):
            cfg = ScheduleConfig(target_time=t)
            te = TimerEvent(kind=Symbol("at"), name=Symbol("at-test"), time=t)
            asserts(TimerResult(msg=Symbol("at-done")))

        self.env.define(TimerResult)
        self.env.define(ScheduleConfig)
        self.env.define(_make_at_goal_handler())
        self.env.define(OnAtFired)
        self.env.reset()

        scname = ScheduleConfig.__clipspyx_dsl__.name
        self.env.find_template(scname).assert_fact(target_time=target)

        asyncio.run(self.env.async_run())

        rname = TimerResult.__clipspyx_dsl__.name
        results = [f for f in self.env.find_template(rname).facts()]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['msg'], Symbol('at-done'))

    def test_timer_at_past_fires_immediately(self):
        """Absolute time in the past fires immediately."""
        target = time.time() - 1.0

        class OnPastFired(Rule):
            cfg = ScheduleConfig(target_time=t)
            te = TimerEvent(kind=Symbol("at"), name=Symbol("past-test"), time=t)
            asserts(TimerResult(msg=Symbol("past-done")))

        self.env.define(TimerResult)
        self.env.define(ScheduleConfig)
        self.env.define(_make_at_goal_handler())
        self.env.define(OnPastFired)
        self.env.reset()

        scname = ScheduleConfig.__clipspyx_dsl__.name
        self.env.find_template(scname).assert_fact(target_time=target)

        start = time.time()
        asyncio.run(self.env.async_run())
        elapsed = time.time() - start

        self.assertLess(elapsed, 1.0)
        rname = TimerResult.__clipspyx_dsl__.name
        results = [f for f in self.env.find_template(rname).facts()]
        self.assertEqual(len(results), 1)


# ---------------------------------------------------------------------------
# Timer EVERY tests (DSL)
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestTimerEvery(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        from clipspyx.async_goals import enable_goal_handlers
        enable_goal_handlers(self.env)

    def test_timer_every_fires_multiple_times(self):
        """Periodic timer fires multiple times with incrementing count."""

        class BeatLog(Template):
            n: int

        class OnBeat(Rule):
            te = TimerEvent(
                kind=Symbol("every"), name=Symbol("beat"),
                seconds=0.05, count=c)
            asserts(BeatLog(n=c))

        self.env.define(BeatLog)
        self.env.define(_make_goal_handler())
        self.env.define(OnBeat)
        self.env.reset()

        asyncio.run(self.env.async_run(max_cycles=4))

        blname = BeatLog.__clipspyx_dsl__.name
        logs = sorted(
            [f for f in self.env.find_template(blname).facts()],
            key=lambda f: int(f['n']))
        self.assertGreaterEqual(len(logs), 3)
        self.assertEqual(int(logs[0]['n']), 0)
        self.assertEqual(int(logs[1]['n']), 1)
        self.assertEqual(int(logs[2]['n']), 2)

    def test_cancel_periodic_by_retracting_controlling_fact(self):
        """Retracting a controlling fact stops periodic timer and exits loop."""

        class Active(Template):
            pass

        class BeatLog2(Template):
            n: int

        class OnBeat(Rule):
            Active()
            te = TimerEvent(
                kind=Symbol("every"), name=Symbol("canc-beat"),
                seconds=0.05, count=c)
            asserts(BeatLog2(n=c))

        # Stop after 2 beats by retracting Active
        class StopAfter2(Rule):
            a = Active()
            BeatLog2(n=2)
            retracts(a)

        self.env.define(Active)
        self.env.define(BeatLog2)
        self.env.define(_make_goal_handler())
        self.env.define(OnBeat)
        self.env.define(StopAfter2)
        self.env.reset()

        Active(__env__=self.env)

        # Should exit on its own - no max_cycles needed
        asyncio.run(self.env.async_run())

        blname = BeatLog2.__clipspyx_dsl__.name
        logs = [f for f in self.env.find_template(blname).facts()]
        # Got at least beats 0, 1, 2 before stopping
        self.assertGreaterEqual(len(logs), 3)
        # Active fact should be gone
        aname = Active.__clipspyx_dsl__.name
        active_facts = list(self.env.find_template(aname).facts())
        self.assertEqual(len(active_facts), 0)


# ---------------------------------------------------------------------------
# Concurrent goals tests (DSL)
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestConcurrentGoals(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        from clipspyx.async_goals import enable_goal_handlers
        enable_goal_handlers(self.env)

    def test_concurrent_timers(self):
        """Multiple timer goals dispatch concurrently."""

        class ConcResult(Template):
            name: Symbol

        class OnFastFired(Rule):
            te = TimerEvent(
                kind=Symbol("after"), name=Symbol("fast"), seconds=0.02)
            asserts(ConcResult(name=Symbol("fast")))

        class OnSlowFired(Rule):
            te = TimerEvent(
                kind=Symbol("after"), name=Symbol("slow"), seconds=0.05)
            asserts(ConcResult(name=Symbol("slow")))

        self.env.define(ConcResult)
        self.env.define(_make_goal_handler())
        self.env.define(OnFastFired)
        self.env.define(OnSlowFired)
        self.env.reset()

        start = time.time()
        asyncio.run(self.env.async_run())
        elapsed = time.time() - start

        crname = ConcResult.__clipspyx_dsl__.name
        results = {str(f['name'])
                   for f in self.env.find_template(crname).facts()}
        self.assertEqual(results, {'fast', 'slow'})
        self.assertLess(elapsed, 0.15)


# ---------------------------------------------------------------------------
# Error handling tests (DSL)
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestHandlerError(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        from clipspyx.async_goals import enable_goal_handlers
        enable_goal_handlers(self.env)

        class FailingOp(Template):
            x: int

        async def bad_handler(goal, env):
            raise ValueError("handler broke")

        self.env.define(FailingOp)
        self.FailingOp = FailingOp
        self.env.register_goal_handler(FailingOp, bad_handler)

    def test_handler_error_propagates(self):
        """Handler exceptions are wrapped in GoalHandlerError."""
        from clipspyx.async_goals import GoalHandlerError
        FailingOp = self.FailingOp

        class NeedFailing(Rule):
            goal(FailingOp(x=v))

        class TriggerFailing(Rule):
            f = FailingOp(x=42)

        self.env.define(NeedFailing)
        self.env.define(TriggerFailing)
        self.env.reset()

        with self.assertRaises(GoalHandlerError):
            asyncio.run(self.env.async_run())


# ---------------------------------------------------------------------------
# Custom goal handler tests (DSL)
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestCustomGoalHandler(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        from clipspyx.async_goals import enable_goal_handlers
        enable_goal_handlers(self.env)

        class ComputeRequest(Template):
            input: int

        class ComputeResponse(Template):
            input: int
            output: int

        self.ComputeRequest = ComputeRequest
        self.ComputeResponse = ComputeResponse

        async def compute_handler(goal, env):
            val = int(goal['input'])
            await asyncio.sleep(0.01)
            ComputeRequest(__env__=env, input=val)
            ComputeResponse(__env__=env, input=val, output=val * 2)

        self.env.define(ComputeRequest)
        self.env.define(ComputeResponse)
        self.env.register_goal_handler(ComputeRequest, compute_handler)

    def test_custom_handler_fulfills_goal(self):
        """Custom async handler asserts facts that satisfy the goal."""
        ComputeRequest = self.ComputeRequest
        ComputeResponse = self.ComputeResponse

        class ResultD(Template):
            doubled: int

        class NeedCompute(Rule):
            goal(ComputeRequest(input=n))

        class Process(Rule):
            req = ComputeRequest(input=5)
            resp = ComputeResponse(input=5, output=out)
            asserts(ResultD(doubled=out))

        self.env.define(ResultD)
        self.env.define(NeedCompute)
        self.env.define(Process)
        self.env.reset()

        asyncio.run(self.env.async_run())

        resp_name = ComputeResponse.__clipspyx_dsl__.name
        results = [f for f in self.env.find_template(resp_name).facts()]
        self.assertGreater(len(results), 0)
        self.assertEqual(int(results[0]['output']), 10)


if __name__ == '__main__':
    unittest.main()
