"""Public API for CLIPS periodic callback functions.

Periodic functions are invoked by CLIPS during rule execution (e.g. inside
``Run()``).  They allow embedded applications to perform background tasks
such as polling for signals, updating progress indicators, or enforcing
timeouts.

**Important constraint from the CLIPS documentation:** periodic callbacks
must not modify CLIPS data structures – they may only examine them.
"""

import traceback
from dataclasses import dataclass

from clipspyx._clipspyx import lib, ffi


@dataclass
class PeriodicEntry:
    name: str
    callback: object       # callable(env) — the user's Python function
    handle: object = None  # CData from ffi.new_handle (prevent GC)
    env: object = None     # reference to the Environment


@ffi.def_extern()
def _periodic_callback(env_ptr, context_void):
    """CFFI callback invoked by CLIPS during rule execution.

    Dispatches to the registered Python callable stored in the handle.
    """
    try:
        entry = ffi.from_handle(context_void)
        entry.callback(entry.env)
    except BaseException:
        msg = "[PERIODIC] callback error:\n" + traceback.format_exc()
        lib.WriteString(env_ptr, b"stderr", msg.encode())


def add_periodic_function(env, name, callback, priority=0):
    """Register a periodic callback for this environment.

    Parameters
    ----------
    env : Environment
        The clipspyx Environment instance.
    name : str
        Unique name identifying this callback (used for removal).
    callback : callable
        Python function receiving ``(env,)`` as its single argument.
        Must not modify CLIPS data structures.
    priority : int, optional
        Higher values are called first.  Range -2000..2000 is reserved
        for CLIPS internals.  Defaults to 0.
    """
    entry = PeriodicEntry(name=name, callback=callback, env=env)
    handle = ffi.new_handle(entry)
    entry.handle = handle

    lib.AddPeriodicFunction(
        env._env, name.encode(), lib._periodic_callback, priority, handle,
    )
    env._periodic_functions[name] = entry


def remove_periodic_function(env, name):
    """Remove a previously registered periodic callback.

    Parameters
    ----------
    env : Environment
        The clipspyx Environment instance.
    name : str
        The name passed to :func:`add_periodic_function`.
    """
    lib.RemovePeriodicFunction(env._env, name.encode())
    env._periodic_functions.pop(name, None)
