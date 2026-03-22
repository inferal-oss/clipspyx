from clipspyx.dsl.ir import (
    TemplateDef, RuleDef,
    PatternCE, AssignedPatternCE, TestCE,
    NotCE, ExistsCE, ForallCE, OrCE, LogicalCE, GoalCE, ExplicitCE,
)


def generate_deftemplate(tdef: TemplateDef) -> str:
    """Generate a CLIPS deftemplate string from a TemplateDef IR."""
    lines = [f'(deftemplate {tdef.name}']
    lines.append(f'  (slot __py_type__ (type SYMBOL) (default {tdef.name}))')

    for slot in tdef.slots:
        keyword = 'multislot' if slot.multi else 'slot'
        parts = [f'({keyword} {slot.name}']
        if slot.clips_type:
            parts.append(f'(type {slot.clips_type})')
        if slot.has_default:
            default_str = _format_default(slot.default)
            parts.append(f'(default {default_str})')
        line = ' '.join(parts) + ')'
        lines.append(f'  {line}')

    lines.append(')')
    return '\n'.join(lines)


def generate_defrule(rdef: RuleDef, tracing: bool = False) -> str:
    """Generate a CLIPS defrule string from a RuleDef IR."""
    lines = [f'(defrule {rdef.name}']

    if rdef.salience is not None:
        lines.append(f'  (declare (salience {rdef.salience}))')

    # When tracing, add implicit fact-address bindings for unbound patterns
    implicit_bindings = []
    for i, ce in enumerate(rdef.conditions):
        if tracing and _needs_implicit_binding(ce):
            var_name = f'_ce{i}'
            implicit_bindings.append(var_name)
            lines.append(f'  ?{var_name} <- {ce.to_clips()}')
        elif tracing and isinstance(ce, AssignedPatternCE):
            lines.append(f'  {ce.to_clips()}')
        else:
            lines.append(f'  {ce.to_clips()}')

    lines.append('  =>')

    # When tracing, prepend the trace-begin call before any RHS content
    if tracing:
        # Collect all fact-address var names: implicit + explicit, in order
        trace_vars = []
        for i, ce in enumerate(rdef.conditions):
            if isinstance(ce, AssignedPatternCE):
                trace_vars.append(ce.var_name)
            elif _needs_implicit_binding(ce):
                trace_vars.append(f'_ce{i}')
        if trace_vars:
            vars_str = ' '.join(f'?{v}' for v in trace_vars)
            lines.append(f'  (__dsl_trace_begin "{rdef.name}" {vars_str})')
        else:
            lines.append(f'  (__dsl_trace_begin "{rdef.name}")')

    if rdef.effects:
        # Native CLIPS RHS: emit effect actions directly
        for effect in rdef.effects:
            lines.append(f'  {effect.to_clips()}')
    else:
        # Build RHS: call the bridge deffunction with bound vars
        arg_names = _build_arg_list(rdef)
        multifield_set = set(rdef.multifield_vars)
        if arg_names:
            args_parts = []
            for n in arg_names:
                if n in multifield_set:
                    args_parts.append(f'$?{n}')
                else:
                    args_parts.append(f'?{n}')
            args_str = ' '.join(args_parts)
            if rdef.multifield_vars:
                lines.append(
                    f'  (python-function {rdef.action_func_name}'
                    f' {args_str})')
            else:
                lines.append(f'  ({rdef.action_func_name} {args_str})')
        else:
            lines.append(f'  ({rdef.action_func_name})')

    lines.append(')')
    return '\n'.join(lines)


def _needs_implicit_binding(ce) -> bool:
    """Return True if this CE type needs an implicit fact-address binding for tracing."""
    return isinstance(ce, PatternCE)


def _build_arg_list(rdef: RuleDef) -> list[str]:
    """Build the ordered argument list for the bridge function.

    Order: pattern_vars first, then remaining bound_vars (sorted).
    """
    pattern_set = set(rdef.pattern_vars)
    remaining = sorted(v for v in rdef.bound_vars if v not in pattern_set)
    return rdef.pattern_vars + remaining


def generate_typecheck_rule(template_name: str, slot_name: str,
                            expected_template: str) -> str:
    """Generate a CLIPS defrule that validates a fact-address slot's __py_type__."""
    rule_name = f'__py_typecheck_{template_name}_{slot_name}'
    return (
        f'(defrule {rule_name}\n'
        f'  (declare (salience 10000))\n'
        f'  ({template_name} ({slot_name} ?ref))\n'
        f'  (test (neq (fact-slot-value ?ref __py_type__) {expected_template}))\n'
        f'  =>\n'
        f'  (__py_typecheck_error "{template_name}" "{slot_name}"'
        f' "{expected_template}" (fact-slot-value ?ref __py_type__)))'
    )


def _format_default(value) -> str:
    """Format a default value for CLIPS."""
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, (int, float)):
        return str(value)
    if value is None:
        return 'nil'
    return str(value)
