"""Snapshot schema for rule-loader A/B comparisons.

Phase 4 (ai-rules-eval-results-dir plan) migrated the on-disk layout from
the legacy ``out/<label>/eval/`` tree to a streaming ``results/``-style
tree, so a directory produced by :func:`write_eval_snapshot` is now a
minimal ``ResultsRunWriter`` output that :func:`read_eval_snapshot` can
also consume::

    <snapshot_dir>/
      manifest.json                       # translated from SnapshotMeta
      summary.json                        # aggregate summary (§5.4)
      run-01/
        run_meta.json                     # per-pass metadata
        summary.json                      # per-pass summary (§5.3)
        fixtures/
          <fixture_id>.json               # per-fixture snapshot row

The in-memory ``FixtureSnapshot`` / ``SnapshotMeta`` / ``SnapshotSummary`` /
``Snapshot`` dataclasses are unchanged — only the serializers switch to
the new file layout. Business logic in ``compare.py`` and
``merge-snapshots`` therefore does not change.

Read-side is **new-layout only** (§8 of the plan). Reading legacy
``out/<label>/`` snapshots is out of scope; users re-run under the new
layout if they need to compare against an old baseline.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_rules.rule_loader_eval.engine import RunResult
    from ai_rules.rule_loader_eval.fixtures import Fixture

SNAPSHOT_SCHEMA_VERSION = 1

# Constants matching the results_schemas.py schema_version strings so
# manifest/summary files read by ``read_eval_snapshot`` carry the same
# markers a fresh eval run writes.
_MANIFEST_SCHEMA = "ai-rules-eval-manifest/v1"
_RUN_META_SCHEMA = "ai-rules-eval-run-meta/v1"
_PASS_SUMMARY_SCHEMA = "ai-rules-eval-summary/v1"
_AGG_SUMMARY_SCHEMA = "ai-rules-eval-aggregate/v1"
_FIXTURE_SCHEMA = "ai-rules-eval-fixture-snapshot/v1"


@dataclass(frozen=True)
class FixtureSnapshot:
    """One fixture's evaluation outcome captured for cross-snapshot diffing.

    Field set chosen to be stable across rule-loading mechanism changes.
    All values are derived from the live ``RunResult`` plus the static fixture; nothing is recomputed
    against current rule metadata when read back, so a snapshot remains
    valid forever.
    """

    fixture_id: str
    passed: bool
    loaded: tuple[str, ...]
    expected_required: tuple[str, ...]
    expected_dependencies: tuple[str, ...]
    expected_optional: tuple[str, ...]
    expected_forbidden: tuple[str, ...]
    missing_required: tuple[str, ...]
    missing_dependencies: tuple[str, ...]
    forbidden_present: tuple[str, ...]
    signal_disagreements: int
    citation_drifts: int
    turns: int
    duration_ms: int
    model: str = ""
    stop_reason: str = ""
    is_infra_error: bool = False
    """v3.15: True when the run was an SDK / model / connection failure (not a fixture failure)."""
    infra_error_detail: str = ""
    """v3.15: Human-readable detail for is_infra_error rows."""
    # Signal-investigation fields (added schema_version 2). Empty tuples on
    # snapshots produced before these fields were persisted.
    loaded_via_reads: tuple[str, ...] = ()
    """Paths captured from real ``read_file`` tool calls."""
    loaded_via_section: tuple[str, ...] = ()
    """Paths the agent declared under its ``## Rules Loaded`` section."""
    disagreement_details: tuple[str, ...] = ()
    """Per-rule mismatch records (e.g. ``only-in-rules-loaded-vs-tool-reads: rules/...``)."""
    # Flake / variance fields (added for multi-run merge). Defaults for
    # snapshots produced by single-run eval (n_runs=1, flake_score=0.0).
    flake_score: float = 0.0
    """1 - jaccard(union, intersection) of loaded sets across input runs."""
    n_runs: int = 1
    """Number of runs merged into this snapshot row (1 for single-run eval)."""
    skill_invocations: tuple[str, ...] = ()
    """Names of skills invoked during this run (e.g. ``(\"rule-loader\",)``)."""
    depends_violations: tuple[str, ...] = ()
    """R8 violations: rules loaded whose required: deps were not loaded.
    Each entry formatted as ``'PARENT requires CHILD (not loaded)'``.
    """
    output_violations: tuple[str, ...] = ()
    """Bootstrap/no-match output-shape violations from the final assistant text."""
    # Token / cost fields (added for eval cost tracking). Zero for non-live runs.
    input_tokens: int = 0
    """Total input tokens for this fixture (0 when SDK unavailable or non-live run)."""
    output_tokens: int = 0
    """Total output tokens for this fixture."""
    total_tokens: int = 0
    """input_tokens + output_tokens (computed at serialize time)."""
    total_cost_usd: float = 0.0
    """Total cost in USD for this fixture run (0 when SDK unavailable)."""

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict (tuples become lists)."""
        return {
            "fixture_id": self.fixture_id,
            "passed": self.passed,
            "loaded": list(self.loaded),
            "expected_required": list(self.expected_required),
            "expected_dependencies": list(self.expected_dependencies),
            "expected_optional": list(self.expected_optional),
            "expected_forbidden": list(self.expected_forbidden),
            "missing_required": list(self.missing_required),
            "missing_dependencies": list(self.missing_dependencies),
            "forbidden_present": list(self.forbidden_present),
            "signal_disagreements": self.signal_disagreements,
            "citation_drifts": self.citation_drifts,
            "turns": self.turns,
            "duration_ms": self.duration_ms,
            "model": self.model,
            "stop_reason": self.stop_reason,
            "is_infra_error": self.is_infra_error,
            "infra_error_detail": self.infra_error_detail,
            "loaded_via_reads": list(self.loaded_via_reads),
            "loaded_via_section": list(self.loaded_via_section),
            "disagreement_details": list(self.disagreement_details),
            "flake_score": self.flake_score,
            "n_runs": self.n_runs,
            "skill_invocations": list(self.skill_invocations),
            "depends_violations": list(self.depends_violations),
            "output_violations": list(self.output_violations),
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost_usd,
        }

    @classmethod
    def from_dict(cls, data: dict) -> FixtureSnapshot:
        """Parse a snapshot back from JSON. Missing fields default to empty/zero."""
        return cls(
            fixture_id=data["fixture_id"],
            passed=bool(data["passed"]),
            loaded=tuple(data.get("loaded") or ()),
            expected_required=tuple(data.get("expected_required") or ()),
            expected_dependencies=tuple(data.get("expected_dependencies") or ()),
            expected_optional=tuple(data.get("expected_optional") or ()),
            expected_forbidden=tuple(data.get("expected_forbidden") or ()),
            missing_required=tuple(data.get("missing_required") or ()),
            missing_dependencies=tuple(data.get("missing_dependencies") or ()),
            forbidden_present=tuple(data.get("forbidden_present") or ()),
            signal_disagreements=int(data.get("signal_disagreements") or 0),
            citation_drifts=int(data.get("citation_drifts") or 0),
            turns=int(data.get("turns") or 0),
            duration_ms=int(data.get("duration_ms") or 0),
            model=str(data.get("model") or ""),
            stop_reason=str(data.get("stop_reason") or ""),
            is_infra_error=bool(data.get("is_infra_error") or False),
            infra_error_detail=str(data.get("infra_error_detail") or ""),
            loaded_via_reads=tuple(data.get("loaded_via_reads") or ()),
            loaded_via_section=tuple(data.get("loaded_via_section") or ()),
            disagreement_details=tuple(data.get("disagreement_details") or ()),
            flake_score=float(data.get("flake_score") or 0.0),
            n_runs=int(data.get("n_runs") or 1),
            skill_invocations=tuple(data.get("skill_invocations") or ()),
            depends_violations=tuple(data.get("depends_violations") or ()),
            output_violations=tuple(data.get("output_violations") or ()),
            input_tokens=int(data.get("input_tokens") or 0),
            output_tokens=int(data.get("output_tokens") or 0),
            total_tokens=int(data.get("total_tokens") or 0),
            total_cost_usd=float(data.get("total_cost_usd") or 0.0),
        )


@dataclass(frozen=True)
class SnapshotMeta:
    """Environment metadata captured alongside the per-fixture snapshots."""

    schema_version: int = SNAPSHOT_SCHEMA_VERSION
    captured_at: str = ""
    git_commit: str = ""
    git_branch: str = ""
    model: str = ""
    max_turns: int = 0
    effort: str = ""
    fixtures_dir: str = "fixtures/rule_loader_eval"
    rules_dir: str = "rules"
    label: str = ""
    notes: str = ""

    def to_dict(self) -> dict:  # noqa: D102
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> SnapshotMeta:  # noqa: D102
        return cls(
            schema_version=int(data.get("schema_version") or SNAPSHOT_SCHEMA_VERSION),
            captured_at=str(data.get("captured_at") or ""),
            git_commit=str(data.get("git_commit") or ""),
            git_branch=str(data.get("git_branch") or ""),
            model=str(data.get("model") or ""),
            max_turns=int(data.get("max_turns") or 0),
            effort=str(data.get("effort") or ""),
            fixtures_dir=str(data.get("fixtures_dir") or "fixtures/rule_loader_eval"),
            rules_dir=str(data.get("rules_dir") or "rules"),
            label=str(data.get("label") or ""),
            notes=str(data.get("notes") or ""),
        )


@dataclass(frozen=True)
class SnapshotSummary:
    """Aggregate statistics over a snapshot's per-fixture results."""

    total: int
    passed: int
    failed: int
    mean_turns: float
    mean_duration_ms: float
    total_signal_disagreements: int
    total_citation_drifts: int
    mean_input_tokens: float = 0.0
    mean_output_tokens: float = 0.0
    mean_total_tokens: float = 0.0
    mean_total_cost_usd: float = 0.0

    def to_dict(self) -> dict:  # noqa: D102
        return asdict(self)


@dataclass(frozen=True)
class Snapshot:
    """A complete snapshot: meta + per-fixture results + summary."""

    meta: SnapshotMeta
    fixtures: tuple[FixtureSnapshot, ...] = field(default_factory=tuple)
    summary: SnapshotSummary | None = None


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------


def serialize_run_result(result: RunResult, fixture: Fixture) -> FixtureSnapshot:
    """Convert an in-memory ``RunResult`` into a stable on-disk snapshot row."""
    return FixtureSnapshot(
        fixture_id=result.fixture_id,
        passed=result.passed,
        loaded=tuple(result.run.loaded),
        expected_required=tuple(fixture.required),
        expected_dependencies=tuple(fixture.dependencies),
        expected_optional=tuple(fixture.optional),
        expected_forbidden=tuple(fixture.forbidden),
        missing_required=tuple(result.match.missing_required),
        missing_dependencies=tuple(result.match.missing_dependencies),
        forbidden_present=tuple(result.match.forbidden_present),
        signal_disagreements=len(result.signal_report.disagreements),
        citation_drifts=len(result.citation_drifts),
        turns=result.run.turns,
        duration_ms=result.run.duration_ms,
        model=result.run.model,
        stop_reason=result.run.stop_reason,
        is_infra_error=getattr(result.run, "is_infra_error", False),
        infra_error_detail=getattr(result.run, "infra_error_detail", ""),
        loaded_via_reads=tuple(result.run.loaded_via_reads),
        loaded_via_section=tuple(result.run.loaded_via_section),
        disagreement_details=tuple(result.run.disagreements),
        skill_invocations=tuple(result.run.skill_invocations),
        depends_violations=tuple(str(v) for v in result.depends_violations),
        output_violations=tuple(result.run.output_violations),
        input_tokens=getattr(result.run, "input_tokens", 0),
        output_tokens=getattr(result.run, "output_tokens", 0),
        total_tokens=getattr(result.run, "input_tokens", 0)
        + getattr(result.run, "output_tokens", 0),
        total_cost_usd=float(getattr(result.run, "total_cost_usd", 0.0) or 0.0),
    )


def compute_summary(fixtures: list[FixtureSnapshot]) -> SnapshotSummary:
    """Aggregate per-fixture metrics into a single summary record."""
    total = len(fixtures)
    if total == 0:
        return SnapshotSummary(0, 0, 0, 0.0, 0.0, 0, 0)
    passed = sum(1 for f in fixtures if f.passed)
    return SnapshotSummary(
        total=total,
        passed=passed,
        failed=total - passed,
        mean_turns=round(sum(f.turns for f in fixtures) / total, 2),
        mean_duration_ms=round(sum(f.duration_ms for f in fixtures) / total, 2),
        total_signal_disagreements=sum(f.signal_disagreements for f in fixtures),
        total_citation_drifts=sum(f.citation_drifts for f in fixtures),
        mean_input_tokens=round(sum(f.input_tokens for f in fixtures) / total, 2),
        mean_output_tokens=round(sum(f.output_tokens for f in fixtures) / total, 2),
        mean_total_tokens=round(sum(f.total_tokens for f in fixtures) / total, 2),
        mean_total_cost_usd=round(sum(f.total_cost_usd for f in fixtures) / total, 6),
    )


def _meta_to_manifest(meta: SnapshotMeta, *, fixture_count: int) -> dict:
    """Translate a :class:`SnapshotMeta` into a §5.1 manifest dict.

    The captured-at timestamp becomes ``started_at`` / ``updated_at`` /
    ``completed_at``; git fields are collapsed under ``git``; the label
    passes through. Fields not present on ``SnapshotMeta`` (run_id,
    concurrency, runs_requested) are given reproducible defaults so the
    manifest still validates against the §5.1 shape.
    """
    ts = meta.captured_at or ""
    return {
        "schema_version": _MANIFEST_SCHEMA,
        "run_id": f"snapshot-{(meta.label or 'snapshot').strip() or 'snapshot'}",
        "run_dir_name": (meta.label or "snapshot").strip() or "snapshot",
        "started_at": ts,
        "updated_at": ts,
        "completed_at": ts,
        "model_requested": meta.model,
        "model_resolved": meta.model or None,
        "effort": meta.effort,
        "max_turns": int(meta.max_turns),
        "strict_forbidden": False,
        "concurrency": 1,
        "runs_requested": 1,
        "label": meta.label or None,
        "connection": "",
        "git": {"sha": meta.git_commit, "branch": meta.git_branch, "dirty": False},
        "ai_rules_version": "",
        "fixture_selection": ["all"],
        "fixture_count": int(fixture_count),
        "passes": [
            {
                "run_number": 1,
                "dir": "run-01",
                "status": "completed",
                "started_at": ts,
                "completed_at": ts,
                "totals": {"passed": 0, "failed": 0, "errors": 0},
            }
        ],
        "aggregate_status": "completed",
        # Round-trip helpers for SnapshotMeta fields not in §5.1.
        "snapshot_meta_extras": {
            "fixtures_dir": meta.fixtures_dir,
            "rules_dir": meta.rules_dir,
            "notes": meta.notes,
            "snapshot_schema_version": int(meta.schema_version),
        },
    }


def _manifest_to_meta(manifest: dict) -> SnapshotMeta:
    """Inverse of :func:`_meta_to_manifest` — best-effort SnapshotMeta reconstruction."""
    extras = manifest.get("snapshot_meta_extras") or {}
    git = manifest.get("git") or {}
    return SnapshotMeta(
        schema_version=int(extras.get("snapshot_schema_version") or SNAPSHOT_SCHEMA_VERSION),
        captured_at=str(manifest.get("started_at") or ""),
        git_commit=str(git.get("sha") or ""),
        git_branch=str(git.get("branch") or ""),
        model=str(manifest.get("model_requested") or ""),
        max_turns=int(manifest.get("max_turns") or 0),
        effort=str(manifest.get("effort") or ""),
        fixtures_dir=str(extras.get("fixtures_dir") or "fixtures/rule_loader_eval"),
        rules_dir=str(extras.get("rules_dir") or "rules"),
        label=str(manifest.get("label") or ""),
        notes=str(extras.get("notes") or ""),
    )


def _fixture_to_doc(fx: FixtureSnapshot, *, run_number: int = 1) -> dict:
    """Emit a per-fixture doc that satisfies §5.5 while preserving snapshot extras.

    Fields required by §5.5 are written at the top level with the exact
    types documented there. Snapshot-specific fields that don't fit §5.5
    (``flake_score``, ``n_runs``, ``loaded_via_section``,
    ``disagreement_details``, ``expected_*``, ``total_tokens``) live under
    ``snapshot_extras`` so ``read_eval_snapshot`` can round-trip a
    ``FixtureSnapshot`` losslessly.
    """
    if fx.is_infra_error:
        result_str = "error"
    elif fx.passed:
        result_str = "pass"
    else:
        result_str = "fail"
    return {
        "schema_version": _FIXTURE_SCHEMA,
        "fixture_id": fx.fixture_id,
        "run_number": int(run_number),
        "model": fx.model,
        "passed": bool(fx.passed),
        "result": result_str,
        "match": {
            "missing_required": list(fx.missing_required),
            "missing_dependencies": list(fx.missing_dependencies),
            "forbidden_present": list(fx.forbidden_present),
            "extra_loaded": [],
        },
        "signal_report": {
            "ok": int(fx.signal_disagreements) == 0,
            "disagreements": list(fx.disagreement_details),
        },
        "citation_drifts": [{"index": i} for i in range(int(fx.citation_drifts))],
        "depends_violations": list(fx.depends_violations),
        "output_violations": list(fx.output_violations),
        "turns": int(fx.turns),
        "input_tokens": int(fx.input_tokens),
        "output_tokens": int(fx.output_tokens),
        "total_cost_usd": float(fx.total_cost_usd),
        "duration_ms": int(fx.duration_ms),
        "final_text": None,
        "stop_reason": fx.stop_reason,
        "is_infra_error": bool(fx.is_infra_error),
        "infra_error_detail": fx.infra_error_detail or None,
        "skill_invocations": list(fx.skill_invocations),
        "loaded": list(fx.loaded),
        "loaded_via_reads": list(fx.loaded_via_reads),
        # Round-trip helpers.
        "snapshot_extras": {
            "expected_required": list(fx.expected_required),
            "expected_dependencies": list(fx.expected_dependencies),
            "expected_optional": list(fx.expected_optional),
            "expected_forbidden": list(fx.expected_forbidden),
            "loaded_via_section": list(fx.loaded_via_section),
            "flake_score": float(fx.flake_score),
            "n_runs": int(fx.n_runs),
            "total_tokens": int(fx.total_tokens),
            "signal_disagreements_count": int(fx.signal_disagreements),
            "citation_drifts_count": int(fx.citation_drifts),
        },
    }


def _doc_to_fixture(doc: dict) -> FixtureSnapshot:
    """Inverse of :func:`_fixture_to_doc` — reconstruct a :class:`FixtureSnapshot`."""
    extras = doc.get("snapshot_extras") or {}
    match = doc.get("match") or {}
    signal_report = doc.get("signal_report") or {}
    citation_drifts_field = doc.get("citation_drifts")
    if isinstance(citation_drifts_field, list):
        cd_count = int(extras.get("citation_drifts_count") or len(citation_drifts_field))
    else:
        cd_count = int(citation_drifts_field or 0)
    disagreements = signal_report.get("disagreements") or []
    sd_raw = extras.get("signal_disagreements_count")
    sd_count = len(disagreements) if sd_raw is None else int(sd_raw)
    return FixtureSnapshot(
        fixture_id=str(doc.get("fixture_id") or ""),
        passed=bool(doc.get("passed") or False),
        loaded=tuple(doc.get("loaded") or ()),
        expected_required=tuple(extras.get("expected_required") or ()),
        expected_dependencies=tuple(extras.get("expected_dependencies") or ()),
        expected_optional=tuple(extras.get("expected_optional") or ()),
        expected_forbidden=tuple(extras.get("expected_forbidden") or ()),
        missing_required=tuple(match.get("missing_required") or ()),
        missing_dependencies=tuple(match.get("missing_dependencies") or ()),
        forbidden_present=tuple(match.get("forbidden_present") or ()),
        signal_disagreements=sd_count,
        citation_drifts=cd_count,
        turns=int(doc.get("turns") or 0),
        duration_ms=int(doc.get("duration_ms") or 0),
        model=str(doc.get("model") or ""),
        stop_reason=str(doc.get("stop_reason") or ""),
        is_infra_error=bool(doc.get("is_infra_error") or False),
        infra_error_detail=str(doc.get("infra_error_detail") or ""),
        loaded_via_reads=tuple(doc.get("loaded_via_reads") or ()),
        loaded_via_section=tuple(extras.get("loaded_via_section") or ()),
        disagreement_details=tuple(str(d) for d in disagreements),
        flake_score=float(extras.get("flake_score") or 0.0),
        n_runs=int(extras.get("n_runs") or 1),
        skill_invocations=tuple(doc.get("skill_invocations") or ()),
        depends_violations=tuple(doc.get("depends_violations") or ()),
        output_violations=tuple(doc.get("output_violations") or ()),
        input_tokens=int(doc.get("input_tokens") or 0),
        output_tokens=int(doc.get("output_tokens") or 0),
        total_tokens=int(extras.get("total_tokens") or 0),
        total_cost_usd=float(doc.get("total_cost_usd") or 0.0),
    )


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_eval_snapshot(
    out_dir: Path,
    fixtures: list[FixtureSnapshot],
    meta: SnapshotMeta,
) -> None:
    """Write a snapshot to ``out_dir`` using the results/ layout (Phase 4).

    Layout:
      <out_dir>/manifest.json
      <out_dir>/summary.json                          (aggregate)
      <out_dir>/run-01/run_meta.json
      <out_dir>/run-01/summary.json                   (per-pass)
      <out_dir>/run-01/fixtures/<fixture_id>.json     (one per fixture)

    ``SnapshotMeta`` extras (fixtures_dir, rules_dir, notes) and
    ``FixtureSnapshot`` extras (flake_score, expected_*, etc.) that don't
    fit §5.1/§5.5 are stored under ``snapshot_meta_extras`` / ``snapshot_extras``
    so :func:`read_eval_snapshot` round-trips losslessly.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    pass_dir = out_dir / "run-01"
    fixtures_dir = pass_dir / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    summary = compute_summary(fixtures)
    passed = sum(1 for f in fixtures if f.passed)
    errors = sum(1 for f in fixtures if f.is_infra_error)
    failed = len(fixtures) - passed - errors
    failures = [f.fixture_id for f in fixtures if not f.passed]

    manifest = _meta_to_manifest(meta, fixture_count=len(fixtures))
    manifest["passes"][0]["totals"] = {
        "passed": passed,
        "failed": failed,
        "errors": errors,
    }
    _write_json(out_dir / "manifest.json", manifest)

    aggregate = {
        "schema_version": _AGG_SUMMARY_SCHEMA,
        "runs": 1,
        "fixture_count": len(fixtures),
        "per_fixture": {
            f.fixture_id: {
                "n_runs": int(f.n_runs),
                "passes": 1 if f.passed else 0,
                "fails": 0 if f.passed else 1,
                "flake_score": float(f.flake_score),
                "pass_rate": 1.0 if f.passed else 0.0,
            }
            for f in fixtures
        },
        "aggregate": {
            "mean_pass_rate": round(passed / len(fixtures), 3) if fixtures else 0.0,
            "flaky_fixtures": [],
            "total_cost_usd": float(sum(f.total_cost_usd for f in fixtures)),
            "total_input_tokens": int(sum(f.input_tokens for f in fixtures)),
            "total_output_tokens": int(sum(f.output_tokens for f in fixtures)),
            "total_duration_ms": int(sum(f.duration_ms for f in fixtures)),
            "total_signal_disagreements": int(summary.total_signal_disagreements),
            "total_citation_drifts": int(summary.total_citation_drifts),
        },
        # Round-trip helpers so read_eval_snapshot can reconstruct SnapshotSummary.
        "snapshot_summary_extras": {
            "mean_turns": float(summary.mean_turns),
            "mean_duration_ms": float(summary.mean_duration_ms),
            "mean_input_tokens": float(summary.mean_input_tokens),
            "mean_output_tokens": float(summary.mean_output_tokens),
            "mean_total_tokens": float(summary.mean_total_tokens),
            "mean_total_cost_usd": float(summary.mean_total_cost_usd),
            "total": int(summary.total),
            "passed": int(summary.passed),
            "failed": int(summary.failed),
        },
    }
    _write_json(out_dir / "summary.json", aggregate)

    run_meta = {
        "schema_version": _RUN_META_SCHEMA,
        "run_id": manifest["run_id"],
        "run_number": 1,
        "started_at": manifest["started_at"],
        "completed_at": manifest["completed_at"],
        "model_requested": meta.model,
        "model_resolved": meta.model or None,
        "effort": meta.effort,
        "max_turns": int(meta.max_turns),
        "strict_forbidden": False,
        "concurrency": 1,
        "git": manifest["git"],
        "fixture_count": len(fixtures),
        "fixtures": {
            f.fixture_id: {
                "status": "completed",
                "result": "error" if f.is_infra_error else ("pass" if f.passed else "fail"),
                "started_at": manifest["started_at"],
                "completed_at": manifest["completed_at"],
            }
            for f in fixtures
        },
    }
    _write_json(pass_dir / "run_meta.json", run_meta)

    pass_summary = {
        "schema_version": _PASS_SUMMARY_SCHEMA,
        "run_number": 1,
        "total": len(fixtures),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "pass_rate": round(passed / len(fixtures), 3) if fixtures else 0.0,
        "totals": {
            "turns": int(sum(f.turns for f in fixtures)),
            "input_tokens": int(sum(f.input_tokens for f in fixtures)),
            "output_tokens": int(sum(f.output_tokens for f in fixtures)),
            "total_cost_usd": float(sum(f.total_cost_usd for f in fixtures)),
            "duration_ms": int(sum(f.duration_ms for f in fixtures)),
        },
        "failures": failures,
    }
    _write_json(pass_dir / "summary.json", pass_summary)

    for fx in fixtures:
        safe = fx.fixture_id.replace("/", "_").replace(" ", "_")
        _write_json(fixtures_dir / f"{safe}.json", _fixture_to_doc(fx))


def read_eval_snapshot(snapshot_dir: Path) -> Snapshot:
    """Load a snapshot from the new results/ layout (Phase 4, new-layout only).

    Raises ``ValueError`` for a missing ``manifest.json`` or unsupported
    embedded ``snapshot_schema_version``. Returns a :class:`Snapshot` with
    empty fixtures tuple when the ``run-01/fixtures/`` subdir is absent.
    Legacy ``out/<label>/`` snapshots are **not** supported — see §8 of
    the eval results-dir plan.
    """
    manifest_path = snapshot_dir / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError(f"no manifest.json under {snapshot_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    embedded_schema = (manifest.get("snapshot_meta_extras") or {}).get(
        "snapshot_schema_version"
    ) or SNAPSHOT_SCHEMA_VERSION
    if int(embedded_schema) != SNAPSHOT_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported snapshot schema_version {embedded_schema!r}; "
            f"expected {SNAPSHOT_SCHEMA_VERSION}"
        )

    meta = _manifest_to_meta(manifest)

    pass_dir = snapshot_dir / "run-01"
    fixtures_dir = pass_dir / "fixtures"
    fixture_rows: list[FixtureSnapshot] = []
    if fixtures_dir.is_dir():
        for path in sorted(fixtures_dir.glob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            fixture_rows.append(_doc_to_fixture(doc))

    summary: SnapshotSummary | None = None
    aggregate_path = snapshot_dir / "summary.json"
    if aggregate_path.is_file():
        agg = json.loads(aggregate_path.read_text(encoding="utf-8"))
        extras = agg.get("snapshot_summary_extras") or {}
        aggregate_totals = agg.get("aggregate") or {}
        summary = SnapshotSummary(
            total=int(extras.get("total") or agg.get("fixture_count") or 0),
            passed=int(extras.get("passed") or 0),
            failed=int(extras.get("failed") or 0),
            mean_turns=float(extras.get("mean_turns") or 0.0),
            mean_duration_ms=float(extras.get("mean_duration_ms") or 0.0),
            total_signal_disagreements=int(aggregate_totals.get("total_signal_disagreements") or 0),
            total_citation_drifts=int(aggregate_totals.get("total_citation_drifts") or 0),
            mean_input_tokens=float(extras.get("mean_input_tokens") or 0.0),
            mean_output_tokens=float(extras.get("mean_output_tokens") or 0.0),
            mean_total_tokens=float(extras.get("mean_total_tokens") or 0.0),
            mean_total_cost_usd=float(extras.get("mean_total_cost_usd") or 0.0),
        )

    return Snapshot(meta=meta, fixtures=tuple(fixture_rows), summary=summary)


def capture_meta(
    project_root: Path,
    *,
    model: str,
    max_turns: int,
    effort: str,
    label: str = "",
    notes: str = "",
) -> SnapshotMeta:
    """Capture environment metadata at run time (commit SHA, branch, timestamp)."""
    git_commit = _git_short_sha(project_root)
    git_branch = _git_branch(project_root)
    now = datetime.now().astimezone().replace(microsecond=0).isoformat()
    return SnapshotMeta(
        schema_version=SNAPSHOT_SCHEMA_VERSION,
        captured_at=now,
        git_commit=git_commit,
        git_branch=git_branch,
        model=model,
        max_turns=max_turns,
        effort=effort,
        label=label,
        notes=notes,
    )


def _git_short_sha(project_root: Path) -> str:
    """Best-effort: return short SHA of HEAD, or "" when not a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _git_branch(project_root: Path) -> str:
    """Best-effort: return current branch name, or "" when detached / not a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            return "" if branch == "HEAD" else branch
        return ""
    except (OSError, subprocess.SubprocessError):
        return ""
