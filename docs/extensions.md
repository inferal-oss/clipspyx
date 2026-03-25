# Periodic Functions, SIGINT Handling, and Loop Detection

CLIPS fires rules inside `Run()`, which blocks the calling thread. Periodic
functions let you execute Python code *during* that blocked `Run()` call,
between rule firings. The SIGINT handler and loop detection are built-in uses
of periodic functions.

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

## Loop detection

Rule systems can loop infinitely when rules trigger each other in cycles.
Loop detection uses the tracing system's `RuleFiring` provenance facts to
find causal cycles of any length and halt execution when a cycle repeats
too many times.

### Complete example

Two rules form a ping-pong cycle: `EscalateRule` sees a low-priority ticket
and bumps it, `ReviewRule` sees a high-priority ticket and resets it. Neither
rule has a termination condition, so they trigger each other forever.

```python
from clipspyx import Environment
from clipspyx.dsl import Template, Rule
from clipspyx.tracing import enable_tracing
from clipspyx.loops import enable_loop_detection, RuleLoopError

# 1. Create environment with tracing and loop detection.
#    Tracing records RuleFiring facts (which rule fired, what facts it
#    consumed and produced). Loop detection analyzes those facts to find
#    causal cycles.
env = Environment()
enable_tracing(env)
enable_loop_detection(env, threshold=5)  # allow up to 5 firings per cycled rule

# 2. Define templates.
class Ticket(Template):
    """A support ticket with a priority level."""
    priority: int

# 3. Define rules that form an unintentional cycle.
class EscalateRule(Rule):
    """Escalate low-priority tickets."""
    t = Ticket(priority=p)
    p < 10

    retracts(t)
    asserts(Ticket(priority=p + 5))

class ReviewRule(Rule):
    """Review high-priority tickets and reset them."""
    t = Ticket(priority=p)
    p >= 10

    retracts(t)
    asserts(Ticket(priority=1))

# 4. Register everything.
for cls in (Ticket, EscalateRule, ReviewRule):
    env.define(cls)

# 5. Assert initial fact and run.
tpl = env.find_template(Ticket.__clipspyx_dsl__.name)
tpl.assert_fact(priority=3)

try:
    env.run()
except RuleLoopError as e:
    print(e)
    # "Cycle involving rule '...EscalateRule': fired 6 times (threshold: 5)"
```

What happens step by step:

1. `EscalateRule` fires on `Ticket(priority=3)`, retracts it, asserts
   `Ticket(priority=8)`.
2. `EscalateRule` fires again on `Ticket(priority=8)`, asserts
   `Ticket(priority=13)`.
3. `ReviewRule` fires on `Ticket(priority=13)`, asserts `Ticket(priority=1)`.
4. `EscalateRule` fires on `Ticket(priority=1)` -- the cycle repeats.
5. After the threshold is exceeded, `RuleLoopError` is raised.

Between business rule firings, the infrastructure rules run at high salience:
`BuildDirectEdge` finds that `EscalateRule` produced a fact consumed by
`ReviewRule` (and vice versa), `BuildTransitive` extends the chain, and
`DetectCycle` marks both rules as participants in a cycle. The periodic
callback then counts `RuleFiring` facts for the cycled rules and halts
execution once the count exceeds the threshold.

### How it works

Loop detection defines three infrastructure rules and a periodic callback:

1. **BuildDirectEdge** (salience 9999): scans `RuleFiring` facts for causal
   links. If rule A produced a fact (in `outputs`) that rule B consumed (in
   `inputs`), it asserts `RuleTriggered(cause=A, effect=B)`.

2. **BuildTransitive** (salience 9998): extends chains. If A triggers B and B
   triggers C, it asserts `RuleTriggered(cause=A, effect=C)`.

3. **DetectCycle** (salience 10000): watches for self-edges. If
   `RuleTriggered(cause=A, effect=A)` appears, it asserts
   `CycleDetected(rule=A)`.

4. **Periodic callback**: counts `RuleFiring` facts for each rule marked in
   `CycleDetected`. When the count exceeds the threshold, it halts execution
   and the `run()` wrapper raises `RuleLoopError`.

The infrastructure rules use multifield matching to trace fact references
across `RuleFiring.outputs` and `RuleFiring.inputs`:

```python
# BuildDirectEdge pattern (simplified):
f1 = RuleFiring(rule=a, outputs=(*_, shared, *_))
f2 = RuleFiring(rule=b, inputs=(*_, shared, *_))
```

CLIPS unifies the `shared` variable across both patterns, finding a specific
fact that A produced and B consumed. The transitive closure finds cycles of
any length without needing to specify the length in advance.

### Cycle detection for different chain lengths

| Chain | Example | Detection |
|-------|---------|-----------|
| Self-loop | A → A | `BuildDirectEdge` creates `RuleTriggered(A, A)` directly |
| Cycle-2 | A → B → A | Direct edges A→B, B→A; transitive step yields A→A |
| Cycle-N | A → B → ... → A | Direct edges accumulate; transitive closure reaches A→A |

For a cycle of length N, detection fires after one complete cycle (N+1 business
rule firings). The threshold then controls how many additional repetitions are
allowed before raising `RuleLoopError`.

### Threshold behavior

The `threshold` parameter sets how many times a rule in a detected cycle may
fire during a single `run()` before an error is raised:

```python
enable_loop_detection(env, threshold=10)  # allow 10 firings before error
```

With `threshold=1`, the error is raised on the first cycle repetition. With
higher thresholds, intentionally cyclic systems (e.g. control loops that
converge) can run for several iterations before being stopped.

### Infrastructure isolation

The `RuleTriggered` and `CycleDetected` facts are excluded from tracing's
assert callback, so the infrastructure rules' own firings never create false
causal edges among themselves.

### API

```python
env.enable_loop_detection(threshold=3)   # enable (requires tracing)
env.disable_loop_detection()             # disable
```

Or using the module functions directly:

```python
from clipspyx.loops import enable_loop_detection, disable_loop_detection
enable_loop_detection(env, threshold=3)
disable_loop_detection(env)
```

### Requirements

- Tracing must be enabled before loop detection (`enable_tracing(env)`)
- Both must be enabled before defining business rules (so tracing hooks are
  injected into the rule RHS)
- Only DSL-defined rules are tracked; raw `env.build("(defrule ...)")` rules
  are invisible to the detection system
