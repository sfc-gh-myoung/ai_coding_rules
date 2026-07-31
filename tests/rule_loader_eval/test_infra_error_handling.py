"""Tests for v3.15 infra-error handling: classifier, resolver, fail-fast, snapshot."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from ai_rules.commands.rule_loader import (
    EXIT_INFRA_ERROR,
    _require_connection_or_exit,
    _resolve_connection,
    _write_aggregate_and_finalize,
)
from ai_rules.rule_loader_eval.agent_runner import AgentRun, _classify_infra
from ai_rules.rule_loader_eval.diagnostics import SignalReport
from ai_rules.rule_loader_eval.engine import InfraError, RunResult, _synthetic_failure
from ai_rules.rule_loader_eval.fixtures import Fixture
from ai_rules.rule_loader_eval.matcher import MatchResult
from ai_rules.rule_loader_eval.results_writer import ResultsRunWriter, make_run_context
from ai_rules.rule_loader_eval.snapshot import FixtureSnapshot

# ---------------------------------------------------------------------------
# _classify_infra
# ---------------------------------------------------------------------------


def test_classify_infra_stop_reason_error_during_execution():
    is_infra, detail = _classify_infra(
        stop_reason="error_during_execution",
        turns=0,
        duration_ms=2000,
        reads_set=set(),
        saw_result_message=True,
    )
    assert is_infra is True
    assert "error_during_execution" in detail


def test_classify_infra_no_result_message():
    is_infra, detail = _classify_infra(
        stop_reason="",
        turns=0,
        duration_ms=10_000,
        reads_set={"rules/999-test-core.md"},
        saw_result_message=False,
    )
    assert is_infra is True
    assert "ResultMessage" in detail


def test_classify_infra_zero_turns_short_duration():
    is_infra, detail = _classify_infra(
        stop_reason="success",
        turns=0,
        duration_ms=1500,
        reads_set=set(),
        saw_result_message=True,
    )
    assert is_infra is True
    assert "zero turns" in detail


def test_classify_infra_zero_turns_no_reads():
    is_infra, detail = _classify_infra(
        stop_reason="success",
        turns=0,
        duration_ms=8000,
        reads_set=set(),
        saw_result_message=True,
    )
    assert is_infra is True
    assert "zero turns and zero reads" in detail


def test_classify_infra_healthy_run():
    is_infra, detail = _classify_infra(
        stop_reason="success",
        turns=4,
        duration_ms=38_000,
        reads_set={"rules/999-test-core.md", "rules/119-snowflake-warehouse-management.md"},
        saw_result_message=True,
    )
    assert is_infra is False
    assert detail == ""


def test_classify_infra_transport_error_wins_over_healthy_signals():
    """A transport error is infra even when every other signal looks healthy.

    Regression guard: transport/SDK exceptions were previously converted to a
    synthetic FAIL row scored as a rule-discovery failure, which understated
    pass rates and bypassed --retry-infra.
    """
    is_infra, detail = _classify_infra(
        stop_reason="success",
        turns=4,
        duration_ms=38_000,
        reads_set={"rules/999-test-core.md"},
        saw_result_message=True,
        transport_error="ConnectionResetError: peer closed connection",
    )
    assert is_infra is True
    assert "transport" in detail.lower()
    assert "ConnectionResetError" in detail


def test_classify_infra_transport_error_empty_string_is_not_infra():
    """Empty transport_error must not trip the check (default arg safety)."""
    is_infra, detail = _classify_infra(
        stop_reason="success",
        turns=4,
        duration_ms=38_000,
        reads_set={"rules/999-test-core.md"},
        saw_result_message=True,
        transport_error="",
    )
    assert is_infra is False
    assert detail == ""


def test_classify_infra_transport_error_defaults_to_absent():
    """transport_error is optional -- existing callers keep working unchanged."""
    is_infra, _ = _classify_infra(
        stop_reason="success",
        turns=4,
        duration_ms=38_000,
        reads_set={"rules/999-test-core.md"},
        saw_result_message=True,
    )
    assert is_infra is False


# ---------------------------------------------------------------------------
# _resolve_connection / _require_connection_or_exit
# ---------------------------------------------------------------------------


def test_resolve_connection_explicit_arg_wins():
    with patch.dict(os.environ, {"SNOWFLAKE_CONNECTION_NAME": "envdef"}, clear=False):
        assert _resolve_connection("explicit") == "explicit"


def test_resolve_connection_env_fallback():
    with patch.dict(os.environ, {"SNOWFLAKE_CONNECTION_NAME": "envdef"}, clear=False):
        assert _resolve_connection(None) == "envdef"


def test_resolve_connection_neither_returns_none():
    env_no_conn = {k: v for k, v in os.environ.items() if k != "SNOWFLAKE_CONNECTION_NAME"}
    with patch.dict(os.environ, env_no_conn, clear=True):
        assert _resolve_connection(None) is None


def test_require_connection_exits_when_unset():
    env_no_conn = {k: v for k, v in os.environ.items() if k != "SNOWFLAKE_CONNECTION_NAME"}
    with patch.dict(os.environ, env_no_conn, clear=True):
        with pytest.raises(typer.Exit) as exc_info:
            _require_connection_or_exit(None)
        assert exc_info.value.exit_code == EXIT_INFRA_ERROR


def test_require_connection_returns_resolved():
    with patch.dict(os.environ, {"SNOWFLAKE_CONNECTION_NAME": "envdef"}, clear=False):
        assert _require_connection_or_exit(None) == "envdef"
        assert _require_connection_or_exit("explicit") == "explicit"


# ---------------------------------------------------------------------------
# _synthetic_failure(infra=True)
# ---------------------------------------------------------------------------


def test_synthetic_failure_infra_marker():
    fx = Fixture(
        path=None,
        schema_version=3,
        updated="2026-05-19",
        id="test",
        description="",
        variant="simple",
        prompt="hello",
        required=("rules/999-test-core.md",),
        dependencies=(),
        forbidden=(),
        optional=(),
        trigger_evidence={},
    )
    err = RuntimeError("SDK unavailable")
    result = _synthetic_failure(fx, err, infra=True)
    assert result.run.is_infra_error is True
    assert "SDK unavailable" in result.run.infra_error_detail
    assert any("INFRA ERROR" in note for note in result.run.notes)
    assert result.passed is False


def test_synthetic_failure_non_infra_no_marker():
    fx = Fixture(
        path=None,
        schema_version=3,
        updated="2026-05-19",
        id="test",
        description="",
        variant="simple",
        prompt="hello",
        required=("rules/999-test-core.md",),
        dependencies=(),
        forbidden=(),
        optional=(),
        trigger_evidence={},
    )
    err = ValueError("regular failure")
    result = _synthetic_failure(fx, err)
    assert result.run.is_infra_error is False
    assert result.run.infra_error_detail == ""


def test_infra_error_is_runtime_error():
    """InfraError is RuntimeError subclass for backward-compat with existing.

    `except RuntimeError` blocks.
    """
    assert issubclass(InfraError, RuntimeError)


# ---------------------------------------------------------------------------
# Snapshot persistence
# ---------------------------------------------------------------------------


def test_snapshot_round_trip_infra_fields():
    fs = FixtureSnapshot(
        fixture_id="t",
        passed=False,
        loaded=(),
        expected_required=(),
        expected_dependencies=(),
        expected_optional=(),
        expected_forbidden=(),
        missing_required=(),
        missing_dependencies=(),
        forbidden_present=(),
        signal_disagreements=0,
        citation_drifts=0,
        turns=0,
        duration_ms=0,
        is_infra_error=True,
        infra_error_detail="model unavailable",
    )
    d = fs.to_dict()
    assert d["is_infra_error"] is True
    assert d["infra_error_detail"] == "model unavailable"
    fs2 = FixtureSnapshot.from_dict(d)
    assert fs2.is_infra_error is True
    assert fs2.infra_error_detail == "model unavailable"


def test_snapshot_backward_compat_missing_fields():
    """Old snapshots without the v3.15 fields default to False/empty."""
    fs = FixtureSnapshot.from_dict(
        {
            "fixture_id": "t",
            "passed": True,
            "loaded": [],
            "expected_required": [],
            "expected_dependencies": [],
            "expected_optional": [],
            "expected_forbidden": [],
            "missing_required": [],
            "missing_dependencies": [],
            "forbidden_present": [],
            "signal_disagreements": 0,
            "citation_drifts": 0,
            "turns": 0,
            "duration_ms": 0,
        }
    )
    assert fs.is_infra_error is False
    assert fs.infra_error_detail == ""


# ---------------------------------------------------------------------------
# _write_aggregate_and_finalize — early-abort runs count
# ---------------------------------------------------------------------------


def _make_minimal_run_result(fixture_id: str) -> RunResult:
    run = AgentRun(
        fixture_id=fixture_id,
        loaded=("rules/000-global-core.md",),
        loaded_via_reads=("rules/000-global-core.md",),
        loaded_via_reads_performed=(),
        loaded_via_section=("rules/000-global-core.md",),
    )
    match = MatchResult(
        missing_required=(),
        missing_dependencies=(),
        forbidden_present=(),
        optional_loaded=(),
        passed=True,
    )
    return RunResult(
        fixture_id=fixture_id,
        run=run,
        match=match,
        signal_report=SignalReport(ok=True, disagreements=()),
    )


def _make_results_run_writer(tmp_path: pytest.TempPathFactory) -> ResultsRunWriter:
    ctx = make_run_context(
        model_requested="test-model",
        effort="medium",
        max_turns=10,
        strict_forbidden=False,
        concurrency=1,
        runs_requested=3,
        label=None,
        connection="default",
        ai_rules_version="test",
        fixture_selection=("fx-test",),
        fixture_count=1,
        run_id="test-run-id-aabbcc",
    )
    return ResultsRunWriter(root=tmp_path, run_dir_name="test-run", context=ctx)


def test_aggregator_early_abort_runs_count(tmp_path):
    """summary.json["runs"] must equal len(all_run_results) on early-abort path.

    Regression guard: calling with runs=3 (the buggy value) writes runs=3.
    Fixed path: calling with len(all_run_results)=1 writes runs=1.
    """
    fixture_id = "fx-test"
    completed_pass = [_make_minimal_run_result(fixture_id)]
    all_run_results = [completed_pass]  # 1 pass completed out of 3 configured

    # --- Fixed path: pass len(all_run_results) ---
    writer_fixed = _make_results_run_writer(tmp_path / "fixed")
    _write_aggregate_and_finalize(
        writer_fixed, all_run_results, len(all_run_results), status="failed"
    )
    summary_fixed = json.loads((tmp_path / "fixed" / "test-run" / "summary.json").read_text())
    assert summary_fixed["runs"] == 1, "Fixed path: runs should equal completed pass count"
    assert summary_fixed["per_fixture"][fixture_id]["n_runs"] == 1

    # --- Regression guard: original buggy value runs=3 ---
    writer_buggy = _make_results_run_writer(tmp_path / "buggy")
    _write_aggregate_and_finalize(writer_buggy, all_run_results, 3, status="failed")
    summary_buggy = json.loads((tmp_path / "buggy" / "test-run" / "summary.json").read_text())
    assert summary_buggy["runs"] == 3, "Regression guard: passing runs=3 must still write runs=3"
    # per_fixture n_runs is always correct regardless of the top-level runs field
    assert summary_buggy["per_fixture"][fixture_id]["n_runs"] == 1


# ---------------------------------------------------------------------------
# --retry-infra: retry on InfraError with timing exclusion
# ---------------------------------------------------------------------------


def _make_fixture(fixture_id: str) -> Fixture:
    """Helper to build a minimal Fixture for retry tests."""
    return Fixture(
        path=None,
        schema_version=3,
        updated="2026-07-18",
        id=fixture_id,
        description="",
        variant="simple",
        prompt="test prompt",
        required=("rules/000-global-core.md",),
        dependencies=(),
        forbidden=(),
        optional=(),
        trigger_evidence={},
    )


def test_retry_infra_retries_then_succeeds():
    """When retry_infra > 1, a transient InfraError is retried and the fixture passes."""
    from ai_rules.commands.rule_loader import _run_single_eval
    from ai_rules.rule_loader_eval.engine import InfraError, RunResult

    fixture = _make_fixture("test-retry")

    call_count = 0

    # Mock run_fixture_async to fail on first call, succeed on second
    async def mock_run_fixture_async(fixture, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise InfraError("SDK reported stop_reason='error_during_execution'")
        # Return a passing RunResult
        run = AgentRun(
            fixture_id=fixture.id,
            loaded=("rules/000-global-core.md",),
            loaded_via_reads=("rules/000-global-core.md",),
            loaded_via_reads_performed=(),
            loaded_via_section=("rules/000-global-core.md",),
            disagreements=(),
            turns=3,
            duration_ms=5000,
            model="test-model",
        )
        match = MatchResult(
            missing_required=(),
            missing_dependencies=(),
            forbidden_present=(),
            optional_loaded=(),
            extras=(),
            passed=True,
            warnings=(),
        )
        return RunResult(
            fixture_id=fixture.id,
            run=run,
            match=match,
            signal_report=SignalReport(ok=True, disagreements=()),
            citation_drifts=(),
        )

    with (
        patch("ai_rules.rule_loader_eval.engine.run_fixture_async", mock_run_fixture_async),
        patch("ai_rules.commands.rule_loader.load_rules_metadata", return_value={}),
        patch(
            "ai_rules.rule_loader_eval.agent_runner.build_prompt", return_value="mock system prompt"
        ),
        patch("asyncio.sleep", return_value=None),
    ):
        _results, is_infra = _run_single_eval(
            fixtures=[fixture],
            root=Path("/fake"),
            resolved_connection="test",
            strict_forbidden=False,
            max_turns=10,
            effort="medium",
            model="auto",
            debug=False,
            out_dir=None,
            label="",
            concurrency=1,
            retry_infra=2,
        )

    assert call_count == 2, "Should have been called twice (1 failure + 1 success)"
    assert is_infra is False, "Should not be infra error after successful retry"
    assert len(_results) == 1
    assert _results[0].passed is True


def test_retry_infra_exhausted_triggers_failfast():
    """When all retries exhausted, InfraError propagates and triggers fail-fast."""
    from ai_rules.commands.rule_loader import _run_single_eval
    from ai_rules.rule_loader_eval.engine import InfraError

    fixture = _make_fixture("test-retry-fail")

    call_count = 0

    async def mock_run_fixture_async(fixture, **kwargs):
        nonlocal call_count
        call_count += 1
        raise InfraError("SDK reported stop_reason='error_during_execution'")

    with (
        patch("ai_rules.rule_loader_eval.engine.run_fixture_async", mock_run_fixture_async),
        patch("ai_rules.commands.rule_loader.load_rules_metadata", return_value={}),
        patch(
            "ai_rules.rule_loader_eval.agent_runner.build_prompt", return_value="mock system prompt"
        ),
        patch("asyncio.sleep", return_value=None),
    ):
        _results, is_infra = _run_single_eval(
            fixtures=[fixture],
            root=Path("/fake"),
            resolved_connection="test",
            strict_forbidden=False,
            max_turns=10,
            effort="medium",
            model="auto",
            debug=False,
            out_dir=None,
            label="",
            concurrency=1,
            retry_infra=2,
        )

    assert call_count == 2, "Should have tried twice before giving up"
    assert is_infra is True, "Should signal infra error after exhausting retries"


def test_retry_infra_default_no_retry():
    """With default retry_infra=1, first InfraError triggers immediate fail-fast."""
    from ai_rules.commands.rule_loader import _run_single_eval
    from ai_rules.rule_loader_eval.engine import InfraError

    fixture = _make_fixture("test-no-retry")

    call_count = 0

    async def mock_run_fixture_async(fixture, **kwargs):
        nonlocal call_count
        call_count += 1
        raise InfraError("SDK reported stop_reason='error_during_execution'")

    with (
        patch("ai_rules.rule_loader_eval.engine.run_fixture_async", mock_run_fixture_async),
        patch("ai_rules.commands.rule_loader.load_rules_metadata", return_value={}),
        patch(
            "ai_rules.rule_loader_eval.agent_runner.build_prompt", return_value="mock system prompt"
        ),
    ):
        _results, is_infra = _run_single_eval(
            fixtures=[fixture],
            root=Path("/fake"),
            resolved_connection="test",
            strict_forbidden=False,
            max_turns=10,
            effort="medium",
            model="auto",
            debug=False,
            out_dir=None,
            label="",
            concurrency=1,
            retry_infra=1,
        )

    assert call_count == 1, "Should only try once with retry_infra=1"
    assert is_infra is True


# ---------------------------------------------------------------------------
# run_live_async transport-error containment (Option B regression guards)
# ---------------------------------------------------------------------------


def test_run_live_async_converts_transport_exception_to_infra_flag(monkeypatch):
    """A raising SDK stream must yield an infra-flagged AgentRun, not propagate.

    Before this fix the exception escaped run_live_async, was caught by
    concurrency.py, and became a synthetic FAIL row scored as a rule-discovery
    failure with zeroed metrics and an unfiltered missing_required list.
    """
    import asyncio

    import ai_rules.rule_loader_eval.agent_runner as ar

    def _boom(*_args, **_kwargs):
        async def _gen():
            raise ConnectionResetError("peer closed connection")
            yield  # pragma: no cover — makes this an async generator

        return _gen()

    fake_sdk = type(
        "FakeSDK",
        (),
        {
            "AssistantMessage": type("AM", (), {"content": ()}),
            "ResultMessage": type("RM", (), {"stop_reason": "success"}),
            "CortexCodeAgentOptions": lambda **kw: object(),
            "HookMatcher": lambda **kw: object(),
            "query": staticmethod(_boom),
        },
    )
    monkeypatch.setitem(sys.modules, "cortex_code_agent_sdk", fake_sdk)

    run = asyncio.run(
        ar.run_live_async(
            "fx-transport",
            "prompt",
            project_root=Path("/fake"),
            max_turns=5,
            effort="medium",
            model="auto",
            connection=None,
        )
    )

    assert run.is_infra_error is True, "transport exception must be flagged as infra"
    assert "ConnectionResetError" in run.infra_error_detail
    assert any("transport error" in n for n in run.notes)


def test_build_run_result_raises_infra_error_for_transport_flagged_run():
    """_build_run_result must convert an infra-flagged run into InfraError.

    This is the seam that makes --retry-infra and fail-fast abort work. Together
    with the run_live_async change it closes the phantom-record path end to end.
    """
    from ai_rules.rule_loader_eval.engine import _build_run_result

    run = AgentRun(
        fixture_id="fx-transport",
        loaded=(),
        loaded_via_reads=(),
        loaded_via_reads_performed=(),
        loaded_via_section=(),
        is_infra_error=True,
        infra_error_detail="SDK transport failure: ConnectionResetError: boom",
    )

    with pytest.raises(InfraError) as excinfo:
        _build_run_result(_make_fixture("fx-transport"), run, {}, strict_forbidden=False)

    assert "ConnectionResetError" in str(excinfo.value)


def _fake_sdk_raising(exc_factory):
    """Build a fake cortex_code_agent_sdk whose query() stream raises."""

    def _q(*_args, **_kwargs):
        async def _gen():
            raise exc_factory()
            yield  # pragma: no cover — makes this an async generator

        return _gen()

    return type(
        "FakeSDK",
        (),
        {
            "AssistantMessage": type("AM", (), {"content": ()}),
            "ResultMessage": type("RM", (), {"stop_reason": "success"}),
            "CortexCodeAgentOptions": lambda **kw: object(),
            "HookMatcher": lambda **kw: object(),
            "query": staticmethod(_q),
        },
    )


def test_run_live_async_reraises_programming_errors(monkeypatch):
    """A defect in our own loop handling must NOT be laundered into infra.

    Consensus finding (skeptic D3): a bare `except Exception` would convert an
    AttributeError into an infra retry, masking a real bug behind two 30s sleeps
    and an abort attributed to infrastructure.
    """
    import asyncio

    import ai_rules.rule_loader_eval.agent_runner as ar

    monkeypatch.setitem(
        sys.modules,
        "cortex_code_agent_sdk",
        _fake_sdk_raising(lambda: AttributeError("'NoneType' has no attribute 'content'")),
    )

    with pytest.raises(AttributeError):
        asyncio.run(
            ar.run_live_async(
                "fx-bug",
                "prompt",
                project_root=Path("/fake"),
                max_turns=5,
                effort="medium",
                model="auto",
                connection=None,
            )
        )


def test_run_live_async_exception_group_of_ordinary_errors_is_infra(monkeypatch):
    """TaskGroup (anyio) wraps failures in ExceptionGroup, which is an Exception.

    A group carrying only ordinary errors must be classified as infra rather
    than escaping into the phantom-record path.
    """
    import asyncio

    import ai_rules.rule_loader_eval.agent_runner as ar

    monkeypatch.setitem(
        sys.modules,
        "cortex_code_agent_sdk",
        _fake_sdk_raising(lambda: ExceptionGroup("tg", [OSError("broken pipe")])),
    )

    run = asyncio.run(
        ar.run_live_async(
            "fx-group",
            "prompt",
            project_root=Path("/fake"),
            max_turns=5,
            effort="medium",
            model="auto",
            connection=None,
        )
    )
    assert run.is_infra_error is True
    assert "ExceptionGroup" in run.infra_error_detail


def test_synthetic_failure_filters_foundation_rule_from_missing_required():
    """Consensus finding: the raw missing_required list was the phantom fingerprint.

    _build_run_result filters _FOUNDATION_RULE (engine.py) because the
    micro-kernel replaces it. _synthetic_failure must filter identically, or a
    synthetic row is falsely distinguishable as a discovery failure that missed
    the foundation.
    """
    fx = _make_fixture("fx-filter")
    assert "rules/000-global-core.md" in fx.required, "precondition: fixture requires foundation"

    rr = _synthetic_failure(fx, RuntimeError("boom"), infra=False)

    assert "rules/000-global-core.md" not in rr.match.missing_required


def test_transport_failure_does_not_produce_scored_discovery_fail(monkeypatch, tmp_path):
    """FULL-CHAIN guard: SDK raise -> infra flag -> InfraError -> abort, not a scored FAIL.

    This is the end-to-end assertion both reviewers flagged as missing. It
    stitches run_live_async -> _build_run_result -> InfraError so a regression at
    any single seam is caught here.
    """
    import asyncio

    import ai_rules.rule_loader_eval.agent_runner as ar
    from ai_rules.rule_loader_eval.engine import _build_run_result

    monkeypatch.setitem(
        sys.modules,
        "cortex_code_agent_sdk",
        _fake_sdk_raising(lambda: ConnectionResetError("peer closed connection")),
    )

    run = asyncio.run(
        ar.run_live_async(
            "fx-chain",
            "prompt",
            project_root=tmp_path,
            max_turns=5,
            effort="medium",
            model="auto",
            connection=None,
        )
    )

    # Seam 1: run_live_async contained the exception and flagged it.
    assert run.is_infra_error is True

    # Seam 2: _build_run_result refuses to score it and raises InfraError, which
    # is what --retry-infra and should_abort_exception both discriminate on.
    with pytest.raises(InfraError):
        _build_run_result(_make_fixture("fx-chain"), run, {}, strict_forbidden=False)
