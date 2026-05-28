"""Unit tests for the deterministic suggestion engine in suggestions.py.

Covers:
- _literal_aliases: hyphen/space/underscore variant generation
- _find_literal_match: alias-normalised literal phrase lookup
- _extract_prompt_phrases: high-signal n-gram extraction from prompts
- _augment_kw_evidence: kw evidence padding up to target
- build_suggestions integration: literal phrase emission, target 5,
  no fabricated evidence, deterministic ordering
- Fixture-validator compatibility: emitted kw values pass _kw_pattern
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.fixtures import _kw_pattern
from ai_rules.rule_loader_eval.rules_meta import RuleMetadata, parse_rule_metadata
from ai_rules.rule_loader_eval.suggestions import (
    MIN_KW_EVIDENCE_TARGET,
    _augment_kw_evidence,
    _extract_prompt_phrases,
    _find_literal_match,
    _literal_aliases,
    build_suggestions,
)

# ---------------------------------------------------------------------------
# _literal_aliases
# ---------------------------------------------------------------------------


def test_literal_aliases_hyphen_gets_space_variant() -> None:
    """A hyphenated term gains a space-separated alias."""
    aliases = _literal_aliases("stored-procedure")
    assert "stored-procedure" in aliases
    assert "stored procedure" in aliases


def test_literal_aliases_space_gets_hyphen_variant() -> None:
    """A space-separated term gains a hyphenated alias."""
    aliases = _literal_aliases("stored procedure")
    assert "stored procedure" in aliases
    assert "stored-procedure" in aliases


def test_literal_aliases_underscore_gets_space_variant() -> None:
    """An underscored term gains a space-separated alias."""
    aliases = _literal_aliases("create_procedure")
    assert "create_procedure" in aliases
    assert "create procedure" in aliases


def test_literal_aliases_no_separators_returns_original_only() -> None:
    """A plain word returns only itself."""
    aliases = _literal_aliases("streamlit")
    assert aliases == ("streamlit",)


def test_literal_aliases_preserves_insertion_order() -> None:
    """Original term is always first in the tuple."""
    aliases = _literal_aliases("stored-procedure")
    assert aliases[0] == "stored-procedure"


def test_literal_aliases_deduplicates() -> None:
    """No duplicate entries in the returned tuple."""
    aliases = _literal_aliases("stored-procedure")
    assert len(aliases) == len(set(aliases))


# ---------------------------------------------------------------------------
# _find_literal_match
# ---------------------------------------------------------------------------


def test_find_literal_match_hyphen_in_prompt() -> None:
    """Returns the hyphen form when the prompt contains hyphen."""
    prompt = "Help me draft a stored-procedure that purges stale rows."
    result = _find_literal_match(prompt, "stored-procedure")
    assert result == "stored-procedure"


def test_find_literal_match_space_in_prompt_via_alias() -> None:
    """Returns space form from prompt when term is hyphenated metadata token."""
    prompt = "Help me draft a stored procedure in procs/cleanup.sql nightly."
    result = _find_literal_match(prompt, "stored-procedure")
    assert result == "stored procedure"


def test_find_literal_match_space_term_finds_hyphen_in_prompt() -> None:
    """Returns hyphen form when term has spaces but prompt uses hyphens."""
    prompt = "Write a create-procedure for the etl pipeline."
    result = _find_literal_match(prompt, "create procedure")
    assert result == "create-procedure"


def test_find_literal_match_case_insensitive() -> None:
    """Match is case-insensitive; returns the exact prompt casing."""
    prompt = "Build a Streamlit dashboard."
    result = _find_literal_match(prompt, "streamlit")
    assert result == "Streamlit"


def test_find_literal_match_no_match_returns_none() -> None:
    """Returns None when no alias matches the prompt."""
    result = _find_literal_match("Fix the Python file.", "stored-procedure")
    assert result is None


def test_find_literal_match_word_boundary_enforced() -> None:
    """Partial substring (e.g. 'sql' inside 'nosql') does not match."""
    prompt = "Use a nosql database."
    # 'sql' is a substring of 'nosql' but the lookbehind should prevent it
    result = _find_literal_match(prompt, "sql")
    assert result is None


def test_find_literal_match_sql_in_extension() -> None:
    """'sql' is matched inside a filename like 'cleanup.sql'."""
    prompt = "Edit procs/cleanup.sql to add a new procedure."
    result = _find_literal_match(prompt, "sql")
    assert result is not None
    assert result.lower() == "sql"


# ---------------------------------------------------------------------------
# _extract_prompt_phrases
# ---------------------------------------------------------------------------


def test_extract_prompt_phrases_returns_literals_from_prompt() -> None:
    """Every returned phrase is a literal substring of the prompt."""
    prompt = "Help me draft a stored procedure in procs/cleanup.sql that purges stale rows nightly."
    phrases = _extract_prompt_phrases(prompt)
    for phrase in phrases:
        assert phrase in prompt, f"{phrase!r} not found literally in prompt"


def test_extract_prompt_phrases_excludes_pure_stop_word_phrases() -> None:
    """Phrases composed entirely of stop words are excluded."""
    prompt = "Help me draft a stored procedure."
    phrases = _extract_prompt_phrases(prompt)
    assert all(phrase.lower() not in {"help me", "me", "a", "help"} for phrase in phrases)


def test_extract_prompt_phrases_no_gap_spanning_slash() -> None:
    """N-grams must not span '/' or '.' boundaries (no 'procs/cleanup')."""
    prompt = "Edit procs/cleanup.sql to fix the stored procedure."
    phrases = _extract_prompt_phrases(prompt)
    assert "procs/cleanup" not in phrases
    assert "cleanup.sql" not in phrases


def test_extract_prompt_phrases_no_gap_spanning_newline() -> None:
    r"""N-grams must not span line breaks.

    Regression: multi-line prompts (the kind generated for ``complex-*``
    fixtures) used to produce kw values like ``"concrete\\nsuggestions for
    naming"``, which serialized into a multi-line YAML token and broke the
    fixture's ``kw: [...]`` array. The fix tightens the n-gram gap regex to
    spaces/tabs only.
    """
    prompt = (
        "Our snowflake.yml has gotten unwieldy as more teams contribute services.\n"
        "I want a clean review of every block in snowflake.yml with concrete\n"
        "suggestions for naming conventions, secret handling, and which fields\n"
        "should live in environment-specific overlays."
    )
    phrases = _extract_prompt_phrases(prompt)
    for p in phrases:
        assert "\n" not in p, f"phrase contains newline: {p!r}"
        assert "\r" not in p, f"phrase contains carriage return: {p!r}"
    # Sanity: at least one valid intra-line phrase still appears.
    assert any("clean review" in p.lower() for p in phrases)
    # The pre-fix bug produced phrases like "concrete\nsuggestions for
    # naming" — make sure no phrase joins tokens from adjacent lines.
    assert not any("concrete suggestions" in p.lower() for p in phrases), (
        "phrase still spans newline boundary"
    )


def test_extract_prompt_phrases_deterministic() -> None:
    """Calling twice with same prompt returns identical tuple."""
    prompt = "Create a Snowflake stored procedure to merge incremental data nightly."
    assert _extract_prompt_phrases(prompt) == _extract_prompt_phrases(prompt)


def test_extract_prompt_phrases_deduplicates_case_insensitively() -> None:
    """Duplicate phrases (case-insensitive) appear only once."""
    prompt = "Use Streamlit streamlit in your Streamlit app."
    phrases = _extract_prompt_phrases(prompt)
    lower_phrases = [p.lower() for p in phrases]
    assert len(lower_phrases) == len(set(lower_phrases))


def test_extract_prompt_phrases_passes_kw_pattern() -> None:
    """Every returned phrase passes the fixture validator's _kw_pattern check."""
    prompt = "Help me draft a stored procedure in procs/cleanup.sql that purges stale rows nightly."
    phrases = _extract_prompt_phrases(prompt)
    for phrase in phrases:
        assert _kw_pattern(phrase).search(prompt), (
            f"phrase {phrase!r} does not pass _kw_pattern against prompt"
        )


# ---------------------------------------------------------------------------
# _augment_kw_evidence
# ---------------------------------------------------------------------------


def test_augment_kw_evidence_pads_to_target() -> None:
    """Adds phrases from prompt until target is reached."""
    prompt = "Draft a stored procedure to purge stale rows nightly in cleanup.sql."
    phrases = _extract_prompt_phrases(prompt)
    evidence: dict[str, set[str]] = {
        "kw": {"stored-procedure"},
        "ext": set(),
        "file": set(),
        "dir": set(),
    }
    _augment_kw_evidence(evidence, phrases, target=5)
    assert len(evidence["kw"]) >= min(5, len(phrases) + 1)


def test_augment_kw_evidence_does_not_exceed_target() -> None:
    """Does not add more than target items."""
    prompt = "Use Streamlit to build a dashboard with data from Snowflake using Python."
    phrases = _extract_prompt_phrases(prompt)
    evidence: dict[str, set[str]] = {"kw": set(), "ext": set(), "file": set(), "dir": set()}
    _augment_kw_evidence(evidence, phrases, target=3)
    assert len(evidence["kw"]) <= 3


def test_augment_kw_evidence_no_duplicates() -> None:
    """Does not add phrases already present (case-insensitive)."""
    evidence: dict[str, set[str]] = {
        "kw": {"stored-procedure"},
        "ext": set(),
        "file": set(),
        "dir": set(),
    }
    phrases = ("stored procedure", "stale", "nightly")
    _augment_kw_evidence(evidence, phrases, target=5)
    lower_vals = [v.lower() for v in evidence["kw"]]
    assert len(lower_vals) == len(set(lower_vals))


def test_augment_kw_evidence_sparse_prompt_emits_fewer() -> None:
    """If prompt has fewer phrases than target, emits fewer without fabrication."""
    evidence: dict[str, set[str]] = {"kw": set(), "ext": set(), "file": set(), "dir": set()}
    phrases = ("sql",)  # only one phrase available
    _augment_kw_evidence(evidence, phrases, target=5)
    assert len(evidence["kw"]) == 1


# ---------------------------------------------------------------------------
# build_suggestions integration
# ---------------------------------------------------------------------------


def _make_meta(
    path: str, keywords: str, typed_keywords: str, depends: str = "999-test-core.md"
) -> RuleMetadata:
    """Helper: parse a minimal rule metadata block.

    v3.3: typed Keywords is the sole trigger evidence source. Already-prefixed
    ``typed_keywords`` entries are merged with bare ``keywords`` entries (wrapped
    as ``kw:``) into a single Keywords field.
    """
    parts: list[str] = []
    # Already typed-prefixed entries come first.
    if typed_keywords:
        parts.extend(t.strip() for t in typed_keywords.split(",") if t.strip())
    # Bare keyword entries are wrapped as kw: (lowercase).
    if keywords:
        seen = {p.lower() for p in parts}
        for kw in keywords.split(","):
            kw = kw.strip()
            if not kw:
                continue
            typed = f"kw:{' '.join(kw.lower().split())}"
            if typed not in seen:
                parts.append(typed)
                seen.add(typed)
    typed_keywords = ", ".join(parts) if parts else "kw:rule"
    content = f"**Keywords:** {typed_keywords}\n**Depends:** {depends}\n"
    return parse_rule_metadata(Path(path), content)


@pytest.mark.unit
def test_build_suggestions_stored_procedure_space_emits_literal() -> None:
    """Prompt with 'stored procedure' (space) emits that literal phrase in kw evidence."""
    prompt = "Help me draft a stored procedure in procs/cleanup.sql that purges stale rows nightly."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md",
            keywords="workflow, safety",
            typed_keywords="",
            depends="",
        ),
        "rules/102b-snowflake-sql-procedures.md": _make_meta(
            "rules/102b-snowflake-sql-procedures.md",
            keywords="stored procedure, CREATE PROCEDURE, UDF",
            typed_keywords="kw:stored-procedure, kw:create-procedure",
            depends="102-snowflake-sql-core.md",
        ),
    }
    loaded = (
        "rules/999-test-core.md",
        "rules/102b-snowflake-sql-procedures.md",
    )
    sugg = build_suggestions(loaded, prompt, rules_meta)
    kw = sugg.trigger_evidence.get("kw", ())
    assert "stored procedure" in kw, f"expected 'stored procedure' in kw, got {kw}"


@pytest.mark.unit
def test_build_suggestions_stored_procedure_hyphen_emits_literal() -> None:
    """Prompt with 'stored-procedure' (hyphen) emits that literal phrase in kw evidence."""
    prompt = "Help me draft a stored-procedure in procs/cleanup.sql that purges stale rows nightly."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md",
            keywords="workflow, safety",
            typed_keywords="",
            depends="",
        ),
        "rules/102b-snowflake-sql-procedures.md": _make_meta(
            "rules/102b-snowflake-sql-procedures.md",
            keywords="stored procedure, CREATE PROCEDURE, UDF",
            typed_keywords="kw:stored-procedure, kw:create-procedure",
            depends="102-snowflake-sql-core.md",
        ),
    }
    loaded = (
        "rules/999-test-core.md",
        "rules/102b-snowflake-sql-procedures.md",
    )
    sugg = build_suggestions(loaded, prompt, rules_meta)
    kw = sugg.trigger_evidence.get("kw", ())
    assert "stored-procedure" in kw, f"expected 'stored-procedure' in kw, got {kw}"


@pytest.mark.unit
def test_build_suggestions_targets_five_kw() -> None:
    """build_suggestions emits up to MIN_KW_EVIDENCE_TARGET n-gram suggestions for
    a rich prompt.

    Under the valid-by-construction contract, n-gram-derived prompt phrases live
    in ``Suggestions.ngram_kw_suggestions`` (rendered as inline ``# n-gram (no
    rule):`` comments) rather than padding ``trigger_evidence['kw']``. This test
    asserts the combined "rule-tied + n-gram suggestion" count meets the target.
    """
    prompt = (
        "Help me draft a stored procedure in procs/cleanup.sql "
        "that purges stale rows nightly using EXECUTE AS OWNER."
    )
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md",
            keywords="workflow, safety",
            typed_keywords="",
            depends="",
        ),
        "rules/102b-snowflake-sql-procedures.md": _make_meta(
            "rules/102b-snowflake-sql-procedures.md",
            keywords="stored procedure, CREATE PROCEDURE, UDF, EXECUTE AS, dynamic SQL",
            typed_keywords="kw:stored-procedure",
            depends="102-snowflake-sql-core.md",
        ),
    }
    loaded = (
        "rules/999-test-core.md",
        "rules/102b-snowflake-sql-procedures.md",
    )
    sugg = build_suggestions(loaded, prompt, rules_meta)
    kw = sugg.trigger_evidence.get("kw", ())
    ngrams = sugg.ngram_kw_suggestions
    combined = len(kw) + len(ngrams)
    assert combined >= MIN_KW_EVIDENCE_TARGET, (
        f"expected >= {MIN_KW_EVIDENCE_TARGET} combined kw + n-gram entries, "
        f"got {combined} (kw={kw}, ngrams={ngrams})"
    )


@pytest.mark.unit
def test_build_suggestions_sparse_prompt_emits_fewer_than_target() -> None:
    """build_suggestions emits fewer than target when prompt is sparse."""
    prompt = "Write a UDF."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md",
            keywords="workflow",
            typed_keywords="",
            depends="",
        ),
        "rules/102b-snowflake-sql-procedures.md": _make_meta(
            "rules/102b-snowflake-sql-procedures.md",
            keywords="UDF",
            typed_keywords="kw:udf",
            depends="102-snowflake-sql-core.md",
        ),
    }
    loaded = ("rules/999-test-core.md", "rules/102b-snowflake-sql-procedures.md")
    sugg = build_suggestions(loaded, prompt, rules_meta)
    kw = sugg.trigger_evidence.get("kw", ())
    # Every emitted value must appear literally in the prompt.
    for val in kw:
        assert _kw_pattern(val).search(prompt), (
            f"emitted kw {val!r} not found literally in sparse prompt"
        )


@pytest.mark.unit
def test_build_suggestions_all_kw_pass_kw_pattern() -> None:
    """Every emitted kw value passes the fixture validator's _kw_pattern check."""
    prompt = "Help me draft a stored procedure in procs/cleanup.sql that purges stale rows nightly."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md",
            keywords="workflow, safety",
            typed_keywords="",
            depends="",
        ),
        "rules/102b-snowflake-sql-procedures.md": _make_meta(
            "rules/102b-snowflake-sql-procedures.md",
            keywords="stored procedure, CREATE PROCEDURE, procedure body",
            typed_keywords="kw:stored-procedure",
            depends="102-snowflake-sql-core.md",
        ),
    }
    loaded = ("rules/999-test-core.md", "rules/102b-snowflake-sql-procedures.md")
    sugg = build_suggestions(loaded, prompt, rules_meta)
    kw = sugg.trigger_evidence.get("kw", ())
    for val in kw:
        assert _kw_pattern(val).search(prompt), (
            f"emitted kw {val!r} does not pass _kw_pattern against prompt"
        )


@pytest.mark.unit
def test_build_suggestions_deterministic_ordering() -> None:
    """Repeated calls with same inputs return identical Suggestions."""
    prompt = "Help me draft a stored procedure to purge stale rows nightly."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md", keywords="workflow", typed_keywords="", depends=""
        ),
        "rules/102b-snowflake-sql-procedures.md": _make_meta(
            "rules/102b-snowflake-sql-procedures.md",
            keywords="stored procedure, procedure body",
            typed_keywords="kw:stored-procedure",
            depends="102-snowflake-sql-core.md",
        ),
    }
    loaded = ("rules/999-test-core.md", "rules/102b-snowflake-sql-procedures.md")
    result_a = build_suggestions(loaded, prompt, rules_meta)
    result_b = build_suggestions(loaded, prompt, rules_meta)
    assert result_a == result_b


@pytest.mark.unit
def test_build_suggestions_no_duplicate_kw_case_insensitive() -> None:
    """Kw evidence contains no case-insensitive duplicates."""
    prompt = "Help me draft a stored procedure in procs/cleanup.sql."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md", keywords="workflow", typed_keywords="", depends=""
        ),
        "rules/102b-snowflake-sql-procedures.md": _make_meta(
            "rules/102b-snowflake-sql-procedures.md",
            keywords="stored procedure",
            typed_keywords="kw:stored-procedure",
            depends="102-snowflake-sql-core.md",
        ),
    }
    loaded = ("rules/999-test-core.md", "rules/102b-snowflake-sql-procedures.md")
    sugg = build_suggestions(loaded, prompt, rules_meta)
    kw = sugg.trigger_evidence.get("kw", ())
    lower = [v.lower() for v in kw]
    assert len(lower) == len(set(lower)), f"duplicates found: {kw}"


# ---------------------------------------------------------------------------
# Integration test using real project fixtures and rule metadata
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_build_suggestions_real_stored_procedure_space_prompt(
    tmp_path: Path,
) -> None:
    """With the real rules/ directory, space-form prompt emits literal evidence."""
    from ai_rules.rule_loader_eval.agent_runner import AgentRun
    from ai_rules.rule_loader_eval.snippet import format_fixture_snippet

    here = Path(__file__).resolve()
    project_root = next(p for p in (here, *here.parents) if (p / "pyproject.toml").exists())

    prompt = "Help me draft a stored procedure in procs/cleanup.sql that purges stale rows nightly."
    run = AgentRun(
        fixture_id="test",
        loaded=(
            "rules/999-test-core.md",
            "rules/100-snowflake-core.md",
            "rules/102-snowflake-sql-core.md",
            "rules/102b-snowflake-sql-procedures.md",
        ),
        loaded_via_reads=(),
        loaded_via_reads_performed=(),
        loaded_via_section=(),
    )
    snippet = format_fixture_snippet(
        run, prompt, "test-stored-proc", "simple", project_root, "2026-05-16T12:00:00-07:00"
    )
    assert "stored procedure" in snippet, f"'stored procedure' not found in snippet:\n{snippet}"
    # Also confirm the fixture validator would accept it by checking kw pattern
    assert _kw_pattern("stored procedure").search(prompt)
