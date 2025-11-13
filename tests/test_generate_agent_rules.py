"""Tests for the generate_agent_rules module."""

import tempfile
from pathlib import Path

# Import the module we're testing
import generate_agent_rules as gar
import pytest


class TestRuleGenerator:
    """Test the main rule generator functionality."""

    def test_strip_existing_yaml_header(self):
        """Test removing YAML frontmatter from content."""
        # Test content with YAML header
        content_with_yaml = """---
description: "Test rule"
globs:
  - "**/*.py"
---

# Rule Content

This is the actual rule content.
"""
        expected = """
# Rule Content

This is the actual rule content.
"""
        result = gar.strip_existing_yaml_header(content_with_yaml)
        assert result == expected

        # Test content without YAML header
        content_without_yaml = "# Rule Content\n\nThis is rule content."
        result = gar.strip_existing_yaml_header(content_without_yaml)
        assert result == content_without_yaml

    def test_strip_markdown_metadata_lines(self):
        """Test removing metadata lines from markdown content."""
        content = """**Description:** This is a test rule
**AppliesTo:** `**/*.py`, `**/*.sql`
**AutoAttach:** true
**Version:** 1.0

# Test Rule

This is the rule content.
"""
        expected = """
# Test Rule

This is the rule content.
"""
        result = gar.strip_markdown_metadata_lines(content)
        assert result == expected

    def test_parse_applies_to(self):
        """Test parsing 'AppliesTo' patterns."""
        # Test backtick format
        content_backticks = "**AppliesTo:** `**/*.py`, `**/*.sql`"
        result = gar.parse_applies_to(content_backticks)
        assert result == ["**/*.py", "**/*.sql"]

        # Test comma-separated format
        content_comma = "**AppliesTo:** *.py, *.sql, *.md"
        result = gar.parse_applies_to(content_comma)
        assert result == ["*.py", "*.sql", "*.md"]

        # Test no applies to
        content_empty = "# Some content\nNo applies to here"
        result = gar.parse_applies_to(content_empty)
        assert result == []

    def test_serialize_list_yaml(self):
        """Test YAML list serialization."""
        result = gar.serialize_list_yaml("globs", ["**/*.py", "**/*.sql"], "**/*")
        expected = """---
globs:
  - "**/*.py"
  - "**/*.sql"
---
"""
        assert result == expected

        # Test empty list uses default
        result = gar.serialize_list_yaml("globs", [], "**/*")
        expected = """---
globs:
  - "**/*"
---
"""
        assert result == expected


class TestAgentSpec:
    """Test agent-specific specifications."""

    def test_cursor_spec_build_header(self):
        """Test Cursor-specific header generation."""
        spec = gar.AgentSpec(
            name="cursor", dest_dir=Path(".cursor/rules"), header_key="globs", prepend_comment=None
        )

        patterns = ["**/*.py", "**/*.sql"]
        description = "Test rule for Python and SQL files"
        header = spec.build_header(patterns, description, always_apply=True)

        assert 'description: "Test rule for Python and SQL files"' in header
        assert '"**/*.py"' in header
        assert '"**/*.sql"' in header
        assert "alwaysApply: true" in header

    def test_copilot_spec_build_header(self):
        """Test Copilot-specific header generation."""
        spec = gar.AgentSpec(
            name="copilot",
            dest_dir=Path(".github/instructions"),
            header_key="appliesTo",
            prepend_comment=None,
        )

        patterns = ["**/*.py"]
        header = spec.build_header(patterns)

        assert "appliesTo:" in header
        assert '"**/*.py"' in header


class TestAgentRuleGenerator:
    """Test the main rule generator class."""

    def test_initialization_cursor(self):
        """Test initialization for Cursor agent."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source"
            dest = Path(temp_dir) / "dest"

            generator = gar.AgentRuleGenerator("cursor", source, dest)

            assert generator.agent == "cursor"
            assert generator.source == source
            assert generator.destination == dest
            assert generator.spec.name == "cursor"
            assert generator.spec.header_key == "globs"

    def test_initialization_copilot(self):
        """Test initialization for Copilot agent."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source"
            dest = Path(temp_dir) / "dest"

            generator = gar.AgentRuleGenerator("copilot", source, dest)

            assert generator.agent == "copilot"
            assert generator.spec.name == "copilot"
            assert generator.spec.header_key == "appliesTo"

    def test_initialization_invalid_agent(self):
        """Test initialization with invalid agent."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source"
            dest = Path(temp_dir) / "dest"

            with pytest.raises(ValueError, match="agent must be one of"):
                gar.AgentRuleGenerator("invalid", source, dest)

    def test_parse_description_and_autoattach(self):
        """Test parsing description and auto-attach from content."""
        content = """**Description:** Test rule description
**AutoAttach:** true

# Rule Content
"""
        result = gar.AgentRuleGenerator._parse_description_and_autoattach(content, "fallback")
        description, _, always_apply = result

        assert description == "Test rule description"
        assert always_apply

        # Test fallback description
        content_no_desc = "# Rule Content\nNo description here"
        result = gar.AgentRuleGenerator._parse_description_and_autoattach(
            content_no_desc, "fallback"
        )
        description, _, always_apply = result

        assert description == "fallback"
        assert always_apply is None


def test_rule_files_exist():
    """Test that expected rule files exist in the repository."""
    # Rule files are in templates/, scripts are in scripts/
    expected_files = {
        "templates/000-global-core.md": "Rule file",
        "templates/100-snowflake-core.md": "Rule file",
        "templates/200-python-core.md": "Rule file",
        "scripts/generate_agent_rules.py": "Generator script",
        "README.md": "Project README",
    }

    for file_path, description in expected_files.items():
        assert Path(file_path).exists(), f"Expected {description} {file_path} not found"


def test_readme_has_required_sections():
    """Test that README contains required sections."""
    readme_path = Path("README.md")
    if readme_path.exists():
        content = readme_path.read_text()

        required_sections = [
            "# AI Coding Rules",
            "## Quick Start",
            "## Rule Categories",
            "## Rule Generator Architecture",
            "## Contributing",
        ]

        for section in required_sections:
            assert section in content, f"README missing required section: {section}"
