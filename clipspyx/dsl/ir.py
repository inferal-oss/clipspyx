from dataclasses import dataclass, field


# --- Template IR ---

@dataclass
class SlotDef:
    name: str
    multi: bool
    clips_type: str | None
    default: object = None
    has_default: bool = False
    fact_template: str | None = None
    description: str | None = None


@dataclass
class TemplateDef:
    name: str
    slots: list[SlotDef]


# --- Rule IR: Slot-level constraints ---

@dataclass
class Var:
    name: str

    def to_clips(self) -> str:
        return f'?{self.name}'


@dataclass
class Wildcard:
    def to_clips(self) -> str:
        return '?'


@dataclass
class Literal:
    value: object

    def to_clips(self) -> str:
        if isinstance(self.value, str):
            return f'"{self.value}"'
        return str(self.value)


@dataclass
class NotConstraint:
    inner: object

    def to_clips(self) -> str:
        return f'~{self.inner.to_clips()}'


@dataclass
class OrConstraint:
    alternatives: list

    def to_clips(self) -> str:
        return '|'.join(a.to_clips() for a in self.alternatives)


@dataclass
class AndConstraint:
    parts: list

    def to_clips(self) -> str:
        return '&'.join(p.to_clips() for p in self.parts)


@dataclass
class PredicateConstraint:
    var: str
    clips_expr: str

    def to_clips(self) -> str:
        return f'?{self.var}&:({self.clips_expr})'


# --- Rule IR: Conditional elements ---

@dataclass
class SlotConstraint:
    name: str
    constraint: object

    def to_clips(self) -> str:
        return f'({self.name} {self.constraint.to_clips()})'


@dataclass
class PatternCE:
    template_name: str
    slots: list[SlotConstraint] = field(default_factory=list)
    label: str | None = None
    description: str | None = None

    def to_clips(self) -> str:
        if self.slots:
            slots_str = ' '.join(s.to_clips() for s in self.slots)
            return f'({self.template_name} {slots_str})'
        return f'({self.template_name})'


@dataclass
class AssignedPatternCE:
    var_name: str
    pattern: PatternCE
    label: str | None = None
    description: str | None = None

    def to_clips(self) -> str:
        return f'?{self.var_name} <- {self.pattern.to_clips()}'


@dataclass
class TestCE:
    __test__ = False  # prevent pytest collection
    clips_expr: str
    label: str | None = None
    description: str | None = None

    def to_clips(self) -> str:
        return f'(test ({self.clips_expr}))'


@dataclass
class NotCE:
    pattern: PatternCE
    label: str | None = None
    description: str | None = None

    def to_clips(self) -> str:
        return f'(not {self.pattern.to_clips()})'


@dataclass
class OrCE:
    alternatives: list
    label: str | None = None
    description: str | None = None

    def to_clips(self) -> str:
        alts = ' '.join(a.to_clips() for a in self.alternatives)
        return f'(or {alts})'


@dataclass
class ExistsCE:
    elements: list
    label: str | None = None
    description: str | None = None

    def to_clips(self) -> str:
        elems = ' '.join(e.to_clips() for e in self.elements)
        return f'(exists {elems})'


@dataclass
class ForallCE:
    initial: PatternCE
    conditions: list
    label: str | None = None
    description: str | None = None

    def to_clips(self) -> str:
        parts = [self.initial.to_clips()]
        parts.extend(c.to_clips() for c in self.conditions)
        return f'(forall {" ".join(parts)})'


@dataclass
class LogicalCE:
    elements: list
    label: str | None = None
    description: str | None = None

    def to_clips(self) -> str:
        elems = ' '.join(e.to_clips() for e in self.elements)
        return f'(logical {elems})'


@dataclass
class GoalCE:
    pattern: PatternCE
    label: str | None = None
    description: str | None = None

    def to_clips(self) -> str:
        return f'(goal {self.pattern.to_clips()})'


@dataclass
class ExplicitCE:
    pattern: PatternCE
    label: str | None = None
    description: str | None = None

    def to_clips(self) -> str:
        return f'(explicit {self.pattern.to_clips()})'


# --- Rule IR: Top level ---

@dataclass
class RuleDef:
    name: str
    conditions: list
    action_func_name: str
    bound_vars: list[str] = field(default_factory=list)
    pattern_vars: list[str] = field(default_factory=list)
    salience: int | None = None
