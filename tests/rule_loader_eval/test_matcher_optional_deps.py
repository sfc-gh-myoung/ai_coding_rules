"""Tests for matcher.MatchResult ``unloaded_optional`` reporting."""

from __future__ import annotations

from ai_rules.rule_loader_eval.matcher import match_loaded_rules


def test_unloaded_optional_listed() -> None:
    result = match_loaded_rules(
        loaded=("rules/999-test-core.md", "rules/119-snowflake-warehouse-management.md"),
        required=("rules/999-test-core.md",),
        dependencies=(),
        optional=(
            "rules/103-snowflake-performance-tuning.md",
            "rules/105-snowflake-cost-governance.md",
            "rules/119-snowflake-warehouse-management.md",
        ),
    )
    assert result.passed is True
    assert "rules/119-snowflake-warehouse-management.md" in result.optional_loaded
    assert sorted(result.unloaded_optional) == [
        "rules/103-snowflake-performance-tuning.md",
        "rules/105-snowflake-cost-governance.md",
    ]


def test_optional_does_not_drive_failure() -> None:
    result = match_loaded_rules(
        loaded=("rules/999-test-core.md",),
        required=("rules/999-test-core.md",),
        dependencies=(),
        optional=("rules/103-snowflake-performance-tuning.md",),
    )
    assert result.passed is True
    assert result.unloaded_optional == ("rules/103-snowflake-performance-tuning.md",)


def test_required_dependency_still_drives_failure() -> None:
    result = match_loaded_rules(
        loaded=("rules/999-test-core.md",),
        required=("rules/999-test-core.md",),
        dependencies=("rules/100-snowflake-core.md",),
    )
    assert result.passed is False
    assert result.missing_dependencies == ("rules/100-snowflake-core.md",)
