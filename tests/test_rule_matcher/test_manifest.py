"""Unit tests for manifest.py — build_manifest, token budget, schema."""

from __future__ import annotations

from pathlib import Path

from ai_rules.rule_matcher.frontmatter import RuleFrontmatter
from ai_rules.rule_matcher.manifest import (
    build_manifest,
)


def _rule(filename: str, tier: str = "High", budget: int = 1000) -> RuleFrontmatter:
    return RuleFrontmatter(
        filename=filename,
        path=Path(filename),
        context_tier=tier,
        token_budget=budget,
        depends=None,
        typed_kw=[],
        typed_ext=[],
        file_patterns=[],
        dir_patterns=[],
        rule_version="v1.0",
        description="A test rule.",
    )


# ---------------------------------------------------------------------------
# build_manifest — basic
# ---------------------------------------------------------------------------


class TestBuildManifest:
    def test_schema_version(self):
        manifest = build_manifest([], [])
        assert manifest.schema == "rule-loader-manifest/v2"

    def test_empty_resolved_produces_empty_manifest(self):
        manifest = build_manifest([], [])
        assert manifest.load_sequence == []
        assert manifest.warnings == []

    def test_single_rule_in_load_sequence(self):
        rule = _rule("200.md")
        manifest = build_manifest([rule], [], matched_filenames={"200.md"})
        assert len(manifest.load_sequence) == 1
        assert manifest.load_sequence[0].filename == "200.md"

    def test_max_entries_cap_on_direct_matches(self):
        rules = [_rule(f"{i}.md", budget=100) for i in range(5)]
        matched = {r.filename for r in rules}
        manifest = build_manifest(rules, [], matched_filenames=matched, max_entries=3)
        assert len(manifest.load_sequence) == 3
        assert len(manifest.deferred_rules) == 2
        for d in manifest.deferred_rules:
            assert d.reason == "entry_cap"

    def test_dependency_only_rules_not_capped(self):
        """Dep-only rules don't count against max_entries."""
        direct = [_rule(f"d{i}.md", budget=100) for i in range(3)]
        dep = _rule("000.md", budget=100)
        all_rules = [*direct, dep]
        matched = {r.filename for r in direct}
        manifest = build_manifest(all_rules, [], matched_filenames=matched, max_entries=3)
        filenames = [r.filename for r in manifest.load_sequence]
        assert "000.md" in filenames
        assert len([r for r in manifest.load_sequence if not r.is_dependency_only]) == 3

    def test_token_budget_enforcement(self):
        """When token estimate exceeds max_tokens, entries are popped."""
        rules = [_rule(f"{i}.md", budget=8000) for i in range(3)]
        matched = {r.filename for r in rules}
        manifest = build_manifest(rules, [], matched_filenames=matched, max_tokens=10_000)
        total = sum(r.token_budget or 0 for r in manifest.load_sequence)
        assert total <= 10_000
        assert len(manifest.deferred_rules) >= 1

    def test_token_budget_while_loop_terminates(self):
        """Even with absurdly small budget, at least 1 rule stays (no empty loop)."""
        rules = [_rule("big.md", budget=50_000)]
        matched = {"big.md"}
        manifest = build_manifest(rules, [], matched_filenames=matched, max_tokens=1)
        # Only 1 rule, can't pop to empty — stays
        assert len(manifest.load_sequence) == 1

    def test_warnings_propagated(self):
        w = [{"rule": "100.md", "missing_dep": "999.md"}]
        manifest = build_manifest([], w)
        assert manifest.warnings == w

    def test_deferred_rules_populated_on_token_budget(self):
        rules = [_rule("a.md", budget=6000), _rule("b.md", budget=6000)]
        matched = {"a.md", "b.md"}
        manifest = build_manifest(rules, [], matched_filenames=matched, max_tokens=8000)
        reasons = [d.reason for d in manifest.deferred_rules]
        assert "token_budget" in reasons


# ---------------------------------------------------------------------------
# to_dict output schema
# ---------------------------------------------------------------------------


class TestManifestToDict:
    def test_schema_key_present(self):
        manifest = build_manifest([], [])
        d = manifest.to_dict()
        assert d["schema_version"] == "rule-loader-manifest/v2"

    def test_required_keys_present(self):
        manifest = build_manifest([], [])
        d = manifest.to_dict()
        for key in (
            "schema_version",
            "load_sequence",
            "deferred_rules",
            "candidate_rules",
            "warnings",
        ):
            assert key in d

    def test_rule_dict_has_expected_fields(self):
        rule = _rule("200.md")
        manifest = build_manifest([rule], [], matched_filenames={"200.md"})
        entry = manifest.to_dict()["load_sequence"][0]
        assert entry["filename"] == "200.md"
        assert entry["rule_path"] == "rules/200.md"
        assert entry["context_tier"] == "High"
        assert entry["rule_version"] == "v1.0"
        assert entry["description"] == "A test rule."

    def test_dependency_only_flag_emitted(self):
        direct = _rule("100.md", budget=100)
        dep = _rule("000.md", budget=100)
        manifest = build_manifest([direct, dep], [], matched_filenames={"100.md"})
        dep_entry = next(
            e for e in manifest.to_dict()["load_sequence"] if e["filename"] == "000.md"
        )
        assert dep_entry.get("is_dependency_only") is True
