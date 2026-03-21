from clipspyx.dsl.template import _template_registry


class _Placeholder:
    """Inert placeholder returned by the rule namespace for undefined names.

    Supports all comparison and arithmetic operators, returning another
    _Placeholder each time so that expressions like ``age >= 18`` or
    ``name and name != "Admin"`` evaluate without errors during class body
    execution.
    """

    def __bool__(self):
        return True

    # Comparison
    def __eq__(self, other): return _Placeholder()
    def __ne__(self, other): return _Placeholder()
    def __lt__(self, other): return _Placeholder()
    def __le__(self, other): return _Placeholder()
    def __gt__(self, other): return _Placeholder()
    def __ge__(self, other): return _Placeholder()

    # Arithmetic
    def __add__(self, other): return _Placeholder()
    def __radd__(self, other): return _Placeholder()
    def __sub__(self, other): return _Placeholder()
    def __rsub__(self, other): return _Placeholder()
    def __mul__(self, other): return _Placeholder()
    def __rmul__(self, other): return _Placeholder()
    def __truediv__(self, other): return _Placeholder()
    def __rtruediv__(self, other): return _Placeholder()
    def __mod__(self, other): return _Placeholder()
    def __rmod__(self, other): return _Placeholder()

    # Bitwise (for | used as or-CE)
    def __or__(self, other): return _Placeholder()
    def __ror__(self, other): return _Placeholder()
    def __and__(self, other): return _Placeholder()
    def __rand__(self, other): return _Placeholder()
    def __invert__(self): return _Placeholder()

    # Callable (for template calls and CE wrappers)
    def __call__(self, *args, **kwargs): return _Placeholder()

    # Hash needed since __eq__ is overridden
    def __hash__(self): return id(self)


def _make_ce_func():
    """Create a callable that returns _Placeholder for CE wrappers."""
    def ce_func(*args, **kwargs):
        return _Placeholder()
    return ce_func


class _RuleNamespace(dict):
    """Custom namespace dict for rule class bodies.

    Returns _Placeholder() for any undefined name that doesn't start with '_',
    allowing pattern expressions like ``Person(name=name, age=age)`` to
    execute without NameError.
    """

    def __init__(self):
        super().__init__()
        # Seed wildcard
        self['_'] = _Placeholder()
        # Seed NIL as None (Python keyword None needs no seeding)
        self['NIL'] = None
        # Seed template names as callables returning _Placeholder
        for name in _template_registry:
            self[name] = _make_ce_func()
        # Seed CE wrapper functions
        for ce_name in ('exists', 'forall', 'logical', 'goal', 'explicit'):
            self[ce_name] = _make_ce_func()
        # Seed effect functions
        for eff_name in ('asserts', 'retracts', 'modifies'):
            self[eff_name] = _make_ce_func()
        # Seed ordering functions
        for ord_name in ('before', 'after', 'concurrent'):
            self[ord_name] = _make_ce_func()
        # Seed Symbol as a callable returning _Placeholder
        self['Symbol'] = _make_ce_func()

    def __missing__(self, key):
        if key.startswith('_'):
            raise KeyError(key)
        p = _Placeholder()
        self[key] = p
        return p


class _RuleMeta(type):
    """Metaclass for Rule subclasses.

    Uses _RuleNamespace during class body execution so that bare names
    resolve to _Placeholder objects. After class creation, invokes the
    libcst parser to extract the rule IR from source code.
    """

    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        # For the Rule base class itself, use a normal dict
        if not bases:
            return {}
        return _RuleNamespace()

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, dict(namespace))

        # Only parse user subclasses, not the Rule base itself
        if bases:
            # Extract __action__ before parsing
            action = namespace.get('__action__')
            if action is not None:
                cls.__clipspyx_action__ = action
            else:
                cls.__clipspyx_action__ = None

            # Extract salience
            salience = namespace.get('__salience__')
            if isinstance(salience, int):
                cls.__clipspyx_salience__ = salience
            else:
                cls.__clipspyx_salience__ = None

            # Lazy parse: done when define() is called, or eagerly here
            from clipspyx.dsl.parser import parse_rule
            cls.__clipspyx_dsl__ = parse_rule(cls)

            # Mutual exclusivity: effects and __action__ cannot coexist
            if cls.__clipspyx_dsl__.effects and cls.__clipspyx_action__ is not None:
                raise TypeError(
                    f"Rule {name} cannot define both effects "
                    f"(asserts/retracts/modifies) and __action__")

            # Mutual exclusivity: ordering and __salience__ cannot coexist
            if (cls.__clipspyx_dsl__.ordering
                    and cls.__clipspyx_dsl__.salience is not None):
                raise TypeError(
                    f"Rule {name} cannot define both ordering "
                    f"(before/after/concurrent) and __salience__")

            # Resolve ordering target strings to class references
            if cls.__clipspyx_dsl__.ordering:
                import sys
                module_ns = sys.modules.get(cls.__module__)
                if module_ns is not None:
                    module_dict = vars(module_ns)
                    for oc in cls.__clipspyx_dsl__.ordering:
                        if isinstance(oc.target, str) and oc.target in module_dict:
                            target_cls = module_dict[oc.target]
                            if (isinstance(target_cls, type)
                                    and issubclass(target_cls, Rule)):
                                oc.target = target_cls

        return cls


class Rule(metaclass=_RuleMeta):
    """Base class for DSL rules.

    Subclass this to define CLIPS rules using Python syntax::

        class GreetAdult(Rule):
            p = Person(name=name, age=age)
            age >= 18

            def __action__(self):
                print(f"Hello {self.name}, age {self.age}")
    """
    pass
