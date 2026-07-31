"""Unit tests for rule-loader-manifest/v1 validator.

Tests:
- valid-basic.json passes
- valid-token-budget-deferral.json passes and has required deferral shape
- each invalid-* fixture fails with an issue mentioning the right cause
- direct completeness-violation dict fails
- body-content dict fails
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.manifest import load_and_validate_manifest, validate_manifest

# Resolve the manifests fixture directory relative to this file.
_REPO_ROOT = Path(__file__).parent.parent.parent
_MANIFESTS_DIR = _REPO_ROOT / "fixtures" / "rule_loader_eval" / "manifests"


# ── helpers ───────────────────────────────────────────────────────────────────


def _load(name: str) -> list[str]:
    return load_and_validate_manifest(_MANIFESTS_DIR / name)


def _foundation_only_sequence() -> list[dict]:
    return [
        {
            "order": 1,
            "rule_path": "rules/000-global-core.md",
            "rule_name": "000-global-core.md",
            "reason_type": "foundation",
            "reason": "foundation",
            "context_tier": "Critical",
            "token_estimate": 2550,
            "layer": "FOUNDATION",
            "required": True,
        }
    ]


def _minimal_valid() -> dict:
    """Build a minimal valid manifest dict in Python (no file I/O)."""
    return {
        "schema_version": "rule-loader-manifest/v1",
        "runtime": {
            "primitive": "Task",
            "spawn_evidence": "toolu_test",
            "agent_id": "agent-test",
        },
        "keywords_searched": ["test"],
        "index_evidence": [{"kind": "hook", "target": "hook-injected-manifest"}],
        "candidate_rules": [
            {
                "rule_path": "rules/200-python-core.md",
                "rule_name": "200-python-core.md",
                "reason_type": "extension",
                "reason": "ext=.py HARD match",
                "context_tier": "High",
                "token_estimate": 2600,
                "layer": "HARD",
                "required": True,
            }
        ],
        "candidate_count": 1,
        "load_sequence": [
            *_foundation_only_sequence(),
            {
                "order": 2,
                "rule_path": "rules/200-python-core.md",
                "rule_name": "200-python-core.md",
                "reason_type": "extension",
                "reason": "ext=.py HARD match",
                "context_tier": "High",
                "token_estimate": 2600,
                "layer": "HARD",
                "required": True,
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
    """load_sequence must contain at least one non-foundation entry."""
    import json

    data = json.loads((_MANIFESTS_DIR / "valid-token-budget-deferral.json").read_text())
    non_foundation = [e for e in data["load_sequence"] if e.get("reason_type") != "foundation"]
    assert len(non_foundation) >= 1, (
        "valid-token-budget-deferral.json must have >=1 non-foundation entry in load_sequence"
    )


@pytest.mark.unit
def test_valid_token_budget_has_deferred_entry() -> None:
    """deferred_rules must contain at least one entry with all required keys."""
    import json

    data = json.loads((_MANIFESTS_DIR / "valid-token-budget-deferral.json").read_text())
    dr = data["deferred_rules"]
    assert len(dr) >= 1, "valid-token-budget-deferral.json must have >=1 deferred_rules entry"
    entry = dr[0]
    for key in ("rule_path", "reason_type", "reason", "deferred_because"):
        assert entry.get(key), f"deferred_rules[0] must have non-empty {key!r}"


# ── invalid-missing-agent-id.json ─────────────────────────────────────────────


@pytest.mark.unit
def test_invalid_missing_agent_id_fails() -> None:
    issues = _load("invalid-missing-agent-id.json")
    assert issues, "Expected at least one issue for missing/empty agent_id"
    combined = " ".join(issues)
    assert "agent_id" in combined, f"Expected 'agent_id' mentioned in issues, got: {issues}"


# ── invalid-candidate-count.json ──────────────────────────────────────────────


@pytest.mark.unit
def test_invalid_candidate_count_fails() -> None:
    issues = _load("invalid-candidate-count.json")
    assert issues, "Expected at least one issue for wrong candidate_count"
    combined = " ".join(issues)
    assert "candidate_count" in combined, (
        f"Expected 'candidate_count' mentioned in issues, got: {issues}"
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
    # Add a second candidate that is NOT in load_sequence or deferred_rules.
    manifest["candidate_rules"].append(
        {
            "rule_path": "rules/999-orphan.md",
            "rule_name": "999-orphan.md",
            "reason_type": "activity_keyword",
            "reason": "keyword: orphan",
            "context_tier": "Low",
            "token_estimate": 500,
            "layer": "SOFT",
            "required": False,
        }
    )
    manifest["candidate_count"] = 2
    issues = validate_manifest(manifest)
    assert any("completeness" in i for i in issues), f"Expected a completeness issue, got: {issues}"


@pytest.mark.unit
def test_completeness_both_sides_fails() -> None:
    """A candidate that appears in BOTH load_sequence and deferred_rules is invalid."""
    manifest = _minimal_valid()
    # Place the candidate in both load_sequence AND deferred_rules.
    manifest["deferred_rules"].append(
        {
            "rule_path": "rules/200-python-core.md",
            "rule_name": "200-python-core.md",
            "reason_type": "context_tier_cap",
            "reason": "deferred",
            "context_tier": "High",
            "token_estimate": 2600,
            "layer": "HARD",
            "deferred_because": "test: appears in both",
        }
    )
    issues = validate_manifest(manifest)
    assert any("completeness" in i for i in issues), (
        f"Expected a completeness issue for duplicate placement, got: {issues}"
    )


# ── direct dict: body content ─────────────────────────────────────────────────


@pytest.mark.unit
def test_body_content_dict_fails() -> None:
    """A manifest with a 'content' key in a load_sequence entry is rejected."""
    manifest = _minimal_valid()
    manifest["load_sequence"][1]["content"] = "# Rule body content here..."
    issues = validate_manifest(manifest)
    assert any("body" in i or "content" in i for i in issues), (
        f"Expected a body-content issue, got: {issues}"
    )


@pytest.mark.unit
def test_long_string_value_rejected_as_body() -> None:
    """A string value exceeding 600 chars in a manifest entry is treated as a body."""
    manifest = _minimal_valid()
    manifest["load_sequence"][1]["reason"] = "x" * 601
    issues = validate_manifest(manifest)
    assert any("body" in i for i in issues), (
        f"Expected a body-content issue for long value, got: {issues}"
    )


# ── additional edge cases ─────────────────────────────────────────────────────


@pytest.mark.unit
def test_wrong_schema_version_fails() -> None:
    manifest = _minimal_valid()
    manifest["schema_version"] = "rule-loader-manifest/v0"
    issues = validate_manifest(manifest)
    assert any("schema_version" in i for i in issues)


@pytest.mark.unit
def test_missing_top_level_key_fails() -> None:
    manifest = _minimal_valid()
    del manifest["index_evidence"]
    issues = validate_manifest(manifest)
    assert any("index_evidence" in i for i in issues)


@pytest.mark.unit
def test_empty_index_evidence_fails() -> None:
    manifest = _minimal_valid()
    manifest["index_evidence"] = []
    issues = validate_manifest(manifest)
    assert any("index_evidence" in i for i in issues)


@pytest.mark.unit
def test_empty_load_sequence_fails() -> None:
    manifest = _minimal_valid()
    manifest["load_sequence"] = []
    issues = validate_manifest(manifest)
    assert any("load_sequence" in i for i in issues)


@pytest.mark.unit
def test_rule_path_missing_prefix_fails() -> None:
    manifest = _minimal_valid()
    manifest["candidate_rules"][0]["rule_path"] = "200-python-core.md"  # no "rules/" prefix
    issues = validate_manifest(manifest)
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
