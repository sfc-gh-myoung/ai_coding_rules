"""One-shot in-place migration: rule schema v3.2 -> v3.3.

Derives v3.3 typed `**Keywords:**` from each rule's *own* existing
`**Keywords:**` (untyped semantic terms) and `**LoadTrigger:**`
(typed `kind:value`) lines, then deletes `**LoadTrigger:**` and bumps
`**SchemaVersion:**` to v3.3. Also rewrites `**Depends:**` to add
`required:` prefix to every bare-name entry.

Invariants:

* **Idempotent.** Running twice produces no diff on the second run.
* **Body untouched.** Only the four metadata-block lines are mutated.
* **No information loss.** Every existing `kw` term and every
  `LoadTrigger` entry appears in the new `**Keywords:**` line.
* **No Depends loss.** Every existing `Depends:` entry is preserved with
  `required:` prefix unless the value is `None`/`-`/`-`/empty.

Usage::

    uv run python scripts/migrate_v32_to_v33.py rules/
    uv run python scripts/migrate_v32_to_v33.py --dry-run rules/
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RE_KEYWORDS = re.compile(r"^\*\*Keywords:\*\*\s*(.*)$", re.MULTILINE | re.IGNORECASE)
RE_LOAD_TRIGGER = re.compile(r"^\*\*LoadTrigger:\*\*\s*(.*)$\n?", re.MULTILINE | re.IGNORECASE)
RE_DEPENDS = re.compile(r"^\*\*Depends:\*\*\s*(.*)$", re.MULTILINE | re.IGNORECASE)
RE_SCHEMA_VERSION = re.compile(r"^(\*\*SchemaVersion:\*\*\s*)(.*)$", re.MULTILINE | re.IGNORECASE)

SKIP_NAMES = {"RULES_INDEX.md", "README.md", "CHANGELOG.md"}

TYPED_PREFIXES = ("kw:", "ext:", "file:", "dir:")
DEPENDS_PREFIXES = ("required:", "optional:")
DEPENDS_NONE_TOKENS = {"none", "-", ""}


def _split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _typed_keyword(term: str) -> str:
    """Return ``term`` formatted as a typed Keywords entry.

    LoadTrigger entries already carry a typed prefix and are returned
    verbatim. Bare semantic terms are lowercased and emitted as ``kw:``.
    """
    stripped = term.strip()
    if not stripped:
        return ""
    if stripped.lower().startswith(TYPED_PREFIXES):
        return stripped
    return f"kw:{stripped.lower()}"


def merge_keywords(keywords_value: str, load_trigger_value: str) -> str:
    """Merge legacy Keywords + LoadTrigger lines into a v3.3 typed Keywords value.

    LoadTrigger entries come first (already typed), then ``kw:`` terms
    derived from the legacy semantic Keywords list. Duplicates are
    eliminated while preserving first-seen order.
    """
    merged: list[str] = []
    seen: set[str] = set()

    for entry in _split_csv(load_trigger_value):
        normalized = entry.strip()
        if not normalized:
            continue
        if normalized not in seen:
            merged.append(normalized)
            seen.add(normalized)

    for entry in _split_csv(keywords_value):
        typed = _typed_keyword(entry)
        if not typed:
            continue
        if typed not in seen:
            merged.append(typed)
            seen.add(typed)

    return ", ".join(merged)


def rewrite_depends(value: str) -> str:
    """Rewrite a legacy ``Depends:`` value to v3.3 prefixed form.

    ``None`` (and similar empty markers) is preserved as-is. Every other
    bare-name entry is prefixed with ``required:``. Already-prefixed
    entries (``required:``/``optional:``) are kept verbatim for
    idempotency.
    """
    stripped = value.strip()
    if stripped.lower() in DEPENDS_NONE_TOKENS:
        return stripped or "None"

    parts: list[str] = []
    for entry in _split_csv(stripped):
        normalized = entry.strip()
        if not normalized:
            continue
        if normalized.lower().startswith(DEPENDS_PREFIXES):
            parts.append(normalized)
        else:
            parts.append(f"required:{normalized}")
    return ", ".join(parts) if parts else "None"


def migrate_content(content: str) -> tuple[str, bool]:
    """Apply the migration to a single rule's text.

    Returns ``(new_content, changed)``.
    """
    original = content

    keywords_match = RE_KEYWORDS.search(content)
    load_trigger_match = RE_LOAD_TRIGGER.search(content)

    keywords_value = keywords_match.group(1) if keywords_match else ""
    load_trigger_value = load_trigger_match.group(1) if load_trigger_match else ""

    # Build merged keywords; if neither line exists, leave Keywords alone.
    if keywords_match:
        merged = merge_keywords(keywords_value, load_trigger_value)
        new_keywords_line = f"**Keywords:** {merged}" if merged else "**Keywords:**"
        content = (
            content[: keywords_match.start()] + new_keywords_line + content[keywords_match.end() :]
        )

    # Drop the LoadTrigger line entirely (including its trailing newline).
    content = RE_LOAD_TRIGGER.sub("", content)

    # Rewrite Depends to v3.3 prefix form.
    depends_match = RE_DEPENDS.search(content)
    if depends_match:
        new_depends_value = rewrite_depends(depends_match.group(1))
        new_depends_line = f"**Depends:** {new_depends_value}"
        content = (
            content[: depends_match.start()] + new_depends_line + content[depends_match.end() :]
        )

    # Bump SchemaVersion to v3.3.
    def _bump(match: re.Match[str]) -> str:
        return f"{match.group(1)}v3.3"

    content = RE_SCHEMA_VERSION.sub(_bump, content, count=1)

    return content, content != original


def iter_rule_files(target: Path) -> list[Path]:
    """Return ``rules/*.md`` files under ``target``, excluding skip names."""
    if target.is_file():
        return [target] if target.suffix == ".md" and target.name not in SKIP_NAMES else []
    return sorted(p for p in target.glob("*.md") if p.is_file() and p.name not in SKIP_NAMES)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    description = (__doc__ or "").splitlines()[0] if __doc__ else "Migrate rules to v3.3"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "target",
        type=Path,
        help="Rule file or directory of rules to migrate.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report which files would change without writing.",
    )
    args = parser.parse_args(argv)

    files = iter_rule_files(args.target)
    if not files:
        print(f"No rule files found at {args.target}", file=sys.stderr)
        return 1

    changed_count = 0
    for path in files:
        before = path.read_text(encoding="utf-8")
        after, changed = migrate_content(before)
        if changed:
            changed_count += 1
            if args.dry_run:
                print(f"would migrate: {path}")
            else:
                path.write_text(after, encoding="utf-8")
                print(f"migrated: {path}")

    total = len(files)
    if args.dry_run:
        print(f"\n{changed_count}/{total} file(s) would change.")
    else:
        print(f"\n{changed_count}/{total} file(s) migrated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
