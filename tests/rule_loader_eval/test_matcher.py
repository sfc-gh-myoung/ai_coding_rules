"""Tests for the matcher (required + dependencies + forbidden)."""

from __future__ import annotations

import pytest

from ai_rules.rule_loader_eval.matcher import match_loaded_rules


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
