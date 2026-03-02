import subprocess
from collections import defaultdict

from clipspyx.dsl.ir import (
    TemplateDef, RuleDef, PatternCE, AssignedPatternCE,
    NotCE, OrCE, ExistsCE, ForallCE, LogicalCE, GoalCE, ExplicitCE,
    TestCE,
)


def _short_template(name):
    """Return the short class name from a qualified template name."""
    if '.' in name:
        return name.rsplit('.', 1)[1]
    return name


def _pattern_summary(pattern):
    """Summarize a PatternCE as 'Template(slot, slot, ...)'."""
    short = _short_template(pattern.template_name)
    if pattern.slots:
        slots = ', '.join(s.name for s in pattern.slots)
        return f'{short}({slots})'
    return f'{short}()'


def _clips_test_to_python(clips_expr):
    """Convert a CLIPS test expression to Python-like infix notation.

    Handles simple prefix expressions like ``>= ?age 18`` -> ``age >= 18``
    and ``neq ?name "Admin"`` -> ``name != "Admin"``.
    Compound expressions with ``and``/``or`` are also converted.
    """
    _op_map = {
        '>=': '>=', '<=': '<=', '>': '>', '<': '<',
        '=': '==', 'eq': '==', 'neq': '!=',
    }

    def _strip_var(token):
        return token[1:] if token.startswith('?') else token

    def _convert_simple(expr):
        """Convert a single prefix expression to infix."""
        expr = expr.strip()
        # Strip wrapping parens
        if expr.startswith('(') and expr.endswith(')'):
            expr = expr[1:-1].strip()
        tokens = expr.split(None, 2)
        if len(tokens) == 3:
            op, a, b = tokens
            if op in _op_map:
                return f'{_strip_var(a)} {_op_map[op]} {_strip_var(b)}'
        # Fallback: just strip ? from variables
        return ' '.join(_strip_var(t) for t in expr.split())

    # Handle compound: and (...) (...) or or (...) (...)
    expr = clips_expr.strip()
    if expr.startswith('and ') or expr.startswith('or '):
        connector = 'and' if expr.startswith('and ') else 'or'
        rest = expr[len(connector):].strip()
        # Split on top-level parenthesized sub-expressions
        parts = []
        depth = 0
        current = []
        for ch in rest:
            if ch == '(':
                depth += 1
                if depth > 1:
                    current.append(ch)
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    parts.append(''.join(current).strip())
                    current = []
                else:
                    current.append(ch)
            else:
                if depth > 0:
                    current.append(ch)
        if parts:
            converted = [_convert_simple(p) for p in parts]
            return f' {connector} '.join(converted)

    return _convert_simple(expr)


def _ce_summary(ce):
    """Build a one-line human-readable summary of a conditional element."""
    if isinstance(ce, PatternCE):
        return _pattern_summary(ce)
    elif isinstance(ce, AssignedPatternCE):
        return f'{ce.var_name} = {_pattern_summary(ce.pattern)}'
    elif isinstance(ce, TestCE):
        return _clips_test_to_python(ce.clips_expr)
    elif isinstance(ce, NotCE):
        return f'not {_pattern_summary(ce.pattern)}'
    elif isinstance(ce, OrCE):
        parts = []
        for alt in ce.alternatives:
            if isinstance(alt, PatternCE):
                parts.append(_pattern_summary(alt))
            else:
                parts.append(_ce_summary(alt))
        return ' | '.join(parts)
    elif isinstance(ce, ExistsCE):
        elems = ', '.join(
            _pattern_summary(e) if isinstance(e, PatternCE) else _ce_summary(e)
            for e in ce.elements
        )
        return f'exists({elems})'
    elif isinstance(ce, ForallCE):
        parts = [_pattern_summary(ce.initial)]
        for c in ce.conditions:
            if isinstance(c, PatternCE):
                parts.append(_pattern_summary(c))
            else:
                parts.append(_ce_summary(c))
        return f'forall({", ".join(parts)})'
    elif isinstance(ce, LogicalCE):
        elems = ', '.join(
            _pattern_summary(e) if isinstance(e, PatternCE) else _ce_summary(e)
            for e in ce.elements
        )
        return f'logical({elems})'
    elif isinstance(ce, GoalCE):
        return f'goal({_pattern_summary(ce.pattern)})'
    elif isinstance(ce, ExplicitCE):
        return f'explicit({_pattern_summary(ce.pattern)})'
    return '?'


def _extract_edges(ce):
    """Extract (ce_type, template_name, [slot_names]) tuples from a CE.

    ce_type is a string like 'match', 'not', 'exists', 'forall', etc.
    """
    if isinstance(ce, PatternCE):
        slot_names = [s.name for s in ce.slots]
        return [('match', ce.template_name, slot_names)]
    elif isinstance(ce, AssignedPatternCE):
        slot_names = [s.name for s in ce.pattern.slots]
        return [('match', ce.pattern.template_name, slot_names)]
    elif isinstance(ce, NotCE):
        slot_names = [s.name for s in ce.pattern.slots]
        return [('not', ce.pattern.template_name, slot_names)]
    elif isinstance(ce, OrCE):
        result = []
        for alt in ce.alternatives:
            for ce_type, tpl, slots in _extract_edges(alt):
                result.append(('or', tpl, slots))
        return result
    elif isinstance(ce, ExistsCE):
        result = []
        for elem in ce.elements:
            for ce_type, tpl, slots in _extract_edges(elem):
                result.append(('exists', tpl, slots))
        return result
    elif isinstance(ce, ForallCE):
        result = []
        for ce_type, tpl, slots in _extract_edges(ce.initial):
            result.append(('forall', tpl, slots))
        for cond in ce.conditions:
            for ce_type, tpl, slots in _extract_edges(cond):
                result.append(('forall', tpl, slots))
        return result
    elif isinstance(ce, LogicalCE):
        result = []
        for elem in ce.elements:
            for ce_type, tpl, slots in _extract_edges(elem):
                result.append(('logical', tpl, slots))
        return result
    elif isinstance(ce, GoalCE):
        slot_names = [s.name for s in ce.pattern.slots]
        return [('goal', ce.pattern.template_name, slot_names)]
    elif isinstance(ce, ExplicitCE):
        slot_names = [s.name for s in ce.pattern.slots]
        return [('explicit', ce.pattern.template_name, slot_names)]
    elif isinstance(ce, TestCE):
        return []
    return []


def _d2_container_id(module):
    """Convert a module name to a D2-safe container identifier."""
    return module.replace('.', '_') if module else 'root'


def _escape_d2(text):
    """Escape text for D2 string values."""
    return text.replace('\\', '\\\\').replace('"', '\\"')


def _slot_label(slot):
    """Build display text for a slot row in a sql_table."""
    parts = []
    if slot.fact_template:
        # Show the typed template name instead of FACT-ADDRESS
        parts.append(_short_template(slot.fact_template))
    elif slot.clips_type:
        parts.append(slot.clips_type)
    if slot.has_default:
        parts.append(f"= {slot.default}")
    if parts:
        return f"{slot.name}: {' '.join(parts)}"
    return slot.name


def _edge_label(ce_type, slot_names):
    """Build edge label from CE type and slot names."""
    if ce_type == 'match':
        # Plain match: just show slots
        if slot_names:
            return ', '.join(slot_names)
        return ''
    else:
        # Annotated CE type
        if slot_names:
            return f'{ce_type}: {", ".join(slot_names)}'
        return ce_type


def generate_d2(defs, group_by_kind=False):
    """Generate a D2 diagram string from a list of DSL classes.

    Each class must have a ``__clipspyx_dsl__`` attribute (TemplateDef or RuleDef)
    and optionally a ``__doc__`` for note annotations.

    When *group_by_kind* is ``True``, templates and rules are placed in separate
    sub-containers (``Templates`` and ``Rules``) within each module container.

    Returns an empty string if *defs* is empty.
    """
    if not defs:
        return ''

    # Group classes by module (prefix before last dot in the IR name)
    modules = defaultdict(list)
    for cls in defs:
        dsl_def = cls.__clipspyx_dsl__
        if '.' in dsl_def.name:
            module, short = dsl_def.name.rsplit('.', 1)
        else:
            module, short = '', dsl_def.name
        modules[module].append((cls, dsl_def, short))

    # Build a mapping: IR name -> D2 path (container.node)
    d2_path = {}
    for module, entries in modules.items():
        container_id = _d2_container_id(module)
        for _cls, dsl_def, short in entries:
            if group_by_kind:
                kind = 'Templates' if isinstance(dsl_def, TemplateDef) \
                    else 'Rules'
                d2_path[dsl_def.name] = \
                    f'{container_id}.{kind}.{short}'
            else:
                d2_path[dsl_def.name] = f'{container_id}.{short}'

    lines = []
    edges = []

    # Track template names for fact-address edge generation
    template_names = set()
    for cls in defs:
        dsl_def = cls.__clipspyx_dsl__
        if isinstance(dsl_def, TemplateDef):
            template_names.add(dsl_def.name)

    for module, entries in modules.items():
        container_id = _d2_container_id(module)

        lines.append(f'{container_id}: {{')
        lines.append(f'  label: "{_escape_d2(module or "root")}"')
        lines.append('')

        if group_by_kind:
            # Split entries into templates and rules
            tpl_entries = [(c, d, s) for c, d, s in entries
                          if isinstance(d, TemplateDef)]
            rule_entries = [(c, d, s) for c, d, s in entries
                           if isinstance(d, RuleDef)]
            groups = []
            if tpl_entries:
                groups.append(('Templates', tpl_entries))
            if rule_entries:
                groups.append(('Rules', rule_entries))
        else:
            groups = [(None, entries)]

        for group_label, group_entries in groups:
            if group_label:
                lines.append(f'  {group_label}: {{')
                lines.append(f'    label: "{group_label}"')
                lines.append('')
                indent = '    '
            else:
                indent = '  '

            for cls, dsl_def, short in group_entries:
                node_id = short

                if isinstance(dsl_def, TemplateDef):
                    lines.append(f'{indent}{node_id}: {{')
                    lines.append(f'{indent}  shape: sql_table')
                    lines.append(f'{indent}  style.fill: "#4a90d9"')
                    for slot in dsl_def.slots:
                        label = _slot_label(slot)
                        lines.append(
                            f'{indent}  {slot.name}: '
                            f'"{_escape_d2(label)}"')
                    lines.append(f'{indent}}}')

                    # Docstring note (connected via dotted edge)
                    if cls.__doc__:
                        note_id = f'{node_id}_note'
                        doc_line = cls.__doc__.strip().split('\n')[0]
                        lines.append(
                            f'{indent}{note_id}: '
                            f'"{_escape_d2(doc_line)}" {{')
                        lines.append(f'{indent}  shape: cloud')
                        lines.append(f'{indent}}}')
                        lines.append(
                            f'{indent}{note_id} -> {node_id}: '
                            f'{{style.stroke-dash: 3; style.opacity: 0.5}}'
                        )

                    # Slot descriptions: individual note per slot
                    for slot in dsl_def.slots:
                        if not slot.description:
                            continue
                        doc_id = f'{node_id}_{slot.name}_doc'
                        lines.append(
                            f'{indent}{doc_id}: '
                            f'"{_escape_d2(slot.description)}" {{')
                        lines.append(f'{indent}  shape: page')
                        lines.append(f'{indent}}}')
                        lines.append(
                            f'{indent}{doc_id} -> {node_id}.{slot.name}: '
                            f'{{style.stroke-dash: 3; style.opacity: 0.5}}'
                        )

                    # Fact-address edges (template -> template)
                    for slot in dsl_def.slots:
                        if (slot.fact_template
                                and slot.fact_template in template_names):
                            src = d2_path[dsl_def.name]
                            dst = d2_path[slot.fact_template]
                            edges.append(
                                f'{src} -> {dst}: '
                                f'"{_escape_d2(slot.name)}" '
                                f'{{style.stroke-dash: 3}}'
                            )

                elif isinstance(dsl_def, RuleDef):
                    lines.append(f'{indent}{node_id}: {{')
                    lines.append(f'{indent}  shape: sql_table')
                    lines.append(f'{indent}  style.fill: "#8b5cf6"')
                    lines.append(f'{indent}  style.italic: true')

                    # Header row with salience
                    if dsl_def.salience is not None:
                        lines.append(
                            f'{indent}  salience: '
                            f'"salience: {dsl_def.salience}"')

                    # CE rows
                    for i, ce in enumerate(dsl_def.conditions):
                        summary = _ce_summary(ce)
                        if ce.label:
                            key = ce.label
                        elif isinstance(ce, AssignedPatternCE):
                            key = ce.var_name
                        else:
                            key = f'ce{i}'
                        lines.append(
                            f'{indent}  {key}: '
                            f'"{_escape_d2(summary)}"')

                    # Bound variables row
                    all_vars = dsl_def.pattern_vars + sorted(
                        v for v in dsl_def.bound_vars
                        if v not in set(dsl_def.pattern_vars)
                    )
                    if all_vars:
                        var_list = ', '.join(all_vars)
                        lines.append(
                            f'{indent}  vars: '
                            f'"{_escape_d2(var_list)}"')

                    lines.append(f'{indent}}}')

                    # Docstring note (connected via dotted edge)
                    if cls.__doc__:
                        note_id = f'{node_id}_note'
                        doc_line = cls.__doc__.strip().split('\n')[0]
                        lines.append(
                            f'{indent}{note_id}: '
                            f'"{_escape_d2(doc_line)}" {{')
                        lines.append(f'{indent}  shape: cloud')
                        lines.append(f'{indent}}}')
                        lines.append(
                            f'{indent}{note_id} -> {node_id}: '
                            f'{{style.stroke-dash: 3; style.opacity: 0.5}}'
                        )

                    # CE descriptions: individual note per CE
                    for i, ce in enumerate(dsl_def.conditions):
                        if not ce.description:
                            continue
                        if ce.label:
                            ce_key = ce.label
                        elif isinstance(ce, AssignedPatternCE):
                            ce_key = ce.var_name
                        else:
                            ce_key = f'ce{i}'
                        doc_id = f'{node_id}_{ce_key}_doc'
                        lines.append(
                            f'{indent}{doc_id}: '
                            f'"{_escape_d2(ce.description)}" {{')
                        lines.append(f'{indent}  shape: page')
                        lines.append(f'{indent}}}')
                        lines.append(
                            f'{indent}{doc_id} -> {node_id}.{ce_key}: '
                            f'{{style.stroke-dash: 3; style.opacity: 0.5}}'
                        )

                    # Rule -> template edges with CE type annotations
                    for ce in dsl_def.conditions:
                        for ce_type, tpl_name, slot_names in \
                                _extract_edges(ce):
                            src = d2_path[dsl_def.name]
                            dst = d2_path.get(tpl_name)
                            if dst is None:
                                continue
                            label = _edge_label(ce_type, slot_names)
                            if label:
                                edges.append(
                                    f'{src} -> {dst}: '
                                    f'"{_escape_d2(label)}"'
                                )
                            else:
                                edges.append(f'{src} -> {dst}')

                lines.append('')

            if group_label:
                lines.append(f'  }}')
                lines.append('')

        lines.append('}')
        lines.append('')

    # Append edges
    for edge in edges:
        lines.append(edge)

    # Strip trailing blank lines
    while lines and lines[-1] == '':
        lines.pop()

    return '\n'.join(lines) + '\n'


def render_d2(d2_text, output_path, layout='elk'):
    """Render D2 text to an output file (SVG, PNG, etc.) using the d2 CLI.

    *layout* selects the D2 layout engine (default ``'elk'``).

    Raises FileNotFoundError if the ``d2`` command is not installed.
    Raises RuntimeError if d2 exits with an error.
    """
    cmd = ['d2', '--layout', layout, '-', output_path]
    try:
        result = subprocess.run(
            cmd,
            input=d2_text,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "d2 CLI not found. Install it from https://d2lang.com to render diagrams."
        )
    if result.returncode != 0:
        raise RuntimeError(f"d2 failed (exit {result.returncode}): {result.stderr}")
