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
    # (path relative to ROOT, pattern, replacement template)
    ("pyproject.toml", re.compile(r'^(version\s*=\s*")([^"]+)(")', re.MULTILINE)),
    ("clipspyx/__init__.py", re.compile(r"^(__version__\s*=\s*')([^']+)(')", re.MULTILINE)),
    ("backends/ffi/pyproject.toml", re.compile(r'^(version\s*=\s*")([^"]+)(")', re.MULTILINE)),
    ("backends/ffi-64x/pyproject.toml", re.compile(r'^(version\s*=\s*")([^"]+)(")', re.MULTILINE)),
    ("backends/ffi-70x/pyproject.toml", re.compile(r'^(version\s*=\s*")([^"]+)(")', re.MULTILINE)),
]

CHANGELOG = "CHANGELOG.md"
UNRELEASED_RE = re.compile(r"^(## \[Unreleased\])\s*$", re.MULTILINE)


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


def bump_changelog(new_version: str, dry_run: bool) -> bool:
    """Stamp [Unreleased] as [new_version] with today's date.

    Inserts a fresh [Unreleased] heading above the new version.
    Returns True if the changelog was modified.
    """
    path = ROOT / CHANGELOG
    if not path.exists():
        print(f"  SKIP {CHANGELOG} (not found)", file=sys.stderr)
        return False
    text = path.read_text()
    if not UNRELEASED_RE.search(text):
        print(f"  SKIP {CHANGELOG} (no [Unreleased] section)")
        return False
    today = date.today().isoformat()
    replacement = f"## [Unreleased]\n\n## [{new_version}] - {today}"
    new_text = UNRELEASED_RE.sub(replacement, text)
    if new_text == text:
        return False
    if not dry_run:
        path.write_text(new_text)
    return True


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
    for relpath, old, new in changes:
        print(f"  {relpath}: {old} -> {new}")

    if bump_changelog(version, args.dry_run):
        print(f"  {CHANGELOG}: [Unreleased] -> [{version}] - {date.today().isoformat()}")

    if not changes:
        print("\nNo version files changed.")
    else:
        print(f"\n{label}Updated {len(changes)} file(s).")


if __name__ == "__main__":
    main()
