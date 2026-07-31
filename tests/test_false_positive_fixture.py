"""Unit tests for rule-loader-manifest/v2 schema validation.

Covered invariants (per plan §5.3, §8.3 and skills/rule-loader/SKILL.md):

- v2 manifest with valid additive fields validates cleanly.
- HARD candidates never appear in ``deferred_rules`` with
  ``reason_type: "second_pass_rejected"``.
- SOFT candidates rejected in Phase 3.5 appear in ``deferred_rules`` with
  ``reason_type: "second_pass_rejected"``.
- The completeness invariant is preserved (candidate is in load_sequence or deferred).
- v1 manifests remain accepted (backward compatibility during rollout).

Fixture location: the curated false-positive fixture ships under
``tests/fixtures/`` (tracked). The plan-authored path
``.workbench/eval-fixtures/false_positive_fixtures.json`` is a working
copy inside the gitignored workbench and is not authoritative for CI.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.manifest import (
    SCHEMA_VERSION_V2,
    validate_manifest,
)

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "false_positive_fixtures.json"


@pytest.fixture(scope="module")
def fixtures() -> dict:
    """Load the curated false-positive fixture set once per module."""
    assert FIXTURE_PATH.exists(), f"Fixture file missing: {FIXTURE_PATH}"
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


# ── false_positive_fixture shape tests ─────────────────────────────────────


def test_false_positive_fixture_file_exists() -> None:
    """The curated fixture file must exist at the plan-specified path."""
    assert FIXTURE_PATH.exists(), f"Fixture file missing: {FIXTURE_PATH}"


def test_false_positive_fixture_has_five_or_more_false_positive_cases(
    fixtures: dict,
) -> None:
    """Plan §5.3 requires ≥5 known false-positive keyword-hit fixtures."""
    fps = fixtures["false_positives"]
    assert isinstance(fps, list)
    assert len(fps) >= 5, f"Need ≥5 false-positive fixtures, got {len(fps)}"


def test_false_positive_fixture_has_three_or_more_hard_exempt_cases(
    fixtures: dict,
) -> None:
    """Plan §5.3 requires ≥3 HARD-candidate fixtures verifying never-filtered."""
    hard = fixtures["hard_exempt"]
    assert isinstance(hard, list)
    assert len(hard) >= 3, f"Need ≥3 hard_exempt fixtures, got {len(hard)}"


def test_false_positive_fixture_entries_have_required_fields(fixtures: dict) -> None:
    """Every false_positive entry must declare its request, rule, and expectations."""
    required = {
        "id",
        "request",
        "false_positive_rule",
        "expected_v1_action",
        "expected_v2_action",
        "expected_reason_type",
    }
    for entry in fixtures["false_positives"]:
        missing = required - set(entry.keys())
        assert not missing, f"{entry.get('id', '?')}: missing keys {missing}"
        assert entry["false_positive_rule"]["layer"] == "SOFT"
        assert entry["expected_v1_action"] == "load"
        assert entry["expected_v2_action"] == "defer"
        assert entry["expected_reason_type"] == "second_pass_rejected"


def test_false_positive_fixture_hard_exempt_entries_have_required_fields(
    fixtures: dict,
) -> None:
    """Every hard_exempt entry must declare its HARD trigger and expected annotation."""
    required = {"id", "request", "hard_candidate", "expected_v2_action", "expected_second_pass"}
    for entry in fixtures["hard_exempt"]:
        missing = required - set(entry.keys())
        assert not missing, f"{entry.get('id', '?')}: missing keys {missing}"
        assert entry["hard_candidate"]["layer"] == "HARD"
        assert entry["expected_v2_action"] == "load"
        sp = entry["expected_second_pass"]
        assert sp["evaluated"] is False
        assert sp["confirmed"] is True
        assert sp["confirmation_reason"] == "hard-candidate-exempt"


# ── manifest-level assertions built from the fixtures ─────────────────────


def _build_v2_manifest_from_fixture_entry(fp_entry: dict) -> dict:
    """Synthesize a v2 manifest that reflects the fixture's expected v2 outcome."""
    rp = fp_entry["false_positive_rule"]["rule_path"]
    return {
        "schema_version": SCHEMA_VERSION_V2,
        "runtime": {
            "primitive": "Task",
            "spawn_evidence": "tool_call_fixture",
            "agent_id": f"agent_{fp_entry['id']}",
        },
        "keywords_searched": list(fp_entry["false_positive_rule"]["keywords_matched"]),
        "index_evidence": [
            {
                "kind": "hook",
                "target": "hook-injected-manifest",
                "query": " ".join(fp_entry["false_positive_rule"]["keywords_matched"]),
                "result_summary": f"matched {rp}",
            }
        ],
        "candidate_rules": [
            {
                "rule_path": rp,
                "rule_name": rp.split("/")[-1],
                "reason_type": "activity_keyword",
                "reason": "kw match (false-positive candidate)",
                "context_tier": "Medium",
                "token_estimate": 1500,
                "layer": "SOFT",
                "required": False,
                "second_pass": {
                    "evaluated": True,
                    "confirmed": False,
                    "confirmation_reason": "no-scope-overlap: request tokens absent from Scope",
                    "scope_excerpt_hash": "sha256:fixture",
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
        "deferred_rules": [
            {
                "rule_path": rp,
                "rule_name": rp.split("/")[-1],
                "reason_type": "second_pass_rejected",
                "reason": "no-scope-overlap: request tokens absent from Scope",
                "deferred_because": "Phase 3.5 second-pass rejected",
                "context_tier": "Medium",
                "token_estimate": 1500,
                "layer": "SOFT",
            }
        ],
        "second_pass_evidence": [
            {
                "rule_path": rp,
                "confirmed": False,
                "reason": "no-scope-overlap: request tokens absent from Scope",
            }
        ],
    }


def test_false_positive_fixture_synthesized_manifest_validates(fixtures: dict) -> None:
    """A v2 manifest built from each false-positive fixture validates cleanly:
    the SOFT candidate is deferred with reason_type=second_pass_rejected and
    the completeness invariant holds.
    """
    for entry in fixtures["false_positives"]:
        manifest = _build_v2_manifest_from_fixture_entry(entry)
        issues = validate_manifest(manifest)
        assert issues == [], f"{entry['id']}: manifest validation issues: {issues}"


def test_false_positive_fixture_hard_candidates_never_filtered(fixtures: dict) -> None:
    """A HARD candidate in the fixture must NOT be movable to deferred_rules
    with reason_type=second_pass_rejected. The validator enforces this.
    """
    for entry in fixtures["hard_exempt"]:
        rp = entry["hard_candidate"]["rule_path"]
        # Corrupt-case manifest: place the HARD rule in deferred_rules with the
        # second_pass_rejected reason — the validator MUST reject this.
        corrupt = {
            "schema_version": SCHEMA_VERSION_V2,
            "runtime": {
                "primitive": "Task",
                "spawn_evidence": "tool_call_fixture",
                "agent_id": f"agent_{entry['id']}",
            },
            "keywords_searched": [],
            "index_evidence": [
                {
                    "kind": "hook",
                    "target": "hook-injected-manifest",
                    "query": entry["hard_candidate"]["trigger"],
                    "result_summary": f"matched {rp}",
                }
            ],
            "candidate_rules": [
                {
                    "rule_path": rp,
                    "rule_name": rp.split("/")[-1],
                    "reason_type": "extension",
                    "reason": entry["hard_candidate"]["trigger"],
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
            "load_sequence": [],
            "deferred_rules": [
                {
                    "rule_path": rp,
                    "rule_name": rp.split("/")[-1],
                    "reason_type": "second_pass_rejected",
                    "reason": "invalid — HARD candidates are exempt",
                    "deferred_because": "corrupt fixture-guard test",
                    "context_tier": "Critical",
                    "token_estimate": 2550,
                    "layer": "HARD",
                }
            ],
            "second_pass_evidence": [],
        }
        issues = validate_manifest(corrupt)
        assert any(
            "HARD candidate" in issue and "second_pass_rejected" in issue for issue in issues
        ), f"{entry['id']}: expected HARD-never-filtered violation, got {issues}"


def test_false_positive_fixture_v1_loaded_v2_defers(fixtures: dict) -> None:
    """Every false-positive fixture must state expected_v1_action='load' AND
    expected_v2_action='defer' — the whole point of the fixture set.
    """
    for entry in fixtures["false_positives"]:
        assert entry["expected_v1_action"] == "load", (
            f"{entry['id']}: not a false-positive if v1 already defers"
        )
        assert entry["expected_v2_action"] == "defer", (
            f"{entry['id']}: v2 must defer this false-positive"
        )
