# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.10.4] - 2026-03-29

### Added
- `AsyncRunner.schedule(coro)`: schedule an external coroutine to run during
  `run()` on the runner's event loop; safe to call from CLIPS rule actions
  (CFFI callbacks) where `asyncio.get_event_loop()` may not return the correct
  loop; tasks are added to the wait set and woken automatically

## [0.10.3] - 2026-03-29

### Fixed
- External async tasks created outside the runner (e.g. `schedule_async`
  coroutines from rule actions) were starved while `runner.run()` was active;
  `_run_loop` now yields to the event loop between cycles, giving external
  tasks a chance to execute

### Changed
- `_timer_every` now retracts the previous timer-event fact before asserting
  the next one (instead of on generator re-step via `finally`); this ensures
  timer facts survive event-loop yields between cycles so `env.run()` can
  see them

## [0.10.2] - 2026-03-29

### Fixed
- External async tasks created outside the runner (e.g. `schedule_async`
  coroutines from rule actions) were starved while `runner.run()` was active;
  `_wait_for_handlers` now yields to the event loop before waiting, giving
  external tasks a chance to execute each cycle

## [0.10.1] - 2026-03-28

### Fixed
- Persistent async generator handlers (e.g. WebSocket ingress) could starve
  non-persistent coroutine handlers (e.g. HTTP response); two fixes applied:
  `_gen_step` now yields to the event loop after each generator advance to
  prevent I/O starvation, and retracted-goal handlers are detached to an
  orphaned set instead of cancelled, allowing in-flight work to complete

## [0.10.0] - 2026-03-25

### Added
- Auto-wake: fact operations (`assert_fact`, `assert_string`, `retract`,
  `modify_slots`, `update_slots`, `load_facts`) automatically wake the
  `AsyncRunner` when a runner is active, eliminating the need for manual
  `wake()` calls after injecting facts from external async code; suppressed
  during rule execution (`env.run()`) and from within handler tasks to
  prevent spurious cycles; uses weak references for zero-leak lifecycle

## [0.9.0] - 2026-03-24

### Fixed
- `AsyncRunner` could only dispatch one generator-backed handler per template;
  multiple goals for the same template (e.g. two `every` timers, or an `every`
  timer blocking an `after` timer) now dispatch concurrently; `_persistent_tasks`
  is keyed by goal index instead of template name

### Added
- Loop detection via transitive closure of `RuleFiring` provenance:
  `env.enable_loop_detection(threshold=3)` defines infrastructure rules that
  compute causal chains between rules (A's output consumed by B's input) and
  detect cycles of any length; a periodic callback counts firings for cycled
  rules and raises `RuleLoopError` when the threshold is exceeded; requires
  tracing to be enabled first
- Periodic callback API: `env.add_periodic_function(name, callback, priority)`
  registers a Python callback invoked by CLIPS during rule execution (e.g. inside
  `Run()`); useful for polling signals, progress indicators, or timeouts;
  `env.remove_periodic_function(name)` unregisters it
- Opt-in SIGINT (Ctrl-C) handling: `env.enable_sigint_handler()` /
  `env.disable_sigint_handler()` and `with env.sigint_handler():` context
  manager; pressing Ctrl-C during `env.run()` gracefully halts CLIPS execution
  and raises `KeyboardInterrupt`; works with both sync `run()` and async
  `AsyncRunner.run()`; supports multiple simultaneous environments

## [0.8.0] - 2026-03-24

### Added
- Bound assert effects in DSL: `a = asserts(T(...))` captures the CLIPS fact
  address via `(bind ?a (assert ...))`, usable as slot values in subsequent
  `asserts()` calls or as the target of `retracts()` / `modifies()`; supports
  chaining (`b = asserts(U(ref=a))`)
- `AsyncRunner.wake()` method: interrupts a blocked `_wait_for_handlers` wait,
  causing the run loop to cycle back to `env.run()` immediately; safe to call
  from any coroutine, latching (pre-set wake consumed on next wait), and
  idempotent; enables external code to inject facts and have them processed
  without waiting for an existing handler to complete

## [0.7.2] - 2026-03-23
### Added
- `list[T]` type annotations on DSL template slots now work as multislots,
  equivalent to `Multi[T]`
- `object` and custom class type annotations on DSL template slots store
  arbitrary Python objects via CLIPS external addresses; works in templates,
  rules, and declarative effects
- `scripts/bump-version.py` for reliable version bumping across all packages,
  changelog headings, and release links

### Fixed
- External address slot values can now be read multiple times; previously,
  `python_external_address` destructively deleted the handle on first read,
  crashing on subsequent access to the same slot
## [0.7.1] - 2026-03-23

### Fixed
- `AsyncRunner` infinite re-dispatch of coroutine goal handlers that complete
  without satisfying their goal; handler now runs once per goal per `run()` call
  and the runner returns `"completed"` instead of looping

## [0.7.0] - 2026-03-23

### Added
- `AsyncRunner` class: resource context for async goal handling; manages full
  lifecycle (enable on init, disable on close); handlers can be async generators
  where bare `yield` encodes persistence and `try/finally` scopes resource
  cleanup to the yield point
- `**` (power) operator in DSL LHS expressions and effects; compiles to
  CLIPS `**` function (returns FLOAT)

### Removed
- `async_run()` function, `env.async_run()` method, `stop_event` parameter,
  `persistent` flag on `register_handler`: replaced by `AsyncRunner` with
  generator-based persistence

## [0.6.1] - 2026-03-22

### Fixed

- `concurrent()` ordering in multi-level chains: when a concurrent target had
  already-resolved negative salience (from being defined in an earlier ordering
  batch), the concurrent rule incorrectly received salience 0 instead of
  matching its target; caused rules to fire out of order in pipelines with 3+
  ordering levels
- String literals containing double quotes in `asserts()`/`modifies()` effects
  and `Literal` pattern slots now escape embedded `"` as `\"` for CLIPS;
  previously, strings like `'{"key": "val"}'` caused TMPLTDEF2 parse errors

## [0.6.0] - 2026-03-22

### Added

- Async run cancellation: `halt_async()` for internal (rule-driven) cancellation,
  `stop_event` parameter for external cancellation; `async_run()` now returns a
  reason string (`"completed"`, `"max_cycles"`, `"halted"`, `"stopped"`)
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

[Unreleased]: https://github.com/inferal-oss/clipspyx/compare/v0.10.4...HEAD
[0.10.4]: https://github.com/inferal-oss/clipspyx/compare/v0.10.3...v0.10.4
[0.10.3]: https://github.com/inferal-oss/clipspyx/compare/v0.10.2...v0.10.3
[0.10.2]: https://github.com/inferal-oss/clipspyx/compare/v0.10.1...v0.10.2
[0.10.1]: https://github.com/inferal-oss/clipspyx/compare/v0.10.0...v0.10.1
[0.10.0]: https://github.com/inferal-oss/clipspyx/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/inferal-oss/clipspyx/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/inferal-oss/clipspyx/compare/v0.7.2...v0.8.0
[0.7.2]: https://github.com/inferal-oss/clipspyx/compare/v0.7.1...v0.7.2
[0.7.1]: https://github.com/inferal-oss/clipspyx/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/inferal-oss/clipspyx/compare/v0.6.1...v0.7.0
[0.6.1]: https://github.com/inferal-oss/clipspyx/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/inferal-oss/clipspyx/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/inferal-oss/clipspyx/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/inferal-oss/clipspyx/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/inferal-oss/clipspyx/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/inferal-oss/clipspyx/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/inferal-oss/clipspyx/commits/v0.1.0
