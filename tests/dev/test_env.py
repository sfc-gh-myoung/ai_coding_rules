"""Unit tests for ai_rules.commands.dev.env."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_rules.commands.dev.env import env_app

runner = CliRunner()


class TestEnvSetup:
    """Tests for env setup command."""

    @pytest.mark.unit
    def test_setup_calls_uv_commands_in_order(self):
        """Env setup runs uv python install, pin, and venv in order."""
        calls = []

        def fake_run(argv, **kwargs):
            import subprocess

            calls.append((argv, kwargs))
            return subprocess.CompletedProcess(args=argv, returncode=0, stdout="", stderr="")

        with patch("ai_rules.commands.dev.env.run", side_effect=fake_run):
            result = runner.invoke(env_app, ["setup"])

        assert result.exit_code == 0
        assert [c for c, _ in calls] == [
            ["uv", "python", "install", "3.11"],
            ["uv", "python", "pin", "3.11"],
            ["uv", "venv"],
        ]
        assert all(
            kwargs["failure_hint"].summary == "Environment setup failed." for _, kwargs in calls
        )
        assert all(
            "uv run ai-rules dev status preflight" in kwargs["failure_hint"].next_steps
            for _, kwargs in calls
        )
        assert all(
            kwargs["display_command"] == ["uv", "run", "ai-rules", "dev", "env", "setup"]
            for _, kwargs in calls
        )

    @pytest.mark.unit
    def test_setup_exits_on_runner_failure(self):
        """Env setup propagates friendly runner exits."""
        import typer

        with patch("ai_rules.commands.dev.env.run", side_effect=typer.Exit(1)):
            result = runner.invoke(env_app, ["setup"])

        assert result.exit_code == 1


class TestEnvSync:
    """Tests for env sync command."""

    @pytest.mark.unit
    def test_sync_calls_uv_sync(self):
        """Env sync calls uv sync --all-groups."""
        calls = []

        def fake_run(argv, **kwargs):
            import subprocess

            calls.append((argv, kwargs))
            return subprocess.CompletedProcess(args=argv, returncode=0, stdout="", stderr="")

        with patch("ai_rules.commands.dev.env.run", side_effect=fake_run):
            result = runner.invoke(env_app, ["sync"])

        assert result.exit_code == 0
        assert [c for c, _ in calls] == [["uv", "sync", "--all-groups"]]
        assert calls[0][1]["failure_hint"].summary == "Dependency sync failed."
        assert "uv run ai-rules dev env sync" in calls[0][1]["failure_hint"].next_steps
        assert calls[0][1]["display_command"] == [
            "uv",
            "run",
            "ai-rules",
            "dev",
            "env",
            "sync",
        ]


class TestEnvLock:
    """Tests for env lock command."""

    @pytest.mark.unit
    def test_lock_calls_uv_lock_then_sync(self):
        """Env lock calls uv lock followed by uv sync --all-groups."""
        calls = []

        def fake_run(argv, **kwargs):
            import subprocess

            calls.append((argv, kwargs))
            return subprocess.CompletedProcess(args=argv, returncode=0, stdout="", stderr="")

        with patch("ai_rules.commands.dev.env.run", side_effect=fake_run):
            result = runner.invoke(env_app, ["lock"])

        assert result.exit_code == 0
        assert [c for c, _ in calls] == [
            ["uv", "lock"],
            ["uv", "sync", "--all-groups"],
        ]
        assert calls[0][1]["failure_hint"].summary == "Dependency lock failed."
        assert calls[1][1]["failure_hint"].summary == "Dependency sync failed."
        assert "uv run ai-rules dev env lock" in calls[0][1]["failure_hint"].next_steps
        assert "uv run ai-rules dev env sync" in calls[1][1]["failure_hint"].next_steps
        assert calls[0][1]["display_command"] == [
            "uv",
            "run",
            "ai-rules",
            "dev",
            "env",
            "lock",
        ]
        assert calls[1][1]["display_command"] == [
            "uv",
            "run",
            "ai-rules",
            "dev",
            "env",
            "sync",
        ]
