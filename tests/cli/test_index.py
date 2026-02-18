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
        assert "Generate and check" in result.output
        assert "generate" in result.output
        assert "check" in result.output

    @pytest.mark.unit
    def test_help_shows_examples(self):
        """Test --help includes subcommand names."""
        result = runner.invoke(app, ["index", "--help"])
        assert result.exit_code == 0
        assert "generate" in result.output
        assert "check" in result.output


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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

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
        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        # Act - run check
        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(
            app, ["index", "generate", "--dry-run", "--rules-dir", str(rules_dir)]
        )

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
        result = runner.invoke(
            app, ["index", "generate", "--dry-run", "--rules-dir", str(rules_dir)]
        )

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
        result = runner.invoke(app, ["index", "generate", "-n", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(custom_rules)])

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
        result = runner.invoke(app, ["index", "generate"])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(missing_dir)])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

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
        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

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


# ============================================================================
# extract_scope_from_content edge cases (lines 85, 98, 109-117)
# ============================================================================


class TestExtractScopeEdgeCases:
    """Test extract_scope_from_content edge cases."""

    @pytest.mark.unit
    def test_scope_hits_next_section(self):
        """Test scope extraction stops at next ## heading."""
        content = dedent("""\
            ## Scope

            ## Next Section
            This is a different section.
        """)

        result = index_module.extract_scope_from_content(content)

        assert result == "No scope provided"

    @pytest.mark.unit
    def test_scope_marker_content_on_same_line(self):
        """Test scope with content on same line as marker."""
        content = dedent("""\
            ## Scope

            **What This Rule Covers:** Inline scope description here.
        """)

        result = index_module.extract_scope_from_content(content)

        assert result == "Inline scope description here."

    @pytest.mark.unit
    def test_scope_marker_content_on_next_line(self):
        """Test scope with content on next line after marker."""
        content = dedent("""\
            ## Scope

            **What This Rule Covers:**
            Content on next line after marker.
        """)

        result = index_module.extract_scope_from_content(content)

        assert result == "Content on next line after marker."

    @pytest.mark.unit
    def test_scope_marker_no_content(self):
        """Test scope with marker but no content following."""
        content = dedent("""\
            ## Scope

            **What This Rule Covers:**
            **Another Bold Field:** something
        """)

        result = index_module.extract_scope_from_content(content)

        # Marker found but no plain text content follows
        assert result == "No scope provided"

    @pytest.mark.unit
    def test_scope_plain_text_format(self):
        """Test scope with plain text (no marker) after ## Scope."""
        content = dedent("""\
            ## Scope

            This rule covers plain text scope.
        """)

        result = index_module.extract_scope_from_content(content)

        assert result == "This rule covers plain text scope."

    @pytest.mark.unit
    def test_scope_not_found(self):
        """Test when no ## Scope heading exists."""
        content = "# Title\n\nSome content without scope section.\n"

        result = index_module.extract_scope_from_content(content)

        assert result == "No scope provided"


# ============================================================================
# extract_metadata edge cases (lines 138-139, 189)
# ============================================================================


class TestExtractMetadataEdgeCases:
    """Test extract_metadata error paths."""

    @pytest.mark.unit
    def test_extract_metadata_read_failure(self, tmp_path: Path):
        """Test extract_metadata raises ValueError on read failure."""
        nonexistent = tmp_path / "nonexistent.md"

        with pytest.raises(ValueError, match="Failed to read"):
            index_module.extract_metadata(nonexistent)

    @pytest.mark.unit
    def test_extract_metadata_missing_scope_warning(self, tmp_path: Path):
        """Test extract_metadata warns about missing scope."""
        rule_file = tmp_path / "000-test.md"
        rule_file.write_text(
            dedent("""\
            # 000-test: Test Rule

            ## Metadata

            **Keywords:** test, example
            **Depends:** None
        """)
        )

        metadata = index_module.extract_metadata(rule_file)

        # Should still return metadata, scope defaults to "No scope provided"
        assert metadata.scope == "No scope provided"
        assert metadata.keywords == "test, example"

    @pytest.mark.unit
    def test_extract_metadata_with_load_trigger(self, tmp_path: Path):
        """Test extract_metadata parses LoadTrigger field."""
        rule_file = tmp_path / "200-test.md"
        rule_file.write_text(
            dedent("""\
            # 200-test: Python Test

            ## Metadata

            **Keywords:** python
            **Depends:** None
            **LoadTrigger:** ext:.py, file:pyproject.toml

            ## Scope

            Python test rule.
        """)
        )

        metadata = index_module.extract_metadata(rule_file)

        assert metadata.load_trigger == "ext:.py, file:pyproject.toml"


# ============================================================================
# scan_rules edge cases (lines 230, 236-241)
# ============================================================================


class TestScanRulesEdgeCases:
    """Test scan_rules edge cases."""

    @pytest.mark.unit
    def test_scan_rules_skips_examples_directory(self, tmp_path: Path):
        """Test scan_rules skips files in examples/ subdirectory."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text(SAMPLE_RULE_CONTENT)

        examples_dir = rules_dir / "examples"
        examples_dir.mkdir()
        (examples_dir / "example.md").write_text("# Example\n**Keywords:** example\n")

        rules = index_module.scan_rules(rules_dir)

        assert len(rules) == 1
        assert rules[0].filename == "000-test.md"

    @pytest.mark.unit
    def test_scan_rules_handles_value_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test scan_rules handles ValueError from extract_metadata."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-good.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "100-bad.md").write_text("# Bad\n**Keywords:** test\n")

        original_extract = index_module.extract_metadata

        def patched_extract(filepath):
            if "100-bad" in str(filepath):
                raise ValueError("Test error")
            return original_extract(filepath)

        monkeypatch.setattr(index_module, "extract_metadata", patched_extract)

        rules = index_module.scan_rules(rules_dir)

        # Should only have the good rule
        assert len(rules) == 1

    @pytest.mark.unit
    def test_scan_rules_handles_generic_exception(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test scan_rules handles generic Exception from extract_metadata."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-good.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "100-broken.md").write_text("# Broken\n**Keywords:** test\n")

        original_extract = index_module.extract_metadata

        def patched_extract(filepath):
            if "100-broken" in str(filepath):
                raise RuntimeError("Unexpected error")
            return original_extract(filepath)

        monkeypatch.setattr(index_module, "extract_metadata", patched_extract)

        rules = index_module.scan_rules(rules_dir)

        assert len(rules) == 1


# ============================================================================
# parse_load_triggers (lines 431, 434-437)
# ============================================================================


class TestParseLoadTriggersEdgeCases:
    """Test parse_load_triggers with all trigger types."""

    @pytest.mark.unit
    def test_all_trigger_types(self):
        """Test parsing dir:, ext:, file:, and kw: triggers."""
        rules = [
            index_module.RuleMetadata(
                filename="100-test.md",
                filepath=Path("100-test.md"),
                keywords="test",
                depends="—",
                scope="Test",
                load_trigger="dir:skills/, ext:.py, file:Dockerfile, kw:test",
            ),
        ]

        dir_t, ext_t, file_t, kw_t = index_module.parse_load_triggers(rules)

        assert dir_t == {"skills/": "100-test.md"}
        assert ext_t == {".py": "100-test.md"}
        assert file_t == {"Dockerfile": "100-test.md"}
        assert kw_t == {"test": "100-test.md"}

    @pytest.mark.unit
    def test_no_load_trigger(self):
        """Test rules without load_trigger are skipped."""
        rules = [
            index_module.RuleMetadata(
                filename="000-test.md",
                filepath=Path("000-test.md"),
                keywords="test",
                depends="—",
                scope="Test",
                load_trigger=None,
            ),
        ]

        dir_t, ext_t, file_t, kw_t = index_module.parse_load_triggers(rules)

        assert dir_t == {}
        assert ext_t == {}
        assert file_t == {}
        assert kw_t == {}


# ============================================================================
# generate_loading_strategy edge cases (lines 460, 469, 480, 484-485)
# ============================================================================


class TestGenerateLoadingStrategyEdgeCases:
    """Test generate_loading_strategy with various trigger combinations."""

    @pytest.mark.unit
    def test_no_triggers_defined(self):
        """Test loading strategy with no triggers at all."""
        rules = [
            index_module.RuleMetadata(
                filename="000-test.md",
                filepath=Path("000-test.md"),
                keywords="test",
                depends="—",
                scope="Test",
                load_trigger=None,
            ),
        ]

        result = index_module.generate_loading_strategy(rules)

        assert "No directory-based triggers defined" in result
        assert "No extension-based triggers defined" in result
        assert "No keyword-based triggers defined" in result

    @pytest.mark.unit
    def test_with_dir_and_kw_triggers(self):
        """Test loading strategy with dir and keyword triggers."""
        rules = [
            index_module.RuleMetadata(
                filename="100-test.md",
                filepath=Path("100-test.md"),
                keywords="test",
                depends="—",
                scope="Test",
                load_trigger="dir:skills/, kw:testing, kw:pytest",
            ),
        ]

        result = index_module.generate_loading_strategy(rules)

        assert "skills/" in result
        assert "testing" in result
        assert "pytest" in result

    @pytest.mark.unit
    def test_with_file_triggers(self):
        """Test loading strategy with file: triggers grouped with ext:."""
        rules = [
            index_module.RuleMetadata(
                filename="350-docker.md",
                filepath=Path("350-docker.md"),
                keywords="docker",
                depends="—",
                scope="Docker",
                load_trigger="file:Dockerfile, ext:.dockerfile",
            ),
        ]

        result = index_module.generate_loading_strategy(rules)

        assert "Dockerfile" in result
        assert ".dockerfile" in result


# ============================================================================
# _show_diff edge cases (lines 723, 738)
# ============================================================================


class TestShowDiffEdgeCases:
    """Test _show_diff function."""

    @pytest.mark.unit
    def test_show_diff_no_differences(self):
        """Test _show_diff with identical content (no diff)."""
        content = "# Same Content\nLine 1\nLine 2\n"

        # Should not raise
        index_module._show_diff(content, content)

    @pytest.mark.unit
    def test_show_diff_large_diff_truncated(self):
        """Test _show_diff truncates output for large diffs."""
        current = "\n".join([f"old line {i}" for i in range(200)])
        generated = "\n".join([f"new line {i}" for i in range(200)])

        # Should not raise (truncation at 100 lines)
        index_module._show_diff(current, generated)


# ============================================================================
# index CLI fallback and error paths (lines 793-799, 811-813, 824-826, 854-856, 875-877)
# ============================================================================


class TestIndexCLIEdgeCases:
    """Test index CLI command error paths."""

    @pytest.mark.unit
    def test_fallback_to_cwd_rules_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test fallback to cwd rules/ when project root not found."""
        # Create rules/ in tmp_path
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text(SAMPLE_RULE_CONTENT)

        def raise_not_found():
            raise FileNotFoundError("No project root")

        monkeypatch.setattr(index_module, "find_project_root", raise_not_found)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["index", "generate"])

        assert result.exit_code == 0

    @pytest.mark.unit
    def test_fallback_no_rules_dir_anywhere(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test error when neither project root nor cwd has rules/."""

        def raise_not_found():
            raise FileNotFoundError("No project root")

        monkeypatch.setattr(index_module, "find_project_root", raise_not_found)
        monkeypatch.chdir(tmp_path)  # tmp_path has no rules/

        result = runner.invoke(app, ["index", "generate"])

        assert result.exit_code == 1
        assert "not found" in result.output

    @pytest.mark.unit
    def test_scan_rules_exception(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test index CLI handles scan_rules exception."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        def raising_scan(path):
            raise RuntimeError("Scan failed")

        monkeypatch.setattr(index_module, "scan_rules", raising_scan)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "Error scanning" in result.output

    @pytest.mark.unit
    def test_generate_rules_index_exception(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test index CLI handles generate_rules_index exception."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        def raising_generate(rules):
            raise RuntimeError("Generation failed")

        monkeypatch.setattr(index_module, "generate_rules_index", raising_generate)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "Error generating" in result.output

    @pytest.mark.unit
    def test_check_mode_read_exception(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test --check handles read exception on existing file."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text(SAMPLE_RULE_CONTENT)
        # Create index file but make it unreadable
        index_file = rules_dir / "RULES_INDEX.md"
        index_file.write_text("# Index\n")

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Patch read_text to raise
        original_read_text = Path.read_text

        def failing_read_text(self, **kwargs):
            if self.name == "RULES_INDEX.md":
                raise PermissionError("Permission denied")
            return original_read_text(self, **kwargs)

        monkeypatch.setattr(Path, "read_text", failing_read_text)

        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "Error reading" in result.output

    @pytest.mark.unit
    def test_write_exception(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test index CLI handles write exception."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        original_write_text = Path.write_text

        def failing_write_text(self, content, **kwargs):
            if self.name == "RULES_INDEX.md":
                raise PermissionError("Permission denied")
            return original_write_text(self, content, **kwargs)

        monkeypatch.setattr(Path, "write_text", failing_write_text)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "Error writing" in result.output
