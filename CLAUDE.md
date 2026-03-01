# CLAUDE.md

## Project

clipspyx: CLIPS Python bindings via CFFI. Fork of clipspy with a simplified build system.

## Build

```bash
uv pip install -e .                          # Default: uses clips-64x orphan branch
CLIPS_BRANCH=clips-70x uv pip install -e .   # Use 70x source
CLIPS_SOURCE_DIR=/path/to/core pip install -e .  # Arbitrary source
```

CLIPS C source is compiled directly into the CFFI extension (no separate libclips).
Source resolution: `CLIPS_SOURCE_DIR` > `CLIPS_BRANCH` env var > default `clips-64x` branch.
Auto-checkout uses `git worktree add .clips-source <branch>`.

## Test

```bash
uv run pytest tests/ -v
```

## Key Files

| File | Purpose |
|------|---------|
| `clipspyx/clipspyx_build.py` | CFFI builder, resolves CLIPS source, compiles extension |
| `clipspyx/clips.cdef` | C function declarations for CFFI |
| `clipspyx/environment.py` | Main Environment class |
| `clipspyx/common.py` | Shared types, enums, error handling |
| `clipspyx/values.py` | Python <-> CLIPS value conversion |
| `clipspyx/facts.py` | Fact, Template classes |
| `clipspyx/classes.py` | Class, Instance classes |
| `clipspyx/routers.py` | I/O router system |
| `clipspyx/functions.py` | User-defined functions |
| `clipspyx/modules.py` | Module, Global variable classes |
| `scripts/sync-svn.py` | SVN sync: orphan branches + docs conversion |

## CLIPS Source Branches

Orphan branches contain CLIPS C source (no Python code):
- `clips-64x`: CLIPS 6.4.x source
- `clips-70x`: CLIPS 7.0.x source

Synced via `uv run scripts/sync-svn.py <branch-suffix>`.

## Reference Documentation

CLIPS reference docs are chunked into `docs/clips-reference/{branch}/`.
Each branch directory has an `AGENTS.md` mapping sections to files.
