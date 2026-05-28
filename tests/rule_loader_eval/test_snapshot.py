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
    """read_eval_snapshot raises ValueError when meta.json is missing."""
    with pytest.raises(ValueError, match="no meta.json"):
        read_eval_snapshot(tmp_path)


def test_unsupported_schema_version_rejected(tmp_path: Path) -> None:
    """A snapshot with future schema_version is rejected."""
    (tmp_path / "meta.json").write_text(json.dumps({"schema_version": 999}), encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported snapshot schema_version"):
        read_eval_snapshot(tmp_path)


def test_missing_eval_dir_returns_empty_fixtures(tmp_path: Path) -> None:
    """A snapshot dir with meta.json but no eval/ subdir is valid (empty)."""
    meta = SnapshotMeta(label="empty")
    (tmp_path / "meta.json").write_text(json.dumps(meta.to_dict()), encoding="utf-8")
    snapshot = read_eval_snapshot(tmp_path)
    assert snapshot.fixtures == ()
    assert snapshot.summary is None


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
    """Writing produces one JSON per fixture plus summary.json."""
    rows = [_row("fx1"), _row("fx2"), _row("fx3", passed=False)]
    meta = SnapshotMeta(label="test")
    write_eval_snapshot(tmp_path, rows, meta)
    eval_dir = tmp_path / "eval"
    assert (eval_dir / "fx1.json").is_file()
    assert (eval_dir / "fx2.json").is_file()
    assert (eval_dir / "fx3.json").is_file()
    assert (eval_dir / "summary.json").is_file()
    assert (tmp_path / "meta.json").is_file()


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
