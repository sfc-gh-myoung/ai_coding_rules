"""Tests for ``merge_snapshots`` and the ``merge-snapshots`` CLI subcommand."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.rule_loader_eval.compare import (
    merge_snapshots,
    render_merge_summary,
)
from ai_rules.rule_loader_eval.snapshot import (
    FixtureSnapshot,
    Snapshot,
    SnapshotMeta,
    compute_summary,
    read_eval_snapshot,
    write_eval_snapshot,
)

runner = CliRunner()


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
    )


def _snap(label: str, rows: list[FixtureSnapshot]) -> Snapshot:
    return Snapshot(
        meta=SnapshotMeta(label=label),
        fixtures=tuple(rows),
        summary=compute_summary(rows),
    )


# ---------------------------------------------------------------------------
# merge_snapshots core
# ---------------------------------------------------------------------------


def test_merge_empty_raises() -> None:
    """No snapshots => ValueError."""
    with pytest.raises(ValueError, match="at least one snapshot"):
        merge_snapshots([])


def test_merge_no_fixtures_raises() -> None:
    """All-empty snapshots => ValueError."""
    a = _snap("a", [])
    b = _snap("b", [])
    with pytest.raises(ValueError, match="no fixtures"):
        merge_snapshots([a, b])


def test_majority_pass_three_runs() -> None:
    """Q1: 2 of 3 passing fixtures yields a passing merged fixture (strict majority)."""
    runs = [
        _snap("r1", [_row("fx", passed=True)]),
        _snap("r2", [_row("fx", passed=True)]),
        _snap("r3", [_row("fx", passed=False)]),
    ]
    merged = merge_snapshots(runs)
    assert merged.fixtures[0].passed is True


def test_majority_fail_three_runs() -> None:
    """1 of 3 passing fixtures fails the strict-majority threshold."""
    runs = [
        _snap("r1", [_row("fx", passed=True)]),
        _snap("r2", [_row("fx", passed=False)]),
        _snap("r3", [_row("fx", passed=False)]),
    ]
    merged = merge_snapshots(runs)
    assert merged.fixtures[0].passed is False


def test_majority_pass_even_runs_requires_strict_majority() -> None:
    """With 4 runs, exactly 2/4 (tie) is NOT majority; needs >= 3/4."""
    runs = [
        _snap("r1", [_row("fx", passed=True)]),
        _snap("r2", [_row("fx", passed=True)]),
        _snap("r3", [_row("fx", passed=False)]),
        _snap("r4", [_row("fx", passed=False)]),
    ]
    merged = merge_snapshots(runs)
    # threshold = 4//2 + 1 = 3 -> 2/4 fails majority
    assert merged.fixtures[0].passed is False


def test_majority_loaded_set_filters_speculative() -> None:
    """Q2: a rule loaded in only one of three runs is dropped from merged loaded."""
    runs = [
        _snap("r1", [_row("fx", loaded=("rules/A.md", "rules/B.md"))]),
        _snap("r2", [_row("fx", loaded=("rules/A.md",))]),
        _snap("r3", [_row("fx", loaded=("rules/A.md",))]),
    ]
    merged = merge_snapshots(runs)
    # A in 3/3 -> kept; B in 1/3 -> dropped
    assert merged.fixtures[0].loaded == ("rules/A.md",)


def test_majority_loaded_set_keeps_2_of_3() -> None:
    """A rule loaded in 2 of 3 runs is kept (strict majority)."""
    runs = [
        _snap("r1", [_row("fx", loaded=("rules/A.md", "rules/B.md"))]),
        _snap("r2", [_row("fx", loaded=("rules/A.md", "rules/B.md"))]),
        _snap("r3", [_row("fx", loaded=("rules/A.md",))]),
    ]
    merged = merge_snapshots(runs)
    assert "rules/B.md" in merged.fixtures[0].loaded


def test_fill_from_available_runs_when_fixture_missing() -> None:
    """Q3: a fixture present in 2 of 3 runs is included; majority computed over the 2."""
    # fx-a only in run1 + run2; fx-b only in run3.
    runs = [
        _snap("r1", [_row("fx-a", passed=True), _row("fx-shared", passed=True)]),
        _snap("r2", [_row("fx-a", passed=False), _row("fx-shared", passed=True)]),
        _snap("r3", [_row("fx-b", passed=True), _row("fx-shared", passed=True)]),
    ]
    merged = merge_snapshots(runs)
    ids = {f.fixture_id for f in merged.fixtures}
    assert "fx-a" in ids
    assert "fx-b" in ids
    assert "fx-shared" in ids
    by_id = {f.fixture_id: f for f in merged.fixtures}
    # fx-a: 1/2 passing -> threshold = 2//2 + 1 = 2 -> not majority
    assert by_id["fx-a"].passed is False
    # fx-b: 1/1 passing -> threshold = 1//2 + 1 = 1 -> majority
    assert by_id["fx-b"].passed is True


def test_median_numerics_robust_to_outlier() -> None:
    """Q4: median ignores a single slow run that would dominate the mean."""
    runs = [
        _snap("r1", [_row("fx", turns=3, duration_ms=500)]),
        _snap("r2", [_row("fx", turns=3, duration_ms=500)]),
        _snap("r3", [_row("fx", turns=20, duration_ms=50000)]),  # outlier
    ]
    merged = merge_snapshots(runs)
    assert merged.fixtures[0].turns == 3
    assert merged.fixtures[0].duration_ms == 500


def test_median_for_signal_and_citation_drifts() -> None:
    """Median is also applied to signal_disagreements and citation_drifts."""
    runs = [
        _snap("r1", [_row("fx", signal=0, citation=0)]),
        _snap("r2", [_row("fx", signal=5, citation=1)]),
        _snap("r3", [_row("fx", signal=0, citation=0)]),
    ]
    merged = merge_snapshots(runs)
    assert merged.fixtures[0].signal_disagreements == 0
    assert merged.fixtures[0].citation_drifts == 0


def test_merged_meta_records_source_labels() -> None:
    """The merged meta.notes lists every input run's label."""
    runs = [
        _snap("r1", [_row("fx")]),
        _snap("r2", [_row("fx")]),
    ]
    merged = merge_snapshots(runs, label="my-merged")
    assert merged.meta.label == "my-merged"
    assert "r1" in merged.meta.notes
    assert "r2" in merged.meta.notes


def test_render_merge_summary_includes_fixture_count() -> None:
    """The summary renderer reports the merged fixture count."""
    runs = [_snap("r1", [_row("a"), _row("b")]), _snap("r2", [_row("a"), _row("b")])]
    merged = merge_snapshots(runs)
    lines = render_merge_summary(merged, 2)
    assert any("merged 2 run" in ln for ln in lines)
    assert any("2 fixture" in ln for ln in lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_merge_writes_snapshot(tmp_path: Path) -> None:
    """CLI: merge-snapshots produces a readable snapshot directory."""
    base1 = tmp_path / "base1"
    base2 = tmp_path / "base2"
    out = tmp_path / "merged"

    write_eval_snapshot(base1, [_row("a", passed=True)], SnapshotMeta(label="run-1"))
    write_eval_snapshot(base2, [_row("a", passed=True)], SnapshotMeta(label="run-2"))

    result = runner.invoke(
        app,
        [
            "rule-loader",
            "merge-snapshots",
            str(base1),
            str(base2),
            "-o",
            str(out),
            "--label",
            "merged-test",
        ],
    )
    assert result.exit_code == 0, result.output

    # Output directory has expected new-layout files.
    assert (out / "manifest.json").is_file()
    assert (out / "summary.json").is_file()
    assert (out / "run-01" / "summary.json").is_file()
    assert (out / "run-01" / "fixtures" / "a.json").is_file()

    # And it round-trips through read_eval_snapshot.
    snap = read_eval_snapshot(out)
    assert snap.meta.label == "merged-test"
    assert len(snap.fixtures) == 1


def test_cli_merge_requires_at_least_two_dirs(tmp_path: Path) -> None:
    """Single input dir is rejected (no point merging one)."""
    base1 = tmp_path / "base1"
    write_eval_snapshot(base1, [_row("a")], SnapshotMeta(label="run-1"))
    result = runner.invoke(
        app,
        [
            "rule-loader",
            "merge-snapshots",
            str(base1),
            "-o",
            str(tmp_path / "merged"),
        ],
    )
    assert result.exit_code == 4, result.output


def test_cli_merge_then_compare_round_trip(tmp_path: Path) -> None:
    """Merge two flake-y baseline runs, then compare against a clean post snapshot.

    This is the headline workflow: take 3+ noisy baselines, merge to a stable
    reference, compare against post-change. Verify the merged snapshot is
    consumable by the compare command.
    """
    base1 = tmp_path / "base1"
    base2 = tmp_path / "base2"
    base3 = tmp_path / "base3"
    merged = tmp_path / "merged"
    post = tmp_path / "post"

    # Three baseline runs: fixture 'fx' passes in 2 of 3.
    write_eval_snapshot(base1, [_row("fx", passed=True)], SnapshotMeta(label="b1"))
    write_eval_snapshot(base2, [_row("fx", passed=True)], SnapshotMeta(label="b2"))
    write_eval_snapshot(base3, [_row("fx", passed=False)], SnapshotMeta(label="b3"))
    # Post run: fx still passes (no regression).
    write_eval_snapshot(post, [_row("fx", passed=True)], SnapshotMeta(label="post"))

    merge_result = runner.invoke(
        app,
        [
            "rule-loader",
            "merge-snapshots",
            str(base1),
            str(base2),
            str(base3),
            "-o",
            str(merged),
        ],
    )
    assert merge_result.exit_code == 0, merge_result.output

    compare_result = runner.invoke(app, ["rule-loader", "compare", str(merged), str(post)])
    # Merged baseline says 'fx' passes (2/3 majority); post also passes -> exit 0.
    assert compare_result.exit_code == 0, compare_result.output


def _row_with_signals(
    fixture_id: str,
    *,
    loaded_via_reads: tuple[str, ...],
    loaded_via_section: tuple[str, ...],
    disagreement_details: tuple[str, ...] = (),
) -> FixtureSnapshot:
    """Helper for signal-investigation merge tests."""
    return FixtureSnapshot(
        fixture_id=fixture_id,
        passed=True,
        loaded=tuple(sorted(set(loaded_via_reads) | set(loaded_via_section))),
        expected_required=("rules/999-test-core.md",),
        expected_dependencies=(),
        expected_optional=(),
        expected_forbidden=(),
        missing_required=(),
        missing_dependencies=(),
        forbidden_present=(),
        signal_disagreements=len(disagreement_details),
        citation_drifts=0,
        turns=3,
        duration_ms=500,
        loaded_via_reads=loaded_via_reads,
        loaded_via_section=loaded_via_section,
        disagreement_details=disagreement_details,
    )


def test_merge_aggregates_signal_fields_strict_majority_and_union() -> None:
    """loaded_via_reads/section use strict majority; disagreement_details unions."""
    # 3 runs. 'X' appears in reads in 2/3 runs (majority); 'Y' in 1/3 (drops).
    # Section: 'X' in all 3, 'Z' in 1/3 (drops).
    # Disagreements: each run has a different message; union should keep all 3.
    rows = [
        _row_with_signals(
            "fx",
            loaded_via_reads=("rules/X.md", "rules/Y.md"),
            loaded_via_section=("rules/X.md",),
            disagreement_details=("only-in-tool-reads-vs-rules-loaded: rules/Y.md",),
        ),
        _row_with_signals(
            "fx",
            loaded_via_reads=("rules/X.md",),
            loaded_via_section=("rules/X.md", "rules/Z.md"),
            disagreement_details=("only-in-rules-loaded-vs-tool-reads: rules/Z.md",),
        ),
        _row_with_signals(
            "fx",
            loaded_via_reads=("rules/X.md",),
            loaded_via_section=("rules/X.md",),
            disagreement_details=("misc: rules/W.md",),
        ),
    ]
    snapshots = [
        Snapshot(meta=SnapshotMeta(label=f"r{i}"), fixtures=(r,), summary=compute_summary([r]))
        for i, r in enumerate(rows)
    ]
    merged = merge_snapshots(snapshots, label="merged")
    fx = merged.fixtures[0]
    # X: 3/3 -> kept. Y: 1/3 -> dropped. Strict-majority threshold = 2.
    assert fx.loaded_via_reads == ("rules/X.md",)
    # Section: X 3/3 kept; Z 1/3 dropped.
    assert fx.loaded_via_section == ("rules/X.md",)
    # Disagreement details: union across runs (sorted).
    assert set(fx.disagreement_details) == {
        "only-in-tool-reads-vs-rules-loaded: rules/Y.md",
        "only-in-rules-loaded-vs-tool-reads: rules/Z.md",
        "misc: rules/W.md",
    }


def test_merge_signal_fields_round_trip_through_disk(tmp_path: Path) -> None:
    """Persisted signal fields survive write -> read -> merge -> write."""
    r1 = tmp_path / "r1"
    r2 = tmp_path / "r2"
    merged = tmp_path / "merged"
    write_eval_snapshot(
        r1,
        [
            _row_with_signals(
                "fx",
                loaded_via_reads=("rules/A.md",),
                loaded_via_section=("rules/A.md",),
                disagreement_details=("d1",),
            )
        ],
        SnapshotMeta(label="r1"),
    )
    write_eval_snapshot(
        r2,
        [
            _row_with_signals(
                "fx",
                loaded_via_reads=("rules/A.md",),
                loaded_via_section=("rules/A.md",),
                disagreement_details=("d2",),
            )
        ],
        SnapshotMeta(label="r2"),
    )
    s1 = read_eval_snapshot(r1)
    s2 = read_eval_snapshot(r2)
    merged_snap = merge_snapshots([s1, s2], label="merged")
    write_eval_snapshot(merged, list(merged_snap.fixtures), merged_snap.meta)
    reread = read_eval_snapshot(merged)
    fx = reread.fixtures[0]
    assert fx.loaded_via_reads == ("rules/A.md",)
    assert fx.loaded_via_section == ("rules/A.md",)
    assert set(fx.disagreement_details) == {"d1", "d2"}
