"""Non-live unit tests for eval concurrency: async per-item producer, the
``--concurrency`` optional-value resolver, deterministic re-sort, unified
progress wiring, and infra fail-fast. All paths mock ``run_live_async`` — no
live SDK required.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

from ai_rules.rule_loader_eval.agent_runner import AgentRun
from ai_rules.rule_loader_eval.fixtures import Fixture, TriggerEvidence

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_run(fixture_id: str = "fx") -> AgentRun:
    return AgentRun(
        fixture_id=fixture_id,
        loaded=("rules/999-test-core.md",),
        loaded_via_reads=("rules/999-test-core.md",),
        loaded_via_reads_performed=("rules/999-test-core.md",),
        loaded_via_section=("rules/999-test-core.md",),
        disagreements=(),
        turns=3,
        duration_ms=500,
        model="claude-test",
        notes=(),
    )


def _make_fixture(fixture_id: str = "fx") -> Fixture:
    return Fixture(
        path=Path(f"fixtures/{fixture_id}.yaml"),
        schema_version=1,
        updated="2025-01-01",
        id=fixture_id,
        description="",
        variant="",
        prompt=f"Test prompt for {fixture_id}",
        required=("rules/999-test-core.md",),
        dependencies=(),
        forbidden=(),
        optional=(),
        trigger_evidence=TriggerEvidence(),
    )


def _fake_async(run: AgentRun):
    async def _inner(*args: object, **kwargs: object) -> AgentRun:
        return run

    return _inner


# ---------------------------------------------------------------------------
# Phase 3: run_fixture_async parity with sync run_fixture
# ---------------------------------------------------------------------------


def test_run_fixture_async_matches_sync() -> None:
    """run_fixture_async produces an identical RunResult to run_fixture for the
    same underlying AgentRun and rules metadata.
    """
    from ai_rules.rule_loader_eval import engine

    fixture = _make_fixture()
    run = _make_run()
    rules_meta: dict = {}

    with patch.object(engine, "run_live", return_value=run):
        sync_result = engine.run_fixture(fixture, project_root=Path("."), rules_meta=rules_meta)

    with patch.object(engine, "run_live_async", side_effect=_fake_async(run)):
        async_result = asyncio.run(
            engine.run_fixture_async(fixture, project_root=Path("."), rules_meta=rules_meta)
        )

    assert async_result.fixture_id == sync_result.fixture_id
    assert async_result.run == sync_result.run
    assert async_result.match == sync_result.match
    assert async_result.signal_report == sync_result.signal_report
    assert async_result.citation_drifts == sync_result.citation_drifts
    assert async_result.depends_violations == sync_result.depends_violations
    assert async_result.passed == sync_result.passed


# ---------------------------------------------------------------------------
# Shared helpers for _run_single_eval-level tests
# ---------------------------------------------------------------------------


def _pass_run(fixture_id: str) -> AgentRun:
    """An AgentRun that satisfies the minimal fixture (required rule loaded)."""
    loaded = ("rules/999-test-core.md",)
    return AgentRun(
        fixture_id=fixture_id,
        loaded=loaded,
        loaded_via_reads=loaded,
        loaded_via_reads_performed=(),
        loaded_via_section=loaded,
        disagreements=(),
        turns=1,
        duration_ms=10,
        model="claude-test",
        notes=(),
        input_tokens=100,
        output_tokens=10,
        total_cost_usd=0.001,
    )


def _run_eval(fixtures, *, concurrency, out_dir=None, dispatch=None):
    """Invoke _run_single_eval with run_live_async + rules metadata mocked."""
    from pathlib import Path

    from ai_rules.commands import rule_loader as rl

    async def _default_async(fixture_id, prompt, **kwargs):
        return _pass_run(fixture_id)

    async def _dispatch_async(fixture_id, prompt, **kwargs):
        assert dispatch is not None
        delay, run = dispatch(fixture_id)
        if delay:
            await asyncio.sleep(delay)
        return run

    impl = _dispatch_async if dispatch is not None else _default_async

    with (
        patch("ai_rules.rule_loader_eval.engine.run_live_async", new=impl),
        patch.object(rl, "load_rules_metadata", return_value={}),
    ):
        return rl._run_single_eval(
            fixtures=list(fixtures),
            root=Path("."),
            resolved_connection="test-conn",
            strict_forbidden=False,
            max_turns=3,
            effort="low",
            model="auto",
            debug=False,
            out_dir=out_dir,
            label="test",
            concurrency=concurrency,
        )


# ---------------------------------------------------------------------------
# Phase 5: determinism — re-sort to input order; parallel == sequential
# ---------------------------------------------------------------------------


def test_parallel_results_resorted_to_input_order() -> None:
    """Completion order is scrambled by inverse delays; results stay input-ordered."""
    fixtures = [_make_fixture(f"fx{i}") for i in range(5)]

    def dispatch(fid: str):
        idx = int(fid[2:])
        return ((5 - idx) * 0.01, _pass_run(fid))  # later fixtures finish first

    results = _run_eval(fixtures, concurrency=5, dispatch=dispatch)[0]
    assert [r.fixture_id for r in results] == [f"fx{i}" for i in range(5)]


def test_parallel_output_equals_sequential() -> None:
    """N=4 produces the same (fixture_id, passed) sequence as N=1."""
    fixtures = [_make_fixture(f"fx{i}") for i in range(6)]

    seq = _run_eval(fixtures, concurrency=1)[0]
    par = _run_eval(fixtures, concurrency=4)[0]

    assert [(r.fixture_id, r.passed) for r in seq] == [(r.fixture_id, r.passed) for r in par]
    # Sanity: the mocked runs all pass.
    assert all(r.passed for r in seq)


# ---------------------------------------------------------------------------
# Phase 3 (plain-log): per-fixture start/finish lines emitted for every N
# ---------------------------------------------------------------------------


def test_plain_log_start_and_finish_lines_emitted_all_concurrency() -> None:
    """_log_item_start/_log_item_finish fire for every fixture regardless of N."""
    from pathlib import Path

    from ai_rules.commands import rule_loader as rl

    def _run_for(n: int) -> tuple[list[str], list[str]]:
        started: list[str] = []
        finished: list[str] = []

        fixtures = [_make_fixture(f"fx{i}") for i in range(3)]

        async def _async(fixture_id, prompt, **kwargs):
            return _pass_run(fixture_id)

        with (
            patch("ai_rules.rule_loader_eval.engine.run_live_async", new=_async),
            patch.object(rl, "load_rules_metadata", return_value={}),
            patch.object(rl, "_log_item_start", side_effect=started.append),
            patch.object(
                rl,
                "_log_item_finish",
                side_effect=lambda fid, **kw: finished.append(fid),
            ),
        ):
            rl._run_single_eval(
                fixtures=fixtures,
                root=Path("."),
                resolved_connection="c",
                strict_forbidden=False,
                max_turns=3,
                effort="low",
                model="auto",
                debug=False,
                out_dir=None,
                label="t",
                concurrency=n,
            )
        return started, finished

    for n in (1, 3):
        started, finished = _run_for(n)
        assert set(started) == {"fx0", "fx1", "fx2"}
        assert set(finished) == {"fx0", "fx1", "fx2"}


# ---------------------------------------------------------------------------
# Phase 7: infra fail-fast
# ---------------------------------------------------------------------------


def test_infra_failfast_aborts_skips_snapshot_and_diagnoses(tmp_path) -> None:
    """An InfraError (before any RunResult) aborts: infra row returned, no snapshot,
    cancelled/queued fixtures never appear as fixture-fail rows, is_infra True.
    """
    fixtures = [_make_fixture(f"fx{i}") for i in range(5)]

    def dispatch(fid: str):
        if fid == "fx0":
            run = _pass_run(fid)
            # Mark as infra: run_fixture_async raises InfraError for this run.
            object.__setattr__(run, "is_infra_error", True)
            object.__setattr__(run, "infra_error_detail", "sdk down")
            return (0.0, run)
        return (0.1, _pass_run(fid))  # keep peers in-flight/queued

    results, is_infra = _run_eval(
        fixtures, concurrency=2, out_dir=tmp_path / "snap", dispatch=dispatch
    )

    assert is_infra is True
    # The aborting fixture is present as an infra row.
    infra_rows = [r for r in results if getattr(r.run, "is_infra_error", False)]
    assert [r.fixture_id for r in infra_rows] == ["fx0"]
    # No non-infra FAIL rows: cancelled/queued fixtures are diagnostics only.
    assert all(r.fixture_id == "fx0" for r in results)
    # Snapshot must NOT be written on infra fail-fast.
    assert not (tmp_path / "snap").exists() or not any((tmp_path / "snap").iterdir())


# ---------------------------------------------------------------------------
# Phase 4: --concurrency flag guard
# ---------------------------------------------------------------------------


def test_eval_concurrency_zero_exits_fixture_invalid() -> None:
    """`eval --concurrency 0` exits EXIT_FIXTURE_INVALID before any SDK work."""
    from typer.testing import CliRunner

    from ai_rules.cli import app
    from ai_rules.commands.rule_loader import EXIT_FIXTURE_INVALID

    result = CliRunner().invoke(app, ["rule-loader", "eval", "--concurrency", "0"])
    assert result.exit_code == EXIT_FIXTURE_INVALID


def test_eval_concurrency_value_threaded_to_run_single_eval() -> None:
    """Omitted -> 1 and `--concurrency 4` -> 4 reach _run_single_eval."""
    from unittest.mock import patch

    from typer.testing import CliRunner

    from ai_rules.cli import app

    captured: list[int] = []

    def _fake_single(*args, **kwargs):
        captured.append(kwargs["concurrency"])
        return ([], False)

    for argv, expected in (
        (["rule-loader", "eval", "--runs", "1"], 1),
        (["rule-loader", "eval", "--runs", "1", "--concurrency", "4"], 4),
    ):
        captured.clear()
        with (
            patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
            patch("ai_rules.commands.rule_loader._require_connection_or_exit", return_value="c"),
            patch(
                "ai_rules.commands.rule_loader.load_fixtures", return_value=[_make_fixture("fx")]
            ),
            patch("ai_rules.commands.rule_loader.load_rules_metadata", return_value={}),
            patch("ai_rules.commands.rule_loader._run_single_eval", side_effect=_fake_single),
        ):
            result = CliRunner().invoke(app, argv)
        assert result.exit_code == 0, result.output
        assert captured == [expected]
