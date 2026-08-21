"""Legacy rejection tests for rule-loader-manifest/v1 and v2.

These tests serve as negative controls proving that the old agent-authored
manifest formats are now rejected with an unsupported-schema error. They
are intentionally preserved as the legacy-tolerance coverage required by
the Phase 3 cutover plan.
"""

from __future__ import annotations

import pytest

from ai_rules.rule_loader_eval.manifest import _LEGACY_SCHEMA_VERSIONS, validate_manifest


@pytest.mark.unit
@pytest.mark.parametrize("legacy_sv", sorted(_LEGACY_SCHEMA_VERSIONS))
def test_legacy_manifest_versions_are_rejected(legacy_sv: str) -> None:
    """rule-loader-manifest/v1 and v2 must raise 'unsupported schema version' error."""
    manifest = {
        "schema_version": legacy_sv,
        "load_sequence": [],
    }
    issues = validate_manifest(manifest)
    assert issues, f"Expected rejection for {legacy_sv!r}, got empty issues"
    combined = " ".join(issues)
    assert "unsupported schema version" in combined, (
        f"Expected 'unsupported schema version' for {legacy_sv!r}, got: {issues}"
    )


@pytest.mark.unit
def test_v1_manifest_with_all_required_fields_still_rejected() -> None:
    """Even a well-formed v1 manifest is rejected after cutover."""
    manifest = {
        "schema_version": "rule-loader-manifest/v1",
        "runtime": {"primitive": "Task", "spawn_evidence": "x", "agent_id": "y"},
        "keywords_searched": ["python"],
        "index_evidence": [{"kind": "hook", "target": "hook-injected-manifest"}],
        "candidate_rules": [
            {
                "rule_path": "rules/200-python-core.md",
                "rule_name": "200-python-core.md",
                "reason_type": "extension",
                "reason": "ext=.py",
                "context_tier": "High",
                "token_estimate": 2600,
                "layer": "HARD",
                "required": True,
            }
        ],
        "candidate_count": 1,
        "load_sequence": [
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
        ],
        "deferred_rules": [],
    }
    issues = validate_manifest(manifest)
    assert any("unsupported schema version" in i for i in issues), (
        f"Expected unsupported-schema rejection, got: {issues}"
    )
