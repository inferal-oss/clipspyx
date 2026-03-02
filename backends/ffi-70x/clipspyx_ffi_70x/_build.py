import glob
import os
import re
import subprocess
import sys

from clipspyx_ffi.build import resolve_clips_source, make_ffibuilder

clips_src = resolve_clips_source(default_branch="clips-70x")


# ---------------------------------------------------------------------------
# Patch modulbin.c: initialize hashmap fields in UpdateDefmoduleItemHeaderHM
#
# CLIPS 7.0x Bload() crashes with SEGV because UpdateDefmoduleItemHeaderHM
# does not initialize itemCount, hashTableSize, and hashTable fields of the
# defmoduleItemHeaderHM struct.  Since genalloc does not zero memory, these
# fields contain garbage.  When AssignHashMapSize is called it sees non-zero
# hashTableSize and dereferences the garbage hashTable pointer.
#
# See patches/bload-init-hashmap.patch for the canonical diff.
# We try git apply first; if that fails, fall back to a Python-based
# patcher.  The .gitattributes file forces *.patch to LF line endings,
# which resolved the original Windows failure ("corrupt patch at line 14"
# caused by CRLF conversion).  The fallback remains as insurance for
# environments where .gitattributes is not honored (e.g. source archives).
# ---------------------------------------------------------------------------

_SENTINEL = "theHeader->itemCount = 0;"

_PATCH_LINES = (
    "   theHeader->itemCount = 0;\n"
    "   theHeader->hashTableSize = 0;\n"
    "   theHeader->hashTable = NULL;\n"
)


def _already_patched(clips_source_dir):
    path = os.path.join(clips_source_dir, "modulbin.c")
    with open(path, "r") as f:
        return _SENTINEL in f.read()


def _try_git_apply(clips_source_dir):
    """Try to apply patches via git apply. Returns True on success."""
    patches_dir = os.path.join(os.path.dirname(__file__), "..", "patches")
    patches_dir = os.path.normpath(patches_dir)
    patch_files = sorted(glob.glob(os.path.join(patches_dir, "*.patch")))
    if not patch_files:
        print("  git apply: no patch files found")
        return False
    for patch_file in patch_files:
        name = os.path.basename(patch_file)
        result = subprocess.run(
            ["git", "apply", os.path.abspath(patch_file)],
            cwd=clips_source_dir, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  git apply {name}: failed (rc={result.returncode})")
            if result.stderr:
                for line in result.stderr.strip().splitlines():
                    print(f"    {line}")
            return False
        print(f"  git apply {name}: ok")
    return True


def _python_fallback(clips_source_dir):
    """Patch modulbin.c directly via string manipulation."""
    path = os.path.join(clips_source_dir, "modulbin.c")
    with open(path, "r") as f:
        text = f.read()

    pattern = re.compile(
        r"(void\s+UpdateDefmoduleItemHeaderHM\b"
        r".*?"
        r"theHeader->theModule\s*=\s*ModulePointer\([^)]*\)\s*;[^\n]*\n)",
        re.DOTALL,
    )
    m = pattern.search(text)
    assert m, "Cannot find UpdateDefmoduleItemHeaderHM patch site in modulbin.c"

    patched = text[:m.end()] + _PATCH_LINES + text[m.end():]
    with open(path, "w") as f:
        f.write(patched)


if _already_patched(clips_src):
    print("  modulbin.c: already patched (skipping)")
elif _try_git_apply(clips_src):
    print("  modulbin.c: patched via git apply")
else:
    print("  modulbin.c: git apply failed, trying Python fallback...")
    _python_fallback(clips_src)
    print("  modulbin.c: patched via Python fallback")

assert _already_patched(clips_src), "modulbin.c patch failed to apply"

# Link so setuptools sees sources inside the project directory.
# Symlinks require developer mode on Windows, so use a copy instead.
local_link = os.path.join(os.path.dirname(__file__), "..", ".clips-source")
local_link = os.path.normpath(local_link)
if not os.path.lexists(local_link):
    if sys.platform == "win32":
        import shutil
        shutil.copytree(clips_src, local_link)
    else:
        os.symlink(clips_src, local_link)
os.environ["CLIPS_SOURCE_DIR"] = os.path.abspath(local_link)

ffibuilder = make_ffibuilder(
    module_name="clipspyx_ffi_70x._clipspyx",
    default_branch="clips-70x",
)
