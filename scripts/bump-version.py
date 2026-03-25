# /// script
# dependencies = []
# ///
"""Bump version across all packages and changelog.

Usage:
    uv run scripts/bump-version.py 0.8.0
    uv run scripts/bump-version.py 0.8.0 --dry-run
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VERSION_FILES = [
    # (path relative to ROOT, pattern)
    ("pyproject.toml", re.compile(r'^(version\s*=\s*")([^"]+)(")', re.MULTILINE)),
    ("clipspyx/__init__.py", re.compile(r"^(__version__\s*=\s*')([^']+)(')", re.MULTILINE)),
    ("backends/ffi/pyproject.toml", re.compile(r'^(version\s*=\s*")([^"]+)(")', re.MULTILINE)),
    ("backends/ffi-64x/pyproject.toml", re.compile(r'^(version\s*=\s*")([^"]+)(")', re.MULTILINE)),
    ("backends/ffi-70x/pyproject.toml", re.compile(r'^(version\s*=\s*")([^"]+)(")', re.MULTILINE)),
]

# Pinned dependency versions (clipspyx-ffi==X.Y.Z, clipspyx-ffi-64x==X.Y.Z, etc.)
# These use replace_all because each file may contain multiple occurrences.
PINNED_DEP_FILES = [
    # (path relative to ROOT, pattern matching "clipspyx-ffi-NNx==VERSION")
    ("pyproject.toml", re.compile(r"(clipspyx-ffi-(?:64|70)x==)(\d+\.\d+\.\d+)")),
    # (path relative to ROOT, pattern matching "clipspyx-ffi==VERSION")
    ("backends/ffi-64x/pyproject.toml", re.compile(r"(clipspyx-ffi==)(\d+\.\d+\.\d+)")),
    ("backends/ffi-70x/pyproject.toml", re.compile(r"(clipspyx-ffi==)(\d+\.\d+\.\d+)")),
]

CHANGELOG = "CHANGELOG.md"
UNRELEASED_RE = re.compile(r"^## \[Unreleased\]\s*\n\n*", re.MULTILINE)
VERSION_HEADING_RE = re.compile(r"^## \[(\d+\.\d+\.\d+)\]", re.MULTILINE)
LINK_SECTION_RE = re.compile(
    r"^\[Unreleased\]:.*(?:\n\[[\d.]+\]:.*)*\n?$", re.MULTILINE)
REPO_URL_RE = re.compile(r"\[Unreleased\]:\s*(https://[^/]+/[^/]+/[^/]+)/compare/")


def bump_version_files(new_version: str, dry_run: bool) -> list[tuple[str, str, str]]:
    """Update version in all tracked files. Returns list of (path, old, new)."""
    changes = []
    for relpath, pattern in VERSION_FILES:
        path = ROOT / relpath
        if not path.exists():
            print(f"  SKIP {relpath} (not found)", file=sys.stderr)
            continue
        text = path.read_text()
        m = pattern.search(text)
        if not m:
            print(f"  SKIP {relpath} (no version match)", file=sys.stderr)
            continue
        old_version = m.group(2)
        if old_version == new_version:
            print(f"  SKIP {relpath} (already {new_version})")
            continue
        new_text = pattern.sub(rf"\g<1>{new_version}\3", text)
        if not dry_run:
            path.write_text(new_text)
        changes.append((relpath, old_version, new_version))
    return changes


def bump_pinned_deps(new_version: str, dry_run: bool) -> list[tuple[str, str, str]]:
    """Update pinned dependency versions (e.g. clipspyx-ffi==X.Y.Z).

    Returns list of (path, old, new) for files that changed.
    """
    changes = []
    for relpath, pattern in PINNED_DEP_FILES:
        path = ROOT / relpath
        if not path.exists():
            print(f"  SKIP {relpath} pins (not found)", file=sys.stderr)
            continue
        text = path.read_text()
        m = pattern.search(text)
        if not m:
            print(f"  SKIP {relpath} pins (no match)", file=sys.stderr)
            continue
        old_version = m.group(2)
        if old_version == new_version:
            print(f"  SKIP {relpath} pins (already {new_version})")
            continue
        new_text = pattern.sub(rf"\g<1>{new_version}", text)
        if not dry_run:
            path.write_text(new_text)
        changes.append((relpath + " (pinned deps)", old_version, new_version))
    return changes


def read_changelog() -> str | None:
    """Read changelog text, or None if missing."""
    path = ROOT / CHANGELOG
    if path.exists():
        return path.read_text()
    return None


def write_changelog(text: str):
    """Write changelog text to disk."""
    (ROOT / CHANGELOG).write_text(text)


def stamp_unreleased(text: str, new_version: str) -> str | None:
    """Stamp [Unreleased] as [new_version] with today's date.

    Returns the modified text, or None if no change was needed.
    """
    if not UNRELEASED_RE.search(text):
        print(f"  SKIP {CHANGELOG} heading (no [Unreleased] section)")
        return None
    if re.search(rf"^## \[{re.escape(new_version)}\]", text, re.MULTILINE):
        print(f"  SKIP {CHANGELOG} heading (v{new_version} already exists)")
        return None
    today = date.today().isoformat()
    replacement = f"## [Unreleased]\n\n## [{new_version}] - {today}\n\n"
    new_text = UNRELEASED_RE.sub(replacement, text)
    return new_text if new_text != text else None


def regenerate_links(text: str) -> tuple[str | None, int]:
    """Regenerate the reference links at the bottom of the changelog.

    Returns (modified_text, link_count) or (None, 0) if unchanged.
    """
    m = REPO_URL_RE.search(text)
    if not m:
        print(f"  SKIP {CHANGELOG} links (no repo URL found)", file=sys.stderr)
        return None, 0
    repo_url = m.group(1)

    versions = VERSION_HEADING_RE.findall(text)
    if not versions:
        return None, 0

    lines = [f"[Unreleased]: {repo_url}/compare/v{versions[0]}...HEAD"]
    for i, version in enumerate(versions):
        if i + 1 < len(versions):
            prev = versions[i + 1]
            lines.append(f"[{version}]: {repo_url}/compare/v{prev}...v{version}")
        else:
            lines.append(f"[{version}]: {repo_url}/commits/v{version}")

    new_links = "\n".join(lines) + "\n"

    if LINK_SECTION_RE.search(text):
        new_text = LINK_SECTION_RE.sub(new_links, text)
    else:
        new_text = text.rstrip() + "\n\n" + new_links

    if new_text == text:
        return None, 0
    return new_text, len(lines)


def main():
    parser = argparse.ArgumentParser(description="Bump version everywhere")
    parser.add_argument("version", help="New version (e.g. 0.8.0)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change")
    args = parser.parse_args()

    version = args.version
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        parser.error(f"Invalid version format: {version!r} (expected X.Y.Z)")

    label = "[dry run] " if args.dry_run else ""
    print(f"{label}Bumping to {version}\n")

    changes = bump_version_files(version, args.dry_run)
    changes += bump_pinned_deps(version, args.dry_run)
    for relpath, old, new in changes:
        print(f"  {relpath}: {old} -> {new}")

    # Changelog: work on in-memory text so stamp + links are consistent
    changelog_text = read_changelog()
    changelog_changed = False
    n_links = 0

    if changelog_text is not None:
        stamped = stamp_unreleased(changelog_text, version)
        if stamped is not None:
            changelog_text = stamped
            changelog_changed = True
            print(f"  {CHANGELOG}: [Unreleased] -> [{version}] - {date.today().isoformat()}")

        linked, n_links = regenerate_links(changelog_text)
        if linked is not None:
            changelog_text = linked
            changelog_changed = True
            print(f"  {CHANGELOG}: regenerated {n_links} release links")

        if changelog_changed and not args.dry_run:
            write_changelog(changelog_text)

    if not changes and not changelog_changed:
        print("\nNothing to do.")
    else:
        total = len(changes) + (1 if changelog_changed else 0)
        print(f"\n{label}Updated {total} file(s).")


if __name__ == "__main__":
    main()
