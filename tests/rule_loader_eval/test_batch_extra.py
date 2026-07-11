"""Extra branch-coverage tests for batch.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from ai_rules.rule_loader_eval.agent_runner import AgentRun
from ai_rules.rule_loader_eval.batch import (
    BatchItem,
    extract_prompt_from_fixture,
    run_batch,
)

# ---------------------------------------------------------------------------
# extract_prompt_from_fixture error paths
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_extract_prompt_invalid_yaml_raises(tmp_path: Path) -> None:
    """extract_prompt_from_fixture raises ValueError on malformed YAML."""
    bad = tmp_path / "bad.yaml"
    bad.write_text("{not: valid: yaml: [[", encoding="utf-8")
    with pytest.raises(ValueError, match="failed to parse"):
        extract_prompt_from_fixture(bad)


@pytest.mark.unit
def test_extract_prompt_non_dict_yaml_raises(tmp_path: Path) -> None:
    """extract_prompt_from_fixture raises ValueError when YAML is not a mapping."""
    f = tmp_path / "f.yaml"
    f.write_text("- just a list\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a mapping"):
        extract_prompt_from_fixture(f)


@pytest.mark.unit
def test_extract_prompt_missing_prompt_key_raises(tmp_path: Path) -> None:
    """extract_prompt_from_fixture raises ValueError when prompt is absent."""
    f = tmp_path / "f.yaml"
    f.write_text("id: test\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing a non-empty"):
        extract_prompt_from_fixture(f)


# ---------------------------------------------------------------------------
# _extract_fixture_id exception path
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_extract_batch_item_malformed_yaml_falls_back_to_stem(tmp_path: Path) -> None:
    """extract_batch_item falls back to stem when YAML parse fails."""
    bad = tmp_path / "my-fixture.yaml"
    # Valid enough for the id extractor but malformed YAML triggers the except
    # Actually _extract_fixture_id catches ALL exceptions and falls back to stem
    bad.write_text("{: broken: [[", encoding="utf-8")
    # extract_prompt_from_fixture will also fail on this malformed YAML
    # Test _extract_fixture_id fallback directly
    from ai_rules.rule_loader_eval.batch import _extract_fixture_id

    result = _extract_fixture_id(bad)
    assert result == "my-fixture"


# ---------------------------------------------------------------------------
# run_batch (synchronous wrapper)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_run_batch_synchronous_wrapper_calls_async(tmp_path: Path) -> None:
    """run_batch is a synchronous asyncio.run wrapper that returns a BatchSummary."""
    from ai_rules.rule_loader_eval.batch import BatchSummary

    item = BatchItem(
        id="test-fixture",
        safe_id="test-fixture",
        path=tmp_path / "test.yaml",
        prompt="Fix the bug in auth.py",
    )

    mock_run = AgentRun(
        fixture_id="test-fixture",
        loaded=("rules/000-global-core.md",),
        loaded_via_reads=(),
        loaded_via_reads_performed=(),
        loaded_via_section=(),
    )

    def fake_run_live_async(*args, **kwargs):

        async def _inner():
            return mock_run

        return _inner()

    with patch(
        "ai_rules.rule_loader_eval.agent_runner.run_live_async",
        side_effect=fake_run_live_async,
    ):
        summary = run_batch([item], concurrency=1)

    assert isinstance(summary, BatchSummary)
    assert summary.total == 1


@pytest.mark.unit
def test_run_batch_behavior_unchanged_after_driver_delegation(tmp_path: Path) -> None:
    """Regression guard: after delegating to concurrency.run_concurrent_async,
    run_batch still returns a BatchSummary with input-order outcomes, correct
    ``concurrency``, populated ``wall_seconds``, and slot values via callbacks.
    """
    from ai_rules.rule_loader_eval.batch import BatchSummary

    items = [
        BatchItem(id=f"fx-{n}", safe_id=f"fx-{n}", path=tmp_path / f"{n}.yaml", prompt=f"p{n}")
        for n in range(4)
    ]

    def fake_run_live_async(fixture_id, prompt, **kwargs):
        async def _inner():
            return AgentRun(
                fixture_id=fixture_id,
                loaded=("rules/000-global-core.md",),
                loaded_via_reads=(),
                loaded_via_reads_performed=(),
                loaded_via_section=(),
            )

        return _inner()

    start_slots: list[int] = []
    outcome_slots: list[int] = []

    with patch(
        "ai_rules.rule_loader_eval.agent_runner.run_live_async",
        side_effect=fake_run_live_async,
    ):
        summary = run_batch(
            items,
            concurrency=2,
            on_start=lambda item, slot: start_slots.append(slot),
            on_outcome=lambda outcome, slot: outcome_slots.append(slot),
        )

    assert isinstance(summary, BatchSummary)
    assert summary.concurrency == 2
    assert summary.wall_seconds >= 0.0
    # Outcomes are in INPUT order regardless of completion order.
    assert [o.item.id for o in summary.outcomes] == ["fx-0", "fx-1", "fx-2", "fx-3"]
    assert all(o.succeeded for o in summary.outcomes)
    # Slots stay within [1..concurrency] for both callbacks.
    assert start_slots and all(1 <= s <= 2 for s in start_slots)
    assert outcome_slots and all(1 <= s <= 2 for s in outcome_slots)
