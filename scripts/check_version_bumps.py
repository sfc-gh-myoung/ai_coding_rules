"""Assert every rule file's ``RuleVersion`` is strictly greater than baseline.

Reads a baseline JSON file (default: ``.workbench/baselines/pre-track-a/
rule_versions.json``) of the form ``{filename: {rule_version: "vX.Y.Z", ...}}``
and compares each entry against the CURRENT ``**RuleVersion:**`` line in the
corresponding rule file.  Exits 0 iff every rule currently in the repo has a
strictly higher version than its baseline entry (missing-in-baseline rules
pass unconditionally; missing-in-repo rules are reported as errors).

Version comparison uses semantic-version integer tuples.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
_VERSION_RE = re.compile(
    r"^\*\*RuleVersion:\*\*\s*v?(?P<maj>\d+)\.(?P<min>\d+)\.(?P<pat>\d+)\s*$",
    re.MULTILINE,
)


def parse_version(v: str) -> tuple[int, int, int]:
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", v.strip())
    if not m:
        raise ValueError(f"Unparseable version: {v!r}")
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def rule_current_version(path: Path) -> tuple[int, int, int] | None:
    if not path.exists():
        return None
    m = _VERSION_RE.search(path.read_text(encoding="utf-8"))
    if not m:
        return None
    return (int(m.group("maj")), int(m.group("min")), int(m.group("pat")))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--baseline",
        type=Path,
        default=REPO_ROOT / ".workbench" / "baselines" / "pre-track-a" / "rule_versions.json",
    )
    ap.add_argument("--rules-dir", type=Path, default=REPO_ROOT / "rules")
    ap.add_argument(
        "--only-changed",
        action="store_true",
        help=(
            "Only assert strict increase for rules whose file has actually been "
            "modified (i.e., current version != baseline version). Missing-in-repo "
            "rules are still errors."
        ),
    )
    args = ap.parse_args()

    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    failures: list[tuple[str, str]] = []
    checked = 0
    increased = 0

    for filename, meta in sorted(baseline.items()):
        base_v = meta.get("rule_version")
        if not base_v:
            continue
        try:
            base_tup = parse_version(base_v)
        except ValueError as e:
            failures.append((filename, f"baseline unparseable: {e}"))
            continue
        cur = rule_current_version(args.rules_dir / filename)
        if cur is None:
            failures.append((filename, "missing in repo or no RuleVersion line"))
            continue
        checked += 1
        if cur == base_tup:
            if args.only_changed:
                continue
            failures.append(
                (
                    filename,
                    f"unchanged (baseline={base_v}, current=v{cur[0]}.{cur[1]}.{cur[2]})",
                )
            )
            continue
        if cur > base_tup:
            increased += 1
        else:
            failures.append(
                (
                    filename,
                    f"regressed (baseline={base_v}, current=v{cur[0]}.{cur[1]}.{cur[2]})",
                )
            )

    if failures:
        print(f"FAIL: {len(failures)} rule(s) did not strictly increase RuleVersion:")
        for fn, msg in failures:
            print(f"  {fn}: {msg}")
        return 1

    print(
        f"OK: {checked} baseline rules checked; {increased} strictly increased "
        f"(remaining {checked - increased} unchanged - allowed with --only-changed)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
