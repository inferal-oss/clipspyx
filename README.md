# clipspyx

Python bindings and DSL for [CLIPS](https://www.clipsrules.net/), the
production rule engine. Write rules as Python classes, run them with an async
goal handler loop, trace fact derivation chains, and visualize your rule
network as D2 diagrams.

Originally forked from [clipspy](https://github.com/noxdafox/clipspy), clipspyx
adds a Python-native DSL, async backward chaining, fact tracing, and full
CLIPS 7.0 support while keeping the low-level CFFI API available for everything
else.

## Quick start

```bash
pip install clipspyx          # or: uv add clipspyx
```

### Low-level API

```python
from clipspyx import Environment

env = Environment()
env.build('(defrule hello (initial-fact) => (println "Hello CLIPS!"))')
env.reset()
env.run()
```

### Python DSL

Define CLIPS templates and rules as Python classes:

```python
from clipspyx import Environment
from clipspyx.dsl import Template, Rule, Multi

class Employee(Template):
    name: str
    title: str
    years: int = 0

class Skill(Template):
    name: str
    proficiency: int = 1

class Project(Template):
    name: str
    required_skill: str
    min_proficiency: int = 1

class AssignProject(Rule):
    """Match employees to projects by skill."""
    e = Employee(name=name)
    Skill(name=skill, proficiency=prof)
    Project(name=proj, required_skill=skill, min_proficiency=min_prof)
    prof >= min_prof

    def __action__(self):
        print(f"Assign {self.name} to project {self.proj}")

env = Environment()
NewEmployee = env.define(Employee)
NewSkill = env.define(Skill)
NewProject = env.define(Project)
env.define(AssignProject)

env.reset()
NewEmployee(name="Alice", title="Engineer", years=5)
NewSkill(name="Python", proficiency=4)
NewProject(name="Atlas", required_skill="Python", min_proficiency=3)
env.run()
# => Assign Alice to project Atlas
```

The DSL supports the full range of CLIPS conditional elements:

| Python syntax | CLIPS CE |
|---------------|----------|
| `p = Person(name=name)` | Assigned pattern |
| `Person(age=_)` | Wildcard |
| `Person(age=25)` | Literal constraint |
| `Person(name=not "Bob")` | Field negation |
| `Person(age=25 or 30)` | Field or |
| `age >= 18` | Test CE |
| `~Person(name="Bob")` | Negation |
| `exists(Person())` | Exists CE |
| `forall(Person(name=n), Badge(owner=n))` | Forall CE |
| `logical(Person(name=n))` | Logical CE |

Rules can declare effects without a Python bridge function:

```python
class DoubleInput(Rule):
    i = Input(value=v)
    asserts(Output(value=v * 2))

class Cleanup(Rule):
    p = Temp(flag=Symbol("done"))
    retracts(p)
```

### Fact tracing

Track which rules produced which facts:

```python
env.enable_tracing()
env.reset()
# ... assert facts and run ...

for firing in env.find_template('RuleFiring').facts():
    print(f"{firing['rule']}: {firing['inputs']} -> {firing['outputs']}")
```

Each `RuleFiring` fact records the rule name, the input facts that matched,
and the output facts that were asserted.

### Visualization

Generate D2 diagrams of your rule network:

```python
# Print D2 text
print(env.visualize(group_by_kind=True))

# Render to SVG (requires d2 CLI)
env.visualize(output="diagram.svg", group_by_kind=True)
```

Templates, rules, pattern edges, fact-address references, and effect edges
are all represented. See `examples/hr_system.py` for a full example.

### Async goal handlers (CLIPS 7.0)

CLIPS 7.0 backward chaining generates goals when a rule needs a fact that
doesn't exist yet. clipspyx dispatches these goals to Python async handlers,
enabling rules that wait on timers, HTTP calls, or any async I/O:

```python
import asyncio
from clipspyx import Environment
from clipspyx.dsl import Template, Rule, TimerEvent, AFTER
from clipspyx.values import Symbol

class Alert(Template):
    msg: str

class DelayedAlert(Rule):
    te = TimerEvent(kind=AFTER, name=Symbol("alarm"), seconds=2.0)
    asserts(Alert(msg=Symbol("time-is-up")))

env = Environment()
env.enable_goal_handlers()
env.define(Alert)
env.define(DelayedAlert)
env.reset()
asyncio.run(env.async_run())
```

Built-in `TimerEvent` supports one-shot (`AFTER`), absolute (`AT`), and
periodic (`EVERY`) timers. Register custom handlers for your own goal
templates:

```python
async def query_handler(goal, env):
    result = await fetch_from_service(goal['service'], goal['query'])
    env.find_template('QueryResult').assert_fact(result=result)

env.register_goal_handler('query-goal', query_handler)
```

## CLIPS 7.0 features

When built against CLIPS 7.0x, clipspyx also supports:

- **Template inheritance**: `(deftemplate car (is-a vehicle) (slot doors))`
- **Certainty factors**: `(deftemplate sensor (is-a CFD) (slot reading))`
  with CF propagation through rule chains
- **Deftables**: static lookup tables accessible from rules and Python
- **Backward chaining**: goal generation with `(goal ...)` patterns
- **`update_slots`**: selective rete re-evaluation (only rules matching
  the changed slot)

## Building from source

clipspyx compiles CLIPS source directly into the CFFI extension. No separate
`libclips` build step.

### Prerequisites

- Python 3.10+
- C compiler (gcc/clang on Linux/macOS, MSVC on Windows)
- CLIPS source (auto-checked out from orphan branch, or provide your own)

### Install for development

```bash
# Install with 64x backend (CLIPS 6.4x)
uv sync --extra 64x

# Install with 70x backend (CLIPS 7.0x)
uv sync --extra 70x
```

### Switching backends

The 64x and 70x backends conflict with each other. Always use `uv sync` to switch:

```bash
uv sync --extra 64x   # switch to 6.4x
uv sync --extra 70x   # switch to 7.0x
```

`uv run --extra` does *not* remove the previously installed conflicting backend.
Only `uv sync --extra <variant>` correctly handles the switch.

### CLIPS source override

```bash
CLIPS_SOURCE_DIR=/path/to/clips/core uv sync --extra 64x
```

### Build distributable wheels

```bash
uv run scripts/build-backend.py 64x   # builds clipspyx-ffi + clipspyx-ffi-64x wheels
uv run scripts/build-backend.py 70x   # builds clipspyx-ffi + clipspyx-ffi-70x wheels
```

## Testing

```bash
uv run pytest tests/ -v
```

## License

BSD-3-Clause. See [LICENSE.txt](LICENSE.txt).
