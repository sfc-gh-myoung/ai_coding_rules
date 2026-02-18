"""Tests for ai-rules refs command."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

from typer.testing import CliRunner

from ai_rules.cli import app

runner = CliRunner()


class TestRefsHelp:
    """Test --help output."""

    def test_help_shows_description(self):
        """Test --help shows command description."""
        result = runner.invoke(app, ["refs", "--help"])
        assert result.exit_code == 0
        assert "Validate rule references" in result.output
        assert "check" in result.output

    def test_help_shows_check_options(self):
        """Test check subcommand --help shows options."""
        result = runner.invoke(app, ["refs", "check", "--help"])
        assert result.exit_code == 0
        assert "--check-orphans" in result.output
        assert "--verbose" in result.output
        assert "--index-path" in result.output
        assert "--rules-dir" in result.output


class TestRefsHappyPath:
    """Test successful validation scenarios."""

    def test_valid_references_passes(self, tmp_path: Path):
        """Test validation passes when all references are valid."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text(
            dedent("""
            # Rule Index

            - 000-global-core.md
            - 100-snowflake-core.md
            - 200-python-core.md
            """)
        )

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text("content")
        (rules_dir / "100-snowflake-core.md").write_text("content")
        (rules_dir / "200-python-core.md").write_text("content")

        result = runner.invoke(
            app,
            ["refs", "check", "--index-path", str(index_file), "--rules-dir", str(rules_dir)],
        )

        assert result.exit_code == 0
        assert "VALIDATION PASSED" in result.output

    def test_empty_index_passes(self, tmp_path: Path):
        """Test validation passes with empty index (no references)."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("# Empty Index\n")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        result = runner.invoke(
            app,
            ["refs", "check", "--index-path", str(index_file), "--rules-dir", str(rules_dir)],
        )

        assert result.exit_code == 0
        assert "VALIDATION PASSED" in result.output


class TestRefsBrokenReferences:
    """Test broken reference detection."""

    def test_detects_broken_references(self, tmp_path: Path):
        """Test exit code 1 when references point to missing files."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-exists.md, 100-missing.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-exists.md").write_text("content")

        result = runner.invoke(
            app,
            ["refs", "check", "--index-path", str(index_file), "--rules-dir", str(rules_dir)],
        )

        assert result.exit_code == 1
        assert "BROKEN REFERENCES" in result.output
        assert "100-missing.md" in result.output

    def test_multiple_broken_references(self, tmp_path: Path):
        """Test detection of multiple broken references."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-a.md, 100-b.md, 200-c.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        result = runner.invoke(
            app,
            ["refs", "check", "--index-path", str(index_file), "--rules-dir", str(rules_dir)],
        )

        assert result.exit_code == 1
        assert "BROKEN REFERENCES (3)" in result.output
        assert "000-a.md" in result.output
        assert "100-b.md" in result.output
        assert "200-c.md" in result.output


class TestRefsCheckOrphans:
    """Test --check-orphans flag."""

    def test_detects_orphaned_files(self, tmp_path: Path):
        """Test --check-orphans reports unreferenced files."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-referenced.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-referenced.md").write_text("content")
        (rules_dir / "100-orphaned.md").write_text("content")

        result = runner.invoke(
            app,
            [
                "refs",
                "check",
                "--index-path",
                str(index_file),
                "--rules-dir",
                str(rules_dir),
                "--check-orphans",
            ],
        )

        assert result.exit_code == 0
        assert "ORPHANED FILES" in result.output
        assert "100-orphaned.md" in result.output

    def test_no_orphans_without_flag(self, tmp_path: Path):
        """Test orphans not reported without --check-orphans."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-referenced.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-referenced.md").write_text("content")
        (rules_dir / "100-orphaned.md").write_text("content")

        result = runner.invoke(
            app,
            ["refs", "check", "--index-path", str(index_file), "--rules-dir", str(rules_dir)],
        )

        assert result.exit_code == 0
        assert "ORPHANED" not in result.output


class TestRefsVerbose:
    """Test --verbose flag."""

    def test_verbose_shows_reference_counts(self, tmp_path: Path):
        """Test --verbose shows reference and file counts."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-test.md, 100-test.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text("content")
        (rules_dir / "100-test.md").write_text("content")

        result = runner.invoke(
            app,
            [
                "refs",
                "check",
                "--index-path",
                str(index_file),
                "--rules-dir",
                str(rules_dir),
                "--verbose",
            ],
        )

        assert result.exit_code == 0
        assert "References found" in result.output
        assert "Rule files found" in result.output

    def test_verbose_short_flag(self, tmp_path: Path):
        """Test -v works same as --verbose."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-test.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text("content")

        result = runner.invoke(
            app,
            ["refs", "check", "--index-path", str(index_file), "--rules-dir", str(rules_dir), "-v"],
        )

        assert result.exit_code == 0
        assert "References found" in result.output


class TestRefsErrorCases:
    """Test error handling."""

    def test_missing_index_file(self, tmp_path: Path):
        """Test exit code 1 when index file doesn't exist."""
        index_file = tmp_path / "MISSING_INDEX.md"
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        result = runner.invoke(
            app,
            ["refs", "check", "--index-path", str(index_file), "--rules-dir", str(rules_dir)],
        )

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_missing_rules_directory(self, tmp_path: Path):
        """Test exit code 1 when rules directory doesn't exist."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("content")
        rules_dir = tmp_path / "missing_rules"

        result = runner.invoke(
            app,
            ["refs", "check", "--index-path", str(index_file), "--rules-dir", str(rules_dir)],
        )

        assert result.exit_code == 1
        assert "not found" in result.output


class TestRefsEdgeCases:
    """Test edge cases."""

    def test_files_in_subdirectories(self, tmp_path: Path):
        """Test finding files in subdirectories."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-top.md, 100-nested.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        subdir = rules_dir / "subdir"
        subdir.mkdir()
        (rules_dir / "000-top.md").write_text("content")
        (subdir / "100-nested.md").write_text("content")

        result = runner.invoke(
            app,
            ["refs", "check", "--index-path", str(index_file), "--rules-dir", str(rules_dir)],
        )

        assert result.exit_code == 0
        assert "VALIDATION PASSED" in result.output

    def test_skips_readme_and_changelog(self, tmp_path: Path):
        """Test README.md and CHANGELOG.md are not counted as rules."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-test.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text("content")
        (rules_dir / "README.md").write_text("documentation")
        (rules_dir / "CHANGELOG.md").write_text("changes")

        result = runner.invoke(
            app,
            [
                "refs",
                "check",
                "--index-path",
                str(index_file),
                "--rules-dir",
                str(rules_dir),
                "--check-orphans",
            ],
        )

        assert result.exit_code == 0
        assert "README.md" not in result.output
        assert "CHANGELOG.md" not in result.output


class TestRefsDefaultPathResolution:
    """Test default path resolution via find_project_root()."""

    def test_resolves_defaults_from_project_root(self, tmp_path: Path):
        """Test check resolves index_path and rules_dir from project root when not provided."""
        # Set up a fake project with pyproject.toml
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "RULES_INDEX.md").write_text(
            dedent("""
            # Rule Index
            - 000-global-core.md
            """)
        )
        (rules_dir / "000-global-core.md").write_text("content")

        with patch("ai_rules.commands.refs.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["refs", "check"])

        assert result.exit_code == 0
        assert "VALIDATION PASSED" in result.output

    def test_explicit_paths_override_project_root(self, tmp_path: Path):
        """Test explicit --index-path and --rules-dir override project root defaults."""
        # Create explicit paths (not under any pyproject.toml)
        index_file = tmp_path / "custom" / "RULES_INDEX.md"
        index_file.parent.mkdir()
        index_file.write_text("Rules: 000-test.md")

        custom_rules = tmp_path / "custom" / "rules"
        custom_rules.mkdir()
        (custom_rules / "000-test.md").write_text("content")

        result = runner.invoke(
            app,
            [
                "refs",
                "check",
                "--index-path",
                str(index_file),
                "--rules-dir",
                str(custom_rules),
            ],
        )

        assert result.exit_code == 0
        assert "VALIDATION PASSED" in result.output

    def test_error_when_no_project_root_found(self):
        """Test exit code 1 when find_project_root() raises FileNotFoundError."""
        with patch(
            "ai_rules.commands.refs.find_project_root",
            side_effect=FileNotFoundError("no pyproject.toml"),
        ):
            result = runner.invoke(app, ["refs", "check"])

        assert result.exit_code == 1
        assert "Could not find project root" in result.output
