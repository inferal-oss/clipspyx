#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Sync CLIPS SVN branches into git orphan branches and convert docs to markdown.

Usage:
    uv run scripts/sync-svn.py 64x
    uv run scripts/sync-svn.py 70x
    uv run scripts/sync-svn.py 64x --docs-only   # skip source sync
    uv run scripts/sync-svn.py 64x --source-only  # skip docs conversion

Requires: svn, pandoc

What it does:
1. Exports core/ from SVN branch into orphan branch clips-{branch}
2. Exports documentation/*.docx from SVN branch
3. Converts each .docx to markdown via pandoc, splits by top-level sections
4. Generates AGENTS.md and CLAUDE.md for LLM navigation
5. Writes docs to docs/clips-reference/{branch}/ (does not auto-commit)

Versioning: each run is a full SVN export (snapshot). Re-running overwrites
the orphan branch and docs directory with the latest SVN content.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SVN_BASE = "https://svn.code.sf.net/p/clipsrules/code/branches"
DOCS = ("basic", "advanced", "interfaces")


def run(cmd, **kwargs):
    """Run a command, raising on failure."""
    kwargs.setdefault("check", True)
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    return subprocess.run(cmd, **kwargs)


def git(repo_root, *args, **kwargs):
    """Run git in the repo root."""
    return run(["git", "-C", str(repo_root)] + list(args), **kwargs)


def svn_revision(svn_url):
    """Get the latest SVN revision for a URL."""
    result = run(["svn", "info", "--show-item", "last-changed-revision", svn_url])
    return result.stdout.strip()


def svn_export(svn_path, local_path):
    """Export from SVN, overwriting local_path."""
    if os.path.exists(local_path):
        if os.path.isdir(local_path):
            shutil.rmtree(local_path)
        else:
            os.unlink(local_path)
    run(["svn", "export", svn_path, str(local_path)])


# ---------- Source sync ----------


def sync_source(repo_root, branch_suffix):
    """Export core/ from SVN and commit to orphan branch clips-{suffix}."""
    branch_name = f"clips-{branch_suffix}"
    svn_url = f"{SVN_BASE}/{branch_suffix}/core"

    with tempfile.TemporaryDirectory() as tmpdir:
        rev = svn_revision(f"{SVN_BASE}/{branch_suffix}")
        print(f"SVN revision: r{rev}")

        src_dir = os.path.join(tmpdir, "core")
        print(f"Exporting {svn_url} ...")
        svn_export(svn_url, src_dir)

        # Check if orphan branch exists
        result = git(repo_root, "branch", "--list", branch_name, check=False)
        branch_exists = bool(result.stdout.strip())

        if branch_exists:
            # Update existing branch via worktree
            wt_dir = os.path.join(tmpdir, "worktree")
            git(repo_root, "worktree", "add", wt_dir, branch_name)
            try:
                # Clear old files and copy new
                for f in Path(wt_dir).glob("*"):
                    if f.name == ".git":
                        continue
                    if f.is_dir():
                        shutil.rmtree(f)
                    else:
                        f.unlink()

                for f in Path(src_dir).iterdir():
                    dest = Path(wt_dir) / f.name
                    if f.is_dir():
                        shutil.copytree(f, dest)
                    else:
                        shutil.copy2(f, dest)

                run(["git", "-C", wt_dir, "add", "-A"])
                diff = run(
                    ["git", "-C", wt_dir, "diff", "--cached", "--quiet"],
                    check=False,
                )
                if diff.returncode != 0:
                    run([
                        "git", "-C", wt_dir, "commit",
                        "-m", f"Update CLIPS {branch_suffix} source from SVN r{rev}",
                    ])
                    print(f"Updated branch {branch_name} (r{rev})")
                else:
                    print(f"Branch {branch_name} already up to date (r{rev})")
            finally:
                git(repo_root, "worktree", "remove", wt_dir, check=False)
        else:
            # Create new orphan branch
            wt_dir = os.path.join(tmpdir, "worktree")
            git(repo_root, "worktree", "add", "--orphan", wt_dir,
                "-b", branch_name)
            try:
                for f in Path(src_dir).iterdir():
                    dest = Path(wt_dir) / f.name
                    if f.is_dir():
                        shutil.copytree(f, dest)
                    else:
                        shutil.copy2(f, dest)

                run(["git", "-C", wt_dir, "add", "-A"])
                run([
                    "git", "-C", wt_dir, "commit",
                    "-m", f"Import CLIPS {branch_suffix} source from SVN r{rev}",
                ])
                print(f"Created orphan branch {branch_name} (r{rev})")
            finally:
                git(repo_root, "worktree", "remove", wt_dir, check=False)


# ---------- Documentation ----------


def docx_to_markdown(docx_path, media_dir):
    """Convert a .docx file to markdown using pandoc."""
    result = run([
        "pandoc", str(docx_path),
        "-t", "markdown",
        "--wrap=none",
        f"--extract-media={media_dir}",
    ])
    return result.stdout


def split_sections(markdown_text):
    """Split markdown by top-level `# ` headings.

    Returns list of (slug, title, content) tuples.
    """
    # Match lines starting with '# ' that have actual content (not just '# ')
    heading_pattern = re.compile(r"^(# \S.*)$", re.MULTILINE)

    sections = []
    matches = list(heading_pattern.finditer(markdown_text))

    for i, match in enumerate(matches):
        raw_title = match.group(1)
        # Strip the '# ' prefix to get the title text
        title = raw_title[2:].strip()
        if not title:
            continue

        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
        content = markdown_text[start:end].strip()

        # Generate slug from title
        # "Section 3: Deftemplate Construct" -> "03-deftemplate-construct"
        section_match = re.match(r"Section (\d+):\s*(.+)", title)
        appendix_match = re.match(r"Appendix ([A-Z]):\s*(.+)", title)
        if section_match:
            num = int(section_match.group(1))
            name = section_match.group(2)
            slug = f"{num:02d}-{slugify(name)}"
        elif appendix_match:
            letter = appendix_match.group(1).lower()
            name = appendix_match.group(2)
            slug = f"appendix-{letter}-{slugify(name)}"
        elif title.lower() in ("preface", "license information"):
            slug = f"00-{slugify(title)}"
        elif title.lower() == "index":
            slug = "zz-index"
        else:
            slug = slugify(title)

        sections.append((slug, title, content))

    return sections


def slugify(text):
    """Convert text to a filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = text.strip("-")
    return text


def generate_agents_md(branch_suffix, doc_sections):
    """Generate AGENTS.md mapping sections to files."""
    lines = [
        f"# CLIPS {branch_suffix} Reference Documentation",
        "",
        "Section map for LLM navigation. Load the specific file you need.",
        "",
    ]

    for doc_name, sections in doc_sections.items():
        lines.append(f"## {doc_name.title()} Programming Guide")
        lines.append("")
        lines.append("| File | Section |")
        lines.append("|------|---------|")
        for slug, title, content in sections:
            line_count = content.count("\n")
            lines.append(
                f"| `{doc_name}/{slug}.md` | {title} (~{line_count} lines) |"
            )
        lines.append("")

    return "\n".join(lines) + "\n"


def sync_docs(repo_root, branch_suffix):
    """Export docs from SVN, convert to chunked markdown."""
    docs_dir = repo_root / "docs" / "clips-reference" / branch_suffix

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Export documentation from SVN
        for doc_name in DOCS:
            svn_url = (
                f"{SVN_BASE}/{branch_suffix}/documentation/{doc_name}.docx"
            )
            local_path = tmpdir / f"{doc_name}.docx"
            print(f"Exporting {svn_url} ...")
            try:
                svn_export(svn_url, str(local_path))
            except subprocess.CalledProcessError:
                print(f"  Warning: {doc_name}.docx not found, skipping")
                continue

        # Clean target directory
        if docs_dir.exists():
            shutil.rmtree(docs_dir)
        docs_dir.mkdir(parents=True)

        media_dir = docs_dir / "media"
        media_dir.mkdir()

        doc_sections = {}

        for doc_name in DOCS:
            docx_path = tmpdir / f"{doc_name}.docx"
            if not docx_path.exists():
                continue

            print(f"Converting {doc_name}.docx to markdown (pandoc) ...")
            md = docx_to_markdown(str(docx_path), str(media_dir))

            sections = split_sections(md)
            if not sections:
                out_dir = docs_dir / doc_name
                out_dir.mkdir()
                (out_dir / "00-full.md").write_text(md)
                doc_sections[doc_name] = [("00-full", doc_name.title(), md)]
                continue

            doc_sections[doc_name] = sections

            out_dir = docs_dir / doc_name
            out_dir.mkdir()

            for slug, title, content in sections:
                (out_dir / f"{slug}.md").write_text(content + "\n")

            print(f"  Split into {len(sections)} chunks")

        # Generate AGENTS.md and CLAUDE.md
        agents_md = generate_agents_md(branch_suffix, doc_sections)
        (docs_dir / "AGENTS.md").write_text(agents_md)
        (docs_dir / "CLAUDE.md").write_text("@AGENTS.md\n")

        print(f"Documentation written to {docs_dir}")


def main():
    parser = argparse.ArgumentParser(description="Sync CLIPS SVN to git")
    parser.add_argument("branch", help="SVN branch suffix (e.g., 64x, 70x)")
    parser.add_argument("--docs-only", action="store_true",
                        help="Skip source sync, only convert docs")
    parser.add_argument("--source-only", action="store_true",
                        help="Skip docs conversion")
    args = parser.parse_args()

    # Check prerequisites
    for tool in ("svn", "pandoc"):
        if shutil.which(tool) is None:
            print(f"Error: {tool} not found. Install it first.", file=sys.stderr)
            sys.exit(1)

    # Find repo root
    repo_root = Path(__file__).resolve().parent.parent

    if not args.docs_only:
        sync_source(repo_root, args.branch)

    if not args.source_only:
        sync_docs(repo_root, args.branch)

    print("\nDone. Review changes and commit.")


if __name__ == "__main__":
    main()
