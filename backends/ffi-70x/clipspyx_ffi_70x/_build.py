import os
import re
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
# This patcher inserts the three missing initializations after the
# theHeader->theModule = ModulePointer(...) line, but only inside
# UpdateDefmoduleItemHeaderHM (NOT the similar UpdateDefmoduleItemHeader).
# ---------------------------------------------------------------------------

PATCH_LINES = (
    "   theHeader->itemCount = 0;\n"
    "   theHeader->hashTableSize = 0;\n"
    "   theHeader->hashTable = NULL;\n"
)

SENTINEL = "theHeader->itemCount = 0;"


def patch_modulbin(clips_source_dir: str) -> None:
    """Patch modulbin.c to initialize hashmap fields in UpdateDefmoduleItemHeaderHM."""
    path = os.path.join(clips_source_dir, "modulbin.c")
    with open(path, "r") as f:
        text = f.read()

    # Already patched: the sentinel line is present.
    if SENTINEL in text:
        print(f"  modulbin.c: already patched (skipping)")
        return

    # Locate the UpdateDefmoduleItemHeaderHM function and, within it, the
    # "theHeader->theModule = ModulePointer(...)" assignment.  We insert
    # our three initialization lines immediately after that assignment.
    #
    # We match the HM variant specifically by looking for the function
    # signature with defmoduleItemHeaderHM in it.
    pattern = re.compile(
        r"(void\s+UpdateDefmoduleItemHeaderHM\b"  # function name
        r".*?"                                      # params, opening brace, locals
        r"([ \t]*theHeader->theModule\s*=\s*ModulePointer\([^)]*\)\s*;[^\n]*\n))",  # assignment line
        re.DOTALL,
    )

    m = pattern.search(text)
    assert m, (
        "Cannot find patch site in modulbin.c: expected "
        "'UpdateDefmoduleItemHeaderHM' containing "
        "'theHeader->theModule = ModulePointer(...)'"
    )

    insert_pos = m.end()
    patched = text[:insert_pos] + PATCH_LINES + text[insert_pos:]

    with open(path, "w") as f:
        f.write(patched)

    print(f"  modulbin.c: patched UpdateDefmoduleItemHeaderHM (hashmap init)")


patch_modulbin(clips_src)

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
