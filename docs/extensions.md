# Periodic Functions and SIGINT Handling

CLIPS fires rules inside `Run()`, which blocks the calling thread. Periodic
functions let you execute Python code *during* that blocked `Run()` call,
between rule firings. The SIGINT handler is a built-in use of periodic
functions that makes Ctrl-C work during `env.run()`.

## Periodic functions

Register a callback that CLIPS invokes periodically while rules are executing:

```python
from clipspyx import Environment

env = Environment()

counter = [0]

def tick(env):
    counter[0] += 1

env.add_periodic_function("my-tick", tick)
env.run()
print(counter[0])  # > 0, incremented during run()

env.remove_periodic_function("my-tick")
```

### API

```python
env.add_periodic_function(name, callback, priority=0)
env.remove_periodic_function(name)
```

**name**: unique string identifying the callback (used for removal).

**callback**: a callable receiving `(env,)`. Called by CLIPS between rule
firings inside `Run()`.

**priority**: integer controlling call order. Higher values run first.
The range -2000 to 2000 is reserved for CLIPS internals.

### Constraints

Periodic callbacks **must not modify CLIPS data structures**. They may examine
facts, check flags, or interact with external systems, but calling `assert`,
`retract`, `build`, or similar CLIPS-mutating operations from inside a periodic
callback is undefined behavior per the CLIPS embedding documentation.

Safe operations: reading flags, setting Python variables, calling
`SetHaltExecution` / `SetHaltRules` (these only set internal flags).

### Use cases

- Progress indicators during long inference runs
- Timeout enforcement (halt after N seconds)
- Polling external systems for cancellation signals
- The built-in SIGINT handler (see below)

## SIGINT handling (Ctrl-C)

By default, pressing Ctrl-C during `env.run()` has no effect because execution
is inside CLIPS C code. Enable the SIGINT handler to make Ctrl-C work:

```python
env.enable_sigint_handler()
try:
    env.run()
except KeyboardInterrupt:
    print("interrupted")
finally:
    env.disable_sigint_handler()
```

Or with the context manager:

```python
with env.sigint_handler():
    env.run()
```

### How it works

1. `enable_sigint_handler()` registers a periodic function (`__py_sigint`) and
   installs a Python SIGINT handler
2. When Ctrl-C arrives, the Python handler sets an `interrupted` flag
3. The periodic callback checks the flag between rule firings and calls the
   CLIPS `SetHaltExecution` / `SetHaltRules` APIs
4. `Run()` returns after the current rule completes
5. The `run()` wrapper detects the interruption and raises `KeyboardInterrupt`

### Multiple environments

The SIGINT handler supports multiple environments simultaneously. A single
process-wide signal handler sets the `interrupted` flag on all environments
that have SIGINT handling enabled. Each environment halts independently.

```python
env1.enable_sigint_handler()
env2.enable_sigint_handler()
# Ctrl-C halts both
```

### Async runner integration

When SIGINT fires during an `AsyncRunner.run()`, the async goal handler state
is also flagged as halted. The run loop returns `"halted"` after the current
cycle completes.

### Reuse after interrupt

After catching `KeyboardInterrupt`, the environment is immediately reusable.
The halt flags are cleared automatically:

```python
with env.sigint_handler():
    try:
        env.run()
    except KeyboardInterrupt:
        pass
    # Environment is clean, run again if needed
    env.run()
```

### API

```python
env.enable_sigint_handler()    # opt in
env.disable_sigint_handler()   # opt out, restores previous SIGINT handler
env.sigint_handler()           # context manager (enable on enter, disable on exit)
```

`disable_sigint_handler()` restores the original Python SIGINT handler when no
environments have SIGINT handling enabled. It is safe to call multiple times.
