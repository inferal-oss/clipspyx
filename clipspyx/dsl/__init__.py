from clipspyx.dsl.types import Multi, Fact
from clipspyx.dsl.template import Template
from clipspyx.dsl.rule import Rule, _Placeholder


def before(target):
    """Declare this rule fires before target rule."""
    return _Placeholder()


def after(target):
    """Declare this rule fires after target rule."""
    return _Placeholder()


def concurrent(target):
    """Declare this rule fires at the same priority as target rule."""
    return _Placeholder()


NIL = None

__all__ = ['Template', 'Rule', 'Multi', 'Fact', 'NIL', 'before', 'after', 'concurrent']
