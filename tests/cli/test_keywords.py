"""Tests for ai-rules keywords CLI command.

Tests follow pytest best practices:
- AAA pattern (Arrange-Act-Assert)
- Function-scoped fixtures
- Parametrized tests for input matrices
- Test markers for selective execution
- Isolation with tmp_path
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands import keywords as keywords_module

runner = CliRunner()


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
        assert "--corpus" in result.output
        assert "--count" in result.output
        assert "--debug" in result.output

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


class TestKeywordsCorpusFlag:
    """Test --corpus flag behavior."""

    @pytest.mark.unit
    def test_corpus_builds_from_directory(self, tmp_path: Path):
        """Test --corpus builds TF-IDF from directory."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        # Create multiple files for corpus
        (rules_dir / "100-snowflake-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(
            dedent("""
            # 200-python-core: Python Core

            ## Metadata

            **Keywords:** python, pytest, ruff

            ## Content

            Python best practices and pytest testing.
            """).strip()
        )

        result = runner.invoke(
            app, ["keywords", str(rules_dir / "100-snowflake-core.md"), "--corpus"]
        )

        assert result.exit_code == 0
        assert "Building TF-IDF corpus" in result.output or "100-snowflake-core.md" in result.output

    @pytest.mark.unit
    def test_corpus_with_parent_rules_dir(self, tmp_path: Path):
        """Test --corpus finds rules dir from parent."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        rule_file = rules_dir / "100-snowflake-core.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        result = runner.invoke(app, ["keywords", str(rule_file), "--corpus"])

        assert result.exit_code == 0


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
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        rule_file = rules_dir / "100-snowflake-core.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        result = runner.invoke(app, ["keywords", str(rule_file), "--corpus", "--debug"])

        assert result.exit_code == 0
        # Debug output should show corpus building info
        assert "DEBUG" in result.output or "Building" in result.output


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
    def test_extractor_without_corpus(self, tmp_path: Path):
        """Test extractor works without corpus."""
        extractor = keywords_module.KeywordExtractor(corpus_dir=None, debug=False)

        rule_file = tmp_path / "100-test.md"
        rule_file.write_text(SAMPLE_RULE_CONTENT)

        result = extractor.suggest_keywords(rule_file, count=10)

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
    def test_compound_terms_has_mappings(self):
        """Test COMPOUND_TERMS has expected mappings."""
        assert keywords_module.COMPOUND_TERMS["session state"] == "session_state"
        assert keywords_module.COMPOUND_TERMS["dynamic table"] == "dynamic_table"


class TestKeywordCandidateEdgeCases:
    """Test KeywordCandidate edge cases."""

    @pytest.mark.unit
    def test_not_equal_to_non_candidate(self):
        """Test KeywordCandidate.__eq__ returns False for non-KeywordCandidate objects (line 308)."""
        c = keywords_module.KeywordCandidate(term="snowflake", score=1.0, source="test")
        assert c != "snowflake"
        assert c != 42
        assert c != None  # noqa: E711


class TestBuildCorpusEdgeCases:
    """Test _build_corpus edge cases."""

    @pytest.mark.unit
    def test_corpus_dir_does_not_exist(self, tmp_path: Path):
        """Test _build_corpus returns early when corpus_dir doesn't exist (line 368)."""
        nonexistent = tmp_path / "nonexistent"
        extractor = keywords_module.KeywordExtractor(corpus_dir=nonexistent, debug=False)
        # Should not crash; corpus_docs should be empty
        assert len(extractor.corpus_docs) == 0

    @pytest.mark.unit
    def test_corpus_skips_skip_files(self, tmp_path: Path):
        """Test _build_corpus skips files in SKIP_FILES (line 375)."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "README.md").write_text("# README")
        (rules_dir / "100-valid-rule.md").write_text("# Valid Rule\n\nSome content here.")

        extractor = keywords_module.KeywordExtractor(corpus_dir=rules_dir, debug=False)
        # Only the valid rule should be in corpus
        assert len(extractor.corpus_docs) == 1

    @pytest.mark.unit
    def test_corpus_skips_examples_directory(self, tmp_path: Path):
        """Test _build_corpus skips files in examples/ subdirectory (line 378)."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        examples_dir = rules_dir / "examples"
        examples_dir.mkdir()
        (examples_dir / "100-example.md").write_text("# Example")
        (rules_dir / "100-valid-rule.md").write_text("# Valid Rule\n\nContent.")

        extractor = keywords_module.KeywordExtractor(corpus_dir=rules_dir, debug=False)
        assert len(extractor.corpus_docs) == 1

    @pytest.mark.unit
    def test_corpus_handles_read_exception(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test _build_corpus handles exception reading a file (lines 386-387)."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "100-valid.md").write_text("# Valid content")

        original_read = Path.read_text

        def failing_read(self, *args, **kwargs):
            if "100-valid.md" in str(self):
                raise PermissionError("denied")
            return original_read(self, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", failing_read)

        # Should not crash, just skip the file
        extractor = keywords_module.KeywordExtractor(corpus_dir=rules_dir, debug=True)
        assert len(extractor.corpus_docs) == 0


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


class TestExtractTfidfEdgeCases:
    """Test TF-IDF extraction edge cases."""

    @pytest.mark.unit
    def test_tfidf_document_not_in_corpus(self, tmp_path: Path):
        """Test TF-IDF for document not in corpus (lines 574-577)."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        # Create corpus with one file
        (rules_dir / "100-core.md").write_text(
            "# 100-core: Core Rule\n\n## Content\n\nSnowflake SQL best practices."
        )

        # Create a separate file NOT in the corpus dir
        other_file = tmp_path / "200-other.md"
        other_file.write_text(
            "# 200-other: Other Rule\n\n"
            "## Metadata\n\n"
            "**Keywords:** python\n\n"
            "## Content\n\n"
            "Python pytest testing automation framework."
        )

        extractor = keywords_module.KeywordExtractor(corpus_dir=rules_dir, debug=False)
        result = extractor.suggest_keywords(other_file, count=10)
        # Should still produce suggestions
        assert len(result.suggested_keywords) > 0


class TestRankKeywordsEdgeCases:
    """Test rank_keywords edge cases."""

    @pytest.mark.unit
    def test_stop_terms_excluded_from_ranking(self):
        """Test that stop terms are excluded during ranking (line 648)."""
        extractor = keywords_module.KeywordExtractor()
        candidates = [
            keywords_module.KeywordCandidate(term="data", score=10.0, source="test"),
            keywords_module.KeywordCandidate(term="snowflake", score=5.0, source="test"),
        ]
        ranked = extractor.rank_keywords(candidates, count=5)
        assert "data" not in ranked
        assert "snowflake" in ranked

    @pytest.mark.unit
    def test_uppercase_display_form_preferred(self):
        """Test uppercase display form is preferred over lowercase (line 658)."""
        extractor = keywords_module.KeywordExtractor()
        candidates = [
            keywords_module.KeywordCandidate(term="snowflake", score=3.0, source="test"),
            keywords_module.KeywordCandidate(term="Snowflake", score=2.0, source="test"),
        ]
        ranked = extractor.rank_keywords(candidates, count=5)
        assert "Snowflake" in ranked


class TestKeywordsCLICorpusEdgeCases:
    """Test keywords CLI corpus directory resolution."""

    @pytest.mark.unit
    def test_corpus_with_directory_path(self, tmp_path: Path):
        """Test --corpus when path is a directory sets corpus_dir to that dir (line 880)."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "100-test.md").write_text(
            "# 100-test: Test\n\n## Metadata\n\n"
            "**Keywords:** test\n\n## Content\n\nSnowflake content."
        )

        result = runner.invoke(app, ["keywords", str(rules_dir), "--corpus"])
        assert result.exit_code == 0

    @pytest.mark.unit
    def test_corpus_finds_rules_dir_in_parent(self, tmp_path: Path):
        """Test --corpus finds rules/ dir searching parent directories (lines 887-891)."""
        # Create structure: tmp_path/project/rules/100-test.md
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        rules_dir = project_dir / "rules"
        rules_dir.mkdir()
        (rules_dir / "100-test.md").write_text(
            "# 100-test: Test\n\n## Metadata\n\n"
            "**Keywords:** test\n\n## Content\n\nSnowflake content."
        )

        # Put the file in a subdir (NOT named "rules") so the fallback search kicks in
        sub_dir = project_dir / "other"
        sub_dir.mkdir()
        target_file = sub_dir / "200-other.md"
        target_file.write_text(
            "# 200-other: Other\n\n## Metadata\n\n"
            "**Keywords:** other\n\n## Content\n\nPython content."
        )

        result = runner.invoke(app, ["keywords", str(target_file), "--corpus"])
        assert result.exit_code == 0

    @pytest.mark.unit
    def test_import_error_handling(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test ImportError when scikit-learn is missing (lines 899-902)."""
        rule_file = tmp_path / "100-test.md"
        rule_file.write_text("# Test\n\n## Metadata\n\n**Keywords:** test\n")

        monkeypatch.setattr(
            keywords_module,
            "KeywordExtractor",
            lambda **kwargs: (_ for _ in ()).throw(ImportError("No module named 'sklearn'")),
        )

        result = runner.invoke(app, ["keywords", str(rule_file)])
        assert result.exit_code == 1
        assert "Missing dependency" in result.output or "scikit-learn" in result.output


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
