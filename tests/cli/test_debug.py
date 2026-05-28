"""Unit tests for top-level CLI debug handling."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from ai_rules._shared.runtime import is_debug_enabled, set_debug
from ai_rules.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def reset_debug_flag():
    """Reset process-global debug state around each test."""
    set_debug(False)
    yield
    set_debug(False)


@pytest.mark.unit
def test_debug_flag_sets_runtime_debug_mode():
    """The top-level --debug option enables runtime debug mode."""
    result = runner.invoke(app, ["--debug", "dev", "--help"])

    assert result.exit_code == 0
    assert is_debug_enabled() is True


@pytest.mark.unit
def test_debug_flag_is_shown_in_help():
    """The top-level help lists the debug flag."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "--debug" in result.output
