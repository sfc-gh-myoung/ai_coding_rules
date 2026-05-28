"""Tests for v3.15 infra-error handling: classifier, resolver, fail-fast, snapshot."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
import typer

from ai_rules.commands.rule_loader import (
    EXIT_INFRA_ERROR,
    _require_connection_or_exit,
    _resolve_connection,
)
from ai_rules.rule_loader_eval.agent_runner import _classify_infra
from ai_rules.rule_loader_eval.engine import InfraError, _synthetic_failure
from ai_rules.rule_loader_eval.fixtures import Fixture
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
