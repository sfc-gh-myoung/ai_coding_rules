"""Phase 0.5 T8/T9 challenger report generator.

Reads the challenger-run rationale JSONL and produces:

* ``.workbench/results/challenger_keywords.jsonl`` — challenger keyword sets in
  the same shape as ``.workbench/baselines/pre-refinement/keyword_baselines.jsonl``.
* ``.workbench/eval/keyword_command_challenger_report.md`` — T8 discrimination
  regression report (baseline vs challenger, via
  :func:`ai_rules.rule_loader_eval.matcher.match_loaded_rules`).
* ``.workbench/audit/keyword_command_acceptance.json`` — T9 empirical acceptance
  gate result.

Run once per Phase 0.5 challenger run; idempotent.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from ai_rules.commands.keywords import (
    build_keyword_collision_map,
    load_keyword_stoplist,
    load_keyword_stoplist_overrides,
)
from ai_rules.rule_loader_eval.matcher import match_loaded_rules

REPO_ROOT = Path(__file__).resolve().parents[1]
RATIONALE_JSONL = REPO_ROOT / ".workbench/audit/keyword_rationale.jsonl"
BASELINE_JSONL = REPO_ROOT / ".workbench/baselines/pre-refinement/keyword_baselines.jsonl"
FIXTURE_JSON = REPO_ROOT / ".workbench/eval-fixtures/keyword-precision-baseline.json"

CHALLENGER_JSONL = REPO_ROOT / ".workbench/results/challenger_keywords.jsonl"
CHALLENGER_MD = REPO_ROOT / ".workbench/eval/keyword_command_challenger_report.md"
ACCEPTANCE_JSON = REPO_ROOT / ".workbench/audit/keyword_command_acceptance.json"


def _load_rationale_entries() -> dict[str, list[dict]]:
    entries: dict[str, list[dict]] = defaultdict(list)
    for raw in RATIONALE_JSONL.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        e = json.loads(raw)
        entries[e["rule_path"]].append(e)
    return entries


def _load_baselines() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for raw in BASELINE_JSONL.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        e = json.loads(raw)
        out[e["rule_path"]] = e["keywords"]
    return out


def _compound_ratio(keywords: list[str]) -> float:
    if not keywords:
        return 0.0
    compound = sum(1 for kw in keywords if " " in kw or "-" in kw)
    return compound / len(keywords)


def _forbidden_count_for_side(keyword_sets: dict[str, list[str]]) -> int:
    """Count fixture-forbidden matches across all fixtures for one side.

    The seeded fixture set (30 fixtures) has empty ``required``/``forbidden``
    lists — this is documented in the fixture's ``adapt_note``. The count is
    therefore zero for both sides; the report captures this explicitly.
    """
    fx = json.loads(FIXTURE_JSON.read_text(encoding="utf-8"))
    total = 0
    for entry in fx.get("fixtures", []):
        forbidden = entry.get("forbidden", [])
        # Treat each rule's keyword set as if it were "loaded". Since forbidden
        # lists are empty, this trivially returns 0. We still call the matcher
        # to prove the harness is wired.
        result = match_loaded_rules(
            loaded=list(keyword_sets.keys()),
            required=entry.get("required", []),
            forbidden=forbidden,
        )
        total += len(result.forbidden_present)
    return total


def _required_recall_for_side(keyword_sets: dict[str, list[str]]) -> float:
    fx = json.loads(FIXTURE_JSON.read_text(encoding="utf-8"))
    required_hits = 0
    required_total = 0
    for entry in fx.get("fixtures", []):
        required = entry.get("required", [])
        required_total += len(required)
        result = match_loaded_rules(
            loaded=list(keyword_sets.keys()),
            required=required,
            forbidden=entry.get("forbidden", []),
        )
        required_hits += len(required) - len(result.missing_required)
    if required_total == 0:
        return 1.0
    return required_hits / required_total


def main() -> int:
    rationale = _load_rationale_entries()
    baselines = _load_baselines()
    stoplist = load_keyword_stoplist()
    overrides = load_keyword_stoplist_overrides()
    collision_map = build_keyword_collision_map()

    # Build challenger keyword sets and per-file challenger JSONL
    challenger_sets: dict[str, list[str]] = {}
    CHALLENGER_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with CHALLENGER_JSONL.open("w", encoding="utf-8") as fh:
        for rule_path, entries in rationale.items():
            keywords = [e["keyword"] for e in entries]
            challenger_sets[rule_path] = keywords
            fh.write(
                json.dumps(
                    {
                        "rule_path": rule_path,
                        "keywords": keywords,
                        "keyword_count": len(keywords),
                        "source": "post-improvement live cortex run",
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )
                + "\n"
            )

    # -------------- T8: challenger vs baseline discrimination -----------
    baseline_forbidden = _forbidden_count_for_side(baselines)
    challenger_forbidden = _forbidden_count_for_side(challenger_sets)
    baseline_recall = _required_recall_for_side(baselines)
    challenger_recall = _required_recall_for_side(challenger_sets)

    CHALLENGER_MD.parent.mkdir(parents=True, exist_ok=True)
    with CHALLENGER_MD.open("w", encoding="utf-8") as fh:
        fh.write("# Phase 0.5 Task 8 — Challenger vs Baseline Discrimination Report\n\n")
        fh.write(f"Generated: {datetime.now(UTC).isoformat()}\n\n")
        fh.write("## Summary\n\n")
        fh.write(
            f"| Side       | forbidden_count | required_recall |\n"
            f"|------------|-----------------|-----------------|\n"
            f"| Baseline   | {baseline_forbidden}               | {baseline_recall:.3f}         |\n"
            f"| Challenger | {challenger_forbidden}               | {challenger_recall:.3f}         |\n\n"
        )
        pass_ok = (
            challenger_forbidden <= baseline_forbidden and challenger_recall >= baseline_recall
        )
        fh.write(
            f"**Gate:** challenger forbidden_count ≤ baseline forbidden_count "
            f"AND challenger required_recall ≥ baseline required_recall = "
            f"**{'PASS' if pass_ok else 'FAIL'}**\n\n"
        )
        fh.write("## Note on Fixture Coverage\n\n")
        fh.write(
            "The fixture set at `.workbench/eval-fixtures/keyword-precision-baseline.json`\n"
            "(30 fixtures) currently has empty `required` and `forbidden` lists per its\n"
            "`adapt_note` (deferred from T2 to keep LLM cost bounded). The matcher is still\n"
            "wired end-to-end; both sides trivially satisfy the gate because there are no\n"
            "declared forbidden or required rules. Populating these lists is out of scope\n"
            "for T8 but tracked as follow-up work for the Track A eval hardening.\n\n"
        )
        fh.write("## Per-Rule Diff\n\n")
        for rule_path in sorted(rationale.keys()):
            fh.write(f"### `{rule_path}`\n\n")
            fh.write(
                f"- baseline ({len(baselines.get(rule_path, []))}): "
                f"{', '.join(baselines.get(rule_path, [])) or '(none)'}\n"
            )
            fh.write(
                f"- challenger ({len(challenger_sets[rule_path])}): "
                f"{', '.join(challenger_sets[rule_path])}\n\n"
            )

    # -------------- T9: empirical acceptance gate ----------------------
    acceptance_rules = []
    for rule_path, entries in rationale.items():
        keywords = [e["keyword"] for e in entries]
        rule_filename = Path(rule_path).name
        permitted = overrides.get(rule_filename, set())

        stoplist_violations = [
            kw for kw in keywords if kw.lower() in stoplist and kw.lower() not in permitted
        ]
        collision_violations = [
            kw
            for kw in keywords
            if len([r for r in collision_map.get(kw.lower(), []) if r != rule_filename]) > 3
        ]
        compound_ratio = _compound_ratio(keywords)
        keyword_count = len(keywords)

        passed = (
            5 <= keyword_count <= 7
            and compound_ratio >= 0.6
            and not stoplist_violations
            and not collision_violations
        )
        acceptance_rules.append(
            {
                "rule_path": rule_path,
                "keyword_count": keyword_count,
                "compound_ratio": round(compound_ratio, 3),
                "stoplist_violations": stoplist_violations,
                "collision_violations": collision_violations,
                "passed": passed,
            }
        )

    overall_status = "pass" if all(r["passed"] for r in acceptance_rules) else "fail"
    acceptance = {
        "generated_at": datetime.now(UTC).isoformat(),
        "rules": acceptance_rules,
        "overall_status": overall_status,
    }
    ACCEPTANCE_JSON.parent.mkdir(parents=True, exist_ok=True)
    ACCEPTANCE_JSON.write_text(
        json.dumps(acceptance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"Challenger keywords → {CHALLENGER_JSONL}")
    print(f"T8 report          → {CHALLENGER_MD}")
    print(f"T9 acceptance      → {ACCEPTANCE_JSON}")
    print(f"T9 overall_status  = {overall_status}")
    for r in acceptance_rules:
        print(
            f"  {r['rule_path']}: count={r['keyword_count']} compound={r['compound_ratio']} stoplist={r['stoplist_violations']} collisions={r['collision_violations']} passed={r['passed']}"
        )

    return 0 if overall_status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
