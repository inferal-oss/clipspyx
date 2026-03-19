import unittest

from clipspyx import Environment, TemplateFact
from clipspyx.common import CLIPS_MAJOR
from clipspyx.dsl import Template, Rule, Multi, NIL
from clipspyx.values import Symbol
from clipspyx.dsl.types import clips_type_name, is_multi, multi_element_type
from clipspyx.dsl.ir import (
    TemplateDef, SlotDef, PatternCE, AssignedPatternCE, TestCE,
    NotCE, OrCE, ExistsCE, ForallCE, LogicalCE, GoalCE, ExplicitCE,
    SlotConstraint, Var, Wildcard, Literal,
    NotConstraint, OrConstraint, PredicateConstraint,
    SlotValue, AssertEffect, RetractEffect, ModifyEffect,
)
from clipspyx.dsl.codegen import generate_deftemplate, generate_defrule, generate_typecheck_rule


# --- Templates used across tests ---

class Person(Template):
    name: str
    age: int = 0


class Badge(Template):
    owner: str
    level: int = 0


class Animal(Template):
    species: str


class Department(Template):
    name: str
    head: Person  # fact-address slot typed to Person


class Counter(Template):
    value: int


class Result(Template):
    msg: str


# =============================================================================
# Types module tests
# =============================================================================

class TestTypes(unittest.TestCase):
    def test_clips_type_name_int(self):
        self.assertEqual(clips_type_name(int), 'INTEGER')

    def test_clips_type_name_float(self):
        self.assertEqual(clips_type_name(float), 'FLOAT')

    def test_clips_type_name_str(self):
        self.assertEqual(clips_type_name(str), 'STRING')

    def test_clips_type_name_unknown(self):
        self.assertIsNone(clips_type_name(list))

    def test_multi_is_multi(self):
        self.assertTrue(is_multi(Multi[str]))
        self.assertTrue(is_multi(Multi[int]))

    def test_non_multi(self):
        self.assertFalse(is_multi(int))
        self.assertFalse(is_multi(str))

    def test_multi_element_type(self):
        self.assertEqual(multi_element_type(Multi[str]), str)
        self.assertEqual(multi_element_type(Multi[int]), int)


# =============================================================================
# Template IR tests
# =============================================================================

class TestTemplateIR(unittest.TestCase):
    def test_template_slots(self):
        td = Person.__clipspyx_dsl__
        self.assertEqual(td.name, f'{Person.__module__}.Person')
        self.assertEqual(len(td.slots), 2)

    def test_slot_name(self):
        td = Person.__clipspyx_dsl__
        self.assertEqual(td.slots[0].name, 'name')
        self.assertEqual(td.slots[0].clips_type, 'STRING')
        self.assertFalse(td.slots[0].multi)
        self.assertFalse(td.slots[0].has_default)

    def test_slot_default(self):
        td = Person.__clipspyx_dsl__
        age_slot = td.slots[1]
        self.assertEqual(age_slot.name, 'age')
        self.assertTrue(age_slot.has_default)
        self.assertEqual(age_slot.default, 0)

    def test_multislot(self):
        class WithMulti(Template):
            tags: Multi[str]

        td = WithMulti.__clipspyx_dsl__
        self.assertTrue(td.slots[0].multi)
        self.assertEqual(td.slots[0].clips_type, 'STRING')

    def test_fact_address_slot(self):
        td = Department.__clipspyx_dsl__
        head_slot = td.slots[1]
        self.assertEqual(head_slot.name, 'head')
        self.assertEqual(head_slot.clips_type, 'FACT-ADDRESS')
        self.assertEqual(head_slot.fact_template, Person.__clipspyx_dsl__.name)

    def test_fact_address_slot_name_slot_unaffected(self):
        td = Department.__clipspyx_dsl__
        name_slot = td.slots[0]
        self.assertEqual(name_slot.clips_type, 'STRING')
        self.assertIsNone(name_slot.fact_template)


# =============================================================================
# Rule parsing tests
# =============================================================================

class TestRuleParsing(unittest.TestCase):
    def test_basic_pattern_ce(self):
        class R(Rule):
            Person(name=name)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.conditions), 1)
        ce = rd.conditions[0]
        self.assertIsInstance(ce, PatternCE)
        self.assertEqual(ce.template_name, Person.__clipspyx_dsl__.name)
        self.assertEqual(len(ce.slots), 1)
        self.assertIsInstance(ce.slots[0].constraint, Var)
        self.assertEqual(ce.slots[0].constraint.name, 'name')

    def test_assigned_pattern(self):
        class R(Rule):
            p = Person(name=name, age=age)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.conditions), 1)
        ce = rd.conditions[0]
        self.assertIsInstance(ce, AssignedPatternCE)
        self.assertEqual(ce.var_name, 'p')
        self.assertEqual(ce.pattern.template_name, Person.__clipspyx_dsl__.name)
        self.assertIn('p', rd.pattern_vars)

    def test_wildcard(self):
        class R(Rule):
            Person(age=_)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        ce = rd.conditions[0]
        self.assertIsInstance(ce.slots[0].constraint, Wildcard)

    def test_literal_int(self):
        class R(Rule):
            Person(age=25)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        ce = rd.conditions[0]
        self.assertIsInstance(ce.slots[0].constraint, Literal)
        self.assertEqual(ce.slots[0].constraint.value, 25)

    def test_literal_string(self):
        class R(Rule):
            Person(name="Bob")
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        ce = rd.conditions[0]
        self.assertIsInstance(ce.slots[0].constraint, Literal)
        self.assertEqual(ce.slots[0].constraint.value, 'Bob')

    def test_symbol_literal(self):
        class R(Rule):
            Person(name=Symbol("Bob"))
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        ce = rd.conditions[0]
        self.assertIsInstance(ce.slots[0].constraint, Literal)
        self.assertIsInstance(ce.slots[0].constraint.value, Symbol)
        self.assertEqual(ce.slots[0].constraint.value, 'Bob')

    def test_test_ce(self):
        class R(Rule):
            Person(name=name, age=age)
            age >= 18
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.conditions), 2)
        test_ce = rd.conditions[1]
        self.assertIsInstance(test_ce, TestCE)
        self.assertIn('>=', test_ce.clips_expr)

    def test_not_ce(self):
        class R(Rule):
            ~Person(name="Bob")
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.conditions), 1)
        ce = rd.conditions[0]
        self.assertIsInstance(ce, NotCE)
        self.assertIsInstance(ce.pattern, PatternCE)
        self.assertEqual(ce.pattern.template_name, Person.__clipspyx_dsl__.name)

    def test_or_ce(self):
        class R(Rule):
            Person(name="Alice") | Person(name="Bob")
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.conditions), 1)
        ce = rd.conditions[0]
        self.assertIsInstance(ce, OrCE)
        self.assertEqual(len(ce.alternatives), 2)

    def test_field_not(self):
        class R(Rule):
            Person(name=not "Bob")
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        ce = rd.conditions[0]
        constraint = ce.slots[0].constraint
        self.assertIsInstance(constraint, NotConstraint)
        self.assertIsInstance(constraint.inner, Literal)
        self.assertEqual(constraint.inner.value, 'Bob')

    def test_field_or(self):
        class R(Rule):
            Person(age=25 or 30 or 35)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        ce = rd.conditions[0]
        constraint = ce.slots[0].constraint
        self.assertIsInstance(constraint, OrConstraint)
        self.assertEqual(len(constraint.alternatives), 3)

    def test_salience(self):
        class R(Rule):
            __salience__ = 10
            Person(name=name)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertEqual(rd.salience, 10)

    def test_predicate_constraint(self):
        class R(Rule):
            Person(age=age and age > 5)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        ce = rd.conditions[0]
        constraint = ce.slots[0].constraint
        self.assertIsInstance(constraint, PredicateConstraint)
        self.assertEqual(constraint.var, 'age')
        self.assertIn('>', constraint.clips_expr)

    def test_none_literal(self):
        class R(Rule):
            Person(name=None)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        ce = rd.conditions[0]
        constraint = ce.slots[0].constraint
        self.assertIsInstance(constraint, Literal)
        self.assertIsNone(constraint.value)

    def test_nil_literal(self):
        class R(Rule):
            Person(name=NIL)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        ce = rd.conditions[0]
        constraint = ce.slots[0].constraint
        self.assertIsInstance(constraint, Literal)
        self.assertIsNone(constraint.value)

    def test_not_none(self):
        class R(Rule):
            Person(name=not None)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        ce = rd.conditions[0]
        constraint = ce.slots[0].constraint
        self.assertIsInstance(constraint, NotConstraint)
        self.assertIsInstance(constraint.inner, Literal)
        self.assertIsNone(constraint.inner.value)

    def test_none_not_in_bound_vars(self):
        class R(Rule):
            Person(name=None)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertNotIn('None', rd.bound_vars)
        self.assertNotIn('NIL', rd.bound_vars)

    def test_nil_not_in_bound_vars(self):
        class R(Rule):
            Person(name=NIL)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertNotIn('None', rd.bound_vars)
        self.assertNotIn('NIL', rd.bound_vars)

    def test_none_or_constraint(self):
        class R(Rule):
            Person(name=None or "x")
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        ce = rd.conditions[0]
        constraint = ce.slots[0].constraint
        self.assertIsInstance(constraint, OrConstraint)
        self.assertEqual(len(constraint.alternatives), 2)
        self.assertIsInstance(constraint.alternatives[0], Literal)
        self.assertIsNone(constraint.alternatives[0].value)
        self.assertIsInstance(constraint.alternatives[1], Literal)
        self.assertEqual(constraint.alternatives[1].value, 'x')

    def test_not_nil(self):
        class R(Rule):
            Person(name=not NIL)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        ce = rd.conditions[0]
        constraint = ce.slots[0].constraint
        self.assertIsInstance(constraint, NotConstraint)
        self.assertIsInstance(constraint.inner, Literal)
        self.assertIsNone(constraint.inner.value)

    def test_exists_ce(self):
        class R(Rule):
            exists(Person())
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.conditions), 1)
        ce = rd.conditions[0]
        self.assertIsInstance(ce, ExistsCE)

    def test_forall_ce(self):
        class R(Rule):
            forall(Person(name=name), Badge(owner=name))
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.conditions), 1)
        ce = rd.conditions[0]
        self.assertIsInstance(ce, ForallCE)
        self.assertIsInstance(ce.initial, PatternCE)
        self.assertEqual(len(ce.conditions), 1)

    def test_logical_ce(self):
        class R(Rule):
            logical(Person(name=name, age=age))
            age >= 18
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertIsInstance(rd.conditions[0], LogicalCE)
        self.assertIsInstance(rd.conditions[1], TestCE)

    def test_forall_vars_not_on_rhs(self):
        """Variables inside forall should not appear in bound_vars."""
        class R(Rule):
            forall(Person(name=name), Badge(owner=name))
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertEqual(rd.bound_vars, [])

    def test_exists_vars_not_on_rhs(self):
        """Variables inside exists should not appear in bound_vars."""
        class R(Rule):
            exists(Person(name=name))
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertEqual(rd.bound_vars, [])

    @unittest.skipIf(CLIPS_MAJOR < 7, "goal CE requires CLIPS 7.0+")
    def test_goal_ce(self):
        class R(Rule):
            goal(Person(name=name))
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.conditions), 1)
        ce = rd.conditions[0]
        self.assertIsInstance(ce, GoalCE)
        self.assertIsInstance(ce.pattern, PatternCE)
        self.assertEqual(ce.pattern.template_name, Person.__clipspyx_dsl__.name)

    @unittest.skipIf(CLIPS_MAJOR < 7, "explicit CE requires CLIPS 7.0+")
    def test_explicit_ce(self):
        class R(Rule):
            explicit(Person(name=name))
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.conditions), 1)
        ce = rd.conditions[0]
        self.assertIsInstance(ce, ExplicitCE)
        self.assertIsInstance(ce.pattern, PatternCE)
        self.assertEqual(ce.pattern.template_name, Person.__clipspyx_dsl__.name)


# =============================================================================
# Effect parsing tests
# =============================================================================

class TestEffectParsing(unittest.TestCase):
    def test_assert_effect_parsed(self):
        class R(Rule):
            asserts(Result(msg="hello"))

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.effects), 1)
        eff = rd.effects[0]
        self.assertIsInstance(eff, AssertEffect)
        self.assertEqual(eff.template_name, Result.__clipspyx_dsl__.name)
        self.assertEqual(len(eff.slots), 1)
        self.assertEqual(eff.slots[0].name, 'msg')

    def test_retract_effect_parsed(self):
        class R(Rule):
            p = Person(name=name)
            retracts(p)

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.effects), 1)
        eff = rd.effects[0]
        self.assertIsInstance(eff, RetractEffect)
        self.assertEqual(eff.var_name, 'p')

    def test_modify_effect_parsed(self):
        class R(Rule):
            p = Counter(value=v)
            modifies(p, value=99)

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.effects), 1)
        eff = rd.effects[0]
        self.assertIsInstance(eff, ModifyEffect)
        self.assertEqual(eff.var_name, 'p')
        self.assertEqual(len(eff.slots), 1)
        self.assertEqual(eff.slots[0].name, 'value')

    def test_action_func_name_none_with_effects(self):
        class R(Rule):
            asserts(Result(msg="x"))

        rd = R.__clipspyx_dsl__
        self.assertIsNone(rd.action_func_name)

    def test_action_func_name_set_without_effects(self):
        class R(Rule):
            Person(name=name)
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        self.assertIsNotNone(rd.action_func_name)

    def test_effects_and_action_mutual_exclusivity(self):
        with self.assertRaises(TypeError):
            class R(Rule):
                Person(name=name)
                asserts(Result(msg="x"))
                def __action__(self):
                    pass

    def test_multiple_effects_parsed(self):
        class R(Rule):
            p = Person(name=name)
            retracts(p)
            asserts(Result(msg=name))

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.effects), 2)
        self.assertIsInstance(rd.effects[0], RetractEffect)
        self.assertIsInstance(rd.effects[1], AssertEffect)

    def test_assert_effect_with_arithmetic(self):
        class R(Rule):
            Counter(value=v)
            asserts(Counter(value=v + 1))

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.effects), 1)
        eff = rd.effects[0]
        self.assertIsInstance(eff, AssertEffect)
        self.assertIn('+', eff.slots[0].clips_expr)

    def test_assert_effect_with_bound_var(self):
        class R(Rule):
            Person(name=name)
            asserts(Result(msg=name))

        rd = R.__clipspyx_dsl__
        eff = rd.effects[0]
        self.assertEqual(eff.slots[0].clips_expr, '?name')

    def test_assert_effect_no_slots(self):
        class R(Rule):
            asserts(Person())

        rd = R.__clipspyx_dsl__
        eff = rd.effects[0]
        self.assertIsInstance(eff, AssertEffect)
        self.assertEqual(eff.slots, [])

    def test_conditions_still_parsed_with_effects(self):
        """CEs before effects are still parsed as conditions."""
        class R(Rule):
            p = Person(name=name)
            retracts(p)

        rd = R.__clipspyx_dsl__
        self.assertEqual(len(rd.conditions), 1)
        self.assertIsInstance(rd.conditions[0], AssignedPatternCE)
        self.assertEqual(len(rd.effects), 1)


# =============================================================================
# Codegen tests
# =============================================================================

class TestCodegen(unittest.TestCase):
    def test_deftemplate_basic(self):
        td = Person.__clipspyx_dsl__
        result = generate_deftemplate(td)
        self.assertIn(f'(deftemplate {td.name}', result)
        self.assertIn('(slot name (type STRING))', result)
        self.assertIn('(slot age (type INTEGER) (default 0))', result)

    def test_deftemplate_multislot(self):
        class WithMulti(Template):
            tags: Multi[str]

        result = generate_deftemplate(WithMulti.__clipspyx_dsl__)
        self.assertIn('(multislot tags (type STRING))', result)

    def test_defrule_basic(self):
        class R(Rule):
            p = Person(name=name, age=age)
            age >= 18
            def __action__(self):
                pass

        rd = R.__clipspyx_dsl__
        pname = Person.__clipspyx_dsl__.name
        result = generate_defrule(rd)
        self.assertIn(f'(defrule {rd.name}', result)
        self.assertIn(f'?p <- ({pname} (name ?name) (age ?age))', result)
        self.assertIn('(test (>= ?age 18))', result)
        self.assertIn('=>', result)

    def test_defrule_not_ce(self):
        class R(Rule):
            ~Person(name="Bob")
            def __action__(self):
                pass

        pname = Person.__clipspyx_dsl__.name
        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn(f'(not ({pname} (name "Bob")))', result)

    def test_defrule_or_ce(self):
        class R(Rule):
            Person(name="Alice") | Person(name="Bob")
            def __action__(self):
                pass

        pname = Person.__clipspyx_dsl__.name
        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn(f'(or ({pname} (name "Alice")) ({pname} (name "Bob")))', result)

    def test_defrule_field_not(self):
        class R(Rule):
            Person(name=not "Bob")
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(name ~"Bob")', result)

    def test_defrule_field_or(self):
        class R(Rule):
            Person(age=25 or 30 or 35)
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(age 25|30|35)', result)

    def test_defrule_salience(self):
        class R(Rule):
            __salience__ = 10
            Person(name=name)
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(declare (salience 10))', result)

    def test_defrule_predicate(self):
        class R(Rule):
            Person(age=age and age >= 18)
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('?age&:(>= ?age 18)', result)

    def test_defrule_none_literal(self):
        class R(Rule):
            Person(name=None)
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(name nil)', result)
        self.assertNotIn('?None', result)

    def test_defrule_symbol_literal(self):
        class R(Rule):
            Person(name=Symbol("Bob"))
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        # Symbol produces unquoted value, string would produce "Bob"
        self.assertIn('(name Bob)', result)
        self.assertNotIn('"Bob"', result)

    def test_defrule_nil_literal(self):
        class R(Rule):
            Person(name=NIL)
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(name nil)', result)

    def test_defrule_not_none(self):
        class R(Rule):
            Person(name=not None)
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(name ~nil)', result)

    def test_defrule_test_ce_eq_none(self):
        class R(Rule):
            Person(name=name)
            name == None
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('eq ?name nil', result)

    def test_defrule_test_ce_is_none(self):
        class R(Rule):
            Person(name=name)
            name is None
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('eq ?name nil', result)

    def test_defrule_test_ce_is_not_none(self):
        class R(Rule):
            Person(name=name)
            name is not None
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('neq ?name nil', result)

    def test_defrule_none_or_literal(self):
        class R(Rule):
            Person(name=None or "x")
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(name nil|"x")', result)

    def test_defrule_not_nil(self):
        class R(Rule):
            Person(name=not NIL)
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(name ~nil)', result)

    def test_defrule_predicate_neq_none(self):
        class R(Rule):
            Person(name=name and name != None)
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('neq ?name nil', result)

    def test_defrule_exists(self):
        class R(Rule):
            exists(Person())
            def __action__(self):
                pass

        pname = Person.__clipspyx_dsl__.name
        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn(f'(exists ({pname}))', result)

    def test_defrule_forall(self):
        class R(Rule):
            forall(Person(name=name), Badge(owner=name))
            def __action__(self):
                pass

        pname = Person.__clipspyx_dsl__.name
        bname = Badge.__clipspyx_dsl__.name
        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn(f'(forall ({pname} (name ?name)) ({bname} (owner ?name)))', result)

    def test_defrule_logical(self):
        class R(Rule):
            logical(Person(name=name))
            def __action__(self):
                pass

        pname = Person.__clipspyx_dsl__.name
        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn(f'(logical ({pname} (name ?name)))', result)

    @unittest.skipIf(CLIPS_MAJOR < 7, "goal CE requires CLIPS 7.0+")
    def test_defrule_goal(self):
        class R(Rule):
            goal(Person(name=name))
            def __action__(self):
                pass

        pname = Person.__clipspyx_dsl__.name
        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn(f'(goal ({pname} (name ?name)))', result)

    @unittest.skipIf(CLIPS_MAJOR < 7, "explicit CE requires CLIPS 7.0+")
    def test_defrule_explicit(self):
        class R(Rule):
            explicit(Person(name=name))
            def __action__(self):
                pass

        pname = Person.__clipspyx_dsl__.name
        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn(f'(explicit ({pname} (name ?name)))', result)

    def test_deftemplate_py_type_slot(self):
        td = Person.__clipspyx_dsl__
        result = generate_deftemplate(td)
        self.assertIn(f'(slot __py_type__ (type SYMBOL) (default {td.name}))', result)

    def test_deftemplate_fact_address_slot(self):
        td = Department.__clipspyx_dsl__
        result = generate_deftemplate(td)
        self.assertIn('(slot head (type FACT-ADDRESS))', result)
        self.assertIn(f'(slot __py_type__ (type SYMBOL) (default {td.name}))', result)

    def test_typecheck_rule_codegen(self):
        dname = Department.__clipspyx_dsl__.name
        pname = Person.__clipspyx_dsl__.name
        result = generate_typecheck_rule(dname, 'head', pname)
        self.assertIn(f'(defrule __py_typecheck_{dname}_head', result)
        self.assertIn('(declare (salience 10000))', result)
        self.assertIn(f'({dname} (head ?ref))', result)
        self.assertIn(f'(test (neq (fact-slot-value ?ref __py_type__) {pname}))', result)
        self.assertIn('__py_typecheck_error', result)


# =============================================================================
# Effect codegen tests
# =============================================================================

class TestEffectCodegen(unittest.TestCase):
    def test_defrule_assert_effect(self):
        class R(Rule):
            asserts(Result(msg="hello"))

        result = generate_defrule(R.__clipspyx_dsl__)
        rname = Result.__clipspyx_dsl__.name
        self.assertIn(f'(assert ({rname} (msg "hello")))', result)
        self.assertIn('=>', result)

    def test_defrule_retract_effect(self):
        class R(Rule):
            p = Person(name=name)
            retracts(p)

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(retract ?p)', result)

    def test_defrule_modify_effect(self):
        class R(Rule):
            p = Counter(value=v)
            modifies(p, value=99)

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(modify ?p (value 99))', result)

    def test_defrule_no_bridge_with_effects(self):
        class R(Rule):
            asserts(Result(msg="test"))

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertNotIn('__dsl_', result)

    def test_defrule_bridge_without_effects(self):
        class R(Rule):
            Person(name=name)
            def __action__(self):
                pass

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('__dsl_', result)

    def test_defrule_arithmetic_in_assert(self):
        class R(Rule):
            Counter(value=v)
            asserts(Counter(value=v + 1))

        cname = Counter.__clipspyx_dsl__.name
        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn(f'(assert ({cname} (value (+ ?v 1))))', result)

    def test_defrule_multiple_effects(self):
        class R(Rule):
            p = Person(name=name)
            retracts(p)
            asserts(Result(msg=name))

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(retract ?p)', result)
        rname = Result.__clipspyx_dsl__.name
        self.assertIn(f'(assert ({rname} (msg ?name)))', result)

    def test_defrule_assert_no_slots(self):
        class R(Rule):
            asserts(Person())

        pname = Person.__clipspyx_dsl__.name
        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn(f'(assert ({pname}))', result)

    def test_defrule_modify_multiple_slots(self):
        class R(Rule):
            p = Person(name=name, age=age)
            modifies(p, name="updated", age=99)

        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(modify ?p', result)
        self.assertIn('(name "updated")', result)
        self.assertIn('(age 99)', result)

    def test_defrule_string_literal_in_assert(self):
        class R(Rule):
            asserts(Person(name="Alice", age=30))

        pname = Person.__clipspyx_dsl__.name
        result = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn(f'(assert ({pname} (name "Alice") (age 30)))', result)


# =============================================================================
# End-to-end tests (require CLIPS environment)
# =============================================================================

class TestEndToEnd(unittest.TestCase):
    def test_template_and_rule_basic(self):
        """Define template + rule, assert fact via bound asserter, run, verify action fires."""
        results = []

        class GreetAdult(Rule):
            p = Person(name=name, age=age)
            age >= 18

            def __action__(self):
                results.append(f'Hello {self.name}, age {self.age}')

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(GreetAdult)
        env.reset()

        PersonAssert(name='Alice', age=25)
        PersonAssert(name='Bob', age=15)
        env.run()

        self.assertIn('Hello Alice, age 25', results)
        self.assertEqual(len(results), 1)

    def test_assert_returns_template_fact(self):
        """Asserting via bound asserter returns TemplateFact."""
        env = Environment()
        PersonAssert = env.define(Person)
        env.reset()

        fact = PersonAssert(name='Alice', age=25)
        self.assertIsInstance(fact, TemplateFact)

    def test_fact_attribute_access(self):
        """TemplateFact slots are accessible as attributes."""
        env = Environment()
        PersonAssert = env.define(Person)
        env.reset()

        fact = PersonAssert(name='Alice', age=25)
        self.assertEqual(fact.name, 'Alice')
        self.assertEqual(fact.age, 25)

    def test_fact_attribute_access_in_action(self):
        """Bound fact-address in action supports attribute access."""
        results = []

        class InspectPerson(Rule):
            p = Person(name=name, age=age)
            age >= 18

            def __action__(self):
                results.append((self.p.name, self.p.age))

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(InspectPerson)
        env.reset()

        PersonAssert(name='Alice', age=25)
        env.run()

        self.assertEqual(results, [('Alice', 25)])

    def test_assert_via_dunder_env_kwarg(self):
        """Asserting via __env__= kwarg still works as fallback."""
        env = Environment()
        env.define(Person)
        env.reset()

        fact = Person(__env__=env, name='Alice', age=25)
        self.assertIsInstance(fact, TemplateFact)

    def test_dunder_env_kwarg_with_rule(self):
        """__env__= kwarg works end-to-end with rules."""
        results = []

        class GreetAdult2(Rule):
            Person(name=name, age=age)
            age >= 18

            def __action__(self):
                results.append(self.name)

        env = Environment()
        env.define(Person)
        env.define(GreetAdult2)
        env.reset()

        Person(__env__=env, name='Alice', age=25)
        env.run()

        self.assertEqual(results, ['Alice'])

    def test_not_ce_fires_when_no_match(self):
        """Not CE: fires when no matching fact exists."""
        results = []

        class NoBob(Rule):
            ~Person(name='Bob')

            def __action__(self):
                results.append('no_bob')

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(NoBob)
        env.reset()

        PersonAssert(name='Alice', age=25)
        env.run()

        self.assertIn('no_bob', results)

    def test_not_ce_does_not_fire_when_match(self):
        """Not CE: does not fire when matching fact exists."""
        results = []

        class NoBob2(Rule):
            ~Person(name='Bob')

            def __action__(self):
                results.append('no_bob')

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(NoBob2)
        env.reset()

        PersonAssert(name='Bob', age=30)
        env.run()

        self.assertEqual(len(results), 0)

    def test_multi_pattern_variable_binding(self):
        """Variables bind across multiple patterns."""
        results = []

        class PersonWithBadge(Rule):
            Person(name=name)
            Badge(owner=name, level=level)

            def __action__(self):
                results.append(f'{self.name}:lvl{self.level}')

        env = Environment()
        PersonAssert = env.define(Person)
        BadgeAssert = env.define(Badge)
        env.define(PersonWithBadge)
        env.reset()

        PersonAssert(name='Alice')
        PersonAssert(name='Bob')
        BadgeAssert(owner='Alice', level=5)
        env.run()

        self.assertEqual(results, ['Alice:lvl5'])

    def test_salience_ordering(self):
        """Higher salience fires first."""
        results = []

        class LowP(Rule):
            __salience__ = 1
            Person(name=name)

            def __action__(self):
                results.append(f'low:{self.name}')

        class HighP(Rule):
            __salience__ = 10
            Person(name=name)

            def __action__(self):
                results.append(f'high:{self.name}')

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(LowP)
        env.define(HighP)
        env.reset()

        PersonAssert(name='Alice')
        env.run()

        self.assertEqual(results[0], 'high:Alice')
        self.assertEqual(results[1], 'low:Alice')

    def test_predicate_constraint(self):
        """Predicate constraint filters correctly."""
        results = []

        class AdultNotAdmin(Rule):
            Person(name=name and name != "Admin", age=age and age >= 18)

            def __action__(self):
                results.append(self.name)

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(AdultNotAdmin)
        env.reset()

        PersonAssert(name='Alice', age=25)
        PersonAssert(name='Admin', age=30)
        PersonAssert(name='Bob', age=10)
        env.run()

        self.assertEqual(results, ['Alice'])

    def test_exists_ce(self):
        """Exists CE fires once when at least one match exists."""
        results = []

        class HasAnyPerson(Rule):
            exists(Person())

            def __action__(self):
                results.append('exists')

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(HasAnyPerson)
        env.reset()

        PersonAssert(name='Alice')
        PersonAssert(name='Bob')
        env.run()

        self.assertEqual(results, ['exists'])

    def test_forall_ce(self):
        """Forall CE fires when all persons have badges."""
        results = []

        class AllHaveBadges(Rule):
            forall(Person(name=name), Badge(owner=name))

            def __action__(self):
                results.append('all_have_badges')

        env = Environment()
        PersonAssert = env.define(Person)
        BadgeAssert = env.define(Badge)
        env.define(AllHaveBadges)
        env.reset()

        PersonAssert(name='Alice')
        PersonAssert(name='Bob')
        BadgeAssert(owner='Alice', level=1)
        BadgeAssert(owner='Bob', level=2)
        env.run()

        self.assertIn('all_have_badges', results)

    def test_or_ce(self):
        """Or CE matches either pattern."""
        results = []

        class AliceOrCat(Rule):
            Person(name='Alice') | Animal(species='cat')

            def __action__(self):
                results.append('matched_or')

        env = Environment()
        env.define(Person)
        AnimalAssert = env.define(Animal)
        env.define(AliceOrCat)
        env.reset()

        AnimalAssert(species='cat')
        env.run()

        self.assertIn('matched_or', results)

    def test_field_or_constraint(self):
        """Field-level or matches one of the values."""
        results = []

        class SpecificAges(Rule):
            Person(name=name, age=25 or 30 or 35)

            def __action__(self):
                results.append(self.name)

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(SpecificAges)
        env.reset()

        PersonAssert(name='Alice', age=25)
        PersonAssert(name='Bob', age=28)
        PersonAssert(name='Charlie', age=30)
        env.run()

        self.assertIn('Alice', results)
        self.assertIn('Charlie', results)
        self.assertNotIn('Bob', results)

    def test_field_not_constraint(self):
        """Field-level not excludes the value."""
        results = []

        class NotBobField(Rule):
            Person(name=not "Bob")

            def __action__(self):
                results.append('matched')

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(NotBobField)
        env.reset()

        PersonAssert(name='Alice')
        PersonAssert(name='Bob')
        PersonAssert(name='Charlie')
        env.run()

        self.assertEqual(len(results), 2)

    def test_logical_ce(self):
        """Logical CE with test: variables from logical are RHS-visible."""
        results = []

        class LogicalRule(Rule):
            logical(Person(name=name, age=age))
            age >= 18

            def __action__(self):
                results.append(self.name)

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(LogicalRule)
        env.reset()

        PersonAssert(name='Alice', age=25)
        PersonAssert(name='Bob', age=15)
        env.run()

        self.assertEqual(results, ['Alice'])

    def test_nil_slot_matching(self):
        """Rule with None constraint fires for fact with nil-valued SYMBOL slot."""
        results = []

        class Tag(Template):
            label: Symbol

        class MatchNilLabel(Rule):
            Tag(label=None)

            def __action__(self):
                results.append('nil_matched')

        env = Environment()
        TagAssert = env.define(Tag)
        env.define(MatchNilLabel)
        env.reset()

        TagAssert()  # label defaults to nil (SYMBOL slot)
        TagAssert(label=Symbol('hello'))
        env.run()

        self.assertIn('nil_matched', results)
        self.assertEqual(len(results), 1)

    def test_symbol_literal_matching(self):
        """Rule with Symbol constraint fires only for matching symbol value."""
        results = []

        class Tag(Template):
            label: Symbol

        class MatchHello(Rule):
            Tag(label=Symbol("hello"))

            def __action__(self):
                results.append('matched')

        env = Environment()
        TagAssert = env.define(Tag)
        env.define(MatchHello)
        env.reset()

        TagAssert(label=Symbol('hello'))
        TagAssert(label=Symbol('world'))
        env.run()

        self.assertEqual(results, ['matched'])

    def test_is_not_none_constraint(self):
        """Rule with `name is not None` test CE fires for non-nil facts only."""
        results = []

        class Tag(Template):
            label: Symbol

        class MatchNotNilLabel(Rule):
            Tag(label=label)
            label is not None

            def __action__(self):
                results.append(str(self.label))

        env = Environment()
        TagAssert = env.define(Tag)
        env.define(MatchNotNilLabel)
        env.reset()

        TagAssert()  # nil label - should not fire
        TagAssert(label=Symbol('hello'))
        env.run()

        self.assertEqual(results, ['hello'])

    def test_action_receives_env(self):
        """__action__ can access the environment via self.__env__."""
        captured = []

        class CaptureEnv(Rule):
            Person(name=name)

            def __action__(self):
                captured.append(self.__env__)

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(CaptureEnv)
        env.reset()

        PersonAssert(name='Alice')
        env.run()

        self.assertEqual(len(captured), 1)
        self.assertIs(captured[0], env)

    def test_define_returns_bound_asserter(self):
        """env.define() returns a callable bound asserter for templates."""
        env = Environment()
        result = env.define(Person)
        self.assertTrue(callable(result))

    def test_define_returns_none_for_rules(self):
        """env.define() returns None for rules."""
        class SimpleRule(Rule):
            Person(name=name)
            def __action__(self):
                pass

        env = Environment()
        env.define(Person)
        result = env.define(SimpleRule)
        self.assertIsNone(result)

    @unittest.skipIf(CLIPS_MAJOR >= 7, "error only raised on CLIPS 6.4x")
    def test_goal_requires_clips7(self):
        """goal() raises TypeError on CLIPS 6.4x."""
        class GoalRule(Rule):
            goal(Person(name=name))
            def __action__(self):
                pass

        env = Environment()
        env.define(Person)
        with self.assertRaises(TypeError) as ctx:
            env.define(GoalRule)
        self.assertIn('CLIPS 7.0', str(ctx.exception))

    def test_fact_address_correct_type(self):
        """Dept with Person head: env.run() succeeds, no error."""
        env = Environment()
        PersonAssert = env.define(Person)
        DeptAssert = env.define(Department)
        env.reset()

        p = PersonAssert(name='Alice', age=30)
        DeptAssert(name='Engineering', head=p)
        env.run()

    def test_fact_address_wrong_type(self):
        """Dept with Animal head: env.run() raises TypeError."""
        env = Environment()
        env.define(Person)
        AnimalAssert = env.define(Animal)
        DeptAssert = env.define(Department)
        env.reset()

        a = AnimalAssert(species='cat')
        DeptAssert(name='Engineering', head=a)

        with self.assertRaises(TypeError) as ctx:
            env.run()

        self.assertIn('Department.head', str(ctx.exception))
        self.assertIn('Person', str(ctx.exception))

    @unittest.skipIf(CLIPS_MAJOR >= 7, "error only raised on CLIPS 6.4x")
    def test_explicit_requires_clips7(self):
        """explicit() raises TypeError on CLIPS 6.4x."""
        class ExplicitRule(Rule):
            explicit(Person(name=name))
            def __action__(self):
                pass

        env = Environment()
        env.define(Person)
        with self.assertRaises(TypeError) as ctx:
            env.define(ExplicitRule)
        self.assertIn('CLIPS 7.0', str(ctx.exception))


# =============================================================================
# Negative tests: rules must NOT fire when conditions are unmet
# =============================================================================

class TestNegative(unittest.TestCase):
    def test_test_ce_rejects_non_matching(self):
        """Test CE: age < 18 must not fire."""
        results = []

        class OnlyAdults(Rule):
            Person(name=name, age=age)
            age >= 18

            def __action__(self):
                results.append(self.name)

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(OnlyAdults)
        env.reset()

        PersonAssert(name='Child', age=10)
        PersonAssert(name='Teen', age=17)
        env.run()

        self.assertEqual(results, [])

    def test_literal_slot_rejects_mismatch(self):
        """Literal slot constraint rejects non-matching values."""
        results = []

        class OnlyBob(Rule):
            Person(name="Bob")

            def __action__(self):
                results.append('fired')

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(OnlyBob)
        env.reset()

        PersonAssert(name='Alice')
        PersonAssert(name='Charlie')
        env.run()

        self.assertEqual(results, [])

    def test_field_not_rejects_negated_value(self):
        """Field-level ~"Bob" must not match Bob."""
        results = []

        class NotBobOnly(Rule):
            Person(name=not "Bob")

            def __action__(self):
                results.append('fired')

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(NotBobOnly)
        env.reset()

        PersonAssert(name='Bob')
        env.run()

        self.assertEqual(results, [])

    def test_field_or_rejects_unlisted_value(self):
        """Field-level 25|30 must not match 28."""
        results = []

        class AgeFilter(Rule):
            Person(name=name, age=25 or 30)

            def __action__(self):
                results.append(self.name)

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(AgeFilter)
        env.reset()

        PersonAssert(name='Alice', age=28)
        PersonAssert(name='Bob', age=31)
        env.run()

        self.assertEqual(results, [])

    def test_predicate_rejects_failing_condition(self):
        """Predicate age >= 18 must not match age 10."""
        results = []

        class Adults(Rule):
            Person(age=age and age >= 18)

            def __action__(self):
                results.append('fired')

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(Adults)
        env.reset()

        PersonAssert(name='Child', age=10)
        env.run()

        self.assertEqual(results, [])

    def test_predicate_name_neq_rejects(self):
        """Predicate name != "Admin" must not match Admin."""
        results = []

        class NoAdmin(Rule):
            Person(name=name and name != "Admin")

            def __action__(self):
                results.append(self.name)

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(NoAdmin)
        env.reset()

        PersonAssert(name='Admin')
        env.run()

        self.assertEqual(results, [])

    def test_not_ce_suppressed_when_fact_exists(self):
        """~Person(name="Bob") must not fire when Bob is present."""
        results = []

        class NoBob(Rule):
            ~Person(name='Bob')

            def __action__(self):
                results.append('fired')

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(NoBob)
        env.reset()

        PersonAssert(name='Bob')
        env.run()

        self.assertEqual(results, [])

    def test_or_ce_rejects_when_neither_matches(self):
        """Or CE: neither alternative present means no firing."""
        results = []

        class AliceOrBobOnly(Rule):
            Person(name="Alice") | Person(name="Bob")

            def __action__(self):
                results.append('fired')

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(AliceOrBobOnly)
        env.reset()

        PersonAssert(name='Charlie')
        PersonAssert(name='Dave')
        env.run()

        self.assertEqual(results, [])

    def test_multi_pattern_rejects_unjoined(self):
        """Two patterns sharing a variable: no match when join fails."""
        results = []

        class PersonBadge(Rule):
            Person(name=name)
            Badge(owner=name)

            def __action__(self):
                results.append(self.name)

        env = Environment()
        PersonAssert = env.define(Person)
        BadgeAssert = env.define(Badge)
        env.define(PersonBadge)
        env.reset()

        PersonAssert(name='Alice')
        BadgeAssert(owner='Bob')  # owner doesn't match any Person.name
        env.run()

        self.assertEqual(results, [])

    def test_forall_rejects_when_condition_missing(self):
        """Forall: must not fire when one person lacks a badge."""
        results = []

        class AllBadged(Rule):
            forall(Person(name=name), Badge(owner=name))

            def __action__(self):
                results.append('fired')

        env = Environment()
        PersonAssert = env.define(Person)
        BadgeAssert = env.define(Badge)
        env.define(AllBadged)
        env.reset()

        PersonAssert(name='Alice')
        PersonAssert(name='Bob')
        BadgeAssert(owner='Alice')
        # Bob has no badge
        env.run()

        self.assertEqual(results, [])

    def test_exists_does_not_fire_with_no_facts(self):
        """Exists: must not fire when no matching fact exists."""
        results = []

        class AnyPerson(Rule):
            exists(Person())

            def __action__(self):
                results.append('fired')

        env = Environment()
        env.define(Person)
        env.define(AnyPerson)
        env.reset()
        # no Person facts asserted
        env.run()

        self.assertEqual(results, [])

    def test_logical_rejects_failing_test(self):
        """Logical + test: must not fire when test fails."""
        results = []

        class LogAdult(Rule):
            logical(Person(name=name, age=age))
            age >= 18

            def __action__(self):
                results.append(self.name)

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(LogAdult)
        env.reset()

        PersonAssert(name='Kid', age=5)
        env.run()

        self.assertEqual(results, [])

    def test_no_facts_no_firing(self):
        """Rule with a pattern must not fire if no facts are asserted."""
        results = []

        class NeedsPerson(Rule):
            Person(name=name)

            def __action__(self):
                results.append('fired')

        env = Environment()
        env.define(Person)
        env.define(NeedsPerson)
        env.reset()
        env.run()

        self.assertEqual(results, [])

    def test_combined_predicate_rejects_partial(self):
        """Both predicates in a single pattern must hold."""
        results = []

        class AdultNonAdmin(Rule):
            Person(name=name and name != "Admin", age=age and age >= 18)

            def __action__(self):
                results.append(self.name)

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(AdultNonAdmin)
        env.reset()

        PersonAssert(name='Admin', age=30)  # name fails
        PersonAssert(name='Kid', age=10)     # age fails
        env.run()

        self.assertEqual(results, [])


# =============================================================================
# Effect end-to-end tests
# =============================================================================

class TestEffectEndToEnd(unittest.TestCase):
    def test_assert_effect_creates_fact(self):
        """Assert effect fires and creates a new fact."""
        class Trigger(Template):
            go: int

        class MakeResult(Rule):
            Trigger(go=1)
            asserts(Result(msg="done"))

        env = Environment()
        TriggerAssert = env.define(Trigger)
        env.define(Result)
        env.define(MakeResult)
        env.reset()

        TriggerAssert(go=1)
        env.run()

        tpl = env.find_template(Result.__clipspyx_dsl__.name)
        facts = list(tpl.facts())
        self.assertGreaterEqual(len(facts), 1)
        self.assertEqual(facts[0]['msg'], 'done')

    def test_retract_effect_removes_fact(self):
        """Retract effect fires and removes the matched fact."""
        class RemovePerson(Rule):
            p = Person(name=name)
            retracts(p)

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(RemovePerson)
        env.reset()

        PersonAssert(name='temp')
        tpl = env.find_template(Person.__clipspyx_dsl__.name)
        self.assertGreaterEqual(len(list(tpl.facts())), 1)

        env.run()
        self.assertEqual(len(list(tpl.facts())), 0)

    def test_modify_effect_changes_slot(self):
        """Modify effect fires and changes a slot value."""
        class SetCounter(Rule):
            p = Counter(value=v)
            modifies(p, value=99)

        env = Environment()
        CounterAssert = env.define(Counter)
        env.define(SetCounter)
        env.reset()

        CounterAssert(value=0)
        env.run()

        tpl = env.find_template(Counter.__clipspyx_dsl__.name)
        facts = list(tpl.facts())
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0]['value'], 99)

    def test_bound_vars_in_assert_effect(self):
        """Variables bound on LHS are used in assert effect slot values."""
        class Input(Template):
            x: int
            y: int

        class Total(Template):
            sum: int

        class ComputeTotal(Rule):
            Input(x=x, y=y)
            asserts(Total(sum=x + y))

        env = Environment()
        InputAssert = env.define(Input)
        env.define(Total)
        env.define(ComputeTotal)
        env.reset()

        InputAssert(x=3, y=7)
        env.run()

        tpl = env.find_template(Total.__clipspyx_dsl__.name)
        facts = list(tpl.facts())
        self.assertGreaterEqual(len(facts), 1)
        self.assertEqual(facts[0]['sum'], 10)

    def test_multiple_effects_retract_and_assert(self):
        """Rule with retract + assert: removes source, creates result."""
        class ProcessPerson(Rule):
            p = Person(name=name)
            retracts(p)
            asserts(Result(msg=name))

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(Result)
        env.define(ProcessPerson)
        env.reset()

        PersonAssert(name='Alice')
        env.run()

        ptpl = env.find_template(Person.__clipspyx_dsl__.name)
        self.assertEqual(len(list(ptpl.facts())), 0)

        rtpl = env.find_template(Result.__clipspyx_dsl__.name)
        facts = list(rtpl.facts())
        self.assertGreaterEqual(len(facts), 1)
        self.assertEqual(facts[0]['msg'], 'Alice')

    def test_retracts_non_pattern_var_raises(self):
        """retracts() with a non-pattern variable raises TypeError at define time."""
        class BadRetract(Rule):
            Person(name=name)
            retracts(name)

        env = Environment()
        env.define(Person)
        with self.assertRaises(TypeError):
            env.define(BadRetract)

    def test_modifies_non_pattern_var_raises(self):
        """modifies() with a non-pattern variable raises TypeError at define time."""
        class BadModify(Rule):
            Counter(value=v)
            modifies(v, value=1)

        env = Environment()
        env.define(Counter)
        with self.assertRaises(TypeError):
            env.define(BadModify)

    def test_effects_only_rule_no_action(self):
        """Effects-only rule works without __action__."""
        class NoAction(Rule):
            Person(name=name)
            asserts(Result(msg=name))

        env = Environment()
        PersonAssert = env.define(Person)
        env.define(Result)
        env.define(NoAction)
        env.reset()

        PersonAssert(name='test')
        env.run()

        tpl = env.find_template(Result.__clipspyx_dsl__.name)
        facts = list(tpl.facts())
        self.assertGreaterEqual(len(facts), 1)

    def test_assert_effect_with_string_literal(self):
        """Assert effect with string literal creates correct fact."""
        class MakeGreeting(Rule):
            asserts(Result(msg="hello world"))

        env = Environment()
        env.define(Result)
        env.define(MakeGreeting)
        env.reset()
        env.run()

        tpl = env.find_template(Result.__clipspyx_dsl__.name)
        facts = list(tpl.facts())
        self.assertGreaterEqual(len(facts), 1)
        self.assertEqual(facts[0]['msg'], 'hello world')


if __name__ == '__main__':
    unittest.main()
