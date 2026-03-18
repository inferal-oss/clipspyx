"""Meta-template reflection for CLIPS environments.

Provides __Template__ and __TemplateSlot__ deftemplates whose facts describe
all other templates in the environment, enabling rule-based reasoning about
schema metadata.

Automatically enabled for every Environment. After reset + run,
__Template__ and __TemplateSlot__ facts are available for all defined
templates. Call (sync-meta-templates) from CLIPS to refresh manually.

"""

from clipspyx.dsl import Template as _TemplateBase, Multi
from clipspyx.values import Symbol
from clipspyx.common import TemplateSlotDefaultType


DEFTEMPLATE_META = """\
(deftemplate __Template__
  (slot name (type SYMBOL))
  (slot module (type SYMBOL))
  (slot implied (type SYMBOL))
  (multislot slots (type SYMBOL)))"""

DEFTEMPLATE_META_SLOT = """\
(deftemplate __TemplateSlot__
  (slot template (type SYMBOL))
  (slot name (type SYMBOL))
  (multislot types (type SYMBOL))
  (slot single (type SYMBOL))
  (slot has_default (type SYMBOL)))"""

DEFFACTS_TRIGGER = """\
(deffacts __meta-templates-trigger
  (__meta-sync-trigger))"""

DEFRULE_SYNC = """\
(defrule __sync-meta-templates
  (declare (salience 10000))
  (__meta-sync-trigger)
  =>
  (sync-meta-templates))"""

# --- DSL companion classes for Rule pattern matching ---
# These are NOT env.define()-d; the raw deftemplates already exist.
# Import and use in Rule bodies to match __Template__/__TemplateSlot__ facts.

class MetaTemplate(_TemplateBase):
    """DSL type stub for __Template__ facts. Use in Rule patterns."""
    __clips_name__ = "__Template__"

    name: Symbol
    module: Symbol
    implied: Symbol
    slots: Multi[Symbol]


class MetaTemplateSlot(_TemplateBase):
    """DSL type stub for __TemplateSlot__ facts. Use in Rule patterns."""
    __clips_name__ = "__TemplateSlot__"

    template: Symbol
    name: Symbol
    types: Multi[Symbol]
    single: Symbol
    has_default: Symbol


_DEFAULT_TYPE_MAP = {
    TemplateSlotDefaultType.STATIC_DEFAULT: Symbol("STATIC"),
    TemplateSlotDefaultType.DYNAMIC_DEFAULT: Symbol("DYNAMIC"),
}


def enable_meta_templates(env):
    """Enable meta-template reflection in a CLIPS environment.

    Builds __Template__ and __TemplateSlot__ deftemplates, a trigger deffacts,
    a sync rule, and registers sync-meta-templates as a callable CLIPS function.

    """
    env.build(DEFTEMPLATE_META)
    env.build(DEFTEMPLATE_META_SLOT)

    def _sync(env=env):
        _sync_meta_templates(env)

    env.define_function(_sync, name='sync-meta-templates')
    env.build(DEFFACTS_TRIGGER)
    env.build(DEFRULE_SYNC)


def _sync_meta_templates(env):
    """Retract stale meta-facts and assert current template metadata."""
    to_retract = []
    for fact in env.facts():
        tname = fact.template.name
        if tname in ('__Template__', '__TemplateSlot__'):
            to_retract.append(fact)
    for fact in to_retract:
        fact.retract()

    meta_tpl = env.find_template('__Template__')
    slot_tpl = env.find_template('__TemplateSlot__')

    for template in env.templates():
        implied = template.implied
        slots = () if implied else tuple(
            Symbol(s.name) for s in template.slots
        )

        meta_tpl.assert_fact(
            name=Symbol(template.name),
            module=Symbol(template.module.name),
            implied=Symbol("TRUE") if implied else Symbol("FALSE"),
            slots=slots,
        )

        if not implied:
            for slot in template.slots:
                default_sym = _DEFAULT_TYPE_MAP.get(
                    slot.default_type, Symbol("NONE")
                )
                slot_tpl.assert_fact(
                    template=Symbol(template.name),
                    name=Symbol(slot.name),
                    types=slot.types,
                    single=Symbol("TRUE") if not slot.multifield else Symbol("FALSE"),
                    has_default=default_sym,
                )
