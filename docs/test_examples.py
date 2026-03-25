"""Verify that code examples in documentation are correct.

Scans all Markdown files in docs/ for fenced Python code blocks and tests them:
- All blocks must be valid Python (ast.parse)
- Blocks that define Templates and Rules and call env.run() are executed
  end-to-end as subprocesses

Run: uv run --extra dsl pytest docs/test_examples.py -v
"""

import ast
import re
import subprocess
import tempfile
import textwrap
from pathlib import Path

import pytest

DOCS_DIR = Path(__file__).parent
GUIDE_FILES = sorted(DOCS_DIR.glob("*.md"))


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def _extract_python_blocks(text: str) -> list[tuple[int, str]]:
    """Extract (line_number, code) for each ```python block."""
    blocks = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("```python"):
            start = i + 1
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            code = "\n".join(code_lines)
            blocks.append((start, code))
        i += 1
    return blocks


def _has_class(code: str, base: str) -> bool:
    """Check if code defines a class inheriting from `base`."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for b in node.bases:
                if isinstance(b, ast.Name) and b.id == base:
                    return True
    return False


def _has_env_run(code: str) -> bool:
    return "env.run()" in code


# ---------------------------------------------------------------------------
# Syntax tests: every Python code block must parse
# ---------------------------------------------------------------------------

def _collect_all_blocks() -> list[tuple[str, int, str]]:
    """Return (filename, line, code) for every Python block in all docs."""
    all_blocks = []
    for md in GUIDE_FILES:
        text = md.read_text()
        for line, code in _extract_python_blocks(text):
            all_blocks.append((md.name, line, code))
    return all_blocks


ALL_BLOCKS = _collect_all_blocks()


@pytest.mark.parametrize(
    "filename,line,code",
    ALL_BLOCKS,
    ids=[f"{fn}:L{line}" for fn, line, _ in ALL_BLOCKS],
)
def test_block_parses(filename, line, code):
    """Every Python code block must be valid syntax."""
    # Skip intentionally abbreviated snippets (contain ... as placeholder)
    if re.search(r'[,{]\s*\.\.\.\s*[})]', code):
        pytest.skip("abbreviated snippet with ...")
    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(
            f"Syntax error in {filename} line {line + e.lineno}: {e.msg}")


# ---------------------------------------------------------------------------
# Executable examples: blocks that define an Environment, Templates, and Rules
# and call env.run(). Collected per-section from each guide.
# ---------------------------------------------------------------------------

def _build_executable_examples_from(md_path: Path) -> list[tuple[str, str]]:
    """Find self-contained executable examples in a single Markdown file.

    Strategy: scan for blocks that contain env.run(). For each, collect
    the preceding blocks in the same section (they likely define the
    templates and rules needed). A "section" resets at each ## heading.
    """
    text = md_path.read_text()
    blocks = _extract_python_blocks(text)
    if not blocks:
        return []

    lines = text.split("\n")

    # Map line numbers to section headings
    sections = []
    current_heading = "top"
    heading_start = 0
    for i, line in enumerate(lines):
        if line.startswith("## "):
            if sections:
                sections[-1] = (current_heading, heading_start, i)
            current_heading = line.strip("# ").strip()
            heading_start = i
            sections.append((current_heading, heading_start, len(lines)))
        elif not sections:
            sections.append((current_heading, 0, len(lines)))
    if not sections:
        return []

    # Group blocks by section
    section_blocks: dict[str, list[tuple[int, str]]] = {}
    for bline, bcode in blocks:
        for heading, start, end in sections:
            if start <= bline < end:
                section_blocks.setdefault(heading, []).append((bline, bcode))
                break

    # For each section that has an env.run() block, build a combined source
    examples = []
    for heading, sblocks in section_blocks.items():
        has_run = any(_has_env_run(code) for _, code in sblocks)
        if not has_run:
            continue

        # Collect all blocks up to and including the env.run() block
        combined_parts = []
        for _, code in sblocks:
            combined_parts.append(code)
            if _has_env_run(code):
                break

        combined = "\n\n".join(combined_parts)

        # Only include if it has at least one Template and looks self-contained
        if not _has_class(combined, "Template"):
            continue

        # Skip async examples (need 7.0x and special setup)
        if "async_run" in combined or "await " in combined:
            continue

        label = f"{md_path.name}::{heading}"
        examples.append((label, combined))

    return examples


def _collect_all_executable() -> list[tuple[str, str]]:
    examples = []
    for md in GUIDE_FILES:
        examples.extend(_build_executable_examples_from(md))
    return examples


EXECUTABLE = _collect_all_executable()


PREAMBLE = textwrap.dedent("""\
    import sys, types
    # Module registration for inspect.getsource (DSL requirement)
    _this = sys.modules.get(__name__)
    if _this is None or not hasattr(_this, "__file__"):
        _this = sys.modules.setdefault(__name__, types.ModuleType(__name__))
        _this.__file__ = __file__
    del _this

    from clipspyx import Environment
    from clipspyx.dsl import Template, Rule, Multi, before, after, concurrent
    from clipspyx.values import Symbol
    from clipspyx.tracing import enable_tracing
    from clipspyx.loops import enable_loop_detection, RuleLoopError
    import json
""")


@pytest.mark.parametrize(
    "label,code",
    EXECUTABLE,
    ids=[label[:60] for label, _ in EXECUTABLE],
)
def test_example_executes(label, code):
    """Executable examples must run without errors.

    The DSL uses inspect.getsource(), so code must live in a real file.
    We write each example to a temp file and run it as a subprocess.
    """
    full_code = PREAMBLE + "\n" + code

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", prefix="doc_test_", delete=False
    ) as f:
        f.write(full_code)
        f.flush()
        result = subprocess.run(
            ["uv", "run", "--extra", "dsl", "python", f.name],
            capture_output=True, text=True, timeout=15,
            cwd=str(DOCS_DIR.parent),
        )

    if result.returncode != 0:
        pytest.fail(
            f"Example in '{label}' failed (exit {result.returncode}):\n"
            f"  stderr: {result.stderr.strip()[:500]}\n"
            f"  First 5 code lines:\n"
            + "\n".join(f"    {l}" for l in code.split("\n")[:5])
        )
