"""Rule loop detection via transitive closure of RuleFiring provenance.

When enabled, three infrastructure rules compute the transitive closure of
the "triggers" relationship: if Rule A's output fact appears in Rule B's
inputs, A triggers B.  A self-edge (A triggers A transitively) indicates
a causal cycle.  A periodic callback counts firings for cycled rules and
halts execution when a configurable threshold is exceeded.

Usage::

    from clipspyx.tracing import enable_tracing
    from clipspyx.loops import enable_loop_detection

    env = Environment()
    enable_tracing(env)
    enable_loop_detection(env, threshold=5)

    # define templates and rules...
    env.run()  # raises RuleLoopError if a cycle repeats > 5 times
"""

from dataclasses import dataclass

from clipspyx._clipspyx import lib
from clipspyx.dsl import Template, Rule, Multi, Fact
from clipspyx.values import Symbol

# Import RuleFiring so it is registered in _template_registry before
# the infrastructure Rule subclasses are parsed by _RuleMeta.
from clipspyx.tracing import RuleFiring  # noqa: F401


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------

class RuleLoopError(Exception):
    """Raised when a rule in a detected cycle exceeds the firing threshold."""
    pass


# ---------------------------------------------------------------------------
# Infrastructure templates
# ---------------------------------------------------------------------------

class RuleTriggered(Template):
    """Direct or transitive causal link between rules."""
    __clips_name__ = "RuleTriggered"
    cause: Symbol
    effect: Symbol


class CycleDetected(Template):
    """Marks a rule as participating in a causal cycle."""
    __clips_name__ = "CycleDetected"
    rule: Symbol


# ---------------------------------------------------------------------------
# Infrastructure rules
# ---------------------------------------------------------------------------

class BuildDirectEdge(Rule):
    """Extract direct causal links: A produced a fact that B consumed."""
    __salience__ = 9999
    f1 = RuleFiring(rule=a, outputs=(*_, shared, *_))
    f2 = RuleFiring(rule=b, inputs=(*_, shared, *_))
    not RuleTriggered(cause=a, effect=b)

    asserts(RuleTriggered(cause=a, effect=b))


class BuildTransitive(Rule):
    """Extend causal chains: if A triggers B and B triggers C, then A triggers C."""
    __salience__ = 9998
    t1 = RuleTriggered(cause=a, effect=b)
    t2 = RuleTriggered(cause=b, effect=c)
    not RuleTriggered(cause=a, effect=c)

    asserts(RuleTriggered(cause=a, effect=c))


class DetectCycle(Rule):
    """Self-edge in transitive closure = cycle.  Mark it."""
    __salience__ = 10000
    t = RuleTriggered(cause=a, effect=a)
    not CycleDetected(rule=a)

    asserts(CycleDetected(rule=a))


# ---------------------------------------------------------------------------
# Per-environment state
# ---------------------------------------------------------------------------

@dataclass(eq=False)
class LoopDetectionState:
    threshold: int = 3
    detected_loop: tuple | None = None  # (rule_name, count) if exceeded


# ---------------------------------------------------------------------------
# Periodic callback
# ---------------------------------------------------------------------------

def _loop_check(env):
    """Periodic callback: count firings for cycled rules, halt if threshold exceeded."""
    state = env._loop_detection_state
    if state is None:
        return

    try:
        cd_tpl = env.find_template("CycleDetected")
    except LookupError:
        return

    cycled_rules = []
    for fact in cd_tpl.facts():
        cycled_rules.append(str(fact['rule']))

    if not cycled_rules:
        return

    rf_tpl = env.find_template("RuleFiring")
    for rule in cycled_rules:
        count = sum(1 for f in rf_tpl.facts() if str(f['rule']) == rule)
        if count > state.threshold:
            lib.SetHaltExecution(env._env, True)
            lib.SetHaltRules(env._env, True)
            state.detected_loop = (rule, count)
            return


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def enable_loop_detection(env, threshold=3):
    """Enable loop detection via transitive closure of RuleFiring provenance.

    Requires tracing to be enabled first (for ``RuleFiring`` facts).
    Must be called before defining business rules so that tracing hooks
    are injected into the rule RHS.

    Parameters
    ----------
    env : Environment
        The clipspyx Environment instance.
    threshold : int, optional
        Maximum number of firings allowed for a rule in a detected cycle
        before ``RuleLoopError`` is raised.  Defaults to 3.
    """
    if getattr(env, '_tracing_state', None) is None:
        raise RuntimeError(
            "Tracing must be enabled before loop detection. "
            "Call enable_tracing(env) first.")

    from clipspyx.dsl.define import define

    # Define infrastructure templates
    define(env, RuleTriggered)
    define(env, CycleDetected)

    # Define infrastructure rules
    define(env, BuildDirectEdge)
    define(env, BuildTransitive)
    define(env, DetectCycle)

    # Create per-environment state
    state = LoopDetectionState(threshold=threshold)
    env._loop_detection_state = state

    # Register periodic callback
    env.add_periodic_function("__py_loop_check", _loop_check)

    # Wrap agenda.run() for halt flag management and error raising
    agenda = env._agenda
    original_run = agenda.run

    def loop_checked_run(limit=None):
        state.detected_loop = None
        lib.SetHaltExecution(env._env, False)
        lib.SetHaltRules(env._env, False)
        result = original_run(limit)
        if state.detected_loop:
            rule, count = state.detected_loop
            state.detected_loop = None
            raise RuleLoopError(
                f"Cycle involving rule '{rule}': fired {count} times "
                f"(threshold: {state.threshold})")
        return result

    agenda.run = loop_checked_run


def disable_loop_detection(env):
    """Disable loop detection for the given environment."""
    state = getattr(env, '_loop_detection_state', None)
    if state is None:
        return

    env.remove_periodic_function("__py_loop_check")

    lib.SetHaltExecution(env._env, False)
    lib.SetHaltRules(env._env, False)

    env._loop_detection_state = None
