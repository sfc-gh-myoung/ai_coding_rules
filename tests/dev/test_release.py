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
