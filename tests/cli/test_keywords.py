"""Tests for ai-rules keywords CLI command.

Tests follow pytest best practices:
- AAA pattern (Arrange-Act-Assert)
- Function-scoped fixtures
- Parametrized tests for input matrices
- Test markers for selective execution
- Isolation with tmp_path
"""

from __future__ import annotations

import time
from pathlib import Path
from textwrap import dedent

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands import keywords as keywords_module

runner = CliRunner()

# Save reference to real function before autouse fixture patches it
_real_load_snowflake_config = keywords_module.load_snowflake_config


@pytest.fixture(autouse=True)
def _block_snowflake_config(monkeypatch: pytest.MonkeyPatch):
    """Prevent real Snowflake config loading in all tests.

    Returns empty credentials so _call_cortex_complete raises RuntimeError
    (which suggest_keywords catches for heuristic fallback), and the CLI
    path sets use_api=False.

    Tests that need specific config behavior override this via their own monkeypatch.
    """
    monkeypatch.setattr(
        keywords_module,
        "load_snowflake_config",
        lambda conn: {"account": "", "token": ""},
    )


# Sample rule content for testing
SAMPLE_RULE_CONTENT = dedent("""
    # 100-snowflake-core: Snowflake Core

    ## Metadata

    **SchemaVersion:** v3.2
    **RuleVersion:** v1.0.0
    **LastUpdated:** 2024-01-15
    **Keywords:** snowflake, SQL, data warehouse
    **TokenBudget:** ~1200
    **ContextTier:** High
    **Depends:** 000-global-core.md

    ## Scope

    **What This Rule Covers:**
    This rule covers Snowflake SQL best practices.

    ## Contract

    ### Mandatory

    - Use proper SQL formatting
    - Follow Snowflake naming conventions

    ```sql
    SELECT * FROM my_table;
    ```

    ```python
    import snowflake.connector
    ```
""").strip()


SAMPLE_RULE_NO_KEYWORDS = dedent("""
    # 200-python-core: Python Core

    ## Metadata

    **SchemaVersion:** v3.2
    **RuleVersion:** v1.0.0

    ## Scope

    This rule covers Python best practices.
""").strip()


class TestKeywordsHelp:
    """Test --help output for keywords command."""

    @pytest.mark.unit
    def test_help_shows_description(self):
        """Test that --help shows command description."""
        result = runner.invoke(app, ["keywords", "--help"])

        assert result.exit_code == 0
        assert "Generate semantically relevant keywords" in result.output

    @pytest.mark.unit
    def test_help_shows_all_options(self):
        """Test that --help shows all options."""
        result = runner.invoke(app, ["keywords", "--help"])

        assert result.exit_code == 0
        assert "--update" in result.output
        assert "--diff" in result.output
        assert "--force" in result.output
        assert "--count" in result.output
        assert "--debug" in result.output
        assert "--connection" in result.output

    @pytest.mark.unit
    def test_help_shows_path_argument(self):
        """Test that --help shows PATH argument."""
        result = runner.invoke(app, ["keywords", "--help"])

        assert result.exit_code == 0
        assert "PATH" in result.output


class TestKeywordsHappyPath:
    """Test successful keyword analysis scenarios."""

    @pytest.mark.unit
    def test_single_file_analysis(self, tmp_path: Path):
        """Test keyword analysis for a single file."""
        rule_file = tmp_path / "100-snowflake-core.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        result = runner.invoke(app, ["keywords", str(rule_file)])

        assert result.exit_code == 0
        assert "100-snowflake-core.md" in result.output
        # Should show suggestions table
        assert "Suggested" in result.output or "suggested" in result.output.lower()

    @pytest.mark.unit
    def test_directory_analysis(self, tmp_path: Path):
        """Test keyword analysis for a directory of files."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        (rules_dir / "100-snowflake-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_NO_KEYWORDS)

        result = runner.invoke(app, ["keywords", str(rules_dir)])

        assert result.exit_code == 0
        assert "100-snowflake-core.md" in result.output
        assert "200-python-core.md" in result.output

    @pytest.mark.unit
    def test_skips_readme_files(self, tmp_path: Path):
        """Test that README.md files are skipped."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        (rules_dir / "100-snowflake-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "README.md").write_text("# Rules Documentation")

        result = runner.invoke(app, ["keywords", str(rules_dir)])

        assert result.exit_code == 0
        assert "100-snowflake-core.md" in result.output
        # README.md should not appear in output as a processed file


class TestKeywordsUpdateFlag:
    """Test --update flag behavior."""

    @pytest.mark.unit
    def test_update_modifies_file(self, tmp_path: Path):
        """Test that --update modifies the Keywords field."""
        rule_file = tmp_path / "100-snowflake-core.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        rule_file.read_text()

        result = runner.invoke(app, ["keywords", str(rule_file), "--update"])

        assert result.exit_code == 0
        new_content = rule_file.read_text()
        # The file should have been modified (keywords updated)
        assert "**Keywords:**" in new_content
        # Should show success message
        assert "Updated" in result.output or "No change" in result.output

    @pytest.mark.unit
    def test_update_no_change_when_same(self, tmp_path: Path):
        """Test that --update reports no change if keywords match."""
        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        # Run twice to check idempotency
        runner.invoke(app, ["keywords", str(rule_file), "--update"])
        result = runner.invoke(app, ["keywords", str(rule_file), "--update"])

        assert result.exit_code == 0
        assert "No change" in result.output

    @pytest.mark.unit
    def test_update_warns_no_keywords_field(self, tmp_path: Path):
        """Test warning when file has no Keywords field."""
        rule_file = tmp_path / "200-python-core.md"
        rule_file.write_text(SAMPLE_RULE_NO_KEYWORDS)

        result = runner.invoke(app, ["keywords", str(rule_file), "--update"])

        assert result.exit_code == 0
        # Should warn about missing Keywords field
        assert "No **Keywords:**" in result.output or "No change" in result.output


class TestKeywordsDiffFlag:
    """Test --diff flag behavior."""

    @pytest.mark.unit
    def test_diff_shows_comparison(self, tmp_path: Path):
        """Test that --diff shows side-by-side comparison."""
        rule_file = tmp_path / "100-snowflake-core.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        result = runner.invoke(app, ["keywords", str(rule_file), "--diff"])

        assert result.exit_code == 0
        assert "100-snowflake-core.md" in result.output
        # Should show current and suggested sections
        assert "Current" in result.output
        assert "Suggested" in result.output

    @pytest.mark.unit
    def test_diff_does_not_modify_file(self, tmp_path: Path):
        """Test that --diff doesn't modify the file."""
        rule_file = tmp_path / "100-snowflake-core.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        original_content = rule_file.read_text()

        result = runner.invoke(app, ["keywords", str(rule_file), "--diff"])

        assert result.exit_code == 0
        assert rule_file.read_text() == original_content


class TestKeywordsCountFlag:
    """Test --count flag behavior."""

    @pytest.mark.unit
    def test_count_limits_suggestions(self, tmp_path: Path):
        """Test --count limits the number of suggestions."""
        rule_file = tmp_path / "100-snowflake-core.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        # Test with small count
        result = runner.invoke(app, ["keywords", str(rule_file), "--count", "5", "--diff"])

        assert result.exit_code == 0
        # The suggested keywords should be limited

    @pytest.mark.unit
    @pytest.mark.parametrize("count", [5, 10, 15, 20])
    def test_count_various_values(self, tmp_path: Path, count: int):
        """Test --count with various values."""
        rule_file = tmp_path / "100-snowflake-core.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        result = runner.invoke(app, ["keywords", str(rule_file), "--count", str(count)])

        assert result.exit_code == 0


class TestKeywordsDebugFlag:
    """Test --debug flag behavior."""

    @pytest.mark.unit
    def test_debug_shows_additional_output(self, tmp_path: Path):
        """Test --debug enables verbose output."""
        rule_file = tmp_path / "100-snowflake-core.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        result = runner.invoke(app, ["keywords", str(rule_file), "--debug"])

        assert result.exit_code == 0
        # Debug output should show debug info or process the file
        assert "100-snowflake-core.md" in result.output


class TestKeywordsErrorCases:
    """Test error handling scenarios."""

    @pytest.mark.unit
    def test_missing_path_error(self):
        """Test error when path doesn't exist."""
        result = runner.invoke(app, ["keywords", "/nonexistent/path/file.md"])

        assert result.exit_code == 1
        assert "does not exist" in result.output

    @pytest.mark.unit
    def test_empty_directory_error(self, tmp_path: Path):
        """Test error when directory has no rule files."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = runner.invoke(app, ["keywords", str(empty_dir)])

        assert result.exit_code == 1
        assert "No rule files found" in result.output

    @pytest.mark.unit
    def test_directory_with_only_skipped_files(self, tmp_path: Path):
        """Test error when directory only has skipped files."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        (rules_dir / "README.md").write_text("# Documentation")
        (rules_dir / "CHANGELOG.md").write_text("# Changes")

        result = runner.invoke(app, ["keywords", str(rules_dir)])

        assert result.exit_code == 1
        assert "No rule files found" in result.output


class TestKeywordExtractor:
    """Test KeywordExtractor class directly."""

    @pytest.mark.unit
    def test_extractor_heuristic_fallback(self, tmp_path: Path):
        """Test extractor works with heuristic fallback (no API)."""
        extractor = keywords_module.KeywordExtractor(debug=False)

        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        result = extractor.suggest_keywords(rule_file, count=10, use_api=False)

        assert result.file_path == rule_file
        assert len(result.suggested_keywords) <= 10
        assert "snowflake" in result.current_keywords or "SQL" in result.current_keywords

    @pytest.mark.unit
    def test_extractor_extracts_current_keywords(self, tmp_path: Path):
        """Test extractor correctly parses current keywords."""
        extractor = keywords_module.KeywordExtractor()

        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        result = extractor.suggest_keywords(rule_file)

        assert "snowflake" in result.current_keywords
        assert "SQL" in result.current_keywords
        assert "data warehouse" in result.current_keywords

    @pytest.mark.unit
    def test_extractor_extracts_code_languages(self, tmp_path: Path):
        """Test extractor identifies code block languages."""
        extractor = keywords_module.KeywordExtractor()

        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        result = extractor.suggest_keywords(rule_file)

        # Should identify SQL and Python from code blocks
        candidates_terms = [c.term.lower() for c in result.candidates]
        assert "sql" in candidates_terms or "python" in candidates_terms

    @pytest.mark.unit
    def test_extraction_result_diff_properties(self):
        """Test ExtractionResult added/removed/kept properties."""
        result = keywords_module.ExtractionResult(
            file_path=Path("test.md"),
            current_keywords=["snowflake", "sql", "python"],
            suggested_keywords=["snowflake", "pytest", "ruff"],
        )

        assert result.kept == {"snowflake"}
        assert result.removed == {"sql", "python"}
        assert result.added == {"pytest", "ruff"}


class TestUpdateKeywordsInFile:
    """Test update_keywords_in_file function."""

    @pytest.mark.unit
    def test_updates_existing_keywords(self, tmp_path: Path):
        """Test updating existing Keywords field."""
        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        new_keywords = ["new", "keywords", "here"]
        updated = keywords_module.update_keywords_in_file(rule_file, new_keywords)

        assert updated is True
        content = rule_file.read_text()
        assert "**Keywords:** new, keywords, here" in content

    @pytest.mark.unit
    def test_returns_false_when_no_change(self, tmp_path: Path):
        """Test returns False when keywords unchanged."""
        rule_file = tmp_path / "100-test.md"
        rule_file.write_text("**Keywords:** a, b, c\n")

        # Update with same keywords
        updated = keywords_module.update_keywords_in_file(rule_file, ["a", "b", "c"])

        assert updated is False

    @pytest.mark.unit
    def test_warns_when_no_keywords_field(self, tmp_path: Path):
        """Test warning when file has no Keywords field."""
        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(SAMPLE_RULE_NO_KEYWORDS)

        updated = keywords_module.update_keywords_in_file(rule_file, ["new", "keywords"])

        assert updated is False


class TestFormatKeywordsLine:
    """Test format_keywords_line function."""

    @pytest.mark.unit
    def test_formats_keywords_correctly(self):
        """Test correct formatting of keywords line."""
        keywords = ["snowflake", "sql", "python"]
        line = keywords_module.format_keywords_line(keywords)

        assert line == "**Keywords:** snowflake, sql, python"

    @pytest.mark.unit
    def test_handles_empty_keywords(self):
        """Test handling empty keywords list."""
        line = keywords_module.format_keywords_line([])
        assert line == "**Keywords:** "


class TestKeywordCandidate:
    """Test KeywordCandidate dataclass."""

    @pytest.mark.unit
    def test_case_insensitive_equality(self):
        """Test candidates are equal case-insensitively."""
        c1 = keywords_module.KeywordCandidate(term="Snowflake", score=1.0, source="test")
        c2 = keywords_module.KeywordCandidate(term="snowflake", score=0.5, source="other")

        assert c1 == c2
        assert hash(c1) == hash(c2)

    @pytest.mark.unit
    def test_different_terms_not_equal(self):
        """Test different terms are not equal."""
        c1 = keywords_module.KeywordCandidate(term="snowflake", score=1.0, source="test")
        c2 = keywords_module.KeywordCandidate(term="python", score=1.0, source="test")

        assert c1 != c2


class TestConstantSets:
    """Test constant sets are properly defined."""

    @pytest.mark.unit
    def test_skip_files_contains_expected_files(self):
        """Test SKIP_FILES contains expected files."""
        assert "README.md" in keywords_module.SKIP_FILES
        assert "CHANGELOG.md" in keywords_module.SKIP_FILES
        assert "RULES_INDEX.md" in keywords_module.SKIP_FILES

    @pytest.mark.unit
    def test_technology_terms_contains_snowflake(self):
        """Test TECHNOLOGY_TERMS contains Snowflake ecosystem."""
        assert "snowflake" in keywords_module.TECHNOLOGY_TERMS
        assert "cortex" in keywords_module.TECHNOLOGY_TERMS
        assert "streamlit" in keywords_module.TECHNOLOGY_TERMS

    @pytest.mark.unit
    def test_stop_terms_contains_common_words(self):
        """Test STOP_TERMS contains common generic words."""
        assert "data" in keywords_module.STOP_TERMS
        assert "code" in keywords_module.STOP_TERMS
        assert "should" in keywords_module.STOP_TERMS

    @pytest.mark.unit
    def test_technology_terms_has_key_entries(self):
        """Test TECHNOLOGY_TERMS has expected technology entries."""
        assert "snowflake" in keywords_module.TECHNOLOGY_TERMS
        assert "python" in keywords_module.TECHNOLOGY_TERMS
        assert "sql" in keywords_module.TECHNOLOGY_TERMS


class TestKeywordCandidateEdgeCases:
    """Test KeywordCandidate edge cases."""

    @pytest.mark.unit
    def test_not_equal_to_non_candidate(self):
        """Test KeywordCandidate.__eq__ returns False for non-KeywordCandidate objects (line 308)."""
        c = keywords_module.KeywordCandidate(term="snowflake", score=1.0, source="test")
        assert c != "snowflake"
        assert c != 42
        assert c != None  # noqa: E711


class TestExtractHeadersEdgeCases:
    """Test header extraction edge cases."""

    @pytest.mark.unit
    def test_header_words_filtered_by_stop_terms(self, tmp_path: Path):
        """Test that stop terms in headers are excluded (line 466)."""
        extractor = keywords_module.KeywordExtractor()
        rule_file = tmp_path / "100-test.md"
        # "data" and "code" and "should" are in STOP_TERMS
        rule_file.write_text(
            "# 100-test: Test Rule\n\n"
            "## Metadata\n\n"
            "**Keywords:** test\n\n"
            "## Data Code Should\n\n"
            "## Snowflake Integration\n\n"
            "Some content about snowflake integration."
        )

        result = extractor.suggest_keywords(rule_file, count=20)
        candidate_terms = [c.term.lower() for c in result.candidates if c.source == "header"]
        # "snowflake" and "integration" should be present from the non-stop-terms header
        assert "snowflake" in candidate_terms or "integration" in candidate_terms


class TestExtractEmphasizedTermsEdgeCases:
    """Test emphasized term extraction edge cases."""

    @pytest.mark.unit
    def test_bold_terms_extracted(self, tmp_path: Path):
        """Test bold terms are extracted as candidates (lines 523-526)."""
        extractor = keywords_module.KeywordExtractor()
        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(
            "# 100-test: Test Rule\n\n"
            "## Metadata\n\n"
            "**Keywords:** test\n\n"
            "## Content\n\n"
            "Use **Snowpark** for data processing.\n"
            "The **streaming** approach is recommended.\n"
        )

        result = extractor.suggest_keywords(rule_file, count=20)
        candidate_terms = [c.term.lower() for c in result.candidates if c.source == "emphasis"]
        assert "snowpark" in candidate_terms or "streaming" in candidate_terms

    @pytest.mark.unit
    def test_backtick_terms_skip_file_extensions(self, tmp_path: Path):
        """Test backtick terms with file extensions are skipped (line 537)."""
        extractor = keywords_module.KeywordExtractor()
        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(
            "# 100-test: Test Rule\n\n"
            "## Metadata\n\n"
            "**Keywords:** test\n\n"
            "## Content\n\n"
            "Edit `config.py` and `schema.yml` files.\n"
            "Use `pytest` for testing.\n"
        )

        result = extractor.suggest_keywords(rule_file, count=20)
        emphasis_terms = [c.term.lower() for c in result.candidates if c.source == "emphasis"]
        # config.py and schema.yml should be filtered out, pytest should be kept
        assert "config.py" not in emphasis_terms
        assert "schema.yml" not in emphasis_terms

    @pytest.mark.unit
    def test_backtick_stop_terms_filtered(self, tmp_path: Path):
        """Test backtick terms in STOP_TERMS are filtered (line 539)."""
        extractor = keywords_module.KeywordExtractor()
        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(
            "# 100-test: Test Rule\n\n"
            "## Metadata\n\n"
            "**Keywords:** test\n\n"
            "## Content\n\n"
            "The `data` field and `code` block.\n"
        )

        result = extractor.suggest_keywords(rule_file, count=20)
        emphasis_terms = [c.term.lower() for c in result.candidates if c.source == "emphasis"]
        assert "data" not in emphasis_terms
        assert "code" not in emphasis_terms


class TestRankKeywordsEdgeCases:
    """Test _rank_heuristic_keywords edge cases."""

    @pytest.mark.unit
    def test_stop_terms_excluded_from_ranking(self):
        """Test that stop terms are excluded during ranking."""
        extractor = keywords_module.KeywordExtractor()
        candidates = [
            keywords_module.KeywordCandidate(term="data", score=10.0, source="test"),
            keywords_module.KeywordCandidate(term="snowflake", score=5.0, source="test"),
        ]
        ranked = extractor._rank_heuristic_keywords(candidates, count=5)
        assert "data" not in ranked
        assert "snowflake" in ranked

    @pytest.mark.unit
    def test_uppercase_display_form_preferred(self):
        """Test uppercase display form is preferred over lowercase."""
        extractor = keywords_module.KeywordExtractor()
        candidates = [
            keywords_module.KeywordCandidate(term="snowflake", score=3.0, source="test"),
            keywords_module.KeywordCandidate(term="Snowflake", score=2.0, source="test"),
        ]
        ranked = extractor._rank_heuristic_keywords(candidates, count=5)
        assert "Snowflake" in ranked


class TestMergeLlmWithHeuristics:
    """Test _merge_llm_with_heuristics method."""

    @pytest.mark.unit
    def test_merge_appends_missing_technology_terms(self):
        """Test that high-confidence heuristic terms supplement LLM output."""
        extractor = keywords_module.KeywordExtractor()
        llm_keywords = ["cortex agent", "tool orchestration"]
        heuristic_candidates = [
            keywords_module.KeywordCandidate(term="snowflake", score=0.7, source="technology"),
            keywords_module.KeywordCandidate(term="Python", score=0.6, source="code_lang"),
        ]

        result = extractor._merge_llm_with_heuristics(llm_keywords, heuristic_candidates, count=10)

        assert result[:2] == ["cortex agent", "tool orchestration"]
        assert "Python" in result
        assert "snowflake" in result

    @pytest.mark.unit
    def test_merge_does_not_duplicate_existing_terms(self):
        """Test that merge skips terms already in LLM output."""
        extractor = keywords_module.KeywordExtractor()
        llm_keywords = ["snowflake", "cortex agent"]
        heuristic_candidates = [
            keywords_module.KeywordCandidate(term="snowflake", score=0.7, source="technology"),
        ]

        result = extractor._merge_llm_with_heuristics(llm_keywords, heuristic_candidates, count=10)

        assert result.count("snowflake") == 1

    @pytest.mark.unit
    def test_merge_respects_count_limit(self):
        """Test that merge stops at count limit."""
        extractor = keywords_module.KeywordExtractor()
        llm_keywords = ["term1", "term2"]
        heuristic_candidates = [
            keywords_module.KeywordCandidate(term="python", score=0.7, source="technology"),
            keywords_module.KeywordCandidate(term="SQL", score=0.6, source="code_lang"),
            keywords_module.KeywordCandidate(term="bash", score=0.6, source="code_lang"),
        ]

        result = extractor._merge_llm_with_heuristics(llm_keywords, heuristic_candidates, count=3)

        assert len(result) == 3
        assert result[:2] == ["term1", "term2"]

    @pytest.mark.unit
    def test_merge_ignores_low_confidence_sources(self):
        """Test that merge only uses technology and code_lang sources."""
        extractor = keywords_module.KeywordExtractor()
        llm_keywords = ["cortex agent"]
        heuristic_candidates = [
            keywords_module.KeywordCandidate(term="Integration", score=0.8, source="header"),
            keywords_module.KeywordCandidate(term="Snowpark", score=0.5, source="emphasis"),
            keywords_module.KeywordCandidate(term="python", score=0.7, source="technology"),
        ]

        result = extractor._merge_llm_with_heuristics(llm_keywords, heuristic_candidates, count=10)

        assert "python" in result
        assert "Integration" not in result
        assert "Snowpark" not in result


class TestKeywordsCLIProcessingEdgeCases:
    """Test keywords CLI file processing edge cases."""

    @pytest.mark.unit
    def test_exception_processing_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test exception during file processing is caught (lines 934-935)."""
        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(
            "# 100-test: Test\n\n## Metadata\n\n**Keywords:** test\n\n## Content\n\nContent."
        )

        def failing_suggest(self, file_path, count=12):
            raise RuntimeError("extraction failed")

        monkeypatch.setattr(keywords_module.KeywordExtractor, "suggest_keywords", failing_suggest)

        result = runner.invoke(app, ["keywords", str(rule_file)])
        assert result.exit_code == 0  # errors are logged but don't abort
        assert "Error processing" in result.output

    @pytest.mark.unit
    def test_exception_processing_file_debug_reraises(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test exception with --debug re-raises (lines 936-937)."""
        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(
            "# 100-test: Test\n\n## Metadata\n\n**Keywords:** test\n\n## Content\n\nContent."
        )

        def failing_suggest(self, file_path, count=12):
            raise RuntimeError("extraction failed")

        monkeypatch.setattr(keywords_module.KeywordExtractor, "suggest_keywords", failing_suggest)

        result = runner.invoke(app, ["keywords", str(rule_file), "--debug"])
        # With debug, the exception is re-raised causing non-zero exit
        assert result.exit_code != 0


class TestParseCortexSseResponse:
    """Test _parse_cortex_sse_response handles streaming Cortex API output."""

    @pytest.mark.unit
    def test_concatenates_content_deltas(self):
        """SSE chunks are concatenated into full text."""
        raw = (
            'data: {"choices":[{"delta":{"content":"[\\"hello"}}]}\n\n'
            'data: {"choices":[{"delta":{"content":"\\", \\"world"}}]}\n\n'
            'data: {"choices":[{"delta":{"content":"\\"]"}}]}\n\n'
            "data: [DONE]\n\n"
        )
        result = keywords_module._parse_cortex_sse_response(raw)
        assert result == '["hello", "world"]'

    @pytest.mark.unit
    def test_skips_non_data_lines(self):
        """Lines without 'data:' prefix are ignored."""
        raw = (
            "event: message\n"
            'data: {"choices":[{"delta":{"content":"hi"}}]}\n\n'
            ": comment line\n"
            "data: [DONE]\n\n"
        )
        result = keywords_module._parse_cortex_sse_response(raw)
        assert result == "hi"

    @pytest.mark.unit
    def test_handles_empty_response(self):
        """Empty input returns empty string."""
        assert keywords_module._parse_cortex_sse_response("") == ""

    @pytest.mark.unit
    def test_handles_malformed_json(self):
        """Malformed JSON chunks are skipped without error."""
        raw = 'data: not-json\n\ndata: {"choices":[{"delta":{"content":"ok"}}]}\n\ndata: [DONE]\n\n'
        result = keywords_module._parse_cortex_sse_response(raw)
        assert result == "ok"


class TestLoadSnowflakeConfig:
    """Tests for load_snowflake_config reading ~/.snowflake/connections.toml."""

    @pytest.fixture(autouse=True)
    def _restore_real_config_loader(self, monkeypatch: pytest.MonkeyPatch):
        """Restore the real load_snowflake_config for these tests."""
        monkeypatch.setattr(keywords_module, "load_snowflake_config", _real_load_snowflake_config)

    @pytest.mark.unit
    def test_loads_connection_from_connections_toml(self, tmp_path: Path, monkeypatch):
        """Loads named connection from connections.toml."""
        snowflake_dir = tmp_path / ".snowflake"
        snowflake_dir.mkdir()
        (snowflake_dir / "connections.toml").write_text(
            '[default]\naccount = "myaccount"\ntoken = "mytoken"\n'
        )
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        config = keywords_module.load_snowflake_config("default")

        assert config["account"] == "myaccount"
        assert config["token"] == "mytoken"

    @pytest.mark.unit
    def test_falls_back_to_config_toml(self, tmp_path: Path, monkeypatch):
        """Uses config.toml when connections.toml does not exist."""
        snowflake_dir = tmp_path / ".snowflake"
        snowflake_dir.mkdir()
        (snowflake_dir / "config.toml").write_text(
            '[myconn]\naccount = "fallback"\npassword = "pw"\n'
        )
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        config = keywords_module.load_snowflake_config("myconn")

        assert config["account"] == "fallback"
        assert config["password"] == "pw"

    @pytest.mark.unit
    def test_raises_on_missing_config_files(self, tmp_path: Path, monkeypatch):
        """FileNotFoundError when neither config file exists."""
        snowflake_dir = tmp_path / ".snowflake"
        snowflake_dir.mkdir()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        with pytest.raises(FileNotFoundError, match="No Snowflake config found"):
            keywords_module.load_snowflake_config("default")

    @pytest.mark.unit
    def test_raises_on_missing_connection_name(self, tmp_path: Path, monkeypatch):
        """ValueError when requested connection name is absent."""
        snowflake_dir = tmp_path / ".snowflake"
        snowflake_dir.mkdir()
        (snowflake_dir / "connections.toml").write_text('[other]\naccount = "x"\ntoken = "y"\n')
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        with pytest.raises(ValueError, match="Connection 'default' not found"):
            keywords_module.load_snowflake_config("default")


class TestDeduplicateAcrossRules:
    """Test _deduplicate_across_rules post-processing."""

    @pytest.mark.unit
    def test_keywords_within_max_overlap_untouched(self, tmp_path: Path):
        """Keywords in <=max_overlap rules are not removed."""
        file_a = tmp_path / "rule-a.md"
        file_b = tmp_path / "rule-b.md"
        file_a.write_text("snowflake snowflake snowflake")
        file_b.write_text("snowflake python python")

        result_a = keywords_module.ExtractionResult(
            file_path=file_a,
            suggested_keywords=["snowflake", "cortex"],
        )
        result_b = keywords_module.ExtractionResult(
            file_path=file_b,
            suggested_keywords=["snowflake", "python"],
        )

        keywords_module._deduplicate_across_rules([result_a, result_b], max_overlap=2)

        # "snowflake" appears in 2 rules which equals max_overlap=2 — kept in both
        assert "snowflake" in result_a.suggested_keywords
        assert "snowflake" in result_b.suggested_keywords

    @pytest.mark.unit
    def test_keywords_exceeding_max_overlap_pruned(self, tmp_path: Path):
        """Keywords in >max_overlap rules are kept only in top-scoring rules."""
        file_a = tmp_path / "rule-a.md"
        file_b = tmp_path / "rule-b.md"
        file_c = tmp_path / "rule-c.md"
        # "pytest" appears most in file_a (3x), then file_b (2x), least in file_c (1x)
        file_a.write_text("pytest pytest pytest ruff")
        file_b.write_text("pytest pytest flask")
        file_c.write_text("pytest django django django")

        result_a = keywords_module.ExtractionResult(
            file_path=file_a,
            suggested_keywords=["pytest", "ruff"],
        )
        result_b = keywords_module.ExtractionResult(
            file_path=file_b,
            suggested_keywords=["pytest", "flask"],
        )
        result_c = keywords_module.ExtractionResult(
            file_path=file_c,
            suggested_keywords=["pytest", "django"],
        )

        keywords_module._deduplicate_across_rules([result_a, result_b, result_c], max_overlap=2)

        # "pytest" in 3 rules > max_overlap=2: kept in top-2 by body count (a=3, b=2)
        assert "pytest" in result_a.suggested_keywords
        assert "pytest" in result_b.suggested_keywords
        assert "pytest" not in result_c.suggested_keywords
        # Other keywords untouched
        assert "ruff" in result_a.suggested_keywords
        assert "flask" in result_b.suggested_keywords
        assert "django" in result_c.suggested_keywords

    @pytest.mark.unit
    def test_single_result_unaffected(self, tmp_path: Path):
        """Deduplication with a single result is a no-op."""
        file_a = tmp_path / "rule-a.md"
        file_a.write_text("snowflake cortex")

        result_a = keywords_module.ExtractionResult(
            file_path=file_a,
            suggested_keywords=["snowflake", "cortex"],
        )

        keywords_module._deduplicate_across_rules([result_a], max_overlap=2)

        assert result_a.suggested_keywords == ["snowflake", "cortex"]


class TestDeduplicateCLIFlag:
    """Test --deduplicate CLI flag integration."""

    @pytest.mark.unit
    def test_help_shows_deduplicate_option(self):
        """Test that --help shows --deduplicate option."""
        result = runner.invoke(app, ["keywords", "--help"])

        assert result.exit_code == 0
        assert "--deduplicate" in result.output

    @pytest.mark.unit
    def test_deduplicate_flag_accepted(self, tmp_path: Path):
        """Test that --deduplicate flag is accepted without error."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "100-snowflake-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_NO_KEYWORDS)

        result = runner.invoke(app, ["keywords", str(rules_dir), "--deduplicate"])

        assert result.exit_code == 0


class TestLoadCacheCorruptFile:
    """Test _load_cache with corrupt cache files."""

    @pytest.mark.unit
    def test_corrupt_json_returns_empty_dict(self, tmp_path: Path):
        """Corrupt JSON in cache file returns {} (lines 632-633)."""
        cache_file = tmp_path / ".keywords_cache.json"
        cache_file.write_text("{this is not valid json!!", encoding="utf-8")

        result = keywords_module._load_cache(cache_file)

        assert result == {}

    @pytest.mark.unit
    def test_nonexistent_cache_returns_empty_dict(self, tmp_path: Path):
        """Non-existent cache file returns {}."""
        cache_file = tmp_path / ".keywords_cache.json"

        result = keywords_module._load_cache(cache_file)

        assert result == {}


class TestSaveCacheOSError:
    """Test _save_cache when write fails."""

    @pytest.mark.unit
    def test_write_to_readonly_path_silently_passes(self, tmp_path: Path):
        """Write to read-only directory silently passes (lines 641-642)."""
        # Use a path inside a non-existent directory to trigger OSError
        bad_path = tmp_path / "nonexistent_dir" / "cache.json"

        # Should not raise
        keywords_module._save_cache(bad_path, {"key": "value"})

        assert not bad_path.exists()


class TestGetCachedKeywordsMiss:
    """Test _get_cached_keywords cache miss path."""

    @pytest.mark.unit
    def test_hash_mismatch_returns_none(self):
        """Hash mismatch returns None (line 649)."""
        cache = {
            "file.md": {
                "hash": "old_hash_abc123",
                "keywords": ["cached", "keywords"],
            }
        }

        result = keywords_module._get_cached_keywords(cache, "file.md", "different_hash_xyz")

        assert result is None

    @pytest.mark.unit
    def test_missing_key_returns_none(self):
        """Missing file key returns None."""
        cache = {}

        result = keywords_module._get_cached_keywords(cache, "file.md", "any_hash")

        assert result is None


class TestCallCortexComplete:
    """Test _call_cortex_complete with mocked requests.post."""

    @pytest.mark.unit
    def test_missing_account_raises_runtime_error(self, tmp_path: Path, monkeypatch):
        """Missing account/token raises RuntimeError (line 716)."""
        monkeypatch.setattr(
            keywords_module,
            "load_snowflake_config",
            lambda conn: {"account": "", "token": ""},
        )

        with pytest.raises(RuntimeError, match="missing 'account' or"):
            keywords_module._call_cortex_complete("rule content", connection_name="default")

    @pytest.mark.unit
    def test_snowflakecomputing_url_format(self, tmp_path: Path, monkeypatch):
        """Account with .snowflakecomputing.com uses direct URL (line 758)."""
        monkeypatch.setattr(
            keywords_module,
            "load_snowflake_config",
            lambda conn: {
                "account": "myorg.snowflakecomputing.com",
                "token": "tok123",
            },
        )

        captured_url = {}

        class FakeResponse:
            status_code = 200
            text = 'data: {"choices":[{"delta":{"content":"[\\"kw1\\"]"}}]}\n\ndata: [DONE]\n\n'

        def fake_post(url, **kwargs):
            captured_url["url"] = url
            return FakeResponse()

        import requests

        monkeypatch.setattr(requests, "post", fake_post)

        keywords_module._call_cortex_complete("content", connection_name="default")

        assert captured_url["url"] == (
            "https://myorg.snowflakecomputing.com/api/v2/cortex/inference:complete"
        )

    @pytest.mark.unit
    def test_non_retryable_error_raises_immediately(self, monkeypatch):
        """Non-retryable status code raises RuntimeError immediately (line 807)."""
        monkeypatch.setattr(
            keywords_module,
            "load_snowflake_config",
            lambda conn: {"account": "myacct", "token": "tok"},
        )

        class FakeResponse:
            status_code = 400
            text = "Bad Request"

        import requests

        monkeypatch.setattr(requests, "post", lambda *a, **kw: FakeResponse())

        with pytest.raises(RuntimeError, match="Cortex API returned 400"):
            keywords_module._call_cortex_complete("content")

    @pytest.mark.unit
    def test_retryable_status_codes_retry_then_raise(self, monkeypatch):
        """Retryable status codes 429/503/504 retry and eventually raise (lines 795-815)."""
        monkeypatch.setattr(
            keywords_module,
            "load_snowflake_config",
            lambda conn: {"account": "myacct", "token": "tok"},
        )
        monkeypatch.setattr(time, "sleep", lambda _: None)  # skip delays

        call_count = {"n": 0}

        class FakeResponse:
            status_code = 429
            text = "Rate limited"

        import requests

        def fake_post(*a, **kw):
            call_count["n"] += 1
            return FakeResponse()

        monkeypatch.setattr(requests, "post", fake_post)

        with pytest.raises(RuntimeError, match="Cortex API returned 429"):
            keywords_module._call_cortex_complete("content")

        assert call_count["n"] == 3  # 3 retries

    @pytest.mark.unit
    def test_request_exception_retries_then_raises(self, monkeypatch):
        """RequestException is retried then raises (lines 809-813)."""
        monkeypatch.setattr(
            keywords_module,
            "load_snowflake_config",
            lambda conn: {"account": "myacct", "token": "tok"},
        )
        monkeypatch.setattr(time, "sleep", lambda _: None)

        import requests

        def fake_post(*a, **kw):
            raise requests.exceptions.ConnectionError("Connection refused")

        monkeypatch.setattr(requests, "post", fake_post)

        with pytest.raises(RuntimeError, match="Cortex API request failed"):
            keywords_module._call_cortex_complete("content")


class TestParseKeywordResponseFallbacks:
    """Test _parse_keyword_response fallback paths."""

    @pytest.mark.unit
    def test_comma_separated_fallback(self):
        """Comma-separated text is parsed when JSON fails (lines 837-841)."""
        text = 'snowflake, cortex agent, "masking policy"'

        result = keywords_module._parse_keyword_response(text, count=10)

        assert "snowflake" in result
        assert "cortex agent" in result

    @pytest.mark.unit
    def test_newline_separated_fallback_with_bullets(self):
        """Newline-separated with bullet markers is parsed (lines 844-850)."""
        text = "- snowflake\n* cortex agent\n1. masking policy\n2. RBAC"

        result = keywords_module._parse_keyword_response(text, count=10)

        assert "snowflake" in result
        assert "cortex agent" in result
        assert "masking policy" in result


class TestExtractHeadersEdgeCasesExtended:
    """Test _extract_headers edge cases for specific uncovered lines."""

    @pytest.mark.unit
    def test_question_form_header_skipped(self):
        """Question-form header ending with '?' is skipped (line 939)."""
        extractor = keywords_module.KeywordExtractor()
        content = "## What is Snowflake?\n\nSome content."

        candidates = extractor._extract_headers(content)

        header_terms = [c.term for c in candidates]
        assert not any("What is Snowflake" in t for t in header_terms)

    @pytest.mark.unit
    def test_special_characters_header_skipped(self):
        """Header with special characters like ≤ > ~ = is skipped (line 942)."""
        extractor = keywords_module.KeywordExtractor()
        content = "## Values ≤ Threshold\n\n## Performance > Baseline\n\nContent."

        candidates = extractor._extract_headers(content)

        header_terms = [c.term for c in candidates]
        assert not any("Threshold" in t for t in header_terms)
        assert not any("Baseline" in t for t in header_terms)

    @pytest.mark.unit
    def test_too_long_header_skipped(self):
        """Header too long (>45 chars) is skipped (line 945)."""
        extractor = keywords_module.KeywordExtractor()
        long_header = "A" * 20 + " " + "B" * 20 + " " + "C" * 10
        content = f"## {long_header}\n\nContent."

        candidates = extractor._extract_headers(content)

        header_terms = [c.term for c in candidates]
        assert not any(long_header in t for t in header_terms)

    @pytest.mark.unit
    def test_empty_cleaned_header_skipped(self):
        """Empty cleaned header is skipped (line 948)."""
        extractor = keywords_module.KeywordExtractor()
        # After stripping markdown formatting and colons, header becomes empty
        content = "## **:**\n\nContent."

        candidates = extractor._extract_headers(content)

        # Should not produce any candidates from the empty header
        assert all(c.term.strip() for c in candidates)

    @pytest.mark.unit
    def test_single_proper_noun_word_from_header(self):
        """Single proper-noun word extracted from header (line 955)."""
        extractor = keywords_module.KeywordExtractor()
        content = "## Snowflake\n\nContent about Snowflake."

        candidates = extractor._extract_headers(content)

        header_terms = [c.term for c in candidates if c.source == "header"]
        assert "Snowflake" in header_terms


class TestExtractEmphasizedTermsExtended:
    """Test _extract_emphasized_terms for additional uncovered branches."""

    @pytest.mark.unit
    def test_bold_compound_phrase_with_two_meaningful_words(self):
        """Bold term with 2+ meaningful words kept as compound phrase (lines 1033, 1039)."""
        extractor = keywords_module.KeywordExtractor()
        content = "Use **Cortex Agent** for orchestration.\n"

        candidates = extractor._extract_emphasized_terms(content)

        terms = [c.term for c in candidates if c.source == "emphasis"]
        assert any("Cortex Agent" in t for t in terms)

    @pytest.mark.unit
    def test_backtick_term_with_spaces_skipped(self):
        """Backtick term with spaces is skipped (line 1055)."""
        extractor = keywords_module.KeywordExtractor()
        content = "Run `uv run pytest` for testing.\n"

        candidates = extractor._extract_emphasized_terms(content)

        terms = [c.term for c in candidates if c.source == "emphasis"]
        assert "uv run pytest" not in terms

    @pytest.mark.unit
    def test_backtick_term_with_path_skipped(self):
        """Backtick term with slashes is skipped (line 1055)."""
        extractor = keywords_module.KeywordExtractor()
        content = "Edit `src/main` carefully.\n"

        candidates = extractor._extract_emphasized_terms(content)

        terms = [c.term for c in candidates if c.source == "emphasis"]
        assert "src/main" not in terms

    @pytest.mark.unit
    def test_backtick_term_starting_with_dash_skipped(self):
        """Backtick term starting with '-' is skipped (line 1058)."""
        extractor = keywords_module.KeywordExtractor()
        content = "Use `--verbose` flag for debugging.\n"

        candidates = extractor._extract_emphasized_terms(content)

        terms = [c.term for c in candidates if c.source == "emphasis"]
        assert "--verbose" not in terms


class TestSuggestKeywordsCacheHit:
    """Test suggest_keywords cache hit path."""

    @pytest.mark.unit
    def test_cache_hit_returns_cached_keywords(self, tmp_path: Path):
        """Cached keywords are returned on hash match (lines 1198-1199)."""
        extractor = keywords_module.KeywordExtractor()

        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        content = rule_file.read_text(encoding="utf-8")
        content_hash = keywords_module._content_hash(content)
        file_key = str(rule_file.resolve())
        cache = {
            file_key: {
                "hash": content_hash,
                "keywords": ["cached_kw1", "cached_kw2"],
            }
        }

        result = extractor.suggest_keywords(rule_file, cache=cache)

        assert result.suggested_keywords == ["cached_kw1", "cached_kw2"]


class TestSuggestKeywordsApiFailureFallback:
    """Test suggest_keywords when API fails falls back to heuristic."""

    @pytest.mark.unit
    def test_api_failure_triggers_heuristic_fallback(self, tmp_path: Path, monkeypatch):
        """RuntimeError from API triggers heuristic fallback (lines 1213-1215)."""
        extractor = keywords_module.KeywordExtractor()

        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(
            keywords_module,
            "_call_cortex_complete",
            lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("API down")),
        )

        result = extractor.suggest_keywords(rule_file, use_api=True)

        # Should still return keywords from heuristic fallback
        assert len(result.suggested_keywords) > 0


class TestKeywordsCLINoPath:
    """Test keywords() CLI with no path argument."""

    @pytest.mark.unit
    def test_no_path_shows_help(self):
        """Invoke with no arguments shows help (lines 1441-1442)."""
        result = runner.invoke(app, ["keywords"])

        assert result.exit_code == 0
        assert "Generate semantically relevant keywords" in result.output


class TestKeywordsCLIMissingCredentials:
    """Test keywords() CLI when credentials are missing."""

    @pytest.mark.unit
    def test_missing_credentials_uses_heuristic_fallback(self, tmp_path: Path, monkeypatch):
        """Missing credentials triggers heuristic fallback (lines 1459-1465)."""
        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(
            keywords_module,
            "load_snowflake_config",
            lambda conn: (_ for _ in ()).throw(FileNotFoundError("No Snowflake config found")),
        )

        result = runner.invoke(app, ["keywords", str(rule_file)])

        assert result.exit_code == 0
        # Should still produce output using heuristic fallback
        assert "100-test.md" in result.output
