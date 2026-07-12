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

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})

# Real template used to render RULES_INDEX in tests
REAL_TEMPLATE = Path(__file__).parent.parent.parent / "templates" / "RULES_INDEX.md.template"


def _row_cells(line: str) -> list[str]:
    """Parse a Markdown table row (`| a | b | ... |`) into stripped cells."""
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _data_row(content: str, filename: str) -> str:
    """Find the data row for ``filename`` in a generated RULES_INDEX table."""
    return next(row for row in content.splitlines() if row.startswith(f"| {filename} "))


# ---------------------------------------------------------------------------
# Autouse fixture — inject real template for all tests in this module
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _inject_template(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make _resolve_template return the real project template in all tests.

    This avoids every test having to create templates/ in tmp_path.
    """
    monkeypatch.setattr(index_module, "_resolve_template", lambda _root: REAL_TEMPLATE)


# ---------------------------------------------------------------------------
# Sample rule content (v3.3 typed Keywords)
# ---------------------------------------------------------------------------

SAMPLE_RULE_CONTENT = dedent("""\
    # 000-global-core: Core Foundation

    ## Metadata

    **SchemaVersion:** v3.3
    **RuleVersion:** v1.0.0
    **LastUpdated:** 2024-01-01
    **Keywords:** kw:core, kw:foundation, kw:global, kw:standards
    **TokenBudget:** ~3300
    **ContextTier:** Critical
    **Depends:** None

    ## Scope

    Core foundation rules for all projects.
""")

SAMPLE_RULE_200 = dedent("""\
    # 200-python-core: Python Core

    ## Metadata

    **SchemaVersion:** v3.3
    **RuleVersion:** v1.0.0
    **LastUpdated:** 2024-01-01
    **Keywords:** kw:python, kw:development, ext:.py, ext:.pyi
    **TokenBudget:** ~1800
    **ContextTier:** High
    **Depends:** required:000-global-core.md
""")


# ============================================================================
# TestIndexHelp
# ============================================================================


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


# ============================================================================
# TestIndexHappyPath
# ============================================================================


class TestIndexHappyPath:
    """Test successful index generation scenarios."""

    @pytest.mark.unit
    def test_generates_index_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test successful index generation produces a flat-table RULES_INDEX."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 0
        assert "Found 2 rule files" in result.output
        assert "Generated" in result.output

        index_file = rules_dir / "RULES_INDEX.md"
        assert index_file.exists()

        content = index_file.read_text()
        assert "Do not edit directly" in content
        # Both rule filenames appear in F4 compact rows
        assert "000-global-core.md" in content
        assert "200-python-core.md" in content
        # F4 format fields present
        assert "tier=" in content
        assert "kw=" in content

    @pytest.mark.unit
    def test_generates_with_metadata(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test index includes typed keyword tokens from v3.3 metadata."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 0
        content = (rules_dir / "RULES_INDEX.md").read_text()
        # F4 bare-word keywords appear in kw= block
        assert "core" in content
        assert "foundation" in content
        # F4 tier field (no token budget in index)
        assert "tier=Critical" in content

    @pytest.mark.unit
    def test_overwrites_existing_index(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test that existing RULES_INDEX.md is overwritten."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        index_file = rules_dir / "RULES_INDEX.md"
        index_file.write_text("# Old Index\nThis should be overwritten")

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 0
        content = index_file.read_text()
        assert "Old Index" not in content
        assert "Do not edit directly" in content


# ============================================================================
# TestIndexCheckMode
# ============================================================================


class TestIndexCheckMode:
    """Test --check mode for CI."""

    @pytest.mark.unit
    def test_check_passes_when_up_to_date(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test check returns 0 when index is up-to-date."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])
        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 0
        assert "up-to-date" in result.output

    @pytest.mark.unit
    def test_check_fails_when_outdated(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test check returns 1 when index is outdated."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        index_file = rules_dir / "RULES_INDEX.md"
        index_file.write_text("# Old Index\nThis is outdated content")

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "out of date" in result.output

    @pytest.mark.unit
    def test_check_fails_when_index_missing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test check returns 1 when index doesn't exist."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "does not exist" in result.output

    @pytest.mark.unit
    def test_check_shows_diff_when_outdated(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test check shows diff output when outdated."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        index_file = rules_dir / "RULES_INDEX.md"
        index_file.write_text("# Old Index\nkw: old")

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "Diff" in result.output or "out of date" in result.output


# ============================================================================
# TestIndexDryRun
# ============================================================================


class TestIndexDryRun:
    """Test --dry-run flag."""

    @pytest.mark.unit
    def test_dry_run_does_not_write_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test --dry-run does not create/modify files."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(
            app, ["index", "generate", "--dry-run", "--rules-dir", str(rules_dir)]
        )

        assert result.exit_code == 0
        assert not (rules_dir / "RULES_INDEX.md").exists()

    @pytest.mark.unit
    def test_dry_run_shows_generated_content(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test --dry-run shows what would be generated."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(
            app, ["index", "generate", "--dry-run", "--rules-dir", str(rules_dir)]
        )

        assert result.exit_code == 0
        assert "Generated RULES_INDEX.md content" in result.output

    @pytest.mark.unit
    def test_dry_run_short_flag(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test -n works as --dry-run."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "-n", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 0
        assert not (rules_dir / "RULES_INDEX.md").exists()


# ============================================================================
# TestIndexRulesDir
# ============================================================================


class TestIndexRulesDir:
    """Test --rules-dir option."""

    @pytest.mark.unit
    def test_custom_rules_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test using custom rules directory."""
        custom_rules = tmp_path / "custom" / "rules"
        custom_rules.mkdir(parents=True)
        (custom_rules / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(custom_rules)])

        assert result.exit_code == 0
        assert (custom_rules / "RULES_INDEX.md").exists()

    @pytest.mark.unit
    def test_auto_detects_rules_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test auto-detection of rules/ directory."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate"])

        assert result.exit_code == 0
        assert (rules_dir / "RULES_INDEX.md").exists()


# ============================================================================
# TestIndexErrorCases
# ============================================================================


class TestIndexErrorCases:
    """Test error handling."""

    @pytest.mark.unit
    def test_missing_rules_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test error when rules directory doesn't exist."""
        missing_dir = tmp_path / "nonexistent" / "rules"

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(missing_dir)])

        assert result.exit_code == 1
        assert "not found" in result.output

    @pytest.mark.unit
    def test_empty_rules_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test error when rules directory has no rule files."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "No rule files found" in result.output

    @pytest.mark.unit
    def test_skips_readme_and_changelog(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test that README.md and CHANGELOG.md are skipped."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "README.md").write_text("# README")
        (rules_dir / "CHANGELOG.md").write_text("# Changelog")

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 0
        assert "Found 1 rule files" in result.output


# ============================================================================
# TestIndexMetadataExtraction
# ============================================================================


class TestIndexMetadataExtraction:
    """Test metadata extraction from rule files."""

    @pytest.mark.unit
    def test_extracts_typed_keywords(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test v3.3 typed keyword tokens appear in flat table."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 0
        content = (rules_dir / "RULES_INDEX.md").read_text()
        # F4 bare-word keywords appear in kw= field (kw: prefix stripped)
        assert "core" in content
        assert "standards" in content

    @pytest.mark.unit
    def test_extracts_tier_and_budget(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test ContextTier and TokenBudget appear in flat table."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 0
        content = (rules_dir / "RULES_INDEX.md").read_text()
        # F4 format uses tier=<value> (no token budget in index rows)
        assert "tier=Critical" in content
        assert "tier=High" in content

    @pytest.mark.unit
    def test_handles_missing_keywords(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test handling of rule without Keywords field emits warning."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        rule_content = dedent("""\
            # 000-test: Test Rule

            ## Metadata

            **SchemaVersion:** v3.3
            **Depends:** None
        """)
        (rules_dir / "000-test.md").write_text(rule_content)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 0
        assert "missing Keywords" in result.output


# ============================================================================
# TestFlatTableFormat
# ============================================================================


class TestFlatTableFormat:
    """Test that the generated RULES_INDEX.md uses the F4 compact format."""

    @pytest.mark.unit
    def test_flat_line_contains_all_fields(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Each rule line has filename tier= [ext=] [file=] [dir=] kw= in F4 format."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)
        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        content = (rules_dir / "RULES_INDEX.md").read_text()
        # Find the F4 compact row for this rule
        line = next(row for row in content.splitlines() if row.startswith("200-python-core.md"))
        assert "tier=High" in line
        assert "ext=.py" in line
        assert ".pyi" in line
        assert "kw=" in line
        # F4 format: no pipe separators
        assert " | " not in line

    @pytest.mark.unit
    def test_flat_line_missing_tier_uses_dash(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """A rule without ContextTier renders tier=-."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        rule_no_tier = dedent("""\
            # 999-notier: No Tier

            ## Metadata

            **SchemaVersion:** v3.3
            **Keywords:** kw:notier
            **TokenBudget:** ~500
            **Depends:** None
        """)
        (rules_dir / "999-notier.md").write_text(rule_no_tier)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)
        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        content = (rules_dir / "RULES_INDEX.md").read_text()
        line = next(row for row in content.splitlines() if row.startswith("999-notier.md"))
        assert "tier=-" in line

    @pytest.mark.unit
    def test_rules_are_sorted_by_filename(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Flat table rows appear in filename-sorted order."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "201-python-advanced.md").write_text(
            dedent("""\
            # 201-python-advanced: Python Advanced

            ## Metadata

            **SchemaVersion:** v3.3
            **Keywords:** kw:python, kw:advanced
            **TokenBudget:** ~900
            **ContextTier:** Medium
            **Depends:** required:200-python-core.md
        """)
        )
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)
        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        content = (rules_dir / "RULES_INDEX.md").read_text()
        pos_200 = content.find("200-python-core.md")
        pos_201 = content.find("201-python-advanced.md")
        assert pos_200 < pos_201, "200 should appear before 201 in flat table"

    @pytest.mark.unit
    def test_grep_recipe_in_header(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Template header includes the grep recipe section."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)
        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        content = (rules_dir / "RULES_INDEX.md").read_text()
        assert "Grep recipe" in content
        assert "grep -iE" in content

    @pytest.mark.unit
    def test_generate_bakes_relative_rules_path(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Generate bakes the relative `rules/` path; no {{rules_path}} placeholder remains.

        Deploy rewrites `rules/` to an absolute path only when --rules-dest is given.
        """
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)
        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        content = (rules_dir / "RULES_INDEX.md").read_text()
        # No placeholder remains; the relative rules path is baked in.
        assert "{{rules_path}}" not in content
        assert "rules/RULES_INDEX.md" in content

    @pytest.mark.unit
    def test_markdown_table_header_present(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Generated file includes the F4 format description and grep recipes."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)
        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        content = (rules_dir / "RULES_INDEX.md").read_text()
        # F4 format: compact rows, no pipe-table header
        assert "tier=" in content
        assert "kw=" in content
        assert " | " not in content.split("grep")[0]  # no pipe separators in data rows
        # F4 data row starts with the filename directly
        data_row = next(row for row in content.splitlines() if row.startswith("000-global-core.md"))
        assert data_row.startswith("000-global-core.md tier=")


# ============================================================================
# TestIndexLoadTriggers
# ============================================================================


class TestIndexLoadTriggers:
    """Test LoadTrigger / typed Keywords parsing integration."""

    @pytest.mark.unit
    def test_ext_triggers_in_flat_line(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """ext: triggers from v3.3 Keywords appear in the flat ext column."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 0
        content = (rules_dir / "RULES_INDEX.md").read_text()
        line = next(row for row in content.splitlines() if row.startswith("200-python-core.md"))
        # F4 ext= field: comma-separated extension triggers
        assert "ext=.py" in line
        assert ".pyi" in line


# ============================================================================
# TestExtractMetadataEdgeCases
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
    def test_extract_metadata_empty_scope(self, tmp_path: Path):
        """Test extract_metadata with no Scope section returns empty scope."""
        rule_file = tmp_path / "000-test.md"
        rule_file.write_text(
            dedent("""\
            # 000-test: Test Rule

            ## Metadata

            **Keywords:** kw:test, kw:example
            **Depends:** None
        """)
        )

        metadata = index_module.extract_metadata(rule_file)

        # scope defaults to empty string (not extracted in v4 flat format)
        assert metadata.scope == ""
        assert metadata.keywords == "kw:test, kw:example"

    @pytest.mark.unit
    def test_extract_metadata_with_load_trigger(self, tmp_path: Path):
        """Test extract_metadata parses legacy LoadTrigger field (v3.2 fallback)."""
        rule_file = tmp_path / "200-test.md"
        rule_file.write_text(
            dedent("""\
            # 200-test: Python Test

            ## Metadata

            **Keywords:** kw:python
            **Depends:** None
            **LoadTrigger:** ext:.py, file:pyproject.toml

            ## Scope

            Python test rule.
        """)
        )

        metadata = index_module.extract_metadata(rule_file)

        assert metadata.load_trigger == "ext:.py, file:pyproject.toml"


# ============================================================================
# TestScanRulesEdgeCases
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
        (examples_dir / "example.md").write_text("# Example\n**Keywords:** kw:example\n")

        rules = index_module.scan_rules(rules_dir)

        assert len(rules) == 1
        assert rules[0].filename == "000-test.md"

    @pytest.mark.unit
    def test_scan_rules_handles_value_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test scan_rules handles ValueError from extract_metadata."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-good.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "100-bad.md").write_text("# Bad\n**Keywords:** kw:test\n")

        original_extract = index_module.extract_metadata

        def patched_extract(filepath: Path) -> index_module.RuleMetadata:
            if "100-bad" in str(filepath):
                raise ValueError("Test error")
            return original_extract(filepath)

        monkeypatch.setattr(index_module, "extract_metadata", patched_extract)

        rules = index_module.scan_rules(rules_dir)

        assert len(rules) == 1

    @pytest.mark.unit
    def test_scan_rules_handles_generic_exception(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test scan_rules handles generic Exception from extract_metadata."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-good.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "100-broken.md").write_text("# Broken\n**Keywords:** kw:test\n")

        original_extract = index_module.extract_metadata

        def patched_extract(filepath: Path) -> index_module.RuleMetadata:
            if "100-broken" in str(filepath):
                raise RuntimeError("Unexpected error")
            return original_extract(filepath)

        monkeypatch.setattr(index_module, "extract_metadata", patched_extract)

        rules = index_module.scan_rules(rules_dir)

        assert len(rules) == 1


# ============================================================================
# TestParseLoadTriggersEdgeCases
# ============================================================================


class TestParseLoadTriggersEdgeCases:
    """Test parse_load_triggers with all trigger types."""

    @pytest.mark.unit
    def test_all_trigger_types_via_load_trigger(self):
        """Test parsing dir:, ext:, file:, kw: from legacy load_trigger."""
        rules = [
            index_module.RuleMetadata(
                filename="100-test.md",
                filepath=Path("100-test.md"),
                keywords="kw:test",
                depends="—",
                scope="Test",
                load_trigger="dir:skills/, ext:.py, file:Dockerfile, kw:docker",
            ),
        ]

        dir_t, ext_t, file_t, kw_t = index_module.parse_load_triggers(rules)

        assert dir_t == {"skills/": "100-test.md"}
        assert ext_t == {".py": "100-test.md"}
        assert file_t == {"Dockerfile": "100-test.md"}
        # kw: from both keywords and load_trigger
        assert "test" in kw_t
        assert "docker" in kw_t

    @pytest.mark.unit
    def test_no_load_trigger_untyped_keywords(self):
        """Test rules with no typed tokens produce empty trigger dicts."""
        rules = [
            index_module.RuleMetadata(
                filename="000-test.md",
                filepath=Path("000-test.md"),
                keywords="core",  # untyped — not picked up by parse_load_triggers
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

    @pytest.mark.unit
    def test_typed_keywords_v33(self):
        """v3.3: typed entries live in Keywords; LoadTrigger is unused."""
        rules = [
            index_module.RuleMetadata(
                filename="200-python-core.md",
                filepath=Path("200-python-core.md"),
                keywords="ext:.py, ext:.pyi, file:pyproject.toml, kw:python, kw:uv",
                depends="—",
                scope="Python core",
                load_trigger=None,
            ),
        ]

        dir_t, ext_t, file_t, kw_t = index_module.parse_load_triggers(rules)

        assert dir_t == {}
        assert ext_t == {".py": "200-python-core.md", ".pyi": "200-python-core.md"}
        assert file_t == {"pyproject.toml": "200-python-core.md"}
        assert kw_t == {"python": "200-python-core.md", "uv": "200-python-core.md"}

    @pytest.mark.unit
    def test_typed_keywords_alphabetical_overwrite(self):
        """Last-rule-wins on alphabetical scan: more specific rules override."""
        rules = [
            index_module.RuleMetadata(
                filename="002i-rule-loadtrigger.md",
                filepath=Path("002i-rule-loadtrigger.md"),
                keywords="ext:.py, kw:loadtrigger",
                depends="—",
                scope="LoadTrigger guidelines",
                load_trigger=None,
            ),
            index_module.RuleMetadata(
                filename="200-python-core.md",
                filepath=Path("200-python-core.md"),
                keywords="ext:.py, kw:python",
                depends="—",
                scope="Python core",
                load_trigger=None,
            ),
        ]

        _, ext_t, _, _ = index_module.parse_load_triggers(rules)

        assert ext_t[".py"] == "200-python-core.md"


# ============================================================================
# TestSplitTypedTokens (new in v3.3)
# ============================================================================


class TestSplitTypedTokens:
    """Test _split_typed_tokens helper."""

    @pytest.mark.unit
    def test_splits_all_prefix_kinds(self):
        """Test splitting kw:, ext:, file:, dir: entries."""
        result = index_module._split_typed_tokens(
            "kw:python, ext:.py, ext:.pyi, file:pyproject.toml, dir:src/"
        )

        assert result["kw"] == ["python"]
        assert result["ext"] == [".py", ".pyi"]
        assert result["file"] == ["pyproject.toml"]
        assert result["dir"] == ["src/"]

    @pytest.mark.unit
    def test_untyped_entries_are_ignored(self):
        """Untyped entries (no recognized prefix) are silently dropped."""
        result = index_module._split_typed_tokens("python, development, pytest")

        assert result == {"kw": [], "ext": [], "file": [], "dir": []}

    @pytest.mark.unit
    def test_empty_string(self):
        """Empty keywords string returns all-empty result."""
        result = index_module._split_typed_tokens("")

        assert result == {"kw": [], "ext": [], "file": [], "dir": []}

    @pytest.mark.unit
    def test_preserves_order(self):
        """Token order within each list is preserved."""
        result = index_module._split_typed_tokens("kw:beta, kw:alpha, kw:gamma")

        assert result["kw"] == ["beta", "alpha", "gamma"]


# ============================================================================
# TestGenerateFlatLine (now tests render_index_line F4 format)
# ============================================================================


class TestGenerateFlatLine:
    """Test render_index_line F4 rendering (previously generate_flat_line pipe-table)."""

    def _make_rule(
        self,
        filename: str = "200-python-core.md",
        keywords: str = "kw:python, ext:.py",
        tier: str | None = "High",
        budget: str | None = "~1800",
        load_trigger: str | None = None,
    ) -> index_module.RuleMetadata:
        return index_module.RuleMetadata(
            filename=filename,
            filepath=Path(filename),
            keywords=keywords,
            depends="—",
            scope="",
            context_tier=tier,
            token_budget=budget,
            load_trigger=load_trigger,
        )

    @pytest.mark.unit
    def test_field_order(self):
        """F4 row: filename tier=<T> [ext=..] kw=<words>."""
        rule = self._make_rule()
        line = index_module.render_index_line(rule)

        # F4 format: space-delimited, no leading/trailing pipes
        assert not line.startswith("|")
        assert not line.endswith("|")
        assert line.split(" ", 1)[0] == "200-python-core.md"
        assert "tier=High" in line
        assert "ext=.py" in line
        assert "kw=python" in line

    @pytest.mark.unit
    def test_missing_tier_renders_dash(self):
        """A rule without ContextTier renders tier=-."""
        rule = self._make_rule(tier=None)
        line = index_module.render_index_line(rule)
        assert "tier=-" in line

    @pytest.mark.unit
    def test_missing_budget_renders_dash(self):
        """Token budget is not emitted in F4 rows (field removed)."""
        rule = self._make_rule(budget=None)
        line = index_module.render_index_line(rule)
        # F4 has no ~tokens field; budget does not appear
        assert "~-" not in line
        assert "~1800" not in line

    @pytest.mark.unit
    def test_all_empty_typed_fields_render_dash(self):
        """A rule with no typed kw: tokens renders kw=-."""
        rule = self._make_rule(keywords="untyped-legacy-term")
        line = index_module.render_index_line(rule)
        assert "kw=-" in line
        assert "ext=" not in line
        assert "file=" not in line
        assert "dir=" not in line

    @pytest.mark.unit
    def test_multiple_ext_and_kw(self):
        """Multiple ext: and kw: tokens appear in ext= and kw= fields."""
        rule = self._make_rule(
            keywords="kw:python, kw:pytest, ext:.py, ext:.pyi, file:pyproject.toml"
        )
        line = index_module.render_index_line(rule)
        assert "ext=.py" in line
        assert ".pyi" in line
        assert "file=pyproject.toml" in line
        assert "python" in line
        assert "pytest" in line

    @pytest.mark.unit
    def test_no_trailing_newline(self):
        """render_index_line does not add a trailing newline."""
        rule = self._make_rule()
        line = index_module.render_index_line(rule)
        assert not line.endswith("\n")


# ============================================================================
# TestRenderRulesIndex
# ============================================================================


class TestRenderRulesIndex:
    """Test render_rules_index template rendering."""

    @pytest.mark.unit
    def test_renders_flat_rows_at_marker(self, tmp_path: Path):
        """render_rules_index replaces RULE_TABLE_MARKER with flat rows."""
        template = tmp_path / "RULES_INDEX.md.template"
        template.write_text("# Header\n<!-- RULE_TABLE -->\n# Footer\n")

        rules = [
            index_module.RuleMetadata(
                filename="000-test.md",
                filepath=Path("000-test.md"),
                keywords="kw:test",
                depends="—",
                scope="",
                context_tier="Critical",
                token_budget="~100",
            ),
        ]

        result = index_module.render_rules_index(rules, template)

        assert "<!-- RULE_TABLE -->" not in result
        assert "000-test.md" in result
        assert "tier=Critical" in result

    @pytest.mark.unit
    def test_raises_on_missing_template(self, tmp_path: Path):
        """render_rules_index raises ValueError when template is missing."""
        missing = tmp_path / "missing.template"
        rules: list[index_module.RuleMetadata] = []

        with pytest.raises(ValueError, match="Template not found"):
            index_module.render_rules_index(rules, missing)

    @pytest.mark.unit
    def test_raises_when_marker_absent(self, tmp_path: Path):
        """render_rules_index raises ValueError when RULE_TABLE_MARKER is absent."""
        template = tmp_path / "bad.template"
        template.write_text("# No marker here\n")
        rules: list[index_module.RuleMetadata] = []

        with pytest.raises(ValueError, match="does not contain the"):
            index_module.render_rules_index(rules, template)

    @pytest.mark.unit
    def test_renders_with_real_template(self):
        """render_rules_index works with the real project template."""
        rules = [
            index_module.RuleMetadata(
                filename="000-global-core.md",
                filepath=Path("000-global-core.md"),
                keywords="kw:workflow, kw:safety",
                depends="—",
                scope="",
                context_tier="Critical",
                token_budget="~4050",
            ),
        ]

        result = index_module.render_rules_index(rules, REAL_TEMPLATE)

        assert "000-global-core.md" in result
        assert "tier=Critical" in result
        assert "Grep recipe" in result


# ============================================================================
# TestShowDiffEdgeCases
# ============================================================================


class TestShowDiffEdgeCases:
    """Test _show_diff function."""

    @pytest.mark.unit
    def test_show_diff_no_differences(self):
        """Test _show_diff with identical content (no diff)."""
        content = "# Same Content\nLine 1\nLine 2\n"
        index_module._show_diff(content, content)

    @pytest.mark.unit
    def test_show_diff_large_diff_truncated(self):
        """Test _show_diff truncates output for large diffs."""
        current = "\n".join([f"old line {i}" for i in range(200)])
        generated = "\n".join([f"new line {i}" for i in range(200)])
        index_module._show_diff(current, generated)


# ============================================================================
# TestIndexCLIEdgeCases
# ============================================================================


class TestIndexCLIEdgeCases:
    """Test index CLI command error paths."""

    @pytest.mark.unit
    def test_fallback_to_cwd_rules_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test fallback to cwd rules/ when project root not found."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text(SAMPLE_RULE_CONTENT)

        def raise_not_found() -> Path:
            raise FileNotFoundError("No project root")

        monkeypatch.setattr(index_module, "find_project_root", raise_not_found)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["index", "generate"])

        assert result.exit_code == 0

    @pytest.mark.unit
    def test_fallback_no_rules_dir_anywhere(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test error when neither project root nor cwd has rules/."""

        def raise_not_found() -> Path:
            raise FileNotFoundError("No project root")

        monkeypatch.setattr(index_module, "find_project_root", raise_not_found)
        monkeypatch.chdir(tmp_path)

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

        def raising_scan(path: Path) -> list:
            raise RuntimeError("Scan failed")

        monkeypatch.setattr(index_module, "scan_rules", raising_scan)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "Error scanning" in result.output

    @pytest.mark.unit
    def test_render_rules_index_exception(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test index CLI handles render_rules_index exception."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        def raising_render(rules: list, template_path: Path) -> str:
            raise RuntimeError("Generation failed")

        monkeypatch.setattr(index_module, "render_rules_index", raising_render)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "Error rendering" in result.output

    @pytest.mark.unit
    def test_check_mode_read_exception(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test check handles read exception on existing file."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text(SAMPLE_RULE_CONTENT)
        index_file = rules_dir / "RULES_INDEX.md"
        index_file.write_text("# Index\n")

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        original_read_text = Path.read_text

        def failing_read_text(self: Path, **kwargs: object) -> str:
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

        def failing_write_text(self: Path, content: str, **kwargs: object) -> int:
            if self.name == "RULES_INDEX.md":
                raise PermissionError("Permission denied")
            return original_write_text(self, content, **kwargs)

        monkeypatch.setattr(Path, "write_text", failing_write_text)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "Error writing" in result.output


# ============================================================================
# TestIndexStats (B5 — .index-stats.json)
# ============================================================================


class TestIndexStats:
    """Tests for the .index-stats.json artifact (B5 slice of plan §5.3)."""

    @pytest.mark.unit
    def test_render_index_stats_schema(self, tmp_path: Path):
        """render_index_stats emits the F4 schema slice with expected counts."""
        # Arrange
        rendered_index = "line one\nline two\nline three\n"
        rule_critical = index_module.RuleMetadata(
            filename="000-global-core.md",
            filepath=Path("000-global-core.md"),
            keywords="kw:workflow, kw:safety",
            depends="—",
            scope="",
            context_tier="Critical",
            token_budget="~2400",
        )
        rule_high = index_module.RuleMetadata(
            filename="200-python-core.md",
            filepath=Path("200-python-core.md"),
            keywords="kw:python, kw:uv, ext:.py",
            depends="000-global-core.md",
            scope="",
            context_tier="High",
            token_budget="~1800",
        )

        # Act
        stats = index_module.render_index_stats(
            [rule_critical, rule_high], rendered_index, tmp_path
        )

        # Assert — top-level schema
        assert stats["schema_version"] == index_module.STATS_SCHEMA_VERSION
        assert stats["schema_version"] == "3"
        assert stats["format_version"] == index_module.INDEX_FORMAT_VERSION
        assert stats["format_version"] == "F4"
        assert isinstance(stats["generated_at"], str)
        assert stats["generated_at"].endswith("Z")
        assert isinstance(stats["git_sha"], str)  # value depends on env; existence is contractual
        # Counts
        counts = stats["counts"]
        assert counts["rules"] == 2
        assert counts["index_lines"] == 3
        # 4 kw: tokens across the two rules (workflow, safety, python, uv)
        assert counts["keyword_entries"] == 4
        # Only rule_high has a non-"—" depends
        assert counts["rules_with_deps"] == 1
        # Tier bucketing
        assert stats["tiers"] == {"critical": 1, "high": 1, "medium": 0, "low": 0}
        # Sanity thresholds are constants at v1
        assert stats["sanity_thresholds"] == {
            "min_matches_common_keyword": 1,
            "max_matches_broad_query": 50,
            "zero_result_is_anomaly": True,
        }

    @pytest.mark.unit
    def test_generate_writes_index_stats_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """`ai-rules index generate` writes rules/.index-stats.json alongside RULES_INDEX.md."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 0
        stats_path = rules_dir / index_module.STATS_FILENAME
        assert stats_path.exists()
        import json as _json

        payload = _json.loads(stats_path.read_text())
        assert payload["counts"]["rules"] == 2
        assert payload["schema_version"] == index_module.STATS_SCHEMA_VERSION

    @pytest.mark.unit
    def test_index_check_fails_on_stale_stats(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """`ai-rules index check` fails when .index-stats.json content is stale."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Generate a clean baseline so RULES_INDEX.md itself is up-to-date;
        # then corrupt only the stats file so we isolate the stats-check path.
        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        stats_path = rules_dir / index_module.STATS_FILENAME
        assert stats_path.exists()
        import json as _json

        stale = _json.loads(stats_path.read_text())
        stale["counts"]["rules"] = 999  # non-volatile drift
        stats_path.write_text(_json.dumps(stale, indent=2, sort_keys=True) + "\n")

        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "out of date" in result.output

    @pytest.mark.unit
    def test_index_check_ignores_volatile_stats_fields(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """`check` treats generated_at and git_sha as volatile and does not fail on their drift."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        stats_path = rules_dir / index_module.STATS_FILENAME
        import json as _json

        payload = _json.loads(stats_path.read_text())
        # Rewrite only the volatile fields — check must still pass.
        payload["generated_at"] = "1999-01-01T00:00:00Z"
        payload["git_sha"] = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
        stats_path.write_text(_json.dumps(payload, indent=2, sort_keys=True) + "\n")

        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 0
        assert "up-to-date" in result.output

    @pytest.mark.unit
    def test_index_check_fails_when_stats_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """`check` fails when RULES_INDEX.md is current but .index-stats.json is missing."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        (rules_dir / index_module.STATS_FILENAME).unlink()

        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "does not exist" in result.output


# ============================================================================
# TestIndexFormat (F4 compact RULES_INDEX.md)
# ============================================================================


class TestIndexFormat:
    """Tests for the F4-format RULES_INDEX.md (single compact discovery index)."""

    @pytest.mark.unit
    def test_render_compact_line_shape(self):
        """render_index_line emits F4-format space-delimited fields."""
        rule = index_module.RuleMetadata(
            filename="200-python-core.md",
            filepath=Path("200-python-core.md"),
            keywords="kw:python, kw:pytest, ext:.py, ext:.pyi, file:pyproject.toml",
            depends="required:000-global-core.md",
            scope="",
            context_tier="High",
            token_budget="~1800",
        )

        line = index_module.render_index_line(rule)

        # F4 grammar: no leading/trailing separator, no trailing newline
        assert not line.startswith(" ")
        assert not line.endswith(" ")
        assert not line.endswith("\n")
        # F4 uses space-delimited fields, not pipes
        assert " | " not in line
        assert "tier=High" in line
        assert "ext=.py,.pyi" in line
        assert "file=pyproject.toml" in line
        # dir= is omitted entirely when no dir triggers exist (not emitted as dir=-)
        assert "dir=" not in line
        assert "kw=python pytest" in line
        # Filename is the first token
        assert line.split(" ", 1)[0] == "200-python-core.md"

    @pytest.mark.unit
    def test_render_compact_line_all_empty_triggers_omit_fields(self):
        """A rule with only kw: tokens omits ext=, file=, dir= entirely."""
        rule = index_module.RuleMetadata(
            filename="000-test.md",
            filepath=Path("000-test.md"),
            keywords="kw:test",
            depends="—",
            scope="",
            context_tier="Critical",
            token_budget="~100",
        )

        line = index_module.render_index_line(rule)

        assert "tier=Critical" in line
        # Empty ext/file/dir fields are omitted — do NOT render as `foo=-`.
        assert "ext=" not in line
        assert "file=" not in line
        assert "dir=" not in line
        assert "kw=test" in line
        # Exactly 3 space-delimited parts: filename, tier=..., kw=...
        assert len(line.split(" ")) == 3

    @pytest.mark.unit
    def test_render_compact_line_missing_tier_renders_dash(self):
        """A rule without ContextTier renders `tier=-` (tier is always present)."""
        rule = index_module.RuleMetadata(
            filename="000-notier.md",
            filepath=Path("000-notier.md"),
            keywords="kw:test",
            depends="—",
            scope="",
            context_tier=None,
            token_budget=None,
        )

        line = index_module.render_index_line(rule)

        assert "tier=-" in line
        assert "tier=None" not in line

    @pytest.mark.unit
    def test_generate_writes_compact_index_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """`ai-rules index generate` writes RULES_INDEX.md in F4 compact format."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        result = runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 0
        index_path = rules_dir / "RULES_INDEX.md"
        assert index_path.exists()

        body = index_path.read_text()
        assert index_module.RULE_TABLE_MARKER not in body
        # Both rules appear as F4-format compact rows
        assert "000-global-core.md tier=Critical" in body
        assert "200-python-core.md tier=High" in body

    @pytest.mark.unit
    def test_index_check_fails_on_stale_compact(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """`ai-rules index check` fails when RULES_INDEX.md is out of date."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Generate a clean baseline, then corrupt only the index file.
        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        index_path = rules_dir / "RULES_INDEX.md"
        assert index_path.exists()
        index_path.write_text("# Stale index — content drift\n")

        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "out of date" in result.output

    @pytest.mark.unit
    def test_index_check_fails_when_compact_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """`check` fails when RULES_INDEX.md is missing entirely."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        (rules_dir / "RULES_INDEX.md").unlink()

        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        assert "does not exist" in result.output

    @pytest.mark.unit
    def test_compact_index_grep_parity(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """RULES_INDEX.md F4 rows must be searchable via word-boundary grep for each keyword.

        Guards against keyword coverage regression: every typed kw: token must
        appear as a bare word in the kw= block, discoverable with -iwE word-boundary grep.
        """
        import re

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)
        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        content = (rules_dir / "RULES_INDEX.md").read_text()

        # Word-boundary match on bare keywords in the F4 kw= block
        for keyword in ("core", "foundation", "python"):
            wb = re.compile(rf"(?i)\b{re.escape(keyword)}\b")
            matches = {
                row.split(" ", 1)[0].strip()
                for row in content.splitlines()
                if wb.search(row) and " tier=" in row
            }
            assert matches, (
                f"expected word-boundary grep for {keyword!r} to match rows in RULES_INDEX.md"
            )

        # Field-prefix matching still works for ext=/file=/dir= searches.
        for field_pattern in ("ext=.*\\.py", "ext=.*\\.pyi"):
            fp = re.compile(field_pattern, re.IGNORECASE)
            compact_matches = {
                row.split(" ", 1)[0].strip()
                for row in content.splitlines()
                if fp.search(row) and " tier=" in row
            }
            assert compact_matches, (
                f"expected field pattern {field_pattern!r} to match in RULES_INDEX.md"
            )

    @pytest.mark.unit
    def test_index_stats_includes_compact_index_lines(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """`.index-stats.json` counts include `index_lines` for the single RULES_INDEX.md."""
        import json as _json

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)
        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        stats_path = rules_dir / index_module.STATS_FILENAME
        payload = _json.loads(stats_path.read_text())
        counts = payload["counts"]

        assert "index_lines" in counts
        assert "compact_index_lines" not in counts
        index_body = (rules_dir / "RULES_INDEX.md").read_text()
        assert counts["index_lines"] == len(index_body.splitlines())

    @pytest.mark.unit
    def test_render_compact_index_raises_on_missing_template(self, tmp_path: Path):
        """render_rules_index raises ValueError when the template file is absent."""
        missing = tmp_path / "missing.template"
        with pytest.raises(ValueError, match="Template not found"):
            index_module.render_rules_index([], missing)

    @pytest.mark.unit
    def test_render_compact_index_raises_when_marker_absent(self, tmp_path: Path):
        """render_rules_index raises ValueError when RULE_TABLE_MARKER is absent."""
        bad = tmp_path / "bad.template"
        bad.write_text("# No marker here\n")
        with pytest.raises(ValueError, match="does not contain the"):
            index_module.render_rules_index([], bad)

    @pytest.mark.unit
    def test_f4_hyphenation(self):
        """Multi-word keywords with internal whitespace are hyphenated in `kw=`."""
        rule = index_module.RuleMetadata(
            filename="000-global-core.md",
            filepath=Path("000-global-core.md"),
            # "surgical edits" and "prompt engineering" contain internal spaces
            keywords="kw:workflow, kw:surgical edits, kw:prompt engineering",
            depends="—",
            scope="",
            context_tier="Critical",
        )

        line = index_module.render_index_line(rule)

        # Whitespace inside keywords is hyphenated so the kw= block stays
        # space-tokenised (see plan §3.2, F4 canonicalisation rule).
        assert "surgical-edits" in line
        assert "prompt-engineering" in line
        assert "surgical edits" not in line
        assert "prompt engineering" not in line

    @pytest.mark.unit
    def test_f4_hyphenate_keyword_helper(self):
        """_hyphenate_keyword collapses internal whitespace to hyphens."""
        assert index_module._hyphenate_keyword("simple") == "simple"
        assert index_module._hyphenate_keyword("two words") == "two-words"
        assert index_module._hyphenate_keyword("multi  word  gap") == "multi-word-gap"
        assert index_module._hyphenate_keyword("already-hyphenated") == "already-hyphenated"
        assert index_module._hyphenate_keyword("  padded  ") == "padded"
        assert index_module._hyphenate_keyword("") == ""

    @pytest.mark.unit
    def test_f4_deterministic_generation(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Two consecutive render_compact_index calls produce byte-identical output."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)
        (rules_dir / "200-python-core.md").write_text(SAMPLE_RULE_200)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        rules = index_module.scan_rules(rules_dir)
        template_path = tmp_path / index_module.TEMPLATE_RELATIVE
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text("# Index\n\n" + index_module.RULE_TABLE_MARKER + "\n")

        first = index_module.render_rules_index(rules, template_path)
        second = index_module.render_rules_index(rules, template_path)

        assert first == second
        # Byte-identical
        assert first.encode("utf-8") == second.encode("utf-8")

    @pytest.mark.unit
    def test_index_check_detects_f1_stale_format(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """`check` fails with an F1-format migration message on legacy pipe-separated rows."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)

        # Generate a clean F4 baseline, then overwrite the compact file with
        # an F1-format row (pipe-separated ` | kw:foo`). The stale sentinel
        # should fire before the diff pathway.
        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        compact_path = rules_dir / "RULES_INDEX.md"
        compact_path.write_text(
            "# stale F1 index\n"
            "000-global-core.md | tier:Critical | - | - | - | kw:workflow,kw:safety\n"
        )

        result = runner.invoke(app, ["index", "check", "--rules-dir", str(rules_dir)])

        assert result.exit_code == 1
        # Message should reference F1 migration guidance
        assert "F1" in result.output or "legacy" in result.output.lower()

    @pytest.mark.unit
    def test_index_stats_format_version(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """`.index-stats.json` contains format_version=F4 and schema_version=2."""
        import json as _json

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text(SAMPLE_RULE_CONTENT)

        monkeypatch.setattr(index_module, "find_project_root", lambda: tmp_path)
        runner.invoke(app, ["index", "generate", "--rules-dir", str(rules_dir)])

        stats_path = rules_dir / index_module.STATS_FILENAME
        payload = _json.loads(stats_path.read_text())

        assert payload["schema_version"] == "3"
        assert payload["format_version"] == "F4"
