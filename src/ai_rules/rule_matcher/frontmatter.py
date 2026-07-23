"""YAML frontmatter parser for rule files.

Consolidates the three existing parsing locations:
  - commands/index.py:_parse_frontmatter()
  - rule_loader_eval/rules_meta.py:_parse_frontmatter()
  - commands/keywords.py:_parse_frontmatter_block()

Handles rules with >2 ``---`` fences by consuming only the first two.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

_FENCE_RE = re.compile(r"^---\s*$")
_TOKEN_BUDGET_RE = re.compile(r"~?(\d+)")

TIER_ORDER: dict[str, int] = {
    "Critical": 0,
    "High": 1,
    "Medium": 2,
    "Low": 3,
}


@dataclass
class TypedKeywords:
    kw: list[str] = field(default_factory=list)
    ext: list[str] = field(default_factory=list)
    file_patterns: list[str] = field(default_factory=list)
    dir_patterns: list[str] = field(default_factory=list)


@dataclass
class RuleFrontmatter:
    filename: str
    path: Path
    context_tier: str
    token_budget: int | None
    depends: dict[str, list[str]] | None
    typed_kw: list[str]
    typed_ext: list[str]
    file_patterns: list[str]
    dir_patterns: list[str]
    rule_version: str
    description: str


def _parse_raw_frontmatter(content: str) -> dict[str, Any] | None:
    """Return the YAML frontmatter dict from the first ``---`` fence pair.

    Only the first two fences delimit frontmatter; additional ``---`` lines in
    the body are ignored.
    """
    lines = content.split("\n")
    if not lines or not _FENCE_RE.match(lines[0]):
        return None
    for idx in range(1, min(len(lines), 200)):
        if _FENCE_RE.match(lines[idx]):
            block = "\n".join(lines[1:idx])
            try:
                data = yaml.safe_load(block)
            except yaml.YAMLError:
                return None
            return data if isinstance(data, dict) else None
    return None


def parse_typed_keywords(raw_keywords: list[Any]) -> TypedKeywords:
    """Split the raw ``keywords:`` list by prefix into typed match lists.

    Prefix map::

        kw:   → keyword phrases (bare entries without a prefix also treated as kw:)
        ext:  → file extensions (e.g. ``.py``, ``.sql``)
        file: → file glob patterns (e.g. ``auth.py``, ``*.config``)
        dir:  → directory glob patterns (e.g. ``src/``, ``tests/``)
    """
    kw: list[str] = []
    ext: list[str] = []
    file_pats: list[str] = []
    dir_pats: list[str] = []

    for item in raw_keywords or []:
        s = str(item).strip()
        if not s:
            continue
        if s.startswith("ext:"):
            ext.append(s[4:])
        elif s.startswith("file:"):
            file_pats.append(s[5:])
        elif s.startswith("dir:"):
            dir_pats.append(s[4:])
        else:
            kw.append(s[3:] if s.startswith("kw:") else s)

    return TypedKeywords(kw=kw, ext=ext, file_patterns=file_pats, dir_patterns=dir_pats)


def _parse_token_budget(value: Any) -> int | None:
    if value is None:
        return None
    m = _TOKEN_BUDGET_RE.search(str(value))
    return int(m.group(1)) if m else None


def _parse_depends(value: Any) -> dict[str, list[str]] | None:
    """Normalise the ``depends:`` value to ``{required: [...], optional: [...]}``.

    Accepts:
    - ``None`` / absent key → return ``None``
    - dict with ``required``/``optional`` lists (current schema)
    - flat list of strings (legacy)
    """
    if not value:
        return None
    if isinstance(value, dict):
        return {k: [str(v) for v in (value.get(k) or [])] for k in ("required", "optional")}
    if isinstance(value, list):
        # Legacy flat list: items may be "required:foo.md" or bare "foo.md"
        required: list[str] = []
        optional: list[str] = []
        for item in value:
            s = str(item).strip()
            if s.startswith("optional:"):
                optional.append(s[9:])
            else:
                required.append(s[9:] if s.startswith("required:") else s)
        return {"required": required, "optional": optional}
    return None


def parse_rule_file(path: Path) -> RuleFrontmatter | None:
    """Parse a single rule ``.md`` file and return a ``RuleFrontmatter``.

    Returns ``None`` and logs a warning when the file cannot be read or has no
    valid frontmatter (non-fatal; those rules are simply excluded from the DB).
    """
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Cannot read rule file %s: %s", path, exc)
        return None

    data = _parse_raw_frontmatter(content)
    if data is None:
        logger.debug("No frontmatter in %s — skipped", path.name)
        return None

    raw_kw = data.get("keywords") or []
    typed = parse_typed_keywords(raw_kw)

    tier = str(data.get("context_tier") or "Low")

    return RuleFrontmatter(
        filename=path.name,
        path=path,
        context_tier=tier,
        token_budget=_parse_token_budget(data.get("token_budget")),
        depends=_parse_depends(data.get("depends")),
        typed_kw=typed.kw,
        typed_ext=typed.ext,
        file_patterns=typed.file_patterns,
        dir_patterns=typed.dir_patterns,
        rule_version=str(data.get("rule_version") or ""),
        description=str(data.get("description") or ""),
    )


def load_rules_db(rules_dir: Path) -> dict[str, RuleFrontmatter]:
    """Scan *rules_dir* for ``*.md`` files and return a filename-keyed dict.

    Skips files without valid frontmatter with a debug log (non-fatal).
    Raises ``FileNotFoundError`` when *rules_dir* does not exist (caller should
    treat this as exit-code-2 fatal).
    """
    if not rules_dir.is_dir():
        raise FileNotFoundError(f"rules-dir not found: {rules_dir}")

    db: dict[str, RuleFrontmatter] = {}
    for md_path in sorted(rules_dir.glob("*.md")):
        rule = parse_rule_file(md_path)
        if rule is not None:
            db[md_path.name] = rule
    return db
