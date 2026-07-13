"""Unit tests for the snapshot schema + serialization helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.snapshot import (
    SNAPSHOT_SCHEMA_VERSION,
    FixtureSnapshot,
    SnapshotMeta,
    capture_meta,
    compute_summary,
    read_eval_snapshot,
    serialize_run_result,
    write_eval_snapshot,
)


def _row(
    fixture_id: str = "fx",
    *,
    passed: bool = True,
    loaded: tuple[str, ...] = ("rules/999-test-core.md",),
    turns: int = 3,
    duration_ms: int = 500,
    signal: int = 0,
    citation: int = 0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_tokens: int = 0,
    total_cost_usd: float = 0.0,
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
        signal_disagreements=signal,
        citation_drifts=citation,
        turns=turns,
        duration_ms=duration_ms,
        model="auto",
        stop_reason="end_turn",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        total_cost_usd=total_cost_usd,
    )


def test_round_trip_single_fixture(tmp_path: Path) -> None:
    """Writing then reading a snapshot reproduces the input rows."""
    rows = [_row("simple-foo"), _row("complex-bar", passed=False)]
    meta = SnapshotMeta(
        schema_version=SNAPSHOT_SCHEMA_VERSION,
        captured_at="2026-05-17T03:00:00-04:00",
        git_commit="abc1234",
        git_branch="feature/test",
        model="auto",
        max_turns=15,
        effort="low",
        label="test-baseline",
    )
    write_eval_snapshot(tmp_path, rows, meta)

    snapshot = read_eval_snapshot(tmp_path)
    assert snapshot.meta.label == "test-baseline"
    assert snapshot.meta.git_commit == "abc1234"
    assert {f.fixture_id for f in snapshot.fixtures} == {"simple-foo", "complex-bar"}
    by_id = {f.fixture_id: f for f in snapshot.fixtures}
    assert by_id["simple-foo"].passed is True
    assert by_id["complex-bar"].passed is False
    assert snapshot.summary is not None
    assert snapshot.summary.total == 2
    assert snapshot.summary.passed == 1
    assert snapshot.summary.failed == 1


def test_summary_aggregates_correctly() -> None:
    """compute_summary aggregates totals/means correctly."""
    rows = [
        _row("a", turns=2, duration_ms=400),
        _row("b", turns=4, duration_ms=600),
        _row("c", passed=False, turns=6, duration_ms=800, signal=1, citation=2),
    ]
    s = compute_summary(rows)
    assert s.total == 3
    assert s.passed == 2
    assert s.failed == 1
    assert s.mean_turns == 4.0
    assert s.mean_duration_ms == 600.0
    assert s.total_signal_disagreements == 1
    assert s.total_citation_drifts == 2


def test_empty_summary() -> None:
    """compute_summary with empty list yields all zeros."""
    s = compute_summary([])
    assert s.total == 0
    assert s.passed == 0
    assert s.mean_turns == 0.0


def test_meta_required_for_read(tmp_path: Path) -> None:
    """read_eval_snapshot raises ValueError when manifest.json is missing (new layout)."""
    with pytest.raises(ValueError, match="no manifest.json"):
        read_eval_snapshot(tmp_path)


def test_unsupported_schema_version_rejected(tmp_path: Path) -> None:
    """A snapshot manifest with an unsupported embedded snapshot_schema_version is rejected."""
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "ai-rules-eval-manifest/v1",
                "snapshot_meta_extras": {"snapshot_schema_version": 999},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unsupported snapshot schema_version"):
        read_eval_snapshot(tmp_path)


def test_missing_fixtures_dir_returns_empty_fixtures(tmp_path: Path) -> None:
    """A snapshot dir with manifest.json but no run-01/fixtures/ subdir is valid (empty)."""
    meta = SnapshotMeta(label="empty")
    # Write a minimal new-layout manifest so read_eval_snapshot accepts the dir.
    write_eval_snapshot(tmp_path, [], meta)
    # Then remove the fixtures directory to simulate an incomplete write.
    import shutil

    shutil.rmtree(tmp_path / "run-01" / "fixtures", ignore_errors=True)
    snapshot = read_eval_snapshot(tmp_path)
    assert snapshot.fixtures == ()


def test_capture_meta_populates_fields(tmp_path: Path) -> None:
    """capture_meta returns a meta object with required fields populated."""
    meta = capture_meta(tmp_path, model="auto", max_turns=10, effort="low", label="x")
    assert meta.schema_version == SNAPSHOT_SCHEMA_VERSION
    assert meta.captured_at  # non-empty timestamp
    assert meta.model == "auto"
    assert meta.max_turns == 10
    assert meta.effort == "low"
    assert meta.label == "x"


def test_fixture_snapshot_to_dict_round_trip() -> None:
    """to_dict / from_dict round-trip preserves all fields."""
    row = _row("test-fx", loaded=("rules/A.md", "rules/B.md"))
    parsed = FixtureSnapshot.from_dict(row.to_dict())
    assert parsed == row


def test_write_creates_summary_and_per_fixture_files(tmp_path: Path) -> None:
    """Writing produces one JSON per fixture plus per-pass + aggregate summary (new layout)."""
    rows = [_row("fx1"), _row("fx2"), _row("fx3", passed=False)]
    meta = SnapshotMeta(label="test")
    write_eval_snapshot(tmp_path, rows, meta)
    fixtures_dir = tmp_path / "run-01" / "fixtures"
    assert (fixtures_dir / "fx1.json").is_file()
    assert (fixtures_dir / "fx2.json").is_file()
    assert (fixtures_dir / "fx3.json").is_file()
    assert (tmp_path / "run-01" / "summary.json").is_file()
    assert (tmp_path / "run-01" / "run_meta.json").is_file()
    assert (tmp_path / "summary.json").is_file()
    assert (tmp_path / "manifest.json").is_file()


def test_signal_investigation_fields_round_trip() -> None:
    """loaded_via_reads, loaded_via_section, disagreement_details survive to_dict/from_dict."""
    row = FixtureSnapshot(
        fixture_id="fx",
        passed=False,
        loaded=("rules/999-test-core.md", "rules/102.md"),
        expected_required=("rules/999-test-core.md",),
        expected_dependencies=(),
        expected_optional=(),
        expected_forbidden=(),
        missing_required=(),
        missing_dependencies=(),
        forbidden_present=(),
        signal_disagreements=2,
        citation_drifts=0,
        turns=3,
        duration_ms=500,
        loaded_via_reads=("rules/999-test-core.md", "rules/102.md", "rules/extra.md"),
        loaded_via_section=("rules/999-test-core.md", "rules/102.md"),
        disagreement_details=("only-in-tool-reads-vs-rules-loaded: rules/extra.md",),
    )
    parsed = FixtureSnapshot.from_dict(row.to_dict())
    assert parsed == row
    # And the JSON contains the new keys for jq-based investigation:
    d = row.to_dict()
    assert "loaded_via_reads" in d
    assert "loaded_via_section" in d
    assert "disagreement_details" in d


def test_old_snapshot_without_signal_fields_parses(tmp_path: Path) -> None:
    """Legacy JSON missing the three new fields parses with empty-tuple defaults."""
    legacy_json = {
        "fixture_id": "fx-legacy",
        "passed": True,
        "loaded": ["rules/999-test-core.md"],
        "expected_required": ["rules/999-test-core.md"],
        "expected_dependencies": [],
        "expected_optional": [],
        "expected_forbidden": [],
        "missing_required": [],
        "missing_dependencies": [],
        "forbidden_present": [],
        "signal_disagreements": 0,
        "citation_drifts": 0,
        "turns": 2,
        "duration_ms": 400,
        "model": "auto",
        "stop_reason": "end_turn",
    }
    parsed = FixtureSnapshot.from_dict(legacy_json)
    assert parsed.loaded_via_reads == ()
    assert parsed.loaded_via_section == ()
    assert parsed.disagreement_details == ()


def test_token_fields_serialize_and_deserialize() -> None:
    """Round-trip preserves non-zero token and cost values."""
    row = _row(
        "tok-fx",
        input_tokens=1000,
        output_tokens=200,
        total_tokens=1200,
        total_cost_usd=0.005,
    )
    parsed = FixtureSnapshot.from_dict(row.to_dict())
    assert parsed.input_tokens == 1000
    assert parsed.output_tokens == 200
    assert parsed.total_tokens == 1200
    assert parsed.total_cost_usd == 0.005
    assert parsed == row


def test_old_snapshot_missing_token_fields_defaults_to_zero() -> None:
    """Legacy JSON without token fields loads with zero defaults (backward compat)."""
    legacy_json = {
        "fixture_id": "x",
        "passed": True,
        "loaded": [],
        "expected_required": [],
        "expected_dependencies": [],
        "expected_optional": [],
        "expected_forbidden": [],
        "missing_required": [],
        "missing_dependencies": [],
        "forbidden_present": [],
        "signal_disagreements": 0,
        "citation_drifts": 0,
        "turns": 2,
        "duration_ms": 400,
    }
    fx = FixtureSnapshot.from_dict(legacy_json)
    assert fx.input_tokens == 0
    assert fx.output_tokens == 0
    assert fx.total_tokens == 0
    assert fx.total_cost_usd == 0.0


def test_serialize_run_result_maps_tokens() -> None:
    """serialize_run_result maps input/output/cost from result.run."""
    from unittest.mock import MagicMock

    fixture = MagicMock()
    fixture.required = ["rules/999-test-core.md"]
    fixture.dependencies = []
    fixture.optional = []
    fixture.forbidden = []

    run = MagicMock()
    run.loaded = ["rules/999-test-core.md"]
    run.loaded_via_reads = []
    run.loaded_via_section = []
    run.disagreements = []
    run.skill_invocations = []
    run.output_violations = []
    run.turns = 3
    run.duration_ms = 500
    run.model = "auto"
    run.stop_reason = "end_turn"
    run.input_tokens = 1500
    run.output_tokens = 300
    run.total_cost_usd = 0.012

    result = MagicMock()
    result.fixture_id = "fx"
    result.passed = True
    result.run = run
    result.match.missing_required = []
    result.match.missing_dependencies = []
    result.match.forbidden_present = []
    result.signal_report.disagreements = []
    result.citation_drifts = []
    result.depends_violations = []

    snap = serialize_run_result(result, fixture)
    assert snap.input_tokens == 1500
    assert snap.output_tokens == 300
    assert snap.total_tokens == 1800
    assert snap.total_cost_usd == 0.012
