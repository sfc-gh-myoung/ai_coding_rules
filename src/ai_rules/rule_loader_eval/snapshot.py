"""Snapshot schema for rule-loader A/B comparisons.

A snapshot directory captures one ``ai-rules rule-loader eval`` run plus
its companion ``refresh-all`` run, plus a ``meta.json`` describing the
environment that produced them. Two snapshots can be diffed by the
``compare`` command to answer "did rule loading get better or worse"
between two states of the rules / process.

Layout::

    out/<label>/
      meta.json
      eval/
        summary.json
        <fixture_id>.json    # one per fixture
      refresh-all/             (optional; written by refresh-all --out-dir)
        summary.json
        <safe_id>.yaml
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
    )


def write_eval_snapshot(
    out_dir: Path,
    fixtures: list[FixtureSnapshot],
    meta: SnapshotMeta,
) -> None:
    """Write a snapshot to disk.

    Layout:
      <out_dir>/meta.json
      <out_dir>/eval/summary.json
      <out_dir>/eval/<fixture_id>.json
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    eval_dir = out_dir / "eval"
    eval_dir.mkdir(parents=True, exist_ok=True)

    summary = compute_summary(fixtures)

    (out_dir / "meta.json").write_text(
        json.dumps(meta.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (eval_dir / "summary.json").write_text(
        json.dumps(summary.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for fx in fixtures:
        # Use safe_id-style filename: replace path separators just in case.
        safe = fx.fixture_id.replace("/", "_").replace(" ", "_")
        (eval_dir / f"{safe}.json").write_text(
            json.dumps(fx.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def read_eval_snapshot(snapshot_dir: Path) -> Snapshot:
    """Load a snapshot from disk.

    Raises ``ValueError`` for missing meta.json or unsupported schema_version.
    Returns ``Snapshot`` with empty fixtures tuple if the eval/ subdir is missing
    (refresh-all-only snapshots are valid input but produce no per-fixture rows).
    """
    meta_path = snapshot_dir / "meta.json"
    if not meta_path.is_file():
        raise ValueError(f"no meta.json under {snapshot_dir}")
    meta = SnapshotMeta.from_dict(json.loads(meta_path.read_text(encoding="utf-8")))
    if meta.schema_version != SNAPSHOT_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported snapshot schema_version {meta.schema_version!r}; "
            f"expected {SNAPSHOT_SCHEMA_VERSION}"
        )

    eval_dir = snapshot_dir / "eval"
    fixtures: list[FixtureSnapshot] = []
    summary: SnapshotSummary | None = None
    if eval_dir.is_dir():
        for path in sorted(eval_dir.glob("*.json")):
            if path.name == "summary.json":
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            fixtures.append(FixtureSnapshot.from_dict(data))
        summary_path = eval_dir / "summary.json"
        if summary_path.is_file():
            sdata = json.loads(summary_path.read_text(encoding="utf-8"))
            summary = SnapshotSummary(
                total=int(sdata.get("total") or 0),
                passed=int(sdata.get("passed") or 0),
                failed=int(sdata.get("failed") or 0),
                mean_turns=float(sdata.get("mean_turns") or 0.0),
                mean_duration_ms=float(sdata.get("mean_duration_ms") or 0.0),
                total_signal_disagreements=int(sdata.get("total_signal_disagreements") or 0),
                total_citation_drifts=int(sdata.get("total_citation_drifts") or 0),
            )

    return Snapshot(meta=meta, fixtures=tuple(fixtures), summary=summary)


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
