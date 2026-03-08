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

runner = CliRunner(env={"NO_COLOR": "1"})


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
        """Test help text shown when no destination is provided."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text('[project]\nname = "test"\n')

        monkeypatch.setattr(deploy_module, "find_project_root", lambda: project)

        result = runner.invoke(app, ["deploy"])

        assert result.exit_code == 0
        assert "Usage" in result.output or "deploy" in result.output

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


# ============================================================================
# substitute_template edge cases (lines 86, 91)
# ============================================================================


class TestSubstituteTemplateEdgeCases:
    """Test substitute_template when paths.rules or paths.skills is None."""

    @pytest.mark.unit
    def test_substitute_template_no_rules_path(self, tmp_path: Path):
        """Test substitute_template falls back to CWD/rules when rules is None."""
        paths = deploy_module.DeploymentPaths(
            agents=tmp_path / "agents",
            rules=None,
            skills=tmp_path / "skills",
        )
        template = "Rules at {{rules_path}}, Skills at {{skills_path}}"

        result = deploy_module.substitute_template(template, paths)

        assert "rules" in result
        assert str(tmp_path / "skills") in result

    @pytest.mark.unit
    def test_substitute_template_no_skills_path(self, tmp_path: Path):
        """Test substitute_template falls back to CWD/skills when skills is None."""
        paths = deploy_module.DeploymentPaths(
            agents=tmp_path / "agents",
            rules=tmp_path / "rules",
            skills=None,
        )
        template = "Rules at {{rules_path}}, Skills at {{skills_path}}"

        result = deploy_module.substitute_template(template, paths)

        assert str(tmp_path / "rules") in result
        assert "skills" in result

    @pytest.mark.unit
    def test_substitute_template_both_none(self, tmp_path: Path):
        """Test substitute_template when both rules and skills are None."""
        paths = deploy_module.DeploymentPaths(
            agents=tmp_path / "agents",
            rules=None,
            skills=None,
        )
        template = "Rules at {{rules_path}}, Skills at {{skills_path}}"

        result = deploy_module.substitute_template(template, paths)

        # Should contain CWD-based paths
        assert "rules" in result
        assert "skills" in result


# ============================================================================
# load_template (line 108)
# ============================================================================


class TestLoadTemplate:
    """Test load_template function."""

    @pytest.mark.unit
    def test_load_template_exists(self, tmp_path: Path):
        """Test load_template when template file exists."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "AGENTS_MODE.md.template").write_text(
            "<!-- Template: mode -->\n\n# AGENTS\nContent with {{rules_path}}"
        )

        result = deploy_module.load_template(tmp_path, no_mode=False)

        assert result is not None
        assert "{{rules_path}}" in result

    @pytest.mark.unit
    def test_load_template_no_mode(self, tmp_path: Path):
        """Test load_template with no_mode=True."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "AGENTS_NO_MODE.md.template").write_text(
            "<!-- Template: no-mode -->\n\n# NO MODE\nSimplified."
        )

        result = deploy_module.load_template(tmp_path, no_mode=True)

        assert result is not None
        assert "NO MODE" in result

    @pytest.mark.unit
    def test_load_template_not_found(self, tmp_path: Path):
        """Test load_template returns None when template missing."""
        result = deploy_module.load_template(tmp_path, no_mode=False)

        assert result is None


# ============================================================================
# _prompt_create_directory (lines 122-133)
# ============================================================================


class TestPromptCreateDirectory:
    """Test _prompt_create_directory function."""

    @pytest.mark.unit
    def test_prompt_create_directory_user_accepts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test user accepting directory creation."""
        target = tmp_path / "new_dir"
        monkeypatch.setattr(deploy_module.console, "input", lambda _: "y")

        result = deploy_module._prompt_create_directory(target, "--agents-dest")

        assert result is True
        assert target.exists()

    @pytest.mark.unit
    def test_prompt_create_directory_user_declines(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test user declining directory creation."""
        target = tmp_path / "new_dir"
        monkeypatch.setattr(deploy_module.console, "input", lambda _: "n")

        result = deploy_module._prompt_create_directory(target, "--agents-dest")

        assert result is False
        assert not target.exists()

    @pytest.mark.unit
    def test_prompt_create_directory_eof_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test non-interactive environment (EOFError)."""
        target = tmp_path / "new_dir"

        def raise_eof(_):
            raise EOFError

        monkeypatch.setattr(deploy_module.console, "input", raise_eof)

        result = deploy_module._prompt_create_directory(target, "--agents-dest")

        assert result is False

    @pytest.mark.unit
    def test_prompt_create_directory_empty_response(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test empty response (defaults to yes)."""
        target = tmp_path / "new_dir"
        monkeypatch.setattr(deploy_module.console, "input", lambda _: "")

        result = deploy_module._prompt_create_directory(target, "--agents-dest")

        assert result is True
        assert target.exists()


# ============================================================================
# validate_split_destinations prompt path (lines 174-175)
# ============================================================================


class TestValidateSplitDestinationsPrompt:
    """Test validate_split_destinations with directory prompting."""

    @pytest.mark.unit
    def test_validate_split_prompt_decline(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test validation fails when user declines dir creation."""
        nonexistent = tmp_path / "missing"
        monkeypatch.setattr(deploy_module.console, "input", lambda _: "n")

        is_valid, errors = deploy_module.validate_split_destinations(
            agents_dest=nonexistent, rules_dest=None, skills_dest=None, force=False
        )

        assert is_valid is False
        assert any("does not exist" in e for e in errors)


# ============================================================================
# validate_source_structure only_skills branches (lines 205, 207, 213, 221, 226)
# ============================================================================


class TestValidateSourceStructureOnlySkills:
    """Test validate_source_structure with only_skills=True."""

    @pytest.mark.unit
    def test_only_skills_no_skills_dir(self, tmp_path: Path):
        """Test only_skills when skills directory does not exist."""
        is_valid, errors = deploy_module.validate_source_structure(tmp_path, only_skills=True)

        assert is_valid is False
        assert any("not found" in e for e in errors)

    @pytest.mark.unit
    def test_only_skills_not_a_directory(self, tmp_path: Path):
        """Test only_skills when skills path is a file, not directory."""
        (tmp_path / "skills").write_text("not a directory")

        is_valid, errors = deploy_module.validate_source_structure(tmp_path, only_skills=True)

        assert is_valid is False
        assert any("not a directory" in e for e in errors)

    @pytest.mark.unit
    def test_only_skills_empty_directory(self, tmp_path: Path):
        """Test only_skills with empty skills directory."""
        (tmp_path / "skills").mkdir()

        is_valid, errors = deploy_module.validate_source_structure(tmp_path, only_skills=True)

        assert is_valid is False
        assert any("No skill directories" in e for e in errors)

    @pytest.mark.unit
    def test_only_skills_valid(self, tmp_path: Path):
        """Test only_skills with valid skills directory."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "my-skill").mkdir()
        (skills_dir / "my-skill" / "prompt.md").write_text("# Skill\n")

        is_valid, errors = deploy_module.validate_source_structure(tmp_path, only_skills=True)

        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_no_mode_template_fallback(self, tmp_path: Path):
        """Test no_mode falls back to template when AGENTS_NO_MODE.md missing."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "100-test.md").write_text("# Test\n")
        (rules_dir / "RULES_INDEX.md").write_text("# Index\n")

        is_valid, errors = deploy_module.validate_source_structure(tmp_path, no_mode=True)

        # Should fail because neither AGENTS_NO_MODE.md nor template exists
        assert is_valid is False
        assert any("AGENTS_NO_MODE.md" in e for e in errors)

    @pytest.mark.unit
    def test_rules_dir_not_a_directory(self, tmp_path: Path):
        """Test when rules path exists but is a file."""
        (tmp_path / "rules").write_text("not a directory")
        (tmp_path / "AGENTS.md").write_text("# Agents\n")

        is_valid, errors = deploy_module.validate_source_structure(tmp_path)

        assert is_valid is False
        assert any("not a directory" in e for e in errors)

    @pytest.mark.unit
    def test_rules_dir_empty(self, tmp_path: Path):
        """Test when rules directory has no .md files."""
        (tmp_path / "rules").mkdir()
        (tmp_path / "AGENTS.md").write_text("# Agents\n")

        is_valid, errors = deploy_module.validate_source_structure(tmp_path)

        assert is_valid is False
        assert any("No .md files" in e for e in errors)


# ============================================================================
# copy_rules edge cases (lines 272-273, 300-302)
# ============================================================================


class TestCopyRulesEdgeCases:
    """Test copy_rules edge cases."""

    @pytest.mark.unit
    def test_copy_rules_no_md_files(self, tmp_path: Path):
        """Test copy_rules when no .md files exist."""
        source = tmp_path / "rules"
        source.mkdir()
        (source / "readme.txt").write_text("not markdown")
        dest = tmp_path / "dest"
        dest.mkdir()

        copied, failed = deploy_module.copy_rules(source, dest, dry_run=False, verbose=False)

        assert copied == 0
        assert failed == 0

    @pytest.mark.unit
    def test_copy_rules_exception_during_copy(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test copy_rules handles exception during file copy."""
        source = tmp_path / "rules"
        source.mkdir()
        (source / "100-test.md").write_text("# Test\n")
        dest = tmp_path / "dest"
        dest.mkdir()

        # Make shutil.copy2 raise an exception
        import shutil

        def failing_copy2(src, dst, **kwargs):
            raise PermissionError("Permission denied")

        monkeypatch.setattr(shutil, "copy2", failing_copy2)

        _copied, failed = deploy_module.copy_rules(source, dest, dry_run=False, verbose=False)

        assert failed == 1

    @pytest.mark.unit
    def test_copy_rules_direct_copy_mode(self, tmp_path: Path):
        """Test copy_rules with direct_copy=True (split mode)."""
        source = tmp_path / "rules"
        source.mkdir()
        (source / "100-test.md").write_text("# Test Rule\n")
        dest = tmp_path / "dest"
        dest.mkdir()

        copied, failed = deploy_module.copy_rules(
            source, dest, dry_run=False, verbose=True, direct_copy=True
        )

        assert copied == 1
        assert failed == 0
        # In direct_copy mode, files go directly to dest, not dest/rules
        assert (dest / "100-test.md").exists()


# ============================================================================
# copy_root_files template paths (lines 345-358, 367-375, 383-385, 414-415, 428-430)
# ============================================================================


class TestCopyRootFilesTemplates:
    """Test copy_root_files template substitution and fallback paths."""

    @pytest.mark.unit
    def test_split_mode_with_template(self, tmp_path: Path):
        """Test copy_root_files in split mode with template substitution."""
        project = tmp_path / "project"
        project.mkdir()
        templates_dir = project / "templates"
        templates_dir.mkdir()
        (templates_dir / "AGENTS_MODE.md.template").write_text(
            "<!-- Template: mode -->\n\n# AGENTS\nRules: {{rules_path}}\nSkills: {{skills_path}}"
        )
        rules_dir = project / "rules"
        rules_dir.mkdir()
        (rules_dir / "RULES_INDEX.md").write_text("# Index\n- rules/100-test.md\n")

        dest = tmp_path / "dest"
        dest.mkdir()
        paths = deploy_module.DeploymentPaths(
            agents=dest,
            rules=tmp_path / "rules_out",
            skills=tmp_path / "skills_out",
        )

        copied, failed = deploy_module.copy_root_files(
            project, dest, dry_run=False, verbose=True, paths=paths
        )

        assert copied == 2
        assert failed == 0
        content = (dest / "AGENTS.md").read_text()
        assert str(tmp_path / "rules_out") in content

    @pytest.mark.unit
    def test_split_mode_template_dry_run(self, tmp_path: Path):
        """Test copy_root_files split mode template in dry_run."""
        project = tmp_path / "project"
        project.mkdir()
        templates_dir = project / "templates"
        templates_dir.mkdir()
        (templates_dir / "AGENTS_MODE.md.template").write_text(
            "<!-- Template: mode -->\n\n# AGENTS\nRules: {{rules_path}}"
        )
        rules_dir = project / "rules"
        rules_dir.mkdir()
        (rules_dir / "RULES_INDEX.md").write_text("# Index\n")

        dest = tmp_path / "dest"
        dest.mkdir()
        paths = deploy_module.DeploymentPaths(
            agents=dest,
            rules=tmp_path / "rules_out",
            skills=None,
        )

        copied, failed = deploy_module.copy_root_files(
            project, dest, dry_run=True, verbose=True, paths=paths
        )

        assert copied == 2
        assert failed == 0
        # File should NOT be written in dry_run
        assert not (dest / "AGENTS.md").exists()

    @pytest.mark.unit
    def test_unified_mode_template_fallback(self, tmp_path: Path):
        """Test copy_root_files unified mode template fallback when AGENTS.md missing."""
        project = tmp_path / "project"
        project.mkdir()
        templates_dir = project / "templates"
        templates_dir.mkdir()
        (templates_dir / "AGENTS_MODE.md.template").write_text(
            "<!-- Template: mode -->\n\n# AGENTS\nGenerated from template."
        )
        rules_dir = project / "rules"
        rules_dir.mkdir()
        (rules_dir / "RULES_INDEX.md").write_text("# Index\n")
        # No AGENTS.md file — will fallback to template

        dest = tmp_path / "dest"
        dest.mkdir()

        copied, failed = deploy_module.copy_root_files(project, dest, dry_run=False, verbose=True)

        assert copied == 2
        assert failed == 0
        content = (dest / "AGENTS.md").read_text()
        assert "Generated from template" in content

    @pytest.mark.unit
    def test_unified_mode_template_fallback_dry_run(self, tmp_path: Path):
        """Test template fallback in dry_run mode."""
        project = tmp_path / "project"
        project.mkdir()
        templates_dir = project / "templates"
        templates_dir.mkdir()
        (templates_dir / "AGENTS_MODE.md.template").write_text(
            "<!-- Template: mode -->\n\n# AGENTS\nTemplate content."
        )
        rules_dir = project / "rules"
        rules_dir.mkdir()
        (rules_dir / "RULES_INDEX.md").write_text("# Index\n")

        dest = tmp_path / "dest"
        dest.mkdir()

        copied, _failed = deploy_module.copy_root_files(project, dest, dry_run=True, verbose=True)

        assert copied == 2
        assert not (dest / "AGENTS.md").exists()

    @pytest.mark.unit
    def test_direct_copy_dry_run_verbose(self, tmp_path: Path):
        """Test copy_root_files direct copy in dry_run verbose mode."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("# Agents\n")
        rules_dir = project / "rules"
        rules_dir.mkdir()
        (rules_dir / "RULES_INDEX.md").write_text("# Index\n")

        dest = tmp_path / "dest"
        dest.mkdir()

        copied, failed = deploy_module.copy_root_files(project, dest, dry_run=True, verbose=True)

        assert copied == 2
        assert failed == 0

    @pytest.mark.unit
    def test_split_mode_rules_index_verbose(self, tmp_path: Path):
        """Test split mode RULES_INDEX.md with path substitution and verbose."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("# Agents\n")
        rules_dir = project / "rules"
        rules_dir.mkdir()
        (rules_dir / "RULES_INDEX.md").write_text(
            "# Index\n- rules/100-test.md\n- skills/my-skill\n"
        )

        dest = tmp_path / "dest"
        dest.mkdir()
        rules_out = tmp_path / "rules_out"
        rules_out.mkdir()
        skills_out = tmp_path / "skills_out"

        paths = deploy_module.DeploymentPaths(
            agents=dest,
            rules=rules_out,
            skills=skills_out,
        )

        copied, failed = deploy_module.copy_root_files(
            project, dest, dry_run=False, verbose=True, paths=paths
        )

        assert copied == 2
        assert failed == 0
        content = (rules_out / "RULES_INDEX.md").read_text()
        assert str(rules_out) in content

    @pytest.mark.unit
    def test_copy_root_files_rules_index_exception(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test copy_root_files when RULES_INDEX.md copy fails."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("# Agents\n")
        rules_dir = project / "rules"
        rules_dir.mkdir()
        # No RULES_INDEX.md — reading it will fail

        dest = tmp_path / "dest"
        dest.mkdir()

        copied, failed = deploy_module.copy_root_files(project, dest, dry_run=False, verbose=False)

        # AGENTS.md copies ok, RULES_INDEX.md fails
        assert copied == 1
        assert failed == 1

    @pytest.mark.unit
    def test_split_mode_agents_only_skips_rules_index(self, tmp_path: Path):
        """Test split mode with rules=None skips RULES_INDEX.md."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("# Agents\n")
        rules_dir = project / "rules"
        rules_dir.mkdir()
        (rules_dir / "RULES_INDEX.md").write_text("# Index\n")

        dest = tmp_path / "dest"
        dest.mkdir()
        paths = deploy_module.DeploymentPaths(agents=dest, rules=None, skills=None)

        copied, failed = deploy_module.copy_root_files(
            project, dest, dry_run=False, verbose=False, paths=paths
        )

        # Only AGENTS.md copied, rules_index skipped
        assert copied == 1
        assert failed == 0


# ============================================================================
# load_skill_exclusions exception (lines 468-471)
# ============================================================================


class TestLoadSkillExclusionsEdgeCases:
    """Test load_skill_exclusions error paths."""

    @pytest.mark.unit
    def test_load_skill_exclusions_invalid_toml(self, tmp_path: Path):
        """Test load_skill_exclusions with invalid TOML file."""
        (tmp_path / "pyproject.toml").write_text("this is [[[invalid toml")

        result = deploy_module.load_skill_exclusions(tmp_path, verbose=False)

        assert result == set()

    @pytest.mark.unit
    def test_load_skill_exclusions_empty_list(self, tmp_path: Path):
        """Test load_skill_exclusions with empty exclude_skills list."""
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "test"\n\n[tool.rule_deployer]\nexclude_skills = []\n'
        )

        result = deploy_module.load_skill_exclusions(tmp_path, verbose=False)

        assert result == set()


# ============================================================================
# copy_skills edge cases (lines 505-506, 529, 542-549, 574-576)
# ============================================================================


class TestCopySkillsEdgeCases:
    """Test copy_skills edge cases."""

    @pytest.mark.unit
    def test_copy_skills_no_skills_dir(self, tmp_path: Path):
        """Test copy_skills when skills directory does not exist."""
        dest = tmp_path / "dest"
        dest.mkdir()

        skills_count, files_copied, failed = deploy_module.copy_skills(
            tmp_path, dest, dry_run=False, verbose=False
        )

        assert skills_count == 0
        assert files_copied == 0
        assert failed == 0

    @pytest.mark.unit
    def test_copy_skills_trailing_slash_exclusion(self, tmp_path: Path):
        """Test copy_skills excludes with trailing slash in exclusions."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text(
            '[project]\nname = "test"\n\n[tool.rule_deployer]\nexclude_skills = ["excluded/"]\n'
        )
        skills_dir = project / "skills"
        skills_dir.mkdir()
        excluded = skills_dir / "excluded"
        excluded.mkdir()
        (excluded / "prompt.md").write_text("# Excluded\n")
        included = skills_dir / "included"
        included.mkdir()
        (included / "prompt.md").write_text("# Included\n")

        dest = tmp_path / "dest"
        dest.mkdir()

        _skills_count, _files_copied, _failed = deploy_module.copy_skills(
            project, dest, dry_run=False, verbose=True
        )

        assert (dest / "skills" / "included" / "prompt.md").exists()
        assert not (dest / "skills" / "excluded").exists()

    @pytest.mark.unit
    def test_copy_skills_individual_file(self, tmp_path: Path):
        """Test copy_skills with an individual file in skills directory."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text('[project]\nname = "test"\n')
        skills_dir = project / "skills"
        skills_dir.mkdir()
        # Individual file (not a subdirectory)
        (skills_dir / "standalone.md").write_text("# Standalone Skill\n")

        dest = tmp_path / "dest"
        dest.mkdir()

        skills_count, files_copied, _failed = deploy_module.copy_skills(
            project, dest, dry_run=False, verbose=True
        )

        assert skills_count == 1
        assert files_copied == 1
        assert (dest / "skills" / "standalone.md").exists()

    @pytest.mark.unit
    def test_copy_skills_individual_file_dry_run(self, tmp_path: Path):
        """Test copy_skills file in dry_run verbose mode."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text('[project]\nname = "test"\n')
        skills_dir = project / "skills"
        skills_dir.mkdir()
        (skills_dir / "standalone.md").write_text("# Standalone\n")

        dest = tmp_path / "dest"
        dest.mkdir()

        skills_count, _files_copied, _failed = deploy_module.copy_skills(
            project, dest, dry_run=True, verbose=True
        )

        assert skills_count == 1
        assert not (dest / "skills" / "standalone.md").exists()

    @pytest.mark.unit
    def test_copy_skills_exception_during_copy(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test copy_skills handles exception during copytree."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text('[project]\nname = "test"\n')
        skills_dir = project / "skills"
        skills_dir.mkdir()
        skill = skills_dir / "broken-skill"
        skill.mkdir()
        (skill / "prompt.md").write_text("# Broken\n")

        dest = tmp_path / "dest"
        dest.mkdir()

        import shutil

        def failing_copytree(src, dst, **kwargs):
            raise PermissionError("Permission denied")

        monkeypatch.setattr(shutil, "copytree", failing_copytree)

        _skills_count, _files_copied, failed = deploy_module.copy_skills(
            project, dest, dry_run=False, verbose=False
        )

        assert failed == 1

    @pytest.mark.unit
    def test_copy_skills_hidden_dir_skipped(self, tmp_path: Path):
        """Test copy_skills skips hidden directories."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text('[project]\nname = "test"\n')
        skills_dir = project / "skills"
        skills_dir.mkdir()
        (skills_dir / ".hidden").mkdir()
        (skills_dir / ".hidden" / "prompt.md").write_text("# Hidden\n")
        visible = skills_dir / "visible"
        visible.mkdir()
        (visible / "prompt.md").write_text("# Visible\n")

        dest = tmp_path / "dest"
        dest.mkdir()

        _skills_count, _files_copied, _failed = deploy_module.copy_skills(
            project, dest, dry_run=False, verbose=False
        )

        assert not (dest / "skills" / ".hidden").exists()
        assert (dest / "skills" / "visible" / "prompt.md").exists()


# ============================================================================
# deploy_rules edge cases (lines 739-740, 777-800, 856-857)
# ============================================================================


class TestDeployRulesEdgeCases:
    """Test deploy_rules function edge cases."""

    @pytest.mark.unit
    def test_only_skills_no_destination(self, tmp_path: Path):
        """Test only_skills with no destination specified."""
        project = tmp_path / "project"
        project.mkdir()
        skills_dir = project / "skills"
        skills_dir.mkdir()
        (skills_dir / "my-skill").mkdir()
        (skills_dir / "my-skill" / "prompt.md").write_text("# Skill\n")

        result = deploy_module.deploy_rules(
            project_root=project,
            dest=None,
            only_skills=True,
            verbose=False,
        )

        assert result is False

    @pytest.mark.unit
    def test_deploy_with_examples_directory(self, source_project: Path, dest_dir: Path):
        """Test deploy copies examples/ subdirectory."""
        # Create examples directory
        examples_dir = source_project / "rules" / "examples"
        examples_dir.mkdir()
        (examples_dir / "example-1.md").write_text("# Example 1\n")
        (examples_dir / "example-2.md").write_text("# Example 2\n")

        result = deploy_module.deploy_rules(
            project_root=source_project,
            dest=dest_dir,
            verbose=True,
        )

        assert result is True
        assert (dest_dir / "rules" / "examples" / "example-1.md").exists()
        assert (dest_dir / "rules" / "examples" / "example-2.md").exists()

    @pytest.mark.unit
    def test_deploy_with_examples_dry_run(self, source_project: Path, dest_dir: Path):
        """Test deploy examples in dry_run mode."""
        examples_dir = source_project / "rules" / "examples"
        examples_dir.mkdir()
        (examples_dir / "example-1.md").write_text("# Example 1\n")

        result = deploy_module.deploy_rules(
            project_root=source_project,
            dest=dest_dir,
            dry_run=True,
            verbose=True,
        )

        assert result is True
        assert not (dest_dir / "rules" / "examples").exists()

    @pytest.mark.unit
    def test_deploy_with_examples_overwrite(self, source_project: Path, dest_dir: Path):
        """Test deploy overwrites existing examples directory."""
        # Pre-existing examples
        existing = dest_dir / "rules" / "examples"
        existing.mkdir(parents=True)
        (existing / "old.md").write_text("# Old\n")

        # Source examples
        examples_dir = source_project / "rules" / "examples"
        examples_dir.mkdir()
        (examples_dir / "new.md").write_text("# New\n")

        result = deploy_module.deploy_rules(
            project_root=source_project,
            dest=dest_dir,
            verbose=False,
        )

        assert result is True
        assert (dest_dir / "rules" / "examples" / "new.md").exists()
        # Old file should be gone (rmtree + copytree)
        assert not (dest_dir / "rules" / "examples" / "old.md").exists()

    @pytest.mark.unit
    def test_deploy_with_failures(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test deploy_rules returns False when there are copy failures."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text('[project]\nname = "test"\n')
        (project / "AGENTS.md").write_text("# Agents\n")
        rules_dir = project / "rules"
        rules_dir.mkdir()
        (rules_dir / "100-test.md").write_text("# Test\n")
        (rules_dir / "RULES_INDEX.md").write_text("# Index\n")
        skills_dir = project / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill1").mkdir()
        (skills_dir / "skill1" / "prompt.md").write_text("# Skill\n")

        dest = tmp_path / "dest"
        dest.mkdir()

        # Patch copy_rules to return failures
        monkeypatch.setattr(deploy_module, "copy_rules", lambda *args, **kwargs: (0, 5))

        result = deploy_module.deploy_rules(
            project_root=project,
            dest=dest,
            verbose=False,
        )

        assert result is False


# ============================================================================
# deploy CLI --split without args (lines 1014-1015)
# ============================================================================


class TestDeployCLISplitEdge:
    """Test deploy CLI --split flag edge cases."""

    @pytest.mark.unit
    def test_split_flag_without_split_args(
        self, source_project: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test --split flag without any split destination args."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        result = runner.invoke(app, ["deploy", "--split"])

        assert result.exit_code == 1
        assert "--split requires at least one" in result.output

    @pytest.mark.unit
    def test_split_mode_rules_only(
        self, source_project: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test split deployment with only rules destination."""
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)

        rules_dest = tmp_path / "rules_out"
        rules_dest.mkdir()

        result = runner.invoke(
            app,
            ["deploy", "--split", "--rules-dest", str(rules_dest)],
        )

        assert result.exit_code == 0

    @pytest.mark.unit
    def test_no_mode_verbose_info(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test --no-mode with --verbose shows info message."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text('[project]\nname = "test"\n')
        (project / "AGENTS_NO_MODE.md").write_text("# NO MODE\nSimplified.")
        rules_dir = project / "rules"
        rules_dir.mkdir()
        (rules_dir / "100-test.md").write_text("# Test\n")
        (rules_dir / "RULES_INDEX.md").write_text("# Index\n")
        skills_dir = project / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill1").mkdir()
        (skills_dir / "skill1" / "prompt.md").write_text("# Skill\n")

        dest = tmp_path / "dest"
        dest.mkdir()

        monkeypatch.setattr(deploy_module, "find_project_root", lambda: project)

        result = runner.invoke(app, ["deploy", str(dest), "--no-mode", "--verbose"])

        assert result.exit_code == 0
        assert "NO-MODE" in result.output


# ============================================================================
# build_deployment_tree (ensure all branches covered)
# ============================================================================


class TestBuildDeploymentTree:
    """Test build_deployment_tree function."""

    @pytest.mark.unit
    def test_only_skills_tree(self, tmp_path: Path):
        """Test tree for only_skills deployment."""
        paths = deploy_module.DeploymentPaths(agents=None, rules=None, skills=tmp_path / "skills")

        tree = deploy_module.build_deployment_tree(
            paths=paths,
            dest=None,
            is_split_mode=True,
            skip_skills=False,
            only_skills=True,
            rules_copied=0,
            root_copied=0,
            skills_count=3,
            skills_files_copied=10,
        )

        assert tree is not None

    @pytest.mark.unit
    def test_split_mode_tree_partial(self, tmp_path: Path):
        """Test tree for split mode with only agents."""
        paths = deploy_module.DeploymentPaths(agents=tmp_path / "agents", rules=None, skills=None)

        tree = deploy_module.build_deployment_tree(
            paths=paths,
            dest=None,
            is_split_mode=True,
            skip_skills=False,
            only_skills=False,
            rules_copied=5,
            root_copied=2,
            skills_count=0,
            skills_files_copied=0,
        )

        assert tree is not None

    @pytest.mark.unit
    def test_unified_tree_skip_skills(self, tmp_path: Path):
        """Test tree for unified mode with skip_skills."""
        paths = deploy_module.DeploymentPaths(
            agents=tmp_path, rules=tmp_path / "rules", skills=None
        )

        tree = deploy_module.build_deployment_tree(
            paths=paths,
            dest=tmp_path,
            is_split_mode=False,
            skip_skills=True,
            only_skills=False,
            rules_copied=5,
            root_copied=2,
            skills_count=0,
            skills_files_copied=0,
        )

        assert tree is not None


# ============================================================================
# Remaining uncovered lines (383-385, 778, 783, 798-800)
# ============================================================================


class TestCopyRootFilesAgentsException:
    """Test copy_root_files AGENTS.md copy exception (lines 383-385)."""

    @pytest.mark.unit
    def test_agents_md_copy_exception(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test copy_root_files when AGENTS.md source is missing and no template."""
        project = tmp_path / "project"
        project.mkdir()
        # No AGENTS.md and no template — will raise FileNotFoundError on copy2
        rules_dir = project / "rules"
        rules_dir.mkdir()
        (rules_dir / "RULES_INDEX.md").write_text("# Index\n")

        dest = tmp_path / "dest"
        dest.mkdir()

        _copied, failed = deploy_module.copy_root_files(project, dest, dry_run=False, verbose=False)

        # AGENTS.md copy fails, RULES_INDEX.md succeeds
        assert failed == 1


class TestDeployExamplesSplitMode:
    """Test examples copy in split mode (line 778) and exception (lines 798-800)."""

    @pytest.mark.unit
    def test_examples_copy_split_mode(self, tmp_path: Path):
        """Test deploy copies examples in split mode."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "pyproject.toml").write_text('[project]\nname = "test"\n')
        (project / "AGENTS.md").write_text("# Agents\n")
        rules_dir = project / "rules"
        rules_dir.mkdir()
        (rules_dir / "100-test.md").write_text("# Test\n")
        (rules_dir / "RULES_INDEX.md").write_text("# Index\n")
        examples_dir = rules_dir / "examples"
        examples_dir.mkdir()
        (examples_dir / "example.md").write_text("# Example\n")
        skills_dir = project / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill1").mkdir()
        (skills_dir / "skill1" / "prompt.md").write_text("# Skill\n")

        agents_out = tmp_path / "agents_out"
        agents_out.mkdir()
        rules_out = tmp_path / "rules_out"
        rules_out.mkdir()

        result = deploy_module.deploy_rules(
            project_root=project,
            agents_dest=agents_out,
            rules_dest=rules_out,
            verbose=True,
        )

        assert result is True
        assert (rules_out / "examples" / "example.md").exists()

    @pytest.mark.unit
    def test_examples_copy_exception(
        self, source_project: Path, dest_dir: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test deploy handles examples copy exception."""
        examples_dir = source_project / "rules" / "examples"
        examples_dir.mkdir()
        (examples_dir / "example.md").write_text("# Example\n")

        import shutil

        original_copytree = shutil.copytree

        def failing_copytree(src, dst, **kwargs):
            if "examples" in str(src):
                raise PermissionError("Permission denied")
            return original_copytree(src, dst, **kwargs)

        monkeypatch.setattr(shutil, "copytree", failing_copytree)

        result = deploy_module.deploy_rules(
            project_root=source_project,
            dest=dest_dir,
            verbose=False,
        )

        # Deployment fails because of the examples copy failure
        assert result is False
