# Async Goal Handlers

An asyncio-based framework for fulfilling CLIPS 7.0x backward chaining goals
from Python. Rules declare what they need, the runtime fulfills those needs
asynchronously. Timers are the first built-in handler; the framework is general
enough for any async operation.

**Requires CLIPS 7.0x.** Goals are a 7.0x backward chaining feature.

## How it works

CLIPS 7.0x generates goals automatically when a rule needs a fact that doesn't
exist. If another rule has a `goal()` conditional element for that template,
CLIPS creates a goal fact. The async run loop watches for goals, dispatches
them to registered Python async handlers, and asserts facts to satisfy them.

```
Rule needs (timer-event ...) fact
  -> CLIPS generates goal
    -> Python handler sees goal, creates asyncio timer
      -> timer fires, handler asserts (timer-event ...) fact
        -> goal satisfied, original rule fires
```

## Quick start

```python
import asyncio
from clipspyx import Environment, Symbol
from clipspyx.dsl import Template, Rule, TimerEvent
from clipspyx.async_goals import AsyncRunner

class Ticket(Template):
    id: Symbol
    status: Symbol

# Goal handler rule: enables backward chaining for TimerEvent
class HandleTimerGoal(Rule):
    goal(TimerEvent(kind=k, name=n, seconds=s))

# Consuming rule: needs a timer-event with specific parameters.
# When no matching timer-event fact exists, CLIPS generates a goal.
# The async runtime picks up the goal and creates an OS timer.
class EscalateStale(Rule):
    t = Ticket(id=tid, status=Symbol("open"))
    te = TimerEvent(
        kind=Symbol("after"), name=Symbol("escalate"), seconds=300.0)

    def __action__(self):
        print(f"Escalating ticket {self.tid}")

env = Environment()
env.define(Ticket)
env.define(HandleTimerGoal)
env.define(EscalateStale)
env.reset()

# Assert a ticket - CLIPS generates a timer goal
Ticket(__env__=env, id=Symbol("T-1"), status=Symbol("open"))

# Run with async context manager - fires after 300 seconds
async def main():
    async with AsyncRunner(env) as runner:
        result = await runner.run()
        print(f"Finished: {result}")

asyncio.run(main())
```

## AsyncRunner

`AsyncRunner` is the primary API for running async goal handlers. It wraps the
environment in a resource context that manages handler registration, task
lifecycle, and cleanup.

### Context manager pattern

Use `async with` to ensure proper setup and teardown. The constructor
auto-enables goal handlers on the environment if they are not already enabled.
On exit, all pending tasks are cancelled and goal handlers are disabled.

```python
from clipspyx.async_goals import AsyncRunner

async with AsyncRunner(env) as runner:
    result = await runner.run()
```

You can also manage the lifecycle manually:

```python
runner = AsyncRunner(env)
await runner.__aenter__()
try:
    result = await runner.run()
finally:
    await runner.close()
```

### Registering handlers

Register async handlers for any template. This replaces calling
`env.register_goal_handler` directly:

```python
async with AsyncRunner(env) as runner:
    runner.register_handler(FetchRequest, fetch_handler)
    result = await runner.run()
```

The built-in timer handler is registered automatically when goal handlers are
enabled.

### Persistent handlers

By default, a handler's task is cancelled when the run loop exits (due to a
stop event, max cycles, or halt). A persistent handler survives stop events and
stays alive across multiple `run()` calls. Use this for long-lived background
operations that should keep running while the main loop restarts.

```python
async def monitor_handler(goal, env):
    """Long-lived handler that polls an external service."""
    url = str(goal['url'])
    while True:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
        MonitorResult(__env__=env, url=url, status=resp.status_code)
        await asyncio.sleep(30)

async with AsyncRunner(env) as runner:
    runner.register_handler(MonitorRequest, monitor_handler, persistent=True)

    work_ready = asyncio.Event()
    done = False
    while not done:
        work_ready.clear()
        result = await runner.run(stop_event=work_ready)
        # Persistent handler tasks survive the stop_event.
        # Process results, then loop to run() again.
        done = check_if_finished(env)
```

Persistent tasks are only cancelled when the runner is closed (either by
exiting the `async with` block or calling `runner.close()` explicitly).

### Running the loop

```python
await runner.run()                  # run until no goals and no pending handlers
await runner.run(limit=10)          # pass limit to each env.run() call
await runner.run(max_cycles=5)      # stop after N dispatch cycles
await runner.run(stop_event=evt)    # stop when the event is set
```

Each cycle:

1. `env.run()` processes the CLIPS agenda (fires rules)
2. Auto-retract periodic timer facts (so goals regenerate)
3. Scan goals for registered handlers
4. Dispatch matching goals as asyncio tasks
5. Wait for at least one task to complete
6. Loop

Returns when no goals remain and no handlers are pending, when `max_cycles`
is reached, when `halt_async()` is called, or when `stop_event` is set.

## TimerEvent template

The `TimerEvent` DSL template is defined in `clipspyx.dsl.timer` and
auto-registered by `enable_goal_handlers`. Import it for use in rules:

```python
from clipspyx.dsl import TimerEvent
```

Slots:

| Slot | Type | Default | Description |
|------|------|---------|-------------|
| `kind` | SYMBOL | (required) | `after`, `at`, or `every` |
| `name` | SYMBOL | (required) | Timer identity (for deduplication) |
| `seconds` | FLOAT | 0.0 | Duration for `after`/`every` |
| `time` | FLOAT | 0.0 | Unix epoch for `at` |
| `count` | INTEGER | 0 | Firing count (increments for `every`) |
| `fired_at` | FLOAT | 0.0 | Actual fire time (set by handler) |

### Timer kinds

**after**: fire once after a delay.

```python
class OnTimeout(Rule):
    te = TimerEvent(
        kind=Symbol("after"), name=Symbol("my-timeout"), seconds=5.0)
    asserts(Alert(msg=Symbol("timed-out")))
```

**at**: fire at an absolute wall-clock time (Unix epoch). Since the epoch value
is dynamic, pass it through a fact:

```python
class ScheduleConfig(Template):
    target_time: float

class OnScheduled(Rule):
    cfg = ScheduleConfig(target_time=t)
    te = TimerEvent(kind=Symbol("at"), name=Symbol("morning"), time=t)
    asserts(Report(msg=Symbol("good-morning")))

# At runtime:
ScheduleConfig(__env__=env, target_time=tomorrow_9am.timestamp())
```

**every**: fire periodically. The `count` slot increments each cycle. The
framework auto-retracts the timer-event fact after each `run()` cycle so the
goal regenerates.

```python
class BeatLog(Template):
    n: int

class Heartbeat(Rule):
    te = TimerEvent(
        kind=Symbol("every"), name=Symbol("hb"), seconds=10.0, count=c)
    asserts(BeatLog(n=c))
```

To stop a periodic timer, retract a controlling fact so the goal stops
regenerating. See [Cancellation](#cancellation).

## Goal handler rules

Every template that participates in backward chaining needs a **goal handler
rule** with a `goal()` conditional element. This tells CLIPS to generate goals
for that template:

```python
# Enables goal generation for TimerEvent
class HandleTimerGoal(Rule):
    goal(TimerEvent(kind=k, name=n, seconds=s))
```

Without this rule, CLIPS won't generate goals for `timer-event` patterns, and
the async handler won't be triggered.

The goal handler rule's LHS determines which slots appear in the generated
goal. Slots not mentioned in the goal CE or the consuming rule's pattern will
have universally quantified values (`??`) in the goal.

## Symbol constants

Timer kind constants are available for runtime use (actions, assertions,
comparisons):

```python
from clipspyx.dsl import AFTER, AT, EVERY

# Use in __action__ methods or programmatic code:
if str(fact['kind']) == str(AFTER):
    ...
```

In DSL rule patterns, use `Symbol("after")` directly since the parser resolves
literal values from source code, not runtime variables.

## Custom goal handlers

Register async handlers for any template, not just timers:

```python
class FetchRequest(Template):
    url: str

class FetchResponse(Template):
    url: str
    status: int
    body: str

async def fetch_handler(goal, env):
    """Fulfill a fetch-request goal by making an HTTP request."""
    url = str(goal['url'])
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    # Assert both the request (satisfies the goal) and the response
    FetchRequest(__env__=env, url=url)
    FetchResponse(__env__=env, url=url, status=resp.status_code,
                  body=resp.text[:1000])

env.define(FetchRequest)
env.define(FetchResponse)

async with AsyncRunner(env) as runner:
    runner.register_handler(FetchRequest, fetch_handler)
    result = await runner.run()
```

`register_handler` accepts a DSL Template class or a CLIPS template name
string:

```python
# With DSL Template class (preferred)
runner.register_handler(FetchRequest, fetch_handler)

# With string (for raw deftemplates)
runner.register_handler('fetch-request', fetch_handler)
```

Handler signature:

```python
async def handler(goal, env) -> None
```

- `goal`: a `TemplateFact` with slot access via `goal['slot_name']`
- `env`: the `Environment` for asserting facts

The handler must assert a fact matching the goal's template to satisfy it.
Multiple handlers dispatch concurrently via `asyncio.gather`.

## Cancellation

Cancel timers (or any goal-driven operation) by retracting a controlling fact.
When the controlling fact disappears, the consuming rule's LHS is no longer
satisfied, CLIPS retracts the goal, and the async loop cancels the pending
handler. No special API needed.

```python
class Active(Template):
    pass

class BeatLog(Template):
    n: int

# Goal only generated while (Active) exists
class Heartbeat(Rule):
    Active()
    te = TimerEvent(
        kind=Symbol("every"), name=Symbol("hb"),
        seconds=10.0, count=c)
    asserts(BeatLog(n=c))

# Stop after 5 beats
class StopAfter5(Rule):
    a = Active()
    BeatLog(n=5)
    retracts(a)
```

When `StopAfter5` fires, it retracts `(Active)`. The `Heartbeat` rule's LHS
is no longer satisfied, CLIPS retracts the timer-event goal, the async loop
cancels the pending sleep, and `runner.run()` returns.

This pattern works for any goal type, not just timers. The controlling fact
acts as an on/off switch for the entire goal chain.

### Programmatic cancellation

**Internal (from rules):** Call `halt_async()` from a rule action to stop the
loop after the current cycle:

```python
class StopOnError(Rule):
    ErrorCount(count=c)
    c >= 10
    def __action__(self):
        self.__env__.halt_async()
```

**External (from Python):** Pass an `asyncio.Event` as `stop_event`. When set,
the loop exits cleanly, cancelling all non-persistent pending handlers:

```python
stop = asyncio.Event()

async with AsyncRunner(env) as runner:
    task = asyncio.create_task(runner.run(stop_event=stop))

    # Later, from external code:
    stop.set()
    reason = await task  # "stopped"
```

### Return values

`runner.run()` returns a string indicating why the loop stopped:

| Return value | Meaning |
|-------------|---------|
| `"completed"` | No goals remain, no pending handlers |
| `"max_cycles"` | Reached the `max_cycles` limit |
| `"halted"` | `halt_async()` was called from a rule |
| `"stopped"` | `stop_event` was set externally |

## Error handling

Handler exceptions are wrapped in `GoalHandlerError`:

```python
from clipspyx.async_goals import AsyncRunner, GoalHandlerError

try:
    async with AsyncRunner(env) as runner:
        await runner.run()
except GoalHandlerError as e:
    print(f"Handler failed: {e.__cause__}")
```

## Legacy API (deprecated)

The `enable_goal_handlers` + `async_run` pattern still works but is deprecated.
Prefer `AsyncRunner`, which handles setup, teardown, and persistent handlers
automatically.

> **Deprecation notice:** `enable_goal_handlers`, `disable_goal_handlers`, and
> `env.async_run()` will be removed in a future release. Migrate to
> `AsyncRunner` for new code.

```python
from clipspyx.async_goals import enable_goal_handlers, disable_goal_handlers

env = Environment()
enable_goal_handlers(env)  # registers timer-event template + built-in handler

# Register handlers directly on the environment
env.register_goal_handler(FetchRequest, fetch_handler)

# Run the loop
await env.async_run()
await env.async_run(limit=10)
await env.async_run(max_cycles=5)
await env.async_run(stop_event=stop)

# Disable when done
disable_goal_handlers(env)  # cancels pending tasks, clears state
```

## API reference

| Class | Description |
|-------|-------------|
| `AsyncRunner(env)` | Async context manager for running goal handlers. Auto-enables goal handlers if not already enabled. |
| `AsyncRunner.register_handler(template, handler, persistent=False)` | Register an async handler. Set `persistent=True` for tasks that survive stop events. |
| `AsyncRunner.run(limit, max_cycles, stop_event)` | Run the async event loop. Returns `"completed"`, `"max_cycles"`, `"halted"`, or `"stopped"`. |
| `AsyncRunner.close()` | Cancel all tasks and disable goal handlers. Called automatically on context manager exit. |

| Function (legacy) | Description |
|--------------------|-------------|
| `enable_goal_handlers(env)` | Register timer-event template and built-in handler |
| `disable_goal_handlers(env)` | Cancel pending tasks and clear state |
| `env.register_goal_handler(template, handler)` | Register async handler (template class or string) |
| `env.async_run(limit, max_cycles, stop_event)` | Run the async event loop |
| `env.halt_async()` | Signal the run loop to stop after the current cycle |

| Class/Constant | Description |
|----------------|-------------|
| `TimerEvent` | DSL Template for timer events |
| `AFTER` | `Symbol('after')` |
| `AT` | `Symbol('at')` |
| `EVERY` | `Symbol('every')` |
| `GoalHandlerError` | Exception wrapping handler failures |
