# clipspyx

CLIPS Python bindings via CFFI. Fork of [clipspy](https://github.com/noxdafox/clipspy).

## Building

clipspyx compiles CLIPS source directly into the CFFI extension. No separate `libclips` build step.

### Prerequisites

- Python 3.10+
- C compiler (gcc/clang)
- CLIPS source (auto-checked out from orphan branch, or provide your own)

### Install

```bash
# Default: auto-checkouts clips-64x orphan branch
uv pip install -e .

# Use a specific CLIPS branch
CLIPS_BRANCH=clips-70x uv pip install -e .

# Use an arbitrary CLIPS source directory
CLIPS_SOURCE_DIR=/path/to/clips/core uv pip install -e .
```

### CLIPS Source Management

CLIPS source is stored in git orphan branches (e.g., `clips-64x`, `clips-70x`).
Sync from SVN:

```bash
./scripts/sync-svn.sh 64x   # syncs core/ -> orphan branch clips-64x
./scripts/sync-svn.sh 70x   # syncs core/ -> orphan branch clips-70x
```

## Usage

```python
import clipspyx

env = clipspyx.Environment()
env.build('(defrule hello (initial-fact) => (println "Hello CLIPS!"))')
env.reset()
env.run()
```

## License

BSD-3-Clause. See [LICENSE.txt](LICENSE.txt).
