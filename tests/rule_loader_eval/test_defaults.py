"""Default-invariant tests for rule-loader live-agent defaults.

Verifies that DEFAULT_MAX_TURNS=25 and DEFAULT_EFFORT="medium" are consistently
exposed across the Python constants module, library function signatures, and
CLI help output.

Future drift at any of these sites fails these tests immediately.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.rule_loader_eval.defaults import DEFAULT_EFFORT, DEFAULT_MAX_TURNS

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})


@pytest.fixture(scope="module")
def project_root() -> Path:
    """Return the repo root."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("project root not found")


# ---------------------------------------------------------------------------
# 1. Python constants
# ---------------------------------------------------------------------------


def test_default_max_turns_value() -> None:
    """DEFAULT_MAX_TURNS must equal 25."""
    assert DEFAULT_MAX_TURNS == 25


def test_default_effort_value() -> None:
    """DEFAULT_EFFORT must equal 'medium'."""
    assert DEFAULT_EFFORT == "medium"


# ---------------------------------------------------------------------------
# 2. Library function signatures
# ---------------------------------------------------------------------------


def _default_for(func: object, param: str) -> object:
    sig = inspect.signature(func)  # type: ignore[arg-type]
    return sig.parameters[param].default


def test_run_fixture_defaults() -> None:
    """run_fixture exposes max_turns=25, effort='medium' by default."""
    from ai_rules.rule_loader_eval.engine import run_fixture

    assert _default_for(run_fixture, "max_turns") == 25
    assert _default_for(run_fixture, "effort") == "medium"


def test_run_fixtures_defaults() -> None:
    """run_fixtures exposes max_turns=25, effort='medium' by default."""
    from ai_rules.rule_loader_eval.engine import run_fixtures

    assert _default_for(run_fixtures, "max_turns") == 25
    assert _default_for(run_fixtures, "effort") == "medium"


def test_run_live_defaults() -> None:
    """run_live exposes max_turns=25, effort='medium' by default."""
    from ai_rules.rule_loader_eval.agent_runner import run_live

    assert _default_for(run_live, "max_turns") == 25
    assert _default_for(run_live, "effort") == "medium"


def test_run_batch_defaults() -> None:
    """run_batch exposes max_turns=25, effort='medium' by default."""
    from ai_rules.rule_loader_eval.batch import run_batch

    assert _default_for(run_batch, "max_turns") == 25
    assert _default_for(run_batch, "effort") == "medium"


def test_run_batch_async_defaults() -> None:
    """run_batch_async exposes max_turns=25, effort='medium' by default."""
    from ai_rules.rule_loader_eval.batch import run_batch_async

    assert _default_for(run_batch_async, "max_turns") == 25
    assert _default_for(run_batch_async, "effort") == "medium"


# ---------------------------------------------------------------------------
# 3. CLI help output
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("command", ["eval", "create", "refresh", "refresh-all"])
def test_cli_help_defaults(command: str) -> None:
    """All four CLI commands show max_turns=25 and effort=medium in --help output."""
    result = runner.invoke(app, ["rule-loader", command, "--help"])
    assert result.exit_code == 0, result.output
    assert "25" in result.output, f"{command} --help missing max_turns default 25"
    assert "medium" in result.output, f"{command} --help missing effort default 'medium'"
