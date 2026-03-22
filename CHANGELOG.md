# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Fact lifecycle events: `env.enable_fact_events()` generates `FactAsserted`,
  `FactRetracted`, and `FactModified` meta-facts for every fact base change;
  retracted facts captured as ppform strings; modify events deferred to next
  `run()` cycle; coexists with tracing

## [0.5.0] - 2026-03-22

### Added

- Return-value constraints in DSL pattern slots: arithmetic expressions
  (`x + y`, `x * 2`, `(x + y) * z`) compile to CLIPS `=(expr)` syntax,
  enabling computed slot matching and backward chaining with evaluated values
- Function calls in DSL pattern slots: CLIPS built-ins like `abs(x)` compile
  to `=(abs ?x)` directly; Python functions are auto-registered at
  `env.define()` time via the `python-function` bridge with no manual
  `define_function()` step needed

## [0.4.0] - 2026-03-22

### Added

- Fact provenance tracing: `env.enable_tracing()` records every rule firing as
  a `RuleFiring` fact with `FACT-ADDRESS` multislots for inputs and outputs;
  works for both `__action__` and declarative-effect rules; chain is walkable
  to trace any fact back to its origins
- `Fact` sentinel type for generic `FACT-ADDRESS` slots and multislots
  (`Multi[Fact]`); enables templates that reference facts of any template type
- C-level fact lifecycle callbacks: `AddAssertFunction`, `AddRetractFunction`,
  `AddModifyFunction` exposed in CFFI bindings (both 6.4x and 7.0x)
- Multifield pattern matching in DSL rules: `...` for multifield wildcards,
  `*name` for multifield variables, tuple syntax for sequence patterns
  (`(*before, "chess", *after)`); works in both LHS patterns and
  declarative effects
- Async goal handler framework (CLIPS 7.0x): `env.enable_goal_handlers()`
  enables an asyncio-based run loop (`await env.async_run()`) that dispatches
  backward chaining goals to registered Python async handlers; built-in
  `TimerEvent` template supports one-shot (`after`), absolute (`at`), and
  periodic (`every`) timers; custom handlers registered via
  `env.register_goal_handler(TemplateClass, handler)` accept DSL Template
  classes or CLIPS name strings; cancellation via controlling fact retraction
- `Symbol("...")` literals now work in declarative effects (`asserts`,
  `modifies`); previously fell through to wildcard `?` in effect codegen
- `UniversallyQuantifiedValue` sentinel for CLIPS universally quantified
  values (type 12, displayed as `??`); reading unspecified goal slots now
  returns this sentinel instead of crashing with `KeyError`

## [0.3.0] - 2026-03-21

### Added

- Declarative ordering constraints for DSL rules: `before()`, `after()`,
  `concurrent()` compute CLIPS salience automatically from a topological sort
  of the ordering graph; supports transitive ordering, transitive concurrent
  groups, cycle detection, and auto-finalization on `define()`

### Changed

- DSL documentation now covers declarative effect declarations (`asserts()`,
  `retracts()`, `modifies()`), `__clips_name__` for custom CLIPS names, and
  updated RHS overview
- CLIPS 7.0x source updated to SVN r970; build-time `modulbin.c` patch removed
  (fix now included upstream)

## [0.2.0] - 2026-03-20

### Added

- Declarative effect declarations for DSL rules: `asserts()`, `retracts()`,
  `modifies()` generate native CLIPS RHS code without a Python bridge function;
  visualization renders effect edges with distinct styling
  ([d00dba6](https://github.com/inferal-oss/clipspyx/commit/d00dba6))
- Meta-template reflection: every `Environment` auto-defines `__Template__`
  and `__TemplateSlot__` deftemplates populated after each `reset()`, enabling
  rules that reason about schema structure
  ([f911a6b](https://github.com/inferal-oss/clipspyx/commit/f911a6b))
- `__clips_name__` support on DSL templates for custom CLIPS names
  ([f911a6b](https://github.com/inferal-oss/clipspyx/commit/f911a6b))

## [0.1.0]

### Added

- Fork of clipspy, renamed to clipspyx ([f44e3b2](https://github.com/inferal-oss/clipspyx/commit/f44e3b2))
- Direct CFFI compilation of CLIPS C source, no separate Makefile step ([c39b9db](https://github.com/inferal-oss/clipspyx/commit/c39b9db))
- Split into four packages: `clipspyx-ffi`, `clipspyx-ffi-64x`,
  `clipspyx-ffi-70x`, `clipspyx` with `[64x]`/`[70x]` extras ([3848e64](https://github.com/inferal-oss/clipspyx/commit/3848e64))
- CLIPS 7.0x support: deftables, backward chaining, template inheritance,
  certainty factors, `update_slots` ([f6737a6](https://github.com/inferal-oss/clipspyx/commit/f6737a6), [a28c076](https://github.com/inferal-oss/clipspyx/commit/a28c076))
- Python-native DSL via `Template` and `Rule` base classes ([71b629c](https://github.com/inferal-oss/clipspyx/commit/71b629c))
- Attribute-style slot access on `TemplateFact` ([3407bb1](https://github.com/inferal-oss/clipspyx/commit/3407bb1))
- `env.visualize()` for D2 diagram generation with templates, rules, edges,
  docstring notes, and `group_by_kind` grouping ([22af4b7](https://github.com/inferal-oss/clipspyx/commit/22af4b7))

### Fixed

- Build-time patch for CLIPS 7.0x `Bload()` SEGV in `RehashValues` ([5fc5cd1](https://github.com/inferal-oss/clipspyx/commit/5fc5cd1))
- `git apply` patch failure on Windows due to CRLF corruption ([989e154](https://github.com/inferal-oss/clipspyx/commit/989e154), [f95829d](https://github.com/inferal-oss/clipspyx/commit/f95829d))
- Linux wheels rejected by PyPI due to `linux_x86_64` platform tag ([233faa3](https://github.com/inferal-oss/clipspyx/commit/233faa3))

[Unreleased]: https://github.com/inferal-oss/clipspyx/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/inferal-oss/clipspyx/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/inferal-oss/clipspyx/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/inferal-oss/clipspyx/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/inferal-oss/clipspyx/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/inferal-oss/clipspyx/commits/v0.1.0
