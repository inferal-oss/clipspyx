import inspect
import textwrap
import typing

from clipspyx.dsl.types import is_multi, multi_element_type, clips_type_name
from clipspyx.dsl.ir import TemplateDef, SlotDef


def _extract_slot_descriptions(cls) -> dict[str, str]:
    """Parse class source to extract standalone strings after annotations.

    Returns a mapping of slot name -> description string.
    """
    try:
        import libcst as cst
    except ImportError:
        return {}

    try:
        source = inspect.getsource(cls)
    except OSError:
        return {}

    source = textwrap.dedent(source)
    module = cst.parse_module(source)

    class_def = None
    for stmt in module.body:
        if isinstance(stmt, cst.ClassDef) and stmt.name.value == cls.__name__:
            class_def = stmt
            break
    if class_def is None:
        return {}

    descriptions = {}
    last_slot_name = None

    for stmt in class_def.body.body:
        if isinstance(stmt, cst.SimpleStatementLine):
            for item in stmt.body:
                if isinstance(item, cst.AnnAssign) and isinstance(
                        item.target, cst.Name):
                    last_slot_name = item.target.value
                elif isinstance(item, cst.Expr) and isinstance(
                        item.value,
                        (cst.SimpleString, cst.ConcatenatedString,
                         cst.FormattedString)):
                    if last_slot_name is not None:
                        raw = item.value
                        if isinstance(raw, cst.SimpleString):
                            descriptions[last_slot_name] = \
                                raw.evaluated_value
                        elif isinstance(raw, cst.ConcatenatedString):
                            parts = []
                            for p in raw.parts:
                                if isinstance(p, cst.SimpleString):
                                    parts.append(p.evaluated_value)
                                elif hasattr(p, 'evaluated_value'):
                                    parts.append(p.evaluated_value)
                            descriptions[last_slot_name] = ''.join(parts)
                        last_slot_name = None
                        continue
                else:
                    last_slot_name = None
        else:
            last_slot_name = None

    return descriptions


def _is_template_class(annotation) -> bool:
    """Check if an annotation is a Template subclass with a TemplateDef."""
    dsl = getattr(annotation, '__clipspyx_dsl__', None)
    return isinstance(dsl, TemplateDef)

_SENTINEL = object()

# Registry maps class name -> class object so the rule parser can recognize
# template calls in class bodies.
_template_registry: dict[str, type] = {}


def _process_template_class(cls):
    """Extract type hints from *cls* and attach a TemplateDef as __clipspyx_dsl__."""
    hints = typing.get_type_hints(cls)
    slot_descriptions = _extract_slot_descriptions(cls)
    slots = []

    for slot_name, annotation in hints.items():
        multi = is_multi(annotation)
        fact_template = None

        if multi:
            element_type = multi_element_type(annotation)
            ctype = clips_type_name(element_type)
        elif _is_template_class(annotation):
            ctype = 'FACT-ADDRESS'
            fact_template = annotation.__clipspyx_dsl__.name
        else:
            ctype = clips_type_name(annotation)

        default_val = getattr(cls, slot_name, _SENTINEL)
        has_default = default_val is not _SENTINEL

        slots.append(SlotDef(
            name=slot_name,
            multi=multi,
            clips_type=ctype,
            default=default_val if has_default else None,
            has_default=has_default,
            fact_template=fact_template,
            description=slot_descriptions.get(slot_name),
        ))

    clips_name = getattr(cls, '__clips_name__', f"{cls.__module__}.{cls.__name__}")
    tdef = TemplateDef(name=clips_name, slots=slots)
    cls.__clipspyx_dsl__ = tdef

    _template_registry[cls.__name__] = cls


class _TemplateMeta(type):
    """Metaclass that processes Template subclasses at creation time."""

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:  # skip the Template base class itself
            _process_template_class(cls)
        return cls

    def __call__(cls, *args, **kwargs):
        if '__env__' in kwargs:
            env = kwargs.pop('__env__')
            tdef = cls.__clipspyx_dsl__
            tpl = env.find_template(tdef.name)
            return tpl.assert_fact(**kwargs)
        return super().__call__(*args, **kwargs)


class Template(metaclass=_TemplateMeta):
    """Base class for CLIPS template definitions.

    Usage::

        class Person(Template):
            name: str
            age: int = 0
            hobbies: Multi[str]

    The class can then be:
    - Passed to ``env.define(Person)`` to build the deftemplate
    - Called with ``__env__`` kwarg to assert facts: ``Person(__env__=env, name="Alice")``
    """
    pass
