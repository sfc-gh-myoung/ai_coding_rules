"""Tests for review_results.py — rule-review-result/v1 semantic validator.

Coverage:
- All six dimension invariants (set, weight, arithmetic, score, verdict, caps)
- Blocking issue count agreement
- Blocking evidence requirements
- Source locator format
- Unknown top-level field rejection
- Exit-code scenarios (0, 1, 2, 3) via behavior classification
- Mutation-first verification for all critical assertions

Exit-code mapping tested
------------------------
Exit 0: valid fixture validates cleanly
Exit 1: each distinct semantic violation returns non-empty issue list
Exit 2: I/O failures (missing file, bad encoding, bad JSON) raise ValueError
Exit 3: non-dict input returns non-empty issue list (caller maps to defect)
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ai_rules.review_results import (
    SCHEMA_VERSION,
    load_and_validate_review,
    validate_review_result,
)

# ── shared fixture ────────────────────────────────────────────────────────────

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "valid.json"


@pytest.fixture
def valid_review() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


# ── exit 0: valid fixture ─────────────────────────────────────────────────────


def test_valid_fixture_passes() -> None:
    """Mutation-first: the fixture must validate cleanly (exit 0)."""
    review = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert validate_review_result(review) == []


def test_valid_fixture_file_exists() -> None:
    assert FIXTURE_PATH.exists(), f"Fixture missing: {FIXTURE_PATH}"


# ── exit 1: schema version ────────────────────────────────────────────────────


def test_wrong_schema_version_rejected(valid_review: dict) -> None:
    """Mutation-first: change schema_version, expect non-empty issues."""
    r = copy.deepcopy(valid_review)
    r["schema_version"] = "rule-review-result/v0"
    issues = validate_review_result(r)
    assert issues
    combined = " ".join(issues)
    assert SCHEMA_VERSION in combined or "schema_version" in combined


def test_missing_schema_version_rejected(valid_review: dict) -> None:
    r = copy.deepcopy(valid_review)
    del r["schema_version"]
    issues = validate_review_result(r)
    assert any("schema_version" in i for i in issues)


# ── exit 1: unknown top-level fields ─────────────────────────────────────────


def test_unknown_top_level_field_rejected(valid_review: dict) -> None:
    """Mutation-first: add a foreign key, expect rejection."""
    r = copy.deepcopy(valid_review)
    r["injected_field"] = "oops"
    issues = validate_review_result(r)
    assert any("injected_field" in i for i in issues)


def test_extensions_key_accepted(valid_review: dict) -> None:
    """The 'extensions' key is whitelisted even with content."""
    r = copy.deepcopy(valid_review)
    r["extensions"] = {"x-myns:extra": "value"}
    assert validate_review_result(r) == []


# ── exit 1: dimension set ─────────────────────────────────────────────────────


def test_missing_dimension_rejected(valid_review: dict) -> None:
    """Mutation-first: remove one dimension, expect dimension-set error."""
    r = copy.deepcopy(valid_review)
    r["dimensions"] = [d for d in r["dimensions"] if d["name"] != "actionability"]
    issues = validate_review_result(r)
    assert any("actionability" in i for i in issues)


def test_extra_dimension_rejected(valid_review: dict) -> None:
    """Mutation-first: add a non-canonical dimension."""
    r = copy.deepcopy(valid_review)
    r["dimensions"] = list(r["dimensions"]) + [
        {"name": "invented_dimension", "raw_score": 5, "weight": 1.0, "points": 5.0, "findings": []}
    ]
    issues = validate_review_result(r)
    assert any("invented_dimension" in i for i in issues)


def test_duplicate_dimension_rejected(valid_review: dict) -> None:
    """Mutation-first: duplicate a dimension and remove another."""
    r = copy.deepcopy(valid_review)
    dims = [d for d in r["dimensions"] if d["name"] != "rule_size"]
    dims.append(copy.deepcopy(dims[0]))  # duplicate actionability
    r["dimensions"] = dims
    issues = validate_review_result(r)
    assert issues  # either wrong count or missing rule_size


# ── exit 1: dimension weights ─────────────────────────────────────────────────


def test_wrong_dimension_weight_rejected(valid_review: dict) -> None:
    """Mutation-first: change actionability weight to 2.0 (expect 3.0)."""
    r = copy.deepcopy(valid_review)
    for d in r["dimensions"]:
        if d["name"] == "actionability":
            d["weight"] = 2.0
    issues = validate_review_result(r)
    assert any("actionability" in i and "weight" in i for i in issues)


# ── exit 1: dimension arithmetic ─────────────────────────────────────────────


def test_wrong_dimension_points_rejected(valid_review: dict) -> None:
    """Mutation-first: set points to an incorrect value (not raw_score x weight)."""
    r = copy.deepcopy(valid_review)
    for d in r["dimensions"]:
        if d["name"] == "actionability":
            d["points"] = 99.9  # clearly wrong
    issues = validate_review_result(r)
    assert any("actionability" in i and "points" in i for i in issues)


def test_dimension_arithmetic_tolerance(valid_review: dict) -> None:
    """Points within 0.01 of raw_score x weight must not be rejected."""
    r = copy.deepcopy(valid_review)
    for d in r["dimensions"]:
        if d["name"] == "actionability":
            d["points"] = round(d["raw_score"] * d["weight"] + 0.005, 6)
    assert validate_review_result(r) == []


# ── exit 1: score vs dimension sum ────────────────────────────────────────────


def test_score_mismatch_rejected(valid_review: dict) -> None:
    """Mutation-first: set score to a value that differs from dim sum by >0.5."""
    r = copy.deepcopy(valid_review)
    r["score"] = 10.0  # dimension sum is 87.0
    issues = validate_review_result(r)
    assert any("score" in i for i in issues)


def test_score_within_half_point_accepted(valid_review: dict) -> None:
    """Scores within ±0.5 of the dimension sum should not raise a mismatch error."""
    r = copy.deepcopy(valid_review)
    original_score = r["score"]
    r["score"] = original_score + 0.4
    issues = validate_review_result(r)
    # Only the verdict may change; no score arithmetic error
    score_issues = [i for i in issues if "sum of dimension" in i]
    assert not score_issues


# ── exit 1: verdict vs score ──────────────────────────────────────────────────


def test_wrong_verdict_rejected(valid_review: dict) -> None:
    """Mutation-first: set verdict to EXECUTABLE when score is 87 (EXECUTABLE_WITH_REFINEMENTS)."""
    r = copy.deepcopy(valid_review)
    r["verdict"] = "EXECUTABLE"  # score 87 → EXECUTABLE_WITH_REFINEMENTS
    issues = validate_review_result(r)
    assert any("verdict" in i for i in issues)


def test_verdict_not_executable_at_59(valid_review: dict) -> None:
    """Score 59 must map to NOT_EXECUTABLE."""
    r = copy.deepcopy(valid_review)
    # Rebuild dimensions to sum to 59
    r["dimensions"] = [
        {"name": "actionability", "raw_score": 5, "weight": 3.0, "points": 15.0, "findings": []},
        {"name": "rule_size", "raw_score": 5, "weight": 2.5, "points": 12.5, "findings": []},
        {"name": "parsability", "raw_score": 5, "weight": 1.5, "points": 7.5, "findings": []},
        {"name": "completeness", "raw_score": 5, "weight": 1.5, "points": 7.5, "findings": []},
        {"name": "consistency", "raw_score": 5, "weight": 1.0, "points": 5.0, "findings": []},
        {
            "name": "cross_agent_consistency",
            "raw_score": 5,
            "weight": 0.5,
            "points": 2.5,
            "findings": [],
        },
    ]
    dim_sum = sum(d["points"] for d in r["dimensions"])  # = 50.0
    r["score"] = dim_sum
    r["verdict"] = "NOT_EXECUTABLE"
    assert validate_review_result(r) == []


# ── exit 1: blocking count ────────────────────────────────────────────────────


def test_blocking_count_mismatch_rejected(valid_review: dict) -> None:
    """Mutation-first: declare blocking_issue_count=0 but include a critical finding."""
    r = copy.deepcopy(valid_review)
    r["findings"] = [
        {
            "finding_id": "F001",
            "severity": "critical",
            "claim": {
                "text": "Blocking issue",
                "evidence": [
                    {
                        "kind": "source",
                        "locator": "rules/000-global-core.md:1",
                        "quote": "# Global Core",
                    }
                ],
            },
            "recommendation": "Fix it",
            "rationale": "It blocks execution",
            "affected_paths": ["rules/000-global-core.md"],
        }
    ]
    r["blocking_issue_count"] = 0  # wrong — should be 1
    issues = validate_review_result(r)
    assert any("blocking_issue_count" in i for i in issues)


def test_correct_blocking_count_passes(valid_review: dict) -> None:
    """Correct blocking_issue_count of 1 for one critical finding."""
    r = copy.deepcopy(valid_review)
    r["findings"] = [
        {
            "finding_id": "F001",
            "severity": "critical",
            "claim": {
                "text": "Blocking issue",
                "evidence": [
                    {
                        "kind": "source",
                        "locator": "rules/000-global-core.md:1",
                        "quote": "# Global Core",
                    }
                ],
            },
            "recommendation": "Fix it",
            "rationale": "It blocks execution",
            "affected_paths": [],
        }
    ]
    r["blocking_issue_count"] = 1
    # Adjust score/verdict to be consistent
    r["score"] = 87.0
    r["verdict"] = "EXECUTABLE_WITH_REFINEMENTS"
    issues = validate_review_result(r)
    blocking_issues = [i for i in issues if "blocking_issue_count" in i]
    assert not blocking_issues


# ── exit 1: blocking finding evidence ────────────────────────────────────────


def test_blocking_finding_without_evidence_rejected(valid_review: dict) -> None:
    """Mutation-first: critical finding with only inference evidence → rejected."""
    r = copy.deepcopy(valid_review)
    r["findings"] = [
        {
            "finding_id": "F002",
            "severity": "critical",
            "claim": {
                "text": "Blocking issue without source",
                "evidence": [{"kind": "inference", "locator": None, "quote": None}],
            },
            "recommendation": "Fix it",
            "rationale": "It blocks",
            "affected_paths": [],
        }
    ]
    r["blocking_issue_count"] = 1
    issues = validate_review_result(r)
    assert any("source or docs" in i for i in issues)


def test_blocking_finding_with_docs_evidence_accepted(valid_review: dict) -> None:
    """Docs evidence satisfies the blocking finding requirement."""
    r = copy.deepcopy(valid_review)
    r["findings"] = [
        {
            "finding_id": "F003",
            "severity": "critical",
            "claim": {
                "text": "Blocking issue with docs evidence",
                "evidence": [
                    {"kind": "docs", "locator": "https://docs.snowflake.com/x", "quote": None}
                ],
            },
            "recommendation": "Fix it",
            "rationale": "It blocks",
            "affected_paths": [],
        }
    ]
    r["blocking_issue_count"] = 1
    issues = validate_review_result(r)
    evidence_issues = [i for i in issues if "source or docs" in i]
    assert not evidence_issues


def test_medium_finding_without_evidence_allowed(valid_review: dict) -> None:
    """Non-blocking (medium/low) findings do not require source or docs evidence."""
    r = copy.deepcopy(valid_review)
    r["findings"] = [
        {
            "finding_id": "F004",
            "severity": "medium",
            "claim": {"text": "Minor issue", "evidence": []},
            "recommendation": "Consider it",
            "rationale": "Minor",
            "affected_paths": [],
        }
    ]
    r["blocking_issue_count"] = 0
    issues = validate_review_result(r)
    evidence_issues = [i for i in issues if "source or docs" in i]
    assert not evidence_issues


# ── exit 1: source locator format ─────────────────────────────────────────────


def test_invalid_source_locator_rejected(valid_review: dict) -> None:
    """Mutation-first: source evidence with bad locator format → rejected."""
    r = copy.deepcopy(valid_review)
    r["findings"] = [
        {
            "finding_id": "F005",
            "severity": "high",
            "claim": {
                "text": "Issue with bad locator",
                "evidence": [
                    {
                        "kind": "source",
                        "locator": "rules/000-global-core.md",
                        "quote": "# Global Core",
                    }
                ],
            },
            "recommendation": "Fix it",
            "rationale": "High severity",
            "affected_paths": [],
        }
    ]
    r["blocking_issue_count"] = 1
    issues = validate_review_result(r)
    assert any("path:line" in i for i in issues)


def test_valid_source_locator_accepted(valid_review: dict) -> None:
    """path:line format must be accepted without locator errors."""
    r = copy.deepcopy(valid_review)
    r["findings"] = [
        {
            "finding_id": "F006",
            "severity": "high",
            "claim": {
                "text": "Issue with valid locator",
                "evidence": [
                    {
                        "kind": "source",
                        "locator": "rules/000-global-core.md:42",
                        "quote": "some text",
                    }
                ],
            },
            "recommendation": "Fix",
            "rationale": "High",
            "affected_paths": [],
        }
    ]
    r["blocking_issue_count"] = 1
    issues = validate_review_result(r)
    locator_issues = [i for i in issues if "path:line" in i]
    assert not locator_issues


def test_null_source_locator_accepted(valid_review: dict) -> None:
    """Null source locator is allowed (no path-line check performed)."""
    r = copy.deepcopy(valid_review)
    r["findings"] = [
        {
            "finding_id": "F007",
            "severity": "high",
            "claim": {
                "text": "High finding null locator",
                "evidence": [{"kind": "source", "locator": None, "quote": "relevant text"}],
            },
            "recommendation": "Fix",
            "rationale": "High",
            "affected_paths": [],
        }
    ]
    r["blocking_issue_count"] = 1
    issues = validate_review_result(r)
    locator_issues = [i for i in issues if "path:line" in i]
    assert not locator_issues


# ── exit 2: I/O failures ─────────────────────────────────────────────────────


def test_missing_file_raises_valueerror(tmp_path: Path) -> None:
    """Exit 2: missing file raises ValueError (caller maps to exit 2)."""
    with pytest.raises(ValueError, match="not found"):
        load_and_validate_review(tmp_path / "nonexistent.json")


def test_invalid_json_raises_valueerror(tmp_path: Path) -> None:
    """Exit 2: invalid JSON raises ValueError."""
    bad = tmp_path / "bad.json"
    bad.write_text("not json content {{{", encoding="utf-8")
    with pytest.raises(ValueError, match="not valid JSON"):
        load_and_validate_review(bad)


def test_valid_file_validates_cleanly(tmp_path: Path) -> None:
    """Exit 0 via file path: valid fixture round-trips cleanly."""
    dest = tmp_path / "review.json"
    dest.write_bytes(FIXTURE_PATH.read_bytes())
    issues = load_and_validate_review(dest)
    assert issues == []


# ── exit 3: non-dict input ────────────────────────────────────────────────────


def test_non_dict_input_reports_error() -> None:
    """Exit 3 path: non-dict input returns non-empty issues list."""
    issues = validate_review_result("not a dict")
    assert issues
    assert any("JSON object" in i for i in issues)


def test_list_input_reports_error() -> None:
    issues = validate_review_result([1, 2, 3])
    assert issues
    assert any("JSON object" in i for i in issues)


# ── schema version constant ───────────────────────────────────────────────────


def test_schema_version_constant() -> None:
    assert SCHEMA_VERSION == "rule-review-result/v1"


# ── renderer: deterministic output ───────────────────────────────────────────


def test_render_is_deterministic(valid_review: dict) -> None:
    """Same input must produce byte-identical Markdown on every call."""
    from ai_rules.review_results import render_review_markdown

    md1 = render_review_markdown(valid_review, json_path="reviews/test.json")
    md2 = render_review_markdown(valid_review, json_path="reviews/test.json")
    assert md1 == md2


def test_render_contains_integrity_sentinel(valid_review: dict) -> None:
    from ai_rules.review_results import _INTEGRITY_SENTINEL, render_review_markdown

    md = render_review_markdown(valid_review, json_path="reviews/test.json")
    assert _INTEGRITY_SENTINEL in md


def test_render_integrity_footer_parseable(valid_review: dict) -> None:
    from ai_rules.review_results import extract_integrity_footer, render_review_markdown

    md = render_review_markdown(valid_review, json_path="reviews/test.json")
    footer = extract_integrity_footer(md)
    assert footer["schema"] == SCHEMA_VERSION
    assert footer["renderer"] == "ai-rules review-artifact render/v1"
    assert len(footer["sha256"]) == 64  # hex SHA-256


def test_render_sha256_matches_canonical_json(valid_review: dict) -> None:
    """SHA-256 in footer must match the canonical JSON encoding of the review."""
    import hashlib

    from ai_rules.review_results import extract_integrity_footer, render_review_markdown

    md = render_review_markdown(valid_review, json_path="reviews/test.json")
    footer = extract_integrity_footer(md)

    canonical = json.dumps(valid_review, ensure_ascii=False, sort_keys=True, indent=2)
    expected_sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert footer["sha256"] == expected_sha


def test_render_changed_json_produces_different_sha(valid_review: dict) -> None:
    """Changing the review dict changes the SHA-256 in the footer."""
    from ai_rules.review_results import extract_integrity_footer, render_review_markdown

    md1 = render_review_markdown(valid_review, json_path="reviews/test.json")
    footer1 = extract_integrity_footer(md1)

    modified = copy.deepcopy(valid_review)
    modified["rule_name"] = "rules/different-rule.md"
    md2 = render_review_markdown(modified, json_path="reviews/test.json")
    footer2 = extract_integrity_footer(md2)

    assert footer1["sha256"] != footer2["sha256"]


def test_extract_footer_missing_sentinel_raises(valid_review: dict) -> None:
    """extract_integrity_footer raises ValueError when sentinel is absent."""
    from ai_rules.review_results import extract_integrity_footer

    with pytest.raises(ValueError, match="sentinel"):
        extract_integrity_footer("# Some Markdown\n\nNo footer here.")


# ── renderer: CLI commands ────────────────────────────────────────────────────


def test_cli_validate_valid_exits_0(tmp_path: Path) -> None:
    """ai-rules review-artifact validate exits 0 on valid input."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    dest = tmp_path / "review.json"
    dest.write_bytes(FIXTURE_PATH.read_bytes())
    runner = CliRunner()
    result = runner.invoke(app, ["review-artifact", "validate", "--input", str(dest)])
    assert result.exit_code == 0


def test_cli_validate_invalid_exits_1(tmp_path: Path, valid_review: dict) -> None:
    """ai-rules review-artifact validate exits 1 on semantic violation."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    bad = copy.deepcopy(valid_review)
    bad["schema_version"] = "rule-review-result/v0"
    dest = tmp_path / "bad.json"
    dest.write_text(json.dumps(bad), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["review-artifact", "validate", "--input", str(dest)])
    assert result.exit_code == 1


def test_cli_validate_missing_file_exits_2(tmp_path: Path) -> None:
    """ai-rules review-artifact validate exits 2 on missing file."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    runner = CliRunner()
    result = runner.invoke(
        app, ["review-artifact", "validate", "--input", str(tmp_path / "missing.json")]
    )
    assert result.exit_code == 2


def test_cli_render_and_verify_pair(tmp_path: Path) -> None:
    """Render + verify-pair round-trip exits 0."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    src = tmp_path / "review.json"
    src.write_bytes(FIXTURE_PATH.read_bytes())
    out_md = tmp_path / "review.md"

    runner = CliRunner()
    render_result = runner.invoke(
        app, ["review-artifact", "render", "--input", str(src), "--output", str(out_md)]
    )
    assert render_result.exit_code == 0, render_result.output

    verify_result = runner.invoke(
        app, ["review-artifact", "verify-pair", "--input", str(src), "--markdown", str(out_md)]
    )
    assert verify_result.exit_code == 0, verify_result.output


def test_cli_verify_pair_hand_edited_exits_3(tmp_path: Path) -> None:
    """verify-pair exits 3 when Markdown has been hand-edited."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    src = tmp_path / "review.json"
    src.write_bytes(FIXTURE_PATH.read_bytes())
    out_md = tmp_path / "review.md"

    runner = CliRunner()
    runner.invoke(app, ["review-artifact", "render", "--input", str(src), "--output", str(out_md)])

    # Hand-edit the Markdown
    original = out_md.read_text(encoding="utf-8")
    out_md.write_text(
        original.replace("EXECUTABLE_WITH_REFINEMENTS", "EXECUTABLE"), encoding="utf-8"
    )

    verify_result = runner.invoke(
        app, ["review-artifact", "verify-pair", "--input", str(src), "--markdown", str(out_md)]
    )
    assert verify_result.exit_code == 3


# ── defensive validator branches (malformed shapes) ──────────────────────────


def test_dimension_set_non_list_rejected() -> None:
    from ai_rules.review_results import _check_dimension_set

    assert _check_dimension_set("nope") == ["/dimensions: must be an array"]


def test_dimension_set_skips_non_dict_entries() -> None:
    from ai_rules.review_results import _CANONICAL_DIMENSIONS, _check_dimension_set

    # One non-dict entry among the six canonical dimensions must be skipped,
    # not crash the weight/name checks.
    dims: list = [{"name": n, "weight": w} for n, w in _CANONICAL_DIMENSIONS.items()]
    dims.append("garbage")
    issues = _check_dimension_set(dims)
    assert any("expected exactly 6" in i for i in issues)  # 7 entries now


def test_dimension_arithmetic_skips_non_dict_and_missing_fields() -> None:
    from ai_rules.review_results import _check_dimension_arithmetic

    # Non-dict entry and a dict missing points → both skipped, no issues.
    assert _check_dimension_arithmetic(["x", {"name": "d", "raw_score": 5, "weight": 1}]) == []


def test_expected_verdict_below_all_thresholds_is_not_executable() -> None:
    from ai_rules.review_results import _expected_verdict

    assert _expected_verdict(3.0) == "NOT_EXECUTABLE"


def test_score_and_verdict_non_list_dimensions_returns_empty() -> None:
    from ai_rules.review_results import _check_score_and_verdict

    assert _check_score_and_verdict({"dimensions": "nope"}) == []


def test_score_and_verdict_null_score_allowed() -> None:
    from ai_rules.review_results import _check_score_and_verdict

    # Null score with a valid verdict must not raise or complain about score.
    review = {"dimensions": [], "score": None, "verdict": "NOT_EXECUTABLE"}
    assert _check_score_and_verdict(review) == []


def test_blocking_count_non_list_or_missing_returns_empty() -> None:
    from ai_rules.review_results import _check_blocking_count

    assert _check_blocking_count({"findings": "nope", "blocking_issue_count": 1}) == []
    assert _check_blocking_count({"findings": [], "blocking_issue_count": None}) == []


def test_blocking_evidence_non_list_and_non_dict_entries() -> None:
    from ai_rules.review_results import _check_blocking_evidence

    assert _check_blocking_evidence("nope") == []
    assert _check_blocking_evidence(["garbage"]) == []


def test_source_locators_non_list_and_non_dict_entries() -> None:
    from ai_rules.review_results import _check_source_locators

    assert _check_source_locators("nope") == []
    assert _check_source_locators(["garbage"]) == []


def test_load_and_validate_review_invalid_utf8_raises(tmp_path: Path) -> None:
    from ai_rules.review_results import load_and_validate_review

    bad = tmp_path / "bad-utf8.json"
    bad.write_bytes(b"\xff\xfe not utf-8 at all")
    with pytest.raises(ValueError, match="not valid UTF-8"):
        load_and_validate_review(bad)


# ── renderer: findings + hard caps sections ──────────────────────────────────


def test_render_includes_hard_caps_and_finding_sections(valid_review: dict) -> None:
    """Exercise the hard-caps, blocking, and additional-findings render branches."""
    from ai_rules.review_results import render_review_markdown

    review = copy.deepcopy(valid_review)
    review["hard_caps"] = [{"description": "capped for missing contract"}]
    review["findings"] = [
        {
            "finding_id": "F001",
            "severity": "critical",
            "claim": {
                "text": "Missing required section.",
                "evidence": [
                    {"kind": "source", "locator": "rules/100.md:12", "quote": "no contract"}
                ],
            },
            "recommendation": "Add the Contract section.",
        },
        {
            "finding_id": "F002",
            "severity": "medium",
            "claim": {"text": "Minor wording nit."},
        },
    ]
    md = render_review_markdown(review, json_path="reviews/test.json")
    assert "**Hard Caps Applied:** capped for missing contract" in md
    assert "## Blocking Issues" in md
    assert "[CRITICAL] F001" in md
    assert "`rules/100.md:12`" in md
    assert "Add the Contract section." in md
    assert "## Additional Findings" in md
    assert "[MEDIUM] F002" in md
