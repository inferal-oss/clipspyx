import glob
import os
import subprocess
import sys

from clipspyx_ffi.build import resolve_clips_source, make_ffibuilder

clips_src = resolve_clips_source(default_branch="clips-70x")

# Apply patches to the resolved CLIPS source.
patches_dir = os.path.join(os.path.dirname(__file__), "..", "patches")
patches_dir = os.path.normpath(patches_dir)
for patch_file in sorted(glob.glob(os.path.join(patches_dir, "*.patch"))):
    subprocess.run(
        ["git", "apply", "--check", os.path.abspath(patch_file)],
        cwd=clips_src, capture_output=True) and subprocess.run(
        ["git", "apply", os.path.abspath(patch_file)],
        cwd=clips_src, capture_output=True)

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
