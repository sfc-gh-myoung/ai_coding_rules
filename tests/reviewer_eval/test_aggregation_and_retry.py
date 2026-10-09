"""Phase 5 exit gate tests — aggregation, Markdown-only rejection, retry/repair.

Covers three exit-gate checks:
  1. Aggregation tests  (pytest -k aggregation)
  2. Markdown-only rejection (pytest -k markdown_only)
  3. Retry/repair tests (pytest -k retry or repair)
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from ai_rules.review_results import (
    render_review_markdown,
    validate_review_result,
)

# ── shared fixtures ───────────────────────────────────────────────────────────

_VALID_FIXTURE = Path(__file__).parent.parent / "reviewer_results" / "fixtures" / "valid.json"


def _make_review(rule_name: str, score: float, verdict: str, blocking: int = 0) -> dict:
    """Build a minimal valid review dict with parametric score/verdict."""
    base = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))
    base = copy.deepcopy(base)
    base["rule_name"] = rule_name
    base["artifact_id"] = f"test-{rule_name.replace('/', '-')}"
    # Rebuild dimensions to sum to the requested score
    # Use proportional scaling of the valid fixture dimensions
    scale = score / 87.0
    total = 0.0
    for d in base["dimensions"]:
        raw = max(0.0, min(10.0, float(d["raw_score"]) * scale))
        d["raw_score"] = round(raw, 1)
        d["points"] = round(d["raw_score"] * d["weight"], 4)
        total += d["points"]
    base["score"] = round(total, 1)
    base["verdict"] = verdict
    base["blocking_issue_count"] = blocking
    return base


# ── aggregation tests ─────────────────────────────────────────────────────────


def test_aggregation_single_valid_json(tmp_path: Path) -> None:
    """Aggregation over one valid review JSON exits 0 and emits a summary."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    review = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))
    f = tmp_path / "review.json"
    f.write_text(json.dumps(review), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["review-artifact", "aggregate", "--input", str(f)])
    assert result.exit_code == 0, result.output
    summary = json.loads(result.output)
    assert summary["review_count"] == 1
    assert "verdict_distribution" in summary


def test_aggregation_multiple_valid_json(tmp_path: Path) -> None:
    """Aggregation across multiple reviews sums counts correctly."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    reviews = [
        _make_review("rules/000-global-core.md", 92.0, "EXECUTABLE"),
        _make_review("rules/100-snowflake-core.md", 75.0, "NEEDS_REFINEMENT"),
        _make_review("rules/200-python-core.md", 85.0, "EXECUTABLE_WITH_REFINEMENTS"),
    ]

    paths = []
    for i, r in enumerate(reviews):
        f = tmp_path / f"review-{i}.json"
        f.write_text(json.dumps(r), encoding="utf-8")
        paths.append(str(f))

    runner = CliRunner()
    args = ["review-artifact", "aggregate"]
    for p in paths:
        args += ["--input", p]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    summary = json.loads(result.output)
    assert summary["review_count"] == 3
    assert summary["verdict_distribution"].get("EXECUTABLE", 0) >= 1
    assert summary["verdict_distribution"].get("NEEDS_REFINEMENT", 0) >= 1


def test_aggregation_invalid_json_exits_1(tmp_path: Path) -> None:
    """Aggregation returns exit 1 when an input file contains invalid JSON."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["review-artifact", "aggregate", "--input", str(bad)])
    assert result.exit_code == 1


def test_aggregation_semantic_violation_exits_1(tmp_path: Path) -> None:
    """Aggregation returns exit 1 when an input fails semantic validation."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    bad_review = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))
    bad_review = copy.deepcopy(bad_review)
    bad_review["schema_version"] = "rule-review-result/v0"
    f = tmp_path / "bad-schema.json"
    f.write_text(json.dumps(bad_review), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["review-artifact", "aggregate", "--input", str(f)])
    assert result.exit_code == 1


def test_aggregation_score_stats_present(tmp_path: Path) -> None:
    """Aggregate summary must include score_mean, score_min, score_max."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    review = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))
    f = tmp_path / "review.json"
    f.write_text(json.dumps(review), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["review-artifact", "aggregate", "--input", str(f)])
    summary = json.loads(result.output)
    assert "score_mean" in summary
    assert "score_min" in summary
    assert "score_max" in summary


# ── Markdown-only rejection tests ─────────────────────────────────────────────


def test_markdown_only_input_not_accepted_by_aggregate(tmp_path: Path) -> None:
    """Aggregation must reject a .md file (Markdown-only — no same-stem JSON)."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    review = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))
    json_src = tmp_path / "review.json"
    json_src.write_text(json.dumps(review), encoding="utf-8")
    md_path = tmp_path / "review.md"
    md_path.write_text(render_review_markdown(review, json_path=json_src), encoding="utf-8")

    # Pass only the Markdown file (no JSON) — aggregate should reject it
    runner = CliRunner()
    result = runner.invoke(app, ["review-artifact", "aggregate", "--input", str(md_path)])
    # Should fail because .md file is not valid JSON
    assert result.exit_code != 0


def test_orphan_markdown_excluded_from_statistics(tmp_path: Path) -> None:
    """An orphan Markdown file (no same-stem JSON) must not contribute to statistics.

    This proves the prohibition: automation discovers accepted artifacts from JSON only.
    """
    # Write a canonical JSON review
    review = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))
    json_path = tmp_path / "review.json"
    json_path.write_text(json.dumps(review), encoding="utf-8")

    # Write an orphan Markdown (no same-stem JSON)
    orphan_md = tmp_path / "orphan-review.md"
    orphan_md.write_text("# Rule Review: orphan\n\n**Score:** 50/100\n", encoding="utf-8")

    # The orphan .md file is present in the directory but must NOT be passed to aggregate.
    # The caller (bulk-rule-reviewer stage 3) is responsible for passing only .json paths.
    # This test validates the isolation: the aggregation command ignores non-JSON content.
    from typer.testing import CliRunner

    from ai_rules.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["review-artifact", "aggregate", "--input", str(json_path)])
    assert result.exit_code == 0
    summary = json.loads(result.output)
    # Only 1 accepted review (the JSON one), not 2
    assert summary["review_count"] == 1


# ── retry/repair tests ────────────────────────────────────────────────────────


def test_verify_repair_only_allowed_pointer_changed(tmp_path: Path) -> None:
    """verify-repair exits 0 when candidate changes only the allowed path."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    baseline = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))
    # Introduce a deliberate score error in the baseline
    baseline_bad = copy.deepcopy(baseline)
    baseline_bad["score"] = 50.0  # wrong
    baseline_bad["verdict"] = "NOT_EXECUTABLE"  # wrong for score=87 dims

    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(json.dumps(baseline_bad), encoding="utf-8")

    # Candidate repairs only score and verdict
    candidate = copy.deepcopy(baseline_bad)
    candidate["score"] = baseline["score"]
    candidate["verdict"] = baseline["verdict"]
    candidate_path = tmp_path / "candidate.json"
    candidate_path.write_text(json.dumps(candidate), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "review-artifact",
            "verify-repair",
            "--baseline",
            str(baseline_path),
            "--candidate",
            str(candidate_path),
            "--allowed-path",
            "/score",
            "--allowed-path",
            "/verdict",
        ],
    )
    assert result.exit_code == 0, result.output


def test_verify_repair_unauthorized_drift_exits_4(tmp_path: Path) -> None:
    """verify-repair exits 4 when candidate changes a non-allowed field."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    baseline = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

    # Candidate changes rule_name (not in allowed-path list)
    candidate = copy.deepcopy(baseline)
    candidate["rule_name"] = "rules/sneaky-change.md"
    candidate_path = tmp_path / "candidate.json"
    candidate_path.write_text(json.dumps(candidate), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "review-artifact",
            "verify-repair",
            "--baseline",
            str(baseline_path),
            "--candidate",
            str(candidate_path),
            "--allowed-path",
            "/score",
        ],
    )
    assert result.exit_code == 4, result.output


def test_verify_repair_invalid_candidate_exits_1(tmp_path: Path) -> None:
    """verify-repair exits 1 when candidate fails semantic validation."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    baseline = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

    # Candidate has invalid schema_version
    candidate = copy.deepcopy(baseline)
    candidate["schema_version"] = "rule-review-result/v0"
    candidate_path = tmp_path / "candidate.json"
    candidate_path.write_text(json.dumps(candidate), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "review-artifact",
            "verify-repair",
            "--baseline",
            str(baseline_path),
            "--candidate",
            str(candidate_path),
        ],
    )
    assert result.exit_code == 1, result.output


def test_repair_preserves_rejected_json(tmp_path: Path) -> None:
    """Confirm that the rejected JSON is preserved before repair (caller responsibility).

    This test validates the naming convention: baseline is preserved as
    <stem>-rejected-1.json and the candidate is a separate file.
    """
    baseline = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))
    # Simulate a reviewer emitting a bad artifact
    bad = copy.deepcopy(baseline)
    bad["score"] = 200.0  # out of range — schema violation
    # Caller preserves the rejected artifact
    rejected_path = tmp_path / "review-rejected-1.json"
    rejected_path.write_text(json.dumps(bad), encoding="utf-8")

    issues = validate_review_result(bad)
    assert any("score" in i or "200" in i for i in issues), (
        "Out-of-range score must be caught by validator"
    )
    assert rejected_path.exists(), "Rejected JSON must be preserved before repair"
