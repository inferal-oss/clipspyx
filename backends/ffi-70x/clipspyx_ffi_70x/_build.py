import os
import sys

from clipspyx_ffi.build import resolve_clips_source, make_ffibuilder

clips_src = resolve_clips_source(default_branch="clips-70x")

# Link so setuptools sees sources inside the project directory.
# Symlinks require developer mode on Windows, so use a copy instead.
local_link = os.path.join(os.path.dirname(__file__), "..", ".clips-source")
local_link = os.path.normpath(local_link)
if not os.path.exists(local_link):
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
