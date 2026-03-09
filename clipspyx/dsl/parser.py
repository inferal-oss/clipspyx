import inspect
import textwrap

import libcst as cst

from clipspyx.dsl.template import _template_registry
from clipspyx.dsl.ir import (
    RuleDef, PatternCE, AssignedPatternCE, TestCE, NotCE, OrCE,
    ExistsCE, ForallCE, LogicalCE, GoalCE, ExplicitCE,
    SlotConstraint, Var, Wildcard, Literal,
    NotConstraint, OrConstraint, AndConstraint, PredicateConstraint,
)

_CE_WRAPPERS = {'exists', 'forall', 'logical', 'goal', 'explicit'}

_NIL_NAMES = frozenset({'None', 'NIL'})

_CMP_OPS = {
    'GreaterThan': '>',
    'LessThan': '<',
    'GreaterThanEqual': '>=',
    'LessThanEqual': '<=',
    'Equal': 'eq',
    'NotEqual': 'neq',
    'Is': 'eq',
    'IsNot': 'neq',
}


def parse_rule(cls) -> RuleDef:
    """Parse a Rule subclass source to extract rule IR."""
    source = inspect.getsource(cls)
    source = textwrap.dedent(source)
    module = cst.parse_module(source)

    # Find the class definition
    class_def = None
    for stmt in module.body:
        if isinstance(stmt, cst.ClassDef) and stmt.name.value == cls.__name__:
            class_def = stmt
            break

    if class_def is None:
        raise ValueError(f"Could not find class {cls.__name__} in source")

    conditions = []
    # all_vars: every variable seen (for CLIPS syntax generation)
    # rhs_vars: variables visible on the RHS (excludes forall/exists/not scoped vars)
    all_vars = set()
    rhs_vars = set()
    pattern_vars = []
    salience = None

    # CEs that scope their variables (not visible on RHS)
    _SCOPED_CES = (NotCE, ExistsCE, ForallCE)

    # Track last CE for attaching descriptions from standalone strings
    last_ce = None

    for stmt in class_def.body.body:
        # Skip __action__ method
        if isinstance(stmt, cst.FunctionDef):
            continue

        if isinstance(stmt, cst.SimpleStatementLine):
            # Extract inline comment as CE label
            comment_label = _extract_comment(stmt)

            for item in stmt.body:
                if isinstance(item, cst.Assign):
                    ce_vars = set()
                    result = _process_assign(item, ce_vars, pattern_vars)
                    if result == '__salience__':
                        salience = _extract_int(item.value)
                    elif result is not None:
                        if comment_label:
                            result.label = comment_label
                        conditions.append(result)
                        last_ce = result
                        all_vars.update(ce_vars)
                        # Assigned patterns are always RHS-visible
                        rhs_vars.update(ce_vars)
                elif isinstance(item, cst.Expr):
                    # Standalone string -> description for previous CE
                    if (_is_standalone_string(item.value)
                            and last_ce is not None):
                        last_ce.description = _extract_string(item.value)
                        continue

                    ce_vars = set()
                    result = _process_expr(item.value, ce_vars)
                    if result is not None:
                        if comment_label:
                            result.label = comment_label
                        conditions.append(result)
                        last_ce = result
                        all_vars.update(ce_vars)
                        if not isinstance(result, _SCOPED_CES):
                            rhs_vars.update(ce_vars)

    qualified = f"{cls.__module__}.{cls.__name__}"
    action_func_name = f'__dsl_{qualified}'

    return RuleDef(
        name=qualified,
        conditions=conditions,
        action_func_name=action_func_name,
        bound_vars=sorted(rhs_vars),
        pattern_vars=pattern_vars,
        salience=salience,
    )


def _process_assign(node, bound_vars, pattern_vars):
    """Process an assignment statement in the rule body."""
    # Check for __salience__
    if (len(node.targets) == 1
            and isinstance(node.targets[0], cst.AssignTarget)
            and isinstance(node.targets[0].target, cst.Name)
            and node.targets[0].target.value == '__salience__'):
        return '__salience__'

    # p = Person(name=name, age=age)  -> AssignedPatternCE
    if (len(node.targets) == 1
            and isinstance(node.targets[0], cst.AssignTarget)
            and isinstance(node.targets[0].target, cst.Name)
            and isinstance(node.value, cst.Call)):
        target_name = node.targets[0].target.value
        call = node.value
        if _is_template_call(call):
            pattern = _parse_call_to_pattern(call, bound_vars)
            pattern_vars.append(target_name)
            return AssignedPatternCE(
                var_name=target_name, pattern=pattern)

    return None


def _process_expr(node, bound_vars):
    """Process an expression statement in the rule body."""
    # Template call: Person(name=name)
    if isinstance(node, cst.Call) and _is_template_call(node):
        return _parse_call_to_pattern(node, bound_vars)

    # not Person(...) -> NotCE
    if isinstance(node, cst.UnaryOperation) and isinstance(node.operator, cst.Not):
        inner = node.expression
        if isinstance(inner, cst.Call) and _is_template_call(inner):
            pattern = _parse_call_to_pattern(inner, bound_vars)
            return NotCE(pattern=pattern)

    # Bitwise not ~Person(...) -> NotCE
    if isinstance(node, cst.UnaryOperation) and isinstance(node.operator, cst.BitInvert):
        inner = node.expression
        if isinstance(inner, cst.Call) and _is_template_call(inner):
            pattern = _parse_call_to_pattern(inner, bound_vars)
            return NotCE(pattern=pattern)

    # Person(...) | Other(...) -> OrCE
    if isinstance(node, cst.BinaryOperation) and isinstance(node.operator, cst.BitOr):
        alternatives = _flatten_bitor(node, bound_vars)
        return OrCE(alternatives=alternatives)

    # CE wrappers: exists(...), forall(...), logical(...), goal(...), explicit(...)
    if isinstance(node, cst.Call) and _is_ce_wrapper(node):
        return _parse_ce_wrapper(node, bound_vars)

    # Comparison: age >= 18 -> TestCE
    if isinstance(node, cst.Comparison):
        return _parse_comparison_to_test(node, bound_vars)

    # Boolean operation at top level: could be test CE
    if isinstance(node, cst.BooleanOperation):
        # Could be a test CE like `x > 5 and x < 10`
        expr_str = _expr_to_clips_test(node, bound_vars)
        if expr_str:
            return TestCE(clips_expr=expr_str)

    return None


def _is_template_call(node) -> bool:
    """Check if a Call node is a template call."""
    if isinstance(node.func, cst.Name):
        return node.func.value in _template_registry
    return False


def _extract_comment(stmt) -> str | None:
    """Extract inline comment text from a SimpleStatementLine."""
    tw = stmt.trailing_whitespace
    if hasattr(tw, 'comment') and tw.comment is not None:
        return tw.comment.value.lstrip('#').strip()
    return None


def _is_standalone_string(node) -> bool:
    """Check if a CST node is a string literal (standalone docstring)."""
    return isinstance(node, (cst.SimpleString, cst.ConcatenatedString,
                             cst.FormattedString))


def _is_ce_wrapper(node) -> bool:
    """Check if a Call node is a CE wrapper function."""
    if isinstance(node.func, cst.Name):
        return node.func.value in _CE_WRAPPERS
    return False


def _parse_call_to_pattern(call_node, bound_vars) -> PatternCE:
    """Parse a template call into a PatternCE."""
    source_name = call_node.func.value
    template_cls = _template_registry[source_name]
    template_name = template_cls.__clipspyx_dsl__.name
    slots = []

    for arg in call_node.args:
        if arg.keyword is None:
            continue
        slot_name = arg.keyword.value
        constraint = _parse_constraint(arg.value, bound_vars)
        slots.append(SlotConstraint(name=slot_name, constraint=constraint))

    return PatternCE(template_name=template_name, slots=slots)


def _parse_constraint(node, bound_vars):
    """Parse a constraint value in a slot."""
    # Wildcard: _
    if isinstance(node, cst.Name) and node.value == '_':
        return Wildcard()

    # None / NIL -> CLIPS nil
    if isinstance(node, cst.Name) and node.value in _NIL_NAMES:
        return Literal(value=None)

    # Variable: bare name
    if isinstance(node, cst.Name):
        bound_vars.add(node.value)
        return Var(name=node.value)

    # Integer literal
    if isinstance(node, cst.Integer):
        return Literal(value=int(node.value))

    # Float literal
    if isinstance(node, cst.Float):
        return Literal(value=float(node.value))

    # String literal
    if isinstance(node, (cst.SimpleString, cst.FormattedString, cst.ConcatenatedString)):
        return Literal(value=_extract_string(node))

    # Negated number: -5, -3.14
    if (isinstance(node, cst.UnaryOperation)
            and isinstance(node.operator, cst.Minus)):
        inner = node.expression
        if isinstance(inner, cst.Integer):
            return Literal(value=-int(inner.value))
        if isinstance(inner, cst.Float):
            return Literal(value=-float(inner.value))

    # not X -> NotConstraint (field-level)
    if isinstance(node, cst.UnaryOperation) and isinstance(node.operator, cst.Not):
        inner = _parse_constraint(node.expression, bound_vars)
        return NotConstraint(inner=inner)

    # X or Y or Z -> OrConstraint (field-level)
    if isinstance(node, cst.BooleanOperation) and isinstance(node.operator, cst.Or):
        alternatives = _flatten_or(node, bound_vars)
        return OrConstraint(alternatives=alternatives)

    # X and Y -> AndConstraint or PredicateConstraint
    if isinstance(node, cst.BooleanOperation) and isinstance(node.operator, cst.And):
        return _parse_and_constraint(node, bound_vars)

    # Comparison in slot context (e.g., age > 5 as part of and)
    if isinstance(node, cst.Comparison):
        # This is a predicate within a constraint
        expr_str = _comparison_to_clips(node, bound_vars)
        # Find the variable in the comparison
        var_name = _find_var_in_comparison(node)
        if var_name:
            bound_vars.add(var_name)
            return PredicateConstraint(var=var_name, clips_expr=expr_str)

    return Wildcard()


def _parse_and_constraint(node, bound_vars):
    """Parse an `and` expression in constraint context.

    Cases:
    - `name and name != "Admin"` -> PredicateConstraint
    - `not "a" and not "b"` -> AndConstraint([NotConstraint, NotConstraint])
    - `age and age >= 18` -> PredicateConstraint
    """
    parts = _flatten_and(node, bound_vars)

    # Check if this is a variable binding + predicate pattern
    # e.g. `name and name != "Admin"` or `age and age >= 18`
    if (len(parts) >= 2
            and isinstance(parts[0], Var)):
        var_name = parts[0].name
        # Remaining parts should be predicates
        predicate_parts = []
        for part in parts[1:]:
            if isinstance(part, PredicateConstraint):
                predicate_parts.append(part.clips_expr)
            elif isinstance(part, NotConstraint):
                # Mixed: var + not constraints -> AndConstraint
                return AndConstraint(parts=parts)
            else:
                return AndConstraint(parts=parts)

        if predicate_parts:
            # Combine multiple predicates with and
            combined = predicate_parts[0] if len(predicate_parts) == 1 \
                else ' '.join(predicate_parts)
            return PredicateConstraint(var=var_name, clips_expr=combined)

    return AndConstraint(parts=parts)


def _flatten_or(node, bound_vars):
    """Flatten chained `or` into a list of constraints."""
    result = []
    if isinstance(node, cst.BooleanOperation) and isinstance(node.operator, cst.Or):
        result.extend(_flatten_or(node.left, bound_vars))
        result.extend(_flatten_or(node.right, bound_vars))
    else:
        result.append(_parse_constraint(node, bound_vars))
    return result


def _flatten_and(node, bound_vars):
    """Flatten chained `and` into a list of constraints."""
    result = []
    if isinstance(node, cst.BooleanOperation) and isinstance(node.operator, cst.And):
        result.extend(_flatten_and(node.left, bound_vars))
        result.extend(_flatten_and(node.right, bound_vars))
    else:
        result.append(_parse_constraint(node, bound_vars))
    return result


def _flatten_bitor(node, bound_vars):
    """Flatten chained `|` into a list of PatternCEs."""
    result = []
    if isinstance(node, cst.BinaryOperation) and isinstance(node.operator, cst.BitOr):
        result.extend(_flatten_bitor(node.left, bound_vars))
        result.extend(_flatten_bitor(node.right, bound_vars))
    elif isinstance(node, cst.Call) and _is_template_call(node):
        result.append(_parse_call_to_pattern(node, bound_vars))
    return result


def _parse_comparison_to_test(comp_node, bound_vars) -> TestCE:
    """Parse a comparison into a TestCE."""
    expr_str = _comparison_to_clips(comp_node, bound_vars)
    return TestCE(clips_expr=expr_str)


def _comparison_to_clips(comp_node, bound_vars) -> str:
    """Convert a comparison CST node to a CLIPS expression string."""
    left = _atom_to_clips(comp_node.left, bound_vars)

    # Handle chained comparisons
    parts = []
    current_left = left
    for comp in comp_node.comparisons:
        op_name = type(comp.operator).__name__
        clips_op = _CMP_OPS.get(op_name, op_name.lower())
        right = _atom_to_clips(comp.comparator, bound_vars)
        parts.append(f'{clips_op} {current_left} {right}')
        current_left = right

    if len(parts) == 1:
        return parts[0]
    # Multiple comparisons -> and
    return 'and ' + ' '.join(f'({p})' for p in parts)


def _atom_to_clips(node, bound_vars) -> str:
    """Convert an atomic CST node to its CLIPS string representation."""
    if isinstance(node, cst.Name) and node.value in _NIL_NAMES:
        return 'nil'
    if isinstance(node, cst.Name):
        bound_vars.add(node.value)
        return f'?{node.value}'
    if isinstance(node, cst.Integer):
        return node.value
    if isinstance(node, cst.Float):
        return node.value
    if isinstance(node, (cst.SimpleString, cst.FormattedString, cst.ConcatenatedString)):
        return f'"{_extract_string(node)}"'
    if isinstance(node, cst.UnaryOperation) and isinstance(node.operator, cst.Minus):
        inner = node.expression
        if isinstance(inner, cst.Integer):
            return f'-{inner.value}'
        if isinstance(inner, cst.Float):
            return f'-{inner.value}'
    # Binary arithmetic
    if isinstance(node, cst.BinaryOperation):
        left = _atom_to_clips(node.left, bound_vars)
        right = _atom_to_clips(node.right, bound_vars)
        op = _binop_to_clips(node.operator)
        return f'({op} {left} {right})'
    return '?'


def _binop_to_clips(op) -> str:
    """Convert a binary operator to CLIPS."""
    if isinstance(op, cst.Add):
        return '+'
    if isinstance(op, cst.Subtract):
        return '-'
    if isinstance(op, cst.Multiply):
        return '*'
    if isinstance(op, cst.Divide):
        return '/'
    if isinstance(op, cst.Modulo):
        return 'mod'
    return '?'


def _expr_to_clips_test(node, bound_vars) -> str | None:
    """Convert a boolean expression to a CLIPS test expression string."""
    if isinstance(node, cst.BooleanOperation) and isinstance(node.operator, cst.And):
        left = _expr_to_clips_test(node.left, bound_vars)
        right = _expr_to_clips_test(node.right, bound_vars)
        if left and right:
            return f'and ({left}) ({right})'
    if isinstance(node, cst.BooleanOperation) and isinstance(node.operator, cst.Or):
        left = _expr_to_clips_test(node.left, bound_vars)
        right = _expr_to_clips_test(node.right, bound_vars)
        if left and right:
            return f'or ({left}) ({right})'
    if isinstance(node, cst.Comparison):
        return _comparison_to_clips(node, bound_vars)
    return None


def _find_var_in_comparison(comp_node) -> str | None:
    """Find the first variable Name in a comparison."""
    if isinstance(comp_node.left, cst.Name) and comp_node.left.value not in _NIL_NAMES:
        return comp_node.left.value
    for comp in comp_node.comparisons:
        if isinstance(comp.comparator, cst.Name) and comp.comparator.value not in _NIL_NAMES:
            return comp.comparator.value
    return None


def _extract_int(node) -> int:
    """Extract an integer value from a CST node."""
    if isinstance(node, cst.Integer):
        return int(node.value)
    if (isinstance(node, cst.UnaryOperation)
            and isinstance(node.operator, cst.Minus)
            and isinstance(node.expression, cst.Integer)):
        return -int(node.expression.value)
    raise ValueError(f"Expected integer, got {type(node).__name__}")


def _extract_string(node) -> str:
    """Extract a string value from a CST node."""
    if isinstance(node, cst.SimpleString):
        return node.evaluated_value
    if isinstance(node, cst.FormattedString):
        # For f-strings, just use the raw value
        return node.value if hasattr(node, 'value') else str(node)
    if isinstance(node, cst.ConcatenatedString):
        parts = []
        for part in node.left, node.right:
            parts.append(_extract_string(part))
        return ''.join(parts)
    return str(node)


def _parse_ce_wrapper(call_node, bound_vars):
    """Parse a CE wrapper call: exists(...), forall(...), etc."""
    func_name = call_node.func.value
    args = call_node.args

    if func_name == 'exists':
        elements = []
        for arg in args:
            val = arg.value
            if isinstance(val, cst.Call) and _is_template_call(val):
                elements.append(_parse_call_to_pattern(val, bound_vars))
        return ExistsCE(elements=elements)

    if func_name == 'forall':
        if len(args) < 2:
            raise ValueError("forall requires at least 2 arguments")
        initial = _parse_call_to_pattern(args[0].value, bound_vars)
        conditions = []
        for arg in args[1:]:
            val = arg.value
            if isinstance(val, cst.Call) and _is_template_call(val):
                conditions.append(_parse_call_to_pattern(val, bound_vars))
        return ForallCE(initial=initial, conditions=conditions)

    if func_name == 'logical':
        elements = []
        for arg in args:
            val = arg.value
            if isinstance(val, cst.Call) and _is_template_call(val):
                elements.append(_parse_call_to_pattern(val, bound_vars))
        return LogicalCE(elements=elements)

    if func_name == 'goal':
        if args:
            val = args[0].value
            if isinstance(val, cst.Call) and _is_template_call(val):
                return GoalCE(pattern=_parse_call_to_pattern(val, bound_vars))
        raise ValueError("goal requires a template pattern argument")

    if func_name == 'explicit':
        if args:
            val = args[0].value
            if isinstance(val, cst.Call) and _is_template_call(val):
                return ExplicitCE(pattern=_parse_call_to_pattern(val, bound_vars))
        raise ValueError("explicit requires a template pattern argument")

    return None
