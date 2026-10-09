"""Keyword formatting, file update, and JSONL emission utilities."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from ai_rules._shared.console import log_warning

# ---------------------------------------------------------------------------
# Frontmatter helpers (dual-parse; schema v3.5)
# ---------------------------------------------------------------------------

_FRONTMATTER_FENCE_RE = re.compile(r"^---\s*$")


def _parse_frontmatter_block(content: str) -> dict[str, Any] | None:
    """Return the YAML frontmatter mapping if `content` begins with a `---` fence.

    Returns None when no frontmatter fence is present, when the closing fence is
    missing within the first 200 lines, or when the block does not parse to a
    mapping.
    """
    lines = content.split("\n")
    if not lines or not _FRONTMATTER_FENCE_RE.match(lines[0]):
        return None
    for idx in range(1, min(len(lines), 200)):
        if _FRONTMATTER_FENCE_RE.match(lines[idx]):
            block = "\n".join(lines[1:idx])
            try:
                data = yaml.safe_load(block)
            except yaml.YAMLError:
                return None
            return data if isinstance(data, dict) else None
    return None


# ---------------------------------------------------------------------------
# Keyword line formatting
# ---------------------------------------------------------------------------


def format_keywords_line(keywords: list[str], style: str = "inline") -> str:
    r"""Format keywords as a metadata line.

    Args:
        keywords: keyword strings (already typed with kw:/ext:/file:/dir: prefixes).
        style: ``"inline"`` (default) emits ``**Keywords:** k1, k2, ...``
            ``"yaml"`` emits the v3.5 canonical YAML block form.
    """
    if style == "yaml":
        if not keywords:
            return "keywords: []"
        return "keywords:\n" + "\n".join(f"  - {k}" for k in keywords)
    return f"**Keywords:** {', '.join(keywords)}"


# ---------------------------------------------------------------------------
# File update helpers
# ---------------------------------------------------------------------------


def _update_keywords_in_frontmatter(content: str, new_keywords: list[str]) -> tuple[str, bool]:
    """Replace `keywords:` inside the leading YAML frontmatter block.

    Returns (new_content, updated). Returns (content, False) when no frontmatter
    block is present or when the value is unchanged.
    """
    lines = content.split("\n")
    if not lines or not _FRONTMATTER_FENCE_RE.match(lines[0]):
        return content, False
    close_idx: int | None = None
    for idx in range(1, min(len(lines), 200)):
        if _FRONTMATTER_FENCE_RE.match(lines[idx]):
            close_idx = idx
            break
    if close_idx is None:
        return content, False

    body = "\n".join(lines[1:close_idx])
    try:
        data = yaml.safe_load(body) or {}
    except yaml.YAMLError:
        return content, False
    if not isinstance(data, dict):
        return content, False

    existing = data.get("keywords")
    normalized_existing: list[str] = []
    if isinstance(existing, list):
        normalized_existing = [str(k).strip() for k in existing if str(k).strip()]
    elif isinstance(existing, str):
        normalized_existing = [k.strip() for k in existing.split(",") if k.strip()]
    if normalized_existing == new_keywords:
        return content, False

    data["keywords"] = list(new_keywords)
    new_body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).rstrip("\n")
    new_content = "---\n" + new_body + "\n---" + "\n".join(["", *lines[close_idx + 1 :]])
    return new_content, True


def update_keywords_in_file(file_path: Path, new_keywords: list[str]) -> bool:
    """Update the keywords list in a rule file (dual-parse: v3.5 YAML → inline fallback).

    Args:
        file_path: Path to rule file
        new_keywords: New keywords to set

    Returns:
        True if updated, False if no change needed
    """
    content = file_path.read_text(encoding="utf-8")

    # Canonical v3.5 path: rewrite the `keywords:` key inside YAML frontmatter.
    if _parse_frontmatter_block(content) is not None:
        new_content, updated = _update_keywords_in_frontmatter(content, new_keywords)
        if not updated:
            return False
        file_path.write_text(new_content, encoding="utf-8")
        return True

    # Fallback: inline **Keywords:** line rewrite (pre-v3.5 rules).
    pattern = r"(\*\*Keywords:\*\*\s*)(.+)"
    new_line = format_keywords_line(new_keywords, style="inline")

    new_content, count = re.subn(pattern, new_line, content, count=1)

    if count == 0:
        log_warning(f"No **Keywords:** field found in {file_path}")
        return False

    if new_content == content:
        return False

    file_path.write_text(new_content, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# JSONL rationale emission
# ---------------------------------------------------------------------------


def _emit_rationale_jsonl(results: list, output_path: Path) -> int:
    """Append per-keyword rationale JSONL entries to ``output_path``.

    T7: one JSON line per (rule, keyword) pair. Skips entries with no rationale.

    Args:
        results: Extraction results (list of ExtractionResult) in order produced.
        output_path: Destination JSONL file (created with parent dirs).

    Returns:
        Number of JSONL lines actually appended.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).isoformat()
    emitted = 0
    with output_path.open("a", encoding="utf-8") as fh:
        for result in results:
            for kw in result.suggested_keywords:
                rationale_text = (result.rationale_map or {}).get(kw, "")
                if not rationale_text:
                    continue
                entry = {
                    "rule_path": str(result.file_path),
                    "keyword": kw,
                    "rationale": rationale_text,
                    "timestamp": timestamp,
                }
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
                emitted += 1
    return emitted
