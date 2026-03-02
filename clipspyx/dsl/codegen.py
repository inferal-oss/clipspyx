from clipspyx.dsl.ir import TemplateDef, RuleDef


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


def generate_defrule(rdef: RuleDef) -> str:
    """Generate a CLIPS defrule string from a RuleDef IR."""
    lines = [f'(defrule {rdef.name}']

    if rdef.salience is not None:
        lines.append(f'  (declare (salience {rdef.salience}))')

    for ce in rdef.conditions:
        lines.append(f'  {ce.to_clips()}')

    lines.append('  =>')

    # Build RHS: call the bridge deffunction with bound vars
    arg_names = _build_arg_list(rdef)
    if arg_names:
        args_str = ' '.join(f'?{n}' for n in arg_names)
        lines.append(f'  ({rdef.action_func_name} {args_str})')
    else:
        lines.append(f'  ({rdef.action_func_name})')

    lines.append(')')
    return '\n'.join(lines)


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
