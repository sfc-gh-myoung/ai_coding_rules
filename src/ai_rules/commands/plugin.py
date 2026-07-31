"""ai-rules plugin build — assemble the distributable plugin directory."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, cast

import typer

from ai_rules._shared.console import console

plugin_app = typer.Typer(
    name="plugin",
    help="Plugin build and management commands.",
    no_args_is_help=True,
)

# Repo root: 3 levels up from this file (src/ai_rules/commands/plugin.py)
_REPO_ROOT = Path(__file__).resolve().parents[3]
_PLUGIN_DIR = _REPO_ROOT / "ai-coding-rules-plugin"

# Single source of truth for the plugin's artifact contract.
#
# EXPECTED_ARTIFACTS lists individual files the build MUST emit. EXPECTED_TREES
# lists directory prefixes whose contents are copied wholesale and therefore vary
# in count (rules grow, workflows change) — those are validated by prefix, not by
# enumeration, so adding a rule never requires editing this module.
#
# Together they define the contract in BOTH directions: every expected artifact
# must be present, and every emitted file must be accounted for. The second
# direction is what catches a new copy step that was never registered here.
EXPECTED_ARTIFACTS: tuple[str, ...] = (
    ".cortex-plugin/plugin.json",
    "hooks/hooks.json",
    "hooks/user-prompt-submit",
    "micro_kernel_content.md",
    "skills/rule-loader/CHANGELOG.md",
    "skills/rule-loader/SKILL.md",
    "skills/rule-loader/scripts/match_rules.py",
    "skills/show-rules/SKILL.md",
)

EXPECTED_TREES: tuple[str, ...] = (
    "rules",
    "skills/rule-loader/examples",
    "skills/rule-loader/workflows",
)

# Filesystem noise that is never part of the contract.
_IGNORED_NAMES: frozenset[str] = frozenset({".DS_Store"})

# Manifest contract. The Cortex CLI exposes no `plugin validate` subcommand, so a
# malformed manifest would otherwise surface only at install time on a consumer's
# machine. check_manifest() enforces this at build time instead.
REQUIRED_MANIFEST_KEYS: tuple[str, ...] = ("name", "version", "description", "skills", "hooks")

# Hook events the plugin host recognises. An unrecognised event is silently
# ignored at runtime, which makes a typo here indistinguishable from a hook that
# simply never fires — the exact failure this check exists to surface.
KNOWN_HOOK_EVENTS: frozenset[str] = frozenset(
    {
        "UserPromptSubmit",
        "PreToolUse",
        "PostToolUse",
        "SessionStart",
        "SessionEnd",
        "Stop",
        "SubagentStop",
        "Notification",
        "PreCompact",
    }
)


def _emitted_files(plugin_dir: Path) -> list[str]:
    """Collect every file the build produced, as plugin-relative POSIX paths.

    Args:
        plugin_dir: Root of a built plugin directory.

    Returns:
        Sorted plugin-relative paths, excluding known filesystem noise.
    """
    return sorted(
        p.relative_to(plugin_dir).as_posix()
        for p in plugin_dir.rglob("*")
        if p.is_file() and p.name not in _IGNORED_NAMES
    )


def check_manifest(plugin_dir: Path) -> list[str]:
    """Validate the generated plugin manifest against the Cortex plugin contract.

    The Cortex CLI has no ``plugin validate`` subcommand — a malformed manifest
    is only discovered at install time, on the consumer's machine. This check
    moves that failure to build time.

    Verifies required keys are present and non-empty, that hook events are
    recognised, that each hook entry has the expected shape, and that every
    referenced hook command actually exists and is executable once
    ``${CLAUDE_PLUGIN_ROOT}`` is resolved. The last check is the one that
    catches a renamed or unshipped hook script.

    Args:
        plugin_dir: Root of a built plugin directory.

    Returns:
        Human-readable problem descriptions. Empty when the manifest is valid.
    """
    import json

    problems: list[str] = []
    manifest_path = plugin_dir / ".cortex-plugin" / "plugin.json"

    if not manifest_path.is_file():
        return [f"missing manifest: {manifest_path.relative_to(plugin_dir)}"]

    try:
        decoded = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid plugin.json: {exc}"]

    if not isinstance(decoded, dict):
        return ["plugin.json must be a JSON object"]

    manifest = cast("dict[str, Any]", decoded)

    for key in REQUIRED_MANIFEST_KEYS:
        if key not in manifest:
            problems.append(f"plugin.json missing required key: {key}")
        elif not manifest[key]:
            problems.append(f"plugin.json key is empty: {key}")

    skills = manifest.get("skills")
    if skills is not None and not isinstance(skills, list):
        problems.append("plugin.json 'skills' must be a list")

    hooks = manifest.get("hooks")
    if hooks is not None and not isinstance(hooks, dict):
        problems.append("plugin.json 'hooks' must be an object")
    elif isinstance(hooks, dict):
        event_map = cast("dict[str, Any]", hooks)
        for event, groups in event_map.items():
            if event not in KNOWN_HOOK_EVENTS:
                problems.append(
                    f"plugin.json unknown hook event: {event} "
                    f"(known: {', '.join(sorted(KNOWN_HOOK_EVENTS))})"
                )
            if not isinstance(groups, list):
                problems.append(f"plugin.json hooks.{event} must be a list")
                continue
            group_list = cast("list[Any]", groups)
            for i, group in enumerate(group_list):
                loc = f"hooks.{event}[{i}]"
                if not isinstance(group, dict):
                    problems.append(f"plugin.json {loc} must be an object")
                    continue
                group_map = cast("dict[str, Any]", group)
                entries = group_map.get("hooks")
                if not isinstance(entries, list) or not entries:
                    problems.append(f"plugin.json {loc}.hooks must be a non-empty list")
                    continue
                entry_list = cast("list[Any]", entries)
                for j, entry in enumerate(entry_list):
                    eloc = f"{loc}.hooks[{j}]"
                    if not isinstance(entry, dict):
                        problems.append(f"plugin.json {eloc} must be an object")
                        continue
                    entry_map = cast("dict[str, Any]", entry)
                    if entry_map.get("type") != "command":
                        problems.append(f"plugin.json {eloc}.type must be 'command'")
                    command = entry_map.get("command")
                    if not isinstance(command, str) or not command:
                        problems.append(f"plugin.json {eloc}.command must be a non-empty string")
                        continue
                    problems.extend(_check_hook_command(plugin_dir, command, eloc))

    return problems


def _check_hook_command(plugin_dir: Path, command: str, loc: str) -> list[str]:
    """Resolve a manifest hook command and confirm it is runnable.

    Args:
        plugin_dir: Root of a built plugin directory.
        command: Raw command string from the manifest.
        loc: Manifest location, for error messages.

    Returns:
        Problems found, or empty when the command resolves to an executable.
    """
    if "${CLAUDE_PLUGIN_ROOT}" not in command:
        # An absolute or bare command may be legitimate; we cannot resolve it.
        return []

    rel = command.replace("${CLAUDE_PLUGIN_ROOT}", "").lstrip("/")
    target = plugin_dir / rel
    if not target.is_file():
        return [f"plugin.json {loc}.command does not exist in the build: {rel}"]
    if not os.access(target, os.X_OK):
        return [f"plugin.json {loc}.command is not executable: {rel}"]
    return []


def check_artifacts(plugin_dir: Path) -> list[str]:
    """Validate a built plugin directory against the artifact contract.

    Checks both directions: every ``EXPECTED_ARTIFACTS`` entry is present, and
    every emitted file is either an expected artifact or lives under an
    ``EXPECTED_TREES`` prefix. Also validates the generated manifest via
    :func:`check_manifest`.

    Args:
        plugin_dir: Root of a built plugin directory.

    Returns:
        Human-readable problem descriptions. Empty when the contract holds.
    """
    problems: list[str] = []

    for rel in EXPECTED_ARTIFACTS:
        if not (plugin_dir / rel).is_file():
            problems.append(f"missing expected artifact: {rel}")

    for tree in EXPECTED_TREES:
        if not (plugin_dir / tree).is_dir():
            problems.append(f"missing expected tree: {tree}/")

    declared = set(EXPECTED_ARTIFACTS)
    for rel in _emitted_files(plugin_dir):
        if rel in declared:
            continue
        if any(rel.startswith(f"{tree}/") for tree in EXPECTED_TREES):
            continue
        problems.append(f"undeclared output (add to EXPECTED_ARTIFACTS/EXPECTED_TREES): {rel}")

    problems.extend(check_manifest(plugin_dir))

    return problems


@plugin_app.command()
def build(
    plugin_dir: Path = typer.Option(_PLUGIN_DIR, help="Output plugin directory"),  # noqa: B008
) -> None:
    """Build the self-contained plugin from source files."""
    plugin_dir = plugin_dir.resolve()

    # --- 1. Copy match_rules.py (canonical source → plugin script) ---
    src_script = _REPO_ROOT / "src" / "ai_rules" / "match_rules.py"
    dest_script = plugin_dir / "skills" / "rule-loader" / "scripts" / "match_rules.py"
    dest_script.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_script, dest_script)

    # --- 2. Copy rules/*.md ---
    rules_src = _REPO_ROOT / "rules"
    rules_dest = plugin_dir / "rules"
    if rules_dest.exists():
        shutil.rmtree(rules_dest)
    rules_dest.mkdir(parents=True, exist_ok=True)
    for md in sorted(rules_src.glob("*.md")):
        shutil.copy2(md, rules_dest / md.name)

    # --- 3. Copy hooks ---
    hooks_dest = plugin_dir / "hooks"
    hooks_dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(_REPO_ROOT / "hooks" / "user-prompt-submit", hooks_dest / "user-prompt-submit")
    shutil.copy2(_REPO_ROOT / "hooks" / "hooks.json", hooks_dest / "hooks.json")

    # --- 4. Copy rule-loader skill (SKILL.md, workflows/, examples/) ---
    skill_src = _REPO_ROOT / "skills" / "rule-loader"
    skill_dest = plugin_dir / "skills" / "rule-loader"
    skill_dest.mkdir(parents=True, exist_ok=True)

    for fname in ("SKILL.md", "CHANGELOG.md"):
        src_file = skill_src / fname
        if src_file.exists():
            shutil.copy2(src_file, skill_dest / fname)

    for subdir in ("workflows", "examples"):
        src_sub = skill_src / subdir
        dest_sub = skill_dest / subdir
        if src_sub.is_dir():
            if dest_sub.exists():
                shutil.rmtree(dest_sub)
            shutil.copytree(src_sub, dest_sub)

    # --- 4b. Copy show-rules skill (SKILL.md only) ---
    # $show-rules is the user-invocable PRE-FLIGHT diagnostic. It is advertised as
    # bundled in README.md and docs/ARCHITECTURE.md, so the build must emit it.
    show_rules_src = _REPO_ROOT / "skills" / "show-rules" / "SKILL.md"
    if show_rules_src.exists():
        show_rules_dest = plugin_dir / "skills" / "show-rules"
        show_rules_dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(show_rules_src, show_rules_dest / "SKILL.md")

    # --- 5. Copy micro-kernel content ---
    micro_kernel_src = _REPO_ROOT / "src" / "ai_rules" / "plugin" / "micro_kernel_content.md"
    if micro_kernel_src.exists():
        micro_kernel_dest = plugin_dir / "micro_kernel_content.md"
        shutil.copy2(micro_kernel_src, micro_kernel_dest)

    # --- 6. Write plugin manifests ---
    # Shared hook block — matcher omitted (equivalent to "*", matches all prompts).
    # Timeout omitted (UserPromptSubmit default: 30 s; the script runs in <1 s).
    _hook_block = (
        '  "hooks": {\n'
        '    "UserPromptSubmit": [\n'
        "      {\n"
        '        "hooks": [\n'
        "          {\n"
        '            "type": "command",\n'
        '            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/user-prompt-submit"\n'
        "          }\n"
        "        ]\n"
        "      }\n"
        "    ]\n"
        "  }\n"
    )

    cortex_manifest = plugin_dir / ".cortex-plugin" / "plugin.json"
    cortex_manifest.parent.mkdir(parents=True, exist_ok=True)
    cortex_manifest.write_text(
        "{\n"
        '  "name": "ai-coding-rules",\n'
        '  "version": "1.0.0",\n'
        '  "description": "Deterministic rule loading for AI coding assistants",\n'
        '  "author": { "name": "Michael Young" },\n'
        '  "skills": ["./skills"],\n' + _hook_block + "}\n",
        encoding="utf-8",
    )

    # --- 7. Validate: ensure the script runs standalone ---
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, str(dest_script), "--mode", "metadata", "--rules-dir", str(rules_dest)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        console.print(f"[red]Validation failed:[/red] script exited {result.returncode}")
        console.print(result.stderr)
        raise typer.Exit(1)

    import json

    meta = json.loads(result.stdout)
    rule_count = len(meta.get("rules", {}))

    # --- 7b. Validate the artifact contract (same check as `plugin verify`) ---
    problems = check_artifacts(plugin_dir)
    if problems:
        console.print("[red]Artifact contract violated:[/red]")
        for problem in problems:
            console.print(f"  - {problem}")
        raise typer.Exit(1)

    console.print(f"[green]Plugin built successfully:[/green] {plugin_dir}")
    console.print(f"  Rules: {rule_count}")
    console.print(f"  Script: {dest_script.relative_to(plugin_dir)}")
    console.print("  Hook: hooks/user-prompt-submit")


@plugin_app.command()
def verify(
    plugin_dir: Path = typer.Option(_PLUGIN_DIR, help="Plugin directory to verify"),  # noqa: B008
) -> None:
    """Verify a built plugin directory against the artifact contract.

    Asserts every expected artifact is present, that no undeclared output was
    emitted, and that the generated manifest is valid JSON. Exits 1 listing all
    problems when the contract is violated.
    """
    plugin_dir = plugin_dir.resolve()

    if not plugin_dir.is_dir():
        console.print(f"[red]Not a directory:[/red] {plugin_dir}")
        raise typer.Exit(1)

    problems = check_artifacts(plugin_dir)
    if problems:
        console.print(f"[red]Artifact contract violated:[/red] {plugin_dir}")
        for problem in problems:
            console.print(f"  - {problem}")
        raise typer.Exit(1)

    console.print(f"[green]Artifact contract satisfied:[/green] {plugin_dir}")
    console.print(f"  Expected artifacts: {len(EXPECTED_ARTIFACTS)}")
    console.print(f"  Expected trees: {len(EXPECTED_TREES)}")
