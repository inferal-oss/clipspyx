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
        """Retracting a controlling fact stops the consuming rule from
        firing, though the generator keeps ticking until close()."""

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

        async def drive():
            # Run enough cycles for beats 0, 1, 2 and Active retraction
            result = await self.runner.run(max_cycles=6)
            self.assertEqual(result, "max_cycles")

            blname = BeatLog2.__clipspyx_dsl__.name
            logs = [f for f in self.env.find_template(blname).facts()]
            # Got at least beats 0, 1, 2 before Active was retracted
            self.assertGreaterEqual(len(logs), 3)
            # Active fact should be gone
            aname = Active.__clipspyx_dsl__.name
            active_facts = list(self.env.find_template(aname).facts())
            self.assertEqual(len(active_facts), 0)

            await self.runner.close()

        asyncio.run(drive())


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

    def test_persistent_maintains_state_across_runs(self):
        """A persistent handler task maintains state across run() calls."""

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

        async def stream_handler(goal, env):
            StreamEvent(__env__=env, data=Symbol("stream-data"))
            for i in range(10):
                await asyncio.sleep(0.02)
                collected.append(f"item-{i}")
                yield

        runner = AsyncRunner(self.env)
        self.env.define(StreamEvent)
        self.env.define(StreamResult)
        self.env.define(HandleStreamGoal)
        self.env.define(OnStream)
        runner.register_handler(StreamEvent, stream_handler)
        self.env.reset()

        async def drive():
            # First run: limited cycles, handler starts producing
            result1 = await runner.run(max_cycles=3)
            count_after_first = len(collected)
            self.assertGreater(count_after_first, 0)

            # Second run: handler continues from where it left off
            result2 = await runner.run(max_cycles=5)
            self.assertGreater(len(collected), count_after_first)

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
            PingEvent(__env__=env, seq=0)
            while True:
                await asyncio.sleep(0.01)
                yield

        runner = AsyncRunner(self.env)
        self.env.define(PingEvent)
        self.env.define(PingResult)
        self.env.define(HandlePingGoal)
        self.env.define(OnPing)
        runner.register_handler(PingEvent, ping_handler)
        self.env.reset()

        async def drive():
            result = await runner.run(max_cycles=2)
            # Persistent task should exist
            self.assertTrue(len(runner._persistent_tasks) > 0)

            await runner.close()
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
        """Non-persistent handler completes per-goal, persistent survives."""

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
                yield

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
        runner.register_handler(LongStream, long_handler)
        runner.register_handler(ShortTask, short_handler)
        self.env.reset()

        async def drive():
            result = await runner.run(max_cycles=3)

            # Non-persistent tasks should be done (per-goal, completed or exhausted)
            state = self.env._goal_handler_state
            # Persistent task should still be alive
            alive = any(not t.done() for t in runner._persistent_tasks.values())
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
        runner.register_handler(BadStream, bad_handler)
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
        """A persistent handler that completes is removed from tracking,
        allowing re-dispatch when a new goal appears.

        Uses max_cycles to drive two cycles. The handler completes in each
        cycle and must be re-dispatched for the second.
        """

        class Fetch(Template):
            tag: Symbol

        class FetchResult(Template):
            tag: Symbol

        class HandleFetchGoal(Rule):
            goal(Fetch(tag=t))

        class Active(Template):
            pass

        # Consuming rule retracts Fetch so the goal regenerates
        class OnFetch(Rule):
            Active()
            f = Fetch(tag=t)
            retracts(f)
            asserts(FetchResult(tag=t))

        dispatch_count = []

        async def fetch_handler(goal, env):
            dispatch_count.append(1)
            await asyncio.sleep(0.01)
            Fetch(__env__=env, tag=Symbol("data"))

        runner = AsyncRunner(self.env)
        self.env.define(Fetch)
        self.env.define(FetchResult)
        self.env.define(Active)
        self.env.define(HandleFetchGoal)
        self.env.define(OnFetch)
        runner.register_handler(Fetch, fetch_handler)
        self.env.reset()
        Active(__env__=self.env)

        async def drive():
            # Run enough cycles for multiple dispatches
            await runner.run(max_cycles=6)

            # Handler should have been dispatched multiple times
            # (completes, goal regenerates via retraction, re-dispatched)
            self.assertGreaterEqual(len(dispatch_count), 2)

            await runner.close()

        asyncio.run(drive())



# ---------------------------------------------------------------------------
# Persistent handler edge case tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerPersistentDedup(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_one_task_per_template(self):
        """Multiple goals for the same persistent template share one task."""

        class Sensor(Template):
            reading: int

        class SensorLog(Template):
            tag: Symbol

        class HandleSensorGoal(Rule):
            goal(Sensor(reading=r))

        # Two consuming rules that both need Sensor facts
        class LogSensorA(Rule):
            s = Sensor(reading=42)
            asserts(SensorLog(tag=Symbol("a")))

        class LogSensorB(Rule):
            s = Sensor(reading=99)
            asserts(SensorLog(tag=Symbol("b")))

        dispatch_count = []

        async def sensor_handler(goal, env):
            dispatch_count.append(1)
            await asyncio.sleep(0.01)
            Sensor(__env__=env, reading=42)
            Sensor(__env__=env, reading=99)
            yield

        runner = AsyncRunner(self.env)
        self.env.define(Sensor)
        self.env.define(SensorLog)
        self.env.define(HandleSensorGoal)
        self.env.define(LogSensorA)
        self.env.define(LogSensorB)
        runner.register_handler(Sensor, sensor_handler)
        self.env.reset()

        result = asyncio.run(runner.run())
        self.assertEqual(result, "completed")
        # Should have been dispatched exactly once (one task per template)
        self.assertEqual(len(dispatch_count), 1)


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerPersistentGoalRetraction(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_goal_retraction_does_not_cancel_persistent(self):
        """Persistent task survives when its triggering goal is retracted."""

        class Feed(Template):
            tag: Symbol

        class FeedResult(Template):
            tag: Symbol

        class Active(Template):
            pass

        class HandleFeedGoal(Rule):
            goal(Feed(tag=t))

        # Goal only generated while Active exists
        class OnFeed(Rule):
            Active()
            f = Feed(tag=t)
            asserts(FeedResult(tag=t))

        # Retract Active after first cycle to kill the goal
        class DeactivateAfterFeed(Rule):
            a = Active()
            FeedResult(tag=t)
            retracts(a)

        handler_alive = []

        async def feed_handler(goal, env):
            Feed(__env__=env, tag=Symbol("data"))
            # Keep running after satisfying the goal
            for i in range(5):
                await asyncio.sleep(0.02)
                handler_alive.append(i)

        runner = AsyncRunner(self.env)
        self.env.define(Feed)
        self.env.define(FeedResult)
        self.env.define(Active)
        self.env.define(HandleFeedGoal)
        self.env.define(OnFeed)
        self.env.define(DeactivateAfterFeed)
        runner.register_handler(Feed, feed_handler)
        self.env.reset()
        Active(__env__=self.env)

        async def drive():
            # Run until handler finishes (goal gets retracted mid-run
            # when Active is removed, but persistent task keeps going)
            result = await runner.run()
            self.assertEqual(result, "completed")
            # Handler kept running after goal retraction
            self.assertEqual(len(handler_alive), 5)
            await runner.close()

        asyncio.run(drive())


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerPersistentHalt(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_halt_returns_with_persistent_alive(self):
        """halt_async() returns 'halted' but persistent tasks stay alive."""

        class Monitor(Template):
            tag: Symbol

        class MonitorResult(Template):
            tag: Symbol

        class HandleMonitorGoal(Rule):
            goal(Monitor(tag=t))

        class OnMonitor(Rule):
            m = Monitor(tag=t)
            asserts(MonitorResult(tag=t))

        # Halt after seeing the result
        class HaltOnResult(Rule):
            MonitorResult(tag=t)
            def __action__(self):
                self.__env__.halt_async()

        async def monitor_handler(goal, env):
            Monitor(__env__=env, tag=Symbol("ping"))
            while True:
                await asyncio.sleep(0.01)
                yield

        runner = AsyncRunner(self.env)
        self.env.define(Monitor)
        self.env.define(MonitorResult)
        self.env.define(HandleMonitorGoal)
        self.env.define(OnMonitor)
        self.env.define(HaltOnResult)
        runner.register_handler(Monitor, monitor_handler)
        self.env.reset()

        async def drive():
            result = await runner.run()
            self.assertEqual(result, "halted")

            alive = any(not t.done() for t in runner._persistent_tasks.values())
            self.assertTrue(alive, "persistent task should survive halt")

            await runner.close()
            self.assertEqual(len(runner._persistent_tasks), 0)

        asyncio.run(drive())


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerPersistentMaxCycles(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_max_cycles_with_persistent_alive(self):
        """max_cycles returns with persistent tasks still running.

        Uses an EVERY timer to drive cycles (timer completes each cycle,
        letting the loop iterate). The persistent handler runs alongside.
        max_cycles limits how many timer cycles execute.
        """

        class Stream(Template):
            tag: Symbol

        class StreamLog(Template):
            tag: Symbol

        class HandleStreamGoal(Rule):
            goal(Stream(tag=t))

        class OnStream(Rule):
            s = Stream(tag=t)
            asserts(StreamLog(tag=t))

        # EVERY timer drives cycles (the timer handler completes each
        # cycle, allowing the loop to iterate and hit max_cycles)
        class OnBeat(Rule):
            te = TimerEvent(
                kind=Symbol("every"), name=Symbol("mc-beat"),
                seconds=0.01)

        stream_running = []

        async def stream_handler(goal, env):
            Stream(__env__=env, tag=Symbol("data"))
            while True:
                await asyncio.sleep(0.01)
                stream_running.append(1)
                yield

        runner = AsyncRunner(self.env)
        self.env.define(Stream)
        self.env.define(StreamLog)
        self.env.define(HandleStreamGoal)
        self.env.define(OnStream)
        self.env.define(_make_goal_handler())
        self.env.define(OnBeat)
        runner.register_handler(Stream, stream_handler)
        self.env.reset()

        async def drive():
            result = await runner.run(max_cycles=3)
            self.assertEqual(result, "max_cycles")

            # Persistent task still alive
            alive = any(
                not t.done() for t in runner._persistent_tasks.values())
            self.assertTrue(alive, "persistent task should survive max_cycles")

            await runner.close()

        asyncio.run(drive())


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerPersistentFactCycle(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_persistent_handler_drives_fact_cycle(self):
        """Persistent handler asserts facts across multiple yields,
        driving a fact processing cycle.

        Verifies that multiple facts are processed, with the persistent
        handler producing messages that CLIPS rules consume.
        """

        class Message(Template):
            seq: int

        class Processed(Template):
            seq: int

        class HandleMessageGoal(Rule):
            goal(Message(seq=s))

        class ProcessMessage(Rule):
            m = Message(seq=s)
            asserts(Processed(seq=s))

        async def message_handler(goal, env):
            for seq in [1, 2, 3]:
                await asyncio.sleep(0.02)
                Message(__env__=env, seq=seq)
                yield

        runner = AsyncRunner(self.env)
        self.env.define(Message)
        self.env.define(Processed)
        self.env.define(HandleMessageGoal)
        self.env.define(ProcessMessage)
        runner.register_handler(Message, message_handler)
        self.env.reset()

        async def drive():
            result = await runner.run(max_cycles=10)

            pname = Processed.__clipspyx_dsl__.name
            final = list(self.env.find_template(pname).facts())
            seqs = sorted(int(f['seq']) for f in final)
            self.assertGreaterEqual(len(seqs), 2,
                                    f"expected multiple processed messages, got {seqs}")

            await runner.close()

        asyncio.run(drive())


# ---------------------------------------------------------------------------
# AsyncRunner lifecycle edge cases
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerLifecycle(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_run_after_close_raises(self):
        """Calling run() after close() raises RuntimeError."""

        async def drive():
            runner = AsyncRunner(self.env)
            await runner.close()
            with self.assertRaises(RuntimeError):
                await runner.run()

        asyncio.run(drive())

    def test_close_idempotent(self):
        """Calling close() twice does not raise."""

        async def drive():
            runner = AsyncRunner(self.env)
            await runner.close()
            await runner.close()  # should not raise

        asyncio.run(drive())


# ---------------------------------------------------------------------------
# Noop handler (whitebox) — verifies dispatch count
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerNoopHandler(unittest.TestCase):
    """Regression: coroutine handler that cannot satisfy its goal
    must not be re-dispatched infinitely."""

    def setUp(self):
        self.env = Environment()

    def test_noop_handler_dispatched_once(self):
        """A handler that completes without satisfying the goal runs once."""

        class Wanted(Template):
            x: int

        class WantedResult(Template):
            x: int

        class NeedWanted(Rule):
            goal(Wanted(x=v))

        class OnWanted(Rule):
            w = Wanted(x=v)
            asserts(WantedResult(x=v))

        dispatch_count = []

        async def noop_handler(goal, env):
            dispatch_count.append(1)
            await asyncio.sleep(0.001)
            # Does NOT assert a Wanted fact → goal stays unsatisfied

        runner = AsyncRunner(self.env)
        self.env.define(Wanted)
        self.env.define(WantedResult)
        self.env.define(NeedWanted)
        self.env.define(OnWanted)
        runner.register_handler(Wanted, noop_handler)
        self.env.reset()

        async def drive():
            result = await asyncio.wait_for(runner.run(), timeout=2.0)
            self.assertEqual(result, "completed")
            self.assertEqual(len(dispatch_count), 1)
            await runner.close()

        asyncio.run(drive())


# ---------------------------------------------------------------------------
# Unsatisfied-goal blackbox tests — no access to runner internals
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerUnsatisfiedGoalBlackbox(unittest.TestCase):
    """Blackbox tests for unsatisfied coroutine goal behavior."""

    def setUp(self):
        self.env = Environment()

    def test_unsatisfied_handler_terminates(self):
        """Runner terminates when a handler can't satisfy its goal."""

        class Info(Template):
            key: Symbol

        class InfoResult(Template):
            key: Symbol

        class NeedInfo(Rule):
            goal(Info(key=k))

        class OnInfo(Rule):
            i = Info(key=k)
            asserts(InfoResult(key=k))

        async def noop(goal, env):
            await asyncio.sleep(0.001)

        runner = AsyncRunner(self.env)
        self.env.define(Info)
        self.env.define(InfoResult)
        self.env.define(NeedInfo)
        self.env.define(OnInfo)
        runner.register_handler(Info, noop)
        self.env.reset()

        async def drive():
            result = await asyncio.wait_for(runner.run(), timeout=2.0)
            self.assertEqual(result, "completed")
            # Goal should still exist (unsatisfied, not retracted)
            goals = list(self.env.goals())
            self.assertGreater(len(goals), 0,
                               "Unsatisfied goal should persist")
            await runner.close()

        asyncio.run(drive())

    def test_satisfied_handler_not_blocked(self):
        """A satisfying handler works normally alongside an unsatisfying one."""

        class Alpha(Template):
            tag: Symbol

        class AlphaResult(Template):
            tag: Symbol

        class NeedAlpha(Rule):
            goal(Alpha(tag=t))

        class OnAlpha(Rule):
            a = Alpha(tag=t)
            asserts(AlphaResult(tag=t))

        class Beta(Template):
            tag: Symbol

        class BetaResult(Template):
            tag: Symbol

        class NeedBeta(Rule):
            goal(Beta(tag=t))

        class OnBeta(Rule):
            b = Beta(tag=t)
            asserts(BetaResult(tag=t))

        alpha_calls = []
        beta_calls = []

        async def alpha_handler(goal, env):
            """Satisfies its goal by asserting the needed fact."""
            alpha_calls.append(1)
            await asyncio.sleep(0.001)
            Alpha(__env__=env, tag=Symbol("ok"))

        async def beta_handler(goal, env):
            """Cannot satisfy its goal — does nothing."""
            beta_calls.append(1)
            await asyncio.sleep(0.001)

        runner = AsyncRunner(self.env)
        self.env.define(Alpha)
        self.env.define(AlphaResult)
        self.env.define(NeedAlpha)
        self.env.define(OnAlpha)
        self.env.define(Beta)
        self.env.define(BetaResult)
        self.env.define(NeedBeta)
        self.env.define(OnBeta)
        runner.register_handler(Alpha, alpha_handler)
        runner.register_handler(Beta, beta_handler)
        self.env.reset()

        async def drive():
            result = await asyncio.wait_for(runner.run(), timeout=5.0)
            self.assertEqual(result, "completed")
            # Alpha handler ran and satisfied its goal
            self.assertGreater(len(alpha_calls), 0)
            alpha_name = AlphaResult.__clipspyx_dsl__.name
            alpha_results = list(self.env.find_template(alpha_name).facts())
            self.assertGreater(len(alpha_results), 0,
                               "Alpha goal should be satisfied")
            # Beta handler ran once but could not satisfy
            self.assertEqual(len(beta_calls), 1)
            await runner.close()

        asyncio.run(drive())

    def test_new_goal_dispatched_after_unsatisfied(self):
        """After reset(), a new goal (same template, new index) is dispatched
        even though the previous incarnation was skipped."""

        class Fetch(Template):
            url: Symbol

        class FetchResult(Template):
            url: Symbol

        class NeedFetch(Rule):
            goal(Fetch(url=u))

        class OnFetch(Rule):
            f = Fetch(url=u)
            asserts(FetchResult(url=u))

        calls = []

        async def fetch_handler(goal, env):
            calls.append(1)
            await asyncio.sleep(0.001)
            # Never satisfies the goal

        runner = AsyncRunner(self.env)
        self.env.define(Fetch)
        self.env.define(FetchResult)
        self.env.define(NeedFetch)
        self.env.define(OnFetch)
        runner.register_handler(Fetch, fetch_handler)
        self.env.reset()

        async def drive():
            # First run: handler dispatched, can't satisfy, skipped
            result = await asyncio.wait_for(runner.run(), timeout=2.0)
            self.assertEqual(result, "completed")
            self.assertEqual(len(calls), 1)

            # Reset creates fresh goals with new indices
            self.env.reset()

            # Second run: new goal (different index) should be dispatched
            result = await asyncio.wait_for(runner.run(), timeout=2.0)
            self.assertEqual(result, "completed")
            self.assertEqual(len(calls), 2,
                             "Handler should be dispatched for new goal")
            await runner.close()

        asyncio.run(drive())


if __name__ == '__main__':
    unittest.main()
