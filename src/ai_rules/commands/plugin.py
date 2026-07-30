"""ai-rules plugin build — assemble the distributable plugin directory."""

from __future__ import annotations

import shutil
from pathlib import Path

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


def check_artifacts(plugin_dir: Path) -> list[str]:
    """Validate a built plugin directory against the artifact contract.

    Checks both directions: every ``EXPECTED_ARTIFACTS`` entry is present, and
    every emitted file is either an expected artifact or lives under an
    ``EXPECTED_TREES`` prefix. Also confirms the generated manifest parses.

    Args:
        plugin_dir: Root of a built plugin directory.

    Returns:
        Human-readable problem descriptions. Empty when the contract holds.
    """
    import json

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

    manifest = plugin_dir / ".cortex-plugin" / "plugin.json"
    if manifest.is_file():
        try:
            json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"invalid plugin.json: {exc}")

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
    micro_kernel_src = (
        _REPO_ROOT / "src" / "ai_rules" / "progressive_eval" / "micro_kernel_content.md"
    )
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
