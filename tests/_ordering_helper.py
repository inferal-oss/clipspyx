"""Helper module defining rules for cross-module ordering tests."""
from clipspyx.dsl import Template, Rule


class HelperItem(Template):
    label: str


class HelperFirst(Rule):
    """A rule defined in a separate module, to be imported elsewhere."""
    HelperItem(label=label)

    def __action__(self):
        pass


class HelperLast(Rule):
    """Another rule for cross-module ordering."""
    after(HelperFirst)
    HelperItem(label=label)

    def __action__(self):
        pass
