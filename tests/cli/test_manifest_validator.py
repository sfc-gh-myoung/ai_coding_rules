"""Unit tests for rule-loader-matcher/v1 validator and legacy rejection.

Tests:
- valid-basic.json passes
- valid-token-budget-deferral.json passes and has required deferral shape
- each invalid-* fixture fails with an issue mentioning the right cause
- direct completeness-violation dict fails
- body-content dict fails
- legacy v1/v2 manifests are rejected with unsupported-schema error
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.manifest import (
    _LEGACY_SCHEMA_VERSIONS,
    load_and_validate_manifest,
    validate_manifest,
    validate_matcher_manifest,
)

# Resolve the manifests fixture directory relative to this file.
_REPO_ROOT = Path(__file__).parent.parent.parent
_MANIFESTS_DIR = _REPO_ROOT / "fixtures" / "rule_loader_eval" / "manifests"


# ── helpers ───────────────────────────────────────────────────────────────────


def _load(name: str) -> list[str]:
    return load_and_validate_manifest(_MANIFESTS_DIR / name)


def _minimal_valid() -> dict:
    """Build a minimal valid matcher/v1 manifest dict."""
    return {
        "schema_version": "rule-loader-matcher/v1",
        "candidate_rules": [
            {
                "rule_path": "rules/200-python-core.md",
                "layer": "SOFT",
                "context_tier": "High",
                "description": "Python core",
            }
        ],
        "load_sequence": [
            {
                "rule_path": "rules/000-global-core.md",
                "layer": "HARD",
                "context_tier": "Critical",
                "description": "Foundation",
            },
            {
                "rule_path": "rules/200-python-core.md",
                "layer": "SOFT",
                "context_tier": "High",
                "description": "Python core",
            },
        ],
        "deferred_rules": [],
    }


# ── valid-basic.json ──────────────────────────────────────────────────────────


@pytest.mark.unit
def test_valid_basic_passes() -> None:
    issues = _load("valid-basic.json")
    assert issues == [], f"Expected no issues, got: {issues}"


# ── valid-token-budget-deferral.json ──────────────────────────────────────────


@pytest.mark.unit
def test_valid_token_budget_passes() -> None:
    issues = _load("valid-token-budget-deferral.json")
    assert issues == [], f"Expected no issues, got: {issues}"


@pytest.mark.unit
def test_valid_token_budget_has_nonfoundation_load_sequence_entry() -> None:
    """load_sequence must contain at least one non-HARD entry."""
    import json

    data = json.loads((_MANIFESTS_DIR / "valid-token-budget-deferral.json").read_text())
    non_foundation = [e for e in data["load_sequence"] if e.get("layer") != "HARD"]
    assert len(non_foundation) >= 1, (
        "valid-token-budget-deferral.json must have >=1 non-HARD entry in load_sequence"
    )


@pytest.mark.unit
def test_valid_token_budget_has_deferred_entry() -> None:
    """deferred_rules must contain at least one entry with required keys."""
    import json

    data = json.loads((_MANIFESTS_DIR / "valid-token-budget-deferral.json").read_text())
    dr = data["deferred_rules"]
    assert len(dr) >= 1, "valid-token-budget-deferral.json must have >=1 deferred_rules entry"
    entry = dr[0]
    assert entry.get("rule_path"), "deferred_rules[0] must have non-empty 'rule_path'"
    assert entry.get("reason"), "deferred_rules[0] must have non-empty 'reason'"


# ── invalid-missing-agent-id.json (now: bad rule_path prefix) ─────────────────


@pytest.mark.unit
def test_invalid_rule_path_prefix_fails() -> None:
    issues = _load("invalid-missing-agent-id.json")
    assert issues, "Expected at least one issue for missing rules/ prefix"
    combined = " ".join(issues)
    assert "rule_path" in combined, f"Expected 'rule_path' mentioned in issues, got: {issues}"


# ── invalid-candidate-count.json (now: empty load_sequence) ──────────────────


@pytest.mark.unit
def test_invalid_empty_load_sequence_fails() -> None:
    issues = _load("invalid-candidate-count.json")
    assert issues, "Expected at least one issue for empty load_sequence"
    combined = " ".join(issues)
    assert "load_sequence" in combined or "completeness" in combined, (
        f"Expected 'load_sequence' or 'completeness' mentioned in issues, got: {issues}"
    )


# ── invalid-incomplete-candidate.json ────────────────────────────────────────


@pytest.mark.unit
def test_invalid_incomplete_candidate_fails() -> None:
    """A candidate whose rule_path doesn't appear in load_sequence or deferred_rules."""
    issues = _load("invalid-incomplete-candidate.json")
    assert issues, "Expected at least one completeness issue"
    combined = " ".join(issues)
    assert "completeness" in combined, f"Expected 'completeness' mentioned in issues, got: {issues}"


# ── invalid-contains-body.json ────────────────────────────────────────────────


@pytest.mark.unit
def test_invalid_contains_body_fails() -> None:
    issues = _load("invalid-contains-body.json")
    assert issues, "Expected at least one issue for body content in manifest"
    combined = " ".join(issues)
    assert "body" in combined or "content" in combined, (
        f"Expected 'body' or 'content' mentioned in issues, got: {issues}"
    )


# ── direct dict: completeness violation ──────────────────────────────────────


@pytest.mark.unit
def test_completeness_violation_dict_fails() -> None:
    """A candidate not in load_sequence or deferred_rules triggers a completeness error."""
    manifest = _minimal_valid()
    manifest["candidate_rules"].append(
        {
            "rule_path": "rules/999-orphan.md",
            "layer": "SOFT",
            "context_tier": "Low",
            "description": "orphan",
        }
    )
    issues = validate_matcher_manifest(manifest)
    assert any("completeness" in i for i in issues), f"Expected a completeness issue, got: {issues}"


@pytest.mark.unit
def test_completeness_both_sides_fails() -> None:
    """A candidate in both load_sequence and deferred_rules is invalid."""
    manifest = _minimal_valid()
    manifest["deferred_rules"].append(
        {"rule_path": "rules/200-python-core.md", "reason": "token_budget"}
    )
    issues = validate_matcher_manifest(manifest)
    assert any("completeness" in i for i in issues), (
        f"Expected a completeness issue for duplicate placement, got: {issues}"
    )


# ── direct dict: body content ─────────────────────────────────────────────────


@pytest.mark.unit
def test_body_content_dict_fails() -> None:
    """A manifest with a 'content' key in a load_sequence entry is rejected."""
    manifest = _minimal_valid()
    manifest["load_sequence"][1]["content"] = "# Rule body content here..."
    issues = validate_matcher_manifest(manifest)
    assert any("body" in i or "content" in i for i in issues), (
        f"Expected a body-content issue, got: {issues}"
    )


@pytest.mark.unit
def test_long_string_value_rejected_as_body() -> None:
    """A string value exceeding 600 chars in a manifest entry is treated as a body."""
    manifest = _minimal_valid()
    manifest["load_sequence"][1]["description"] = "x" * 601
    issues = validate_matcher_manifest(manifest)
    assert any("body" in i for i in issues), (
        f"Expected a body-content issue for long value, got: {issues}"
    )


# ── additional edge cases ─────────────────────────────────────────────────────


@pytest.mark.unit
def test_wrong_schema_version_fails() -> None:
    manifest = _minimal_valid()
    manifest["schema_version"] = "rule-loader-matcher/v99"
    issues = validate_matcher_manifest(manifest)
    assert any("schema_version" in i for i in issues)


@pytest.mark.unit
def test_empty_load_sequence_fails() -> None:
    manifest = _minimal_valid()
    manifest["load_sequence"] = []
    issues = validate_matcher_manifest(manifest)
    assert any("load_sequence" in i for i in issues)


@pytest.mark.unit
def test_rule_path_missing_prefix_fails() -> None:
    manifest = _minimal_valid()
    manifest["candidate_rules"][0]["rule_path"] = "200-python-core.md"
    issues = validate_matcher_manifest(manifest)
    assert any("rule_path" in i for i in issues)


@pytest.mark.unit
def test_load_and_validate_nonexistent_file_returns_issue() -> None:
    issues = load_and_validate_manifest("/tmp/nonexistent-manifest-xyz.json")
    assert issues
    assert any("cannot read" in i for i in issues)


@pytest.mark.unit
def test_load_and_validate_invalid_json_returns_issue(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{ not valid json }")
    issues = load_and_validate_manifest(bad)
    assert issues
    assert any("invalid JSON" in i for i in issues)


# ── legacy rejection tests ────────────────────────────────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize("legacy_sv", sorted(_LEGACY_SCHEMA_VERSIONS))
def test_legacy_schema_versions_rejected(legacy_sv: str) -> None:
    """rule-loader-manifest/v1 and v2 must be rejected with unsupported-schema error."""
    manifest = {"schema_version": legacy_sv, "load_sequence": []}
    issues = validate_manifest(manifest)
    assert issues, f"Expected rejection for {legacy_sv}"
    combined = " ".join(issues)
    assert "unsupported schema version" in combined, (
        f"Expected 'unsupported schema version' in rejection for {legacy_sv}, got: {issues}"
    )


@pytest.mark.unit
def test_validate_manifest_delegates_to_matcher_validator_for_v1() -> None:
    """validate_manifest passes matcher/v1 input through to validate_matcher_manifest."""
    manifest = _minimal_valid()
    assert validate_manifest(manifest) == []
