"""Unit tests for ai_rules.commands.dev.orchestrate."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from ai_rules.commands.dev.orchestrate import run_validate


def _noop_run(argv, **kwargs):
    """Fake run() that returns success."""
    return subprocess.CompletedProcess(args=argv, returncode=0, stdout="", stderr="")


def _failing_run(argv, **kwargs):
    """Fake run() that raises CalledProcessError."""
    raise subprocess.CalledProcessError(1, argv)


class TestRunValidate:
    """Tests for the run_validate() orchestration function."""

    @pytest.mark.unit
    def test_validate_calls_quality_and_tests_in_order(self, tmp_path: Path):
        """run_validate() calls quality checks, tests, and schema validation."""
        (tmp_path / "pyproject.toml").write_text(
            "[project]\nname = 'test'\nversion = '0.1'\n"
            "[tool.ai_rules.dev]\nmarkdown_rules_targets = []\nmarkdown_docs_targets = []\n"
        )
        calls: list = []

        def recording_run(argv, **kwargs):
            calls.append((list(argv), kwargs))
            return subprocess.CompletedProcess(args=argv, returncode=0, stdout="", stderr="")

        with (
            patch("ai_rules.commands.dev.quality.run", side_effect=recording_run),
            patch("ai_rules.commands.dev.orchestrate.run", side_effect=recording_run),
            patch("shutil.which", return_value="/usr/bin/uv"),
            patch(
                "ai_rules.commands.dev.orchestrate.find_project_root",
                return_value=tmp_path,
            ),
            patch(
                "ai_rules.commands.dev.quality.find_project_root",
                return_value=tmp_path,
            ),
        ):
            run_validate(tmp_path)

        commands = [c for c, _ in calls]
        tool_names = [c[0] for c in commands if c]
        assert "uv" in tool_names
        pytest_call = next(c for c in calls if "pytest" in c[0])
        assert pytest_call[1]["failure_hint"].summary == "Tests failed."

    @pytest.mark.unit
    def test_validate_exits_on_pipeline_failure(self, tmp_path: Path, capsys):
        """run_validate() raises SystemExit when a validation step fails."""
        (tmp_path / "pyproject.toml").write_text(
            "[project]\nname = 'test'\nversion = '0.1'\n"
            "[tool.ai_rules.dev]\nmarkdown_rules_targets = []\nmarkdown_docs_targets = []\n"
        )

        def failing_validate_run(argv, **kwargs):
            result = subprocess.CompletedProcess(args=argv, returncode=0, stdout="", stderr="")
            if "ai-rules" in argv:
                result = subprocess.CompletedProcess(args=argv, returncode=1, stdout="", stderr="")
            return result

        with (
            patch(
                "ai_rules.commands.dev.quality.run",
                side_effect=lambda a, **kw: subprocess.CompletedProcess(
                    args=a, returncode=0, stdout="", stderr=""
                ),
            ),
            patch(
                "ai_rules.commands.dev.orchestrate.run",
                side_effect=failing_validate_run,
            ),
            patch("shutil.which", return_value="/usr/bin/uv"),
            patch(
                "ai_rules.commands.dev.orchestrate.find_project_root",
                return_value=tmp_path,
            ),
            patch(
                "ai_rules.commands.dev.quality.find_project_root",
                return_value=tmp_path,
            ),
            pytest.raises(SystemExit),
        ):
            run_validate(tmp_path)

        captured = capsys.readouterr()
        assert "uv run ai-rules validate rules/" in captured.err
