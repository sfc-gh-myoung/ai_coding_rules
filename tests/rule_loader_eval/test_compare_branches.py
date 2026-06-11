"""Branch-coverage tests for rule_loader_eval/compare.py.

Targets uncovered lines: fail->fail, infra, skill_invocations, depends_violations,
flaky, render_markdown, _md_delta_block, _render_delta_block with rules_meta,
_kw_evidence_for_rule, merge_snapshots, _compute_flake_score, render_merge_summary.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.compare import (
    _compute_flake_score,
    _detect_universal_churn,
    _kw_evidence_for_rule,
    _md_delta_block,
    _render_delta_block,
    compare_snapshots,
    iter_lines,
    merge_snapshots,
    parse_alias_map,
    render_markdown,
    render_merge_summary,
    render_table,
)
from ai_rules.rule_loader_eval.rules_meta import RuleMetadata
from ai_rules.rule_loader_eval.snapshot import (
    FixtureSnapshot,
    Snapshot,
    SnapshotMeta,
    compute_summary,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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
    is_infra_error: bool = False,
    infra_error_detail: str = "",
    flake_score: float = 0.0,
    skill_invocations: tuple[str, ...] = (),
    depends_violations: tuple[str, ...] = (),
    n_runs: int = 1,
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
        is_infra_error=is_infra_error,
        infra_error_detail=infra_error_detail,
        flake_score=flake_score,
        skill_invocations=skill_invocations,
        depends_violations=depends_violations,
        n_runs=n_runs,
    )


def _snap(label: str, rows: list[FixtureSnapshot]) -> Snapshot:
    return Snapshot(
        meta=SnapshotMeta(label=label),
        fixtures=tuple(rows),
        summary=compute_summary(rows),
    )


# ---------------------------------------------------------------------------
# fail->fail branch in _compute_delta (line 283)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_fail_to_fail_pass_delta() -> None:
    base = _snap("base", [_row("x", passed=False)])
    post = _snap("post", [_row("x", passed=False)])
    report = compare_snapshots(base, post)
    assert report.regressions == ()
    assert report.improvements == ()
    assert report.deltas[0].pass_delta == "fail->fail"


# ---------------------------------------------------------------------------
# is_infra_error branch (line 63) — infra fixtures not counted as regressions
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_infra_error_not_counted_as_regression() -> None:
    base = _snap("base", [_row("x", passed=True)])
    post = _snap(
        "post", [_row("x", passed=False, is_infra_error=True, infra_error_detail="timeout")]
    )
    report = compare_snapshots(base, post)
    assert report.regressions == ()
    assert len(report.infra) == 1
    assert not report.deltas[0].is_regression
    assert report.deltas[0].is_infra


@pytest.mark.unit
def test_render_table_infra_section() -> None:
    base = _snap("base", [_row("x", passed=True)])
    post = _snap(
        "post", [_row("x", passed=False, is_infra_error=True, infra_error_detail="SDK down")]
    )
    report = compare_snapshots(base, post)
    lines = render_table(report)
    joined = "\n".join(lines)
    assert "INFRA" in joined
    assert "SDK down" in joined


# ---------------------------------------------------------------------------
# Flaky section in render_table (lines 431-435)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_table_flaky_section() -> None:
    # flake_score >= threshold (0.50) makes a fixture flaky
    base = _snap("base", [_row("f", flake_score=0.75)])
    post = _snap("post", [_row("f", flake_score=0.75)])
    report = compare_snapshots(base, post, flake_threshold=0.50)
    lines = render_table(report)
    joined = "\n".join(lines)
    assert "FLAKY" in joined
    assert "flake_score" in joined


@pytest.mark.unit
def test_flaky_excluded_from_regressions_when_ignore_flaky() -> None:
    base = _snap("base", [_row("f", passed=True, flake_score=0.80)])
    post = _snap("post", [_row("f", passed=False, flake_score=0.80)])
    report = compare_snapshots(base, post, flake_threshold=0.50, ignore_flaky=True)
    assert report.regressions == ()
    assert len(report.flaky) == 1


# ---------------------------------------------------------------------------
# SKILL_NOT_INVOKED verdict (line 326)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_verdict_skill_not_invoked() -> None:
    # Need >=1 post fixture with skill_invocations (triggers has_invocation_data=True)
    # but post_skill_invocations < n_total
    base_rows = [_row("a"), _row("b")]
    post_rows = [
        _row("a", skill_invocations=("rule-loader",)),
        _row("b", skill_invocations=()),  # no invocation → post < total
    ]
    report = compare_snapshots(_snap("base", base_rows), _snap("post", post_rows))
    lines = render_table(report)
    assert lines[0].startswith("VERDICT: SKILL_NOT_INVOKED")


# ---------------------------------------------------------------------------
# Skill invocation display lines (lines 364-372)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_table_skill_invocation_partial() -> None:
    """Partial invocation: some post fixtures missing rule-loader skill."""
    base_rows = [
        _row("a", skill_invocations=("rule-loader",)),
        _row("b", skill_invocations=("rule-loader",)),
    ]
    post_rows = [
        _row("a", skill_invocations=("rule-loader",)),
        _row("b", skill_invocations=()),
    ]
    report = compare_snapshots(_snap("base", base_rows), _snap("post", post_rows))
    lines = render_table(report)
    joined = "\n".join(lines)
    assert "rule-loader invoked" in joined
    assert "SKILL_NOT_INVOKED" in joined


@pytest.mark.unit
def test_render_table_skill_invocation_all_present() -> None:
    """All fixtures have invocation data and count matches total."""
    rows = [
        _row("a", skill_invocations=("rule-loader",)),
        _row("b", skill_invocations=("rule-loader",)),
    ]
    report = compare_snapshots(_snap("base", rows), _snap("post", rows))
    lines = render_table(report)
    joined = "\n".join(lines)
    assert "rule-loader invoked" in joined
    assert "SKILL_NOT_INVOKED" not in joined


# ---------------------------------------------------------------------------
# depends violations in render_table (line 378)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_table_depends_violations_r8() -> None:
    base = _snap("base", [_row("x")])
    post = _snap("post", [_row("x", depends_violations=("R8: rules/dep.md missing",))])
    report = compare_snapshots(base, post)
    lines = render_table(report)
    joined = "\n".join(lines)
    assert "depends:" in joined
    assert "R8 VIOLATIONS" in joined


# ---------------------------------------------------------------------------
# render_markdown — verdict branches (lines 478, 480, 482)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_markdown_improvement_verdict() -> None:
    base = _snap("base", [_row("x", passed=False)])
    post = _snap("post", [_row("x", passed=True)])
    report = compare_snapshots(base, post)
    lines = render_markdown(report)
    joined = "\n".join(lines)
    assert "IMPROVEMENT" in joined


@pytest.mark.unit
def test_render_markdown_drift_only_verdict() -> None:
    base = _snap("base", [_row("x", loaded=("rules/A.md",))])
    post = _snap("post", [_row("x", loaded=("rules/B.md",))])
    report = compare_snapshots(base, post)
    lines = render_markdown(report)
    joined = "\n".join(lines)
    assert "DRIFT ONLY" in joined


@pytest.mark.unit
def test_render_markdown_clean_verdict() -> None:
    rows = [_row("x"), _row("y")]
    report = compare_snapshots(_snap("base", rows), _snap("post", rows))
    lines = render_markdown(report)
    joined = "\n".join(lines)
    assert "CLEAN" in joined
    assert "_no per-fixture changes detected_" in joined


# ---------------------------------------------------------------------------
# render_markdown churn note (lines 504-509)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_markdown_churn_note() -> None:
    churn_rule = "rules/DELETED.md"
    base_rows = [_row("a", loaded=(churn_rule,)), _row("b", loaded=(churn_rule,))]
    post_rows = [_row("a", loaded=()), _row("b", loaded=())]
    report = compare_snapshots(_snap("base", base_rows), _snap("post", post_rows))
    lines = render_markdown(report)
    joined = "\n".join(lines)
    assert churn_rule in joined
    assert "universal churn" in joined


# ---------------------------------------------------------------------------
# render_markdown regression/improvement/drift sections (lines 516-532)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_markdown_regression_section() -> None:
    base = _snap("base", [_row("r", passed=True)])
    post = _snap("post", [_row("r", passed=False)])
    report = compare_snapshots(base, post)
    lines = render_markdown(report)
    joined = "\n".join(lines)
    assert "## Regressions" in joined


@pytest.mark.unit
def test_render_markdown_improvement_section() -> None:
    base = _snap("base", [_row("r", passed=False)])
    post = _snap("post", [_row("r", passed=True)])
    report = compare_snapshots(base, post)
    lines = render_markdown(report)
    joined = "\n".join(lines)
    assert "## Improvements" in joined


@pytest.mark.unit
def test_render_markdown_drift_only_collapsed() -> None:
    base = _snap("base", [_row("d", loaded=("rules/A.md",))])
    post = _snap("post", [_row("d", loaded=("rules/B.md",))])
    report = compare_snapshots(base, post)
    lines = render_markdown(report)
    joined = "\n".join(lines)
    assert "--verbose to expand" in joined


@pytest.mark.unit
def test_render_markdown_drift_only_verbose() -> None:
    base = _snap("base", [_row("d", loaded=("rules/A.md",))])
    post = _snap("post", [_row("d", loaded=("rules/B.md",))])
    report = compare_snapshots(base, post)
    lines = render_markdown(report, verbose=True)
    joined = "\n".join(lines)
    assert "## Load-drift only" in joined


# ---------------------------------------------------------------------------
# _render_delta_block with rules_meta and delta details (lines 557-602)
# ---------------------------------------------------------------------------


def _make_rules_meta(rule: str, keywords: list[str]) -> dict[str, RuleMetadata]:
    return {rule: RuleMetadata(path=Path(rule), typed_kw=tuple(keywords))}


@pytest.mark.unit
def test_render_delta_block_signal_detail() -> None:
    base = _snap("base", [_row("x", signal=0)])
    post = _snap("post", [_row("x", signal=2)])
    report = compare_snapshots(base, post)
    d = report.deltas[0]
    lines = _render_delta_block(d, indent="  ")
    joined = "\n".join(lines)
    assert "signal +2" in joined


@pytest.mark.unit
def test_render_delta_block_citation_and_turns_detail() -> None:
    base = _snap("base", [_row("x", citation=0, turns=2, duration_ms=100)])
    post = _snap("post", [_row("x", citation=1, turns=5, duration_ms=300)])
    report = compare_snapshots(base, post)
    d = report.deltas[0]
    lines = _render_delta_block(d, indent="  ")
    joined = "\n".join(lines)
    assert "citation +1" in joined
    assert "turns +3" in joined
    assert "duration +200ms" in joined


@pytest.mark.unit
def test_render_delta_block_spurious_with_rules_meta_firing() -> None:
    """Spurious +loaded with rules_meta that has a matching kw fires evidence line."""
    rule = "rules/102a.md"
    meta = _make_rules_meta(rule, ["sql", "procedure"])
    base = _snap("base", [_row("x", passed=True, loaded=("rules/999-test-core.md",))])
    post = _snap("post", [_row("x", passed=False, loaded=("rules/999-test-core.md", rule))])
    report = compare_snapshots(base, post)
    d = report.deltas[0]
    lines = _render_delta_block(d, rules_meta=meta, fixture_prompt="sql procedure call")
    joined = "\n".join(lines)
    assert "[spurious]" in joined
    assert "fired-on:" in joined


@pytest.mark.unit
def test_render_delta_block_spurious_no_rules_meta() -> None:
    """Spurious +loaded without rules_meta: no fired-on line."""
    rule = "rules/102a.md"
    base = _snap("base", [_row("x", passed=True)])
    post = _snap("post", [_row("x", passed=False, loaded=("rules/999-test-core.md", rule))])
    report = compare_snapshots(base, post)
    d = report.deltas[0]
    lines = _render_delta_block(d)
    joined = "\n".join(lines)
    assert "[spurious]" in joined
    assert "fired-on:" not in joined


@pytest.mark.unit
def test_render_delta_block_missing_required_with_rules_meta_kw() -> None:
    """Missing-required -loaded with matching kw in meta shows current-kw line."""
    rule = "rules/109b.md"
    meta = _make_rules_meta(rule, ["stored procedure"])
    base = _snap("base", [_row("x", passed=True, loaded=("rules/999-test-core.md", rule))])
    post = _snap(
        "post",
        [
            _row(
                "x",
                passed=False,
                loaded=("rules/999-test-core.md",),
                expected_required=("rules/999-test-core.md", rule),
                missing_required=(rule,),
            )
        ],
    )
    report = compare_snapshots(base, post)
    d = report.deltas[0]
    lines = _render_delta_block(d, rules_meta=meta, fixture_prompt="stored procedure call")
    joined = "\n".join(lines)
    assert "[missing-required]" in joined
    assert "current-kw:" in joined


@pytest.mark.unit
def test_render_delta_block_missing_required_no_kw_match() -> None:
    """Missing-required with rules_meta but no matching prompt shows no-kw-match message."""
    rule = "rules/109b.md"
    meta = _make_rules_meta(rule, ["stored procedure"])
    base = _snap("base", [_row("x", passed=True, loaded=("rules/999-test-core.md", rule))])
    post = _snap(
        "post",
        [
            _row(
                "x",
                passed=False,
                loaded=("rules/999-test-core.md",),
                expected_required=("rules/999-test-core.md", rule),
                missing_required=(rule,),
            )
        ],
    )
    report = compare_snapshots(base, post)
    d = report.deltas[0]
    lines = _render_delta_block(d, rules_meta=meta, fixture_prompt="unrelated python request")
    joined = "\n".join(lines)
    assert "no kw: matched prompt" in joined


@pytest.mark.unit
def test_render_delta_block_depends_violation_fix_hint() -> None:
    """depends_violations on a regression produces R8 fix hint."""
    base = _snap("base", [_row("x", passed=True)])
    post = _snap("post", [_row("x", passed=False, depends_violations=("rules/dep.md missing",))])
    report = compare_snapshots(base, post)
    d = report.deltas[0]
    lines = _render_delta_block(d)
    joined = "\n".join(lines)
    assert "R8 violation" in joined


# ---------------------------------------------------------------------------
# _md_delta_block function (lines 612-645)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_md_delta_block_basic_pass_pass() -> None:
    rows = [_row("x")]
    report = compare_snapshots(_snap("base", rows), _snap("post", rows))
    d = report.deltas[0]
    lines = _md_delta_block(d)
    assert any("`pass->pass`" in ln for ln in lines)


@pytest.mark.unit
def test_md_delta_block_with_loaded_added_and_spurious() -> None:
    spurious = "rules/unrelated.md"
    base = _snap("base", [_row("x", passed=True)])
    post = _snap("post", [_row("x", passed=False, loaded=("rules/999-test-core.md", spurious))])
    report = compare_snapshots(base, post)
    d = report.deltas[0]
    lines = _md_delta_block(d)
    joined = "\n".join(lines)
    assert "+loaded:" in joined
    assert "[spurious]" in joined
    assert "→ fix: narrow kw: triggers" in joined


@pytest.mark.unit
def test_md_delta_block_with_loaded_removed_missing_required() -> None:
    rule = "rules/109b.md"
    base = _snap("base", [_row("x", passed=True, loaded=("rules/999-test-core.md", rule))])
    post = _snap(
        "post",
        [
            _row(
                "x",
                passed=False,
                loaded=("rules/999-test-core.md",),
                expected_required=("rules/999-test-core.md", rule),
                missing_required=(rule,),
            )
        ],
    )
    report = compare_snapshots(base, post)
    d = report.deltas[0]
    lines = _md_delta_block(d)
    joined = "\n".join(lines)
    assert "-loaded:" in joined
    assert "[missing-required]" in joined
    assert "→ fix: add kw: trigger to" in joined


@pytest.mark.unit
def test_md_delta_block_with_signal_and_citation_detail() -> None:
    base = _snap("base", [_row("x", signal=1, citation=1, turns=2, duration_ms=200)])
    post = _snap("post", [_row("x", signal=3, citation=2, turns=4, duration_ms=400)])
    report = compare_snapshots(base, post)
    d = report.deltas[0]
    lines = _md_delta_block(d)
    joined = "\n".join(lines)
    assert "signal +2" in joined
    assert "citation +1" in joined
    assert "turns +2" in joined
    assert "duration +200ms" in joined


@pytest.mark.unit
def test_md_delta_block_missing_dep_fix_hint() -> None:
    rule = "rules/dep.md"
    base = _snap("base", [_row("x", passed=True, loaded=("rules/999-test-core.md", rule))])
    post = _snap(
        "post",
        [
            _row(
                "x",
                passed=False,
                loaded=("rules/999-test-core.md",),
                expected_required=("rules/999-test-core.md",),
                expected_dependencies=(rule,),
                missing_dependencies=(rule,),
            )
        ],
    )
    report = compare_snapshots(base, post)
    d = report.deltas[0]
    lines = _md_delta_block(d)
    joined = "\n".join(lines)
    assert "[missing-dep]" in joined
    assert "→ fix: add kw: trigger to" in joined


@pytest.mark.unit
def test_md_delta_block_churn_suppression() -> None:
    """Universal churn rules are suppressed in -loaded blocks by default."""
    churn_rule = "rules/GONE.md"
    base_rows = [_row("a", loaded=(churn_rule,)), _row("b", loaded=(churn_rule,))]
    post_rows = [_row("a", loaded=()), _row("b", loaded=())]
    report = compare_snapshots(_snap("base", base_rows), _snap("post", post_rows))
    from ai_rules.rule_loader_eval.compare import _detect_universal_churn

    churn = _detect_universal_churn(report)
    # churn rule should be suppressed from md delta block
    for d in report.deltas:
        lines = _md_delta_block(d, churn=churn, verbose=False)
        joined = "\n".join(lines)
        assert churn_rule not in joined


@pytest.mark.unit
def test_md_delta_block_churn_verbose() -> None:
    """With verbose=True churn rules appear in -loaded blocks."""
    churn_rule = "rules/GONE.md"
    base_rows = [_row("a", loaded=(churn_rule,)), _row("b", loaded=(churn_rule,))]
    post_rows = [_row("a", loaded=()), _row("b", loaded=())]
    report = compare_snapshots(_snap("base", base_rows), _snap("post", post_rows))
    from ai_rules.rule_loader_eval.compare import _detect_universal_churn

    churn = _detect_universal_churn(report)
    found_any = False
    for d in report.deltas:
        lines = _md_delta_block(d, churn=churn, verbose=True)
        if churn_rule in "\n".join(lines):
            found_any = True
    assert found_any


# ---------------------------------------------------------------------------
# _detect_universal_churn with empty deltas (line 655)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_detect_universal_churn_empty_deltas() -> None:
    # Snapshots with no shared fixtures → empty deltas → empty churn set
    base = _snap("base", [_row("only-base")])
    post = _snap("post", [_row("only-post")])
    report = compare_snapshots(base, post)
    assert report.deltas == ()
    churn = _detect_universal_churn(report)
    assert churn == frozenset()


# ---------------------------------------------------------------------------
# _kw_evidence_for_rule (lines 676-683)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_kw_evidence_rules_meta_none() -> None:
    firing, all_kw = _kw_evidence_for_rule("rules/X.md", "some prompt", None)
    assert firing == []
    assert all_kw == []


@pytest.mark.unit
def test_kw_evidence_rule_not_found() -> None:
    meta = _make_rules_meta("rules/OTHER.md", ["sql"])
    firing, all_kw = _kw_evidence_for_rule("rules/MISSING.md", "sql prompt", meta)
    assert firing == []
    assert all_kw == []


@pytest.mark.unit
def test_kw_evidence_matching_keyword() -> None:
    meta = _make_rules_meta("rules/102.md", ["stored procedure", "sql"])
    firing, all_kw = _kw_evidence_for_rule("rules/102.md", "SQL stored procedure example", meta)
    assert "stored procedure" in firing
    assert "sql" in firing
    assert set(all_kw) == {"stored procedure", "sql"}


@pytest.mark.unit
def test_kw_evidence_no_match() -> None:
    meta = _make_rules_meta("rules/102.md", ["python", "fastapi"])
    firing, all_kw = _kw_evidence_for_rule("rules/102.md", "write a sql query", meta)
    assert firing == []
    assert set(all_kw) == {"python", "fastapi"}


# ---------------------------------------------------------------------------
# parse_alias_map non-string entry validation (line 722)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_parse_alias_map_non_string_value_raises(tmp_path) -> None:
    import json

    p = tmp_path / "bad_types.json"
    p.write_text(json.dumps({"rules/old.md": 42}), encoding="utf-8")
    with pytest.raises(ValueError, match="entries must be strings"):
        parse_alias_map(p)


# ---------------------------------------------------------------------------
# iter_lines (line 729)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_iter_lines_joins_with_newline() -> None:
    result = iter_lines(["line1", "line2", "line3"])
    assert result == "line1\nline2\nline3\n"


@pytest.mark.unit
def test_iter_lines_empty() -> None:
    result = iter_lines([])
    assert result == "\n"


# ---------------------------------------------------------------------------
# merge_snapshots and _merge_fixture_rows (lines 785-875)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_merge_snapshots_single_snapshot() -> None:
    snap = _snap("run1", [_row("a"), _row("b")])
    merged = merge_snapshots([snap], label="merged")
    assert len(merged.fixtures) == 2
    assert merged.meta.label == "merged"


@pytest.mark.unit
def test_merge_snapshots_majority_pass() -> None:
    """With 3 runs, majority (>=2) pass wins."""
    run1 = _snap("r1", [_row("a", passed=True)])
    run2 = _snap("r2", [_row("a", passed=True)])
    run3 = _snap("r3", [_row("a", passed=False)])
    merged = merge_snapshots([run1, run2, run3])
    fx = {f.fixture_id: f for f in merged.fixtures}
    assert fx["a"].passed is True


@pytest.mark.unit
def test_merge_snapshots_majority_fail() -> None:
    """With 3 runs, majority (>=2) fail wins."""
    run1 = _snap("r1", [_row("a", passed=False)])
    run2 = _snap("r2", [_row("a", passed=False)])
    run3 = _snap("r3", [_row("a", passed=True)])
    merged = merge_snapshots([run1, run2, run3])
    fx = {f.fixture_id: f for f in merged.fixtures}
    assert fx["a"].passed is False


@pytest.mark.unit
def test_merge_snapshots_majority_loaded() -> None:
    """Rules loaded in majority of runs appear in merged loaded set."""
    run1 = _snap("r1", [_row("a", loaded=("rules/A.md", "rules/B.md"))])
    run2 = _snap("r2", [_row("a", loaded=("rules/A.md",))])
    run3 = _snap("r3", [_row("a", loaded=("rules/A.md", "rules/B.md"))])
    merged = merge_snapshots([run1, run2, run3])
    fx = {f.fixture_id: f for f in merged.fixtures}
    # A.md appears in all 3 (majority), B.md in 2/3 (majority)
    assert "rules/A.md" in fx["a"].loaded
    assert "rules/B.md" in fx["a"].loaded


@pytest.mark.unit
def test_merge_snapshots_minority_rule_excluded() -> None:
    """Rule in only 1 of 3 runs is excluded from merged loaded set."""
    run1 = _snap("r1", [_row("a", loaded=("rules/A.md", "rules/SPECULATIVE.md"))])
    run2 = _snap("r2", [_row("a", loaded=("rules/A.md",))])
    run3 = _snap("r3", [_row("a", loaded=("rules/A.md",))])
    merged = merge_snapshots([run1, run2, run3])
    fx = {f.fixture_id: f for f in merged.fixtures}
    assert "rules/SPECULATIVE.md" not in fx["a"].loaded


@pytest.mark.unit
def test_merge_snapshots_fill_missing_fixture() -> None:
    """Fixture present in some runs but not all is included (fill_missing=True)."""
    run1 = _snap("r1", [_row("a"), _row("b")])
    run2 = _snap("r2", [_row("a")])
    merged = merge_snapshots([run1, run2])
    ids = {f.fixture_id for f in merged.fixtures}
    assert "a" in ids
    assert "b" in ids


@pytest.mark.unit
def test_merge_snapshots_empty_list_raises() -> None:
    with pytest.raises(ValueError, match="at least one snapshot"):
        merge_snapshots([])


@pytest.mark.unit
def test_merge_snapshots_empty_fixtures_raises() -> None:
    empty_snap = Snapshot(
        meta=SnapshotMeta(label="empty"),
        fixtures=(),
        summary=None,
    )
    with pytest.raises(ValueError, match="no fixtures found"):
        merge_snapshots([empty_snap])


@pytest.mark.unit
def test_merge_snapshots_median_numerics() -> None:
    """Numeric metrics use median aggregation."""
    run1 = _snap("r1", [_row("a", turns=1, duration_ms=100, signal=0, citation=0)])
    run2 = _snap("r2", [_row("a", turns=5, duration_ms=300, signal=2, citation=1)])
    run3 = _snap("r3", [_row("a", turns=3, duration_ms=200, signal=1, citation=0)])
    merged = merge_snapshots([run1, run2, run3])
    fx = {f.fixture_id: f for f in merged.fixtures}
    assert fx["a"].turns == 3
    assert fx["a"].duration_ms == 200
    assert fx["a"].signal_disagreements == 1


@pytest.mark.unit
def test_merge_snapshots_flake_score_populated() -> None:
    """flake_score > 0 when loaded sets differ across runs."""
    run1 = _snap("r1", [_row("a", loaded=("rules/A.md",))])
    run2 = _snap("r2", [_row("a", loaded=("rules/B.md",))])
    merged = merge_snapshots([run1, run2])
    fx = {f.fixture_id: f for f in merged.fixtures}
    assert fx["a"].flake_score > 0.0


@pytest.mark.unit
def test_merge_snapshots_n_runs_populated() -> None:
    run1 = _snap("r1", [_row("a")])
    run2 = _snap("r2", [_row("a")])
    run3 = _snap("r3", [_row("a")])
    merged = merge_snapshots([run1, run2, run3])
    fx = {f.fixture_id: f for f in merged.fixtures}
    assert fx["a"].n_runs == 3


@pytest.mark.unit
def test_merge_snapshots_source_labels_in_notes() -> None:
    run1 = _snap("run-A", [_row("a")])
    run2 = _snap("run-B", [_row("a")])
    merged = merge_snapshots([run1, run2], label="combined")
    assert "run-A" in merged.meta.notes
    assert "run-B" in merged.meta.notes
    assert merged.meta.label == "combined"


# ---------------------------------------------------------------------------
# _compute_flake_score (lines 902-911)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_compute_flake_score_single_row_zero() -> None:
    rows = [_row("a", loaded=("rules/A.md",))]
    assert _compute_flake_score(rows) == 0.0


@pytest.mark.unit
def test_compute_flake_score_identical_rows_zero() -> None:
    rows = [_row("a", loaded=("rules/A.md",)), _row("b", loaded=("rules/A.md",))]
    assert _compute_flake_score(rows) == 0.0


@pytest.mark.unit
def test_compute_flake_score_disjoint_sets_max() -> None:
    rows = [_row("a", loaded=("rules/A.md",)), _row("b", loaded=("rules/B.md",))]
    score = _compute_flake_score(rows)
    assert score == 1.0


@pytest.mark.unit
def test_compute_flake_score_empty_loaded_sets_zero() -> None:
    rows = [_row("a", loaded=()), _row("b", loaded=())]
    assert _compute_flake_score(rows) == 0.0


@pytest.mark.unit
def test_compute_flake_score_partial_overlap() -> None:
    rows = [
        _row("a", loaded=("rules/A.md", "rules/B.md")),
        _row("b", loaded=("rules/A.md", "rules/C.md")),
    ]
    score = _compute_flake_score(rows)
    # union = {A, B, C} = 3, intersection = {A} = 1, flake = 1 - 1/3 ≈ 0.6667
    assert 0.0 < score < 1.0


# ---------------------------------------------------------------------------
# render_merge_summary (lines 916-919)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_merge_summary_no_summary() -> None:
    snap = Snapshot(meta=SnapshotMeta(label="empty"), fixtures=(), summary=None)
    lines = render_merge_summary(snap, n_inputs=3)
    assert lines == ["merged 3 run(s) -> 0 fixtures"]


@pytest.mark.unit
def test_render_merge_summary_with_fixtures() -> None:
    snap = _snap("merged", [_row("a"), _row("b")])
    lines = render_merge_summary(snap, n_inputs=2)
    joined = "\n".join(lines)
    assert "merged 2 run(s) -> 2 fixture(s)" in joined
    assert "pass:" in joined


# ---------------------------------------------------------------------------
# render_table with fixtures_only_in_baseline/post sections (lines 398-406)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_table_fixtures_only_in_baseline_and_post() -> None:
    base = _snap("base", [_row("shared"), _row("only-base")])
    post = _snap("post", [_row("shared"), _row("only-post")])
    report = compare_snapshots(base, post)
    lines = render_table(report)
    joined = "\n".join(lines)
    assert "only in baseline:" in joined
    assert "- only-base" in joined
    assert "only in post:" in joined
    assert "+ only-post" in joined


# ---------------------------------------------------------------------------
# _render_delta_block: churn rule skipped in removed-block (line 562)
# and churn rule skipped in regression fix hints (line 590)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_delta_block_churn_suppression_in_removed_block() -> None:
    """Churn rule in d.loaded_removed is skipped (continue) when verbose=False."""
    churn_rule = "rules/GLOBAL-GONE.md"
    # 3 fixtures all lose churn_rule — qualifies as universal churn
    base_rows = [
        _row("r", passed=True, loaded=(churn_rule, "rules/999-test-core.md")),
        _row("b", loaded=(churn_rule, "rules/999-test-core.md")),
        _row("c", loaded=(churn_rule, "rules/999-test-core.md")),
    ]
    post_rows = [_row("r", passed=False), _row("b"), _row("c")]
    report = compare_snapshots(_snap("base", base_rows), _snap("post", post_rows))
    from ai_rules.rule_loader_eval.compare import _detect_universal_churn

    churn = _detect_universal_churn(report)
    assert churn_rule in churn
    # Call _render_delta_block directly with churn
    reg_delta = report.regressions[0]
    lines = _render_delta_block(reg_delta, churn=churn, verbose=False)
    joined = "\n".join(lines)
    # churn rule suppressed from the -loaded block
    assert churn_rule not in joined
    # and NOT in fix hints either (590: continue)


@pytest.mark.unit
def test_render_delta_block_churn_suppression_in_verbose() -> None:
    """With verbose=True, churn rule is NOT skipped in removed block."""
    churn_rule = "rules/GLOBAL-GONE.md"
    base_rows = [
        _row("r", passed=True, loaded=(churn_rule, "rules/999-test-core.md")),
        _row("b", loaded=(churn_rule, "rules/999-test-core.md")),
    ]
    post_rows = [_row("r", passed=False), _row("b")]
    report = compare_snapshots(_snap("base", base_rows), _snap("post", post_rows))
    from ai_rules.rule_loader_eval.compare import _detect_universal_churn

    churn = _detect_universal_churn(report)
    reg_delta = report.regressions[0]
    lines = _render_delta_block(reg_delta, churn=churn, verbose=True)
    joined = "\n".join(lines)
    assert churn_rule in joined


# ---------------------------------------------------------------------------
# _render_delta_block: [missing-dep] fix hint (lines 596-597)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_render_delta_block_missing_dep_fix_hint() -> None:
    dep_rule = "rules/dep.md"
    base = _snap("base", [_row("x", passed=True, loaded=("rules/999-test-core.md", dep_rule))])
    post = _snap(
        "post",
        [
            _row(
                "x",
                passed=False,
                loaded=("rules/999-test-core.md",),
                expected_required=("rules/999-test-core.md",),
                expected_dependencies=(dep_rule,),
                missing_dependencies=(dep_rule,),
            )
        ],
    )
    report = compare_snapshots(base, post)
    d = report.regressions[0]
    lines = _render_delta_block(d)
    joined = "\n".join(lines)
    assert "[missing-dep]" in joined
    assert "→ fix: add kw: trigger to" in joined
    assert "(was missing-dep)" in joined


# ---------------------------------------------------------------------------
# _md_delta_block: regression churn skip (line 636)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_md_delta_block_regression_churn_skip() -> None:
    """In _md_delta_block regression section, churn rules are skipped (continue)."""
    churn_rule = "rules/CHURN.md"
    # Only 2 fixtures needed for 100% threshold coverage
    base_rows = [
        _row("r", passed=True, loaded=(churn_rule, "rules/999-test-core.md")),
        _row("b", loaded=(churn_rule, "rules/999-test-core.md")),
    ]
    post_rows = [_row("r", passed=False), _row("b")]
    report = compare_snapshots(_snap("base", base_rows), _snap("post", post_rows))
    from ai_rules.rule_loader_eval.compare import _detect_universal_churn

    churn = _detect_universal_churn(report)
    reg_delta = report.regressions[0]
    # verbose=False, churn set passed — regression fix hints skip churn rule (line 636)
    lines = _md_delta_block(reg_delta, churn=churn, verbose=False)
    joined = "\n".join(lines)
    # churn rule should not appear in fix hints
    assert f"`{churn_rule}`" not in joined or "→ fix:" not in joined


# ---------------------------------------------------------------------------
# _merge_fixture_rows._majority_set inner loop (line 852)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_merge_snapshots_majority_missing_required() -> None:
    """_majority_set is exercised when rows have non-empty missing_required fields."""
    missing = "rules/MISSING-CORE.md"
    run1 = _snap("r1", [_row("a", passed=False, missing_required=(missing,))])
    run2 = _snap("r2", [_row("a", passed=False, missing_required=(missing,))])
    run3 = _snap("r3", [_row("a", passed=True, missing_required=())])
    merged = merge_snapshots([run1, run2, run3])
    fx = {f.fixture_id: f for f in merged.fixtures}
    # majority (2/3) have it missing → it should be in merged missing_required
    assert missing in fx["a"].missing_required


@pytest.mark.unit
def test_merge_snapshots_minority_missing_required_excluded() -> None:
    """A missing_required entry in only 1 of 3 runs is NOT in the merged row."""
    missing = "rules/RARE-MISS.md"
    run1 = _snap("r1", [_row("a", passed=False, missing_required=(missing,))])
    run2 = _snap("r2", [_row("a", passed=True, missing_required=())])
    run3 = _snap("r3", [_row("a", passed=True, missing_required=())])
    merged = merge_snapshots([run1, run2, run3])
    fx = {f.fixture_id: f for f in merged.fixtures}
    assert missing not in fx["a"].missing_required
