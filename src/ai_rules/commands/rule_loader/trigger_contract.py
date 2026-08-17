"""Scoped trigger-count contract validator (Phase 4).

Replaces repository-wide text-grep governance checks with a focused validator
that:

1. Derives the canonical keyword-count bound (min, max) from the authoritative
   ``schemas/rule-schema.yml``: the single source of truth.
2. Verifies every *registered* contract surface expresses that combined bound
   with the correct total-vs-semantic meaning, rejecting any contradictory
   parsed bound (not merely a blocklist of historical strings).
3. Runs a full-tree completeness scan: any file that carries a total
   keyword-count bound token but is neither registered nor allowlisted fails
   the gate, so a new bound-bearing surface cannot silently drift.

Semantics
---------
- A ``5-<n>`` (or ``5–<n>`` en-dash) token on a line whose lowercased text
  mentions a keyword context (``keyword`` / ``typed entr`` / ``combined typed``)
  is a **total** bound claim and must equal the canonical maximum.
- The same token is treated as **semantic advisory** (allowed within the hard
  bound) when its line also mentions ``semantic`` or ``kw:``.
- The ``(?<!\\d)`` / ``(?!\\d)`` guards exclude date substrings
  (``sonnet-45-2025``) and percentages (``95-96%``), which are not bounds.
"""

# This module intentionally documents en-dash vs hyphen handling and regex
# escapes, so its docstrings/comments contain literal en dashes and backslashes.
# ruff: noqa: RUF002, RUF003, D301

from __future__ import annotations

import re
from pathlib import Path

import typer
import yaml

from ai_rules._shared.console import log_error, log_success
from ai_rules._shared.paths import find_project_root

# ── canonical-bound extraction ───────────────────────────────────────────────


def canonical_bounds(schema_text: str) -> tuple[int, int]:
    """Return the (min_items, max_items) declared for the Keywords field.

    Raises:
        ValueError: the schema does not declare a Keywords min/max bound.
    """
    data = yaml.safe_load(schema_text)
    fields = (data or {}).get("metadata", {}).get("required_fields", [])
    for field in fields:
        if field.get("name") == "Keywords":
            lo = field.get("min_items")
            hi = field.get("max_items")
            if isinstance(lo, int) and isinstance(hi, int):
                return lo, hi
    raise ValueError("schema does not declare a Keywords min_items/max_items bound")


# ── bound-token detection ────────────────────────────────────────────────────

# A "5-N" / "5–N" token not embedded in a longer number (excludes 45-2025, 95-96).
_BOUND_RE = re.compile(r"(?<!\d)5\s*[-\u2013]\s*(\d{1,2})(?!\d)")

_KEYWORD_CONTEXT = ("keyword", "typed entr", "combined typed")
_SEMANTIC_MARKERS = ("semantic", "kw:")


def _is_keyword_context(line_lower: str) -> bool:
    return any(marker in line_lower for marker in _KEYWORD_CONTEXT)


def _is_semantic(line_lower: str) -> bool:
    return any(marker in line_lower for marker in _SEMANTIC_MARKERS)


def has_total_bound_token(text: str) -> bool:
    """True if any line carries a *total* keyword-count bound token.

    Total = keyword-context line that is not semantic-qualified. Semantic-only
    guidance (``5-7 semantic kw: keywords``) is not a total bound and does not
    require registration.
    """
    for raw in text.splitlines():
        low = raw.lower()
        if _is_keyword_context(low) and not _is_semantic(low) and _BOUND_RE.search(raw):
            return True
    return False


def surface_violations(rel_path: str, text: str, min_items: int, max_items: int) -> list[str]:
    """Return contract violations for a single registered surface."""
    violations: list[str] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        low = raw.lower()
        if not _is_keyword_context(low):
            continue
        for m in _BOUND_RE.finditer(raw):
            n = int(m.group(1))
            token = m.group(0)
            if _is_semantic(low):
                # Semantic advisory: must stay within the hard bound.
                if n > max_items:
                    violations.append(
                        f"{rel_path}:{lineno}: semantic advisory '{token}' exceeds "
                        f"hard maximum {max_items}"
                    )
            elif n != max_items:
                violations.append(
                    f"{rel_path}:{lineno}: total keyword bound '{token}' contradicts "
                    f"schema-derived {min_items}-{max_items}"
                )
    return violations


# ── registry + allowlist ─────────────────────────────────────────────────────

# Surfaces that carry the combined trigger-count contract. Each must express the
# schema-derived bound and must not contradict it.
REGISTERED_SURFACES: frozenset[str] = frozenset(
    {
        "schemas/rule-schema.yml",
        "rules/002-rule-governance.md",
        "rules/002a-rule-creation.md",
        "rules/002b-rule-update.md",
        "rules/002e-schema-validator-usage.md",
        "rules/002f-schema-validator-advanced.md",
        "rules/examples/002a-rule-template.md",
        "docs/USING_RULE_CREATOR_SKILL.md",
        "CONTRIBUTING.md",
        "src/ai_rules/commands/rule_loader/keywords/app.py",
        "src/ai_rules/commands/rule_loader/keywords/client.py",
        "src/ai_rules/commands/new.py",
        "src/ai_rules/match_rules.py",
        "schemas/README.md",
        "skills/rule-creator/tests/test_cases.yaml",
        "skills/rule-creator/workflows/validation.md",
    }
)

# Files that carry bound-like tokens that are NOT the trigger contract
# (incidental domain content). Kept explicit for documentation; the keyword-
# context detector already excludes these because their tokens are not on
# keyword-context lines.
ALLOWLISTED_SURFACES: frozenset[str] = frozenset(
    {
        "rules/940-business-analytics.md",
        "rules/109a-snowflake-notebooks-tutorials.md",
        "rules/109e-snowflake-notebook-checkpoints.md",
        "rules/examples/116-cortex-search-service-example.md",
        # Generic Cortex client illustrative example prompt (API usage), not the
        # rule trigger-count contract.
        "src/ai_rules/cortex/README.md",
        "src/ai_rules/cortex/client.py",
        # Byte-identical vendored copy of the registered matcher source
        # (src/ai_rules/match_rules.py); its bound literals are governed there.
        "skills/rule-loader/scripts/match_rules.py",
    }
)

# Directories excluded from the completeness scan: generated output, tests with
# their own schema doubles, historical artifacts, and tooling caches.
_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        ".uv-cache",
        ".pytest_cache",
        ".ruff_cache",
        ".workbench",
        "tests",
        "reviews",
        "plans",
        ".snowflake",
        ".cortex",
        "agent_eval",
        "results",
        "ai-coding-rules-plugin",
        "htmlcov",
    }
)
_EXCLUDED_FILES: frozenset[str] = frozenset({"CHANGELOG.md", "README.md"})
_SCANNED_SUFFIXES: frozenset[str] = frozenset({".md", ".yml", ".yaml", ".py"})


def iter_scanned_files(root: Path):
    """Yield (relative-posix-path, Path) for in-scope files under ``root``."""
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in _SCANNED_SUFFIXES:
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in _EXCLUDED_DIRS for part in rel_parts):
            continue
        rel = path.relative_to(root).as_posix()
        if rel in _EXCLUDED_FILES:
            continue
        yield rel, path


def validate_trigger_contract(root: Path) -> list[str]:
    """Validate the trigger-count contract across the repository.

    Returns a list of violation strings; empty means the contract is consistent.
    """
    violations: list[str] = []

    schema_path = root / "schemas" / "rule-schema.yml"
    if not schema_path.is_file():
        return [f"schema not found at {schema_path}"]
    try:
        min_items, max_items = canonical_bounds(schema_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"cannot derive canonical bound: {exc}"]

    # 1. Every registered surface must exist and must not contradict the bound.
    for rel in sorted(REGISTERED_SURFACES):
        surface = root / rel
        if not surface.is_file():
            violations.append(f"registered surface missing: {rel}")
            continue
        violations.extend(
            surface_violations(rel, surface.read_text(encoding="utf-8"), min_items, max_items)
        )

    # 2. Completeness: no unregistered, non-allowlisted file may carry a total
    #    keyword-count bound token.
    known = REGISTERED_SURFACES | ALLOWLISTED_SURFACES
    for rel, path in iter_scanned_files(root):
        if rel in known:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if has_total_bound_token(text):
            violations.append(
                f"{rel}: carries a total keyword-count bound but is not a registered "
                f"contract surface (register it in trigger_contract.py or allowlist it)"
            )

    return violations


def validate_trigger_contract_cmd() -> None:
    """Validate that every trigger-count contract surface agrees on 5-11.

    Exit 0 when all registered surfaces express the schema-derived bound and no
    unregistered surface carries a total keyword-count bound; exit 1 otherwise.
    """
    root = find_project_root()
    violations = validate_trigger_contract(root)
    if violations:
        for v in violations:
            log_error(v)
        log_error(f"{len(violations)} trigger-contract violation(s)")
        raise typer.Exit(1)
    log_success("trigger contract consistent: all surfaces agree on the schema-derived bound")
