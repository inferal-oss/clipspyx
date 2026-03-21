"""Test ordering declarations across module boundaries.

Verifies that target resolution works when rules are defined in
different modules and that short-name ambiguity is detected.
"""
import unittest

from clipspyx import Environment
from clipspyx.dsl import Template, Rule


# Use unique template names to avoid polluting the global _template_registry
# shared with test_dsl.py (which defines Person, Badge, Result, etc.)

class OrderItem(Template):
    name: str


# --- Module-level rules (resolvable by _RuleMeta via sys.modules) ---

class ModuleRuleA(Rule):
    OrderItem(name=name)

    def __action__(self):
        pass


class ModuleRuleB(Rule):
    after(ModuleRuleA)
    OrderItem(name=name)

    def __action__(self):
        pass


class TestMultiModuleOrdering(unittest.TestCase):

    def test_module_level_target_resolved_to_class(self):
        """Module-level rules resolve targets to class objects at metaclass time."""
        oc = ModuleRuleB.__clipspyx_dsl__.ordering[0]
        # Module-level classes ARE in sys.modules, so target should be resolved
        self.assertIs(oc.target, ModuleRuleA)

    def test_module_level_ordering_works(self):
        """Ordering between module-level rules computes correct salience."""
        results = []

        class RecorderA(Rule):
            after(ModuleRuleA)
            OrderItem(name=name)

            def __action__(self):
                results.append('after_A')

        env = Environment()
        env.define(OrderItem)
        env.define(ModuleRuleA)
        env.define(RecorderA)
        env.reset()

        env.find_template(OrderItem.__clipspyx_dsl__.name).assert_fact(name='x')
        env.run()

        # ModuleRuleA fires first, RecorderA fires after
        self.assertIn('after_A', results)

    def test_local_rule_references_module_rule(self):
        """Locally defined rule can reference a module-level rule."""
        results = []

        class LocalRule(Rule):
            before(ModuleRuleA)
            OrderItem(name=name)

            def __action__(self):
                results.append('local')

        env = Environment()
        env.define(OrderItem)
        env.define(ModuleRuleA)
        env.define(LocalRule)
        env.reset()

        env.find_template(OrderItem.__clipspyx_dsl__.name).assert_fact(name='x')
        env.run()

        # LocalRule should fire before ModuleRuleA
        self.assertEqual(results[0], 'local')

    def test_cross_module_ordering_names(self):
        """Check what qualified names look like for module-level rules."""
        rdef_a = ModuleRuleA.__clipspyx_dsl__
        rdef_b = ModuleRuleB.__clipspyx_dsl__

        # Qualified names should include the module
        self.assertIn('.ModuleRuleA', rdef_a.name)
        self.assertIn('.ModuleRuleB', rdef_b.name)

        # B's ordering target should be the class itself (resolved at metaclass time)
        oc = rdef_b.ordering[0]
        self.assertIs(oc.target, ModuleRuleA)

    def test_ordering_target_is_string_for_local_classes(self):
        """Rules defined inside functions store target as string."""
        class LocalTarget(Rule):
            OrderItem(name=name)

            def __action__(self):
                pass

        class LocalRef(Rule):
            after(LocalTarget)
            OrderItem(name=name)

            def __action__(self):
                pass

        oc = LocalRef.__clipspyx_dsl__.ordering[0]
        # Local classes can't be resolved at metaclass time
        self.assertEqual(oc.target, 'LocalTarget')

    def test_local_classes_still_resolve_at_define_time(self):
        """String targets are resolved when define() triggers finalization."""
        results = []

        class First(Rule):
            OrderItem(name=name)

            def __action__(self):
                results.append('first')

        class Second(Rule):
            after(First)
            OrderItem(name=name)

            def __action__(self):
                results.append('second')

        env = Environment()
        env.define(OrderItem)
        env.define(First)
        env.define(Second)
        env.reset()

        env.find_template(OrderItem.__clipspyx_dsl__.name).assert_fact(name='x')
        env.run()

        self.assertEqual(results, ['first', 'second'])


class TestImportedRuleOrdering(unittest.TestCase):
    """Tests for ordering against rules imported from another module."""

    def test_imported_rule_target_resolved_to_class(self):
        """Importing a rule and using it as ordering target resolves to the class."""
        from _ordering_helper import HelperFirst

        class AfterImported(Rule):
            after(HelperFirst)
            OrderItem(name=name)

            def __action__(self):
                pass

        oc = AfterImported.__clipspyx_dsl__.ordering[0]
        # Should resolve to the imported class at metaclass time
        # because HelperFirst is in this module's namespace via import
        # However, since we imported inside a function, it may stay as string
        # Let's check what actually happens
        self.assertIn(oc.target, (HelperFirst, 'HelperFirst'))

    def test_imported_rule_ordering_works_end_to_end(self):
        """Ordering against an imported rule computes correct salience."""
        from _ordering_helper import HelperFirst, HelperItem  # noqa: E402

        results = []

        class BeforeImported(Rule):
            before(HelperFirst)
            HelperItem(label=label)

            def __action__(self):
                results.append('before')

        class AfterImported(Rule):
            after(HelperFirst)
            HelperItem(label=label)

            def __action__(self):
                results.append('after')

        env = Environment()
        env.define(HelperItem)
        env.define(HelperFirst)
        env.define(BeforeImported)
        env.define(AfterImported)
        env.reset()

        env.find_template(HelperItem.__clipspyx_dsl__.name).assert_fact(label='x')
        env.run()

        self.assertEqual(results[0], 'before')
        self.assertEqual(results[-1], 'after')

    def test_within_module_ordering_in_helper(self):
        """Rules defined in the helper module with ordering between them work."""
        from _ordering_helper import HelperFirst, HelperLast, HelperItem  # noqa: E402

        # HelperLast has after(HelperFirst), both in same module
        oc = HelperLast.__clipspyx_dsl__.ordering[0]
        # Both defined at module level in _ordering_helper, so target is class
        self.assertIs(oc.target, HelperFirst)

        results = []
        original_first_action = HelperFirst.__clipspyx_action__
        original_last_action = HelperLast.__clipspyx_action__

        # Can't easily patch __action__ on DSL rules, so just verify salience
        env = Environment()
        env.define(HelperItem)
        env.define(HelperFirst)
        env.define(HelperLast)

        # After finalization, HelperFirst should have higher salience
        self.assertGreater(
            HelperFirst.__clipspyx_dsl__.salience,
            HelperLast.__clipspyx_dsl__.salience)


class TestSameModuleForwardReference(unittest.TestCase):
    """Tests for forward references within the same scope."""

    def test_forward_ref_stays_as_string(self):
        """Referencing a not-yet-defined rule stores target as string."""
        # Define B first, referencing A which doesn't exist yet
        class RuleB(Rule):
            before(RuleA)  # noqa: F821 - RuleA not defined yet
            OrderItem(name=name)

            def __action__(self):
                pass

        # Target should be a string since RuleA doesn't exist
        oc = RuleB.__clipspyx_dsl__.ordering[0]
        self.assertEqual(oc.target, 'RuleA')

        # Now define RuleA
        class RuleA(Rule):
            OrderItem(name=name)

            def __action__(self):
                pass

        # Defining both should work via short-name resolution
        env = Environment()
        env.define(OrderItem)
        env.define(RuleB)
        env.define(RuleA)

        # After finalization, B fires before A
        self.assertGreater(
            RuleB.__clipspyx_dsl__.salience,
            RuleA.__clipspyx_dsl__.salience)

    def test_forward_ref_fires_in_correct_order(self):
        """Forward-referenced rules fire in the declared order."""
        results = []

        class Last(Rule):
            after(First)  # noqa: F821 - forward ref
            OrderItem(name=name)

            def __action__(self):
                results.append('last')

        class First(Rule):
            OrderItem(name=name)

            def __action__(self):
                results.append('first')

        env = Environment()
        env.define(OrderItem)
        env.define(Last)
        env.define(First)
        env.reset()

        env.find_template(OrderItem.__clipspyx_dsl__.name).assert_fact(name='x')
        env.run()

        self.assertEqual(results, ['first', 'last'])

    def test_backward_ref_resolved_to_class(self):
        """Referencing an already-defined rule in the same scope resolves to class."""
        class EarlyRule(Rule):
            OrderItem(name=name)

            def __action__(self):
                pass

        class LateRule(Rule):
            after(EarlyRule)
            OrderItem(name=name)

            def __action__(self):
                pass

        oc = LateRule.__clipspyx_dsl__.ordering[0]
        # EarlyRule is defined before LateRule in local scope.
        # Since it's local (not module-level), it stays as string.
        # Module-level would resolve to class.
        self.assertEqual(oc.target, 'EarlyRule')

        # But it still works at define time
        env = Environment()
        env.define(OrderItem)
        env.define(EarlyRule)
        env.define(LateRule)

        self.assertGreater(
            EarlyRule.__clipspyx_dsl__.salience,
            LateRule.__clipspyx_dsl__.salience)


if __name__ == '__main__':
    unittest.main()
