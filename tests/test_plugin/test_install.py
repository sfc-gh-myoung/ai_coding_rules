"""Tests for plugin install and uninstall commands."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_rules.commands.plugin import (
    _PLUGIN_NAME,
    TargetPlatform,
    _global_dest,
    _is_our_plugin,
    _project_dest,
    plugin_app,
)

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_DIR = REPO_ROOT / "ai-coding-rules-plugin"


@pytest.fixture()
def built_plugin(tmp_path: Path) -> Path:
    """Build a minimal valid plugin for testing."""
    out = tmp_path / "plugin"
    result = runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)])
    assert result.exit_code == 0, f"build failed: {result.output}"
    return out


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------


class TestGlobalDest:
    def test_cortex(self) -> None:
        dest = _global_dest(TargetPlatform.cortex)
        assert dest == Path.home() / ".snowflake" / "cortex" / "plugins" / _PLUGIN_NAME

    def test_claude(self) -> None:
        dest = _global_dest(TargetPlatform.claude)
        assert dest == Path.home() / ".claude" / "skills" / _PLUGIN_NAME


class TestProjectDest:
    def test_cortex(self, tmp_path: Path) -> None:
        dest = _project_dest(TargetPlatform.cortex, tmp_path)
        assert dest == tmp_path / ".cortex" / "plugins" / _PLUGIN_NAME

    def test_claude(self, tmp_path: Path) -> None:
        dest = _project_dest(TargetPlatform.claude, tmp_path)
        assert dest == tmp_path / ".claude" / "plugins" / _PLUGIN_NAME


class TestIsOurPlugin:
    def test_valid_plugin(self, tmp_path: Path) -> None:
        manifest_dir = tmp_path / ".cortex-plugin"
        manifest_dir.mkdir()
        (manifest_dir / "plugin.json").write_text(
            json.dumps({"name": _PLUGIN_NAME}), encoding="utf-8"
        )
        assert _is_our_plugin(tmp_path) is True

    def test_valid_claude_plugin(self, tmp_path: Path) -> None:
        """A claude install carries only .claude-plugin/, which must also pass."""
        manifest_dir = tmp_path / ".claude-plugin"
        manifest_dir.mkdir()
        (manifest_dir / "plugin.json").write_text(
            json.dumps({"name": _PLUGIN_NAME}), encoding="utf-8"
        )
        assert _is_our_plugin(tmp_path) is True

    def test_wrong_name(self, tmp_path: Path) -> None:
        manifest_dir = tmp_path / ".cortex-plugin"
        manifest_dir.mkdir()
        (manifest_dir / "plugin.json").write_text(
            json.dumps({"name": "other-plugin"}), encoding="utf-8"
        )
        assert _is_our_plugin(tmp_path) is False

    def test_missing_manifest(self, tmp_path: Path) -> None:
        assert _is_our_plugin(tmp_path) is False


# ---------------------------------------------------------------------------
# Install command tests
# ---------------------------------------------------------------------------


def test_install_help_documents_hook_and_cortex_install_path() -> None:
    result = runner.invoke(plugin_app, ["install", "--help"])

    assert result.exit_code == 0
    assert "--with-hook" in result.output
    assert "Hooks are omitted by default" in result.output
    assert "UserPromptSubmit" in result.output
    assert "cortex plugin install" in result.output


class TestInstallProjectLocal:
    def test_install_cortex(self, built_plugin: Path, tmp_path: Path) -> None:
        project = tmp_path / "my-project"
        project.mkdir()
        result = runner.invoke(
            plugin_app,
            [
                "install",
                "--target",
                "cortex",
                "--project",
                str(project),
                "--plugin-dir",
                str(built_plugin),
            ],
        )
        assert result.exit_code == 0
        dest = project / ".cortex" / "plugins" / _PLUGIN_NAME
        assert (dest / ".cortex-plugin" / "plugin.json").is_file()
        # Only the target platform's manifest ships
        assert not (dest / ".claude-plugin").exists()
        # Hook excluded by default
        assert not (dest / "hooks").exists()
        assert "Use --with-hook to enable the plugin hook" in result.output
        manifest = json.loads((dest / ".cortex-plugin" / "plugin.json").read_text())
        assert "hooks" not in manifest

    def test_install_claude(self, built_plugin: Path, tmp_path: Path) -> None:
        project = tmp_path / "my-project"
        project.mkdir()
        result = runner.invoke(
            plugin_app,
            [
                "install",
                "--target",
                "claude",
                "--project",
                str(project),
                "--plugin-dir",
                str(built_plugin),
            ],
        )
        assert result.exit_code == 0
        dest = project / ".claude" / "plugins" / _PLUGIN_NAME
        # Claude Code only reads .claude-plugin/plugin.json; the cortex manifest
        # must not ship with a claude install.
        assert (dest / ".claude-plugin" / "plugin.json").is_file()
        assert not (dest / ".cortex-plugin").exists()
        assert not (dest / "hooks").exists()

    def test_with_hook_includes_hooks(self, built_plugin: Path, tmp_path: Path) -> None:
        project = tmp_path / "my-project"
        project.mkdir()
        result = runner.invoke(
            plugin_app,
            [
                "install",
                "--target",
                "cortex",
                "--project",
                str(project),
                "--plugin-dir",
                str(built_plugin),
                "--with-hook",
            ],
        )
        assert result.exit_code == 0
        dest = project / ".cortex" / "plugins" / _PLUGIN_NAME
        assert (dest / "hooks" / "user-prompt-submit").is_file()
        # hooks/hooks.json is the single declaration and must survive the install.
        # It was previously deleted here in favour of an inline manifest key, which
        # is what made Desktop (inline) and CLI (hooks.json) disagree.
        hooks_file = dest / "hooks" / "hooks.json"
        assert hooks_file.is_file()
        manifest = json.loads((dest / ".cortex-plugin" / "plugin.json").read_text())
        assert "hooks" not in manifest, "hooks must not be declared inline"
        # No per-platform rewrite: every supported host substitutes the variable.
        hooks = json.loads(hooks_file.read_text())
        command = hooks["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
        assert command == "${CLAUDE_PLUGIN_ROOT}/hooks/user-prompt-submit"

    def test_with_hook_claude_uses_plugin_root_var(
        self, built_plugin: Path, tmp_path: Path
    ) -> None:
        project = tmp_path / "my-project"
        project.mkdir()
        result = runner.invoke(
            plugin_app,
            [
                "install",
                "--target",
                "claude",
                "--project",
                str(project),
                "--plugin-dir",
                str(built_plugin),
                "--with-hook",
            ],
        )
        assert result.exit_code == 0
        dest = project / ".claude" / "plugins" / _PLUGIN_NAME
        assert (dest / "hooks" / "user-prompt-submit").is_file()
        # Same hook layout as the cortex target: hooks are platform-neutral
        # because Claude Code substitutes ${CLAUDE_PLUGIN_ROOT} just as CoCo does.
        hooks_file = dest / "hooks" / "hooks.json"
        assert hooks_file.is_file()
        manifest = json.loads((dest / ".claude-plugin" / "plugin.json").read_text())
        assert "hooks" not in manifest, "hooks must not be declared inline"
        hooks = json.loads(hooks_file.read_text())
        command = hooks["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
        assert command == "${CLAUDE_PLUGIN_ROOT}/hooks/user-prompt-submit"

    def test_errors_without_force_when_exists(self, built_plugin: Path, tmp_path: Path) -> None:
        project = tmp_path / "my-project"
        project.mkdir()
        dest = project / ".cortex" / "plugins" / _PLUGIN_NAME
        dest.mkdir(parents=True)
        (dest / "existing-file.txt").write_text("x")

        result = runner.invoke(
            plugin_app,
            [
                "install",
                "--target",
                "cortex",
                "--project",
                str(project),
                "--plugin-dir",
                str(built_plugin),
            ],
        )
        assert result.exit_code == 1
        assert "already exists" in result.output

    def test_force_overwrites(self, built_plugin: Path, tmp_path: Path) -> None:
        project = tmp_path / "my-project"
        project.mkdir()
        dest = project / ".cortex" / "plugins" / _PLUGIN_NAME
        dest.mkdir(parents=True)
        (dest / "stale-file.txt").write_text("old")

        result = runner.invoke(
            plugin_app,
            [
                "install",
                "--target",
                "cortex",
                "--project",
                str(project),
                "--plugin-dir",
                str(built_plugin),
                "--force",
            ],
        )
        assert result.exit_code == 0
        assert (dest / ".cortex-plugin" / "plugin.json").is_file()
        assert not (dest / "stale-file.txt").exists()


class TestInstallGlobalCortex:
    def test_uses_cli_when_with_hook(self, built_plugin: Path) -> None:
        with patch("ai_rules.commands.plugin.shutil.which", return_value="/usr/bin/cortex"):
            with patch("ai_rules.commands.plugin.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "Installed."
                mock_run.return_value.stderr = ""
                result = runner.invoke(
                    plugin_app,
                    [
                        "install",
                        "--target",
                        "cortex",
                        "--plugin-dir",
                        str(built_plugin),
                        "--with-hook",
                    ],
                )
        assert result.exit_code == 0
        assert "cortex CLI" in result.output
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "/usr/bin/cortex"
        assert args[1:3] == ["plugin", "install"]

    def test_without_hook_skips_cli(self, built_plugin: Path, tmp_path: Path) -> None:
        """Without --with-hook, uses copy path even when CLI is available (to exclude hooks)."""
        fake_dest = tmp_path / ".snowflake" / "cortex" / "plugins" / _PLUGIN_NAME
        with patch("ai_rules.commands.plugin.shutil.which", return_value="/usr/bin/cortex"):
            with patch("ai_rules.commands.plugin._global_dest", return_value=fake_dest):
                result = runner.invoke(
                    plugin_app,
                    ["install", "--target", "cortex", "--plugin-dir", str(built_plugin)],
                )
        assert result.exit_code == 0
        assert fake_dest.is_dir()
        assert not (fake_dest / "hooks").exists()
        assert "Use --with-hook to enable the plugin hook" in result.output

    def test_fallback_copy_when_no_cli_user_confirms(
        self, built_plugin: Path, tmp_path: Path
    ) -> None:
        fake_dest = tmp_path / ".snowflake" / "cortex" / "plugins" / _PLUGIN_NAME
        with patch("ai_rules.commands.plugin.shutil.which", return_value=None):
            with patch("ai_rules.commands.plugin._global_dest", return_value=fake_dest):
                result = runner.invoke(
                    plugin_app,
                    ["install", "--target", "cortex", "--plugin-dir", str(built_plugin)],
                    input="y\n",
                )
        assert result.exit_code == 0
        assert fake_dest.is_dir()
        assert (fake_dest / ".cortex-plugin" / "plugin.json").is_file()

    def test_fallback_abort_when_user_declines(self, built_plugin: Path) -> None:
        with patch("ai_rules.commands.plugin.shutil.which", return_value=None):
            result = runner.invoke(
                plugin_app,
                ["install", "--target", "cortex", "--plugin-dir", str(built_plugin)],
                input="n\n",
            )
        assert result.exit_code == 0
        assert "Aborted" in result.output


class TestInstallGlobalClaude:
    def test_copies_to_skills_dir(self, built_plugin: Path, tmp_path: Path) -> None:
        fake_dest = tmp_path / ".claude" / "skills" / _PLUGIN_NAME
        with patch("ai_rules.commands.plugin._global_dest", return_value=fake_dest):
            result = runner.invoke(
                plugin_app,
                ["install", "--target", "claude", "--plugin-dir", str(built_plugin)],
            )
        assert result.exit_code == 0
        # .claude-plugin/plugin.json is what makes ~/.claude/skills/<name> load
        # as a <name>@skills-dir plugin; without it Claude Code ignores the dir.
        assert (fake_dest / ".claude-plugin" / "plugin.json").is_file()
        assert not (fake_dest / ".cortex-plugin").exists()
        assert "skills-dir" in result.output
        assert "Use --with-hook to enable the plugin hook" in result.output


class TestInstallTargetAll:
    def test_project_install_all_installs_both_platforms(
        self, built_plugin: Path, tmp_path: Path
    ) -> None:
        project = tmp_path / "my-project"
        project.mkdir()
        result = runner.invoke(
            plugin_app,
            [
                "install",
                "--target",
                "all",
                "--project",
                str(project),
                "--plugin-dir",
                str(built_plugin),
            ],
        )
        assert result.exit_code == 0

        cortex_dest = project / ".cortex" / "plugins" / _PLUGIN_NAME
        claude_dest = project / ".claude" / "plugins" / _PLUGIN_NAME
        # Each install carries only its own platform's manifest.
        assert (cortex_dest / ".cortex-plugin" / "plugin.json").is_file()
        assert not (cortex_dest / ".claude-plugin").exists()
        assert (claude_dest / ".claude-plugin" / "plugin.json").is_file()
        assert not (claude_dest / ".cortex-plugin").exists()


class TestInstallBuildNotFound:
    def test_missing_build_dir(self, tmp_path: Path) -> None:
        result = runner.invoke(
            plugin_app,
            ["install", "--target", "cortex", "--plugin-dir", str(tmp_path / "nope")],
        )
        assert result.exit_code == 1
        assert "not found" in result.output


# ---------------------------------------------------------------------------
# Uninstall command tests
# ---------------------------------------------------------------------------


class TestUninstallProjectLocal:
    def test_removes_plugin(self, built_plugin: Path, tmp_path: Path) -> None:
        project = tmp_path / "my-project"
        project.mkdir()
        # First install
        runner.invoke(
            plugin_app,
            [
                "install",
                "--target",
                "cortex",
                "--project",
                str(project),
                "--plugin-dir",
                str(built_plugin),
            ],
        )
        dest = project / ".cortex" / "plugins" / _PLUGIN_NAME
        assert dest.is_dir()

        # Then uninstall
        result = runner.invoke(
            plugin_app, ["uninstall", "--target", "cortex", "--project", str(project)]
        )
        assert result.exit_code == 0
        assert not dest.exists()

    def test_not_installed(self, tmp_path: Path) -> None:
        result = runner.invoke(
            plugin_app, ["uninstall", "--target", "cortex", "--project", str(tmp_path)]
        )
        assert result.exit_code == 0
        assert "Not installed" in result.output

    def test_removes_claude_install(self, built_plugin: Path, tmp_path: Path) -> None:
        """A claude install carries only .claude-plugin/, and the safety check
        must recognise it as ours.
        """
        project = tmp_path / "my-project"
        project.mkdir()
        runner.invoke(
            plugin_app,
            [
                "install",
                "--target",
                "claude",
                "--project",
                str(project),
                "--plugin-dir",
                str(built_plugin),
            ],
        )
        dest = project / ".claude" / "plugins" / _PLUGIN_NAME
        assert dest.is_dir()

        result = runner.invoke(
            plugin_app, ["uninstall", "--target", "claude", "--project", str(project)]
        )
        assert result.exit_code == 0
        assert not dest.exists()

    def test_uninstall_all_removes_both_platforms(self, built_plugin: Path, tmp_path: Path) -> None:
        project = tmp_path / "my-project"
        project.mkdir()
        runner.invoke(
            plugin_app,
            [
                "install",
                "--target",
                "all",
                "--project",
                str(project),
                "--plugin-dir",
                str(built_plugin),
            ],
        )
        cortex_dest = project / ".cortex" / "plugins" / _PLUGIN_NAME
        claude_dest = project / ".claude" / "plugins" / _PLUGIN_NAME
        assert cortex_dest.is_dir() and claude_dest.is_dir()

        result = runner.invoke(
            plugin_app, ["uninstall", "--target", "all", "--project", str(project)]
        )
        assert result.exit_code == 0
        assert not cortex_dest.exists()
        assert not claude_dest.exists()

    def test_uninstall_all_continues_past_missing_platform(
        self, built_plugin: Path, tmp_path: Path
    ) -> None:
        """With --target all, a platform that was never installed is reported
        and skipped rather than aborting the other platform's removal.
        """
        project = tmp_path / "my-project"
        project.mkdir()
        runner.invoke(
            plugin_app,
            [
                "install",
                "--target",
                "claude",
                "--project",
                str(project),
                "--plugin-dir",
                str(built_plugin),
            ],
        )
        claude_dest = project / ".claude" / "plugins" / _PLUGIN_NAME
        assert claude_dest.is_dir()

        result = runner.invoke(
            plugin_app, ["uninstall", "--target", "all", "--project", str(project)]
        )
        assert result.exit_code == 0
        assert "Not installed" in result.output
        assert not claude_dest.exists()


class TestUninstallSafetyCheck:
    def test_refuses_wrong_plugin(self, tmp_path: Path) -> None:
        # Create a directory that looks like a plugin but with wrong name
        dest = tmp_path / ".cortex" / "plugins" / _PLUGIN_NAME
        manifest_dir = dest / ".cortex-plugin"
        manifest_dir.mkdir(parents=True)
        (manifest_dir / "plugin.json").write_text(
            json.dumps({"name": "not-ours"}), encoding="utf-8"
        )
        result = runner.invoke(
            plugin_app, ["uninstall", "--target", "cortex", "--project", str(tmp_path)]
        )
        assert result.exit_code == 1
        assert "Safety check" in result.output
        assert dest.is_dir()  # not removed
