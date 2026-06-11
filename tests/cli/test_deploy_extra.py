"""Extra unit tests for deploy.py covering verbose paths and error branches.

Covers:
- validate_source_structure: only_skills edge cases (lines 244, 249)
- validate_source_structure: rules not a dir, no .md files (lines 257, 261)
- copy_rules: verbose=True dry_run and real copy (lines 307, 312, 314, 322, 324)
- copy_rules: RULES_INDEX.md is excluded from copy
- copy_root_files: verbose=True with agents and rules destinations (lines 376, 402-404)
- copy_root_files: failure when RULES_INDEX.md missing (lines 406-408)
- copy_skills: exclusions + verbose (lines 484, 487, 492-494, 502, 512-514, 523-527)
- deploy_rules: only_skills with no skills-dest returns False (lines 664-666)
- deploy_rules: source validation failure returns False (lines 640-643)
- deploy_rules: total_failed > 0 returns False (lines 760-761)
- deploy CLI: no destinations shows help (exits 0)
- deploy CLI: legacy positional arg rejected (exit 2)
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands.deploy import (
    DeploymentPaths,
    copy_root_files,
    copy_rules,
    copy_skills,
    deploy_rules,
    validate_source_structure,
)

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_minimal_source(base: Path) -> None:
    """Create a minimal valid source structure for deploy tests."""
    (base / "rules").mkdir(exist_ok=True)
    (base / "rules" / "000-test.md").write_text("# Test")
    (base / "rules" / "RULES_INDEX.md").write_text("# Index\n")
    (base / "templates").mkdir(exist_ok=True)
    (base / "templates" / "AGENTS_NO_MODE.md.template").write_text(
        "<!-- Template: test -->\n\n"
        'Foundation: read_file("{{rules_path}}/000-global-core.md")\n'
        "Skills: {{skills_path}}/\n"
    )
    (base / "templates" / "AGENTS_MODE.md.template").write_text(
        "<!-- Template: test -->\n\n"
        'Foundation: read_file("{{rules_path}}/000-global-core.md")\n'
        "Skills: {{skills_path}}/\n"
    )


# ---------------------------------------------------------------------------
# validate_source_structure edge cases
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_validate_source_structure_only_skills_dir_is_file(tmp_path: Path) -> None:
    """Skills path is a plain file → error (line 244)."""
    (tmp_path / "skills").write_text("not a directory")
    ok, errors = validate_source_structure(tmp_path, only_skills=True)
    assert not ok
    assert any("not a directory" in e for e in errors)


@pytest.mark.unit
def test_validate_source_structure_only_skills_empty_dir(tmp_path: Path) -> None:
    """Skills dir exists but has no subdirs → error (line 249)."""
    (tmp_path / "skills").mkdir()
    # Place only a file (not a subdirectory) to trigger the no-skill-dirs branch
    (tmp_path / "skills" / "lone_file.md").write_text("# file")
    ok, errors = validate_source_structure(tmp_path, only_skills=True)
    assert not ok
    assert any("No skill directories" in e for e in errors)


@pytest.mark.unit
def test_validate_source_structure_rules_is_file(tmp_path: Path) -> None:
    """Rules path is a plain file → error (line 257)."""
    (tmp_path / "rules").write_text("not a directory")
    ok, errors = validate_source_structure(tmp_path)
    assert not ok
    assert any("not a directory" in e for e in errors)


@pytest.mark.unit
def test_validate_source_structure_rules_dir_no_md_files(tmp_path: Path) -> None:
    """Rules dir exists but contains no .md files → error (line 261)."""
    (tmp_path / "rules").mkdir()
    ok, errors = validate_source_structure(tmp_path)
    assert not ok
    assert any("No .md files" in e for e in errors)


# ---------------------------------------------------------------------------
# copy_rules: verbose paths
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_copy_rules_verbose_dry_run_logs_would_copy(tmp_path: Path) -> None:
    """verbose=True + dry_run=True logs [dry-run] messages (lines 307, 314, 324)."""
    src = tmp_path / "rules"
    src.mkdir()
    (src / "100-test.md").write_text("# Test rule")
    dest = tmp_path / "dest_rules"
    copied, failed = copy_rules(src, dest, dry_run=True, verbose=True)
    assert copied == 1
    assert failed == 0
    assert not dest.exists()  # dry run: nothing written


@pytest.mark.unit
def test_copy_rules_verbose_real_copy_creates_dir(tmp_path: Path) -> None:
    """verbose=True + dry_run=False copies files and creates dest dir (lines 307, 312, 322)."""
    src = tmp_path / "rules"
    src.mkdir()
    (src / "100-test.md").write_text("# Test rule")
    dest = tmp_path / "dest_rules"
    copied, failed = copy_rules(src, dest, dry_run=False, verbose=True)
    assert copied == 1
    assert failed == 0
    assert (dest / "100-test.md").exists()


@pytest.mark.unit
def test_copy_rules_excludes_rules_index(tmp_path: Path) -> None:
    """RULES_INDEX.md is never included in copy_rules output."""
    src = tmp_path / "rules"
    src.mkdir()
    (src / "RULES_INDEX.md").write_text("# Index")
    (src / "001-rule.md").write_text("# Rule")
    dest = tmp_path / "dest"
    copied, _ = copy_rules(src, dest, dry_run=False, verbose=False)
    assert copied == 1
    assert not (dest / "RULES_INDEX.md").exists()


# ---------------------------------------------------------------------------
# copy_root_files: verbose paths
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_copy_root_files_verbose_agents_logs_generated(tmp_path: Path) -> None:
    """verbose=True logs 'Generated: AGENTS.md' when writing agents dest (line 376)."""
    _make_minimal_source(tmp_path)
    dest_agents = tmp_path / "dest_agents"
    dest_agents.mkdir()
    paths = DeploymentPaths(agents=dest_agents, rules=None, skills=None)
    written, failed = copy_root_files(tmp_path, paths, dry_run=False, verbose=True)
    assert written == 1
    assert failed == 0
    assert (dest_agents / "AGENTS.md").exists()


@pytest.mark.unit
def test_copy_root_files_verbose_rules_index_copied(tmp_path: Path) -> None:
    """verbose=True logs RULES_INDEX.md generation (lines 402-404)."""
    _make_minimal_source(tmp_path)
    dest_rules = tmp_path / "dest_rules"
    dest_rules.mkdir()
    paths = DeploymentPaths(agents=None, rules=dest_rules, skills=None)
    written, failed = copy_root_files(tmp_path, paths, dry_run=False, verbose=True)
    assert written >= 1
    assert failed == 0
    assert (dest_rules / "RULES_INDEX.md").exists()


@pytest.mark.unit
def test_copy_root_files_rules_index_missing_counts_failure(tmp_path: Path) -> None:
    """Missing RULES_INDEX.md → files_failed += 1 (lines 406-408)."""
    _make_minimal_source(tmp_path)
    (tmp_path / "rules" / "RULES_INDEX.md").unlink()  # remove it
    dest_rules = tmp_path / "dest_rules"
    dest_rules.mkdir()
    paths = DeploymentPaths(agents=None, rules=dest_rules, skills=None)
    _written, failed = copy_root_files(tmp_path, paths, dry_run=False, verbose=True)
    assert failed >= 1


# ---------------------------------------------------------------------------
# copy_skills: exclusions and verbose paths
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_copy_skills_excludes_and_logs(tmp_path: Path) -> None:
    """Excluded skill dirs are skipped; verbose logs 'Skipping excluded' (lines 484, 487, 502)."""
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "keep-skill").mkdir()
    (tmp_path / "skills" / "excluded-skill").mkdir()
    (tmp_path / "pyproject.toml").write_text(
        dedent("""\
            [project]
            name = "test"
            version = "1.0.0"

            [tool.rule_deployer]
            exclude_skills = ["excluded-skill"]
        """)
    )
    dest = tmp_path / "dest_skills"
    skills_count, _files_copied, failed = copy_skills(tmp_path, dest, dry_run=False, verbose=True)
    assert skills_count == 1
    assert failed == 0
    assert (dest / "keep-skill").exists()
    assert not (dest / "excluded-skill").exists()


@pytest.mark.unit
def test_copy_skills_verbose_creates_dest_dir(tmp_path: Path) -> None:
    """verbose=True + dry_run=False logs 'Created destination directory' (lines 492-494)."""
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "my-skill").mkdir()
    dest = tmp_path / "dest_skills"
    copy_skills(tmp_path, dest, dry_run=False, verbose=True)
    assert dest.exists()


@pytest.mark.unit
def test_copy_skills_dry_run_verbose_logs_would_create(tmp_path: Path) -> None:
    """verbose=True + dry_run=True logs '[dry-run] Would create directory' (line 494)."""
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "my-skill").mkdir()
    dest = tmp_path / "dest_skills"
    copy_skills(tmp_path, dest, dry_run=True, verbose=True)
    assert not dest.exists()


@pytest.mark.unit
def test_copy_skills_file_in_skills_dir_verbose(tmp_path: Path) -> None:
    """A file directly in skills/ is copied individually; verbose logs it (lines 512-514)."""
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "README.md").write_text("# standalone file")
    dest = tmp_path / "dest_skills"
    skills_count, files_copied, _ = copy_skills(tmp_path, dest, dry_run=False, verbose=True)
    assert skills_count == 1
    assert files_copied == 1
    assert (dest / "README.md").exists()


@pytest.mark.unit
def test_copy_skills_dir_verbose_logs_copied_directory(tmp_path: Path) -> None:
    """A subdirectory in skills/ is copytree'd; verbose logs it (lines 523-527)."""
    (tmp_path / "skills").mkdir()
    skill_dir = tmp_path / "skills" / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Skill content")
    dest = tmp_path / "dest_skills"
    skills_count, files_copied, _ = copy_skills(tmp_path, dest, dry_run=False, verbose=True)
    assert skills_count == 1
    assert files_copied == 1
    assert (dest / "my-skill" / "SKILL.md").exists()


@pytest.mark.unit
def test_copy_skills_dry_run_dir_verbose_logs_would_copy(tmp_path: Path) -> None:
    """dry_run=True dir in skills logs '[dry-run] Would copy directory' (lines 526-529)."""
    (tmp_path / "skills").mkdir()
    skill_dir = tmp_path / "skills" / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# content")
    dest = tmp_path / "dest_skills"
    skills_count, _, _ = copy_skills(tmp_path, dest, dry_run=True, verbose=True)
    assert skills_count == 1
    assert not dest.exists()


# ---------------------------------------------------------------------------
# deploy_rules: key decision branches
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_deploy_rules_only_skills_no_dest_returns_false(tmp_path: Path) -> None:
    """only_skills=True with no skills_dest returns False (lines 664-666)."""
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "my-skill").mkdir()
    result = deploy_rules(tmp_path, only_skills=True, skills_dest=None)
    assert result is False


@pytest.mark.unit
def test_deploy_rules_source_validation_failure_returns_false(tmp_path: Path) -> None:
    """Invalid source structure (no rules/ dir) returns False (lines 640-643)."""
    result = deploy_rules(tmp_path, rules_dest=tmp_path / "dest_rules")
    assert result is False


@pytest.mark.unit
def test_deploy_rules_total_failed_returns_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When copy_rules returns failures, deploy_rules returns False (lines 760-761)."""
    _make_minimal_source(tmp_path)
    monkeypatch.setattr(
        "ai_rules.commands.deploy.copy_rules",
        lambda *a, **kw: (0, 3),  # simulate 3 copy failures
    )
    dest = tmp_path / "dest"
    result = deploy_rules(
        tmp_path,
        agents_dest=dest,
        rules_dest=dest / "rules",
        verbose=False,
    )
    assert result is False


@pytest.mark.unit
def test_deploy_rules_verbose_skills_dest_logs_path(tmp_path: Path) -> None:
    """verbose=True with skills_dest logs the skills destination (line 621)."""
    _make_minimal_source(tmp_path)
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "my-skill").mkdir()
    dest = tmp_path / "dest"
    result = deploy_rules(
        tmp_path,
        agents_dest=dest,
        rules_dest=dest / "rules",
        skills_dest=dest / "skills",
        verbose=True,
    )
    assert result is True


# ---------------------------------------------------------------------------
# deploy CLI: top-level behavior
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_deploy_cli_no_destinations_shows_help() -> None:
    """Deploy with no destination args prints help and exits 0."""
    result = runner.invoke(app, ["deploy"])
    assert result.exit_code == 0


@pytest.mark.unit
def test_deploy_cli_legacy_positional_arg_rejected(tmp_path: Path) -> None:
    """Legacy unified positional destination is rejected with exit code 2."""
    result = runner.invoke(app, ["deploy", str(tmp_path / "dest")])
    assert result.exit_code == 2


# ---------------------------------------------------------------------------
# copy_root_files: dry_run=True verbose path (lines 403-404, 445-448)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_copy_root_files_dry_run_verbose_agents(tmp_path: Path) -> None:
    """verbose=True + dry_run=True for agents logs '[dry-run] Would generate' (lines 403-404)."""
    _make_minimal_source(tmp_path)
    dest_agents = tmp_path / "dest_agents"
    dest_agents.mkdir()
    paths = DeploymentPaths(agents=dest_agents, rules=None, skills=None)
    written, failed = copy_root_files(tmp_path, paths, dry_run=True, verbose=True)
    assert written == 1
    assert failed == 0
    # dry run: AGENTS.md should NOT be written
    assert not (dest_agents / "AGENTS.md").exists()


@pytest.mark.unit
def test_copy_root_files_dry_run_verbose_rules_index(tmp_path: Path) -> None:
    """verbose=True + dry_run=True for rules logs '[dry-run] Would generate RULES_INDEX' (lines 445-448)."""
    _make_minimal_source(tmp_path)
    dest_rules = tmp_path / "dest_rules"
    dest_rules.mkdir()
    paths = DeploymentPaths(agents=None, rules=dest_rules, skills=None)
    written, failed = copy_root_files(tmp_path, paths, dry_run=True, verbose=True)
    assert written == 1
    assert failed == 0
    assert not (dest_rules / "RULES_INDEX.md").exists()


# ---------------------------------------------------------------------------
# load_skill_exclusions: no-exclusions and parse-failure paths (lines 439, 445-448)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_load_skill_exclusions_empty_list_returns_empty_set(tmp_path: Path) -> None:
    """pyproject.toml with empty exclude_skills returns empty set (line 439)."""
    from ai_rules.commands.deploy import load_skill_exclusions

    (tmp_path / "pyproject.toml").write_text(
        dedent("""\
            [project]
            name = "test"
            version = "1.0.0"

            [tool.rule_deployer]
            exclude_skills = []
        """)
    )
    result = load_skill_exclusions(tmp_path, verbose=False)
    assert result == set()


@pytest.mark.unit
def test_load_skill_exclusions_malformed_toml_returns_empty_set(tmp_path: Path) -> None:
    """Malformed pyproject.toml logs warning and returns empty set (lines 445-448)."""
    from ai_rules.commands.deploy import load_skill_exclusions

    (tmp_path / "pyproject.toml").write_bytes(b"\xff\xfe invalid utf-8 \x80")
    result = load_skill_exclusions(tmp_path, verbose=True)
    assert result == set()


# ---------------------------------------------------------------------------
# copy_skills: file dry_run verbose path (lines 513-514)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_copy_skills_file_dry_run_verbose_logs_would_copy(tmp_path: Path) -> None:
    """verbose=True + dry_run=True for a file logs '[dry-run] Would copy' (lines 513-514)."""
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "README.md").write_text("# standalone")
    dest = tmp_path / "dest_skills"
    skills_count, _, _ = copy_skills(tmp_path, dest, dry_run=True, verbose=True)
    assert skills_count == 1
    assert not dest.exists()


# ---------------------------------------------------------------------------
# deploy_rules: examples dir + skip_skills verbose (lines 694-709, 722)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_deploy_rules_copies_examples_subdirectory(tmp_path: Path) -> None:
    """rules/examples/ is copytree'd to dest/rules/examples/ (lines 694-709)."""
    _make_minimal_source(tmp_path)
    (tmp_path / "rules" / "examples").mkdir()
    (tmp_path / "rules" / "examples" / "001-example.md").write_text("# Example")
    dest = tmp_path / "dest"
    result = deploy_rules(
        tmp_path,
        agents_dest=dest,
        rules_dest=dest / "rules",
        verbose=False,
    )
    assert result is True
    assert (dest / "rules" / "examples" / "001-example.md").exists()


@pytest.mark.unit
def test_deploy_rules_skip_skills_verbose_logs_skipping(tmp_path: Path) -> None:
    """skip_skills=True + verbose=True logs 'Skipping skills deployment' (line 722)."""
    _make_minimal_source(tmp_path)
    dest = tmp_path / "dest"
    result = deploy_rules(
        tmp_path,
        agents_dest=dest,
        rules_dest=dest / "rules",
        skip_skills=True,
        verbose=True,
    )
    assert result is True
