"""Tests for keyword_generator.py keyword extraction functionality."""

from __future__ import annotations

from pathlib import Path

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
