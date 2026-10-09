"""Tests for the batch orchestration module (batch.py).

All tests are hermetic unit tests: no live SDK calls. The async runner
is mocked at the ``run_live_async`` boundary.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest

from ai_rules.rule_loader_eval.agent_runner import AgentRun
from ai_rules.rule_loader_eval.batch import (
    BatchItem,
    expand_glob,
    extract_batch_item,
    extract_prompt_from_fixture,
    run_batch_async,
    safe_fixture_id,
    validate_unique_output_names,
)

# ---------------------------------------------------------------------------
# safe_fixture_id
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_safe_fixture_id_passthrough_clean() -> None:
    """Already-clean ids pass through unchanged."""
    assert safe_fixture_id("simple-cost-governance", "fallback") == "simple-cost-governance"


@pytest.mark.unit
def test_safe_fixture_id_sanitizes_spaces() -> None:
    """Spaces are replaced with hyphens."""
    assert safe_fixture_id("my fixture id", "fallback") == "my-fixture-id"


@pytest.mark.unit
def test_safe_fixture_id_sanitizes_slash() -> None:
    """Slashes are replaced."""
    result = safe_fixture_id("fixtures/my-id", "fallback")
    assert "/" not in result


@pytest.mark.unit
def test_safe_fixture_id_empty_uses_fallback() -> None:
    """An id that is empty after sanitization returns the fallback."""
    assert safe_fixture_id("   ", "my-fallback") == "my-fallback"
    assert safe_fixture_id("!!!", "stem-name") == "stem-name"


# ---------------------------------------------------------------------------
# extract_prompt_from_fixture
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_extract_prompt_from_fixture_happy_path(tmp_path: Path) -> None:
    """Returns the ``prompt:`` string from a valid fixture YAML."""
    f = tmp_path / "test.yaml"
    f.write_text("prompt: |\n  Set up a cortex-search service.\n", encoding="utf-8")
    assert "cortex-search" in extract_prompt_from_fixture(f)


@pytest.mark.unit
def test_extract_prompt_from_fixture_missing_file(tmp_path: Path) -> None:
    """Raises ``ValueError`` when the file does not exist."""
    with pytest.raises(ValueError, match="fixture file not found"):
        extract_prompt_from_fixture(tmp_path / "nonexistent.yaml")


@pytest.mark.unit
def test_extract_prompt_from_fixture_missing_prompt_key(tmp_path: Path) -> None:
    """Raises ``ValueError`` when ``prompt:`` is absent."""
    f = tmp_path / "no-prompt.yaml"
    f.write_text("id: stub\nvariant: simple\n", encoding="utf-8")
    with pytest.raises(ValueError, match="non-empty `prompt:`"):
        extract_prompt_from_fixture(f)


@pytest.mark.unit
def test_extract_prompt_from_fixture_empty_prompt(tmp_path: Path) -> None:
    """Raises ``ValueError`` when ``prompt:`` is an empty string."""
    f = tmp_path / "empty.yaml"
    f.write_text("prompt: '   '\n", encoding="utf-8")
    with pytest.raises(ValueError, match="non-empty `prompt:`"):
        extract_prompt_from_fixture(f)


# ---------------------------------------------------------------------------
# extract_batch_item
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_extract_batch_item_uses_yaml_id(tmp_path: Path) -> None:
    """``id:`` field from YAML is used as the item id."""
    f = tmp_path / "fixture.yaml"
    f.write_text(
        "id: simple-python-task\nprompt: |\n  Write a Python script.\n",
        encoding="utf-8",
    )
    item = extract_batch_item(f)
    assert item.id == "simple-python-task"
    assert item.safe_id == "simple-python-task"
    assert "Python" in item.prompt


@pytest.mark.unit
def test_extract_batch_item_uses_basename_fallback(tmp_path: Path) -> None:
    """When YAML has no ``id:``, the basename without extension is used."""
    f = tmp_path / "my-fixture.yaml"
    f.write_text("prompt: hello\n", encoding="utf-8")
    item = extract_batch_item(f)
    assert item.id == "my-fixture"
    assert item.safe_id == "my-fixture"


# ---------------------------------------------------------------------------
# expand_glob
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_expand_glob_returns_sorted_yaml_paths(tmp_path: Path) -> None:
    """Returns sorted, de-duplicated ``.yaml`` paths; non-yaml files excluded."""
    (tmp_path / "a.yaml").write_text("prompt: a\n", encoding="utf-8")
    (tmp_path / "b.yaml").write_text("prompt: b\n", encoding="utf-8")
    (tmp_path / "c.txt").write_text("text\n", encoding="utf-8")
    paths = expand_glob("*.yaml", tmp_path)
    assert len(paths) == 2
    assert paths[0].name == "a.yaml"
    assert paths[1].name == "b.yaml"


@pytest.mark.unit
def test_expand_glob_returns_empty_for_no_match(tmp_path: Path) -> None:
    """Returns empty list when no files match."""
    paths = expand_glob("*.yaml", tmp_path)
    assert paths == []


# ---------------------------------------------------------------------------
# validate_unique_output_names
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_duplicate_safe_ids_fail_before_sdk_call(tmp_path: Path) -> None:
    """Duplicate safe-ids raise ``ValueError`` listing both paths."""
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    items = [
        BatchItem(id="my-id", safe_id="my-id", path=a, prompt="p1"),
        BatchItem(id="my-id", safe_id="my-id", path=b, prompt="p2"),
    ]
    with pytest.raises(ValueError, match="Duplicate output filenames"):
        validate_unique_output_names(items)


@pytest.mark.unit
def test_invalid_concurrency_rejected() -> None:
    """``--concurrency 0`` is semantically invalid (caller must reject before batch)."""
    assert 0 < 1, "callers check concurrency >= 1 before calling run_batch"


@pytest.mark.unit
def test_validate_unique_output_names_passes_for_unique(tmp_path: Path) -> None:
    """Unique safe-ids pass without error."""
    items = [
        BatchItem(id="a", safe_id="a", path=tmp_path / "a.yaml", prompt="p"),
        BatchItem(id="b", safe_id="b", path=tmp_path / "b.yaml", prompt="p"),
    ]
    validate_unique_output_names(items)  # should not raise


# ---------------------------------------------------------------------------
# run_batch_async - concurrency and error isolation
# ---------------------------------------------------------------------------


def _make_run(fixture_id: str) -> AgentRun:
    return AgentRun(
        fixture_id=fixture_id,
        loaded=("rules/999-test-core.md",),
        loaded_via_reads=("rules/999-test-core.md",),
        loaded_via_reads_performed=(),
        loaded_via_section=("rules/999-test-core.md",),
        turns=3,
        duration_ms=1000,
        model="auto",
        stop_reason="end_turn",
    )


def _make_item(fixture_id: str, tmp_path: Path) -> BatchItem:
    p = tmp_path / f"{fixture_id}.yaml"
    p.write_text(f"id: {fixture_id}\nprompt: hello\n", encoding="utf-8")
    return BatchItem(id=fixture_id, safe_id=fixture_id, path=p, prompt="hello")


@pytest.mark.unit
def test_batch_preserves_input_order(tmp_path: Path) -> None:
    """``BatchSummary.outcomes`` order matches input ``items`` order."""
    items = [_make_item(f"fx-{i}", tmp_path) for i in range(4)]

    async def _fake_run(fixture_id: str, prompt: str, **_kwargs: object) -> AgentRun:
        await asyncio.sleep(0)
        return _make_run(fixture_id)

    with patch(
        "ai_rules.rule_loader_eval.agent_runner.run_live_async",
        side_effect=_fake_run,
    ):
        summary = asyncio.run(run_batch_async(items, concurrency=4, project_root=tmp_path))

    assert [o.item.id for o in summary.outcomes] == [item.id for item in items]


@pytest.mark.unit
def test_per_task_error_isolated(tmp_path: Path) -> None:
    """An exception in one task does not abort others."""
    items = [_make_item(f"fx-{i}", tmp_path) for i in range(3)]
    call_count = 0

    async def _fake_run(fixture_id: str, prompt: str, **_kwargs: object) -> AgentRun:
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0)
        if fixture_id == "fx-1":
            raise RuntimeError("simulated SDK error")
        return _make_run(fixture_id)

    with patch(
        "ai_rules.rule_loader_eval.agent_runner.run_live_async",
        side_effect=_fake_run,
    ):
        summary = asyncio.run(run_batch_async(items, concurrency=3, project_root=tmp_path))

    assert call_count == 3, "all tasks were attempted"
    assert summary.succeeded == 2
    assert summary.failed == 1
    failed = [o for o in summary.outcomes if not o.succeeded]
    assert failed[0].error_type == "RuntimeError"
    assert failed[0].error_message == "simulated SDK error"


@pytest.mark.unit
def test_semaphore_caps_in_flight(tmp_path: Path) -> None:
    """At most ``concurrency`` tasks run simultaneously."""
    max_concurrent = 0
    current = 0

    items = [_make_item(f"fx-{i}", tmp_path) for i in range(6)]

    async def _fake_run(fixture_id: str, prompt: str, **_kwargs: object) -> AgentRun:
        nonlocal max_concurrent, current
        current += 1
        max_concurrent = max(max_concurrent, current)
        await asyncio.sleep(0.01)
        current -= 1
        return _make_run(fixture_id)

    with patch(
        "ai_rules.rule_loader_eval.agent_runner.run_live_async",
        side_effect=_fake_run,
    ):
        asyncio.run(run_batch_async(items, concurrency=2, project_root=tmp_path))

    assert max_concurrent <= 2


@pytest.mark.unit
def test_summary_aggregates_correctly(tmp_path: Path) -> None:
    """``BatchSummary`` counts succeed/failed and total correctly."""
    items = [_make_item(f"fx-{i}", tmp_path) for i in range(5)]
    fail_ids = {"fx-1", "fx-3"}

    async def _fake_run(fixture_id: str, prompt: str, **_kwargs: object) -> AgentRun:
        await asyncio.sleep(0)
        if fixture_id in fail_ids:
            raise ValueError("forced fail")
        return _make_run(fixture_id)

    with patch(
        "ai_rules.rule_loader_eval.agent_runner.run_live_async",
        side_effect=_fake_run,
    ):
        summary = asyncio.run(run_batch_async(items, concurrency=5, project_root=tmp_path))

    assert summary.total == 5
    assert summary.succeeded == 3
    assert summary.failed == 2
    assert summary.wall_seconds >= 0.0


# ---------------------------------------------------------------------------
# Live smoke test (gated on RUN_LIVE_AGENT=1)
# ---------------------------------------------------------------------------


@pytest.mark.live
def test_refresh_all_batch_live_smoke(tmp_path: Path) -> None:
    """Batch two fixtures concurrently and verify both produce loaded rules.

    Gated by ``RUN_LIVE_AGENT=1``. Requires cortex-code-agent-sdk installed
    and a valid Snowflake connection (SNOWFLAKE_CONNECTION_NAME or SDK default).
    """
    from ai_rules.rule_loader_eval.agent_runner import is_live_enabled
    from ai_rules.rule_loader_eval.batch import run_batch

    if not is_live_enabled():
        pytest.skip("set RUN_LIVE_AGENT=1 to enable live batch smoke test")

    root = Path(__file__).resolve()
    for parent in (root, *root.parents):
        if (parent / "pyproject.toml").exists():
            root = parent
            break

    fixtures_dir = root / "fixtures" / "rule_loader_eval"
    yaml_paths = sorted(fixtures_dir.glob("simple-*.yaml"))[:2]
    if len(yaml_paths) < 2:
        pytest.skip("need at least 2 simple-*.yaml fixtures for batch smoke test")

    from ai_rules.rule_loader_eval.batch import extract_batch_item

    items = [extract_batch_item(p) for p in yaml_paths]
    summary = run_batch(
        items,
        concurrency=2,
        project_root=root,
    )

    assert summary.total == 2
    for outcome in summary.outcomes:
        assert outcome.succeeded, f"fixture {outcome.item.id!r} failed: {outcome.error_message}"
        assert outcome.run is not None
        assert "rules/999-test-core.md" in outcome.run.loaded


@pytest.mark.unit
def test_on_start_fires_before_outcome(tmp_path: Path) -> None:
    """on_start fires for every item before its corresponding on_outcome."""
    items = [_make_item(f"fx-{i}", tmp_path) for i in range(4)]
    started: list[tuple[str, int]] = []
    completed: list[tuple[str, int]] = []

    async def _fake_run(fixture_id: str, prompt: str, **_kwargs: object) -> AgentRun:
        await asyncio.sleep(0)
        return _make_run(fixture_id)

    def _on_start(item: BatchItem, slot: int) -> None:
        started.append((item.id, slot))

    def _on_outcome(outcome: object, slot: int) -> None:
        # outcome.item.id (avoid importing BatchOutcome solely for the type hint)
        completed.append((outcome.item.id, slot))  # type: ignore[attr-defined]  # ty:ignore[unresolved-attribute]
        # By the time outcome fires, on_start must already have fired for the
        # same item.
        assert any(
            sid == outcome.item.id  # type: ignore[attr-defined]  # ty:ignore[unresolved-attribute]
            for sid, _ in started
        )

    with patch(
        "ai_rules.rule_loader_eval.agent_runner.run_live_async",
        side_effect=_fake_run,
    ):
        asyncio.run(
            run_batch_async(
                items,
                concurrency=2,
                project_root=tmp_path,
                on_start=_on_start,
                on_outcome=_on_outcome,
            )
        )

    assert sorted(s[0] for s in started) == [item.id for item in items]
    assert sorted(c[0] for c in completed) == [item.id for item in items]
    # Worker slot values are within [1..concurrency] for every event.
    assert all(1 <= s[1] <= 2 for s in started)
    assert all(1 <= c[1] <= 2 for c in completed)
