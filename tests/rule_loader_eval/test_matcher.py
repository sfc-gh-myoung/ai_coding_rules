"""Tests for the matcher (required + dependencies + forbidden)."""

from __future__ import annotations

import logging

import pytest

from ai_rules.rule_loader_eval.matcher import match_loaded_rules
from ai_rules.rule_loader_eval.rules_meta import RuleMetadata


def _meta(path: str, required_deps: tuple[str, ...] = ()) -> RuleMetadata:
    """Build a minimal RuleMetadata for testing."""
    from pathlib import Path

    return RuleMetadata(path=Path(path), depends_required=required_deps)


@pytest.mark.unit
def test_required_only_passes() -> None:
    """All required rules loaded; no deps; passes."""
    res = match_loaded_rules(
        loaded=("rules/999-test-core.md", "rules/100-snowflake-core.md"),
        required=("rules/999-test-core.md", "rules/100-snowflake-core.md"),
    )
    assert res.passed is True
    assert res.missing_required == ()
    assert res.missing_dependencies == ()


@pytest.mark.unit
def test_missing_required_partitioned() -> None:
    """Missing direct match shows up in missing_required."""
    res = match_loaded_rules(
        loaded=("rules/999-test-core.md",),
        required=("rules/999-test-core.md", "rules/100-snowflake-core.md"),
    )
    assert res.passed is False
    assert res.missing_required == ("rules/100-snowflake-core.md",)
    assert res.missing_dependencies == ()


@pytest.mark.unit
def test_missing_dependency_partitioned() -> None:
    """Missing dependency shows up in missing_dependencies (separate from required)."""
    res = match_loaded_rules(
        loaded=("rules/999-test-core.md", "rules/101-snowflake-streamlit-core.md"),
        required=("rules/999-test-core.md", "rules/101-snowflake-streamlit-core.md"),
        dependencies=("rules/100-snowflake-core.md",),
    )
    assert res.passed is False
    assert res.missing_required == ()
    assert res.missing_dependencies == ("rules/100-snowflake-core.md",)


@pytest.mark.unit
def test_required_and_dependency_loaded_passes() -> None:
    """Required + dependency both loaded; passes."""
    res = match_loaded_rules(
        loaded=(
            "rules/999-test-core.md",
            "rules/100-snowflake-core.md",
            "rules/101-snowflake-streamlit-core.md",
        ),
        required=("rules/999-test-core.md", "rules/101-snowflake-streamlit-core.md"),
        dependencies=("rules/100-snowflake-core.md",),
    )
    assert res.passed is True


@pytest.mark.unit
def test_forbidden_warn_only_default() -> None:
    """v3.15: Forbidden rules in the fixture's forbidden list now always fail.

    Pre-v3.15 the strict_forbidden flag gated this; in v3.15 the flag is a no-op
    because forbidden lists are explicit fixture authoring intent (a fixture only
    declares a rule forbidden when its presence indicates a rule-loading bug).
    """
    res = match_loaded_rules(
        loaded=("rules/999-test-core.md", "rules/100-python-x.md"),
        required=("rules/999-test-core.md",),
        forbidden=("rules/100-python-x.md",),
    )
    assert res.passed is False  # v3.15: forbidden always fails
    assert res.forbidden_present == ("rules/100-python-x.md",)
    assert any("forbidden" in w for w in res.warnings)


@pytest.mark.unit
def test_forbidden_strict_fails() -> None:
    """Forbidden rule loaded fails when strict_forbidden=True."""
    res = match_loaded_rules(
        loaded=("rules/999-test-core.md", "rules/100-python-x.md"),
        required=("rules/999-test-core.md",),
        forbidden=("rules/100-python-x.md",),
        strict_forbidden=True,
    )
    assert res.passed is False


@pytest.mark.unit
def test_optional_does_not_fail() -> None:
    """Optional rule omitted from loaded set does not fail."""
    res = match_loaded_rules(
        loaded=("rules/999-test-core.md",),
        required=("rules/999-test-core.md",),
        optional=("rules/100-snowflake-core.md",),
    )
    assert res.passed is True


# ---------------------------------------------------------------------------
# Option A: rules_meta dep-closure subtraction (Steps 0.2 + 1.5)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_option_a_transitive_dep_excluded_from_extras() -> None:
    """Transitive dep of a required rule is NOT counted as FM-6 extra."""
    # 102 requires 100; 100 is not in fixture required/deps/optional/forbidden
    rules_meta = {
        "rules/102-snowflake-sql-core.md": _meta(
            "rules/102-snowflake-sql-core.md",
            required_deps=("rules/100-snowflake-core.md",),
        ),
        "rules/100-snowflake-core.md": _meta("rules/100-snowflake-core.md"),
    }
    res = match_loaded_rules(
        loaded=("rules/102-snowflake-sql-core.md", "rules/100-snowflake-core.md"),
        required=("rules/102-snowflake-sql-core.md",),
        rules_meta=rules_meta,
    )
    assert res.passed is True
    # 100 is a transitive dep of required 102 → must NOT appear in extras
    assert "rules/100-snowflake-core.md" not in res.extras


@pytest.mark.unit
def test_option_a_non_dep_still_in_extras() -> None:
    """A loaded rule that is NOT a transitive dep still appears in extras."""
    rules_meta = {
        "rules/102-snowflake-sql-core.md": _meta(
            "rules/102-snowflake-sql-core.md",
            required_deps=("rules/100-snowflake-core.md",),
        ),
        "rules/100-snowflake-core.md": _meta("rules/100-snowflake-core.md"),
        "rules/200-python-core.md": _meta("rules/200-python-core.md"),
    }
    res = match_loaded_rules(
        loaded=(
            "rules/102-snowflake-sql-core.md",
            "rules/100-snowflake-core.md",
            "rules/200-python-core.md",  # unrelated — should stay in extras
        ),
        required=("rules/102-snowflake-sql-core.md",),
        rules_meta=rules_meta,
    )
    assert "rules/200-python-core.md" in res.extras
    assert "rules/100-snowflake-core.md" not in res.extras


@pytest.mark.unit
def test_option_a_backward_compat_rules_meta_none() -> None:
    """rules_meta=None (default) leaves extras unchanged — backward compat."""
    res_no_meta = match_loaded_rules(
        loaded=("rules/A.md", "rules/B.md"),
        required=("rules/A.md",),
        rules_meta=None,
    )
    assert "rules/B.md" in res_no_meta.extras


@pytest.mark.unit
def test_option_a_missing_dep_target_skip_and_log(caplog: pytest.LogCaptureFixture) -> None:
    """Dep target absent from rules_meta → skip-and-log, no exception, rest of closure computed.

    Covers the preflight anomaly found in Phase 0: rules/002i-rule-loadtrigger.md
    has a dep target that doesn't exist in rules_meta.
    """
    rules_meta = {
        "rules/parent.md": _meta(
            "rules/parent.md",
            required_deps=("rules/MISSING.md", "rules/real-dep.md"),
        ),
        "rules/real-dep.md": _meta("rules/real-dep.md"),
        # rules/MISSING.md is deliberately absent
    }
    with caplog.at_level(logging.WARNING, logger="ai_rules.rule_loader_eval.matcher"):
        res = match_loaded_rules(
            loaded=("rules/parent.md", "rules/real-dep.md"),
            required=("rules/parent.md",),
            rules_meta=rules_meta,
        )
    # No exception raised; real-dep excluded from extras; warning emitted
    assert "rules/real-dep.md" not in res.extras
    assert any("MISSING" in w for w in res.warnings)
    assert any("MISSING" in r.message for r in caplog.records)


@pytest.mark.unit
def test_option_a_self_referential_dep_no_infinite_loop() -> None:
    """Self-referential dep (rule A requires rule A) terminates without loop."""
    rules_meta = {
        "rules/self-ref.md": _meta(
            "rules/self-ref.md",
            required_deps=("rules/self-ref.md",),
        ),
    }
    # Must not raise RecursionError or hang
    res = match_loaded_rules(
        loaded=("rules/self-ref.md",),
        required=("rules/self-ref.md",),
        rules_meta=rules_meta,
    )
    assert res.passed is True
    assert "rules/self-ref.md" not in res.extras


@pytest.mark.unit
def test_option_a_circular_dep_no_infinite_loop() -> None:
    """Circular dep chain (A → B → A) is handled by fixpoint — no infinite loop."""
    rules_meta = {
        "rules/A.md": _meta("rules/A.md", required_deps=("rules/B.md",)),
        "rules/B.md": _meta("rules/B.md", required_deps=("rules/A.md",)),
    }
    res = match_loaded_rules(
        loaded=("rules/A.md", "rules/B.md"),
        required=("rules/A.md",),
        rules_meta=rules_meta,
    )
    # Both are in the closure; neither should appear in extras
    assert "rules/A.md" not in res.extras
    assert "rules/B.md" not in res.extras
