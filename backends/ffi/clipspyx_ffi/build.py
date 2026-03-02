# Copyright (c) 2016-2025, Matteo Cafasso
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import glob
import hashlib
import os
import re
import subprocess
import sys


def _subdir_for_branch(branch: str) -> str:
    """Return subdirectory name for a CLIPS branch.

    Known branches like clips-64x map to '64x'; arbitrary names
    are hashed to an 8-char hex prefix.
    """
    prefix = "clips-"
    if branch.startswith(prefix):
        return branch[len(prefix):]
    return hashlib.sha256(branch.encode()).hexdigest()[:8]


def _find_repo_root() -> str | None:
    """Find the git repository root using git rev-parse.

    Returns None if not inside a git repository.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def resolve_clips_source(default_branch=None):
    """Resolve CLIPS C source directory.

    Priority:
    1. CLIPS_SOURCE_DIR env var - arbitrary checkout path
    2. CLIPS_BRANCH env var - checkout that orphan branch
    3. default_branch argument
    4. Default - auto-checkout clips-64x branch

    Each branch gets its own subdirectory under .clips-source/<suffix>/
    so multiple source checkouts coexist without switching.
    """
    # Priority 1: explicit source directory
    src_dir = os.environ.get("CLIPS_SOURCE_DIR")
    if src_dir:
        src_dir = os.path.abspath(src_dir)
        if not os.path.isdir(src_dir):
            raise FileNotFoundError(
                f"CLIPS_SOURCE_DIR={src_dir} does not exist")
        return src_dir

    # Priority 2/3/4: checkout from local orphan branch
    branch = os.environ.get("CLIPS_BRANCH", default_branch or "clips-64x")
    repo_root = _find_repo_root()
    if repo_root is None:
        raise FileNotFoundError(
            "Not inside a git repository. "
            "Set CLIPS_SOURCE_DIR to point to CLIPS source.")

    base_dir = os.path.join(repo_root, ".clips-source")
    subdir = _subdir_for_branch(branch)
    checkout_dir = os.path.join(base_dir, subdir)

    # Migration: if .clips-source is an old single-worktree layout, remove it
    git_file = os.path.join(base_dir, ".git")
    if os.path.isfile(git_file):
        import shutil
        subprocess.run(
            ["git", "worktree", "remove", base_dir],
            capture_output=True, text=True, cwd=repo_root)
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir, ignore_errors=True)
        subprocess.run(
            ["git", "worktree", "prune"],
            capture_output=True, text=True, cwd=repo_root)

    # Already checked out: return immediately
    if os.path.isdir(checkout_dir):
        return checkout_dir

    # Create parent directory and prune stale worktrees
    os.makedirs(base_dir, exist_ok=True)
    subprocess.run(
        ["git", "worktree", "prune"],
        capture_output=True, text=True, cwd=repo_root)

    # Attempt git worktree checkout
    try:
        subprocess.run(
            ["git", "worktree", "add", checkout_dir, branch],
            check=True, capture_output=True, text=True,
            cwd=repo_root)
    except subprocess.CalledProcessError as e:
        # Check if branch exists locally
        result = subprocess.run(
            ["git", "branch", "--list", branch],
            capture_output=True, text=True, cwd=repo_root)
        if not result.stdout.strip():
            # Branch missing locally — try fetching from origin
            # (common when installed as a git dependency: uv only clones the default branch)
            print(f"  Branch '{branch}' not found locally, fetching from origin...")
            fetch = subprocess.run(
                ["git", "fetch", "origin", f"{branch}:{branch}"],
                capture_output=True, text=True, cwd=repo_root)
            if fetch.returncode == 0:
                print(f"  Fetched '{branch}' from origin")
                try:
                    subprocess.run(
                        ["git", "worktree", "add", checkout_dir, branch],
                        check=True, capture_output=True, text=True,
                        cwd=repo_root)
                    return checkout_dir
                except subprocess.CalledProcessError as e2:
                    raise FileNotFoundError(
                        f"Cannot checkout CLIPS source from branch '{branch}': "
                        f"{e2.stderr.strip()}")
            else:
                print(
                    f"Error: Branch '{branch}' not found locally or on origin.\n"
                    f"Run: ./scripts/sync-svn.sh 64x\n"
                    f"Or set CLIPS_SOURCE_DIR to point to CLIPS source.",
                    file=sys.stderr)
        raise FileNotFoundError(
            f"Cannot checkout CLIPS source from branch '{branch}': "
            f"{e.stderr.strip()}")

    return checkout_dir


def _detect_clips_major(clips_src: str) -> int:
    """Detect CLIPS major version from constant.h in the source directory."""
    constant_h = os.path.join(clips_src, "constant.h")
    if os.path.exists(constant_h):
        with open(constant_h) as f:
            m = re.search(r'#define\s+VERSION_STRING\s+"(\d+)', f.read())
            if m:
                return int(m.group(1))
    return 6


CLIPS_SOURCE = """
#include <clips.h>

const int CLIPSPYX_CLIPS_MAJOR = CLIPS_MAJOR;

/* CLIPS 7.0 renamed DeftemplateGet/SetWatch -> DeftemplateGet/SetWatchFacts. */
#if CLIPS_MAJOR >= 7
#define DeftemplateGetWatch DeftemplateGetWatchFacts
#define DeftemplateSetWatch DeftemplateSetWatchFacts

#include "tabledef.h"
#include "tablebsc.h"
#endif

/* Return true if the template is implied. */
bool ImpliedDeftemplate(Deftemplate *template)
{
    return template->implied;
}

#if CLIPS_MAJOR >= 7
/* Return the row count for a deftable. */
unsigned long DeftableRowCount(Deftable *table)
{
    return table->rowCount;
}

/* Return the column count for a deftable. */
unsigned long DeftableColumnCount(Deftable *table)
{
    return table->columnCount;
}
#endif

/* User Defined Functions support. */
static void python_function(Environment *env, UDFContext *udfc, UDFValue *out);

int DefinePythonFunction(Environment *environment)
{
    return AddUDF(
        environment, "python-function",
        NULL, UNBOUNDED, UNBOUNDED, NULL,
        python_function, "python_function", NULL);
}
"""


def make_ffibuilder(module_name="clipspyx._clipspyx",
                    default_branch=None,
                    cdef_dir=None):
    """Create and configure a CFFI FFIBuilder for CLIPS.

    Args:
        module_name: Dotted module name for the compiled extension
            (e.g. "clipspyx_ffi_64x._clipspyx").
        default_branch: Default CLIPS source branch to use if neither
            CLIPS_SOURCE_DIR nor CLIPS_BRANCH is set.
        cdef_dir: Directory containing .cdef files. Defaults to this
            package's own directory.

    Returns:
        Configured cffi.FFI instance ready for compilation.
    """
    from cffi import FFI

    clips_src = resolve_clips_source(default_branch)

    # setuptools requires relative paths; compute relative to CWD
    # (which is the package directory during build)
    clips_src_rel = os.path.relpath(clips_src)

    # Collect all .c files from CLIPS source (as relative paths)
    clips_c_files = sorted(glob.glob(os.path.join(clips_src_rel, "*.c")))
    if not clips_c_files:
        raise FileNotFoundError(
            f"No .c files found in {clips_src}. "
            f"Is this a valid CLIPS source directory?")

    clips_major = _detect_clips_major(clips_src)

    ffibuilder = FFI()

    if sys.platform == "win32":
        extra_compile_args = [f"/DCLIPS_MAJOR={clips_major}"]
        extra_link_args = []
    else:
        extra_compile_args = ["-std=c99", "-O2", "-fno-strict-aliasing",
                              f"-DCLIPS_MAJOR={clips_major}"]
        extra_link_args = ["-lm"]

    ffibuilder.set_source(
        module_name,
        CLIPS_SOURCE,
        sources=clips_c_files,
        include_dirs=[clips_src_rel],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args)

    # Read CFFI definitions from the .cdef files
    if cdef_dir is None:
        cdef_dir = os.path.dirname(os.path.abspath(__file__))

    cdef_path = os.path.join(cdef_dir, "clips.cdef")
    with open(cdef_path) as cdef_file:
        ffibuilder.cdef(cdef_file.read())

    if clips_major >= 7:
        cdef_70x_path = os.path.join(cdef_dir, "clips-70x.cdef")
        with open(cdef_70x_path) as cdef_70x_file:
            ffibuilder.cdef(cdef_70x_file.read())

    return ffibuilder
