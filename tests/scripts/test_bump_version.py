"""Tests for the inlined version-bump helpers in ai_rules.commands.dev.release."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
import typer

from ai_rules.commands.dev import release as release_module

_bump_version_files = release_module._bump_version_files


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Callable[[str, str], Path]:
    """Create a fake project tree in tmp_path and chdir there."""

    def _make(pyproject_body: str, readme_body: str) -> Path:
        (tmp_path / "pyproject.toml").write_text(pyproject_body, encoding="utf-8")
        (tmp_path / "README.md").write_text(readme_body, encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        return tmp_path

    return _make


PYPROJECT_VALID = '[project]\nname = "demo"\nversion = "1.0.0"\nrequires-python = ">=3.12"\n'
README_WITH_BADGE = "# Demo\n\n![Version](https://img.shields.io/badge/version-1.0.0-blue)\n"
README_NO_BADGE = "# Demo\n\nNo badge here.\n"


def test_valid_semver_updates_both_files(project):
    """Valid semver updates both pyproject.toml and the README badge."""
    root = project(PYPROJECT_VALID, README_WITH_BADGE)
    _bump_version_files("2.3.4", cwd=root)
    assert 'version = "2.3.4"' in (root / "pyproject.toml").read_text()
    assert "badge/version-2.3.4" in (root / "README.md").read_text()


def test_pre_release_version_accepted(project):
    """Pre-release suffixes such as -rc1 are accepted by the file writer."""
    root = project(PYPROJECT_VALID, README_WITH_BADGE)
    _bump_version_files("3.8.0-rc1", cwd=root)
    assert 'version = "3.8.0-rc1"' in (root / "pyproject.toml").read_text()
    assert "badge/version-3.8.0-rc1" in (root / "README.md").read_text()


def test_missing_readme_badge_succeeds_with_warning(project, capsys):
    """Missing README badge logs a warning but still updates pyproject."""
    root = project(PYPROJECT_VALID, README_NO_BADGE)
    _bump_version_files("2.0.0", cwd=root)
    assert 'version = "2.0.0"' in (root / "pyproject.toml").read_text()
    assert (root / "README.md").read_text() == README_NO_BADGE
    captured = capsys.readouterr()
    assert "no version badge" in captured.err or "no version badge" in captured.out


def test_multiple_pyproject_versions_raises(project, capsys):
    """More than one version line in pyproject.toml is ambiguous; raise typer.Exit(1)."""
    bad = '[project]\nname = "demo"\nversion = "1.0.0"\n[tool.other]\nversion = "9.9.9"\n'
    root = project(bad, README_WITH_BADGE)
    pyproject_before = (root / "pyproject.toml").read_text()
    readme_before = (root / "README.md").read_text()
    with pytest.raises(typer.Exit):
        _bump_version_files("2.0.0", cwd=root)
    assert (root / "pyproject.toml").read_text() == pyproject_before
    assert (root / "README.md").read_text() == readme_before


def test_missing_pyproject_raises(tmp_path, monkeypatch):
    """Missing pyproject.toml is reported as an error and raises typer.Exit(1)."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(typer.Exit):
        _bump_version_files("1.2.3", cwd=tmp_path)


def test_readme_with_two_badges_raises(project):
    """Two badge tokens in README are ambiguous; bail out without changes."""
    bad_readme = README_WITH_BADGE + "Second badge: badge/version-1.0.0\n"
    root = project(PYPROJECT_VALID, bad_readme)
    pyproject_before = (root / "pyproject.toml").read_text()
    readme_before = (root / "README.md").read_text()
    with pytest.raises(typer.Exit):
        _bump_version_files("2.0.0", cwd=root)
    assert (root / "pyproject.toml").read_text() == pyproject_before
    assert (root / "README.md").read_text() == readme_before
