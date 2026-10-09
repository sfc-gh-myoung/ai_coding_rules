"""Unit tests for kw_suggester."""

from __future__ import annotations

from pathlib import Path

import pytest  # noqa: F401  # used indirectly via pytest.raises in remaining tests

from ai_rules.rule_loader_eval.kw_suggester import (
    KwProposal,
    _build_kw_corpus,
    _idf,
    _ngrams,
    _tokenize,
    render_proposals_table,
    suggest_for_fixture,
)
from ai_rules.rule_loader_eval.rules_meta import RuleMetadata


def _meta(path: str, typed_kw: tuple[str, ...] = ()) -> RuleMetadata:
    return RuleMetadata(path=Path(path), typed_kw=typed_kw)


def _corpus(*entries: tuple[str, tuple[str, ...]]) -> dict[str, RuleMetadata]:
    return {path: _meta(path, kws) for path, kws in entries}


class TestTokenize:
    def test_lowercases(self) -> None:
        assert "snow" in _tokenize("SNOW")

    def test_removes_stop_words(self) -> None:
        tokens = _tokenize("the quick brown fox")
        assert "the" not in tokens
        assert "quick" in tokens

    def test_splits_on_non_alnum(self) -> None:
        tokens = _tokenize("snow-app-deploy")
        assert "snow" in tokens
        assert "app" in tokens
        assert "deploy" in tokens

    def test_filters_short_tokens(self) -> None:
        tokens = _tokenize("a x deploy")
        assert "a" not in tokens
        assert "x" not in tokens
        assert "deploy" in tokens


class TestNgrams:
    def test_unigrams(self) -> None:
        assert _ngrams(["a", "b", "c"], 1) == ["a", "b", "c"]

    def test_bigrams(self) -> None:
        assert _ngrams(["snow", "app", "deploy"], 2) == ["snow app", "app deploy"]

    def test_too_short(self) -> None:
        assert _ngrams(["snow"], 3) == []


class TestBuildKwCorpus:
    def test_counts_per_rule(self) -> None:
        corpus = _corpus(
            ("rules/A.md", ("deploy", "snowflake")),
            ("rules/B.md", ("deploy",)),
        )
        df = _build_kw_corpus(corpus)
        assert df["deploy"] == 2
        assert df["snowflake"] == 1

    def test_empty_corpus(self) -> None:
        assert _build_kw_corpus({}) == {}


class TestIdf:
    def test_novel_term_high_idf(self) -> None:
        df = {"known": 5}
        score = _idf("novel", df, n_docs=10)
        assert score > 2.0

    def test_common_term_lower_idf(self) -> None:
        df = {"common": 9}
        score = _idf("common", df, n_docs=10)
        assert score < 0.5


class TestSuggestForFixture:
    def test_missing_required_returns_proposal(self) -> None:
        corpus = _corpus(
            ("rules/999-test-core.md", ("foundation",)),
            ("rules/109b.md", ("app deployment",)),
        )
        proposals = suggest_for_fixture(
            "Deploy a Snowflake Native App using snow app deploy",
            missing_required=["rules/109b.md"],
            spurious_loaded=[],
            rules_meta=corpus,
            top_k=5,
        )
        assert len(proposals) == 1
        assert proposals[0].rule_path == "rules/109b.md"
        assert proposals[0].kind == "missing-required"
        assert len(proposals[0].candidates) > 0

    def test_spurious_returns_firing_kw(self) -> None:
        corpus = _corpus(
            ("rules/102a.md", ("sql automation",)),
        )
        proposals = suggest_for_fixture(
            "Implement SQL automation pipeline for deploy",
            missing_required=[],
            spurious_loaded=["rules/102a.md"],
            rules_meta=corpus,
            top_k=5,
        )
        assert len(proposals) == 1
        p = proposals[0]
        assert p.kind == "spurious"
        assert "sql automation" in p.firing_kw

    def test_no_spurious_firing_when_kw_not_in_prompt(self) -> None:
        corpus = _corpus(("rules/X.md", ("kubernetes pods",)))
        proposals = suggest_for_fixture(
            "Deploy Streamlit dashboard",
            missing_required=[],
            spurious_loaded=["rules/X.md"],
            rules_meta=corpus,
        )
        assert len(proposals) == 1
        assert proposals[0].firing_kw == ()

    def test_top_k_respected(self) -> None:
        corpus = _corpus(("rules/A.md", ()))
        proposals = suggest_for_fixture(
            "one two three four five six seven eight nine ten",
            missing_required=["rules/A.md"],
            spurious_loaded=[],
            rules_meta=corpus,
            top_k=3,
        )
        assert len(proposals[0].candidates) <= 3

    def test_empty_inputs_returns_empty(self) -> None:
        corpus = _corpus(("rules/A.md", ()))
        proposals = suggest_for_fixture("some prompt", [], [], corpus)
        assert proposals == []

    def test_unknown_spurious_rule_skipped_gracefully(self) -> None:
        corpus = _corpus(("rules/A.md", ()))
        proposals = suggest_for_fixture(
            "some prompt",
            missing_required=[],
            spurious_loaded=["rules/DOES_NOT_EXIST.md"],
            rules_meta=corpus,
        )
        assert proposals == []


class TestRenderProposalsTable:
    def test_empty_proposals_returns_no_suggestions_line(self) -> None:
        lines = render_proposals_table([])
        assert any("no suggestions" in ln for ln in lines)

    def test_missing_required_proposal_rendered(self) -> None:
        p = KwProposal(
            rule_path="rules/109b.md",
            kind="missing-required",
            candidates=(("snow app deploy", 3.2),),
            firing_kw=(),
            narrowing_suggestions=(),
        )
        lines = render_proposals_table([p])
        joined = "\n".join(lines)
        assert "rules/109b.md" in joined
        assert "missing-required" in joined
        assert "snow app deploy" in joined

    def test_spurious_proposal_rendered(self) -> None:
        p = KwProposal(
            rule_path="rules/102a.md",
            kind="spurious",
            candidates=(),
            firing_kw=("sql automation",),
            narrowing_suggestions=("sql automation pipeline",),
        )
        lines = render_proposals_table([p])
        joined = "\n".join(lines)
        assert "spurious" in joined
        assert "sql automation" in joined
        assert "sql automation pipeline" in joined
