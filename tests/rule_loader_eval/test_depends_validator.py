"""Unit tests for depends_validator — validate_depends_propagation and format_violations."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.depends_validator import (
    DependsViolation,
    format_violations,
    validate_depends_propagation,
)
from ai_rules.rule_loader_eval.rules_meta import RuleMetadata


def _meta(path: str, depends_required: tuple[str, ...] = ()) -> RuleMetadata:
    return RuleMetadata(path=Path(path), depends_required=depends_required)


# ---------------------------------------------------------------------------
# validate_depends_propagation
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_validate_empty_loaded_and_meta() -> None:
    assert validate_depends_propagation([], {}) == []


@pytest.mark.unit
def test_validate_no_violations_dep_present() -> None:
    meta = {
        "rules/200-python-core.md": _meta(
            "rules/200-python-core.md",
            depends_required=("rules/000-global-core.md",),
        ),
        "rules/000-global-core.md": _meta("rules/000-global-core.md"),
    }
    result = validate_depends_propagation(
        ["rules/200-python-core.md", "rules/000-global-core.md"], meta
    )
    assert result == []


@pytest.mark.unit
def test_validate_missing_dep_single_violation() -> None:
    meta = {"rules/X.md": _meta("rules/X.md", depends_required=("rules/000-global-core.md",))}
    result = validate_depends_propagation(["rules/X.md"], meta)
    assert len(result) == 1
    assert result[0].parent == "rules/X.md"
    assert result[0].missing_dep == "rules/000-global-core.md"


@pytest.mark.unit
def test_validate_rule_not_in_meta_is_silently_skipped() -> None:
    result = validate_depends_propagation(["rules/unknown.md"], {})
    assert result == []


@pytest.mark.unit
def test_validate_multiple_missing_deps() -> None:
    meta = {"rules/X.md": _meta("rules/X.md", depends_required=("rules/A.md", "rules/B.md"))}
    result = validate_depends_propagation(["rules/X.md"], meta)
    assert len(result) == 2
    missing = {v.missing_dep for v in result}
    assert missing == {"rules/A.md", "rules/B.md"}


@pytest.mark.unit
def test_validate_violations_sorted_by_parent_then_dep() -> None:
    meta = {
        "rules/B.md": _meta("rules/B.md", depends_required=("rules/Z.md",)),
        "rules/A.md": _meta("rules/A.md", depends_required=("rules/Z.md",)),
    }
    result = validate_depends_propagation(["rules/A.md", "rules/B.md"], meta)
    assert result[0].parent == "rules/A.md"
    assert result[1].parent == "rules/B.md"


# ---------------------------------------------------------------------------
# DependsViolation.__str__
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_violation_str_format() -> None:
    v = DependsViolation(parent="rules/X.md", missing_dep="rules/Y.md")
    assert str(v) == "rules/X.md requires rules/Y.md (not loaded)"


# ---------------------------------------------------------------------------
# format_violations
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_format_violations_empty_returns_empty_list() -> None:
    assert format_violations([]) == []


@pytest.mark.unit
def test_format_violations_single_line_has_r8_prefix() -> None:
    v = DependsViolation(parent="rules/X.md", missing_dep="rules/Y.md")
    lines = format_violations([v])
    assert len(lines) == 1
    assert "R8 violation" in lines[0]
    assert "rules/X.md" in lines[0]
    assert "rules/Y.md" in lines[0]


@pytest.mark.unit
def test_format_violations_one_line_per_violation() -> None:
    violations = [
        DependsViolation(parent="rules/A.md", missing_dep="rules/Z.md"),
        DependsViolation(parent="rules/B.md", missing_dep="rules/Z.md"),
    ]
    lines = format_violations(violations)
    assert len(lines) == 2
    assert all("R8 violation" in line for line in lines)
