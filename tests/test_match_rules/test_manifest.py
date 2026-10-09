"""Unit tests for match_rules.py: build_manifest, token budget, schema."""

from __future__ import annotations

from pathlib import Path

from ai_rules.match_rules import RuleEntry, build_manifest


def _rule(
    filename: str,
    tier: str = "High",
    budget: int = 1000,
    depends_required: list[str] | None = None,
) -> RuleEntry:
    return RuleEntry(
        filename=filename,
        path=Path(filename),
        context_tier=tier,
        token_budget=budget,
        depends_required=depends_required or [],
        depends_optional=[],
        typed_kw=[],
        typed_ext=[],
        file_patterns=[],
        dir_patterns=[],
        rule_version="v1.0",
        description="A test rule.",
        line_count=10,
        last_updated="2026-01-01",
        schema_version="v3.5",
        keywords_raw=[],
    )


# ---------------------------------------------------------------------------
# build_manifest: basic
# ---------------------------------------------------------------------------


class TestBuildManifest:
    def test_schema_version(self):
        manifest = build_manifest([], [])
        assert manifest["schema_version"] == "rule-loader-matcher/v1"

    def test_empty_resolved_produces_empty_manifest(self):
        manifest = build_manifest([], [])
        assert manifest["load_sequence"] == []
        assert manifest["warnings"] == []

    def test_single_rule_in_load_sequence(self):
        rule = _rule("200.md")
        manifest = build_manifest([rule], [], matched_filenames={"200.md"})
        assert len(manifest["load_sequence"]) == 1
        assert manifest["load_sequence"][0]["rule_path"] == "rules/200.md"

    def test_max_entries_cap_on_direct_matches(self):
        rules = [_rule(f"{i}.md", budget=100) for i in range(5)]
        matched = {r.filename for r in rules}
        manifest = build_manifest(rules, [], matched_filenames=matched, max_entries=3)
        assert len(manifest["load_sequence"]) == 3
        assert len(manifest["deferred_rules"]) == 2
        for d in manifest["deferred_rules"]:
            assert d["reason"] == "entry_cap"

    def test_dependency_only_rules_not_capped(self):
        """Dep-only rules don't count against max_entries."""
        direct = [_rule(f"d{i}.md", budget=100) for i in range(3)]
        dep = _rule("000.md", budget=100)
        all_rules = [*direct, dep]
        matched = {r.filename for r in direct}
        manifest = build_manifest(all_rules, [], matched_filenames=matched, max_entries=3)
        rule_paths = [r["rule_path"] for r in manifest["load_sequence"]]
        assert "rules/000.md" in rule_paths
        # All 3 direct + 1 dep are in load_sequence (dep does not consume the cap)
        assert len(manifest["load_sequence"]) == 4

    def test_token_budget_enforcement(self):
        """When token estimate exceeds max_tokens, entries are popped."""
        rules = [_rule(f"{i}.md", budget=8000) for i in range(3)]
        matched = {r.filename for r in rules}
        manifest = build_manifest(rules, [], matched_filenames=matched, max_tokens=10_000)
        total = sum(r.get("token_budget", 0) for r in manifest["load_sequence"])
        assert total <= 10_000
        assert len(manifest["deferred_rules"]) >= 1

    def test_token_budget_while_loop_terminates(self):
        """Even with absurdly small budget, at least 1 rule stays."""
        rules = [_rule("big.md", budget=50_000)]
        matched = {"big.md"}
        manifest = build_manifest(rules, [], matched_filenames=matched, max_tokens=1)
        assert len(manifest["load_sequence"]) == 1

    def test_warnings_propagated(self):
        w = [{"rule": "100.md", "missing_dep": "999.md"}]
        manifest = build_manifest([], w)
        assert manifest["warnings"] == w

    def test_deferred_rules_populated_on_token_budget(self):
        rules = [_rule("a.md", budget=6000), _rule("b.md", budget=6000)]
        matched = {"a.md", "b.md"}
        manifest = build_manifest(rules, [], matched_filenames=matched, max_tokens=8000)
        reasons = [d["reason"] for d in manifest["deferred_rules"]]
        assert "token_budget" in reasons


# ---------------------------------------------------------------------------
# dict output schema
# ---------------------------------------------------------------------------


class TestManifestDict:
    def test_required_keys_present(self):
        manifest = build_manifest([], [])
        for key in (
            "schema_version",
            "load_sequence",
            "deferred_rules",
            "candidate_rules",
            "warnings",
        ):
            assert key in manifest

    def test_rule_dict_has_expected_fields(self):
        rule = _rule("200.md")
        manifest = build_manifest([rule], [], matched_filenames={"200.md"})
        entry = manifest["load_sequence"][0]
        assert entry["rule_path"] == "rules/200.md"
        assert entry["context_tier"] == "High"
        assert entry["description"] == "A test rule."
        assert "layer" in entry

    def test_dependency_only_flag_emitted(self):
        direct = _rule("100.md", budget=100)
        dep = _rule("000.md", budget=100)
        manifest = build_manifest([direct, dep], [], matched_filenames={"100.md"})
        dep_entry = next(e for e in manifest["load_sequence"] if e["rule_path"] == "rules/000.md")
        assert dep_entry.get("layer") == "SOFT"  # default when no foundation passed


# ---------------------------------------------------------------------------
# build_manifest: dependency-first ordering
# ---------------------------------------------------------------------------


class TestDependencyOrdering:
    def test_chain_emits_dependencies_before_dependents(self):
        """206 -> 200 -> 000: exact order, deps ahead of the match that needs them."""
        foundation = _rule("000-global-core.md")
        core = _rule("200.md", depends_required=["000-global-core.md"])
        leaf = _rule("206.md", depends_required=["200.md"])
        manifest = build_manifest(
            [leaf, core, foundation],
            [],
            matched_filenames={"206.md"},
            foundation=foundation,
        )
        paths = [e["rule_path"] for e in manifest["load_sequence"]]
        assert paths == ["rules/000-global-core.md", "rules/200.md", "rules/206.md"]

    def test_diamond_shared_dependency_emitted_once_before_both(self):
        """Two direct matches share a dependency: it appears once, before both."""
        shared = _rule("100.md")
        d1 = _rule("101.md", depends_required=["100.md"])
        d2 = _rule("102.md", depends_required=["100.md"])
        manifest = build_manifest(
            [d1, d2, shared],
            [],
            matched_filenames={"101.md", "102.md"},
        )
        paths = [e["rule_path"] for e in manifest["load_sequence"]]
        assert paths.count("rules/100.md") == 1
        shared_idx = paths.index("rules/100.md")
        assert shared_idx < paths.index("rules/101.md")
        assert shared_idx < paths.index("rules/102.md")

    def test_cycle_terminates_each_rule_once(self):
        """A depends on B and B on A: ordering terminates; each rule once."""
        a = _rule("a.md", depends_required=["b.md"])
        b = _rule("b.md", depends_required=["a.md"])
        manifest = build_manifest([a, b], [], matched_filenames={"a.md", "b.md"})
        paths = [e["rule_path"] for e in manifest["load_sequence"]]
        assert sorted(paths) == ["rules/a.md", "rules/b.md"]
        assert len(paths) == 2
