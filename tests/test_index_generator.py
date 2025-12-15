#!/usr/bin/env python3
"""Test suite for scripts/index_generator.py.

Tests metadata extraction, index generation, and CLI functionality.
Target coverage: 80%+
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.index_generator import (  # noqa: E402
    extract_metadata,
    extract_scope_from_content,
    generate_agent_guidance,
    generate_loading_strategy,
    generate_rules_index,
    generate_table_row,
    main,
    scan_rules,
)


@pytest.fixture
def sample_rule_file(tmp_path):
    """Create a valid rule file with complete metadata."""
    rule_file = tmp_path / "100-test-rule.md"
    content = """# Test Rule Title

**Keywords:** testing, validation, CI/CD
**Depends:** 000-global-core.md, 001-foundations.md
**TokenBudget:** ~500
**ContextTier:** 2

## Rule Scope

This rule applies to all test files and validation scripts.

## Quick Start TL;DR

Quick reference for testing.

## Contract

Test contract details.
"""
    rule_file.write_text(content, encoding="utf-8")
    return rule_file


@pytest.fixture
def rule_file_missing_keywords(tmp_path):
    """Create rule file without Keywords field."""
    rule_file = tmp_path / "200-no-keywords.md"
    content = """# Rule Without Keywords

**Depends:** None
**TokenBudget:** ~300

## Rule Scope

This rule has no keywords defined.
"""
    rule_file.write_text(content, encoding="utf-8")
    return rule_file


@pytest.fixture
def rule_file_minimal_metadata(tmp_path):
    """Create rule file with only required fields."""
    rule_file = tmp_path / "300-minimal.md"
    content = """# Minimal Rule

**Keywords:** minimal

## Rule Scope

Minimal rule scope description.
"""
    rule_file.write_text(content, encoding="utf-8")
    return rule_file


@pytest.fixture
def multiple_rule_files(tmp_path):
    """Create directory with multiple rule files."""
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()

    # Create 3 rule files
    for i, name in enumerate(["000-core.md", "100-python.md", "200-snowflake.md"], 1):
        rule_file = rules_dir / name
        content = f"""# Rule {i}

**Keywords:** keyword{i}, test
**Depends:** {"—" if i == 1 else "000-core.md"}

## Rule Scope

Rule {i} scope description.
"""
        rule_file.write_text(content, encoding="utf-8")

    # Create README.md (should be skipped)
    readme = rules_dir / "README.md"
    readme.write_text("# README\n\nThis should be skipped.", encoding="utf-8")

    return rules_dir


@pytest.fixture
def outdated_index_file(tmp_path):
    """Create outdated RULES_INDEX.md file."""
    index_file = tmp_path / "RULES_INDEX.md"
    content = """# RULES_INDEX

|| File | Scope | Keywords | Depends |
|------|-------|----------|---------|
|| `old-rule.md` | Old scope | old keywords | — |
"""
    index_file.write_text(content, encoding="utf-8")
    return index_file


@pytest.mark.unit
class TestRuleMetadata:
    """Test RuleMetadata extraction and validation."""

    def test_extract_from_valid_rule_file(self, sample_rule_file):
        """Test metadata extraction from valid rule file.

        Validates that all metadata fields (Keywords, Depends, TokenBudget,
        ContextTier, and Scope) are correctly parsed from a well-formed
        rule file. This ensures accurate index generation for rule discovery.
        """
        metadata = extract_metadata(sample_rule_file)

        assert metadata.filename == "100-test-rule.md"
        assert metadata.filepath == sample_rule_file
        assert metadata.keywords == "testing, validation, CI/CD"
        assert metadata.depends == "000-global-core.md, 001-foundations.md"
        assert metadata.token_budget == "~500"
        assert metadata.context_tier == "2"
        assert "test files and validation scripts" in metadata.scope

    def test_extract_handles_missing_optional_fields(self, rule_file_minimal_metadata):
        """Test extraction with missing optional fields.

        Ensures the extractor handles rules with only required fields
        (Keywords and Scope) gracefully, using defaults for optional fields.
        This prevents index generation failures for minimal but valid rules.
        """
        metadata = extract_metadata(rule_file_minimal_metadata)

        assert metadata.filename == "300-minimal.md"
        assert metadata.keywords == "minimal"
        assert metadata.depends == "—"
        assert metadata.token_budget is None
        assert metadata.context_tier is None
        assert metadata.scope == "Minimal rule scope description."

    def test_extract_handles_missing_keywords(self, rule_file_missing_keywords, capsys):
        """Test extraction warns when Keywords field is missing."""
        metadata = extract_metadata(rule_file_missing_keywords)

        assert metadata.filename == "200-no-keywords.md"
        assert metadata.keywords == ""
        assert metadata.depends == "—"

        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "missing Keywords field" in captured.out

    def test_extract_handles_missing_scope(self, tmp_path, capsys):
        """Test extraction warns when Rule Scope section is missing (line 157)."""
        rule_file = tmp_path / "no-scope.md"
        content = """# Rule Without Scope

**Keywords:** test, validation
**Depends:** —
"""
        rule_file.write_text(content, encoding="utf-8")

        metadata = extract_metadata(rule_file)

        assert metadata.filename == "no-scope.md"
        assert metadata.scope == "No scope provided"

        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "missing ## Rule Scope section" in captured.out

    def test_extract_handles_depends_none(self, tmp_path):
        """Test Depends field normalization for None/— values."""
        rule_file = tmp_path / "test-depends.md"
        content = """# Test Depends

**Keywords:** test
**Depends:** None

## Rule Scope

Test scope.
"""
        rule_file.write_text(content, encoding="utf-8")

        metadata = extract_metadata(rule_file)
        assert metadata.depends == "—"

    def test_extract_handles_malformed_metadata(self, tmp_path):
        """Test extraction handles file read errors gracefully."""
        non_existent = tmp_path / "non-existent.md"

        with pytest.raises(ValueError, match="Failed to read"):
            extract_metadata(non_existent)

    def test_extract_scope_from_content_valid(self):
        """Test scope extraction from valid content."""
        content = """# Title

## Rule Scope

This is the scope description.

More content here.
"""
        scope = extract_scope_from_content(content)
        assert scope == "This is the scope description."

    def test_extract_scope_from_content_missing_section(self):
        """Test scope extraction when section is missing."""
        content = """# Title

## Some Other Section

Content here.
"""
        scope = extract_scope_from_content(content)
        assert scope == "No scope provided"

    def test_extract_scope_from_content_empty_section(self):
        """Test scope extraction when section is empty."""
        content = """# Title

## Rule Scope

## Next Section
"""
        scope = extract_scope_from_content(content)
        assert scope == "No scope provided"


@pytest.mark.unit
class TestIndexGenerator:
    """Test index generation functionality."""

    def test_scan_rules_finds_markdown_files(self, multiple_rule_files):
        """Test scanner finds .md files in directory."""
        rules = scan_rules(multiple_rule_files)

        assert len(rules) == 3
        assert rules[0].filename == "000-core.md"
        assert rules[1].filename == "100-python.md"
        assert rules[2].filename == "200-snowflake.md"

    def test_scan_rules_excludes_skip_files(self, multiple_rule_files):
        """Test scanner ignores files in SKIP_FILES."""
        rules = scan_rules(multiple_rule_files)

        filenames = [r.filename for r in rules]
        assert "README.md" not in filenames

    def test_scan_rules_handles_empty_directory(self, tmp_path):
        """Test scanner handles empty directory."""
        empty_dir = tmp_path / "empty_rules"
        empty_dir.mkdir()

        rules = scan_rules(empty_dir)
        assert rules == []

    def test_scan_rules_sorts_by_filename(self, tmp_path):
        """Test scanner sorts rules by filename."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        # Create files in non-sorted order
        for name in ["200-last.md", "000-first.md", "100-middle.md"]:
            rule_file = rules_dir / name
            content = f"""# {name}
**Keywords:** test
## Rule Scope
Test scope.
"""
            rule_file.write_text(content, encoding="utf-8")

        rules = scan_rules(rules_dir)

        assert len(rules) == 3
        assert rules[0].filename == "000-first.md"
        assert rules[1].filename == "100-middle.md"
        assert rules[2].filename == "200-last.md"

    def test_scan_rules_handles_general_exception(self, tmp_path, capsys, monkeypatch):
        """Test scanner handles general exceptions in extract_metadata (lines 189-191)."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        # Create a valid file
        rule_file = rules_dir / "valid.md"
        content = """# Valid Rule
**Keywords:** test
## Rule Scope
Test scope.
"""
        rule_file.write_text(content, encoding="utf-8")

        # Mock extract_metadata to raise a general exception
        def mock_extract_metadata(filepath):
            if filepath.name == "valid.md":
                raise RuntimeError("Unexpected error during processing")
            return None

        monkeypatch.setattr("scripts.index_generator.extract_metadata", mock_extract_metadata)

        rules = scan_rules(rules_dir)

        # Should catch and continue, returning empty list
        assert rules == []

        captured = capsys.readouterr()
        assert "Error processing" in captured.out
        assert "Unexpected error" in captured.out

    def test_scan_rules_handles_value_error(self, tmp_path, capsys, monkeypatch):
        """Test scanner handles ValueError exceptions in extract_metadata (lines 186-188)."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        # Create a valid file
        rule_file = rules_dir / "invalid.md"
        content = """# Invalid Rule
**Keywords:** test
## Rule Scope
Test scope.
"""
        rule_file.write_text(content, encoding="utf-8")

        # Mock extract_metadata to raise a ValueError
        def mock_extract_metadata(filepath):
            if filepath.name == "invalid.md":
                raise ValueError("Failed to read file: invalid.md")
            return None

        monkeypatch.setattr("scripts.index_generator.extract_metadata", mock_extract_metadata)

        rules = scan_rules(rules_dir)

        # Should catch and continue, returning empty list
        assert rules == []

        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "Failed to read" in captured.out

    def test_generate_table_row_formats_correctly(self, sample_rule_file):
        """Test table row generation produces valid markdown."""
        metadata = extract_metadata(sample_rule_file)
        row = generate_table_row(metadata)

        assert row.startswith("|")
        assert not row.startswith("||")
        assert "`100-test-rule.md`" in row
        assert "testing, validation, CI/CD" in row
        assert "`000-global-core.md`" in row
        assert "`001-foundations.md`" in row

    def test_generate_table_row_handles_no_dependencies(self, rule_file_minimal_metadata):
        """Test table row generation with no dependencies."""
        metadata = extract_metadata(rule_file_minimal_metadata)
        row = generate_table_row(metadata)

        assert "—" in row
        assert "`300-minimal.md`" in row

    def test_generate_rules_index_includes_all_sections(self, multiple_rule_files):
        """Test full index includes header, agent guidance, loading strategy, table, and footer."""
        rules = scan_rules(multiple_rule_files)
        index_content = generate_rules_index(rules)

        # Check for agent guidance section
        assert "For AI Agents:" in index_content
        assert "READ-ONLY" in index_content

        # Check for loading strategy section
        assert "Rule Loading Strategy" in index_content
        assert "Token Budget Management" in index_content

        # Check for table structure (standard markdown pipes)
        assert "| File | Scope | Keywords/Hints | Depends On |" in index_content
        assert "|------|-------|----------------|------------|" in index_content

        # Verify no double pipes (old format)
        assert (
            "||" not in index_content or "||" in index_content.split("```")[0]
        )  # Allow in code blocks

        # Check rules are present
        assert "`000-core.md`" in index_content
        assert "`100-python.md`" in index_content
        assert "`200-snowflake.md`" in index_content

        # Check footer is present
        assert "Common Rule Dependency Chains" in index_content

        # Verify section ordering (catalog header removed, so check table comes after strategy)
        agent_pos = index_content.find("For AI Agents:")
        strategy_pos = index_content.find("Rule Loading Strategy")
        table_pos = index_content.find("| File | Scope | Keywords/Hints | Depends On |")
        footer_pos = index_content.find("Common Rule Dependency Chains")

        assert agent_pos < strategy_pos < table_pos < footer_pos

    def test_generate_rules_index_empty_rules_list(self):
        """Test index generation with empty rules list."""
        index_content = generate_rules_index([])

        # Should still have agent guidance
        assert "For AI Agents:" in index_content

        # Should still have loading strategy
        assert "Rule Loading Strategy" in index_content

        # Should still have table structure (standard markdown pipes)
        assert "| File | Scope | Keywords/Hints | Depends On |" in index_content
        assert "|------|-------|----------------|------------|" in index_content

        # Should have footer
        assert "Common Rule Dependency Chains" in index_content


@pytest.mark.unit
class TestNewSections:
    """Test new sections in generated RULES_INDEX.md."""

    def test_generate_agent_guidance_returns_content(self):
        """Test agent guidance section generation."""
        guidance = generate_agent_guidance()

        assert len(guidance) > 0
        assert "READ-ONLY" in guidance
        assert "AI Agents" in guidance
        assert "grep" in guidance or "read_file" in guidance

    def test_generate_loading_strategy_returns_content(self):
        """Test loading strategy section generation."""
        strategy = generate_loading_strategy()

        assert len(strategy) > 0
        assert "Rule Loading Strategy" in strategy
        assert "Foundation" in strategy
        assert "Domain Rules" in strategy
        assert "Activity Rules" in strategy
        assert "Token Budget" in strategy

    def test_generate_loading_strategy_includes_example(self):
        """Test loading strategy includes worked example."""
        strategy = generate_loading_strategy()

        assert "Example Workflow" in strategy or "example" in strategy.lower()
        assert "Write tests for my Streamlit dashboard" in strategy

    def test_generate_loading_strategy_includes_six_steps(self):
        """Test loading strategy includes all 6 steps."""
        strategy = generate_loading_strategy()

        assert "### 1. Foundation" in strategy
        assert "### 2. Domain Rules" in strategy
        assert "### 3. Activity Rules" in strategy
        assert "### 4. Check Dependencies" in strategy
        assert "### 5. Token Budget Management" in strategy
        assert "### 6. Declare Loaded Rules" in strategy


@pytest.mark.unit
class TestIndexGeneratorCLI:
    """Test CLI functionality."""

    def test_main_normal_mode_generates_index(self, multiple_rule_files, tmp_path, monkeypatch):
        """Test CLI generates index in normal mode."""
        # Change to tmp_path so RULES_INDEX.md is created there
        monkeypatch.chdir(tmp_path)
        output_file = tmp_path / "RULES_INDEX.md"

        # Mock sys.argv
        test_args = [
            "index_generator.py",
            "--rules-dir",
            str(multiple_rule_files),
        ]
        monkeypatch.setattr(sys, "argv", test_args)

        # Run main
        exit_code = main()

        assert exit_code == 0
        assert output_file.exists()

        # Verify content
        content = output_file.read_text()
        assert "`000-core.md`" in content
        assert "`100-python.md`" in content

    def test_main_dry_run_prints_without_writing(
        self, multiple_rule_files, tmp_path, monkeypatch, capsys
    ):
        """Test --dry-run prints but doesn't write."""
        monkeypatch.chdir(tmp_path)
        output_file = tmp_path / "RULES_INDEX.md"

        test_args = [
            "index_generator.py",
            "--rules-dir",
            str(multiple_rule_files),
            "--dry-run",
        ]
        monkeypatch.setattr(sys, "argv", test_args)

        exit_code = main()

        assert exit_code == 0
        assert not output_file.exists()

        # Should print to stdout
        captured = capsys.readouterr()
        assert "`000-core.md`" in captured.out

    def test_main_check_mode_detects_outdated(
        self, multiple_rule_files, outdated_index_file, tmp_path, monkeypatch
    ):
        """Test --check mode fails when index is outdated."""
        # Change to directory where outdated_index_file exists
        monkeypatch.chdir(outdated_index_file.parent)

        test_args = [
            "index_generator.py",
            "--rules-dir",
            str(multiple_rule_files),
            "--check",
        ]
        monkeypatch.setattr(sys, "argv", test_args)

        exit_code = main()

        # Should exit with error when outdated
        assert exit_code == 1

    def test_main_check_mode_missing_index_file(
        self, multiple_rule_files, tmp_path, monkeypatch, capsys
    ):
        """Test --check mode fails when RULES_INDEX.md doesn't exist (lines 507-509)."""
        monkeypatch.chdir(tmp_path)

        test_args = [
            "index_generator.py",
            "--rules-dir",
            str(multiple_rule_files),
            "--check",
        ]
        monkeypatch.setattr(sys, "argv", test_args)

        exit_code = main()

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "RULES_INDEX.md does not exist" in captured.out

    def test_main_check_mode_succeeds_when_current(
        self, multiple_rule_files, tmp_path, monkeypatch
    ):
        """Test --check mode succeeds when index is current."""
        monkeypatch.chdir(tmp_path)
        output_file = tmp_path / "RULES_INDEX.md"

        # First generate the index
        rules = scan_rules(multiple_rule_files)
        index_content = generate_rules_index(rules)
        output_file.write_text(index_content, encoding="utf-8")

        # Now check it
        test_args = [
            "index_generator.py",
            "--rules-dir",
            str(multiple_rule_files),
            "--check",
        ]
        monkeypatch.setattr(sys, "argv", test_args)

        exit_code = main()

        assert exit_code == 0

    def test_main_invalid_rules_directory(self, tmp_path, monkeypatch, capsys):
        """Test main exits with error for non-existent directory."""
        non_existent = tmp_path / "non_existent_rules"

        test_args = [
            "index_generator.py",
            "--rules-dir",
            str(non_existent),
        ]
        monkeypatch.setattr(sys, "argv", test_args)

        exit_code = main()

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "Error" in captured.out or "not found" in captured.out

    def test_main_auto_detect_rules_directory_success(self, tmp_path, monkeypatch, capsys):
        """Test CLI auto-detects rules/ directory when not specified (lines 461-464)."""
        # Create rules/ directory in tmp_path
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        # Create test rule files
        for name in ["000-core.md", "100-python.md"]:
            rule_file = rules_dir / name
            content = f"""# {name}
**Keywords:** test
## Rule Scope
Test scope.
"""
            rule_file.write_text(content, encoding="utf-8")

        # Change to tmp_path so auto-detection finds rules/
        monkeypatch.chdir(tmp_path)

        test_args = ["index_generator.py"]
        monkeypatch.setattr(sys, "argv", test_args)

        exit_code = main()

        assert exit_code == 0

        captured = capsys.readouterr()
        assert "Using rules/ directory" in captured.out

    def test_main_auto_detect_rules_directory_not_found(self, tmp_path, monkeypatch, capsys):
        """Test CLI fails when auto-detect doesn't find rules/ (lines 465-467)."""
        # Change to tmp_path where there's no rules/ directory
        monkeypatch.chdir(tmp_path)

        test_args = ["index_generator.py"]
        monkeypatch.setattr(sys, "argv", test_args)

        exit_code = main()

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "rules/ directory not found" in captured.out

    def test_main_scan_error(self, tmp_path, monkeypatch, capsys):
        """Test CLI handles scan_rules exceptions (lines 477-479)."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        monkeypatch.chdir(tmp_path)

        # Mock scan_rules to raise an exception
        def mock_scan_rules(path):
            raise RuntimeError("Failed to scan rules")

        monkeypatch.setattr("scripts.index_generator.scan_rules", mock_scan_rules)

        test_args = ["index_generator.py", "--rules-dir", str(rules_dir)]
        monkeypatch.setattr(sys, "argv", test_args)

        exit_code = main()

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "Error scanning rules" in captured.out

    def test_main_no_rules_found(self, tmp_path, monkeypatch, capsys):
        """Test CLI fails when no rules are found (lines 481-483)."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        test_args = ["index_generator.py", "--rules-dir", str(rules_dir)]
        monkeypatch.setattr(sys, "argv", test_args)

        exit_code = main()

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "No rule files found" in captured.out

    def test_main_generation_error(self, multiple_rule_files, tmp_path, monkeypatch, capsys):
        """Test CLI handles generate_rules_index exceptions (lines 490-492)."""
        monkeypatch.chdir(tmp_path)

        # Mock generate_rules_index to raise an exception
        def mock_generate_rules_index(rules):
            raise RuntimeError("Failed to generate index")

        monkeypatch.setattr(
            "scripts.index_generator.generate_rules_index", mock_generate_rules_index
        )

        test_args = ["index_generator.py", "--rules-dir", str(multiple_rule_files)]
        monkeypatch.setattr(sys, "argv", test_args)

        exit_code = main()

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "Error generating RULES_INDEX.md" in captured.out

    def test_main_check_mode_read_error(self, multiple_rule_files, tmp_path, monkeypatch, capsys):
        """Test --check mode handles file read errors (lines 513-515)."""
        monkeypatch.chdir(tmp_path)
        output_file = tmp_path / "RULES_INDEX.md"
        output_file.write_text("dummy content", encoding="utf-8")

        # Mock read_text to raise an exception
        original_read_text = Path.read_text

        def mock_read_text(self, *args, **kwargs):
            if self.name == "RULES_INDEX.md":
                raise PermissionError("Permission denied")
            return original_read_text(self, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", mock_read_text)

        test_args = [
            "index_generator.py",
            "--rules-dir",
            str(multiple_rule_files),
            "--check",
        ]
        monkeypatch.setattr(sys, "argv", test_args)

        exit_code = main()

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "Error reading RULES_INDEX.md" in captured.out

    def test_main_write_error(self, multiple_rule_files, tmp_path, monkeypatch, capsys):
        """Test normal mode handles file write errors (lines 535-537)."""
        monkeypatch.chdir(tmp_path)

        # Mock write_text to raise an exception
        original_write_text = Path.write_text

        def mock_write_text(self, *args, **kwargs):
            if self.name == "RULES_INDEX.md":
                raise PermissionError("Permission denied")
            return original_write_text(self, *args, **kwargs)

        monkeypatch.setattr(Path, "write_text", mock_write_text)

        test_args = ["index_generator.py", "--rules-dir", str(multiple_rule_files)]
        monkeypatch.setattr(sys, "argv", test_args)

        exit_code = main()

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "Error writing RULES_INDEX.md" in captured.out


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_extract_metadata_with_unicode_content(self, tmp_path):
        """Test extraction handles unicode characters."""
        rule_file = tmp_path / "unicode-rule.md"
        content = """# Unicode Rule 🚀

**Keywords:** unicode, émojis, 中文
**Depends:** —

## Rule Scope

This rule contains unicode: café, naïve, 日本語
"""
        rule_file.write_text(content, encoding="utf-8")

        metadata = extract_metadata(rule_file)
        assert metadata.keywords == "unicode, émojis, 中文"
        assert "café" in metadata.scope or "unicode" in metadata.scope

    def test_generate_table_row_escapes_pipe_characters(self, tmp_path):
        """Test table row generation handles pipe characters in content."""
        rule_file = tmp_path / "pipes.md"
        content = """# Pipes Rule

**Keywords:** test
**Depends:** —

## Rule Scope

Scope with | pipe characters.
"""
        rule_file.write_text(content, encoding="utf-8")

        metadata = extract_metadata(rule_file)
        row = generate_table_row(metadata)

        # Should still be valid markdown table row (single pipe start)
        assert row.startswith("|")
        assert not row.startswith("||")
        assert "`pipes.md`" in row

    def test_scan_rules_handles_nested_directories(self, tmp_path):
        """Test scanner finds rules in nested directories."""
        rules_dir = tmp_path / "rules"
        nested_dir = rules_dir / "nested"
        nested_dir.mkdir(parents=True)

        # Create rule in nested directory
        rule_file = nested_dir / "nested-rule.md"
        content = """# Nested Rule
**Keywords:** nested
## Rule Scope
Nested scope.
"""
        rule_file.write_text(content, encoding="utf-8")

        rules = scan_rules(rules_dir)

        assert len(rules) == 1
        assert rules[0].filename == "nested-rule.md"

    def test_extract_depends_adds_md_extension(self, tmp_path):
        """Test Depends field automatically adds .md extension."""
        rule_file = tmp_path / "depends-test.md"
        content = """# Depends Test

**Keywords:** test
**Depends:** 000-core, 100-python

## Rule Scope

Test scope.
"""
        rule_file.write_text(content, encoding="utf-8")

        metadata = extract_metadata(rule_file)
        assert metadata.depends == "000-core.md, 100-python.md"

    def test_extract_metadata_large_file(self, tmp_path):
        """Test extraction handles large files efficiently."""
        rule_file = tmp_path / "large-rule.md"

        # Create large content (metadata should still be in first 30 lines)
        content = """# Large Rule

**Keywords:** large, performance
**Depends:** —

## Rule Scope

Large rule scope.

"""
        # Add 1000 lines of content
        content += "\n".join([f"Line {i}" for i in range(1000)])

        rule_file.write_text(content, encoding="utf-8")

        metadata = extract_metadata(rule_file)
        assert metadata.filename == "large-rule.md"
        assert metadata.keywords == "large, performance"
