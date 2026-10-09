"""ai-rules plugin: build, verify, install, and uninstall the plugin."""

from __future__ import annotations

import difflib
import json
import os
import shutil
import subprocess
from enum import StrEnum
from pathlib import Path
from typing import Any, cast

import typer

from ai_rules._shared.console import console
from ai_rules.plugin.replicas import (
    BUILD_COPIES,
    REPO_REPLICAS,
    BuildCopy,
    RepoReplica,
    expected_artifacts,
    expected_trees,
)


class TargetPlatform(StrEnum):
    """Supported assistant platforms for plugin installation.

    ``all`` is a CLI convenience that expands to every concrete platform via
    :func:`_resolve_targets`; it is never a valid destination on its own.
    """

    cortex = "cortex"
    claude = "claude"
    all = "all"


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
# Both tuples are DERIVED from the replica manifest in ai_rules.plugin.replicas,
# not maintained by hand. Previously the copy steps in build() and this contract
# were two independent lists, so a new copy step could ship an artifact that
# nothing verified. Deriving them removes that failure mode by construction.
#
# EXPECTED_ARTIFACTS lists individual files the build MUST emit. EXPECTED_TREES
# lists directory prefixes whose contents are copied wholesale and therefore vary
# in count (rules grow, workflows change): those are validated by prefix, not by
# enumeration, so adding a rule never requires editing this module.
#
# Together they define the contract in BOTH directions: every expected artifact
# must be present, and every emitted file must be accounted for. The second
# direction is what catches a new copy step that was never registered.
EXPECTED_ARTIFACTS: tuple[str, ...] = expected_artifacts()

EXPECTED_TREES: tuple[str, ...] = expected_trees()

# Filesystem noise that is never part of the contract.
_IGNORED_NAMES: frozenset[str] = frozenset({".DS_Store"})

# Manifest contract. `cortex plugin validate` checks a plugin against CoCo's own
# loader expectations, but it is an external binary that may not be installed, and
# it does not know this repo's source-fidelity requirements. check_manifest()
# enforces the shape at build time so a malformed manifest fails here rather than
# at install time on a consumer's machine. `task plugin:verify` runs both.
#
# "hooks" is deliberately absent: CoCo auto-discovers ./hooks/hooks.json, which is
# the single hook declaration. check_manifest() rejects an inline 'hooks' key.
REQUIRED_MANIFEST_KEYS: tuple[str, ...] = ("name", "version", "description", "skills")

# Claude Code auto-discovers skills/ and hooks/hooks.json, so its manifest carries
# only identity keys; a "skills" key is not part of Claude Code's schema.
CLAUDE_REQUIRED_MANIFEST_KEYS: tuple[str, ...] = ("name", "version", "description")

# Manifest directory each platform reads. CoCo only recognises .cortex-plugin/ and
# Claude Code only recognises .claude-plugin/ (a directory under ~/.claude/skills/
# loads as a <name>@skills-dir plugin only when .claude-plugin/plugin.json exists).
# The build emits both; install ships only the target platform's.
MANIFEST_DIRS: dict[TargetPlatform, str] = {
    TargetPlatform.cortex: ".cortex-plugin",
    TargetPlatform.claude: ".claude-plugin",
}

# Placeholder the plugin host substitutes with the installed plugin's root directory.
# CoCo Desktop substitutes it at config-load time (the variable is NOT exported into
# the hook process env, so the hook script cannot rely on reading it); Claude Code
# supports the same placeholder.
_PLUGIN_ROOT_VAR = "${CLAUDE_PLUGIN_ROOT}"

# Hook events the plugin host recognises. An unrecognised event is silently
# ignored at runtime, which makes a typo here indistinguishable from a hook that
# simply never fires: the exact failure this check exists to surface.
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
    """Validate both generated plugin manifests against their host contracts.

    The Cortex CLI has no ``plugin validate`` subcommand: a malformed manifest
    is only discovered at install time, on the consumer's machine. This check
    moves that failure to build time.

    Verifies required keys are present and non-empty, that hook events are
    recognised, that each hook entry has the expected shape, and that every
    referenced hook command actually exists and is executable once relative
    paths are resolved against the plugin root. The last check is the one
    that catches a renamed or unshipped hook script.

    Args:
        plugin_dir: Root of a built plugin directory.

    Returns:
        Human-readable problem descriptions. Empty when the manifests are valid.
    """
    problems: list[str] = []
    problems.extend(
        _check_one_manifest(plugin_dir, ".cortex-plugin/plugin.json", REQUIRED_MANIFEST_KEYS)
    )
    problems.extend(
        _check_one_manifest(plugin_dir, ".claude-plugin/plugin.json", CLAUDE_REQUIRED_MANIFEST_KEYS)
    )
    problems.extend(check_hooks_file(plugin_dir))
    return problems


def _check_one_manifest(plugin_dir: Path, rel: str, required_keys: tuple[str, ...]) -> list[str]:
    """Validate a single plugin manifest file.

    Args:
        plugin_dir: Root of a built plugin directory.
        rel: Manifest path relative to the plugin root, for lookup and messages.
        required_keys: Keys that must be present and non-empty.

    Returns:
        Human-readable problem descriptions. Empty when the manifest is valid.
    """
    problems: list[str] = []
    manifest_path = plugin_dir / rel

    if not manifest_path.is_file():
        return [f"missing manifest: {rel}"]

    try:
        decoded = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid {rel}: {exc}"]

    if not isinstance(decoded, dict):
        return [f"{rel} must be a JSON object"]

    manifest = cast("dict[str, Any]", decoded)

    for key in required_keys:
        if key not in manifest:
            problems.append(f"{rel} missing required key: {key}")
        elif not manifest[key]:
            problems.append(f"{rel} key is empty: {key}")

    skills = manifest.get("skills")
    if skills is not None and not isinstance(skills, list):
        problems.append(f"{rel} 'skills' must be a list")

    # Hooks must NOT be declared inline. Every supported host auto-discovers
    # ./hooks/hooks.json when the manifest omits the key, and both CoCo Desktop
    # and CoCo CLI were verified to load it and substitute ${CLAUDE_PLUGIN_ROOT}
    # from there. Two declarations previously disagreed: Desktop read the inline
    # key and ignored hooks.json, the CLI read hooks.json, so a fix applied to
    # one silently did nothing on the other host.
    if "hooks" in manifest:
        problems.append(
            f"{rel} must not declare 'hooks' inline; hooks/hooks.json is the "
            "single source (hosts auto-discover it). Two declarations diverge per host."
        )

    return problems


def check_hooks_file(plugin_dir: Path) -> list[str]:
    """Validate the plugin's hooks/hooks.json, the single hook declaration.

    Args:
        plugin_dir: Root of a built plugin directory.

    Returns:
        Human-readable problem descriptions. Empty when the file is well-formed.
    """
    rel = "hooks/hooks.json"
    path = plugin_dir / "hooks" / "hooks.json"

    if not path.is_file():
        return [f"missing {rel}"]

    try:
        decoded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid {rel}: {exc}"]

    if not isinstance(decoded, dict):
        return [f"{rel} must be a JSON object"]

    wrapper = cast("dict[str, Any]", decoded)
    hooks = wrapper.get("hooks")
    if not isinstance(hooks, dict) or not hooks:
        return [f"{rel} must contain a non-empty 'hooks' object"]

    return _check_hooks_events(plugin_dir, cast("dict[str, Any]", hooks), rel)


def _check_hooks_events(plugin_dir: Path, event_map: dict[str, Any], source: str) -> list[str]:
    """Validate a HooksConfig event map and every command it declares.

    Args:
        plugin_dir: Root of a built plugin directory.
        event_map: Mapping of hook event name to matcher groups.
        source: File the config came from, for error messages.

    Returns:
        Human-readable problem descriptions.
    """
    problems: list[str] = []

    for event, groups in event_map.items():
        if event not in KNOWN_HOOK_EVENTS:
            problems.append(
                f"{source} unknown hook event: {event} "
                f"(known: {', '.join(sorted(KNOWN_HOOK_EVENTS))})"
            )
        if not isinstance(groups, list):
            problems.append(f"{source} hooks.{event} must be a list")
            continue
        group_list = cast("list[Any]", groups)
        for i, group in enumerate(group_list):
            loc = f"hooks.{event}[{i}]"
            if not isinstance(group, dict):
                problems.append(f"{source} {loc} must be an object")
                continue
            group_map = cast("dict[str, Any]", group)
            entries = group_map.get("hooks")
            if not isinstance(entries, list) or not entries:
                problems.append(f"{source} {loc}.hooks must be a non-empty list")
                continue
            entry_list = cast("list[Any]", entries)
            for j, entry in enumerate(entry_list):
                eloc = f"{loc}.hooks[{j}]"
                if not isinstance(entry, dict):
                    problems.append(f"{source} {eloc} must be an object")
                    continue
                entry_map = cast("dict[str, Any]", entry)
                if entry_map.get("type") != "command":
                    problems.append(f"{source} {eloc}.type must be 'command'")
                command = entry_map.get("command")
                if not isinstance(command, str) or not command:
                    problems.append(f"{source} {eloc}.command must be a non-empty string")
                    continue
                problems.extend(_check_hook_command(plugin_dir, command, eloc, source))

    return problems


def _check_hook_command(plugin_dir: Path, command: str, loc: str, source: str) -> list[str]:
    """Resolve a declared hook command and confirm it is runnable.

    A bare relative command is rejected outright. Plugin hosts run hook commands with
    cwd set to the user's workspace, not the plugin root, so a relative command either
    fails with exit 127 or silently executes a same-named script from whatever project
    the user happens to be in. Resolving it against ``plugin_dir`` here would report a
    pass for a command that cannot work at runtime.

    Args:
        plugin_dir: Root of a built plugin directory.
        command: Raw command string from the hook config.
        loc: Config location, for error messages.
        source: File the command came from, for error messages.

    Returns:
        Problems found, or empty when the command resolves to an executable.
    """
    if command.startswith(_PLUGIN_ROOT_VAR):
        rel = command[len(_PLUGIN_ROOT_VAR) :].lstrip("/")
        target = plugin_dir / rel
    elif command.startswith("/"):
        # Absolute path: cannot validate against the build directory
        return []
    else:
        return [
            f"{source} {loc}.command must be absolute or start with "
            f"{_PLUGIN_ROOT_VAR}; a relative command resolves against the user's "
            f"workspace at runtime, not the plugin root: {command}"
        ]

    if not target.is_file():
        return [f"{source} {loc}.command does not exist in the build: {rel}"]
    if not os.access(target, os.X_OK):
        return [f"{source} {loc}.command is not executable: {rel}"]
    return []


def _check_copy_content(copy: BuildCopy, plugin_dir: Path) -> list[str]:
    """Byte-compare one emitted artifact against its primary.

    Existence alone is not evidence of correctness: a stale or truncated copy is
    still a file. This is what distinguishes a plugin directory that was built
    from the current sources from one left over from an earlier build.

    Args:
        copy: The manifest entry to check.
        plugin_dir: Root of a built plugin directory.

    Returns:
        Problem descriptions, empty when the emitted bytes match the primary.
    """
    src = _REPO_ROOT / copy.primary
    dest = plugin_dir / copy.dest

    if not src.exists():
        # A missing optional primary means nothing should have been emitted.
        # Absence is validated by the EXPECTED_ARTIFACTS pass, not here.
        return []

    if not copy.is_tree:
        if not dest.is_file():
            return []
        if dest.read_bytes() != src.read_bytes():
            return [f"stale artifact (differs from primary {copy.primary}): {copy.dest}"]
        return []

    if not dest.is_dir():
        return []

    pattern = copy.pattern or "**/*"
    problems: list[str] = []
    src_files = {
        p.relative_to(src).as_posix(): p
        for p in sorted(src.glob(pattern))
        if p.is_file() and p.name not in _IGNORED_NAMES
    }
    dest_files = {
        p.relative_to(dest).as_posix(): p
        for p in sorted(dest.glob(pattern))
        if p.is_file() and p.name not in _IGNORED_NAMES
    }

    for name in sorted(set(src_files) - set(dest_files)):
        problems.append(f"missing from emitted tree {copy.dest}/: {name}")
    for name in sorted(set(dest_files) - set(src_files)):
        problems.append(f"extra file in emitted tree {copy.dest}/: {name}")
    for name in sorted(set(src_files) & set(dest_files)):
        if dest_files[name].read_bytes() != src_files[name].read_bytes():
            problems.append(
                f"stale artifact (differs from primary {copy.primary}): {copy.dest}/{name}"
            )

    return problems


def check_artifacts(plugin_dir: Path) -> list[str]:
    """Validate a built plugin directory against the artifact contract.

    Checks three things: every ``EXPECTED_ARTIFACTS`` entry is present, every
    emitted file is either an expected artifact or lives under an
    ``EXPECTED_TREES`` prefix, and every copied artifact is byte-identical to its
    primary. Also validates the generated manifest via :func:`check_manifest`.

    The content pass matters because the first two checks are satisfied by a
    stale build. Without it, a plugin directory carrying an outdated matcher
    verifies clean, which is how a drifted copy can ship unnoticed.

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

    # Generated artifacts are excluded: plugin.json is written from an inline
    # literal and has no primary to compare against.
    for copy in BUILD_COPIES:
        problems.extend(_check_copy_content(copy, plugin_dir))

    problems.extend(check_manifest(plugin_dir))

    return problems


def _apply_copy(copy: BuildCopy, plugin_dir: Path) -> None:
    """Execute one manifest copy into the built plugin.

    Tree destinations are removed before copying so a source file deleted since
    the last build does not linger in the output. ``shutil.copy2`` preserves the
    mode bits, which is what keeps ``hooks/user-prompt-submit`` executable.

    Args:
        copy: The manifest entry to apply.
        plugin_dir: Root of the output plugin directory.

    Raises:
        FileNotFoundError: If a required primary is missing.
    """
    src = _REPO_ROOT / copy.primary
    dest = plugin_dir / copy.dest

    if not src.exists():
        if copy.required:
            raise FileNotFoundError(f"required primary missing: {copy.primary}")
        return

    if not copy.is_tree:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return

    if dest.exists():
        shutil.rmtree(dest)

    if copy.pattern is None:
        shutil.copytree(src, dest)
        return

    dest.mkdir(parents=True, exist_ok=True)
    for match in sorted(src.glob(copy.pattern)):
        shutil.copy2(match, dest / match.name)


@plugin_app.command()
def build(
    plugin_dir: Path = typer.Option(_PLUGIN_DIR, help="Output plugin directory"),  # noqa: B008
) -> None:
    """Build the self-contained plugin from source files."""
    plugin_dir = plugin_dir.resolve()

    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)

    # --- 1. Copy every declared primary into the plugin ---
    # Driven by BUILD_COPIES so this loop and the artifact contract cannot diverge.
    for copy in BUILD_COPIES:
        _apply_copy(copy, plugin_dir)

    dest_script = plugin_dir / "skills" / "rule-loader" / "scripts" / "match_rules.py"
    rules_dest = plugin_dir / "rules"

    # --- 2. Write plugin manifests ---
    # One manifest per platform: CoCo only reads .cortex-plugin/plugin.json and
    # Claude Code only reads .claude-plugin/plugin.json (a directory under
    # ~/.claude/skills/ loads as a <name>@skills-dir plugin only when that
    # manifest exists). The build emits both; install ships the target's.
    #
    # No inline "hooks" key in either. Both hosts auto-discover ./hooks/hooks.json,
    # and that file is the single declaration -- verified firing on both CoCo
    # Desktop and CoCo CLI with the inline key absent, in both cases with
    # ${CLAUDE_PLUGIN_ROOT} substituted at config-load time.
    #
    # Declaring hooks in both places was actively harmful: Desktop read the inline
    # key and ignored hooks/hooks.json, while the CLI read hooks/hooks.json. A fix
    # applied to one file therefore appeared to work on one host and silently did
    # nothing on the other.
    cortex_manifest = plugin_dir / ".cortex-plugin" / "plugin.json"
    cortex_manifest.parent.mkdir(parents=True, exist_ok=True)
    cortex_manifest.write_text(
        "{\n"
        '  "name": "ai-coding-rules",\n'
        '  "version": "1.0.0",\n'
        '  "description": "Deterministic rule loading for AI coding assistants",\n'
        '  "author": { "name": "Michael Young" },\n'
        '  "skills": ["./skills"]\n'
        "}\n",
        encoding="utf-8",
    )

    # Claude Code auto-discovers skills/ and hooks/hooks.json, so its manifest
    # carries identity keys only; "skills" is not part of Claude Code's schema.
    claude_manifest = plugin_dir / ".claude-plugin" / "plugin.json"
    claude_manifest.parent.mkdir(parents=True, exist_ok=True)
    claude_manifest.write_text(
        "{\n"
        '  "name": "ai-coding-rules",\n'
        '  "version": "1.0.0",\n'
        '  "description": "Deterministic rule loading for AI coding assistants",\n'
        '  "author": { "name": "Michael Young" }\n'
        "}\n",
        encoding="utf-8",
    )

    # --- 3. Validate: ensure the script runs standalone ---
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

    meta = json.loads(result.stdout)
    rule_count = len(meta.get("rules", {}))

    # --- 3b. Validate the artifact contract (same check as `plugin verify`) ---
    problems = check_artifacts(plugin_dir)
    if problems:
        console.print("[red]Artifact contract violated:[/red]")
        for problem in problems:
            console.print(f"  - {problem}")
        raise typer.Exit(1)

    console.print(f"[green]Plugin built successfully:[/green] {plugin_dir}")
    console.print(f"  Rules: {rule_count}")
    console.print(f"  Script: {dest_script.relative_to(plugin_dir)}")
    console.print("  Hook: ${CLAUDE_PLUGIN_ROOT}/hooks/user-prompt-submit")


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
    console.print(f"  Content verified against primaries: {len(BUILD_COPIES)} copies")


@plugin_app.command()
def sync(
    check: bool = typer.Option(
        False,
        "--check",
        help="Report drift and exit 1 instead of writing. For CI and pre-commit.",
    ),
) -> None:
    """Regenerate the tracked in-repo replicas from their primaries.

    The plugin ships as a self-contained directory without ``src/``, so the
    matcher must also exist under ``skills/rule-loader/scripts/``. That copy is
    generated output, not a file to hand-edit: run this command after changing the
    primary.

    ``--check`` regenerates nothing and instead byte-compares each replica against
    its primary, printing a unified diff and exiting 1 on the first divergence.
    """
    drifted: list[RepoReplica] = []

    for replica in REPO_REPLICAS:
        primary_path = _REPO_ROOT / replica.primary
        replica_path = _REPO_ROOT / replica.replica

        if not primary_path.is_file():
            console.print(f"[red]Primary missing:[/red] {replica.primary}")
            raise typer.Exit(1)

        primary_bytes = primary_path.read_bytes()
        current = replica_path.read_bytes() if replica_path.is_file() else None

        if current == primary_bytes:
            continue

        drifted.append(replica)

        if check:
            console.print(f"[red]Replica out of sync:[/red] {replica.replica}")
            console.print(f"  Primary: {replica.primary}")
            diff = difflib.unified_diff(
                primary_path.read_text(encoding="utf-8").splitlines(keepends=True),
                replica_path.read_text(encoding="utf-8").splitlines(keepends=True)
                if replica_path.is_file()
                else [],
                fromfile=f"{replica.primary} (primary)",
                tofile=f"{replica.replica} (replica)",
                n=2,
            )
            for line in list(diff)[:40]:
                console.print(f"  {line.rstrip()}")
            continue

        replica_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(primary_path, replica_path)
        console.print(f"[green]Synced:[/green] {replica.replica}")

    if check and drifted:
        console.print(
            f"\n[red]{len(drifted)} replica(s) out of sync.[/red] "
            "Run `ai-rules plugin sync` to regenerate."
        )
        raise typer.Exit(1)

    if not drifted:
        console.print(f"[green]All {len(REPO_REPLICAS)} replica(s) in sync.[/green]")


# ---------------------------------------------------------------------------
# Install / Uninstall
# ---------------------------------------------------------------------------

_PLUGIN_NAME = "ai-coding-rules"


def _resolve_targets(target: TargetPlatform) -> tuple[TargetPlatform, ...]:
    """Expand the CLI target into concrete platforms.

    Args:
        target: The value passed to --target, possibly ``all``.

    Returns:
        Concrete platforms to act on, in a stable order.
    """
    if target == TargetPlatform.all:
        return (TargetPlatform.cortex, TargetPlatform.claude)
    return (target,)


def _global_dest(target: TargetPlatform) -> Path:
    home = Path.home()
    if target == TargetPlatform.cortex:
        return home / ".snowflake" / "cortex" / "plugins" / _PLUGIN_NAME
    return home / ".claude" / "skills" / _PLUGIN_NAME


def _project_dest(target: TargetPlatform, project: Path) -> Path:
    if target == TargetPlatform.cortex:
        return project / ".cortex" / "plugins" / _PLUGIN_NAME
    return project / ".claude" / "plugins" / _PLUGIN_NAME


def _is_our_plugin(path: Path) -> bool:
    """Check that a directory is actually our plugin before removing.

    An installed copy carries only its target platform's manifest, so a match
    in either .cortex-plugin/ or .claude-plugin/ is accepted.
    """
    for manifest_dir in MANIFEST_DIRS.values():
        manifest = path / manifest_dir / "plugin.json"
        if not manifest.is_file():
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if data.get("name") == _PLUGIN_NAME:
            return True
    return False


def _copy_plugin(
    src: Path,
    dest: Path,
    *,
    target: TargetPlatform,
    force: bool,
    with_hook: bool = True,
) -> None:
    """Copy the built plugin to dest, shipping only the target's manifest.

    The build emits both .cortex-plugin/ and .claude-plugin/; the other
    platform's manifest directory is excluded from the copy. Everything else is
    platform-neutral: hooks/hooks.json is auto-discovered and every supported
    host substitutes ${CLAUDE_PLUGIN_ROOT} itself.
    """
    if dest.exists():
        if not force:
            console.print(
                f"[red]Destination already exists:[/red] {dest}\n  Use --force to overwrite."
            )
            raise typer.Exit(1)
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    excluded = [d for t, d in MANIFEST_DIRS.items() if t != target]
    if not with_hook:
        # Omitting the hooks tree is sufficient to disable hooks. With no
        # hooks/hooks.json to auto-discover and no inline key in the manifest,
        # there is nothing for the host to load.
        excluded.append("hooks")
    # When hooks ship, hooks/hooks.json is copied and kept: it is the single hook
    # declaration, auto-discovered by every host. It was previously deleted here
    # in favour of an inline manifest key, which is exactly what made CoCo
    # Desktop and CoCo CLI disagree.
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns(*excluded))

    # No per-platform manifest rewrite. Both CoCo Desktop and CoCo CLI substitute
    # ${CLAUDE_PLUGIN_ROOT} at config-load time (verified: argv0 arrives fully
    # resolved on both, while the env var itself is unset in the hook process), as
    # does Claude Code. Rewriting to an absolute install path was only necessary
    # while the relative-command form was being emitted.


def _validate_build(plugin_dir: Path) -> None:
    """Ensure the build exists and is valid. Exits on failure."""
    if not plugin_dir.is_dir():
        console.print(
            f"[red]Plugin build not found:[/red] {plugin_dir}\n"
            "  Run [bold]ai-rules plugin build[/bold] first."
        )
        raise typer.Exit(1)
    problems = check_artifacts(plugin_dir)
    if problems:
        console.print("[red]Plugin build is invalid:[/red]")
        for problem in problems:
            console.print(f"  - {problem}")
        console.print("\n  Run [bold]ai-rules plugin build[/bold] to rebuild.")
        raise typer.Exit(1)


@plugin_app.command()
def install(
    target: TargetPlatform = typer.Option(  # noqa: B008
        ..., help="Target platform: cortex, claude, or all"
    ),
    project: Path | None = typer.Option(None, help="Project directory for local install"),  # noqa: B008
    force: bool = typer.Option(False, help="Overwrite existing installation"),
    with_hook: bool = typer.Option(
        False,
        "--with-hook",
        help="Include the UserPromptSubmit hook. Hooks are omitted by default.",
    ),
    plugin_dir: Path = typer.Option(_PLUGIN_DIR, help="Built plugin directory"),  # noqa: B008
) -> None:
    """Install the plugin for use with CoCo (cortex), Claude Code (claude), or both (all).

    Each install ships only the target platform's manifest: .cortex-plugin/ for
    CoCo, .claude-plugin/ for Claude Code.

    Hooks are omitted by default. Add --with-hook to include the UserPromptSubmit
    hook so rules are injected automatically on every prompt.

    For global CoCo installs with hooks, this wrapper uses `cortex plugin install
    <plugin-dir>` when the cortex CLI is available. You can also run `cortex
    plugin install ./ai-coding-rules-plugin` directly.
    """
    plugin_dir = plugin_dir.resolve()
    _validate_build(plugin_dir)

    for resolved in _resolve_targets(target):
        _install_one(
            resolved,
            project=project,
            force=force,
            with_hook=with_hook,
            plugin_dir=plugin_dir,
        )


def _install_one(
    target: TargetPlatform,
    *,
    project: Path | None,
    force: bool,
    with_hook: bool,
    plugin_dir: Path,
) -> None:
    """Install the built plugin for a single concrete platform."""
    if project is not None:
        # Project-local install: always copy
        dest = _project_dest(target, project.resolve())
        _copy_plugin(plugin_dir, dest, target=target, force=force, with_hook=with_hook)
        console.print(f"[green]Installed to project:[/green] {dest}")
        if not with_hook:
            console.print(
                "  Hook not included. Use $rule-loader skill on demand. "
                "Use --with-hook to enable the plugin hook."
            )
        console.print("  Restart your assistant or run /plugin reload to activate.")
        return

    # Global install
    if target == TargetPlatform.cortex:
        cli = shutil.which("cortex")
        if cli and with_hook:
            # Native CLI install includes everything
            args = [cli, "plugin", "install", str(plugin_dir)]
            if force:
                args.append("--force")
            result = subprocess.run(args, capture_output=True, text=True)
            if result.returncode == 0:
                console.print("[green]Installed via cortex CLI (with hook).[/green]")
                if result.stdout.strip():
                    console.print(result.stdout.strip())
                return
            # If "already installed", uninstall and retry once
            if "already installed" in (result.stderr or "").lower() and force:
                subprocess.run(
                    [cli, "plugin", "uninstall", _PLUGIN_NAME],
                    capture_output=True,
                    text=True,
                )
                retry = subprocess.run(args, capture_output=True, text=True)
                if retry.returncode == 0:
                    console.print("[green]Reinstalled via cortex CLI (with hook).[/green]")
                    if retry.stdout.strip():
                        console.print(retry.stdout.strip())
                    return
            # CLI failed; fall through to manual copy
            console.print(
                f"[yellow]cortex plugin install failed (exit {result.returncode}).[/yellow]"
            )
            if result.stderr.strip():
                console.print(f"  Error: {result.stderr.strip()}")
            console.print("  Falling back to direct copy.")

        # Manual copy fallback
        dest = _global_dest(TargetPlatform.cortex)
        if not cli and not typer.confirm(
            f"cortex CLI not found. Copy plugin to {dest}?", default=False
        ):
            console.print("Aborted.")
            raise typer.Exit(0)
        _copy_plugin(plugin_dir, dest, target=target, force=force, with_hook=with_hook)
        console.print(f"[green]Installed (copy):[/green] {dest}")
        if not with_hook:
            console.print(
                "  Hook not included. Use $rule-loader skill on demand. "
                "Use --with-hook to enable the plugin hook."
            )

    else:
        # Claude: always copy (no local-path install CLI)
        dest = _global_dest(TargetPlatform.claude)
        _copy_plugin(plugin_dir, dest, target=target, force=force, with_hook=with_hook)
        console.print(f"[green]Installed:[/green] {dest}")
        console.print(
            "  Plugin will appear as ai-coding-rules@skills-dir in Claude Code.\n"
            "  Run /reload-plugins or start a new session to activate."
        )
        if not with_hook:
            console.print(
                "  Hook not included. Use $rule-loader skill on demand. "
                "Use --with-hook to enable the plugin hook."
            )


@plugin_app.command()
def uninstall(
    target: TargetPlatform = typer.Option(  # noqa: B008
        ..., help="Target platform: cortex, claude, or all"
    ),
    project: Path | None = typer.Option(None, help="Project directory for local uninstall"),  # noqa: B008
) -> None:
    """Uninstall the plugin from CoCo (cortex), Claude Code (claude), or both (all)."""
    for resolved in _resolve_targets(target):
        _uninstall_one(resolved, project)


def _uninstall_one(target: TargetPlatform, project: Path | None) -> None:
    """Uninstall the plugin from a single concrete platform."""
    dest = _project_dest(target, project.resolve()) if project is not None else _global_dest(target)

    if not dest.exists():
        console.print(f"[yellow]Not installed at:[/yellow] {dest}")
        if project is None:
            # Hint: maybe it's project-local
            cwd_dest = _project_dest(target, Path.cwd())
            if cwd_dest.exists():
                console.print(
                    f"  Found project-local install at: {cwd_dest}\n"
                    f"  Use --project . to uninstall it."
                )
        return

    if not _is_our_plugin(dest):
        console.print(
            f"[red]Safety check failed:[/red] {dest} does not contain "
            f"a plugin.json with name '{_PLUGIN_NAME}'. Refusing to remove."
        )
        raise typer.Exit(1)

    # For global cortex, try CLI first
    if project is None and target == TargetPlatform.cortex:
        cli = shutil.which("cortex")
        if cli:
            result = subprocess.run(
                [cli, "plugin", "uninstall", _PLUGIN_NAME],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                console.print("[green]Uninstalled via cortex CLI.[/green]")
                return
            # CLI failed; fall through to manual removal

    shutil.rmtree(dest)
    console.print(f"[green]Uninstalled:[/green] {dest}")
