import unittest

from clipspyx import Environment, TemplateFact
from clipspyx.dsl import Template, Rule, Multi, Fact
from clipspyx.values import Symbol
from clipspyx.tracing import RuleFiring


# --- Templates ---

class Input(Template):
    value: int

class Output(Template):
    value: int

class A(Template):
    value: int

class B(Template):
    value: int

class C(Template):
    value: int


# --- Rules (declarative effects) ---

class DoubleEffect(Rule):
    i = Input(value=v)
    asserts(Output(value=v))


class AtoB(Rule):
    a = A(value=v)
    asserts(B(value=v))


class BtoC(Rule):
    b = B(value=v)
    asserts(C(value=v))


# --- Rules (__action__) ---

class DoubleAction(Rule):
    i = Input(value=v)

    def __action__(self):
        Output(__env__=self.__env__, value=self.v * 2)


# =============================================================================
# Fact sentinel type
# =============================================================================

class TestFactType(unittest.TestCase):

    def test_fact_type_maps_to_fact_address(self):
        from clipspyx.dsl.types import clips_type_name, Fact as FactType
        self.assertEqual(clips_type_name(FactType), 'FACT-ADDRESS')

    def test_multi_fact_in_template(self):
        dsl_def = RuleFiring.__clipspyx_dsl__
        slots = {s.name: s for s in dsl_def.slots}
        self.assertTrue(slots['inputs'].multi)
        self.assertEqual(slots['inputs'].clips_type, 'FACT-ADDRESS')
        self.assertTrue(slots['outputs'].multi)
        self.assertEqual(slots['outputs'].clips_type, 'FACT-ADDRESS')


# =============================================================================
# Enable / disable tracing
# =============================================================================

class TestEnableDisable(unittest.TestCase):

    def test_enable_registers_rulefiring_template(self):
        env = Environment()
        env.enable_tracing()
        tpl = env.find_template("RuleFiring")
        self.assertIsNotNone(tpl)

    def test_disable_clears_state(self):
        env = Environment()
        env.enable_tracing()
        self.assertIsNotNone(env._tracing_state)
        env.disable_tracing()
        self.assertIsNone(env._tracing_state)

    def test_disable_without_enable(self):
        env = Environment()
        env.disable_tracing()  # should not raise


# =============================================================================
# Declarative effects tracing
# =============================================================================

class TestDeclarativeEffectsTracing(unittest.TestCase):

    def setUp(self):
        self.env = Environment()
        self.env.enable_tracing()
        self.InputAssert = self.env.define(Input)
        self.env.define(Output)
        self.env.define(DoubleEffect)
        self.env.reset()

    def test_rulefiring_asserted(self):
        self.InputAssert(value=5)
        self.env.run()
        firings = [f for f in self.env.facts()
                   if f.template.name == 'RuleFiring']
        self.assertEqual(len(firings), 1)

    def test_rulefiring_has_rule_name(self):
        self.InputAssert(value=5)
        self.env.run()
        firing = next(f for f in self.env.facts()
                      if f.template.name == 'RuleFiring')
        self.assertIn('DoubleEffect', str(firing['rule']))

    def test_rulefiring_has_inputs(self):
        f1 = self.InputAssert(value=5)
        self.env.run()
        firing = next(f for f in self.env.facts()
                      if f.template.name == 'RuleFiring')
        inputs = firing['inputs']
        self.assertEqual(len(inputs), 1)
        self.assertEqual(inputs[0].index, f1.index)

    def test_rulefiring_has_outputs(self):
        self.InputAssert(value=5)
        self.env.run()
        firing = next(f for f in self.env.facts()
                      if f.template.name == 'RuleFiring')
        outputs = firing['outputs']
        self.assertEqual(len(outputs), 1)
        output_fact = next(f for f in self.env.facts()
                           if f.template.name == 'test_tracing.Output')
        self.assertEqual(outputs[0].index, output_fact.index)


# =============================================================================
# __action__ rule tracing
# =============================================================================

class TestActionRuleTracing(unittest.TestCase):

    def setUp(self):
        self.env = Environment()
        self.env.enable_tracing()
        self.InputAssert = self.env.define(Input)
        self.env.define(Output)
        self.env.define(DoubleAction)
        self.env.reset()

    def test_rulefiring_asserted(self):
        self.InputAssert(value=5)
        self.env.run()
        firings = [f for f in self.env.facts()
                   if f.template.name == 'RuleFiring']
        self.assertEqual(len(firings), 1)

    def test_rulefiring_has_correct_rule(self):
        self.InputAssert(value=5)
        self.env.run()
        firing = next(f for f in self.env.facts()
                      if f.template.name == 'RuleFiring')
        self.assertIn('DoubleAction', str(firing['rule']))

    def test_output_captured(self):
        self.InputAssert(value=5)
        self.env.run()
        firing = next(f for f in self.env.facts()
                      if f.template.name == 'RuleFiring')
        self.assertEqual(len(firing['outputs']), 1)


# =============================================================================
# Chain tracing
# =============================================================================

class TestChainTracing(unittest.TestCase):

    def setUp(self):
        self.env = Environment()
        self.env.enable_tracing()
        self.AAssert = self.env.define(A)
        self.env.define(B)
        self.env.define(C)
        self.env.define(AtoB)
        self.env.define(BtoC)
        self.env.reset()

    def test_two_firings_recorded(self):
        self.AAssert(value=42)
        self.env.run()
        firings = [f for f in self.env.facts()
                   if f.template.name == 'RuleFiring']
        self.assertEqual(len(firings), 2)

    def test_chain_is_traceable(self):
        """The output of rule 1 should be the input of rule 2."""
        f1 = self.AAssert(value=42)
        self.env.run()
        firings = [f for f in self.env.facts()
                   if f.template.name == 'RuleFiring']
        # Sort by fact index to get firing order
        firings.sort(key=lambda f: f.index)
        first, second = firings[0], firings[1]
        # First rule's output should be second rule's input
        first_output = first['outputs'][0]
        second_input = second['inputs'][0]
        self.assertEqual(first_output.index, second_input.index)


# =============================================================================
# No tracing when disabled
# =============================================================================

class TestTracingDisabled(unittest.TestCase):

    def test_no_rulefiring_facts(self):
        env = Environment()
        InputAssert = env.define(Input)
        env.define(Output)
        env.define(DoubleEffect)
        env.reset()
        InputAssert(value=5)
        env.run()
        firings = [f for f in env.facts()
                   if f.template.name == 'RuleFiring']
        self.assertEqual(len(firings), 0)


# =============================================================================
# Multiple activations
# =============================================================================

class TestMultipleActivations(unittest.TestCase):

    def test_multiple_inputs_multiple_firings(self):
        env = Environment()
        env.enable_tracing()
        InputAssert = env.define(Input)
        env.define(Output)
        env.define(DoubleEffect)
        env.reset()
        InputAssert(value=1)
        InputAssert(value=2)
        InputAssert(value=3)
        env.run()
        firings = [f for f in env.facts()
                   if f.template.name == 'RuleFiring']
        self.assertEqual(len(firings), 3)


# =============================================================================
# RuleFiring as DSL pattern in user rules
# =============================================================================

class TestRuleFiringAsPattern(unittest.TestCase):

    def test_rulefiring_template_has_clips_name(self):
        self.assertEqual(RuleFiring.__clipspyx_dsl__.name, 'RuleFiring')

    def test_rulefiring_importable_from_tracing(self):
        from clipspyx.tracing import RuleFiring as RF
        self.assertIs(RF, RuleFiring)


# =============================================================================
# Or CE tracing
# =============================================================================

class PersonT(Template):
    name: str

class AnimalT(Template):
    species: str

class Greeting(Template):
    msg: str


class GreetEither(Rule):
    """Fires on Person or Animal via or CE."""
    PersonT(name=name) | AnimalT(species=name)
    asserts(Greeting(msg=name))


class TestOrCETracing(unittest.TestCase):

    def test_or_ce_records_firing(self):
        env = Environment()
        env.enable_tracing()
        PersonAssert = env.define(PersonT)
        env.define(AnimalT)
        env.define(Greeting)
        env.define(GreetEither)
        env.reset()
        PersonAssert(name="Alice")
        env.run()
        firings = [f for f in env.facts()
                   if f.template.name == 'RuleFiring']
        self.assertEqual(len(firings), 1)

    def test_or_ce_other_branch(self):
        env = Environment()
        env.enable_tracing()
        env.define(PersonT)
        AnimalAssert = env.define(AnimalT)
        env.define(Greeting)
        env.define(GreetEither)
        env.reset()
        AnimalAssert(species="cat")
        env.run()
        firings = [f for f in env.facts()
                   if f.template.name == 'RuleFiring']
        self.assertEqual(len(firings), 1)


# =============================================================================
# Scoped CEs (not, exists, forall) - no implicit bindings
# =============================================================================

class Marker(Template):
    tag: str


class NotRule(Rule):
    """Fires when no Marker with tag='stop' exists."""
    i = Input(value=v)
    ~Marker(tag="stop")
    asserts(Output(value=v))


class ExistsRule(Rule):
    """Fires once when at least one Input exists."""
    exists(Input())
    asserts(Marker(tag="seen"))


class TestScopedCETracing(unittest.TestCase):

    def test_not_ce_no_crash(self):
        """Not CE should not get implicit binding; tracing still works."""
        env = Environment()
        env.enable_tracing()
        InputAssert = env.define(Input)
        env.define(Output)
        env.define(Marker)
        env.define(NotRule)
        env.reset()
        InputAssert(value=1)
        env.run()
        firings = [f for f in env.facts()
                   if f.template.name == 'RuleFiring']
        self.assertEqual(len(firings), 1)
        # Input fact should be in inputs
        firing = firings[0]
        self.assertGreaterEqual(len(firing['inputs']), 1)

    def test_exists_ce_no_crash(self):
        """Exists CE should not get implicit binding; tracing still works."""
        env = Environment()
        env.enable_tracing()
        InputAssert = env.define(Input)
        env.define(Marker)
        env.define(ExistsRule)
        env.reset()
        InputAssert(value=1)
        env.run()
        firings = [f for f in env.facts()
                   if f.template.name == 'RuleFiring']
        self.assertEqual(len(firings), 1)


if __name__ == '__main__':
    unittest.main()
