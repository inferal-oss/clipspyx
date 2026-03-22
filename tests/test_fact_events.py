"""Tests for fact lifecycle event meta-facts."""

import unittest

from clipspyx import Environment
from clipspyx.values import Symbol


class TestEnableDisable(unittest.TestCase):
    def test_enable(self):
        env = Environment()
        env.enable_fact_events()
        self.assertIsNotNone(env._fact_events_state)
        self.assertTrue(env._fact_events_state.enabled)

    def test_disable(self):
        env = Environment()
        env.enable_fact_events()
        env.disable_fact_events()
        self.assertIsNone(env._fact_events_state)

    def test_templates_registered(self):
        env = Environment()
        env.enable_fact_events()
        for name in ('FactAsserted', 'FactRetracted', 'FactModified'):
            tpl = env.find_template(name)
            self.assertEqual(tpl.name, name)


class TestFactAsserted(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.env.enable_fact_events()
        self.env.build('(deftemplate item (slot name) (slot qty))')
        self.env.reset()

    def test_assert_generates_event(self):
        self.env.assert_string('(item (name apple) (qty 5))')
        events = [f for f in self.env.facts()
                  if f.template.name == 'FactAsserted']
        self.assertEqual(len(events), 1)
        self.assertEqual(str(events[0]['template']), 'item')

    def test_event_fact_is_readable(self):
        self.env.assert_string('(item (name apple) (qty 5))')
        events = [f for f in self.env.facts()
                  if f.template.name == 'FactAsserted']
        ref = events[0]['fact']
        self.assertEqual(ref['name'], 'apple')
        self.assertEqual(ref['qty'], 5)

    def test_no_event_for_meta_facts(self):
        self.env.assert_string('(item (name a) (qty 1))')
        events = [f for f in self.env.facts()
                  if f.template.name == 'FactAsserted']
        templates = [str(e['template']) for e in events]
        self.assertNotIn('FactAsserted', templates)

    def test_multiple_asserts(self):
        self.env.assert_string('(item (name a) (qty 1))')
        self.env.assert_string('(item (name b) (qty 2))')
        events = [f for f in self.env.facts()
                  if f.template.name == 'FactAsserted']
        self.assertEqual(len(events), 2)


class TestFactRetracted(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.env.enable_fact_events()
        self.env.build('(deftemplate item (slot name) (slot qty))')
        self.env.reset()

    def test_retract_generates_event(self):
        f = self.env.assert_string('(item (name apple) (qty 5))')
        f.retract()
        events = [f for f in self.env.facts()
                  if f.template.name == 'FactRetracted']
        self.assertEqual(len(events), 1)
        self.assertEqual(str(events[0]['template']), 'item')

    def test_retracted_ppform_captures_values(self):
        f = self.env.assert_string('(item (name apple) (qty 5))')
        f.retract()
        events = [f for f in self.env.facts()
                  if f.template.name == 'FactRetracted']
        ppform = events[0]['ppform']
        self.assertIn('apple', ppform)
        self.assertIn('5', ppform)

    def test_retracted_index(self):
        f = self.env.assert_string('(item (name apple) (qty 5))')
        idx = f.index
        f.retract()
        events = [f for f in self.env.facts()
                  if f.template.name == 'FactRetracted']
        self.assertEqual(events[0]['index'], idx)


class TestFactModified(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.env.enable_fact_events()
        self.env.build('(deftemplate item (slot name) (slot qty))')
        self.env.reset()

    def test_modify_generates_event(self):
        f = self.env.assert_string('(item (name apple) (qty 5))')
        f.modify_slots(qty=10)
        self.env.run()  # flushes deferred modify events
        events = [e for e in self.env.facts()
                  if e.template.name == 'FactModified']
        self.assertEqual(len(events), 1)
        self.assertEqual(str(events[0]['template']), 'item')

    def test_modify_has_new_value(self):
        f = self.env.assert_string('(item (name apple) (qty 5))')
        f.modify_slots(qty=10)
        self.env.run()
        events = [e for e in self.env.facts()
                  if e.template.name == 'FactModified']
        self.assertEqual(events[0]['fact']['qty'], 10)

    def test_modify_captures_old_ppform(self):
        f = self.env.assert_string('(item (name apple) (qty 5))')
        f.modify_slots(qty=10)
        self.env.run()
        events = [e for e in self.env.facts()
                  if e.template.name == 'FactModified']
        ppform = events[0]['old_ppform']
        self.assertIn('apple', ppform)
        self.assertIn('5', ppform)


class TestRulesReactToEvents(unittest.TestCase):
    def test_rule_fires_on_assert_event(self):
        env = Environment()
        env.enable_fact_events()
        env.build('(deftemplate item (slot name))')
        env.build('(deftemplate log (slot msg))')
        env.build(
            '(defrule on-item-added'
            ' (FactAsserted (template item))'
            ' =>'
            ' (assert (log (msg "item added"))))')
        env.reset()
        env.assert_string('(item (name apple))')
        env.run()
        logs = [f for f in env.facts() if f.template.name == 'log']
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['msg'], 'item added')

    def test_rule_fires_on_retract_event(self):
        env = Environment()
        env.enable_fact_events()
        env.build('(deftemplate item (slot name))')
        env.build('(deftemplate log (slot msg))')
        env.build(
            '(defrule on-item-removed'
            ' (FactRetracted (template item))'
            ' =>'
            ' (assert (log (msg "item removed"))))')
        env.reset()
        f = env.assert_string('(item (name apple))')
        f.retract()
        env.run()
        logs = [f for f in env.facts() if f.template.name == 'log']
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['msg'], 'item removed')


class TestDSLRulesWithEvents(unittest.TestCase):
    """Use FactAsserted/FactRetracted/FactModified as DSL Template classes in rules."""

    def test_dsl_rule_reacts_to_assert(self):
        from clipspyx.dsl import Template, Rule
        from clipspyx.fact_events import FactAsserted

        class Item4(Template):
            __clips_name__ = "Item4"
            name: str

        class AssertLog4(Template):
            __clips_name__ = "AssertLog4"
            item_name: str

        class OnItemAsserted4(Rule):
            ev = FactAsserted(template=Symbol("Item4"), fact=f)
            asserts(AssertLog4(item_name="logged"))

        env = Environment()
        env.enable_fact_events()
        NewItem = env.define(Item4)
        env.define(AssertLog4)
        env.define(OnItemAsserted4)
        env.reset()
        NewItem(name='apple')
        env.run()
        logs = [f for f in env.facts()
                if f.template.name == 'AssertLog4']
        self.assertGreater(len(logs), 0)

    def test_dsl_rule_reads_asserted_fact_index(self):
        from clipspyx.dsl import Template, Rule
        from clipspyx.fact_events import FactAsserted

        class Sensor5(Template):
            __clips_name__ = "Sensor5"
            reading: int

        class IndexLog5(Template):
            __clips_name__ = "IndexLog5"
            idx: int

        class LogIndex5(Rule):
            ev = FactAsserted(template=Symbol("Sensor5"), index=idx)
            asserts(IndexLog5(idx=idx))

        env = Environment()
        env.enable_fact_events()
        NewSensor = env.define(Sensor5)
        env.define(IndexLog5)
        env.define(LogIndex5)
        env.reset()
        s = NewSensor(reading=42)
        env.run()
        logs = [f for f in env.facts()
                if f.template.name == 'IndexLog5']
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['idx'], s.index)

    def test_dsl_rule_reacts_to_retract(self):
        from clipspyx.dsl import Template, Rule
        from clipspyx.fact_events import FactRetracted

        class Item6(Template):
            __clips_name__ = "Item6"
            name: str

        class RetractLog6(Template):
            __clips_name__ = "RetractLog6"
            removed_index: int

        class OnItemRetracted6(Rule):
            ev = FactRetracted(template=Symbol("Item6"), index=idx)
            asserts(RetractLog6(removed_index=idx))

        env = Environment()
        env.enable_fact_events()
        NewItem = env.define(Item6)
        env.define(RetractLog6)
        env.define(OnItemRetracted6)
        env.reset()
        f = NewItem(name='banana')
        original_index = f.index
        f.retract()
        env.run()
        logs = [f for f in env.facts()
                if f.template.name == 'RetractLog6']
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['removed_index'], original_index)

    def test_dsl_rule_reacts_to_modify(self):
        from clipspyx.dsl import Template, Rule
        from clipspyx.fact_events import FactModified

        class Counter7(Template):
            __clips_name__ = "Counter7"
            value: int

        class ModifyLog7(Template):
            __clips_name__ = "ModifyLog7"
            new_value: int

        class OnCounterModified7(Rule):
            ev = FactModified(template=Symbol("Counter7"), fact=f)
            c = Counter7(value=v)
            asserts(ModifyLog7(new_value=v))

        env = Environment()
        env.enable_fact_events()
        NewCounter = env.define(Counter7)
        env.define(ModifyLog7)
        env.define(OnCounterModified7)
        env.reset()
        c = NewCounter(value=1)
        c.modify_slots(value=10)
        env.run()  # flushes deferred modify + fires rules
        logs = [f for f in env.facts()
                if f.template.name == 'ModifyLog7']
        self.assertGreater(len(logs), 0)
        self.assertEqual(logs[0]['new_value'], 10)

    def test_dsl_rule_accesses_asserted_fact_slots(self):
        """Rule reads slot values from the fact address in FactAsserted."""
        from clipspyx.dsl import Template, Rule
        from clipspyx.fact_events import FactAsserted

        class Measurement8(Template):
            __clips_name__ = "Measurement8"
            sensor: str
            value: int

        class Alert8(Template):
            __clips_name__ = "Alert8"
            sensor: str

        class HighValueAlert8(Rule):
            ev = FactAsserted(template=Symbol("Measurement8"), fact=m)
            m_fact = Measurement8(sensor=s, value=v)
            v >= 100
            asserts(Alert8(sensor=s))

        env = Environment()
        env.enable_fact_events()
        NewMeasurement = env.define(Measurement8)
        env.define(Alert8)
        env.define(HighValueAlert8)
        env.reset()
        NewMeasurement(sensor='temp', value=50)   # below threshold
        NewMeasurement(sensor='temp', value=150)  # above threshold
        env.run()
        alerts = [f for f in env.facts()
                  if f.template.name == 'Alert8']
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['sensor'], 'temp')


class TestCoexistenceWithTracing(unittest.TestCase):
    def test_both_enabled_no_conflict(self):
        """Enabling both tracing and fact events doesn't crash."""
        env = Environment()
        env.enable_tracing()
        env.enable_fact_events()
        env.build('(deftemplate item (slot name))')
        env.reset()
        env.assert_string('(item (name apple))')
        # Both should have registered their templates without conflict
        tpl_names = {t.name for t in env.templates()}
        self.assertIn('FactAsserted', tpl_names)
        self.assertIn('RuleFiring', tpl_names)
        # FactAsserted events should still work
        events = [f for f in env.facts() if f.template.name == 'FactAsserted']
        self.assertGreater(len(events), 0)


if __name__ == '__main__':
    unittest.main()
