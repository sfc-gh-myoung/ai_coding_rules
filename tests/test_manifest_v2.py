"""Unit tests for rule-loader-manifest/v2 schema validation.

Covered invariants (per plan §5.3, §8.3 and skills/rule-loader/SKILL.md):

- v2 manifest with valid additive fields validates cleanly.
- HARD candidates never appear in ``deferred_rules`` with
  ``reason_type: "second_pass_rejected"``.
- SOFT candidates rejected in Phase 3.5 appear in ``deferred_rules`` with
  ``reason_type: "second_pass_rejected"``.
- The completeness invariant is preserved (candidate is in load_sequence or deferred).
- v1 manifests remain accepted (backward compatibility during rollout).
"""

from __future__ import annotations

import copy

from ai_rules.rule_loader_eval.manifest import (
    SCHEMA_VERSION_V1,
    SCHEMA_VERSION_V2,
    validate_manifest,
)


def _v2_hard_only_manifest() -> dict:
    """Return a minimal-but-valid v2 manifest with one HARD foundation rule."""
    return {
        "schema_version": SCHEMA_VERSION_V2,
        "runtime": {
            "primitive": "Task",
            "spawn_evidence": "tool_call_abc",
            "agent_id": "agent_123",
        },
        "keywords_searched": ["python"],
        "index_evidence": [
            {
                "kind": "grep",
                "target": "rules/RULES_INDEX.md",
                "query": "python",
                "result_summary": "matched 200-python-core.md",
            }
        ],
        "candidate_rules": [
            {
                "rule_path": "rules/000-global-core.md",
                "rule_name": "000-global-core.md",
                "reason_type": "foundation",
                "reason": "always loaded",
                "context_tier": "Critical",
                "token_estimate": 2550,
                "layer": "HARD",
                "required": True,
                "second_pass": {
                    "evaluated": False,
                    "confirmed": True,
                    "confirmation_reason": "hard-candidate-exempt",
                },
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
        "second_pass_evidence": [],
    }


def _v2_mixed_manifest() -> dict:
    """v2 manifest with one HARD rule (loaded), one SOFT accepted, one SOFT rejected."""
    manifest = _v2_hard_only_manifest()
    manifest["keywords_searched"] = ["pytest", "fastapi"]
    manifest["candidate_rules"].extend(
        [
            {
                "rule_path": "rules/206-python-pytest.md",
                "rule_name": "206-python-pytest.md",
                "reason_type": "activity_keyword",
                "reason": "kw:pytest matched",
                "context_tier": "High",
                "token_estimate": 1800,
                "layer": "SOFT",
                "required": False,
                "second_pass": {
                    "evaluated": True,
                    "confirmed": True,
                    "confirmation_reason": "scope-overlap: pytest",
                    "scope_excerpt_hash": "sha256:aa",
                },
            },
            {
                "rule_path": "rules/210c-python-fastapi-deployment.md",
                "rule_name": "210c-python-fastapi-deployment.md",
                "reason_type": "activity_keyword",
                "reason": "kw:fastapi matched",
                "context_tier": "High",
                "token_estimate": 2200,
                "layer": "SOFT",
                "required": False,
                "second_pass": {
                    "evaluated": True,
                    "confirmed": False,
                    "confirmation_reason": "no-scope-overlap: request tokens absent from Scope",
                    "scope_excerpt_hash": "sha256:bb",
                },
            },
        ]
    )
    manifest["candidate_count"] = 3
    manifest["load_sequence"].append(
        {
            "order": 2,
            "rule_path": "rules/206-python-pytest.md",
            "rule_name": "206-python-pytest.md",
            "reason_type": "activity_keyword",
            "reason": "kw:pytest matched",
            "context_tier": "High",
            "token_estimate": 1800,
            "layer": "SOFT",
            "required": False,
        }
    )
    manifest["deferred_rules"].append(
        {
            "rule_path": "rules/210c-python-fastapi-deployment.md",
            "rule_name": "210c-python-fastapi-deployment.md",
            "reason_type": "second_pass_rejected",
            "reason": "no-scope-overlap: request tokens absent from Scope",
            "deferred_because": "Phase 3.5 second-pass rejected",
            "context_tier": "High",
            "token_estimate": 2200,
            "layer": "SOFT",
        }
    )
    manifest["second_pass_evidence"] = [
        {
            "rule_path": "rules/206-python-pytest.md",
            "confirmed": True,
            "reason": "scope-overlap: pytest",
        },
        {
            "rule_path": "rules/210c-python-fastapi-deployment.md",
            "confirmed": False,
            "reason": "no-scope-overlap: request tokens absent from Scope",
        },
    ]
    return manifest


# ── manifest_v2 tests ───────────────────────────────────────────────────────


def test_manifest_v2_hard_only_is_valid() -> None:
    """A v2 manifest with only a HARD foundation rule validates cleanly."""
    assert validate_manifest(_v2_hard_only_manifest()) == []


def test_manifest_v2_mixed_hard_and_soft_is_valid() -> None:
    """A v2 manifest with HARD + SOFT-accepted + SOFT-rejected validates cleanly."""
    assert validate_manifest(_v2_mixed_manifest()) == []


def test_manifest_v2_soft_rejected_uses_second_pass_rejected() -> None:
    """SOFT candidates rejected in Phase 3.5 appear in deferred_rules with the
    ``second_pass_rejected`` reason_type. Manifest is valid.
    """
    manifest = _v2_mixed_manifest()
    rejected = next(
        e
        for e in manifest["deferred_rules"]
        if e["rule_path"] == "rules/210c-python-fastapi-deployment.md"
    )
    assert rejected["reason_type"] == "second_pass_rejected"
    assert validate_manifest(manifest) == []


def test_manifest_v2_hard_candidate_never_second_pass_rejected() -> None:
    """A HARD candidate placed in deferred_rules with reason_type
    ``second_pass_rejected`` MUST produce a validation issue.
    """
    manifest = _v2_mixed_manifest()
    # Corrupt: mark the HARD foundation rule as second_pass_rejected.
    manifest["deferred_rules"].append(
        {
            "rule_path": "rules/000-global-core.md",
            "rule_name": "000-global-core.md",
            "reason_type": "second_pass_rejected",
            "reason": "invalid — HARD candidates are exempt",
            "deferred_because": "test-corruption",
            "context_tier": "Critical",
            "token_estimate": 2550,
            "layer": "HARD",
        }
    )
    issues = validate_manifest(manifest)
    assert any("HARD candidate" in issue and "second_pass_rejected" in issue for issue in issues), (
        issues
    )


def test_manifest_v2_completeness_invariant_holds() -> None:
    """Every candidate_rules[*].rule_path must appear in exactly one of
    load_sequence or deferred_rules (completeness invariant).
    """
    manifest = _v2_mixed_manifest()
    # Corrupt: drop the SOFT-accepted rule from load_sequence.
    manifest["load_sequence"] = [
        entry
        for entry in manifest["load_sequence"]
        if entry["rule_path"] != "rules/206-python-pytest.md"
    ]
    issues = validate_manifest(manifest)
    assert any("completeness" in issue and "206-python-pytest.md" in issue for issue in issues), (
        issues
    )


def test_manifest_v2_missing_second_pass_annotation_fails() -> None:
    """Every candidate in v2 must carry a ``second_pass`` annotation."""
    manifest = _v2_mixed_manifest()
    del manifest["candidate_rules"][1]["second_pass"]  # remove from SOFT-accepted
    issues = validate_manifest(manifest)
    assert any("second_pass" in issue for issue in issues), issues


def test_manifest_v2_missing_second_pass_evidence_root_fails() -> None:
    """v2 manifests must have ``second_pass_evidence`` at root."""
    manifest = _v2_mixed_manifest()
    del manifest["second_pass_evidence"]
    issues = validate_manifest(manifest)
    assert any("second_pass_evidence" in issue for issue in issues), issues


def test_manifest_v2_hard_candidate_wrong_confirmation_reason_fails() -> None:
    """HARD candidates must use ``confirmation_reason='hard-candidate-exempt'``."""
    manifest = _v2_mixed_manifest()
    manifest["candidate_rules"][0]["second_pass"]["confirmation_reason"] = "wrong-value"
    issues = validate_manifest(manifest)
    assert any("hard-candidate-exempt" in issue for issue in issues), issues


def test_manifest_v2_hard_candidate_evaluated_true_fails() -> None:
    """HARD candidates must have ``evaluated: false`` (they are exempt)."""
    manifest = _v2_mixed_manifest()
    manifest["candidate_rules"][0]["second_pass"]["evaluated"] = True
    issues = validate_manifest(manifest)
    assert any("evaluated=false" in issue for issue in issues), issues


# ── backward-compat: manifest_v2 validator still accepts v1 ─────────────────


def test_manifest_v2_validator_still_accepts_v1() -> None:
    """v1 manifests remain accepted during rollout (backward compatibility).

    v1 manifests have no ``second_pass`` annotations and no
    ``second_pass_evidence`` root; the validator must NOT require them for v1.
    """
    v1_manifest = copy.deepcopy(_v2_hard_only_manifest())
    v1_manifest["schema_version"] = SCHEMA_VERSION_V1
    # Strip v2-only additive fields — v1 must not require them.
    del v1_manifest["second_pass_evidence"]
    del v1_manifest["candidate_rules"][0]["second_pass"]
    assert validate_manifest(v1_manifest) == []


def test_manifest_v2_unknown_schema_version_fails() -> None:
    """An unrecognized schema_version must produce a validation issue."""
    manifest = _v2_hard_only_manifest()
    manifest["schema_version"] = "rule-loader-manifest/v99"
    issues = validate_manifest(manifest)
    assert any("schema_version" in issue for issue in issues), issues
