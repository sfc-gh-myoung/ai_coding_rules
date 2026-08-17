"""Unit tests for the --without-plugin eval mode enhancements.

Covers:
- build_prompt_without_plugin() output shape and isolation
- RunResult.result classification for discovery-budget-exhausted
- _run_single_eval with without_plugin=True (patched, no live SDK)
- manifest.json metadata for mode and effective_max_turns
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_rules.rule_loader_eval.agent_runner import AgentRun
from ai_rules.rule_loader_eval.engine import RunResult, _is_missing_gate3_violation
from ai_rules.rule_loader_eval.fixtures import Fixture, TriggerEvidence

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_GATE3_VIOLATION = "missing Rules Loaded (Gate 3 or **Rules Loaded**) section"


def _make_fixture(fixture_id: str = "fx") -> Fixture:
    return Fixture(
        path=Path(f"fixtures/{fixture_id}.yaml"),
        schema_version=1,
        updated="2025-01-01",
        id=fixture_id,
        description="",
        variant="",
        prompt=f"Test prompt for {fixture_id}",
        required=("rules/999-test-core.md",),
        dependencies=(),
        forbidden=(),
        optional=(),
        trigger_evidence=TriggerEvidence(),
    )


def _make_run(
    fixture_id: str = "fx",
    *,
    loaded: tuple[str, ...] = ("rules/999-test-core.md",),
    turns: int = 3,
    output_violations: tuple[str, ...] = (),
    manifest_paths: frozenset[str] | None = None,
) -> AgentRun:
    mp = manifest_paths if manifest_paths is not None else frozenset(loaded)
    return AgentRun(
        fixture_id=fixture_id,
        loaded=loaded,
        loaded_via_reads=loaded,
        loaded_via_reads_performed=(),
        loaded_via_section=loaded,
        disagreements=(),
        turns=turns,
        duration_ms=10,
        model="claude-test",
        notes=(),
        output_violations=output_violations,
        manifest_paths=mp,
    )


def _make_run_result(
    *,
    mode: str = "plugin",
    turns: int = 3,
    max_turns_used: int = 5,
    output_violations: tuple[str, ...] = (),
    loaded: tuple[str, ...] = ("rules/999-test-core.md",),
    manifest_paths: frozenset[str] | None = None,
) -> RunResult:
    from ai_rules.rule_loader_eval.diagnostics import SignalReport
    from ai_rules.rule_loader_eval.matcher import MatchResult

    run = _make_run(
        turns=turns,
        output_violations=output_violations,
        loaded=loaded,
        manifest_paths=manifest_paths if manifest_paths is not None else frozenset(loaded),
    )
    match = MatchResult(
        missing_required=(),
        missing_dependencies=(),
        forbidden_present=(),
        optional_loaded=(),
        extras=(),
        passed=True,
        warnings=(),
    )
    return RunResult(
        fixture_id="fx",
        run=run,
        match=match,
        signal_report=SignalReport(ok=True, disagreements=()),
        citation_drifts=(),
        effective_loaded=loaded,
        required=("rules/999-test-core.md",),
        mode=mode,
        max_turns_used=max_turns_used,
    )


# ---------------------------------------------------------------------------
# build_prompt_without_plugin tests
# ---------------------------------------------------------------------------


def test_build_prompt_without_plugin_contains_seed_fixture_complete(tmp_path: Path) -> None:
    from ai_rules.rule_loader_eval.without_plugin_prompt import build_prompt_without_plugin

    result = build_prompt_without_plugin(tmp_path / "rules")
    assert "SEED_FIXTURE_COMPLETE" in result


def test_build_prompt_without_plugin_contains_schema_hints(tmp_path: Path) -> None:
    from ai_rules.rule_loader_eval.without_plugin_prompt import build_prompt_without_plugin

    result = build_prompt_without_plugin(tmp_path / "rules")
    assert "keywords:" in result
    assert "triggers:" in result


def test_build_prompt_without_plugin_no_matched_rules_section(tmp_path: Path) -> None:
    from ai_rules.rule_loader_eval.without_plugin_prompt import build_prompt_without_plugin

    result = build_prompt_without_plugin(tmp_path / "rules")
    assert "## Matched Rules for This Request" not in result


def test_build_prompt_without_plugin_does_not_call_manifest_or_db(tmp_path: Path) -> None:
    from ai_rules.rule_loader_eval import without_plugin_prompt as wp

    with (
        patch.object(wp, "build_prompt_without_plugin", wraps=wp.build_prompt_without_plugin),
        patch("ai_rules.rule_loader_eval.agent_runner.build_eval_manifest") as mock_manifest,
        patch("ai_rules.match_rules.load_rules_db") as mock_db,
    ):
        wp.build_prompt_without_plugin(tmp_path / "rules")

    mock_manifest.assert_not_called()
    mock_db.assert_not_called()


# ---------------------------------------------------------------------------
# _is_missing_gate3_violation tests
# ---------------------------------------------------------------------------


def test_is_missing_gate3_violation_exact_match() -> None:
    assert _is_missing_gate3_violation((_GATE3_VIOLATION,)) is True


def test_is_missing_gate3_violation_empty() -> None:
    assert _is_missing_gate3_violation(()) is False


def test_is_missing_gate3_violation_non_gate3() -> None:
    assert (
        _is_missing_gate3_violation(
            ("zero loaded rules must use explicit no-match Rules Loaded body",)
        )
        is False
    )


# ---------------------------------------------------------------------------
# RunResult.result: discovery-budget-exhausted classification
# ---------------------------------------------------------------------------


def test_result_discovery_budget_exhausted_fires() -> None:
    """without-plugin + turns exhausted + gate3 violation → discovery-budget-exhausted."""
    rr = _make_run_result(
        mode="without-plugin",
        turns=5,
        max_turns_used=5,
        output_violations=(_GATE3_VIOLATION,),
        manifest_paths=frozenset(),
    )
    assert rr.result == "discovery-budget-exhausted"


def test_result_discovery_budget_exhausted_not_fired_non_gate3_violation() -> None:
    """Non-Gate-3 violation with exhausted turns does NOT produce budget-exhausted."""
    rr = _make_run_result(
        mode="without-plugin",
        turns=5,
        max_turns_used=5,
        output_violations=("zero loaded rules must use explicit no-match Rules Loaded body",),
        manifest_paths=frozenset(),
    )
    assert rr.result != "discovery-budget-exhausted"


def test_result_discovery_budget_exhausted_not_fired_plugin_mode() -> None:
    """Plugin mode with exhausted turns + gate3 violation still uses normal classification."""
    rr = _make_run_result(
        mode="plugin",
        turns=5,
        max_turns_used=5,
        output_violations=(_GATE3_VIOLATION,),
        manifest_paths=frozenset(),
    )
    assert rr.result != "discovery-budget-exhausted"


def test_result_discovery_budget_exhausted_not_fired_turns_not_exhausted() -> None:
    """without-plugin with gate3 violation but turns < max does not fire."""
    rr = _make_run_result(
        mode="without-plugin",
        turns=4,
        max_turns_used=5,
        output_violations=(_GATE3_VIOLATION,),
        manifest_paths=frozenset(),
    )
    assert rr.result != "discovery-budget-exhausted"


def test_result_discovery_budget_exhausted_not_fired_max_turns_zero() -> None:
    """max_turns_used=0 (legacy/default) prevents the classification from firing."""
    rr = _make_run_result(
        mode="without-plugin",
        turns=5,
        max_turns_used=0,
        output_violations=(_GATE3_VIOLATION,),
        manifest_paths=frozenset(),
    )
    assert rr.result != "discovery-budget-exhausted"


# ---------------------------------------------------------------------------
# _run_single_eval with without_plugin=True
# ---------------------------------------------------------------------------


def _pass_run(fixture_id: str, *, with_gate3: bool = False) -> AgentRun:
    loaded = ("rules/999-test-core.md",)
    violations = () if not with_gate3 else (_GATE3_VIOLATION,)
    return AgentRun(
        fixture_id=fixture_id,
        loaded=loaded,
        loaded_via_reads=loaded,
        loaded_via_reads_performed=(),
        loaded_via_section=loaded,
        disagreements=(),
        turns=1,
        duration_ms=10,
        model="claude-test",
        notes=(),
        input_tokens=100,
        output_tokens=10,
        total_cost_usd=0.001,
        manifest_paths=frozenset({"rules/999-test-core.md"}),
        output_violations=violations,
    )


def test_run_single_eval_without_plugin_manifest_available(tmp_path: Path) -> None:
    """_run_single_eval(without_plugin=True) produces result.manifest_available=True
    and manifest_paths contains the rule from build_eval_manifest.
    """
    from ai_rules.commands import rule_loader as rl

    fixture = _make_fixture("fx")
    synthetic_manifest = {"load_sequence": [{"rule_path": "rules/999-test-core.md"}]}

    async def _fake_async(fixture_id, prompt, **kwargs):
        return _pass_run(fixture_id)

    with (
        patch("ai_rules.rule_loader_eval.engine.run_live_async", new=_fake_async),
        patch.object(rl, "load_rules_metadata", return_value={}),
        patch(
            "ai_rules.rule_loader_eval.without_plugin_prompt.build_prompt_without_plugin",
            return_value="SYNTHETIC PROMPT",
        ),
        patch(
            "ai_rules.rule_loader_eval.agent_runner.build_eval_manifest",
            return_value=synthetic_manifest,
        ),
        patch(
            "ai_rules.match_rules.load_rules_db",
            return_value={},
        ),
    ):
        results, is_infra = rl._run_single_eval(
            fixtures=[fixture],
            root=Path("."),
            resolved_connection="test-conn",
            strict_forbidden=False,
            max_turns=3,
            effort="low",
            model="auto",
            debug=False,
            out_dir=None,
            label="test",
            concurrency=1,
            without_plugin=True,
        )

    assert len(results) == 1
    result = results[0]
    assert result.manifest_available is True
    assert "rules/999-test-core.md" in result.run.manifest_paths


def test_run_single_eval_without_plugin_false_never_calls_build_prompt(tmp_path: Path) -> None:
    """_run_single_eval(without_plugin=False) does not import/call build_prompt_without_plugin."""
    from ai_rules.commands import rule_loader as rl

    fixture = _make_fixture("fx")

    async def _fake_async(fixture_id, prompt, **kwargs):
        return _pass_run(fixture_id)

    mock_build_wp = MagicMock(side_effect=AssertionError("must not be called"))

    with (
        patch("ai_rules.rule_loader_eval.engine.run_live_async", new=_fake_async),
        patch.object(rl, "load_rules_metadata", return_value={}),
        patch(
            "ai_rules.rule_loader_eval.without_plugin_prompt.build_prompt_without_plugin",
            mock_build_wp,
        ),
    ):
        results, _ = rl._run_single_eval(
            fixtures=[fixture],
            root=Path("."),
            resolved_connection="test-conn",
            strict_forbidden=False,
            max_turns=3,
            effort="low",
            model="auto",
            debug=False,
            out_dir=None,
            label="test",
            concurrency=1,
            without_plugin=False,
        )

    mock_build_wp.assert_not_called()
    assert len(results) == 1


# ---------------------------------------------------------------------------
# RunResult mode field wired through from _run_single_eval
# ---------------------------------------------------------------------------


def test_run_result_mode_set_for_without_plugin(tmp_path: Path) -> None:
    """RunResult produced by without_plugin=True run carries mode='without-plugin'."""
    from ai_rules.commands import rule_loader as rl

    fixture = _make_fixture("fx")
    synthetic_manifest = {"load_sequence": [{"rule_path": "rules/999-test-core.md"}]}

    async def _fake_async(fixture_id, prompt, **kwargs):
        return _pass_run(fixture_id)

    with (
        patch("ai_rules.rule_loader_eval.engine.run_live_async", new=_fake_async),
        patch.object(rl, "load_rules_metadata", return_value={}),
        patch(
            "ai_rules.rule_loader_eval.without_plugin_prompt.build_prompt_without_plugin",
            return_value="SYNTHETIC PROMPT",
        ),
        patch(
            "ai_rules.rule_loader_eval.agent_runner.build_eval_manifest",
            return_value=synthetic_manifest,
        ),
        patch(
            "ai_rules.match_rules.load_rules_db",
            return_value={},
        ),
    ):
        results, _ = rl._run_single_eval(
            fixtures=[fixture],
            root=Path("."),
            resolved_connection="test-conn",
            strict_forbidden=False,
            max_turns=3,
            effort="low",
            model="auto",
            debug=False,
            out_dir=None,
            label="test",
            concurrency=1,
            without_plugin=True,
        )

    assert results[0].mode == "without-plugin"
    assert results[0].max_turns_used == 3


# ---------------------------------------------------------------------------
# eval_cmd: effective_max_turns defaults to 15 for without-plugin
# ---------------------------------------------------------------------------


def test_eval_cmd_without_plugin_defaults_to_15_turns() -> None:
    """Eval --without-plugin with no --max-turns uses 15 turns (not DEFAULT_MAX_TURNS)."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    captured: list[int] = []

    def _fake_single(*args, **kwargs):
        captured.append(kwargs["max_turns"])
        return ([], False)

    runner = CliRunner()
    mock_ctx = MagicMock()
    mock_ctx.started_at = "2026-08-03T00:00:00"
    mock_ctx.run_id = "test"
    mock_ctx.model_requested = "auto"
    mock_ctx.runs_requested = 1
    with (
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch("ai_rules.commands.rule_loader._require_connection_or_exit", return_value="c"),
        patch("ai_rules.commands.rule_loader.load_fixtures", return_value=[_make_fixture("fx")]),
        patch("ai_rules.commands.rule_loader.load_rules_metadata", return_value={}),
        patch("ai_rules.commands.rule_loader._run_single_eval", side_effect=_fake_single),
        patch("ai_rules.rule_loader_eval.results_writer.make_run_context", return_value=mock_ctx),
        patch("ai_rules.rule_loader_eval.results_writer.ResultsRunWriter"),
        patch(
            "ai_rules.rule_loader_eval.results_writer.build_run_dir_name", return_value="test_run"
        ),
        patch(
            "ai_rules.rule_loader_eval.results_writer.resolve_results_root",
            return_value=Path("/tmp/r"),
        ),
        patch("ai_rules.commands.rule_loader._write_aggregate_and_finalize"),
    ):
        result = runner.invoke(app, ["rule-loader", "eval", "--without-plugin", "--runs", "1"])

    assert captured == [15], f"Expected 15 turns, got {captured}"


def test_eval_cmd_without_plugin_max_turns_override_wins() -> None:
    """Eval --without-plugin --max-turns 8 uses 8 (user override wins over default 15)."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    captured: list[int] = []

    def _fake_single(*args, **kwargs):
        captured.append(kwargs["max_turns"])
        return ([], False)

    runner = CliRunner()
    mock_ctx = MagicMock()
    mock_ctx.started_at = "2026-08-03T00:00:00"
    mock_ctx.run_id = "test"
    mock_ctx.model_requested = "auto"
    mock_ctx.runs_requested = 1
    with (
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch("ai_rules.commands.rule_loader._require_connection_or_exit", return_value="c"),
        patch("ai_rules.commands.rule_loader.load_fixtures", return_value=[_make_fixture("fx")]),
        patch("ai_rules.commands.rule_loader.load_rules_metadata", return_value={}),
        patch("ai_rules.commands.rule_loader._run_single_eval", side_effect=_fake_single),
        patch("ai_rules.rule_loader_eval.results_writer.make_run_context", return_value=mock_ctx),
        patch("ai_rules.rule_loader_eval.results_writer.ResultsRunWriter"),
        patch(
            "ai_rules.rule_loader_eval.results_writer.build_run_dir_name", return_value="test_run"
        ),
        patch(
            "ai_rules.rule_loader_eval.results_writer.resolve_results_root",
            return_value=Path("/tmp/r"),
        ),
        patch("ai_rules.commands.rule_loader._write_aggregate_and_finalize"),
    ):
        result = runner.invoke(
            app, ["rule-loader", "eval", "--without-plugin", "--max-turns", "8", "--runs", "1"]
        )

    assert captured == [8], f"Expected 8 turns, got {captured}"
