"""Tests for scripts/badge_updater.py README badge update functionality.

Tests follow pytest best practices:
- AAA pattern (Arrange-Act-Assert)
- Function-scoped fixtures
- Parametrized tests for input matrices
- Test markers for selective execution
- Isolation with tmp_path
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import module under test
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts import badge_updater as bu


class TestVersionExtraction:
    """Test version extraction from pyproject.toml."""

    @pytest.mark.unit
    def test_extract_version_valid_file(self, tmp_path: Path):
        """Test extracting version from valid pyproject.toml."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test"\nversion = "1.2.3"\ndescription = "test"')

        # Act
        version = bu.extract_version(pyproject)

        # Assert
        assert version == "1.2.3"

    @pytest.mark.unit
    def test_extract_version_different_format(self, tmp_path: Path):
        """Test extracting version with different formatting."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion="3.1.0"\n')

        # Act
        version = bu.extract_version(pyproject)

        # Assert
        assert version == "3.1.0"

    @pytest.mark.unit
    def test_extract_version_missing_field(self, tmp_path: Path):
        """Test error when version field is missing."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test"\n')

        # Act & Assert
        with pytest.raises(ValueError, match="Could not find version"):
            bu.extract_version(pyproject)

    @pytest.mark.unit
    def test_extract_version_multiline_content(self, tmp_path: Path):
        """Test version extraction from complex multiline pyproject.toml."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        content = """
[project]
name = "ai-coding-rules"
description = "AI coding rules"
version = "2.5.1"
authors = [
    {name = "Test", email = "test@example.com"}
]
"""
        pyproject.write_text(content)

        # Act
        version = bu.extract_version(pyproject)

        # Assert
        assert version == "2.5.1"


class TestTestPercentageCalculation:
    """Test pytest output parsing and percentage calculation."""

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_get_test_percentage_all_passed(self, mock_run: MagicMock):
        """Test parsing pytest output when all tests pass."""
        # Arrange
        mock_run.return_value = MagicMock(
            stdout="======================== 100 passed in 1.23s ========================\n",
            stderr="",
        )

        # Act
        passed, total, percentage = bu.get_test_percentage()

        # Assert
        assert passed == 100
        assert total == 100
        assert percentage == 100.0

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_get_test_percentage_some_failed(self, mock_run: MagicMock):
        """Test parsing pytest output with failures."""
        # Arrange
        mock_run.return_value = MagicMock(
            stdout="=============== 45 passed, 5 failed in 2.34s ===============\n",
            stderr="",
        )

        # Act
        passed, total, percentage = bu.get_test_percentage()

        # Assert
        assert passed == 45
        assert total == 50
        assert percentage == 90.0

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_get_test_percentage_all_failed(self, mock_run: MagicMock):
        """Test parsing pytest output when all tests fail."""
        # Arrange
        mock_run.return_value = MagicMock(
            stdout="======================== 10 failed in 0.56s ========================\n",
            stderr="",
        )

        # Act
        passed, total, percentage = bu.get_test_percentage()

        # Assert
        assert passed == 0
        assert total == 10
        assert percentage == 0.0

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_get_test_percentage_with_skipped(self, mock_run: MagicMock):
        """Test parsing pytest output with skipped tests."""
        # Arrange
        mock_run.return_value = MagicMock(
            stdout="=============== 80 passed, 2 failed, 3 skipped in 1.5s ===============\n",
            stderr="",
        )

        # Act
        passed, total, percentage = bu.get_test_percentage()

        # Assert
        assert passed == 80
        assert total == 82
        assert percentage == pytest.approx(97.56, abs=0.01)

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_get_test_percentage_no_tests(self, mock_run: MagicMock):
        """Test handling when no tests are found."""
        # Arrange
        mock_run.return_value = MagicMock(
            stdout="======================== no tests ran in 0.01s ========================\n",
            stderr="",
        )

        # Act
        passed, total, percentage = bu.get_test_percentage()

        # Assert
        assert passed == 0
        assert total == 0
        assert percentage == 0.0

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_get_test_percentage_timeout(self, mock_run: MagicMock):
        """Test handling subprocess timeout."""
        # Arrange
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("pytest", 60)

        # Act
        passed, total, percentage = bu.get_test_percentage()

        # Assert
        assert passed == 0
        assert total == 0
        assert percentage == 0.0

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_get_test_percentage_exception(self, mock_run: MagicMock):
        """Test handling general exception."""
        # Arrange
        mock_run.side_effect = RuntimeError("Test error")

        # Act
        passed, total, percentage = bu.get_test_percentage()

        # Assert
        assert passed == 0
        assert total == 0
        assert percentage == 0.0


class TestBadgeUpdating:
    """Test README badge update logic."""

    @pytest.mark.unit
    def test_update_readme_badges_replaces_existing(self, tmp_path: Path):
        """Test updating existing badges in README."""
        # Arrange
        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n"
            "![Version](https://img.shields.io/badge/version-1.0.0-blue)\n"
            "![Tests](https://img.shields.io/badge/tests-80%25%20passing-yellow)\n"
            "Content"
        )

        # Act
        bu.update_readme_badges(readme, "2.0.0", 95.0)

        # Assert
        content = readme.read_text()
        assert "version-2.0.0-blue" in content
        assert "tests-95%25%20passing-brightgreen" in content
        assert "version-1.0.0" not in content
        assert "tests-80" not in content

    @pytest.mark.unit
    def test_update_readme_badges_inserts_missing(self, tmp_path: Path):
        """Test inserting badges when they don't exist."""
        # Arrange
        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n"
            "[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)]\n"
            "Content"
        )

        # Act
        bu.update_readme_badges(readme, "3.1.0", 100.0)

        # Assert
        content = readme.read_text()
        assert "version-3.1.0-blue" in content
        assert "tests-100%25%20passing-brightgreen" in content
        # Version badge should be on line after license badge
        lines = content.split("\n")
        license_idx = next(i for i, line in enumerate(lines) if "License: Apache" in line)
        assert "version-3.1.0" in lines[license_idx + 1]

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "percentage,expected_color",
        [
            (100.0, "brightgreen"),
            (95.0, "brightgreen"),
            (80.0, "brightgreen"),
            (79.9, "yellow"),
            (70.0, "yellow"),
            (60.0, "yellow"),
            (59.9, "red"),
            (30.0, "red"),
            (0.0, "red"),
        ],
    )
    def test_update_readme_badges_color_thresholds(
        self, tmp_path: Path, percentage: float, expected_color: str
    ):
        """Test badge color changes based on test percentage thresholds."""
        # Arrange
        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n![Tests](https://img.shields.io/badge/tests-50%25%20passing-yellow)\n"
        )

        # Act
        bu.update_readme_badges(readme, "1.0.0", percentage)

        # Assert
        content = readme.read_text()
        assert f"passing-{expected_color}" in content

    @pytest.mark.unit
    def test_update_readme_badges_no_license_badge(self, tmp_path: Path):
        """Test behavior when license badge not found (no insertion point)."""
        # Arrange
        readme = tmp_path / "README.md"
        readme.write_text("# Project\nContent without badges")

        # Act
        bu.update_readme_badges(readme, "1.0.0", 90.0)

        # Assert
        content = readme.read_text()
        # Badges won't be inserted if no license badge exists
        assert "version-1.0.0" not in content
        assert "tests-90" not in content

    @pytest.mark.unit
    def test_update_readme_badges_preserves_content(self, tmp_path: Path):
        """Test that badge updates preserve other README content."""
        # Arrange
        readme = tmp_path / "README.md"
        original_content = (
            "# AI Coding Rules\n"
            "![Version](https://img.shields.io/badge/version-1.0.0-blue)\n"
            "![Tests](https://img.shields.io/badge/tests-80%25%20passing-yellow)\n"
            "\n"
            "## Overview\n"
            "This is important content.\n"
            "\n"
            "## Features\n"
            "- Feature 1\n"
            "- Feature 2\n"
        )
        readme.write_text(original_content)

        # Act
        bu.update_readme_badges(readme, "2.0.0", 95.0)

        # Assert
        content = readme.read_text()
        assert "## Overview" in content
        assert "This is important content." in content
        assert "## Features" in content
        assert "- Feature 1" in content
        assert "- Feature 2" in content


class TestMainFunction:
    """Test main entry point integration."""

    @pytest.mark.integration
    def test_main_success(self, tmp_path: Path):
        """Test successful main execution."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.0.0"\n')

        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n"
            "[![License: Apache-2.0](link)]\n"
            "![Version](https://img.shields.io/badge/version-0.0.1-blue)\n"
            "![Tests](https://img.shields.io/badge/tests-50%25%20passing-yellow)\n"
        )

        # Act
        with (
            patch("scripts.badge_updater.Path") as mock_path,
            patch("scripts.badge_updater.get_test_percentage") as mock_tests,
        ):
            mock_path.return_value.parent.parent = tmp_path
            mock_path(__file__).parent.parent = tmp_path
            mock_tests.return_value = (100, 100, 100.0)

            exit_code = bu.main()

        # Assert
        assert exit_code == 0
        content = readme.read_text()
        assert "version-1.0.0" in content
        assert "tests-100%25%20passing" in content

    @pytest.mark.integration
    def test_main_missing_pyproject(self, tmp_path: Path):
        """Test main when pyproject.toml is missing."""
        # Arrange - no pyproject.toml created
        readme = tmp_path / "README.md"
        readme.write_text("# Project\n")

        # Act
        with patch("scripts.badge_updater.Path") as mock_path:
            mock_path.return_value.parent.parent = tmp_path
            mock_path(__file__).parent.parent = tmp_path

            exit_code = bu.main()

        # Assert
        assert exit_code == 1

    @pytest.mark.integration
    def test_main_missing_readme(self, tmp_path: Path):
        """Test main when README.md is missing."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.0.0"\n')
        # No README.md created

        # Act
        with patch("scripts.badge_updater.Path") as mock_path:
            mock_path.return_value.parent.parent = tmp_path
            mock_path(__file__).parent.parent = tmp_path

            exit_code = bu.main()

        # Assert
        assert exit_code == 1

    @pytest.mark.integration
    def test_main_exception_handling(self, tmp_path: Path):
        """Test main handles exceptions gracefully."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "1.0.0"\n')

        readme = tmp_path / "README.md"
        readme.write_text("# Project\n")

        # Act
        with (
            patch("scripts.badge_updater.Path") as mock_path,
            patch("scripts.badge_updater.get_test_percentage") as mock_tests,
        ):
            mock_path.return_value.parent.parent = tmp_path
            mock_path(__file__).parent.parent = tmp_path
            mock_tests.side_effect = RuntimeError("Test error")

            exit_code = bu.main()

        # Assert
        assert exit_code == 1


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.unit
    def test_extract_version_whitespace_variations(self, tmp_path: Path):
        """Test version extraction with various whitespace patterns."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('version   =   "1.2.3"  \n')

        # Act
        version = bu.extract_version(pyproject)

        # Assert
        assert version == "1.2.3"

    @pytest.mark.unit
    @patch("subprocess.run")
    def test_get_test_percentage_stderr_output(self, mock_run: MagicMock):
        """Test parsing when pytest output is in stderr."""
        # Arrange
        mock_run.return_value = MagicMock(
            stdout="",
            stderr="======================== 50 passed in 1.0s ========================\n",
        )

        # Act
        passed, total, percentage = bu.get_test_percentage()

        # Assert
        assert passed == 50
        assert total == 50
        assert percentage == 100.0

    @pytest.mark.unit
    def test_update_readme_badges_exact_percentage(self, tmp_path: Path):
        """Test badge formatting with decimal percentages."""
        # Arrange
        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n![Tests](https://img.shields.io/badge/tests-50%25%20passing-yellow)\n"
        )

        # Act
        bu.update_readme_badges(readme, "1.0.0", 97.561)

        # Assert
        content = readme.read_text()
        # Should round to nearest integer
        assert "tests-98%25%20passing" in content

    @pytest.mark.unit
    def test_update_readme_badges_multiple_badge_lines(self, tmp_path: Path):
        """Test updating when badges are on separate lines."""
        # Arrange
        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n\n"
            "![Version](https://img.shields.io/badge/version-1.0.0-blue)\n"
            "![Tests](https://img.shields.io/badge/tests-80%25%20passing-yellow)\n"
            "![Python](https://img.shields.io/badge/python-3.11-blue)\n\n"
            "Content"
        )

        # Act
        bu.update_readme_badges(readme, "2.0.0", 100.0)

        # Assert
        content = readme.read_text()
        assert "version-2.0.0-blue" in content
        assert "tests-100%25%20passing-brightgreen" in content
        # Other badges should be preserved
        assert "python-3.11-blue" in content


# Run tests with: pytest tests/test_badge_updater.py -v
