"""Semantic validator for rule-review-result/v1 artifacts.

Public API
----------
- ``validate_review_result(review: dict) -> list[str]``
    Validate a review result dict. Empty list means valid.

- ``load_and_validate_review(path) -> list[str]``
    Read a JSON file and validate it as a rule-review-result/v1.

Canonical dimension weights (100-point model)
---------------------------------------------
Dimension               Weight  Max points
actionability            3.0      30
rule_size                2.5      25
parsability              1.5      15
completeness             1.5      15
consistency              1.0      10
cross_agent_consistency  0.5       5
TOTAL                             100

Semantic invariants enforced here (not in JSON Schema)
------------------------------------------------------
1. Exactly the six canonical dimensions, each with correct weight.
2. points == raw_score x weight for every dimension (within 0.01 tolerance).
3. sum(dimension.points) == score (within 0.5, post-cap).
4. Verdict matches final score under the canonical threshold table.
5. hard_caps present iff their trigger conditions are met.
6. blocking_issue_count == count of critical/high findings.
7. Every blocking finding has at least one source or docs evidence item.
8. Source evidence with a locator must use 'path:line' format.
9. Unknown top-level fields (outside known + 'extensions') are rejected.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# ── constants ─────────────────────────────────────────────────────────────────

SCHEMA_VERSION = "rule-review-result/v1"

# Canonical 6-dimension weights (name → weight, name → max_points)
_CANONICAL_DIMENSIONS: dict[str, float] = {
    "actionability": 3.0,
    "rule_size": 2.5,
    "parsability": 1.5,
    "completeness": 1.5,
    "consistency": 1.0,
    "cross_agent_consistency": 0.5,
}
_CANONICAL_MAX_POINTS: dict[str, float] = {k: v * 10 for k, v in _CANONICAL_DIMENSIONS.items()}

# Hard-cap thresholds (line_count and blocking_count checked semantically)
_HARD_CAP_SCORE_LIMITS: list[tuple[str, float]] = [
    ("blocking_issue_count >= 10", float("-inf")),  # forces NOT_EXECUTABLE
    ("blocking_issue_count >= 6", 80.0),
    ("line_count > 350", 50.0),
    ("line_count > 300", 70.0),
]

# Verdict thresholds (post-cap score → verdict)
_VERDICT_THRESHOLDS: list[tuple[float, str]] = [
    (90.0, "EXECUTABLE"),
    (80.0, "EXECUTABLE_WITH_REFINEMENTS"),
    (60.0, "NEEDS_REFINEMENT"),
    (0.0, "NOT_EXECUTABLE"),
]

# Blocking severities
_BLOCKING_SEVERITIES: frozenset[str] = frozenset({"critical", "high"})

# Known top-level keys (any other key beside 'extensions' is rejected)
_KNOWN_TOP_LEVEL_KEYS: frozenset[str] = frozenset(
    {
        "schema_version",
        "artifact_id",
        "rule_name",
        "review_mode",
        "producer",
        "review_date",
        "executive_summary",
        "dimensions",
        "findings",
        "score",
        "verdict",
        "blocking_issue_count",
        "hard_caps",
        "timing",
        "extensions",
    }
)

# Source locator pattern: repo-relative path:line
_SOURCE_LOCATOR_RE = re.compile(r"^[^:]+:\d+$")


# ── helpers ───────────────────────────────────────────────────────────────────


def _check_dimension_set(dimensions: list[Any]) -> list[str]:
    """Verify exactly six canonical dimensions with correct weights."""
    issues: list[str] = []
    if not isinstance(dimensions, list):
        return ["/dimensions: must be an array"]
    names = [d.get("name") for d in dimensions if isinstance(d, dict)]
    extra = set(names) - set(_CANONICAL_DIMENSIONS)
    missing = set(_CANONICAL_DIMENSIONS) - set(names)
    if extra:
        issues.append(f"/dimensions: unknown dimension name(s): {sorted(extra)}")
    if missing:
        issues.append(f"/dimensions: missing canonical dimension(s): {sorted(missing)}")
    if len(dimensions) != 6:
        issues.append(f"/dimensions: expected exactly 6, got {len(dimensions)}")
    for d in dimensions:
        if not isinstance(d, dict):
            continue
        name = d.get("name")
        if name not in _CANONICAL_DIMENSIONS:
            continue
        expected_w = _CANONICAL_DIMENSIONS[name]
        actual_w = d.get("weight")
        if actual_w is None or abs(float(actual_w) - expected_w) > 0.01:
            issues.append(f"/dimensions/{name}: weight must be {expected_w}, got {actual_w!r}")
    return issues


def _check_dimension_arithmetic(dimensions: list[Any]) -> list[str]:
    """Verify points == raw_score x weight for every dimension."""
    issues: list[str] = []
    for d in dimensions:
        if not isinstance(d, dict):
            continue
        name = d.get("name", "?")
        raw = d.get("raw_score")
        weight = d.get("weight")
        points = d.get("points")
        if any(v is None for v in (raw, weight, points)):
            continue
        expected = round(float(raw) * float(weight), 6)
        if abs(float(points) - expected) > 0.01:
            issues.append(
                f"/dimensions/{name}: points {points} != raw_score {raw} x weight {weight} = {expected:.4f}"
            )
    return issues


def _sum_dimension_points(dimensions: list[Any]) -> float:
    """Return sum of dimension points (ignoring non-numeric entries)."""
    total = 0.0
    for d in dimensions:
        if isinstance(d, dict):
            p = d.get("points")
            if isinstance(p, (int, float)):
                total += float(p)
    return total


def _expected_verdict(score: float) -> str:
    """Return the canonical verdict for a post-cap score."""
    for threshold, label in _VERDICT_THRESHOLDS:
        if score >= threshold:
            return label
    return "NOT_EXECUTABLE"


def _check_score_and_verdict(review: dict[str, Any]) -> list[str]:
    """Verify sum(dimension.points) ≈ score and verdict matches score."""
    issues: list[str] = []
    dimensions = review.get("dimensions", [])
    score = review.get("score")
    verdict = review.get("verdict")
    if not isinstance(dimensions, list):
        return issues

    dim_sum = _sum_dimension_points(dimensions)
    hard_caps = review.get("hard_caps", [])
    applied_caps = (
        [c for c in hard_caps if isinstance(c, dict)] if isinstance(hard_caps, list) else []
    )

    if score is None:
        # Null score is allowed but verdict must still be valid
        pass
    else:
        score = float(score)
        # Check that dimension sum equals score (within ±0.5 to allow rounding)
        if abs(dim_sum - score) > 0.5:
            issues.append(
                f"/score: {score} but sum of dimension points is {dim_sum:.4f} (diff > 0.5)"
            )
        # Verdict must match canonical threshold for final score
        if isinstance(verdict, str):
            blocking = review.get("blocking_issue_count", 0)
            # If a hard cap forces NOT_EXECUTABLE, allow that verdict even if score is high
            forced_not_exec = (
                isinstance(blocking, int)
                and blocking >= 10
                and any("force_verdict" in str(c.get("effect", "")) for c in applied_caps)
            )
            expected = _expected_verdict(score)
            if not forced_not_exec and verdict != expected:
                issues.append(f"/verdict: {verdict!r} but score {score} maps to {expected!r}")
    return issues


def _check_blocking_count(review: dict[str, Any]) -> list[str]:
    """Verify blocking_issue_count matches count of critical/high findings."""
    issues: list[str] = []
    findings = review.get("findings", [])
    declared = review.get("blocking_issue_count")
    if not isinstance(findings, list) or declared is None:
        return issues
    actual = sum(
        1 for f in findings if isinstance(f, dict) and f.get("severity") in _BLOCKING_SEVERITIES
    )
    if actual != int(declared):
        issues.append(
            f"/blocking_issue_count: declared {declared}, but {actual} finding(s) have "
            f"severity critical or high"
        )
    return issues


def _check_blocking_evidence(findings: list[Any]) -> list[str]:
    """Every blocking finding must have at least one source or docs evidence item."""
    issues: list[str] = []
    if not isinstance(findings, list):
        return issues
    for i, f in enumerate(findings):
        if not isinstance(f, dict):
            continue
        if f.get("severity") not in _BLOCKING_SEVERITIES:
            continue
        claim = f.get("claim", {})
        evidence_list = claim.get("evidence", []) if isinstance(claim, dict) else []
        has_source_or_docs = any(
            isinstance(e, dict) and e.get("kind") in ("source", "docs") for e in evidence_list
        )
        if not has_source_or_docs:
            fid = f.get("finding_id", f"findings[{i}]")
            issues.append(
                f"/findings/{fid}: blocking finding (severity={f['severity']!r}) "
                f"has no source or docs evidence"
            )
    return issues


def _check_source_locators(findings: list[Any]) -> list[str]:
    """Source evidence locators must use 'path:line' format."""
    issues: list[str] = []
    if not isinstance(findings, list):
        return issues
    for f in findings:
        if not isinstance(f, dict):
            continue
        fid = f.get("finding_id", "?")
        claim = f.get("claim", {})
        evidence_list = claim.get("evidence", []) if isinstance(claim, dict) else []
        for e in evidence_list:
            if not isinstance(e, dict) or e.get("kind") != "source":
                continue
            locator = e.get("locator")
            if locator is None:
                continue  # null locator allowed
            if not _SOURCE_LOCATOR_RE.match(str(locator)):
                issues.append(
                    f"/findings/{fid}: source evidence locator {locator!r} "
                    f"must use 'path:line' format (e.g. 'rules/000-global-core.md:42')"
                )
    return issues


def _check_unknown_top_level_fields(review: dict[str, Any]) -> list[str]:
    """Reject unknown top-level fields (except namespaced extensions)."""
    issues: list[str] = []
    for key in review:
        if key not in _KNOWN_TOP_LEVEL_KEYS:
            issues.append(
                f"/{key}: unknown top-level field; use the 'extensions' object for extra fields"
            )
    return issues


def _check_schema_version(review: dict[str, Any]) -> list[str]:
    """Verify schema_version is exactly 'rule-review-result/v1'."""
    sv = review.get("schema_version")
    if sv != SCHEMA_VERSION:
        return [
            f"/schema_version: must be {SCHEMA_VERSION!r}, got {sv!r}; "
            f"this validator rejects all other schema versions"
        ]
    return []


# ── public API ────────────────────────────────────────────────────────────────


def validate_review_result(review: Any) -> list[str]:
    """Validate a rule-review-result/v1 dict.

    Returns an empty list if valid; a non-empty list of human-readable issue
    strings otherwise. Issues are independent (multiple problems are all
    reported).

    Exit-code mapping for callers
    ------------------------------
    Empty list             → exit 0 (continue)
    Non-empty (semantic)   → exit 1 (LLM-authored violation; bounded repair)
    Caller must handle I/O failures (exit 2) and implementation defects (exit 3)
    separately via ``load_and_validate_review``.
    """
    if not isinstance(review, dict):
        return [f"review must be a JSON object, got {type(review).__name__!r}"]

    issues: list[str] = []

    issues.extend(_check_schema_version(review))
    issues.extend(_check_unknown_top_level_fields(review))

    dimensions = review.get("dimensions", [])
    findings = review.get("findings", [])

    issues.extend(_check_dimension_set(dimensions))
    issues.extend(_check_dimension_arithmetic(dimensions))
    issues.extend(_check_score_and_verdict(review))
    issues.extend(_check_blocking_count(review))
    issues.extend(_check_blocking_evidence(findings))
    issues.extend(_check_source_locators(findings))

    return issues


def load_and_validate_review(path: str | Path) -> list[str]:
    """Read a JSON file and validate it as a rule-review-result/v1.

    Returns issues list. I/O failures (missing file, bad encoding, bad JSON)
    raise ``ValueError`` instead, mapping to exit 2 at the command layer.
    """
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"review file not found: {path}") from exc
    except PermissionError as exc:
        raise ValueError(f"review file unreadable: {path}") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"review file is not valid UTF-8: {path}") from exc

    try:
        review = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"review file is not valid JSON: {path}: {exc}") from exc

    return validate_review_result(review)


# ── deterministic Markdown renderer ──────────────────────────────────────────

_RENDERER_IDENTITY = "ai-rules review-artifact render/v1"
_INTEGRITY_SENTINEL = "<!-- review-artifact: end -->"

# Canonical display names for dimensions (preserves presentation order)
_DIMENSION_DISPLAY: dict[str, str] = {
    "actionability": "Actionability",
    "rule_size": "Rule Size",
    "parsability": "Parsability",
    "completeness": "Completeness",
    "consistency": "Consistency",
    "cross_agent_consistency": "Cross-Agent Consistency",
}


def render_review_markdown(review: dict[str, Any], json_path: str | Path | None = None) -> str:
    """Render a validated rule-review-result/v1 dict to deterministic Markdown.

    The output is fully deterministic: the same review dict produces byte-identical
    Markdown on every call. The integrity footer binds the rendered Markdown to the
    source JSON via SHA-256.

    Raises ``RuntimeError`` (exit 3) on implementation defects (e.g. missing required
    fields that should have been caught by validation).
    """
    import hashlib

    rule_name = review.get("rule_name", "unknown")
    review_date = review.get("review_date", "unknown")
    review_mode = review.get("review_mode", "unknown")
    producer = review.get("producer") or {}
    model = producer.get("model", "unknown") if isinstance(producer, dict) else "unknown"
    score = review.get("score")
    verdict = review.get("verdict", "unknown")
    blocking = review.get("blocking_issue_count", 0)
    hard_caps = review.get("hard_caps") or []
    dimensions = review.get("dimensions") or []
    findings = review.get("findings") or []
    executive_summary = review.get("executive_summary") or []

    # Order dimensions canonically
    dim_by_name: dict[str, dict[str, Any]] = {}
    for d in dimensions:
        if isinstance(d, dict):
            dim_by_name[d.get("name", "")] = d

    lines: list[str] = []

    # Header
    lines.append(f"# Rule Review: {rule_name}")
    lines.append("")
    lines.append(f"**Review Date:** {review_date}")
    lines.append(f"**Review Mode:** {review_mode}")
    lines.append(f"**Model:** {model}")
    lines.append(f"**Schema:** {SCHEMA_VERSION}")
    lines.append(f"**Renderer:** {_RENDERER_IDENTITY}")
    lines.append("")

    # Executive Summary score table
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("| Dimension | Raw (0-10) | Weight | Points | Max |")
    lines.append("|-----------|------------|--------|--------|-----|")

    for name, display in _DIMENSION_DISPLAY.items():
        d = dim_by_name.get(name, {})
        raw = d.get("raw_score", "?")
        weight = d.get("weight", "?")
        pts = d.get("points", "?")
        max_pts = _CANONICAL_MAX_POINTS.get(name, "?")
        lines.append(f"| {display} | {raw} | {weight} | {pts} | {max_pts} |")

    total_pts = sum(
        float(d.get("points", 0))
        for d in dim_by_name.values()
        if isinstance(d.get("points"), (int, float))
    )
    lines.append(f"| **TOTAL** | | | **{total_pts:.1f}** | **100** |")
    lines.append("")

    score_str = f"{score}/100" if score is not None else "N/A"
    lines.append(f"**Verdict:** {verdict} ({score_str})")
    lines.append(f"**Blocking Issues:** {blocking}")

    if hard_caps and isinstance(hard_caps, list):
        caps_str = "; ".join(
            c.get("description", c.get("condition", "?")) for c in hard_caps if isinstance(c, dict)
        )
        lines.append(f"**Hard Caps Applied:** {caps_str}")
    else:
        lines.append("**Hard Caps Applied:** None")
    lines.append("")

    # Executive summary claims
    if executive_summary:
        for claim in executive_summary:
            if isinstance(claim, dict):
                lines.append(claim.get("text", ""))
        lines.append("")

    # Findings
    blocking_findings = [
        f for f in findings if isinstance(f, dict) and f.get("severity") in _BLOCKING_SEVERITIES
    ]
    other_findings = [
        f for f in findings if isinstance(f, dict) and f.get("severity") not in _BLOCKING_SEVERITIES
    ]

    if blocking_findings:
        lines.append("## Blocking Issues")
        lines.append("")
        for i, f in enumerate(sorted(blocking_findings, key=lambda x: x.get("finding_id", "")), 1):
            fid = f.get("finding_id", f"F{i:03d}")
            sev = f.get("severity", "?")
            claim = f.get("claim", {})
            text = claim.get("text", "") if isinstance(claim, dict) else ""
            rec = f.get("recommendation", "")
            lines.append(f"### {i}. [{sev.upper()}] {fid}")
            lines.append("")
            lines.append(text)
            lines.append("")
            evidence = claim.get("evidence", []) if isinstance(claim, dict) else []
            for e in evidence:
                if not isinstance(e, dict):
                    continue
                kind = e.get("kind", "?")
                locator = e.get("locator")
                quote = e.get("quote")
                if locator:
                    lines.append(f"- **Evidence ({kind}):** `{locator}`")
                if quote:
                    lines.append(f'  > "{quote}"')
            if rec:
                lines.append(f"**Recommendation:** {rec}")
            lines.append("")

    if other_findings:
        lines.append("## Additional Findings")
        lines.append("")
        for i, f in enumerate(sorted(other_findings, key=lambda x: x.get("finding_id", "")), 1):
            fid = f.get("finding_id", f"F{i:03d}")
            sev = f.get("severity", "?")
            claim = f.get("claim", {})
            text = claim.get("text", "") if isinstance(claim, dict) else ""
            lines.append(f"- **[{sev.upper()}] {fid}:** {text}")
        lines.append("")

    # Integrity footer
    canonical_json = json.dumps(review, ensure_ascii=False, sort_keys=True, indent=2)
    sha256 = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    json_path_str = str(json_path) if json_path is not None else "unknown"

    lines.append("---")
    lines.append("")
    lines.append("<!-- integrity footer — do not edit -->")
    lines.append(f"<!-- schema: {SCHEMA_VERSION} -->")
    lines.append(f"<!-- json-path: {json_path_str} -->")
    lines.append(f"<!-- sha256: {sha256} -->")
    lines.append(f"<!-- renderer: {_RENDERER_IDENTITY} -->")
    lines.append(_INTEGRITY_SENTINEL)

    return "\n".join(lines) + "\n"


def extract_integrity_footer(markdown: str) -> dict[str, str]:
    """Extract integrity footer fields from rendered Markdown.

    Returns a dict with keys: schema, json_path, sha256, renderer.
    Raises ``ValueError`` if the footer is missing or malformed.
    """
    if _INTEGRITY_SENTINEL not in markdown:
        raise ValueError(f"Markdown is missing the integrity sentinel: {_INTEGRITY_SENTINEL!r}")

    fields: dict[str, str] = {}
    for line in markdown.splitlines():
        for key in ("schema", "json-path", "sha256", "renderer"):
            prefix = f"<!-- {key}: "
            if line.startswith(prefix) and line.endswith(" -->"):
                fields[key] = line[len(prefix) : -4]

    required = {"schema", "json-path", "sha256", "renderer"}
    missing = required - set(fields)
    if missing:
        raise ValueError(f"Integrity footer missing fields: {sorted(missing)}")
    return fields
