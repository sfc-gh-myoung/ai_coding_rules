"""Rule front-matter metadata extraction for the evaluator.

Parses typed ``Keywords``, ``ContextTier``, and ``TokenBudget``
from rule files (schema v3.3+). Used by the trigger-evidence validator to
cross-check fixtures against the rules they claim to load.

v3.3: typed ``Keywords`` entries (``ext:``, ``file:``, ``dir:``, ``kw:``)
serve as trigger evidence. All four prefix kinds are parsed into separate
categorised fields on ``RuleMetadata`` and combined into the ``triggers`` tuple.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

RE_KEYWORDS = re.compile(r"^\*\*Keywords:\*\*\s*(.*)$", re.IGNORECASE | re.MULTILINE)
RE_DEPENDS = re.compile(r"^\*\*Depends:\*\*\s*(.*)$", re.IGNORECASE | re.MULTILINE)
RE_CONTEXT_TIER = re.compile(r"^\*\*ContextTier:\*\*\s*(.*)$", re.IGNORECASE | re.MULTILINE)
RE_SCHEMA_VERSION = re.compile(r"^\*\*SchemaVersion:\*\*\s*(.*)$", re.IGNORECASE | re.MULTILINE)
RE_RULE_VERSION = re.compile(r"^\*\*RuleVersion:\*\*\s*v?(.*)$", re.IGNORECASE | re.MULTILINE)
RE_LAST_UPDATED = re.compile(r"^\*\*LastUpdated:\*\*\s*(.*)$", re.IGNORECASE | re.MULTILINE)

_FRONTMATTER_FENCE_RE = re.compile(r"^---\s*$")


def _parse_frontmatter(content: str) -> dict[str, Any] | None:
    """Return the YAML frontmatter mapping if `content` begins with `---`."""
    lines = content.split("\n")
    if not lines or not _FRONTMATTER_FENCE_RE.match(lines[0]):
        return None
    for idx in range(1, min(len(lines), 200)):
        if _FRONTMATTER_FENCE_RE.match(lines[idx]):
            body = "\n".join(lines[1:idx])
            try:
                data = yaml.safe_load(body)
            except yaml.YAMLError:
                return None
            return data if isinstance(data, dict) else None
    return None


def _flatten_yaml_keywords(value: Any) -> str:
    """Return a comma-separated string form of a YAML keywords list/string."""
    if not value:
        return ""
    if isinstance(value, list):
        return ", ".join(str(k).strip() for k in value if str(k).strip())
    return str(value).strip()


def _flatten_yaml_depends(value: Any) -> str:
    """Flatten a YAML depends mapping/list into the inline required:foo, optional:bar form."""
    if not value:
        return ""
    entries: list[str] = []
    if isinstance(value, dict):
        for key in ("required", "optional"):
            for item in value.get(key) or []:
                if not item:
                    continue
                name = str(item).strip()
                if not name.endswith(".md"):
                    name = f"{name}.md"
                entries.append(f"{key}:{name}")
    elif isinstance(value, list):
        for item in value:
            if not item:
                continue
            name = str(item).strip()
            if ":" not in name:
                name = f"required:{name}"
            prefix, rest = name.split(":", 1)
            if not rest.endswith(".md"):
                rest = f"{rest}.md"
            entries.append(f"{prefix}:{rest}")
    return ", ".join(entries)


@dataclass(frozen=True)
class RuleMetadata:
    """Parsed rule metadata used by the evaluator."""

    path: Path
    """Path relative to the project root, e.g. ``rules/100-snowflake-core.md``."""

    keywords: tuple[str, ...] = ()
    """Lower-cased keyword tokens parsed from ``Keywords:``."""

    triggers: tuple[str, ...] = ()
    """Typed trigger tokens (e.g. ``ext:.py``, ``kw:streamlit``).

    In schema v3.3 this is the union of all four typed-prefix kinds from
    ``Keywords:`` (``kw:``, ``ext:``, ``file:``, ``dir:``).
    """

    typed_kw: tuple[str, ...] = ()
    """``kw:`` values from typed ``Keywords:`` (without prefix, lowercased)."""

    typed_ext: tuple[str, ...] = ()
    """``ext:`` values from typed ``Keywords:`` (without prefix, e.g. ``.py``)."""

    typed_file: tuple[str, ...] = ()
    """``file:`` values from typed ``Keywords:`` (without prefix, e.g. ``Dockerfile``)."""

    typed_dir: tuple[str, ...] = ()
    """``dir:`` values from typed ``Keywords:`` (without prefix, e.g. ``tests/``)."""

    context_tier: str = ""
    schema_version: str = ""
    rule_version: str = ""
    """Parsed ``RuleVersion`` value (``vX.Y.Z`` form, leading ``v`` stripped)."""
    last_updated: str = ""
    """Parsed ``LastUpdated`` value (typically ``YYYY-MM-DD``)."""
    line_count: int = 0
    """Total line count of the rule file (used for citation validation)."""

    trigger_kinds: frozenset[str] = field(default_factory=frozenset)
    """Set of ``kw``/``ext``/``file``/``dir`` kinds present in triggers."""

    depends: tuple[str, ...] = ()
    """Rule paths this rule depends on (parsed from ``**Depends:**`` line, normalized to ``rules/<name>.md``).
    Union of required + optional buckets for backward-compatible callers."""

    depends_required: tuple[str, ...] = ()
    """Subset of ``depends`` carrying the ``required:`` prefix (or unprefixed in transitional mode)."""

    depends_optional: tuple[str, ...] = ()
    """Subset of ``depends`` carrying the ``optional:`` prefix."""

    def trigger_values(self, kind: str) -> tuple[str, ...]:
        """Return values for triggers of the given kind (without prefix)."""
        prefix = f"{kind}:"
        return tuple(t[len(prefix) :] for t in self.triggers if t.startswith(prefix))


def _split_csv(raw: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in raw.split(",") if part.strip())


def split_depends_buckets(raw: str) -> tuple[list[str], list[str]]:
    """Split a Depends value into (required_names, optional_names).

    Names are bare filenames (not prefixed with ``rules/``). Unprefixed
    entries default to required for backward compatibility. If a name
    lacks a ``.md`` extension, one is appended.
    """
    required: list[str] = []
    optional: list[str] = []
    for entry in _split_csv(raw):
        if entry.lower() in {"none", "—", "-", ""}:
            continue
        bucket = "required"
        payload = entry
        lowered = entry.lower()
        if lowered.startswith("required:"):
            bucket = "required"
            payload = entry.split(":", 1)[1].strip()
        elif lowered.startswith("optional:"):
            bucket = "optional"
            payload = entry.split(":", 1)[1].strip()
        if not payload:
            continue
        if not payload.endswith(".md"):
            payload = payload + ".md"
        if bucket == "required":
            required.append(payload)
        else:
            optional.append(payload)
    return required, optional


def _split_depends(raw: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split a Depends value into (required_paths, optional_paths).

    Each path is normalized to ``rules/<filename>.md``. Unprefixed entries
    default to required for transitional backward compatibility.
    """
    required: list[str] = []
    optional: list[str] = []
    for entry in _split_csv(raw):
        if entry.lower() in {"none", "—", "-", ""}:
            continue
        bucket = "required"
        payload = entry
        lowered = entry.lower()
        if lowered.startswith("required:"):
            bucket = "required"
            payload = entry.split(":", 1)[1].strip()
        elif lowered.startswith("optional:"):
            bucket = "optional"
            payload = entry.split(":", 1)[1].strip()
        if not payload:
            continue
        normalized = f"rules/{payload}" if not payload.startswith("rules/") else payload
        if bucket == "required":
            required.append(normalized)
        else:
            optional.append(normalized)
    return tuple(required), tuple(optional)


def parse_rule_metadata(path: Path, content: str) -> RuleMetadata:
    """Parse metadata from a rule file's content (dual-parse: v3.5 frontmatter → inline fallback).

    v3.5: YAML frontmatter (`---`-fenced block at top-of-file) is the canonical
    metadata form. When present, ``keywords`` and ``depends`` are read from the
    parsed YAML mapping and normalized to the same inline string form the
    downstream splitters expect.

    v3.3/v3.4 fallback: inline ``**Field:**`` markers.
    """
    fm = _parse_frontmatter(content)
    if fm is not None:
        keywords_raw = _flatten_yaml_keywords(fm.get("keywords"))
        depends_raw = _flatten_yaml_depends(fm.get("depends"))
        tier_raw = str(fm.get("context_tier") or "").strip()
        schema_raw = str(fm.get("schema_version") or "").strip()
        rv = str(fm.get("rule_version") or "").strip()
        rule_version_raw = rv[1:] if rv.startswith("v") else rv
        last_updated_raw = str(fm.get("last_updated") or "").strip()
    else:
        keywords_raw = _first_match(RE_KEYWORDS, content)
        depends_raw = _first_match(RE_DEPENDS, content)
        tier_raw = _first_match(RE_CONTEXT_TIER, content)
        schema_raw = _first_match(RE_SCHEMA_VERSION, content)
        rule_version_raw = _first_match(RE_RULE_VERSION, content)
        last_updated_raw = _first_match(RE_LAST_UPDATED, content)

    keywords = tuple(kw.lower() for kw in _split_csv(keywords_raw))

    # Build four categorised lists from typed Keywords (v3.3+).
    _all_typed = _split_csv(keywords_raw)
    t_kw = tuple(t[3:] for t in _all_typed if t.startswith("kw:"))
    t_ext = tuple(t[4:] for t in _all_typed if t.startswith("ext:"))
    t_file = tuple(t[5:] for t in _all_typed if t.startswith("file:"))
    t_dir = tuple(t[4:] for t in _all_typed if t.startswith("dir:"))

    triggers = tuple(t for t in _all_typed if t.startswith(("kw:", "ext:", "file:", "dir:")))

    kinds = frozenset(t.split(":", 1)[0] for t in triggers if ":" in t)
    depends_required, depends_optional = _split_depends(depends_raw)
    depends = depends_required + depends_optional
    line_count = content.count("\n") + (0 if content.endswith("\n") else 1) if content else 0

    return RuleMetadata(
        path=path,
        keywords=keywords,
        triggers=triggers,
        typed_kw=t_kw,
        typed_ext=t_ext,
        typed_file=t_file,
        typed_dir=t_dir,
        context_tier=tier_raw,
        schema_version=schema_raw,
        rule_version=rule_version_raw,
        last_updated=last_updated_raw,
        line_count=line_count,
        trigger_kinds=kinds,
        depends=depends,
        depends_required=depends_required,
        depends_optional=depends_optional,
    )


def _first_match(pattern: re.Pattern[str], content: str) -> str:
    match = pattern.search(content)
    return match.group(1).strip() if match else ""


def load_rules_metadata(rules_dir: Path) -> dict[str, RuleMetadata]:
    """Load metadata for every ``*.md`` rule under ``rules_dir``.

    The returned dict is keyed by the path relative to the rules directory's
    parent (e.g. ``rules/100-snowflake-core.md``) so it matches how fixtures
    reference rules.
    """
    rules_dir = rules_dir.resolve()
    project_root = rules_dir.parent
    out: dict[str, RuleMetadata] = {}
    skip_names = {"README.md"}
    for path in sorted(rules_dir.glob("*.md")):
        if path.name in skip_names:
            continue
        rel = path.resolve().relative_to(project_root).as_posix()
        out[rel] = parse_rule_metadata(Path(rel), path.read_text(encoding="utf-8"))
    return out
