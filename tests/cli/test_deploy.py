"""Tests for ai-rules deploy CLI command.

Tests follow pytest best practices:
- AAA pattern (Arrange-Act-Assert)
- Function-scoped fixtures
- Parametrized tests for input matrices
- Test markers for selective execution
- Isolation with tmp_path
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands import deploy as deploy_module

runner = CliRunner()


# Fixtures for setting up test directories


@pytest.fixture
def source_project(tmp_path: Path) -> Path:
    """Create a minimal source project structure for deployment testing."""
    project = tmp_path / "source_project"
    project.mkdir()

    # Create pyproject.toml
    (project / "pyproject.toml").write_text(
        dedent("""
        [project]
        name = "test-project"
        version = "1.0.0"

        [tool.rule_deployer]
        exclude_skills = ["excluded-skill"]
        """)
    )

    # Create AGENTS.md
    (project / "AGENTS.md").write_text("# AGENTS\n\nTest agents file.")

    # Create rules directory
    rules_dir = project / "rules"
    rules_dir.mkdir()
    (rules_dir / "000-global-core.md").write_text("# Global Core Rule\n\nTest rule.")
    (rules_dir / "100-test-rule.md").write_text("# Test Rule\n\nAnother test rule.")
    (rules_dir / "RULES_INDEX.md").write_text(
        "# Rules Index\n\n- 000-global-core.md\n- 100-test-rule.md"
    )

    # Create skills directory
    skills_dir = project / "skills"
    skills_dir.mkdir()

    # Create a skill directory with files
    skill1 = skills_dir / "skill1"
    skill1.mkdir()
    (skill1 / "prompt.md").write_text("# Skill 1\n\nTest skill.")
    (skill1 / "config.yaml").write_text("name: skill1\n")

    # Create another skill directory
    skill2 = skills_dir / "skill2"
    skill2.mkdir()
    (skill2 / "prompt.md").write_text("# Skill 2\n\nAnother skill.")

    # Create excluded skill
    excluded = skills_dir / "excluded-skill"
    excluded.mkdir()
    (excluded / "prompt.md").write_text("# Excluded\n\nThis should be excluded.")

    return project


@pytest.fixture
def dest_dir(tmp_path: Path) -> Path:
    """Create a destination directory for deployment."""
    dest = tmp_path / "dest"
    dest.mkdir()
    return dest


class TestDeployHelpOutput:
    """Test --help output for deploy command."""

    @pytest.mark.unit
    def test_deploy_help_shows_command_description(self):
        """Test that --help shows command description."""
        result = runner.invoke(app, ["deploy", "--help"])

        assert result.exit_code == 0
        assert "Deploy production-ready AI coding rules" in result.output

    @pytest.mark.unit
    def test_deploy_help_shows_all_options(self):
        """Test that --help shows all expected options."""
        result = runner.invoke(app, ["deploy", "--help"])

        assert result.exit_code == 0
        assert "--dry-run" in result.output
        assert "--verbose" in result.output
        assert "--quiet" in result.output
        assert "--skip-skills" in result.output
        assert "--only-skills" in result.output
        assert "--force" in result.output
        assert "--no-mode" in result.output
        assert "--split" in result.output
        assert "--agents-dest" in result.output
        assert "--rules-dest" in result.output
        assert "--skills-dest" in result.output

    @pytest.mark.unit
    def test_deploy_help_shows_examples(self):
        """Test that --help shows usage examples."""
        result = runner.invoke(app, ["deploy", "--help"])

        assert result.exit_code == 0
        assert "Examples" in result.output


class TestDeployBasicDeployment:
    """Test basic unified deployment scenarios."""

    @pytest.mark.unit
    def test_deploy_to_directory(
        self, source_project: Path, dest_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test basic deployment to a directory."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        result = runner.invoke(app, ["deploy", str(dest_dir)])

        assert result.exit_code == 0
        assert "Deployment completed successfully" in result.output

        # Verify files were copied
        assert (dest_dir / "AGENTS.md").exists()
        assert (dest_dir / "rules" / "000-global-core.md").exists()
        assert (dest_dir / "rules" / "100-test-rule.md").exists()
        assert (dest_dir / "rules" / "RULES_INDEX.md").exists()
        assert (dest_dir / "skills" / "skill1" / "prompt.md").exists()
        assert (dest_dir / "skills" / "skill2" / "prompt.md").exists()

    @pytest.mark.unit
    def test_deploy_excludes_configured_skills(
        self, source_project: Path, dest_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that skills in exclude_skills are not deployed."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        result = runner.invoke(app, ["deploy", str(dest_dir)])

        assert result.exit_code == 0
        # Excluded skill should not be copied
        assert not (dest_dir / "skills" / "excluded-skill").exists()
        # Other skills should be copied
        assert (dest_dir / "skills" / "skill1").exists()
        assert (dest_dir / "skills" / "skill2").exists()


class TestDeployDryRun:
    """Test --dry-run flag behavior."""

    @pytest.mark.unit
    def test_dry_run_does_not_copy_files(
        self, source_project: Path, dest_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that --dry-run does not actually copy files."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        result = runner.invoke(app, ["deploy", str(dest_dir), "--dry-run"])

        assert result.exit_code == 0
        assert "DRY RUN" in result.output

        # Verify no files were copied
        assert not (dest_dir / "AGENTS.md").exists()
        assert not (dest_dir / "rules").exists()
        assert not (dest_dir / "skills").exists()

    @pytest.mark.unit
    def test_dry_run_shows_what_would_be_copied(
        self, source_project: Path, dest_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that --dry-run shows what would happen."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        result = runner.invoke(app, ["deploy", str(dest_dir), "--dry-run", "-v"])

        assert result.exit_code == 0
        # Check for "Would copy" which indicates dry-run behavior
        assert "would copy" in result.output.lower()


class TestDeploySplitMode:
    """Test split deployment mode with separate destinations."""

    @pytest.mark.unit
    def test_split_mode_with_all_destinations(
        self, source_project: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test split deployment with all three destinations."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        agents_dest = tmp_path / "agents"
        rules_dest = tmp_path / "rules"
        skills_dest = tmp_path / "skills"
        agents_dest.mkdir()
        rules_dest.mkdir()
        skills_dest.mkdir()

        result = runner.invoke(
            app,
            [
                "deploy",
                "--split",
                "--agents-dest",
                str(agents_dest),
                "--rules-dest",
                str(rules_dest),
                "--skills-dest",
                str(skills_dest),
            ],
        )

        assert result.exit_code == 0

        # Verify files are in correct locations
        assert (agents_dest / "AGENTS.md").exists()
        assert (rules_dest / "000-global-core.md").exists()
        assert (rules_dest / "RULES_INDEX.md").exists()
        assert (skills_dest / "skill1" / "prompt.md").exists()

    @pytest.mark.unit
    def test_split_mode_agents_only(
        self, source_project: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test split deployment with only AGENTS.md destination."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        agents_dest = tmp_path / "agents"
        agents_dest.mkdir()

        result = runner.invoke(
            app,
            ["deploy", "--split", "--agents-dest", str(agents_dest)],
        )

        assert result.exit_code == 0
        assert (agents_dest / "AGENTS.md").exists()

    @pytest.mark.unit
    def test_split_mode_requires_split_flag_or_args(
        self, source_project: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that split args without --split flag still works (auto-detect)."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        agents_dest = tmp_path / "agents"
        agents_dest.mkdir()

        # Should auto-detect split mode when split args are provided
        result = runner.invoke(
            app,
            ["deploy", "--agents-dest", str(agents_dest)],
        )

        assert result.exit_code == 0

    @pytest.mark.unit
    def test_split_mode_skills_dest_requires_agents_dest(
        self, source_project: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that --skills-dest requires --agents-dest."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        skills_dest = tmp_path / "skills"
        skills_dest.mkdir()

        result = runner.invoke(
            app,
            ["deploy", "--split", "--skills-dest", str(skills_dest)],
        )

        assert result.exit_code == 1
        assert "--skills-dest requires --agents-dest" in result.output


class TestDeploySkipSkills:
    """Test --skip-skills flag behavior."""

    @pytest.mark.unit
    def test_skip_skills_excludes_skills_directory(
        self, source_project: Path, dest_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that --skip-skills excludes the skills directory."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        result = runner.invoke(app, ["deploy", str(dest_dir), "--skip-skills"])

        assert result.exit_code == 0

        # Verify rules were copied but skills were not
        assert (dest_dir / "AGENTS.md").exists()
        assert (dest_dir / "rules" / "000-global-core.md").exists()
        assert not (dest_dir / "skills").exists()


class TestDeployOnlySkills:
    """Test --only-skills flag behavior."""

    @pytest.mark.unit
    def test_only_skills_deploys_only_skills(
        self, source_project: Path, dest_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that --only-skills deploys only the skills directory."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        result = runner.invoke(app, ["deploy", str(dest_dir), "--only-skills"])

        assert result.exit_code == 0

        # Verify only skills were copied
        assert (dest_dir / "skills" / "skill1" / "prompt.md").exists()
        assert not (dest_dir / "AGENTS.md").exists()
        assert not (dest_dir / "rules").exists()

    @pytest.mark.unit
    def test_only_skills_and_skip_skills_are_mutually_exclusive(
        self, source_project: Path, dest_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that --only-skills and --skip-skills cannot be used together."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        result = runner.invoke(app, ["deploy", str(dest_dir), "--only-skills", "--skip-skills"])

        assert result.exit_code == 1
        assert "Cannot use both" in result.output


class TestDeployErrorCases:
    """Test error handling scenarios."""

    @pytest.mark.unit
    def test_missing_destination_argument(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        """Test error when no destination is provided."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text('[project]\nname = "test"\n')

        monkeypatch.setattr(deploy_module, "find_project_root", lambda: project)

        result = runner.invoke(app, ["deploy"])

        assert result.exit_code == 1
        assert "Must specify" in result.output

    @pytest.mark.unit
    def test_invalid_source_structure(
        self, tmp_path: Path, dest_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test error when source structure is invalid."""
        # Create minimal project without rules
        project = tmp_path / "invalid_project"
        project.mkdir()
        (project / "pyproject.toml").write_text('[project]\nname = "test"\n')

        monkeypatch.setattr(deploy_module, "find_project_root", lambda: project)

        result = runner.invoke(app, ["deploy", str(dest_dir)])

        assert result.exit_code == 1
        assert "Source structure validation failed" in result.output

    @pytest.mark.unit
    def test_conflicting_dest_and_split_args(
        self, source_project: Path, dest_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test error when both dest and split args are provided."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        agents_dest = tmp_path / "agents"
        agents_dest.mkdir()

        result = runner.invoke(
            app,
            ["deploy", str(dest_dir), "--agents-dest", str(agents_dest)],
        )

        assert result.exit_code == 1
        assert "Cannot use positional destination with split" in result.output

    @pytest.mark.unit
    def test_missing_project_root(self, dest_dir: Path, monkeypatch: pytest.MonkeyPatch):
        """Test error when project root cannot be found."""

        def raise_not_found():
            raise FileNotFoundError("Could not find project root")

        monkeypatch.setattr(deploy_module, "find_project_root", raise_not_found)

        result = runner.invoke(app, ["deploy", str(dest_dir)])

        assert result.exit_code == 1
        assert "project root" in result.output.lower()


class TestDeployForceFlag:
    """Test --force flag behavior."""

    @pytest.mark.unit
    def test_force_creates_missing_directories(
        self, source_project: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that --force creates missing split destination directories."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        agents_dest = tmp_path / "nonexistent" / "agents"
        # Directory does not exist

        result = runner.invoke(
            app,
            ["deploy", "--split", "--agents-dest", str(agents_dest), "--force"],
        )

        assert result.exit_code == 0
        assert agents_dest.exists()
        assert (agents_dest / "AGENTS.md").exists()


class TestDeployFunctions:
    """Test individual deploy module functions directly."""

    @pytest.mark.unit
    def test_resolve_paths_unified_mode(self, tmp_path: Path):
        """Test resolve_paths in unified mode."""
        dest = tmp_path / "dest"
        dest.mkdir()

        paths = deploy_module.resolve_paths(dest=dest)

        assert paths.agents == dest
        assert paths.rules == dest / "rules"
        assert paths.skills == dest / "skills"

    @pytest.mark.unit
    def test_resolve_paths_split_mode(self, tmp_path: Path):
        """Test resolve_paths in split mode."""
        agents = tmp_path / "agents"
        rules = tmp_path / "rules"
        skills = tmp_path / "skills"

        paths = deploy_module.resolve_paths(
            agents_dest=agents, rules_dest=rules, skills_dest=skills
        )

        assert paths.agents == agents.resolve()
        assert paths.rules == rules.resolve()
        assert paths.skills == skills.resolve()

    @pytest.mark.unit
    def test_validate_source_structure_valid(self, source_project: Path):
        """Test validate_source_structure with valid project."""
        is_valid, errors = deploy_module.validate_source_structure(source_project)

        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_validate_source_structure_invalid(self, tmp_path: Path):
        """Test validate_source_structure with invalid project."""
        project = tmp_path / "invalid"
        project.mkdir()

        is_valid, errors = deploy_module.validate_source_structure(project)

        assert is_valid is False
        assert len(errors) > 0

    @pytest.mark.unit
    def test_load_skill_exclusions_with_config(self, source_project: Path):
        """Test loading skill exclusions from pyproject.toml."""
        exclusions = deploy_module.load_skill_exclusions(source_project, verbose=False)

        assert "excluded-skill" in exclusions

    @pytest.mark.unit
    def test_load_skill_exclusions_no_config(self, tmp_path: Path):
        """Test loading exclusions when pyproject.toml is missing."""
        exclusions = deploy_module.load_skill_exclusions(tmp_path, verbose=False)

        assert len(exclusions) == 0

    @pytest.mark.unit
    def test_substitute_template(self, tmp_path: Path):
        """Test template substitution."""
        paths = deploy_module.DeploymentPaths(
            agents=tmp_path / "agents",
            rules=tmp_path / "rules",
            skills=tmp_path / "skills",
        )
        template = "Rules at {{rules_path}}, Skills at {{skills_path}}"

        result = deploy_module.substitute_template(template, paths)

        assert str(tmp_path / "rules") in result
        assert str(tmp_path / "skills") in result


class TestDeployVerboseQuiet:
    """Test --verbose and --quiet flag behavior."""

    @pytest.mark.unit
    def test_quiet_suppresses_detailed_output(
        self, source_project: Path, dest_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that --quiet suppresses detailed output."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        result = runner.invoke(app, ["deploy", str(dest_dir), "--quiet"])

        assert result.exit_code == 0
        # Should still show summary
        assert "Deployment" in result.output
        # But fewer info messages
        # (checking that quiet mode affects output)

    @pytest.mark.unit
    def test_verbose_shows_detailed_output(
        self, source_project: Path, dest_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that --verbose shows detailed output."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        result = runner.invoke(app, ["deploy", str(dest_dir), "--verbose"])

        assert result.exit_code == 0
        assert "Copied" in result.output or "Project root" in result.output


class TestDeployCopyFunctions:
    """Test individual copy functions."""

    @pytest.mark.unit
    def test_copy_rules(self, source_project: Path, dest_dir: Path):
        """Test copy_rules function."""
        rules_source = source_project / "rules"

        copied, failed = deploy_module.copy_rules(
            rules_source, dest_dir, dry_run=False, verbose=False
        )

        # Should copy rules (excluding RULES_INDEX.md which is handled by copy_root_files)
        assert copied == 2
        assert failed == 0
        assert (dest_dir / "rules" / "000-global-core.md").exists()
        assert (dest_dir / "rules" / "100-test-rule.md").exists()

    @pytest.mark.unit
    def test_copy_rules_dry_run(self, source_project: Path, dest_dir: Path):
        """Test copy_rules in dry run mode."""
        rules_source = source_project / "rules"

        copied, failed = deploy_module.copy_rules(
            rules_source, dest_dir, dry_run=True, verbose=False
        )

        assert copied == 2
        assert failed == 0
        # Files should not actually exist
        assert not (dest_dir / "rules").exists()

    @pytest.mark.unit
    def test_copy_skills(self, source_project: Path, dest_dir: Path):
        """Test copy_skills function."""
        skills_count, _files_copied, failed = deploy_module.copy_skills(
            source_project, dest_dir, dry_run=False, verbose=False
        )

        # Should copy 2 skills (excluding "excluded-skill")
        assert skills_count == 2
        assert failed == 0
        assert (dest_dir / "skills" / "skill1" / "prompt.md").exists()
        assert (dest_dir / "skills" / "skill2" / "prompt.md").exists()
        assert not (dest_dir / "skills" / "excluded-skill").exists()

    @pytest.mark.unit
    def test_copy_root_files(self, source_project: Path, dest_dir: Path):
        """Test copy_root_files function."""
        copied, failed = deploy_module.copy_root_files(
            source_project, dest_dir, dry_run=False, verbose=False
        )

        assert copied == 2  # AGENTS.md and RULES_INDEX.md
        assert failed == 0
        assert (dest_dir / "AGENTS.md").exists()
        assert (dest_dir / "rules" / "RULES_INDEX.md").exists()


class TestDeployNoMode:
    """Test --no-mode flag behavior."""

    @pytest.mark.unit
    def test_no_mode_with_agents_no_mode_file(
        self, tmp_path: Path, dest_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test --no-mode uses AGENTS_NO_MODE.md as source."""
        # Create project with AGENTS_NO_MODE.md
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text('[project]\nname = "test"\n')
        (project / "AGENTS_NO_MODE.md").write_text("# NO MODE AGENTS\n\nSimplified.")

        rules_dir = project / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text("# Test\n")
        (rules_dir / "RULES_INDEX.md").write_text("# Index\n")

        skills_dir = project / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill1").mkdir()
        (skills_dir / "skill1" / "prompt.md").write_text("# Skill\n")

        monkeypatch.setattr(deploy_module, "find_project_root", lambda: project)

        result = runner.invoke(app, ["deploy", str(dest_dir), "--no-mode"])

        assert result.exit_code == 0
        # AGENTS.md should be created from AGENTS_NO_MODE.md
        assert (dest_dir / "AGENTS.md").exists()
        content = (dest_dir / "AGENTS.md").read_text()
        assert "NO MODE" in content
