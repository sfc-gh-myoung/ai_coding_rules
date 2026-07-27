"""Non-live unit tests for rule_loader_eval/engine.py.

Covers: RunResult dataclass + passed property, InfraError, _synthetic_failure,
        _build_run_result progressive mode (000-global-core.md exclusion).
Skips: run_fixture / run_fixtures (lines 70-110, 162-199) — live SDK paths.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.agent_runner import AgentRun
from ai_rules.rule_loader_eval.diagnostics import SignalReport
from ai_rules.rule_loader_eval.engine import (
    InfraError,
    RunResult,
    _build_run_result,
    _synthetic_failure,
)
from ai_rules.rule_loader_eval.fixtures import Fixture, TriggerEvidence
from ai_rules.rule_loader_eval.matcher import MatchResult

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


def _make_match(*, passed: bool = True) -> MatchResult:
    return MatchResult(
        missing_required=() if passed else ("rules/X.md",),
        missing_dependencies=(),
        forbidden_present=(),
        optional_loaded=(),
        extras=(),
        passed=passed,
        warnings=(),
    )


def _make_signal(*, ok: bool = True) -> SignalReport:
    return SignalReport(ok=ok, disagreements=())


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


# ---------------------------------------------------------------------------
# RunResult dataclass construction and passed property
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_run_result_all_pass() -> None:
    result = RunResult(
        fixture_id="fx",
        run=_make_run(),
        match=_make_match(passed=True),
        signal_report=_make_signal(ok=True),
        citation_drifts=(),
        depends_violations=(),
    )
    assert result.fixture_id == "fx"
    assert result.passed is True


@pytest.mark.unit
def test_run_result_fails_when_match_fails() -> None:
    result = RunResult(
        fixture_id="fx",
        run=_make_run(),
        match=_make_match(passed=False),
        signal_report=_make_signal(ok=True),
        citation_drifts=(),
        depends_violations=(),
    )
    assert result.passed is False


@pytest.mark.unit
def test_run_result_fails_when_signal_fails() -> None:
    result = RunResult(
        fixture_id="fx",
        run=_make_run(),
        match=_make_match(passed=True),
        signal_report=_make_signal(ok=False),
        citation_drifts=(),
        depends_violations=(),
    )
    assert result.passed is False


@pytest.mark.unit
def test_run_result_fails_when_citation_drifts_present() -> None:
    from ai_rules.rule_loader_eval.matcher import CitationDrift

    drift = CitationDrift(
        rule_path="rules/999.md",
        field="line_count",
        declared="100",
        actual="200",
        section="Rules Loaded",
    )
    result = RunResult(
        fixture_id="fx",
        run=_make_run(),
        match=_make_match(passed=True),
        signal_report=_make_signal(ok=True),
        citation_drifts=(drift,),
        depends_violations=(),
    )
    assert result.passed is False


@pytest.mark.unit
def test_run_result_fails_when_output_violations() -> None:
    run_with_violation = AgentRun(
        fixture_id="fx",
        loaded=(),
        loaded_via_reads=(),
        loaded_via_reads_performed=(),
        loaded_via_section=(),
        disagreements=(),
        turns=1,
        duration_ms=10,
        model="test",
        notes=(),
        output_violations=("missing PRE-FLIGHT header",),
    )
    result = RunResult(
        fixture_id="fx",
        run=run_with_violation,
        match=_make_match(passed=True),
        signal_report=_make_signal(ok=True),
        citation_drifts=(),
        depends_violations=(),
    )
    assert result.passed is False


@pytest.mark.unit
def test_run_result_passes_when_depends_violations_present() -> None:
    """R8 violations are reported via depends_ok but do NOT gate pass/fail (Phase 1 decouple)."""
    from ai_rules.rule_loader_eval.depends_validator import DependsViolation

    violation = DependsViolation(parent="rules/A.md", missing_dep="rules/B.md")
    result = RunResult(
        fixture_id="fx",
        run=_make_run(),
        match=_make_match(passed=True),
        signal_report=_make_signal(ok=True),
        citation_drifts=(),
        depends_violations=(violation,),
    )
    assert result.passed is True
    assert result.depends_ok is False


@pytest.mark.unit
def test_run_result_is_frozen() -> None:
    result = RunResult(
        fixture_id="fx",
        run=_make_run(),
        match=_make_match(passed=True),
        signal_report=_make_signal(ok=True),
    )
    with pytest.raises((AttributeError, TypeError)):
        result.fixture_id = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# InfraError
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_infra_error_is_runtime_error() -> None:
    err = InfraError("agent SDK unavailable")
    assert isinstance(err, RuntimeError)
    assert "agent SDK unavailable" in str(err)


@pytest.mark.unit
def test_infra_error_can_be_raised_and_caught() -> None:
    with pytest.raises(InfraError, match="connection refused"):
        raise InfraError("connection refused")


# ---------------------------------------------------------------------------
# _synthetic_failure — non-infra path
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_synthetic_failure_non_infra() -> None:
    fixture = _make_fixture("my-test")
    exc = ValueError("something went wrong")
    result = _synthetic_failure(fixture, exc, infra=False)
    assert result.fixture_id == "my-test"
    assert result.passed is False
    assert result.run.is_infra_error is False
    assert "runtime error" in result.run.notes[0]
    assert "ValueError" in result.run.notes[0]
    assert "something went wrong" in result.run.notes[0]


@pytest.mark.unit
def test_synthetic_failure_non_infra_match_has_missing_required() -> None:
    fixture = _make_fixture("check-required")
    exc = RuntimeError("boom")
    result = _synthetic_failure(fixture, exc, infra=False)
    # required rules should appear in missing_required
    assert "rules/999-test-core.md" in result.match.missing_required
    assert result.match.passed is False


@pytest.mark.unit
def test_synthetic_failure_non_infra_zeros_timing() -> None:
    fixture = _make_fixture("fx")
    exc = TimeoutError("timed out")
    result = _synthetic_failure(fixture, exc)
    assert result.run.turns == 0
    assert result.run.duration_ms == 0
    assert result.run.model == "error"


@pytest.mark.unit
def test_synthetic_failure_non_infra_signal_report_not_ok() -> None:
    fixture = _make_fixture("fx")
    exc = Exception("err")
    result = _synthetic_failure(fixture, exc)
    assert result.signal_report.ok is False


# ---------------------------------------------------------------------------
# _synthetic_failure — infra path
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_synthetic_failure_infra_sets_flag() -> None:
    fixture = _make_fixture("infra-fx")
    exc = InfraError("model endpoint down")
    result = _synthetic_failure(fixture, exc, infra=True)
    assert result.passed is False
    assert result.run.is_infra_error is True
    assert "INFRA ERROR" in result.run.notes[0]
    assert "model endpoint down" in result.run.infra_error_detail


@pytest.mark.unit
def test_synthetic_failure_infra_fixture_id_preserved() -> None:
    fixture = _make_fixture("special-fixture")
    exc = InfraError("timeout")
    result = _synthetic_failure(fixture, exc, infra=True)
    assert result.fixture_id == "special-fixture"


@pytest.mark.unit
def test_synthetic_failure_infra_empty_dependencies() -> None:
    fixture = Fixture(
        path=Path("fixtures/fx.yaml"),
        schema_version=1,
        updated="2025-01-01",
        id="no-deps",
        description="",
        variant="",
        prompt="test",
        required=(),
        dependencies=("rules/dep.md",),
        forbidden=(),
        optional=(),
        trigger_evidence=TriggerEvidence(),
    )
    exc = InfraError("error")
    result = _synthetic_failure(fixture, exc, infra=True)
    assert "rules/dep.md" in result.match.missing_dependencies


# ---------------------------------------------------------------------------
# _build_run_result — progressive mode (000-global-core.md exclusion)
# ---------------------------------------------------------------------------


def _make_progressive_run(loaded: tuple[str, ...] = ()) -> AgentRun:
    """AgentRun that does NOT include 000-global-core.md (as models do in progressive mode)."""
    return AgentRun(
        fixture_id="prog-fx",
        loaded=loaded,
        loaded_via_reads=loaded,
        loaded_via_reads_performed=loaded,
        loaded_via_section=loaded,
        disagreements=(),
        turns=3,
        duration_ms=500,
        model="claude-test",
        notes=(),
    )


def _make_progressive_fixture(
    fixture_id: str = "prog-fx",
    required: tuple[str, ...] = (
        "rules/000-global-core.md",
        "rules/116-snowflake-cortex-search.md",
    ),
) -> Fixture:
    return Fixture(
        path=Path(f"fixtures/{fixture_id}.yaml"),
        schema_version=3,
        updated="2026-07-19T00:00:00Z",
        id=fixture_id,
        description="",
        variant="simple",
        prompt="Set up a cortex search service.",
        required=required,
        dependencies=(),
        forbidden=(),
        optional=(),
        trigger_evidence=TriggerEvidence(),
    )


@pytest.mark.unit
def test_build_run_result_progressive_excludes_foundation() -> None:
    """000-global-core.md absent from loaded set does not fail the fixture (always excluded)."""
    fixture = _make_progressive_fixture()
    # Agent loaded the domain rule but NOT the foundation (correct behavior)
    run = _make_progressive_run(loaded=("rules/116-snowflake-cortex-search.md",))
    rules_meta: dict = {}

    result = _build_run_result(fixture, run, rules_meta, strict_forbidden=False)

    assert result.match.passed is True
    assert "rules/000-global-core.md" not in result.match.missing_required


@pytest.mark.unit
def test_build_run_result_nonprogressive_requires_foundation() -> None:
    """000-global-core.md is always excluded from required set (regression guard)."""
    fixture = _make_progressive_fixture()
    # Agent loaded the domain rule but NOT the foundation — should pass since foundation always excluded
    run = _make_progressive_run(loaded=("rules/116-snowflake-cortex-search.md",))
    rules_meta: dict = {}

    result = _build_run_result(fixture, run, rules_meta, strict_forbidden=False)

    # Foundation is always excluded, so this passes even without it
    assert result.match.passed is True
    assert "rules/000-global-core.md" not in result.match.missing_required


@pytest.mark.unit
def test_build_run_result_progressive_still_requires_domain_rule() -> None:
    """Only 000-global-core.md is excluded; other required rules still needed."""
    fixture = _make_progressive_fixture()
    # Agent loaded NEITHER the foundation NOR the domain rule
    run = _make_progressive_run(loaded=())
    rules_meta: dict = {}

    result = _build_run_result(fixture, run, rules_meta, strict_forbidden=False)

    assert result.match.passed is False
    assert "rules/116-snowflake-cortex-search.md" in result.match.missing_required
    assert "rules/000-global-core.md" not in result.match.missing_required
