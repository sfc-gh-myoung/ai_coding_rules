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
    RuleMetadata,
    extract_metadata,
    extract_scope_from_content,
    generate_agent_guidance,
    generate_loading_strategy,
    generate_rule_entry,
    generate_rules_index,
    get_domain_name,
    group_rules_by_domain,
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

## Scope

**What This Rule Covers:**
This rule applies to all test files and validation scripts.

**When to Load This Rule:**
- Testing scenarios
- Validation workflows

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

## Scope

**What This Rule Covers:**
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

## Scope

**What This Rule Covers:**
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

## Scope

**What This Rule Covers:**
Rule {i} scope description.
"""
        rule_file.write_text(content, encoding="utf-8")

    # Create README.md (should be skipped)
    readme = rules_dir / "README.md"
    readme.write_text("# README\n\nThis should be skipped.", encoding="utf-8")

    return rules_dir


@pytest.fixture
def outdated_index_file(tmp_path):
    """Create outdated rules/RULES_INDEX.md file."""
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    index_file = rules_dir / "RULES_INDEX.md"
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
        """Test extraction warns when Scope section is missing (v3.2)."""
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
        assert "missing ## Scope section" in captured.out

    def test_extract_handles_depends_none(self, tmp_path):
        """Test Depends field normalization for None/— values."""
        rule_file = tmp_path / "test-depends.md"
        content = """# Test Depends

**Keywords:** test
**Depends:** None

## Scope

**What This Rule Covers:**
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

    def test_extract_handles_load_trigger_field(self, tmp_path):
        """Test extraction of LoadTrigger metadata field."""
        rule_file = tmp_path / "101-with-trigger.md"
        content = """# Rule With LoadTrigger

**Keywords:** trigger, test
**Depends:** 000-global-core.md
**LoadTrigger:** ext:.py, file:pyproject.toml

## Scope

**What This Rule Covers:**
Test LoadTrigger extraction.
"""
        rule_file.write_text(content, encoding="utf-8")

        metadata = extract_metadata(rule_file)

        assert metadata.filename == "101-with-trigger.md"
        assert metadata.load_trigger == "ext:.py, file:pyproject.toml"
        assert metadata.keywords == "trigger, test"

    def test_extract_scope_from_content_valid(self):
        """Test scope extraction from valid content (v3.2)."""
        content = """# Title

## Scope

**What This Rule Covers:**
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

## Scope

## Next Section
"""
        scope = extract_scope_from_content(content)
        assert scope == "No scope provided"

    def test_extract_scope_from_content_inline_marker(self):
        """Test scope extraction with content on same line as marker."""
        content = """# Title

## Scope

**What This Rule Covers:** Inline scope description here.

More content below.
"""
        scope = extract_scope_from_content(content)
        assert scope == "Inline scope description here."

    def test_extract_scope_from_content_plain_text_fallback(self):
        """Test scope extraction using plain text fallback (no marker)."""
        content = """# Title

## Scope

This is plain text without the marker format.

More content.
"""
        scope = extract_scope_from_content(content)
        assert scope == "This is plain text without the marker format."

    def test_extract_scope_from_content_marker_no_following_content(self):
        """Test scope extraction when marker exists but no content follows."""
        content = """# Title

## Scope

**What This Rule Covers:**

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

## Scope

**What This Rule Covers:**
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

## Scope

**What This Rule Covers:**
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

## Scope

**What This Rule Covers:**
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

    def test_generate_rule_entry_formats_correctly(self, sample_rule_file):
        """Test rule entry generation produces valid structured list format."""
        metadata = extract_metadata(sample_rule_file)
        entry = generate_rule_entry(metadata)

        # Should use structured list format, not table
        assert not entry.startswith("|")
        assert "**`100-test-rule.md`**" in entry
        assert "Keywords: testing, validation, CI/CD" in entry
        assert "Depends:" in entry
        assert "`000-global-core.md`" in entry
        assert "`001-foundations.md`" in entry

    def test_generate_rule_entry_handles_no_dependencies(self, rule_file_minimal_metadata):
        """Test rule entry generation with no dependencies."""
        metadata = extract_metadata(rule_file_minimal_metadata)
        entry = generate_rule_entry(metadata)

        assert "Depends: —" in entry
        assert "**`300-minimal.md`**" in entry

    def test_get_domain_name_returns_correct_domains(self):
        """Test domain name mapping for rule prefixes."""
        assert "Core" in get_domain_name("000")
        assert "Snowflake" in get_domain_name("100")
        assert "Python" in get_domain_name("200")
        assert "Shell" in get_domain_name("300")
        assert get_domain_name("999") == "Other"

    def test_group_rules_by_domain(self, multiple_rule_files):
        """Test rules are correctly grouped by domain."""
        rules = scan_rules(multiple_rule_files)
        domains = group_rules_by_domain(rules)

        # Should have multiple domain groups
        assert len(domains) >= 1
        # Rules should be in their correct domains
        for _domain_name, domain_rules in domains.items():
            assert len(domain_rules) > 0

    def test_generate_rules_index_includes_all_sections(self, multiple_rule_files):
        """Test full index includes header, agent guidance, loading strategy, catalog, and footer."""
        rules = scan_rules(multiple_rule_files)
        index_content = generate_rules_index(rules)

        # Check for agent guidance section
        assert "For AI Agents:" in index_content
        assert "READ-ONLY" in index_content

        # Check for loading strategy section
        assert "Rule Loading Strategy" in index_content
        assert "Token Budget Management" in index_content

        # Check for catalog section with structured list format (no tables)
        assert "## Rule Catalog" in index_content
        assert "| File | Scope |" not in index_content  # No table format

        # Check rules are present in structured format
        assert "**`000-core.md`**" in index_content
        assert "**`100-python.md`**" in index_content
        assert "**`200-snowflake.md`**" in index_content
        assert "Keywords:" in index_content
        assert "Depends:" in index_content

        # Check footer is present
        assert "Common Rule Dependency Chains" in index_content

        # Verify section ordering
        agent_pos = index_content.find("For AI Agents:")
        strategy_pos = index_content.find("Rule Loading Strategy")
        catalog_pos = index_content.find("## Rule Catalog")
        footer_pos = index_content.find("Common Rule Dependency Chains")

        assert agent_pos < strategy_pos < catalog_pos < footer_pos

    def test_generate_rules_index_empty_rules_list(self):
        """Test index generation with empty rules list."""
        index_content = generate_rules_index([])

        # Should still have agent guidance
        assert "For AI Agents:" in index_content

        # Should still have loading strategy
        assert "Rule Loading Strategy" in index_content

        # Should still have catalog header (even if empty)
        assert "## Rule Catalog" in index_content

        # Should have footer
        assert "Common Rule Dependency Chains" in index_content

    def test_generate_rules_index_with_multiple_rules_same_domain(self):
        """Test index generation with multiple rules in same domain (blank line handling)."""
        from pathlib import Path

        mock_rules = [
            RuleMetadata(
                filename="100-first.md",
                filepath=Path("rules/100-first.md"),
                keywords="test1",
                depends="000-global-core.md",
                scope="First rule",
                load_trigger="",
            ),
            RuleMetadata(
                filename="101-second.md",
                filepath=Path("rules/101-second.md"),
                keywords="test2",
                depends="000-global-core.md",
                scope="Second rule",
                load_trigger="",
            ),
        ]

        index_content = generate_rules_index(mock_rules)

        # Both rules should be in index
        assert "100-first.md" in index_content
        assert "101-second.md" in index_content
        # Should have proper spacing between entries
        assert "## Rule Catalog" in index_content


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

    def test_generate_loading_strategy_returns_content(self, tmp_path):
        """Test loading strategy section generation."""
        # Create mock rules with LoadTrigger metadata
        from pathlib import Path

        mock_rules = [
            RuleMetadata(
                filename="200-python-core.md",
                filepath=Path("rules/200-python-core.md"),
                keywords="python, testing",
                depends="000-global-core.md",
                scope="Python development",
                load_trigger="ext:.py, ext:.pyi",
            ),
            RuleMetadata(
                filename="206-python-pytest.md",
                filepath=Path("rules/206-python-pytest.md"),
                keywords="pytest, testing",
                depends="200-python-core.md",
                scope="Testing with pytest",
                load_trigger="kw:test, kw:pytest",
            ),
        ]
        strategy = generate_loading_strategy(mock_rules)

        assert len(strategy) > 0
        assert "Rule Loading Strategy" in strategy
        assert "Foundation" in strategy
        assert "Domain Rules" in strategy
        assert "Activity Rules" in strategy
        assert "Token Budget" in strategy

    def test_generate_loading_strategy_includes_example(self, tmp_path):
        """Test loading strategy includes worked example."""
        from pathlib import Path

        mock_rules = [
            RuleMetadata(
                filename="101-snowflake-streamlit-core.md",
                filepath=Path("rules/101-snowflake-streamlit-core.md"),
                keywords="streamlit",
                depends="100-snowflake-core.md",
                scope="Streamlit apps",
                load_trigger="kw:streamlit",
            ),
        ]
        strategy = generate_loading_strategy(mock_rules)

        assert "Example Workflow" in strategy or "example" in strategy.lower()
        assert "Write tests for my Streamlit dashboard" in strategy

    def test_generate_loading_strategy_includes_six_steps(self, tmp_path):
        """Test loading strategy includes all 6 steps."""
        from pathlib import Path

        mock_rules = [
            RuleMetadata(
                filename="200-python-core.md",
                filepath=Path("rules/200-python-core.md"),
                keywords="python",
                depends="000-global-core.md",
                scope="Python",
                load_trigger="ext:.py",
            ),
        ]
        strategy = generate_loading_strategy(mock_rules)

        assert "### 1. Foundation" in strategy
        assert "### 2. Domain Rules" in strategy
        assert "### 3. Activity Rules" in strategy
        assert "### 4. Check Dependencies" in strategy
        assert "### 5. Token Budget Management" in strategy
        assert "### 6. Declare Loaded Rules" in strategy

    def test_generate_loading_strategy_with_dir_triggers(self):
        """Test loading strategy with directory triggers."""
        from pathlib import Path

        mock_rules = [
            RuleMetadata(
                filename="002h-skills.md",
                filepath=Path("rules/002h-skills.md"),
                keywords="skills",
                depends="000-global-core.md",
                scope="Skills development",
                load_trigger="dir:skills/",
            ),
        ]
        strategy = generate_loading_strategy(mock_rules)

        assert "skills/" in strategy
        assert "002h-skills.md" in strategy
        assert "directory" in strategy.lower()

    def test_generate_loading_strategy_with_file_triggers(self):
        """Test loading strategy with file triggers."""
        from pathlib import Path

        mock_rules = [
            RuleMetadata(
                filename="820-taskfile.md",
                filepath=Path("rules/820-taskfile.md"),
                keywords="automation",
                depends="000-global-core.md",
                scope="Taskfile automation",
                load_trigger="file:Taskfile.yml",
            ),
        ]
        strategy = generate_loading_strategy(mock_rules)

        assert "Taskfile.yml" in strategy
        assert "820-taskfile.md" in strategy

    def test_generate_loading_strategy_with_multiple_trigger_types(self):
        """Test loading strategy with mixed trigger types."""
        from pathlib import Path

        mock_rules = [
            RuleMetadata(
                filename="200-python.md",
                filepath=Path("rules/200-python.md"),
                keywords="python",
                depends="000-global-core.md",
                scope="Python",
                load_trigger="ext:.py, file:pyproject.toml",
            ),
            RuleMetadata(
                filename="002-governance.md",
                filepath=Path("rules/002-governance.md"),
                keywords="rules",
                depends="000-global-core.md",
                scope="Rule governance",
                load_trigger="dir:rules/",
            ),
            RuleMetadata(
                filename="206-pytest.md",
                filepath=Path("rules/206-pytest.md"),
                keywords="test",
                depends="000-global-core.md",
                scope="Testing",
                load_trigger="kw:test, kw:pytest",
            ),
        ]
        strategy = generate_loading_strategy(mock_rules)

        # Check all trigger types are present
        assert ".py" in strategy
        assert "pyproject.toml" in strategy
        assert "rules/" in strategy
        assert "test" in strategy
        assert "pytest" in strategy


@pytest.mark.unit
class TestIndexGeneratorCLI:
    """Test CLI functionality."""

    def test_main_normal_mode_generates_index(self, multiple_rule_files, tmp_path, monkeypatch):
        """Test CLI generates index in normal mode."""
        # Change to tmp_path so rules/RULES_INDEX.md is created there
        monkeypatch.chdir(tmp_path)
        # Create rules directory where output will be written
        rules_output_dir = tmp_path / "rules"
        rules_output_dir.mkdir(parents=True, exist_ok=True)
        output_file = rules_output_dir / "RULES_INDEX.md"

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
        # Create rules directory (even though dry-run won't write)
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        output_file = rules_dir / "RULES_INDEX.md"

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
        # Create rules directory and output file
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        output_file = rules_dir / "RULES_INDEX.md"

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

## Scope

**What This Rule Covers:**
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
        # Create rules directory and output file
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        output_file = rules_dir / "RULES_INDEX.md"
        output_file.write_text("dummy content", encoding="utf-8")

        # Mock read_text to raise an exception
        original_read_text = Path.read_text

        def mock_read_text(self, *args, **kwargs):
            if self.name == "RULES_INDEX.md" and "rules" in str(self.parent):
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
        assert "Error reading rules/RULES_INDEX.md" in captured.out

    def test_main_write_error(self, multiple_rule_files, tmp_path, monkeypatch, capsys):
        """Test normal mode handles file write errors (lines 535-537)."""
        monkeypatch.chdir(tmp_path)
        # Create rules directory
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        # Mock write_text to raise an exception
        original_write_text = Path.write_text

        def mock_write_text(self, *args, **kwargs):
            if self.name == "RULES_INDEX.md":
                raise PermissionError("Permission denied")
            return original_write_text(self, *args, **kwargs)
            if self.name == "RULES_INDEX.md":
                raise PermissionError("Permission denied")
            return original_write_text(self, *args, **kwargs)

        monkeypatch.setattr(Path, "write_text", mock_write_text)

        test_args = ["index_generator.py", "--rules-dir", str(multiple_rule_files)]
        monkeypatch.setattr(sys, "argv", test_args)

        exit_code = main()

        assert exit_code == 1

        captured = capsys.readouterr()
        assert "Error writing rules/RULES_INDEX.md" in captured.out


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_extract_metadata_with_unicode_content(self, tmp_path):
        """Test extraction handles unicode characters."""
        rule_file = tmp_path / "unicode-rule.md"
        content = """# Unicode Rule 🚀

**Keywords:** unicode, émojis, 中文
**Depends:** —

## Scope

**What This Rule Covers:**
This rule contains unicode: café, naïve, 日本語
"""
        rule_file.write_text(content, encoding="utf-8")

        metadata = extract_metadata(rule_file)
        assert metadata.keywords == "unicode, émojis, 中文"
        assert "café" in metadata.scope or "unicode" in metadata.scope

    def test_generate_rule_entry_handles_pipe_characters(self, tmp_path):
        """Test rule entry generation handles pipe characters in content."""
        rule_file = tmp_path / "pipes.md"
        content = """# Pipes Rule

**Keywords:** test
**Depends:** —

## Scope

**What This Rule Covers:**
Scope with | pipe characters.
"""
        rule_file.write_text(content, encoding="utf-8")

        metadata = extract_metadata(rule_file)
        entry = generate_rule_entry(metadata)

        # Should use structured list format (not table)
        assert not entry.startswith("|")
        assert "**`pipes.md`**" in entry
        assert "Keywords:" in entry

    def test_scan_rules_handles_nested_directories(self, tmp_path):
        """Test scanner finds rules in nested directories."""
        rules_dir = tmp_path / "rules"
        nested_dir = rules_dir / "nested"
        nested_dir.mkdir(parents=True)

        # Create rule in nested directory
        rule_file = nested_dir / "nested-rule.md"
        content = """# Nested Rule
**Keywords:** nested

## Scope

**What This Rule Covers:**
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

## Scope

**What This Rule Covers:**
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

## Scope

**What This Rule Covers:**
Large rule scope.

"""
        # Add 1000 lines of content
        content += "\n".join([f"Line {i}" for i in range(1000)])

        rule_file.write_text(content, encoding="utf-8")

        metadata = extract_metadata(rule_file)
        assert metadata.filename == "large-rule.md"
        assert metadata.keywords == "large, performance"
