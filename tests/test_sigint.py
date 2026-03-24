"""Tests for the opt-in SIGINT (Ctrl-C) handler."""

import os
import signal

import clipspyx


def _make_env_with_counting_rule(n=100):
    """Return an env with a rule that fires n times."""
    env = clipspyx.Environment()
    env.build("(deffacts start (counter 0))")
    env.build(
        "(defrule bump"
        "  ?f <- (counter ?c&:(< ?c %d))"
        "  =>"
        "  (retract ?f)"
        "  (assert (counter (+ ?c 1))))" % n
    )
    env.reset()
    return env


class TestLifecycle:
    """Enable/disable lifecycle management."""

    def test_enable_disable(self):
        env = clipspyx.Environment()
        env.enable_sigint_handler()
        assert env._sigint_state is not None
        env.disable_sigint_handler()
        assert env._sigint_state is None

    def test_disable_restores_original_handler(self):
        original = signal.getsignal(signal.SIGINT)
        env = clipspyx.Environment()
        env.enable_sigint_handler()
        assert signal.getsignal(signal.SIGINT) is not original
        env.disable_sigint_handler()
        assert signal.getsignal(signal.SIGINT) is original

    def test_double_disable_is_safe(self):
        env = clipspyx.Environment()
        env.enable_sigint_handler()
        env.disable_sigint_handler()
        env.disable_sigint_handler()  # should not raise


class TestInterrupt:
    """SIGINT during run() raises KeyboardInterrupt."""

    def test_sigint_raises_keyboard_interrupt(self):
        env = _make_env_with_counting_rule(100)
        # Register a UDF that sends SIGINT on first invocation.
        sent = [False]

        def send_sigint():
            if not sent[0]:
                sent[0] = True
                os.kill(os.getpid(), signal.SIGINT)

        env.define_function(send_sigint)
        env.build(
            "(defrule trigger (declare (salience 10))"
            "  (counter ?c&:(= ?c 1))"
            "  =>"
            "  (send_sigint))"
        )
        env.enable_sigint_handler()
        raised = False
        try:
            env.run()
        except KeyboardInterrupt:
            raised = True
        finally:
            env.disable_sigint_handler()
        assert raised, "KeyboardInterrupt was not raised"

    def test_env_reusable_after_interrupt(self):
        env = _make_env_with_counting_rule(100)
        sent = [False]

        def send_sigint():
            if not sent[0]:
                sent[0] = True
                os.kill(os.getpid(), signal.SIGINT)

        env.define_function(send_sigint)
        env.build(
            "(defrule trigger (declare (salience 10))"
            "  (counter ?c&:(= ?c 1))"
            "  =>"
            "  (send_sigint))"
        )
        env.reset()
        env.enable_sigint_handler()
        try:
            try:
                env.run()
            except KeyboardInterrupt:
                pass

            # Environment should be usable again.
            # Don't reset sent[0]: the trigger rule will fire again on
            # counter=1, but since sent[0] is True the UDF is a no-op.
            env.reset()
            fired = env.run()
            assert fired > 0
        finally:
            env.disable_sigint_handler()


class TestContextManager:
    """Context manager form."""

    def test_context_manager_enables_and_disables(self):
        env = clipspyx.Environment()
        original = signal.getsignal(signal.SIGINT)
        with env.sigint_handler():
            assert env._sigint_state is not None
        assert env._sigint_state is None
        assert signal.getsignal(signal.SIGINT) is original

    def test_context_manager_with_interrupt(self):
        env = _make_env_with_counting_rule(100)
        sent = [False]

        def send_sigint():
            if not sent[0]:
                sent[0] = True
                os.kill(os.getpid(), signal.SIGINT)

        env.define_function(send_sigint)
        env.build(
            "(defrule trigger (declare (salience 10))"
            "  (counter ?c&:(= ?c 1))"
            "  =>"
            "  (send_sigint))"
        )
        raised = False
        with env.sigint_handler():
            try:
                env.run()
            except KeyboardInterrupt:
                raised = True
        assert raised, "KeyboardInterrupt was not raised"
        # Handler should be cleaned up.
        assert env._sigint_state is None


class TestMultipleEnvironments:
    """Multiple environments with SIGINT enabled."""

    def test_both_environments_interrupted(self):
        from clipspyx.sigint import _active_states

        env1 = clipspyx.Environment()
        env2 = clipspyx.Environment()
        env1.enable_sigint_handler()
        env2.enable_sigint_handler()
        try:
            assert len(_active_states) == 2
            # Simulate SIGINT.
            os.kill(os.getpid(), signal.SIGINT)
            assert env1._sigint_state.interrupted
            assert env2._sigint_state.interrupted
        finally:
            env1.disable_sigint_handler()
            env2.disable_sigint_handler()
