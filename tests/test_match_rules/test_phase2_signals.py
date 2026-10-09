"""Phase 2 signal tests: each trigger class independently selects a rule, and
registered n-gram phrases stay effective under top-three competition.

Covers AC4 (bare filename), AC5 (exact directory), AC6 (extension + 2-4 word
semantic phrase, competitive), plus negative controls and the exact-phrase
n-gram scoring contract.
"""

from __future__ import annotations

from pathlib import Path

from ai_rules.match_rules import (
    FileContext,
    RuleEntry,
    extract_context,
    load_rules_db,
    match_rules,
)


def _rule(
    filename: str,
    kw: list[str] | None = None,
    ext: list[str] | None = None,
    file_pats: list[str] | None = None,
    dir_pats: list[str] | None = None,
    tier: str = "Medium",
) -> RuleEntry:
    return RuleEntry(
        filename=filename,
        path=Path(filename),
        context_tier=tier,
        token_budget=1000,
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


def _noise(n: int) -> list[RuleEntry]:
    return [_rule(f"noise{i}.md", kw=[f"unrelated concept {i}"]) for i in range(n)]


def _scored(prompt: str, rules: list[RuleEntry]):
    pc = extract_context(prompt)
    return match_rules(pc.keywords, FileContext(extensions=pc.extensions, paths=pc.paths), rules)


def _top(prompt: str, rules: list[RuleEntry], n: int = 3) -> list[str]:
    return [s.rule.filename for s in _scored(prompt, rules)[:n]]


# ---------------------------------------------------------------------------
# AC4: bare filename alone selects its rule
# ---------------------------------------------------------------------------


def test_ac4_bare_filename_alone_selects_its_rule():
    target = _rule("112.md", file_pats=["snowflake.yml"])
    scored = _scored("Please review my snowflake.yml before we deploy.", [target, *_noise(5)])
    assert scored, "bare filename produced no match"
    assert scored[0].rule.filename == "112.md"


def test_ac4_bare_filename_selects_snowcli_in_real_corpus():
    db = load_rules_db(Path("rules"))
    top3 = _top("Please review my snowflake.yml before we deploy.", list(db.values()))
    assert "112-snowflake-snowcli.md" in top3


# ---------------------------------------------------------------------------
# AC5: exact directory alone selects its rule
# ---------------------------------------------------------------------------


def test_ac5_exact_dir_alone_selects_its_rule():
    target = _rule("002h.md", dir_pats=["skills/"])
    scored = _scored("Where do files under skills/ belong in the bundle?", [target, *_noise(5)])
    assert scored, "exact dir produced no match"
    assert scored[0].rule.filename == "002h.md"


def test_ac5_exact_dir_crosses_threshold_alone():
    # dir: exact award is 4, exactly the inclusion threshold (RC3 fix).
    target = _rule("002h.md", dir_pats=["skills/"])
    scored = _scored("organize the skills/ layout", [target])
    assert scored and scored[0].score >= 4


# ---------------------------------------------------------------------------
# AC6: extension and semantic phrase each independently select
# ---------------------------------------------------------------------------


def test_ac6_extension_alone_selects_its_rule():
    target = _rule("102.md", ext=[".sql"])
    scored = _scored("edit transforms/clean.sql for the landing table", [target, *_noise(5)])
    assert scored and scored[0].rule.filename == "102.md"


def test_ac6_bigram_phrase_selects_its_rule():
    target = _rule("r.md", kw=["cortex search"])
    scored = _scored("we are building a cortex search index", [target, *_noise(5)])
    assert scored and scored[0].rule.filename == "r.md"


def test_ac6_trigram_phrase_selects_its_rule():
    target = _rule("116.md", kw=["cortex search service"])
    scored = _scored("stand up a cortex search service for the app", [target, *_noise(5)])
    assert scored and scored[0].rule.filename == "116.md"


def test_ac6_four_word_phrase_selects_its_rule():
    target = _rule("r.md", kw=["create semantic view syntax"])
    scored = _scored("walk me through create semantic view syntax end to end", [target, *_noise(5)])
    assert scored and scored[0].rule.filename == "r.md"


def test_ac6_semantic_phrase_selects_in_real_corpus():
    db = load_rules_db(Path("rules"))
    top3 = _top("help me configure a cortex search service for chat", list(db.values()))
    assert "116-snowflake-cortex-search.md" in top3


# ---------------------------------------------------------------------------
# Competitive top-three: registered phrases survive competition
# ---------------------------------------------------------------------------


def test_trigram_phrase_stays_in_top3_under_competition():
    target = _rule("target.md", kw=["cortex search service"])
    competitors = [
        _rule("c1.md", kw=["python data pipeline"]),
        _rule("c2.md", kw=["streamlit dashboard"]),
        _rule("c3.md", kw=["warehouse sizing"]),
        _rule("c4.md", kw=["dbt model"]),
        _rule("c5.md", kw=["iceberg table"]),
    ]
    prompt = (
        "We are building a python data pipeline and a streamlit dashboard, but the core "
        "ask is to stand up a cortex search service over our documents."
    )
    top3 = _top(prompt, [target, *competitors])
    assert "target.md" in top3


def test_bare_filename_stays_in_top3_under_competition():
    target = _rule("snowcli.md", file_pats=["snowflake.yml"])
    competitors = [_rule(f"c{i}.md", kw=[f"topic number {i}"]) for i in range(6)]
    prompt = "Review the whole project, but especially the structure of snowflake.yml."
    top3 = _top(prompt, [target, *competitors])
    assert "snowcli.md" in top3


# ---------------------------------------------------------------------------
# Negative controls + exact-phrase contract
# ---------------------------------------------------------------------------


def test_generic_prompt_does_not_select_specialist_rule():
    specialist = _rule("116.md", kw=["cortex search service"])
    scored = _scored("Tell me a joke about the weather today.", [specialist])
    assert scored == []


def test_long_ngram_does_not_fuzzily_inflate_unrelated_rule():
    # A raw 4-gram that shares single words with a rule's phrase must NOT score,
    # because multi-word user tokens are exact-only (the inflation fix).
    rule = _rule("sem.md", kw=["raw landing table"])
    # prompt contains the words but never the exact phrase contiguously
    scored = _scored("we load a raw file into a landing zone and a staging table", [rule])
    assert scored == []


def test_exact_phrase_still_matches_when_present():
    rule = _rule("sem.md", kw=["raw landing table"])
    scored = _scored("write to the raw landing table nightly", [rule])
    assert scored and scored[0].rule.filename == "sem.md"
