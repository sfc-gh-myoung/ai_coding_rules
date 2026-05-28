"""Unit tests for ai_rules.commands.dev.quality."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_rules.commands.dev.quality import quality_app

runner = CliRunner()


def _make_fake_run(calls: list):
    """Return a fake run() that records calls and returns success."""

    def fake_run(argv, **kwargs):
        calls.append((list(argv), kwargs))
        return subprocess.CompletedProcess(args=argv, returncode=0, stdout="", stderr="")

    return fake_run


class TestQualityAll:
    """Tests for the `all` subcommand (run all checks)."""

    @pytest.mark.unit
    def test_quality_all_runs_four_checks(self, tmp_path: Path):
        """`quality all` runs lint, format, typecheck, markdown."""
        calls: list = []

        (tmp_path / "pyproject.toml").write_text(
            "[tool.ai_rules.dev]\nmarkdown_rules_targets = []\nmarkdown_docs_targets = []\n"
        )

        with (
            patch("ai_rules.commands.dev.quality.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.quality.run", side_effect=_make_fake_run(calls)),
        ):
            result = runner.invoke(quality_app, ["all"])

        assert result.exit_code == 0
        commands = [c for c, _ in calls]
        assert any("ruff" in c and "check" in c for c in commands)
        assert any("ruff" in c and "format" in c for c in commands)
        assert any("ty" in c for c in commands)

    @pytest.mark.unit
    def test_quality_all_fix_passes_fix_flag(self, tmp_path: Path):
        """`quality all --fix` passes --fix to ruff check and omits --check from ruff format."""
        calls: list = []

        (tmp_path / "pyproject.toml").write_text(
            "[tool.ai_rules.dev]\nmarkdown_rules_targets = []\nmarkdown_docs_targets = []\n"
        )

        with (
            patch("ai_rules.commands.dev.quality.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.quality.run", side_effect=_make_fake_run(calls)),
        ):
            result = runner.invoke(quality_app, ["all", "--fix"])

        assert result.exit_code == 0
        commands = [c for c, _ in calls]
        lint_call = next(c for c in commands if "ruff" in c and "check" in c)
        assert "--fix" in lint_call
        format_call = next(c for c in commands if "ruff" in c and "format" in c)
        assert "--check" not in format_call

    @pytest.mark.unit
    def test_quality_no_args_shows_help(self):
        """`quality` with no subcommand exits with help (does NOT run checks)."""
        result = runner.invoke(quality_app, [])
        # no_args_is_help=True returns exit code 2 (Click missing command)
        assert result.exit_code != 0
        assert "Usage:" in result.output
        assert "all" in result.output


class TestQualityLint:
    """Tests for quality lint subcommand."""

    @pytest.mark.unit
    def test_lint_calls_ruff_check(self, tmp_path: Path):
        """Quality lint runs ruff check ."""
        calls: list = []

        with (
            patch("ai_rules.commands.dev.quality.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.quality.run", side_effect=_make_fake_run(calls)),
        ):
            result = runner.invoke(quality_app, ["lint"])

        assert result.exit_code == 0
        assert ["uv", "run", "ruff", "check", "."] in [c for c, _ in calls]
        kwargs = calls[0][1]
        hint = kwargs["failure_hint"]
        assert hint.summary == "Lint failed."
        assert "uv run ai-rules dev quality lint --fix" in hint.next_steps
        assert kwargs["display_command"] == [
            "uv",
            "run",
            "ai-rules",
            "dev",
            "quality",
            "lint",
        ]

    @pytest.mark.unit
    def test_lint_fix_adds_fix_flag(self, tmp_path: Path):
        """Quality lint --fix adds --fix to ruff check."""
        calls: list = []

        with (
            patch("ai_rules.commands.dev.quality.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.quality.run", side_effect=_make_fake_run(calls)),
        ):
            result = runner.invoke(quality_app, ["lint", "--fix"])

        assert result.exit_code == 0
        assert ["uv", "run", "ruff", "check", "--fix", "."] in [c for c, _ in calls]
        kwargs = calls[0][1]
        hint = kwargs["failure_hint"]
        assert hint.summary == "Lint auto-fix failed."
        assert "uv run ai-rules dev quality lint" in hint.next_steps
        assert kwargs["display_command"] == [
            "uv",
            "run",
            "ai-rules",
            "dev",
            "quality",
            "lint",
            "--fix",
        ]


class TestQualityFormat:
    """Tests for quality format subcommand."""

    @pytest.mark.unit
    def test_format_uses_check_flag_by_default(self, tmp_path: Path):
        """Quality format runs ruff format --check ."""
        calls: list = []

        with (
            patch("ai_rules.commands.dev.quality.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.quality.run", side_effect=_make_fake_run(calls)),
        ):
            result = runner.invoke(quality_app, ["format"])

        assert result.exit_code == 0
        assert ["uv", "run", "ruff", "format", "--check", "."] in [c for c, _ in calls]
        kwargs = calls[0][1]
        hint = kwargs["failure_hint"]
        assert hint.summary == "Format check failed: Ruff found files that need formatting."
        assert "uv run ai-rules dev quality format --fix" in hint.next_steps
        assert kwargs["display_command"] == [
            "uv",
            "run",
            "ai-rules",
            "dev",
            "quality",
            "format",
        ]

    @pytest.mark.unit
    def test_format_fix_omits_check_flag(self, tmp_path: Path):
        """Quality format --fix omits --check."""
        calls: list = []

        with (
            patch("ai_rules.commands.dev.quality.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.quality.run", side_effect=_make_fake_run(calls)),
        ):
            result = runner.invoke(quality_app, ["format", "--fix"])

        assert result.exit_code == 0
        commands = [c for c, _ in calls]
        format_call = next(c for c in commands if "ruff" in c and "format" in c)
        assert "--check" not in format_call
        kwargs = calls[0][1]
        hint = kwargs["failure_hint"]
        assert hint.summary == "Format failed."
        assert "uv run ai-rules dev quality format" in hint.next_steps
        assert kwargs["display_command"] == [
            "uv",
            "run",
            "ai-rules",
            "dev",
            "quality",
            "format",
            "--fix",
        ]


class TestQualityTypecheck:
    """Tests for quality typecheck subcommand."""

    @pytest.mark.unit
    def test_typecheck_calls_ty(self, tmp_path: Path):
        """Quality typecheck runs ty check ."""
        calls: list = []

        with (
            patch("ai_rules.commands.dev.quality.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.quality.run", side_effect=_make_fake_run(calls)),
        ):
            result = runner.invoke(quality_app, ["typecheck"])

        assert result.exit_code == 0
        assert ["uv", "run", "ty", "check", "."] in [c for c, _ in calls]
        kwargs = calls[0][1]
        hint = kwargs["failure_hint"]
        assert hint.summary == "Type check failed."
        assert "uv run ai-rules dev quality typecheck" in hint.next_steps
        assert kwargs["display_command"] == [
            "uv",
            "run",
            "ai-rules",
            "dev",
            "quality",
            "typecheck",
        ]


class TestQualityMarkdown:
    """Tests for quality markdown subcommand."""

    @pytest.mark.unit
    def test_markdown_skips_empty_targets(self, tmp_path: Path):
        """Quality markdown does not run pymarkdownlnt when targets are empty."""
        calls: list = []

        (tmp_path / "pyproject.toml").write_text(
            "[tool.ai_rules.dev]\nmarkdown_rules_targets = []\nmarkdown_docs_targets = []\n"
        )

        with (
            patch("ai_rules.commands.dev.quality.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.quality.run", side_effect=_make_fake_run(calls)),
        ):
            result = runner.invoke(quality_app, ["markdown"])

        assert result.exit_code == 0
        assert not any("pymarkdownlnt" in str(c) for c, _ in calls)

    @pytest.mark.unit
    def test_markdown_runs_scan_on_rules_targets(self, tmp_path: Path):
        """Quality markdown runs pymarkdownlnt scan on configured rules targets."""
        calls: list = []

        (tmp_path / "pyproject.toml").write_text(
            '[tool.ai_rules.dev]\nmarkdown_rules_targets = ["rules/"]\nmarkdown_docs_targets = []\n'
        )

        with (
            patch("ai_rules.commands.dev.quality.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.quality.run", side_effect=_make_fake_run(calls)),
        ):
            result = runner.invoke(quality_app, ["markdown"])

        assert result.exit_code == 0
        md_calls = [(c, kwargs) for c, kwargs in calls if "pymarkdownlnt" in str(c)]
        assert len(md_calls) == 1
        assert "scan" in md_calls[0][0]
        assert "rules/" in md_calls[0][0]
        assert md_calls[0][1]["failure_hint"].summary == "Markdown check failed."
        assert (
            "uv run ai-rules dev quality markdown --fix"
            in md_calls[0][1]["failure_hint"].next_steps
        )
        assert md_calls[0][1]["display_command"] == [
            "uv",
            "run",
            "ai-rules",
            "dev",
            "quality",
            "markdown",
        ]

    @pytest.mark.unit
    def test_markdown_fix_uses_fix_verb(self, tmp_path: Path):
        """Quality markdown --fix uses 'fix' verb instead of 'scan'."""
        calls: list = []

        (tmp_path / "pyproject.toml").write_text(
            '[tool.ai_rules.dev]\nmarkdown_rules_targets = ["rules/"]\nmarkdown_docs_targets = []\n'
        )

        with (
            patch("ai_rules.commands.dev.quality.find_project_root", return_value=tmp_path),
            patch("ai_rules.commands.dev.quality.run", side_effect=_make_fake_run(calls)),
        ):
            result = runner.invoke(quality_app, ["markdown", "--fix"])

        assert result.exit_code == 0
        md_calls = [(c, kwargs) for c, kwargs in calls if "pymarkdownlnt" in str(c)]
        assert "fix" in md_calls[0][0]
        assert "scan" not in md_calls[0][0]
        assert md_calls[0][1]["failure_hint"].summary == "Markdown auto-fix failed."
        assert "uv run ai-rules dev quality markdown" in md_calls[0][1]["failure_hint"].next_steps
        assert md_calls[0][1]["display_command"] == [
            "uv",
            "run",
            "ai-rules",
            "dev",
            "quality",
            "markdown",
            "--fix",
        ]
