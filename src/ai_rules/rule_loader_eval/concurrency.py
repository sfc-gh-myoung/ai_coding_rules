"""Generic concurrent task driver shared by ``refresh-all`` and ``eval``.

Runs a list of items concurrently, capped at ``concurrency`` in-flight tasks via
``asyncio.Semaphore``, assigning each active task a stable ``[1..N]`` worker slot
from an ``asyncio.Queue`` pool. The mechanics (semaphore, slot pool, explicit task
creation, ``asyncio.gather``, ``CancelledError`` re-raise) were lifted from
``batch.py::run_batch_async`` and generalised over an injected ``work(item, slot)``
coroutine so both the fixture-refresh path (capture-and-continue) and the eval
path (fail-fast on infra error) share one implementation.

Two abort policies are supported, both optional:

- ``should_abort_result(result)`` — a *completed* result triggers an abort.
- ``should_abort_exception(item, exc)`` — an exception raised by ``work`` triggers
  an abort (e.g. ``InfraError`` raised before any result exists).

On abort, in-flight sibling tasks are cancelled and not-yet-started items are
skipped; both are reported as :class:`ConcurrentNotRun` diagnostics (never as
results). The aborting item is captured in :attr:`ConcurrentSummary.aborted`.

Non-aborting exceptions are converted to a per-item result via the mandatory
``exception_to_result(item, exc)`` callback (capture-and-continue) so a single
item's failure never short-circuits the gather.

External cancellation (Ctrl-C) is distinguished from deliberate abort by the
``_abort`` event: a ``CancelledError`` seen while ``_abort`` is unset is re-raised
so cancellation propagates cleanly; when ``_abort`` is set it is a deliberate
teardown and is recorded as a ``not_run`` diagnostic instead.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import cast


@dataclass(frozen=True)
class ConcurrentNotRun[T]:
    """An item that did not produce a result because the run aborted.

    Attributes:
        item: The original input item.
        reason: ``"queued"`` (never started) or ``"cancelled"`` (in-flight when
            the abort fired).
    """

    item: T
    reason: str


@dataclass(frozen=True)
class ConcurrentAbort[T, R]:
    """Metadata about the item that triggered a run abort.

    Exactly one of ``exception`` / ``result`` is populated: ``exception`` for an
    ``should_abort_exception`` trigger (no result existed), ``result`` for a
    ``should_abort_result`` trigger.

    Attributes:
        item: The input item whose outcome triggered the abort.
        exception: The exception that triggered the abort, if any.
        result: The completed result that triggered the abort, if any.
    """

    item: T
    exception: BaseException | None
    result: R | None


@dataclass(frozen=True)
class ConcurrentSummary[T, R]:
    """Aggregated outcome of a :func:`run_concurrent_async` invocation.

    Attributes:
        results: Completed, non-aborting results in INPUT order (includes results
            produced by ``exception_to_result``).
        not_run: Diagnostic entries for queued/cancelled items when the run
            aborted. Empty when the run completed normally.
        aborted: Abort metadata, or ``None`` when the run completed normally.
        concurrency: The in-flight cap used for the run.
        wall_seconds: Wall-clock duration of the run, rounded to 3 decimals.
    """

    results: tuple[R, ...]
    not_run: tuple[ConcurrentNotRun[T], ...]
    aborted: ConcurrentAbort[T, R] | None
    concurrency: int
    wall_seconds: float


# Internal per-task return markers. Kept private: callers only see ConcurrentSummary.
@dataclass(frozen=True)
class _Holder[R]:
    """A completed, non-aborting result."""

    result: R


@dataclass(frozen=True)
class _NotRun[T]:
    """A queued/cancelled item captured during abort teardown."""

    item: T
    reason: str


class _AbortSentinel:
    """Sentinel returned by the task that triggered the abort."""


_ABORT = _AbortSentinel()


async def run_concurrent_async[T, R](
    items: list[T],
    *,
    concurrency: int,
    work: Callable[[T, int], Awaitable[R]],
    exception_to_result: Callable[[T, Exception], R],
    should_abort_result: Callable[[R], bool] | None = None,
    should_abort_exception: Callable[[T, Exception], bool] | None = None,
    on_start: Callable[[T, int], None] | None = None,
    on_outcome: Callable[[R, int], None] | None = None,
) -> ConcurrentSummary[T, R]:
    """Run all *items* concurrently, capped at *concurrency* in-flight tasks.

    Args:
        items: The input items, processed in order for slot/result ordering.
        concurrency: Maximum number of in-flight ``work`` coroutines (>= 1).
        work: Coroutine factory ``work(item, slot)`` producing a result.
        exception_to_result: Converts a NON-aborting exception into a per-item
            result (capture-and-continue). Mandatory.
        should_abort_result: Optional predicate; when it returns True for a
            completed result, the run aborts.
        should_abort_exception: Optional predicate; when it returns True for a
            ``work`` exception, the run aborts.
        on_start: Optional callback fired after a slot is acquired, before
            ``work`` begins. Receives ``(item, slot)``.
        on_outcome: Optional callback fired for each completed, non-aborting
            result. Receives ``(result, slot)``. NOT fired for aborting,
            cancelled, or queued items.

    Returns:
        A :class:`ConcurrentSummary` with results in input order plus any abort /
        not-run diagnostics.

    Raises:
        asyncio.CancelledError: On external cancellation (e.g. Ctrl-C) that is not
            a deliberate abort.
    """
    sem = asyncio.Semaphore(concurrency)
    slot_pool: asyncio.Queue[int] = asyncio.Queue(maxsize=concurrency)
    for _slot in range(1, concurrency + 1):
        slot_pool.put_nowait(_slot)

    abort = asyncio.Event()
    aborted: ConcurrentAbort[T, R] | None = None
    started: list[bool] = [False] * len(items)
    tasks: list[asyncio.Task[object]] = []

    def _trigger_abort(item: T, exc: BaseException | None, result: R | None) -> None:
        nonlocal aborted
        if abort.is_set():
            return
        aborted = ConcurrentAbort(item=item, exception=exc, result=result)
        abort.set()
        current = asyncio.current_task()
        # Only cancel IN-FLIGHT (started) tasks. Not-yet-started tasks are left to
        # the abort-event gate below: cancelling a coroutine before it has begun
        # raises CancelledError outside its try/except and would escape gather.
        for i, task in enumerate(tasks):
            if task is not current and not task.done() and started[i]:
                task.cancel()

    async def _one(index: int, item: T) -> object:
        slot: int | None = None
        try:
            async with sem:
                if abort.is_set():
                    return _NotRun(item, "queued")
                slot = await slot_pool.get()
                try:
                    if on_start is not None:
                        on_start(item, slot)
                    started[index] = True
                    try:
                        result = await work(item, slot)
                    except asyncio.CancelledError:
                        if abort.is_set():
                            return _NotRun(item, "cancelled")
                        raise
                    except Exception as exc:
                        if should_abort_exception is not None and should_abort_exception(item, exc):
                            _trigger_abort(item, exc, None)
                            return _ABORT
                        result = exception_to_result(item, exc)
                    else:
                        if should_abort_result is not None and should_abort_result(result):
                            _trigger_abort(item, None, result)
                            return _ABORT
                    if on_outcome is not None:
                        on_outcome(result, slot)
                    return _Holder(result)
                finally:
                    if slot is not None:
                        slot_pool.put_nowait(slot)
        except asyncio.CancelledError:
            # Cancelled while waiting on the semaphore/slot (before work began).
            if abort.is_set():
                return _NotRun(item, "cancelled" if started[index] else "queued")
            raise

    start = time.perf_counter()
    tasks = [asyncio.create_task(_one(i, item)) for i, item in enumerate(items)]
    raw = await asyncio.gather(*tasks)
    wall = time.perf_counter() - start

    results: list[R] = []
    not_run: list[ConcurrentNotRun[T]] = []
    for entry in raw:
        if isinstance(entry, _Holder):
            results.append(cast("R", entry.result))
        elif isinstance(entry, _NotRun):
            not_run.append(ConcurrentNotRun(item=cast("T", entry.item), reason=entry.reason))
        # _ABORT sentinel: the aborting item is captured in `aborted`; skip.

    return ConcurrentSummary(
        results=tuple(results),
        not_run=tuple(not_run),
        aborted=aborted,
        concurrency=concurrency,
        wall_seconds=round(wall, 3),
    )


def run_concurrent[T, R](
    items: list[T],
    *,
    concurrency: int,
    work: Callable[[T, int], Awaitable[R]],
    exception_to_result: Callable[[T, Exception], R],
    should_abort_result: Callable[[R], bool] | None = None,
    should_abort_exception: Callable[[T, Exception], bool] | None = None,
    on_start: Callable[[T, int], None] | None = None,
    on_outcome: Callable[[R, int], None] | None = None,
) -> ConcurrentSummary[T, R]:
    """Synchronous wrapper around :func:`run_concurrent_async`.

    Enters one ``asyncio.run`` event loop. Do not call inside an existing event
    loop (use :func:`run_concurrent_async` directly instead).
    """
    return asyncio.run(
        run_concurrent_async(
            items,
            concurrency=concurrency,
            work=work,
            exception_to_result=exception_to_result,
            should_abort_result=should_abort_result,
            should_abort_exception=should_abort_exception,
            on_start=on_start,
            on_outcome=on_outcome,
        )
    )
