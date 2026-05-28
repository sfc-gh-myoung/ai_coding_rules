"""Unit tests for ai_rules._shared.runner."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from ai_rules._shared.runner import CommandFailureHint, run
from ai_rules._shared.runtime import set_debug


@pytest.fixture(autouse=True)
def reset_debug_flag():
    """Reset process-global debug state around each test."""
    set_debug(False)
    yield
    set_debug(False)


class TestRunnerRun:
    """Tests for the run() subprocess wrapper."""

    @pytest.mark.unit
    def test_resolves_binary_and_calls_subprocess(self, tmp_path: Path):
        """run() resolves the binary with shutil.which and calls subprocess.run."""
        with (
            patch(
                "ai_rules._shared.runner.shutil.which", return_value="/usr/bin/echo"
            ) as mock_which,
            patch("ai_rules._shared.runner.subprocess.run") as mock_run,
        ):
            mock_run.return_value = subprocess.CompletedProcess(
                args=["/usr/bin/echo", "hello"], returncode=0, stdout="", stderr=""
            )
            run(["echo", "hello"])

        mock_which.assert_called_once_with("echo")
        called_args = mock_run.call_args[1]["args"]
        assert called_args[0] == "/usr/bin/echo"
        assert called_args[1] == "hello"
        assert mock_run.call_args[1]["check"] is False

    @pytest.mark.unit
    def test_friendly_missing_binary_exits_when_debug_disabled(self, capsys):
        """run() emits a friendly missing-binary message by default."""
        with (
            patch("ai_rules._shared.runner.shutil.which", return_value=None),
            pytest.raises(typer.Exit) as exc_info,
        ):
            run(["no-such-binary"])

        assert exc_info.value.exit_code == 127
        captured = capsys.readouterr()
        assert "Command not found: no-such-binary" in captured.err
        assert "Install no-such-binary or add it to PATH." in captured.err
        assert "--debug" in captured.err

    @pytest.mark.unit
    def test_debug_missing_binary_raises_file_not_found(self):
        """run() raises FileNotFoundError for missing binaries when debug is enabled."""
        set_debug(True)
        with (
            patch("ai_rules._shared.runner.shutil.which", return_value=None),
            pytest.raises(FileNotFoundError, match="no-such-binary"),
        ):
            run(["no-such-binary"])

    @pytest.mark.unit
    def test_friendly_false_missing_binary_raises_file_not_found(self):
        """run(friendly=False) preserves raw FileNotFoundError behavior."""
        with (
            patch("ai_rules._shared.runner.shutil.which", return_value=None),
            pytest.raises(FileNotFoundError, match="no-such-binary"),
        ):
            run(["no-such-binary"], friendly=False)

    @pytest.mark.unit
    def test_raises_value_error_on_empty_argv(self):
        """run() raises ValueError for empty argv."""
        with pytest.raises(ValueError, match="argv must be non-empty"):
            run([])

    @pytest.mark.unit
    def test_capture_true_uses_capture_output(self):
        """run() passes capture_output=True when capture=True."""
        with (
            patch("ai_rules._shared.runner.shutil.which", return_value="/usr/bin/uv"),
            patch("ai_rules._shared.runner.subprocess.run") as mock_run,
        ):
            mock_run.return_value = subprocess.CompletedProcess(
                args=["/usr/bin/uv", "version"], returncode=0, stdout="uv 0.5.0", stderr=""
            )
            run(["uv", "version"], capture=True)

        kwargs = mock_run.call_args[1]
        assert kwargs.get("capture_output") is True
        assert "stdout" not in kwargs or kwargs.get("stdout") is None

    @pytest.mark.unit
    def test_shell_is_always_false(self):
        """run() never passes shell=True."""
        with (
            patch("ai_rules._shared.runner.shutil.which", return_value="/usr/bin/echo"),
            patch("ai_rules._shared.runner.subprocess.run") as mock_run,
        ):
            mock_run.return_value = subprocess.CompletedProcess(
                args=["/usr/bin/echo"], returncode=0, stdout="", stderr=""
            )
            run(["echo"])

        kwargs = mock_run.call_args[1]
        assert kwargs.get("shell") is False

    @pytest.mark.unit
    def test_custom_cwd_is_forwarded(self, tmp_path: Path):
        """run() passes the cwd parameter to subprocess.run."""
        with (
            patch("ai_rules._shared.runner.shutil.which", return_value="/usr/bin/echo"),
            patch("ai_rules._shared.runner.subprocess.run") as mock_run,
        ):
            mock_run.return_value = subprocess.CompletedProcess(
                args=["/usr/bin/echo"], returncode=0, stdout="", stderr=""
            )
            run(["echo"], cwd=tmp_path)

        kwargs = mock_run.call_args[1]
        assert kwargs.get("cwd") == tmp_path

    @pytest.mark.unit
    def test_check_false_does_not_raise_on_nonzero(self):
        """run(check=False) returns the result even on non-zero exit."""
        with (
            patch("ai_rules._shared.runner.shutil.which", return_value="/usr/bin/false"),
            patch("ai_rules._shared.runner.subprocess.run") as mock_run,
        ):
            mock_run.return_value = subprocess.CompletedProcess(
                args=["/usr/bin/false"], returncode=1, stdout="", stderr=""
            )
            result = run(["false"], check=False)

        assert result.returncode == 1

    @pytest.mark.unit
    def test_nonzero_exit_prints_friendly_hint(self, capsys):
        """run() converts non-zero exits into concise friendly errors."""
        with (
            patch("ai_rules._shared.runner.shutil.which", return_value="/usr/bin/false"),
            patch("ai_rules._shared.runner.subprocess.run") as mock_run,
            pytest.raises(typer.Exit) as exc_info,
        ):
            mock_run.return_value = subprocess.CompletedProcess(
                args=["/usr/bin/false"], returncode=2, stdout="", stderr=""
            )
            run(
                ["false"],
                failure_hint=CommandFailureHint(
                    summary="Example command failed.",
                    next_steps=("Run the fix command.",),
                    details="Extra context.",
                ),
            )

        assert exc_info.value.exit_code == 2
        captured = capsys.readouterr()
        assert "Example command failed." in captured.err
        assert "Command:" in captured.err
        assert "false" in captured.err
        assert "Extra context." in captured.err
        assert "Run the fix command." in captured.err
        assert "--debug" in captured.err

    @pytest.mark.unit
    def test_debug_nonzero_exit_raises_called_process_error(self):
        """run() preserves CalledProcessError diagnostics when debug is enabled."""
        set_debug(True)
        with (
            patch("ai_rules._shared.runner.shutil.which", return_value="/usr/bin/false"),
            patch("ai_rules._shared.runner.subprocess.run") as mock_run,
            pytest.raises(subprocess.CalledProcessError) as exc_info,
        ):
            mock_run.return_value = subprocess.CompletedProcess(
                args=["/usr/bin/false"], returncode=3, stdout="out", stderr="err"
            )
            run(["false"])

        assert exc_info.value.returncode == 3
        assert exc_info.value.output == "out"
        assert exc_info.value.stderr == "err"
