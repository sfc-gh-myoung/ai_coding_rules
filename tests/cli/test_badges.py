"""Tests for ai-rules badges CLI command.

Tests follow pytest best practices:
- AAA pattern (Arrange-Act-Assert)
- Function-scoped fixtures
- Parametrized tests for input matrices
- Test markers for selective execution
- Isolation with tmp_path
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands import badges

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})


class TestBadgesHelpOutput:
    """Test --help output for badges command."""

    @pytest.mark.unit
    def test_badges_help_shows_command_description(self):
        """Test that --help shows command description."""
        # Act
        result = runner.invoke(app, ["badges", "--help"])

        # Assert
        assert result.exit_code == 0
        assert "Update README badges" in result.output
        assert "update" in result.output

    @pytest.mark.unit
    def test_badges_help_shows_dry_run_option(self):
        """Test that --help for update subcommand shows --dry-run option."""
        # Act
        result = runner.invoke(app, ["badges", "update", "--help"])

        # Assert
        assert result.exit_code == 0
        assert "--dry-run" in result.output


class TestBadgesHappyPath:
    """Test successful badge update scenarios."""

    @pytest.mark.unit
    def test_badges_updates_readme(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test successful badge update with mocked dependencies."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.2.3"\n')

        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n"
            "[![License: Apache-2.0](link)]\n"
            "![Version](https://img.shields.io/badge/version-1.0.0-blue)\n"
            "![Tests](https://img.shields.io/badge/tests-80%25%20passing-yellow)\n"
            "![Coverage](https://img.shields.io/badge/coverage-70%25-yellow)\n"
        )

        htmlcov = tmp_path / "htmlcov"
        htmlcov.mkdir()
        (htmlcov / "index.html").write_text('<span class="pc_cov">95%</span>')

        monkeypatch.setattr(badges, "find_project_root", lambda: tmp_path)

        with patch.object(badges, "get_test_percentage", return_value=(98, 100, 98.0)):
            # Act
            result = runner.invoke(app, ["badges", "update"])

        # Assert
        assert result.exit_code == 0
        content = readme.read_text()
        assert "version-1.2.3-blue" in content
        assert "tests-98%25%20passing-brightgreen" in content
        assert "coverage-95%25-brightgreen" in content

    @pytest.mark.unit
    def test_badges_all_tests_pass(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test badge update when all tests pass."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "2.0.0"\n')

        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n"
            "![Version](https://img.shields.io/badge/version-1.0.0-blue)\n"
            "![Tests](https://img.shields.io/badge/tests-0%25%20passing-red)\n"
            "![Coverage](https://img.shields.io/badge/coverage-0%25-red)\n"
        )

        htmlcov = tmp_path / "htmlcov"
        htmlcov.mkdir()
        (htmlcov / "index.html").write_text('<span class="pc_cov">100%</span>')

        monkeypatch.setattr(badges, "find_project_root", lambda: tmp_path)

        with patch.object(badges, "get_test_percentage", return_value=(100, 100, 100.0)):
            # Act
            result = runner.invoke(app, ["badges", "update"])

        # Assert
        assert result.exit_code == 0
        content = readme.read_text()
        assert "tests-100%25%20passing-brightgreen" in content
        assert "coverage-100%25-brightgreen" in content


class TestBadgesDryRun:
    """Test --dry-run flag behavior."""

    @pytest.mark.unit
    def test_dry_run_does_not_modify_readme(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test that --dry-run does not write to README."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "3.0.0"\n')

        readme = tmp_path / "README.md"
        original_content = (
            "# Project\n"
            "![Version](https://img.shields.io/badge/version-1.0.0-blue)\n"
            "![Tests](https://img.shields.io/badge/tests-50%25%20passing-yellow)\n"
        )
        readme.write_text(original_content)

        htmlcov = tmp_path / "htmlcov"
        htmlcov.mkdir()
        (htmlcov / "index.html").write_text('<span class="pc_cov">90%</span>')

        monkeypatch.setattr(badges, "find_project_root", lambda: tmp_path)

        with patch.object(badges, "get_test_percentage", return_value=(90, 100, 90.0)):
            # Act
            result = runner.invoke(app, ["badges", "update", "--dry-run"])

        # Assert
        assert result.exit_code == 0
        assert "Would update badges" in result.output
        # README should be unchanged
        assert readme.read_text() == original_content

    @pytest.mark.unit
    def test_dry_run_shows_planned_changes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test that --dry-run shows what would change."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "4.5.6"\n')

        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n![Version](https://img.shields.io/badge/version-1.0.0-blue)\n"
        )

        htmlcov = tmp_path / "htmlcov"
        htmlcov.mkdir()
        (htmlcov / "index.html").write_text('<span class="pc_cov">85%</span>')

        monkeypatch.setattr(badges, "find_project_root", lambda: tmp_path)

        with patch.object(badges, "get_test_percentage", return_value=(85, 100, 85.0)):
            # Act
            result = runner.invoke(app, ["badges", "update", "--dry-run"])

        # Assert
        assert result.exit_code == 0
        assert "4.5.6" in result.output
        assert "85%" in result.output


class TestBadgesErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.unit
    def test_missing_pyproject_toml(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test error when pyproject.toml is missing."""
        # Arrange
        readme = tmp_path / "README.md"
        readme.write_text("# Project\n")
        # No pyproject.toml

        monkeypatch.setattr(badges, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["badges", "update"])

        # Assert
        assert result.exit_code == 1
        assert "not found" in result.output

    @pytest.mark.unit
    def test_missing_readme(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test error when README.md is missing."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.0.0"\n')
        # No README.md

        monkeypatch.setattr(badges, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["badges", "update"])

        # Assert
        assert result.exit_code == 1
        assert "not found" in result.output

    @pytest.mark.unit
    def test_missing_project_root(self, monkeypatch: pytest.MonkeyPatch):
        """Test error when project root cannot be found."""

        # Arrange
        def raise_not_found():
            raise FileNotFoundError("Could not find project root")

        monkeypatch.setattr(badges, "find_project_root", raise_not_found)

        # Act
        result = runner.invoke(app, ["badges", "update"])

        # Assert
        assert result.exit_code == 1
        assert "project root" in result.output.lower()

    @pytest.mark.unit
    def test_missing_version_in_pyproject(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test error when version is missing from pyproject.toml."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test"\n')  # No version

        readme = tmp_path / "README.md"
        readme.write_text("# Project\n")

        monkeypatch.setattr(badges, "find_project_root", lambda: tmp_path)

        # Act
        result = runner.invoke(app, ["badges", "update"])

        # Assert
        assert result.exit_code == 1
        assert "version" in result.output.lower()


class TestBadgesFunctions:
    """Test individual badge functions directly."""

    @pytest.mark.unit
    def test_extract_version_valid(self, tmp_path: Path):
        """Test version extraction from valid pyproject.toml."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.2.3"\n')

        # Act
        version = badges.extract_version(pyproject)

        # Assert
        assert version == "1.2.3"

    @pytest.mark.unit
    def test_extract_version_missing(self, tmp_path: Path):
        """Test version extraction when version is missing."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test"\n')

        # Act & Assert
        with pytest.raises(ValueError, match="Could not find version"):
            badges.extract_version(pyproject)

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "percentage,expected_color",
        [
            (100.0, "brightgreen"),
            (80.0, "brightgreen"),
            (79.9, "yellow"),
            (60.0, "yellow"),
            (59.9, "red"),
            (0.0, "red"),
        ],
    )
    def test_get_badge_color(self, percentage: float, expected_color: str):
        """Test badge color selection for various percentages."""
        # Act
        color = badges.get_badge_color(percentage)

        # Assert
        assert color == expected_color

    @pytest.mark.unit
    def test_get_coverage_percentage_valid(self, tmp_path: Path):
        """Test coverage extraction from valid htmlcov."""
        # Arrange
        htmlcov = tmp_path / "htmlcov"
        htmlcov.mkdir()
        (htmlcov / "index.html").write_text('<span class="pc_cov">96%</span>')

        # Act
        coverage = badges.get_coverage_percentage(tmp_path)

        # Assert
        assert coverage == 96.0

    @pytest.mark.unit
    def test_get_coverage_percentage_missing_file(self, tmp_path: Path):
        """Test coverage returns 0 when file is missing."""
        # Act
        coverage = badges.get_coverage_percentage(tmp_path)

        # Assert
        assert coverage == 0.0

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_get_test_percentage_all_passed(self, mock_run: MagicMock):
        """Test parsing pytest output when all tests pass."""
        # Arrange
        mock_run.return_value = MagicMock(
            stdout="======================== 50 passed in 1.0s ========================\n",
            stderr="",
        )

        # Act
        passed, total, percentage = badges.get_test_percentage()

        # Assert
        assert passed == 50
        assert total == 50
        assert percentage == 100.0

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_get_test_percentage_with_failures(self, mock_run: MagicMock):
        """Test parsing pytest output with failures."""
        # Arrange
        mock_run.return_value = MagicMock(
            stdout="=============== 45 passed, 5 failed in 2.0s ===============\n",
            stderr="",
        )

        # Act
        passed, total, percentage = badges.get_test_percentage()

        # Assert
        assert passed == 45
        assert total == 50
        assert percentage == 90.0


class TestUpdateReadmeBadges:
    """Test the update_readme_badges function."""

    @pytest.mark.unit
    def test_update_existing_badges(self, tmp_path: Path):
        """Test updating existing badges."""
        # Arrange
        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n"
            "![Version](https://img.shields.io/badge/version-1.0.0-blue)\n"
            "![Tests](https://img.shields.io/badge/tests-80%25%20passing-yellow)\n"
            "![Coverage](https://img.shields.io/badge/coverage-70%25-yellow)\n"
        )

        # Act
        badges.update_readme_badges(readme, "2.0.0", 95.0, 98.0)

        # Assert
        content = readme.read_text()
        assert "version-2.0.0-blue" in content
        assert "tests-95%25%20passing-brightgreen" in content
        assert "coverage-98%25-brightgreen" in content

    @pytest.mark.unit
    def test_insert_missing_badges(self, tmp_path: Path):
        """Test inserting badges when they don't exist."""
        # Arrange
        readme = tmp_path / "README.md"
        readme.write_text("# Project\n[![License: Apache-2.0](link)]\nContent here\n")

        # Act
        badges.update_readme_badges(readme, "1.0.0", 90.0, 85.0)

        # Assert
        content = readme.read_text()
        assert "version-1.0.0-blue" in content
        assert "tests-90%25%20passing-brightgreen" in content
        assert "coverage-85%25-brightgreen" in content

    @pytest.mark.unit
    def test_preserves_other_content(self, tmp_path: Path):
        """Test that badge updates preserve other README content."""
        # Arrange
        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n"
            "![Version](https://img.shields.io/badge/version-1.0.0-blue)\n"
            "\n"
            "## Features\n"
            "- Feature 1\n"
            "- Feature 2\n"
        )

        # Act
        badges.update_readme_badges(readme, "2.0.0", 100.0, 100.0)

        # Assert
        content = readme.read_text()
        assert "## Features" in content
        assert "- Feature 1" in content
        assert "- Feature 2" in content


class TestGetTestPercentageEdgeCases:
    """Test edge cases in get_test_percentage."""

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_no_passed_no_failed_returns_zero(self, mock_run: MagicMock):
        """Test returns zeros when pytest output has no passed/failed counts."""
        # Arrange — output with no "passed" or "failed" tokens
        mock_run.return_value = MagicMock(
            stdout="no tests ran in 0.01s\n",
            stderr="",
        )

        # Act
        passed, total, percentage = badges.get_test_percentage()

        # Assert
        assert passed == 0
        assert total == 0
        assert percentage == 0.0

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_timeout_returns_zero(self, mock_run: MagicMock):
        """Test returns zeros when pytest times out."""
        import subprocess

        # Arrange
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="pytest", timeout=300)

        # Act
        passed, total, percentage = badges.get_test_percentage()

        # Assert
        assert passed == 0
        assert total == 0
        assert percentage == 0.0

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_generic_exception_returns_zero(self, mock_run: MagicMock):
        """Test returns zeros when subprocess raises generic exception."""
        # Arrange
        mock_run.side_effect = OSError("Command not found")

        # Act
        passed, total, percentage = badges.get_test_percentage()

        # Assert
        assert passed == 0
        assert total == 0
        assert percentage == 0.0

    @pytest.mark.unit
    def test_pre_captured_output_all_passed(self):
        """Test parsing pre-captured pytest output when all tests pass."""
        # Arrange
        output = "======================== 50 passed in 1.0s ========================\n"

        # Act
        passed, total, percentage = badges.get_test_percentage(pytest_output=output)

        # Assert
        assert passed == 50
        assert total == 50
        assert percentage == 100.0

    @pytest.mark.unit
    def test_pre_captured_output_with_failures(self):
        """Test parsing pre-captured pytest output with failures."""
        # Arrange
        output = "=============== 45 passed, 5 failed in 2.0s ===============\n"

        # Act
        passed, total, percentage = badges.get_test_percentage(pytest_output=output)

        # Assert
        assert passed == 45
        assert total == 50
        assert percentage == 90.0


class TestGetCoveragePercentageEdgeCases:
    """Test edge cases in get_coverage_percentage."""

    @pytest.mark.unit
    def test_no_match_in_html_returns_zero(self, tmp_path: Path):
        """Test returns 0 when htmlcov/index.html has no coverage span."""
        # Arrange
        htmlcov = tmp_path / "htmlcov"
        htmlcov.mkdir()
        (htmlcov / "index.html").write_text("<html><body>No coverage here</body></html>")

        # Act
        coverage = badges.get_coverage_percentage(tmp_path)

        # Assert
        assert coverage == 0.0

    @pytest.mark.unit
    def test_read_exception_returns_zero(self, tmp_path: Path):
        """Test returns 0 when reading htmlcov/index.html raises exception."""
        # Arrange
        htmlcov = tmp_path / "htmlcov"
        htmlcov.mkdir()
        html_file = htmlcov / "index.html"
        html_file.write_text('<span class="pc_cov">96%</span>')

        # Make reading fail by replacing read_text with an error
        with patch.object(Path, "read_text", side_effect=PermissionError("denied")):
            # Act
            coverage = badges.get_coverage_percentage(tmp_path)

        # Assert
        assert coverage == 0.0
