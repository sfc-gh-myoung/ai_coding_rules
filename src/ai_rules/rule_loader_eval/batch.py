"""Batch orchestration for ``seed-fixtures`` command.

Drives multiple fixture YAML files concurrently through the live Cortex Code
Agent SDK. Concurrency mechanics (``asyncio.Semaphore`` cap, ``[1..N]`` slot
pool, ``gather``, ``CancelledError`` re-raise) are delegated to the shared
``concurrency.run_concurrent_async`` driver; this module supplies the
refresh-specific per-item ``work`` and ``exception_to_result`` (capture-and-
continue) and adapts the generic ``ConcurrentSummary`` back to ``BatchSummary``.

Public API:
- ``BatchItem`` / ``BatchOutcome`` / ``BatchSummary`` — result shapes.
- ``run_batch_async`` — async entry point; delegates to ``run_concurrent_async``.
- ``run_batch`` — sync wrapper via ``asyncio.run``.
- ``expand_glob`` — resolve ``--glob`` / ``--all`` patterns to sorted Path lists.
- ``extract_prompt_from_fixture`` — read ``prompt:`` field from YAML tolerantly.
- ``extract_batch_item`` — parse a fixture YAML into a ``BatchItem``.
- ``safe_fixture_id`` — sanitize an id to ``[A-Za-z0-9_.-]``-only string.
- ``validate_unique_output_names`` — fail fast on duplicate safe-ids.
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ai_rules.rule_loader_eval.defaults import DEFAULT_EFFORT, DEFAULT_MAX_TURNS

if TYPE_CHECKING:
    from ai_rules.rule_loader_eval.agent_runner import AgentRun

_SAFE_ID_RE = re.compile(r"[^A-Za-z0-9_.\-]")


def safe_fixture_id(value: str, fallback: str) -> str:
    """Sanitize *value* to contain only ``[A-Za-z0-9_.-]`` characters.

    Characters outside the allowed set are replaced with ``-``. When *value*
    is empty after sanitization, *fallback* (the YAML basename without
    extension) is returned as-is (it is already filesystem-safe).
    """
    sanitized = _SAFE_ID_RE.sub("-", value).strip("-")
    return sanitized if sanitized else fallback


@dataclass(frozen=True)
class BatchItem:
    """One resolved fixture ready for a live SDK call."""

    id: str
    safe_id: str
    path: Path
    prompt: str


@dataclass(frozen=True)
class BatchOutcome:
    """Result of one SDK call, successful or failed."""

    item: BatchItem
    run: AgentRun | None
    error_type: str | None
    error_message: str | None

    @property
    def succeeded(self) -> bool:
        """Return True when the run completed without error."""
        return self.error_type is None and self.run is not None


@dataclass(frozen=True)
class BatchSummary:
    """Aggregated outcome of a full batch run."""

    concurrency: int
    outcomes: tuple[BatchOutcome, ...]
    wall_seconds: float

    @property
    def total(self) -> int:
        """Total number of outcomes."""
        return len(self.outcomes)

    @property
    def succeeded(self) -> int:
        """Number of succeeded outcomes."""
        return sum(1 for o in self.outcomes if o.succeeded)

    @property
    def failed(self) -> int:
        """Number of failed outcomes."""
        return self.total - self.succeeded


def expand_glob(pattern: str, project_root: Path) -> list[Path]:
    """Expand *pattern* relative to *project_root* and return sorted ``.yaml`` paths.

    Resolves to absolute paths, de-duplicates, filters non-``.yaml`` files,
    and returns a sorted list. An empty result is a caller-level error
    (``EXIT_FIXTURE_INVALID``).
    """
    paths = [p.resolve() for p in project_root.glob(pattern) if p.suffix == ".yaml"]
    return sorted(set(paths))


def extract_prompt_from_fixture(path: Path) -> str:
    """Read the top-level ``prompt:`` field from a fixture YAML file.

    Tolerant parser: only the ``prompt`` key is required; every other
    top-level key is ignored. Supports partially-authored fixtures whose
    ``expected`` / ``trigger_evidence`` / siblings are still TODO.

    Raises ``ValueError`` on: missing file, malformed YAML,
    missing/empty/non-string ``prompt`` value.
    """
    import yaml

    if not path.exists():
        raise ValueError(f"fixture file not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"failed to parse fixture YAML at {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"fixture YAML at {path} must be a mapping with a top-level `prompt:` key")
    value = raw.get("prompt")
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"fixture YAML at {path} is missing a non-empty `prompt:` string")
    return value


def _extract_fixture_id(path: Path) -> str:
    """Return the YAML ``id:`` field or the basename without extension."""
    import yaml

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and isinstance(raw.get("id"), str) and raw["id"].strip():
            return raw["id"].strip()
    except Exception:
        pass
    return path.stem


def extract_batch_item(path: Path) -> BatchItem:
    """Parse a fixture YAML into a ``BatchItem``.

    Uses the YAML ``id:`` field when present; falls back to the basename
    without extension. The ``safe_id`` is the sanitized form for output
    filenames.

    Raises ``ValueError`` if the file is missing or the ``prompt:`` field
    is absent/empty (delegated to ``extract_prompt_from_fixture``).
    """
    fixture_id = _extract_fixture_id(path)
    fallback = path.stem
    sid = safe_fixture_id(fixture_id, fallback)
    prompt = extract_prompt_from_fixture(path)
    return BatchItem(id=fixture_id, safe_id=sid, path=path, prompt=prompt)


def validate_unique_output_names(items: list[BatchItem]) -> None:
    """Fail fast when two fixtures would write to the same output filename.

    Raises ``ValueError`` listing the colliding paths so the caller can
    surface it as ``EXIT_FIXTURE_INVALID`` before any SDK calls are made.
    """
    seen: dict[str, Path] = {}
    collisions: list[str] = []
    for item in items:
        if item.safe_id in seen:
            collisions.append(f"  {item.safe_id!r}: {seen[item.safe_id]} and {item.path}")
        else:
            seen[item.safe_id] = item.path
    if collisions:
        raise ValueError(
            "Duplicate output filenames would overwrite each other. "
            "Rename one of the conflicting fixtures or adjust their `id:` fields:\n"
            + "\n".join(collisions)
        )


async def run_batch_async(
    items: list[BatchItem],
    *,
    concurrency: int,
    project_root: Path | None = None,
    max_turns: int = DEFAULT_MAX_TURNS,
    effort: str = DEFAULT_EFFORT,
    model: str = "auto",
    connection: str | None = None,
    on_start: Callable[[BatchItem, int], None] | None = None,
    on_outcome: Callable[[BatchOutcome, int], None] | None = None,
) -> BatchSummary:
    """Run all *items* concurrently, capped at *concurrency* in-flight sessions.

    Each task acquires the semaphore before calling ``run_live_async`` and
    releases it on completion or exception. Exceptions are captured into
    ``BatchOutcome`` rather than re-raised so ``asyncio.gather`` does not
    short-circuit. ``asyncio.CancelledError`` (e.g. on Ctrl-C) is
    re-raised so the gather propagates cancellation cleanly.

    ``on_start`` (optional) fires immediately after the worker slot is
    acquired, before the SDK call begins. The second argument is a
    1-based ``worker_slot`` that disambiguates concurrent tasks for live
    progress UIs.

    ``on_outcome`` is called immediately when each individual outcome is
    ready, before all tasks finish. The second argument is the same
    ``worker_slot`` value passed to ``on_start``. Use this to write
    per-fixture files as they complete rather than buffering all results
    in memory. The final ``BatchSummary`` still carries all outcomes
    (for ``summary.json``); output order in the summary matches sorted
    source-path input order.

    Concurrency mechanics (semaphore, slot pool, gather, ``CancelledError``
    re-raise) are delegated to the shared ``concurrency.run_concurrent_async``
    driver. Refresh-all uses the capture-and-continue policy: per-item
    exceptions are converted to failed ``BatchOutcome`` values via
    ``exception_to_result`` and no abort predicate is wired, so the batch
    never short-circuits.
    """
    from ai_rules.rule_loader_eval.agent_runner import run_live_async
    from ai_rules.rule_loader_eval.concurrency import run_concurrent_async

    async def _one_batch(item: BatchItem, slot: int) -> BatchOutcome:
        run = await run_live_async(
            item.id,
            item.prompt,
            project_root=project_root,
            max_turns=max_turns,
            effort=effort,
            model=model,
            connection=connection,
        )
        return BatchOutcome(item=item, run=run, error_type=None, error_message=None)

    def _exc_to_outcome(item: BatchItem, exc: Exception) -> BatchOutcome:
        return BatchOutcome(
            item=item,
            run=None,
            error_type=type(exc).__name__,
            error_message=str(exc),
        )

    summary = await run_concurrent_async(
        items,
        concurrency=concurrency,
        work=_one_batch,
        exception_to_result=_exc_to_outcome,
        on_start=on_start,
        on_outcome=on_outcome,
    )
    # Refresh-all never aborts and never skips items (capture-and-continue).
    assert summary.aborted is None
    assert summary.not_run == ()
    return BatchSummary(
        concurrency=concurrency,
        outcomes=summary.results,
        wall_seconds=summary.wall_seconds,
    )


def run_batch(
    items: list[BatchItem],
    *,
    concurrency: int,
    project_root: Path | None = None,
    max_turns: int = DEFAULT_MAX_TURNS,
    effort: str = DEFAULT_EFFORT,
    model: str = "auto",
    connection: str | None = None,
    on_start: Callable[[BatchItem, int], None] | None = None,
    on_outcome: Callable[[BatchOutcome, int], None] | None = None,
) -> BatchSummary:
    """Synchronous wrapper around ``run_batch_async``.

    ``on_start`` fires when each fixture begins active execution, with a
    1-based ``worker_slot`` integer that disambiguates concurrent tasks.
    ``on_outcome`` fires when each fixture's outcome is ready (with the
    same slot value), enabling streaming writes (see ``run_batch_async``
    for details).

    Enters one ``asyncio.run`` event loop; ``run_live_async`` coroutines
    share it through the semaphore. Do not call this inside an existing
    event loop (use ``run_batch_async`` directly instead).
    """
    return asyncio.run(
        run_batch_async(
            items,
            concurrency=concurrency,
            project_root=project_root,
            max_turns=max_turns,
            effort=effort,
            model=model,
            connection=connection,
            on_start=on_start,
            on_outcome=on_outcome,
        )
    )
