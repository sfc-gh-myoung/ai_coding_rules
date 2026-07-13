"""Schema helpers for the streaming ``results/`` eval layout.

Companion to :mod:`ai_rules.rule_loader_eval.results_writer`. This module
owns:

- TypedDicts describing the five JSON shapes written under
  ``results/<run_dir>/`` (manifest, per-pass run_meta, per-pass summary,
  run-root aggregate summary, per-fixture result). Types are documentation-
  only; the writer emits plain dicts.
- ``serialize_run_result`` — an explicit field mapping from
  :class:`ai_rules.rule_loader_eval.engine.RunResult` (plus its
  :class:`~ai_rules.rule_loader_eval.agent_runner.AgentRun`) to the
  per-fixture ``<id>.json`` shape (§5.5 of the plan).
- ``serialize_turn_event`` — a trivial line serializer for the three
  JSON-native fields on :class:`~ai_rules.rule_loader_eval.agent_runner.TurnEvent`
  plus writer-assigned ``seq`` and ``ts`` (§5.6).
- ``git_context`` — captures ``{sha, branch, dirty}`` for run metadata.

Every field on ``TurnEvent`` is a JSON-native primitive (``int``/``str``),
so no defensive encoder is required. See the Phase-1 investigation note in
the plan for the resolved concurrency + serialization contracts.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from ai_rules.rule_loader_eval.agent_runner import TurnEvent
    from ai_rules.rule_loader_eval.engine import RunResult


# ---------------------------------------------------------------------------
# Schema version constants (mirror the ``schema_version`` field on each file)
# ---------------------------------------------------------------------------

MANIFEST_SCHEMA = "ai-rules-eval-manifest/v1"
RUN_META_SCHEMA = "ai-rules-eval-run-meta/v1"
PASS_SUMMARY_SCHEMA = "ai-rules-eval-summary/v1"
AGGREGATE_SUMMARY_SCHEMA = "ai-rules-eval-aggregate/v1"
FIXTURE_RESULT_SCHEMA = "ai-rules-eval-fixture/v1"


# ---------------------------------------------------------------------------
# TypedDicts (documentation-only; writer emits plain dicts)
# ---------------------------------------------------------------------------


class GitContext(TypedDict):
    """Git commit / branch / dirty flag captured at run-start."""

    sha: str
    branch: str
    dirty: bool


class PassEntryTotals(TypedDict):
    """Per-pass counts recorded on the manifest's ``passes[*]`` list."""

    passed: int
    failed: int
    errors: int


class PassEntry(TypedDict, total=False):
    """One row on ``manifest.json.passes``."""

    run_number: int
    dir: str
    status: str  # pending | running | completed | failed
    started_at: str | None
    completed_at: str | None
    totals: PassEntryTotals


class ManifestDoc(TypedDict, total=False):
    """Shape of ``results/<run_dir>/manifest.json`` (§5.1)."""

    schema_version: str
    run_id: str
    run_dir_name: str
    started_at: str
    updated_at: str
    completed_at: str | None
    model_requested: str
    model_resolved: str | None
    effort: str
    max_turns: int
    strict_forbidden: bool
    concurrency: int
    runs_requested: int
    label: str | None
    connection: str
    git: GitContext
    ai_rules_version: str
    fixture_selection: list[str]
    fixture_count: int
    passes: list[PassEntry]
    aggregate_status: str


class FixtureStatusEntry(TypedDict, total=False):
    """One entry in ``run_meta.json.fixtures``."""

    status: str  # pending | in_progress | completed
    result: str | None  # pass | fail | error | null
    started_at: str | None
    completed_at: str | None


class RunMetaDoc(TypedDict, total=False):
    """Shape of ``results/<run_dir>/run-0N/run_meta.json`` (§5.2)."""

    schema_version: str
    run_id: str
    run_number: int
    started_at: str
    completed_at: str | None
    model_requested: str
    model_resolved: str | None
    effort: str
    max_turns: int
    strict_forbidden: bool
    concurrency: int
    git: GitContext
    fixture_count: int
    fixtures: dict[str, FixtureStatusEntry]


class PassTotals(TypedDict):
    """``summary.json.totals`` on a per-pass summary."""

    turns: int
    input_tokens: int
    output_tokens: int
    total_cost_usd: float
    duration_ms: int


class PassSummaryDoc(TypedDict, total=False):
    """Shape of ``results/<run_dir>/run-0N/summary.json`` (§5.3)."""

    schema_version: str
    run_number: int
    total: int
    passed: int
    failed: int
    errors: int
    pass_rate: float
    totals: PassTotals
    failures: list[str]


class PerFixtureAggregate(TypedDict):
    """One entry in run-root ``summary.json.per_fixture``."""

    n_runs: int
    passes: int
    fails: int
    flake_score: float
    pass_rate: float


class AggregateTotals(TypedDict):
    """``summary.json.aggregate`` on the run-root summary."""

    mean_pass_rate: float
    flaky_fixtures: list[str]
    total_cost_usd: float
    total_input_tokens: int
    total_output_tokens: int
    total_duration_ms: int
    total_signal_disagreements: int
    total_citation_drifts: int


class AggregateSummaryDoc(TypedDict, total=False):
    """Shape of ``results/<run_dir>/summary.json`` (§5.4)."""

    schema_version: str
    runs: int
    fixture_count: int
    per_fixture: dict[str, PerFixtureAggregate]
    aggregate: AggregateTotals


class MatchDoc(TypedDict):
    """``<id>.json.match`` subdict."""

    missing_required: list[str]
    missing_dependencies: list[str]
    forbidden_present: list[str]
    extra_loaded: list[str]


class FixtureResultDoc(TypedDict, total=False):
    """Shape of ``results/<run_dir>/run-0N/fixtures/<fixture_id>.json`` (§5.5)."""

    schema_version: str
    fixture_id: str
    run_number: int
    model: str
    passed: bool
    result: str  # pass | fail | error
    match: MatchDoc
    signal_report: dict[str, object]
    citation_drifts: list[dict[str, object]]
    depends_violations: list[str]
    output_violations: list[str]
    turns: int
    input_tokens: int
    output_tokens: int
    total_cost_usd: float
    duration_ms: int
    final_text: str | None
    stop_reason: str
    is_infra_error: bool
    infra_error_detail: str | None
    skill_invocations: list[str]
    loaded: list[str]
    loaded_via_reads: list[str]


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------


def _classify_result(run_result: RunResult) -> str:
    """Map a :class:`RunResult` to the authoritative ``result`` string enum.

    - ``error`` iff the underlying run is an infra error (SDK/model/connection
      failure); the fixture was not validly assessed.
    - ``pass`` iff :attr:`RunResult.passed` (composite of match + signal +
      citation + output + depends checks).
    - ``fail`` otherwise.
    """
    if getattr(run_result.run, "is_infra_error", False):
        return "error"
    return "pass" if run_result.passed else "fail"


def _serialize_signal_report(report: object) -> dict[str, object]:
    """Best-effort conversion of a :class:`SignalReport` frozen dataclass to a dict."""
    to_dict = getattr(report, "to_dict", None)
    if callable(to_dict):
        result = to_dict()
        if isinstance(result, dict):
            return result
    from dataclasses import asdict, is_dataclass

    if is_dataclass(report) and not isinstance(report, type):
        return asdict(report)
    return {"repr": repr(report)}


def _serialize_citation_drifts(drifts: object) -> list[dict[str, object]]:
    """Convert a tuple of ``CitationDrift`` dataclasses to a list of dicts."""
    from collections.abc import Iterable
    from dataclasses import asdict, is_dataclass

    out: list[dict[str, object]] = []
    if not drifts or not isinstance(drifts, Iterable):
        return out
    for d in drifts:
        if is_dataclass(d) and not isinstance(d, type):
            out.append(asdict(d))
        elif isinstance(d, dict):
            out.append({str(k): v for k, v in d.items()})
        else:
            out.append({"repr": repr(d)})
    return out


def serialize_run_result(run_result: RunResult, run_number: int) -> FixtureResultDoc:
    """Convert one :class:`RunResult` (+ its :class:`AgentRun`) to a fixture doc.

    Produces the per-fixture ``<id>.json`` shape defined in §5.5 of the plan.

    ``run_number`` is the 1-based pass index this fixture belongs to.
    Fields on :class:`AgentRun` are read via ``getattr`` with defensive
    defaults so a subset ``RunResult`` (used in unit tests) still
    serializes cleanly.
    """
    run = run_result.run
    match = run_result.match
    result = _classify_result(run_result)

    infra = bool(getattr(run, "is_infra_error", False))
    final_text_raw = getattr(run, "final_text", "")
    final_text: str | None = None if infra else (final_text_raw or "")
    infra_detail_raw = getattr(run, "infra_error_detail", "") or ""
    infra_detail: str | None = infra_detail_raw if infra else None

    doc: FixtureResultDoc = {
        "schema_version": FIXTURE_RESULT_SCHEMA,
        "fixture_id": run_result.fixture_id,
        "run_number": run_number,
        "model": getattr(run, "model", "") or "",
        "passed": bool(run_result.passed),
        "result": result,
        "match": {
            "missing_required": list(match.missing_required),
            "missing_dependencies": list(match.missing_dependencies),
            "forbidden_present": list(match.forbidden_present),
            "extra_loaded": list(getattr(match, "extras", ()) or ()),
        },
        "signal_report": _serialize_signal_report(run_result.signal_report),
        "citation_drifts": _serialize_citation_drifts(run_result.citation_drifts),
        "depends_violations": [str(v) for v in (run_result.depends_violations or ())],
        "output_violations": list(getattr(run, "output_violations", ()) or ()),
        "turns": int(getattr(run, "turns", 0) or 0),
        "input_tokens": int(getattr(run, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(run, "output_tokens", 0) or 0),
        "total_cost_usd": float(getattr(run, "total_cost_usd", 0.0) or 0.0),
        "duration_ms": int(getattr(run, "duration_ms", 0) or 0),
        "final_text": final_text,
        "stop_reason": getattr(run, "stop_reason", "") or "",
        "is_infra_error": infra,
        "infra_error_detail": infra_detail,
        "skill_invocations": list(getattr(run, "skill_invocations", ()) or ()),
        "loaded": list(getattr(run, "loaded", ()) or ()),
        "loaded_via_reads": list(getattr(run, "loaded_via_reads", ()) or ()),
    }
    return doc


def serialize_turn_event(event: TurnEvent, seq: int, ts: str) -> str:
    r"""Return one JSON line for a single :class:`TurnEvent`.

    ``TurnEvent`` has exactly three JSON-native fields (``t_ms:int``,
    ``kind:str``, ``detail:str``). The writer supplies the monotonic
    per-fixture counter ``seq`` and the wall-clock ISO-8601 UTC ``ts``.
    No trailing newline is added — the caller writes ``line + "\n"``.
    """
    return json.dumps(
        {
            "seq": int(seq),
            "ts": str(ts),
            "t_ms": int(event.t_ms),
            "kind": str(event.kind),
            "detail": str(event.detail),
        }
    )


# ---------------------------------------------------------------------------
# Git context
# ---------------------------------------------------------------------------


def git_context(cwd: Path | None = None) -> GitContext:
    """Capture ``{sha, branch, dirty}`` for the current git checkout.

    Returns empty-string ``sha`` / ``branch`` and ``dirty=False`` when git is
    unavailable or the working directory is not a git repo. Never raises.
    """
    base = cwd if cwd is not None else Path.cwd()

    def _run(args: list[str]) -> str:
        try:
            proc = subprocess.run(
                args,
                cwd=str(base),
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired):
            return ""
        if proc.returncode != 0:
            return ""
        return proc.stdout.strip()

    sha = _run(["git", "rev-parse", "HEAD"])
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    porcelain = _run(["git", "status", "--porcelain"])
    dirty = bool(porcelain)
    return {"sha": sha, "branch": branch, "dirty": dirty}
