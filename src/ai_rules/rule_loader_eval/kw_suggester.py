"""Fixture-aware kw: keyword suggestion for rule-loading improvement.

Given a fixture and its comparison outcome (missing-required / spurious loads),
this module proposes concrete ``kw:`` edits to rule files' ``Keywords:``
metadata to fix the gap.

Algorithm (heuristic — no LLM required):

For **missing-required** rules:
  1. Extract candidate n-grams (1..3 words) from the fixture prompt.
  2. Score by IDF across the existing ``typed_kw`` corpus — rare across rules
     means high signal.
  3. Filter out candidates already present in *any* rule's ``typed_kw``.
  4. Return top-K ranked candidates for the target rule.

For **spurious** rules:
  1. Find which ``typed_kw`` entries of the rule matched the prompt.
  2. Propose narrower variants (extend the phrase by one more token from
     the prompt context).

Usage::

    from ai_rules.rule_loader_eval.kw_suggester import suggest_for_fixture

    proposals = suggest_for_fixture(
        fixture_prompt="Deploy a Snowflake Native App using snow app deploy",
        missing_required=["rules/109b-snowflake-app-deployment-core.md"],
        spurious_loaded=["rules/102a-snowflake-sql-automation.md"],
        rules_meta=load_rules_metadata(Path("rules")),
    )
    for p in proposals:
        print(p.rule_path, p.kind, p.candidates)
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_rules.rule_loader_eval.rules_meta import RuleMetadata

_STOP_WORDS: frozenset[str] = frozenset(
    [
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "as",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "that",
        "this",
        "these",
        "those",
        "it",
        "its",
        "i",
        "you",
        "we",
        "they",
        "he",
        "she",
        "what",
        "which",
        "who",
        "how",
        "when",
        "where",
        "why",
        "not",
        "no",
        "nor",
        "so",
        "yet",
        "both",
        "either",
        "neither",
        "just",
        "very",
        "also",
        "only",
        "even",
        "if",
        "then",
        "than",
        "though",
        "although",
        "while",
        "because",
        "since",
        "after",
        "before",
        "until",
        "unless",
        "s",
        "t",
        "re",
        "ve",
        "ll",
        "d",
    ]
)

_TOKEN_SPLIT = re.compile(r"[^a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    """Lower-case tokenize, returning non-stop non-empty tokens."""
    raw = _TOKEN_SPLIT.split(text.lower())
    return [t for t in raw if t and t not in _STOP_WORDS and len(t) >= 2]


def _ngrams(tokens: list[str], n: int) -> list[str]:
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _build_kw_corpus(
    rules_meta: dict[str, RuleMetadata],
) -> dict[str, int]:
    """Return document-frequency mapping: kw -> number of rules containing it."""
    df: dict[str, int] = {}
    for meta in rules_meta.values():
        for kw in meta.typed_kw:
            df[kw] = df.get(kw, 0) + 1
    return df


def _idf(term: str, df: dict[str, int], n_docs: int) -> float:
    """Log IDF for a candidate term (0 if already in corpus, high if novel)."""
    count = df.get(term, 0)
    if count == 0:
        return math.log(n_docs + 1)
    return math.log((n_docs + 1) / (count + 1))


@dataclass(frozen=True)
class KwProposal:
    """A kw: suggestion for a single rule."""

    rule_path: str
    """Relative path of the rule to edit (e.g. ``rules/109b-...md``)."""

    kind: str
    """Why this proposal exists: ``missing-required`` or ``spurious``."""

    candidates: tuple[tuple[str, float], ...]
    """Ranked (candidate_kw, idf_score) tuples — highest first."""

    firing_kw: tuple[str, ...]
    """For ``spurious`` rules: kw: values that currently cause the rule to fire."""

    narrowing_suggestions: tuple[str, ...]
    """For ``spurious`` rules: proposed narrower kw: variants."""


def suggest_for_fixture(
    fixture_prompt: str,
    missing_required: list[str],
    spurious_loaded: list[str],
    rules_meta: dict[str, RuleMetadata],
    *,
    top_k: int = 5,
    max_ngram: int = 3,
) -> list[KwProposal]:
    """Generate kw: improvement proposals for a single fixture outcome.

    Args:
        fixture_prompt: the fixture's prompt text.
        missing_required: rule paths that were expected but not loaded.
        spurious_loaded: rule paths that loaded but were not expected.
        rules_meta: dict[rule_path, RuleMetadata] for the full corpus.
        top_k: number of candidate kw: terms to return per missing rule.
        max_ngram: max n-gram size to consider (default 3).

    Returns:
        One ``KwProposal`` per rule in ``missing_required + spurious_loaded``.
    """
    proposals: list[KwProposal] = []
    df = _build_kw_corpus(rules_meta)
    n_docs = len(rules_meta)
    tokens = _tokenize(fixture_prompt)

    all_candidates: list[str] = []
    for n in range(1, max_ngram + 1):
        all_candidates.extend(_ngrams(tokens, n))

    for rule_path in missing_required:
        scored: list[tuple[str, float]] = []
        seen: set[str] = set()
        for candidate in all_candidates:
            if candidate in seen:
                continue
            seen.add(candidate)
            score = _idf(candidate, df, n_docs)
            if score > 0:
                scored.append((candidate, round(score, 2)))
        scored.sort(key=lambda x: (-x[1], x[0]))
        proposals.append(
            KwProposal(
                rule_path=rule_path,
                kind="missing-required",
                candidates=tuple(scored[:top_k]),
                firing_kw=(),
                narrowing_suggestions=(),
            )
        )

    for rule_path in spurious_loaded:
        meta = rules_meta.get(rule_path)
        if meta is None:
            continue
        firing: list[str] = []
        for kw in meta.typed_kw:
            kw_tokens = _tokenize(kw)
            if all(t in tokens for t in kw_tokens):
                firing.append(kw)
        narrowing: list[str] = []
        for kw in firing:
            kw_tokens = _tokenize(kw)
            last_idx = -1
            for t in reversed(kw_tokens):
                for idx, tok in enumerate(tokens):
                    if tok == t:
                        last_idx = idx
                        break
            if last_idx >= 0 and last_idx + 1 < len(tokens):
                extended = kw + " " + tokens[last_idx + 1]
                narrowing.append(extended)
        proposals.append(
            KwProposal(
                rule_path=rule_path,
                kind="spurious",
                candidates=(),
                firing_kw=tuple(firing),
                narrowing_suggestions=tuple(narrowing),
            )
        )

    return proposals


def render_proposals_table(proposals: list[KwProposal]) -> list[str]:
    """Render proposals as human-readable lines for CLI output."""
    if not proposals:
        return ["(no suggestions — all expected rules loaded correctly)"]
    lines: list[str] = []
    for p in proposals:
        rule_short = Path(p.rule_path).name
        lines.append(f"\nFor {p.rule_path}  [{p.kind}]:")
        if p.kind == "missing-required":
            if not p.candidates:
                lines.append("  (no candidate kw: terms found in prompt)")
            else:
                lines.append("  Candidate kw: terms (ranked by IDF — add to rule's Keywords):")
                for term, score in p.candidates:
                    lines.append(f"    + kw:{term:<40}  idf={score:.1f}")
        else:
            if p.firing_kw:
                lines.append("  Currently firing kw: (causing spurious load):")
                for kw in p.firing_kw:
                    lines.append(f"    - kw:{kw}")
                if p.narrowing_suggestions:
                    lines.append("  Suggested narrowing (longer phrases that retain match):")
                    for ns in p.narrowing_suggestions:
                        lines.append(f"    → kw:{ns}")
                else:
                    lines.append(
                        f"  (no auto-narrowing found — review kw: in {rule_short} manually)"
                    )
            else:
                lines.append(
                    "  (rule fired but no typed_kw matched prompt — "
                    "may be ext:/file:/dir: trigger or missing metadata)"
                )
    return lines
