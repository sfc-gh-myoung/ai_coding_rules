"""Unit tests for match_rules.py — scoring algorithm and match_rules."""

from __future__ import annotations

from pathlib import Path

from ai_rules.match_rules import (
    FileContext,
    RuleEntry,
    _score_kw,
    match_rules,
)


def _rule(
    filename: str = "test.md",
    kw: list[str] | None = None,
    ext: list[str] | None = None,
    file_pats: list[str] | None = None,
    dir_pats: list[str] | None = None,
    tier: str = "Medium",
    token_budget: int = 1000,
) -> RuleEntry:
    return RuleEntry(
        filename=filename,
        path=Path(filename),
        context_tier=tier,
        token_budget=token_budget,
        depends_required=[],
        depends_optional=[],
        typed_kw=kw or [],
        typed_ext=ext or [],
        file_patterns=file_pats or [],
        dir_patterns=dir_pats or [],
        rule_version="v1.0",
        description="",
        line_count=10,
        last_updated="2026-01-01",
        schema_version="v3.5",
        keywords_raw=[],
    )


# ---------------------------------------------------------------------------
# _score_kw
# ---------------------------------------------------------------------------


class TestScoreKw:
    def test_exact_phrase_match_scores_10(self):
        assert _score_kw("pytest fixtures", "pytest fixtures") == 10

    def test_user_substring_of_rule_scores_10(self):
        assert _score_kw("pytest", "pytest fixtures") == 10

    def test_rule_substring_of_user_scores_10(self):
        assert _score_kw("pytest fixtures setup", "pytest fixtures") == 10

    def test_case_insensitive(self):
        assert _score_kw("Streamlit", "streamlit") == 10

    def test_hyphen_normalized(self):
        assert _score_kw("cortex-search", "cortex search") == 10

    def test_underscore_normalized(self):
        assert _score_kw("session_state", "session state") == 10

    def test_bigram_overlap_scores_5(self):
        assert _score_kw("python test coverage", "test coverage report") == 5

    def test_single_word_match_scores_1(self):
        assert _score_kw("snowflake", "snowflake cortex agents") == 1

    def test_short_words_no_match(self):
        assert _score_kw("do", "do something") == 0

    def test_no_match_zero(self):
        assert _score_kw("python", "javascript") == 0


# ---------------------------------------------------------------------------
# match_rules
# ---------------------------------------------------------------------------


class TestMatchRules:
    def test_keyword_match_returns_scored_rules(self):
        rule = _rule("200.md", kw=["streamlit"])
        scored = match_rules(["streamlit"], FileContext(), [rule])
        assert len(scored) == 1
        assert scored[0].rule.filename == "200.md"

    def test_extension_match(self):
        rule = _rule("200.md", ext=[".py"])
        scored = match_rules([], FileContext(extensions=[".py"]), [rule], score_threshold=3)
        assert len(scored) == 1

    def test_below_threshold_excluded(self):
        rule = _rule("200.md", kw=["some long keyword"])
        scored = match_rules(["xyz"], FileContext(), [rule], score_threshold=3)
        assert len(scored) == 0

    def test_sorted_by_score_descending(self):
        r1 = _rule("low.md", kw=["streamlit"])
        r2 = _rule("high.md", kw=["streamlit", "python"])
        scored = match_rules(["streamlit", "python"], FileContext(), [r1, r2])
        assert scored[0].rule.filename == "high.md"

    def test_file_pattern_match(self):
        rule = _rule("200.md", file_pats=["auth.py"])
        scored = match_rules([], FileContext(paths=["src/auth.py"]), [rule])
        assert len(scored) == 1

    def test_dir_pattern_match(self):
        rule = _rule("200.md", dir_pats=["tests"])
        scored = match_rules(
            [], FileContext(paths=["tests/test_foo.py"]), [rule], score_threshold=3
        )
        assert len(scored) == 1

    def test_tier_used_for_tiebreaking(self):
        r_high = _rule("high.md", kw=["python"], tier="High")
        r_low = _rule("low.md", kw=["python"], tier="Low")
        scored = match_rules(["python"], FileContext(), [r_high, r_low])
        assert scored[0].rule.filename == "high.md"
        assert scored[1].rule.filename == "low.md"
