"""CLIG.dev invariants for the ai-rules CLI surface.

These tests enforce CLI guidelines (https://clig.dev/) project-wide:
- Help-on-bare for namespace commands.
- `-h` alias parity with `--help`.
- NO_COLOR honored.
- did-you-mean suggestions remain enabled.
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app

runner = CliRunner()

NAMESPACE_PATHS: list[list[str]] = [
    [],
    ["badges"],
]


@pytest.mark.unit
@pytest.mark.parametrize("argv", NAMESPACE_PATHS)
def test_namespace_bare_invoke_shows_help(argv: list[str]) -> None:
    """Every namespace command shows help when invoked with no args."""
    result = runner.invoke(app, argv)
    assert "Usage:" in result.output, f"argv={argv}: missing 'Usage:' in output"


@pytest.mark.unit
@pytest.mark.parametrize("argv", NAMESPACE_PATHS)
def test_h_alias_matches_help(argv: list[str]) -> None:
    """`-h` is an alias for `--help` everywhere."""
    long_result = runner.invoke(app, [*argv, "--help"])
    short_result = runner.invoke(app, [*argv, "-h"])
    assert long_result.exit_code == 0, f"--help failed for {argv}"
    assert short_result.exit_code == 0, f"-h failed for {argv}"
    assert long_result.output.strip() == short_result.output.strip(), (
        f"-h diverged from --help for argv={argv}"
    )


@pytest.mark.unit
def test_no_color_helper_respects_env(monkeypatch) -> None:
    """NO_COLOR env var disables color via the shared helper."""
    from ai_rules._shared import console as console_mod

    monkeypatch.setenv("NO_COLOR", "1")
    assert console_mod._should_use_color() is False


@pytest.mark.unit
def test_did_you_mean_suggestion_active() -> None:
    """Click's did-you-mean suggestion still works after context_settings change."""
    result = runner.invoke(app, ["validatte"])
    assert "Did you mean" in result.output, (
        "did-you-mean suggestion missing; context_settings may have broken it"
    )
