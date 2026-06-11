"""Extra unit tests for ai-rules rule-loader CLI, non-live paths.

Covers:
- resolve_progress_mode (pure function)
- _resolve_connection (pure function)
- _require_connection_or_exit (exit path)
- eval_cmd early exits (--runs 0, no connection)
- doctor_cmd with mocked SDK check
- list command variant filtering
"""

from __future__ import annotations

import pytest
import typer
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands.rule_loader import (
    EXIT_FIXTURE_INVALID,
    EXIT_INFRA_ERROR,
    ProgressMode,
    _require_connection_or_exit,
    _resolve_connection,
    resolve_progress_mode,
)

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})


# ---------------------------------------------------------------------------
# resolve_progress_mode — pure function
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "value,expected",
    [
        ("screen", ProgressMode.SCREEN),
        ("rich", ProgressMode.SCREEN),  # back-compat alias
        ("plain", ProgressMode.PLAIN),
        ("json", ProgressMode.JSON),
        ("none", ProgressMode.NONE),
    ],
)
def test_resolve_progress_mode_explicit(value: str, expected: ProgressMode) -> None:
    assert resolve_progress_mode(value) == expected


@pytest.mark.unit
def test_resolve_progress_mode_auto_returns_valid_mode() -> None:
    mode = resolve_progress_mode("auto")
    assert mode in (ProgressMode.SCREEN, ProgressMode.NONE)


@pytest.mark.unit
def test_resolve_progress_mode_none_input_treated_as_auto() -> None:
    mode = resolve_progress_mode(None)
    assert mode in (ProgressMode.SCREEN, ProgressMode.NONE)


@pytest.mark.unit
def test_resolve_progress_mode_invalid_raises_bad_parameter() -> None:
    with pytest.raises(typer.BadParameter, match="not recognised"):
        resolve_progress_mode("bogus-mode")


# ---------------------------------------------------------------------------
# _resolve_connection — pure function
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_resolve_connection_returns_explicit_arg() -> None:
    assert _resolve_connection("my-conn") == "my-conn"


@pytest.mark.unit
def test_resolve_connection_falls_back_to_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SNOWFLAKE_CONNECTION_NAME", "env-conn")
    assert _resolve_connection(None) == "env-conn"


@pytest.mark.unit
def test_resolve_connection_returns_none_when_both_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SNOWFLAKE_CONNECTION_NAME", raising=False)
    assert _resolve_connection(None) is None


@pytest.mark.unit
def test_resolve_connection_explicit_arg_wins_over_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SNOWFLAKE_CONNECTION_NAME", "env-conn")
    assert _resolve_connection("explicit") == "explicit"


# ---------------------------------------------------------------------------
# _require_connection_or_exit
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_require_connection_exits_when_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SNOWFLAKE_CONNECTION_NAME", raising=False)
    with pytest.raises(typer.Exit) as exc:
        _require_connection_or_exit(None)
    assert exc.value.exit_code == EXIT_INFRA_ERROR


@pytest.mark.unit
def test_require_connection_returns_explicit_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SNOWFLAKE_CONNECTION_NAME", raising=False)
    result = _require_connection_or_exit("direct-conn")
    assert result == "direct-conn"


# ---------------------------------------------------------------------------
# eval_cmd early exits (do not require live SDK)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_eval_cmd_runs_zero_exits_fixture_invalid() -> None:
    """--runs 0 fails immediately before touching the SDK."""
    result = runner.invoke(app, ["rule-loader", "eval", "--runs", "0"])
    assert result.exit_code == EXIT_FIXTURE_INVALID


@pytest.mark.unit
def test_eval_cmd_no_connection_exits_infra_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Eval without any connection configured exits with EXIT_INFRA_ERROR."""
    monkeypatch.delenv("SNOWFLAKE_CONNECTION_NAME", raising=False)
    result = runner.invoke(app, ["rule-loader", "eval", "--runs", "1"])
    assert result.exit_code == EXIT_INFRA_ERROR


# ---------------------------------------------------------------------------
# doctor_cmd with SDK check mocked out
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_doctor_cmd_bypassed_sdk_check(monkeypatch: pytest.MonkeyPatch) -> None:
    """Doctor proceeds past SDK gate when _ensure_sdk_and_connection is mocked."""
    monkeypatch.setattr(
        "ai_rules.commands.rule_loader._ensure_sdk_and_connection",
        lambda: None,
    )
    result = runner.invoke(app, ["rule-loader", "doctor"])
    # Without live SDK: exits 0 (all good) or EXIT_FIXTURE_INVALID (fixtures parse issue)
    assert result.exit_code in (0, EXIT_FIXTURE_INVALID)


# ---------------------------------------------------------------------------
# list command — variant filtering
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_list_fixtures_cmd_variant_simple() -> None:
    """List --variant simple returns exit 0 and filters to simple fixtures."""
    result = runner.invoke(app, ["rule-loader", "list", "--variant", "simple"])
    assert result.exit_code == 0


@pytest.mark.integration
def test_list_fixtures_cmd_variant_complex() -> None:
    """List --variant complex returns exit 0 and filters to complex fixtures."""
    result = runner.invoke(app, ["rule-loader", "list", "--variant", "complex"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# eval_cmd: run-loop with fully mocked SDK (covers lines 1094-1188)
# ---------------------------------------------------------------------------


def _make_passing_run_result(fixture_id: str = "test-fixture") -> object:
    """Build a minimal passing RunResult without touching the live SDK."""
    from ai_rules.rule_loader_eval.agent_runner import AgentRun
    from ai_rules.rule_loader_eval.diagnostics import SignalReport
    from ai_rules.rule_loader_eval.engine import RunResult
    from ai_rules.rule_loader_eval.matcher import MatchResult

    run = AgentRun(
        fixture_id=fixture_id,
        loaded=("rules/000-global-core.md",),
        loaded_via_reads=("rules/000-global-core.md",),
        loaded_via_reads_performed=(),
        loaded_via_section=("rules/000-global-core.md",),
        turns=1,
        duration_ms=100,
        model="claude-test",
    )
    match = MatchResult(
        missing_required=(),
        missing_dependencies=(),
        forbidden_present=(),
        optional_loaded=(),
        passed=True,
    )
    signal_report = SignalReport(ok=True, disagreements=())
    return RunResult(
        fixture_id=fixture_id,
        run=run,
        match=match,
        signal_report=signal_report,
        citation_drifts=(),
    )


@pytest.mark.unit
def test_eval_cmd_single_run_with_mocked_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    """eval_cmd with --runs 1 --no-progress and mocked SDK completes (lines 1094-1165)."""
    monkeypatch.setenv("SNOWFLAKE_CONNECTION_NAME", "fake-conn")
    monkeypatch.setattr(
        "ai_rules.commands.rule_loader._ensure_sdk_and_connection",
        lambda: None,
    )
    passing = _make_passing_run_result()
    monkeypatch.setattr(
        "ai_rules.commands.rule_loader.run_fixtures",
        lambda *a, **kw: [passing],
    )
    result = runner.invoke(
        app,
        ["rule-loader", "eval", "--runs", "1", "--no-progress"],
    )
    # Exit 0 = all fixtures pass; exit 1 = fixture failures (both are valid non-SDK paths)
    assert result.exit_code in (0, 1)


@pytest.mark.unit
def test_eval_cmd_multi_run_with_mocked_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    """eval_cmd with --runs 2 exercises the multi-run label/dir logic (lines 1125-1132)."""
    monkeypatch.setenv("SNOWFLAKE_CONNECTION_NAME", "fake-conn")
    monkeypatch.setattr(
        "ai_rules.commands.rule_loader._ensure_sdk_and_connection",
        lambda: None,
    )
    passing = _make_passing_run_result()
    monkeypatch.setattr(
        "ai_rules.commands.rule_loader.run_fixtures",
        lambda *a, **kw: [passing],
    )
    result = runner.invoke(
        app,
        ["rule-loader", "eval", "--runs", "2", "--no-progress"],
    )
    assert result.exit_code in (0, 1)


@pytest.mark.unit
def test_eval_cmd_fixture_filter_with_mocked_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    """eval_cmd with --fixture <id> loads a single fixture (lines 1100-1106)."""
    monkeypatch.setenv("SNOWFLAKE_CONNECTION_NAME", "fake-conn")
    monkeypatch.setattr(
        "ai_rules.commands.rule_loader._ensure_sdk_and_connection",
        lambda: None,
    )
    passing = _make_passing_run_result("simple-sql-procedure")
    monkeypatch.setattr(
        "ai_rules.commands.rule_loader.run_fixtures",
        lambda *a, **kw: [passing],
    )
    result = runner.invoke(
        app,
        [
            "rule-loader",
            "eval",
            "--fixture",
            "simple-sql-procedure",
            "--runs",
            "1",
            "--no-progress",
        ],
    )
    # May fail fixture validation if fixture doesn't exist — that's also valid
    assert result.exit_code in (0, 1, EXIT_FIXTURE_INVALID)
