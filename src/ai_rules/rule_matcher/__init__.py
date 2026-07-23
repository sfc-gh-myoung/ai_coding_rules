"""Deterministic rule matcher — Python-based rule discovery replacing grep-on-RULES_INDEX.md.

Reads YAML frontmatter directly from rules/*.md, scores against user keywords
using phrase/bigram/word matching, resolves dependency graph, and returns a
structured ``rule-loader-manifest/v2`` manifest.
"""

from ai_rules.rule_matcher.dependency import resolve_dependencies
from ai_rules.rule_matcher.frontmatter import (
    RuleFrontmatter,
    TypedKeywords,
    load_rules_db,
    parse_rule_file,
    parse_typed_keywords,
)
from ai_rules.rule_matcher.manifest import RuleLoaderManifest, build_manifest
from ai_rules.rule_matcher.matcher import FileContext, ScoredRule, match_rules

__all__ = [
    "FileContext",
    "RuleFrontmatter",
    "RuleLoaderManifest",
    "ScoredRule",
    "TypedKeywords",
    "build_manifest",
    "load_rules_db",
    "match_rules",
    "parse_rule_file",
    "parse_typed_keywords",
    "resolve_dependencies",
]
