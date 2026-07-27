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

    console.print(f"[green]Plugin built successfully:[/green] {plugin_dir}")
    console.print(f"  Rules: {rule_count}")
    console.print(f"  Script: {dest_script.relative_to(plugin_dir)}")
    console.print("  Hook: hooks/user-prompt-submit")
