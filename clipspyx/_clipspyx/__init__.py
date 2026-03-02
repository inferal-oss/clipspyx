"""Redirect imports to the appropriate CLIPS FFI backend."""
try:
    from clipspyx_ffi_70x._clipspyx import lib, ffi  # noqa: F401
except ImportError:
    try:
        from clipspyx_ffi_64x._clipspyx import lib, ffi  # noqa: F401
    except ImportError:
        raise ImportError(
            "No CLIPS FFI backend found. "
            "Install clipspyx[64x] or clipspyx[70x]."
        ) from None
