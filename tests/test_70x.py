"""Tests for CLIPS 7.0 features.

All tests in this module are skipped when built against CLIPS 6.4x.

"""

import unittest

import clipspyx
from clipspyx import Environment, Symbol

CLIPS_70 = clipspyx.CLIPS_MAJOR >= 7


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestDeftable(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_deftable_build_and_iterate(self):
        """Deftables can be built and iterated."""
        self.env.build(
            '(deftable colors (name red green blue)'
            ' (hex ff0000 00ff00 0000ff))')

        tables = list(self.env.deftables())
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0].name, 'colors')

    def test_deftable_find(self):
        """Deftables can be found by name."""
        self.env.build(
            '(deftable sizes (label small medium large)'
            ' (value 1 2 3))')

        table = self.env.find_deftable('sizes')
        self.assertEqual(table.name, 'sizes')

    def test_deftable_find_not_found(self):
        """LookupError when deftable not found."""
        with self.assertRaises(LookupError):
            self.env.find_deftable('nonexistent')

    def test_deftable_properties(self):
        """Deftable properties are accessible."""
        self.env.build(
            '(deftable props (x a b) (y 1 2))')

        table = self.env.find_deftable('props')
        self.assertEqual(table.name, 'props')
        self.assertEqual(table.module.name, 'MAIN')
        self.assertTrue(table.deletable)
        self.assertGreater(table.row_count, 0)
        self.assertGreater(table.column_count, 0)

    def test_deftable_ppform(self):
        """Deftable string representation works."""
        self.env.build(
            '(deftable t1 (col a b) (val x y))')

        table = self.env.find_deftable('t1')
        self.assertIn('deftable', str(table))
        self.assertIn('Deftable:', repr(table))

    def test_deftable_lookup(self):
        """Table values can be looked up by row and column index."""
        self.env.build(
            '(deftable colors (name red green blue)'
            ' (hex ff0000 00ff00 0000ff))')

        table = self.env.find_deftable('colors')
        # Row 0 is the first data row (hex)
        val = table.lookup(0, 0)
        self.assertEqual(val, Symbol('hex'))
        val = table.lookup(0, 1)
        self.assertEqual(val, Symbol('ff0000'))

    def test_deftable_undefine(self):
        """Deftables can be undefined."""
        self.env.build(
            '(deftable removable (col a b) (val x y))')

        table = self.env.find_deftable('removable')
        self.assertTrue(table.deletable)

        table.undefine()

        with self.assertRaises(LookupError):
            self.env.find_deftable('removable')

    def test_deftable_equality(self):
        """Deftable equality and hashing."""
        self.env.build(
            '(deftable eq-test (col a b) (val x y))')

        t1 = self.env.find_deftable('eq-test')
        t2 = self.env.find_deftable('eq-test')
        self.assertEqual(t1, t2)
        self.assertEqual(hash(t1), hash(t2))

    def test_multiple_deftables(self):
        """Multiple deftables can coexist."""
        self.env.build('(deftable t1 (col a b) (val x y))')
        self.env.build('(deftable t2 (name p q) (data r s))')

        tables = list(self.env.deftables())
        names = {t.name for t in tables}
        self.assertEqual(names, {'t1', 't2'})


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestGoals(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_goals_empty(self):
        """Goals list is empty by default."""
        goals = list(self.env.goals())
        self.assertEqual(len(goals), 0)

    def test_goal_list_changed(self):
        """Goal list changed flag can be read and set."""
        self.env.goal_list_changed = False
        self.assertFalse(self.env.goal_list_changed)

    def test_can_match_goal(self):
        """Template can_match_goal reflects backward chaining rules."""
        self.env.build('(deftemplate data (slot value))')
        self.env.build('(deftemplate other (slot x))')

        # Before any backward chaining rule, should not match goals
        data_tpl = self.env.find_template('data')
        other_tpl = self.env.find_template('other')

        # Add a backward chaining rule referencing data
        self.env.build(
            '(defrule bc-rule'
            ' (goal (data (value ?v)))'
            ' =>'
            ' (assert (other (x ?v))))')

        # Re-check after rule
        data_tpl = self.env.find_template('data')
        self.assertTrue(data_tpl.can_match_goal())


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestTemplateInheritance(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_has_supertemplate(self):
        """Deftemplate inheritance via is-a."""
        self.env.build('(deftemplate vehicle (slot make) (slot year))')
        self.env.build('(deftemplate car (is-a vehicle) (slot doors))')

        car = self.env.find_template('car')
        vehicle = self.env.find_template('vehicle')

        self.assertTrue(car.has_supertemplate(vehicle))
        self.assertFalse(vehicle.has_supertemplate(car))

    def test_no_supertemplate(self):
        """Unrelated templates are not supertemplates."""
        self.env.build('(deftemplate alpha (slot a))')
        self.env.build('(deftemplate beta (slot b))')

        alpha = self.env.find_template('alpha')
        beta = self.env.find_template('beta')

        self.assertFalse(alpha.has_supertemplate(beta))
        self.assertFalse(beta.has_supertemplate(alpha))

    def test_inherited_slots(self):
        """Child template inherits parent slots."""
        self.env.build('(deftemplate parent-tpl (slot base-slot))')
        self.env.build(
            '(deftemplate child-tpl (is-a parent-tpl) (slot extra-slot))')

        child = self.env.find_template('child-tpl')
        slot_names = {s.name for s in child.slots}
        self.assertIn('base-slot', slot_names)
        self.assertIn('extra-slot', slot_names)


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestCertaintyFactors(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_default_certainty_factor(self):
        """Facts without CFD have default CF of 100."""
        self.env.build('(deftemplate basic (slot x))')
        f = self.env.assert_string('(basic (x 1))')
        self.assertEqual(f.certainty_factor, 100)

    def test_cfd_template(self):
        """CFD templates support certainty factors."""
        self.env.build('(deftemplate sensor (is-a CFD) (slot reading))')
        t = self.env.find_template('sensor')

        # Default CF is 100
        f = t.assert_fact(reading=42)
        self.assertEqual(f.certainty_factor, 100)

        # Assert with explicit CF
        f2 = t.assert_fact(reading=99, CF=75)
        self.assertEqual(f2.certainty_factor, 75)


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestWatchGoals(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_watch_goals(self):
        """Template goal watching can be toggled."""
        self.env.build('(deftemplate watched (slot x))')
        t = self.env.find_template('watched')

        self.assertFalse(t.watch_goals)
        t.watch_goals = True
        self.assertTrue(t.watch_goals)
        t.watch_goals = False
        self.assertFalse(t.watch_goals)


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestFMUpdate(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_update_slots(self):
        """update_slots creates a new fact with updated values."""
        self.env.build('(deftemplate item (slot name) (slot qty))')
        t = self.env.find_template('item')

        original = t.assert_fact(name='apple', qty=5)
        updated = original.update_slots(qty=10)

        self.assertEqual(updated['qty'], 10)
        self.assertEqual(updated['name'], 'apple')

    def test_update_returns_template_fact(self):
        """update_slots returns a TemplateFact."""
        self.env.build('(deftemplate data (slot val))')
        t = self.env.find_template('data')
        f = t.assert_fact(val=1)

        result = f.update_slots(val=2)
        self.assertIsInstance(result, clipspyx.TemplateFact)


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestVersionExports(unittest.TestCase):
    def test_clips_major(self):
        """CLIPS_MAJOR is accessible and correct."""
        self.assertEqual(clipspyx.CLIPS_MAJOR, 7)

    def test_deftable_importable(self):
        """Deftable is importable from clipspyx on 7.0."""
        from clipspyx import Deftable
        self.assertIsNotNone(Deftable)


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestGoalGeneration(unittest.TestCase):
    """Test that backward chaining actually generates goals at runtime."""

    def setUp(self):
        self.env = Environment()

    def _setup_backward_chaining(self):
        """Set up a backward chaining scenario.

        Two rules are needed:
        1. A goal CE rule that enables goal generation for the template
        2. A forward rule with regular patterns that triggers goal generation
           when prior patterns match but later ones don't

        """
        self.env.build('(deftemplate symptom (slot name))')
        self.env.build('(deftemplate diagnosis (slot disease))')

        # This rule enables goal generation for symptom template
        self.env.build(
            '(defrule goal-handler'
            ' (goal (symptom (name ?n)))'
            ' (not (symptom (name ?n)))'
            ' =>'
            ' (printout t ""))')

        # This forward rule generates goals when fever matches but rash doesn't
        self.env.build(
            '(defrule check-measles'
            ' (symptom (name fever))'
            ' (symptom (name rash))'
            ' =>'
            ' (assert (diagnosis (disease measles))))')

    def test_goals_generated_by_backward_chaining(self):
        """Asserting a matching fact triggers goal generation."""
        self._setup_backward_chaining()

        self.env.reset()
        self.env.assert_string('(symptom (name fever))')

        goals = list(self.env.goals())
        self.assertGreater(len(goals), 0)

    def test_goal_iterable_as_facts(self):
        """Goals appear as TemplateFact objects with slot values."""
        self._setup_backward_chaining()

        self.env.reset()
        self.env.assert_string('(symptom (name fever))')

        goals = list(self.env.goals())
        self.assertGreater(len(goals), 0)
        goal = goals[0]
        self.assertEqual(goal['name'], Symbol('rash'))

    def test_retract_all_goals(self):
        """retract_all_goals clears generated goals."""
        self._setup_backward_chaining()

        self.env.reset()
        self.env.assert_string('(symptom (name fever))')

        goals = list(self.env.goals())
        self.assertGreater(len(goals), 0)

        self.env.retract_all_goals()

        goals = list(self.env.goals())
        self.assertEqual(len(goals), 0)

    def test_goal_list_changed_after_generation(self):
        """goal_list_changed reflects engine activity."""
        self._setup_backward_chaining()

        self.env.goal_list_changed = False
        self.env.reset()
        self.env.assert_string('(symptom (name fever))')

        self.assertTrue(self.env.goal_list_changed)


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestUpdateVsModifySemantics(unittest.TestCase):
    """Verify update vs modify rete network reevaluation differences.

    Both update and modify change the fact in place (same index).
    The difference is in rete reevaluation:
    - modify: reevaluates ALL potentially matching patterns
    - update: only reevaluates rules explicitly matching the changed slot

    """

    def setUp(self):
        self.env = Environment()

    def test_update_changes_value_same_index(self):
        """update_slots changes slot values but keeps the same fact index."""
        self.env.build('(deftemplate item (slot name) (slot qty))')
        t = self.env.find_template('item')

        original = t.assert_fact(name='apple', qty=5)
        original_index = original.index

        updated = original.update_slots(qty=10)

        self.assertEqual(updated.index, original_index)
        self.assertEqual(updated['qty'], 10)
        self.assertEqual(updated['name'], 'apple')

    def test_modify_changes_value_same_index(self):
        """modify_slots also keeps the same fact index."""
        self.env.build('(deftemplate item (slot name) (slot qty))')
        t = self.env.find_template('item')

        original = t.assert_fact(name='apple', qty=5)
        original_index = original.index

        original.modify_slots(qty=10)

        facts = list(t.facts())
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0].index, original_index)
        self.assertEqual(facts[0]['qty'], 10)

    def test_update_on_cfd_template(self):
        """update_slots works on CFD templates for CF changes."""
        self.env.build('(deftemplate sensor (is-a CFD) (slot reading))')
        t = self.env.find_template('sensor')

        f = t.assert_fact(reading=42, CF=80)
        self.assertEqual(f.certainty_factor, 80)

        updated = f.update_slots(CF=50)
        self.assertEqual(updated.certainty_factor, 50)
        self.assertEqual(updated['reading'], 42)

    def test_update_only_reevaluates_matching_slot_rules(self):
        """update does not trigger rules that don't match the changed slot."""
        self.env.build('(deftemplate item (slot name) (slot qty))')
        self.env.build('(deftemplate log (slot msg))')

        # Rule that matches on name (not qty)
        self.env.build(
            '(defrule name-watcher'
            ' (item (name ?n))'
            ' =>'
            ' (assert (log (msg ?n))))')

        t = self.env.find_template('item')
        f = t.assert_fact(name='apple', qty=5)
        self.env.run()

        log_t = self.env.find_template('log')
        logs_before = len(list(log_t.facts()))

        # update qty -- should NOT re-trigger name-watcher
        f.update_slots(qty=10)
        self.env.run()

        logs_after = len(list(log_t.facts()))
        self.assertEqual(logs_before, logs_after)


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestDeftableLookupViaCLIPS(unittest.TestCase):
    """Test deftable lookup via CLIPS (lookup) function, not just C API."""

    def setUp(self):
        self.env = Environment()

    def test_lookup_via_eval(self):
        """Table values accessible via CLIPS (lookup) function."""
        self.env.build(
            '(deftable colors (name red green blue)'
            ' (hex ff0000 00ff00 0000ff))')

        result = self.env.eval('(lookup colors hex red)')
        self.assertEqual(result, Symbol('ff0000'))

    def test_lookup_different_columns(self):
        """Lookup works across different column/row combinations."""
        self.env.build(
            '(deftable prices (item apple banana cherry)'
            ' (cost 1.50 0.75 3.00))')

        result = self.env.eval('(lookup prices cost banana)')
        self.assertAlmostEqual(float(result), 0.75)

    def test_c_api_and_eval_agree(self):
        """C API lookup and CLIPS eval return the same value."""
        self.env.build(
            '(deftable colors (name red green blue)'
            ' (hex ff0000 00ff00 0000ff))')

        table = self.env.find_deftable('colors')
        # First group is column headers, second group is data row 0.
        # Row 0 elements: [hex, ff0000, 00ff00, 0000ff]
        # Col 3 = 0000ff (blue's hex)
        c_val = table.lookup(0, 3)

        # CLIPS eval
        clips_val = self.env.eval('(lookup colors hex blue)')

        self.assertEqual(c_val, clips_val)


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestCertaintyFactorPropagation(unittest.TestCase):
    """Test CF propagation through rule firing."""

    def setUp(self):
        self.env = Environment()

    def test_cf_combination_on_duplicate(self):
        """Asserting duplicate CFD facts combines their CFs."""
        self.env.build('(deftemplate symptom (is-a CFD) (slot name))')

        f1 = self.env.assert_string('(symptom (name fever) (CF 60))')
        self.assertEqual(f1.certainty_factor, 60)

        # Assert same fact again with different CF: should combine
        f2 = self.env.assert_string('(symptom (name fever) (CF 50))')
        # Both positive: CF = 60 + 50 - (60*50)/100 = 110 - 30 = 80
        self.assertEqual(f2.certainty_factor, 80)

    def test_cf_adjustment_through_rule(self):
        """Rule with (declare (certainty N)) adjusts asserted fact CF."""
        self.env.build('(deftemplate symptom (is-a CFD) (slot name))')
        self.env.build('(deftemplate diagnosis (is-a CFD) (slot disease))')

        # Rule with certainty 80
        self.env.build(
            '(defrule measles'
            ' (declare (certainty 80))'
            ' (symptom (name fever))'
            ' (symptom (name rash))'
            ' =>'
            ' (assert (diagnosis (disease measles))))')

        # Assert symptoms with known CFs
        self.env.assert_string('(symptom (name fever) (CF 50))')
        self.env.assert_string('(symptom (name rash) (CF 64))')

        self.env.run()

        # Tally = min(50, 64) = 50
        # Adjusted = (50/100) * (80/100) * 100 = 40
        diag = self.env.find_template('diagnosis')
        facts = list(diag.facts())
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0].certainty_factor, 40)

    def test_cf_below_threshold_no_match(self):
        """Facts with CF < 20 do not trigger rule patterns."""
        self.env.build('(deftemplate symptom (is-a CFD) (slot name))')
        self.env.build('(deftemplate diagnosis (is-a CFD) (slot disease))')

        self.env.build(
            '(defrule simple'
            ' (symptom (name fever))'
            ' =>'
            ' (assert (diagnosis (disease detected))))')

        # Assert with CF below threshold (< 20)
        self.env.assert_string('(symptom (name fever) (CF 10))')
        self.env.run()

        diag = self.env.find_template('diagnosis')
        facts = list(diag.facts())
        self.assertEqual(len(facts), 0)


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestMultiLevelInheritance(unittest.TestCase):
    """Test grandparent/multi-level template inheritance chains."""

    def setUp(self):
        self.env = Environment()

    def test_grandparent_chain(self):
        """Three-level inheritance: grandchild -> child -> parent."""
        self.env.build('(deftemplate vehicle (slot make))')
        self.env.build('(deftemplate car (is-a vehicle) (slot doors))')
        self.env.build('(deftemplate sedan (is-a car) (slot trunk-size))')

        sedan = self.env.find_template('sedan')
        car = self.env.find_template('car')
        vehicle = self.env.find_template('vehicle')

        # Direct parent
        self.assertTrue(sedan.has_supertemplate(car))
        # Grandparent
        self.assertTrue(sedan.has_supertemplate(vehicle))
        # Reverse is false
        self.assertFalse(vehicle.has_supertemplate(sedan))
        self.assertFalse(car.has_supertemplate(sedan))

    def test_grandchild_inherits_all_slots(self):
        """Grandchild template has slots from all ancestors."""
        self.env.build('(deftemplate base (slot id))')
        self.env.build('(deftemplate mid (is-a base) (slot level))')
        self.env.build('(deftemplate leaf (is-a mid) (slot detail))')

        leaf = self.env.find_template('leaf')
        slot_names = {s.name for s in leaf.slots}
        self.assertIn('id', slot_names)
        self.assertIn('level', slot_names)
        self.assertIn('detail', slot_names)

    def test_grandchild_fact_has_ancestor_slots(self):
        """Facts from grandchild template include ancestor slot values."""
        self.env.build('(deftemplate base (slot id))')
        self.env.build('(deftemplate mid (is-a base) (slot level))')
        self.env.build('(deftemplate leaf (is-a mid) (slot detail))')

        leaf = self.env.find_template('leaf')
        f = leaf.assert_fact(id='root', level='middle', detail='fine')

        self.assertEqual(f['id'], 'root')
        self.assertEqual(f['level'], 'middle')
        self.assertEqual(f['detail'], 'fine')

    def test_sibling_templates_not_related(self):
        """Two children of the same parent are not supertemplates of each other."""
        self.env.build('(deftemplate animal (slot name))')
        self.env.build('(deftemplate dog (is-a animal) (slot breed))')
        self.env.build('(deftemplate cat (is-a animal) (slot color))')

        dog = self.env.find_template('dog')
        cat = self.env.find_template('cat')
        animal = self.env.find_template('animal')

        self.assertFalse(dog.has_supertemplate(cat))
        self.assertFalse(cat.has_supertemplate(dog))
        # Both share the same parent
        self.assertTrue(dog.has_supertemplate(animal))
        self.assertTrue(cat.has_supertemplate(animal))


@unittest.skipUnless(CLIPS_70, "CLIPS 7.0+ required")
class TestUQVHandling(unittest.TestCase):
    """Test universally quantified value (UQV) handling in goal slots."""

    def setUp(self):
        self.env = Environment()
        # Template with two slots; backward chaining constrains only 'name'
        self.env.build('(deftemplate person (slot name) (slot age))')
        self.env.build('(deftemplate result (slot found))')

        # Goal CE rule enabling goal generation for person
        self.env.build(
            '(defrule goal-person'
            ' (goal (person (name ?n)))'
            ' (not (person (name ?n)))'
            ' =>'
            ' (printout t ""))')

        # Forward rule: triggers goal for person when result exists
        # but person doesn't; only 'name' is constrained, 'age' gets UQV
        self.env.build(
            '(defrule need-person'
            ' (result (found yes))'
            ' (person (name bob))'
            ' =>'
            ' (printout t ""))')

        self.env.reset()
        self.env.assert_string('(result (found yes))')

    def test_uqv_slot_returns_sentinel(self):
        """Reading an unspecified goal slot returns UniversallyQuantifiedValue."""
        goals = list(self.env.goals())
        self.assertGreater(len(goals), 0)
        goal = goals[0]
        age_val = goal['age']
        self.assertIsInstance(age_val, clipspyx.UniversallyQuantifiedValue)

    def test_uqv_singleton(self):
        """UniversallyQuantifiedValue is a singleton."""
        from clipspyx import UniversallyQuantifiedValue
        self.assertIs(UniversallyQuantifiedValue(), UniversallyQuantifiedValue())

    def test_uqv_repr_str(self):
        """str() and repr() of UQV return '??'."""
        from clipspyx import UniversallyQuantifiedValue
        v = UniversallyQuantifiedValue()
        self.assertEqual(repr(v), '??')
        self.assertEqual(str(v), '??')

    def test_uqv_bool_false(self):
        """bool(UniversallyQuantifiedValue()) is False."""
        from clipspyx import UniversallyQuantifiedValue
        self.assertFalse(bool(UniversallyQuantifiedValue()))

    def test_goal_slot_iteration_with_uqv(self):
        """Iterating all goal slots works without error when UQV is present."""
        goals = list(self.env.goals())
        self.assertGreater(len(goals), 0)
        goal = goals[0]
        # __iter__ yields (slot_name, value) pairs via slot_values()
        values = dict(goal)
        self.assertIn(Symbol('name'), values)
        self.assertIn(Symbol('age'), values)
        self.assertIsInstance(values[Symbol('age')], clipspyx.UniversallyQuantifiedValue)


class TestVersionQuery(unittest.TestCase):
    """These tests run regardless of CLIPS version."""

    def test_clips_major_exists(self):
        """CLIPS_MAJOR is always available."""
        self.assertIn(clipspyx.CLIPS_MAJOR, (6, 7))

    def test_clips_major_in_all(self):
        """CLIPS_MAJOR is in __all__."""
        self.assertIn('CLIPS_MAJOR', clipspyx.__all__)
