"""Tests for scripts/rule_deployer.py (v3.0 - production-ready rules).

Tests the new simplified deployment workflow that copies production-ready rules
from rules/ directory to destination without any generation step.

Tests follow pytest best practices:
- AAA pattern (Arrange-Act-Assert)
- Function-scoped fixtures
- Parametrized tests for input matrices
- Test markers for selective execution
- Isolation with tmp_path
"""

import argparse
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Import module under test
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts import rule_deployer as dr


@pytest.fixture
def mock_project_root(tmp_path: Path) -> Path:
    """Create a minimal project structure for testing."""
    project = tmp_path / "ai_coding_rules"
    project.mkdir()

    # Create rules directory with sample files
    rules_dir = project / "rules"
    rules_dir.mkdir()
    (rules_dir / "000-global-core.md").write_text("# Global Core Rule\nContent here")
    (rules_dir / "100-snowflake-core.md").write_text("# Snowflake Rule\nContent here")
    (rules_dir / "200-python-core.md").write_text("# Python Rule\nContent here")

    # Create root files
    (project / "AGENTS.md").write_text("# AGENTS\nRule loading instructions")
    (project / "rules/RULES_INDEX.md").write_text("# Rules Index\nRule catalog")

    # Create scripts directory (where rule_deployer.py would be)
    scripts_dir = project / "scripts"
    scripts_dir.mkdir()

    return project


@pytest.fixture
def dest_dir(tmp_path: Path) -> Path:
    """Create a temporary destination directory."""
    dest = tmp_path / "destination"
    dest.mkdir()
    return dest


class TestValidateSourceStructure:
    """Test source structure validation."""

    @pytest.mark.unit
    def test_valid_structure(self, mock_project_root: Path) -> None:
        """Test validation passes with complete source structure."""
        # Act
        is_valid, errors = dr.validate_source_structure(mock_project_root)

        # Assert
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_missing_rules_directory(self, tmp_path: Path) -> None:
        """Test validation fails when rules/ directory is missing."""
        # Arrange
        project = tmp_path / "incomplete_project"
        project.mkdir()
        (project / "AGENTS.md").write_text("content")
        (project / "rules/RULES_INDEX.md").write_text("content")

        # Act
        is_valid, errors = dr.validate_source_structure(project)

        # Assert
        assert is_valid is False
        assert any("rules directory not found" in e.lower() for e in errors)

    @pytest.mark.unit
    def test_missing_agents_md(self, mock_project_root: Path) -> None:
        """Test validation fails when AGENTS.md is missing."""
        # Arrange
        (mock_project_root / "AGENTS.md").unlink()

        # Act
        is_valid, errors = dr.validate_source_structure(mock_project_root)

        # Assert
        assert is_valid is False
        assert any("AGENTS.md not found" in e for e in errors)

    @pytest.mark.unit
    def test_missing_rules_index(self, mock_project_root: Path) -> None:
        """Test validation fails when RULES_INDEX.md is missing."""
        # Arrange
        (mock_project_root / "rules/RULES_INDEX.md").unlink()

        # Act
        is_valid, errors = dr.validate_source_structure(mock_project_root)

        # Assert
        assert is_valid is False
        assert any("RULES_INDEX.md not found" in e for e in errors)

    @pytest.mark.unit
    def test_empty_rules_directory(self, mock_project_root: Path) -> None:
        """Test validation fails when rules/ directory is empty."""
        # Arrange
        rules_dir = mock_project_root / "rules"
        for rule_file in rules_dir.glob("*.md"):
            rule_file.unlink()

        # Act
        is_valid, errors = dr.validate_source_structure(mock_project_root)

        # Assert
        assert is_valid is False
        assert any("No .md files found" in e for e in errors)

    @pytest.mark.unit
    def test_rules_path_is_file_not_directory(self, tmp_path: Path) -> None:
        """Test validation fails when rules path is a file instead of directory."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        # Create rules as a file, not a directory
        (project / "rules").write_text("not a directory")
        (project / "AGENTS.md").write_text("# Agents")
        (project / "rules/RULES_INDEX.md").write_text("# Index")

        # Act
        is_valid, errors = dr.validate_source_structure(project)

        # Assert
        assert is_valid is False
        assert any("not a directory" in e for e in errors)


class TestCopyRules:
    """Test rule file copying functionality."""

    @pytest.mark.unit
    def test_copy_all_rules(self, mock_project_root: Path, dest_dir: Path) -> None:
        """Test copying all rule files to destination."""
        # Arrange
        source_rules = mock_project_root / "rules"

        # Act
        files_copied, files_failed = dr.copy_rules(
            source_rules, dest_dir, dry_run=False, verbose=False
        )

        # Assert
        assert files_copied == 3  # 3 rule files in fixture
        assert files_failed == 0
        assert (dest_dir / "rules" / "000-global-core.md").exists()
        assert (dest_dir / "rules" / "100-snowflake-core.md").exists()
        assert (dest_dir / "rules" / "200-python-core.md").exists()

    @pytest.mark.unit
    def test_dry_run_no_copy(self, mock_project_root: Path, dest_dir: Path) -> None:
        """Test dry-run mode doesn't actually copy files."""
        # Arrange
        source_rules = mock_project_root / "rules"

        # Act
        files_copied, files_failed = dr.copy_rules(
            source_rules, dest_dir, dry_run=True, verbose=False
        )

        # Assert
        assert files_copied == 3  # Reports would copy
        assert files_failed == 0
        assert not (dest_dir / "rules").exists()  # No actual copy

    @pytest.mark.unit
    def test_empty_source_directory(self, tmp_path: Path, dest_dir: Path) -> None:
        """Test copying from empty source directory."""
        # Arrange
        empty_rules = tmp_path / "empty_rules"
        empty_rules.mkdir()

        # Act
        files_copied, files_failed = dr.copy_rules(
            empty_rules, dest_dir, dry_run=False, verbose=False
        )

        # Assert
        assert files_copied == 0
        assert files_failed == 0

    @pytest.mark.unit
    def test_copy_failure_handles_exception(self, mock_project_root: Path, tmp_path: Path) -> None:
        """Test that copy failures are handled gracefully."""
        # Arrange
        source_rules = mock_project_root / "rules"
        dest_dir = tmp_path / "dest"

        # Act - mock shutil.copy2 to raise exception
        with patch("shutil.copy2") as mock_copy:
            mock_copy.side_effect = PermissionError("Permission denied")
            files_copied, files_failed = dr.copy_rules(
                source_rules, dest_dir, dry_run=False, verbose=False
            )

        # Assert
        assert files_copied == 0
        assert files_failed == 3  # All 3 files should fail


class TestCopyRootFiles:
    """Test root file (AGENTS.md, RULES_INDEX.md) copying."""

    @pytest.mark.unit
    def test_copy_root_files(self, mock_project_root: Path, dest_dir: Path) -> None:
        """Test copying AGENTS.md and RULES_INDEX.md."""
        # Act
        files_copied, files_failed = dr.copy_root_files(
            mock_project_root, dest_dir, dry_run=False, verbose=False
        )

        # Assert
        assert files_copied == 2
        assert files_failed == 0
        assert (dest_dir / "AGENTS.md").exists()
        assert (dest_dir / "rules/RULES_INDEX.md").exists()

    @pytest.mark.unit
    def test_dry_run_root_files(self, mock_project_root: Path, dest_dir: Path) -> None:
        """Test dry-run mode for root files."""
        # Act
        files_copied, files_failed = dr.copy_root_files(
            mock_project_root, dest_dir, dry_run=True, verbose=False
        )

        # Assert
        assert files_copied == 2  # Reports would copy
        assert files_failed == 0
        assert not (dest_dir / "AGENTS.md").exists()  # No actual copy
        assert not (dest_dir / "rules/RULES_INDEX.md").exists()

    @pytest.mark.unit
    def test_root_files_copy_failure(self, mock_project_root: Path, tmp_path: Path) -> None:
        """Test handling of root file copy failures."""
        # Arrange
        dest_dir = tmp_path / "dest"

        # Act - mock shutil.copy2 to raise exception
        with patch("shutil.copy2") as mock_copy:
            mock_copy.side_effect = OSError("Disk full")
            files_copied, files_failed = dr.copy_root_files(
                mock_project_root, dest_dir, dry_run=False, verbose=False
            )

        # Assert
        assert files_copied == 0
        assert files_failed == 2  # Both AGENTS.md and RULES_INDEX.md should fail


class TestDeployRules:
    """Test end-to-end deployment functionality."""

    @pytest.mark.integration
    def test_successful_deployment(self, mock_project_root: Path, dest_dir: Path) -> None:
        """Test complete successful deployment."""
        # Act
        with patch("scripts.rule_deployer.Path") as mock_path:
            # Mock script location to return our test project root
            mock_path(__file__).resolve.return_value.parent.parent = mock_project_root

            success = dr.deploy_rules(dest_dir, dry_run=False, verbose=False)

        # Assert
        assert success is True
        assert (dest_dir / "rules" / "000-global-core.md").exists()
        assert (dest_dir / "AGENTS.md").exists()
        assert (dest_dir / "rules/RULES_INDEX.md").exists()

    @pytest.mark.integration
    def test_deployment_dry_run(self, mock_project_root: Path, dest_dir: Path) -> None:
        """Test deployment in dry-run mode."""
        # Act
        with patch("scripts.rule_deployer.Path") as mock_path:
            mock_path(__file__).resolve.return_value.parent.parent = mock_project_root

            success = dr.deploy_rules(dest_dir, dry_run=True, verbose=False)

        # Assert
        assert success is True
        # Verify no files were actually copied
        assert not (dest_dir / "rules").exists()
        assert not (dest_dir / "AGENTS.md").exists()

    @pytest.mark.integration
    def test_deployment_invalid_source(self, tmp_path: Path, dest_dir: Path) -> None:
        """Test deployment fails with invalid source structure."""
        # Arrange
        invalid_project = tmp_path / "invalid"
        invalid_project.mkdir()

        # Act
        with patch("scripts.rule_deployer.Path") as mock_path:
            mock_path(__file__).resolve.return_value.parent.parent = invalid_project

            success = dr.deploy_rules(dest_dir, dry_run=False, verbose=False)

        # Assert
        assert success is False

    @pytest.mark.integration
    def test_deployment_with_copy_failures(self, mock_project_root: Path, dest_dir: Path) -> None:
        """Test deployment reports failure when files fail to copy."""
        # Act - mock shutil.copy2 to fail for some files
        with (
            patch("scripts.rule_deployer.Path") as mock_path,
            patch("shutil.copy2") as mock_copy,
        ):
            mock_path(__file__).resolve.return_value.parent.parent = mock_project_root
            mock_copy.side_effect = Exception("Copy failed")

            success = dr.deploy_rules(dest_dir, dry_run=False, verbose=False)

        # Assert
        assert success is False  # Should report failure due to copy errors


class TestCLIArguments:
    """Test command-line argument parsing."""

    @pytest.mark.unit
    def test_dest_required(self) -> None:
        """Test that --dest argument is required."""
        # Act & Assert
        with pytest.raises(SystemExit) as exc_info, patch("sys.argv", ["rule_deployer.py"]):
            dr.main()

        assert exc_info.value.code != 0

    @pytest.mark.integration
    def test_dry_run_flag(self, mock_project_root: Path, tmp_path: Path) -> None:
        """Test --dry-run flag is respected."""
        # Arrange
        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        with (
            patch("sys.argv", ["rule_deployer.py", "--dest", str(dest), "--dry-run"]),
            patch("scripts.rule_deployer.Path") as mock_path,
        ):
            mock_path(__file__).resolve.return_value.parent.parent = mock_project_root

            exit_code = dr.main()

        # Assert
        assert exit_code == 0
        assert not (dest / "rules").exists()  # Dry run - no copy

    @pytest.mark.unit
    def test_quiet_verbose_argument_logic(self) -> None:
        """Test that quiet and verbose flags work correctly together."""
        # Test quiet overrides verbose
        parser = argparse.ArgumentParser()
        parser.add_argument("--dest", type=Path, required=False)
        parser.add_argument("--verbose", action="store_true", default=True)
        parser.add_argument("--quiet", action="store_true")

        # Case 1: quiet flag set
        args = parser.parse_args(["--dest", "/tmp", "--quiet"])
        verbose = args.verbose and not args.quiet
        assert verbose is False

        # Case 2: verbose flag set (default)
        args = parser.parse_args(["--dest", "/tmp"])
        verbose = args.verbose and not args.quiet
        assert verbose is True

        # Case 3: verbose explicitly set
        args = parser.parse_args(["--dest", "/tmp", "--verbose"])
        verbose = args.verbose and not args.quiet
        assert verbose is True

    @pytest.mark.integration
    def test_main_deployment_failure(self, tmp_path: Path) -> None:
        """Test main returns non-zero exit code on deployment failure."""
        # Arrange
        invalid_project = tmp_path / "invalid"
        invalid_project.mkdir()
        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        with (
            patch("sys.argv", ["rule_deployer.py", "--dest", str(dest)]),
            patch("scripts.rule_deployer.Path") as mock_path,
        ):
            mock_path(__file__).resolve.return_value.parent.parent = invalid_project

            exit_code = dr.main()

        # Assert
        assert exit_code == 1  # Should return error code


# Run tests with: pytest tests/test_deployment.py -v
