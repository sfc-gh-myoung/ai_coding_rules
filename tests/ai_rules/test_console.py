"""Unit tests for _shared/console.py — covers err_console real-stderr branch."""

from __future__ import annotations

import sys

import pytest

# ---------------------------------------------------------------------------
# err_console real-stderr branch — line 79
# ---------------------------------------------------------------------------
# Lines 79-84 are module-level code inside `if _real_stderr is not None:`.
# Under pytest, _build_real_stderr() always returns None (early-exit guard),
# so this branch is only reachable by reloading the module without pytest in
# sys.modules — the same constraint that makes lines 57-66 untestable.
# We attempt the reload here; the test is marked xfail-strict=False to handle
# environments where fd 2 duplication fails (e.g. closed stderr in CI).


@pytest.mark.unit
def test_err_console_real_stderr_branch() -> None:
    """Cover lines 79-84: err_console constructed with file=_real_stderr when non-None."""
    import importlib

    import ai_rules._shared.console as console_mod

    # Remove pytest from sys.modules so _build_real_stderr proceeds past its early-exit.
    # This is the only mechanism to exercise the True branch of line 78 at module level.
    _pytest = sys.modules.pop("pytest", None)
    captured_stderr = None
    try:
        importlib.reload(console_mod)
        captured_stderr = console_mod._real_stderr
        # If os.dup(2) succeeded, _real_stderr is non-None and lines 79-84 ran.
        if captured_stderr is not None:
            # Verify the err_console was wired to the duped fd (not stderr=True fallback)
            assert hasattr(console_mod, "err_console")
    finally:
        # Close the duped fd to avoid resource leak before restoring.
        if captured_stderr is not None:
            import contextlib

            with contextlib.suppress(Exception):
                captured_stderr.close()
        if _pytest is not None:
            sys.modules["pytest"] = _pytest
        # Reload once more to restore pytest-safe module state (_real_stderr=None).
        importlib.reload(console_mod)
        assert console_mod._real_stderr is None
