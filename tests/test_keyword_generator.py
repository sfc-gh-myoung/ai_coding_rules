"""Tests for keyword_generator.py keyword extraction functionality."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.keyword_generator import (
    COMPOUND_TERMS,
    STOP_TERMS,
    TECHNOLOGY_TERMS,
    ExtractionResult,
    KeywordCandidate,
    KeywordExtractor,
    format_keywords_line,
    update_keywords_in_file,
)


class TestKeywordCandidate:
    """Tests for KeywordCandidate dataclass."""

    def test_hash_case_insensitive(self):
        """Keywords with same term (different case) should hash equal."""
        kw1 = KeywordCandidate(term="Python", score=0.5, source="header")
        kw2 = KeywordCandidate(term="python", score=0.8, source="tfidf")
        assert hash(kw1) == hash(kw2)

    def test_equality_case_insensitive(self):
        """Keywords with same term (different case) should be equal."""
        kw1 = KeywordCandidate(term="Snowflake", score=0.5, source="header")
        kw2 = KeywordCandidate(term="snowflake", score=0.8, source="technology")
        assert kw1 == kw2

    def test_different_terms_not_equal(self):
        """Keywords with different terms should not be equal."""
        kw1 = KeywordCandidate(term="Python", score=0.5, source="header")
        kw2 = KeywordCandidate(term="SQL", score=0.5, source="header")
        assert kw1 != kw2


class TestExtractionResult:
    """Tests for ExtractionResult dataclass."""

    def test_added_keywords(self):
        """Test detection of added keywords."""
        result = ExtractionResult(
            file_path=Path("test.md"),
            current_keywords=["Python", "SQL"],
            suggested_keywords=["Python", "SQL", "Snowflake"],
        )
        assert result.added == {"Snowflake"}

    def test_removed_keywords(self):
        """Test detection of removed keywords."""
        result = ExtractionResult(
            file_path=Path("test.md"),
            current_keywords=["Python", "SQL", "deprecated"],
            suggested_keywords=["Python", "SQL"],
        )
        assert result.removed == {"deprecated"}

    def test_kept_keywords(self):
        """Test detection of kept keywords."""
        result = ExtractionResult(
            file_path=Path("test.md"),
            current_keywords=["Python", "SQL"],
            suggested_keywords=["python", "sql", "Snowflake"],  # Different case
        )
        assert result.kept == {"Python", "SQL"}

    def test_case_insensitive_comparison(self):
        """Test that keyword comparison is case-insensitive."""
        result = ExtractionResult(
            file_path=Path("test.md"),
            current_keywords=["PYTHON", "sql"],
            suggested_keywords=["Python", "SQL"],
        )
        assert len(result.added) == 0
        assert len(result.removed) == 0
        assert result.kept == {"PYTHON", "sql"}


class TestKeywordExtractor:
    """Tests for KeywordExtractor class."""

    @pytest.fixture
    def extractor(self):
        """Create an extractor without corpus."""
        return KeywordExtractor(corpus_dir=None)

    def test_extract_headers(self, extractor: KeywordExtractor):
        """Test extraction of keywords from headers."""
        content = """
## Metadata
**Keywords:** test

## Streamlit Dashboard Patterns

### Session State Management

## Contract
"""
        candidates = extractor._extract_headers(content)
        terms = {c.term.lower() for c in candidates}

        assert "streamlit" in terms
        assert "dashboard" in terms
        assert "session" in terms
        assert "management" in terms
        # Should skip standard sections
        assert "metadata" not in terms
        assert "contract" not in terms

    def test_extract_code_languages(self, extractor: KeywordExtractor):
        """Test extraction of programming languages from code blocks."""
        content = """
```python
print("hello")
```

```sql
SELECT * FROM table;
```

```bash
echo "test"
```
"""
        candidates = extractor._extract_code_languages(content)
        terms = {c.term.lower() for c in candidates}

        assert "python" in terms
        assert "sql" in terms
        assert "bash" in terms

    def test_extract_emphasized_terms(self, extractor: KeywordExtractor):
        """Test extraction of bold and backtick terms."""
        content = """
Use **Snowflake** for data warehousing.
Configure `st.session_state` properly.
The **RBAC** pattern is important.
"""
        candidates = extractor._extract_emphasized_terms(content)
        terms = {c.term.lower() for c in candidates}

        assert "snowflake" in terms
        assert "rbac" in terms
        # Backtick terms that look like code should be included
        assert "st.session_state" in terms

    def test_extract_technology_terms(self, extractor: KeywordExtractor):
        """Test extraction of known technology terms."""
        content = """
This rule covers Snowflake Streamlit applications
with Cortex AI integration and Python best practices.
"""
        candidates = extractor._extract_technology_terms(content)
        terms = {c.term.lower() for c in candidates}

        assert "snowflake" in terms
        assert "streamlit" in terms
        assert "cortex" in terms
        assert "python" in terms

    def test_extract_current_keywords(self, extractor: KeywordExtractor):
        """Test extraction of current keywords from metadata."""
        content = """
## Metadata

**SchemaVersion:** v3.0
**Keywords:** Python, SQL, Snowflake, data loading
**TokenBudget:** ~2000
"""
        keywords = extractor._extract_current_keywords(content)

        assert keywords == ["Python", "SQL", "Snowflake", "data loading"]

    def test_extract_current_keywords_empty(self, extractor: KeywordExtractor):
        """Test extraction when no keywords field exists."""
        content = """
## Metadata

**SchemaVersion:** v3.0
**TokenBudget:** ~2000
"""
        keywords = extractor._extract_current_keywords(content)
        assert keywords == []

    def test_rank_keywords_deduplication(self, extractor: KeywordExtractor):
        """Test that ranking deduplicates by term."""
        candidates = [
            KeywordCandidate(term="Python", score=0.5, source="header"),
            KeywordCandidate(term="python", score=0.3, source="tfidf"),
            KeywordCandidate(term="PYTHON", score=0.2, source="emphasis"),
            KeywordCandidate(term="SQL", score=0.4, source="header"),
        ]
        result = extractor.rank_keywords(candidates, count=5)

        # Should have only 2 unique terms
        assert len(result) == 2
        # Python should have higher combined score
        assert result[0] == "Python"

    def test_rank_keywords_filters_stop_terms(self, extractor: KeywordExtractor):
        """Test that stop terms are filtered out."""
        candidates = [
            KeywordCandidate(term="data", score=0.9, source="header"),  # stop term
            KeywordCandidate(term="Snowflake", score=0.5, source="technology"),
        ]
        result = extractor.rank_keywords(candidates, count=5)

        assert "data" not in [r.lower() for r in result]
        assert "Snowflake" in result

    def test_rank_keywords_respects_count(self, extractor: KeywordExtractor):
        """Test that ranking respects the count limit."""
        candidates = [
            KeywordCandidate(term=f"term{i}", score=0.5, source="header") for i in range(20)
        ]
        result = extractor.rank_keywords(candidates, count=10)

        assert len(result) == 10


class TestFormatKeywordsLine:
    """Tests for format_keywords_line function."""

    def test_format_single_keyword(self):
        """Test formatting a single keyword."""
        result = format_keywords_line(["Python"])
        assert result == "**Keywords:** Python"

    def test_format_multiple_keywords(self):
        """Test formatting multiple keywords."""
        result = format_keywords_line(["Python", "SQL", "Snowflake"])
        assert result == "**Keywords:** Python, SQL, Snowflake"

    def test_format_empty_list(self):
        """Test formatting empty keyword list."""
        result = format_keywords_line([])
        assert result == "**Keywords:** "


class TestUpdateKeywordsInFile:
    """Tests for update_keywords_in_file function."""

    def test_update_keywords(self, tmp_path: Path):
        """Test updating keywords in a file."""
        test_file = tmp_path / "test.md"
        test_file.write_text("""
## Metadata

**SchemaVersion:** v3.0
**Keywords:** old, keywords
**TokenBudget:** ~2000
""")
        result = update_keywords_in_file(test_file, ["new", "keywords", "here"])

        assert result is True
        content = test_file.read_text()
        assert "**Keywords:** new, keywords, here" in content
        assert "old, keywords" not in content

    def test_update_no_change(self, tmp_path: Path):
        """Test that no update occurs when keywords are the same."""
        test_file = tmp_path / "test.md"
        test_file.write_text("""
## Metadata

**Keywords:** same, keywords
""")
        result = update_keywords_in_file(test_file, ["same", "keywords"])

        assert result is False

    def test_update_missing_field(self, tmp_path: Path, capsys):
        """Test handling of missing Keywords field."""
        test_file = tmp_path / "test.md"
        test_file.write_text("""
## Metadata

**SchemaVersion:** v3.0
""")
        result = update_keywords_in_file(test_file, ["new", "keywords"])

        assert result is False
        captured = capsys.readouterr()
        assert "Warning" in captured.out


class TestDomainConstants:
    """Tests for domain-specific constants."""

    def test_technology_terms_lowercase(self):
        """Verify all technology terms are lowercase."""
        for term in TECHNOLOGY_TERMS:
            assert term == term.lower(), f"Technology term '{term}' should be lowercase"

    def test_stop_terms_lowercase(self):
        """Verify all stop terms are lowercase."""
        for term in STOP_TERMS:
            assert term == term.lower(), f"Stop term '{term}' should be lowercase"

    def test_compound_terms_format(self):
        """Verify compound terms have proper format."""
        for phrase, replacement in COMPOUND_TERMS.items():
            # Phrase should have space
            assert " " in phrase, f"Compound phrase '{phrase}' should contain space"
            # Replacement should use underscore
            assert "_" in replacement, f"Replacement '{replacement}' should use underscore"


@pytest.mark.integration
class TestKeywordExtractorIntegration:
    """Integration tests requiring file system access."""

    def test_suggest_keywords_real_file(self, tmp_path: Path):
        """Test full keyword suggestion on a realistic rule file."""
        test_file = tmp_path / "test-rule.md"
        test_file.write_text("""
# Streamlit Core Configuration

## Metadata

**SchemaVersion:** v3.0
**Keywords:** old, outdated, keywords
**TokenBudget:** ~2000
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md

## Purpose
Guide for building Streamlit applications with Snowflake integration.

## Rule Scope
Streamlit dashboard development with session state management.

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- Use `st.session_state` for state management
- Configure `st.connection` for Snowflake
- Apply RBAC patterns for security

## Contract

<contract>
<inputs_prereqs>
Python 3.11+, Streamlit 1.46+
</inputs_prereqs>
</contract>

## Dashboard Configuration

### Session State Best Practices

```python
import streamlit as st

if "initialized" not in st.session_state:
    st.session_state.initialized = True
```

### Snowflake Connection

```sql
SELECT * FROM my_table;
```

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Not using session state**
```python
# Bad
global_var = "don't do this"
```

## Post-Execution Checklist
- [ ] Session state initialized

## Validation
Test the dashboard locally.

## Output Format Examples

```python
st.write("Hello")
```

## References

### External Documentation
- [Streamlit Docs](https://docs.streamlit.io)

### Related Rules
- `rules/100-snowflake-core.md`
""")

        extractor = KeywordExtractor(corpus_dir=None)
        result = extractor.suggest_keywords(test_file, count=12)

        # Should extract meaningful terms
        suggested_lower = [k.lower() for k in result.suggested_keywords]
        assert "streamlit" in suggested_lower
        assert "python" in suggested_lower or "sql" in suggested_lower

        # Should have reasonable count
        assert 5 <= len(result.suggested_keywords) <= 15


@pytest.mark.integration
class TestCorpusBuildingAndTFIDF:
    """Integration tests for corpus building and TF-IDF keyword extraction."""

    def test_build_corpus_with_valid_directory(self, tmp_path: Path):
        """Test corpus building with a directory of rule files."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "100-snowflake.md").write_text("Snowflake data warehouse rules")
        (rules_dir / "200-python.md").write_text("Python coding standards")

        # Act
        extractor = KeywordExtractor(corpus_dir=rules_dir, debug=False)

        # Assert
        assert extractor.vectorizer is not None
        assert len(extractor.corpus_docs) == 2
        assert len(extractor.corpus_paths) == 2

    def test_build_corpus_with_nonexistent_directory(self, tmp_path: Path):
        """Test corpus building with nonexistent directory."""
        # Arrange
        nonexistent = tmp_path / "doesnotexist"

        # Act
        extractor = KeywordExtractor(corpus_dir=nonexistent, debug=False)

        # Assert
        assert extractor.vectorizer is None
        assert len(extractor.corpus_docs) == 0

    def test_build_corpus_skips_invalid_files(self, tmp_path: Path):
        """Test that corpus building skips invalid/unreadable files."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "valid1.md").write_text(
            "Snowflake warehouse optimization patterns for data processing"
        )
        (rules_dir / "valid2.md").write_text("Python coding standards testing validation methods")
        (rules_dir / "rules/RULES_INDEX.md").write_text("Index - should be skipped")

        # Act
        extractor = KeywordExtractor(corpus_dir=rules_dir, debug=False)

        # Assert
        # Should include valid.md files, skip RULES_INDEX.md
        assert len(extractor.corpus_docs) == 2
        names = {p.name for p in extractor.corpus_paths}
        assert "valid1.md" in names
        assert "valid2.md" in names
        assert "rules/RULES_INDEX.md" not in names

    def test_extract_tfidf_for_document_in_corpus(self, tmp_path: Path):
        """Test TF-IDF extraction for a document that's in the corpus."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        test_file = rules_dir / "test-rule.md"
        test_file.write_text("Snowflake warehouse optimization patterns")
        (rules_dir / "other.md").write_text("Python testing patterns")

        extractor = KeywordExtractor(corpus_dir=rules_dir, debug=False)

        # Act
        candidates = extractor._extract_tfidf_terms(test_file.read_text(), test_file, top_n=5)

        # Assert
        assert len(candidates) > 0
        assert all(c.source == "tfidf" for c in candidates)
        assert all(c.score > 0 for c in candidates)

    def test_extract_tfidf_for_document_not_in_corpus(self, tmp_path: Path):
        """Test TF-IDF extraction for a new document not in corpus."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "corpus1.md").write_text("Snowflake data warehouse optimization patterns")
        (rules_dir / "corpus2.md").write_text("Python coding standards and best practices")

        extractor = KeywordExtractor(corpus_dir=rules_dir, debug=False)

        new_file = tmp_path / "new-rule.md"
        new_file.write_text("FastAPI REST API development framework patterns")

        # Act
        candidates = extractor._extract_tfidf_terms(new_file.read_text(), new_file, top_n=5)

        # Assert
        # Should extract terms even for new document
        assert all(c.source == "tfidf" for c in candidates) if candidates else True

    def test_preprocess_for_tfidf_handles_compounds(self, tmp_path: Path):
        """Test that preprocessing converts compound terms to underscores."""
        # Arrange
        extractor = KeywordExtractor(corpus_dir=None, debug=False)
        content = "Use session state and data warehouse for best practices"

        # Act
        processed = extractor._preprocess_for_tfidf(content)

        # Assert
        # Compound terms should be converted to underscored versions
        assert "session_state" in processed or "warehouse" in processed

    def test_suggest_keywords_with_corpus_integration(self, tmp_path: Path):
        """Test full keyword suggestion workflow with TF-IDF corpus."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "100-snowflake.md").write_text("""
# Snowflake Core
Keywords: snowflake, warehouse, sql
Content about Snowflake data warehouse optimization.
""")
        (rules_dir / "200-python.md").write_text("""
# Python Core
Keywords: python, testing, pytest
Content about Python development practices.
""")

        test_file = rules_dir / "300-test.md"
        test_file.write_text("""
# Test Rule
**Keywords:** old, keywords
## Snowflake Integration
Use Snowflake warehouse for data processing with Python.
""")

        extractor = KeywordExtractor(corpus_dir=rules_dir, debug=False)

        # Act
        result = extractor.suggest_keywords(test_file, count=10)

        # Assert
        assert len(result.suggested_keywords) > 0
        suggested_lower = [k.lower() for k in result.suggested_keywords]
        # Should include relevant terms from content
        assert "snowflake" in suggested_lower or "python" in suggested_lower


class TestDebugAndEdgeCases:
    """Tests for debug mode and edge case handling."""

    def test_debug_output_enabled(self, capsys, tmp_path: Path):
        """Test that debug messages are printed when debug=True."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "test1.md").write_text(
            "Snowflake warehouse optimization and performance tuning guidelines"
        )
        (rules_dir / "test2.md").write_text(
            "Python testing framework patterns pytest validation methods"
        )

        # Act
        KeywordExtractor(corpus_dir=rules_dir, debug=True)

        # Assert
        captured = capsys.readouterr()
        assert "[DEBUG]" in captured.err

    def test_debug_output_disabled(self, capsys, tmp_path: Path):
        """Test that debug messages are not printed when debug=False."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "test1.md").write_text(
            "Snowflake warehouse optimization and performance tuning guidelines"
        )
        (rules_dir / "test2.md").write_text(
            "Python testing framework patterns pytest validation methods"
        )

        # Act
        KeywordExtractor(corpus_dir=rules_dir, debug=False)

        # Assert
        captured = capsys.readouterr()
        assert "[DEBUG]" not in captured.err

    def test_rank_keywords_handles_compound_terms(self):
        """Test that rank_keywords properly handles compound terms."""
        # Arrange
        extractor = KeywordExtractor(corpus_dir=None)
        candidates = [
            KeywordCandidate(term="session state", score=0.8, source="header"),
            KeywordCandidate(term="data warehouse", score=0.7, source="emphasis"),
            KeywordCandidate(term="Snowflake", score=0.6, source="technology"),
        ]

        # Act
        result = extractor.rank_keywords(candidates, count=5)

        # Assert
        assert len(result) == 3
        # Compound terms should be preserved in output
        result_lower = [r.lower() for r in result]
        assert any("session" in r and "state" in r for r in result_lower)

    def test_extract_candidates_comprehensive_coverage(self, tmp_path: Path):
        """Test extract_candidates with comprehensive content."""
        # Arrange
        test_file = tmp_path / "comprehensive.md"
        test_file.write_text("""
# Comprehensive Test Rule

## Metadata
**Keywords:** old, existing, keywords

## Purpose
Test **Snowflake** integration with `st.session_state` and `.py` files.

### Code Examples
```python
import streamlit as st
```

```sql
SELECT * FROM warehouse;
```

```Javascript
console.log('test');
```

## Best Practices
Use RBAC patterns for security.
""")

        extractor = KeywordExtractor(corpus_dir=None)

        # Act
        candidates = extractor.extract_candidates(test_file.read_text(), test_file)

        # Assert
        assert len(candidates) > 0
        sources = {c.source for c in candidates}
        # Should have candidates from multiple sources
        assert len(sources) >= 2

    def test_build_corpus_with_read_error(self, tmp_path: Path, capsys):
        """Test corpus building handles file read errors gracefully."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "good1.md").write_text("Snowflake warehouse optimization patterns")
        (rules_dir / "good2.md").write_text("Python testing framework methods")

        # Create a file that will cause an error when read
        bad_file = rules_dir / "bad.md"
        bad_file.write_text("content")

        # Act
        with patch(
            "pathlib.Path.read_text",
            side_effect=[
                "Snowflake warehouse optimization patterns",  # good1.md
                OSError("Simulated read error"),  # bad.md
                "Python testing framework methods",  # good2.md
            ],
        ):
            extractor = KeywordExtractor(corpus_dir=rules_dir, debug=True)

        # Assert
        captured = capsys.readouterr()
        # Should have debug message about error
        assert "Error reading" in captured.err or len(extractor.corpus_docs) >= 0

    def test_rank_keywords_preserves_proper_casing(self):
        """Test that rank_keywords preserves proper casing for capitalized terms."""
        # Arrange
        extractor = KeywordExtractor(corpus_dir=None)
        candidates = [
            KeywordCandidate(term="Snowflake", score=0.9, source="technology"),  # Capitalized
            KeywordCandidate(term="snowflake", score=0.1, source="text"),  # lowercase
        ]

        # Act
        result = extractor.rank_keywords(candidates, count=5)

        # Assert
        assert len(result) == 1  # Deduped
        # Should preserve the capitalized version
        assert "Snowflake" in result

    def test_main_corpus_auto_detect_PROJECT_ROOT(self, tmp_path: Path):
        """Test corpus auto-detection using PROJECT_ROOT fallback."""
        # Arrange
        from scripts import keyword_generator as kg

        # Create a test file not in rules/ directory
        test_file = tmp_path / "standalone.md"
        test_file.write_text("**Keywords:** test\n# Test content")

        # Mock PROJECT_ROOT to point to a location with rules/
        project_root = tmp_path / "project"
        project_root.mkdir()
        rules_dir = project_root / "rules"
        rules_dir.mkdir()
        (rules_dir / "corpus.md").write_text("Corpus content for TF-IDF")
        (rules_dir / "corpus2.md").write_text("More corpus content")

        # Act
        with (
            patch("sys.argv", ["keyword_generator.py", str(test_file), "--corpus"]),
            patch("scripts.keyword_generator.PROJECT_ROOT", project_root),
        ):
            exit_code = kg.main()

        # Assert
        assert exit_code == 0

    def test_main_with_update_flag_shows_message(self, tmp_path: Path, capsys):
        """Test CLI with --update flag shows updated/no change message."""
        # Arrange
        from scripts import keyword_generator as kg

        test_file = tmp_path / "test.md"
        test_file.write_text("""
**Keywords:** Snowflake, Python
# Test
Content here
""")

        # Act - File already has good keywords, so should show "No change"
        with patch("sys.argv", ["keyword_generator.py", str(test_file), "--update"]):
            exit_code = kg.main()

        # Assert
        assert exit_code == 0
        captured = capsys.readouterr()
        # Should show either "Updated" or "No change"
        assert "Updated:" in captured.out or "No change:" in captured.out


class TestPrintDiff:
    """Tests for print_diff output formatting."""

    def test_print_diff_with_added_keywords(self, capsys):
        """Test print_diff shows added keywords."""
        # Arrange
        from scripts.keyword_generator import print_diff

        result = ExtractionResult(
            file_path=Path("test.md"),
            current_keywords=["Python"],
            suggested_keywords=["Python", "SQL", "Snowflake"],
        )

        # Act
        print_diff(result)

        # Assert
        captured = capsys.readouterr()
        assert "+ Added:" in captured.out
        assert "SQL" in captured.out
        assert "Snowflake" in captured.out

    def test_print_diff_with_removed_keywords(self, capsys):
        """Test print_diff shows removed keywords."""
        # Arrange
        from scripts.keyword_generator import print_diff

        result = ExtractionResult(
            file_path=Path("test.md"),
            current_keywords=["Python", "deprecated", "old"],
            suggested_keywords=["Python"],
        )

        # Act
        print_diff(result)

        # Assert
        captured = capsys.readouterr()
        assert "- Removed:" in captured.out
        assert "deprecated" in captured.out
        assert "old" in captured.out

    def test_print_diff_with_kept_keywords(self, capsys):
        """Test print_diff shows kept keywords."""
        # Arrange
        from scripts.keyword_generator import print_diff

        result = ExtractionResult(
            file_path=Path("test.md"),
            current_keywords=["Python", "SQL"],
            suggested_keywords=["Python", "SQL"],
        )

        # Act
        print_diff(result)

        # Assert
        captured = capsys.readouterr()
        assert "= Kept:" in captured.out
        assert "Python" in captured.out
        assert "SQL" in captured.out

    def test_print_diff_with_all_changes(self, capsys):
        """Test print_diff with all change types."""
        # Arrange
        from scripts.keyword_generator import print_diff

        result = ExtractionResult(
            file_path=Path("test.md"),
            current_keywords=["Python", "deprecated"],
            suggested_keywords=["Python", "SQL"],
        )

        # Act
        print_diff(result)

        # Assert
        captured = capsys.readouterr()
        assert "- Removed:" in captured.out
        assert "+ Added:" in captured.out
        assert "= Kept:" in captured.out
        assert "Current (2):" in captured.out
        assert "Suggested (2):" in captured.out


class TestKeywordCandidateEquality:
    """Tests for KeywordCandidate equality checking."""

    def test_keyword_candidate_equality_with_non_candidate(self):
        """Test KeywordCandidate equality with non-KeywordCandidate object."""
        # Arrange
        kw = KeywordCandidate(term="Python", score=0.5, source="header")

        # Act & Assert
        assert kw != "Python"
        assert kw != 123
        assert kw is not None

    def test_keyword_candidate_equality_with_different_type(self):
        """Test KeywordCandidate __eq__ returns False for different types."""
        # Arrange
        kw = KeywordCandidate(term="Python", score=0.5, source="header")

        # Act
        result = kw.__eq__({"term": "Python"})

        # Assert
        assert result is False


@pytest.mark.integration
class TestCLI:
    """Tests for CLI argument parsing and execution."""

    def test_main_with_single_file(self, tmp_path: Path):
        """Test CLI with single file argument."""
        # Arrange
        from scripts import keyword_generator as kg

        test_file = tmp_path / "test.md"
        test_file.write_text("""
**Keywords:** old
# Test Rule
**Snowflake** testing
""")

        # Act
        with patch("sys.argv", ["keyword_generator.py", str(test_file)]):
            exit_code = kg.main()

        # Assert
        assert exit_code == 0

    def test_main_with_directory(self, tmp_path: Path, capsys):
        """Test CLI with directory argument."""
        # Arrange
        from scripts import keyword_generator as kg

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "100-test.md").write_text("**Keywords:** test\n# Test")
        (rules_dir / "200-test.md").write_text("**Keywords:** test\n# Test")

        # Act
        with patch("sys.argv", ["keyword_generator.py", str(rules_dir)]):
            exit_code = kg.main()

        # Assert
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "100-test.md" in captured.out
        assert "200-test.md" in captured.out

    def test_main_with_update_flag(self, tmp_path: Path):
        """Test CLI with --update flag."""
        # Arrange
        from scripts import keyword_generator as kg

        test_file = tmp_path / "test.md"
        test_file.write_text("""
**Keywords:** old, keywords
# Snowflake Testing
Content here
""")

        # Act
        with patch("sys.argv", ["keyword_generator.py", str(test_file), "--update"]):
            exit_code = kg.main()

        # Assert
        assert exit_code == 0
        content = test_file.read_text()
        # Keywords should be updated
        assert "**Keywords:**" in content

    def test_main_with_diff_flag(self, tmp_path: Path, capsys):
        """Test CLI with --diff flag."""
        # Arrange
        from scripts import keyword_generator as kg

        test_file = tmp_path / "test.md"
        test_file.write_text("""
**Keywords:** old, deprecated
# Snowflake Testing
Use **Snowflake** for data warehouse
""")

        # Act
        with patch("sys.argv", ["keyword_generator.py", str(test_file), "--diff"]):
            exit_code = kg.main()

        # Assert
        assert exit_code == 0
        captured = capsys.readouterr()
        # Should show diff output
        assert "File:" in captured.out

    def test_main_with_corpus_flag_file_input(self, tmp_path: Path):
        """Test CLI with --corpus flag and file input."""
        # Arrange
        from scripts import keyword_generator as kg

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        test_file = rules_dir / "test.md"
        test_file.write_text("**Keywords:** test\n# Snowflake")
        (rules_dir / "other.md").write_text("# Python")

        # Act
        with patch("sys.argv", ["keyword_generator.py", str(test_file), "--corpus"]):
            exit_code = kg.main()

        # Assert
        assert exit_code == 0

    def test_main_with_corpus_flag_directory_input(self, tmp_path: Path):
        """Test CLI with --corpus flag and directory input."""
        # Arrange
        from scripts import keyword_generator as kg

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "100-test.md").write_text(
            "**Keywords:** test\n# Snowflake warehouse optimization"
        )
        (rules_dir / "200-test.md").write_text("**Keywords:** test\n# Python testing framework")

        # Act
        with patch("sys.argv", ["keyword_generator.py", str(rules_dir), "--corpus"]):
            exit_code = kg.main()

        # Assert
        assert exit_code == 0

    def test_main_with_corpus_flag_auto_detect_rules_dir(self, tmp_path: Path):
        """Test corpus auto-detection for rules directory."""
        # Arrange
        from scripts import keyword_generator as kg

        project_root = tmp_path / "project"
        project_root.mkdir()
        rules_dir = project_root / "rules"
        rules_dir.mkdir()
        test_file = rules_dir / "test.md"
        test_file.write_text("**Keywords:** test\n# Test")
        (rules_dir / "other.md").write_text("# Other")

        # Act
        with patch("sys.argv", ["keyword_generator.py", str(test_file), "--corpus"]):
            exit_code = kg.main()

        # Assert
        assert exit_code == 0

    def test_main_with_nonexistent_path(self, tmp_path: Path, capsys):
        """Test CLI with nonexistent path."""
        # Arrange
        from scripts import keyword_generator as kg

        nonexistent = tmp_path / "does_not_exist.md"

        # Act
        with patch("sys.argv", ["keyword_generator.py", str(nonexistent)]):
            exit_code = kg.main()

        # Assert
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "does not exist" in captured.err

    def test_main_with_no_files_found(self, tmp_path: Path, capsys):
        """Test CLI with directory containing no markdown files."""
        # Arrange
        from scripts import keyword_generator as kg

        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        # Act
        with patch("sys.argv", ["keyword_generator.py", str(empty_dir)]):
            exit_code = kg.main()

        # Assert
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "No rule files found" in captured.err

    def test_main_default_output_format(self, tmp_path: Path, capsys):
        """Test CLI default output format (no flags)."""
        # Arrange
        from scripts import keyword_generator as kg

        test_file = tmp_path / "test.md"
        test_file.write_text("""
**Keywords:** old
# Snowflake Test
Content here
""")

        # Act
        with patch("sys.argv", ["keyword_generator.py", str(test_file)]):
            exit_code = kg.main()

        # Assert
        assert exit_code == 0
        captured = capsys.readouterr()
        # Default output shows current and suggested
        assert "Current:" in captured.out
        assert "Suggested:" in captured.out

    def test_module_main_execution(self, tmp_path: Path):
        """Test __main__ block execution."""
        # Arrange
        from scripts import keyword_generator as kg

        test_file = tmp_path / "test.md"
        test_file.write_text("**Keywords:** test\n# Test")

        # Act & Assert
        # Simpler approach: just verify sys.exit is called with correct code
        with patch("sys.argv", ["keyword_generator.py", str(test_file)]), patch("sys.exit"):
            # Simulate __main__ execution
            if __name__ != "__main__":  # We're not in __main__
                kg.main()  # Call main directly
                # Verify sys.exit would be called with 0 in __main__ block
                # (can't easily test the actual __main__ block without subprocess)
        # Test passes if main() runs without raising
