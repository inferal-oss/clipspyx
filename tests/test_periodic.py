"""Tests for the periodic function public API."""

import clipspyx


class TestAddRemoveLifecycle:
    """Verify that periodic functions can be registered and removed."""

    def test_add_and_remove(self):
        env = clipspyx.Environment()
        calls = []
        env.add_periodic_function("test-tick", lambda e: calls.append(1))
        assert "test-tick" in env._periodic_functions
        env.remove_periodic_function("test-tick")
        assert "test-tick" not in env._periodic_functions

    def test_remove_nonexistent_is_safe(self):
        env = clipspyx.Environment()
        # Should not raise.
        env.remove_periodic_function("does-not-exist")


class TestCallbackFires:
    """Verify the callback is actually invoked during run()."""

    def test_callback_fires_during_run(self):
        env = clipspyx.Environment()
        calls = []
        env.add_periodic_function("counter", lambda e: calls.append(1))
        # Create a rule that fires a few times.
        env.build("(deffacts start (counter 0))")
        env.build(
            "(defrule bump"
            "  ?f <- (counter ?n&:(< ?n 5))"
            "  =>"
            "  (retract ?f)"
            "  (assert (counter (+ ?n 1))))"
        )
        env.reset()
        env.run()
        assert len(calls) > 0, "periodic callback was never invoked"
        env.remove_periodic_function("counter")

    def test_callback_receives_env(self):
        env = clipspyx.Environment()
        received = []
        env.add_periodic_function("env-check", lambda e: received.append(e))
        env.build("(deffacts start (go))")
        env.build("(defrule go (go) => (assert (done)))")
        env.reset()
        env.run()
        assert len(received) > 0
        assert received[0] is env
        env.remove_periodic_function("env-check")


class TestMultipleCallbacks:
    """Verify multiple periodic functions coexist."""

    def test_two_callbacks_both_fire(self):
        env = clipspyx.Environment()
        a_calls = []
        b_calls = []
        env.add_periodic_function("a", lambda e: a_calls.append(1))
        env.add_periodic_function("b", lambda e: b_calls.append(1))
        env.build("(deffacts start (counter 0))")
        env.build(
            "(defrule bump"
            "  ?f <- (counter ?n&:(< ?n 3))"
            "  =>"
            "  (retract ?f)"
            "  (assert (counter (+ ?n 1))))"
        )
        env.reset()
        env.run()
        assert len(a_calls) > 0
        assert len(b_calls) > 0
        env.remove_periodic_function("a")
        env.remove_periodic_function("b")

    def test_remove_one_other_still_fires(self):
        env = clipspyx.Environment()
        a_calls = []
        b_calls = []
        env.add_periodic_function("a", lambda e: a_calls.append(1))
        env.add_periodic_function("b", lambda e: b_calls.append(1))
        env.remove_periodic_function("a")
        env.build("(deffacts start (counter 0))")
        env.build(
            "(defrule bump"
            "  ?f <- (counter ?n&:(< ?n 3))"
            "  =>"
            "  (retract ?f)"
            "  (assert (counter (+ ?n 1))))"
        )
        env.reset()
        env.run()
        assert len(a_calls) == 0, "removed callback should not fire"
        assert len(b_calls) > 0, "remaining callback should still fire"
        env.remove_periodic_function("b")
