"""Corpus trigger-reachability audit (Phase 5).

For every rule and every declared trigger kind (``kw``/``ext``/``file``/``dir``),
build a probe prompt, run the real production manifest pipeline
(:func:`ai_rules.commands.rule_loader.rank_snapshot._manifest_paths`), and record
whether the rule's manifest entry is recalled, at what rank and score. Emits an
identity-pinned, sorted JSON artifact plus a read-only disposition sidecar for
reviewed outcomes, and enforces a scope circuit breaker.

Probe construction (per the plan):
- ``kw``  : a representative fixture prompt when the rule is required by a
  fixture; otherwise a synthetic competitive prompt (the semantic phrase plus
  generic competing signals, never an exact-phrase-only probe).
- ``ext`` : synthetic bare filename ``probe<extension>`` (e.g. ``probe.py``).
- ``file``: the exact declared bare filename.
- ``dir`` : normalized ``<declared-dir-without-trailing-slash>/probe.txt``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any

import typer

from ai_rules._shared.console import log_error, log_success, log_warning
from ai_rules._shared.paths import find_project_root
from ai_rules.commands.rule_loader.rank_snapshot import (
    GENERATOR_VERSION,
    Identity,
    _manifest_paths,
    _schema_version,
    canonical_json,
)
from ai_rules.match_rules import RuleEntry, load_rules_db
from ai_rules.rule_loader_eval.fixtures import Fixture, load_fixtures

DEFAULT_OUTPUT = Path("reports/rule-loader-corpus-audit.json")
DEFAULT_DISPOSITIONS = Path("reports/rule-loader-corpus-audit-dispositions.json")

# Scope circuit-breaker thresholds (v5 binding contract #7).
MISS_LIMIT = 20
NEW_FAMILY_LIMIT = 3
# Families this remediation plan already targets; misses here are in-scope.
KNOWN_AFFECTED_FAMILIES = frozenset({"002h", "112", "116"})

VALID_DISPOSITIONS = frozenset({"ok", "fixed", "intentional-exception"})
FOUNDATION_RULE = "rules/000-global-core.md"

# Generic competing signals appended to synthetic kw probes so they are never
# tautological exact-phrase-only prompts; these are low-signal words that do not
# displace an exact kw match.
_COMPETING_SIGNALS = ("setup", "configuration", "validation")


def _family(rule_id: str) -> str:
    """Rule family = the rule-ID prefix before the first hyphen (e.g. ``112``)."""
    return rule_id.split("/")[-1].split("-", 1)[0]


def _fixture_prompts_by_rule(fixtures: list[Fixture]) -> dict[str, list[str]]:
    by_rule: dict[str, list[str]] = {}
    for fx in fixtures:
        for rule_id in fx.required:
            by_rule.setdefault(rule_id, []).append(fx.prompt)
    return by_rule


def _probe(
    kind: str, value: str, rule_id: str, fx_by_rule: dict[str, list[str]]
) -> tuple[str, str]:
    """Return (probe_prompt, prompt_source) for a rule x trigger-kind."""
    if kind == "kw":
        prompts = fx_by_rule.get(rule_id)
        if prompts:
            return sorted(prompts)[0], "fixture"
        extra = "; cover " + ", ".join(_COMPETING_SIGNALS)
        return f"{value}{extra}", "synthetic"
    if kind == "ext":
        return f"probe{value}", "synthetic"
    if kind == "file":
        return value, "synthetic"
    if kind == "dir":
        return f"{value.rstrip('/')}/probe.txt", "synthetic"
    raise ValueError(f"unknown trigger kind: {kind!r}")


def _rule_trigger_pairs(rule: RuleEntry) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    pairs += [("kw", v) for v in rule.typed_kw]
    pairs += [("ext", v) for v in rule.typed_ext]
    pairs += [("file", v) for v in rule.file_patterns]
    pairs += [("dir", v) for v in rule.dir_patterns]
    return pairs


def build_records(db: dict[str, RuleEntry], fixtures: list[Fixture]) -> list[dict[str, Any]]:
    """Build one sorted record per rule x declared trigger-kind probe."""
    fx_by_rule = _fixture_prompts_by_rule(fixtures)
    records: list[dict[str, Any]] = []
    for filename in sorted(db):
        rule = db[filename]
        rule_id = f"rules/{filename}"
        for kind, value in _rule_trigger_pairs(rule):
            prompt, source = _probe(kind, value, rule_id, fx_by_rule)
            manifest_paths, rank_by_fn, score_by_fn = _manifest_paths(prompt, db)
            records.append(
                {
                    "rule_id": rule_id,
                    "trigger_kind": kind,
                    "trigger_value": value,
                    "probe": prompt,
                    "prompt_source": source,
                    "in_manifest": rule_id in manifest_paths,
                    "rank": rank_by_fn.get(filename),
                    "score": score_by_fn.get(filename),
                }
            )
    records.sort(key=lambda r: (r["rule_id"], r["trigger_kind"], r["trigger_value"]))
    return records


def artifact_identity(root: Path) -> dict[str, str]:
    """Capture the source+corpus identity recorded in the audit artifact."""
    ident = Identity.capture(root, root / "rules")
    return {
        "git_sha": ident.git_sha,
        "rules_digest": ident.rules_digest,
        "matcher_digest": ident.matcher_digest,
        "schema_version": _schema_version(root),
        "generator_version": GENERATOR_VERSION,
    }


def disposition_key(record: dict[str, Any], identity: dict[str, str]) -> str:
    """Stable sidecar key: rule_id + trigger_kind + trigger_value + content identity.

    Content identity (rules/matcher/schema/generator digests) is used rather than
    ``git_sha`` so reviewed dispositions survive commits and are invalidated only
    by a real change to the rules corpus, matcher, schema, or generator. ``git_sha``
    remains in the recorded artifact for provenance.
    """
    return "|".join(
        [
            record["rule_id"],
            record["trigger_kind"],
            record["trigger_value"],
            identity["rules_digest"],
            identity["matcher_digest"],
            identity["schema_version"],
            identity["generator_version"],
        ]
    )


def stable_disposition_identity(record: dict[str, Any]) -> tuple[str, str, str]:
    """Return the identity that survives corpus and matcher revisions."""
    return record["rule_id"], record["trigger_kind"], record["trigger_value"]


def _stable_identity_from_key(key: str) -> tuple[str, str, str] | None:
    parts = key.split("|", maxsplit=3)
    if len(parts) < 4:
        return None
    return parts[0], parts[1], parts[2]


def reconcile_dispositions(
    records: list[dict[str, Any]],
    identity: dict[str, str],
    dispositions: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], int]:
    """Re-key prior approvals for unchanged current misses only.

    Returns the new sidecar, unresolved current misses, and the number of old
    entries retired because their trigger no longer misses or is malformed.
    """
    current_misses = [record for record in records if not record["in_manifest"]]
    current_by_identity = {stable_disposition_identity(record): record for record in current_misses}
    carried: dict[str, dict[str, Any]] = {}

    for old_key, entry in dispositions.items():
        stable_identity = _stable_identity_from_key(old_key)
        if stable_identity is None:
            continue
        record = current_by_identity.pop(stable_identity, None)
        if record is not None:
            carried[disposition_key(record, identity)] = entry

    unresolved = sorted(
        current_by_identity.values(),
        key=lambda record: stable_disposition_identity(record),
    )
    retired = len(dispositions) - len(carried)
    return dict(sorted(carried.items())), unresolved, retired


def _load_dispositions(path: Path) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def evaluate(
    records: list[dict[str, Any]],
    identity: dict[str, str],
    dispositions: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Return (unresolved misses, disposition-integrity errors).

    A record is a miss when ``in_manifest`` is false and no valid sidecar entry
    resolves it. Integrity errors cover stale keys (not matching any current
    record at this identity) and ``intentional-exception`` without justification.
    """
    valid_keys = {disposition_key(r, identity) for r in records}
    integrity: list[str] = []
    for key, entry in dispositions.items():
        if key not in valid_keys:
            integrity.append(
                f"stale disposition key (no matching record at current identity): {key}"
            )
            continue
        disp = (entry or {}).get("disposition")
        if disp not in VALID_DISPOSITIONS:
            integrity.append(f"invalid disposition {disp!r} for key: {key}")
        elif disp == "intentional-exception" and not (entry or {}).get("justification"):
            integrity.append(f"intentional-exception without justification for key: {key}")

    misses: list[dict[str, Any]] = []
    for rec in records:
        if rec["in_manifest"]:
            continue
        entry = dispositions.get(disposition_key(rec, identity))
        disp = (entry or {}).get("disposition")
        resolved = disp in VALID_DISPOSITIONS and not (
            disp == "intentional-exception" and not (entry or {}).get("justification")
        )
        if not resolved:
            misses.append(rec)
    return misses, integrity


def should_circuit_break(misses: list[dict[str, Any]]) -> tuple[bool, set[str]]:
    """Return (break?, previously-unaffected families among the misses).

    Scope break when misses exceed :data:`MISS_LIMIT` or span more than
    :data:`NEW_FAMILY_LIMIT` families outside :data:`KNOWN_AFFECTED_FAMILIES`.
    """
    new_families = {_family(m["rule_id"]) for m in misses} - KNOWN_AFFECTED_FAMILIES
    broke = len(misses) > MISS_LIMIT or len(new_families) > NEW_FAMILY_LIMIT
    return broke, new_families


def audit_cmd(
    output: Annotated[
        Path, typer.Option("--output", help="Corpus-audit JSON output path.")
    ] = DEFAULT_OUTPUT,
    dispositions_path: Annotated[
        Path, typer.Option("--dispositions", help="Reviewed-disposition sidecar path.")
    ] = DEFAULT_DISPOSITIONS,
    fail_on_miss: Annotated[
        bool, typer.Option("--fail-on-miss", help="Exit non-zero on unresolved misses.")
    ] = False,
    reconcile: Annotated[
        bool,
        typer.Option(
            "--reconcile",
            help="Re-key prior approvals for unchanged current misses; never approves new misses.",
        ),
    ] = False,
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Write reconciled dispositions (requires --reconcile)."),
    ] = False,
) -> None:
    """Audit every rule's declared triggers for deterministic manifest reachability.

    ``--reconcile`` defaults to a read-only report. ``--reconcile --apply``
    re-keys only earlier approvals for identical, still-unmatched triggers.
    It deliberately leaves new misses unresolved.

    Exit codes: 0 clean; 1 ordinary unresolved misses (with --fail-on-miss);
    2 scope circuit break or stale/invalid disposition keys.
    """
    root = find_project_root()
    db = load_rules_db(root / "rules")
    fixtures = load_fixtures(root / "fixtures" / "rule_loader_eval", enforce_invariant=False)

    records = build_records(db, fixtures)
    identity = artifact_identity(root)
    dispositions = _load_dispositions(root / dispositions_path)

    if apply and not reconcile:
        raise typer.BadParameter("--apply requires --reconcile", param_hint="--apply")

    out_path = root / output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        canonical_json({"artifact": identity, "records": records}), encoding="utf-8"
    )
    side_path = root / dispositions_path
    if not side_path.exists():
        side_path.parent.mkdir(parents=True, exist_ok=True)
        side_path.write_text(canonical_json({}), encoding="utf-8")

    log_success(f"corpus audit: {len(records)} probe(s) across {len(db)} rule(s) → {output}")

    if reconcile:
        reconciled, unresolved, retired = reconcile_dispositions(records, identity, dispositions)
        log_success(
            "reconciliation: "
            f"carried {len(reconciled)} approval(s), retired {retired}, "
            f"unresolved {len(unresolved)}"
        )
        if apply:
            (root / dispositions_path).write_text(canonical_json(reconciled), encoding="utf-8")
            log_success(f"reconciliation: wrote {dispositions_path}")
        for record in unresolved:
            log_warning(
                f"unresolved: {record['rule_id']} via "
                f"{record['trigger_kind']}:{record['trigger_value']}"
            )
        if fail_on_miss and unresolved:
            raise typer.Exit(1)
        return

    misses, integrity = evaluate(records, identity, dispositions)

    if integrity:
        for msg in integrity:
            log_error(msg)
        log_error("plan-owner-review-required: disposition integrity failure")
        raise typer.Exit(2)

    if not misses:
        log_success("corpus audit: zero unexplained required-rule manifest misses")
        return

    new_families = {_family(m["rule_id"]) for m in misses} - KNOWN_AFFECTED_FAMILIES
    for m in misses:
        log_warning(
            f"miss: {m['rule_id']} via {m['trigger_kind']}:{m['trigger_value']} "
            f"(rank={m['rank']}, score={m['score']}, source={m['prompt_source']})"
        )
    broke, _ = should_circuit_break(misses)
    if broke:
        log_error(
            f"plan-owner-review-required: scope circuit break "
            f"({len(misses)} misses across {len(new_families)} previously-unaffected "
            f"families {sorted(new_families)})"
        )
        raise typer.Exit(2)

    log_error(f"{len(misses)} unresolved required-rule manifest miss(es)")
    if fail_on_miss:
        raise typer.Exit(1)
