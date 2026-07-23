"""Core matching algorithm.

Ports ``_score_keyword_match()`` from
``progressive_eval/manifest_generator.py`` to a user-kw-vs-rule-kw
comparison model.  Matching is deterministic: given the same inputs the
function always returns the same output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from fnmatch import fnmatch
from os.path import dirname

from ai_rules.rule_matcher.frontmatter import TIER_ORDER, RuleFrontmatter

# Extension normalization map
_EXT_ALIASES: dict[str, str] = {
    ".yml": ".yaml",
    ".yaml": ".yaml",
}


@dataclass
class FileContext:
    extensions: list[str] = field(default_factory=list)
    paths: list[str] = field(default_factory=list)


@dataclass
class ScoredRule:
    rule: RuleFrontmatter
    score: int
    is_dependency_only: bool = False


def _word_boundary_match(needle: str, haystack: str) -> bool:
    """Check if needle appears as a complete word/phrase in haystack."""
    pattern = r"(?:^|\s)" + re.escape(needle) + r"(?:\s|$)"
    return bool(re.search(pattern, haystack))


def _score_user_kw_against_rule_kw(user_kw: str, rule_kw: str) -> int:
    """Score one user keyword against one rule keyword.

    Returns:
        10 — full dehyphenated phrase match (exact equality or word-boundary substring).
         5 — any 2 consecutive words from each side share a bigram.
         1 — any single word >= 4 chars matches exactly in the other's word list.
         0 — no match.
    """
    u = user_kw.lower().replace("-", " ").replace("_", " ").strip()
    r = rule_kw.lower().replace("-", " ").replace("_", " ").strip()

    # Exact equality
    if u == r:
        return 10

    # Word-boundary substring match — only scores 10 when the shorter string
    # covers a significant portion of the longer string. This prevents
    # single words like "query" from getting score 10 against 3+ word
    # keywords like "query loop aggregation".
    if len(u) >= 3 and len(r) >= 3:
        u_wc = len(u.split())
        r_wc = len(r.split())
        shorter_wc = min(u_wc, r_wc)
        longer_wc = max(u_wc, r_wc)
        # Allow phrase match when: both single-word, or shorter covers ≥50% of longer
        if ((u_wc == 1 and r_wc == 1) or (shorter_wc * 2 >= longer_wc)) and (
            _word_boundary_match(u, r) or _word_boundary_match(r, u)
        ):
            return 10

    r_words = r.split()
    u_words = u.split()

    # Bigram overlap
    if len(r_words) >= 2 and len(u_words) >= 2:
        bigrams_r = {f"{r_words[i]} {r_words[i + 1]}" for i in range(len(r_words) - 1)}
        bigrams_u = {f"{u_words[i]} {u_words[i + 1]}" for i in range(len(u_words) - 1)}
        if bigrams_r & bigrams_u:
            return 5

    # Word-level exact match (>= 3 chars, must be exact word in the other's word list)
    r_word_set = set(r_words)
    for uw in u_words:
        if len(uw) >= 3 and uw in r_word_set:
            return 1

    return 0


def _normalize_ext(ext: str) -> str:
    """Normalize file extension (.yml → .yaml)."""
    return _EXT_ALIASES.get(ext.lower(), ext.lower())


def match_rules(
    keywords: list[str],
    file_context: FileContext,
    rules_db: list[RuleFrontmatter],
    *,
    score_threshold: int = 3,
) -> list[ScoredRule]:
    """Score and rank rules against *keywords* and *file_context*.

    Rules with score < *score_threshold* are excluded.  Results are sorted by:
    1. Score descending (strongest matches first).
    2. Tier priority as tiebreaker (Critical first when scores are equal).
    """
    scored: list[ScoredRule] = []

    for rule in rules_db:
        score = 0

        # Keyword matching: phrase/bigram/word scoring
        for user_kw in keywords:
            for rule_kw in rule.typed_kw:
                score += _score_user_kw_against_rule_kw(user_kw, rule_kw)

        # Extension match (normalized) — strong signal, worth 3 per match
        rule_exts = {_normalize_ext(e) for e in rule.typed_ext}
        for ext in file_context.extensions:
            if _normalize_ext(ext) in rule_exts:
                score += 3

        # File glob match (prepend **/ for nested path support) — strong signal
        for path in file_context.paths:
            for pattern in rule.file_patterns:
                # Match both bare filename and full path
                if fnmatch(path, pattern) or fnmatch(path, f"**/{pattern}"):
                    score += 5

        # Dir glob match (strip trailing slash from pattern for comparison)
        for path in file_context.paths:
            path_dir = dirname(path)
            for pattern in rule.dir_patterns:
                clean_pattern = pattern.rstrip("/")
                if fnmatch(path_dir, clean_pattern) or fnmatch(path_dir, f"**/{clean_pattern}"):
                    score += 3

        if score >= score_threshold:
            scored.append(ScoredRule(rule=rule, score=score))

    # Sort: score descending (primary), tier as tiebreaker (secondary)
    scored.sort(key=lambda s: (-s.score, TIER_ORDER.get(s.rule.context_tier, 99)))
    return scored
