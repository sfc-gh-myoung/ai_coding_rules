"""Unit tests for ``ProgressTracker`` and ``resolve_progress_mode``.

Covers the screen-backed Live UI, the ``rich`` alias, the auto-detect TTY
heuristic, the active-fixtures + recent-completions ledger model, and the
unchanged PLAIN/JSON/NONE paths.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from ai_rules.commands.rule_loader import (
    ProgressMode,
    ProgressTracker,
    resolve_progress_mode,
)

# ---------------------------------------------------------------------------
# resolve_progress_mode
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_resolve_progress_mode_explicit_values() -> None:
    """Explicit values map directly. ``rich`` is an alias for ``screen``."""
    assert resolve_progress_mode("screen") is ProgressMode.SCREEN
    assert resolve_progress_mode("rich") is ProgressMode.SCREEN
    assert resolve_progress_mode("plain") is ProgressMode.PLAIN
    assert resolve_progress_mode("none") is ProgressMode.NONE


@pytest.mark.unit
def test_resolve_progress_mode_case_and_whitespace_insensitive() -> None:
    """Whitespace and case differences are normalised."""
    assert resolve_progress_mode("  SCREEN  ") is ProgressMode.SCREEN
    assert resolve_progress_mode("Rich") is ProgressMode.SCREEN
    assert resolve_progress_mode("Plain") is ProgressMode.PLAIN


@pytest.mark.unit
def test_resolve_progress_mode_auto_isatty_returns_screen() -> None:
    """Auto + capable TTY → SCREEN (alternate-screen Live UI)."""
    with patch("ai_rules.commands.rule_loader.is_progress_capable", return_value=True):
        assert resolve_progress_mode("auto") is ProgressMode.SCREEN
        assert resolve_progress_mode(None) is ProgressMode.SCREEN


@pytest.mark.unit
def test_resolve_progress_mode_auto_pipe_returns_none() -> None:
    """Auto + non-capable env → NONE (silent)."""
    with patch("ai_rules.commands.rule_loader.is_progress_capable", return_value=False):
        assert resolve_progress_mode("auto") is ProgressMode.NONE


@pytest.mark.unit
def test_resolve_progress_mode_invalid_raises() -> None:
    """Unknown values raise BadParameter (Typer exits with usage)."""
    import typer

    with pytest.raises(typer.BadParameter):
        resolve_progress_mode("verbose")


@pytest.mark.unit
def test_resolve_progress_mode_invalid_message_lists_screen() -> None:
    """Error text advertises the full accepted-value list including ``screen``."""
    import typer

    with pytest.raises(typer.BadParameter) as exc:
        resolve_progress_mode("verbose")
    assert "auto|screen|rich|plain|json|none" in str(exc.value)


# ---------------------------------------------------------------------------
# ProgressTracker — SCREEN mode
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tracker_screen_constructs_alt_screen_live() -> None:
    """SCREEN mode wires Live with screen=True and transient=True."""
    captured: dict[str, object] = {}
    real_live_cls = None

    from ai_rules.commands import rule_loader as rl

    real_live_cls = rl.Live

    class FakeLive:
        def __init__(self, renderable: object, **kwargs: object) -> None:
            captured.update(kwargs)
            captured["renderable"] = renderable
            self._stopped = False

        def __enter__(self) -> FakeLive:
            return self

        def __exit__(self, *_: object) -> None:
            self._stopped = True

        def update(self, renderable: object) -> None:
            captured["renderable"] = renderable

    with patch.object(rl, "Live", FakeLive):
        with ProgressTracker(total=2, mode=ProgressMode.SCREEN, description="t"):
            pass

    assert captured.get("screen") is True
    assert captured.get("transient") is True
    assert captured.get("redirect_stdout") is False
    assert captured.get("redirect_stderr") is False
    # Sanity: the original Live class is the real one
    assert real_live_cls is not FakeLive


@pytest.mark.unit
def test_tracker_screen_active_and_recent_state() -> None:
    """SCREEN mode tracks active items and moves finished ones to a ledger."""
    from ai_rules.commands import rule_loader as rl

    class FakeLive:
        def __init__(self, *_: object, **__: object) -> None: ...
        def __enter__(self):
            return self

        def __exit__(self, *_: object) -> None: ...
        def update(self, *_: object, **__: object) -> None: ...

    with patch.object(rl, "Live", FakeLive):
        with ProgressTracker(total=2, mode=ProgressMode.SCREEN) as tracker:
            tracker.start_item("alpha", slot=1)
            tracker.start_item("beta", slot=2)
            assert "alpha" in tracker._active  # type: ignore[attr-defined]
            assert "beta" in tracker._active  # type: ignore[attr-defined]
            assert len(tracker._recent) == 0  # type: ignore[attr-defined]

            tracker.finish_item("alpha", ok=True, slot=1)
            assert "alpha" not in tracker._active  # type: ignore[attr-defined]
            assert "beta" in tracker._active  # type: ignore[attr-defined]
            assert len(tracker._recent) == 1  # type: ignore[attr-defined]
            entry = tracker._recent[-1]  # type: ignore[attr-defined]
            assert entry["fixture_id"] == "alpha"
            assert entry["ok"] is True

            tracker.finish_item("beta", ok=False, slot=2)
            assert tracker._active == {}  # type: ignore[attr-defined]
            assert len(tracker._recent) == 2  # type: ignore[attr-defined]
            assert tracker._recent[-1]["ok"] is False  # type: ignore[attr-defined]


@pytest.mark.unit
def test_tracker_screen_recent_ledger_capped() -> None:
    """Recent-completions deque is bounded to ``_RECENT_LEDGER_MAX``."""
    from ai_rules.commands import rule_loader as rl

    class FakeLive:
        def __init__(self, *_: object, **__: object) -> None: ...
        def __enter__(self):
            return self

        def __exit__(self, *_: object) -> None: ...
        def update(self, *_: object, **__: object) -> None: ...

    cap = ProgressTracker._RECENT_LEDGER_MAX
    with patch.object(rl, "Live", FakeLive):
        with ProgressTracker(total=cap + 5, mode=ProgressMode.SCREEN) as tracker:
            for i in range(cap + 5):
                fid = f"fx-{i}"
                tracker.start_item(fid)
                tracker.finish_item(fid, ok=True)
            assert len(tracker._recent) == cap  # type: ignore[attr-defined]
            ids = [e["fixture_id"] for e in tracker._recent]  # type: ignore[attr-defined]
            assert ids[0] == f"fx-{5}"
            assert ids[-1] == f"fx-{cap + 4}"


@pytest.mark.unit
def test_tracker_screen_exit_clears_state_on_exception() -> None:
    """``__exit__`` always clears active state, even when the body raises."""
    from ai_rules.commands import rule_loader as rl

    class FakeLive:
        def __init__(self, *_: object, **__: object) -> None: ...
        def __enter__(self):
            return self

        def __exit__(self, *_: object) -> None: ...
        def update(self, *_: object, **__: object) -> None: ...

    tracker = ProgressTracker(total=1, mode=ProgressMode.SCREEN)
    with patch.object(rl, "Live", FakeLive), pytest.raises(KeyboardInterrupt), tracker:
        tracker.start_item("alpha")
        raise KeyboardInterrupt()
    assert tracker._active == {}  # type: ignore[attr-defined]
    assert tracker._start_times == {}  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# ProgressTracker — PLAIN mode
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tracker_plain_emits_log_lines(capsys: pytest.CaptureFixture[str]) -> None:
    """PLAIN mode emits one start and one done line per item, on stderr."""
    with ProgressTracker(total=2, mode=ProgressMode.PLAIN) as tracker:
        tracker.start_item("alpha")
        tracker.finish_item("alpha", ok=True)
        tracker.start_item("beta")
        tracker.finish_item("beta", ok=False)

    captured = capsys.readouterr()
    out = captured.err
    assert "start  alpha" in out
    assert "done   alpha  ok" in out
    assert "start  beta" in out
    assert "done   beta  FAIL" in out


# ---------------------------------------------------------------------------
# ProgressTracker — NONE mode
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tracker_none_is_silent(capsys: pytest.CaptureFixture[str]) -> None:
    """NONE mode produces no output and does not raise."""
    with ProgressTracker(total=2, mode=ProgressMode.NONE) as tracker:
        tracker.start_item("alpha")
        tracker.finish_item("alpha", ok=True)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


# ---------------------------------------------------------------------------
# quiet_sdk
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_quiet_sdk_captures_stdout_when_capture_true() -> None:
    """quiet_sdk(capture=True) redirects stdout into the yielded buffer."""
    from ai_rules.rule_loader_eval.sdk_capture import quiet_sdk

    with quiet_sdk(capture=True) as buf:
        print("noise from SDK")
        assert buf is not None
    assert "noise from SDK" in buf.getvalue()


@pytest.mark.unit
def test_quiet_sdk_noop_when_capture_false() -> None:
    """quiet_sdk(capture=False) is a no-op and yields None."""
    from ai_rules.rule_loader_eval.sdk_capture import quiet_sdk

    with quiet_sdk(capture=False) as buf:
        assert buf is None


@pytest.mark.unit
def test_quiet_sdk_restores_logger_level() -> None:
    """quiet_sdk restores the SDK logger level on exit."""
    import logging

    from ai_rules.rule_loader_eval.sdk_capture import quiet_sdk

    sdk_logger = logging.getLogger("cortex_code_agent_sdk")
    sdk_logger.setLevel(logging.DEBUG)

    with quiet_sdk(capture=True):
        assert sdk_logger.level == logging.ERROR
    assert sdk_logger.level == logging.DEBUG


# ---------------------------------------------------------------------------
# Slot prefix + JSON mode + visual polish
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_resolve_progress_mode_json() -> None:
    """`--progress=json` resolves to ProgressMode.JSON."""
    assert resolve_progress_mode("json") is ProgressMode.JSON


@pytest.mark.unit
def test_tracker_screen_renders_slot_prefix() -> None:
    """SCREEN mode label includes a `[wN]` slot prefix when supplied."""
    label = ProgressTracker(total=2, mode=ProgressMode.SCREEN)._format_label("alpha", slot=2)
    assert label.startswith("[w2] alpha")


@pytest.mark.unit
def test_tracker_plain_renders_slot_prefix(capsys: pytest.CaptureFixture[str]) -> None:
    """PLAIN mode log lines include `[wN]` slot prefix."""
    with ProgressTracker(total=2, mode=ProgressMode.PLAIN) as tracker:
        tracker.start_item("alpha", slot=3)
        tracker.finish_item("alpha", ok=True, slot=3)
    err = capsys.readouterr().err
    assert "[w3] alpha" in err


@pytest.mark.unit
def test_tracker_format_label_pads_to_id_pad() -> None:
    """`_format_label` left-pads short ids to `id_pad` width."""
    tracker = ProgressTracker(total=1, mode=ProgressMode.NONE, id_pad=20)
    assert tracker._format_label("alpha", None) == "alpha               "
    assert tracker._format_label("alpha", 1) == "[w1] alpha               "


@pytest.mark.unit
def test_tracker_format_label_grows_for_long_ids() -> None:
    """`_format_label` never truncates ids longer than `id_pad`."""
    tracker = ProgressTracker(total=1, mode=ProgressMode.NONE, id_pad=5)
    long = "a-very-long-fixture-id"
    assert tracker._format_label(long, None) == long
    assert tracker._format_label(long, 1) == f"[w1] {long}"


@pytest.mark.unit
def test_tracker_json_emits_start_event(capsys: pytest.CaptureFixture[str]) -> None:
    """JSON mode emits a parseable `start` event on stderr."""
    import json

    with ProgressTracker(total=2, mode=ProgressMode.JSON) as tracker:
        tracker.start_item("alpha", slot=1)
    line = capsys.readouterr().err.strip().splitlines()[-1]
    payload = json.loads(line)
    assert payload["event"] == "start"
    assert payload["fixture"] == "alpha"
    assert payload["slot"] == 1
    assert payload["total"] == 2
    assert payload["ts"].endswith("Z")


@pytest.mark.unit
def test_tracker_json_emits_done_event_with_elapsed(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """JSON mode emits a parseable `done` event with elapsed_seconds + ok."""
    import json

    with ProgressTracker(total=1, mode=ProgressMode.JSON) as tracker:
        tracker.start_item("alpha", slot=1)
        tracker.finish_item("alpha", ok=False, slot=1)
    lines = capsys.readouterr().err.strip().splitlines()
    done = json.loads(lines[-1])
    assert done["event"] == "done"
    assert done["fixture"] == "alpha"
    assert done["ok"] is False
    assert done["slot"] == 1
    assert "elapsed_seconds" in done
    assert isinstance(done["elapsed_seconds"], float)


@pytest.mark.unit
def test_tracker_json_emits_run_header_and_footer(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """JSON mode emits start_run + end_run boundary events."""
    import json

    with ProgressTracker(total=1, mode=ProgressMode.JSON) as tracker:
        tracker.start_run(pid=1234, concurrency=2)
        tracker.start_item("alpha", slot=1)
        tracker.finish_item("alpha", ok=True, slot=1)
        tracker.end_run(succeeded=1, failed=0, wall_seconds=0.5)
    payloads = [json.loads(line) for line in capsys.readouterr().err.strip().splitlines()]
    events = [p["event"] for p in payloads]
    assert events == ["start_run", "start", "done", "end_run"]
    assert payloads[0]["pid"] == 1234
    assert payloads[0]["concurrency"] == 2
    assert payloads[-1]["wall_seconds"] == 0.5
    assert payloads[-1]["succeeded"] == 1
    assert payloads[-1]["failed"] == 0


# ---------------------------------------------------------------------------
# Worker-slot pool (asyncio.Queue) invariants
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_slot_queue_yields_1_to_n_in_run_batch() -> None:
    """run_batch_async assigns slots in [1..concurrency], exclusive while held."""
    import asyncio
    from pathlib import Path
    from unittest.mock import patch

    from ai_rules.rule_loader_eval.agent_runner import AgentRun
    from ai_rules.rule_loader_eval.batch import BatchItem, run_batch_async

    items = [
        BatchItem(id=f"fx-{i}", safe_id=f"fx-{i}", path=Path(f"fx-{i}.yaml"), prompt="p")
        for i in range(6)
    ]

    held: set[int] = set()
    seen_slots: list[int] = []
    max_concurrent = 0
    asyncio.Lock()

    async def _fake_run(fixture_id: str, prompt: str, **_kwargs: object) -> AgentRun:
        # Hold the slot briefly to exercise concurrency.
        await asyncio.sleep(0.01)
        return AgentRun(
            fixture_id=fixture_id,
            loaded=("rules/999-test-core.md",),
            loaded_via_reads=("rules/999-test-core.md",),
            loaded_via_reads_performed=(),
            loaded_via_section=("rules/999-test-core.md",),
            turns=1,
            duration_ms=10,
            model="auto",
            stop_reason="end_turn",
        )

    def _on_start(item: BatchItem, slot: int) -> None:
        # Slot must never be duplicated for in-flight tasks.
        assert slot not in held
        held.add(slot)
        seen_slots.append(slot)

    def _on_outcome(outcome: object, slot: int) -> None:
        held.discard(slot)
        nonlocal max_concurrent
        max_concurrent = max(max_concurrent, len(held) + 1)

    with patch(
        "ai_rules.rule_loader_eval.agent_runner.run_live_async",
        side_effect=_fake_run,
    ):
        asyncio.run(
            run_batch_async(
                items,
                concurrency=3,
                on_start=_on_start,
                on_outcome=_on_outcome,
            )
        )

    assert all(1 <= s <= 3 for s in seen_slots)
    assert held == set()  # all released
    assert len(seen_slots) == len(items)


@pytest.mark.unit
def test_slot_released_after_sdk_exception() -> None:
    """A failing SDK call still releases its slot back to the pool."""
    import asyncio
    from pathlib import Path
    from unittest.mock import patch

    from ai_rules.rule_loader_eval.batch import BatchItem, run_batch_async

    items = [
        BatchItem(id=f"fx-{i}", safe_id=f"fx-{i}", path=Path(f"fx-{i}.yaml"), prompt="p")
        for i in range(4)
    ]

    async def _always_fail(fixture_id: str, prompt: str, **_kwargs: object):
        await asyncio.sleep(0.001)
        raise RuntimeError(f"boom {fixture_id}")

    held: set[int] = set()

    def _on_start(_item: BatchItem, slot: int) -> None:
        assert slot not in held
        held.add(slot)

    def _on_outcome(_outcome: object, slot: int) -> None:
        held.discard(slot)

    with patch(
        "ai_rules.rule_loader_eval.agent_runner.run_live_async",
        side_effect=_always_fail,
    ):
        summary = asyncio.run(
            run_batch_async(
                items,
                concurrency=2,
                on_start=_on_start,
                on_outcome=_on_outcome,
            )
        )
    # Every slot was released, every fixture has a synthetic failure outcome.
    assert held == set()
    assert all(o.error_type == "RuntimeError" for o in summary.outcomes)
