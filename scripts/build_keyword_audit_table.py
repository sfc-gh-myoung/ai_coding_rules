"""Build the per-rule keyword audit table (Phase 1 Step 3 deliverable a).

Combines
  - ``.workbench/audit/collision_map.json``   (corpus-wide kw: collision counts)
  - ``.workbench/audit/candidate_keywords.json`` (LLM-proposed replacements)
  - ``rules/RULES_INDEX.md``                  (current kw: tokens per rule)
  - ``.workbench/eval-fixtures/keyword-precision-baseline.json`` (relied-upon oracle)

and emits ``.workbench/audit/keyword_audit_table.csv`` with columns::

    filename | old_kw | keep | drop | new_kw | collision_before |
    collision_after | relied_upon_flags

Where ``relied_upon`` semantics are the plan's machine-checkable definition:
a token T in rule R is relied-upon iff T is the ONLY token in R's current
``kw:`` set that matches any request in the fixture whose ``required``
list contains R.  With the current baseline fixture (empty ``required``
lists), no token qualifies - the flags will all be ``false``.  This is
intentional; Track A hardening later populates the fixture and re-runs
this script.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_COLLISION = REPO_ROOT / ".workbench" / "audit" / "collision_map.json"
DEFAULT_CANDIDATES = REPO_ROOT / ".workbench" / "audit" / "candidate_keywords.json"
DEFAULT_INDEX = REPO_ROOT / "rules" / "RULES_INDEX.md"
DEFAULT_FIXTURE = REPO_ROOT / ".workbench" / "eval-fixtures" / "keyword-precision-baseline.json"
DEFAULT_EXCLUDE = REPO_ROOT / ".workbench" / "config" / "exclude_list.txt"
DEFAULT_OUTPUT = REPO_ROOT / ".workbench" / "audit" / "keyword_audit_table.csv"

# F4 flat-line grammar per index.py:311.
# Example: ``000-global-core.md tier=Critical kw=alpha beta gamma``
_LINE_RE = re.compile(r"^(?P<filename>\S+\.md)\s+.*?\bkw=(?P<kw>.+)$")


def load_current_keywords(index_path: Path) -> dict[str, list[str]]:
    """Return ``{filename: [kw, ...]}`` from the F4 RULES_INDEX.md file."""
    out: dict[str, list[str]] = {}
    for raw in index_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("<!--"):
            continue
        m = _LINE_RE.match(line)
        if not m:
            continue
        toks = [t for t in m.group("kw").split() if t]
        out[m.group("filename")] = toks
    return out


def load_exclude(path: Path) -> set[str]:
    if not path.exists():
        return set()
    excluded: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if s and not s.startswith("#"):
            excluded.add(s)
    return excluded


def compute_relied_upon(
    fixture: dict[str, Any],
    current_kw: dict[str, list[str]],
) -> dict[tuple[str, str], bool]:
    """Return ``{(filename, token): bool}`` for the relied-upon oracle.

    Definition: token T in rule R is relied-upon iff T is the ONLY token
    in R's current kw: set that matches any request whose ``required``
    list contains R.  "Matches" here is a lower-case substring check
    against the request text - the fixture and matcher both use this
    normalization convention.
    """
    result: dict[tuple[str, str], bool] = {}
    fixtures = fixture.get("fixtures", []) if fixture else []
    for filename, tokens in current_kw.items():
        # Find fixture requests that require this rule.
        req_texts = [
            (fx.get("request") or "").lower()
            for fx in fixtures
            if filename in (fx.get("required") or [])
        ]
        if not req_texts:
            for t in tokens:
                result[(filename, t)] = False
            continue
        # For each request, list tokens whose lower-cased form matches.
        for t in tokens:
            relied = False
            for text in req_texts:
                matches = [x for x in tokens if x.lower() in text]
                if matches == [t]:
                    relied = True
                    break
            result[(filename, t)] = relied
    return result


def max_collision(
    tokens: list[str],
    collision_map: dict[str, list[str]],
    self_filename: str,
) -> int:
    """Max number of *other* rules a token appears in (self-excluded)."""
    best = 0
    for tok in tokens:
        rules = collision_map.get(tok, [])
        # Self-exclusion: don't count the rule as colliding with itself.
        others = [r for r in rules if r != self_filename]
        best = max(best, len(others))
    return best


def build_rows(
    current_kw: dict[str, list[str]],
    candidates: dict[str, list[str]],
    collision_map: dict[str, list[str]],
    relied_upon: dict[tuple[str, str], bool],
    excluded: set[str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for filename, new_kw in candidates.items():
        if filename in excluded:
            continue
        old_kw = current_kw.get(filename, [])
        old_set = set(old_kw)
        new_set = set(new_kw)
        keep = [t for t in old_kw if t in new_set]
        drop = [t for t in old_kw if t not in new_set]
        flags = ";".join(
            f"{t}={'true' if relied_upon.get((filename, t), False) else 'false'}" for t in drop
        )
        rows.append(
            {
                "filename": filename,
                "old_kw": ";".join(old_kw),
                "keep": ";".join(keep),
                "drop": ";".join(drop),
                "new_kw": ";".join(new_kw),
                "collision_before": str(max_collision(old_kw, collision_map, filename)),
                "collision_after": str(max_collision(new_kw, collision_map, filename)),
                "relied_upon_flags": flags,
            }
        )
        # Silence "unused" warning on old_set/new_set - kept for readability.
        del old_set, new_set
    rows.sort(key=lambda r: r["filename"])
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--collision-map", type=Path, default=DEFAULT_COLLISION)
    ap.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    ap.add_argument("--rules-index", type=Path, default=DEFAULT_INDEX)
    ap.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    ap.add_argument("--exclude-list", type=Path, default=DEFAULT_EXCLUDE)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    collision_report = json.loads(args.collision_map.read_text(encoding="utf-8"))
    collision_map: dict[str, list[str]] = collision_report["collision_map"]

    candidates_doc = json.loads(args.candidates.read_text(encoding="utf-8"))
    candidates: dict[str, list[str]] = {
        r["filename"]: list(r["keywords"]) for r in candidates_doc["rules"]
    }

    current_kw = load_current_keywords(args.rules_index)
    fixture = json.loads(args.fixture.read_text(encoding="utf-8")) if args.fixture.exists() else {}
    excluded = load_exclude(args.exclude_list)
    relied = compute_relied_upon(fixture, current_kw)

    rows = build_rows(current_kw, candidates, collision_map, relied, excluded)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "filename",
                "old_kw",
                "keep",
                "drop",
                "new_kw",
                "collision_before",
                "collision_after",
                "relied_upon_flags",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    major_bumps = sum(1 for r in rows if "true" in r["relied_upon_flags"])
    minor_bumps = len(rows) - major_bumps
    total_dropped = sum(1 for r in rows if r["drop"])
    print(
        f"Wrote {args.output} "
        f"(rows={len(rows)}, rules_with_drops={total_dropped}, "
        f"MAJOR_bumps={major_bumps}, MINOR_bumps={minor_bumps})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
