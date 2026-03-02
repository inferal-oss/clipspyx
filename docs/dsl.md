# clipspyx DSL

A Python-native DSL for defining CLIPS templates and rules. Instead of writing
raw CLIPS syntax strings, you write annotated Python classes that compile to
CLIPS constructs at define-time.

## Why no CLIPS language on the RHS?

CLIPS has its own programming language for rule actions: variable binding,
loops, string manipulation, I/O, and so on. The DSL does not replicate any of
this. Rule actions are plain Python methods (`__action__`), and the DSL bridges
them back into CLIPS through a generated deffunction. When a rule fires, CLIPS
calls the bridge function, which passes the bound variables into your Python
method.

This means you get Python's full language for actions (string formatting,
library calls, data structures, exception handling) without learning a second
language. The CLIPS engine handles pattern matching and truth maintenance; Python
handles everything else.

## Installation

The DSL requires the `dsl` extra:

```bash
pip install clipspyx[dsl]
```

## Quick start

```python
from clipspyx import Environment
from clipspyx.dsl import Template, Rule, Multi

class Person(Template):
    name: str
    age: int = 0

class GreetAdult(Rule):
    p = Person(name=name, age=age)
    age >= 18

    def __action__(self):
        print(f"Hello {self.name}, age {self.age}")

env = Environment()
Person = env.define(Person)
env.define(GreetAdult)
env.reset()

Person(name="Alice", age=25)
Person(name="Bob", age=15)
env.run()
# prints: Hello Alice, age 25
```

## Templates

Subclass `Template` to define a CLIPS deftemplate. Annotations become slots.
Class-level defaults become slot defaults.

```python
from clipspyx.dsl import Template, Multi

class Person(Template):
    name: str
    age: int = 0
    hobbies: Multi[str]  # multislot
```

This generates (assuming the code lives in a module called `myapp`):

```clips
(deftemplate myapp.Person
  (slot name (type STRING))
  (slot age (type INTEGER) (default 0))
  (multislot hobbies (type STRING)))
```

Template and rule names in CLIPS are qualified with the Python module name
(`module.ClassName`) to prevent cross-module name clashes. See
[Module-qualified names](#module-qualified-names) for details.

### Supported types

| Python type | CLIPS type |
|-------------|------------|
| `str` | `STRING` |
| `int` | `INTEGER` |
| `float` | `FLOAT` |
| `Symbol` | `SYMBOL` |
| `Multi[T]` | multislot of type `T` |

### Typed fact-address slots

A slot can reference another template by using the template class as its type
annotation. The slot becomes a `FACT-ADDRESS` in CLIPS, and a runtime type-check
rule ensures only facts of the correct template are assigned to it.

```python
class Person(Template):
    name: str

class Department(Template):
    name: str
    head: Person   # FACT-ADDRESS slot typed to Person
```

This generates a `(slot head (type FACT-ADDRESS))` in the deftemplate and a
high-salience type-check rule. If you assign a fact of the wrong template type
to the `head` slot, `env.run()` raises a `TypeError`:

```python
env = Environment()
PersonAssert = env.define(Person)
DeptAssert = env.define(Department)
env.reset()

p = PersonAssert(name="Alice")
DeptAssert(name="Engineering", head=p)  # OK: Person fact
env.run()

a = AnimalAssert(species="cat")
DeptAssert(name="Engineering", head=a)  # TypeError on env.run()
```

The mechanism works through a hidden `__py_type__` SYMBOL slot added to every
template. Each fact carries its template name as a symbol, and the generated
type-check rule compares this value against the expected template type.

### Asserting facts

`env.define()` returns a bound asserter: a callable that asserts facts in that
environment. This is the primary API for fact assertion:

```python
Person = env.define(Person)
env.reset()
fact = Person(name="Alice", age=25)
# fact is a TemplateFact object
```

The returned `TemplateFact` supports both dict-style and attribute-style access:

```python
fact["name"]   # "Alice"
fact.name      # "Alice"
fact.age       # 25
```

As an alternative, you can pass `__env__=` directly to the `Template` subclass:

```python
env.define(Person)
env.reset()
fact = Person(__env__=env, name="Alice", age=25)
```

## Rules

Subclass `Rule` to define a CLIPS defrule. The class body contains the LHS
(left-hand side) patterns. An optional `__action__` method is the RHS (right-hand
side) that runs when the rule fires.

```python
class GreetAdult(Rule):
    p = Person(name=name, age=age)   # pattern CE, binds ?p, ?name, ?age
    age >= 18                         # test CE

    def __action__(self):
        print(f"Hello {self.name}, age {self.age}")
```

The DSL parses the class source with libcst at class creation time, compiles it
to a CLIPS defrule string, and registers a bridge deffunction that calls your
`__action__` method.

### How it works

1. The metaclass uses a custom namespace so bare names like `name` and `age`
   resolve to inert placeholder objects during class body execution.
2. libcst parses the class source to extract patterns, constraints, and tests
   into an intermediate representation.
3. `env.define(GreetAdult)` generates the CLIPS defrule string, registers the
   Python action as a bridge deffunction, and calls `env.build()`.
4. When the rule fires, CLIPS calls the bridge function with the bound
   variables. These are set as attributes on a namespace object passed to
   `__action__` as `self`.

### Accessing bound variables in actions

Inside `__action__`, access variables through `self`:

```python
def __action__(self):
    print(self.name)   # the value of ?name
    print(self.age)    # the value of ?age
    print(self.p)      # the TemplateFact bound to ?p
    print(self.p.name) # attribute access on bound facts works too
```

The CLIPS environment is also available as `self.__env__`, so actions can assert
new facts, retract, or call other environment methods:

```python
def __action__(self):
    PersonAssert = self.__env__.find_template("myapp.Person")
    PersonAssert.assert_fact(name="derived", age=0)
```

Only variables that are bound in the LHS and visible on the RHS are available.
Variables inside scoped CEs (forall, exists, not) are not accessible.

## Conditional elements

### Pattern CE

A template call in the rule body becomes a pattern CE:

```python
class R(Rule):
    Person(name=name, age=age)
```

```clips
(myapp.Person (name ?name) (age ?age))
```

### Assigned pattern

Assign a pattern to a name to bind the fact address:

```python
class R(Rule):
    p = Person(name=name)
```

```clips
?p <- (myapp.Person (name ?name))
```

### Test CE

A comparison expression at the top level becomes a test CE:

```python
class R(Rule):
    Person(age=age)
    age >= 18
```

```clips
(myapp.Person (age ?age))
(test (>= ?age 18))
```

### Not CE

Use `~` (bitwise not) before a template call for a CE-level negation. The rule
fires when no matching fact exists:

```python
class R(Rule):
    ~Person(name="Bob")
```

```clips
(not (myapp.Person (name "Bob")))
```

### Or CE

Use `|` (bitwise or) between template calls for a CE-level disjunction:

```python
class R(Rule):
    Person(name="Alice") | Person(name="Bob")
```

```clips
(or (myapp.Person (name "Alice")) (myapp.Person (name "Bob")))
```

### Exists CE

Fires once when at least one matching fact exists:

```python
class R(Rule):
    exists(Person())
```

```clips
(exists (myapp.Person))
```

### Forall CE

Fires when every fact matching the first pattern also satisfies the remaining
conditions:

```python
class R(Rule):
    forall(Person(name=name), Badge(owner=name))
```

```clips
(forall (myapp.Person (name ?name)) (myapp.Badge (owner ?name)))
```

### Logical CE

Truth maintenance: facts asserted by the action are automatically retracted if
the logical support is removed.

```python
class R(Rule):
    logical(Person(name=name, age=age))
    age >= 18

    def __action__(self):
        # assert derived facts here
        pass
```

```clips
(logical (myapp.Person (name ?name) (age ?age)))
(test (>= ?age 18))
```

### Goal and Explicit CE (CLIPS 7.0x)

For backward chaining:

```python
class R(Rule):
    goal(Person(name=name))

class R2(Rule):
    explicit(Person(name=name))
```

## Slot constraints

### Variable binding

A bare name binds a CLIPS variable:

```python
Person(name=name)      # (name ?name)
```

### Wildcard

Use `_` for an anonymous wildcard:

```python
Person(age=_)          # (age ?)
```

### Literal values

Integers, floats, and strings are literal constraints:

```python
Person(age=25)         # (age 25)
Person(name="Bob")     # (name "Bob")
```

### Field-level not

Python's `not` keyword negates a slot value:

```python
Person(name=not "Bob")         # (name ~"Bob")
```

### Field-level or

Python's `or` keyword creates a disjunction of values:

```python
Person(age=25 or 30 or 35)    # (age 25|30|35)
```

### Predicate constraint (and)

Python's `and` keyword binds a variable and applies a predicate:

```python
Person(age=age and age >= 18)
# (age ?age&:(>= ?age 18))

Person(name=name and name != "Admin")
# (name ?name&:(neq ?name "Admin"))
```

## Salience

Set rule priority with `__salience__`:

```python
class HighPriority(Rule):
    __salience__ = 10
    Person(name=name)

    def __action__(self):
        print(f"High priority: {self.name}")
```

```clips
(defrule myapp.HighPriority
  (declare (salience 10))
  (myapp.Person (name ?name))
  =>
  ...)
```

Higher salience fires first.

## Syntax reference

| Python | CLIPS | Scope |
|--------|-------|-------|
| `Person(name=name)` | `(mod.Person (name ?name))` | Pattern CE |
| `p = Person(...)` | `?p <- (mod.Person ...)` | Assigned pattern |
| `age >= 18` | `(test (>= ?age 18))` | Test CE |
| `~Person(...)` | `(not (mod.Person ...))` | CE-level: no such fact |
| `Person(...) \| Other(...)` | `(or (mod.Person ...) (mod.Other ...))` | CE-level: either pattern |
| `exists(Person(...))` | `(exists (mod.Person ...))` | CE: at least one |
| `forall(P(...), Q(...))` | `(forall (mod.P ...) (mod.Q ...))` | CE: universal |
| `logical(Person(...))` | `(logical (mod.Person ...))` | CE: truth maintenance |
| `goal(Person(...))` | `(goal (mod.Person ...))` | CE: backward chain (7.0x) |
| `explicit(Person(...))` | `(explicit (mod.Person ...))` | CE: no goal gen (7.0x) |
| `not "Bob"` | `~"Bob"` | Field: slot is not this value |
| `25 or 30 or 35` | `25\|30\|35` | Field: one of these values |
| `x and x > 5` | `?x&:(> ?x 5)` | Field: bind + predicate |
| `_` | `?` | Field: anonymous wildcard |
| `__salience__ = 10` | `(declare (salience 10))` | Rule priority |
| `P = env.define(Person)` | — | Bound asserter (primary) |
| `Person(__env__=env, ...)` | — | Direct assertion (fallback) |

## Module-qualified names

Templates and rules use `module.ClassName` as their CLIPS identifier, where
`module` is the Python module the class is defined in (`cls.__module__`). For
example, a `Person` template in `myapp/models.py` becomes `myapp.models.Person`
in CLIPS.

This prevents cross-module name clashes: two modules can both define
`class Person(Template)` without conflict, because they produce different CLIPS
names (e.g. `myapp.models.Person` vs `myapp.hr.Person`).

Dots are valid in CLIPS identifiers and do not conflict with CLIPS's own `::`
module separator syntax.

In Python code, you always use the bare class name (`Person`). The qualified
name is only visible in CLIPS constructs (deftemplate, defrule strings) and when
inspecting the IR via `cls.__clipspyx_dsl__.name`.

## Annotations

Templates, rules, and individual CEs can carry human-readable annotations.
These serve two purposes: they appear in generated diagrams (see
[Visualization](#visualization)), and they are accessible programmatically
through the IR for tooling and introspection.

### Template docstrings

A docstring on a `Template` subclass describes what the template represents.
In diagrams it renders as a cloud note connected to the template node.

```python
class Employee(Template):
    """An employee in the organization."""
    name: str
    title: str
    years: int = 0
```

Accessible via `Employee.__doc__`.

### Slot descriptions

A standalone string literal on the line after a slot annotation attaches a
description to that slot. This does not affect CLIPS code generation; it is
metadata for documentation and tooling. In diagrams it renders as a page note
connected to the slot row.

```python
class Employee(Template):
    """An employee in the organization."""
    name: str
    """Full legal name"""
    title: str
    """Current job title"""
    years: int = 0
    """Years of service in the company"""
```

A slot can have a description or not; undocumented slots are unaffected.

Accessible in the IR via `slot.description`:

```python
dsl_def = Employee.__clipspyx_dsl__
slots = {s.name: s for s in dsl_def.slots}
slots['name'].description   # "Full legal name"
slots['years'].description  # "Years of service in the company"
```

### Rule docstrings

A docstring on a `Rule` subclass describes the rule's intent. In diagrams it
renders as a cloud note connected to the rule node.

```python
class PromoteEmployee(Rule):
    """Promote employees with enough experience."""
    e = Employee(name=name, years=years)
    years >= 10

    def __action__(self):
        print(f"Consider promoting {self.name}")
```

Accessible via `PromoteEmployee.__doc__`.

### CE labels

An inline comment on a CE statement gives it a short name. Without a comment,
CEs are labeled `ce0`, `ce1`, etc. in diagrams.

```python
class AssignProject(Rule):
    e = Employee(name=name)
    Skill(name=skill, proficiency=prof)             # has_skill
    Project(name=proj, required_skill=skill)        # needs_skill
    prof >= min_prof                                # qualified
    ~Employee(name="fired")                         # not_fired

    def __action__(self):
        ...
```

Labels apply to any CE type: patterns, tests, not, or, exists, forall,
logical.

Assigned patterns (`p = Person(...)`) use the variable name as the default
label. A comment overrides it:

```python
class R(Rule):
    p = Person(name=name)
    q = Person(name=name)  # partner
```

Here `p` has no comment, so its label defaults to the variable name `p`.
The second pattern has `# partner`, so its label is `partner` instead of `q`.

Accessible in the IR via `ce.label`:

```python
dsl_def = AssignProject.__clipspyx_dsl__
dsl_def.conditions[1].label  # "has_skill"
dsl_def.conditions[3].label  # "qualified"
```

### CE descriptions

A standalone string literal on the line after a CE attaches a longer
description. This does not affect CLIPS code generation; it is metadata for
documentation and tooling.

```python
class AssignProject(Rule):
    Skill(name=skill, proficiency=prof)  # has_skill
    """Employee must have the required skill at sufficient proficiency"""
    Project(name=proj, required_skill=skill)  # needs_skill
    """Project defines which skill is needed and the minimum bar"""
    prof >= min_prof  # qualified

    def __action__(self):
        ...
```

The string attaches to the CE immediately above it. A CE can have both a label
(from the comment) and a description (from the string), or either one alone.

Accessible in the IR via `ce.description`:

```python
dsl_def = AssignProject.__clipspyx_dsl__
dsl_def.conditions[0].description
# "Employee must have the required skill at sufficient proficiency"
```

### Summary

| Construct | Annotation | Syntax | IR access |
|-----------|-----------|--------|-----------|
| Template | Docstring | `"""..."""` under class line | `cls.__doc__` |
| Slot | Description | `"""..."""` on next line | `slot.description` |
| Rule | Docstring | `"""..."""` under class line | `cls.__doc__` |
| CE | Label | `# name` inline comment | `ce.label` |
| CE | Description | `"""..."""` on next line | `ce.description` |

## Visualization

After defining templates and rules, generate a visual overview with
`env.visualize()`. It produces a [D2](https://d2lang.com) diagram.

```python
env = Environment()
env.define(Person)
env.define(Department)
env.define(GreetAdult)

# Get D2 text (always works, no dependencies)
d2_text = env.visualize()
print(d2_text)

# Render to SVG (requires d2 CLI installed)
env.visualize(output="schema.svg")

# Use a different layout engine (default is 'elk')
env.visualize(output="schema.svg", layout="dagre")
```

The diagram includes:

- **Templates** as blue `sql_table` shapes with slot rows (name, type, default)
- **Rules** as purple `sql_table` shapes with CE rows, bound variables, and
  salience
- **Edges** from rules to templates they match, annotated with CE type (not,
  or, exists, forall, logical) and matched slot names
- **Fact-address edges** (dashed) between templates that reference each other
- **Docstring notes** as cloud shapes connected to templates and rules
- **Slot descriptions** as page shapes connected to individual slot rows
- **CE descriptions** as page shapes connected to individual CE rows
- **CE labels** as row keys in rule tables (from inline comments or variable
  names; falls back to `ce0`, `ce1`, ...)
- **Module grouping**: constructs grouped into D2 containers by Python module

The default layout engine is [ELK](https://www.eclipse.org/elk/), which
produces cleaner layouts for complex diagrams. Pass `layout="dagre"` to use
the dagre engine instead.

See `examples/hr_system.py` for a complete example.

## Limitations

- **Source must be in a file.** The parser uses `inspect.getsource()`, so rules
  defined in the REPL or via `python -c` will fail. Rules must live in `.py`
  files.

- **No CLIPS language on the RHS.** Rule actions are Python methods, not CLIPS
  code. If you need to assert or retract facts from an action, use the clipspyx
  Python API (e.g., `env.assert_string(...)`) rather than CLIPS syntax.

- **libcst is required.** The `dsl` extra must be installed. Without it,
  importing `clipspyx.dsl` will raise an `ImportError`.

- **Variables inside scoped CEs are not accessible.** Variables bound inside
  `forall`, `exists`, or `not` CEs cannot be used in `__action__` because CLIPS
  scopes them to the CE.
