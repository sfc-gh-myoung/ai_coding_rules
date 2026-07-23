"""AC-13: Empty-manifest fallback test.

Asserts that when the new matcher returns an empty manifest
(``load_sequence: []``), the agent's Step 2B fallback path (generate_manifest
via RULES_INDEX.md) still produces a non-empty rule set for a known fixture.

This verifies that Step 2B remains functional as a fallback when the Python
script is unavailable or returns an error manifest.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_INDEX_PATH = Path(__file__).resolve().parents[2] / "rules" / "RULES_INDEX.md"

# Empty manifest the skill returns when script is unavailable
_EMPTY_MANIFEST = {
    "schema_version": "rule-loader-manifest/v2",
    "error": "matcher_unavailable",
    "load_sequence": [],
    "deferred_rules": [],
    "candidate_rules": [],
    "warnings": [],
}


def _is_empty_manifest(manifest_json: str) -> bool:
    """Return True when the manifest is the skill's empty-fallback form."""
    try:
        data = json.loads(manifest_json)
    except json.JSONDecodeError:
        return False
    return data.get("error") == "matcher_unavailable" and data.get("load_sequence") == []


def _step2b_fallback(user_request: str) -> list[str]:
    """Invoke the Step 2B path (RULES_INDEX.md) and return matched rule paths."""
    from ai_rules.progressive_eval.manifest_generator import generate_manifest

    manifest = generate_manifest(_INDEX_PATH, user_request=user_request)
    return [e.rule_path for e in manifest.entries]


@pytest.mark.skipif(not _INDEX_PATH.exists(), reason="RULES_INDEX.md not available")
def test_empty_manifest_triggers_step2b_fallback() -> None:
    """When the skill returns an empty manifest (matcher_unavailable), the agent
    falls through to Step 2B.  Step 2B must return a non-empty rule set for the
    known fixture 'edit a Python file'.
    """
    # Simulate: skill returned the empty-fallback manifest
    empty_json = json.dumps(_EMPTY_MANIFEST)
    assert _is_empty_manifest(empty_json), "Helper function broken"

    # Step 2B fallback produces results for the known fixture
    rule_paths = _step2b_fallback("edit a Python file")
    assert len(rule_paths) > 0, "Step 2B fallback returned empty rule set for 'edit a Python file'"


@pytest.mark.skipif(not _INDEX_PATH.exists(), reason="RULES_INDEX.md not available")
def test_step2b_fallback_produces_python_rule() -> None:
    """Step 2B fallback for 'edit a Python file' must include 200-python-core.md."""
    rule_paths = _step2b_fallback("edit a Python file")
    assert "rules/200-python-core.md" in rule_paths, (
        f"200-python-core.md missing from Step 2B fallback. Got: {sorted(rule_paths)}"
    )
