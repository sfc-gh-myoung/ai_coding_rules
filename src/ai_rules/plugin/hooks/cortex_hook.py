"""Hook adapter for Cortex Code UserPromptSubmit hook.

Invoked by the shell hook script; wraps the rule matcher and formats
matched rules as a <system-reminder> block for injection into context.
"""

from __future__ import annotations

from pathlib import Path


def run_hook(prompt: str, rules_dir: Path, *, micro_kernel_path: Path | None = None) -> str:
    """Run the deterministic matcher and return a <system-reminder> block.

    Returns empty string if no rules matched or an error occurred.
    """
    try:
        from ai_rules.match_rules import (
            FileContext,
            build_manifest,
            load_rules_db,
            match_rules,
            resolve_dependencies,
        )
    except ImportError:
        return (
            "<system-reminder>\n"
            "⚠ ai-coding-rules: rule matcher not available. "
            "Run `pip install ai_coding_rules` to enable deterministic rule discovery.\n"
            "</system-reminder>"
        )

    import re

    words = re.split(r"[^\w./-]+", prompt.lower())
    kw_list = [w for w in words if len(w) >= 3 and "/" not in w and not w.startswith(".")]
    ext_list = [w for w in words if w.startswith(".") and len(w) > 1]
    path_list = [w for w in words if "/" in w]

    try:
        db = load_rules_db(rules_dir)
    except FileNotFoundError:
        return ""

    file_ctx = FileContext(extensions=ext_list, paths=path_list)
    scored = match_rules(kw_list, file_ctx, list(db.values()))
    if not scored:
        return ""

    matched_filenames = {sr.rule.filename for sr in scored}
    resolved, warnings = resolve_dependencies(scored, db)
    manifest = build_manifest(resolved, warnings, matched_filenames=matched_filenames)

    rule_paths = [r.get("rule_path", "") for r in manifest.get("load_sequence", [])]
    rule_paths = [p for p in rule_paths if p]
    if not rule_paths:
        return ""

    lines = ["<system-reminder>", "## AI Coding Rules — Matched Rules", ""]
    if micro_kernel_path and micro_kernel_path.exists():
        lines.append(micro_kernel_path.read_text(encoding="utf-8"))
        lines.append("")
    lines.append("## Rules to Read for This Request")
    lines.append("")
    for path in rule_paths:
        lines.append(f"- {path}")
    lines.append("")
    lines.append("Read each rule above using the Read tool before responding.")
    lines.append("</system-reminder>")
    return "\n".join(lines)
