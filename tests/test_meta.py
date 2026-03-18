import unittest

from clipspyx import Environment
from clipspyx.values import Symbol
from clipspyx.dsl import Template, Rule, Multi
from clipspyx.meta import MetaTemplate, MetaTemplateSlot


class TestConstructsExist(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def test_template_deftemplate_exists(self):
        tpl = self.env.find_template('__Template__')
        self.assertEqual(tpl.name, '__Template__')

    def test_template_slot_deftemplate_exists(self):
        tpl = self.env.find_template('__TemplateSlot__')
        self.assertEqual(tpl.name, '__TemplateSlot__')

    def test_sync_function_callable(self):
        self.env.reset()
        self.env.call('sync-meta-templates')


class TestSyncOnReset(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.env.build(
            '(deftemplate person (slot name (type STRING)) (slot age (type INTEGER)))')
        self.env.reset()
        self.env.run()

    def _meta_facts(self, template_name):
        return [
            f for f in self.env.facts()
            if f.template.name == template_name
        ]

    def test_person_template_described(self):
        names = [f['name'] for f in self._meta_facts('__Template__')]
        self.assertIn(Symbol('person'), names)

    def test_person_slots_described(self):
        slots = [
            (f['template'], f['name'])
            for f in self._meta_facts('__TemplateSlot__')
        ]
        person_slots = [s for t, s in slots if t == Symbol('person')]
        self.assertIn(Symbol('name'), person_slots)
        self.assertIn(Symbol('age'), person_slots)

    def test_slot_types(self):
        for f in self._meta_facts('__TemplateSlot__'):
            if f['template'] == Symbol('person') and f['name'] == Symbol('age'):
                self.assertIn(Symbol('INTEGER'), f['types'])
                return
        self.fail('age slot not found')

    def test_slot_single_flag(self):
        for f in self._meta_facts('__TemplateSlot__'):
            if f['template'] == Symbol('person') and f['name'] == Symbol('name'):
                self.assertEqual(f['single'], Symbol('TRUE'))
                return
        self.fail('name slot not found')


class TestSelfReferential(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.env.reset()
        self.env.run()

    def test_template_describes_itself(self):
        names = [
            f['name'] for f in self.env.facts()
            if f.template.name == '__Template__'
        ]
        self.assertIn(Symbol('__Template__'), names)

    def test_template_slot_describes_itself(self):
        names = [
            f['name'] for f in self.env.facts()
            if f.template.name == '__Template__'
        ]
        self.assertIn(Symbol('__TemplateSlot__'), names)


class TestImpliedTemplate(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.env.assert_string('(an-ordered-fact 1 2 3)')
        self.env.reset()
        self.env.run()

    def test_implied_template_has_flag(self):
        for f in self.env.facts():
            if (f.template.name == '__Template__'
                    and f['name'] == Symbol('an-ordered-fact')):
                self.assertEqual(f['implied'], Symbol('TRUE'))
                return
        self.fail('an-ordered-fact not found in meta-facts')

    def test_implied_template_empty_slots(self):
        for f in self.env.facts():
            if (f.template.name == '__Template__'
                    and f['name'] == Symbol('an-ordered-fact')):
                self.assertEqual(f['slots'], ())
                return
        self.fail('an-ordered-fact not found in meta-facts')


class TestManualSync(unittest.TestCase):
    def test_late_defined_template(self):
        env = Environment()
        env.reset()
        env.run()

        env.build('(deftemplate latecomer (slot data (type STRING)))')
        env.call('sync-meta-templates')

        names = [
            f['name'] for f in env.facts()
            if f.template.name == '__Template__'
        ]
        self.assertIn(Symbol('latecomer'), names)


class TestMultipleResets(unittest.TestCase):
    def test_meta_facts_correct_after_second_reset(self):
        env = Environment()
        env.build('(deftemplate alpha (slot x))')
        env.reset()
        env.run()

        env.build('(deftemplate beta (slot y))')
        env.reset()
        env.run()

        names = [
            f['name'] for f in env.facts()
            if f.template.name == '__Template__'
        ]
        self.assertIn(Symbol('alpha'), names)
        self.assertIn(Symbol('beta'), names)


# --- DSL-defined template tests ---

class Pet(Template):
    __clips_name__ = "pet"
    species: str
    name: str
    age: int = 0
    nicknames: Multi[str]


class Task(Template):
    owner: Pet


class TestDSLTemplateMeta(unittest.TestCase):
    """Meta-template facts for DSL-defined templates."""

    def setUp(self):
        self.env = Environment()
        self.env.define(Pet)
        self.env.define(Task)
        self.env.reset()
        self.env.run()

    def _template_fact(self, name):
        for f in self.env.facts():
            if f.template.name == '__Template__' and f['name'] == Symbol(name):
                return f
        return None

    def _slot_facts(self, template_name):
        return [
            f for f in self.env.facts()
            if f.template.name == '__TemplateSlot__'
            and f['template'] == Symbol(template_name)
        ]

    def test_dsl_template_found_by_clips_name(self):
        fact = self._template_fact('pet')
        self.assertIsNotNone(fact, 'pet template not in meta-facts')

    def test_dsl_template_uses_clips_name_not_python_name(self):
        fact = self._template_fact('Pet')
        self.assertIsNone(fact, 'should use __clips_name__, not class name')

    def test_dsl_template_without_clips_name_uses_qualified(self):
        qualified = f'{Task.__module__}.Task'
        fact = self._template_fact(qualified)
        self.assertIsNotNone(fact, f'{qualified} not in meta-facts')

    def test_dsl_slots_described(self):
        slot_names = [f['name'] for f in self._slot_facts('pet')]
        self.assertIn(Symbol('species'), slot_names)
        self.assertIn(Symbol('name'), slot_names)
        self.assertIn(Symbol('age'), slot_names)
        self.assertIn(Symbol('nicknames'), slot_names)

    def test_dsl_py_type_slot_included(self):
        slot_names = [f['name'] for f in self._slot_facts('pet')]
        self.assertIn(Symbol('__py_type__'), slot_names)

    def test_dsl_slot_type_string(self):
        for f in self._slot_facts('pet'):
            if f['name'] == Symbol('species'):
                self.assertIn(Symbol('STRING'), f['types'])
                return
        self.fail('species slot not found')

    def test_dsl_slot_type_integer(self):
        for f in self._slot_facts('pet'):
            if f['name'] == Symbol('age'):
                self.assertIn(Symbol('INTEGER'), f['types'])
                return
        self.fail('age slot not found')

    def test_dsl_multislot_single_flag(self):
        for f in self._slot_facts('pet'):
            if f['name'] == Symbol('nicknames'):
                self.assertEqual(f['single'], Symbol('FALSE'))
                return
        self.fail('nicknames slot not found')

    def test_dsl_single_slot_flag(self):
        for f in self._slot_facts('pet'):
            if f['name'] == Symbol('species'):
                self.assertEqual(f['single'], Symbol('TRUE'))
                return
        self.fail('species slot not found')

    def test_dsl_slot_has_default(self):
        for f in self._slot_facts('pet'):
            if f['name'] == Symbol('age'):
                self.assertEqual(f['has_default'], Symbol('STATIC'))
                return
        self.fail('age slot not found')

    def test_dsl_slot_implicit_default(self):
        # CLIPS auto-provides STATIC defaults for all slots
        # (empty string for STRING, 0 for INTEGER, etc.)
        for f in self._slot_facts('pet'):
            if f['name'] == Symbol('species'):
                self.assertEqual(f['has_default'], Symbol('STATIC'))
                return
        self.fail('species slot not found')

    def test_dsl_fact_address_slot_type(self):
        qualified = f'{Task.__module__}.Task'
        for f in self._slot_facts(qualified):
            if f['name'] == Symbol('owner'):
                self.assertIn(Symbol('FACT-ADDRESS'), f['types'])
                return
        self.fail('owner slot not found')


# --- DSL Rules that pattern-match on meta-template facts ---

# Collects names of all non-implied templates
_collected_templates = []


class CollectTemplateNames(Rule):
    __salience__ = -1  # fire after sync
    MetaTemplate(name=name, implied=Symbol("FALSE"))

    def __action__(self):
        _collected_templates.append(self.name)


# Collects (template, slot) pairs for INTEGER-typed slots
_integer_slots = []


class FindIntegerSlots(Rule):
    __salience__ = -1
    MetaTemplateSlot(template=template, name=name, types=types)

    def __action__(self):
        if Symbol('INTEGER') in self.types:
            _integer_slots.append((self.template, self.name))


# Counts slots per template via meta-facts
_slot_counts = {}


class CountSlotsPerTemplate(Rule):
    __salience__ = -1
    t = MetaTemplate(name=name, implied=Symbol("FALSE"))

    def __action__(self):
        count = 0
        for f in self.__env__.facts():
            if (f.template.name == '__TemplateSlot__'
                    and f['template'] == self.name):
                count += 1
        _slot_counts[str(self.name)] = count


class TestDSLRulesOnMetaFacts(unittest.TestCase):
    """DSL-defined rules that pattern-match on __Template__/__TemplateSlot__."""

    def setUp(self):
        _collected_templates.clear()
        _integer_slots.clear()
        _slot_counts.clear()

        self.env = Environment()
        self.env.build(
            '(deftemplate vehicle (slot make (type STRING)) (slot year (type INTEGER)))')
        self.env.define(Pet)
        self.env.define(CollectTemplateNames)
        self.env.define(FindIntegerSlots)
        self.env.define(CountSlotsPerTemplate)
        self.env.reset()
        self.env.run()

    def test_collect_rule_finds_user_templates(self):
        self.assertIn(Symbol('vehicle'), _collected_templates)
        self.assertIn(Symbol('pet'), _collected_templates)

    def test_collect_rule_finds_meta_templates(self):
        self.assertIn(Symbol('__Template__'), _collected_templates)
        self.assertIn(Symbol('__TemplateSlot__'), _collected_templates)

    def test_collect_rule_excludes_implied(self):
        # __meta-sync-trigger is implied, should not appear
        self.assertNotIn(Symbol('__meta-sync-trigger'), _collected_templates)

    def test_find_integer_slots(self):
        self.assertIn((Symbol('vehicle'), Symbol('year')), _integer_slots)
        self.assertIn((Symbol('pet'), Symbol('age')), _integer_slots)

    def test_find_integer_slots_excludes_string(self):
        string_pairs = [(t, s) for t, s in _integer_slots
                        if t == Symbol('vehicle') and s == Symbol('make')]
        self.assertEqual(string_pairs, [])

    def test_count_slots_vehicle(self):
        # vehicle has: make, year
        self.assertEqual(_slot_counts['vehicle'], 2)

    def test_count_slots_pet(self):
        # pet has: __py_type__, species, name, age, nicknames
        self.assertEqual(_slot_counts['pet'], 5)
