from clipspyx.common import CLIPS_MAJOR
from clipspyx.dsl.ir import (
    TemplateDef, RuleDef, GoalCE, ExplicitCE,
    RetractEffect, ModifyEffect,
)
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
        # and check for unresolved ordering constraints
        agenda = env._agenda
        original_run = agenda.run

        def checked_run(limit=None):
            # Safety net: fail if ordering rules were never finalized
            if env._ordering_pending:
                from clipspyx.dsl.ordering import OrderingError
                names = ', '.join(sorted(env._ordering_pending.keys()))
                raise OrderingError(
                    f"Unresolved ordering constraints for rules: {names}")

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
    Rules with ordering constraints are deferred until all targets are available.
    """
    dsl_def = getattr(cls, '__clipspyx_dsl__', None)
    if dsl_def is None:
        raise TypeError(f"{cls.__name__} is not a DSL template or rule")

    if isinstance(dsl_def, TemplateDef):
        result = _define_template(env, cls, dsl_def)
        env._dsl_defs.append(cls)
        return result
    elif isinstance(dsl_def, RuleDef):
        if dsl_def.ordering:
            # Defer: accumulate for auto-finalization
            env._ordering_pending[dsl_def.name] = (cls, dsl_def)
            env._dsl_defs.append(cls)
            _try_finalize_ordering(env)
        else:
            _define_rule(env, cls, dsl_def)
            env._dsl_defs.append(cls)
            # A non-ordering rule might complete a pending group
            if env._ordering_pending:
                _try_finalize_ordering(env)
    else:
        raise TypeError(f"Unknown DSL definition type: {type(dsl_def).__name__}")


def _try_finalize_ordering(env):
    """Attempt to resolve all pending ordering constraints and build rules.

    Called after each define(). If all targets are resolvable, computes
    salience and builds all pending ordered rules. Otherwise, does nothing
    and waits for more define() calls.

    Non-ordering rules referenced as targets are included as leaf nodes
    in the ordering graph so their salience is computed relative to the group.
    """
    pending = env._ordering_pending
    if not pending:
        return

    from clipspyx.dsl.ordering import compute_ordering_salience

    # Build lookup of already-defined rules (not in pending)
    defined_rules = {}  # short_name -> (cls, rdef)
    for cls_obj in env._dsl_defs:
        dsl_def = getattr(cls_obj, '__clipspyx_dsl__', None)
        if dsl_def is not None and isinstance(dsl_def, RuleDef):
            if dsl_def.name not in pending:
                defined_rules[cls_obj.__name__] = (cls_obj, dsl_def)

    # Collect referenced leaf nodes; return early if any target is missing
    leaf_nodes = {}  # qname -> (cls, rdef)
    for qname, (cls, rdef) in pending.items():
        for oc in rdef.ordering:
            target_name = (oc.target if isinstance(oc.target, str)
                           else oc.target.__name__)
            # Skip if target is among pending rules
            found_in_pending = any(
                c.__name__ == target_name for c, _ in pending.values()
            )
            if found_in_pending:
                continue
            # Check if target is an already-defined rule
            if target_name in defined_rules:
                leaf_cls, leaf_rdef = defined_rules[target_name]
                leaf_nodes[leaf_rdef.name] = (leaf_cls, leaf_rdef)
            else:
                # Target not yet available, wait for more define() calls
                return

    # All targets resolvable -- compute salience including leaf nodes
    full_pending = dict(pending)
    full_pending.update(leaf_nodes)
    salience_map = compute_ordering_salience(
        full_pending, leaf_names=set(leaf_nodes.keys()))

    # Update leaf node rdefs with computed salience for consistency
    for qname, (cls, rdef) in leaf_nodes.items():
        rdef.salience = salience_map[qname]

    # Build all pending rules with computed salience
    for qname in list(pending.keys()):
        cls, rdef = pending[qname]
        rdef.salience = salience_map[qname]
        rdef.ordering = []  # clear so re-inclusion as leaf won't re-resolve
        _define_rule(env, cls, rdef)

    pending.clear()


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

    if rdef.effects:
        # Validate that retracts/modifies reference pattern variables
        pattern_set = set(rdef.pattern_vars)
        for effect in rdef.effects:
            if isinstance(effect, (RetractEffect, ModifyEffect)):
                if effect.var_name not in pattern_set:
                    raise TypeError(
                        f"{effect.__class__.__name__}: '{effect.var_name}' "
                        f"is not a pattern variable (bound via assignment)")
    else:
        action_method = cls.__clipspyx_action__
        arg_names = _build_arg_list(rdef)

        if action_method is not None:
            def action_bridge(*args):
                ns = _ActionNamespace()
                ns.__env__ = env
                for name, val in zip(arg_names, args):
                    setattr(ns, name, val)
                action_method(ns)

            if rdef.multifield_vars:
                # Store directly without deffunction (preserves multifield
                # boundaries). The generated CLIPS code uses
                # (python-function "name" ...) which looks up user_functions.
                from clipspyx.common import environment_data
                user_functions = environment_data(env._env, 'user_functions')
                user_functions.functions[rdef.action_func_name] = action_bridge
            else:
                env.define_function(action_bridge,
                                    name=rdef.action_func_name)
        else:
            def noop_bridge(*args):
                pass
            if rdef.multifield_vars:
                from clipspyx.common import environment_data
                user_functions = environment_data(env._env, 'user_functions')
                user_functions.functions[rdef.action_func_name] = noop_bridge
            else:
                env.define_function(noop_bridge,
                                    name=rdef.action_func_name)

    tracing = (getattr(env, '_tracing_state', None) is not None
               and env._tracing_state.enabled)
    clips_str = generate_defrule(rdef, tracing=tracing)
    env.build(clips_str)
