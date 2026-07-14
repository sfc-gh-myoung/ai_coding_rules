"""Apply the per-rule keyword audit to rule files in a filename range.

Reads ``.workbench/audit/keyword_audit_table.csv`` (produced by
``scripts/build_keyword_audit_table.py``), filters rows whose ``filename``
falls in a caller-supplied numeric range, and for each rule:

  1. Rewrites the ``**Keywords:**`` line with the new 5-7 ``kw:`` tokens.
  2. Bumps ``RuleVersion``: MINOR by default (``vX.Y.Z`` → ``vX.(Y+1).0``),
     or MAJOR when any dropped token in the row has ``relied_upon: true``.
  3. Stamps ``LastUpdated: <today>``.

Exits 0 on success.  On validation failure it prints the failing file and
exits 1 without reverting; the caller is expected to re-run validation and
either fix or revert via git.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_KEYWORDS_LINE_RE = re.compile(r"^\*\*Keywords:\*\* .*$", re.MULTILINE)
_VERSION_LINE_RE = re.compile(
    r"^\*\*RuleVersion:\*\*\s*v(?P<maj>\d+)\.(?P<min>\d+)\.(?P<pat>\d+)\s*$",
    re.MULTILINE,
)
_LAST_UPDATED_LINE_RE = re.compile(r"^\*\*LastUpdated:\*\*\s*\d{4}-\d{2}-\d{2}\s*$", re.MULTILINE)


def format_keywords_line(tokens: list[str]) -> str:
    """Render ``[a, b, c]`` as ``**Keywords:** kw:a, kw:b, kw:c``."""
    return "**Keywords:** " + ", ".join(f"kw:{t}" for t in tokens if t)


def bump_version(current: str, bump: str) -> str:
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", current.strip())
    if not m:
        raise ValueError(f"Unparseable RuleVersion: {current!r}")
    maj, minor, pat = (int(x) for x in m.groups())
    if bump == "MAJOR":
        maj, minor, pat = maj + 1, 0, 0
    elif bump == "MINOR":
        minor, pat = minor + 1, 0
    elif bump == "PATCH":
        pat += 1
    else:
        raise ValueError(f"Unknown bump: {bump}")
    return f"v{maj}.{minor}.{pat}"


def in_range(name: str, start: int, end: int) -> bool:
    """Whether ``name`` begins with a numeric prefix in [start, end]."""
    m = re.match(r"^(\d{1,3})", name)
    if not m:
        return False
    n = int(m.group(1))
    return start <= n <= end


def apply_row(rule_file: Path, new_tokens: list[str], bump: str, today: str) -> bool:
    text = rule_file.read_text(encoding="utf-8")
    orig = text

    # Rewrite Keywords line.
    new_line = format_keywords_line(new_tokens)
    if _KEYWORDS_LINE_RE.search(text):
        text = _KEYWORDS_LINE_RE.sub(new_line, text, count=1)
    else:
        raise RuntimeError(f"No **Keywords:** line found in {rule_file}")

    # Rewrite RuleVersion.
    m = _VERSION_LINE_RE.search(text)
    if not m:
        raise RuntimeError(f"No **RuleVersion:** line found in {rule_file}")
    current = f"v{m.group('maj')}.{m.group('min')}.{m.group('pat')}"
    new_ver = bump_version(current, bump)
    text = _VERSION_LINE_RE.sub(f"**RuleVersion:** {new_ver}", text, count=1)

    # Rewrite LastUpdated.
    if _LAST_UPDATED_LINE_RE.search(text):
        text = _LAST_UPDATED_LINE_RE.sub(f"**LastUpdated:** {today}", text, count=1)
    else:
        raise RuntimeError(f"No **LastUpdated:** line found in {rule_file}")

    if text == orig:
        return False
    rule_file.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--audit-csv",
        type=Path,
        default=REPO_ROOT / ".workbench" / "audit" / "keyword_audit_table.csv",
    )
    ap.add_argument("--rules-dir", type=Path, default=REPO_ROOT / "rules")
    ap.add_argument("--start", type=int, required=True, help="Inclusive prefix start")
    ap.add_argument("--end", type=int, required=True, help="Inclusive prefix end")
    ap.add_argument("--today", default=date.today().isoformat())
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--validate",
        action="store_true",
        help="Run 'ai-rules validate' on touched files after applying.",
    )
    args = ap.parse_args()

    with args.audit_csv.open("r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    touched: list[Path] = []
    major_count = 0
    minor_count = 0
    for row in rows:
        fn = row["filename"]
        if not in_range(fn, args.start, args.end):
            continue
        rule_file = args.rules_dir / fn
        if not rule_file.exists():
            print(f"WARN: {rule_file} does not exist; skipping", file=sys.stderr)
            continue
        new_tokens = [t for t in row["new_kw"].split(";") if t]
        if not (5 <= len(new_tokens) <= 7):
            print(
                f"WARN: {fn} has {len(new_tokens)} tokens (expected 5-7); skipping",
                file=sys.stderr,
            )
            continue
        bump = "MAJOR" if "true" in row["relied_upon_flags"] else "MINOR"
        if bump == "MAJOR":
            major_count += 1
        else:
            minor_count += 1
        if args.dry_run:
            print(f"DRY: {fn} bump={bump} new_kw={new_tokens}")
            continue
        if apply_row(rule_file, new_tokens, bump, args.today):
            touched.append(rule_file)

    print(
        f"Applied to {len(touched)} rules in [{args.start:03d}-{args.end:03d}] "
        f"(MAJOR={major_count} MINOR={minor_count})"
    )

    if args.validate and touched and not args.dry_run:
        cmd = ["uv", "run", "ai-rules", "validate", str(args.rules_dir), "--quiet"]
        print(f"Running: {' '.join(cmd)} (checking {len(touched)} touched files)")
        rc = subprocess.call(cmd)
        if rc != 0:
            print(f"VALIDATION FAILED (rc={rc})", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
