"""Streaming, per-fixture, write-as-you-go persistence for ``ai-rules rule-loader eval``.

This module owns the ``results/<run_dir>/`` on-disk layout defined in the
"eval results-dir" plan (§4). It is the single source of truth for eval
output. Callers construct one :class:`ResultsRunWriter` per invocation and,
for each pass in the ``--runs`` loop, a :class:`RunPassWriter` under it.

Concurrency contract (Phase-1 investigation resolved)
-----------------------------------------------------
``run_concurrent`` (:mod:`ai_rules.rule_loader_eval.concurrency`) is pure
asyncio single-loop cooperative scheduling — fixtures run as coroutines on
one event loop. All writer methods that mutate shared JSON files
(``manifest.json`` and ``run_meta.json``) are plain **synchronous** methods
with **no ``await`` inside the mutation section**. That makes each mutation
atomic from asyncio's perspective: no other coroutine can interleave until
the method returns. No ``threading.Lock``, ``asyncio.Lock``, or serialized
queue is used or needed.

Companion module :mod:`ai_rules.rule_loader_eval.results_schemas` owns the
JSON shapes and per-shape serialization helpers (§5, §5.6).
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, TYPE_CHECKING

from ai_rules.rule_loader_eval.results_schemas import (
    AGGREGATE_SUMMARY_SCHEMA,
    MANIFEST_SCHEMA,
    PASS_SUMMARY_SCHEMA,
    RUN_META_SCHEMA,
    AggregateSummaryDoc,
    FixtureResultDoc,
    GitContext,
    git_context,
    serialize_run_result,
    serialize_turn_event,
)

if TYPE_CHECKING:
    from ai_rules.rule_loader_eval.agent_runner import TurnEvent
    from ai_rules.rule_loader_eval.engine import RunResult


# ---------------------------------------------------------------------------
# Constants & regexes
# ---------------------------------------------------------------------------

DEFAULT_RESULTS_ROOT_NAME = "results"
"""Default results-root directory name (relative to CWD)."""

RESULTS_ROOT_ENV_VAR = "AI_RULES_RESULTS_DIR"
"""Env var that overrides the default results root when no ``--out-dir`` is passed."""

RUN_DIR_REGEX = re.compile(
    r"^(?P<model>.+)_(?P<runs>\d+)x_(?P<date>\d{8})-(?P<time>\d{6})(?:_(?P<suffix>[0-9a-f]{6}))?$"
)
"""Parse regex for run-dir names (§4.1). ``suffix`` is only present on same-second collisions."""

_MODEL_SANITIZE_REGEX = re.compile(r"[\s/\\]+")


# ---------------------------------------------------------------------------
# Path resolution & run-dir naming
# ---------------------------------------------------------------------------


def resolve_results_root(
    out_dir: Path | None,
    *,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> Path:
    """Resolve the base ``results/`` directory per §4.2 precedence.

    Order (locked): explicit ``out_dir`` CLI value beats ``AI_RULES_RESULTS_DIR``
    env var beats the default (``<cwd>/results/``). Relative paths are
    resolved against ``cwd`` (default: :func:`Path.cwd`) so a relative
    ``--out-dir`` follows the caller's working directory, matching the
    documented CLI semantics.

    The returned path is NOT created here — the caller (``ResultsRunWriter``)
    creates ``<root>/<run_dir>/`` when the run starts.
    """
    resolved_cwd = cwd if cwd is not None else Path.cwd()
    resolved_env = env if env is not None else os.environ

    def _resolve(path_str: str | Path) -> Path:
        p = Path(path_str)
        if not p.is_absolute():
            p = resolved_cwd / p
        return p

    if out_dir is not None:
        return _resolve(out_dir)
    env_value = resolved_env.get(RESULTS_ROOT_ENV_VAR)
    if env_value:
        return _resolve(env_value)
    return _resolve(DEFAULT_RESULTS_ROOT_NAME)


def resolve_optional_results_root(
    out_dir: Path | None,
    *,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> Path | None:
    """Resolve output directory for ``refresh-all``, preserving stdout-on-omission.

    Precedence (locked): explicit ``out_dir`` > ``AI_RULES_RESULTS_DIR`` env var
    > ``None`` (stream to stdout). Relative paths resolved against ``cwd``
    (default: :func:`Path.cwd`).

    Unlike :func:`resolve_results_root`, returns ``None`` when neither CLI value
    nor env var is set, preserving ``refresh-all``'s stdout-streaming contract.
    The returned path is NOT created here.
    """
    resolved_cwd = cwd if cwd is not None else Path.cwd()
    resolved_env = env if env is not None else os.environ

    def _resolve(path_str: str | Path) -> Path:
        p = Path(path_str)
        if not p.is_absolute():
            p = resolved_cwd / p
        return p

    if out_dir is not None:
        return _resolve(out_dir)
    env_value = resolved_env.get(RESULTS_ROOT_ENV_VAR)
    if env_value:
        return _resolve(env_value)
    return None


def sanitize_model_label(model_requested: str) -> str:
    """Replace path separators / whitespace with ``-`` for filesystem safety.

    Preserves alphanumerics, ``-``, ``_``, and ``.``. Never returns an empty
    string — callers that pass an empty label get ``"unknown"``.
    """
    if not model_requested:
        return "unknown"
    cleaned = _MODEL_SANITIZE_REGEX.sub("-", model_requested.strip())
    return cleaned or "unknown"


def build_run_dir_name(
    model_requested: str,
    runs: int,
    started_at: datetime,
    *,
    run_id: str | None = None,
    existing: set[str] | None = None,
) -> str:
    """Build the run-dir name per §4.1: ``<model>_<runs>x_YYYYMMDD-HHMMSS``.

    If ``existing`` is provided and the generated name collides with a
    directory already present, append ``_<suffix>`` where ``<suffix>`` is the
    last 6 hex characters of ``run_id`` (a uuid4). Collision suffixing is
    deterministic given the same ``run_id``, so tests can assert exact names.
    """
    model_part = sanitize_model_label(model_requested)
    runs_part = f"{int(runs)}x"
    ts_part = started_at.astimezone(UTC).strftime("%Y%m%d-%H%M%S")
    base = f"{model_part}_{runs_part}_{ts_part}"
    if existing is None or base not in existing:
        return base
    suffix_source = run_id or uuid.uuid4().hex
    suffix = suffix_source.replace("-", "")[-6:]
    return f"{base}_{suffix}"


# ---------------------------------------------------------------------------
# Atomic I/O
# ---------------------------------------------------------------------------


def atomic_write_json(path: Path, obj: object) -> None:
    """Write ``obj`` as pretty-printed JSON atomically.

    Serializes to a temp file in the same directory, then ``os.replace``-s
    over ``path``. A reader never observes a partially-written or truncated
    JSON document even if the process is killed mid-write. The temp file is
    cleaned up on any exception before ``os.replace`` runs.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    fd, tmp_path = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)
        raise


def _utcnow_iso() -> str:
    """Wall-clock UTC ISO-8601 with microseconds and ``+00:00`` suffix."""
    return datetime.now(UTC).isoformat()


# ---------------------------------------------------------------------------
# Run context (parameters shared across manifest + run_meta)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RunContext:
    """Immutable parameters captured at run-start.

    Shared verbatim between ``manifest.json`` and each per-pass
    ``run_meta.json`` so a partial run remains internally consistent.
    """

    run_id: str
    started_at: str
    model_requested: str
    effort: str
    max_turns: int
    strict_forbidden: bool
    concurrency: int
    runs_requested: int
    label: str | None
    connection: str
    ai_rules_version: str
    fixture_selection: tuple[str, ...]
    fixture_count: int
    git: GitContext = field(default_factory=git_context)


def make_run_context(
    *,
    model_requested: str,
    effort: str,
    max_turns: int,
    strict_forbidden: bool,
    concurrency: int,
    runs_requested: int,
    label: str | None,
    connection: str,
    ai_rules_version: str,
    fixture_selection: tuple[str, ...],
    fixture_count: int,
    run_id: str | None = None,
    started_at: datetime | None = None,
    cwd: Path | None = None,
) -> RunContext:
    """Construct a :class:`RunContext` with sensible defaults.

    ``run_id`` defaults to a fresh ``uuid4().hex``; ``started_at`` defaults
    to ``datetime.now(UTC)``. Both are exposed as parameters so tests can
    freeze them for deterministic run-dir names.
    """
    resolved_started = (started_at or datetime.now(UTC)).astimezone(UTC)
    resolved_run_id = run_id or uuid.uuid4().hex
    return RunContext(
        run_id=resolved_run_id,
        started_at=resolved_started.isoformat(),
        model_requested=model_requested,
        effort=effort,
        max_turns=int(max_turns),
        strict_forbidden=bool(strict_forbidden),
        concurrency=int(concurrency),
        runs_requested=int(runs_requested),
        label=label,
        connection=connection,
        ai_rules_version=ai_rules_version,
        fixture_selection=fixture_selection,
        fixture_count=int(fixture_count),
        git=git_context(cwd=cwd),
    )


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------


class ResultsRunWriter:
    """One instance per ``eval`` invocation; owns ``manifest.json`` and the run dir.

    The writer creates ``<root>/<run_dir>/`` on construction, seeds a
    ``manifest.json`` in a ``running`` state, and exposes methods to open
    per-pass writers, patch manifest fields incrementally, and finalize the
    run.

    All mutation methods are synchronous with no ``await`` inside — see the
    module docstring for the concurrency contract.
    """

    def __init__(
        self,
        root: Path,
        run_dir_name: str,
        context: RunContext,
        *,
        model_resolved: str | None = None,
    ) -> None:
        """Create ``<root>/<run_dir_name>/`` and seed a ``running`` manifest."""
        self._root = Path(root)
        self._run_dir_name = run_dir_name
        self._context = context
        self.run_dir: Path = self._root / run_dir_name
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._manifest_path = self.run_dir / "manifest.json"
        self._summary_path = self.run_dir / "summary.json"
        self._model_resolved = model_resolved
        self._passes: list[dict[str, object]] = []
        self._aggregate_status = "running"
        self._completed_at: str | None = None
        self._write_manifest()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def run_id(self) -> str:  # noqa: D102
        return self._context.run_id

    @property
    def run_dir_name(self) -> str:  # noqa: D102
        return self._run_dir_name

    def start_pass(self, run_number: int) -> RunPassWriter:
        """Create ``run-0N/fixtures/`` and seed ``run_meta.json`` for pass ``run_number``."""
        pass_dir_name = f"run-{run_number:02d}"
        pass_dir = self.run_dir / pass_dir_name
        (pass_dir / "fixtures").mkdir(parents=True, exist_ok=True)
        started = _utcnow_iso()
        entry: dict[str, object] = {
            "run_number": int(run_number),
            "dir": pass_dir_name,
            "status": "running",
            "started_at": started,
            "completed_at": None,
            "totals": {"passed": 0, "failed": 0, "errors": 0},
        }
        self._passes.append(entry)
        self._write_manifest()
        return RunPassWriter(
            parent=self,
            pass_dir=pass_dir,
            run_number=int(run_number),
            started_at=started,
        )

    def set_model_resolved(self, model_resolved: str) -> None:
        """Record the SDK-reported resolved model (first non-null wins)."""
        if not model_resolved:
            return
        if self._model_resolved is None:
            self._model_resolved = model_resolved
            self._write_manifest()

    def update_pass_totals(
        self,
        run_number: int,
        *,
        passed: int,
        failed: int,
        errors: int,
        status: str | None = None,
        completed_at: str | None = None,
    ) -> None:
        """Patch the ``passes[*]`` entry for ``run_number`` with fresh totals/status."""
        for entry in self._passes:
            if entry.get("run_number") == run_number:
                entry["totals"] = {
                    "passed": int(passed),
                    "failed": int(failed),
                    "errors": int(errors),
                }
                if status is not None:
                    entry["status"] = status
                if completed_at is not None:
                    entry["completed_at"] = completed_at
                break
        self._write_manifest()

    def touch_manifest(self) -> None:
        """Rewrite ``manifest.json`` with a fresh ``updated_at`` timestamp."""
        self._write_manifest()

    def write_aggregate_summary(self, aggregate: AggregateSummaryDoc) -> None:
        """Write the run-root ``summary.json`` (§5.4)."""
        payload = dict(aggregate)
        payload.setdefault("schema_version", AGGREGATE_SUMMARY_SCHEMA)
        atomic_write_json(self._summary_path, payload)

    def finalize(self, status: str = "completed") -> None:
        """Mark the run finished and record ``completed_at`` in the manifest."""
        self._aggregate_status = status
        self._completed_at = _utcnow_iso()
        self._write_manifest()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _write_manifest(self) -> None:
        """Serialize the current manifest state atomically."""
        ctx = self._context
        doc: dict[str, object] = {
            "schema_version": MANIFEST_SCHEMA,
            "run_id": ctx.run_id,
            "run_dir_name": self._run_dir_name,
            "started_at": ctx.started_at,
            "updated_at": _utcnow_iso(),
            "completed_at": self._completed_at,
            "model_requested": ctx.model_requested,
            "model_resolved": self._model_resolved,
            "effort": ctx.effort,
            "max_turns": ctx.max_turns,
            "strict_forbidden": ctx.strict_forbidden,
            "concurrency": ctx.concurrency,
            "runs_requested": ctx.runs_requested,
            "label": ctx.label,
            "connection": ctx.connection,
            "git": dict(ctx.git),
            "ai_rules_version": ctx.ai_rules_version,
            "fixture_selection": list(ctx.fixture_selection),
            "fixture_count": ctx.fixture_count,
            "passes": [dict(p) for p in self._passes],
            "aggregate_status": self._aggregate_status,
        }
        atomic_write_json(self._manifest_path, doc)


class RunPassWriter:
    """One instance per pass (``run-0N/``); owns ``run_meta.json`` for that pass.

    Two file classes live under ``fixtures/``:

    - ``<fixture_id>.json`` — atomic write on fixture completion.
    - ``<fixture_id>.transcript.jsonl`` — append-only stream of turn events.

    The fixture files are worker-owned (each coroutine writes only its own
    fixture's files), so no coordination is needed on the hot path. The
    shared ``run_meta.json`` is mutated only through synchronous methods
    on this class.
    """

    def __init__(
        self,
        *,
        parent: ResultsRunWriter,
        pass_dir: Path,
        run_number: int,
        started_at: str,
    ) -> None:
        """Prepare per-pass paths and seed an empty ``run_meta.json``."""
        self._parent = parent
        self._pass_dir = pass_dir
        self._run_number = run_number
        self._started_at = started_at
        self._completed_at: str | None = None
        self._run_meta_path = pass_dir / "run_meta.json"
        self._summary_path = pass_dir / "summary.json"
        self._fixtures_dir = pass_dir / "fixtures"
        self._fixtures: dict[str, dict[str, object | None]] = {}
        self._transcript_counters: dict[str, int] = {}
        self._write_run_meta()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def run_number(self) -> int:  # noqa: D102
        return self._run_number

    @property
    def pass_dir(self) -> Path:  # noqa: D102
        return self._pass_dir

    def mark_fixture_started(self, fixture_id: str) -> None:
        """Flip fixture ``fixture_id`` to ``in_progress`` in ``run_meta.json``."""
        self._fixtures[fixture_id] = {
            "status": "in_progress",
            "result": None,
            "started_at": _utcnow_iso(),
            "completed_at": None,
        }
        self._write_run_meta()

    def write_fixture_result(self, run_result: RunResult) -> Path:
        """Serialize one fixture's result and flip ``run_meta.json`` to ``completed``.

        The per-fixture ``<id>.json`` is written atomically BEFORE
        ``run_meta.json`` is updated, so a reader that sees
        ``status == "completed"`` is guaranteed to find a valid
        ``<id>.json`` on disk (§7.5 ordering guarantee).
        """
        doc: FixtureResultDoc = serialize_run_result(run_result, self._run_number)
        # `schema_version` is set by `serialize_run_result`.
        result_str = doc.get("result", "fail")
        model = doc.get("model", "")
        if model:
            self._parent.set_model_resolved(str(model))
        target = self._fixtures_dir / f"{_safe_id(run_result.fixture_id)}.json"
        atomic_write_json(target, doc)

        entry = self._fixtures.setdefault(
            run_result.fixture_id,
            {
                "status": "in_progress",
                "result": None,
                "started_at": _utcnow_iso(),
                "completed_at": None,
            },
        )
        entry["status"] = "completed"
        entry["result"] = result_str
        entry["completed_at"] = _utcnow_iso()
        self._write_run_meta()
        return target

    def open_transcript(self, fixture_id: str) -> TranscriptWriter:
        """Return a helper that appends one JSONL line per ``TurnEvent``."""
        path = self._fixtures_dir / f"{_safe_id(fixture_id)}.transcript.jsonl"
        return TranscriptWriter(path=path, fixture_id=fixture_id, pass_writer=self)

    def write_transcript_from_events(
        self,
        fixture_id: str,
        events: tuple[TurnEvent, ...] | list[TurnEvent],
    ) -> Path:
        """Serialize ``AgentRun.events`` at fixture completion (default path).

        Opens the transcript file fresh, writes one line per event in order,
        and returns the target path. This is the completion-time serializer
        chosen in §15 OQ2 (no per-turn ``on_event`` callback).
        """
        with self.open_transcript(fixture_id) as writer:
            for event in events:
                writer.write_event(event)
        return writer.path  # type: ignore[return-value]

    def write_pass_summary(
        self,
        *,
        total: int,
        passed: int,
        failed: int,
        errors: int,
        totals: dict[str, int | float],
        failures: list[str],
    ) -> None:
        """Write the per-pass ``summary.json`` (§5.3)."""
        pass_rate = round(passed / total, 3) if total else 0.0
        doc: dict[str, object] = {
            "schema_version": PASS_SUMMARY_SCHEMA,
            "run_number": self._run_number,
            "total": int(total),
            "passed": int(passed),
            "failed": int(failed),
            "errors": int(errors),
            "pass_rate": pass_rate,
            "totals": {
                "turns": int(totals.get("turns", 0)),
                "input_tokens": int(totals.get("input_tokens", 0)),
                "output_tokens": int(totals.get("output_tokens", 0)),
                "total_cost_usd": float(totals.get("total_cost_usd", 0.0)),
                "duration_ms": int(totals.get("duration_ms", 0)),
            },
            "failures": list(failures),
        }
        atomic_write_json(self._summary_path, doc)

    def finalize_pass(self, *, status: str = "completed") -> None:
        """Mark the pass complete in ``run_meta.json`` and patch the manifest."""
        self._completed_at = _utcnow_iso()
        self._write_run_meta()
        totals = self._compute_totals()
        self._parent.update_pass_totals(
            self._run_number,
            passed=totals["passed"],
            failed=totals["failed"],
            errors=totals["errors"],
            status=status,
            completed_at=self._completed_at,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _next_seq(self, fixture_id: str) -> int:
        """Monotonic per-fixture counter for transcript ``seq``."""
        current = self._transcript_counters.get(fixture_id, 0)
        self._transcript_counters[fixture_id] = current + 1
        return current

    def _compute_totals(self) -> dict[str, int]:
        passed = 0
        failed = 0
        errors = 0
        for entry in self._fixtures.values():
            result = entry.get("result")
            if result == "pass":
                passed += 1
            elif result == "error":
                errors += 1
            elif result == "fail":
                failed += 1
        return {"passed": passed, "failed": failed, "errors": errors}

    def _write_run_meta(self) -> None:
        ctx = self._parent._context
        doc: dict[str, object] = {
            "schema_version": RUN_META_SCHEMA,
            "run_id": ctx.run_id,
            "run_number": self._run_number,
            "started_at": self._started_at,
            "completed_at": self._completed_at,
            "model_requested": ctx.model_requested,
            "model_resolved": self._parent._model_resolved,
            "effort": ctx.effort,
            "max_turns": ctx.max_turns,
            "strict_forbidden": ctx.strict_forbidden,
            "concurrency": ctx.concurrency,
            "git": dict(ctx.git),
            "fixture_count": ctx.fixture_count,
            "fixtures": {k: dict(v) for k, v in self._fixtures.items()},
        }
        atomic_write_json(self._run_meta_path, doc)


class TranscriptWriter:
    """Context-manager helper for appending JSONL lines to a transcript file.

    Owned by a single coroutine (the one running the fixture), so no locking
    is required. ``flush()`` after each line ensures OS buffer visibility;
    ``fsync`` is NOT called — power-loss durability is out of scope for a
    local eval artifact (§7.4).
    """

    def __init__(
        self,
        *,
        path: Path,
        fixture_id: str,
        pass_writer: RunPassWriter,
    ) -> None:
        """Bind a transcript file path to a fixture on a specific pass."""
        self.path = path
        self._fixture_id = fixture_id
        self._pass_writer = pass_writer
        self._handle: IO[str] | None = None

    def __enter__(self) -> TranscriptWriter:
        """Open the transcript file in append mode."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("a", encoding="utf-8")
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        """Close the transcript file handle."""
        if self._handle is not None:
            self._handle.close()
            self._handle = None

    def write_event(self, event: TurnEvent, *, ts: str | None = None) -> int:
        """Append one ``TurnEvent`` as a JSON line; return its assigned ``seq``.

        ``ts`` defaults to ``datetime.now(UTC).isoformat()``. Returning
        ``seq`` lets callers cross-check monotonicity in tests without
        peeking at private state.
        """
        if self._handle is None:
            # Allow single-shot use without a context manager.
            self.__enter__()
        assert self._handle is not None
        seq = self._pass_writer._next_seq(self._fixture_id)
        line = serialize_turn_event(event, seq, ts or _utcnow_iso())
        self._handle.write(line + "\n")
        self._handle.flush()
        return seq


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_id(fixture_id: str) -> str:
    """Sanitize a fixture id for use as a filename (mirrors ``snapshot.py``)."""
    return fixture_id.replace("/", "_").replace(" ", "_")
