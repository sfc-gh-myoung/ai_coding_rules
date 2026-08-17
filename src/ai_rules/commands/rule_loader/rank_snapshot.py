"""``ai-rules rule-loader rank-snapshot``: identity-pinned before/after rank snapshot.

Focused command module (Phase 2). It captures, for every fixture x required-rule
pair, the matcher rank / score / manifest-membership in two stages: ``baseline``
(before the Phase 2 matcher change) and ``current`` (after): merges them into a
single canonical committed artifact, and validates it (``--check``).

Design contract (v5 plan Section 9, Phase 2):

- Generated observations are canonical and contain no reviewed dispositions.
- Reviewed explanations live in a separate sidecar keyed by stable record identity.
- Both artifacts carry / reference source+corpus identity (git SHA, rules digest,
  matcher digest, schema version, generator version).
- ``--check`` regenerates the current half, compares generated output and identity
  metadata byte-for-byte to the committed artifact, and fails on any unexplained
  regression (``in_manifest_baseline`` true, ``in_manifest_current`` false) that
  lacks a matching sidecar disposition, or on missing/duplicate/stale sidecar keys.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

import typer

from ai_rules._shared.console import console, err_console
from ai_rules._shared.paths import find_project_root
from ai_rules.match_rules import (
    FileContext,
    RuleEntry,
    _extract_from_prompt,
    build_manifest,
    load_rules_db,
    match_rules,
    resolve_dependencies,
)
from ai_rules.rule_loader_eval.fixtures import Fixture, load_fixtures

GENERATOR_VERSION = "1"
FOUNDATION_RULE = "rules/000-global-core.md"
MAX_DIRECT = 3
MAX_TOKENS = 100_000

DEFAULT_OUTPUT = Path("reports/phase2-rank-snapshot.json")
DEFAULT_DISPOSITIONS = Path("reports/phase2-rank-snapshot-dispositions.json")


def _default_baseline_path(output: Path) -> Path:
    """Interim baseline-half path derived from the merged output path."""
    return output.with_suffix(".baseline.json")


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


def _git_sha(project_root: Path) -> str:
    """Return the current git commit SHA, or ``"unknown"`` if unavailable."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip() or "unknown"
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def _rules_digest(rules_dir: Path) -> str:
    """SHA-256 over the sorted rule filenames and their bytes."""
    h = hashlib.sha256()
    for md_path in sorted(rules_dir.glob("*.md")):
        if md_path.name == "README.md":
            continue
        h.update(md_path.name.encode("utf-8"))
        h.update(b"\0")
        h.update(md_path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def _matcher_digest(project_root: Path) -> str:
    """SHA-256 of the canonical matcher source file."""
    matcher = project_root / "src" / "ai_rules" / "match_rules.py"
    try:
        return hashlib.sha256(matcher.read_bytes()).hexdigest()
    except OSError:
        return "unknown"


def _schema_version(project_root: Path) -> str:
    """Parse the ``version`` scalar from the rule schema (stdlib-only)."""
    schema = project_root / "schemas" / "rule-schema.yml"
    try:
        for line in schema.read_text(encoding="utf-8").splitlines():
            m = re.match(r'^version:\s*"?([^"\s]+)"?\s*$', line)
            if m:
                return m.group(1)
    except OSError:
        pass
    return "unknown"


@dataclass(frozen=True)
class Identity:
    """Source + corpus identity captured for one snapshot stage."""

    git_sha: str
    rules_digest: str
    matcher_digest: str

    @classmethod
    def capture(cls, project_root: Path, rules_dir: Path) -> Identity:
        """Capture identity from the checked-out tree."""
        return cls(
            git_sha=_git_sha(project_root),
            rules_digest=_rules_digest(rules_dir),
            matcher_digest=_matcher_digest(project_root),
        )


# ---------------------------------------------------------------------------
# Observations
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Observation:
    """One matcher observation for a fixture x required-rule pair."""

    rank: int | None
    score: int | None
    in_manifest: bool


def _manifest_paths(
    prompt: str, db: dict[str, RuleEntry]
) -> tuple[set[str], dict[str, int], dict[str, int]]:
    """Return (manifest rule_paths, rank-by-filename, score-by-filename) for a prompt.

    ``match_rules`` is called directly against the prompt and loaded rules DB, then
    the production manifest cap/dependency resolution (``MAX_DIRECT``) is applied so
    ``in_manifest`` reflects real manifest membership. The foundation rule is always
    considered present.
    """
    kw, ext, paths = _extract_from_prompt(prompt)
    scored = match_rules(kw, FileContext(extensions=ext, paths=paths), list(db.values()))
    rank_by_fn = {sr.rule.filename: i + 1 for i, sr in enumerate(scored)}
    score_by_fn = {sr.rule.filename: sr.score for sr in scored}
    matched_filenames = {sr.rule.filename for sr in scored[:MAX_DIRECT]}
    resolved, warnings = resolve_dependencies(scored, db, max_direct=MAX_DIRECT)
    manifest = build_manifest(
        resolved,
        warnings,
        matched_filenames=matched_filenames,
        max_entries=MAX_DIRECT,
        max_tokens=MAX_TOKENS,
    )
    manifest_paths = {e["rule_path"] for e in manifest["load_sequence"]}
    manifest_paths.add(FOUNDATION_RULE)
    return manifest_paths, rank_by_fn, score_by_fn


def compute_observations(
    fixtures: list[Fixture], db: dict[str, RuleEntry]
) -> dict[tuple[str, str], Observation]:
    """Compute observations for every (fixture, required-rule) pair.

    Args:
        fixtures: Loaded fixtures.
        db: Loaded rules database.

    Returns:
        A dict keyed by ``(fixture_id, rule_id)`` mapping to an :class:`Observation`.
    """
    result: dict[tuple[str, str], Observation] = {}
    for fx in fixtures:
        manifest_paths, rank_by_fn, score_by_fn = _manifest_paths(fx.prompt, db)
        for rule_id in fx.required:
            filename = rule_id.split("/")[-1]
            result[(fx.id, rule_id)] = Observation(
                rank=rank_by_fn.get(filename),
                score=score_by_fn.get(filename),
                in_manifest=rule_id in manifest_paths,
            )
    return result


# ---------------------------------------------------------------------------
# Canonical serialization
# ---------------------------------------------------------------------------


def canonical_json(obj: Any) -> str:
    """Serialize ``obj`` as canonical JSON (sorted keys, 2-space indent, trailing newline)."""
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _records_from_observations(
    obs: dict[tuple[str, str], Observation],
) -> list[dict[str, Any]]:
    """Sorted per-pair record skeletons (fixture asc, then rule_id asc)."""
    records = []
    for fixture_id, rule_id in sorted(obs.keys()):
        o = obs[(fixture_id, rule_id)]
        records.append(
            {
                "fixture": fixture_id,
                "rule_id": rule_id,
                "rank": o.rank,
                "score": o.score,
                "in_manifest": o.in_manifest,
            }
        )
    return records


# ---------------------------------------------------------------------------
# Stage capture + merge
# ---------------------------------------------------------------------------


def _load_project() -> tuple[Path, dict[str, RuleEntry], list[Fixture]]:
    root = find_project_root()
    rules_dir = root / "rules"
    fixtures_dir = root / "fixtures" / "rule_loader_eval"
    db = load_rules_db(rules_dir)
    fixtures = load_fixtures(fixtures_dir, enforce_invariant=False)
    return root, db, fixtures


def capture_baseline(output: Path) -> Path:
    """Capture the baseline half and write it to the interim baseline file."""
    root, db, fixtures = _load_project()
    obs = compute_observations(fixtures, db)
    identity = Identity.capture(root, root / "rules")
    payload = {
        "stage": "baseline",
        "identity": {
            "git_sha": identity.git_sha,
            "rules_digest": identity.rules_digest,
            "matcher_digest": identity.matcher_digest,
        },
        "records": _records_from_observations(obs),
    }
    baseline_path = _default_baseline_path(output)
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(canonical_json(payload), encoding="utf-8")
    return baseline_path


def build_merged_artifact(
    baseline_payload: dict[str, Any],
    current_obs: dict[tuple[str, str], Observation],
    current_identity: Identity,
    schema_version: str,
) -> dict[str, Any]:
    """Merge a baseline payload with current observations into the committed artifact."""
    baseline_by_key: dict[tuple[str, str], dict[str, Any]] = {
        (r["fixture"], r["rule_id"]): r for r in baseline_payload["records"]
    }
    b_ident = baseline_payload["identity"]

    records: list[dict[str, Any]] = []
    all_keys = set(baseline_by_key) | set(current_obs)
    for fixture_id, rule_id in sorted(all_keys):
        b = baseline_by_key.get((fixture_id, rule_id))
        c = current_obs.get((fixture_id, rule_id))
        records.append(
            {
                "fixture": fixture_id,
                "rule_id": rule_id,
                "rank_baseline": b["rank"] if b else None,
                "score_baseline": b["score"] if b else None,
                "in_manifest_baseline": bool(b["in_manifest"]) if b else False,
                "rank_current": c.rank if c else None,
                "score_current": c.score if c else None,
                "in_manifest_current": bool(c.in_manifest) if c else False,
            }
        )

    return {
        "git_sha_baseline": b_ident["git_sha"],
        "git_sha_current": current_identity.git_sha,
        "rules_digest_baseline": b_ident["rules_digest"],
        "rules_digest_current": current_identity.rules_digest,
        "matcher_digest_baseline": b_ident["matcher_digest"],
        "matcher_digest_current": current_identity.matcher_digest,
        "schema_version": schema_version,
        "generator_version": GENERATOR_VERSION,
        "records": records,
    }


def capture_current(output: Path) -> dict[str, Any]:
    """Capture the current half, merge with the interim baseline, write the artifact."""
    root, db, fixtures = _load_project()
    baseline_path = _default_baseline_path(output)
    if not baseline_path.is_file():
        raise FileNotFoundError(
            f"baseline half not found at {baseline_path}; run `rank-snapshot --stage baseline` first"
        )
    baseline_payload = json.loads(baseline_path.read_text(encoding="utf-8"))
    current_obs = compute_observations(fixtures, db)
    identity = Identity.capture(root, root / "rules")
    artifact = build_merged_artifact(baseline_payload, current_obs, identity, _schema_version(root))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canonical_json(artifact), encoding="utf-8")
    return artifact


# ---------------------------------------------------------------------------
# Check
# ---------------------------------------------------------------------------


def _regression_keys(artifact: dict[str, Any]) -> set[tuple[str, str]]:
    """Keys whose required rule regressed out of the manifest (baseline true → current false)."""
    keys = set()
    for r in artifact["records"]:
        if r["in_manifest_baseline"] and not r["in_manifest_current"]:
            keys.add((r["fixture"], r["rule_id"]))
    return keys


def check_snapshot(output: Path, dispositions: Path) -> list[str]:
    """Validate the committed artifact. Returns a list of error strings (empty = OK).

    Checks:
    1. The artifact exists and is canonical (byte-identical to a re-serialization).
    2. Regenerated current observations + identity match the committed artifact.
    3. Every unexplained regression has exactly one matching sidecar disposition.
    4. No duplicate or stale sidecar keys.
    """
    errors: list[str] = []
    if not output.is_file():
        return [f"snapshot artifact not found: {output}"]

    raw = output.read_text(encoding="utf-8")
    try:
        artifact = json.loads(raw)
    except json.JSONDecodeError as exc:
        return [f"snapshot artifact is not valid JSON: {exc}"]

    # 1. canonical form
    if raw != canonical_json(artifact):
        errors.append("snapshot artifact is not in canonical JSON form")

    # 2. regenerate current half + identity and compare
    root, db, fixtures = _load_project()
    current_obs = compute_observations(fixtures, db)
    ident = Identity.capture(root, root / "rules")
    if artifact.get("git_sha_current") != ident.git_sha:
        errors.append(
            f"git_sha_current mismatch: artifact={artifact.get('git_sha_current')} tree={ident.git_sha}"
        )
    if artifact.get("rules_digest_current") != ident.rules_digest:
        errors.append("rules_digest_current mismatch: rules corpus differs from artifact")
    if artifact.get("matcher_digest_current") != ident.matcher_digest:
        errors.append("matcher_digest_current mismatch: matcher source differs from artifact")

    committed_current = {
        (r["fixture"], r["rule_id"]): (
            r["rank_current"],
            r["score_current"],
            r["in_manifest_current"],
        )
        for r in artifact["records"]
    }
    regen_current = {k: (o.rank, o.score, o.in_manifest) for k, o in current_obs.items()}
    if committed_current != regen_current:
        errors.append("regenerated current observations differ from committed artifact")

    # 3 + 4. sidecar dispositions
    regressions = _regression_keys(artifact)
    disp_keys: list[tuple[str, str]] = []
    if dispositions.is_file():
        try:
            disp_data = json.loads(dispositions.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return [*errors, f"dispositions sidecar is not valid JSON: {exc}"]
        for entry in (
            disp_data if isinstance(disp_data, list) else disp_data.get("dispositions", [])
        ):
            disp_keys.append((entry.get("fixture"), entry.get("rule_id")))

    seen: set[tuple[str, str]] = set()
    for key in disp_keys:
        if key in seen:
            errors.append(f"duplicate sidecar disposition for {key}")
        seen.add(key)
        record_keys = {(r["fixture"], r["rule_id"]) for r in artifact["records"]}
        if key not in record_keys:
            errors.append(f"stale sidecar disposition references unknown record {key}")

    for key in sorted(regressions):
        if key not in seen:
            errors.append(f"unexplained regression without sidecar disposition: {key}")

    return errors


# ---------------------------------------------------------------------------
# CLI command
# ---------------------------------------------------------------------------


def rank_snapshot_cmd(
    check: Annotated[
        Path | None,
        typer.Option("--check", help="Validate the committed snapshot artifact at PATH."),
    ] = None,
    stage: Annotated[
        str | None,
        typer.Option("--stage", help="Capture stage: 'baseline' or 'current'."),
    ] = None,
    output: Annotated[
        Path,
        typer.Option("--output", help="Merged artifact path."),
    ] = DEFAULT_OUTPUT,
    dispositions: Annotated[
        Path,
        typer.Option("--dispositions", help="Reviewed disposition sidecar path."),
    ] = DEFAULT_DISPOSITIONS,
) -> None:
    """Capture or validate the identity-pinned before/after rank snapshot.

    Exit codes: 0 = success / no unexplained regressions; 1 = check failed or
    unexplained regression; 4 = invalid arguments.
    """
    if check is not None:
        errs = check_snapshot(check, dispositions)
        if errs:
            for e in errs:
                err_console.print(f"[red]rank-snapshot check:[/red] {e}")
            raise typer.Exit(1)
        console.print("[green]rank-snapshot check passed[/green]")
        raise typer.Exit(0)

    if stage == "baseline":
        path = capture_baseline(output)
        console.print(f"[green]baseline captured[/green] → {path}")
        raise typer.Exit(0)

    if stage == "current":
        capture_current(output)
        console.print(f"[green]current captured and merged[/green] → {output}")
        raise typer.Exit(0)

    err_console.print("[red]rank-snapshot:[/red] provide --check PATH or --stage baseline|current")
    raise typer.Exit(4)
