# CLAUDE.md

## Project

clipspyx: CLIPS Python bindings via CFFI. Fork of clipspy with a simplified build system.

## Package Structure

Four packages share version `0.1.0`:

| Package | Location | Purpose |
|---------|----------|---------|
| `clipspyx-ffi` | `backends/ffi/` | Shared CFFI build infrastructure, cdef files, C source template |
| `clipspyx-ffi-64x` | `backends/ffi-64x/` | Compiles CLIPS 6.4x CFFI extension |
| `clipspyx-ffi-70x` | `backends/ffi-70x/` | Compiles CLIPS 7.0x CFFI extension |
| `clipspyx` | `.` (root) | Pure Python bindings, uses FFI backends via extras |

## Build

```bash
# Install with 64x backend (default)
uv pip install -e backends/ffi && uv pip install -e backends/ffi-64x && uv pip install -e .

# Install with 70x backend
CLIPS_BRANCH=clips-70x uv pip install -e backends/ffi && uv pip install -e backends/ffi-70x && uv pip install -e .

# Arbitrary CLIPS source
CLIPS_SOURCE_DIR=/path/to/core uv pip install -e backends/ffi-64x

# Build distributable wheels
uv run scripts/build-backend.py 64x   # builds clipspyx-ffi + clipspyx-ffi-64x wheels
uv run scripts/build-backend.py 70x   # builds clipspyx-ffi + clipspyx-ffi-70x wheels

# End-user install (from published wheels)
pip install clipspyx[64x]
pip install clipspyx[70x]
```

CLIPS C source is compiled directly into the CFFI extension (no separate libclips).
Source resolution: `CLIPS_SOURCE_DIR` > `CLIPS_BRANCH` env var > default branch.
Auto-checkout uses `git worktree add .clips-source/<suffix> <branch>` (e.g. `.clips-source/64x/`, `.clips-source/70x/`). Multiple checkouts coexist without switching.

## Test

```bash
uv run pytest tests/ -v
```

## Key Files

| File | Purpose |
|------|---------|
| `backends/ffi/clipspyx_ffi/build.py` | Shared CFFI builder: `resolve_clips_source()`, `make_ffibuilder()` |
| `backends/ffi/clipspyx_ffi/clips.cdef` | C function declarations for CLIPS 6.4x |
| `backends/ffi/clipspyx_ffi/clips-70x.cdef` | Additional C declarations for CLIPS 7.0x |
| `backends/ffi-64x/clipspyx_ffi_64x/_build.py` | CFFI build entry point for 64x backend |
| `backends/ffi-70x/clipspyx_ffi_70x/_build.py` | CFFI build entry point for 70x backend |
| `clipspyx/_clipspyx/__init__.py` | Import redirect: tries 70x, then 64x, else ImportError |
| `clipspyx/environment.py` | Main Environment class |
| `clipspyx/common.py` | Shared types, enums, error handling |
| `clipspyx/values.py` | Python <-> CLIPS value conversion |
| `clipspyx/facts.py` | Fact, Template classes |
| `clipspyx/classes.py` | Class, Instance classes |
| `clipspyx/routers.py` | I/O router system |
| `clipspyx/functions.py` | User-defined functions |
| `clipspyx/modules.py` | Module, Global variable classes |
| `scripts/build-backend.py` | Builds clipspyx-ffi + variant wheels for distribution |
| `scripts/sync-svn.py` | SVN sync: orphan branches + docs conversion |

## CLIPS Source Branches

Orphan branches contain CLIPS C source (no Python code):
- `clips-64x`: CLIPS 6.4.x source
- `clips-70x`: CLIPS 7.0.x source

Synced via `uv run scripts/sync-svn.py <branch-suffix>`.

## Reference Documentation

CLIPS reference docs are chunked into `docs/clips-reference/{branch}/`.
Each branch directory has an `AGENTS.md` mapping sections to files.
