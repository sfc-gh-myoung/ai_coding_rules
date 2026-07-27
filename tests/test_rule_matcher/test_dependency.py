"""Unit tests for match_rules.py — dependency resolution."""

from __future__ import annotations

from pathlib import Path

from ai_rules.match_rules import (
    RuleEntry,
    ScoredRule,
    resolve_dependencies,
)


def _rule(
    filename: str,
    depends_required: list[str] | None = None,
    depends_optional: list[str] | None = None,
    tier: str = "Medium",
) -> RuleEntry:
    return RuleEntry(
        filename=filename,
        path=Path(filename),
        context_tier=tier,
        token_budget=500,
        depends_required=depends_required or [],
        depends_optional=depends_optional or [],
        typed_kw=[],
        typed_ext=[],
        file_patterns=[],
        dir_patterns=[],
        rule_version="v1.0",
        description="",
        line_count=10,
        last_updated="2026-01-01",
        schema_version="v3.5",
        keywords_raw=[],
    )


def _scored(rule: RuleEntry, score: int = 10) -> ScoredRule:
    return ScoredRule(rule=rule, score=score)


# ---------------------------------------------------------------------------
# resolve_dependencies
# ---------------------------------------------------------------------------


class TestResolveDependencies:
    def test_direct_match_no_deps(self):
        rule = _rule("200.md")
        db = {"200.md": rule}
        resolved, warnings = resolve_dependencies([_scored(rule)], db)
        assert [r.filename for r in resolved] == ["200.md"]
        assert warnings == []

    def test_transitive_required_dep_included(self):
        foundation = _rule("000-global-core.md")
        domain = _rule("100.md", depends_required=["000-global-core.md"])
        db = {"000-global-core.md": foundation, "100.md": domain}
        resolved, warnings = resolve_dependencies([_scored(domain)], db)
        filenames = [r.filename for r in resolved]
        assert "100.md" in filenames
        assert "000-global-core.md" in filenames
        assert warnings == []

    def test_optional_deps_not_resolved(self):
        dep = _rule("optional.md")
        rule = _rule("100.md", depends_optional=["optional.md"])
        db = {"100.md": rule, "optional.md": dep}
        resolved, warnings = resolve_dependencies([_scored(rule)], db)
        filenames = [r.filename for r in resolved]
        assert "optional.md" not in filenames
        assert warnings == []

    def test_missing_required_dep_produces_warning_not_exception(self):
        rule = _rule("100.md", depends_required=["missing.md"])
        db = {"100.md": rule}
        resolved, warnings = resolve_dependencies([_scored(rule)], db)
        assert len(warnings) == 1
        assert warnings[0]["rule"] == "100.md"
        assert warnings[0]["missing_dep"] == "missing.md"
        assert [r.filename for r in resolved] == ["100.md"]

    def test_missing_dep_does_not_stop_other_deps(self):
        foundation = _rule("000.md")
        rule = _rule("100.md", depends_required=["missing.md", "000.md"])
        db = {"100.md": rule, "000.md": foundation}
        resolved, warnings = resolve_dependencies([_scored(rule)], db)
        filenames = [r.filename for r in resolved]
        assert "000.md" in filenames
        assert len(warnings) == 1

    def test_cycle_detection_no_infinite_loop(self):
        a = _rule("a.md", depends_required=["b.md"])
        b = _rule("b.md", depends_required=["a.md"])
        db = {"a.md": a, "b.md": b}
        resolved, warnings = resolve_dependencies([_scored(a)], db)
        filenames = [r.filename for r in resolved]
        assert "a.md" in filenames
        assert "b.md" in filenames
        assert warnings == []

    def test_absent_depends(self):
        rule = _rule("no-deps.md")
        db = {"no-deps.md": rule}
        resolved, warnings = resolve_dependencies([_scored(rule)], db)
        assert [r.filename for r in resolved] == ["no-deps.md"]
        assert warnings == []

    def test_deduplication(self):
        foundation = _rule("000.md")
        a = _rule("a.md", depends_required=["000.md"])
        b = _rule("b.md", depends_required=["000.md"])
        db = {"000.md": foundation, "a.md": a, "b.md": b}
        resolved, warnings = resolve_dependencies([_scored(a), _scored(b)], db)
        filenames = [r.filename for r in resolved]
        assert filenames.count("000.md") == 1

    def test_comment_stripped_from_dep_names(self):
        foundation = _rule("000.md")
        rule = _rule("100.md", depends_required=["000.md  # foundation"])
        db = {"100.md": rule, "000.md": foundation}
        resolved, warnings = resolve_dependencies([_scored(rule)], db)
        filenames = [r.filename for r in resolved]
        assert "000.md" in filenames
