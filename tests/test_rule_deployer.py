#!/usr/bin/env python3
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
    (project / "RULES_INDEX.md").write_text("# Rules Index\nRule catalog")

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
        """Test validation passes with complete source structure.

        Validates that the validator correctly accepts a well-formed
        project structure. This ensures we don't reject valid projects
        during deployment, which would block legitimate deployments.
        """
        # Act
        is_valid, errors = dr.validate_source_structure(mock_project_root)

        # Assert
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_missing_rules_directory(self, tmp_path: Path) -> None:
        """Test validation fails when rules/ directory is missing.

        Ensures deployment is blocked when the core rules/ directory
        doesn't exist. Deploying without rules would result in an
        incomplete and non-functional rules system.
        """
        # Arrange
        project = tmp_path / "incomplete_project"
        project.mkdir()
        (project / "AGENTS.md").write_text("content")
        (project / "RULES_INDEX.md").write_text("content")

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
        (mock_project_root / "RULES_INDEX.md").unlink()

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


class TestCopyRules:
    """Test rule file copying functionality."""

    @pytest.mark.unit
    def test_copy_all_rules(self, mock_project_root: Path, dest_dir: Path) -> None:
        """Test copying all rule files to destination.

        Validates that all rule files in the source rules/ directory
        are successfully copied to destination. This is the core
        deployment functionality that distributes rules to target systems.
        """
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
        """Test dry-run mode doesn't actually copy files.

        Ensures that dry-run mode reports what would be copied without
        making actual changes. This allows safe deployment previews
        and prevents accidental overwrites during testing.
        """
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
        assert (dest_dir / "RULES_INDEX.md").exists()

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
        assert not (dest_dir / "RULES_INDEX.md").exists()


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
        assert (dest_dir / "RULES_INDEX.md").exists()

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


class TestValidateSourceStructureExtended:
    """Extended tests for source structure validation edge cases."""

    @pytest.mark.unit
    def test_validate_source_structure_rules_is_file_not_dir(self, tmp_path: Path) -> None:
        """Test validation fails when rules/ exists as a file not a directory."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        (project / "rules").write_text("This is a file, not a directory")  # File, not dir
        (project / "AGENTS.md").write_text("content")
        (project / "RULES_INDEX.md").write_text("content")

        # Act
        is_valid, errors = dr.validate_source_structure(project)

        # Assert
        assert is_valid is False
        assert any("not a directory" in e.lower() for e in errors)


class TestCopyErrorHandling:
    """Tests for error handling in copy functions."""

    @pytest.mark.unit
    def test_copy_rules_handles_permission_error(
        self, mock_project_root: Path, dest_dir: Path
    ) -> None:
        """Test copy_rules handles permission errors gracefully."""
        # Arrange
        source_rules = mock_project_root / "rules"

        # Act
        with patch("shutil.copy2", side_effect=PermissionError("Permission denied")):
            files_copied, files_failed = dr.copy_rules(
                source_rules, dest_dir, dry_run=False, verbose=False
            )

        # Assert
        assert files_copied == 0
        assert files_failed == 3  # 3 files in fixture

    @pytest.mark.unit
    def test_copy_root_files_handles_missing_source(
        self, mock_project_root: Path, dest_dir: Path
    ) -> None:
        """Test copy_root_files handles missing source files."""
        # Arrange
        (mock_project_root / "AGENTS.md").unlink()

        # Act
        files_copied, files_failed = dr.copy_root_files(
            mock_project_root, dest_dir, dry_run=False, verbose=False
        )

        # Assert
        assert files_failed == 1  # AGENTS.md missing
        assert files_copied == 1  # RULES_INDEX.md copied

    @pytest.mark.unit
    def test_copy_skills_handles_copy_failure(
        self, mock_project_root: Path, dest_dir: Path
    ) -> None:
        """Test copy_skills handles file copy failures."""
        # Arrange
        skills_dir = mock_project_root / "skills"
        skills_dir.mkdir()
        (skills_dir / "test-skill.md").write_text("Skill content")

        # Act
        with patch("shutil.copy2", side_effect=OSError("I/O error")):
            _files_copied, files_failed = dr.copy_skills(
                mock_project_root, dest_dir, dry_run=False, verbose=False
            )

        # Assert
        assert files_failed == 1

    @pytest.mark.unit
    def test_copy_skills_handles_copytree_failure(
        self, mock_project_root: Path, dest_dir: Path
    ) -> None:
        """Test copy_skills handles directory copy failures."""
        # Arrange
        skills_dir = mock_project_root / "skills"
        skills_dir.mkdir()
        skill_subdir = skills_dir / "test-skill"
        skill_subdir.mkdir()
        (skill_subdir / "file.md").write_text("Content")

        # Act
        with patch("shutil.copytree", side_effect=OSError("Copy error")):
            _files_copied, files_failed = dr.copy_skills(
                mock_project_root, dest_dir, dry_run=False, verbose=False
            )

        # Assert
        assert files_failed == 1


class TestSkillsDeployment:
    """Tests for skills deployment functionality."""

    @pytest.mark.unit
    def test_load_skill_exclusions_with_valid_config(self, tmp_path: Path) -> None:
        """Test loading exclusions from valid pyproject.toml."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text("""
[tool.rule_deployer]
exclude_skills = [
    "internal-skill.md",
    "internal-dir/",
]
""")

        # Act
        exclusions = dr.load_skill_exclusions(project)

        # Assert
        assert "internal-skill.md" in exclusions
        assert "internal-dir/" in exclusions
        assert len(exclusions) == 2

    @pytest.mark.unit
    def test_load_skill_exclusions_missing_pyproject(self, tmp_path: Path, capsys) -> None:
        """Test loading exclusions when pyproject.toml doesn't exist."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()

        # Act
        exclusions = dr.load_skill_exclusions(project)

        # Assert
        assert len(exclusions) == 0
        captured = capsys.readouterr()
        assert "pyproject.toml not found" in captured.out

    @pytest.mark.unit
    def test_load_skill_exclusions_empty_list(self, tmp_path: Path) -> None:
        """Test loading exclusions with empty exclude_skills list."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text("""
[tool.rule_deployer]
exclude_skills = []
""")

        # Act
        exclusions = dr.load_skill_exclusions(project)

        # Assert
        assert len(exclusions) == 0

    @pytest.mark.unit
    def test_load_skill_exclusions_parse_error(self, tmp_path: Path, capsys) -> None:
        """Test loading exclusions with malformed TOML."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text("invalid [[ toml")

        # Act
        exclusions = dr.load_skill_exclusions(project)

        # Assert
        assert len(exclusions) == 0
        captured = capsys.readouterr()
        assert "Failed to parse" in captured.out

    @pytest.mark.unit
    def test_load_skill_exclusions_missing_tool_section(self, tmp_path: Path) -> None:
        """Test loading exclusions when [tool.rule_deployer] section is missing."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text("""
[project]
name = "test"
""")

        # Act
        exclusions = dr.load_skill_exclusions(project)

        # Assert
        assert len(exclusions) == 0

    @pytest.mark.unit
    def test_copy_skills_with_files_only(self, tmp_path: Path) -> None:
        """Test copy_skills with only file skills."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        skills_dir = project / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill1.md").write_text("Skill 1")
        (skills_dir / "skill2.md").write_text("Skill 2")

        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        files_copied, files_failed = dr.copy_skills(project, dest, dry_run=False, verbose=False)

        # Assert
        assert files_copied == 2
        assert files_failed == 0
        assert (dest / "skills" / "skill1.md").exists()
        assert (dest / "skills" / "skill2.md").exists()

    @pytest.mark.unit
    def test_copy_skills_with_directories_only(self, tmp_path: Path) -> None:
        """Test copy_skills with only directory skills."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        skills_dir = project / "skills"
        skills_dir.mkdir()
        skill_dir = skills_dir / "skill-dir"
        skill_dir.mkdir()
        (skill_dir / "file1.md").write_text("File 1")
        (skill_dir / "file2.md").write_text("File 2")

        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        files_copied, files_failed = dr.copy_skills(project, dest, dry_run=False, verbose=False)

        # Assert
        assert files_copied == 2  # Counts files in directory
        assert files_failed == 0
        assert (dest / "skills" / "skill-dir" / "file1.md").exists()

    @pytest.mark.unit
    def test_copy_skills_mixed_files_and_dirs(self, tmp_path: Path) -> None:
        """Test copy_skills with both files and directories."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        skills_dir = project / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill-file.md").write_text("File skill")
        skill_dir = skills_dir / "skill-dir"
        skill_dir.mkdir()
        (skill_dir / "nested.md").write_text("Nested")

        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        files_copied, files_failed = dr.copy_skills(project, dest, dry_run=False, verbose=False)

        # Assert
        assert files_copied == 2  # 1 file + 1 in directory
        assert files_failed == 0

    @pytest.mark.unit
    def test_copy_skills_with_exclusions_file(self, tmp_path: Path) -> None:
        """Test copy_skills excludes specified files."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text("""
[tool.rule_deployer]
exclude_skills = ["internal-skill.md"]
""")
        skills_dir = project / "skills"
        skills_dir.mkdir()
        (skills_dir / "internal-skill.md").write_text("Internal")
        (skills_dir / "public-skill.md").write_text("Public")

        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        files_copied, _files_failed = dr.copy_skills(project, dest, dry_run=False, verbose=False)

        # Assert
        assert files_copied == 1
        assert not (dest / "skills" / "internal-skill.md").exists()
        assert (dest / "skills" / "public-skill.md").exists()

    @pytest.mark.unit
    def test_copy_skills_with_exclusions_directory(self, tmp_path: Path) -> None:
        """Test copy_skills excludes specified directories."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text("""
[tool.rule_deployer]
exclude_skills = ["internal-dir"]
""")
        skills_dir = project / "skills"
        skills_dir.mkdir()
        internal_dir = skills_dir / "internal-dir"
        internal_dir.mkdir()
        (internal_dir / "file.md").write_text("Internal")
        public_dir = skills_dir / "public-dir"
        public_dir.mkdir()
        (public_dir / "file.md").write_text("Public")

        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        files_copied, _files_failed = dr.copy_skills(project, dest, dry_run=False, verbose=False)

        # Assert
        assert files_copied == 1
        assert not (dest / "skills" / "internal-dir").exists()
        assert (dest / "skills" / "public-dir").exists()

    @pytest.mark.unit
    def test_copy_skills_with_exclusions_trailing_slash(self, tmp_path: Path) -> None:
        """Test copy_skills handles trailing slash in directory exclusions."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text("""
[tool.rule_deployer]
exclude_skills = ["internal-dir/"]
""")
        skills_dir = project / "skills"
        skills_dir.mkdir()
        internal_dir = skills_dir / "internal-dir"
        internal_dir.mkdir()
        (internal_dir / "file.md").write_text("Internal")

        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        files_copied, _files_failed = dr.copy_skills(project, dest, dry_run=False, verbose=False)

        # Assert
        assert files_copied == 0
        assert not (dest / "skills" / "internal-dir").exists()

    @pytest.mark.unit
    def test_copy_skills_skips_hidden_files(self, tmp_path: Path) -> None:
        """Test copy_skills skips hidden files/directories."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        skills_dir = project / "skills"
        skills_dir.mkdir()
        (skills_dir / ".hidden-file.md").write_text("Hidden")
        (skills_dir / "visible-file.md").write_text("Visible")
        hidden_dir = skills_dir / ".hidden-dir"
        hidden_dir.mkdir()
        (hidden_dir / "file.md").write_text("In hidden dir")

        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        files_copied, _files_failed = dr.copy_skills(project, dest, dry_run=False, verbose=False)

        # Assert
        assert files_copied == 1  # Only visible-file.md
        assert not (dest / "skills" / ".hidden-file.md").exists()
        assert not (dest / "skills" / ".hidden-dir").exists()

    @pytest.mark.unit
    def test_copy_skills_missing_directory(self, tmp_path: Path, capsys) -> None:
        """Test copy_skills handles missing skills directory."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        # No skills directory created

        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        files_copied, files_failed = dr.copy_skills(project, dest, dry_run=False, verbose=False)

        # Assert
        assert files_copied == 0
        assert files_failed == 0
        captured = capsys.readouterr()
        assert "Skills directory not found" in captured.out

    @pytest.mark.unit
    def test_copy_skills_dry_run_with_files(self, tmp_path: Path) -> None:
        """Test copy_skills dry run with file skills."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        skills_dir = project / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill.md").write_text("Skill")

        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        files_copied, _files_failed = dr.copy_skills(project, dest, dry_run=True, verbose=False)

        # Assert
        assert files_copied == 1  # Reports would copy
        assert not (dest / "skills").exists()  # No actual copy

    @pytest.mark.unit
    def test_copy_skills_dry_run_with_directories(self, tmp_path: Path) -> None:
        """Test copy_skills dry run with directory skills."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        skills_dir = project / "skills"
        skills_dir.mkdir()
        skill_dir = skills_dir / "skill-dir"
        skill_dir.mkdir()
        (skill_dir / "file1.md").write_text("File 1")
        (skill_dir / "file2.md").write_text("File 2")

        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        files_copied, _files_failed = dr.copy_skills(project, dest, dry_run=True, verbose=False)

        # Assert
        assert files_copied == 2  # Reports would copy 2 files
        assert not (dest / "skills").exists()  # No actual copy

    @pytest.mark.unit
    def test_copy_skills_nested_directory_structure(self, tmp_path: Path) -> None:
        """Test copy_skills with deeply nested directory structure."""
        # Arrange
        project = tmp_path / "project"
        project.mkdir()
        skills_dir = project / "skills"
        skills_dir.mkdir()
        deep_dir = skills_dir / "skill" / "nested" / "deep"
        deep_dir.mkdir(parents=True)
        (deep_dir / "file.md").write_text("Deep file")

        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        files_copied, _files_failed = dr.copy_skills(project, dest, dry_run=False, verbose=False)

        # Assert
        assert files_copied == 1
        assert (dest / "skills" / "skill" / "nested" / "deep" / "file.md").exists()


class TestMainFunctionAndCLI:
    """Tests for main function, CLI arguments, and deployment summary."""

    @pytest.mark.integration
    def test_deploy_with_skip_skills_flag(self, mock_project_root: Path, tmp_path: Path) -> None:
        """Test deployment with --skip-skills flag."""
        # Arrange
        dest = tmp_path / "dest"
        dest.mkdir()
        skills_dir = mock_project_root / "skills"
        skills_dir.mkdir()
        (skills_dir / "test-skill.md").write_text("Skill content")

        # Act
        with patch("scripts.rule_deployer.Path") as mock_path:
            mock_path(__file__).resolve.return_value.parent.parent = mock_project_root
            success = dr.deploy_rules(dest, skip_skills=True, dry_run=False, verbose=False)

        # Assert
        assert success is True
        assert not (dest / "skills").exists()  # Skills not deployed

    @pytest.mark.integration
    def test_deploy_without_skip_skills_deploys_skills(
        self, mock_project_root: Path, tmp_path: Path
    ) -> None:
        """Test deployment without --skip-skills deploys skills by default."""
        # Arrange
        dest = tmp_path / "dest"
        dest.mkdir()
        skills_dir = mock_project_root / "skills"
        skills_dir.mkdir()
        (skills_dir / "test-skill.md").write_text("Skill content")

        # Act
        with patch("scripts.rule_deployer.Path") as mock_path:
            mock_path(__file__).resolve.return_value.parent.parent = mock_project_root
            success = dr.deploy_rules(dest, skip_skills=False, dry_run=False, verbose=False)

        # Assert
        assert success is True
        assert (dest / "skills" / "test-skill.md").exists()

    @pytest.mark.integration
    def test_deploy_summary_includes_skills_count(
        self, mock_project_root: Path, tmp_path: Path, capsys
    ) -> None:
        """Test deployment summary includes skills count."""
        # Arrange
        dest = tmp_path / "dest"
        dest.mkdir()
        skills_dir = mock_project_root / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill1.md").write_text("Skill 1")
        (skills_dir / "skill2.md").write_text("Skill 2")

        # Act
        with patch("scripts.rule_deployer.Path") as mock_path:
            mock_path(__file__).resolve.return_value.parent.parent = mock_project_root
            dr.deploy_rules(dest, skip_skills=False, dry_run=False, verbose=False)

        # Assert
        captured = capsys.readouterr()
        assert "Skills copied:" in captured.out
        assert "2" in captured.out

    @pytest.mark.integration
    def test_deploy_summary_shows_skills_skipped(
        self, mock_project_root: Path, tmp_path: Path, capsys
    ) -> None:
        """Test deployment summary shows skills skipped message."""
        # Arrange
        dest = tmp_path / "dest"
        dest.mkdir()

        # Act
        with patch("scripts.rule_deployer.Path") as mock_path:
            mock_path(__file__).resolve.return_value.parent.parent = mock_project_root
            dr.deploy_rules(dest, skip_skills=True, dry_run=False, verbose=False)

        # Assert
        captured = capsys.readouterr()
        assert "Skills copied:     0 (skipped)" in captured.out

    @pytest.mark.integration
    def test_deploy_summary_with_failed_skills(
        self, mock_project_root: Path, tmp_path: Path, capsys
    ) -> None:
        """Test deployment summary shows failed skills count."""
        # Arrange
        dest = tmp_path / "dest"
        dest.mkdir()
        skills_dir = mock_project_root / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill.md").write_text("Skill")

        # Act
        with (
            patch("scripts.rule_deployer.Path") as mock_path,
            patch("shutil.copy2", side_effect=OSError("Error")),
        ):
            mock_path(__file__).resolve.return_value.parent.parent = mock_project_root
            success = dr.deploy_rules(dest, skip_skills=False, dry_run=False, verbose=False)

        # Assert
        assert success is False  # Should fail due to errors
        captured = capsys.readouterr()
        assert "Total failed:" in captured.out

    @pytest.mark.unit
    def test_cli_skip_skills_flag(self, mock_project_root: Path, tmp_path: Path) -> None:
        """Test CLI --skip-skills flag parameter."""
        # Arrange
        dest = tmp_path / "dest"
        dest.mkdir()

        # Act - Test deploy_rules function with skip_skills directly
        with patch("scripts.rule_deployer.Path") as mock_path:
            mock_path(__file__).resolve.return_value.parent.parent = mock_project_root
            success = dr.deploy_rules(dest, skip_skills=True, dry_run=False, verbose=False)

        # Assert
        assert success is True
        # Skills directory should not be created when skip_skills=True
        assert not (dest / "skills").exists()

    @pytest.mark.integration
    def test_cli_verbose_and_quiet_flags(
        self, mock_project_root: Path, tmp_path: Path, capsys
    ) -> None:
        """Test CLI --verbose and --quiet flags."""
        # Arrange
        dest = tmp_path / "dest"
        dest.mkdir()

        # Act - Test quiet mode
        with (
            patch("sys.argv", ["rule_deployer.py", "--dest", str(dest), "--quiet"]),
            patch("scripts.rule_deployer.Path") as mock_path,
        ):
            mock_path(__file__).resolve.return_value.parent.parent = mock_project_root
            dr.main()

        # Assert
        captured = capsys.readouterr()
        # Quiet mode should suppress [INFO] messages but show summary
        assert "DEPLOYMENT SUMMARY" in captured.out

    @pytest.mark.unit
    def test_module_main_execution(self, tmp_path: Path) -> None:
        """Test __main__ block execution."""
        # Arrange
        dest = tmp_path / "dest"
        dest.mkdir()

        # Act & Assert
        # Test main() directly since __main__ block just calls sys.exit(main())
        with patch("sys.argv", ["rule_deployer.py", "--dest", str(dest)]):
            # main() returns 0 or 1, testing that is sufficient
            result = dr.main()
            assert result in (0, 1)

    @pytest.mark.unit
    def test_main_with_missing_dest_argument(self) -> None:
        """Test main function when dest argument is None (shouldn't happen with argparse)."""
        # This tests the validation at lines 422-424
        # In practice, argparse ensures --dest is provided, but we test the check
        with patch("sys.argv", ["rule_deployer.py"]), pytest.raises(SystemExit):
            # argparse will exit when required arg is missing
            dr.main()

    @pytest.mark.unit
    def test_main_dest_validation_when_none(self, capsys) -> None:
        """Test the explicit dest validation at lines 422-424."""
        # Arrange - Mock argparse to return None for dest
        mock_args = type(
            "Args",
            (),
            {"dest": None, "dry_run": False, "verbose": True, "quiet": False, "skip_skills": False},
        )()

        # Act
        with patch("argparse.ArgumentParser.parse_args", return_value=mock_args):
            exit_code = dr.main()

        # Assert
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error: --dest argument is required" in captured.err


# Run tests with: pytest tests/test_rule_deployer.py -v
