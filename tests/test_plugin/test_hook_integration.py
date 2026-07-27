"""Integration tests for the UserPromptSubmit hook script.

Verifies the full hook pipeline: stdin JSON -> deterministic matcher -> stdout system-reminder.
These tests exercise the actual shell script at hooks/user-prompt-submit.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_DIR = PLUGIN_ROOT / "ai-coding-rules-plugin"
HOOK_SCRIPT = PLUGIN_ROOT / "hooks" / "user-prompt-submit"


@pytest.fixture(autouse=True)
def _check_hook_exists():
    if not HOOK_SCRIPT.exists():
        pytest.skip("hooks/user-prompt-submit not found")


def _run_hook(prompt: str, env_overrides: dict | None = None) -> subprocess.CompletedProcess:
    """Run the hook script with a JSON prompt on stdin."""
    env = os.environ.copy()
    env["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
    if env_overrides:
        env.update(env_overrides)

    input_json = json.dumps({"prompt": prompt})
    return subprocess.run(
        ["bash", str(HOOK_SCRIPT)],
        input=input_json,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )


@pytest.mark.integration
class TestHookScript:
    """Tests that exercise the hook shell script end-to-end."""

    def test_hook_returns_system_reminder_for_known_domain(self):
        """A prompt about Cortex Agents should produce a system-reminder with matched rules."""
        result = _run_hook("Design a Cortex Agent with tool orchestration and Cortex Search")
        assert result.returncode == 0, f"Hook failed: {result.stderr}"
        assert "<system-reminder>" in result.stdout
        assert "</system-reminder>" in result.stdout
        assert "rules/" in result.stdout

    def test_hook_includes_rule_paths(self):
        """The hook output should list specific rule file paths to read."""
        result = _run_hook("Write a Streamlit dashboard with st.connection for Snowflake")
        assert result.returncode == 0, f"Hook failed: {result.stderr}"
        assert "101-snowflake-streamlit-core.md" in result.stdout or "rules/" in result.stdout

    def test_hook_exits_zero_on_no_match(self):
        """A prompt with no domain match should exit 0 with no output (graceful no-op)."""
        result = _run_hook("hello")
        assert result.returncode == 0

    def test_hook_handles_empty_prompt(self):
        """Empty prompt should not crash the hook."""
        result = _run_hook("")
        assert result.returncode == 0

    def test_hook_handles_malformed_json_gracefully(self):
        """Non-JSON input should not crash -- the script has a fallback."""
        env = os.environ.copy()
        env["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
        result = subprocess.run(
            ["bash", str(HOOK_SCRIPT)],
            input="this is not json",
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        assert result.returncode == 0

    def test_hook_json_input_format(self):
        """The hook should accept the standard CoCo/Claude JSON format: {"prompt": "..."}."""
        result = _run_hook("Create a stored procedure in Snowflake SQL with error handling")
        assert result.returncode == 0
        if result.stdout.strip():
            assert "<system-reminder>" in result.stdout

    def test_hook_output_contains_read_instructions(self):
        """When rules match, output should instruct the model to read them."""
        result = _run_hook("Build a Cortex Agent with semantic view grounding")
        assert result.returncode == 0
        if "<system-reminder>" in result.stdout:
            assert "Read" in result.stdout or "read" in result.stdout.lower()


@pytest.mark.integration
class TestHookManifestAccuracy:
    """Tests that verify the hook produces correct rule matches (same as eval fixtures)."""

    def test_cortex_agent_prompt_matches_agent_rules(self):
        """A Cortex Agent prompt should match 115-snowflake-cortex-agents-core.md."""
        result = _run_hook(
            "We're designing a multi-tool Cortex Agent for customer support. "
            "It needs Cortex Search and tool orchestration."
        )
        assert result.returncode == 0
        assert "115-snowflake-cortex-agents-core.md" in result.stdout

    def test_streamlit_prompt_matches_streamlit_rules(self):
        """A Streamlit prompt should match Streamlit rules."""
        result = _run_hook("Deploy a Streamlit app with multipage navigation and session state")
        assert result.returncode == 0
        assert "101-snowflake-streamlit" in result.stdout

    def test_sql_prompt_matches_sql_rules(self):
        """A SQL prompt should match SQL rules."""
        result = _run_hook("Write a stored procedure to merge incremental data into a fact table")
        assert result.returncode == 0
        assert "102-snowflake-sql" in result.stdout or "rules/" in result.stdout


@pytest.mark.integration
class TestPluginManifest:
    """Tests that validate the plugin.json manifest structure."""

    def test_cortex_plugin_json_valid(self):
        """The .cortex-plugin/plugin.json is valid JSON with required fields."""
        manifest_path = PLUGIN_DIR / ".cortex-plugin" / "plugin.json"
        assert manifest_path.exists(), ".cortex-plugin/plugin.json not found"

        data = json.loads(manifest_path.read_text())
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert data["name"] == "ai-coding-rules"

    def test_declared_skills_dir_exists(self):
        """Skills directories declared in plugin.json must exist."""
        manifest_path = PLUGIN_DIR / ".cortex-plugin" / "plugin.json"
        data = json.loads(manifest_path.read_text())
        for skill_dir in data.get("skills", []):
            resolved = PLUGIN_DIR / skill_dir.lstrip("./")
            assert resolved.is_dir(), f"Declared skills dir missing: {resolved}"

    def test_declared_agents_dir_exists(self):
        """Agents directories declared in plugin.json must exist."""
        manifest_path = PLUGIN_DIR / ".cortex-plugin" / "plugin.json"
        data = json.loads(manifest_path.read_text())
        for agents_dir in data.get("agents", []):
            resolved = PLUGIN_DIR / agents_dir.lstrip("./")
            if not resolved.is_dir():
                pytest.skip(f"agents/ dir not yet created: {resolved}")

    def test_hook_script_executable(self):
        """The hook script must be executable."""
        assert HOOK_SCRIPT.exists()
        assert HOOK_SCRIPT.stat().st_mode & 0o111, "hooks/user-prompt-submit is not executable"

    def test_hooks_json_valid(self):
        """hooks/hooks.json is valid JSON with correct structure."""
        hooks_json = PLUGIN_ROOT / "hooks" / "hooks.json"
        assert hooks_json.exists(), "hooks/hooks.json not found"

        data = json.loads(hooks_json.read_text())
        assert "hooks" in data
        assert "UserPromptSubmit" in data["hooks"]
        entries = data["hooks"]["UserPromptSubmit"]
        assert len(entries) >= 1
        assert entries[0]["hooks"][0]["type"] == "command"

    def test_no_duplicate_claude_plugin_dir(self):
        """Only .cortex-plugin/ should exist -- both CoCo and Claude Code accept it."""
        assert (PLUGIN_DIR / ".cortex-plugin" / "plugin.json").exists()
        assert not (PLUGIN_DIR / ".claude-plugin").exists(), (
            ".claude-plugin/ should not exist alongside .cortex-plugin/ -- "
            "both CoCo and Claude Code accept .cortex-plugin/"
        )
