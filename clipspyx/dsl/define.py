from clipspyx.common import CLIPS_MAJOR
from clipspyx.dsl.ir import TemplateDef, RuleDef, GoalCE, ExplicitCE
from clipspyx.dsl.codegen import generate_deftemplate, generate_defrule, generate_typecheck_rule


_typecheck_envs: set = set()
_typecheck_errors: dict = {}


def _ensure_typecheck_bridge(env):
    env_id = id(env._env)
    if env_id not in _typecheck_envs:
        _typecheck_errors[env_id] = None

        def typecheck_error(template, slot, expected, actual):
            err = TypeError(
                f"{template}.{slot} expects a {expected} fact, got {actual}")
            _typecheck_errors[env_id] = err
            raise err

        env.define_function(typecheck_error, name='__py_typecheck_error')

        # Wrap Agenda.run to re-raise stored type-check errors
        agenda = env._agenda
        original_run = agenda.run

        def checked_run(limit=None):
            _typecheck_errors[env_id] = None
            result = original_run(limit)
            pending = _typecheck_errors[env_id]
            if pending is not None:
                _typecheck_errors[env_id] = None
                raise pending
            return result

        agenda.run = checked_run

        _typecheck_envs.add(env_id)


class _ActionNamespace:
    """Simple namespace for action method self parameter.

    Attributes are set dynamically from bound variable values passed
    by the CLIPS bridge function.
    """
    pass


def _build_arg_list(rdef: RuleDef) -> list[str]:
    """Build the ordered argument list matching codegen output."""
    pattern_set = set(rdef.pattern_vars)
    remaining = sorted(v for v in rdef.bound_vars if v not in pattern_set)
    return rdef.pattern_vars + remaining


def define(env, cls):
    """Define a DSL template or rule in a CLIPS environment.

    For templates: builds the deftemplate construct.
    For rules: registers the bridge function and builds the defrule construct.
    """
    dsl_def = getattr(cls, '__clipspyx_dsl__', None)
    if dsl_def is None:
        raise TypeError(f"{cls.__name__} is not a DSL template or rule")

    if isinstance(dsl_def, TemplateDef):
        result = _define_template(env, cls, dsl_def)
        env._dsl_defs.append(cls)
        return result
    elif isinstance(dsl_def, RuleDef):
        _define_rule(env, cls, dsl_def)
        env._dsl_defs.append(cls)
    else:
        raise TypeError(f"Unknown DSL definition type: {type(dsl_def).__name__}")


def _define_template(env, cls, tdef: TemplateDef):
    """Build a deftemplate in the CLIPS environment and return a bound asserter."""
    clips_str = generate_deftemplate(tdef)
    env.build(clips_str)

    for slot in tdef.slots:
        if slot.fact_template:
            _ensure_typecheck_bridge(env)
            rule_str = generate_typecheck_rule(tdef.name, slot.name,
                                               slot.fact_template)
            env.build(rule_str)

    def asserter(**kwargs):
        tpl = env.find_template(tdef.name)
        return tpl.assert_fact(**kwargs)

    return asserter


def _define_rule(env, cls, rdef: RuleDef):
    """Register bridge function and build defrule in the CLIPS environment."""
    if CLIPS_MAJOR < 7:
        for ce in rdef.conditions:
            if isinstance(ce, GoalCE):
                raise TypeError("goal() requires CLIPS 7.0 or later")
            if isinstance(ce, ExplicitCE):
                raise TypeError("explicit() requires CLIPS 7.0 or later")

    action_method = cls.__clipspyx_action__
    arg_names = _build_arg_list(rdef)

    if action_method is not None:
        def action_bridge(*args):
            ns = _ActionNamespace()
            ns.__env__ = env
            for name, val in zip(arg_names, args):
                setattr(ns, name, val)
            action_method(ns)

        env.define_function(action_bridge, name=rdef.action_func_name)
    else:
        def noop_bridge(*args):
            pass
        env.define_function(noop_bridge, name=rdef.action_func_name)

    clips_str = generate_defrule(rdef)
    env.build(clips_str)
