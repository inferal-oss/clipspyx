"""Fact provenance tracing for CLIPS environments.

When tracing is enabled, every rule firing is recorded as a RuleFiring fact
containing the rule name, the input facts that matched its LHS, and the
output facts it asserted on its RHS.

"""

import traceback
from dataclasses import dataclass, field

from clipspyx.dsl import Template, Multi, Fact
from clipspyx.values import Symbol

from clipspyx._clipspyx import lib, ffi


# ---------------------------------------------------------------------------
# DSL template for provenance facts
# ---------------------------------------------------------------------------

class RuleFiring(Template):
    __clips_name__ = "RuleFiring"
    rule: Symbol
    inputs: Multi[Fact]
    outputs: Multi[Fact]


# ---------------------------------------------------------------------------
# Per-environment tracing state
# ---------------------------------------------------------------------------

@dataclass
class TracingState:
    enabled: bool = False
    handle: object = None           # CData from ffi.new_handle
    current_rule: str | None = None
    current_inputs: list = field(default_factory=list)   # TemplateFact objects
    pending_outputs: list = field(default_factory=list)   # raw Fact* CData, retained


# ---------------------------------------------------------------------------
# C callbacks registered via AddAssertFunction / AddRetractFunction / etc.
# ---------------------------------------------------------------------------

@ffi.def_extern()
def _tracing_on_assert(env, fact_void, context_void):
    """Called by CLIPS after every (assert ...).

    If a rule is currently being traced, retain the fact and add it to
    the pending outputs list.
    """
    try:
        state = ffi.from_handle(context_void)
        if state.current_rule is None:
            return

        fact_ptr = ffi.cast("Fact *", fact_void)

        # Skip infrastructure facts to avoid infinite recursion
        tpl = lib.FactDeftemplate(fact_ptr)
        tpl_name = ffi.string(lib.DeftemplateName(tpl)).decode()
        if tpl_name == "RuleFiring":
            return

        lib.RetainFact(fact_ptr)
        state.pending_outputs.append(fact_ptr)
    except BaseException:
        msg = "[TRACING] assert callback error:\n" + traceback.format_exc()
        lib.WriteString(env, b"stderr", msg.encode())


@ffi.def_extern()
def _tracing_on_retract(env, fact_void, context_void):
    """Called by CLIPS after every (retract ...).  No-op for now."""
    pass


@ffi.def_extern()
def _tracing_on_modify(env, old_fact, new_fact, context_void):
    """Called by CLIPS after every (modify ...).  No-op for now."""
    pass


# ---------------------------------------------------------------------------
# Finalize: assert RuleFiring fact from accumulated data
# ---------------------------------------------------------------------------

def _finalize_current(env, state):
    """Assert a RuleFiring fact for the current rule firing, if any."""
    if state.current_rule is None:
        return

    from clipspyx.facts import TemplateFact

    rule_name = state.current_rule
    inputs = tuple(state.current_inputs)

    # Convert raw Fact* CData pointers to TemplateFact objects
    outputs = []
    for fact_ptr in state.pending_outputs:
        outputs.append(TemplateFact(env._env, fact_ptr))
    outputs = tuple(outputs)

    # Assert the RuleFiring fact
    try:
        tpl = env.find_template("RuleFiring")
        tpl.assert_fact(
            rule=Symbol(rule_name),
            inputs=inputs,
            outputs=outputs,
        )
    except Exception:
        msg = "[TRACING] finalize error:\n" + traceback.format_exc()
        lib.WriteString(env._env, b"stderr", msg.encode())

    # Release retained output facts
    for fact_ptr in state.pending_outputs:
        lib.ReleaseFact(fact_ptr)

    # Clear state for next firing
    state.current_rule = None
    state.current_inputs = []
    state.pending_outputs = []


# ---------------------------------------------------------------------------
# Enable / disable tracing
# ---------------------------------------------------------------------------

def enable_tracing(env):
    """Enable fact provenance tracking for the given environment.

    Registers the RuleFiring template, C callbacks for assert/retract/modify,
    and the __dsl_trace_begin bridge function.
    """
    from clipspyx.dsl.define import define

    # Register RuleFiring template
    define(env, RuleFiring)

    # Create state and handle
    state = TracingState(enabled=True)
    handle = ffi.new_handle(state)
    state.handle = handle

    # Register C callbacks
    lib.AddAssertFunction(
        env._env, b"__py_tracing", lib._tracing_on_assert, 0, handle)
    lib.AddRetractFunction(
        env._env, b"__py_tracing", lib._tracing_on_retract, 0, handle)
    lib.AddModifyFunction(
        env._env, b"__py_tracing", lib._tracing_on_modify, 0, handle)

    # Store state on the environment
    env._tracing_state = state

    # Wrap run() to finalize pending trace after each run
    agenda = env._agenda
    original_run = agenda.run

    def tracing_run(limit=None):
        result = original_run(limit)
        _finalize_current(env, state)
        return result

    agenda.run = tracing_run

    # Register trace-begin bridge function
    def trace_begin(rule_name, *input_facts):
        _finalize_current(env, state)
        state.current_rule = str(rule_name)
        state.current_inputs = list(input_facts)
        state.pending_outputs = []

    env.define_function(trace_begin, name='__dsl_trace_begin')


def disable_tracing(env):
    """Disable fact provenance tracking for the given environment."""
    state = getattr(env, '_tracing_state', None)
    if state is None:
        return

    # Finalize any pending recording
    _finalize_current(env, state)

    # Remove C callbacks
    lib.RemoveAssertFunction(env._env, b"__py_tracing")
    lib.RemoveRetractFunction(env._env, b"__py_tracing")
    lib.RemoveModifyFunction(env._env, b"__py_tracing")

    # Clear state
    env._tracing_state = None
