"""DSL Template and constants for timer events."""

from clipspyx.dsl.template import Template
from clipspyx.values import Symbol

AFTER = Symbol('after')
AT = Symbol('at')
EVERY = Symbol('every')


class TimerEvent(Template):
    """Timer event template for use in DSL rules.

    Use in rule patterns with ``goal()`` to request timers::

        class MyRule(Rule):
            goal(TimerEvent(kind=Symbol("after"), name=Symbol("my-timer"), seconds=5.0))

    Kinds:
        - ``Symbol("after")``: fire after ``seconds`` delay
        - ``Symbol("at")``: fire at absolute ``time`` (Unix epoch)
        - ``Symbol("every")``: fire every ``seconds`` (periodic)
    """
    __clips_name__ = 'timer-event'
    kind: Symbol
    name: Symbol
    seconds: float = 0.0
    time: float = 0.0
    count: int = 0
    fired_at: float = 0.0
