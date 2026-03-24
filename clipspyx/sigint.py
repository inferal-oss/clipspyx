"""Opt-in Ctrl-C (SIGINT) handling for CLIPS rule execution.

When enabled, installs a periodic callback (via :mod:`clipspyx.periodic`)
and a Python SIGINT handler.  On Ctrl-C the periodic callback calls
``SetHaltExecution`` / ``SetHaltRules``, causing the current ``Run()`` to
stop gracefully, and the ``run()`` wrapper raises ``KeyboardInterrupt``.

Usage::

    env.enable_sigint_handler()
    try:
        env.run()
    except KeyboardInterrupt:
        print("interrupted")
    finally:
        env.disable_sigint_handler()

Or with the context manager::

    with env.sigint_handler():
        env.run()
"""

import signal
from contextlib import contextmanager
from dataclasses import dataclass

from clipspyx._clipspyx import lib


# -- module-level state shared across all environments -----------------------

_active_states: set = set()
_original_handler = None
_handler_installed = False


# -- per-environment state ---------------------------------------------------

@dataclass(eq=False)
class SigintState:
    interrupted: bool = False
    env: object = None  # reference to the Environment


# -- Python SIGINT handler ---------------------------------------------------

def _sigint_handler(signum, frame):
    """Set the interrupted flag on every active environment."""
    for state in _active_states:
        state.interrupted = True
        # Also halt the async run loop if goal handlers are active.
        ghs = getattr(state.env, '_goal_handler_state', None)
        if ghs is not None:
            ghs.halted = True


# -- periodic callback -------------------------------------------------------

def _sigint_check(env):
    """Periodic callback: translate the Python flag into CLIPS halt flags."""
    state = env._sigint_state
    if state is not None and state.interrupted:
        lib.SetHaltExecution(env._env, True)
        lib.SetHaltRules(env._env, True)


# -- public API --------------------------------------------------------------

def enable_sigint_handler(env):
    """Enable SIGINT handling for *env*.

    Registers a periodic callback and installs a process-wide SIGINT
    handler (shared across all environments that have SIGINT enabled).
    Wraps ``agenda.run()`` so that an interrupted ``Run()`` raises
    ``KeyboardInterrupt`` after clearing the halt flags.
    """
    global _original_handler, _handler_installed

    state = SigintState(env=env)
    env._sigint_state = state

    # Register periodic callback via the public API.
    env.add_periodic_function("__py_sigint", _sigint_check)

    _active_states.add(state)

    # Install the Python SIGINT handler once (shared across environments).
    if not _handler_installed:
        _original_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, _sigint_handler)
        _handler_installed = True

    # Wrap agenda.run() to clear/check halt flags.
    agenda = env._agenda
    original_run = agenda.run

    def sigint_run(limit=None):
        state.interrupted = False
        lib.SetHaltExecution(env._env, False)
        lib.SetHaltRules(env._env, False)
        result = original_run(limit)
        if state.interrupted:
            state.interrupted = False
            lib.SetHaltExecution(env._env, False)
            lib.SetHaltRules(env._env, False)
            raise KeyboardInterrupt
        return result

    agenda.run = sigint_run


def disable_sigint_handler(env):
    """Disable SIGINT handling for *env*."""
    global _handler_installed

    state = getattr(env, '_sigint_state', None)
    if state is None:
        return

    # Remove the periodic callback.
    env.remove_periodic_function("__py_sigint")

    _active_states.discard(state)

    # Restore the original SIGINT handler if no environments remain.
    if not _active_states and _handler_installed:
        signal.signal(signal.SIGINT, _original_handler)
        _handler_installed = False

    # Clear halt flags so the environment is reusable.
    lib.SetHaltExecution(env._env, False)
    lib.SetHaltRules(env._env, False)

    env._sigint_state = None


@contextmanager
def sigint_handler(env):
    """Context manager for scoped SIGINT handling.

    ::

        with sigint_handler(env):
            env.run()
    """
    enable_sigint_handler(env)
    try:
        yield
    finally:
        disable_sigint_handler(env)
