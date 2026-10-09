"""Unit tests for the matcher-owned canonical trigger semantics (Phase 1).

Covers the public API added to ``match_rules``: ``normalize_trigger``,
``parse_typed_triggers``, ``extract_context``, ``validate_trigger_counts``,
``explain_match``, and the exported stop-word constants.
"""

from __future__ import annotations

from pathlib import Path

from ai_rules.match_rules import (
    HARD_STOP_WORDS,
    MAX_TRIGGER_NGRAM,
    SHORT_TECH_ALLOWLIST,
    SOFT_STOP_WORDS,
    TRIGGER_COUNT_MAX,
    TRIGGER_COUNT_MIN,
    FileContext,
    MatchEvidence,
    PromptContext,
    RuleEntry,
    TriggerSet,
    TypedTrigger,
    explain_match,
    extract_context,
    match_rules,
    normalize_trigger,
    parse_typed_triggers,
    validate_trigger_counts,
)


def _rule(
    filename: str = "test.md",
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


# ---------------------------------------------------------------------------
# normalize_trigger
# ---------------------------------------------------------------------------


def test_normalize_trigger_recognizes_each_kind():
    assert normalize_trigger("kw:Cortex Search") == TypedTrigger("kw", "cortex search")
    assert normalize_trigger("ext:.SQL") == TypedTrigger("ext", ".sql")
    assert normalize_trigger("file:snowflake.yml") == TypedTrigger("file", "snowflake.yml")
    assert normalize_trigger("dir:skills/") == TypedTrigger("dir", "skills/")


def test_normalize_trigger_bare_entry_is_keyword():
    assert normalize_trigger("cortex search service") == TypedTrigger("kw", "cortex search service")


def test_normalize_trigger_is_value_idempotent():
    once = normalize_trigger("kw:Cortex Search")
    twice = normalize_trigger(f"{once.kind}:{once.value}")
    assert once == twice


def test_normalize_trigger_strips_whitespace():
    assert normalize_trigger("  kw:  Cortex Search  ") == TypedTrigger("kw", "cortex search")


# ---------------------------------------------------------------------------
# parse_typed_triggers
# ---------------------------------------------------------------------------


def test_parse_typed_triggers_splits_by_kind():
    ts = parse_typed_triggers(
        ["kw:cortex search", "kw:search service", "ext:.sql", "file:snowflake.yml", "dir:skills/"]
    )
    assert ts.kw == ["cortex search", "search service"]
    assert ts.ext == [".sql"]
    assert ts.file == ["snowflake.yml"]
    assert ts.dir == ["skills/"]
    assert ts.total() == 5


def test_parse_typed_triggers_skips_blank_entries():
    ts = parse_typed_triggers(["kw:a", "", "  ", "ext:.py"])
    assert ts.total() == 2


def test_parse_typed_triggers_empty_input():
    assert parse_typed_triggers([]) == TriggerSet()


# ---------------------------------------------------------------------------
# extract_context
# ---------------------------------------------------------------------------


def test_extract_context_emits_contiguous_bigrams_and_trigrams():
    pc = extract_context("cortex search service", max_ngram=4)
    assert "cortex search" in pc.keywords
    assert "search service" in pc.keywords
    assert "cortex search service" in pc.keywords


def test_extract_context_caps_ngram_length_at_four():
    pc = extract_context("one two three four five six seven", max_ngram=10)
    longest = max(len(k.split()) for k in pc.keywords)
    assert longest <= MAX_TRIGGER_NGRAM


def test_extract_context_respects_lower_max_ngram():
    pc = extract_context("cortex search service tool", max_ngram=2)
    assert max(len(k.split()) for k in pc.keywords) == 2


def test_extract_context_bare_filename_dual_routed_without_ext_double_count():
    pc = extract_context("wire the native app into snowflake.yml today")
    # Routed to paths for file: matching...
    assert "snowflake.yml" in pc.paths
    # ...and retained as a keyword for semantic matching...
    assert "snowflake.yml" in pc.keywords
    # ...but NOT emitted as an extension (no within-class double count of the file signal).
    assert pc.extensions == []


def test_extract_context_normalizes_readme_me_to_readme_md():
    pc = extract_context("Review README.me before release")
    assert "readme.md" in pc.paths
    assert "readme.md" in pc.keywords


def test_extract_context_slash_path_extracts_extension():
    pc = extract_context("edit jobs/extract_load.py now")
    assert any(p == "jobs/extract_load.py" for p in pc.paths)
    assert ".py" in pc.extensions


def test_extract_context_unigrams_are_stop_filtered():
    pc = extract_context("the and for with data pipeline")
    # short/stop words are excluded from unigram keywords
    assert "the" not in pc.keywords
    # meaningful unigrams retained
    assert "pipeline" in pc.keywords


def test_extract_context_returns_prompt_context_shape():
    pc = extract_context("cortex search")
    assert isinstance(pc, PromptContext)
    assert set(vars(pc).keys()) == {"keywords", "extensions", "paths"}


# ---------------------------------------------------------------------------
# validate_trigger_counts (boundaries 4 / 5 / 11 / 12)
# ---------------------------------------------------------------------------


def _triggerset_of_size(n: int) -> TriggerSet:
    return parse_typed_triggers([f"kw:w{i}" for i in range(n)])


def test_validate_trigger_counts_below_minimum():
    v = validate_trigger_counts(_triggerset_of_size(4))
    assert len(v) == 1
    assert v[0].code == "too_few"
    assert v[0].count == 4


def test_validate_trigger_counts_at_minimum_is_clean():
    assert validate_trigger_counts(_triggerset_of_size(TRIGGER_COUNT_MIN)) == []


def test_validate_trigger_counts_at_maximum_is_clean():
    assert validate_trigger_counts(_triggerset_of_size(TRIGGER_COUNT_MAX)) == []


def test_validate_trigger_counts_above_maximum():
    v = validate_trigger_counts(_triggerset_of_size(12))
    assert len(v) == 1
    assert v[0].code == "too_many"
    assert v[0].count == 12


def test_validate_trigger_counts_combines_all_kinds():
    ts = parse_typed_triggers(["kw:a", "kw:b", "ext:.py", "file:x.yml", "dir:d/"])
    assert ts.total() == 5
    assert validate_trigger_counts(ts) == []


# ---------------------------------------------------------------------------
# explain_match (parity with match_rules)
# ---------------------------------------------------------------------------


def test_explain_match_returns_evidence_with_signals():
    rule = _rule(kw=["cortex search service"])
    ctx = PromptContext(keywords=["cortex search service"], extensions=[], paths=[])
    ev = explain_match(rule, ctx)
    assert isinstance(ev, MatchEvidence)
    assert ev.total == 10  # exact kw match
    assert any(s.signal == "kw" and s.points == 10 for s in ev.signals)


def test_explain_match_total_equals_match_rules_score():
    rules = [
        _rule(filename="a.md", kw=["cortex search service"]),
        _rule(filename="b.md", ext=[".sql"]),
        _rule(filename="c.md", file_pats=["snowflake.yml"]),
        _rule(filename="d.md", dir_pats=["skills/"]),
    ]
    keywords = ["cortex search service", "pipeline"]
    fc = FileContext(extensions=[".sql"], paths=["snowflake.yml", "skills/manifest"])
    scored = match_rules(keywords, fc, rules)
    ctx = PromptContext(keywords=keywords, extensions=fc.extensions, paths=fc.paths)
    for s in scored:
        assert explain_match(s.rule, ctx).total == s.score


def test_explain_match_soft_stop_word_capped_to_one():
    # pick any soft stop word; it must cap to 1 point even on an exact kw hit
    soft = next(iter(SOFT_STOP_WORDS))
    rule = _rule(kw=[soft])
    ctx = PromptContext(keywords=[soft], extensions=[], paths=[])
    ev = explain_match(rule, ctx)
    assert ev.total == 1


# ---------------------------------------------------------------------------
# exported stop-word constants
# ---------------------------------------------------------------------------


def test_stop_word_constants_are_exported_frozensets():
    assert isinstance(HARD_STOP_WORDS, frozenset)
    assert isinstance(SOFT_STOP_WORDS, frozenset)
    assert isinstance(SHORT_TECH_ALLOWLIST, frozenset)
    assert HARD_STOP_WORDS and SOFT_STOP_WORDS and SHORT_TECH_ALLOWLIST
