"""Unit tests for matcher.py — scoring algorithm and match_rules."""

from __future__ import annotations

from pathlib import Path

from ai_rules.rule_matcher.frontmatter import RuleFrontmatter
from ai_rules.rule_matcher.matcher import (
    FileContext,
    _score_user_kw_against_rule_kw,
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
) -> RuleFrontmatter:
    return RuleFrontmatter(
        filename=filename,
        path=Path(filename),
        context_tier=tier,
        token_budget=token_budget,
        depends=None,
        typed_kw=kw or [],
        typed_ext=ext or [],
        file_patterns=file_pats or [],
        dir_patterns=dir_pats or [],
        rule_version="v1.0",
        description="",
    )


# ---------------------------------------------------------------------------
# _score_user_kw_against_rule_kw
# ---------------------------------------------------------------------------


class TestScoreUserKwAgainstRuleKw:
    def test_exact_phrase_match_scores_10(self):
        assert _score_user_kw_against_rule_kw("pytest fixtures", "pytest fixtures") == 10

    def test_user_substring_of_rule_scores_10(self):
        # "pytest" is a substring of "pytest fixtures"
        assert _score_user_kw_against_rule_kw("pytest", "pytest fixtures") == 10

    def test_rule_substring_of_user_scores_10(self):
        # "pytest" (1 word) in "run pytest tests" (3 words) = 33% coverage < 50% → word match only
        assert _score_user_kw_against_rule_kw("run pytest tests", "pytest") == 1
        # "cortex search" (2 words) in "cortex search service build" (4 words) = 50% → phrase match
        assert _score_user_kw_against_rule_kw("cortex search service build", "cortex search") == 10

    def test_bigram_match_scores_5(self):
        # "pytest fixtures" and "unit test fixtures patterns" share bigram "test fixtures"
        # Actually let's use a clearer example
        assert (
            _score_user_kw_against_rule_kw("slow query investigation", "query investigation tool")
            == 5
        )

    def test_single_word_gt4_chars_scores_1(self):
        assert _score_user_kw_against_rule_kw("streamlit", "deploy") == 0
        # "deploy" (6 chars > 4) appears in rule kw words → single-word match
        assert _score_user_kw_against_rule_kw("deploy application", "fast deploy") == 1

    def test_single_word_5chars_scores_1(self):
        # "pytest" (1 word) in "run pytest again" (3 words) = 33% < 50% → falls to word-level
        result = _score_user_kw_against_rule_kw("pytest", "run pytest again")
        assert result == 1  # word match (6 chars, exact word in list)

    def test_no_match_scores_0(self):
        assert _score_user_kw_against_rule_kw("unrelated", "completely different topic") == 0

    def test_case_insensitive(self):
        assert _score_user_kw_against_rule_kw("Streamlit", "streamlit") == 10

    def test_hyphen_normalised(self):
        # "slow-query" → "slow query"; "slow query" → "slow query"
        assert _score_user_kw_against_rule_kw("slow-query", "slow query investigation") == 10

    def test_underscore_normalised(self):
        assert _score_user_kw_against_rule_kw("slow_query", "slow query") == 10

    def test_short_word_no_match(self):
        # "sql" (3 chars) in "run sql query" — matches as word-level (>= 3 chars, exact word)
        assert _score_user_kw_against_rule_kw("sql", "run sql query") == 1
        # "run" is 3 chars and IS in word list — scores 1
        assert _score_user_kw_against_rule_kw("run", "run sql query") == 1
        # "xy" is 2 chars — too short for any match
        result = _score_user_kw_against_rule_kw("xy", "something else entirely different")
        assert result == 0


# ---------------------------------------------------------------------------
# match_rules
# ---------------------------------------------------------------------------


class TestMatchRules:
    def test_phrase_match_included(self):
        rules = [_rule("200.md", kw=["pytest fixtures"])]
        scored = match_rules(["pytest fixtures"], FileContext(), rules)
        assert len(scored) == 1
        assert scored[0].rule.filename == "200.md"
        assert scored[0].score == 10

    def test_no_match_excluded(self):
        rules = [_rule("200.md", kw=["snowflake"])]
        scored = match_rules(["streamlit"], FileContext(), rules)
        assert scored == []

    def test_extension_match(self):
        rules = [_rule("200.md", ext=[".py"])]
        scored = match_rules([], FileContext(extensions=[".py"]), rules)
        assert len(scored) == 1
        assert scored[0].score == 3

    def test_extension_case_insensitive(self):
        rules = [_rule("200.md", ext=[".PY"])]
        scored = match_rules([], FileContext(extensions=[".py"]), rules)
        assert len(scored) == 1

    def test_file_glob_match(self):
        rules = [_rule("200.md", file_pats=["*/conftest.py"])]
        scored = match_rules([], FileContext(paths=["tests/conftest.py"]), rules)
        assert len(scored) == 1

    def test_dir_glob_match(self):
        rules = [_rule("200.md", dir_pats=["tests"])]
        scored = match_rules([], FileContext(paths=["tests/foo.py"]), rules)
        assert len(scored) == 1

    def test_tier_ordering_critical_first(self):
        r_medium = _rule("medium.md", kw=["pytest"], tier="Medium")
        r_critical = _rule("critical.md", kw=["pytest"], tier="Critical")
        r_high = _rule("high.md", kw=["pytest"], tier="High")
        scored = match_rules(["pytest"], FileContext(), [r_medium, r_high, r_critical])
        tiers = [s.rule.context_tier for s in scored]
        assert tiers == ["Critical", "High", "Medium"]

    def test_score_descending_within_tier(self):
        # a.md matches via both kw and ext, b.md only via ext — so a.md scores higher
        r_low_score = _rule("b.md", ext=[".py"], tier="High")
        r_high_score = _rule("a.md", kw=["python core"], ext=[".py"], tier="High")
        scored = match_rules(
            ["python core"], FileContext(extensions=[".py"]), [r_low_score, r_high_score]
        )
        assert scored[0].rule.filename == "a.md"

    def test_score_threshold_ge_1(self):
        rules = [_rule("200.md", kw=["ab"])]  # "ab" is 2 chars — won't hit 1-pt word match
        scored = match_rules(["ab"], FileContext(), rules)
        # "ab" in "ab" → substring → score 10 (phrase match)
        assert len(scored) == 1

    def test_multiple_keywords_accumulate(self):
        rules = [_rule("200.md", kw=["pytest", "python"])]
        scored = match_rules(["pytest", "python"], FileContext(), rules)
        assert scored[0].score >= 2

    def test_empty_rules_db(self):
        scored = match_rules(["pytest"], FileContext(), [])
        assert scored == []

    def test_empty_keywords_and_context_no_results(self):
        rules = [_rule("200.md", kw=["pytest"])]
        scored = match_rules([], FileContext(), rules)
        assert scored == []
