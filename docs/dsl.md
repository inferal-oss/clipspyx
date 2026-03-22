# clipspyx DSL

A Python-native DSL for defining CLIPS templates and rules. Instead of writing
raw CLIPS syntax strings, you write annotated Python classes that compile to
CLIPS constructs at define-time.

## RHS: effects vs. Python actions

Rules can express their right-hand side in two ways:

- **Declarative effects** (`asserts`, `retracts`, `modifies`) generate native
  CLIPS RHS code. No Python bridge is involved: the CLIPS engine executes the
  assert/retract/modify directly. This is faster and makes side effects visible
  to static analysis and visualization.

- **Python actions** (`__action__` method) run arbitrary Python code when the
  rule fires. The DSL bridges them into CLIPS through a generated deffunction.
  When a rule fires, CLIPS calls the bridge function, which passes bound
  variables into your Python method.

Use effects when the rule only needs to assert, retract, or modify facts. Use
`__action__` when you need Python's full language (string formatting, library
calls, I/O, exception handling). The two cannot be combined in a single rule.

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

### Custom CLIPS names

By default, a template's CLIPS name is `module.ClassName` (see
[Module-qualified names](#module-qualified-names)). Set `__clips_name__` to
override it:

```python
class Person(Template):
    __clips_name__ = "person"
    name: str
    age: int = 0
```

This generates `(deftemplate person ...)` instead of `(deftemplate myapp.Person ...)`.
Useful when integrating with existing CLIPS code that expects specific names.

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

### NIL / None

Python's `None` and the DSL constant `NIL` both produce the CLIPS `nil` value:

```python
Person(name=None)           # (name nil)
Person(name=NIL)            # (name nil)
Person(name=not None)       # (name ~nil)
Person(name=None or "x")    # (name nil|"x")
name is None                # (test (eq ?name nil))
name is not None            # (test (neq ?name nil))
```

Import `NIL` from the DSL module:

```python
from clipspyx.dsl import NIL
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

## Multifield patterns

For multislot matching, the DSL uses Python's `...` (Ellipsis) for multifield
wildcards and `*name` (star unpacking) for multifield variables.

### Multifield wildcard

Use `...` to match zero or more fields without binding:

```python
Person(hobbies=...)         # (hobbies $?)
```

### Multifield variable

Use `*name` inside a tuple to bind zero or more fields:

```python
Person(hobbies=(*h,))       # (hobbies $?h) — binds entire multislot
```

The variable is available in `__action__` as a Python tuple:

```python
class ListHobbies(Rule):
    Person(name=name, hobbies=(*h,))

    def __action__(self):
        for hobby in self.h:  # h is a tuple
            print(hobby)
```

### Sequence patterns

Combine multifield variables, single-field variables, literals, and wildcards
in a tuple to match specific patterns:

```python
# Match multislot containing "chess" anywhere
Person(hobbies=(*before, "chess", *after))
# (hobbies $?before "chess" $?after)

# Match multislot starting with "chess"
Person(hobbies=("chess", *rest))
# (hobbies "chess" $?rest)

# Extract a single element with context
Data(items=(*before, x, *after))
# (items $?before ?x $?after)

# Mix single-field wildcard, literal, and multifield wildcard
Data(items=(_, "chess", ...))
# (items ? "chess" $?)
```

### Multifield variables in effects

Multifield variables can be used in declarative effects:

```python
class CopyItems(Rule):
    d = Data(items=(*h,))
    asserts(Output(items=(*h,)))
```

This generates:
```clips
(assert (mod.Output (items $?h)))
```

## Declarative effects

Instead of writing an `__action__` method, a rule can declare its RHS effects
directly in the class body using `asserts()`, `retracts()`, and `modifies()`.
These generate native CLIPS RHS code with no Python bridge function, which is
faster and makes the rule's side effects visible to static analysis and
visualization.

**Effects and `__action__` are mutually exclusive.** A rule can use one or the
other, not both. Combining them raises `TypeError` at class creation time.

### asserts()

Assert a new fact when the rule fires:

```python
class DeriveGreeting(Rule):
    Person(name=name)
    asserts(Greeting(msg=name))
```

```clips
(defrule myapp.DeriveGreeting
  (myapp.Person (name ?name))
  =>
  (assert (myapp.Greeting (msg ?name))))
```

Slot values support literals, bound variables, and arithmetic expressions:

```python
class IncrementCounter(Rule):
    c = Counter(value=v)
    retracts(c)
    asserts(Counter(value=v + 1))
```

### retracts()

Retract a matched fact. The argument must be a pattern variable (from an
assigned pattern):

```python
class RemovePerson(Rule):
    p = Person(name="Bob")
    retracts(p)
```

```clips
(defrule myapp.RemovePerson
  ?p <- (myapp.Person (name "Bob"))
  =>
  (retract ?p))
```

### modifies()

Modify slots on a matched fact. The first argument is a pattern variable;
keyword arguments specify the new slot values:

```python
class Promote(Rule):
    e = Employee(name=name, level=level)
    level >= 5
    modifies(e, title="Senior")
```

```clips
(defrule myapp.Promote
  ?e <- (myapp.Employee (name ?name) (level ?level))
  (test (>= ?level 5))
  =>
  (modify ?e (title "Senior")))
```

### Multiple effects

A rule can declare any number of effects, including multiple effects of the
same kind:

```python
class TransferDepartment(Rule):
    e = Employee(name=name)
    old = Assignment(employee=name, dept="Sales")
    retracts(old)
    asserts(Assignment(employee=name, dept="Engineering"))
    asserts(AuditLog(action="transfer", employee=name))
    modifies(e, title="Transferred")
```

### Visualization

Effects appear in diagrams as distinct edge types:

| Effect | Edge style | Color |
|--------|-----------|-------|
| `asserts` | Solid, width 2 | Red |
| `retracts` | Dashed, width 1 | Red |
| `modifies` | Solid, width 2 | Orange |

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

## Ordering constraints

Instead of assigning numeric salience values manually, you can declare
relative ordering between rules using `before()`, `after()`, and
`concurrent()`. The DSL computes salience values automatically from a
topological sort of the ordering graph.

**Ordering and `__salience__` are mutually exclusive.** A rule can use one or
the other, not both. Combining them raises `TypeError` at class creation time.

### before() and after()

Declare that a rule should fire before or after another rule:

```python
from clipspyx.dsl import Rule, before, after

class ValidateInput(Rule):
    before(ProcessInput)
    Input(data=data)

    def __action__(self):
        print(f"Validating: {self.data}")

class ProcessInput(Rule):
    Input(data=data)

    def __action__(self):
        print(f"Processing: {self.data}")

class LogResult(Rule):
    after(ProcessInput)
    Input(data=data)

    def __action__(self):
        print(f"Logged: {self.data}")
```

`ValidateInput` fires before `ProcessInput`, and `LogResult` fires after it.
The DSL assigns salience values (e.g. 2, 1, 0) to enforce this order.

Ordering is transitive: if A is before B and B is before C, then A fires
before C. You do not need to declare every pair explicitly.

### concurrent()

Declare that two rules should have the same salience (fire in arbitrary order
relative to each other):

```python
from clipspyx.dsl import Rule, after, concurrent

class NotifyEmail(Rule):
    after(ProcessInput)
    concurrent(NotifySlack)
    Input(data=data)

    def __action__(self):
        print(f"Email: {self.data}")

class NotifySlack(Rule):
    after(ProcessInput)
    Input(data=data)

    def __action__(self):
        print(f"Slack: {self.data}")
```

Both notification rules fire after `ProcessInput` but in either order relative
to each other.

Concurrent groups are transitive: if A is concurrent with B and B is concurrent
with C, all three share the same salience.

### Forward references

Ordering targets can reference rules that have not been defined yet. The DSL
defers rule building until all targets are resolvable:

```python
class B(Rule):
    after(A)
    Person(name=name)

    def __action__(self):
        print("B")

class A(Rule):
    Person(name=name)

    def __action__(self):
        print("A")

env = Environment()
env.define(B)  # deferred: A not yet defined
env.define(A)  # triggers finalization: both rules built with correct salience
```

If `env.run()` is called while ordering rules are still unresolved, it raises
`OrderingError` listing the pending rules.

### Cycle detection

Circular ordering dependencies are detected and reported:

```python
class X(Rule):
    before(Y)
    Person(name=name)

class Y(Rule):
    before(X)  # cycle: X -> Y -> X
    Person(name=name)
```

This raises `OrderingCycleError` with the cycle path when finalization runs.

### Cross-module ordering

Rules can reference rules from other modules. Import the target rule class and
use it directly:

```python
# module_a.py
class Validate(Rule):
    Input(data=data)
    def __action__(self):
        ...

# module_b.py
from module_a import Validate
from clipspyx.dsl import Rule, after

class Process(Rule):
    after(Validate)
    Input(data=data)
    def __action__(self):
        ...
```

For rules in the same module, you can reference them by class name even before
they are defined (forward references are resolved at `define()` time).

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
| `None` or `NIL` | `nil` | Field: CLIPS nil value |
| `not None` | `~nil` | Field: slot is not nil |
| `name is None` | `(test (eq ?name nil))` | Test CE: identity check |
| `name is not None` | `(test (neq ?name nil))` | Test CE: identity check |
| `not "Bob"` | `~"Bob"` | Field: slot is not this value |
| `25 or 30 or 35` | `25\|30\|35` | Field: one of these values |
| `x and x > 5` | `?x&:(> ?x 5)` | Field: bind + predicate |
| `_` | `?` | Field: anonymous wildcard |
| `...` | `$?` | Multifield: zero or more fields |
| `(*h,)` | `$?h` | Multifield: bind all fields |
| `(*a, "x", *b)` | `$?a "x" $?b` | Multifield: sequence pattern |
| `__salience__ = 10` | `(declare (salience 10))` | Rule priority (manual) |
| `before(OtherRule)` | `(declare (salience N))` | Ordering: fire before target |
| `after(OtherRule)` | `(declare (salience N))` | Ordering: fire after target |
| `concurrent(OtherRule)` | `(declare (salience N))` | Ordering: same salience as target |
| `asserts(T(slot=val))` | `(assert (mod.T (slot val)))` | Effect: assert fact |
| `retracts(p)` | `(retract ?p)` | Effect: retract matched fact |
| `modifies(p, slot=val)` | `(modify ?p (slot val))` | Effect: modify matched fact |
| `__clips_name__ = "x"` | `(deftemplate x ...)` | Override CLIPS name |
| `P = env.define(Person)` | — | Bound asserter (primary) |
| `Person(__env__=env, ...)` | — | Direct assertion (fallback) |
| `Fact` | `FACT-ADDRESS` | Slot/multislot type: any fact |
| `Multi[Fact]` | `(multislot ... (type FACT-ADDRESS))` | Multislot of fact addresses |
| `env.enable_tracing()` | — | Enable provenance tracking |

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

## Fact provenance tracing

When tracing is enabled, clipspyx automatically records which facts each rule
consumed and produced. Every rule firing creates a `RuleFiring` fact containing
the rule name, input facts (from the LHS), and output facts (asserted on the
RHS). This works for both `__action__` and declarative-effect rules.

### Enabling tracing

```python
from clipspyx import Environment
from clipspyx.dsl import Template, Rule
from clipspyx.tracing import RuleFiring

env = Environment()
env.enable_tracing()

# define templates and rules as usual...
```

Call `env.enable_tracing()` before defining rules. This registers the
`RuleFiring` template and installs C-level callbacks that track fact assertions
during rule execution.

### RuleFiring facts

Each rule firing produces a `RuleFiring` fact with three slots:

| Slot | Type | Description |
|------|------|-------------|
| `rule` | `SYMBOL` | Qualified name of the rule that fired |
| `inputs` | `FACT-ADDRESS` multislot | Facts that matched the rule's LHS |
| `outputs` | `FACT-ADDRESS` multislot | Facts asserted during the rule's RHS |

```python
env.run()

for f in env.facts():
    if f.template.name == 'RuleFiring':
        print(f"Rule: {f['rule']}")
        print(f"  Inputs:  {[i.index for i in f['inputs']]}")
        print(f"  Outputs: {[o.index for o in f['outputs']]}")
```

### Walking the provenance chain

Since inputs and outputs are fact addresses, you can trace any fact back to its
origins:

```python
def trace_origins(env, fact):
    """Walk RuleFiring facts backwards to find all ancestor facts."""
    firings = [f for f in env.facts() if f.template.name == 'RuleFiring']
    visited = set()
    queue = [fact.index]
    chain = []

    while queue:
        idx = queue.pop(0)
        if idx in visited:
            continue
        visited.add(idx)
        for firing in firings:
            if idx in [o.index for o in firing['outputs']]:
                chain.append(firing)
                for inp in firing['inputs']:
                    queue.append(inp.index)
    return chain
```

### Using RuleFiring in DSL rules

`RuleFiring` is a standard DSL Template. Import it from `clipspyx.tracing` and
use it in your own rules to reason about provenance in-engine:

```python
from clipspyx.tracing import RuleFiring

class CountFirings(Rule):
    RuleFiring(rule=rule_name)

    def __action__(self):
        print(f"Rule fired: {self.rule_name}")
```

### The Fact type

The `Fact` sentinel type enables `FACT-ADDRESS` typed slots and multislots for
any template, not just references to a specific template:

```python
from clipspyx.dsl import Template, Multi, Fact

class FactPair(Template):
    left: Fact       # single FACT-ADDRESS slot (any template)
    right: Fact

class FactBag(Template):
    items: Multi[Fact]  # FACT-ADDRESS multislot
```

### How it works

When tracing is enabled:

1. The DSL injects implicit fact-address bindings (`?_ce0 <-`, etc.) for
   unassigned patterns so every matched fact has a variable
2. A `__dsl_trace_begin` bridge call is prepended to every rule's RHS, passing
   the rule name and all input fact addresses
3. A C-level `AddAssertFunction` callback captures every fact asserted during
   the RHS as an output
4. When the next rule fires (or `run()` returns), the accumulated inputs and
   outputs are asserted as a `RuleFiring` fact

This mechanism is uniform: it works identically for `__action__` rules and
declarative effects. `RuleFiring` facts themselves are excluded from tracing
to prevent infinite recursion.

### Disabling tracing

```python
env.disable_tracing()
```

When tracing is disabled (the default), there is zero overhead: no implicit
bindings, no callbacks, no `RuleFiring` facts.

## Limitations

- **Source must be in a file.** The parser uses `inspect.getsource()`, so rules
  defined in the REPL or via `python -c` will fail. Rules must live in `.py`
  files.

- **Effects and `__action__` are mutually exclusive.** A rule can use declarative
  effects (`asserts`, `retracts`, `modifies`) or a Python `__action__` method,
  but not both. For complex actions that combine fact manipulation with arbitrary
  Python logic, use `__action__` with the clipspyx Python API.

- **libcst is required.** The `dsl` extra must be installed. Without it,
  importing `clipspyx.dsl` will raise an `ImportError`.

- **Variables inside scoped CEs are not accessible.** Variables bound inside
  `forall`, `exists`, or `not` CEs cannot be used in `__action__` because CLIPS
  scopes them to the CE.

- **Ordering and `__salience__` are mutually exclusive.** A rule using
  `before()`, `after()`, or `concurrent()` cannot also set `__salience__`.

- **All ordering targets must be defined before `env.run()`.** If any ordering
  rule references a target that was never `define()`d, `env.run()` raises
  `OrderingError`.
