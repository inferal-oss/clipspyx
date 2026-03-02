# clipspyx

CLIPS Python bindings via CFFI. Fork of [clipspy](https://github.com/noxdafox/clipspy).

## Building

clipspyx compiles CLIPS source directly into the CFFI extension. No separate `libclips` build step.

### Prerequisites

- Python 3.10+
- C compiler (gcc/clang on Linux/macOS, MSVC on Windows)
- CLIPS source (auto-checked out from orphan branch, or provide your own)

### Install for development

```bash
# Install with 64x backend (CLIPS 6.4x)
uv sync --extra 64x

# Install with 70x backend (CLIPS 7.0x)
uv sync --extra 70x
```

### Switching backends

The 64x and 70x backends conflict with each other. Always use `uv sync` to switch:

```bash
# Switch to 64x
uv sync --extra 64x

# Switch to 70x
uv sync --extra 70x
```

**Important:** `uv run --extra 64x` does *not* remove a previously installed 70x backend
(and vice versa). Only `uv sync --extra <variant>` correctly installs the requested
backend and removes the conflicting one.

### CLIPS source override

```bash
# Use an arbitrary CLIPS source directory
CLIPS_SOURCE_DIR=/path/to/clips/core uv sync --extra 64x
```

### Build distributable wheels

```bash
uv run scripts/build-backend.py 64x   # builds clipspyx-ffi + clipspyx-ffi-64x wheels
uv run scripts/build-backend.py 70x   # builds clipspyx-ffi + clipspyx-ffi-70x wheels
```

### CLIPS Source Management

CLIPS source is stored in git orphan branches (`clips-64x`, `clips-70x`).
Sync from SVN:

```bash
uv run scripts/sync-svn.py 64x   # syncs core/ -> orphan branch clips-64x
uv run scripts/sync-svn.py 70x   # syncs core/ -> orphan branch clips-70x
```

## Usage

```python
import clipspyx

env = clipspyx.Environment()
env.build('(defrule hello (initial-fact) => (println "Hello CLIPS!"))')
env.reset()
env.run()
```

## Testing

```bash
uv run pytest tests/ -v
```

## License

BSD-3-Clause. See [LICENSE.txt](LICENSE.txt).
