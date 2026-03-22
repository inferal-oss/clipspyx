from clipspyx.values import Symbol


class Multi:
    """Generic type for CLIPS multislot fields.

    Usage: Multi[str], Multi[int], Multi[float]
    """

    __element_type__ = None

    def __class_getitem__(cls, item):
        ns = type(cls.__name__, (cls,), {'__element_type__': item})
        return ns


def is_multi(annotation) -> bool:
    """Check if an annotation is a Multi[T] type."""
    try:
        return (isinstance(annotation, type)
                and issubclass(annotation, Multi))
    except TypeError:
        return False


def multi_element_type(annotation):
    """Extract the element type from a Multi[T] annotation."""
    return annotation.__element_type__


class Fact:
    """Sentinel type for FACT-ADDRESS slots/multislots."""
    pass


_TYPE_MAP = {
    int: 'INTEGER',
    float: 'FLOAT',
    str: 'STRING',
    Symbol: 'SYMBOL',
    Fact: 'FACT-ADDRESS',
}


def clips_type_name(python_type) -> str | None:
    """Map a Python type to a CLIPS type name string."""
    return _TYPE_MAP.get(python_type)
