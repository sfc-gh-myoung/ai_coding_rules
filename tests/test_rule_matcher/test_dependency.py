"""Unit tests for dependency.py — dep graph resolution."""

from __future__ import annotations

from pathlib import Path

from ai_rules.rule_matcher.dependency import (
    _strip_yaml_comment,
    get_required_deps,
    resolve_dependencies,
)
from ai_rules.rule_matcher.frontmatter import RuleFrontmatter
from ai_rules.rule_matcher.matcher import ScoredRule


def _rule(
    filename: str,
    depends: dict | None = None,
    tier: str = "Medium",
) -> RuleFrontmatter:
    return RuleFrontmatter(
        filename=filename,
        path=Path(filename),
        context_tier=tier,
        token_budget=500,
        depends=depends,
        typed_kw=[],
        typed_ext=[],
        file_patterns=[],
        dir_patterns=[],
        rule_version="v1.0",
        description="",
    )


def _scored(rule: RuleFrontmatter, score: int = 10) -> ScoredRule:
    return ScoredRule(rule=rule, score=score)


# ---------------------------------------------------------------------------
# _strip_yaml_comment
# ---------------------------------------------------------------------------


class TestStripYamlComment:
    def test_strips_inline_comment(self):
        assert _strip_yaml_comment("100-core.md  # justification") == "100-core.md"

    def test_no_comment(self):
        assert _strip_yaml_comment("000-global-core.md") == "000-global-core.md"

    def test_strips_trailing_whitespace(self):
        assert _strip_yaml_comment("100-core.md  ") == "100-core.md"

    def test_empty_string(self):
        assert _strip_yaml_comment("") == ""


# ---------------------------------------------------------------------------
# get_required_deps
# ---------------------------------------------------------------------------


class TestGetRequiredDeps:
    def test_returns_required_list(self):
        rule = _rule(
            "foo.md", depends={"required": ["000-global-core.md  # foundation"], "optional": []}
        )
        deps = get_required_deps(rule)
        assert deps == ["000-global-core.md"]

    def test_absent_depends_returns_empty(self):
        rule = _rule("foo.md", depends=None)
        assert get_required_deps(rule) == []

    def test_no_required_key(self):
        rule = _rule("foo.md", depends={"optional": ["001.md"]})
        assert get_required_deps(rule) == []

    def test_comment_stripped_from_entries(self):
        rule = _rule("foo.md", depends={"required": ["100-core.md  # reason"]})
        deps = get_required_deps(rule)
        assert deps == ["100-core.md"]


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
        domain = _rule("100.md", depends={"required": ["000-global-core.md"], "optional": []})
        db = {"000-global-core.md": foundation, "100.md": domain}
        resolved, warnings = resolve_dependencies([_scored(domain)], db)
        filenames = [r.filename for r in resolved]
        assert "100.md" in filenames
        assert "000-global-core.md" in filenames
        assert warnings == []

    def test_optional_deps_not_resolved(self):
        dep = _rule("optional.md")
        rule = _rule("100.md", depends={"required": [], "optional": ["optional.md"]})
        db = {"100.md": rule, "optional.md": dep}
        resolved, warnings = resolve_dependencies([_scored(rule)], db)
        filenames = [r.filename for r in resolved]
        assert "optional.md" not in filenames
        assert warnings == []

    def test_missing_required_dep_produces_warning_not_exception(self):
        rule = _rule("100.md", depends={"required": ["missing.md"], "optional": []})
        db = {"100.md": rule}
        resolved, warnings = resolve_dependencies([_scored(rule)], db)
        assert len(warnings) == 1
        assert warnings[0]["rule"] == "100.md"
        assert warnings[0]["missing_dep"] == "missing.md"
        assert [r.filename for r in resolved] == ["100.md"]

    def test_missing_dep_does_not_stop_other_deps(self):
        foundation = _rule("000.md")
        rule = _rule(
            "100.md",
            depends={"required": ["missing.md", "000.md"], "optional": []},
        )
        db = {"100.md": rule, "000.md": foundation}
        resolved, warnings = resolve_dependencies([_scored(rule)], db)
        filenames = [r.filename for r in resolved]
        assert "000.md" in filenames
        assert len(warnings) == 1

    def test_cycle_detection_no_infinite_loop(self):
        a = _rule("a.md", depends={"required": ["b.md"], "optional": []})
        b = _rule("b.md", depends={"required": ["a.md"], "optional": []})
        db = {"a.md": a, "b.md": b}
        resolved, warnings = resolve_dependencies([_scored(a)], db)
        filenames = [r.filename for r in resolved]
        assert "a.md" in filenames
        assert "b.md" in filenames
        assert warnings == []

    def test_absent_depends_key(self):
        rule = _rule("no-deps.md", depends=None)
        db = {"no-deps.md": rule}
        resolved, warnings = resolve_dependencies([_scored(rule)], db)
        assert [r.filename for r in resolved] == ["no-deps.md"]
        assert warnings == []

    def test_deduplication(self):
        foundation = _rule("000.md")
        a = _rule("a.md", depends={"required": ["000.md"], "optional": []})
        b = _rule("b.md", depends={"required": ["000.md"], "optional": []})
        db = {"000.md": foundation, "a.md": a, "b.md": b}
        resolved, warnings = resolve_dependencies([_scored(a), _scored(b)], db)
        # 000.md should appear only once
        filenames = [r.filename for r in resolved]
        assert filenames.count("000.md") == 1
