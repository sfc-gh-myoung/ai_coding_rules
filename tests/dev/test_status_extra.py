"""Branch-coverage tests for status.py and dev __init__.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_rules.commands.dev.status import status_app

runner = CliRunner()


class TestRunVersionException:
    """Tests for _run_version exception paths."""

    @pytest.mark.unit
    def test_run_version_returns_not_found_for_missing_cmd(self):
        """_run_version returns 'not found' when command raises FileNotFoundError."""
        from ai_rules.commands.dev.status import _run_version

        result = _run_version(["nonexistent_command_xyz_abc"])
        assert result == "not found"


class TestPreflightNoPyproject:
    """Tests for preflight command when pyproject.toml is missing."""

    @pytest.mark.unit
    def test_preflight_exits_nonzero_without_pyproject(self, tmp_path: Path):
        """Preflight returns non-zero when pyproject.toml is absent."""
        with patch("ai_rules.commands.dev.status.find_project_root", return_value=tmp_path):
            with patch("shutil.which", return_value="/usr/bin/uv"):
                result = runner.invoke(status_app, ["preflight"])
        assert result.exit_code != 0

    @pytest.mark.unit
    def test_preflight_exits_nonzero_without_uv(self, tmp_path: Path):
        """Preflight returns non-zero when uv is not found."""
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        with patch("ai_rules.commands.dev.status.find_project_root", return_value=tmp_path):
            with patch("shutil.which", return_value=None):
                result = runner.invoke(status_app, ["preflight"])
        assert result.exit_code != 0


class TestConfirmDestructiveTTYDecline:
    """Test _confirm_destructive when stdin is TTY but user declines."""

    @pytest.mark.unit
    def test_confirm_destructive_user_declines_raises_exit(self):
        """_confirm_destructive raises when stdin is TTY and user declines."""
        import typer

        from ai_rules.commands.dev.clean import _confirm_destructive

        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            with patch("typer.confirm", return_value=False):
                with pytest.raises(typer.Exit):
                    _confirm_destructive("delete everything", force=False)
