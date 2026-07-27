#!/usr/bin/env python3
"""Precision evaluation script for the rule matcher.

Runs the deterministic rule matcher against all 35 fixtures in
fixtures/rule_loader_eval/*.yaml and reports per-fixture and aggregate metrics.

Extra definition: matched rules NOT in expected.required AND NOT in
expected.optional AND NOT rules/000-global-core.md (foundation always injected).

Usage:
    uv run python scripts/eval_precision.py
    uv run python scripts/eval_precision.py --label "post-phase-a"
    uv run python scripts/eval_precision.py --targets "missing=10,extra=80,avg=7"
    uv run python scripts/eval_precision.py --threshold 3 --max-entries 15
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

_REPO = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO / "src"))

from ai_rules.match_rules import (  # noqa: E402
    FileContext,
    _extract_from_prompt,
    build_manifest,
    load_rules_db,
    match_rules,
    resolve_dependencies,
)

_FIXTURES_DIR = _REPO / "fixtures" / "rule_loader_eval"
_RULES_DIR = _REPO / "rules"
_ALWAYS_ACCEPTABLE = {"rules/000-global-core.md"}


def _load_fixtures(fixtures_dir: Path) -> list[dict]:
    fixtures = []
    for yaml_file in sorted(fixtures_dir.glob("*.yaml")):
        with yaml_file.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict) and "prompt" in data:
            fixtures.append(data)
    return fixtures


def _run_fixture(
    fixture: dict,
    rules_db: dict,
    *,
    score_threshold: int,
    max_entries: int,
) -> dict:
    prompt = fixture.get("prompt", "")
    fixture_id = fixture.get("id", "unknown")
    expected = fixture.get("expected", {}) or {}
    required = set(expected.get("required") or [])
    optional = set(expected.get("optional") or [])

    kw, exts, paths = _extract_from_prompt(prompt)
    file_ctx = FileContext(extensions=exts, paths=paths)

    scored = match_rules(kw, file_ctx, list(rules_db.values()), score_threshold=score_threshold)
    matched_filenames = {sr.rule.filename for sr in scored}

    resolved, warnings = resolve_dependencies(scored, rules_db)
    manifest = build_manifest(
        resolved,
        warnings,
        matched_filenames=matched_filenames,
        max_entries=max_entries,
        max_tokens=100_000,
    )

    matched_paths = {f"rules/{e['filename']}" for e in manifest.get("load_sequence", [])}

    missing = sorted(required - matched_paths)
    acceptable = required | optional | _ALWAYS_ACCEPTABLE
    extra = sorted(matched_paths - acceptable)

    return {
        "fixture_id": fixture_id,
        "required": sorted(required),
        "optional": sorted(optional),
        "matched": sorted(matched_paths),
        "missing": missing,
        "extra": extra,
        "missing_count": len(missing),
        "extra_count": len(extra),
        "matched_count": len(matched_paths),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate rule matcher precision")
    parser.add_argument(
        "--threshold", type=int, default=4, help="score_threshold passed to match_rules"
    )
    parser.add_argument(
        "--max-entries", type=int, default=8, help="max_entries passed to build_manifest"
    )
    parser.add_argument(
        "--targets", default="", help="Comma-separated targets e.g. 'missing=10,extra=80,avg=7'"
    )
    parser.add_argument("--label", default="eval", help="Label for this run")
    parser.add_argument("--rules-dir", type=Path, default=_RULES_DIR)
    parser.add_argument("--fixtures-dir", type=Path, default=_FIXTURES_DIR)
    args = parser.parse_args(argv)

    try:
        rules_db = load_rules_db(args.rules_dir)
    except FileNotFoundError as exc:
        print(json.dumps({"error": str(exc), "label": args.label}))
        return 1

    fixtures = _load_fixtures(args.fixtures_dir)
    if not fixtures:
        print(json.dumps({"error": "no fixtures found", "label": args.label}))
        return 1

    per_fixture: list[dict] = []
    total_missing = 0
    total_extra = 0
    total_matched = 0

    for fixture in fixtures:
        result = _run_fixture(
            fixture,
            rules_db,
            score_threshold=args.threshold,
            max_entries=args.max_entries,
        )
        per_fixture.append(result)
        total_missing += result["missing_count"]
        total_extra += result["extra_count"]
        total_matched += result["matched_count"]

    avg_matched = round(total_matched / len(fixtures), 2) if fixtures else 0.0

    summary = {
        "label": args.label,
        "threshold": args.threshold,
        "max_entries": args.max_entries,
        "fixture_count": len(fixtures),
        "total_missing": total_missing,
        "total_extra": total_extra,
        "avg_matched": avg_matched,
        "per_fixture": per_fixture,
    }

    print(json.dumps(summary, indent=2))

    # Targets gate
    targets: dict[str, float] = {}
    for t in args.targets.split(","):
        t = t.strip()
        if "=" in t:
            k, v = t.split("=", 1)
            targets[k.strip()] = float(v.strip())

    passed = True
    if "missing" in targets and total_missing > targets["missing"]:
        print(
            f"FAIL: total_missing={total_missing} > target={int(targets['missing'])}",
            file=sys.stderr,
        )
        passed = False
    if "extra" in targets and total_extra > targets["extra"]:
        print(f"FAIL: total_extra={total_extra} > target={int(targets['extra'])}", file=sys.stderr)
        passed = False
    if "avg" in targets and avg_matched > targets["avg"]:
        print(f"FAIL: avg_matched={avg_matched} > target={targets['avg']}", file=sys.stderr)
        passed = False

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
