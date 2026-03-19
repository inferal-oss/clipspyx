import unittest
from unittest.mock import patch

from clipspyx import Environment
from clipspyx.dsl import Template, Rule, Multi
from clipspyx.dsl.visualize import generate_d2, render_d2


def _d2_path(cls):
    """Build the D2 container.node path for a DSL class."""
    name = cls.__clipspyx_dsl__.name
    if '.' in name:
        module, short = name.rsplit('.', 1)
        container = module.replace('.', '_')
    else:
        container, short = 'root', name
    return f'{container}.{short}'


# --- Templates with unique names to avoid global registry collisions ---

class VizPerson(Template):
    """A person record."""
    name: str
    age: int = 0


class VizBadge(Template):
    owner: str
    level: int = 0


class VizDepartment(Template):
    """Organizational unit."""
    name: str
    head: VizPerson  # fact-address slot


class VizDocSlots(Template):
    """Template with documented slots."""
    name: str
    """Full legal name of the person"""
    age: int = 0
    """Age in years"""
    title: str


# =============================================================================
# Template D2 generation
# =============================================================================

class TestGenerateD2Templates(unittest.TestCase):
    """Templates: sql_table nodes with slots, grouped by module."""

    def test_single_template(self):
        d2 = generate_d2([VizPerson])
        self.assertIn('shape: sql_table', d2)
        self.assertIn('name:', d2)
        self.assertIn('age:', d2)
        self.assertIn('STRING', d2)
        self.assertIn('INTEGER', d2)

    def test_default_shown(self):
        d2 = generate_d2([VizPerson])
        self.assertIn('= 0', d2)

    def test_module_container(self):
        d2 = generate_d2([VizPerson])
        module = VizPerson.__module__
        container_id = module.replace('.', '_')
        self.assertIn(f'{container_id}:', d2)
        self.assertIn(f'label: "{module}"', d2)

    def test_multiple_templates(self):
        d2 = generate_d2([VizPerson, VizBadge])
        self.assertIn('VizPerson', d2)
        self.assertIn('VizBadge', d2)

    def test_docstring_note(self):
        d2 = generate_d2([VizPerson])
        self.assertIn('A person record.', d2)
        self.assertIn('shape: cloud', d2)
        self.assertIn('VizPerson_note -> VizPerson', d2)

    def test_no_docstring_no_note(self):
        d2 = generate_d2([VizBadge])
        self.assertNotIn('cloud', d2)

    def test_template_fill_color(self):
        d2 = generate_d2([VizPerson])
        self.assertIn('style.fill: "#4a90d9"', d2)


# =============================================================================
# Slot descriptions
# =============================================================================

class TestGenerateD2SlotDescriptions(unittest.TestCase):
    """Slot descriptions from standalone strings after annotations."""

    def test_slot_description_in_ir(self):
        dsl_def = VizDocSlots.__clipspyx_dsl__
        slots = {s.name: s for s in dsl_def.slots}
        self.assertEqual(slots['name'].description,
                         'Full legal name of the person')
        self.assertEqual(slots['age'].description, 'Age in years')
        self.assertIsNone(slots['title'].description)

    def test_slot_description_rendered_as_note(self):
        d2 = generate_d2([VizDocSlots])
        # Page note for documented slot
        self.assertIn('Full legal name of the person', d2)
        self.assertIn('shape: page', d2)
        # Note connects to the slot row
        self.assertIn('_name_doc -> VizDocSlots.name', d2)

    def test_multiple_slot_descriptions(self):
        d2 = generate_d2([VizDocSlots])
        self.assertIn('Full legal name of the person', d2)
        self.assertIn('Age in years', d2)
        # Two page notes (name and age), not title
        self.assertEqual(d2.count('shape: page'), 2)

    def test_undocumented_slot_no_note(self):
        d2 = generate_d2([VizDocSlots])
        self.assertNotIn('_title_doc', d2)

    def test_no_descriptions_no_notes(self):
        d2 = generate_d2([VizPerson])
        self.assertNotIn('shape: page', d2)


# =============================================================================
# Fact-address edges
# =============================================================================

class TestGenerateD2FactAddress(unittest.TestCase):
    """Dashed edges from template to template for fact-address slots."""

    def test_fact_address_edge(self):
        d2 = generate_d2([VizPerson, VizDepartment])
        self.assertIn('stroke-dash', d2)
        self.assertIn('head', d2)

    def test_fact_address_shows_typed_template(self):
        d2 = generate_d2([VizPerson, VizDepartment])
        # Should show "head: VizPerson" not "head: FACT-ADDRESS"
        self.assertIn('VizPerson', d2)
        self.assertNotIn('FACT-ADDRESS', d2)

    def test_fact_address_edge_direction(self):
        d2 = generate_d2([VizPerson, VizDepartment])
        dept_path = _d2_path(VizDepartment)
        person_path = _d2_path(VizPerson)
        self.assertIn(f'{dept_path} -> {person_path}', d2)


# =============================================================================
# Rule detail: sql_table with CE rows, bound vars, edge annotations
# =============================================================================

class TestGenerateD2Rules(unittest.TestCase):
    """Rules rendered as sql_table with CE rows and edges."""

    def test_rule_is_sql_table(self):
        class VizGreetAdult(Rule):
            VizPerson(name=name, age=age)
            age >= 18

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizGreetAdult])
        self.assertIn('shape: sql_table', d2)

    def test_ce_rows_shown(self):
        class VizGreetAdult(Rule):
            VizPerson(name=name, age=age)
            age >= 18

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizGreetAdult])
        # Pattern CE row
        self.assertIn('VizPerson(name, age)', d2)
        # Test CE row shows Python infix, no ?
        self.assertIn('age >= 18', d2)
        self.assertNotIn('?age', d2)

    def test_assigned_pattern_row(self):
        class VizAssigned(Rule):
            p = VizPerson(name=name)

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizAssigned])
        # Python syntax: = not <-
        self.assertIn('p = VizPerson(name)', d2)
        self.assertNotIn('<-', d2)

    def test_bound_vars_row(self):
        class VizGreetAdult(Rule):
            p = VizPerson(name=name, age=age)
            age >= 18

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizGreetAdult])
        self.assertIn('vars:', d2)
        # No ? prefix on variables
        self.assertNotIn('?p', d2)
        self.assertNotIn('?name', d2)
        self.assertNotIn('?age', d2)
        # Bare names present
        self.assertRegex(d2, r'\bp\b')
        self.assertRegex(d2, r'\bname\b')
        self.assertRegex(d2, r'\bage\b')

    def test_rule_edge_to_template(self):
        class VizGreetAdult(Rule):
            VizPerson(name=name, age=age)
            age >= 18

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizGreetAdult])
        rule_path = _d2_path(VizGreetAdult)
        tpl_path = _d2_path(VizPerson)
        self.assertIn(f'{rule_path} -> {tpl_path}', d2)

    def test_rule_edge_slot_label(self):
        class VizGreetAdult(Rule):
            VizPerson(name=name, age=age)
            age >= 18

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizGreetAdult])
        self.assertIn('name, age', d2)

    def test_salience_row(self):
        class VizHighPriority(Rule):
            __salience__ = 10
            VizPerson(name=name)

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizHighPriority])
        self.assertIn('salience: 10', d2)

    def test_rule_fill_color(self):
        class VizColorRule(Rule):
            VizPerson(name=name)

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizColorRule])
        # Rule uses purple fill, template uses blue fill
        self.assertIn('#8b5cf6', d2)
        self.assertIn('#4a90d9', d2)


# =============================================================================
# Complex CEs: edge annotations and CE rows
# =============================================================================

class TestGenerateD2ComplexCEs(unittest.TestCase):
    """Complex CEs produce annotated edges and descriptive rows."""

    def test_not_ce_edge_annotated(self):
        class VizNoBob(Rule):
            ~VizPerson(name="Bob")

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizNoBob])
        rule_path = _d2_path(VizNoBob)
        tpl_path = _d2_path(VizPerson)
        self.assertIn(f'{rule_path} -> {tpl_path}', d2)
        # Edge label includes CE type
        self.assertIn('not:', d2)

    def test_not_ce_row(self):
        class VizNoBob(Rule):
            ~VizPerson(name="Bob")

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizNoBob])
        self.assertIn('not VizPerson(name)', d2)

    def test_or_ce_edges_annotated(self):
        class VizAOrB(Rule):
            VizPerson(name="Alice") | VizBadge(owner="Bob")

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizBadge, VizAOrB])
        rule_path = _d2_path(VizAOrB)
        person_path = _d2_path(VizPerson)
        badge_path = _d2_path(VizBadge)
        self.assertIn(f'{rule_path} -> {person_path}', d2)
        self.assertIn(f'{rule_path} -> {badge_path}', d2)
        # Edge labels include CE type
        self.assertIn('or:', d2)

    def test_or_ce_row(self):
        class VizAOrB(Rule):
            VizPerson(name="Alice") | VizBadge(owner="Bob")

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizBadge, VizAOrB])
        self.assertIn('VizPerson(name) | VizBadge(owner)', d2)

    def test_exists_ce_edge_annotated(self):
        class VizAnyPerson(Rule):
            exists(VizPerson())

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizAnyPerson])
        rule_path = _d2_path(VizAnyPerson)
        tpl_path = _d2_path(VizPerson)
        self.assertIn(f'{rule_path} -> {tpl_path}', d2)
        self.assertIn('exists', d2)

    def test_exists_ce_row(self):
        class VizAnyPerson(Rule):
            exists(VizPerson())

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizAnyPerson])
        self.assertIn('exists(VizPerson())', d2)

    def test_forall_ce_edges_annotated(self):
        class VizAllBadged(Rule):
            forall(VizPerson(name=name), VizBadge(owner=name))

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizBadge, VizAllBadged])
        rule_path = _d2_path(VizAllBadged)
        person_path = _d2_path(VizPerson)
        badge_path = _d2_path(VizBadge)
        self.assertIn(f'{rule_path} -> {person_path}', d2)
        self.assertIn(f'{rule_path} -> {badge_path}', d2)
        self.assertIn('forall:', d2)

    def test_forall_ce_row(self):
        class VizAllBadged(Rule):
            forall(VizPerson(name=name), VizBadge(owner=name))

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizBadge, VizAllBadged])
        self.assertIn('forall(VizPerson(name), VizBadge(owner))', d2)

    def test_logical_ce_edge_annotated(self):
        class VizLogPerson(Rule):
            logical(VizPerson(name=name))

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizLogPerson])
        rule_path = _d2_path(VizLogPerson)
        tpl_path = _d2_path(VizPerson)
        self.assertIn(f'{rule_path} -> {tpl_path}', d2)
        self.assertIn('logical:', d2)

    def test_logical_ce_row(self):
        class VizLogPerson(Rule):
            logical(VizPerson(name=name))

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizLogPerson])
        self.assertIn('logical(VizPerson(name))', d2)


# =============================================================================
# CE labels
# =============================================================================

class TestGenerateD2CELabels(unittest.TestCase):
    """CE labels from inline comments, descriptions from standalone strings."""

    def test_assigned_pattern_uses_var_name_as_key(self):
        class VizLabelAssign(Rule):
            p = VizPerson(name=name)

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizLabelAssign])
        # The assigned var "p" becomes the D2 row key
        self.assertIn('p: "p = VizPerson(name)"', d2)
        self.assertNotIn('ce0', d2)

    def test_comment_labels_pattern_ce(self):
        class VizCommentPattern(Rule):
            VizPerson(name=name)  # find_person

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizCommentPattern])
        self.assertIn('find_person: "VizPerson(name)"', d2)
        self.assertNotIn('ce0', d2)

    def test_comment_labels_test_ce(self):
        class VizCommentTest(Rule):
            VizPerson(name=name, age=age)
            age >= 18  # adult_check

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizCommentTest])
        self.assertIn('adult_check: "age >= 18"', d2)
        self.assertNotIn('ce1', d2)

    def test_comment_labels_not_ce(self):
        class VizCommentNot(Rule):
            ~VizPerson(name="Bob")  # no_bob

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizCommentNot])
        self.assertIn('no_bob: "not VizPerson(name)"', d2)
        self.assertNotIn('ce0', d2)

    def test_comment_overrides_assigned_var_name(self):
        class VizCommentOverride(Rule):
            p = VizPerson(name=name)  # employee

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizCommentOverride])
        self.assertIn('employee:', d2)
        self.assertNotIn('p:', d2)

    def test_unlabeled_ce_falls_back_to_index(self):
        class VizUnlabeled(Rule):
            VizPerson(name=name)

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizUnlabeled])
        self.assertIn('ce0:', d2)

    def test_mixed_labeled_and_unlabeled(self):
        class VizMixed(Rule):
            VizPerson(name=name, age=age)  # find_person
            age >= 18

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizMixed])
        self.assertIn('find_person:', d2)
        self.assertIn('ce1:', d2)
        self.assertNotIn('ce0', d2)

    def test_comment_label_in_ir(self):
        class VizIRComment(Rule):
            VizPerson(name=name)  # eligible

            def __action__(self):
                pass

        dsl_def = VizIRComment.__clipspyx_dsl__
        self.assertEqual(dsl_def.conditions[0].label, 'eligible')

    def test_description_from_string(self):
        class VizDescRule(Rule):
            VizPerson(name=name, age=age)  # find_person
            """Find person records for eligibility check"""
            age >= 18

            def __action__(self):
                pass

        dsl_def = VizDescRule.__clipspyx_dsl__
        self.assertEqual(dsl_def.conditions[0].label, 'find_person')
        self.assertEqual(
            dsl_def.conditions[0].description,
            'Find person records for eligibility check')

    def test_description_rendered_as_note(self):
        class VizDescD2(Rule):
            VizPerson(name=name)  # find_person
            """Match any person record"""

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizDescD2])
        # CE row stays compact
        self.assertIn('find_person: "VizPerson(name)"', d2)
        # Individual page note per CE description
        self.assertIn('Match any person record', d2)
        self.assertIn('shape: page', d2)
        # Note connects to the specific CE row
        self.assertIn('_find_person_doc -> VizDescD2.find_person', d2)

    def test_multiple_descriptions_individual(self):
        class VizMultiDesc(Rule):
            VizPerson(name=name, age=age)  # person
            """Find the person"""
            age >= 18  # adult
            """Must be an adult"""

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizMultiDesc])
        # Individual note per CE description
        self.assertIn('Find the person', d2)
        self.assertIn('Must be an adult', d2)
        # Two separate page notes
        self.assertEqual(d2.count('shape: page'), 2)
        # Each connects to its own CE row
        self.assertIn('_person_doc -> VizMultiDesc.person', d2)
        self.assertIn('_adult_doc -> VizMultiDesc.adult', d2)

    def test_description_without_label(self):
        class VizDescNoLabel(Rule):
            VizPerson(name=name)
            """Match any person"""
            def __action__(self):
                pass

        dsl_def = VizDescNoLabel.__clipspyx_dsl__
        self.assertEqual(
            dsl_def.conditions[0].description,
            'Match any person')


# =============================================================================
# Effect visualization
# =============================================================================

class VizCounter(Template):
    value: int


class VizResult(Template):
    msg: str


class TestGenerateD2Effects(unittest.TestCase):
    """Effect rows and edges in D2 output."""

    def test_assert_effect_row_in_table(self):
        class VizAssertRule(Rule):
            VizPerson(name=name)
            asserts(VizResult(msg=name))

        d2 = generate_d2([VizPerson, VizResult, VizAssertRule])
        self.assertIn('assert', d2.lower())
        self.assertIn('VizResult', d2)

    def test_retract_effect_row_in_table(self):
        class VizRetractRule(Rule):
            p = VizPerson(name=name)
            retracts(p)

        d2 = generate_d2([VizPerson, VizRetractRule])
        self.assertIn('retract p', d2)

    def test_modify_effect_row_in_table(self):
        class VizModifyRule(Rule):
            p = VizCounter(value=v)
            modifies(p, value=99)

        d2 = generate_d2([VizCounter, VizModifyRule])
        self.assertIn('modify p(value)', d2)

    def test_assert_edge_red_solid(self):
        class VizAssertEdge(Rule):
            VizPerson(name=name)
            asserts(VizResult(msg=name))

        d2 = generate_d2([VizPerson, VizResult, VizAssertEdge])
        self.assertIn('#e74c3c', d2)
        self.assertIn('stroke-width: 2', d2)
        # Assert edge should NOT be dashed
        rule_path = _d2_path(VizAssertEdge)
        result_path = _d2_path(VizResult)
        # Find the assert edge line
        for line in d2.splitlines():
            if 'assert' in line and result_path in line:
                self.assertNotIn('stroke-dash', line)
                break

    def test_retract_edge_red_dashed(self):
        class VizRetractEdge(Rule):
            p = VizPerson(name=name)
            retracts(p)

        d2 = generate_d2([VizPerson, VizRetractEdge])
        self.assertIn('#e74c3c', d2)
        self.assertIn('stroke-dash', d2)

    def test_modify_edge_orange(self):
        class VizModifyEdge(Rule):
            p = VizCounter(value=v)
            modifies(p, value=99)

        d2 = generate_d2([VizCounter, VizModifyEdge])
        self.assertIn('#f39c12', d2)

    def test_assert_edge_direction(self):
        class VizAssertDir(Rule):
            VizPerson(name=name)
            asserts(VizResult(msg=name))

        d2 = generate_d2([VizPerson, VizResult, VizAssertDir])
        rule_path = _d2_path(VizAssertDir)
        result_path = _d2_path(VizResult)
        self.assertIn(f'{rule_path} -> {result_path}', d2)

    def test_retract_edge_direction(self):
        class VizRetractDir(Rule):
            p = VizPerson(name=name)
            retracts(p)

        d2 = generate_d2([VizPerson, VizRetractDir])
        rule_path = _d2_path(VizRetractDir)
        person_path = _d2_path(VizPerson)
        self.assertIn(f'{rule_path} -> {person_path}', d2)

    def test_multiple_effect_edges(self):
        class VizMultiEffect(Rule):
            p = VizPerson(name=name)
            retracts(p)
            asserts(VizResult(msg=name))

        d2 = generate_d2([VizPerson, VizResult, VizMultiEffect])
        rule_path = _d2_path(VizMultiEffect)
        person_path = _d2_path(VizPerson)
        result_path = _d2_path(VizResult)
        # Both edges present
        retract_found = False
        assert_found = False
        for line in d2.splitlines():
            if 'retract' in line and person_path in line:
                retract_found = True
            if 'assert' in line and result_path in line:
                assert_found = True
        self.assertTrue(retract_found, "Retract edge not found")
        self.assertTrue(assert_found, "Assert edge not found")

    def test_effects_with_no_action_still_render(self):
        """Effects-only rule (no __action__) renders correctly."""
        class VizEffectsOnly(Rule):
            asserts(VizResult(msg="hello"))

        d2 = generate_d2([VizResult, VizEffectsOnly])
        self.assertIn('VizEffectsOnly', d2)
        self.assertIn('shape: sql_table', d2)


# =============================================================================
# group_by_kind
# =============================================================================

class TestGenerateD2GroupByKind(unittest.TestCase):
    """group_by_kind puts templates and rules in separate sub-containers."""

    def test_creates_templates_container(self):
        class VizGBKRule(Rule):
            VizPerson(name=name)

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizGBKRule], group_by_kind=True)
        self.assertIn('Templates: {', d2)
        self.assertIn('label: "Templates"', d2)

    def test_creates_rules_container(self):
        class VizGBKRule(Rule):
            VizPerson(name=name)

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizGBKRule], group_by_kind=True)
        self.assertIn('Rules: {', d2)
        self.assertIn('label: "Rules"', d2)

    def test_edges_use_kind_path(self):
        class VizGBKRule(Rule):
            VizPerson(name=name)

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizGBKRule], group_by_kind=True)
        module = VizPerson.__module__.replace('.', '_')
        self.assertIn(
            f'{module}.Rules.VizGBKRule -> {module}.Templates.VizPerson',
            d2)

    def test_default_is_flat(self):
        class VizGBKRule(Rule):
            VizPerson(name=name)

            def __action__(self):
                pass

        d2 = generate_d2([VizPerson, VizGBKRule])
        self.assertNotIn('Templates: {', d2)
        self.assertNotIn('Rules: {', d2)

    def test_templates_only(self):
        d2 = generate_d2([VizPerson, VizBadge], group_by_kind=True)
        self.assertIn('Templates: {', d2)
        self.assertNotIn('Rules: {', d2)

    def test_env_passthrough(self):
        class VizGBKRule(Rule):
            VizPerson(name=name)

            def __action__(self):
                pass

        env = Environment()
        env.define(VizPerson)
        env.define(VizGBKRule)
        result = env.visualize(group_by_kind=True)
        self.assertIn('Templates: {', result)
        self.assertIn('Rules: {', result)


# =============================================================================
# Empty
# =============================================================================

class TestGenerateD2Empty(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(generate_d2([]), '')


# =============================================================================
# Environment integration
# =============================================================================

class TestEnvironmentVisualize(unittest.TestCase):

    def test_returns_str(self):
        env = Environment()
        env.define(VizPerson)
        result = env.visualize()
        self.assertIsInstance(result, str)
        self.assertIn('VizPerson', result)

    def test_empty_env(self):
        env = Environment()
        result = env.visualize()
        self.assertEqual(result, '')

    def test_includes_rules(self):
        class VizSimpleRule(Rule):
            VizPerson(name=name)

            def __action__(self):
                pass

        env = Environment()
        env.define(VizPerson)
        env.define(VizSimpleRule)
        result = env.visualize()
        self.assertIn('VizSimpleRule', result)
        self.assertIn('VizPerson', result)

    def test_clear_resets_defs(self):
        env = Environment()
        env.define(VizPerson)
        env.clear()
        result = env.visualize()
        self.assertEqual(result, '')


# =============================================================================
# render_d2
# =============================================================================

class TestRenderD2(unittest.TestCase):

    def test_raises_file_not_found_when_d2_missing(self):
        with patch('clipspyx.dsl.visualize.subprocess.run',
                   side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError) as ctx:
                render_d2('test: {}', '/tmp/test.svg')
            self.assertIn('d2 CLI not found', str(ctx.exception))

    def test_default_layout_is_elk(self):
        with patch('clipspyx.dsl.visualize.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            render_d2('test: {}', '/tmp/test.svg')
            cmd = mock_run.call_args[0][0]
            self.assertIn('--layout', cmd)
            idx = cmd.index('--layout')
            self.assertEqual(cmd[idx + 1], 'elk')

    def test_custom_layout(self):
        with patch('clipspyx.dsl.visualize.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            render_d2('test: {}', '/tmp/test.svg', layout='dagre')
            cmd = mock_run.call_args[0][0]
            idx = cmd.index('--layout')
            self.assertEqual(cmd[idx + 1], 'dagre')


if __name__ == '__main__':
    unittest.main()
