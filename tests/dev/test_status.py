"""Unit tests for ai_rules.commands.dev.status."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_rules.commands.dev.status import status_app

runner = CliRunner()


def _write_pyproject(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\nversion = '0.1'\n")


class TestStatusShow:
    """Tests for status show command."""

    @pytest.mark.unit
    def test_show_displays_project_heading(self, tmp_path: Path):
        """Status show prints the status heading."""
        _write_pyproject(tmp_path)

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(status_app, ["show"])

        assert result.exit_code == 0
        assert "AI Coding Rules" in result.output

    @pytest.mark.unit
    def test_show_displays_count_fields(self, tmp_path: Path):
        """Status show prints Rules, Examples, Skills, Tests labels."""
        _write_pyproject(tmp_path)

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(status_app, ["show"])

        assert result.exit_code == 0
        assert "Rules:" in result.output
        assert "Tests:" in result.output

    @pytest.mark.unit
    def test_show_counts_md_files(self, tmp_path: Path):
        """Status show correctly counts .md files in rules/."""
        _write_pyproject(tmp_path)
        rules = tmp_path / "rules"
        rules.mkdir()
        (rules / "999-test-core.md").write_text("# rule")
        (rules / "200-python-core.md").write_text("# rule")

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(status_app, ["show"])

        assert result.exit_code == 0
        assert "2" in result.output

    @pytest.mark.unit
    def test_show_counts_directory_based_skills(self, tmp_path: Path):
        """Status show counts skills as directories containing SKILL.md."""
        _write_pyproject(tmp_path)
        skills = tmp_path / "skills"
        (skills / "rule-reviewer").mkdir(parents=True)
        (skills / "rule-reviewer" / "SKILL.md").write_text("---\nname: rule-reviewer\n---\n")
        (skills / "skill-timer").mkdir()
        (skills / "skill-timer" / "SKILL.md").write_text("---\nname: skill-timer\n---\n")
        (skills / "README.md").write_text("# Not a skill")

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(status_app, ["show"])

        assert result.exit_code == 0
        assert "Skills:   2 files in skills/" in result.output


class TestStatusPreflight:
    """Tests for status preflight command."""

    @pytest.mark.unit
    def test_preflight_succeeds_when_uv_and_pyproject_present(self, tmp_path: Path):
        """Preflight exits 0 when uv is on PATH and pyproject.toml exists."""
        _write_pyproject(tmp_path)

        with (
            patch("ai_rules.commands.dev.status.shutil.which", return_value="/usr/bin/uv"),
            pytest.MonkeyPatch.context() as mp,
        ):
            mp.chdir(tmp_path)
            result = runner.invoke(status_app, ["preflight"])

        assert result.exit_code == 0
        assert "Environment ready" in result.output

    @pytest.mark.unit
    def test_preflight_fails_when_uv_missing(self, tmp_path: Path):
        """Preflight exits 1 when uv is not found."""
        _write_pyproject(tmp_path)

        with (
            patch("ai_rules.commands.dev.status.shutil.which", return_value=None),
            pytest.MonkeyPatch.context() as mp,
        ):
            mp.chdir(tmp_path)
            result = runner.invoke(status_app, ["preflight"])

        assert result.exit_code != 0

    @pytest.mark.unit
    def test_preflight_fails_when_pyproject_missing(self, tmp_path: Path):
        """Preflight exits 1 when pyproject.toml is absent."""
        with (
            patch("ai_rules.commands.dev.status.shutil.which", return_value="/usr/bin/uv"),
            pytest.MonkeyPatch.context() as mp,
        ):
            mp.chdir(tmp_path)
            result = runner.invoke(status_app, ["preflight"])

        assert result.exit_code != 0
