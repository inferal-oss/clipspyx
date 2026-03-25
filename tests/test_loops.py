"""Tests for rule loop detection via transitive closure of RuleFiring provenance."""

import pytest

from clipspyx import Environment, RuleLoopError
from clipspyx.dsl import Template, Rule
from clipspyx.tracing import enable_tracing
from clipspyx.loops import enable_loop_detection


# ---------------------------------------------------------------------------
# Helper templates
# ---------------------------------------------------------------------------

class Ping(Template):
    value: int


class Pong(Template):
    value: int


class LoopAlpha(Template):
    value: int


class LoopBeta(Template):
    value: int


class LoopGamma(Template):
    value: int


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCycle2WithThreshold:
    """Ping-Pong rules forming a cycle of length 2."""

    def test_raises_after_threshold(self):
        """Cycle A->B->A should raise RuleLoopError after threshold firings."""
        env = Environment()
        enable_tracing(env)
        enable_loop_detection(env, threshold=5)

        class PingRule(Rule):
            p = Ping(value=v)
            retracts(p)
            asserts(Pong(value=v + 1))

        class PongRule(Rule):
            p = Pong(value=v)
            retracts(p)
            asserts(Ping(value=v + 1))

        for cls in (Ping, Pong, PingRule, PongRule):
            env.define(cls)

        tpl = env.find_template(Ping.__clipspyx_dsl__.name)
        tpl.assert_fact(value=0)

        with pytest.raises(RuleLoopError, match="Cycle involving rule"):
            env.run()

    def test_threshold_respected(self):
        """Rules should fire at least threshold times before error."""
        env = Environment()
        enable_tracing(env)
        enable_loop_detection(env, threshold=3)

        class PingRule2(Rule):
            p = Ping(value=v)
            retracts(p)
            asserts(Pong(value=v + 1))

        class PongRule2(Rule):
            p = Pong(value=v)
            retracts(p)
            asserts(Ping(value=v + 1))

        for cls in (Ping, Pong, PingRule2, PongRule2):
            env.define(cls)

        tpl = env.find_template(Ping.__clipspyx_dsl__.name)
        tpl.assert_fact(value=0)

        with pytest.raises(RuleLoopError):
            env.run()


class TestCycle3:
    """Three rules forming A -> B -> C -> A."""

    def test_cycle_3_detected(self):
        """Transitive closure should detect cycles longer than 2."""
        env = Environment()
        enable_tracing(env)
        enable_loop_detection(env, threshold=3)

        class AlphaRule(Rule):
            a = LoopAlpha(value=v)
            retracts(a)
            asserts(LoopBeta(value=v + 1))

        class BetaRule(Rule):
            b = LoopBeta(value=v)
            retracts(b)
            asserts(LoopGamma(value=v + 1))

        class GammaRule(Rule):
            g = LoopGamma(value=v)
            retracts(g)
            asserts(LoopAlpha(value=v + 1))

        for cls in (LoopAlpha, LoopBeta, LoopGamma, AlphaRule, BetaRule, GammaRule):
            env.define(cls)

        tpl = env.find_template(LoopAlpha.__clipspyx_dsl__.name)
        tpl.assert_fact(value=0)

        with pytest.raises(RuleLoopError, match="Cycle involving rule"):
            env.run()


class TestNoFalsePositive:
    """Non-looping rules should complete normally."""

    def test_sequential_rules(self):
        """Rules that fire once each without cycling should not trigger detection."""
        env = Environment()
        enable_tracing(env)
        enable_loop_detection(env, threshold=3)

        class Step1(Template):
            done: int

        class Step2(Template):
            done: int

        class DoStep1(Rule):
            s = Step1(done=0)
            retracts(s)
            asserts(Step2(done=1))

        class DoStep2(Rule):
            s = Step2(done=1)
            retracts(s)

        for cls in (Step1, Step2, DoStep1, DoStep2):
            env.define(cls)

        tpl = env.find_template(Step1.__clipspyx_dsl__.name)
        tpl.assert_fact(done=0)

        # Should complete without error
        fired = env.run()
        assert fired >= 2


class TestThresholdOne:
    """Threshold=1 should detect on first cycle repetition."""

    def test_threshold_1(self):
        """With threshold=1, error should be raised very quickly."""
        env = Environment()
        enable_tracing(env)
        enable_loop_detection(env, threshold=1)

        class PingRule3(Rule):
            p = Ping(value=v)
            retracts(p)
            asserts(Pong(value=v + 1))

        class PongRule3(Rule):
            p = Pong(value=v)
            retracts(p)
            asserts(Ping(value=v + 1))

        for cls in (Ping, Pong, PingRule3, PongRule3):
            env.define(cls)

        tpl = env.find_template(Ping.__clipspyx_dsl__.name)
        tpl.assert_fact(value=0)

        with pytest.raises(RuleLoopError):
            env.run()


class TestDisable:
    """disable_loop_detection should stop detection."""

    def test_disable_allows_cycle(self):
        """After disabling, a cycle should run without raising."""
        from clipspyx.loops import disable_loop_detection

        env = Environment()
        enable_tracing(env)
        enable_loop_detection(env, threshold=2)

        class PingRule4(Rule):
            p = Ping(value=v)
            retracts(p)
            asserts(Pong(value=v + 1))

        class PongRule4(Rule):
            p = Pong(value=v)
            retracts(p)
            asserts(Ping(value=v + 1))

        for cls in (Ping, Pong, PingRule4, PongRule4):
            env.define(cls)

        disable_loop_detection(env)

        tpl = env.find_template(Ping.__clipspyx_dsl__.name)
        tpl.assert_fact(value=0)

        # Should complete (up to limit) without error
        fired = env.run(limit=20)
        assert fired == 20


class TestEnableRequiresTracing:
    """enable_loop_detection should fail without tracing."""

    def test_raises_without_tracing(self):
        env = Environment()
        with pytest.raises(RuntimeError, match="Tracing must be enabled"):
            enable_loop_detection(env)
