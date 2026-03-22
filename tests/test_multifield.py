import unittest

from clipspyx import Environment
from clipspyx.dsl import Template, Rule, Multi
from clipspyx.dsl.ir import (
    MultifieldWildcard, MultifieldVar, Var, Wildcard, Literal,
)
from clipspyx.dsl.codegen import generate_defrule
from clipspyx.values import Symbol


# --- Templates ---

class MFPerson(Template):
    name: str
    hobbies: Multi[str]


class MFData(Template):
    items: Multi[str]


class MFOutput(Template):
    items: Multi[str]


class MFResult(Template):
    msg: str


# =============================================================================
# IR nodes
# =============================================================================

class TestMultifieldIR(unittest.TestCase):

    def test_multifield_wildcard_to_clips(self):
        self.assertEqual(MultifieldWildcard().to_clips(), '$?')

    def test_multifield_var_to_clips(self):
        self.assertEqual(MultifieldVar(name='h').to_clips(), '$?h')


# =============================================================================
# Codegen
# =============================================================================

class TestMultifieldCodegen(unittest.TestCase):

    def test_ellipsis_generates_multifield_wildcard(self):
        class R(Rule):
            MFPerson(name=name, hobbies=...)

            def __action__(self):
                pass
        clips = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(hobbies $?)', clips)

    def test_starred_var_generates_multifield_var(self):
        class R(Rule):
            MFPerson(name=name, hobbies=(*h,))

            def __action__(self):
                pass
        clips = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(hobbies $?h)', clips)

    def test_sequence_pattern_generates_correctly(self):
        class R(Rule):
            MFPerson(hobbies=(*before, "chess", *after))

            def __action__(self):
                pass
        clips = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(hobbies $?before "chess" $?after)', clips)

    def test_mixed_wildcards_generate_correctly(self):
        class R(Rule):
            MFData(items=(_, "chess", ...))

            def __action__(self):
                pass
        clips = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(items ? "chess" $?)', clips)

    def test_literal_plus_starred(self):
        class R(Rule):
            MFData(items=("first", *rest))

            def __action__(self):
                pass
        clips = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(items "first" $?rest)', clips)

    def test_extract_single_element(self):
        class R(Rule):
            MFData(items=(*before, x, *after))

            def __action__(self):
                pass
        clips = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('(items $?before ?x $?after)', clips)

    def test_multifield_vars_tracked_in_ruledef(self):
        class R(Rule):
            MFPerson(hobbies=(*h,))

            def __action__(self):
                pass
        self.assertIn('h', R.__clipspyx_dsl__.multifield_vars)

    def test_multifield_rule_uses_python_function(self):
        class R(Rule):
            MFPerson(hobbies=(*h,))

            def __action__(self):
                pass
        clips = generate_defrule(R.__clipspyx_dsl__)
        self.assertIn('python-function', clips)


# =============================================================================
# End-to-end: ellipsis wildcard
# =============================================================================

class TestEllipsisWildcard(unittest.TestCase):

    def test_matches_any_multislot(self):
        matched = []

        class MatchAny(Rule):
            MFPerson(name=name, hobbies=...)

            def __action__(self):
                matched.append(self.name)

        env = Environment()
        MFPersonAssert = env.define(MFPerson)
        env.define(MatchAny)
        env.reset()
        MFPersonAssert(name="Alice", hobbies=("chess", "reading"))
        env.run()
        self.assertEqual(matched, ["Alice"])

    def test_matches_empty_multislot(self):
        matched = []

        class MatchAny(Rule):
            MFPerson(name=name, hobbies=...)

            def __action__(self):
                matched.append(self.name)

        env = Environment()
        MFPersonAssert = env.define(MFPerson)
        env.define(MatchAny)
        env.reset()
        MFPersonAssert(name="Alice", hobbies=())
        env.run()
        self.assertEqual(matched, ["Alice"])


# =============================================================================
# End-to-end: starred binding
# =============================================================================

class TestStarredBinding(unittest.TestCase):

    def setUp(self):
        self.captured = []

        class ListHobbies(Rule):
            MFPerson(name=name, hobbies=(*h,))

            def __action__(self_r):
                self.captured.append((self_r.name, self_r.h))

        self.env = Environment()
        self.MFPersonAssert = self.env.define(MFPerson)
        self.env.define(ListHobbies)
        self.env.reset()

    def test_binds_entire_multislot(self):
        self.MFPersonAssert(name="Alice", hobbies=("chess", "reading"))
        self.env.run()
        self.assertEqual(len(self.captured), 1)
        name, hobbies = self.captured[0]
        self.assertEqual(name, "Alice")
        self.assertEqual(hobbies, ("chess", "reading"))

    def test_binds_empty_multislot(self):
        self.MFPersonAssert(name="Bob", hobbies=())
        self.env.run()
        self.assertEqual(len(self.captured), 1)
        _, hobbies = self.captured[0]
        self.assertEqual(hobbies, ())


# =============================================================================
# End-to-end: sequence patterns
# =============================================================================

class TestSequencePatterns(unittest.TestCase):

    def test_contains_literal(self):
        matched = []

        class HasChess(Rule):
            MFPerson(name=name, hobbies=(*before, "chess", *after))

            def __action__(self):
                matched.append(self.name)

        env = Environment()
        MFPersonAssert = env.define(MFPerson)
        env.define(HasChess)
        env.reset()
        MFPersonAssert(name="Alice", hobbies=("reading", "chess", "coding"))
        MFPersonAssert(name="Bob", hobbies=("swimming",))
        env.run()
        self.assertEqual(matched, ["Alice"])

    def test_prefix_literal(self):
        matched = []

        class StartsWithChess(Rule):
            MFPerson(name=name, hobbies=("chess", *rest))

            def __action__(self):
                matched.append(self.name)

        env = Environment()
        MFPersonAssert = env.define(MFPerson)
        env.define(StartsWithChess)
        env.reset()
        MFPersonAssert(name="Alice", hobbies=("chess", "reading"))
        MFPersonAssert(name="Bob", hobbies=("reading", "chess"))
        env.run()
        self.assertEqual(matched, ["Alice"])

    def test_extract_single_element(self):
        captured = []

        class ExtractMiddle(Rule):
            MFData(items=(*before, x, *after))

            def __action__(self):
                captured.append((self.before, self.x, self.after))

        env = Environment()
        MFDataAssert = env.define(MFData)
        env.define(ExtractMiddle)
        env.reset()
        MFDataAssert(items=("a", "b", "c"))
        env.run()
        # Should match multiple ways (b at different positions)
        self.assertGreaterEqual(len(captured), 1)


# =============================================================================
# End-to-end: mixed wildcards
# =============================================================================

class TestMixedWildcards(unittest.TestCase):

    def test_single_wildcard_literal_multifield(self):
        matched = []

        class Match(Rule):
            MFData(items=(_, "chess", ...))

            def __action__(self):
                matched.append(True)

        env = Environment()
        MFDataAssert = env.define(MFData)
        env.define(Match)
        env.reset()
        MFDataAssert(items=("any", "chess", "x", "y"))
        MFDataAssert(items=("chess",))  # no match: needs 1 field before
        env.run()
        self.assertEqual(len(matched), 1)


# =============================================================================
# End-to-end: multifield in effects
# =============================================================================

class TestMultifieldEffects(unittest.TestCase):

    def test_starred_var_in_assert(self):
        class CopyItems(Rule):
            d = MFData(items=(*h,))
            asserts(MFOutput(items=(*h,)))

        env = Environment()
        MFDataAssert = env.define(MFData)
        env.define(MFOutput)
        env.define(CopyItems)
        env.reset()
        MFDataAssert(items=("a", "b", "c"))
        env.run()
        outputs = [f for f in env.facts()
                   if f.template.name.endswith('.MFOutput')]
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0]['items'], ("a", "b", "c"))


if __name__ == '__main__':
    unittest.main()
