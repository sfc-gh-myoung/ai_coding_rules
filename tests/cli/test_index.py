"""Tests for ai-rules index command.

Tests follow pytest best practices:
- AAA pattern (Arrange-Act-Assert)
- Function-scoped fixtures
- Test markers for selective execution
- Isolation with tmp_path
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands import index as index_module

runner = CliRunner()


# Sample rule content for testing
SAMPLE_RULE_CONTENT = dedent("""\
    # 000-global-core: Core Foundation

    ## Metadata

    **SchemaVersion:** v3.2
    **RuleVersion:** v1.0.0
    **LastUpdated:** 2024-01-01
    **Keywords:** core, foundation, global, standards
    **TokenBudget:** ~3300
    **ContextTier:** Critical
    **Depends:** None

    ## Scope

    **What This Rule Covers:**
    Core foundation rules for all projects.

    **When to Load This Rule:**
    - Always load for any task
""")

SAMPLE_RULE_200 = dedent("""\
    # 200-python-core: Python Core

    ## Metadata

    **SchemaVersion:** v3.2
    **RuleVersion:** v1.0.0
    **LastUpdated:** 2024-01-01
    **Keywords:** python, development, best practices
    **TokenBudget:** ~1800
    **ContextTier:** High
    **Depends:** 000-global-core.md
    **LoadTrigger:** ext:.py, ext:.pyi

    ## Scope

    **What This Rule Covers:**
    Python development best practices.

    **When to Load This Rule:**
    - When working with Python files
""")


class TestIndexHelp:
    """Test --help output."""

    @pytest.mark.unit
    def test_help_shows_description(self):
        """Test --help shows command description."""
        result = runner.invoke(app, ["index", "--help"])
        assert result.exit_code == 0
        assert "Generate RULES_INDEX.md" in result.output
        assert "--check" in result.output
        assert "--dry-run" in result.output
        assert "--rules-dir" in result.output

    @pytest.mark.unit
    def test_help_shows_examples(self):
        """Test --help includes usage examples."""
        result = runner.invoke(app, ["index", "--help"])
        assert result.exit_code == 0
        assert "ai-rules index" in result.output


class TestIndexHappyPath:
    """Test successful index generation scenarios."""

    @pytest.mark.unit
    def test_generates_index_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test successful index generation."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        assert "Found 2 rule files" in result.output
        assert "Generated" in result.output

        # Check file was created
        index_file = rules_dir / "RULES_INDEX.md"
        assert index_file.exists()

        content = index_file.read_text()
        assert "AUTO-GENERATED FILE" in content
        assert "000-global-core.md" in content
        assert "200-python-core.md" in content
        assert "Core Foundation (000-series)" in content
        assert "Python (200-series)" in content

    @pytest.mark.unit
    def test_generates_with_metadata(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test index includes all metadata fields."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0

        content = (rules_dir / "RULES_INDEX.md").read_text()
        # Check metadata is included
        assert "Keywords:" in content
        assert "core, foundation, global, standards" in content
        assert "Depends:" in content

    @pytest.mark.unit
    def test_overwrites_existing_index(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test that existing RULES_INDEX.md is overwritten."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        # Create existing index with different content
        index_file = rules_dir / "RULES_INDEX.md"
        index_file.write_text("# Old Index\nThis should be overwritten")

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        content = index_file.read_text()
        assert "Old Index" not in content
        assert "AUTO-GENERATED FILE" in content


class TestIndexCheckMode:
    """Test --check mode for CI."""

    @pytest.mark.unit
    def test_check_passes_when_up_to_date(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test --check returns 0 when index is up-to-date."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # First, generate the index
        runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Act - run check
        result = runner.invoke(app, ["index", "--check", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        assert "up-to-date" in result.output

    @pytest.mark.unit
    def test_check_fails_when_outdated(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test --check returns 1 when index is outdated."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        # Create an outdated index
        index_file = rules_dir / "RULES_INDEX.md"
        index_file.write_text("# Old Index\nThis is outdated content")

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--check", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 1
        assert "out of date" in result.output

    @pytest.mark.unit
    def test_check_fails_when_index_missing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test --check returns 1 when index doesn't exist."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--check", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 1
        assert "does not exist" in result.output

    @pytest.mark.unit
    def test_check_shows_diff_when_outdated(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test --check shows diff output when outdated."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        # Create an outdated index
        index_file = rules_dir / "RULES_INDEX.md"
        index_file.write_text("# Old Index\nKeywords: old")

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--check", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 1
        # Should show diff
        assert "Diff" in result.output or "out of date" in result.output


class TestIndexDryRun:
    """Test --dry-run flag."""

    @pytest.mark.unit
    def test_dry_run_does_not_write_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test --dry-run does not create/modify files."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--dry-run", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        # File should NOT exist
        index_file = rules_dir / "RULES_INDEX.md"
        assert not index_file.exists()

    @pytest.mark.unit
    def test_dry_run_shows_generated_content(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test --dry-run shows what would be generated."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--dry-run", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        assert "Generated RULES_INDEX.md content" in result.output
        # Content preview should be shown
        assert "AUTO-GENERATED FILE" in result.output or "Rules Index" in result.output

    @pytest.mark.unit
    def test_dry_run_short_flag(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test -n works as --dry-run."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "-n", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        # File should NOT exist
        assert not (rules_dir / "RULES_INDEX.md").exists()


class TestIndexRulesDir:
    """Test --rules-dir option."""

    @pytest.mark.unit
    def test_custom_rules_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test using custom rules directory."""
        # Arrange
        custom_rules = tmp_path / "custom" / "rules"
        custom_rules.mkdir(parents=True)
        (custom_rules / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(custom_rules)])

        # Assert
        assert result.exit_code == 0
        assert (custom_rules / "RULES_INDEX.md").exists()

    @pytest.mark.unit
    def test_auto_detects_rules_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test auto-detection of rules/ directory."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        # Create pyproject.toml to make it a valid project root
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act - no --rules-dir specified
        result = runner.invoke(app, ["index"])

        # Assert
        assert result.exit_code == 0
        assert (rules_dir / "RULES_INDEX.md").exists()


class TestIndexErrorCases:
    """Test error handling."""

    @pytest.mark.unit
    def test_missing_rules_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test error when rules directory doesn't exist."""
        # Arrange
        missing_dir = tmp_path / "nonexistent" / "rules"

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(missing_dir)])

        # Assert
        assert result.exit_code == 1
        assert "not found" in result.output

    @pytest.mark.unit
    def test_empty_rules_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test error when rules directory has no rule files."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        # Directory exists but is empty

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 1
        assert "No rule files found" in result.output

    @pytest.mark.unit
    def test_skips_readme_and_changelog(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test that README.md and CHANGELOG.md are skipped."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "README.md").write_text("# README")
        (rules_dir / "CHANGELOG.md").write_text("# Changelog")

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        # Should find only 1 rule file (000-global-core.md)
        assert "Found 1 rule files" in result.output


class TestIndexMetadataExtraction:
    """Test metadata extraction from rule files."""

    @pytest.mark.unit
    def test_extracts_keywords(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test keyword extraction from rule files."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        content = (rules_dir / "RULES_INDEX.md").read_text()
        assert "core, foundation, global, standards" in content

    @pytest.mark.unit
    def test_extracts_depends(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test dependency extraction from rule files."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        content = (rules_dir / "RULES_INDEX.md").read_text()
        # 200-python-core depends on 000-global-core.md
        assert "000-global-core.md" in content

    @pytest.mark.unit
    def test_extracts_scope(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test scope extraction from ## Scope section."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        content = (rules_dir / "RULES_INDEX.md").read_text()
        assert "Core foundation rules for all projects" in content

    @pytest.mark.unit
    def test_handles_missing_keywords(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test handling of rule without Keywords field."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        # Rule without Keywords
        rule_content = dedent("""\
            # 000-test: Test Rule

            ## Metadata

            **SchemaVersion:** v3.2
            **Depends:** None

            ## Scope

            **What This Rule Covers:**
            Test rule without keywords.
        """)
        (rules_dir / "000-test.md").write_text(rule_content)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        # Should show warning about missing keywords
        assert "missing Keywords" in result.output


class TestIndexLoadTriggers:
    """Test LoadTrigger parsing and loading strategy generation."""

    @pytest.mark.unit
    def test_generates_loading_strategy(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test that loading strategy section is generated."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        content = (rules_dir / "RULES_INDEX.md").read_text()
        assert "Rule Loading Strategy" in content
        assert "Foundation (Always Load)" in content

    @pytest.mark.unit
    def test_parses_ext_triggers(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test parsing of ext: triggers."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        content = (rules_dir / "RULES_INDEX.md").read_text()
        # Should include extension-based triggers
        assert ".py" in content or "extension" in content.lower()


class TestIndexDomainGrouping:
    """Test domain grouping by filename prefix."""

    @pytest.mark.unit
    def test_groups_by_domain(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test rules are grouped by domain."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        content = (rules_dir / "RULES_INDEX.md").read_text()
        # Should have domain headers
        assert "Core Foundation (000-series)" in content
        assert "Python (200-series)" in content

    @pytest.mark.unit
    def test_sorts_rules_within_domain(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test rules are sorted by filename within domain."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        # Create rules in non-sorted order with distinct content
        rule_201 = dedent("""\
            # 201-python-advanced: Python Advanced

            ## Metadata

            **SchemaVersion:** v3.2
            **Keywords:** python, advanced, patterns
            **Depends:** 200-python-core.md

            ## Scope

            **What This Rule Covers:**
            Advanced Python patterns.
        """)
        (rules_dir / "201-python-advanced.md").write_text(rule_201)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["index", "--rules-dir", str(rules_dir)])

        # Assert
        assert result.exit_code == 0
        content = (rules_dir / "RULES_INDEX.md").read_text()
        # In the Rule Catalog section, 200 should come before 201
        # Find the catalog section and check order there
        catalog_section = content.split("## Rule Catalog")[-1]
        pos_200 = catalog_section.find("**`200-python-core.md`**")
        pos_201 = catalog_section.find("**`201-python-advanced.md`**")
        assert pos_200 < pos_201, (
            f"200 should come before 201 in catalog (200 at {pos_200}, 201 at {pos_201})"
        )
