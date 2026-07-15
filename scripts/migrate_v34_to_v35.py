"""One-shot in-place migration: rule schema v3.3/v3.4 -> v3.5.

Converts each rule's inline `## Metadata` block + `### Dependencies` prose
subsection into a canonical v3.5 YAML frontmatter block at top-of-file.
Deletes the inline metadata block and the `### Dependencies` prose subsection,
preserving each dependency's one-line justification (extracted from the prose
list) as an inline YAML comment on the corresponding `depends:` item (Option B).

Invariants:

* **Idempotent.** Running twice produces no diff on the second run — files that
  already begin with a `---` frontmatter fence are skipped.
* **Body untouched (outside metadata).** Only the inline `## Metadata` block,
  the `### Dependencies` prose subsection, and the newly-written frontmatter
  block are mutated. `## Scope`, `## References` (minus the Dependencies
  subsection), `## Contract`, etc. are byte-preserved.
* **No information loss.** Every prose Dependencies justification appears as a
  YAML comment on the matching `depends:` entry when a match is found.
* **Version discipline.** Each migrated rule receives a MAJOR bump
  (`vN.M.P` → `v{N+1}.0.0`) and `last_updated` is stamped to today.

Usage::

    python scripts/migrate_v34_to_v35.py --dry-run --output-report /tmp/dry_run.json
    python scripts/migrate_v34_to_v35.py --canary rules/206-python-pytest.md \
        --output-report .workbench/results/canary_migration_report.json
    python scripts/migrate_v34_to_v35.py --rules-dir rules/ \
        --output-report .workbench/results/full_migration_report.json \
        --changelog-output CHANGELOG_MIGRATION.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

RE_METADATA_HEADER = re.compile(r"^## Metadata\s*$", re.MULTILINE)
RE_SCHEMA_VERSION = re.compile(r"^\*\*SchemaVersion:\*\*\s*(.+)$", re.MULTILINE | re.IGNORECASE)
RE_RULE_VERSION = re.compile(r"^\*\*RuleVersion:\*\*\s*(.+)$", re.MULTILINE | re.IGNORECASE)
RE_LAST_UPDATED = re.compile(r"^\*\*LastUpdated:\*\*\s*(.+)$", re.MULTILINE | re.IGNORECASE)
RE_KEYWORDS = re.compile(r"^\*\*Keywords:\*\*\s*(.+)$", re.MULTILINE | re.IGNORECASE)
RE_TOKEN_BUDGET = re.compile(r"^\*\*TokenBudget:\*\*\s*(.+)$", re.MULTILINE | re.IGNORECASE)
RE_CONTEXT_TIER = re.compile(r"^\*\*ContextTier:\*\*\s*(.+)$", re.MULTILINE | re.IGNORECASE)
RE_DEPENDS = re.compile(r"^\*\*Depends:\*\*\s*(.+)$", re.MULTILINE | re.IGNORECASE)

# Prose Dependencies subsection: starts with `### Dependencies`, ends at the
# next H2/H3 header. Captured group is the block body (without the H3 line).
RE_DEPS_PROSE = re.compile(
    r"^### Dependencies\s*\n(.*?)(?=^###\s|^##\s)",
    re.MULTILINE | re.DOTALL,
)

# Individual justification bullet: `- **filename.md** - one-line description`.
RE_JUSTIFICATION = re.compile(
    r"^-\s+\*\*(?P<name>[A-Za-z0-9_.+-]+\.md)\*\*\s*[-–—:]\s*(?P<why>.+?)\s*$",
    re.MULTILINE,
)

SKIP_NAMES = {
    "RULES_INDEX.md",
    "README.md",
    "CHANGELOG.md",
    "AGENTS.md",
    "UNIVERSAL_PROMPT.md",
    "002a-rule-boilerplate.md",
    "002a-rule-template.md",
}


def _bump_major(version: str) -> str:
    """Compute the MAJOR bump: v3.3.0 -> v4.0.0, v1.0.0 -> v2.0.0."""
    m = re.match(r"^v(\d+)\.(\d+)\.(\d+)$", version.strip())
    if not m:
        # Accept v3.3 shorthand (no PATCH) as well.
        m = re.match(r"^v(\d+)\.(\d+)$", version.strip())
        if not m:
            raise ValueError(f"Unrecognized RuleVersion: {version!r}")
    major = int(m.group(1))
    return f"v{major + 1}.0.0"


def _parse_depends_line(value: str) -> list[tuple[str, str]]:
    """Parse ``**Depends:**`` inline value into ``[(kind, filename), ...]``.

    Empty / None values yield an empty list.
    """
    stripped = value.strip()
    if stripped.lower() in {"none", "-", "—", ""}:
        return []
    entries: list[tuple[str, str]] = []
    for raw in stripped.split(","):
        item = raw.strip()
        if not item:
            continue
        if ":" in item:
            kind, name = item.split(":", 1)
            kind = kind.strip().lower()
            name = name.strip()
        else:
            kind = "required"
            name = item
        if not name.endswith(".md"):
            name = f"{name}.md"
        if kind not in {"required", "optional"}:
            kind = "required"
        entries.append((kind, name))
    return entries


def _parse_justifications(content: str) -> dict[str, str]:
    """Return a ``{filename: justification}`` map extracted from the prose block."""
    match = RE_DEPS_PROSE.search(content)
    if not match:
        return {}
    block = match.group(1)
    return {m.group("name"): m.group("why").strip() for m in RE_JUSTIFICATION.finditer(block)}


def _parse_keywords_line(value: str) -> list[str]:
    """Split the inline ``**Keywords:**`` value into typed entries."""
    return [k.strip() for k in value.split(",") if k.strip()]


def _render_frontmatter(
    schema_version: str,
    rule_version: str,
    last_updated: str,
    keywords: list[str],
    token_budget: str,
    context_tier: str,
    depends: list[tuple[str, str]],
    justifications: dict[str, str],
) -> str:
    """Serialize the v3.5 frontmatter block. Hand-rolled to preserve YAML comments."""
    lines: list[str] = ["---"]
    lines.append(f"schema_version: {schema_version}")
    lines.append(f"rule_version: {rule_version}")
    lines.append(f"last_updated: {last_updated}")
    if keywords:
        lines.append("keywords:")
        for kw in keywords:
            lines.append(f"  - {kw}")
    else:
        lines.append("keywords: []")
    lines.append(f"token_budget: {token_budget}")
    lines.append(f"context_tier: {context_tier}")
    if not depends:
        lines.append("depends: {}")
    else:
        lines.append("depends:")
        required = [n for kind, n in depends if kind == "required"]
        optional = [n for kind, n in depends if kind == "optional"]
        if required:
            lines.append("  required:")
            for name in required:
                comment = justifications.get(name)
                if comment:
                    lines.append(f"    - {name}  # {comment}")
                else:
                    lines.append(f"    - {name}")
        if optional:
            lines.append("  optional:")
            for name in optional:
                comment = justifications.get(name)
                if comment:
                    lines.append(f"    - {name}  # {comment}")
                else:
                    lines.append(f"    - {name}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def _extract_field(pattern: re.Pattern[str], content: str, default: str = "") -> str:
    m = pattern.search(content)
    return m.group(1).strip() if m else default


def _remove_metadata_block(content: str) -> str:
    """Delete the `## Metadata` H2 and its 7 field lines (up to the next blank/H2)."""
    m = RE_METADATA_HEADER.search(content)
    if not m:
        return content
    start = m.start()
    # Find end: first blank line followed by a non-metadata line, or next H2.
    tail = content[m.end() :]
    # Strip the metadata block: everything up to the next `## ` header
    next_h2 = re.search(r"^##\s", tail, re.MULTILINE)
    end_in_tail = next_h2.start() if next_h2 else len(tail)
    return content[:start] + content[m.end() :][end_in_tail:]


def _remove_deps_prose(content: str) -> str:
    """Delete the `### Dependencies` prose subsection while keeping `## References`."""
    m = RE_DEPS_PROSE.search(content)
    if not m:
        return content
    return content[: m.start()] + content[m.end() :]


def migrate_content(
    content: str,
    today: str,
) -> tuple[str, dict[str, Any], bool]:
    """Apply the v3.4→v3.5 migration to a single rule.

    Returns ``(new_content, report, changed)`` where ``report`` describes the
    diff for the ``--output-report`` JSON emission.
    """
    # Idempotency: skip files that already have a frontmatter fence.
    if content.startswith("---\n") or content.startswith("---\r\n"):
        return content, {"skipped": "already-frontmatter"}, False

    schema_version = _extract_field(RE_SCHEMA_VERSION, content, default="v3.4")
    rule_version_old = _extract_field(RE_RULE_VERSION, content)
    if not rule_version_old:
        return content, {"skipped": "no-rule-version"}, False
    keywords_raw = _extract_field(RE_KEYWORDS, content)
    token_budget = _extract_field(RE_TOKEN_BUDGET, content)
    context_tier = _extract_field(RE_CONTEXT_TIER, content)
    depends_raw = _extract_field(RE_DEPENDS, content)

    keywords = _parse_keywords_line(keywords_raw)
    depends = _parse_depends_line(depends_raw)
    justifications = _parse_justifications(content)

    rule_version_new = _bump_major(rule_version_old)

    frontmatter = _render_frontmatter(
        schema_version="v3.5",
        rule_version=rule_version_new,
        last_updated=today,
        keywords=keywords,
        token_budget=token_budget,
        context_tier=context_tier,
        depends=depends,
        justifications=justifications,
    )

    new_content = _remove_metadata_block(content)
    new_content = _remove_deps_prose(new_content)

    # Also strip empty ### Dependencies blank line that may remain.
    new_content = re.sub(r"\n\n\n+", "\n\n", new_content)
    # Prepend frontmatter; ensure a single blank line between frontmatter and H1.
    if not new_content.startswith("\n"):
        new_content = (
            frontmatter + new_content.lstrip("\n")
            if new_content.lstrip("\n") == new_content
            else frontmatter + new_content
        )
    else:
        new_content = frontmatter + new_content.lstrip("\n")

    report = {
        "old_schema_version": schema_version,
        "new_schema_version": "v3.5",
        "old_version": rule_version_old,
        "new_version": rule_version_new,
        "old_depends": [f"{k}:{n}" for k, n in depends],
        "new_depends_with_comments": [
            {"kind": k, "name": n, "comment": justifications.get(n, "")} for k, n in depends
        ],
        "old_keywords": keywords,
        "new_keywords": keywords,
        "last_updated": today,
    }
    return new_content, report, True


def iter_rule_files(rules_dir: Path, exclude: set[str]) -> list[Path]:
    return sorted(
        p
        for p in rules_dir.glob("*.md")
        if p.is_file() and p.name not in SKIP_NAMES and p.name not in exclude
    )


def load_exclude_list(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()
    names: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            names.add(s)
    return names


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Migrate rules from v3.4 to v3.5")
    parser.add_argument("--rules-dir", type=Path, default=Path("rules"))
    parser.add_argument("--exclude-list", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--canary", type=Path, default=None, help="Migrate only this single file.")
    parser.add_argument("--output-report", type=Path, default=None)
    parser.add_argument("--changelog-output", type=Path, default=None)
    args = parser.parse_args(argv)

    today = datetime.now(UTC).strftime("%Y-%m-%d")
    exclude = load_exclude_list(args.exclude_list)

    if args.canary:
        files = [args.canary]
    else:
        if not args.rules_dir.is_dir():
            print(f"rules-dir not found: {args.rules_dir}", file=sys.stderr)
            return 1
        files = iter_rule_files(args.rules_dir, exclude)

    reports: dict[str, dict[str, Any]] = {}
    changelog_entries: list[str] = []
    changed_count = 0
    for path in files:
        before = path.read_text(encoding="utf-8")
        after, report, changed = migrate_content(before, today)
        reports[path.name] = report
        if changed:
            changed_count += 1
            if args.dry_run:
                print(f"would migrate: {path}")
            else:
                path.write_text(after, encoding="utf-8")
                print(f"migrated: {path}")
            changelog_entries.append(
                f"- `{path.name}`: {report['old_version']} → {report['new_version']} (schema v3.5 migration)"
            )
        else:
            if "skipped" in report:
                print(f"skipped ({report['skipped']}): {path}", file=sys.stderr)

    if args.output_report:
        args.output_report.parent.mkdir(parents=True, exist_ok=True)
        args.output_report.write_text(json.dumps(reports, indent=2, sort_keys=True) + "\n")
        print(f"report written: {args.output_report}")

    if args.changelog_output and changelog_entries and not args.dry_run:
        header = f"## Schema migration v3.4 → v3.5 ({today})\n\n"
        body = "\n".join(changelog_entries) + "\n"
        args.changelog_output.write_text(header + body, encoding="utf-8")
        print(f"changelog written: {args.changelog_output}")

    total = len(files)
    verb = "would change" if args.dry_run else "migrated"
    print(f"\n{changed_count}/{total} file(s) {verb}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
