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

    def test_one_task_per_goal(self):
        """Each goal for the same persistent template gets its own task."""

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
            Sensor(__env__=env, reading=int(goal['reading']))
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
        # Each goal dispatches its own handler (per-goal, not per-template)
        self.assertEqual(len(dispatch_count), 2)


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


# ---------------------------------------------------------------------------
# AsyncRunner wake tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAsyncRunnerWake(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_wake_unblocks_wait(self):
        """wake() interrupts a blocked _wait_for_handlers and lets run() cycle."""

        class Probe(Template):
            tag: Symbol

        class ProbeResult(Template):
            tag: Symbol

        class HandleProbeGoal(Rule):
            goal(Probe(tag=t))

        class OnProbe(Rule):
            p = Probe(tag=t)
            asserts(ProbeResult(tag=t))

        async def slow_handler(goal, env):
            Probe(__env__=env, tag=Symbol("slow"))
            yield                       # first gen step completes quickly
            await asyncio.sleep(300)    # second gen step blocks
            yield

        runner = AsyncRunner(self.env)
        self.env.define(Probe)
        self.env.define(ProbeResult)
        self.env.define(HandleProbeGoal)
        self.env.define(OnProbe)
        runner.register_handler(Probe, slow_handler)
        self.env.reset()

        async def drive():
            # Run with max_cycles=3: cycle 1 dispatches & completes first
            # gen step (quick), cycle 2 blocks in _wait on second gen step
            # (sleeping 300s).
            run_task = asyncio.create_task(runner.run(max_cycles=3))
            await asyncio.sleep(0.1)    # let it reach _wait_for_handlers

            # wake unblocks the wait; cycle 3 hits max_cycles → returns
            runner.wake()
            result = await asyncio.wait_for(run_task, timeout=2.0)
            self.assertEqual(result, "max_cycles")

            await runner.close()

        asyncio.run(drive())

    def test_wake_before_run(self):
        """wake() called before run() is latched and consumed immediately."""

        class Signal(Template):
            tag: Symbol

        class SignalResult(Template):
            tag: Symbol

        class HandleSignalGoal(Rule):
            goal(Signal(tag=t))

        class OnSignal(Rule):
            s = Signal(tag=t)
            asserts(SignalResult(tag=t))

        async def long_handler(goal, env):
            Signal(__env__=env, tag=Symbol("sig"))
            yield                       # first gen step completes quickly
            await asyncio.sleep(300)    # second gen step blocks
            yield

        runner = AsyncRunner(self.env)
        self.env.define(Signal)
        self.env.define(SignalResult)
        self.env.define(HandleSignalGoal)
        self.env.define(OnSignal)
        runner.register_handler(Signal, long_handler)
        self.env.reset()

        async def drive():
            # First run: cycle 1 dispatches & completes first gen step,
            # cycle 2 hits max_cycles before blocking on second gen step.
            r1 = await asyncio.wait_for(runner.run(max_cycles=2), timeout=2.0)
            self.assertEqual(r1, "max_cycles")

            # Wake BEFORE calling run — event is pre-set
            runner.wake()
            # max_cycles=2: cycle 1 does env.run(), then _wait_for_handlers
            # sees the pre-set wake, returns None; cycle 2 hits max_cycles.
            r2 = await asyncio.wait_for(runner.run(max_cycles=2), timeout=2.0)
            self.assertEqual(r2, "max_cycles")

            await runner.close()

        asyncio.run(drive())

    def test_wake_with_no_tasks(self):
        """wake() with no pending tasks causes one extra cycle before completing."""

        runner = AsyncRunner(self.env)

        async def drive():
            # Pre-set wake with no handlers registered
            runner.wake()
            # run() should cycle (env.run finds nothing) and complete
            r = await asyncio.wait_for(runner.run(max_cycles=2), timeout=2.0)
            self.assertEqual(r, "completed")
            await runner.close()

        asyncio.run(drive())

    def test_wake_after_close(self):
        """wake() after close() is harmless — no error raised."""

        runner = AsyncRunner(self.env)

        async def drive():
            await runner.close()
            runner.wake()  # should not raise

        asyncio.run(drive())

    def test_wake_simultaneous_with_handler(self):
        """wake + handler completing at the same time: both are handled."""

        class Item(Template):
            tag: Symbol

        class ItemResult(Template):
            tag: Symbol

        class HandleItemGoal(Rule):
            goal(Item(tag=t))

        class OnItem(Rule):
            i = Item(tag=t)
            asserts(ItemResult(tag=t))

        handler_ran = []

        async def quick_handler(goal, env):
            handler_ran.append(1)
            await asyncio.sleep(0.01)
            Item(__env__=env, tag=Symbol("done"))
            yield                       # first gen step completes fast
            await asyncio.sleep(300)    # second gen step blocks
            yield

        runner = AsyncRunner(self.env)
        self.env.define(Item)
        self.env.define(ItemResult)
        self.env.define(HandleItemGoal)
        self.env.define(OnItem)
        runner.register_handler(Item, quick_handler)
        self.env.reset()

        async def drive():
            # Start run — handler dispatches and first gen step completes
            r1 = await asyncio.wait_for(runner.run(max_cycles=2), timeout=2.0)
            self.assertEqual(len(handler_ran), 1)

            # Now handler is on second gen step (sleeping 300s).
            # Wake and run concurrently — wake fires alongside the blocked handler.
            run_task = asyncio.create_task(runner.run(max_cycles=2))
            await asyncio.sleep(0.05)
            runner.wake()
            # Cycle 1: wake unblocks _wait; cycle 2: hits max_cycles.
            r2 = await asyncio.wait_for(run_task, timeout=2.0)
            self.assertEqual(r2, "max_cycles")

            await runner.close()

        asyncio.run(drive())

    def test_wake_multiple_calls_idempotent(self):
        """Multiple wake() calls before consumption trigger only one extra cycle."""

        class Tick(Template):
            tag: Symbol

        class TickResult(Template):
            tag: Symbol

        class HandleTickGoal(Rule):
            goal(Tick(tag=t))

        class OnTick(Rule):
            tk = Tick(tag=t)
            asserts(TickResult(tag=t))

        async def blocking_handler(goal, env):
            Tick(__env__=env, tag=Symbol("t"))
            yield                       # first gen step completes fast
            await asyncio.sleep(300)    # second gen step blocks
            yield

        runner = AsyncRunner(self.env)
        self.env.define(Tick)
        self.env.define(TickResult)
        self.env.define(HandleTickGoal)
        self.env.define(OnTick)
        runner.register_handler(Tick, blocking_handler)
        self.env.reset()

        async def drive():
            # Start handler
            r1 = await asyncio.wait_for(runner.run(max_cycles=2), timeout=2.0)

            # Multiple wake calls — only one extra cycle should result
            runner.wake()
            runner.wake()
            runner.wake()

            run_task = asyncio.create_task(runner.run(max_cycles=3))
            await asyncio.sleep(0.05)
            # The pre-set wake is consumed on cycle 1's _wait_for_handlers.
            # Cycle 2 blocks on the handler (no more wake events).
            # We need to wake again to unblock cycle 2 so cycle 3 hits max.
            runner.wake()
            r2 = await asyncio.wait_for(run_task, timeout=2.0)
            self.assertEqual(r2, "max_cycles")

            await runner.close()

        asyncio.run(drive())


# ---------------------------------------------------------------------------
# Goal + Not CE with TimerEvent tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestGoalWithNotCETimer(unittest.TestCase):
    """Prove goal + not CE works with async TimerEvent handlers.

    The canonical backward-chaining pattern uses goal() to detect when a
    goal is generated and ~Template() to ensure no matching fact exists.
    This must work with the built-in timer goal handler.
    """

    def setUp(self):
        self.env = Environment()
        self.runner = AsyncRunner(self.env)

    def test_timer_fires_with_goal_plus_not_ce_handler(self):
        """Timer fires when the goal handler rule uses goal + not CE."""

        # Use goal + not CE instead of bare goal() for the handler rule
        class HandleTimerGoalWithNot(Rule):
            goal(TimerEvent(kind=k, name=n, seconds=s))
            ~TimerEvent(kind=k, name=n, seconds=s)

        class OnTimerFired(Rule):
            te = TimerEvent(
                kind=Symbol("after"), name=Symbol("gn-test"), seconds=0.05)
            asserts(TimerResult(msg=Symbol("goal-not-done")))

        self.env.define(TimerResult)
        self.env.define(HandleTimerGoalWithNot)
        self.env.define(OnTimerFired)
        self.env.reset()

        start = time.time()
        asyncio.run(self.runner.run())
        elapsed = time.time() - start

        self.assertGreaterEqual(elapsed, 0.04)
        rname = TimerResult.__clipspyx_dsl__.name
        results = [f for f in self.env.find_template(rname).facts()]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['msg'], Symbol('goal-not-done'))

    def test_periodic_timer_with_goal_plus_not_ce_handler(self):
        """Periodic timer fires multiple times with goal + not CE handler."""

        class BeatLogGN(Template):
            n: int

        class HandleTimerGoalWithNot(Rule):
            goal(TimerEvent(kind=k, name=n, seconds=s))
            ~TimerEvent(kind=k, name=n, seconds=s)

        class OnBeat(Rule):
            te = TimerEvent(
                kind=Symbol("every"), name=Symbol("gn-beat"),
                seconds=0.05, count=c)
            asserts(BeatLogGN(n=c))

        self.env.define(BeatLogGN)
        self.env.define(HandleTimerGoalWithNot)
        self.env.define(OnBeat)
        self.env.reset()

        asyncio.run(self.runner.run(max_cycles=4))

        blname = BeatLogGN.__clipspyx_dsl__.name
        logs = sorted(
            [f for f in self.env.find_template(blname).facts()],
            key=lambda f: int(f['n']))
        self.assertGreaterEqual(len(logs), 3)
        self.assertEqual(int(logs[0]['n']), 0)
        self.assertEqual(int(logs[1]['n']), 1)
        self.assertEqual(int(logs[2]['n']), 2)


# ---------------------------------------------------------------------------
# Goal cancellation via negation CE tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestGoalCancellationViaNegation(unittest.TestCase):
    """Prove that asserting a fact which falsifies a negation CE in the
    goal-generating rule retracts the goal and cancels the async handler.

    Models the "universal timeout" pattern: a timeout rule generates a
    timer-event goal while the test is unresolved.  When the test passes
    (TestPassed asserted), the negation ~TestPassed becomes false, CLIPS
    retracts the goal, and the runner cancels the sleeping timer — returning
    well before the timer would have expired.
    """

    def setUp(self):
        self.env = Environment()
        self.runner = AsyncRunner(self.env)

    def test_timeout_fires_when_unresolved(self):
        """Without external resolution the timer fires and the timeout
        rule asserts TestFailure after the full delay."""

        class TestDecl(Template):
            name: Symbol
            timeout: float

        class RunTest(Template):
            name: Symbol

        class TestPassed(Template):
            name: Symbol

        class TestFailure(Template):
            name: Symbol
            detail: Symbol

        class TimeoutRule(Rule):
            __salience__ = -9000
            t = TestDecl(name=n, timeout=timeout)
            rt = RunTest(name=n)
            ~TestPassed(name=n)
            ~TestFailure(name=n)
            te = TimerEvent(kind=Symbol("after"), name=n, seconds=timeout)
            asserts(TestFailure(name=n, detail=Symbol("timeout")))
            retracts(rt)

        self.env.define(TestDecl)
        self.env.define(RunTest)
        self.env.define(TestPassed)
        self.env.define(TestFailure)
        self.env.define(_make_goal_handler())
        self.env.define(TimeoutRule)

        tname = TestDecl.__clipspyx_dsl__.name
        rname = RunTest.__clipspyx_dsl__.name
        fname = TestFailure.__clipspyx_dsl__.name

        self.env.find_template(tname).assert_fact(
            name=Symbol("t1"), timeout=0.15)
        self.env.find_template(rname).assert_fact(name=Symbol("t1"))

        async def drive():
            start = time.monotonic()
            await self.runner.run()
            elapsed = time.monotonic() - start

            # Timer must have actually waited
            self.assertGreaterEqual(elapsed, 0.10)

            # TestFailure asserted by the timeout rule
            failures = list(self.env.find_template(fname).facts())
            self.assertEqual(len(failures), 1)
            self.assertEqual(str(failures[0]['detail']), 'timeout')

            # RunTest retracted
            remaining = list(self.env.find_template(rname).facts())
            self.assertEqual(len(remaining), 0)

            await self.runner.close()

        asyncio.run(drive())

    def test_early_pass_cancels_timer(self):
        """Asserting TestPassed mid-timer retracts the goal and cancels the
        handler — the runner returns in a fraction of the timeout duration."""

        class TestDecl(Template):
            name: Symbol
            timeout: float

        class RunTest(Template):
            name: Symbol

        class TestPassed(Template):
            name: Symbol

        class TestFailure(Template):
            name: Symbol
            detail: Symbol

        class TimeoutRule(Rule):
            __salience__ = -9000
            t = TestDecl(name=n, timeout=timeout)
            rt = RunTest(name=n)
            ~TestPassed(name=n)
            ~TestFailure(name=n)
            te = TimerEvent(kind=Symbol("after"), name=n, seconds=timeout)
            asserts(TestFailure(name=n, detail=Symbol("timeout")))
            retracts(rt)

        self.env.define(TestDecl)
        self.env.define(RunTest)
        self.env.define(TestPassed)
        self.env.define(TestFailure)
        self.env.define(_make_goal_handler())
        self.env.define(TimeoutRule)

        tname = TestDecl.__clipspyx_dsl__.name
        rname = RunTest.__clipspyx_dsl__.name
        pname = TestPassed.__clipspyx_dsl__.name
        fname = TestFailure.__clipspyx_dsl__.name

        self.env.find_template(tname).assert_fact(
            name=Symbol("t2"), timeout=2.0)
        self.env.find_template(rname).assert_fact(name=Symbol("t2"))

        runner = self.runner

        async def drive():
            async def pass_test():
                await asyncio.sleep(0.15)
                self.env.find_template(pname).assert_fact(name=Symbol("t2"))
                runner.wake()

            asyncio.create_task(pass_test())

            start = time.monotonic()
            await runner.run()
            elapsed = time.monotonic() - start

            # Must return quickly — well under the 2s timeout
            self.assertLess(elapsed, 1.0)

            # No timeout failure
            failures = list(self.env.find_template(fname).facts())
            self.assertEqual(len(failures), 0)

            # TestPassed was asserted
            passed = list(self.env.find_template(pname).facts())
            self.assertEqual(len(passed), 1)

            # No lingering goals
            goals = list(self.env.goals())
            self.assertEqual(len(goals), 0)

            await runner.close()

        asyncio.run(drive())


# ---------------------------------------------------------------------------
# Multi-timer dispatch tests (persistent task keying bug)
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestMultiTimerDispatch(unittest.TestCase):
    """Prove multiple timer-event goals dispatch concurrently.

    The bug: _persistent_tasks was keyed by template name, so one
    generator-backed handler (every timer) blocked all other timer-event
    goals from being dispatched.
    """

    def setUp(self):
        self.env = Environment()
        self.runner = AsyncRunner(self.env)

    def test_two_generator_goals_same_template(self):
        """Two goals for a custom generator handler both dispatch.

        Uses a custom template with a generator handler (not the built-in
        timer handler) so BOTH goals produce generator tasks. With the old
        template-name keying, whichever goal was dispatched first would
        block the second -- regardless of CLIPS goal ordering.
        """

        class Sensor(Template):
            tag: Symbol

        class SensorResult(Template):
            tag: Symbol

        class HandleSensorGoal(Rule):
            goal(Sensor(tag=t))

        class NeedAlpha(Rule):
            s = Sensor(tag=Symbol("alpha"))
            asserts(SensorResult(tag=Symbol("alpha")))

        class NeedBeta(Rule):
            s = Sensor(tag=Symbol("beta"))
            asserts(SensorResult(tag=Symbol("beta")))

        dispatched_tags = []

        async def sensor_gen(goal, env):
            tag = str(goal['tag'])
            dispatched_tags.append(tag)
            await asyncio.sleep(0.01)
            Sensor(__env__=env, tag=Symbol(tag))
            yield

        self.env.define(Sensor)
        self.env.define(SensorResult)
        self.env.define(HandleSensorGoal)
        self.env.define(NeedAlpha)
        self.env.define(NeedBeta)
        self.runner.register_handler(Sensor, sensor_gen)
        self.env.reset()

        asyncio.run(self.runner.run())

        # Both goals must have been dispatched (order doesn't matter)
        self.assertEqual(sorted(dispatched_tags), ['alpha', 'beta'])

        srname = SensorResult.__clipspyx_dsl__.name
        results = {str(f['tag'])
                   for f in self.env.find_template(srname).facts()}
        self.assertEqual(results, {'alpha', 'beta'})

    def test_two_every_timers_concurrent(self):
        """Two independent every-timers must both produce beats."""

        class BeatA(Template):
            n: int

        class BeatB(Template):
            n: int

        class HandleTimerGoal(Rule):
            goal(TimerEvent(kind=k, name=n, seconds=s))

        class OnBeatA(Rule):
            te = TimerEvent(
                kind=Symbol("every"), name=Symbol("beat-a"),
                seconds=0.03, count=c)
            asserts(BeatA(n=c))

        class OnBeatB(Rule):
            te = TimerEvent(
                kind=Symbol("every"), name=Symbol("beat-b"),
                seconds=0.03, count=c)
            asserts(BeatB(n=c))

        self.env.define(BeatA)
        self.env.define(BeatB)
        self.env.define(HandleTimerGoal)
        self.env.define(OnBeatA)
        self.env.define(OnBeatB)
        self.env.reset()

        asyncio.run(self.runner.run(max_cycles=5))

        aname = BeatA.__clipspyx_dsl__.name
        bname = BeatB.__clipspyx_dsl__.name
        a_facts = list(self.env.find_template(aname).facts())
        b_facts = list(self.env.find_template(bname).facts())
        self.assertGreaterEqual(len(a_facts), 1, "beat-a never fired")
        self.assertGreaterEqual(len(b_facts), 1, "beat-b never fired")

    def test_after_timer_does_not_block_every_timer(self):
        """An after-timer must not prevent an every-timer from firing."""

        class EveryResult2(Template):
            n: int

        class AfterResult2(Template):
            msg: Symbol

        class HandleTimerGoal(Rule):
            goal(TimerEvent(kind=k, name=n, seconds=s))

        class OnAfter(Rule):
            te = TimerEvent(
                kind=Symbol("after"), name=Symbol("first"),
                seconds=0.02)
            asserts(AfterResult2(msg=Symbol("done")))

        class OnEvery(Rule):
            te = TimerEvent(
                kind=Symbol("every"), name=Symbol("second"),
                seconds=0.03, count=c)
            asserts(EveryResult2(n=c))

        self.env.define(EveryResult2)
        self.env.define(AfterResult2)
        self.env.define(HandleTimerGoal)
        self.env.define(OnAfter)
        self.env.define(OnEvery)
        self.env.reset()

        asyncio.run(self.runner.run(max_cycles=5))

        arname = AfterResult2.__clipspyx_dsl__.name
        after_facts = list(self.env.find_template(arname).facts())
        self.assertEqual(len(after_facts), 1)

        ername = EveryResult2.__clipspyx_dsl__.name
        every_facts = list(self.env.find_template(ername).facts())
        self.assertGreaterEqual(len(every_facts), 1, "every-timer never fired")


# ---------------------------------------------------------------------------
# Starvation resistance tests (orphaned pending tasks)
# ---------------------------------------------------------------------------

@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestHandlerStarvationResistance(unittest.TestCase):
    """Prove that a persistent generator handler does not starve a coroutine
    handler whose goal is repeatedly retracted and re-created.

    Models the scenario: a fast generator toggles a control fact, causing the
    coroutine handler's goal-generating rule to deactivate and re-activate.
    Without the orphaned-pending fix, the coroutine handler would be cancelled
    on every goal retraction and never complete.
    """

    def setUp(self):
        self.env = Environment()
        self.runner = AsyncRunner(self.env)

    def test_coroutine_completes_despite_goal_toggling(self):
        """Coroutine handler completes even when its goal is retracted
        and re-created by generator-triggered rule changes."""

        class Pulse(Template):
            n: int

        class PulseResult(Template):
            n: int

        class SlowOp(Template):
            key: Symbol

        class SlowResult(Template):
            key: Symbol

        # Goal-generating rules
        class HandlePulseGoal(Rule):
            goal(Pulse(n=v))

        class HandleSlowGoal(Rule):
            goal(SlowOp(key=k))

        # The slow rule needs SlowOp -- backward chain generates the goal.
        class OnSlowDone(Rule):
            s = SlowOp(key=k)
            asserts(SlowResult(key=k))

        # The pulse rule consumes pulse facts.
        class OnPulse(Rule):
            p = Pulse(n=v)
            asserts(PulseResult(n=v))

        handler_completions = []

        async def pulse_gen(goal, env):
            """Fast generator: yields rapidly, simulating a WebSocket feed."""
            for i in range(5):
                await asyncio.sleep(0.01)
                Pulse(__env__=env, n=i)
                yield

        async def slow_handler(goal, env):
            """Slow coroutine: simulates an HTTP request."""
            await asyncio.sleep(0.05)
            SlowOp(__env__=env, key=Symbol("done"))
            handler_completions.append(True)

        self.env.define(Pulse)
        self.env.define(PulseResult)
        self.env.define(SlowOp)
        self.env.define(SlowResult)
        self.env.define(HandlePulseGoal)
        self.env.define(HandleSlowGoal)
        self.env.define(OnPulse)
        self.env.define(OnSlowDone)
        self.runner.register_handler(Pulse, pulse_gen)
        self.runner.register_handler(SlowOp, slow_handler)
        self.env.reset()

        async def drive():
            result = await self.runner.run(max_cycles=50)
            await self.runner.close()
            return result

        asyncio.run(drive())

        # The slow handler must have completed at least once
        self.assertGreaterEqual(len(handler_completions), 1,
                                "Slow handler was starved by generator")

        # SlowResult must have been asserted
        srname = SlowResult.__clipspyx_dsl__.name
        results = list(self.env.find_template(srname).facts())
        self.assertGreaterEqual(len(results), 1,
                                "SlowResult never asserted")

    def test_orphaned_task_cleaned_on_close(self):
        """Orphaned pending tasks are cleaned up when the runner is closed."""
        async def drive():
            # Just run and close -- verify _orphaned_pending is empty
            await self.runner.run(max_cycles=1)
            await self.runner.close()
            self.assertEqual(len(self.runner._orphaned_pending), 0)

        asyncio.run(drive())

    def test_external_async_task_executes_during_run(self):
        """asyncio.create_task() tasks created outside the runner execute
        during runner.run(), not only after it returns.

        Models the schedule_async pattern: a rule action creates a plain
        asyncio task (not a goal handler) that must run while the runner
        is active.  Without the event loop yield in _wait_for_handlers,
        these tasks would be starved by a fast persistent generator.
        """

        class Pulse(Template):
            n: int

        class HandlePulseGoal(Rule):
            goal(Pulse(n=v))

        class PulseResult(Template):
            n: int

        class OnPulse(Rule):
            p = Pulse(n=v)
            asserts(PulseResult(n=v))

        async def pulse_gen(goal, env):
            """Fast generator: yields rapidly."""
            for i in range(5):
                await asyncio.sleep(0.01)
                Pulse(__env__=env, n=i)
                yield

        self.env.define(Pulse)
        self.env.define(PulseResult)
        self.env.define(HandlePulseGoal)
        self.env.define(OnPulse)
        self.runner.register_handler(Pulse, pulse_gen)
        self.env.reset()

        external_executed = []

        async def drive():
            async def external_task():
                """Simulates a schedule_async coroutine."""
                # Use sleep(0) to avoid Windows timer resolution issues
                # (15.6ms granularity).  The point is to verify external
                # tasks get event loop time, not to test real-time delays.
                await asyncio.sleep(0)
                external_executed.append("done")

            # Create external task BEFORE run -- it must execute DURING run
            asyncio.create_task(external_task())
            await self.runner.run(max_cycles=20)
            await self.runner.close()

        asyncio.run(drive())

        self.assertEqual(external_executed, ["done"],
                         "External async task did not execute during run()")

    def test_external_task_runs_with_zero_sleep_generator(self):
        """External asyncio task completes even when the persistent generator
        yields without sleeping (simulating buffered WebSocket messages).

        This is the hardest case for the event loop: the generator's
        __anext__() returns immediately (no suspension), so _gen_step can
        complete within a single event loop callback.  Without the
        sleep(0) in _run_loop, asyncio.wait returns instantly and
        external tasks are starved.
        """

        class Stream(Template):
            seq: int

        class HandleStreamGoal(Rule):
            goal(Stream(seq=n))

        class StreamResult(Template):
            seq: int

        class OnStream(Rule):
            s = Stream(seq=n)
            asserts(StreamResult(seq=n))

        messages_yielded = []

        async def stream_gen(goal, env):
            """Generator that yields immediately (no sleep) -- simulates
            a WebSocket with buffered messages."""
            for i in range(10):
                Stream(__env__=env, seq=i)
                messages_yielded.append(i)
                yield
                # No sleep between yields: __anext__() returns instantly
                # when resumed.

        self.env.define(Stream)
        self.env.define(StreamResult)
        self.env.define(HandleStreamGoal)
        self.env.define(OnStream)
        self.runner.register_handler(Stream, stream_gen)
        self.env.reset()

        external_steps = []

        async def drive():
            async def multi_step_task():
                """External task that needs multiple event loop iterations.
                Simulates a schedule_async coroutine (e.g. HTTP request)."""
                external_steps.append("started")
                await asyncio.sleep(0)  # 1st yield
                external_steps.append("step1")
                await asyncio.sleep(0)  # 2nd yield
                external_steps.append("step2")
                await asyncio.sleep(0)  # 3rd yield
                external_steps.append("completed")

            asyncio.create_task(multi_step_task())
            await self.runner.run(max_cycles=30)
            await self.runner.close()

        asyncio.run(drive())

        # Generator must have yielded (proves it was active)
        self.assertGreater(len(messages_yielded), 0,
                           "Generator never yielded")

        # External task must have completed ALL steps during run()
        self.assertEqual(
            external_steps,
            ["started", "step1", "step2", "completed"],
            f"External task starved by zero-sleep generator: {external_steps}")

    def test_runner_schedule_executes_during_run(self):
        """runner.schedule() tasks execute during run() and are included
        in the wait set.  This is the safe alternative to
        asyncio.get_event_loop().create_task() from CFFI callbacks."""

        class Pulse(Template):
            n: int

        class HandlePulseGoal(Rule):
            goal(Pulse(n=v))

        class PulseResult(Template):
            n: int

        class OnPulse(Rule):
            p = Pulse(n=v)
            asserts(PulseResult(n=v))

        async def pulse_gen(goal, env):
            for i in range(5):
                Pulse(__env__=env, n=i)
                yield

        self.env.define(Pulse)
        self.env.define(PulseResult)
        self.env.define(HandlePulseGoal)
        self.env.define(OnPulse)
        self.runner.register_handler(Pulse, pulse_gen)
        self.env.reset()

        schedule_results = []

        async def drive():
            async def scheduled_work():
                await asyncio.sleep(0)
                schedule_results.append("step1")
                await asyncio.sleep(0)
                schedule_results.append("done")

            self.runner.schedule(scheduled_work())
            await self.runner.run(max_cycles=20)
            await self.runner.close()

        asyncio.run(drive())

        self.assertEqual(schedule_results, ["step1", "done"],
                         "runner.schedule() task did not complete during run()")

    def test_persistent_generator_not_abandoned_across_cycles(self):
        """Persistent generator survives when its gen_step completes outside
        asyncio.wait (e.g. during the end-of-loop sleep(0)).

        Without the fix, _prune_done_persistent would remove the done
        gen_step without closing the generator or creating a replacement.
        _dispatch_goals would create a brand new handler each cycle,
        abandoning the old generator (no finally, no aclose).
        """

        class Feed(Template):
            seq: int

        class HandleFeedGoal(Rule):
            goal(Feed(seq=n))

        class FeedResult(Template):
            seq: int

        class OnFeed(Rule):
            f = Feed(seq=n)
            asserts(FeedResult(seq=n))

        lifecycle = []

        async def feed_gen(goal, env):
            """Generator that tracks its lifecycle."""
            lifecycle.append("started")
            try:
                for i in range(5):
                    Feed(__env__=env, seq=i)
                    lifecycle.append(f"yield-{i}")
                    yield
                    # No sleep: gen_step may complete during end-of-loop
                    # sleep(0), outside asyncio.wait.
            finally:
                lifecycle.append("finally")

        self.env.define(Feed)
        self.env.define(FeedResult)
        self.env.define(HandleFeedGoal)
        self.env.define(OnFeed)
        self.runner.register_handler(Feed, feed_gen)
        self.env.reset()

        async def drive():
            await self.runner.run(max_cycles=20)
            await self.runner.close()

        asyncio.run(drive())

        # Generator must have started exactly ONCE (not re-dispatched)
        self.assertEqual(lifecycle.count("started"), 1,
                         f"Generator re-dispatched: {lifecycle}")

        # Must have yielded multiple times (survived across cycles)
        yields = [e for e in lifecycle if e.startswith("yield-")]
        self.assertGreaterEqual(len(yields), 3,
                                f"Generator didn't survive: {lifecycle}")

        # finally block must have run (on close or exhaustion)
        self.assertIn("finally", lifecycle,
                      f"Generator abandoned without finally: {lifecycle}")

    def test_scheduled_task_blocks_completion(self):
        """runner.run() does not return 'completed' while a scheduled task
        is still running, even if no goals or handlers remain."""

        steps = []

        async def drive():
            async def slow_task():
                steps.append("started")
                # Multiple yields to outlast any handler activity
                for i in range(5):
                    await asyncio.sleep(0)
                steps.append("done")

            self.runner.schedule(slow_task())
            # No handlers registered — without _scheduled_tasks blocking
            # completion, the runner would return "completed" immediately.
            result = await self.runner.run()
            steps.append(f"run:{result}")
            await self.runner.close()

        asyncio.run(drive())

        # Task must complete BEFORE run() returns
        self.assertEqual(steps, ["started", "done", "run:completed"],
                         f"Scheduled task didn't block completion: {steps}")


if __name__ == '__main__':
    unittest.main()
