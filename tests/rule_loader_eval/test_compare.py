"""Unit tests for the snapshot-comparison engine."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.compare import (
    EXIT_DRIFT_ONLY,
    EXIT_NO_CHANGE,
    EXIT_REGRESSION,
    _classify_added,
    _classify_removed,
    _detect_universal_churn,
    compare_snapshots,
    parse_alias_map,
    render_json,
    render_markdown,
    render_merge_summary,
    render_table,
)
from ai_rules.rule_loader_eval.snapshot import (
    FixtureSnapshot,
    Snapshot,
    SnapshotMeta,
    compute_summary,
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
    expected_required: tuple[str, ...] = ("rules/999-test-core.md",),
    expected_dependencies: tuple[str, ...] = (),
    expected_optional: tuple[str, ...] = (),
    missing_required: tuple[str, ...] = (),
    missing_dependencies: tuple[str, ...] = (),
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_tokens: int = 0,
    total_cost_usd: float = 0.0,
) -> FixtureSnapshot:
    return FixtureSnapshot(
        fixture_id=fixture_id,
        passed=passed,
        loaded=loaded,
        expected_required=expected_required,
        expected_dependencies=expected_dependencies,
        expected_optional=expected_optional,
        expected_forbidden=(),
        missing_required=missing_required,
        missing_dependencies=missing_dependencies,
        forbidden_present=(),
        signal_disagreements=signal,
        citation_drifts=citation,
        turns=turns,
        duration_ms=duration_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        total_cost_usd=total_cost_usd,
    )


def _snapshot(label: str, rows: list[FixtureSnapshot]) -> Snapshot:
    return Snapshot(
        meta=SnapshotMeta(label=label),
        fixtures=tuple(rows),
        summary=compute_summary(rows),
    )


def test_identical_snapshots_yield_no_change() -> None:
    """Comparing a snapshot to itself yields exit 0 and zero deltas."""
    rows = [_row("a"), _row("b"), _row("c")]
    s = _snapshot("baseline", rows)
    report = compare_snapshots(s, s)
    assert report.exit_code == EXIT_NO_CHANGE
    assert report.regressions == ()
    assert report.improvements == ()
    assert report.drift_only == ()


def test_pass_to_fail_is_regression() -> None:
    """A pass→fail transition produces exit 1 and lists the fixture under regressions."""
    base = _snapshot("base", [_row("regressing", passed=True)])
    post = _snapshot("post", [_row("regressing", passed=False)])
    report = compare_snapshots(base, post)
    assert report.exit_code == EXIT_REGRESSION
    assert len(report.regressions) == 1
    assert report.regressions[0].fixture_id == "regressing"


def test_fail_to_pass_is_improvement() -> None:
    """A fail→pass transition lists the fixture under improvements (not regression)."""
    base = _snapshot("base", [_row("improving", passed=False)])
    post = _snapshot("post", [_row("improving", passed=True)])
    report = compare_snapshots(base, post)
    # No regressions, no drift on loaded set => exit 0.
    assert report.exit_code == EXIT_NO_CHANGE
    assert len(report.improvements) == 1


def test_load_drift_without_pass_change_yields_drift_only_exit() -> None:
    """Loaded-set membership change with same pass status yields exit 2."""
    base = _snapshot("base", [_row("drifting", loaded=("rules/A.md",))])
    post = _snapshot("post", [_row("drifting", loaded=("rules/A.md", "rules/B.md"))])
    report = compare_snapshots(base, post)
    assert report.exit_code == EXIT_DRIFT_ONLY
    assert len(report.drift_only) == 1
    delta = report.drift_only[0]
    assert delta.loaded_added == ("rules/B.md",)
    assert delta.loaded_removed == ()


def test_alias_map_neutralizes_rename() -> None:
    """An alias map maps baseline.loaded entries before the diff."""
    base = _snapshot("base", [_row("aliased", loaded=("rules/old.md",))])
    post = _snapshot("post", [_row("aliased", loaded=("rules/new.md",))])
    report = compare_snapshots(base, post, alias_map={"rules/old.md": "rules/new.md"})
    assert report.exit_code == EXIT_NO_CHANGE
    # No drift recorded because alias normalised it.
    assert all(not d.has_load_drift for d in report.deltas)


def test_aggregate_metrics() -> None:
    """Aggregate counts (loaded added/removed, signal/citation deltas) are correct."""
    base = _snapshot(
        "base",
        [
            _row("a", loaded=("rules/A.md",), signal=1, citation=2, turns=3, duration_ms=500),
            _row("b", loaded=("rules/A.md",), signal=0, citation=0, turns=2, duration_ms=400),
        ],
    )
    post = _snapshot(
        "post",
        [
            _row(
                "a",
                loaded=("rules/A.md", "rules/B.md"),
                signal=0,
                citation=0,
                turns=2,
                duration_ms=300,
            ),
            _row("b", loaded=(), signal=0, citation=0, turns=1, duration_ms=200),
        ],
    )
    report = compare_snapshots(base, post)
    assert report.total_loaded_added == 1  # +B.md in fixture a
    assert report.total_loaded_removed == 1  # -A.md in fixture b
    assert report.total_signal_disagreements_delta == -1
    assert report.total_citation_drifts_delta == -2
    # Mean turns delta = ((-1) + (-1)) / 2 = -1.0
    assert report.mean_turns_delta == -1.0


def test_fixtures_only_in_one_side_listed_separately() -> None:
    """Fixtures present only in baseline or post are reported under their own buckets."""
    base = _snapshot("base", [_row("shared"), _row("only-base")])
    post = _snapshot("post", [_row("shared"), _row("only-post")])
    report = compare_snapshots(base, post)
    assert report.fixtures_only_in_baseline == ("only-base",)
    assert report.fixtures_only_in_post == ("only-post",)
    # Orphaned fixtures don't trigger regression on their own (the shared
    # fixtures are still pass->pass with no drift).
    assert report.exit_code == EXIT_DRIFT_ONLY


def test_render_table_includes_pass_rate_line() -> None:
    """The text-table renderer includes a pass-rate summary line."""
    rows = [_row("a"), _row("b", passed=False)]
    base = _snapshot("base", rows)
    post = _snapshot("post", [_row("a"), _row("b")])
    report = compare_snapshots(base, post)
    lines = render_table(report)
    assert any("pass rate" in ln for ln in lines)
    # 1/2 -> 2/2 pass rate.
    assert any("1/2" in ln and "2/2" in ln for ln in lines)


def test_render_json_is_parseable() -> None:
    """The JSON renderer emits a parseable object with expected top-level keys."""
    base = _snapshot("base", [_row("a")])
    post = _snapshot("post", [_row("a")])
    report = compare_snapshots(base, post)
    parsed = json.loads(render_json(report))
    for key in (
        "baseline_label",
        "post_label",
        "baseline_pass_rate",
        "post_pass_rate",
        "regressions",
        "improvements",
        "drift_only",
        "deltas",
    ):
        assert key in parsed


def test_render_markdown_includes_metric_table() -> None:
    """The markdown renderer emits a markdown table header."""
    base = _snapshot("base", [_row("a")])
    post = _snapshot("post", [_row("a")])
    report = compare_snapshots(base, post)
    lines = render_markdown(report)
    assert any("|" in ln and "metric" in ln for ln in lines)


def test_parse_alias_map_reads_json(tmp_path: Path) -> None:
    """parse_alias_map reads a JSON file into a dict[str, str]."""
    p = tmp_path / "aliases.json"
    p.write_text(json.dumps({"rules/old.md": "rules/new.md"}), encoding="utf-8")
    out = parse_alias_map(p)
    assert out == {"rules/old.md": "rules/new.md"}


def test_parse_alias_map_none_returns_empty() -> None:
    """parse_alias_map(None) returns an empty dict."""
    assert parse_alias_map(None) == {}


def test_parse_alias_map_rejects_non_object(tmp_path: Path) -> None:
    """parse_alias_map raises when the JSON root is not a dict."""
    p = tmp_path / "bad.json"
    p.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="must be an object"):
        parse_alias_map(p)


# ---------------------------------------------------------------------------
# VERDICT block
# ---------------------------------------------------------------------------


def test_verdict_block_regression() -> None:
    base = _snapshot("base", [_row("r", passed=True)])
    post = _snapshot("post", [_row("r", passed=False)])
    report = compare_snapshots(base, post)
    lines = render_table(report)
    assert lines[0].startswith("VERDICT: REGRESSION")


def test_verdict_block_improvement() -> None:
    base = _snapshot("base", [_row("r", passed=False)])
    post = _snapshot("post", [_row("r", passed=True)])
    report = compare_snapshots(base, post)
    lines = render_table(report)
    assert lines[0].startswith("VERDICT: IMPROVEMENT")


def test_verdict_block_drift_only() -> None:
    base = _snapshot("base", [_row("d", loaded=("rules/A.md",))])
    post = _snapshot("post", [_row("d", loaded=("rules/B.md",))])
    report = compare_snapshots(base, post)
    lines = render_table(report)
    assert lines[0].startswith("VERDICT: DRIFT ONLY")


def test_verdict_block_clean() -> None:
    rows = [_row("a"), _row("b")]
    report = compare_snapshots(_snapshot("base", rows), _snapshot("post", rows))
    lines = render_table(report)
    assert lines[0].startswith("VERDICT: CLEAN")


# ---------------------------------------------------------------------------
# Universal churn detection and suppression
# ---------------------------------------------------------------------------


def test_universal_churn_detected_and_suppressed() -> None:
    """Rule removed from all fixtures appears in header note, NOT in delta blocks (default)."""
    churn_rule = "rules/GONE.md"
    base_rows = [
        _row("a", loaded=(churn_rule, "rules/999-test-core.md")),
        _row("b", loaded=(churn_rule, "rules/999-test-core.md")),
    ]
    post_rows = [_row("a"), _row("b")]
    report = compare_snapshots(_snapshot("base", base_rows), _snapshot("post", post_rows))
    lines = render_table(report)
    joined = "\n".join(lines)
    assert churn_rule in joined
    assert "universal churn" in joined
    assert "suppressed from per-fixture blocks" in joined
    for line in lines:
        if "-loaded:" in line:
            assert churn_rule not in line, (
                "churn rule must not appear in per-fixture blocks by default"
            )


def test_universal_churn_shown_with_verbose() -> None:
    """With verbose=True, churn rule appears in per-fixture blocks tagged [expected-deletion]."""
    churn_rule = "rules/GONE.md"
    base_rows = [_row("a", loaded=(churn_rule,)), _row("b", loaded=(churn_rule,))]
    post_rows = [_row("a", loaded=()), _row("b", loaded=())]
    report = compare_snapshots(_snapshot("base", base_rows), _snapshot("post", post_rows))
    lines = render_table(report, verbose=True)
    joined = "\n".join(lines)
    assert "[expected-deletion]" in joined
    assert "shown below because --verbose" in joined


def test_detect_universal_churn_threshold() -> None:
    """_detect_universal_churn uses >= 80% threshold by default."""
    churn_rule = "rules/X.md"
    base_rows = [
        _row("a", loaded=(churn_rule,)),
        _row("b", loaded=(churn_rule,)),
        _row("c", loaded=(churn_rule,)),
        _row("d", loaded=(churn_rule,)),
        _row("e", loaded=()),
    ]
    post_rows = [_row("a"), _row("b"), _row("c"), _row("d"), _row("e")]
    report = compare_snapshots(_snapshot("base", base_rows), _snapshot("post", post_rows))
    churn = _detect_universal_churn(report)
    assert churn_rule in churn


def test_detect_universal_churn_below_threshold_not_detected() -> None:
    """Rule removed from fewer than 80% of fixtures is not classified as universal churn."""
    partial_rule = "rules/PARTIAL.md"
    base_rows = [
        _row("a", loaded=(partial_rule,)),
        _row("b", loaded=()),
        _row("c", loaded=()),
        _row("d", loaded=()),
    ]
    post_rows = [_row("a"), _row("b"), _row("c"), _row("d")]
    report = compare_snapshots(_snapshot("base", base_rows), _snapshot("post", post_rows))
    churn = _detect_universal_churn(report)
    assert partial_rule not in churn


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------


def test_classify_removed_missing_required() -> None:
    post = _row("x", missing_required=("rules/A.md",))
    assert _classify_removed("rules/A.md", post) == "[missing-required]"


def test_classify_removed_missing_dep() -> None:
    post = _row("x", missing_dependencies=("rules/B.md",))
    assert _classify_removed("rules/B.md", post) == "[missing-dep]"


def test_classify_removed_universal_churn() -> None:
    post = _row("x")
    assert _classify_removed("rules/C.md", post, is_universal_churn=True) == "[expected-deletion]"


def test_classify_removed_no_tag() -> None:
    post = _row("x")
    assert _classify_removed("rules/D.md", post) == ""


def test_classify_added_spurious() -> None:
    post = _row("x", expected_required=("rules/A.md",))
    assert _classify_added("rules/UNRELATED.md", post) == "[spurious]"


def test_classify_added_expected_not_spurious() -> None:
    post = _row("x", expected_required=("rules/A.md",))
    assert _classify_added("rules/A.md", post) == ""


# ---------------------------------------------------------------------------
# Per-regression fix hints
# ---------------------------------------------------------------------------


def test_regression_fix_hint_missing_required() -> None:
    """A removed [missing-required] rule generates a → fix: hint."""
    missing = "rules/109b.md"
    base = _snapshot(
        "base",
        [
            _row("r", passed=True, loaded=("rules/999-test-core.md", missing)),
            _row("ok", passed=True, loaded=("rules/999-test-core.md", missing)),
        ],
    )
    post = _snapshot(
        "post",
        [
            _row(
                "r",
                passed=False,
                loaded=("rules/999-test-core.md",),
                expected_required=("rules/999-test-core.md", missing),
                missing_required=(missing,),
            ),
            _row("ok", loaded=("rules/999-test-core.md", missing)),
        ],
    )
    report = compare_snapshots(base, post)
    lines = render_table(report)
    joined = "\n".join(lines)
    assert "→ fix: add kw: trigger to" in joined
    assert missing in joined


def test_regression_fix_hint_spurious() -> None:
    """A loaded [spurious] rule generates a → fix: hint."""
    spurious = "rules/102a.md"
    base = _snapshot("base", [_row("r", passed=True, loaded=("rules/999-test-core.md",))])
    post = _snapshot(
        "post",
        [
            _row(
                "r",
                passed=False,
                loaded=("rules/999-test-core.md", spurious),
                expected_required=("rules/999-test-core.md",),
            )
        ],
    )
    report = compare_snapshots(base, post)
    lines = render_table(report)
    joined = "\n".join(lines)
    assert "→ fix: narrow kw: triggers in" in joined
    assert spurious in joined


# ---------------------------------------------------------------------------
# Drift-only section collapse
# ---------------------------------------------------------------------------


def test_drift_only_collapsed_default() -> None:
    """drift_only section shows a one-line summary when verbose=False."""
    base = _snapshot("base", [_row("d", loaded=("rules/A.md",))])
    post = _snapshot("post", [_row("d", loaded=("rules/B.md",))])
    report = compare_snapshots(base, post)
    lines = render_table(report)
    joined = "\n".join(lines)
    assert "--verbose to expand" in joined
    assert "load-drift only" not in joined


def test_drift_only_expanded_verbose() -> None:
    """drift_only section shows full per-fixture blocks when verbose=True."""
    base = _snapshot("base", [_row("d", loaded=("rules/A.md",))])
    post = _snapshot("post", [_row("d", loaded=("rules/B.md",))])
    report = compare_snapshots(base, post)
    lines = render_table(report, verbose=True)
    joined = "\n".join(lines)
    assert "load-drift only" in joined
    assert "d  [pass->pass]" in joined


# ---------------------------------------------------------------------------
# Token / cost delta tests
# ---------------------------------------------------------------------------


def test_token_delta_computed_in_compute_delta() -> None:
    """_compute_delta produces correct token and cost deltas."""
    from ai_rules.rule_loader_eval.compare import _compute_delta

    base = _row("fx", input_tokens=1000, output_tokens=200, total_tokens=1200, total_cost_usd=0.010)
    post_row = _row(
        "fx", input_tokens=1500, output_tokens=300, total_tokens=1800, total_cost_usd=0.015
    )
    delta = _compute_delta(base, post_row, {})
    assert delta.input_tokens_delta == 500
    assert delta.output_tokens_delta == 100
    assert delta.total_tokens_delta == 600
    assert abs(delta.total_cost_usd_delta - 0.005) < 1e-9


def test_merge_fixture_rows_includes_token_fields() -> None:
    """_merge_fixture_rows aggregates token/cost fields (not silently zeroed)."""
    from ai_rules.rule_loader_eval.compare import _merge_fixture_rows

    rows = [
        _row("fx", input_tokens=1000, output_tokens=200, total_tokens=1200, total_cost_usd=0.010),
        _row("fx", input_tokens=1200, output_tokens=250, total_tokens=1450, total_cost_usd=0.012),
        _row("fx", input_tokens=1100, output_tokens=220, total_tokens=1320, total_cost_usd=0.011),
    ]
    merged = _merge_fixture_rows("fx", rows)
    # Median of [1000, 1100, 1200] = 1100
    assert merged.input_tokens == 1100
    # Median of [200, 220, 250] = 220
    assert merged.output_tokens == 220
    # total_tokens median of [1200, 1320, 1450] = 1320
    assert merged.total_tokens == 1320
    # cost median of [0.010, 0.011, 0.012] = 0.011
    assert abs(merged.total_cost_usd - 0.011) < 1e-9


def test_compare_snapshots_token_deltas_end_to_end() -> None:
    """compare_snapshots propagates token deltas and render_table shows tokens: line."""
    base = _snapshot(
        "base",
        [
            _row("a", input_tokens=1000, output_tokens=200, total_tokens=1200),
            _row("b", input_tokens=800, output_tokens=150, total_tokens=950),
        ],
    )
    post = _snapshot(
        "post",
        [
            _row("a", input_tokens=1200, output_tokens=250, total_tokens=1450),
            _row("b", input_tokens=900, output_tokens=180, total_tokens=1080),
        ],
    )
    report = compare_snapshots(base, post)
    assert report.mean_input_tokens_delta == 150.0
    assert report.mean_output_tokens_delta == 40.0
    assert report.mean_total_tokens_delta == 190.0

    lines = render_table(report)
    joined = "\n".join(lines)
    assert "tokens:" in joined


def test_render_table_suppresses_token_line_when_no_data() -> None:
    """render_table omits the tokens: line when all token counts are zero."""
    rows = [_row("a"), _row("b")]
    report = compare_snapshots(_snapshot("base", rows), _snapshot("post", rows))
    lines = render_table(report)
    joined = "\n".join(lines)
    assert "tokens:" not in joined


def test_render_merge_summary_shows_token_lines_when_data_present() -> None:
    """render_merge_summary includes median token lines when tokens are non-zero."""
    rows = [
        _row("a", input_tokens=1000, output_tokens=200, total_tokens=1200),
        _row("b", input_tokens=800, output_tokens=150, total_tokens=950),
    ]
    snap = _snapshot("merged", rows)
    lines = render_merge_summary(snap, n_inputs=2)
    joined = "\n".join(lines)
    assert "median input tokens" in joined
    assert "median output tokens" in joined


def test_render_merge_summary_suppresses_token_lines_when_zero() -> None:
    """render_merge_summary omits token lines when all tokens are zero."""
    rows = [_row("a"), _row("b")]
    snap = _snapshot("merged", rows)
    lines = render_merge_summary(snap, n_inputs=2)
    joined = "\n".join(lines)
    assert "median input tokens" not in joined
