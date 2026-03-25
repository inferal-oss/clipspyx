"""Tests for auto-wake: fact operations automatically wake the AsyncRunner.

All tests require CLIPS 7.0+ (backward chaining goals / AsyncRunner).
"""

import asyncio
import unittest

import clipspyx
from clipspyx import Environment, Symbol
from clipspyx.dsl import Template, Rule
from clipspyx.async_goals import AsyncRunner

CLIPS_70 = clipspyx.CLIPS_MAJOR >= 7


class AWPing(Template):
    tag: Symbol


class AWPong(Template):
    tag: Symbol


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAutoWakeAssert(unittest.TestCase):
    """Auto-wake when facts are asserted from external async code."""

    def setUp(self):
        self.env = Environment()

    def _setup_ping_pong(self, runner):
        """Set up Ping→Pong goal chain with a blocking handler."""

        class HandlePingGoal(Rule):
            goal(AWPing(tag=t))

        class OnPing(Rule):
            p = AWPing(tag=t)
            asserts(AWPong(tag=t))

        async def blocking_handler(goal, env):
            await asyncio.sleep(300)

        self.env.define(AWPing)
        self.env.define(AWPong)
        self.env.define(HandlePingGoal)
        self.env.define(OnPing)
        runner.register_handler(AWPing, blocking_handler)

    def test_assert_fact_wakes_runner(self):
        """Template.assert_fact() from external task auto-wakes the runner."""

        runner = AsyncRunner(self.env)
        self._setup_ping_pong(runner)
        self.env.reset()

        async def drive():
            async def inject():
                await asyncio.sleep(0.05)
                tpl = self.env.find_template(AWPing.__clipspyx_dsl__.name)
                tpl.assert_fact(tag=Symbol("hello"))

            asyncio.create_task(inject())
            await asyncio.wait_for(runner.run(max_cycles=3), timeout=2.0)
            await runner.close()

            pongs = list(self.env.find_template(
                AWPong.__clipspyx_dsl__.name).facts())
            self.assertEqual(len(pongs), 1)
            self.assertEqual(str(pongs[0]['tag']), 'hello')

        asyncio.run(drive())

    def test_assert_string_wakes_runner(self):
        """Facts.assert_string() from external task auto-wakes the runner."""

        runner = AsyncRunner(self.env)
        self._setup_ping_pong(runner)
        self.env.reset()

        async def drive():
            async def inject():
                await asyncio.sleep(0.05)
                name = AWPing.__clipspyx_dsl__.name
                self.env.assert_string(f'({name} (tag world))')

            asyncio.create_task(inject())
            await asyncio.wait_for(runner.run(max_cycles=3), timeout=2.0)
            await runner.close()

            pongs = list(self.env.find_template(
                AWPong.__clipspyx_dsl__.name).facts())
            self.assertEqual(len(pongs), 1)
            self.assertEqual(str(pongs[0]['tag']), 'world')

        asyncio.run(drive())


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAutoWakeRetract(unittest.TestCase):
    """Auto-wake when facts are retracted from external async code."""

    def setUp(self):
        self.env = Environment()

    def test_retract_wakes_runner(self):
        """Fact.retract() from external task auto-wakes the runner."""

        class Blocker(Template):
            tag: Symbol

        class Done(Template):
            tag: Symbol

        class HandleBlockerGoal(Rule):
            goal(Blocker(tag=t))

        class OnBlockerRemoved(Rule):
            """Fires when no Blocker facts exist."""
            not_cond = ~Blocker(tag=t)
            asserts(Done(tag=Symbol("ok")))

        async def blocking_handler(goal, env):
            await asyncio.sleep(300)

        self.env.define(Blocker)
        self.env.define(Done)
        self.env.define(HandleBlockerGoal)
        self.env.define(OnBlockerRemoved)
        self.env.reset()

        runner = AsyncRunner(self.env)
        runner.register_handler(Blocker, blocking_handler)

        # Assert a blocker - prevents OnBlockerRemoved from firing
        blocker = Blocker(__env__=self.env, tag=Symbol("x"))

        async def drive():
            async def retract_later():
                await asyncio.sleep(0.05)
                blocker.retract()

            asyncio.create_task(retract_later())
            await asyncio.wait_for(runner.run(max_cycles=4), timeout=2.0)
            await runner.close()

            done = list(self.env.find_template(
                Done.__clipspyx_dsl__.name).facts())
            self.assertGreaterEqual(len(done), 1)

        asyncio.run(drive())


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAutoWakeModify(unittest.TestCase):
    """Auto-wake when facts are modified from external async code."""

    def setUp(self):
        self.env = Environment()

    def test_modify_wakes_runner(self):
        """TemplateFact.modify_slots() from external task auto-wakes the runner."""

        class Status(Template):
            state: Symbol

        class Ready(Template):
            tag: Symbol

        class HandleStatusGoal(Rule):
            goal(Status(state=s))

        class OnReady(Rule):
            st = Status(state=Symbol("ready"))
            asserts(Ready(tag=Symbol("go")))

        async def blocking_handler(goal, env):
            await asyncio.sleep(300)

        self.env.define(Status)
        self.env.define(Ready)
        self.env.define(HandleStatusGoal)
        self.env.define(OnReady)
        self.env.reset()

        runner = AsyncRunner(self.env)
        runner.register_handler(Status, blocking_handler)

        status = Status(__env__=self.env, state=Symbol("waiting"))

        async def drive():
            async def modify_later():
                await asyncio.sleep(0.05)
                status.modify_slots(state=Symbol("ready"))

            asyncio.create_task(modify_later())
            await asyncio.wait_for(runner.run(max_cycles=4), timeout=2.0)
            await runner.close()

            ready = list(self.env.find_template(
                Ready.__clipspyx_dsl__.name).facts())
            self.assertEqual(len(ready), 1)

        asyncio.run(drive())


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAutoWakeNoSpuriousCycles(unittest.TestCase):
    """Rule-execution assertions don't cause spurious cycles."""

    def setUp(self):
        self.env = Environment()

    def test_rule_assertions_complete_normally(self):
        """Rules asserting facts during env.run() don't trigger extra cycles.

        With _in_env_run suppression, the runner completes normally after
        processing the rule chain, without spinning on auto-wake.
        """

        class Input(Template):
            n: int

        class Output(Template):
            n: int

        self.env.define(Input)
        self.env.define(Output)
        imod = Input.__module__
        omod = Output.__module__
        self.env.build(f"""
            (defrule double
                ({imod}.Input (n ?n))
                =>
                (assert ({omod}.Output (n (* ?n 2)))))
        """)
        self.env.reset()

        runner = AsyncRunner(self.env)
        Input(__env__=self.env, n=5)

        async def drive():
            result = await asyncio.wait_for(
                runner.run(max_cycles=5), timeout=2.0)
            await runner.close()

            outputs = list(self.env.find_template(
                Output.__clipspyx_dsl__.name).facts())
            self.assertEqual(len(outputs), 1)
            self.assertEqual(int(outputs[0]['n']), 10)
            # Should complete, not spin to max_cycles
            self.assertEqual(result, "completed")

        asyncio.run(drive())


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAutoWakeAfterRunException(unittest.TestCase):
    """Auto-wake still works after env.run() raises an exception."""

    def setUp(self):
        self.env = Environment()

    def test_notify_works_after_env_run_raises(self):
        """If env.run() raises (e.g., RuleLoopError), _in_env_run must be
        cleared so fact operations between runs still trigger auto-wake.

        Without try/finally around the _in_env_run flag, the flag would
        stay True after the exception. Any fact asserted between the failed
        run() and the next run() would silently fail to set the wake event.
        """
        from clipspyx.tracing import enable_tracing
        from clipspyx.loops import enable_loop_detection

        enable_tracing(self.env)
        enable_loop_detection(self.env, threshold=3)

        # Two rules that form an infinite loop
        class LoopA(Template):
            n: int

        class LoopB(Template):
            n: int

        class AtoB(Rule):
            a = LoopA(n=v)
            retracts(a)
            asserts(LoopB(n=v))

        class BtoA(Rule):
            b = LoopB(n=v)
            retracts(b)
            asserts(LoopA(n=v))

        self.env.define(LoopA)
        self.env.define(LoopB)
        self.env.define(AtoB)
        self.env.define(BtoA)
        self.env.build('(deftemplate aw-signal (slot x))')
        self.env.reset()

        runner = AsyncRunner(self.env)

        async def drive():
            # Trigger the loop: env.run() inside runner will raise
            LoopA(__env__=self.env, n=0)
            with self.assertRaises(Exception):
                await runner.run(max_cycles=3)

            # Key check: _in_env_run must be False after the exception.
            # Without try/finally, env.run() raising leaves the flag True,
            # which would suppress all future _notify() calls.
            self.assertFalse(
                runner._in_env_run,
                "_in_env_run stuck True after env.run() exception; "
                "try/finally guard is missing or broken")

            await runner.close()

        asyncio.run(drive())


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAutoWakeManualStillWorks(unittest.TestCase):
    """Manual wake() still works alongside auto-wake."""

    def setUp(self):
        self.env = Environment()

    def test_manual_wake_still_works(self):
        """Explicit wake() call still interrupts _wait_for_handlers."""

        runner = AsyncRunner(self.env)
        self.env.reset()

        async def drive():
            runner.wake()
            result = await asyncio.wait_for(
                runner.run(max_cycles=2), timeout=2.0)
            self.assertEqual(result, "completed")
            await runner.close()

        asyncio.run(drive())


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAutoWakeNoRunnerNoop(unittest.TestCase):
    """Asserting facts without a runner is a no-op."""

    def setUp(self):
        self.env = Environment()

    def test_assert_without_runner(self):
        """Asserting facts without an active runner doesn't error."""
        self.env.build('(deftemplate foo (slot x))')
        self.env.reset()
        self.env.assert_string('(foo (x 1))')
        tpl = self.env.find_template('foo')
        tpl.assert_fact(x=2)
        facts = list(tpl.facts())
        self.assertEqual(len(facts), 2)


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestAutoWakeCleanup(unittest.TestCase):
    """After runner.close(), assertions don't attempt to wake."""

    def setUp(self):
        self.env = Environment()

    def test_assert_after_close(self):
        """Asserting after runner.close() doesn't error."""
        runner = AsyncRunner(self.env)
        self.env.build('(deftemplate bar (slot y))')
        self.env.reset()

        async def drive():
            await runner.close()
            self.env.assert_string('(bar (y 1))')

        asyncio.run(drive())
