"""Unit tests for ai_rules._shared.runtime."""

from __future__ import annotations

import pytest

from ai_rules._shared.runtime import is_debug_enabled, set_debug


@pytest.fixture(autouse=True)
def reset_debug_flag():
    """Reset process-global debug state around each test."""
    set_debug(False)
    yield
    set_debug(False)


@pytest.mark.unit
def test_debug_flag_defaults_false():
    """Debug mode is disabled by default."""
    assert is_debug_enabled() is False


@pytest.mark.unit
def test_set_debug_updates_debug_flag():
    """set_debug controls the process-wide debug flag."""
    set_debug(True)
    assert is_debug_enabled() is True
    set_debug(False)
    assert is_debug_enabled() is False
