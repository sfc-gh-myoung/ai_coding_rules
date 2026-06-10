"""Tests for ai-rules deploy CLI command (split-only deployment).

Deployment places each artifact (AGENTS.md, rules/, skills/) at its own
destination. Unified positional-destination deployment was removed.

Tests follow pytest best practices:
- AAA pattern (Arrange-Act-Assert)
- Function-scoped fixtures
- Isolation with tmp_path
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands import deploy as deploy_module

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MODE_TEMPLATE = dedent(
    """\
    <!-- Template: Do not edit directly. -->

    # AI Agent Bootstrap Protocol

    Foundation: read_file("{{rules_path}}/000-global-core.md")
    Skills live at {{skills_path}}/

    <!-- MODE-ONLY:start -->
    MODE: [PLAN|ACT]
    <!-- MODE-ONLY:end -->

    End of protocol.
    """
)

NO_MODE_TEMPLATE = dedent(
    """\
    <!-- Template: Do not edit directly. -->

    # AI Agent Bootstrap Protocol

    Foundation: read_file("{{rules_path}}/000-global-core.md")
    Skills live at {{skills_path}}/

    <!-- NO-MODE-ONLY:start -->
    Auto-execute: proceed after task list.
    <!-- NO-MODE-ONLY:end -->

    End of protocol.
    """
)


@pytest.fixture
def source_project(tmp_path: Path) -> Path:
    """Create a minimal source project structure for deployment testing."""
    project = tmp_path / "source_project"
    project.mkdir()

    (project / "pyproject.toml").write_text(
        dedent("""
        [project]
        name = "test-project"
        version = "1.0.0"

        [tool.rule_deployer]
        exclude_skills = ["excluded-skill"]
        """)
    )

    # AGENTS source templates
    templates_dir = project / "templates"
    templates_dir.mkdir()
    (templates_dir / "AGENTS_MODE.md.template").write_text(MODE_TEMPLATE)
    (templates_dir / "AGENTS_NO_MODE.md.template").write_text(NO_MODE_TEMPLATE)

    # A root AGENTS.md so validate_source_structure passes
    (project / "AGENTS.md").write_text("# AGENTS\n\nDeployed artifact.")

    # rules directory (RULES_INDEX uses placeholders to exercise substitution)
    rules_dir = project / "rules"
    rules_dir.mkdir()
    (rules_dir / "000-global-core.md").write_text("# Global Core Rule\n\nTest rule.")
    (rules_dir / "100-test-rule.md").write_text("# Test Rule\n\nAnother test rule.")
    (rules_dir / "RULES_INDEX.md").write_text(
        "# Rules Index\n\nRead rules/000-global-core.md\ngrep ... rules/RULES_INDEX.md\n"
    )

    # skills directory
    skills_dir = project / "skills"
    skills_dir.mkdir()
    skill1 = skills_dir / "skill1"
    skill1.mkdir()
    (skill1 / "prompt.md").write_text("# Skill 1\n\nTest skill.")
    (skill1 / "config.yaml").write_text("name: skill1\n")
    skill2 = skills_dir / "skill2"
    skill2.mkdir()
    (skill2 / "prompt.md").write_text("# Skill 2\n\nAnother skill.")
    excluded = skills_dir / "excluded-skill"
    excluded.mkdir()
    (excluded / "prompt.md").write_text("# Excluded\n\nThis should be excluded.")

    return project


@pytest.fixture
def patched_root(source_project: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point deploy.find_project_root at the source project (for CLI tests)."""
    monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)
    return source_project


@pytest.fixture
def agents_dest(tmp_path: Path) -> Path:
    d = tmp_path / "out_agents"
    d.mkdir()
    return d


@pytest.fixture
def rules_dest(tmp_path: Path) -> Path:
    d = tmp_path / "out_rules"
    d.mkdir()
    return d


@pytest.fixture
def skills_dest(tmp_path: Path) -> Path:
    d = tmp_path / "out_skills"
    d.mkdir()
    return d


# ---------------------------------------------------------------------------
# Help output
# ---------------------------------------------------------------------------


class TestDeployHelpOutput:
    @pytest.mark.unit
    def test_help_shows_split_destination_options(self):
        result = runner.invoke(app, ["deploy", "--help"])
        assert result.exit_code == 0
        assert "--agents-dest" in result.output
        assert "--rules-dest" in result.output
        assert "--skills-dest" in result.output

    @pytest.mark.unit
    def test_help_does_not_advertise_split_flag(self):
        """The --split flag was removed (split is the only model)."""
        result = runner.invoke(app, ["deploy", "--help"])
        assert "--split" not in result.output

    @pytest.mark.unit
    def test_help_uses_with_mode_not_no_mode(self):
        """NO_MODE is the default; --with-mode opts into PLAN/ACT. --no-mode is gone."""
        result = runner.invoke(app, ["deploy", "--help"])
        assert "--with-mode" in result.output
        assert "--no-mode" not in result.output


# ---------------------------------------------------------------------------
# Removed unified mode / migration
# ---------------------------------------------------------------------------


class TestUnifiedRemoved:
    @pytest.mark.unit
    def test_positional_destination_errors_with_hint(self, patched_root: Path, tmp_path: Path):
        result = runner.invoke(app, ["deploy", str(tmp_path / "legacy")])
        assert result.exit_code == 2
        assert "Unified deployment" in result.output
        assert "--agents-dest" in result.output

    @pytest.mark.unit
    def test_no_destination_shows_help(self, patched_root: Path):
        result = runner.invoke(app, ["deploy"])
        assert result.exit_code == 0
        # Help text is printed
        assert "--agents-dest" in result.output


# ---------------------------------------------------------------------------
# resolve_paths
# ---------------------------------------------------------------------------


class TestResolvePaths:
    @pytest.mark.unit
    def test_all_destinations(self, tmp_path: Path):
        paths = deploy_module.resolve_paths(
            agents_dest=tmp_path / "a",
            rules_dest=tmp_path / "r",
            skills_dest=tmp_path / "s",
        )
        assert paths.agents == (tmp_path / "a").resolve()
        assert paths.rules == (tmp_path / "r").resolve()
        assert paths.skills == (tmp_path / "s").resolve()

    @pytest.mark.unit
    def test_omitted_destinations_are_none(self, tmp_path: Path):
        paths = deploy_module.resolve_paths(agents_dest=tmp_path / "a")
        assert paths.agents == (tmp_path / "a").resolve()
        assert paths.rules is None
        assert paths.skills is None


# ---------------------------------------------------------------------------
# substitute_template / strip_template_markers
# ---------------------------------------------------------------------------


class TestSubstituteTemplate:
    @pytest.mark.unit
    def test_absolute_when_dest_provided(self, tmp_path: Path):
        paths = deploy_module.resolve_paths(
            agents_dest=tmp_path / "a", rules_dest=tmp_path / "r", skills_dest=tmp_path / "s"
        )
        out = deploy_module.substitute_template(
            "R={{rules_path}} S={{skills_path}}", paths, tmp_path
        )
        assert str((tmp_path / "r").resolve()) in out
        assert str((tmp_path / "s").resolve()) in out

    @pytest.mark.unit
    def test_absolute_project_fallback_when_rules_omitted(self, tmp_path: Path):
        """Agents-only deploy must use the project's absolute rules/ path, not a relative string."""
        paths = deploy_module.resolve_paths(agents_dest=tmp_path / "a")
        out = deploy_module.substitute_template("read_file({{rules_path}}/x.md)", paths, tmp_path)
        assert f"read_file({tmp_path / 'rules'}/x.md)" in out
        assert "read_file(rules/x.md)" not in out

    @pytest.mark.unit
    def test_absolute_project_fallback_for_both(self, tmp_path: Path):
        paths = deploy_module.resolve_paths(agents_dest=tmp_path / "a")
        out = deploy_module.substitute_template("{{rules_path}}|{{skills_path}}", paths, tmp_path)
        assert out == f"{tmp_path / 'rules'}|{tmp_path / 'skills'}"


class TestStripTemplateMarkers:
    @pytest.mark.unit
    def test_removes_marker_and_sentinels(self):
        content = (
            "<!-- Template: x -->\n"
            "\n"
            "# Title\n"
            "<!-- MODE-ONLY:start -->\n"
            "keep me\n"
            "<!-- MODE-ONLY:end -->\n"
            "<!-- NO-MODE-ONLY:start -->\n"
            "also kept\n"
            "<!-- NO-MODE-ONLY:end -->\n"
        )
        out = deploy_module.strip_template_markers(content)
        assert "<!-- Template:" not in out
        assert "MODE-ONLY" not in out
        assert "NO-MODE-ONLY" not in out
        # Content between sentinels is preserved
        assert "keep me" in out
        assert "also kept" in out
        assert "# Title" in out


# ---------------------------------------------------------------------------
# copy_rules
# ---------------------------------------------------------------------------


class TestCopyRules:
    @pytest.mark.unit
    def test_copies_md_except_index(self, source_project: Path, tmp_path: Path):
        dest = tmp_path / "rdest"
        copied, failed = deploy_module.copy_rules(
            source_project / "rules", dest, dry_run=False, verbose=False
        )
        assert failed == 0
        assert copied == 2  # RULES_INDEX.md excluded
        assert (dest / "000-global-core.md").exists()
        assert (dest / "100-test-rule.md").exists()
        assert not (dest / "RULES_INDEX.md").exists()

    @pytest.mark.unit
    def test_dry_run_copies_nothing(self, source_project: Path, tmp_path: Path):
        dest = tmp_path / "rdest"
        copied, failed = deploy_module.copy_rules(
            source_project / "rules", dest, dry_run=True, verbose=False
        )
        assert copied == 2
        assert failed == 0
        assert not (dest / "000-global-core.md").exists()

    @pytest.mark.unit
    def test_no_md_files(self, tmp_path: Path):
        source = tmp_path / "empty"
        source.mkdir()
        copied, failed = deploy_module.copy_rules(source, tmp_path / "d", verbose=False)
        assert (copied, failed) == (0, 0)

    @pytest.mark.unit
    def test_exception_during_copy(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        source = tmp_path / "rules"
        source.mkdir()
        (source / "000-x.md").write_text("x")

        def boom(*_a, **_k):
            raise OSError("disk full")

        monkeypatch.setattr(deploy_module.shutil, "copy2", boom)
        _copied, failed = deploy_module.copy_rules(
            source, tmp_path / "d", dry_run=False, verbose=False
        )
        assert failed == 1


# ---------------------------------------------------------------------------
# copy_skills
# ---------------------------------------------------------------------------


class TestCopySkills:
    @pytest.mark.unit
    def test_copies_and_excludes(self, source_project: Path, tmp_path: Path):
        dest = tmp_path / "sdest"
        skills_count, files_copied, failed = deploy_module.copy_skills(
            source_project, dest, dry_run=False, verbose=False
        )
        assert failed == 0
        assert skills_count == 2  # excluded-skill skipped
        assert files_copied == 3  # skill1 (2) + skill2 (1)
        assert (dest / "skill1" / "prompt.md").exists()
        assert not (dest / "excluded-skill").exists()

    @pytest.mark.unit
    def test_no_skills_dir(self, tmp_path: Path):
        project = tmp_path / "proj"
        project.mkdir()
        skills_count, files_copied, failed = deploy_module.copy_skills(
            project, tmp_path / "d", verbose=False
        )
        assert (skills_count, files_copied, failed) == (0, 0, 0)

    @pytest.mark.unit
    def test_hidden_dir_skipped(self, tmp_path: Path):
        project = tmp_path / "proj"
        (project / "skills" / ".hidden").mkdir(parents=True)
        (project / "skills" / ".hidden" / "x.md").write_text("x")
        (project / "skills" / "real").mkdir()
        (project / "skills" / "real" / "y.md").write_text("y")
        skills_count, _files, _failed = deploy_module.copy_skills(
            project, tmp_path / "d", dry_run=False, verbose=False
        )
        assert skills_count == 1

    @pytest.mark.unit
    def test_individual_file_skill(self, tmp_path: Path):
        project = tmp_path / "proj"
        (project / "skills").mkdir(parents=True)
        (project / "skills" / "loose.md").write_text("loose")
        dest = tmp_path / "d"
        skills_count, files_copied, _failed = deploy_module.copy_skills(
            project, dest, dry_run=False, verbose=False
        )
        assert skills_count == 1
        assert files_copied == 1
        assert (dest / "loose.md").exists()

    @pytest.mark.unit
    def test_exception_during_copy(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        project = tmp_path / "proj"
        (project / "skills" / "s1").mkdir(parents=True)
        (project / "skills" / "s1" / "p.md").write_text("p")

        def boom(*_a, **_k):
            raise OSError("nope")

        monkeypatch.setattr(deploy_module.shutil, "copytree", boom)
        _count, _files, failed = deploy_module.copy_skills(
            project, tmp_path / "d", dry_run=False, verbose=False
        )
        assert failed == 1


# ---------------------------------------------------------------------------
# copy_root_files
# ---------------------------------------------------------------------------


class TestCopyRootFiles:
    @pytest.mark.unit
    def test_writes_agents_and_index_with_substitution(
        self, source_project: Path, agents_dest: Path, rules_dest: Path
    ):
        paths = deploy_module.resolve_paths(agents_dest=agents_dest, rules_dest=rules_dest)
        written, failed = deploy_module.copy_root_files(
            source_project, paths, dry_run=False, verbose=False
        )
        assert failed == 0
        assert written == 2
        agents = (agents_dest / "AGENTS.md").read_text()
        index = (rules_dest / "RULES_INDEX.md").read_text()
        # Absolute rules path substituted
        assert str(rules_dest) in agents
        assert str(rules_dest) in index
        # RULES_INDEX relative `rules/` references rewritten to the absolute dest
        assert f"{rules_dest}/000-global-core.md" in index
        assert f"{rules_dest}/RULES_INDEX.md" in index
        # Markers and sentinels stripped from AGENTS.md
        assert "<!-- Template:" not in agents
        assert "MODE-ONLY" not in agents
        # MODE content preserved
        assert "MODE: [PLAN|ACT]" in agents

    @pytest.mark.unit
    def test_agents_only_skips_index(self, source_project: Path, agents_dest: Path):
        paths = deploy_module.resolve_paths(agents_dest=agents_dest)
        written, failed = deploy_module.copy_root_files(
            source_project, paths, dry_run=False, verbose=False
        )
        assert failed == 0
        assert written == 1
        agents = (agents_dest / "AGENTS.md").read_text()
        # Absolute project-root fallback used, not relative string
        assert f'read_file("{source_project}/rules/000-global-core.md")' in agents

    @pytest.mark.unit
    def test_no_mode_template_selected(self, source_project: Path, agents_dest: Path):
        paths = deploy_module.resolve_paths(agents_dest=agents_dest)
        deploy_module.copy_root_files(
            source_project, paths, dry_run=False, verbose=False, no_mode=True
        )
        agents = (agents_dest / "AGENTS.md").read_text()
        assert "Auto-execute" in agents
        assert "MODE: [PLAN|ACT]" not in agents
        assert "NO-MODE-ONLY" not in agents

    @pytest.mark.unit
    def test_dry_run_writes_nothing(self, source_project: Path, agents_dest: Path):
        paths = deploy_module.resolve_paths(agents_dest=agents_dest)
        written, failed = deploy_module.copy_root_files(
            source_project, paths, dry_run=True, verbose=False
        )
        assert (written, failed) == (1, 0)
        assert not (agents_dest / "AGENTS.md").exists()

    @pytest.mark.unit
    def test_missing_template_records_failure(self, tmp_path: Path, agents_dest: Path):
        project = tmp_path / "proj"
        (project / "rules").mkdir(parents=True)
        (project / "rules" / "RULES_INDEX.md").write_text("idx")
        # No templates/ dir -> AGENTS generation fails
        paths = deploy_module.resolve_paths(agents_dest=agents_dest)
        _written, failed = deploy_module.copy_root_files(
            project, paths, dry_run=False, verbose=False
        )
        assert failed == 1


# ---------------------------------------------------------------------------
# build_deployment_tree
# ---------------------------------------------------------------------------


class TestBuildDeploymentTree:
    @pytest.mark.unit
    def test_only_skills_tree(self, tmp_path: Path):
        paths = deploy_module.resolve_paths(skills_dest=tmp_path / "s")
        tree = deploy_module.build_deployment_tree(
            paths,
            only_skills=True,
            rules_copied=0,
            root_copied=0,
            skills_count=3,
            skills_files_copied=9,
            project_root=tmp_path,
        )
        assert tree is not None

    @pytest.mark.unit
    def test_partial_tree_omitted_dests(self, tmp_path: Path):
        paths = deploy_module.resolve_paths(agents_dest=tmp_path / "a")
        tree = deploy_module.build_deployment_tree(
            paths,
            only_skills=False,
            rules_copied=0,
            root_copied=1,
            skills_count=0,
            skills_files_copied=0,
            project_root=tmp_path,
        )
        assert tree is not None


# ---------------------------------------------------------------------------
# validate_destinations
# ---------------------------------------------------------------------------


class TestValidateDestinations:
    @pytest.mark.unit
    def test_skills_requires_agents(self, tmp_path: Path):
        is_valid, errors = deploy_module.validate_destinations(
            agents_dest=None, rules_dest=None, skills_dest=tmp_path / "s", force=True
        )
        assert not is_valid
        assert any("--skills-dest requires --agents-dest" in e for e in errors)

    @pytest.mark.unit
    def test_force_creates_missing(self, tmp_path: Path):
        missing = tmp_path / "nope"
        is_valid, errors = deploy_module.validate_destinations(
            agents_dest=missing, rules_dest=None, skills_dest=None, force=True
        )
        assert is_valid
        assert errors == []
        assert missing.exists()

    @pytest.mark.unit
    def test_prompt_decline_records_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        missing = tmp_path / "nope"
        monkeypatch.setattr(deploy_module.console, "input", lambda *_a, **_k: "n")
        is_valid, errors = deploy_module.validate_destinations(
            agents_dest=missing, rules_dest=None, skills_dest=None, force=False
        )
        assert not is_valid
        assert any("does not exist" in e for e in errors)


# ---------------------------------------------------------------------------
# validate_source_structure
# ---------------------------------------------------------------------------


class TestValidateSourceStructure:
    @pytest.mark.unit
    def test_valid(self, source_project: Path):
        is_valid, errors = deploy_module.validate_source_structure(source_project)
        assert is_valid
        assert errors == []

    @pytest.mark.unit
    def test_missing_rules(self, tmp_path: Path):
        is_valid, errors = deploy_module.validate_source_structure(tmp_path)
        assert not is_valid
        assert errors

    @pytest.mark.unit
    def test_no_mode_template_fallback(self, tmp_path: Path):
        """AGENTS.md absent but NO_MODE template present -> valid."""
        project = tmp_path / "proj"
        (project / "rules").mkdir(parents=True)
        (project / "rules" / "000-x.md").write_text("x")
        (project / "rules" / "RULES_INDEX.md").write_text("idx")
        (project / "templates").mkdir()
        (project / "templates" / "AGENTS_NO_MODE.md.template").write_text("t")
        is_valid, errors = deploy_module.validate_source_structure(project, no_mode=True)
        assert is_valid, errors

    @pytest.mark.unit
    def test_only_skills_valid(self, source_project: Path):
        is_valid, errors = deploy_module.validate_source_structure(source_project, only_skills=True)
        assert is_valid, errors

    @pytest.mark.unit
    def test_only_skills_no_dir(self, tmp_path: Path):
        is_valid, _errors = deploy_module.validate_source_structure(tmp_path, only_skills=True)
        assert not is_valid


# ---------------------------------------------------------------------------
# load_template
# ---------------------------------------------------------------------------


class TestLoadTemplate:
    @pytest.mark.unit
    def test_exists(self, source_project: Path):
        content = deploy_module.load_template(source_project, no_mode=False)
        assert content is not None
        assert "MODE-ONLY" in content

    @pytest.mark.unit
    def test_no_mode(self, source_project: Path):
        content = deploy_module.load_template(source_project, no_mode=True)
        assert content is not None
        assert "NO-MODE-ONLY" in content

    @pytest.mark.unit
    def test_not_found(self, tmp_path: Path):
        assert deploy_module.load_template(tmp_path) is None


# ---------------------------------------------------------------------------
# _prompt_create_directory
# ---------------------------------------------------------------------------


class TestPromptCreateDirectory:
    @pytest.mark.unit
    def test_accepts(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        target = tmp_path / "new"
        monkeypatch.setattr(deploy_module.console, "input", lambda *_a, **_k: "y")
        assert deploy_module._prompt_create_directory(target, "--agents-dest") is True
        assert target.exists()

    @pytest.mark.unit
    def test_declines(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        target = tmp_path / "new"
        monkeypatch.setattr(deploy_module.console, "input", lambda *_a, **_k: "n")
        assert deploy_module._prompt_create_directory(target, "--agents-dest") is False
        assert not target.exists()

    @pytest.mark.unit
    def test_eof(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        def raise_eof(*_a, **_k):
            raise EOFError

        monkeypatch.setattr(deploy_module.console, "input", raise_eof)
        assert deploy_module._prompt_create_directory(tmp_path / "x", "--rules-dest") is False

    @pytest.mark.unit
    def test_empty_response_accepts(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        target = tmp_path / "new"
        monkeypatch.setattr(deploy_module.console, "input", lambda *_a, **_k: "")
        assert deploy_module._prompt_create_directory(target, "--agents-dest") is True


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------


class TestDeployCLI:
    @pytest.mark.integration
    def test_full_split_deploy(
        self,
        patched_root: Path,
        agents_dest: Path,
        rules_dest: Path,
        skills_dest: Path,
    ):
        result = runner.invoke(
            app,
            [
                "deploy",
                "--agents-dest",
                str(agents_dest),
                "--rules-dest",
                str(rules_dest),
                "--skills-dest",
                str(skills_dest),
                "--quiet",
            ],
        )
        assert result.exit_code == 0, result.output
        assert (agents_dest / "AGENTS.md").exists()
        assert (rules_dest / "000-global-core.md").exists()
        assert (rules_dest / "RULES_INDEX.md").exists()
        assert (skills_dest / "skill1" / "prompt.md").exists()
        assert not (skills_dest / "excluded-skill").exists()
        # AGENTS.md references the absolute rules destination
        assert str(rules_dest) in (agents_dest / "AGENTS.md").read_text()

    @pytest.mark.integration
    def test_agents_only_uses_absolute_project_rules(self, patched_root: Path, agents_dest: Path):
        result = runner.invoke(app, ["deploy", "--agents-dest", str(agents_dest), "--quiet"])
        assert result.exit_code == 0, result.output
        agents = (agents_dest / "AGENTS.md").read_text()
        assert f'read_file("{patched_root}/rules/000-global-core.md")' in agents
        assert 'read_file("rules/000-global-core.md")' not in agents

    @pytest.mark.integration
    def test_agents_only_no_local_rules_dir(self, patched_root: Path, agents_dest: Path):
        """Agents-only deploy must not create a local rules/ dir or RULES_INDEX.md."""
        result = runner.invoke(app, ["deploy", "--agents-dest", str(agents_dest), "--quiet"])
        assert result.exit_code == 0, result.output
        assert not (agents_dest / "rules").exists()
        assert not (agents_dest / "RULES_INDEX.md").exists()
        agents_text = (agents_dest / "AGENTS.md").read_text()
        assert str(patched_root / "rules") in agents_text

    @pytest.mark.integration
    def test_only_skills_requires_skills_dest(self, patched_root: Path, agents_dest: Path):
        result = runner.invoke(
            app, ["deploy", "--agents-dest", str(agents_dest), "--only-skills", "--quiet"]
        )
        assert result.exit_code == 1
        assert "No destination specified for skills" in result.output

    @pytest.mark.integration
    def test_only_skills_with_skills_dest(self, patched_root: Path, skills_dest: Path):
        result = runner.invoke(
            app, ["deploy", "--skills-dest", str(skills_dest), "--only-skills", "--quiet"]
        )
        assert result.exit_code == 0, result.output
        assert (skills_dest / "skill1").exists()

    @pytest.mark.integration
    def test_only_skills_and_skip_skills_conflict(
        self, patched_root: Path, agents_dest: Path, skills_dest: Path
    ):
        result = runner.invoke(
            app,
            [
                "deploy",
                "--agents-dest",
                str(agents_dest),
                "--skills-dest",
                str(skills_dest),
                "--only-skills",
                "--skip-skills",
            ],
        )
        assert result.exit_code == 1
        assert "Cannot use both" in result.output

    @pytest.mark.integration
    def test_skip_skills(self, patched_root: Path, agents_dest: Path, skills_dest: Path):
        result = runner.invoke(
            app,
            [
                "deploy",
                "--agents-dest",
                str(agents_dest),
                "--skills-dest",
                str(skills_dest),
                "--skip-skills",
                "--quiet",
            ],
        )
        assert result.exit_code == 0, result.output
        assert not (skills_dest / "skill1").exists()

    @pytest.mark.integration
    def test_default_renders_no_mode_template(self, patched_root: Path, agents_dest: Path):
        """Default (no flag) deploys the simplified NO_MODE bootstrap."""
        result = runner.invoke(app, ["deploy", "--agents-dest", str(agents_dest), "--quiet"])
        assert result.exit_code == 0, result.output
        agents = (agents_dest / "AGENTS.md").read_text()
        assert "Auto-execute" in agents
        assert "MODE: [PLAN|ACT]" not in agents

    @pytest.mark.integration
    def test_with_mode_renders_mode_template(self, patched_root: Path, agents_dest: Path):
        """--with-mode deploys the PLAN/ACT (MODE) bootstrap."""
        result = runner.invoke(
            app, ["deploy", "--agents-dest", str(agents_dest), "--with-mode", "--quiet"]
        )
        assert result.exit_code == 0, result.output
        agents = (agents_dest / "AGENTS.md").read_text()
        assert "MODE: [PLAN|ACT]" in agents
        assert "Auto-execute" not in agents

    @pytest.mark.integration
    def test_dry_run_creates_no_files(self, patched_root: Path, agents_dest: Path):
        result = runner.invoke(
            app, ["deploy", "--agents-dest", str(agents_dest), "--dry-run", "-v"]
        )
        assert result.exit_code == 0, result.output
        assert not (agents_dest / "AGENTS.md").exists()

    @pytest.mark.integration
    def test_force_creates_missing_dirs(self, patched_root: Path, tmp_path: Path):
        missing = tmp_path / "made_by_force"
        result = runner.invoke(app, ["deploy", "--agents-dest", str(missing), "--force", "--quiet"])
        assert result.exit_code == 0, result.output
        assert (missing / "AGENTS.md").exists()

    @pytest.mark.integration
    def test_skills_dest_without_agents_dest_errors(self, patched_root: Path, skills_dest: Path):
        result = runner.invoke(app, ["deploy", "--skills-dest", str(skills_dest), "--force"])
        assert result.exit_code == 1
        assert "--skills-dest requires --agents-dest" in result.output

    @pytest.mark.integration
    def test_missing_project_root(self, agents_dest: Path, monkeypatch: pytest.MonkeyPatch):
        def raise_not_found():
            raise FileNotFoundError

        monkeypatch.setattr(deploy_module, "find_project_root", raise_not_found)
        result = runner.invoke(app, ["deploy", "--agents-dest", str(agents_dest)])
        assert result.exit_code == 1
        assert "Could not find project root" in result.output

    @pytest.mark.integration
    def test_rules_index_rewrite_preserves_dir_keyword_token(
        self, source_project: Path, monkeypatch: pytest.MonkeyPatch, rules_dest: Path
    ):
        """Deploying RULES_INDEX rewrites path-prefix `rules/` to absolute but
        preserves the `dir:rules/` keyword trigger token verbatim.
        """
        monkeypatch.setattr(deploy_module, "find_project_root", lambda: source_project)
        # Override fixture RULES_INDEX to include a dir:rules/ keyword token
        rules_index = source_project / "rules" / "RULES_INDEX.md"
        rules_index.write_text(
            "Read rules/000-global-core.md\n"
            "grep rules/RULES_INDEX.md\n"
            "| dir:rules/ | kw:rule governance |\n"
        )

        result = runner.invoke(
            app,
            [
                "deploy",
                "--rules-dest",
                str(rules_dest),
                "--agents-dest",
                str(rules_dest),
                "--quiet",
            ],
        )
        assert result.exit_code == 0, result.output

        deployed = (rules_dest / "RULES_INDEX.md").read_text()
        abs_prefix = str(rules_dest)
        # Path-prefix references must be rewritten to absolute
        assert f"{abs_prefix}/000-global-core.md" in deployed
        assert f"{abs_prefix}/RULES_INDEX.md" in deployed
        # dir:rules/ keyword trigger token must NOT be prefixed with the absolute path
        assert "dir:rules/" in deployed
        assert f"dir:{abs_prefix}" not in deployed
