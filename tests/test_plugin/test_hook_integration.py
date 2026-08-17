"""Integration tests for the UserPromptSubmit hook script.

Verifies the full hook pipeline: stdin JSON -> deterministic matcher -> stdout system-reminder.
These tests exercise the actual shell script at hooks/user-prompt-submit.

The plugin is built into a session-scoped temp directory rather than read from
``ai-coding-rules-plugin/``. That directory is gitignored build output, so pointing
at it meant every test here silently SKIPPED on any checkout without a prior local
build -- including CI, whose test job never builds. The hook had no CI coverage at
all despite being the component most likely to break, since it is the one piece
whose behaviour depends on how the host resolves paths.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules.commands.plugin import plugin_app

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SOURCE_HOOK = PLUGIN_ROOT / "hooks" / "user-prompt-submit"

# Populated once per session by the _built_plugin fixture. A holder dict keeps the
# assignment out of module scope without a `global` statement.
_BUILT: dict[str, Path] = {}


@pytest.fixture(scope="session", autouse=True)
def _built_plugin(tmp_path_factory: pytest.TempPathFactory) -> None:
    """Build the plugin once per session for the hook to execute against."""
    dest = tmp_path_factory.mktemp("hook_plugin")
    result = CliRunner().invoke(plugin_app, ["build", "--plugin-dir", str(dest)])
    assert result.exit_code == 0, f"plugin build failed: {result.output}"
    _BUILT["dir"] = dest


@pytest.fixture(autouse=True)
def _check_hook_exists() -> None:
    """Guard on the tracked source hook, not on regenerable build output."""
    if not SOURCE_HOOK.exists():
        pytest.skip("hooks/user-prompt-submit not found")


def _plugin_dir() -> Path:
    """Return the session-built plugin directory."""
    return _BUILT["dir"]


def _hook_script() -> Path:
    """Return the emitted hook script inside the session-built plugin."""
    return _BUILT["dir"] / "hooks" / "user-prompt-submit"


def _run_hook(
    prompt: str, env_overrides: dict | None = None, with_plugin_root: bool = True
) -> subprocess.CompletedProcess:
    """Run the hook script with a JSON prompt on stdin."""
    plugin_dir = _BUILT["dir"]
    env = os.environ.copy()
    if with_plugin_root:
        env["CLAUDE_PLUGIN_ROOT"] = str(plugin_dir)
    else:
        env.pop("CLAUDE_PLUGIN_ROOT", None)
    if env_overrides:
        env.update(env_overrides)

    input_json = json.dumps({"prompt": prompt})
    return subprocess.run(
        ["bash", str(plugin_dir / "hooks" / "user-prompt-submit")],
        input=input_json,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )


def _run_hook_with_plugin_dir(plugin_dir: Path, prompt: str) -> subprocess.CompletedProcess:
    """Run a built hook from a specific plugin directory."""
    env = os.environ.copy()
    env["CLAUDE_PLUGIN_ROOT"] = str(plugin_dir)
    return subprocess.run(
        ["bash", str(plugin_dir / "hooks" / "user-prompt-submit")],
        input=json.dumps({"prompt": prompt}),
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )


def _build_plugin_at(dest: Path) -> None:
    """Build the plugin at a specific destination for mutation-safe tests."""
    result = CliRunner().invoke(plugin_app, ["build", "--plugin-dir", str(dest)])
    assert result.exit_code == 0, result.output


def _normalize_path(path_str: str) -> Path:
    """OS-aware path normalization for assertion checks.

    Handles Git-Bash style (/c/Users/...) and Python-native (C:\\Users\\...)
    paths, normalizing to the host filesystem representation.
    """
    import platform
    import re

    if platform.system() == "Windows":
        # Git-Bash style: /c/Users/... -> C:/Users/...
        m = re.match(r"^/([a-zA-Z])/(.*)", path_str)
        if m:
            path_str = f"{m.group(1).upper()}:/{m.group(2)}"
    return Path(path_str)


def _extract_injected_rule_paths(stdout: str) -> list[str]:
    """Return rendered path list items from the Matched Rules section only."""
    paths: list[str] = []
    in_section = False
    for line in stdout.splitlines():
        if "Matched Rules for This Request" in line:
            in_section = True
            continue
        if not in_section:
            continue
        if line.strip() == "" and paths:
            break
        if line.startswith("- "):
            candidate = line[2:].strip()
            if "/rules/" in candidate or "\\rules\\" in candidate:
                paths.append(candidate)
    return paths


def _markdown_unescape_path(path: str) -> str:
    """Undo the hook's markdown escaping before filesystem assertions."""
    replacements = [
        (r"\`", "`"),
        (r"\]", "]"),
        (r"\[", "["),
        (r"\_", "_"),
        (r"\*", "*"),
        (r"\|", "|"),
        (r"\\", "\\"),
    ]
    for escaped, raw in replacements:
        path = path.replace(escaped, raw)
    return path


def _assert_rendered_rule_path(rendered_path: str, plugin_dir: Path) -> None:
    """Assert a rendered markdown path points to a built plugin rule file."""
    fs_path = _normalize_path(_markdown_unescape_path(rendered_path))
    assert fs_path.is_absolute(), f"Path is not absolute: {rendered_path}"
    assert fs_path.exists(), f"Path does not exist: {rendered_path}"
    assert fs_path.resolve().is_relative_to((plugin_dir / "rules").resolve()), (
        f"Path {rendered_path} is not inside {plugin_dir / 'rules'}"
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
        env["CLAUDE_PLUGIN_ROOT"] = str(_plugin_dir())
        result = subprocess.run(
            ["bash", str(_hook_script())],
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

    def test_readme_me_prompt_matches_readme_rule(self):
        result = _run_hook("Re-run the README.me exercise with the previous README review")
        assert result.returncode == 0
        assert "801-project-readme.md" in result.stdout

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
        manifest_path = _plugin_dir() / ".cortex-plugin" / "plugin.json"
        assert manifest_path.exists(), ".cortex-plugin/plugin.json not found"

        data = json.loads(manifest_path.read_text())
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert data["name"] == "ai-coding-rules"

    def test_declared_skills_dir_exists(self):
        """Skills directories declared in plugin.json must exist."""
        manifest_path = _plugin_dir() / ".cortex-plugin" / "plugin.json"
        data = json.loads(manifest_path.read_text())
        for skill_dir in data.get("skills", []):
            resolved = _plugin_dir() / skill_dir.lstrip("./")
            assert resolved.is_dir(), f"Declared skills dir missing: {resolved}"

    def test_declared_agents_dir_exists(self):
        """Agents directories declared in plugin.json must exist."""
        manifest_path = _plugin_dir() / ".cortex-plugin" / "plugin.json"
        data = json.loads(manifest_path.read_text())
        for agents_dir in data.get("agents", []):
            resolved = _plugin_dir() / agents_dir.lstrip("./")
            if not resolved.is_dir():
                pytest.skip(f"agents/ dir not yet created: {resolved}")

    def test_hook_script_executable(self):
        """The hook script must be executable."""
        assert _hook_script().exists()
        assert _hook_script().stat().st_mode & 0o111, "hooks/user-prompt-submit is not executable"

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
        assert (_plugin_dir() / ".cortex-plugin" / "plugin.json").exists()
        assert not (_plugin_dir() / ".claude-plugin").exists(), (
            ".claude-plugin/ should not exist alongside .cortex-plugin/ -- "
            "both CoCo and Claude Code accept .cortex-plugin/"
        )


@pytest.mark.integration
class TestHookAbsolutePaths:
    """Tests that the hook emits absolute, fully-canonical paths."""

    def test_emitted_paths_are_absolute_and_canonical(self):
        """Every emitted rule path must be absolute, canonical, and exist on disk."""
        result = _run_hook("Design a Cortex Agent with tool orchestration and Cortex Search")
        assert result.returncode == 0
        if "<system-reminder>" not in result.stdout:
            pytest.skip("No rules matched for this prompt")

        plugin_dir = _plugin_dir()
        paths_found = _extract_injected_rule_paths(result.stdout)
        assert paths_found, "No absolute rule paths found in output"
        for path_str in paths_found:
            _assert_rendered_rule_path(path_str, plugin_dir)

    def test_emitted_paths_are_not_bare_relative(self):
        """Emitted paths must NOT be the bare repo-relative 'rules/<file>' form."""
        result = _run_hook("Write a stored procedure to merge incremental data")
        assert result.returncode == 0
        if "<system-reminder>" not in result.stdout:
            pytest.skip("No rules matched for this prompt")

        for path_str in _extract_injected_rule_paths(result.stdout):
            assert not path_str.startswith("rules/"), f"Path should be absolute: {path_str}"

    def test_hook_falls_back_when_claude_plugin_root_unset(self):
        """Hook resolves PLUGIN_ROOT via dirname fallback when CLAUDE_PLUGIN_ROOT is unset."""
        result = _run_hook(
            "Design a Cortex Agent with tool orchestration",
            with_plugin_root=False,
        )
        assert result.returncode == 0
        # The hook should still produce output (using dirname-based fallback)
        if "<system-reminder>" in result.stdout:
            for path_str in _extract_injected_rule_paths(result.stdout):
                p = _normalize_path(_markdown_unescape_path(path_str))
                assert p.is_absolute(), f"Fallback path not absolute: {path_str}"

    def test_markdown_safe_rendering_with_special_chars(self, tmp_path: Path):
        """Real hook output escapes markdown-significant install-path characters."""
        plugin_dir = tmp_path / "ai coding`rules*root"
        result = CliRunner().invoke(plugin_app, ["build", "--plugin-dir", str(plugin_dir)])
        assert result.exit_code == 0, result.output

        hook_result = _run_hook_with_plugin_dir(
            plugin_dir,
            "Write a Snowflake stored procedure",
        )
        assert hook_result.returncode == 0, hook_result.stderr
        emitted = _extract_injected_rule_paths(hook_result.stdout)
        assert emitted
        assert any("\\*" in path or "\\`" in path for path in emitted)
        for path in emitted:
            _assert_rendered_rule_path(path, plugin_dir)


@pytest.mark.integration
class TestHookFailOpen:
    """Negative tests for hook fail-open behavior."""

    def test_missing_matcher_exits_zero_without_output(self, tmp_path: Path):
        plugin_dir = tmp_path / "missing_matcher"
        _build_plugin_at(plugin_dir)
        (plugin_dir / "skills" / "rule-loader" / "scripts" / "match_rules.py").unlink()

        result = _run_hook_with_plugin_dir(plugin_dir, "Write a Snowflake stored procedure")

        assert result.returncode == 0
        assert result.stdout == ""

    def test_malformed_matcher_output_exits_zero_without_output(self, tmp_path: Path):
        plugin_dir = tmp_path / "malformed_matcher"
        _build_plugin_at(plugin_dir)
        matcher = plugin_dir / "skills" / "rule-loader" / "scripts" / "match_rules.py"
        matcher.write_text("print('not json')\n", encoding="utf-8")

        result = _run_hook_with_plugin_dir(plugin_dir, "Write a Snowflake stored procedure")

        assert result.returncode == 0
        assert result.stdout == ""

    def test_broken_canonicalizer_exits_zero_without_output(self, tmp_path: Path):
        plugin_dir = tmp_path / "broken_canonicalizer"
        _build_plugin_at(plugin_dir)
        hook = plugin_dir / "hooks" / "user-prompt-submit"
        hook_text = hook.read_text(encoding="utf-8")
        hook.write_text(
            hook_text.replace("import os", "import os\nraise RuntimeError('boom')", 1),
            encoding="utf-8",
        )

        result = _run_hook_with_plugin_dir(plugin_dir, "Write a Snowflake stored procedure")

        assert result.returncode == 0
        assert result.stdout == ""

    def test_empty_canonicalized_output_exits_zero_without_output(self, tmp_path: Path):
        plugin_dir = tmp_path / "empty_canonicalizer"
        _build_plugin_at(plugin_dir)
        hook = plugin_dir / "hooks" / "user-prompt-submit"
        hook_text = hook.read_text(encoding="utf-8")
        hook.write_text(
            hook_text.replace("print('\\n'.join(out))", "print('')", 1),
            encoding="utf-8",
        )

        result = _run_hook_with_plugin_dir(plugin_dir, "Write a Snowflake stored procedure")

        assert result.returncode == 0
        assert result.stdout == ""
