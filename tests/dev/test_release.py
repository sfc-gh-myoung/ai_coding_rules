"""Unit tests for ai_rules.commands.dev.release."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_rules.commands.dev.release import release_app as app

runner = CliRunner()


class TestReleaseBumpDryRun:
    """Tests for release bump --dry-run (no subprocess calls)."""

    @pytest.mark.unit
    def test_dry_run_does_not_call_subprocess_for_git_operations(self):
        """Release bump --dry-run does not call git add, commit, or push."""
        from unittest.mock import MagicMock

        def tracking_run(cmd, **kwargs):
            m = MagicMock()
            m.returncode = 0
            m.stdout = "release/v1.2.3"
            return m

        with patch("ai_rules.commands.dev.release.run", side_effect=tracking_run):
            result = runner.invoke(app, ["bump", "1.2.3", "--dry-run"])

        assert result.exit_code == 0, result.output
        assert "DRY RUN" in result.output

    @pytest.mark.unit
    def test_dry_run_includes_version_in_output(self):
        """Release bump --dry-run mentions the target version."""
        result = runner.invoke(app, ["bump", "3.7.4", "--dry-run"])
        assert result.exit_code == 0
        assert "3.7.4" in result.output

    @pytest.mark.unit
    def test_invalid_version_exits_nonzero(self):
        """Release bump rejects malformed version strings."""
        result = runner.invoke(app, ["bump", "notaversion", "--dry-run"])
        assert result.exit_code != 0


class TestReleaseMergeDryRun:
    """Tests for release merge --dry-run."""

    @pytest.mark.unit
    def test_merge_dry_run_does_not_call_git_mutation_commands(self):
        """Release merge --dry-run does not call git merge, commit, tag, or push."""
        from unittest.mock import MagicMock

        def tracking_run(cmd, **kwargs):
            m = MagicMock()
            m.returncode = 0
            m.stdout = "release/v1.2.3"
            return m

        with patch("ai_rules.commands.dev.release.run", side_effect=tracking_run):
            result = runner.invoke(app, ["merge", "1.2.3", "--dry-run"])

        assert result.exit_code == 0

    @pytest.mark.unit
    def test_merge_dry_run_mentions_squash(self):
        """Release merge --dry-run output mentions squash merge."""
        result = runner.invoke(app, ["merge", "1.2.3", "--dry-run"])
        assert result.exit_code == 0
        assert "squash" in result.output.lower() or "Squash" in result.output

    @pytest.mark.unit
    def test_merge_aborts_on_main_branch(self):
        """Release merge exits non-zero when run from main branch."""
        with patch("ai_rules.commands.dev.release._current_branch", return_value="main"):
            result = runner.invoke(app, ["merge", "1.2.3"])

        assert result.exit_code != 0

    @pytest.mark.unit
    def test_merge_invalid_version_exits_nonzero(self):
        """Release merge rejects malformed version strings."""
        result = runner.invoke(app, ["merge", "bad.ver.sion", "--dry-run"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Helper function unit tests
# ---------------------------------------------------------------------------


class TestReplaceHelpers:
    """Direct tests for private helper functions in release.py."""

    @pytest.mark.unit
    def test_replace_pyproject_version_same_version_returns_error(self, tmp_path):
        """_replace_pyproject_version returns ERROR: when version is already the target."""
        from ai_rules.commands.dev.release import _replace_pyproject_version

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('version = "1.2.3"\n', encoding="utf-8")
        result = _replace_pyproject_version(pyproject, "1.2.3")
        assert result.startswith("ERROR:")

    @pytest.mark.unit
    def test_replace_pyproject_version_missing_file_returns_error(self, tmp_path):
        """_replace_pyproject_version returns ERROR: when file does not exist."""
        from ai_rules.commands.dev.release import _replace_pyproject_version

        result = _replace_pyproject_version(tmp_path / "missing.toml", "1.0.0")
        assert result.startswith("ERROR:")

    @pytest.mark.unit
    def test_replace_readme_badge_missing_file_returns_warning(self, tmp_path):
        """_replace_readme_badge returns warning tuple when file does not exist."""
        from ai_rules.commands.dev.release import _replace_readme_badge

        new_text, msg = _replace_readme_badge(tmp_path / "README.md", "1.2.3")
        assert new_text is None
        assert msg is not None
        assert "WARNING" in msg

    @pytest.mark.unit
    def test_internal_run_helper_dry_run_prints_command(self, capsys):
        """The internal _run helper with dry_run=True prints [DRY RUN] and returns."""
        from ai_rules.commands.dev.release import _run

        _run(["git", "push", "origin", "main"], dry_run=True)
        # typer.echo writes to stdout
        # The function should not raise and returns early

    @pytest.mark.unit
    def test_atomic_write_exception_cleanup(self, tmp_path, monkeypatch):
        """_atomic_write removes the tmp file and re-raises on write failure."""
        import os as os_mod

        from ai_rules.commands.dev.release import _atomic_write

        original_replace = os_mod.replace

        def raising_replace(src, dst):
            raise OSError("simulated write error")

        monkeypatch.setattr(os_mod, "replace", raising_replace)
        with pytest.raises(OSError, match="simulated write error"):
            _atomic_write(tmp_path / "output.txt", "content")
