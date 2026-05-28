"""End-to-end tests for the ``compare`` CLI subcommand."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.rule_loader_eval.snapshot import (
    FixtureSnapshot,
    SnapshotMeta,
    write_eval_snapshot,
)

runner = CliRunner()


def _row(
    fixture_id: str,
    *,
    passed: bool = True,
    loaded: tuple[str, ...] = ("rules/999-test-core.md",),
) -> FixtureSnapshot:
    return FixtureSnapshot(
        fixture_id=fixture_id,
        passed=passed,
        loaded=loaded,
        expected_required=("rules/999-test-core.md",),
        expected_dependencies=(),
        expected_optional=(),
        expected_forbidden=(),
        missing_required=(),
        missing_dependencies=(),
        forbidden_present=(),
        signal_disagreements=0,
        citation_drifts=0,
        turns=2,
        duration_ms=300,
    )


def _snap(dir_path: Path, label: str, rows: list[FixtureSnapshot]) -> None:
    write_eval_snapshot(dir_path, rows, SnapshotMeta(label=label))


def test_compare_identical_snapshots_exits_zero(tmp_path: Path) -> None:
    """Compare against itself exits 0 with a 'no changes' message."""
    base_dir = tmp_path / "base"
    post_dir = tmp_path / "post"
    rows = [_row("a"), _row("b")]
    _snap(base_dir, "baseline", rows)
    _snap(post_dir, "post", rows)

    result = runner.invoke(app, ["rule-loader", "compare", str(base_dir), str(post_dir)])
    assert result.exit_code == 0, result.output
    assert "no per-fixture changes detected" in result.output


def test_compare_regression_exits_one(tmp_path: Path) -> None:
    """A pass→fail regression yields exit code 1."""
    base_dir = tmp_path / "base"
    post_dir = tmp_path / "post"
    _snap(base_dir, "baseline", [_row("regressing", passed=True)])
    _snap(post_dir, "post", [_row("regressing", passed=False)])

    result = runner.invoke(app, ["rule-loader", "compare", str(base_dir), str(post_dir)])
    assert result.exit_code == 1, result.output
    assert "REGRESSIONS" in result.output


def test_compare_drift_only_exits_two(tmp_path: Path) -> None:
    """Loaded-set drift without pass change yields exit code 2."""
    base_dir = tmp_path / "base"
    post_dir = tmp_path / "post"
    _snap(base_dir, "baseline", [_row("drifting", loaded=("rules/A.md",))])
    _snap(
        post_dir,
        "post",
        [_row("drifting", loaded=("rules/A.md", "rules/B.md"))],
    )

    result = runner.invoke(app, ["rule-loader", "compare", str(base_dir), str(post_dir)])
    assert result.exit_code == 2, result.output


def test_compare_exit_on_regression_upgrades_drift_to_one(tmp_path: Path) -> None:
    """--exit-on-regression promotes drift-only exit (2) to regression (1)."""
    base_dir = tmp_path / "base"
    post_dir = tmp_path / "post"
    _snap(base_dir, "baseline", [_row("drifting", loaded=("rules/A.md",))])
    _snap(
        post_dir,
        "post",
        [_row("drifting", loaded=("rules/A.md", "rules/B.md"))],
    )

    result = runner.invoke(
        app,
        [
            "rule-loader",
            "compare",
            str(base_dir),
            str(post_dir),
            "--exit-on-regression",
        ],
    )
    assert result.exit_code == 1, result.output


def test_compare_format_json_emits_parseable(tmp_path: Path) -> None:
    """--format=json emits a parseable JSON object with the documented schema."""
    base_dir = tmp_path / "base"
    post_dir = tmp_path / "post"
    _snap(base_dir, "baseline", [_row("a")])
    _snap(post_dir, "post", [_row("a")])

    result = runner.invoke(
        app,
        [
            "rule-loader",
            "compare",
            str(base_dir),
            str(post_dir),
            "--format=json",
        ],
    )
    assert result.exit_code == 0, result.output
    # Find the JSON object in the output (CliRunner may include log lines).
    start = result.output.find("{")
    end = result.output.rfind("}")
    assert start >= 0 and end > start
    data = json.loads(result.output[start : end + 1])
    assert "baseline_pass_rate" in data
    assert "deltas" in data


def test_compare_alias_map_neutralizes_rename(tmp_path: Path) -> None:
    """--alias-map removes the cosmetic-rename drift from the diff."""
    base_dir = tmp_path / "base"
    post_dir = tmp_path / "post"
    _snap(base_dir, "baseline", [_row("aliased", loaded=("rules/old.md",))])
    _snap(post_dir, "post", [_row("aliased", loaded=("rules/new.md",))])

    aliases = tmp_path / "aliases.json"
    aliases.write_text(json.dumps({"rules/old.md": "rules/new.md"}), encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "rule-loader",
            "compare",
            str(base_dir),
            str(post_dir),
            "--alias-map",
            str(aliases),
        ],
    )
    assert result.exit_code == 0, result.output


def test_compare_invalid_format_exits_four(tmp_path: Path) -> None:
    """An unsupported --format value exits 4 with a clear error."""
    base_dir = tmp_path / "base"
    post_dir = tmp_path / "post"
    _snap(base_dir, "baseline", [_row("a")])
    _snap(post_dir, "post", [_row("a")])

    result = runner.invoke(
        app,
        [
            "rule-loader",
            "compare",
            str(base_dir),
            str(post_dir),
            "--format=html",
        ],
    )
    assert result.exit_code == 4, result.output


def test_compare_missing_baseline_exits_four(tmp_path: Path) -> None:
    """A missing snapshot directory yields exit 4 (FIXTURE_INVALID)."""
    post_dir = tmp_path / "post"
    _snap(post_dir, "post", [_row("a")])

    result = runner.invoke(
        app,
        ["rule-loader", "compare", str(tmp_path / "nope"), str(post_dir)],
    )
    assert result.exit_code == 4, result.output


def test_compare_verbose_flag_expands_drift_only(tmp_path: Path) -> None:
    """--verbose expands the drift-only section to show per-fixture blocks."""
    base_dir = tmp_path / "base"
    post_dir = tmp_path / "post"
    _snap(base_dir, "base", [_row("drifting", loaded=("rules/A.md",))])
    _snap(post_dir, "post", [_row("drifting", loaded=("rules/B.md",))])

    result_default = runner.invoke(app, ["rule-loader", "compare", str(base_dir), str(post_dir)])
    result_verbose = runner.invoke(
        app, ["rule-loader", "compare", str(base_dir), str(post_dir), "--verbose"]
    )
    assert "--verbose to expand" in result_default.output
    assert "load-drift only" in result_verbose.output
    assert "drifting  [pass->pass]" in result_verbose.output
