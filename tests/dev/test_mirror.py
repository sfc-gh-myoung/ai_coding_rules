"""Unit/integration tests for commands/dev/mirror.py — dry-run paths and helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_rules.commands.dev.mirror import (
    _assert_clean_working_tree,
    _project_version,
    _run,
    mirror_app,
)

_PROJECT_ROOT = Path(__file__).parent.parent.parent

runner = CliRunner()


# ---------------------------------------------------------------------------
# _run (dry-run path)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_run_dry_run_echoes_command(capsys: pytest.CaptureFixture) -> None:
    """_run with dry_run=True prints '[DRY RUN] <cmd>' without executing."""
    _run(["git", "status"], dry_run=True)
    captured = capsys.readouterr()
    assert "[DRY RUN]" in captured.out
    assert "git status" in captured.out


@pytest.mark.unit
def test_run_dry_run_does_not_invoke_runner() -> None:
    """_run with dry_run=True never calls the real run() helper."""
    with patch("ai_rules.commands.dev.mirror.run") as mock_run:
        _run(["git", "push", "origin", "main"], dry_run=True)
        mock_run.assert_not_called()


# ---------------------------------------------------------------------------
# _assert_clean_working_tree
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_assert_clean_working_tree_dry_run_skips_git_check() -> None:
    """In dry-run mode the git diff check is bypassed entirely."""
    with patch("ai_rules.commands.dev.mirror.run") as mock_run:
        _assert_clean_working_tree(dry_run=True)
        mock_run.assert_not_called()


# ---------------------------------------------------------------------------
# _project_version
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_project_version_reads_real_pyproject_toml(monkeypatch: pytest.MonkeyPatch) -> None:
    """Returns a non-'unknown' version string from the project's pyproject.toml."""
    monkeypatch.chdir(_PROJECT_ROOT)
    version = _project_version()
    assert isinstance(version, str)
    assert version != "unknown"


@pytest.mark.unit
def test_project_version_returns_unknown_when_file_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Returns 'unknown' when pyproject.toml is absent from the CWD."""
    monkeypatch.chdir(tmp_path)
    assert _project_version() == "unknown"


# ---------------------------------------------------------------------------
# mirror sync --dry-run via CliRunner
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_mirror_sync_dry_run_exits_zero() -> None:
    # mirror_app has a single command; invoke without the subcommand name.
    result = runner.invoke(mirror_app, ["--dry-run"])
    assert result.exit_code == 0


@pytest.mark.integration
def test_mirror_sync_dry_run_output_contains_dry_run_header() -> None:
    result = runner.invoke(mirror_app, ["--dry-run"])
    assert "DRY RUN" in result.output


@pytest.mark.integration
def test_mirror_sync_dry_run_output_describes_steps() -> None:
    result = runner.invoke(mirror_app, ["--dry-run"])
    assert "orphan" in result.output.lower()
    assert "gitlab" in result.output.lower()
