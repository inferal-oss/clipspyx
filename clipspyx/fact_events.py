"""Fact lifecycle event meta-facts for CLIPS environments.

When fact events are enabled, every assert/retract/modify generates a
corresponding meta-fact that rules can match against.
"""

import traceback
from dataclasses import dataclass, field

from clipspyx.dsl import Template, Fact
from clipspyx.values import Symbol

from clipspyx._clipspyx import lib, ffi


# ---------------------------------------------------------------------------
# DSL templates for fact event meta-facts
# ---------------------------------------------------------------------------

class FactAsserted(Template):
    __clips_name__ = "FactAsserted"
    fact: Fact
    index: int
    template: Symbol


class FactRetracted(Template):
    __clips_name__ = "FactRetracted"
    index: int
    template: Symbol
    ppform: str


class FactModified(Template):
    __clips_name__ = "FactModified"
    fact: Fact
    old_index: int
    old_ppform: str
    template: Symbol


# ---------------------------------------------------------------------------
# Per-environment state
# ---------------------------------------------------------------------------

_META_TEMPLATES = {"FactAsserted", "FactRetracted", "FactModified"}


def _should_skip(tpl, tpl_name):
    """Check if a fact should not generate events."""
    if tpl_name in _META_TEMPLATES:
        return True
    # Skip internal infrastructure templates (but not module-qualified names
    # like __main__.MyTemplate which are user DSL templates)
    if tpl_name.startswith("__") and "." not in tpl_name:
        return True
    if lib.ImpliedDeftemplate(tpl):
        return True
    return False


@dataclass
class FactEventsState:
    enabled: bool = False
    handle: object = None
    env: object = None
    pending_modifies: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# C callbacks
# ---------------------------------------------------------------------------

def _flush_pending_modifies(state):
    """Assert any queued FactModified events (deferred from modify callback)."""
    while state.pending_modifies:
        data = state.pending_modifies.pop(0)
        try:
            tpl = state.env.find_template("FactModified")
            tpl.assert_fact(**data)
        except BaseException:
            msg = "[FACT_EVENTS] deferred modify assert error:\n" + traceback.format_exc()
            lib.WriteString(state.env._env, b"stderr", msg.encode())


@ffi.def_extern()
def _fact_event_on_assert(env, fact_void, context_void):
    try:
        state = ffi.from_handle(context_void)

        # Flush any pending modify events now that we're in a safe state
        if state.pending_modifies:
            _flush_pending_modifies(state)

        fact_ptr = ffi.cast("Fact *", fact_void)
        tpl = lib.FactDeftemplate(fact_ptr)
        tpl_name = ffi.string(lib.DeftemplateName(tpl)).decode()
        if _should_skip(tpl, tpl_name):
            return

        from clipspyx.facts import TemplateFact
        fact_obj = TemplateFact(env, fact_ptr)
        fact_index = lib.FactIndex(fact_ptr)
        tpl_tpl = state.env.find_template("FactAsserted")
        tpl_tpl.assert_fact(fact=fact_obj, index=fact_index,
                            template=Symbol(tpl_name))
    except BaseException:
        msg = "[FACT_EVENTS] assert callback error:\n" + traceback.format_exc()
        lib.WriteString(env, b"stderr", msg.encode())


@ffi.def_extern()
def _fact_event_on_retract(env, fact_void, context_void):
    try:
        state = ffi.from_handle(context_void)
        fact_ptr = ffi.cast("Fact *", fact_void)
        tpl = lib.FactDeftemplate(fact_ptr)
        tpl_name = ffi.string(lib.DeftemplateName(tpl)).decode()
        if _should_skip(tpl, tpl_name):
            return

        # Capture data before the fact becomes garbage
        from clipspyx.facts import fact_pp_string
        fact_index = lib.FactIndex(fact_ptr)
        ppform = fact_pp_string(env, fact_ptr)

        tpl_tpl = state.env.find_template("FactRetracted")
        tpl_tpl.assert_fact(index=fact_index, template=Symbol(tpl_name),
                            ppform=ppform)
    except BaseException:
        msg = "[FACT_EVENTS] retract callback error:\n" + traceback.format_exc()
        lib.WriteString(env, b"stderr", msg.encode())


@ffi.def_extern()
def _fact_event_on_modify(env, old_fact, new_fact, context_void):
    try:
        state = ffi.from_handle(context_void)

        # CLIPS 7.0 fires the modify callback twice:
        #   1st: old_fact=valid, new_fact=NULL (pre-modify)
        #   2nd: old_fact=NULL, new_fact=valid (post-modify)
        # We capture old data on the first call and emit the event on the second.

        if new_fact == ffi.NULL:
            # Pre-modify: capture old fact data
            tpl = lib.FactDeftemplate(old_fact)
            tpl_name = ffi.string(lib.DeftemplateName(tpl)).decode()
            if _should_skip(tpl, tpl_name):
                return
            from clipspyx.facts import fact_pp_string
            state._modify_pending = {
                'old_index': lib.FactIndex(old_fact),
                'old_ppform': fact_pp_string(env, old_fact),
                'tpl_name': tpl_name,
            }
            return

        if old_fact == ffi.NULL:
            # Post-modify: emit the event with captured old data
            pending = getattr(state, '_modify_pending', None)
            if pending is None:
                return
            from clipspyx.facts import TemplateFact
            new_obj = TemplateFact(env, new_fact)
            # Queue for deferred assertion (not safe to assert mid-callback)
            state.pending_modifies.append({
                'fact': new_obj,
                'old_index': pending['old_index'],
                'old_ppform': pending['old_ppform'],
                'template': Symbol(pending['tpl_name']),
            })
            state._modify_pending = None
    except BaseException:
        msg = "[FACT_EVENTS] modify callback error:\n" + traceback.format_exc()
        lib.WriteString(env, b"stderr", msg.encode())


# ---------------------------------------------------------------------------
# Enable / disable
# ---------------------------------------------------------------------------

def enable_fact_events(env):
    """Enable fact lifecycle event meta-facts."""
    from clipspyx.dsl.define import define

    define(env, FactAsserted)
    define(env, FactRetracted)
    define(env, FactModified)

    state = FactEventsState(enabled=True, env=env)
    handle = ffi.new_handle(state)
    state.handle = handle

    lib.AddAssertFunction(
        env._env, b"__py_fact_events", lib._fact_event_on_assert, 0, handle)
    lib.AddRetractFunction(
        env._env, b"__py_fact_events", lib._fact_event_on_retract, 0, handle)
    lib.AddModifyFunction(
        env._env, b"__py_fact_events", lib._fact_event_on_modify, 0, handle)

    env._fact_events_state = state

    # Flush pending modify events before each run cycle
    agenda = env._agenda
    original_run = agenda.run

    def run_with_flush(limit=None):
        _flush_pending_modifies(state)
        return original_run(limit)

    agenda.run = run_with_flush


def disable_fact_events(env):
    """Disable fact lifecycle event meta-facts."""
    state = getattr(env, '_fact_events_state', None)
    if state is None:
        return

    lib.RemoveAssertFunction(env._env, b"__py_fact_events")
    lib.RemoveRetractFunction(env._env, b"__py_fact_events")
    lib.RemoveModifyFunction(env._env, b"__py_fact_events")

    env._fact_events_state = None
