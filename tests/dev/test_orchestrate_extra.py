"""Branch-coverage tests for orchestrate.py (run_validate error paths) and dev/__init__.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from ai_rules.commands.dev import dev_app

runner = CliRunner()


class TestRunValidatePreflight:
    """Tests for run_validate() preflight checks."""

    @pytest.mark.unit
    def test_validate_exits_when_uv_not_found(self, tmp_path: Path):
        """Run_validate raises when uv is not found in PATH."""
        from ai_rules.commands.dev.orchestrate import run_validate

        (tmp_path / "pyproject.toml").write_text("[project]\n")
        with patch("shutil.which", return_value=None):
            with pytest.raises(typer.Exit):
                run_validate(root=tmp_path)

    @pytest.mark.unit
    def test_validate_exits_when_pyproject_missing(self, tmp_path: Path):
        """Run_validate raises when pyproject.toml is not found."""
        from ai_rules.commands.dev.orchestrate import run_validate

        # tmp_path has no pyproject.toml
        with patch("shutil.which", return_value="/usr/bin/uv"):
            with pytest.raises(typer.Exit):
                run_validate(root=tmp_path)

    @pytest.mark.unit
    def test_dev_validate_command_calls_run_validate(self):
        """Dev validate command invokes run_validate()."""
        with patch("ai_rules.commands.dev.run_validate") as mock_rv:
            mock_rv.return_value = None
            runner.invoke(dev_app, ["validate"])
        mock_rv.assert_called_once()

    @pytest.mark.unit
    def test_dev_ci_command_calls_run_validate(self):
        """Dev ci command also invokes run_validate()."""
        with patch("ai_rules.commands.dev.run_validate") as mock_rv:
            mock_rv.return_value = None
            runner.invoke(dev_app, ["ci"])
        mock_rv.assert_called_once()
