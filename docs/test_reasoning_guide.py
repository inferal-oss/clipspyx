"""Verify that code examples in reasoning-guide.md are correct.

Extracts fenced Python code blocks from the guide and tests them:
- All blocks must be valid Python (ast.parse)
- Blocks that define Templates and Rules are compiled into a CLIPS environment
- Blocks with env.run() are executed end-to-end

Run: uv run --extra dsl pytest docs/test_reasoning_guide.py -v
"""

import ast
import re
import textwrap
from pathlib import Path

import pytest

GUIDE = Path(__file__).parent / "reasoning-guide.md"


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


GUIDE_TEXT = GUIDE.read_text()
BLOCKS = _extract_python_blocks(GUIDE_TEXT)


@pytest.mark.parametrize(
    "line,code",
    BLOCKS,
    ids=[f"L{line}" for line, _ in BLOCKS],
)
def test_block_parses(line, code):
    """Every Python code block must be valid syntax."""
    # Skip intentionally abbreviated snippets (contain ... as placeholder)
    if re.search(r'[,{]\s*\.\.\.\s*[})]', code):
        pytest.skip("abbreviated snippet with ...")
    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(f"Syntax error at guide line {line + e.lineno}: {e.msg}")


# ---------------------------------------------------------------------------
# Executable examples: blocks that define an Environment, Templates, and Rules
# and call env.run(). We collect "sections" -- contiguous groups of code blocks
# that build on each other (share template/rule definitions).
# ---------------------------------------------------------------------------

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


def _build_executable_examples() -> list[tuple[str, str]]:
    """Find self-contained executable examples.

    Strategy: scan for blocks that contain env.run(). For each, collect
    the preceding blocks in the same section (they likely define the
    templates and rules needed). A "section" resets at each ## heading.
    """
    lines = GUIDE_TEXT.split("\n")
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
    for bline, bcode in BLOCKS:
        for heading, start, end in sections:
            if start <= bline < end:
                section_blocks.setdefault(heading, []).append((bline, bcode))
                break

    # For each section that has an env.run() block, build a combined source
    examples = []
    for heading, blocks in section_blocks.items():
        has_run = any(_has_env_run(code) for _, code in blocks)
        if not has_run:
            continue

        # Collect all blocks up to and including the env.run() block
        combined_parts = []
        for _, code in blocks:
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

        examples.append((heading, combined))

    return examples


EXECUTABLE = _build_executable_examples()


@pytest.mark.parametrize(
    "heading,code",
    EXECUTABLE,
    ids=[h[:50] for h, _ in EXECUTABLE],
)
def test_example_executes(heading, code):
    """Executable examples must run without errors.

    The DSL uses inspect.getsource(), so code must live in a real file.
    We write each example to a temp file and run it as a subprocess.
    """
    import subprocess
    import tempfile

    preamble = textwrap.dedent("""\
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
        import json
    """)

    full_code = preamble + "\n" + code

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", prefix="guide_test_", delete=False
    ) as f:
        f.write(full_code)
        f.flush()
        result = subprocess.run(
            ["uv", "run", "--extra", "dsl", "python", f.name],
            capture_output=True, text=True, timeout=15,
            cwd=str(Path(__file__).parent.parent),
        )

    if result.returncode != 0:
        pytest.fail(
            f"Example in '{heading}' failed (exit {result.returncode}):\n"
            f"  stderr: {result.stderr.strip()[:500]}\n"
            f"  First 5 code lines:\n"
            + "\n".join(f"    {l}" for l in code.split("\n")[:5])
        )
