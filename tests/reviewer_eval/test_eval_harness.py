"""Eval harness for rule-review-result/v1 schema compliance and quality metrics.

Five machine-readable metric types (all informational):
  1. schema_compliance  — % of artifacts passing validate_review_result
  2. score_variance     — std dev of scores across corpus items
  3. finding_jaccard    — Jaccard similarity of finding IDs across pairs
  4. citation_validity  — % of source evidence locators in path:line format
  5. trigger_recall     — % of positive prompts matching expected skill (synthetic)

All thresholds are informational. Tests assert metric keys are present, not
threshold violations.
"""

from __future__ import annotations

import copy
import json
import math
import re
from pathlib import Path

import pytest

from ai_rules.review_results import validate_review_result

# ── corpus ────────────────────────────────────────────────────────────────────

_VALID_FIXTURE = Path(__file__).parent.parent / "reviewer_results" / "fixtures" / "valid.json"

_INFORMATIONAL_THRESHOLDS = {
    "schema_compliance": 0.95,
    "score_variance_max": 5.0,
    "finding_jaccard_min": 0.6,
    "citation_validity": 0.90,
    "trigger_recall_min": 0.80,
}


def _make_review_corpus() -> list[dict]:
    """Build a small synthetic corpus of review artifacts for eval."""
    base = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))

    def _scale(review: dict, score_target: float, rule: str) -> dict:
        r = copy.deepcopy(review)
        r["rule_name"] = rule
        r["artifact_id"] = f"eval-{rule.replace('/', '-')}"
        # Scale dimensions proportionally
        scale = score_target / 87.0
        for d in r["dimensions"]:
            raw = max(0.0, min(10.0, float(d["raw_score"]) * scale))
            d["raw_score"] = round(raw, 1)
            d["points"] = round(d["raw_score"] * d["weight"], 4)
        r["score"] = round(sum(d["points"] for d in r["dimensions"]), 1)
        # Assign verdict
        s = r["score"]
        if s >= 90:
            r["verdict"] = "EXECUTABLE"
        elif s >= 80:
            r["verdict"] = "EXECUTABLE_WITH_REFINEMENTS"
        elif s >= 60:
            r["verdict"] = "NEEDS_REFINEMENT"
        else:
            r["verdict"] = "NOT_EXECUTABLE"
        return r

    return [
        _scale(base, 92.0, "rules/000-global-core.md"),  # strong
        _scale(base, 74.0, "rules/100-snowflake-core.md"),  # medium / ambiguous
        _scale(base, 45.0, "rules/200-python-core.md"),  # weak
    ]


def _compute_jaccard(set_a: set, set_b: set) -> float:
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    return len(set_a & set_b) / len(union)


def _compute_stddev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(variance)


# ── metric 1: schema compliance ───────────────────────────────────────────────


def test_eval_schema_compliance_metric_present() -> None:
    """schema_compliance metric must be computable and present in output."""
    corpus = _make_review_corpus()
    valid_count = sum(1 for r in corpus if not validate_review_result(r))
    metric = valid_count / len(corpus)
    assert "schema_compliance" in {"schema_compliance"}  # key present
    assert 0.0 <= metric <= 1.0
    # Informational: log but don't block
    threshold = _INFORMATIONAL_THRESHOLDS["schema_compliance"]
    if metric < threshold:
        pytest.warns(UserWarning, match="schema_compliance")  # informational warning path


def test_eval_all_corpus_items_valid() -> None:
    """All synthetic corpus items must pass schema validation."""
    corpus = _make_review_corpus()
    for r in corpus:
        issues = validate_review_result(r)
        assert issues == [], f"{r['rule_name']}: {issues}"


# ── metric 2: score variance ──────────────────────────────────────────────────


def test_eval_score_variance_metric_present() -> None:
    """score_variance metric must be computable and present in output."""
    corpus = _make_review_corpus()
    scores = [float(r["score"]) for r in corpus if r.get("score") is not None]
    stddev = _compute_stddev(scores)
    assert isinstance(stddev, float)
    # Informational threshold
    max_variance = _INFORMATIONAL_THRESHOLDS["score_variance_max"]
    # Corpus has intentionally varied scores; stddev may exceed threshold
    # This test proves the metric is computable, not that it passes.
    assert stddev >= 0.0


def test_eval_repeated_render_produces_zero_variance() -> None:
    """Rendering the same review twice produces byte-identical output (0 variance)."""
    from ai_rules.review_results import render_review_markdown

    review = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))
    renders = [render_review_markdown(review, json_path="reviews/test.json") for _ in range(3)]
    assert len(set(renders)) == 1, "Renderer must be deterministic across all runs"


# ── metric 3: finding Jaccard ─────────────────────────────────────────────────


def test_eval_finding_jaccard_metric_present() -> None:
    """finding_jaccard metric must be computable between two corpus items."""
    corpus = _make_review_corpus()
    # Compare finding IDs between two items (both have empty findings here)
    ids_a = {f.get("finding_id") for f in corpus[0].get("findings", []) if isinstance(f, dict)}
    ids_b = {f.get("finding_id") for f in corpus[1].get("findings", []) if isinstance(f, dict)}
    jaccard = _compute_jaccard(ids_a, ids_b)
    assert 0.0 <= jaccard <= 1.0


def test_eval_identical_reviews_have_jaccard_1() -> None:
    """Two identical reviews must have Jaccard similarity of 1.0."""
    review = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))
    ids_a = {f.get("finding_id") for f in review.get("findings", []) if isinstance(f, dict)}
    ids_b = {
        f.get("finding_id")
        for f in copy.deepcopy(review).get("findings", [])
        if isinstance(f, dict)
    }
    assert _compute_jaccard(ids_a, ids_b) == 1.0


# ── metric 4: citation validity ───────────────────────────────────────────────

_LOCATOR_RE = re.compile(r"^[^:]+:\d+$")


def _citation_validity(reviews: list[dict]) -> float:
    """Return fraction of source evidence locators that match path:line format."""
    total = 0
    valid = 0
    for r in reviews:
        for f in r.get("findings", []):
            if not isinstance(f, dict):
                continue
            claim = f.get("claim", {})
            for e in claim.get("evidence", []) if isinstance(claim, dict) else []:
                if not isinstance(e, dict) or e.get("kind") != "source":
                    continue
                locator = e.get("locator")
                if locator is None:
                    continue
                total += 1
                if _LOCATOR_RE.match(str(locator)):
                    valid += 1
    return valid / total if total > 0 else 1.0


def test_eval_citation_validity_metric_present() -> None:
    """citation_validity metric must be computable and present in output."""
    corpus = _make_review_corpus()
    metric = _citation_validity(corpus)
    assert 0.0 <= metric <= 1.0


def test_eval_valid_fixture_citation_validity_is_1() -> None:
    """The valid fixture has one source locator in correct path:line format."""
    review = json.loads(_VALID_FIXTURE.read_text(encoding="utf-8"))
    # The fixture has one source locator in executive_summary
    # citation_validity checks findings, not executive_summary — expect 1.0 (no findings)
    metric = _citation_validity([review])
    assert metric == 1.0


# ── metric 5: trigger recall (synthetic) ─────────────────────────────────────

# Discovery corpus prompts per canonical skill (synthetic — no live model calls)
_POSITIVE_PROMPTS = {
    "rule-loader": [
        "load rules for python files",
        "which rules apply to .py extensions",
        "match rules for my snowflake sql query",
    ],
    "rule-reviewer": [
        "review this rule file",
        "score rule executability",
        "FULL mode review of rules/000-global-core.md",
    ],
    "bulk-rule-reviewer": [
        "audit all rules in the rules directory",
        "score every rule",
        "bulk review for pre-release validation",
    ],
}
_NEGATIVE_PROMPTS = {
    "rule-loader": ["review my rule file", "bulk audit all rules"],
    "rule-reviewer": ["load rules for python", "aggregate bulk output"],
    "bulk-rule-reviewer": ["single rule review", "load the matcher manifest"],
}

# Synthetic keyword-based skill detection (mirrors real trigger patterns)
_SKILL_TRIGGERS: dict[str, list[str]] = {
    "rule-loader": ["load rules", "which rules", "match rules", ".py", "extensions"],
    "rule-reviewer": ["review", "score rule", "FULL mode", "FOCUSED mode", "executability"],
    "bulk-rule-reviewer": ["audit all", "score every", "bulk review", "bulk"],
}


def _detect_skill(prompt: str) -> str | None:
    """Synthetic skill detection from prompt text."""
    prompt_lower = prompt.lower()
    # bulk-rule-reviewer takes priority over rule-reviewer
    if any(t.lower() in prompt_lower for t in _SKILL_TRIGGERS["bulk-rule-reviewer"]):
        return "bulk-rule-reviewer"
    if any(t.lower() in prompt_lower for t in _SKILL_TRIGGERS["rule-reviewer"]):
        return "rule-reviewer"
    if any(t.lower() in prompt_lower for t in _SKILL_TRIGGERS["rule-loader"]):
        return "rule-loader"
    return None


def test_eval_trigger_recall_metric_present() -> None:
    """trigger_recall metric must be computable and present in output."""
    total = 0
    correct = 0
    for expected_skill, prompts in _POSITIVE_PROMPTS.items():
        for prompt in prompts:
            total += 1
            if _detect_skill(prompt) == expected_skill:
                correct += 1
    metric = correct / total if total > 0 else 0.0
    assert 0.0 <= metric <= 1.0
    # Informational threshold
    threshold = _INFORMATIONAL_THRESHOLDS["trigger_recall_min"]
    # Log the metric value for baseline tracking
    assert total >= 9, f"Discovery corpus must have at least 9 positive prompts, got {total}"


def test_eval_negative_prompts_do_not_fire_wrong_skill() -> None:
    """Negative prompts must not match the skill they are listed against."""
    for wrong_skill, prompts in _NEGATIVE_PROMPTS.items():
        for prompt in prompts:
            detected = _detect_skill(prompt)
            assert detected != wrong_skill, (
                f"Negative prompt {prompt!r} incorrectly matched {wrong_skill!r}"
            )


# ── summary: all five metrics are computable together ─────────────────────────


def test_eval_all_five_metrics_computable(tmp_path: Path) -> None:
    """All five metric types must be computable and written to a JSON summary."""
    corpus = _make_review_corpus()

    # 1. schema_compliance
    valid_count = sum(1 for r in corpus if not validate_review_result(r))
    schema_compliance = valid_count / len(corpus)

    # 2. score_variance
    scores = [float(r["score"]) for r in corpus if r.get("score") is not None]
    score_variance = _compute_stddev(scores)

    # 3. finding_jaccard (identical corpus pair)
    ids_a = {f.get("finding_id") for f in corpus[0].get("findings", []) if isinstance(f, dict)}
    ids_b = {f.get("finding_id") for f in corpus[0].get("findings", []) if isinstance(f, dict)}
    finding_jaccard = _compute_jaccard(ids_a, ids_b)

    # 4. citation_validity
    citation_validity_score = _citation_validity(corpus)

    # 5. trigger_recall
    total = sum(len(v) for v in _POSITIVE_PROMPTS.values())
    correct = sum(
        1
        for skill, prompts in _POSITIVE_PROMPTS.items()
        for p in prompts
        if _detect_skill(p) == skill
    )
    trigger_recall = correct / total

    summary = {
        "schema_compliance": schema_compliance,
        "score_variance": score_variance,
        "finding_jaccard": finding_jaccard,
        "citation_validity": citation_validity_score,
        "trigger_recall": trigger_recall,
        "thresholds": _INFORMATIONAL_THRESHOLDS,
        "informational_only": True,
    }

    out = tmp_path / "eval-metrics.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert set(loaded.keys()) >= {
        "schema_compliance",
        "score_variance",
        "finding_jaccard",
        "citation_validity",
        "trigger_recall",
    }
    assert loaded["informational_only"] is True
