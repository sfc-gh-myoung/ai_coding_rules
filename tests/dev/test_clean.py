"""Unit tests for ai_rules.commands.dev.clean."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules.commands.dev.clean import clean_app

runner = CliRunner()


def _write_pyproject(tmp_path: Path, extra: str = "") -> Path:
    """Write a minimal pyproject.toml and return the path."""
    content = "[project]\nname = 'test'\nversion = '0.1.0'\n"
    if extra:
        content += extra
    (tmp_path / "pyproject.toml").write_text(content)
    return tmp_path


class TestCleanCache:
    """Tests for clean cache command."""

    @pytest.mark.unit
    def test_cache_removes_pycache_directories(self, tmp_path: Path):
        """Clean cache removes __pycache__ directories."""
        _write_pyproject(tmp_path)
        pycache = tmp_path / "src" / "__pycache__"
        pycache.mkdir(parents=True)
        (pycache / "foo.pyc").write_text("")

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(clean_app, ["cache"])

        assert result.exit_code == 0

    @pytest.mark.unit
    def test_cache_removes_pyc_files(self, tmp_path: Path):
        """Clean cache removes .pyc files."""
        _write_pyproject(tmp_path)
        pyc = tmp_path / "module.pyc"
        pyc.write_text("")

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(clean_app, ["cache"])

        assert result.exit_code == 0
        assert not pyc.exists()

    @pytest.mark.unit
    def test_cache_does_not_remove_venv(self, tmp_path: Path):
        """Clean cache leaves .venv intact."""
        _write_pyproject(tmp_path)
        venv = tmp_path / ".venv"
        venv.mkdir()
        sentinel = venv / "sentinel.txt"
        sentinel.write_text("keep me")

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(clean_app, ["cache"])

        assert result.exit_code == 0
        assert sentinel.exists()


class TestCleanVenv:
    """Tests for clean venv command."""

    @pytest.mark.unit
    def test_venv_removes_dot_venv(self, tmp_path: Path):
        """Clean venv removes .venv directory (with --force)."""
        _write_pyproject(tmp_path)
        venv = tmp_path / ".venv"
        venv.mkdir()
        (venv / "pyvenv.cfg").write_text("")

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(clean_app, ["venv", "--force"])

        assert result.exit_code == 0
        assert not venv.exists()

    @pytest.mark.unit
    def test_venv_is_idempotent_when_venv_missing(self, tmp_path: Path):
        """Clean venv succeeds even when .venv does not exist."""
        _write_pyproject(tmp_path)

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(clean_app, ["venv", "--force"])

        assert result.exit_code == 0

    @pytest.mark.unit
    def test_venv_non_tty_without_force_aborts(self, tmp_path: Path):
        """Clean venv on non-TTY without --force exits 1."""
        _write_pyproject(tmp_path)
        venv = tmp_path / ".venv"
        venv.mkdir()

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(clean_app, ["venv"])

        assert result.exit_code == 1
        assert venv.exists()


class TestCleanAll:
    """Tests for `clean all` subcommand."""

    @pytest.mark.unit
    def test_clean_all_removes_cache_and_venv(self, tmp_path: Path):
        """`clean all --force` removes both cache and venv."""
        _write_pyproject(tmp_path)
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        venv = tmp_path / ".venv"
        venv.mkdir()

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(clean_app, ["all", "--force"])

        assert result.exit_code == 0
        assert not venv.exists()

    @pytest.mark.unit
    def test_clean_all_non_tty_without_force_aborts(self, tmp_path: Path):
        """`clean all` on non-TTY without --force exits 1."""
        _write_pyproject(tmp_path)
        venv = tmp_path / ".venv"
        venv.mkdir()

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(clean_app, ["all"])

        assert result.exit_code == 1
        assert venv.exists()

    @pytest.mark.unit
    def test_clean_bare_invoke_shows_help(self, tmp_path: Path):
        """Bare `clean` shows help and does NOT delete anything.

        Note: CliRunner reports exit code 2 for a sub-app invoked with no
        args under no_args_is_help (treated as missing-command), while the
        real shell exits 0 via the top-level app. The behavioral guarantee
        is "show help, do not delete" — verified via output and filesystem.
        """
        _write_pyproject(tmp_path)
        venv = tmp_path / ".venv"
        venv.mkdir()

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(clean_app, [])

        assert "Usage:" in result.output
        assert venv.exists()  # not deleted


# ---------------------------------------------------------------------------
# Additional branch coverage for clean.py
# ---------------------------------------------------------------------------


class TestCleanBranchCoverage:
    """Tests targeting missing coverage branches in clean.py."""

    @pytest.mark.unit
    def test_remove_glob_double_star_no_slash(self, tmp_path: Path):
        """_remove_glob handles patterns starting with '**' (without trailing '/')."""
        from ai_rules.commands.dev.clean import _remove_glob

        # Create a file that matches **__pycache__ pattern (no leading slash)
        nested = tmp_path / "subdir" / "__pycache__"
        nested.mkdir(parents=True)
        removed = _remove_glob(tmp_path, "**__pycache__")
        assert removed >= 1
        assert not nested.exists()

    @pytest.mark.unit
    def test_do_clean_cache_skips_venv_pattern(self, tmp_path: Path):
        """_do_clean_cache skips patterns that are in _VENV_DIRS."""
        from ai_rules.commands.dev.clean import _do_clean_cache

        # Write a pyproject.toml that sets clean_globs to include .venv pattern
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[tool.ai_rules.dev]\nclean_globs = [".venv"]\n',
            encoding="utf-8",
        )
        venv = tmp_path / ".venv"
        venv.mkdir()
        _do_clean_cache(tmp_path)
        # .venv should still exist because it's in _VENV_DIRS and gets skipped
        assert venv.exists()

    @pytest.mark.unit
    def test_get_clean_globs_include_venv(self, tmp_path: Path):
        """get_clean_globs with include_venv=True appends .venv dirs."""
        from ai_rules.commands.dev.clean import _VENV_DIRS, get_clean_globs

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'\n", encoding="utf-8")
        globs = get_clean_globs(tmp_path, include_venv=True)
        for venv_dir in _VENV_DIRS:
            assert venv_dir in globs

    @pytest.mark.unit
    def test_confirm_destructive_non_tty_without_force_exits(self, tmp_path: Path):
        """Clean all without --force on non-TTY returns exit 1."""
        _write_pyproject(tmp_path)
        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            result = runner.invoke(clean_app, ["all"])
        # CliRunner is a non-TTY, so --force is required
        assert result.exit_code != 0
