# CLIPS Reasoning Guide

This guide teaches how to **think about** rule-based systems using the clipspyx
Python DSL. It does not repeat syntax; see `dsl.md` for DSL reference and
`clips-reference/` for the full CLIPS language specification.

Every example uses the Python DSL. If you need raw CLIPS syntax, consult the
reference docs.

**Version compatibility.** Most of this guide applies to both CLIPS 6.4x and
7.0x backends. Sections marked **(7.0x)** require `uv sync --extra 70x`.
Features unique to 7.0x: `goal()`, `explicit()`, `AsyncRunner`, `TimerEvent`,
and custom goal handlers. Everything else works on both backends.

### How to read this guide

| Goal | Start here |
|------|-----------|
| **Build something now** | [Transformations](#transformations-imperative-to-rules) -- pick the pattern closest to your problem |
| **Understand the paradigm** | [The Paradigm Shift](#the-paradigm-shift-imperative-to-declarative) -- read top to bottom through [Execution Cycle](#the-execution-cycle-what-happens-during-envrun) |
| **Design your fact model** | [Designing Facts](#designing-facts-data-modeling-for-rule-systems) |
| **Control rule ordering** | [Ordering and Salience](#ordering-and-salience) |
| **Write rule actions** | [Effects vs. Actions](#effects-vs-actions-choosing-the-right-rhs) then [The `__action__` Method](#the-__action__-method-python-inside-rules) |
| **Read results from Python** | [Querying Facts](#reading-results-querying-facts-after-envrun) |
| **Debug a broken pipeline** | [Debugging](#debugging-when-rules-dont-fire) |
| **Add async I/O** | [Async Workflows](#async-workflows-using-asyncio-with-the-inference-engine-70x) **(7.0x)** |
| **Avoid common mistakes** | [Anti-Patterns](#anti-patterns-and-common-mistakes) |
| **Quick lookup** | [DSL to Concept Map](#quick-reference-dsl-to-concept-map) (bottom of guide) |

---

## The Paradigm Shift: Imperative to Declarative

In imperative code, you control **when** things happen. You write loops,
conditionals, and function calls in a specific order. The program counter moves
through your code line by line.

In a rule-based system, you declare **what** should happen **given certain
conditions**. The inference engine decides when and in what order rules fire.
You give up explicit control flow and gain automatic reactivity.

### Translation anchors

If you already know these systems, CLIPS maps directly:

| You know | CLIPS equivalent |
|----------|-----------------|
| SQL tables | Facts (flat tuples in working memory) |
| SQL triggers / materialized views | Rules (react to data changes) |
| SQL WHERE + JOIN | Rule conditions (pattern matching across facts) |
| RxJS / reactive streams | Working memory is the observable; rules are subscriptions |
| Event-driven architecture | Asserting a fact = emitting an event; rules = handlers |
| Prolog | Forward chaining (data-driven) instead of backward chaining (goal-driven) |

### The three components

**Working memory (fact list).** The current state of the world. A flat collection
of typed tuples. Think of it as an in-memory database with no indexes.

**Knowledge base (rules).** Declarative statements: "when these conditions hold
across the facts, do this." Rules do not call each other. They react to facts.

**Inference engine (Rete network).** Continuously matches rules against facts.
When conditions are satisfied, the rule is placed on the agenda. The engine
picks the highest-priority activation and fires it. Firing may assert, retract,
or modify facts, which triggers more matching. This continues until the agenda
is empty.

In the DSL:

```python
from clipspyx import Environment
from clipspyx.dsl import Template, Rule

# Working memory schema
class Temperature(Template):
    sensor: str
    value: float

class Alert(Template):
    sensor: str
    level: str

# Knowledge base
class HighTempAlert(Rule):
    Temperature(sensor=name, value=temp)
    temp > 100.0
    asserts(Alert(sensor=name, level="critical"))

# Inference engine
env = Environment()
env.define(Temperature)
env.define(Alert)
env.define(HighTempAlert)
env.reset()

# Seed working memory
Temperature(__env__=env, sensor="boiler-1", value=150.0)

# Hand control to the engine
env.run()
```

After `env.run()`, the engine matches `Temperature(sensor="boiler-1", value=150.0)`
against the rule's conditions, finds `temp=150.0 > 100.0`, fires the rule, and
asserts `Alert(sensor="boiler-1", level="critical")`.

You did not call `HighTempAlert`. You did not loop over temperatures. The engine
did the work.

---

## The Execution Cycle: What Happens During `env.run()`

Understanding the execution cycle is prerequisite for everything that follows.

### The recognize-act cycle

Each iteration of `env.run()`:

1. **Match.** The Rete network identifies all (rule, fact-set) pairs where the
   rule's conditions are satisfied. Each pair is called an **activation**.
2. **Select.** The conflict resolution strategy picks one activation from the
   **agenda** (the queue of pending activations). Default strategy: highest
   salience first, then depth (LIFO) for ties.
3. **Execute.** The selected rule fires. Its right-hand side runs: asserting,
   retracting, or modifying facts, or calling Python code.
4. **Repeat.** Fact changes from step 3 cause the Rete network to update.
   New activations may appear; existing ones may vanish. Go to step 1.
5. **Stop.** When the agenda is empty (no activations remain), `env.run()` returns.

### Rete: incremental matching

The Rete network is a compiled dataflow graph of your rule conditions. When you
assert a fact, only the portions of the network relevant to that fact type are
evaluated. This means:

- Adding one fact does not re-evaluate all rules against all facts.
- Pattern matching cost is proportional to the change, not the total fact count.
- This is what makes rule systems practical with thousands of facts.

You do not need to understand Rete's internals to use CLIPS. But knowing that
matching is incremental helps you understand why the system is efficient and why
fact granularity matters (see "Designing Facts" later).

### Activations and the agenda

A single rule can produce **multiple activations** if its conditions match
multiple fact combinations. For example, if you have 3 `Temperature` facts above
100, the `HighTempAlert` rule appears on the agenda 3 times, once per matching
fact.

The agenda is ordered:
1. Higher salience fires first (default salience is 0).
2. Within the same salience, the **depth strategy** (LIFO) fires the most
   recently activated rule first.

### Refraction: the most surprising behavior

**A rule will not fire twice for the same set of matching facts.**

Once `HighTempAlert` fires for the fact `Temperature(sensor="boiler-1", value=150.0)`,
it will not fire again for that same fact, even if you call `env.run()` again.
This prevents infinite loops and is fundamental to how rule systems terminate.

Refraction is reset when:
- A matching fact is **retracted** and re-asserted.
- A matching fact is **modified** (modify = retract + assert internally).

This means `modifies(p, value=new_val)` will cause rules to re-evaluate
the modified fact, but simply calling `env.run()` again will not re-fire
rules for unchanged facts.

### Concrete trace

```python
class Counter(Template):
    value: int

class Doubler(Rule):
    c = Counter(value=v)
    v < 100
    retracts(c)
    asserts(Counter(value=v * 2))

class Reporter(Rule):
    Counter(value=v)
    v >= 100
    def __action__(self):
        print(f"Final value: {self.v}")
```

Seed with `Counter(value=10)` and call `env.run()`:

| Cycle | Agenda | Fires | Facts after |
|-------|--------|-------|-------------|
| 1 | Doubler(v=10) | Doubler | Counter(value=20) |
| 2 | Doubler(v=20) | Doubler | Counter(value=40) |
| 3 | Doubler(v=40) | Doubler | Counter(value=80) |
| 4 | Doubler(v=80) | Doubler | Counter(value=160) |
| 5 | Reporter(v=160) | Reporter | Counter(value=160), prints "Final value: 160" |
| 6 | (empty) | - | env.run() returns |

Each cycle, Doubler retracts the old Counter and asserts a new one. The new
fact triggers fresh matching (refraction is satisfied because it is a new fact).
When the value reaches 160, `v < 100` fails for Doubler but `v >= 100` succeeds
for Reporter.

---

## Transformations: Imperative to Rules

This section is the core of the guide. Each subsection shows imperative Python
code and its DSL equivalent. The goal: when you see an imperative pattern,
you can recognize which rule-based pattern replaces it.

### 4a. Conditional classification

**Imperative:**

```python
def classify_reading(sensor_name: str, value: float) -> str:
    if value > 100:
        return "critical"
    elif value > 75:
        return "warning"
    else:
        return "normal"

# Usage: for each sensor, call classify_reading and store result
for sensor in sensors:
    level = classify_reading(sensor.name, sensor.value)
    alerts.append(Alert(sensor.name, level))
```

**DSL:**

```python
class Sensor(Template):
    name: str
    value: float

class Alert(Template):
    sensor: str
    level: str

class CriticalAlert(Rule):
    Sensor(name=name, value=val)
    val > 100
    asserts(Alert(sensor=name, level="critical"))

class WarningAlert(Rule):
    Sensor(name=name, value=val)
    val > 75
    ~Alert(sensor=name)  # don't double-alert
    asserts(Alert(sensor=name, level="warning"))

class NormalAlert(Rule):
    Sensor(name=name, value=val)
    val <= 75
    asserts(Alert(sensor=name, level="normal"))
```

**What changed:**
- The `if/elif/else` chain became three separate rules, each handling one case.
- No loop. The engine processes every Sensor fact automatically.
- Each rule is independent. Adding a new classification level means adding a
  new rule, not modifying an existing function.
- The `~Alert(sensor=name)` negation prevents WarningAlert from firing if
  CriticalAlert already produced an alert for that sensor.

### 4b. Loop and accumulate

**Imperative:**

```python
def total_order_value(orders: list[Order]) -> float:
    total = 0.0
    for order in orders:
        total += order.amount
    return total
```

**DSL:**

```python
class Order(Template):
    id: str
    amount: float

class OrderTotal(Template):
    total: float

class Counted(Template):
    order_id: str

class AccumulateOrder(Rule):
    o = Order(id=oid, amount=amt)
    ~Counted(order_id=oid)
    t = OrderTotal(total=current)
    retracts(t)
    asserts(OrderTotal(total=current + amt))
    asserts(Counted(order_id=oid))
```

**Setup:** Assert `OrderTotal(total=0.0)` as the initial accumulator during
`env.reset()` (via a deffacts or manual assertion). Assert all Order facts.
Call `env.run()`.

**What changed:**
- The `for` loop became a rule that fires once per uncounted Order.
- The `Counted` template is a **guard fact** preventing double-counting
  (replacing the implicit "iterator position" of the imperative loop).
- The accumulator (`OrderTotal`) is explicitly represented as a fact.
  Each firing retracts the old total and asserts the new one.
- The engine drives the iteration. When all Orders have corresponding
  Counted facts, the rule's conditions no longer match and it stops.

### 4c. State machine

**Imperative:**

```python
class OrderProcessor:
    def __init__(self):
        self.state = "received"

    def process(self, order):
        match self.state:
            case "received":
                if self.validate(order):
                    self.state = "validated"
                else:
                    self.state = "rejected"
            case "validated":
                self.check_inventory(order)
                self.state = "checked"
            case "checked":
                self.fulfill(order)
                self.state = "fulfilled"
```

**DSL:**

```python
from clipspyx.values import Symbol

class Order(Template):
    id: str
    item: str
    qty: int

class Phase(Template):
    name: Symbol

class Inventory(Template):
    item: str
    stock: int

class Validated(Template):
    order_id: str

class Fulfilled(Template):
    order_id: str

class ValidateOrder(Rule):
    Phase(name=Symbol("validate"))
    o = Order(id=oid, item=item, qty=qty)
    Inventory(item=item, stock=stock)
    qty <= stock
    asserts(Validated(order_id=oid))

class AdvanceToFulfill(Rule):
    p = Phase(name=Symbol("validate"))
    exists(Validated(order_id=_))
    retracts(p)
    asserts(Phase(name=Symbol("fulfill")))

class FulfillOrder(Rule):
    Phase(name=Symbol("fulfill"))
    v = Validated(order_id=oid)
    o = Order(id=oid, item=item, qty=qty)
    inv = Inventory(item=item, stock=stock)
    retracts(v)
    modifies(inv, stock=stock - qty)
    asserts(Fulfilled(order_id=oid))
```

**What changed:**
- The `match self.state:` switch became a `Phase` template. Each rule includes
  `Phase(name=Symbol("..."))` as a gating condition.
- State transitions are explicit: retract old Phase, assert new Phase.
- Each phase's logic is a separate rule. Adding a new phase means adding rules,
  not modifying a switch statement.
- Multiple orders can be validated in parallel (all fire during the "validate"
  phase). The phase only advances when at least one is validated.

### 4d. Function call chain (pipeline)

**Imperative:**

```python
def process_event(raw_event):
    validated = validate(raw_event)
    if validated is None:
        return
    enriched = enrich(validated)
    routed = route(enriched)
    return routed

def validate(event):
    if event.get("type") is None:
        return None
    return {**event, "valid": True}

def enrich(event):
    return {**event, "timestamp": now(), "source": lookup_source(event["id"])}

def route(event):
    destination = "fast" if event["priority"] == "high" else "batch"
    return {**event, "destination": destination}
```

**DSL:**

```python
class RawEvent(Template):
    id: str
    type: str
    priority: str

class ValidatedEvent(Template):
    id: str
    type: str
    priority: str

class EnrichedEvent(Template):
    id: str
    type: str
    priority: str
    source: str

class RoutedEvent(Template):
    id: str
    destination: str

class ValidateEvent(Rule):
    RawEvent(id=eid, type=etype, priority=pri)
    asserts(ValidatedEvent(id=eid, type=etype, priority=pri))

class EnrichEvent(Rule):
    ValidatedEvent(id=eid, type=etype, priority=pri)
    def __action__(self):
        source = lookup_source(self.eid)
        EnrichedEvent(__env__=self.__env__,
                      id=self.eid, type=self.etype,
                      priority=self.pri, source=source)

class RouteHighPriority(Rule):
    EnrichedEvent(id=eid, priority="high")
    asserts(RoutedEvent(id=eid, destination="fast"))

class RouteLowPriority(Rule):
    EnrichedEvent(id=eid, priority=pri)
    pri != "high"
    asserts(RoutedEvent(id=eid, destination="batch"))
```

**What changed:**
- The call chain `validate() -> enrich() -> route()` became a **fact chain**.
  Each rule consumes one fact type and produces the next.
- The chain emerges from data dependencies, not function calls. `EnrichEvent`
  fires because `ValidatedEvent` exists, not because `ValidateEvent` called it.
- Each step is independently testable and replaceable.
- New processing steps can be inserted by adding rules that consume/produce
  the appropriate fact types. No existing rules need modification.
- The `EnrichEvent` rule uses `__action__` because it needs to call external
  Python code (`lookup_source`). The others use pure declarative effects.

### 4e. "When something is missing" checks

**Imperative:**

```python
def find_students_without_grades(students, grades):
    graded = {g.student_id for g in grades}
    for student in students:
        if student.id not in graded:
            send_reminder(student)
```

**DSL:**

```python
class Student(Template):
    id: str
    name: str

class Grade(Template):
    student_id: str
    score: int

class Reminder(Template):
    student_id: str

class MissingGrade(Rule):
    Student(id=sid, name=name)
    ~Grade(student_id=sid)
    asserts(Reminder(student_id=sid))
```

**What changed:**
- The set difference (`graded = {g.student_id for g in grades}`) became a
  negated pattern: `~Grade(student_id=sid)`.
- No loop. The engine automatically checks every Student against every Grade.
- The rule is **reactive**: if a Grade is asserted later for a student who
  had a Reminder, the MissingGrade rule will not re-fire (refraction), but
  you could use `logical()` to auto-retract the Reminder.

With truth maintenance:

```python
class MissingGrade(Rule):
    logical(Student(id=sid, name=name))
    ~Grade(student_id=sid)
    asserts(Reminder(student_id=sid))
```

Now if the Student fact is retracted, the Reminder is automatically retracted
too. No cleanup code needed.

### 4f. "All items must satisfy" (universal quantification)

**Imperative:**

```python
def is_department_certified(dept_id, employees, certifications):
    dept_employees = [e for e in employees if e.dept == dept_id]
    if not dept_employees:
        return False
    return all(
        any(c.employee_id == e.id for c in certifications)
        for e in dept_employees
    )
```

**DSL:**

```python
class Employee(Template):
    id: str

class Certification(Template):
    employee_id: str

class AllCertified(Template):
    pass

class CheckAllCertified(Rule):
    forall(
        Employee(id=eid),
        Certification(employee_id=eid)
    )
    asserts(AllCertified())
```

Note: variables inside `forall()` (like `eid`) are **scoped** -- they are
not visible on the RHS. You cannot use them in `asserts()` or `__action__`.
This is because `forall` tests a universal property across all matching
facts, not a single fact's values.

If you need per-group universals (e.g., "all employees in department X
are certified"), use a separate condition outside `forall` to bind the
group key, and a negation pattern to check for uncertified members:

```python
class Department(Template):
    name: str

class DeptCertified(Template):
    dept: str

class CheckDeptCertified(Rule):
    """Fires once per department where no uncertified employee exists."""
    Department(name=dept)
    ~Employee(dept=dept, id=eid) | ~Certification(employee_id=eid)
    # alternative: use __action__ to iterate and check
    asserts(DeptCertified(dept=dept))
```

**What changed:**
- The nested `all()` + `any()` comprehension became either `forall()` (for
  global universals) or negation patterns (for per-group universals).
- `forall(Employee(...), Certification(...))` means: "for every Employee,
  there exists a matching Certification." The rule fires only when this
  holds universally.
- The rule fires **once** when the universal condition is satisfied, not
  once per employee.
- If a new uncertified employee is added, the activation is removed from
  the agenda (or the fact can be auto-retracted if using truth maintenance).

### 4g. Cleanup on dependency removal (truth maintenance)

**Imperative:**

```python
class DiscountManager:
    def __init__(self):
        self.discounts = {}  # membership_id -> discount

    def add_membership(self, member_id, tier):
        discount = self.calculate_discount(tier)
        self.discounts[member_id] = discount

    def remove_membership(self, member_id):
        # Manual cleanup: must remember to do this everywhere
        if member_id in self.discounts:
            del self.discounts[member_id]

    def calculate_discount(self, tier):
        return {"gold": 0.2, "silver": 0.1}.get(tier, 0.0)
```

**DSL:**

```python
class Membership(Template):
    member_id: str
    tier: str

class Discount(Template):
    member_id: str
    rate: float

class GoldDiscount(Rule):
    logical(Membership(member_id=mid, tier="gold"))
    asserts(Discount(member_id=mid, rate=0.2))

class SilverDiscount(Rule):
    logical(Membership(member_id=mid, tier="silver"))
    asserts(Discount(member_id=mid, rate=0.1))
```

**What changed:**
- The manual `remove_membership` cleanup is gone entirely.
- `logical(Membership(...))` marks the Membership fact as the **logical
  support** for the Discount. When the Membership is retracted, the engine
  automatically retracts the Discount.
- No `del`, no tracking dictionary, no risk of forgetting cleanup.
- This eliminates an entire class of bugs: stale derived data from removed
  source data.

### 4h. Multi-step async workflow (7.0x goals + timers)

**Imperative:**

```python
import asyncio

async def escalation_workflow(ticket_id):
    # Wait 5 minutes
    await asyncio.sleep(300)

    # Check if still open
    ticket = await db.get_ticket(ticket_id)
    if ticket.status != "open":
        return

    # Escalate
    await db.update_ticket(ticket_id, status="escalated")
    await notify_manager(ticket_id)
```

**DSL (CLIPS 7.0x):**

```python
from clipspyx.dsl import Template, Rule, TimerEvent
from clipspyx.values import Symbol

class Ticket(Template):
    id: Symbol
    status: Symbol

class Escalated(Template):
    ticket_id: Symbol

class HandleTimerGoal(Rule):
    goal(TimerEvent(kind=k, name=n, seconds=s))

class EscalateStaleTicket(Rule):
    t = Ticket(id=tid, status=Symbol("open"))
    te = TimerEvent(
        kind=Symbol("after"), name=Symbol("escalate"), seconds=300.0)
    asserts(Escalated(ticket_id=tid))
```

**What changed:**
- `asyncio.sleep(300)` became a `TimerEvent` fact with `kind=Symbol("after")`.
- The timer is **demand-driven**: when the rule needs a TimerEvent that does
  not exist, CLIPS 7.0x generates a **goal**. The async runtime creates an OS
  timer. When it fires, it asserts the TimerEvent fact, satisfying the goal
  and allowing the rule to fire.
- The "check if still open" logic is implicit: the rule only matches tickets
  with `status=Symbol("open")`. If the ticket's status changes before the
  timer fires, the activation is removed.
- Multiple tickets create multiple independent timers automatically.
- Use `AsyncRunner` instead of `env.run()` to enter the async loop (see [Async Workflows](#async-workflows-using-asyncio-with-the-inference-engine-70x)).

---

## Designing Facts: Data Modeling for Rule Systems

Good fact design makes rules simple. Bad fact design makes rules impossible.

### Facts are flat tuples, not objects

Facts have no methods, no inheritance (in 6.4x), no encapsulation. Think of
them as database rows or event records. Each fact is identified by its template
and slot values.

### Template naming: `__clips_name__`

By default, a template's CLIPS name is `{module}.{classname}` -- for example,
`__main__.Temperature` when defined in a script. This is fine for most uses,
but can be awkward when querying facts with `env.find_template()`. Override
with `__clips_name__`:

```python
class Temperature(Template):
    __clips_name__ = "Temperature"  # instead of "__main__.Temperature"
    sensor: str
    value: float
```

Use `__clips_name__` when: you use `find_template()` to query facts, you
build multi-module systems where template names must be stable, or you want
readable CLIPS output for debugging.

### The granularity question

**Split templates when different rules need different subsets of information.**

A `Person` template with 15 slots means every rule mentioning `Person`
participates in matching all Person facts. If only 2 of those slots matter
to a particular rule, the other 13 are wasted work.

Rule of thumb: if you find yourself using `_` (wildcard) for most slots in
a pattern, the template is too broad.

### Three kinds of facts

| Kind | Purpose | Example |
|------|---------|---------|
| **Data facts** | Represent the problem domain | `Sensor`, `Order`, `Employee` |
| **Control facts** | Represent computation state | `Phase`, `ProcessingComplete` |
| **Derived facts** | Conclusions produced by rules | `Alert`, `Discount`, `Validated` |

Separating these is a fundamental design decision. Data facts are seeded from
external input. Control facts manage rule execution flow. Derived facts are
the system's output.

### Typed fact-address slots

When one fact references another, you have two options:

```python
# Option 1: shared key (loose coupling)
class Department(Template):
    name: str
    head_name: str  # references Employee by name

# Option 2: fact address (tight coupling, type-checked)
class Department(Template):
    name: str
    head: Employee  # direct reference to Employee fact
```

Use fact addresses when you need to navigate between facts in rules or
actions. Use shared keys when the relationship is used purely for matching.

---

## Ordering and Salience

### Default: let the engine decide

If rule execution order does not affect correctness, do not specify salience.
Most rules should have default salience (0). The engine's conflict resolution
strategy handles the rest.

### Declarative ordering: `before()` and `after()`

When order matters between specific rules, use the DSL's ordering constraints:

```python
from clipspyx.dsl import before, after

class ValidateFirst(Rule):
    Order(id=oid)
    def __action__(self):
        print(f"Validating {self.oid}")

class FulfillSecond(Rule):
    after(ValidateFirst)
    Order(id=oid)
    def __action__(self):
        print(f"Fulfilling {self.oid}")
```

The DSL computes salience values automatically from the ordering graph. Prefer
this over numeric salience because it makes intent explicit.

### `concurrent()`: same-priority grouping

`concurrent(TargetRule)` gives a rule the same salience as its target. Use it
when two rules are alternatives at the same pipeline stage (e.g., multiple
auth rules that each handle a different case):

```python
class AuthWithToken(Rule):
    Request(id=rid, token=tok)
    Token(value=tok, user=user)
    asserts(AuthResult(request_id=rid, user=user))

class AuthMissingToken(Rule):
    concurrent(AuthWithToken)
    Request(id=rid, token="")
    ~AuthResult(request_id=rid)
    asserts(AuthResult(request_id=rid, user=""))
```

**Use `after()` for pipeline stages, not `concurrent()`.** If you want
"validation runs after auth," use `after(AuthRule)` on the validation rule.
`concurrent()` is for rules that should fire at the **same** priority level,
not for sequencing stages.

### Numeric `__salience__`

Use sparingly, for always-first or always-last rules:

```python
class AlwaysCheckSafety(Rule):
    __salience__ = 1000  # fires before anything else
    DangerousCondition(level=lvl)
    def __action__(self):
        self.__env__.halt()

class CleanupLast(Rule):
    __salience__ = -1000  # fires after everything else
    Phase(name=Symbol("done"))
    def __action__(self):
        print("All processing complete")
```

### Anti-pattern: salience as control flow

If you find yourself assigning 10+ different salience levels to enforce a
specific execution order, you are fighting the engine. Use control facts
(Phase template) or modules instead.

---

## Effects vs. Actions: Choosing the Right RHS

### Declarative effects: `asserts()`, `retracts()`, `modifies()`

- **Faster**: no Python bridge; CLIPS executes natively.
- **Visible**: static analysis and `env.visualize()` can see the data flow.
- **Limited**: can only assert, retract, or modify facts.

### Python actions: `__action__` method

- **Full power**: I/O, complex computation, library calls.
- **Opaque**: visualization cannot see what the action does.
- **Bridged**: each firing crosses the Python/CLIPS boundary.

### Rule of thumb

If the rule's effect can be expressed as asserting, retracting, or modifying
facts, use declarative effects. If it needs Python's full language (string
formatting, HTTP calls, database queries, logging), use `__action__`.

Never combine both in one rule (the DSL enforces this). If you need both
fact manipulation and Python code, split into two rules: one with effects
that produces a trigger fact, and one with an action that matches the trigger.

### String values in effects

String slot values in `asserts()` and `modifies()` are embedded in CLIPS
syntax. Strings containing double quotes (e.g., JSON) are automatically
escaped. This works:

```python
asserts(Response(body='{"status": "ok"}'))
```

Strings containing backslashes are also escaped. No special handling needed.

---

## Reading Results: Querying Facts After `env.run()`

After the engine runs, you read results by inspecting working memory.

### Find facts by template

```python
tpl = env.find_template("Alert")  # uses the CLIPS name (see __clips_name__)
for fact in tpl.facts():
    print(fact["sensor"], fact["level"])
```

`find_template()` takes the CLIPS template name (string). `facts()` returns
an iterator over all asserted facts of that template.

### Access slot values

Facts behave like dicts:

```python
fact["sensor"]       # slot value by name
fact["level"]        # another slot
```

### Iterate all facts

```python
for fact in env.facts():
    print(fact.template.name, fact)
```

`env.facts()` yields every fact in working memory, including internal facts.
Filter by `fact.template.name` to find what you need.

### Retract or modify from Python

```python
fact.retract()                    # remove from working memory
fact.modify_slots(level="critical")  # update (resets refraction)
```

Modifications take effect immediately. If you modify a fact and call
`env.run()` again, rules will re-evaluate against the modified fact.

---

## The `__action__` Method: Python Inside Rules

When a rule uses `__action__`, the method receives bound variables and fact
references via `self`:

```python
class ProcessOrder(Rule):
    o = Order(id=oid, amount=amt)  # assigned pattern: binds 'o', 'oid', 'amt'
    Customer(order_id=oid, name=name)  # unassigned: binds 'name'
    amt > 100

    def __action__(self):
        # Bound variables from pattern slots
        print(self.oid)    # str: the order ID
        print(self.amt)    # int/float: the amount
        print(self.name)   # str: customer name

        # Bound fact references (from assigned patterns)
        print(self.o)              # the Order fact object
        print(self.o["amount"])    # access slots on the fact

        # Environment access
        env = self.__env__

        # Assert new facts from __action__
        Result(__env__=env, order_id=self.oid, status="processed")

        # Retract/modify bound facts
        self.o.retract()
        # or: self.o.modify_slots(amount=0)
```

### Key rules

- **`self.varname`**: every variable bound in the LHS is available
- **`self.factvar`**: assigned patterns (`o = Order(...)`) give access to
  the fact object, supporting `retract()` and `modify_slots()`
- **`self.__env__`**: the CLIPS Environment, for asserting new facts or
  calling environment methods
- **Assert via `Template(__env__=env, ...)`**: the standard way to create
  facts from inside an action
- **Effects and `__action__` are mutually exclusive**: the DSL enforces this
  at parse time

---

## Observability: Tracing and Fact Events

Rule systems are declarative: you say what should happen, not when. This makes
debugging harder -- there is no call stack to step through. clipspyx provides
two built-in mechanisms to make the engine's behavior visible.

### Tracing: which rules fired, with what inputs and outputs

`env.enable_tracing()` causes the engine to record a `RuleFiring` fact each
time a rule fires:

```python
from clipspyx.tracing import RuleFiring

env.enable_tracing()
env.reset()
# ... assert facts, run ...
env.run()

for fact in env.facts():
    if fact.template.name == "RuleFiring":
        print(f"Rule: {fact['rule']}")
        print(f"  Inputs:  {fact['inputs']}")   # list of matched facts
        print(f"  Outputs: {fact['outputs']}")   # list of asserted facts
```

Each `RuleFiring` fact records the rule name, the facts that triggered it
(inputs), and the facts it produced (outputs). This gives you a complete
provenance chain: for any derived fact, you can trace back through the
RuleFiring records to see which rules produced it and what data they consumed.

**When to use:** Debugging unexpected behavior ("why did this rule fire?"),
auditing ("what sequence of rules produced this decision?"), or building
explanation systems ("the loan was rejected because rule X matched facts Y
and Z").

### Fact events: reacting to the fact lifecycle

`env.enable_fact_events()` causes the engine to assert meta-facts whenever
facts are asserted, retracted, or modified:

```python
from clipspyx.fact_events import FactAsserted, FactRetracted, FactModified

env.enable_fact_events()

# Rules can now match on fact lifecycle events
class LogNewAlert(Rule):
    FactAsserted(template=Symbol("Alert"), fact=f)
    def __action__(self):
        print(f"Alert created: {self.f}")

class LogRemovedAlert(Rule):
    FactRetracted(template=Symbol("Alert"), index=idx)
    def __action__(self):
        print(f"Alert {self.idx} was retracted")
```

The three meta-fact templates:

| Template | Slots | When |
|----------|-------|------|
| `FactAsserted` | `fact` (address), `index`, `template` (symbol) | After a fact is asserted |
| `FactRetracted` | `index`, `template` (symbol), `ppform` (string) | After a fact is retracted |
| `FactModified` | `fact` (address), `old_index`, `old_ppform`, `template` | After a fact is modified |

**When to use:** Building reactive logging, audit trails, change-data-capture
pipelines, or synchronizing external systems with working memory. Unlike
tracing (which records rule firings), fact events record data changes
regardless of whether a rule or Python code caused them.

### Combining both

Tracing tells you **why** something happened (which rules fired). Fact events
tell you **what** changed (which facts were created, modified, or removed).
Together they give full visibility into the engine's behavior:

```python
env.enable_tracing()
env.enable_fact_events()
```

For production monitoring, you would typically write rules that match
`RuleFiring` or `FactAsserted` events and push them to an external system
(logging, metrics, event store) via `__action__` methods.

---

## Debugging: When Rules Don't Fire

Rule systems fail silently: a rule that doesn't match simply doesn't fire.
There is no error, no exception, no stack trace. Here are the common symptoms
and how to diagnose them.

### "My rule never fires"

**Check conditions one at a time.** The most common cause is one condition
that doesn't match. Print all facts before `env.run()` to verify the data
you expect is actually in working memory:

```python
for fact in env.facts():
    tpl = fact.template
    if tpl is not None:
        print(f"  {tpl.name}: {fact}")
```

Then check each condition in the rule against the actual facts. Variable
bindings must match across conditions: if `Request(id=rid)` binds `rid` and
`AuthResult(request_id=rid)` uses it, the `request_id` value must be the
exact same string as the `id` value.

### "My rule fires when it shouldn't"

**Check salience/ordering.** If a fallback rule fires before the rule that
should have blocked it, the ordering is wrong. Print effective salience:

```python
for r in env.rules():
    s = str(r)
    if "salience" in s:
        import re
        m = re.search(r'salience (-?\d+)', s)
        print(f"  {r.name}: salience {m.group(1)}")
    else:
        print(f"  {r.name}: salience 0 (default)")
```

### "My rule fires once but I expected it again"

**Refraction.** A rule will not fire twice for the same set of facts. If
you need re-evaluation, modify or retract+reassert the triggering fact.
See the "Refraction" section earlier in this guide.

### "The `__action__` doesn't seem to do anything"

**Check the action actually runs.** Add `print("FIRED")` as the first line.
If it doesn't print, the issue is in the conditions, not the action. If it
does print, the issue is in the action body (check `self.varname` values).

### Useful debugging patterns

```python
# Count rules fired
n = env.run()
print(f"Rules fired: {n}")  # 0 means no conditions matched

# Enable tracing for full provenance
env.enable_tracing()
env.run()
for f in env.facts():
    if f.template and f.template.name == "RuleFiring":
        print(f"  {f['rule']}: {f['inputs']} -> {f['outputs']}")
```

---

## Worked Example 1: Loan Approval System

A complete system that classifies loan applicants and produces approval or
rejection decisions.

### Imperative version

```python
def process_application(applicant):
    score = applicant["credit_score"]
    income = applicant["income"]
    amount = applicant["requested_amount"]
    dti = amount / income if income > 0 else float("inf")

    if score >= 750 and dti <= 3.0:
        return {"applicant": applicant["name"], "decision": "approved",
                "reason": "excellent credit, low DTI"}
    elif score >= 650 and dti <= 4.0:
        return {"applicant": applicant["name"], "decision": "review",
                "reason": "good credit, moderate DTI"}
    else:
        return {"applicant": applicant["name"], "decision": "rejected",
                "reason": "insufficient credit or high DTI"}

# Process all applications
for app in applications:
    result = process_application(app)
    results.append(result)
```

### DSL version

```python
from clipspyx import Environment
from clipspyx.dsl import Template, Rule
from clipspyx.values import Symbol

class Applicant(Template):
    name: str
    credit_score: int
    income: float
    requested_amount: float

class DTI(Template):
    applicant: str
    ratio: float

class Decision(Template):
    applicant: str
    result: Symbol
    reason: str

# Step 1: Compute derived data
class ComputeDTI(Rule):
    Applicant(name=name, income=inc, requested_amount=amt)
    inc > 0
    asserts(DTI(applicant=name, ratio=amt / inc))

# Step 2: Classification rules (independent, order doesn't matter)
class ApproveExcellent(Rule):
    Applicant(name=name, credit_score=score)
    score >= 750
    DTI(applicant=name, ratio=dti)
    dti <= 3.0
    asserts(Decision(applicant=name, result=Symbol("approved"),
                     reason="excellent credit, low DTI"))

class FlagForReview(Rule):
    Applicant(name=name, credit_score=score)
    score >= 650
    score < 750
    DTI(applicant=name, ratio=dti)
    dti <= 4.0
    ~Decision(applicant=name)
    asserts(Decision(applicant=name, result=Symbol("review"),
                     reason="good credit, moderate DTI"))

class Reject(Rule):
    Applicant(name=name, credit_score=score)
    DTI(applicant=name, ratio=dti)
    score < 650 or dti > 4.0
    ~Decision(applicant=name)
    asserts(Decision(applicant=name, result=Symbol("rejected"),
                     reason="insufficient credit or high DTI"))
```

Note: the `score < 650 or dti > 4.0` in Reject uses the DSL's `or` on test
CEs (field-level or). In practice, you might split this into two rules for
clarity. The `~Decision(applicant=name)` guard prevents multiple decisions
for the same applicant.

### Execution trace

Seed: `Applicant(name="Alice", credit_score=780, income=80000, requested_amount=200000)`

| Cycle | Rule | Effect |
|-------|------|--------|
| 1 | ComputeDTI | Asserts DTI(applicant="Alice", ratio=2.5) |
| 2 | ApproveExcellent | Asserts Decision(applicant="Alice", result=approved, ...) |
| 3 | (agenda empty) | env.run() returns |

FlagForReview and Reject do not fire because `~Decision(applicant="Alice")`
fails after cycle 2.

Add a second applicant: `Applicant(name="Bob", credit_score=600, income=50000, requested_amount=300000)`

| Cycle | Rule | Effect |
|-------|------|--------|
| 1 | ComputeDTI | Asserts DTI(applicant="Bob", ratio=6.0) |
| 2 | Reject | Asserts Decision(applicant="Bob", result=rejected, ...) |

Bob's DTI of 6.0 exceeds 4.0 and his credit score is below 650. Both rules
for Alice and Bob run independently; the engine processes all applicants
without an explicit loop.

---

## Worked Example 2: Server Monitoring with Truth Maintenance

A monitoring system that classifies alerts, tracks counts, and automatically
cleans up alerts when conditions normalize.

### Imperative version

```python
class Monitor:
    def __init__(self):
        self.alerts = {}       # server -> alert level
        self.alert_counts = {} # server -> count of alerts raised

    def process_reading(self, server, cpu, memory):
        if cpu > 90 or memory > 90:
            level = "critical"
        elif cpu > 70 or memory > 70:
            level = "warning"
        else:
            # Condition normalized: manual cleanup
            if server in self.alerts:
                del self.alerts[server]
            return

        self.alerts[server] = level
        self.alert_counts[server] = self.alert_counts.get(server, 0) + 1

    def get_alert(self, server):
        return self.alerts.get(server)
```

### DSL version

```python
from clipspyx import Environment
from clipspyx.dsl import Template, Rule
from clipspyx.values import Symbol

class Reading(Template):
    server: str
    cpu: float
    memory: float

class Alert(Template):
    server: str
    level: Symbol

class AlertCount(Template):
    server: str
    count: int

# Classification rules with truth maintenance
class CriticalAlert(Rule):
    logical(Reading(server=srv, cpu=cpu, memory=mem))
    cpu > 90 or mem > 90
    asserts(Alert(server=srv, level=Symbol("critical")))

class WarningAlert(Rule):
    logical(Reading(server=srv, cpu=cpu, memory=mem))
    cpu > 70 or mem > 70
    ~Alert(server=srv)  # don't override critical
    asserts(Alert(server=srv, level=Symbol("warning")))

# Count alerts (no truth maintenance here: counts persist)
class IncrementAlertCount(Rule):
    Alert(server=srv)
    ~AlertCount(server=srv)
    asserts(AlertCount(server=srv, count=1))

class BumpAlertCount(Rule):
    Alert(server=srv)
    c = AlertCount(server=srv, count=n)
    retracts(c)
    asserts(AlertCount(server=srv, count=n + 1))
```

### Truth maintenance in action

1. Assert `Reading(server="web-1", cpu=95, memory=60)`.
2. CriticalAlert fires, asserts `Alert(server="web-1", level=critical)`.
3. IncrementAlertCount fires, asserts `AlertCount(server="web-1", count=1)`.

Now the reading normalizes:
4. Retract the old Reading, assert `Reading(server="web-1", cpu=40, memory=30)`.
5. Because the old Reading was the `logical()` support for the Alert, the engine
   **automatically retracts** `Alert(server="web-1", level=critical)`.
6. No cleanup code ran. No `del self.alerts[server]`. The engine handled it.
7. CriticalAlert and WarningAlert conditions no longer match (cpu=40, memory=30
   are below thresholds), so no new alert is asserted.

The `AlertCount` persists because it was not created with `logical()`. This is
intentional: we want to track the cumulative count of alerts even after they
resolve.

### Key patterns used

- **Truth maintenance** (`logical()`): automatic cleanup of derived facts.
- **Negation** (`~Alert(server=srv)`): prevents WarningAlert from overriding
  CriticalAlert.
- **Accumulation**: AlertCount tracks running totals.
- **No explicit cleanup**: the imperative version's `del self.alerts[server]`
  is entirely replaced by truth maintenance.

---

## Anti-Patterns and Common Mistakes

### Imperative sequencing via facts

**Wrong:**
```python
class Step1(Template):
    data: str

class Step2(Template):
    data: str

class DoStep1(Rule):
    asserts(Step1(data="processed"))

class DoStep2(Rule):
    s = Step1(data=d)
    retracts(s)
    asserts(Step2(data=d))
```

This forces sequential execution through fact chaining, but the intent is
really a pipeline. If you find yourself naming facts `Step1`, `Step2`, `Step3`,
you are encoding control flow in data.

**Better:** Use meaningful fact names that represent the actual state of the
data (`Validated`, `Enriched`, `Routed`), or use a Phase control fact to gate
execution stages.

### Infinite loops from modify

**Wrong:**
```python
class Incrementer(Rule):
    c = Counter(value=v)
    modifies(c, value=v + 1)
```

This rule fires, modifies the Counter (which resets refraction), matches again,
modifies again, forever. The engine runs until you hit a cycle limit.

**Fix:** Add a termination condition:

```python
class Incrementer(Rule):
    c = Counter(value=v)
    v < 100
    modifies(c, value=v + 1)
```

### Over-binding variables

**Wrong:**
```python
class CheckSensor(Rule):
    Sensor(name=name, location=location, unit=unit, calibration=cal, value=val)
    val > 100
    asserts(Alert(sensor=name))
```

You bound `location`, `unit`, and `cal` but never use them. This forces the
engine to track those bindings.

**Fix:** Use wildcards for unused slots:

```python
class CheckSensor(Rule):
    Sensor(name=name, value=val)
    val > 100
    asserts(Alert(sensor=name))
```

Only mention the slots you actually need. Unmentioned slots are implicitly
wildcarded.

### God template

**Wrong:**
```python
class Entity(Template):
    type: str
    name: str
    age: int
    salary: float
    department: str
    manager: str
    location: str
    status: str
    priority: int
    created: str
    updated: str
    # ... 15+ slots
```

Every rule that mentions `Entity` participates in matching against every
Entity fact. If you have 1000 entities and 20 rules, that is a lot of
unnecessary matching.

**Fix:** Split into focused templates:

```python
class Employee(Template):
    name: str
    department: str

class EmployeeStatus(Template):
    name: str
    status: str

class EmployeeSalary(Template):
    name: str
    salary: float
```

Rules that only care about status do not participate in salary matching.

### Salience spaghetti

**Wrong:**
```python
class Rule1(Rule):
    __salience__ = 100
    # ...

class Rule2(Rule):
    __salience__ = 90
    # ...

class Rule3(Rule):
    __salience__ = 85
    # ...

# ... 10 more rules with carefully calibrated salience values
```

This is imperative control flow disguised as salience. Adding a new rule
requires understanding and adjusting the entire salience hierarchy.

**Fix:** Use `before()`/`after()` for local ordering, or Phase control facts
for staged execution. Reserve numeric salience for truly global priorities
(safety checks, final cleanup).

### Python logic that should be rules

**Wrong:**
```python
class ProcessOrder(Rule):
    Order(id=oid, amount=amt)
    def __action__(self):
        if self.amt > 10000:
            # This should be a rule condition
            HighValueOrder(__env__=self.__env__, id=self.oid)
        elif self.amt > 1000:
            MediumValueOrder(__env__=self.__env__, id=self.oid)
        else:
            LowValueOrder(__env__=self.__env__, id=self.oid)
```

The `if/elif/else` inside `__action__` is doing classification, which is exactly
what rule conditions are for.

**Fix:** Three separate rules with appropriate conditions:

```python
class HighValue(Rule):
    Order(id=oid, amount=amt)
    amt > 10000
    asserts(HighValueOrder(id=oid))

class MediumValue(Rule):
    Order(id=oid, amount=amt)
    amt > 1000
    amt <= 10000
    asserts(MediumValueOrder(id=oid))

class LowValue(Rule):
    Order(id=oid, amount=amt)
    amt <= 1000
    asserts(LowValueOrder(id=oid))
```

### Ignoring refraction

**Symptom:** "My rule fired once but I expected it to fire again."

A rule will not fire twice for the same set of matching facts. If you assert
`Sensor(value=50)` and a rule fires for it, the rule will not fire again for
that same fact even if you call `env.run()` again.

**If you need re-evaluation:** modify the fact (`modifies(s, value=new_val)`)
or retract and re-assert it. Modify resets refraction for that fact.

---

## Async Workflows: Using asyncio with the Inference Engine (7.0x)

CLIPS 7.0x adds backward chaining (goals), and clipspyx's `AsyncRunner` bridges
goals to Python's asyncio. This lets rules **wait** for external events: timers,
HTTP responses, database queries, or any async operation.

### The imperative mindset vs. goal-driven rules

**Imperative:**

```python
async def process_ticket(ticket_id):
    ticket = await db.get_ticket(ticket_id)
    if ticket.status == "open":
        await asyncio.sleep(300)  # wait 5 minutes
        ticket = await db.get_ticket(ticket_id)
        if ticket.status == "open":  # still open?
            await escalate(ticket_id)
```

**DSL (goal-driven):**

```python
from clipspyx.dsl import Template, Rule, TimerEvent
from clipspyx.values import Symbol

class Ticket(Template):
    id: Symbol
    status: Symbol

class Escalated(Template):
    ticket_id: Symbol

# Goal handler rule: tells CLIPS to generate goals for TimerEvent
class HandleTimerGoal(Rule):
    goal(TimerEvent(kind=k, name=n, seconds=s))

# Consuming rule: needs a timer fact that does not yet exist
class EscalateStale(Rule):
    t = Ticket(id=tid, status=Symbol("open"))
    te = TimerEvent(
        kind=Symbol("after"), name=Symbol("escalate"), seconds=300.0)
    asserts(Escalated(ticket_id=tid))
```

The rule says: "when a ticket is open AND 5 minutes have passed, escalate it."
CLIPS generates a goal for the missing `TimerEvent`. The async runtime creates
an OS timer. When it fires, the fact is asserted and the rule activates.

If the ticket's status changes to `"closed"` before the timer fires, the rule's
conditions no longer match. CLIPS retracts the goal. The async runtime cancels
the pending timer. No wasted work.

### Running the async loop with AsyncRunner

`AsyncRunner` is the resource context for async goal handling. It auto-enables
goal handlers on creation and disables them on `close()`. Use it as an async
context manager to ensure proper cleanup.

```python
import asyncio
from clipspyx import Environment
from clipspyx.async_goals import AsyncRunner

env = Environment()

# Define templates and rules...
env.define(Ticket)
env.define(Escalated)
env.define(HandleTimerGoal)
env.define(EscalateStale)
env.reset()

# Seed facts
Ticket(__env__=env, id=Symbol("T-1"), status=Symbol("open"))

# Run until all goals are satisfied and agenda is empty
async def main():
    async with AsyncRunner(env) as runner:
        result = await runner.run()
    # result is one of: "completed", "max_cycles", "halted", "stopped"

asyncio.run(main())
```

The `async with` block handles the full lifecycle: enabling goal handlers,
running the inference loop, and cleaning up all tasks on exit.

### Waiting for specific rules to fire

A common need: run the async loop until a particular rule produces its output,
then inspect the result from Python.

**Pattern 1: Run to completion, then query facts.**

```python
async def main():
    # ... setup env, define templates/rules, assert initial facts ...

    async with AsyncRunner(env) as runner:
        result = await runner.run()

        # After run returns, query the fact list
        escalated = list(env.find_template("Escalated").facts())
        for e in escalated:
            print(f"Escalated ticket: {e['ticket_id']}")
```

This is the simplest approach. `runner.run()` runs until no goals remain and
the agenda is empty, then you read the results.

**Pattern 2: Use `max_cycles` for incremental processing.**

```python
async def main():
    # ... setup ...

    async with AsyncRunner(env) as runner:
        while True:
            result = await runner.run(max_cycles=1)

            # Check for a specific fact after each cycle
            results = list(env.find_template("Escalated").facts())
            if results:
                print(f"Found escalation: {results[0]['ticket_id']}")
                break

            if result == "completed":
                print("No escalations needed")
                break
```

Each cycle fires one round of goals + rules. You can inspect state between
cycles and break early when the fact you are waiting for appears.

**Pattern 3: Stop from inside a rule with `halt_async()`.**

```python
class NotifyAndStop(Rule):
    Escalated(ticket_id=tid)
    def __action__(self):
        print(f"Escalated {self.tid}, stopping async loop")
        self.__env__.halt_async()

async def main():
    async with AsyncRunner(env) as runner:
        # runner.run() returns "halted" when halt_async() is called
        result = await runner.run()
        assert result == "halted"

asyncio.run(main())
```

The rule itself decides when to stop the loop. Useful when a terminal condition
is naturally expressed as a rule (e.g., "stop when any critical alert exists").

**Pattern 4: External shutdown with `runner.close()`.**

```python
async def main():
    async with AsyncRunner(env) as runner:
        # External shutdown after a delay
        async def shutdown_after_delay():
            await asyncio.sleep(60)
            await runner.close()

        asyncio.create_task(shutdown_after_delay())
        result = await runner.run()
```

You can also use `asyncio.wait_for(runner.run(), timeout=...)` for simple
timeouts. This lets Python code outside the rule system control when the loop
ends. Useful for integrating with web servers, CLI tools, or other async
frameworks.

### Custom goal handlers: coroutines vs. generators

Handlers registered via `runner.register_handler()` come in two flavors:

**Coroutine handlers** (regular async functions) are one-shot and per-goal.
They run once, assert a fact, and complete. They finish when the goal they
serve is fulfilled.

**Generator handlers** (async functions with `yield`) are persistent and
per-template. They survive across `runner.run()` calls and handle their own
cleanup via try/finally. The bare `yield` is what encodes persistence: each
`yield` suspends the generator, lets the runner call `env.run()` to process
whatever facts were asserted, then resumes the generator for the next iteration.

Here is a coroutine handler for one-shot HTTP fetches:

```python
class FetchRequest(Template):
    url: str

class FetchResponse(Template):
    url: str
    status: int

class HandleFetchGoal(Rule):
    goal(FetchRequest(url=u))

async def fetch_handler(goal, env):
    url = str(goal['url'])
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    FetchRequest(__env__=env, url=url)
    FetchResponse(__env__=env, url=url, status=resp.status_code)

async def main():
    async with AsyncRunner(env) as runner:
        runner.register_handler(FetchRequest, fetch_handler)
        result = await runner.run()
```

Now any rule can request an HTTP fetch by including `FetchRequest(url=...)` in
its conditions. If no matching fact exists, CLIPS generates a goal, the handler
fetches the URL, and asserts both the request (satisfying the goal) and the
response (for downstream rules).

```python
class CheckHealthEndpoint(Rule):
    Service(name=svc, health_url=url)
    FetchResponse(url=url, status=status)
    status != 200
    asserts(ServiceDown(name=svc))
```

This rule reads as: "when a service has a health URL and fetching it returns
non-200, mark the service as down." The fetch happens automatically via the
goal mechanism. No imperative orchestration.

### The try/finally generator pattern

Generator handlers are the right tool for long-lived or repeating async work.
The key insight: `yield` suspends the generator, and try/finally scopes
resources to the yield point. When the generator resumes (normal path) or is
cancelled (`close()` path), the finally block runs, providing guaranteed
cleanup in all cases.

Here is a generator handler that streams data and cleans up on each iteration:

```python
class StreamEvent(Template):
    data: Symbol

class HandleStreamGoal(Rule):
    goal(StreamEvent(data=d))

async def stream_handler(goal, env):
    # Assert the initial fact to satisfy the goal
    StreamEvent(__env__=env, data=Symbol("stream-data"))
    # Then loop, yielding after each batch of work
    for i in range(10):
        await asyncio.sleep(0.02)
        collected.append(f"item-{i}")
        yield  # suspend: runner calls env.run(), then resumes us
```

The bare `yield` is what makes this persistent. Without it, the handler would
be a regular coroutine: one-shot, completing once the goal is fulfilled.

For resources that need cleanup between iterations, wrap the yield in
try/finally:

```python
async def polling_handler(goal, env):
    SensorReading(__env__=env, value=0)  # satisfy the goal
    count = 0
    while True:
        try:
            reading = await sensor.read()
            fact = SensorReading(__env__=env, value=reading)
            yield  # suspend: runner processes the fact via env.run()
        finally:
            # Runs on resume (normal) OR on close/cancellation
            if fact.exists:
                fact.retract()
        count += 1
```

The lifecycle:

1. `yield` suspends the generator. The runner calls `env.run()`.
2. On resume, the `finally` block runs first, retracting the old fact.
3. The next loop iteration reads a new sensor value and asserts a new fact.
4. On `close()` (runner shutdown), the `finally` block also runs, ensuring cleanup.

This is Python's standard generator cleanup guarantee applied to async goal
handlers. The generator owns its full lifecycle; the runner is not involved
in cleanup.

### Periodic work with `EVERY` timers

```python
class PollConfig(Template):
    interval: float

class PollResult(Template):
    tick: int

class HandleTimerGoal(Rule):
    goal(TimerEvent(kind=k, name=n, seconds=s))

class PollEvery(Rule):
    PollConfig(interval=iv)
    te = TimerEvent(
        kind=Symbol("every"), name=Symbol("poll"), seconds=iv, count=c)
    asserts(PollResult(tick=c))

class StopPolling(Rule):
    PollResult(tick=t)
    t >= 10
    def __action__(self):
        self.__env__.halt_async()
```

The `EVERY` timer fires repeatedly. The `count` slot increments each time.
`StopPolling` halts the loop after 10 ticks. Without a stop condition,
`EVERY` timers run indefinitely.

### Key differences from imperative async

| Imperative async | Goal-driven rules |
|-----------------|-------------------|
| `await asyncio.sleep(5)` | `TimerEvent(kind=Symbol("after"), seconds=5.0)` |
| `await fetch(url)` | Custom goal handler + `FetchRequest(url=...)` |
| `if condition: cancel()` | Retract controlling fact; CLIPS cancels automatically |
| `asyncio.gather(t1, t2)` | Multiple independent goals dispatch concurrently |
| `while True: poll()` | `TimerEvent(kind=Symbol("every"), ...)` |
| `try/except` | `GoalHandlerError` wraps handler exceptions |
| Resource cleanup in `finally` | Generator handler with try/finally around `yield` |

The fundamental shift: in imperative async, you orchestrate the sequence of
operations. In goal-driven rules, you declare what facts are needed and the
runtime figures out how and when to produce them.

### Async servers inside the rule loop

The examples above show CLIPS reaching out (timers, HTTP fetches). The
pattern works in reverse: external systems push facts **into** the `AsyncRunner`
loop, turning the rule engine into the application's main event loop.

The mechanism: an `asyncio.Queue` bridges an HTTP server to a goal handler.
The server puts request dicts on the queue. The goal handler awaits them and
asserts facts. Rules process the pipeline. A terminal rule delivers the
response via a `Future` and retracts the request, which triggers the next
goal.

```python
request_queue: asyncio.Queue = asyncio.Queue()
response_futures: dict[str, asyncio.Future] = {}

# Goal rule: tells CLIPS to generate goals for missing HttpRequest facts
class HandleHttpGoal(Rule):
    goal(HttpRequest(id=rid, method=m, path=p, body=b, token=t))

# Goal handler (generator): blocks until a request arrives, then asserts it.
# The bare yield makes this persistent: it loops waiting for requests.
async def http_goal_handler(goal, env):
    while True:
        data = await request_queue.get()
        HttpRequest(__env__=env, **data)
        yield  # suspend: runner processes the request via env.run()

# Terminal rule: deliver response, retract request (triggers next goal)
class SendResponse(Rule):
    req = HttpRequest(id=rid)
    HttpResponse(request_id=rid, status_code=code, body=body)

    def __action__(self):
        future = response_futures.pop(str(self.rid), None)
        if future and not future.done():
            future.set_result({"status": int(self.code), "body": str(self.body)})
        self.req.retract()  # no HttpRequest -> goal fires -> handler awaits next
```

The loop emerges from the rules: retract request -> goal fires -> handler
blocks on queue -> next request arrives -> assert -> rules fire -> repeat. No
`while True` in the application code, no explicit iteration.

The HTTP server is a thin producer that knows nothing about rules:

```python
async def handle(request):
    rid = str(uuid.uuid4())
    future = asyncio.get_event_loop().create_future()
    response_futures[rid] = future
    await request_queue.put({"id": rid, "method": request.method, ...})
    result = await future
    return web.Response(status=result["status"], body=result["body"])
```

Start the server, then hand control to the engine:

```python
async def main():
    await start_http_server(port=8080)
    async with AsyncRunner(env) as runner:
        runner.register_handler(HttpRequest, http_goal_handler)
        await runner.run()  # the rule engine IS the main loop
```

**Why this matters.** HTTP requests, timers, database events, and message queue
consumers are all just goal handlers that produce facts. Rules process them
uniformly. Adding a new event source (WebSocket, cron, file watcher) means
one goal handler and one goal rule -- no changes to existing processing rules.

---

## Quick Reference: DSL to Concept Map

| DSL Construct | Reasoning Concept | Imperative Equivalent |
|---------------|-------------------|----------------------|
| `class X(Template)` | Define a fact schema | `@dataclass` / named tuple |
| `class R(Rule)` body | Declare conditions | `if` chain + loop over data |
| `Pattern(slot=var)` | Match + bind variable | `for item in items` + assignment |
| `var op value` (test CE) | Filter condition | `if var > value` |
| `asserts(X(...))` | Derive new fact | `results.append(...)` |
| `retracts(p)` | Remove fact | `del items[idx]` |
| `modifies(p, slot=val)` | Update fact (resets refraction) | `item.slot = val` |
| `~Pattern(...)` | Negation as failure | `if item not in collection` |
| `exists(Pattern(...))` | Fire once if any match | `if any(...)` |
| `forall(P1, P2)` | Universal quantification | `if all(...)` |
| `logical(Pattern(...))` | Truth maintenance | Manual cleanup callbacks |
| `before(R)` / `after(R)` | Execution ordering | Function call order |
| `goal(Pattern(...))` | Backward chaining (7.0x) | `await some_async_fn()` |
| `env.run()` | Run inference engine | `while work_to_do: process()` |
| `env.enable_tracing()` | Record rule provenance | Logging / audit trail |
| `env.enable_fact_events()` | React to fact lifecycle | Observer pattern callbacks |
| `AsyncRunner(env)` | Async resource context (7.0x) | `asyncio.run(server.serve_forever())` |
| `env.visualize()` | Architecture diagram | Manual documentation |
