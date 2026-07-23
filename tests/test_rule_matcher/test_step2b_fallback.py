"""AC-9: Step 2B fallback path tests.

Verifies that the RULES_INDEX.md grep fallback still functions during the
transition to the deterministic matcher.

Part 1: generate_manifest (existing Step 2B path) returns non-empty for all 5
        AC-9 fixture requests.

Part 2: The deterministic matcher includes rules/000-global-core.md (loaded as
        a required dependency) for requests that match a rule which depends on
        it.  Foundation is always loaded by the agent in Step 1 independently
        of the manifest — this part verifies the matcher's dep-resolution path.

Pass condition: all 5 Step 2B assertions green; deterministic matcher dep test
                passes for Python request.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.progressive_eval.manifest_generator import generate_manifest

_INDEX_PATH = Path(__file__).resolve().parents[2] / "rules" / "RULES_INDEX.md"
_RULES_DIR = Path(__file__).resolve().parents[2] / "rules"

# The 5 AC-9 fixture requests
_FIXTURES = [
    "edit a Python file",
    "write a Snowflake SQL query",
    "deploy a Streamlit app",
    "add error handling",
    "update AGENTS.md",
]


# ---------------------------------------------------------------------------
# Part 1: Step 2B (generate_manifest) returns non-empty rule sets
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _INDEX_PATH.exists(), reason="RULES_INDEX.md not available")
@pytest.mark.parametrize("user_request", _FIXTURES)
def test_step2b_returns_nonempty_ruleset(user_request: str) -> None:
    """Step 2B must return at least one matching rule for each AC-9 fixture."""
    manifest = generate_manifest(_INDEX_PATH, user_request=user_request)
    assert len(manifest.entries) > 0, (
        f"Step 2B returned empty rule set for request: {user_request!r}"
    )


# ---------------------------------------------------------------------------
# Part 2: Deterministic matcher resolves foundation as dep of matched rules
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _RULES_DIR.exists(), reason="rules/ directory not available")
def test_deterministic_matcher_includes_foundation_via_dep() -> None:
    """When the deterministic matcher matches 200-python-core.md, it must
    include 000-global-core.md transitively (via required dep chain).

    Note: the agent always loads foundation separately via Step 1 regardless
    of manifest content.  This test verifies the matcher's dep-resolution path
    correctly discovers it.
    """
    from ai_rules.rule_matcher.dependency import resolve_dependencies
    from ai_rules.rule_matcher.frontmatter import load_rules_db
    from ai_rules.rule_matcher.matcher import FileContext, match_rules

    db = load_rules_db(_RULES_DIR)
    if "200-python-core.md" not in db or "000-global-core.md" not in db:
        pytest.skip("Required rule files not present in rules/")

    scored = match_rules(["python"], FileContext(extensions=[".py"]), list(db.values()))
    resolved, _ = resolve_dependencies(scored, db)
    filenames = [r.filename for r in resolved]

    assert "200-python-core.md" in filenames, "200-python-core.md not matched"
    assert "000-global-core.md" in filenames, (
        "Foundation 000-global-core.md missing from dep-resolved result"
    )
