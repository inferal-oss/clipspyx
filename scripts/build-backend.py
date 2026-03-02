#!/usr/bin/env python3
"""Build backend package wheels for distribution.

Builds the three-package chain:
1. clipspyx-ffi (pure Python, shared build infrastructure)
2. clipspyx-ffi-{variant} (CFFI extension for the requested CLIPS version)

The clipspyx-ffi wheel is built first and made available via UV_FIND_LINKS
so the variant package can resolve it as a build dependency.

Usage:
    uv run scripts/build-backend.py 64x   # builds clipspyx-ffi + clipspyx-ffi-64x
    uv run scripts/build-backend.py 70x   # builds clipspyx-ffi + clipspyx-ffi-70x
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

BACKENDS = {
    "64x": {
        "dir": REPO_ROOT / "backends" / "ffi-64x",
        "pkg": "clipspyx_ffi_64x",
        "branch": "clips-64x",
    },
    "70x": {
        "dir": REPO_ROOT / "backends" / "ffi-70x",
        "pkg": "clipspyx_ffi_70x",
        "branch": "clips-70x",
    },
}

FFI_DIR = REPO_ROOT / "backends" / "ffi"


def build_ffi_wheel(dist_dir: Path) -> None:
    """Build the clipspyx-ffi wheel (pure Python)."""
    print("Building clipspyx-ffi...")
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(dist_dir)],
        cwd=FFI_DIR,
        check=True,
    )
    wheels = sorted(dist_dir.glob("clipspyx_ffi-*.whl"))
    if wheels:
        print(f"  Built: {wheels[-1].name}")
    else:
        print("  Warning: no clipspyx-ffi wheel found in dist/")
        sys.exit(1)


def build_backend(variant: str) -> None:
    if variant not in BACKENDS:
        print(f"Unknown variant: {variant!r}. Choose from: {', '.join(BACKENDS)}")
        sys.exit(1)

    info = BACKENDS[variant]
    backend_dir = info["dir"]
    dist_dir = REPO_ROOT / "dist"
    dist_dir.mkdir(exist_ok=True)

    # Step 1: Build clipspyx-ffi wheel
    build_ffi_wheel(dist_dir)

    # Step 2: Pre-resolve CLIPS source from the main repo
    sys.path.insert(0, str(FFI_DIR))
    from clipspyx_ffi.build import resolve_clips_source
    clips_src = resolve_clips_source(default_branch=info["branch"])
    print(f"  CLIPS source: {clips_src}")

    # Step 3: Build the variant wheel with CLIPS_SOURCE_DIR set and
    # UV_FIND_LINKS pointing to dist/ so it picks up clipspyx-ffi
    print(f"\nBuilding {info['pkg']}...")
    env = os.environ.copy()
    env["CLIPS_SOURCE_DIR"] = clips_src
    env["UV_FIND_LINKS"] = str(dist_dir)
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(dist_dir)],
        cwd=backend_dir,
        check=True,
        env=env,
    )

    wheels = sorted(dist_dir.glob(f"{info['pkg']}-*.whl"))
    if wheels:
        print(f"\nBuilt: {wheels[-1].name}")
    else:
        print("\nWarning: no wheel found in dist/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build clipspyx backend wheels")
    parser.add_argument("variant", choices=BACKENDS.keys(),
                        help="Backend variant to build (64x or 70x)")
    args = parser.parse_args()
    build_backend(args.variant)
