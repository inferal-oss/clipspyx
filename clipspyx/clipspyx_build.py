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

import os
import sys
import glob
import subprocess

from cffi import FFI


def resolve_clips_source():
    """Resolve CLIPS C source directory.

    Priority:
    1. CLIPS_SOURCE_DIR env var - arbitrary checkout path
    2. CLIPS_BRANCH env var - checkout that orphan branch
    3. Default - auto-checkout clips-64x branch
    """
    # Priority 1: explicit source directory
    src_dir = os.environ.get("CLIPS_SOURCE_DIR")
    if src_dir:
        src_dir = os.path.abspath(src_dir)
        if not os.path.isdir(src_dir):
            raise FileNotFoundError(
                f"CLIPS_SOURCE_DIR={src_dir} does not exist")
        return src_dir

    # Priority 2/3: checkout from local orphan branch
    branch = os.environ.get("CLIPS_BRANCH", "clips-64x")
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    checkout_dir = os.path.join(repo_root, ".clips-source")

    if os.path.isdir(checkout_dir):
        # Check if it's the right branch, auto-switch if not
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, check=True,
                cwd=checkout_dir)
            current = result.stdout.strip()
            if current == branch:
                return checkout_dir
            print(f"Switching CLIPS source: {current} -> {branch}")
            subprocess.run(
                ["git", "worktree", "remove", checkout_dir],
                check=True, capture_output=True, text=True,
                cwd=repo_root)
        except subprocess.CalledProcessError:
            import shutil
            shutil.rmtree(checkout_dir, ignore_errors=True)
        # Clean up stale worktree references
        subprocess.run(
            ["git", "worktree", "prune"],
            capture_output=True, text=True, cwd=repo_root)

    # Attempt git worktree checkout
    subprocess.run(
        ["git", "worktree", "prune"],
        capture_output=True, text=True, cwd=repo_root)
    try:
        subprocess.run(
            ["git", "worktree", "add", checkout_dir, branch],
            check=True, capture_output=True, text=True,
            cwd=repo_root)
    except subprocess.CalledProcessError as e:
        # Check if branch exists
        result = subprocess.run(
            ["git", "branch", "--list", branch],
            capture_output=True, text=True, cwd=repo_root)
        if not result.stdout.strip():
            print(
                f"Error: Branch '{branch}' not found.\n"
                f"Run: ./scripts/sync-svn.sh 64x\n"
                f"Or set CLIPS_SOURCE_DIR to point to CLIPS source.",
                file=sys.stderr)
        raise FileNotFoundError(
            f"Cannot checkout CLIPS source from branch '{branch}': "
            f"{e.stderr.strip()}")

    return checkout_dir


# Resolve CLIPS source directory
clips_src = resolve_clips_source()

# setuptools requires relative paths - make relative to repo root
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
clips_src_rel = os.path.relpath(clips_src, repo_root)

# Collect all .c files from CLIPS source (as relative paths)
clips_c_files = sorted(glob.glob(os.path.join(clips_src_rel, "*.c")))
if not clips_c_files:
    raise FileNotFoundError(
        f"No .c files found in {clips_src}. "
        f"Is this a valid CLIPS source directory?")

# Detect CLIPS major version from constant.h
clips_major = 6
constant_h = os.path.join(clips_src, "constant.h")
if os.path.exists(constant_h):
    import re as _re
    with open(constant_h) as f:
        m = _re.search(r'#define\s+VERSION_STRING\s+"(\d+)', f.read())
        if m:
            clips_major = int(m.group(1))

ffibuilder = FFI()

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

# Read CFFI definitions from the .cdef file bundled in the package
cdef_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "clips.cdef")
with open(cdef_path) as cdef_file:
    CLIPS_CDEF = cdef_file.read()

# Compile CLIPS source directly into the CFFI extension
ffibuilder.set_source(
    "clipspyx._clipspyx",
    CLIPS_SOURCE,
    sources=clips_c_files,
    include_dirs=[clips_src_rel],
    extra_compile_args=["-std=c99", "-O2", "-fno-strict-aliasing",
                        f"-DCLIPS_MAJOR={clips_major}"],
    extra_link_args=["-lm"])

ffibuilder.cdef(CLIPS_CDEF)

if clips_major >= 7:
    cdef_70x_path = os.path.join(os.path.dirname(cdef_path), "clips-70x.cdef")
    with open(cdef_70x_path) as cdef_70x_file:
        ffibuilder.cdef(cdef_70x_file.read())

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
