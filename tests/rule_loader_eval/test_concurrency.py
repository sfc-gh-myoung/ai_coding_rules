"""Unit tests for the generic concurrent driver (``concurrency.py``).

All tests use plain in-memory async ``work`` callables; no live SDK required.
"""

from __future__ import annotations

import asyncio

import pytest

from ai_rules.rule_loader_eval.concurrency import (
    ConcurrentSummary,
    run_concurrent_async,
)


def _identity_exc_to_result(item: object, exc: Exception) -> str:
    """Convert a non-aborting exception into a marker string result."""
    return f"ERR:{item}:{type(exc).__name__}"


def test_runs_all_items_with_mocked_work() -> None:
    """(1) The driver runs every item and returns one result each."""

    async def work(item: int, slot: int) -> int:
        return item * 10

    summary: ConcurrentSummary[int, int] = asyncio.run(
        run_concurrent_async(
            [1, 2, 3],
            concurrency=2,
            work=work,
            exception_to_result=lambda i, e: -1,
        )
    )
    assert summary.results == (10, 20, 30)
    assert summary.aborted is None
    assert summary.not_run == ()


def test_results_in_input_order_despite_staggered_completion() -> None:
    """(2) Result tuple is in INPUT order regardless of completion order."""

    async def work(item: int, slot: int) -> int:
        # Later items finish first (inverse delay) to force out-of-order completion.
        await asyncio.sleep((5 - item) * 0.01)
        return item

    summary = asyncio.run(
        run_concurrent_async(
            [1, 2, 3, 4],
            concurrency=4,
            work=work,
            exception_to_result=lambda i, e: -1,
        )
    )
    assert summary.results == (1, 2, 3, 4)


def test_semaphore_caps_in_flight_at_n() -> None:
    """(3) Observed max concurrency never exceeds N."""
    in_flight = 0
    peak = 0

    async def work(item: int, slot: int) -> int:
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.01)
        in_flight -= 1
        return item

    asyncio.run(
        run_concurrent_async(
            list(range(20)),
            concurrency=3,
            work=work,
            exception_to_result=lambda i, e: -1,
        )
    )
    assert peak == 3


def test_slot_pool_assigns_1_to_n_and_releases() -> None:
    """(4) Slots stay within [1..N] and are reused (no leak across > N items)."""
    seen_slots: set[int] = set()

    async def work(item: int, slot: int) -> int:
        seen_slots.add(slot)
        await asyncio.sleep(0.005)
        return item

    asyncio.run(
        run_concurrent_async(
            list(range(10)),
            concurrency=2,
            work=work,
            exception_to_result=lambda i, e: -1,
        )
    )
    assert seen_slots == {1, 2}


def test_on_start_and_on_outcome_fire_with_slot() -> None:
    """(5) Callbacks fire with a valid slot for each completed item."""
    starts: list[tuple[int, int]] = []
    outcomes: list[tuple[int, int]] = []

    async def work(item: int, slot: int) -> int:
        return item

    asyncio.run(
        run_concurrent_async(
            [7, 8],
            concurrency=2,
            work=work,
            exception_to_result=lambda i, e: -1,
            on_start=lambda item, slot: starts.append((item, slot)),
            on_outcome=lambda result, slot: outcomes.append((result, slot)),
        )
    )
    assert {s[0] for s in starts} == {7, 8}
    assert {o[0] for o in outcomes} == {7, 8}
    assert all(1 <= s[1] <= 2 for s in starts)
    assert all(1 <= o[1] <= 2 for o in outcomes)


def test_non_aborting_exception_captured_via_converter() -> None:
    """(6) Non-aborting exceptions become per-item results; peers are not cancelled."""

    async def work(item: int, slot: int) -> str:
        if item == 2:
            raise ValueError("boom")
        return f"ok:{item}"

    outcomes: list[str] = []
    summary = asyncio.run(
        run_concurrent_async(
            [1, 2, 3],
            concurrency=3,
            work=work,
            exception_to_result=_identity_exc_to_result,
            on_outcome=lambda r, s: outcomes.append(r),
        )
    )
    assert summary.results == ("ok:1", "ERR:2:ValueError", "ok:3")
    assert summary.aborted is None
    assert summary.not_run == ()
    # on_outcome fired for the converted exception too.
    assert "ERR:2:ValueError" in outcomes


def test_exception_triggered_abort_cancels_and_skips() -> None:
    """(7) should_abort_exception cancels in-flight + skips queued; abort metadata set."""

    class InfraLike(RuntimeError):
        pass

    async def work(item: int, slot: int) -> int:
        if item == 0:
            raise InfraLike("sdk down")
        await asyncio.sleep(0.05)  # keep peers in-flight so they get cancelled
        return item

    summary = asyncio.run(
        run_concurrent_async(
            [0, 1, 2, 3, 4],
            concurrency=2,
            work=work,
            exception_to_result=lambda i, e: -1,
            should_abort_exception=lambda item, exc: isinstance(exc, InfraLike),
        )
    )
    assert summary.aborted is not None
    assert summary.aborted.item == 0
    assert isinstance(summary.aborted.exception, InfraLike)
    assert summary.aborted.result is None
    # The aborting item is neither a result nor a not_run entry.
    assert 0 not in summary.results
    # Every other item is accounted for as not_run (queued or cancelled).
    not_run_items = {nr.item for nr in summary.not_run}
    assert not_run_items == {1, 2, 3, 4}
    assert all(nr.reason in {"queued", "cancelled"} for nr in summary.not_run)


def test_result_triggered_abort_includes_triggering_result() -> None:
    """(8) should_abort_result aborts and captures the triggering result."""

    async def work(item: int, slot: int) -> int:
        if item == 9:
            return 9
        await asyncio.sleep(0.05)
        return item

    summary = asyncio.run(
        run_concurrent_async(
            [9, 1, 2, 3],
            concurrency=2,
            work=work,
            exception_to_result=lambda i, e: -1,
            should_abort_result=lambda result: result == 9,
        )
    )
    assert summary.aborted is not None
    assert summary.aborted.item == 9
    assert summary.aborted.result == 9
    assert summary.aborted.exception is None
    assert 9 not in summary.results
    assert {nr.item for nr in summary.not_run} == {1, 2, 3}


def test_external_cancellation_reraises() -> None:
    """(9) External cancellation (no abort set) propagates CancelledError."""

    async def work(item: int, slot: int) -> int:
        await asyncio.sleep(10)
        return item

    async def _driver_then_cancel() -> None:
        task = asyncio.create_task(
            run_concurrent_async(
                [1, 2, 3],
                concurrency=2,
                work=work,
                exception_to_result=lambda i, e: -1,
            )
        )
        await asyncio.sleep(0.02)
        task.cancel()
        await task

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(_driver_then_cancel())
