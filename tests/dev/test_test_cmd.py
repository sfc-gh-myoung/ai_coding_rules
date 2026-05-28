"""Unit tests for ai_rules.commands.dev.test."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_rules.commands.dev.test import tests_app

runner = CliRunner()


def _make_fake_run(calls: list):
    """Return a fake run() that records calls and returns success."""

    def fake_run(argv, **kwargs):
        calls.append((list(argv), kwargs))
        return subprocess.CompletedProcess(args=argv, returncode=0, stdout="", stderr="")

    return fake_run


class TestTestRun:
    """Tests for dev test run command."""

    @pytest.mark.unit
    def test_run_invokes_pytest_without_coverage(self, tmp_path: Path):
        """Test run calls uv run pytest tests/ --tb=short by default."""
        calls: list = []

        with (
            patch("ai_rules.commands.dev.test.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.test.run", side_effect=_make_fake_run(calls)),
        ):
            result = runner.invoke(tests_app, [])

        assert result.exit_code == 0, result.output
        assert ["uv", "run", "pytest", "tests/", "--tb=short"] in [c for c, _ in calls]
        assert calls[0][1]["failure_hint"].summary == "Tests failed."
        assert "uv run ai-rules dev test run" in calls[0][1]["failure_hint"].next_steps
        assert calls[0][1]["display_command"] == [
            "uv",
            "run",
            "ai-rules",
            "dev",
            "test",
            "run",
        ]

    @pytest.mark.unit
    def test_run_with_coverage_adds_cov_flags(self, tmp_path: Path):
        """Test run --coverage adds coverage report flags."""
        calls: list = []

        with (
            patch("ai_rules.commands.dev.test.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.test.run", side_effect=_make_fake_run(calls)),
        ):
            result = runner.invoke(tests_app, ["--coverage"])

        assert result.exit_code == 0, result.output
        assert len(calls) == 1
        cmd = calls[0][0]
        assert "--cov=src/ai_rules" in cmd
        assert "--cov-report=term-missing" in cmd
        assert "--cov-report=html" in cmd
        assert calls[0][1]["failure_hint"].summary == "Tests with coverage failed."
        assert "uv run ai-rules dev test run --coverage" in calls[0][1]["failure_hint"].next_steps
        assert calls[0][1]["display_command"] == [
            "uv",
            "run",
            "ai-rules",
            "dev",
            "test",
            "run",
            "--coverage",
        ]

    @pytest.mark.unit
    def test_run_with_open_also_enables_coverage(self, tmp_path: Path):
        """Test run --open implies coverage collection."""
        calls: list = []

        with (
            patch("ai_rules.commands.dev.test.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.test.run", side_effect=_make_fake_run(calls)),
            patch("ai_rules.commands.dev.test.webbrowser.open"),
        ):
            result = runner.invoke(tests_app, ["--open"])

        assert result.exit_code == 0, result.output
        cmd = calls[0][0]
        assert "--cov=src/ai_rules" in cmd

    @pytest.mark.unit
    def test_run_without_coverage_does_not_include_cov_flags(self, tmp_path: Path):
        """Test run --no-coverage does not include --cov flags."""
        calls: list = []

        with (
            patch("ai_rules.commands.dev.test.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.test.run", side_effect=_make_fake_run(calls)),
        ):
            result = runner.invoke(tests_app, ["--no-coverage"])

        assert result.exit_code == 0, result.output
        cmd = calls[0][0]
        assert "--cov=src/ai_rules" not in cmd
