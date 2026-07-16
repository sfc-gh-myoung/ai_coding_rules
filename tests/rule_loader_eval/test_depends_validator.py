"""Unit tests for depends_validator — validate_depends_propagation and format_violations."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.depends_validator import (
    DependsViolation,
    expand_required_closure,
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


# ---------------------------------------------------------------------------
# expand_required_closure (Phase 2)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_closure_includes_seed_with_no_deps() -> None:
    """Seed with no required deps → closure == seed."""
    meta = {"rules/119.md": _meta("rules/119.md")}
    result = expand_required_closure(("rules/119.md",), meta)
    assert result == ("rules/119.md",)


@pytest.mark.unit
def test_closure_expands_direct_required_deps() -> None:
    """119 requires 100, 103, 105 — all three appear in closure."""
    meta = {
        "rules/119.md": _meta(
            "rules/119.md",
            depends_required=("rules/100.md", "rules/103.md", "rules/105.md"),
        ),
        "rules/100.md": _meta("rules/100.md"),
        "rules/103.md": _meta("rules/103.md"),
        "rules/105.md": _meta("rules/105.md"),
    }
    result = expand_required_closure(("rules/119.md",), meta)
    assert set(result) >= {"rules/119.md", "rules/100.md", "rules/103.md", "rules/105.md"}


@pytest.mark.unit
def test_closure_expands_transitively() -> None:
    """A→B→C: loading A alone should pull in both B and C."""
    meta = {
        "rules/A.md": _meta("rules/A.md", depends_required=("rules/B.md",)),
        "rules/B.md": _meta("rules/B.md", depends_required=("rules/C.md",)),
        "rules/C.md": _meta("rules/C.md"),
    }
    result = expand_required_closure(("rules/A.md",), meta)
    assert set(result) == {"rules/A.md", "rules/B.md", "rules/C.md"}


@pytest.mark.unit
def test_closure_cycle_safe() -> None:
    """A→B→A cycle must not loop forever."""
    meta = {
        "rules/A.md": _meta("rules/A.md", depends_required=("rules/B.md",)),
        "rules/B.md": _meta("rules/B.md", depends_required=("rules/A.md",)),
    }
    result = expand_required_closure(("rules/A.md",), meta)
    assert set(result) == {"rules/A.md", "rules/B.md"}


@pytest.mark.unit
def test_closure_result_is_sorted_tuple() -> None:
    meta = {
        "rules/Z.md": _meta("rules/Z.md", depends_required=("rules/A.md",)),
        "rules/A.md": _meta("rules/A.md"),
    }
    result = expand_required_closure(("rules/Z.md",), meta)
    assert result == tuple(sorted(result))


@pytest.mark.unit
def test_closure_unknown_dep_silently_included_in_closure() -> None:
    """A dep not in rules_meta is added to closure but not further expanded."""
    meta = {
        "rules/X.md": _meta("rules/X.md", depends_required=("rules/unknown.md",)),
    }
    result = expand_required_closure(("rules/X.md",), meta)
    assert "rules/X.md" in result
    assert "rules/unknown.md" in result


@pytest.mark.unit
def test_p1_decoupled_then_p2_no_r8(tmp_path: object) -> None:  # type: ignore[type-arg]
    """Phase 1 + Phase 2 integration test using fixture/engine data shapes.

    Scenario: agent loads 119 but not its required parents 100, 103, 105.
    Phase 1 (decouple): passed=True, depends_ok=False on raw loaded.
    Phase 2 (closure): effective_loaded contains {119,100,103,105}, R8=0, passed=True.
    """
    from ai_rules.rule_loader_eval.depends_validator import validate_depends_propagation

    meta = {
        "rules/119.md": _meta(
            "rules/119.md",
            depends_required=("rules/100.md", "rules/103.md", "rules/105.md"),
        ),
        "rules/100.md": _meta("rules/100.md"),
        "rules/103.md": _meta("rules/103.md"),
        "rules/105.md": _meta("rules/105.md"),
    }

    raw_loaded = ("rules/119.md",)

    # Phase 1: violations exist on raw loaded, but passed is decoupled from them.
    raw_violations = validate_depends_propagation(raw_loaded, meta)
    assert len(raw_violations) == 3, "expected 3 R8 violations on raw loaded"
    # (passed is not checked here — that's engine.py's job; just verify violations exist)

    # Phase 2: closure eliminates violations.
    effective = expand_required_closure(raw_loaded, meta)
    assert set(effective) >= {"rules/119.md", "rules/100.md", "rules/103.md", "rules/105.md"}
    closure_violations = validate_depends_propagation(effective, meta)
    assert closure_violations == [], "expected 0 R8 violations after closure expansion"


@pytest.mark.unit
def test_forbidden_via_closure_not_present_in_raw() -> None:
    """A rule reachable via closure but absent from raw loaded must NOT be treated
    as forbidden-present.  Forbidden detection is on raw loaded only (engine.py
    contract).
    """
    # Simulate: raw loaded = {A}, A requires B; B is forbidden in some fixture.
    # The closure-expanded set would include B, but forbidden scoring on raw
    # loaded would NOT flag B as present.
    meta = {
        "rules/A.md": _meta("rules/A.md", depends_required=("rules/B.md",)),
        "rules/B.md": _meta("rules/B.md"),
    }
    raw_loaded = ("rules/A.md",)
    effective = expand_required_closure(raw_loaded, meta)
    assert "rules/B.md" in effective  # B is in closure

    # But the engine checks forbidden on raw_loaded, not effective.
    # Simulate: forbidden = {B}.  Raw loaded does NOT contain B.
    forbidden = {"rules/B.md"}
    forbidden_in_raw = set(raw_loaded) & forbidden
    assert forbidden_in_raw == set(), "B should NOT appear as forbidden when checking raw loaded"
