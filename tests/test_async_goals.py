"""Tests for the async goal handler framework.

All tests require CLIPS 7.0+ (backward chaining goals).
Uses the DSL for rule/template definitions.

"""

import asyncio
import time
import unittest
import warnings

import clipspyx
from clipspyx import Environment, Symbol
from clipspyx.dsl import Template, Rule, TimerEvent, AFTER, AT, EVERY
from clipspyx.async_goals import AsyncRunner, GoalHandlerError

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
        self.runner = AsyncRunner(self.env)

    def test_async_run_no_goals(self):
        """async_run returns immediately when no goals exist."""
        self.env.reset()
        asyncio.run(self.runner.run())

    def test_runner_auto_enables(self):
        """AsyncRunner auto-enables goal handlers if not already enabled."""
        env = Environment()
        runner = AsyncRunner(env)
        self.assertIsNotNone(env._goal_handler_state)
        env.reset()
        result = asyncio.run(runner.run())
        self.assertEqual(result, "completed")


# ---------------------------------------------------------------------------
# Timer AFTER tests (DSL)
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestTimerAfter(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.runner = AsyncRunner(self.env)

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
        asyncio.run(self.runner.run())
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

        asyncio.run(self.runner.run())

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
        self.runner = AsyncRunner(self.env)

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

        asyncio.run(self.runner.run())

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
        asyncio.run(self.runner.run())
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
        self.runner = AsyncRunner(self.env)

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

        asyncio.run(self.runner.run(max_cycles=4))

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
        asyncio.run(self.runner.run())

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
        self.runner = AsyncRunner(self.env)

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
        asyncio.run(self.runner.run())
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
        self.runner = AsyncRunner(self.env)

        class FailingOp(Template):
            x: int

        async def bad_handler(goal, env):
            raise ValueError("handler broke")

        self.env.define(FailingOp)
        self.FailingOp = FailingOp
        self.runner.register_handler(FailingOp, bad_handler)

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
            asyncio.run(self.runner.run())


# ---------------------------------------------------------------------------
# Custom goal handler tests (DSL)
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestCustomGoalHandler(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.runner = AsyncRunner(self.env)

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
        self.runner.register_handler(ComputeRequest, compute_handler)

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

        asyncio.run(self.runner.run())

        resp_name = ComputeResponse.__clipspyx_dsl__.name
        results = [f for f in self.env.find_template(resp_name).facts()]
        self.assertGreater(len(results), 0)
        self.assertEqual(int(results[0]['output']), 10)


# ---------------------------------------------------------------------------
# Cancellation tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestReturnValues(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.runner = AsyncRunner(self.env)

    def test_completed_return_value(self):
        """async_run returns 'completed' when no goals remain."""

        class OnTimer(Rule):
            te = TimerEvent(
                kind=Symbol("after"), name=Symbol("rv-test"), seconds=0.01)
            asserts(TimerResult(msg=Symbol("rv-done")))

        self.env.define(TimerResult)
        self.env.define(_make_goal_handler())
        self.env.define(OnTimer)
        self.env.reset()

        result = asyncio.run(self.runner.run())
        self.assertEqual(result, "completed")

    def test_max_cycles_return_value(self):
        """async_run returns 'max_cycles' when limit is reached."""

        class OnBeat(Rule):
            te = TimerEvent(
                kind=Symbol("every"), name=Symbol("mc-beat"),
                seconds=0.01)

        self.env.define(_make_goal_handler())
        self.env.define(OnBeat)
        self.env.reset()

        result = asyncio.run(self.runner.run(max_cycles=2))
        self.assertEqual(result, "max_cycles")


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestHaltAsync(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.runner = AsyncRunner(self.env)

    def test_halt_async_stops_loop(self):
        """halt_async() called from a rule action stops the loop."""

        class BeatCount(Template):
            n: int

        class OnBeat(Rule):
            te = TimerEvent(
                kind=Symbol("every"), name=Symbol("halt-beat"),
                seconds=0.01, count=c)
            asserts(BeatCount(n=c))

        class StopAt3(Rule):
            BeatCount(n=3)
            def __action__(self):
                self.__env__.halt_async()

        self.env.define(BeatCount)
        self.env.define(_make_goal_handler())
        self.env.define(OnBeat)
        self.env.define(StopAt3)
        self.env.reset()

        result = asyncio.run(self.runner.run())
        self.assertEqual(result, "halted")

        bcname = BeatCount.__clipspyx_dsl__.name
        beats = list(self.env.find_template(bcname).facts())
        # Should have beats 0, 1, 2, 3 (stopped after 3 was processed)
        self.assertGreaterEqual(len(beats), 3)

    def test_halt_async_without_enable(self):
        """halt_async() is a no-op if goal handlers not enabled."""
        env = Environment()
        env.halt_async()  # should not crash


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestStopEvent(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.runner = AsyncRunner(self.env)

    def test_stop_event_stops_loop(self):
        """Setting stop_event from an external task stops the loop."""

        class OnBeat(Rule):
            te = TimerEvent(
                kind=Symbol("every"), name=Symbol("stop-beat"),
                seconds=0.01)

        self.env.define(_make_goal_handler())
        self.env.define(OnBeat)
        self.env.reset()

        async def run_with_stop():
            stop = asyncio.Event()

            async def set_stop():
                await asyncio.sleep(0.05)
                stop.set()

            asyncio.create_task(set_stop())
            return await self.runner.run(stop_event=stop)

        result = asyncio.run(run_with_stop())
        self.assertEqual(result, "stopped")

    def test_stop_event_pre_set(self):
        """If stop_event is already set, async_run returns immediately."""

        class OnTimer(Rule):
            te = TimerEvent(
                kind=Symbol("after"), name=Symbol("pre-stop"), seconds=10.0)

        self.env.define(_make_goal_handler())
        self.env.define(OnTimer)
        self.env.reset()

        async def run_pre_stopped():
            stop = asyncio.Event()
            stop.set()
            return await self.runner.run(stop_event=stop)

        result = asyncio.run(run_pre_stopped())
        self.assertEqual(result, "stopped")


# ---------------------------------------------------------------------------
# AsyncRunner basic tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerBasic(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_runner_no_goals(self):
        """AsyncRunner.run returns 'completed' when no goals exist."""
        runner = AsyncRunner(self.env)
        self.env.reset()
        result = asyncio.run(runner.run())
        self.assertEqual(result, "completed")

    def test_runner_timer(self):
        """AsyncRunner fires a timer handler just like async_run."""
        runner = AsyncRunner(self.env)

        class OnTimer(Rule):
            te = TimerEvent(
                kind=Symbol("after"), name=Symbol("runner-test"), seconds=0.02)
            asserts(TimerResult(msg=Symbol("runner-done")))

        self.env.define(TimerResult)
        self.env.define(_make_goal_handler())
        self.env.define(OnTimer)
        self.env.reset()

        start = time.time()
        result = asyncio.run(runner.run())
        elapsed = time.time() - start

        self.assertEqual(result, "completed")
        self.assertGreaterEqual(elapsed, 0.01)
        rname = TimerResult.__clipspyx_dsl__.name
        results = [f for f in self.env.find_template(rname).facts()]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['msg'], Symbol('runner-done'))


# ---------------------------------------------------------------------------
# AsyncRunner persistent handler tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerPersistent(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_persistent_survives_stop_event(self):
        """A persistent handler task survives stop_event across run() calls."""

        class StreamEvent(Template):
            data: Symbol

        class StreamResult(Template):
            tag: Symbol

        # Goal handler rule: tells CLIPS to generate goals for StreamEvent
        class HandleStreamGoal(Rule):
            goal(StreamEvent(data=d))

        # Consuming rule: needs StreamEvent -> triggers goal generation
        class OnStream(Rule):
            se = StreamEvent(data=d)
            asserts(StreamResult(tag=Symbol("got-it")))

        collected = []
        started = asyncio.Event()

        async def stream_handler(goal, env):
            started.set()
            for i in range(10):
                await asyncio.sleep(0.02)
                collected.append(f"item-{i}")
            # Assert fact to satisfy goal
            StreamEvent(__env__=env, data=Symbol("stream-data"))

        runner = AsyncRunner(self.env)
        self.env.define(StreamEvent)
        self.env.define(StreamResult)
        self.env.define(HandleStreamGoal)
        self.env.define(OnStream)
        runner.register_handler(StreamEvent, stream_handler, persistent=True)
        self.env.reset()

        async def drive():
            # First run: stop quickly, persistent handler should survive
            stop1 = asyncio.Event()

            async def set_stop1():
                await started.wait()
                # Let the handler produce a few items before stopping
                await asyncio.sleep(0.05)
                stop1.set()

            asyncio.create_task(set_stop1())
            result1 = await runner.run(stop_event=stop1)
            self.assertEqual(result1, "stopped")

            # Persistent task should still be alive
            self.assertTrue(len(runner._persistent_tasks) > 0)
            alive = any(
                not t.done() for t in runner._persistent_tasks.values())
            self.assertTrue(alive)

            count_after_first_run = len(collected)
            self.assertGreater(count_after_first_run, 0)

            # Second run: let it finish naturally
            result2 = await runner.run()
            self.assertEqual(result2, "completed")

            # Handler produced items across both runs
            self.assertGreater(len(collected), count_after_first_run)

            await runner.close()

        asyncio.run(drive())


# ---------------------------------------------------------------------------
# AsyncRunner close tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerClose(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_close_cancels_persistent(self):
        """close() cancels persistent handlers and clears state."""

        class PingEvent(Template):
            seq: int

        class PingResult(Template):
            tag: Symbol

        class HandlePingGoal(Rule):
            goal(PingEvent(seq=s))

        # Consuming rule to trigger goal generation
        class OnPing(Rule):
            pe = PingEvent(seq=s)
            asserts(PingResult(tag=Symbol("pinged")))

        async def ping_handler(goal, env):
            # Assert fact to satisfy goal, then loop forever
            PingEvent(__env__=env, seq=0)
            while True:
                await asyncio.sleep(0.01)

        runner = AsyncRunner(self.env)
        self.env.define(PingEvent)
        self.env.define(PingResult)
        self.env.define(HandlePingGoal)
        self.env.define(OnPing)
        runner.register_handler(PingEvent, ping_handler, persistent=True)
        self.env.reset()

        async def drive():
            stop = asyncio.Event()

            async def set_stop():
                await asyncio.sleep(0.05)
                stop.set()

            asyncio.create_task(set_stop())
            result = await runner.run(stop_event=stop)
            self.assertEqual(result, "stopped")

            # Persistent task should be alive before close
            self.assertTrue(len(runner._persistent_tasks) > 0)

            await runner.close()

            # After close, state is cleaned up
            self.assertIsNone(self.env._goal_handler_state)
            self.assertEqual(len(runner._persistent_tasks), 0)

        asyncio.run(drive())


# ---------------------------------------------------------------------------
# AsyncRunner context manager tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerContextManager(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_context_manager(self):
        """async with AsyncRunner auto-enables and auto-closes."""

        async def drive():
            async with AsyncRunner(self.env) as runner:
                # Inside the context, state should exist
                self.assertIsNotNone(self.env._goal_handler_state)
                self.env.reset()
                result = await runner.run()
                self.assertEqual(result, "completed")

            # After exit, state should be cleaned up
            self.assertIsNone(self.env._goal_handler_state)

        asyncio.run(drive())


# ---------------------------------------------------------------------------
# AsyncRunner mixed handler tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerMixed(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_mixed_handlers(self):
        """Non-persistent handler is cancelled on stop, persistent survives."""

        class LongStream(Template):
            tag: Symbol

        class ShortTask(Template):
            tag: Symbol

        class MixedResult(Template):
            tag: Symbol

        class HandleLongStreamGoal(Rule):
            goal(LongStream(tag=t))

        class HandleShortTaskGoal(Rule):
            goal(ShortTask(tag=t))

        # Consuming rules to trigger goal generation
        class OnLongStream(Rule):
            ls = LongStream(tag=t)
            asserts(MixedResult(tag=Symbol("long")))

        class OnShortTask(Rule):
            st = ShortTask(tag=t)
            asserts(MixedResult(tag=Symbol("short")))

        persistent_items = []
        nonpersistent_items = []

        async def long_handler(goal, env):
            LongStream(__env__=env, tag=Symbol("data"))
            for i in range(20):
                await asyncio.sleep(0.02)
                persistent_items.append(i)

        async def short_handler(goal, env):
            for i in range(20):
                await asyncio.sleep(0.02)
                nonpersistent_items.append(i)
            ShortTask(__env__=env, tag=Symbol("done"))

        runner = AsyncRunner(self.env)
        self.env.define(LongStream)
        self.env.define(ShortTask)
        self.env.define(MixedResult)
        self.env.define(HandleLongStreamGoal)
        self.env.define(HandleShortTaskGoal)
        self.env.define(OnLongStream)
        self.env.define(OnShortTask)
        runner.register_handler(LongStream, long_handler, persistent=True)
        runner.register_handler(ShortTask, short_handler, persistent=False)
        self.env.reset()

        async def drive():
            stop = asyncio.Event()

            async def set_stop():
                await asyncio.sleep(0.06)
                stop.set()

            asyncio.create_task(set_stop())
            result = await runner.run(stop_event=stop)
            self.assertEqual(result, "stopped")

            # Non-persistent tasks should have been cancelled (pending cleared)
            state = self.env._goal_handler_state
            self.assertEqual(len(state.pending), 0)

            # Persistent task should still be alive
            alive = any(
                not t.done() for t in runner._persistent_tasks.values())
            self.assertTrue(alive)

            await runner.close()

        asyncio.run(drive())


# ---------------------------------------------------------------------------
# AsyncRunner persistent error propagation tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerPersistentError(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_persistent_error_propagates(self):
        """Error in a persistent handler raises GoalHandlerError."""

        class BadStream(Template):
            code: int

        class BadResult(Template):
            tag: Symbol

        class HandleBadStreamGoal(Rule):
            goal(BadStream(code=c))

        class OnBadStream(Rule):
            bs = BadStream(code=c)
            asserts(BadResult(tag=Symbol("bad")))

        async def bad_handler(goal, env):
            raise ValueError("persistent handler exploded")

        runner = AsyncRunner(self.env)
        self.env.define(BadStream)
        self.env.define(BadResult)
        self.env.define(HandleBadStreamGoal)
        self.env.define(OnBadStream)
        runner.register_handler(BadStream, bad_handler, persistent=True)
        self.env.reset()

        with self.assertRaises(GoalHandlerError):
            asyncio.run(runner.run())


# ---------------------------------------------------------------------------
# AsyncRunner persistent re-dispatch tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerPersistentRedispatch(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_redispatch_after_completion(self):
        """A persistent handler that completes quickly is re-dispatched on
        subsequent goals."""

        class QuickJob(Template):
            tag: Symbol

        class QuickJobResult(Template):
            tag: Symbol

        class HandleQuickJobGoal(Rule):
            goal(QuickJob(tag=t))

        # Consuming rule: needs QuickJob fact
        class OnQuickJob(Rule):
            qj = QuickJob(tag=t)
            asserts(QuickJobResult(tag=t))

        call_count = []

        async def quick_handler(goal, env):
            call_count.append(1)
            await asyncio.sleep(0.01)
            QuickJob(__env__=env, tag=Symbol("done"))

        runner = AsyncRunner(self.env)
        self.env.define(QuickJob)
        self.env.define(QuickJobResult)
        self.env.define(HandleQuickJobGoal)
        self.env.define(OnQuickJob)
        runner.register_handler(QuickJob, quick_handler, persistent=True)
        self.env.reset()

        result = asyncio.run(runner.run())
        self.assertEqual(result, "completed")
        # Handler should have been dispatched at least once
        self.assertGreater(len(call_count), 0)


# ---------------------------------------------------------------------------
# Deprecation warning tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerDeprecation(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_async_run_emits_deprecation(self):
        """async_run() emits DeprecationWarning."""
        from clipspyx.async_goals import async_run, enable_goal_handlers
        enable_goal_handlers(self.env)
        self.env.reset()

        async def drive():
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                await async_run(self.env)
                self.assertTrue(
                    any(issubclass(x.category, DeprecationWarning) for x in w),
                    "async_run() should emit DeprecationWarning")

        asyncio.run(drive())

    def test_env_async_run_emits_deprecation(self):
        """env.async_run() emits DeprecationWarning."""
        from clipspyx.async_goals import enable_goal_handlers
        enable_goal_handlers(self.env)
        self.env.reset()

        async def drive():
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                await self.env.async_run()
                self.assertTrue(
                    any(issubclass(x.category, DeprecationWarning) for x in w),
                    "env.async_run() should emit DeprecationWarning")

        asyncio.run(drive())


if __name__ == '__main__':
    unittest.main()
