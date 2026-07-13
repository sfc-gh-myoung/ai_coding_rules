"""Tests for refresh-all --out-dir precedence parity with eval (plan: refresh-all-results-migration-v1).

Covers AC #1-7 from the plan:
- CLI > AI_RULES_RESULTS_DIR env > None (stdout) precedence for resolve_optional_results_root
- Relative --out-dir resolved against CWD
- Artifact shape unchanged (per-fixture YAML + summary.json, no results/<run_dir>/ tree)
- eval's resolve_results_root unaffected
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.rule_loader_eval.results_writer import (
    RESULTS_ROOT_ENV_VAR,
    resolve_optional_results_root,
    resolve_results_root,
)

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})


# ---------------------------------------------------------------------------
# Unit tests for resolve_optional_results_root (pure function, AC #1-4)
# ---------------------------------------------------------------------------


def test_resolver_explicit_absolute_path(tmp_path: Path) -> None:
    """Explicit absolute --out-dir is returned verbatim."""
    result = resolve_optional_results_root(tmp_path, env={}, cwd=Path("/some/cwd"))
    assert result == tmp_path


def test_resolver_explicit_relative_path_resolved_against_cwd(tmp_path: Path) -> None:
    """Relative --out-dir is resolved against the supplied cwd (AC #1)."""
    cwd = tmp_path / "work"
    result = resolve_optional_results_root(Path("out"), env={}, cwd=cwd)
    assert result == cwd / "out"


def test_resolver_env_var_only(tmp_path: Path) -> None:
    """AI_RULES_RESULTS_DIR env var is used when --out-dir is absent (AC #2)."""
    env_dir = tmp_path / "env-out"
    result = resolve_optional_results_root(
        None, env={RESULTS_ROOT_ENV_VAR: str(env_dir)}, cwd=tmp_path
    )
    assert result == env_dir


def test_resolver_env_var_relative_resolved_against_cwd(tmp_path: Path) -> None:
    """Relative AI_RULES_RESULTS_DIR is resolved against the supplied cwd."""
    result = resolve_optional_results_root(
        None, env={RESULTS_ROOT_ENV_VAR: "env-relative"}, cwd=tmp_path
    )
    assert result == tmp_path / "env-relative"


def test_resolver_cli_beats_env(tmp_path: Path) -> None:
    """Explicit --out-dir takes precedence over AI_RULES_RESULTS_DIR (AC #3)."""
    cli_dir = tmp_path / "cli-out"
    env_dir = tmp_path / "env-out"
    result = resolve_optional_results_root(
        cli_dir, env={RESULTS_ROOT_ENV_VAR: str(env_dir)}, cwd=tmp_path
    )
    assert result == cli_dir


def test_resolver_neither_returns_none(tmp_path: Path) -> None:
    """Returns None when neither --out-dir nor AI_RULES_RESULTS_DIR is set (AC #4)."""
    result = resolve_optional_results_root(None, env={}, cwd=tmp_path)
    assert result is None


def test_resolver_empty_env_var_returns_none(tmp_path: Path) -> None:
    """An empty AI_RULES_RESULTS_DIR is treated as unset — returns None."""
    result = resolve_optional_results_root(None, env={RESULTS_ROOT_ENV_VAR: ""}, cwd=tmp_path)
    assert result is None


# ---------------------------------------------------------------------------
# AC #6: eval's resolve_results_root is byte-for-byte unchanged
# ---------------------------------------------------------------------------


def test_eval_resolver_unaffected_default(tmp_path: Path) -> None:
    """resolve_results_root still falls back to <cwd>/results/ with no args (AC #6)."""
    result = resolve_results_root(None, env={}, cwd=tmp_path)
    assert result == tmp_path / "results"


def test_eval_resolver_unaffected_explicit(tmp_path: Path) -> None:
    """resolve_results_root with explicit path still works (AC #6)."""
    result = resolve_results_root(tmp_path / "my-results", env={}, cwd=tmp_path)
    assert result == tmp_path / "my-results"


# ---------------------------------------------------------------------------
# CLI-level integration tests (batch command plumbing, AC #2-5)
# ---------------------------------------------------------------------------


@pytest.fixture
def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("project root not found")


def _make_fixture_yaml(path: Path, fixture_id: str, prompt: str) -> None:
    path.write_text(
        f"id: {fixture_id}\nprompt: |\n  {prompt}\n",
        encoding="utf-8",
    )


def _make_summary(items, concurrency: int = 1, wall: float = 1.0):
    from ai_rules.rule_loader_eval.agent_runner import AgentRun
    from ai_rules.rule_loader_eval.batch import BatchOutcome, BatchSummary

    outcomes = []
    for item in items:
        run = AgentRun(
            fixture_id=item.id,
            loaded=("rules/999-test-core.md",),
            loaded_via_reads=("rules/999-test-core.md",),
            loaded_via_reads_performed=(),
            loaded_via_section=("rules/999-test-core.md",),
            turns=3,
            duration_ms=500,
            model="auto",
            stop_reason="end_turn",
        )
        outcomes.append(BatchOutcome(item=item, run=run, error_type=None, error_message=None))
    return BatchSummary(concurrency=concurrency, outcomes=tuple(outcomes), wall_seconds=wall)


def _fake_run_batch_factory(items_captured: list | None = None):
    """Return a run_batch stub that calls on_outcome for every item."""

    def _fake(items, **kwargs):
        if items_captured is not None:
            items_captured.extend(items)
        summary = _make_summary(items, wall=0.5)
        on_outcome = kwargs.get("on_outcome")
        if on_outcome is not None:
            for i, outcome in enumerate(summary.outcomes, start=1):
                on_outcome(outcome, i)
        return summary

    return _fake


def test_env_var_steers_output_when_no_cli_out_dir(tmp_path: Path, project_root: Path) -> None:
    """AI_RULES_RESULTS_DIR drives refresh-all output when --out-dir is omitted (AC #2)."""
    env_dir = tmp_path / "env-results"
    fx_path = tmp_path / "simple-test.yaml"
    _make_fixture_yaml(fx_path, "simple-test", "Set up a search service.")

    with (
        patch("ai_rules.rule_loader_eval.batch.run_batch", side_effect=_fake_run_batch_factory()),
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch("ai_rules.commands.rule_loader.find_project_root", return_value=project_root),
        patch("ai_rules.rule_loader_eval.batch.expand_glob", return_value=[fx_path]),
        patch.dict(os.environ, {RESULTS_ROOT_ENV_VAR: str(env_dir)}, clear=False),
    ):
        result = runner.invoke(
            app,
            ["rule-loader", "refresh-all", "--all", "--concurrency", "1"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0, result.output
    assert (env_dir / "summary.json").exists(), "summary.json must land in env-var dir"
    assert any(p.suffix == ".yaml" for p in env_dir.iterdir()), (
        "per-fixture YAML must land in env-var dir"
    )


def test_cli_out_dir_beats_env_var(tmp_path: Path, project_root: Path) -> None:
    """--out-dir takes precedence over AI_RULES_RESULTS_DIR (AC #3)."""
    cli_dir = tmp_path / "cli-out"
    env_dir = tmp_path / "env-out"
    fx_path = tmp_path / "simple-test.yaml"
    _make_fixture_yaml(fx_path, "simple-test", "Set up a search service.")

    with (
        patch("ai_rules.rule_loader_eval.batch.run_batch", side_effect=_fake_run_batch_factory()),
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch("ai_rules.commands.rule_loader.find_project_root", return_value=project_root),
        patch("ai_rules.rule_loader_eval.batch.expand_glob", return_value=[fx_path]),
        patch.dict(os.environ, {RESULTS_ROOT_ENV_VAR: str(env_dir)}, clear=False),
    ):
        result = runner.invoke(
            app,
            [
                "rule-loader",
                "refresh-all",
                "--all",
                "--concurrency",
                "1",
                "--out-dir",
                str(cli_dir),
            ],
            catch_exceptions=False,
        )

    assert result.exit_code == 0, result.output
    assert (cli_dir / "summary.json").exists(), "output must go to --out-dir, not env var dir"
    assert not env_dir.exists(), "env-var dir must not be created when --out-dir overrides it"


def test_stdout_preserved_when_neither_set(tmp_path: Path, project_root: Path) -> None:
    """YAML streams to stdout when neither --out-dir nor AI_RULES_RESULTS_DIR is set (AC #4)."""
    fx_path = tmp_path / "simple-test.yaml"
    _make_fixture_yaml(fx_path, "simple-test", "Set up a search service.")

    env_without_results_dir = {k: v for k, v in os.environ.items() if k != RESULTS_ROOT_ENV_VAR}

    with (
        patch("ai_rules.rule_loader_eval.batch.run_batch", side_effect=_fake_run_batch_factory()),
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch("ai_rules.commands.rule_loader.find_project_root", return_value=project_root),
        patch("ai_rules.rule_loader_eval.batch.expand_glob", return_value=[fx_path]),
        patch.dict(os.environ, env_without_results_dir, clear=True),
    ):
        result = runner.invoke(
            app,
            ["rule-loader", "refresh-all", "--all"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0, result.output
    assert "# fixture:" in result.output or "schema_version" in result.output, (
        "YAML payload must stream to stdout"
    )
    # No directory should have been created by the command itself
    assert not (tmp_path / "summary.json").exists()


def test_artifact_shape_unchanged_with_env_dir(tmp_path: Path, project_root: Path) -> None:
    """When env var supplies the output dir, artifacts match the normal --out-dir shape (AC #5).

    Verifies per-fixture <safe_id>.yaml + summary.json with the refresh-specific schema
    keys {concurrency, wall_seconds, total, succeeded, failed, outcomes}.
    """
    import json

    env_dir = tmp_path / "shape-check"
    fx_path = tmp_path / "simple-test.yaml"
    _make_fixture_yaml(fx_path, "simple-test", "Set up a search service.")

    with (
        patch("ai_rules.rule_loader_eval.batch.run_batch", side_effect=_fake_run_batch_factory()),
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch("ai_rules.commands.rule_loader.find_project_root", return_value=project_root),
        patch("ai_rules.rule_loader_eval.batch.expand_glob", return_value=[fx_path]),
        patch.dict(os.environ, {RESULTS_ROOT_ENV_VAR: str(env_dir)}, clear=False),
    ):
        result = runner.invoke(
            app,
            ["rule-loader", "refresh-all", "--all", "--concurrency", "1"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0, result.output
    summary_path = env_dir / "summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text())
    # Refresh-specific schema keys (not ai-rules-eval-*/v1)
    for key in ("concurrency", "wall_seconds", "total", "succeeded", "failed", "outcomes"):
        assert key in summary, f"summary.json missing key: {key!r}"
    # Per-fixture YAML exists
    assert any(p.suffix == ".yaml" for p in env_dir.iterdir())
    # No results/<run_dir>/ tree created
    assert not (env_dir / "results").exists()
