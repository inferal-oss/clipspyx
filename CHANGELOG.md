# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- DSL documentation now covers declarative effect declarations (`asserts()`,
  `retracts()`, `modifies()`), `__clips_name__` for custom CLIPS names, and
  updated RHS overview

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

[Unreleased]: https://github.com/inferal-oss/clipspyx/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/inferal-oss/clipspyx/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/inferal-oss/clipspyx/commits/v0.1.0
