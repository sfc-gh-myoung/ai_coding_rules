"""Tests for the agent runner's section parsers.

The ``parse_rules_loaded_section`` and ``parse_reads_performed_section``
functions extract ``rules/<name>.md`` paths from the agent's final
assistant text. Edge cases include:

- Absolute paths that include the project directory name
  ``ai_coding_rules`` must not produce ``rules/rules/<name>.md``.
- Markdown link form ``[rules/X.md](rules/X.md)`` should dedupe.
- Text outside the named section is ignored.
- Citations of form ``<path> (<reason>) — N lines`` are extracted via
  ``extract_citations``.
"""

from __future__ import annotations

import pytest

from ai_rules.rule_loader_eval.agent_runner import (
    Citation,
    extract_citations,
    parse_bootstrap_line,
    parse_reads_performed_section,
    parse_rules_loaded_section,
)


@pytest.mark.unit
def test_simple_list_extracted() -> None:
    """A bullet list of rule paths under the bold marker is extracted."""
    text = """
**Rules Loaded**

- rules/999-test-core.md
- rules/100-snowflake-core.md
"""
    assert parse_rules_loaded_section(text) == (
        "rules/100-snowflake-core.md",
        "rules/999-test-core.md",
    )


@pytest.mark.unit
def test_absolute_path_does_not_double_rules() -> None:
    """Absolute paths inside ai_coding_rules/ must not produce rules/rules/...

    Regression for the bug where an unanchored regex matched the ``rules``
    substring inside ``ai_coding_rules`` and greedily consumed across
    a path separator into ``rules/rules/999-test-core.md``.
    """
    text = """
**Rules Loaded**

- /Users/me/Development/ai_coding_rules/rules/999-test-core.md
- /Users/me/Development/ai_coding_rules/rules/116-snowflake-cortex-search.md
"""
    out = parse_rules_loaded_section(text)
    assert "rules/999-test-core.md" in out
    assert "rules/116-snowflake-cortex-search.md" in out
    for rule in out:
        assert not rule.startswith("rules/rules/"), rule


@pytest.mark.unit
def test_markdown_link_form_dedupes() -> None:
    """A markdown link to a rule should produce one entry, not two."""
    text = """
**Rules Loaded**

- [rules/100-snowflake-core.md](rules/100-snowflake-core.md)
"""
    assert parse_rules_loaded_section(text) == ("rules/100-snowflake-core.md",)


@pytest.mark.unit
def test_text_outside_section_ignored() -> None:
    """Rule paths outside a Rules Loaded heading are not picked up."""
    text = """
Some prelude that mentions rules/100-snowflake-core.md inline.

## Other Heading

- rules/200-python-core.md
"""
    assert parse_rules_loaded_section(text) == ()


@pytest.mark.unit
def test_section_terminates_at_task_switch() -> None:
    """Content after Task Switch: is not part of the section (new format)."""
    text = """
**Bootstrap:** rule-loader [scanned: (python) — 1 rules loaded, 0 failed.
**Rules Loaded**
- rules/999-test-core.md

Task Switch: FIRST

Some response content mentioning rules/200-python-core.md.
"""
    assert parse_rules_loaded_section(text) == ("rules/999-test-core.md",)


@pytest.mark.unit
def test_section_terminates_at_next_heading_legacy() -> None:
    """Legacy ## Rules Loaded heading: content after next heading not captured (backward compat)."""
    text = """
## Rules Loaded

- rules/999-test-core.md

## Notes

- rules/200-python-core.md should not be captured.
"""
    assert parse_rules_loaded_section(text) == ("rules/999-test-core.md",)


@pytest.mark.unit
def test_empty_input() -> None:
    """Empty text yields an empty tuple."""
    assert parse_rules_loaded_section("") == ()
    assert parse_rules_loaded_section(None) == ()  # type: ignore[arg-type]


@pytest.mark.unit
def test_parse_reads_performed_section() -> None:
    """``## Reads Performed`` parser extracts paths same as Rules Loaded.

    (Legacy backward-compat — ``## Reads Performed`` retired in v3.8.0.)
    """
    text = """
## Reads Performed
- read_file("rules/999-test-core.md") -> RuleVersion v3.7.0, LastUpdated 2026-05-14, lines 470
- grep rules/*.md (Keywords discovery step)
- read_file("rules/100-snowflake-core.md") -> RuleVersion v1.2.3, LastUpdated 2026-04-01, lines 200

**Rules Loaded**
- rules/999-test-core.md (foundation) — 470 lines
"""
    out = parse_reads_performed_section(text)
    assert "rules/999-test-core.md" in out
    assert "rules/100-snowflake-core.md" in out


@pytest.mark.unit
def test_extract_citations_basic() -> None:
    """Line-count citations are extracted."""
    text = """
**Rules Loaded**
- rules/999-test-core.md (foundation) — 470 lines
- rules/100-snowflake-core.md (keyword: Snowflake) — 200 lines
"""
    out = extract_citations(text, "Rules Loaded")
    assert out["rules/999-test-core.md"] == Citation(line_count=470)
    assert out["rules/100-snowflake-core.md"] == Citation(line_count=200)


@pytest.mark.unit
def test_extract_citations_failed_marker() -> None:
    """``FAILED: not found`` lines yield Citation(failed=True)."""
    text = """
## Reads Performed
- read_file("rules/999-test-core.md") -> RuleVersion v3.7.0, LastUpdated 2026-05-14, lines 470
- read_file("rules/200-python-core.md") -> FAILED: not found
"""
    out = extract_citations(text, "Reads Performed")
    assert out["rules/200-python-core.md"].failed is True
    assert out["rules/999-test-core.md"].failed is False


@pytest.mark.unit
def test_extract_citations_reads_performed_form() -> None:
    """Reads Performed line form ``lines N`` works too.

    (Legacy backward-compat — ``## Reads Performed`` retired in v3.8.0.)
    """
    text = """
## Reads Performed
- read_file("rules/999-test-core.md") -> lines 470
"""
    out = extract_citations(text, "Reads Performed")
    c = out["rules/999-test-core.md"]
    assert c.line_count == 470


@pytest.mark.unit
def test_extract_citations_failed_marker_rules_loaded() -> None:
    """``FAILED: not found`` lines in ``## Rules Loaded`` yield Citation(failed=True)."""
    text = (
        "**Bootstrap:** rule-loader [scanned: (sql) — 1 rules loaded, 1 failed.\n\n"
        "## Rules Loaded\n"
        "- rules/999-test-core.md (foundation) — 601 lines\n"
        "- rules/200-python-core.md — FAILED: not found\n"
    )
    out = extract_citations(text, "Rules Loaded")
    assert out["rules/200-python-core.md"].failed is True
    assert out["rules/999-test-core.md"].failed is False


@pytest.mark.unit
def test_format_timing_lines_renders_event_table() -> None:
    """``format_timing_lines`` renders an ``AgentRun`` event list deterministically."""
    from ai_rules.rule_loader_eval.agent_runner import AgentRun, TurnEvent
    from ai_rules.rule_loader_eval.diagnostics import format_timing_lines

    run = AgentRun(
        fixture_id="candidate",
        loaded=(),
        loaded_via_reads=(),
        loaded_via_reads_performed=(),
        loaded_via_section=(),
        turns=3,
        duration_ms=12_345,
        model="auto",
        events=(
            TurnEvent(t_ms=120, kind="tool_use", detail="Skill skill_name=rule-loader"),
            TurnEvent(t_ms=2_400, kind="tool_use", detail="Read file_path=rules/999-test-core.md"),
            TurnEvent(
                t_ms=11_900,
                kind="assistant_text",
                detail="len=512 head='**Bootstrap:** rule-loader [scanned: (python)'",
            ),
            TurnEvent(t_ms=12_345, kind="result", detail="stop_reason=end_turn turns=3"),
        ),
    )
    lines = format_timing_lines(run, effort="low", model="auto")
    assert lines[0] == "--- diagnostics timing ---"
    assert lines[1] == "total: 12_345 ms across 3 turns (model=auto effort=low)"
    assert lines[2].lstrip().startswith("0 ms")
    assert "[start]" in lines[2]
    assert "Skill skill_name=rule-loader" in lines[3]
    assert "Read file_path=rules/999-test-core.md" in lines[4]
    assert "assistant_text" in lines[5]
    assert "result" in lines[6]
    assert "stop_reason=end_turn" in lines[6]
    assert lines[-1] == "--- end diagnostics timing ---"


# ---------------------------------------------------------------------------
# v3.8 contract compatibility (Phase 0)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_parse_bootstrap_line_counts_loaded_and_failed() -> None:
    """``parse_bootstrap_line`` extracts n_loaded and n_failed from a v3.8 line."""
    text = (
        "**Bootstrap:** rule-loader [scanned: (plan, batch, python) "
        "— 3 rules loaded, 0 failed.\n\n**Rules Loaded**\n"
    )
    result = parse_bootstrap_line(text)
    assert result["found"] is True
    assert result["n_loaded"] == 3
    assert result["n_failed"] == 0


@pytest.mark.unit
def test_parse_bootstrap_line_with_failures() -> None:
    """``parse_bootstrap_line`` captures failure count correctly."""
    text = "**Bootstrap:** rule-loader [scanned: (sql) — 2 rules loaded, 1 failed.\n"
    result = parse_bootstrap_line(text)
    assert result["found"] is True
    assert result["n_loaded"] == 2
    assert result["n_failed"] == 1


@pytest.mark.unit
def test_parse_bootstrap_line_absent() -> None:
    """When no ``**Bootstrap:**`` line is present, ``found`` is False."""
    text = "**Rules Loaded**\n- rules/999-test-core.md\n"
    result = parse_bootstrap_line(text)
    assert result["found"] is False
    assert result["n_loaded"] == 0
    assert result["n_failed"] == 0


@pytest.mark.unit
def test_rules_loaded_remains_authoritative_without_reads_performed() -> None:
    """v3.9 ## Rules Loaded heading format yields correct loaded set."""
    text = (
        "**Bootstrap:** rule-loader [scanned: (python, test) — 2 rules loaded, 0 failed.\n\n"
        "## Rules Loaded\n"
        "- rules/999-test-core.md (foundation) — 601 lines\n"
        "- rules/200-python-core.md (keyword: python) — 454 lines\n\n"
        "Task Switch: FIRST\n"
    )
    loaded = parse_rules_loaded_section(text)
    assert loaded == ("rules/200-python-core.md", "rules/999-test-core.md")
    reads_performed = parse_reads_performed_section(text)
    assert reads_performed == ()


@pytest.mark.unit
def test_citation_drift_uses_rules_loaded_citations() -> None:
    """Citations are extracted from ``**Rules Loaded**`` in v3.9-patch output."""
    text = (
        "**Bootstrap:** rule-loader [scanned: (python) — 1 rules loaded, 0 failed.\n\n"
        "**Rules Loaded**\n"
        "- rules/999-test-core.md (foundation) — 601 lines\n"
    )
    citations = extract_citations(text, "Rules Loaded")
    c = citations["rules/999-test-core.md"]
    assert c.line_count == 601


# ---------------------------------------------------------------------------
# Additional branch coverage for agent_runner.py non-live functions
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_parse_reads_performed_section_with_heading_in_section() -> None:
    """parse_reads_performed_section stops at the next heading inside the section."""
    text = (
        "## Reads Performed\n"
        "- rules/100-snowflake-core.md (loaded)\n"
        "## Next Section\n"
        "- rules/200-python-core.md (should be ignored)\n"
    )
    result = parse_reads_performed_section(text)
    assert "rules/100-snowflake-core.md" in result
    assert "rules/200-python-core.md" not in result


@pytest.mark.unit
def test_parse_reads_performed_section_nonempty_text() -> None:
    """parse_reads_performed_section with non-empty text containing section returns paths."""
    text = "Some preamble.\n## Reads Performed\n- rules/999-test-core.md (loaded)\n"
    result = parse_reads_performed_section(text)
    assert "rules/999-test-core.md" in result


@pytest.mark.unit
def test_parse_bootstrap_line_found_returns_counts() -> None:
    """parse_bootstrap_line extracts n_loaded and n_failed from the Bootstrap line."""
    text = "**Bootstrap:** 3 rules loaded, 1 failed\n"
    result = parse_bootstrap_line(text)
    assert result["found"] is True
    assert result["n_loaded"] == 3
    assert result["n_failed"] == 1


@pytest.mark.unit
def test_validate_output_shape_empty_text() -> None:
    """validate_output_shape returns a single 'empty' violation for empty text."""
    from ai_rules.rule_loader_eval.agent_runner import validate_output_shape

    result = validate_output_shape("", loaded_count=0)
    assert len(result) == 1
    assert "empty" in result[0]


@pytest.mark.unit
def test_extract_citations_empty_text_returns_empty() -> None:
    """extract_citations returns {} when text is empty."""
    result = extract_citations("", "Rules Loaded")
    assert result == {}


@pytest.mark.unit
def test_extract_citations_section_broken_by_heading() -> None:
    """extract_citations stops collecting when it hits a heading inside the section."""
    text = (
        "**Rules Loaded**\n"
        "- rules/100-snowflake-core.md (loaded)\n"
        "## Another Heading\n"
        "- rules/200-python-core.md (should be ignored)\n"
    )
    result = extract_citations(text, "Rules Loaded")
    assert "rules/100-snowflake-core.md" in result
    assert "rules/200-python-core.md" not in result


@pytest.mark.unit
def test_extract_citations_line_without_rule_path_skipped() -> None:
    """Lines in the section with no rule paths are skipped gracefully."""
    text = "**Rules Loaded**\n- (no rule path here)\n- rules/100-snowflake-core.md (loaded)\n"
    result = extract_citations(text, "Rules Loaded")
    # Only the actual rule path should appear
    assert "rules/100-snowflake-core.md" in result


@pytest.mark.unit
def test_extract_citations_path_without_line_count() -> None:
    """A rule path with no line count creates a Citation with line_count=None."""
    text = "**Rules Loaded**\n- rules/100-snowflake-core.md (loaded)\n"
    result = extract_citations(text, "Rules Loaded")
    c = result["rules/100-snowflake-core.md"]
    assert c.line_count is None
    assert not c.failed


@pytest.mark.unit
def test_extract_citations_non_rules_loaded_heading() -> None:
    """extract_citations works with a custom (non-Rules-Loaded) heading."""
    text = "## Reads Performed\n- rules/100-snowflake-core.md (loaded)\n"
    result = extract_citations(text, "Reads Performed")
    assert "rules/100-snowflake-core.md" in result


@pytest.mark.unit
def test_normalize_to_repo_rule_non_relative_path_returns_none() -> None:
    """_normalize_to_repo_rule returns None when path is outside project_root."""
    from pathlib import Path

    from ai_rules.rule_loader_eval.agent_runner import _normalize_to_repo_rule

    result = _normalize_to_repo_rule(
        "/some/completely/other/path/rules/test.md", Path("/my/project")
    )
    assert result is None


@pytest.mark.unit
def test_normalize_to_repo_rule_non_rules_path_returns_none(tmp_path) -> None:
    """_normalize_to_repo_rule returns None for paths not in rules/*.md."""
    from ai_rules.rule_loader_eval.agent_runner import _normalize_to_repo_rule

    # Path is under project_root but not in rules/
    non_rules = tmp_path / "src" / "something.py"
    non_rules.parent.mkdir(parents=True)
    non_rules.touch()
    result = _normalize_to_repo_rule(str(non_rules), tmp_path)
    assert result is None


@pytest.mark.unit
def test_normalize_to_repo_rule_valid_rules_path(tmp_path) -> None:
    """_normalize_to_repo_rule returns relative path for a rules/*.md file."""
    from ai_rules.rule_loader_eval.agent_runner import _normalize_to_repo_rule

    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    rule_file = rules_dir / "100-snowflake-core.md"
    rule_file.touch()
    result = _normalize_to_repo_rule(str(rule_file), tmp_path)
    assert result == "rules/100-snowflake-core.md"


# --- Gate 3 tests ---


@pytest.mark.unit
def test_parse_rules_loaded_section_reads_gate3_subbullets() -> None:
    """Gate 3 sub-bullets are parsed into sorted unique rule paths."""
    text = """\
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — 263 lines
- [x] Gate 2: Searched: python
- [x] Gate 3: Rules loaded:
  - rules/000-global-core.md (foundation) — 263 lines
  - rules/200-python-core.md (ext: .py) — 453 lines

Task Switch: FIRST
"""
    result = parse_rules_loaded_section(text)
    assert result == ("rules/000-global-core.md", "rules/200-python-core.md")


@pytest.mark.unit
def test_parse_rules_loaded_section_gate3_terminates_on_task_switch() -> None:
    """Rule paths after Task Switch: are not included."""
    text = """\
- [x] Gate 3: Rules loaded:
  - rules/000-global-core.md (foundation) — 263 lines

Task Switch: FIRST
- rules/999-should-not-appear.md
"""
    result = parse_rules_loaded_section(text)
    assert "rules/999-should-not-appear.md" not in result
    assert "rules/000-global-core.md" in result


@pytest.mark.unit
def test_extract_citations_gate3_line_counts() -> None:
    """— N lines values are parsed from Gate 3 sub-bullets."""
    text = """\
- [x] Gate 3: Rules loaded:
  - rules/000-global-core.md (foundation) — 263 lines
  - rules/200-python-core.md (ext: .py) — 453 lines

Task Switch: FIRST
"""
    out = extract_citations(text, "Rules Loaded")
    assert out["rules/000-global-core.md"] == Citation(line_count=263)
    assert out["rules/200-python-core.md"] == Citation(line_count=453)


@pytest.mark.unit
def test_extract_citations_gate3_failed_line() -> None:
    """FAILED: not found sub-bullet yields Citation(failed=True)."""
    text = """\
- [x] Gate 3: Rules loaded:
  - rules/000-global-core.md (foundation) — 263 lines
  - rules/999-missing.md FAILED: not found

Task Switch: FIRST
"""
    out = extract_citations(text, "Rules Loaded")
    assert out["rules/999-missing.md"] == Citation(failed=True)
    assert out["rules/000-global-core.md"] == Citation(line_count=263)


@pytest.mark.unit
def test_parse_rules_loaded_section_still_reads_legacy_heading() -> None:
    """Legacy ## Rules Loaded heading remains accepted (C1 regression guard)."""
    text = """\
## Rules Loaded
- rules/000-global-core.md (foundation) — 263 lines
- rules/200-python-core.md (ext: .py) — 453 lines

Task Switch: FIRST
"""
    result = parse_rules_loaded_section(text)
    assert result == ("rules/000-global-core.md", "rules/200-python-core.md")


@pytest.mark.unit
def test_gate3_anchor_rejects_incidental_prose_without_checkbox() -> None:
    """A prose line containing 'Gate 3:' without checkbox anchor does not start the rules section."""
    text = """\
Step Gate 3: Compare against current production version
- rules/999-should-not-appear.md

## Rules Loaded
- rules/000-global-core.md (foundation) — 263 lines
"""
    result = parse_rules_loaded_section(text)
    assert "rules/999-should-not-appear.md" not in result
    assert "rules/000-global-core.md" in result


# ---------------------------------------------------------------------------
# New Gate-1-only shape tests (added 2026-07-10)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_extract_citations_reads_gate1_foundation() -> None:
    """Gate 1 foundation citation is captured when foundation is NOT in Gate 3."""
    text = """\
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — 268 lines
- [x] Gate 2: Searched: python
- [x] Gate 3: +1 domain rule:
  - rules/200-python-core.md (file extension: .py) — 453 lines

Task Switch: FIRST
"""
    out = extract_citations(text, "Rules Loaded")
    assert out["rules/000-global-core.md"] == Citation(line_count=268)
    assert out["rules/200-python-core.md"] == Citation(line_count=453)


@pytest.mark.unit
def test_extract_citations_reads_gate1_foundation_no_line_count() -> None:
    """Gate 1 foundation citation without line count yields Citation() with line_count=None."""
    text = """\
- [x] Gate 1: Foundation rules/000-global-core.md loaded
- [x] Gate 3: none matched

Task Switch: FIRST
"""
    out = extract_citations(text, "Rules Loaded")
    assert "rules/000-global-core.md" in out
    assert out["rules/000-global-core.md"].line_count is None


@pytest.mark.unit
def test_extract_citations_gate1_prose_not_matched() -> None:
    """Prose line mentioning Gate 1 without checkbox prefix does not mis-capture a citation."""
    text = """\
Step Gate 1: Foundation rules/999-test-core.md should not appear
- [x] Gate 3: none matched

Task Switch: FIRST
"""
    out = extract_citations(text, "Rules Loaded")
    assert "rules/999-test-core.md" not in out


@pytest.mark.unit
def test_parse_rules_loaded_section_gate1_only_returns_domain_only() -> None:
    """New Gate-1-only shape: Gate 3 sub-bullets include domain rules but NOT the foundation."""
    text = """\
- [x] Gate 1: Foundation rules/000-global-core.md — 268 lines
- [x] Gate 3: +1 domain rule:
  - rules/200-python-core.md (file extension: .py) — 453 lines

Task Switch: FIRST
"""
    result = parse_rules_loaded_section(text)
    assert "rules/200-python-core.md" in result
    # Foundation is on Gate 1, not in Gate 3 sub-bullets, so parse_rules_loaded returns domain only
    assert "rules/000-global-core.md" not in result


@pytest.mark.unit
def test_no_rules_re_accepts_gate3_none_matched() -> None:
    """New sentinel 'Gate 3: none matched' is matched by _NO_RULES_RE."""
    from ai_rules.rule_loader_eval.agent_runner import _NO_RULES_RE

    assert _NO_RULES_RE.search("- [x] Gate 3: none matched")
    assert _NO_RULES_RE.search("- [x] Gate 3: none matched\n")
    # Legacy form still accepted
    assert _NO_RULES_RE.search("(none — no domain rules matched)")
    assert _NO_RULES_RE.search("(none - no domain rules matched)")
    # Must NOT match unrelated text
    assert not _NO_RULES_RE.search("Gate 3: +1 domain rule:")
    assert not _NO_RULES_RE.search("rules/200-python-core.md")


@pytest.mark.unit
def test_no_ln_shorthand_not_present_in_canonical_artifacts() -> None:
    """Negative guard: templates, rules, docs, and AGENTS.md must not use the shorthand
    '— N ln' (only '— N lines' is accepted by the citation-drift checker).
    """
    import pathlib
    import re as _re

    root = pathlib.Path(__file__).parents[3]
    patterns = _re.compile(r"—\s*\d+\s+ln\b|—\s*N\s+ln\b")
    hits: list[str] = []
    for glob in [
        "templates/*.template",
        "rules/*.md",
        "docs/*.md",
        "AGENTS.md",
    ]:
        for path in root.glob(glob):
            for lineno, line in enumerate(path.read_text().splitlines(), 1):
                if patterns.search(line):
                    hits.append(f"{path.relative_to(root)}:{lineno}: {line.strip()}")
    assert hits == [], "Found '— N ln' shorthand in canonical artifacts:\n" + "\n".join(hits)
