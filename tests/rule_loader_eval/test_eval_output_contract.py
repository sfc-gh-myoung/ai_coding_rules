"""Tests for rule-loader eval output-contract handling (legacy AGENTS.md)."""

from __future__ import annotations

import json as _json
from datetime import UTC as _UTC
from datetime import datetime as _datetime
from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.agent_runner import (
    AgentRun,
    extract_contract_text,
    validate_output_shape,
)
from ai_rules.rule_loader_eval.agent_runner import AgentRun as _AgentRun
from ai_rules.rule_loader_eval.agent_runner import TurnEvent as _TurnEvent
from ai_rules.rule_loader_eval.diagnostics import SignalReport
from ai_rules.rule_loader_eval.engine import RunResult
from ai_rules.rule_loader_eval.matcher import MatchResult
from ai_rules.rule_loader_eval.matcher import MatchResult as _MatchResult
from ai_rules.rule_loader_eval.results_schemas import (
    AGGREGATE_SUMMARY_SCHEMA as _AGG_SCHEMA,
)
from ai_rules.rule_loader_eval.results_schemas import (
    FIXTURE_RESULT_SCHEMA as _FIX_SCHEMA,
)
from ai_rules.rule_loader_eval.results_schemas import (
    MANIFEST_SCHEMA as _MANIFEST_SCHEMA,
)
from ai_rules.rule_loader_eval.results_schemas import (
    PASS_SUMMARY_SCHEMA as _SUMMARY_SCHEMA,
)
from ai_rules.rule_loader_eval.results_schemas import (
    RUN_META_SCHEMA as _RUNMETA_SCHEMA,
)
from ai_rules.rule_loader_eval.results_writer import (
    ResultsRunWriter as _ResultsRunWriter,
)
from ai_rules.rule_loader_eval.results_writer import (
    build_run_dir_name as _build_run_dir_name,
)
from ai_rules.rule_loader_eval.results_writer import (
    make_run_context as _make_run_context,
)


@pytest.mark.unit
def test_validate_output_shape_accepts_legacy_rules_loaded_heading() -> None:
    text = """## Rules Loaded
- rules/000-global-core.md (foundation) — 350 lines
- rules/200-python-core.md (ext: .py) — 453 lines
"""
    assert validate_output_shape(text, loaded_count=2) == ()


@pytest.mark.unit
def test_validate_output_shape_accepts_bold_inline_rules_loaded() -> None:
    text = """**Rules Loaded**
- rules/200-python-core.md (ext:.py) — 453 lines
"""
    assert validate_output_shape(text, loaded_count=1) == ()


@pytest.mark.unit
def test_validate_output_shape_accepts_no_match_rules_loaded_body() -> None:
    text = """## Rules Loaded
(none — no domain rules matched)
"""
    assert validate_output_shape(text, loaded_count=0) == ()


@pytest.mark.unit
def test_validate_output_shape_rejects_missing_rules_loaded_section() -> None:
    text = """Some prose without a Rules Loaded section.

Just some response.
"""
    violations = validate_output_shape(text, loaded_count=0)
    assert "missing Rules Loaded (Gate 3 or **Rules Loaded**) section" in violations


@pytest.mark.unit
def test_validate_output_shape_requires_no_match_body_for_zero_loaded() -> None:
    text = """## Rules Loaded

Task Switch: FIRST
"""
    violations = validate_output_shape(text, loaded_count=0)
    assert "zero loaded rules must use explicit no-match Rules Loaded body" in violations


@pytest.mark.unit
def test_extract_contract_text_anchors_on_rules_loaded() -> None:
    text = """Scanning rules first.

## Rules Loaded
- rules/200-python-core.md (ext:.py) — 453 lines
"""
    assert extract_contract_text(text).startswith("## Rules Loaded")


@pytest.mark.unit
def test_extract_contract_text_anchors_on_legacy_bootstrap() -> None:
    text = """Scanning rules first.

**Bootstrap:** rule Keywords scanned (python) — 1 rules loaded, 0 failed.

**Rules Loaded**
- rules/200-python-core.md (ext:.py) — 453 lines

Task Switch: FIRST
"""
    extracted = extract_contract_text(text)
    assert extracted.startswith("**Bootstrap:**")


@pytest.mark.unit
def test_run_result_fails_on_output_contract_violation() -> None:
    run = AgentRun(
        fixture_id="bad-output",
        loaded=("rules/200-python-core.md",),
        loaded_via_reads=("rules/200-python-core.md",),
        loaded_via_reads_performed=(),
        loaded_via_section=("rules/200-python-core.md",),
        output_violations=("missing Rules Loaded (Gate 3 or **Rules Loaded**) section",),
    )
    result = RunResult(
        fixture_id="bad-output",
        run=run,
        match=MatchResult(
            missing_required=(),
            missing_dependencies=(),
            forbidden_present=(),
            optional_loaded=(),
            passed=True,
        ),
        signal_report=SignalReport(ok=True, disagreements=()),
        citation_drifts=(),
    )
    assert result.passed is False


# --- Gate 3 tests ---


@pytest.mark.unit
def test_validate_output_shape_accepts_gate3_block() -> None:
    text = """\
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — 263 lines
- [x] Gate 2: Searched: python
- [x] Gate 3: Rules loaded:
  - rules/000-global-core.md (foundation) — 263 lines
  - rules/200-python-core.md (ext: .py) — 453 lines

Task Switch: FIRST
"""
    assert validate_output_shape(text, loaded_count=2) == ()


@pytest.mark.unit
def test_validate_output_shape_accepts_gate3_no_match_body() -> None:
    text = """\
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — 263 lines
- [x] Gate 2: Searched: xyz
- [x] Gate 3: (none — no domain rules matched)

Task Switch: FIRST
"""
    assert validate_output_shape(text, loaded_count=0) == ()


@pytest.mark.unit
def test_validate_output_shape_rejects_gate3_zero_loaded_without_no_match_body() -> None:
    text = """\
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — 263 lines
- [x] Gate 2: Searched: xyz
- [x] Gate 3: Rules loaded:

Task Switch: FIRST
"""
    violations = validate_output_shape(text, loaded_count=0)
    assert "zero loaded rules must use explicit no-match Rules Loaded body" in violations


@pytest.mark.unit
def test_extract_contract_text_anchors_on_gate3() -> None:
    text = """\
Some preamble.

PRE-FLIGHT:
- [x] Gate 1: Foundation loaded
- [x] Gate 2: Searched: python
- [x] Gate 3: Rules loaded:
  - rules/000-global-core.md (foundation) — 263 lines

Task Switch: FIRST
"""
    extracted = extract_contract_text(text)
    assert "Gate 3:" in extracted


@pytest.mark.unit
def test_extract_contract_text_prefers_earliest_marker_gate3_vs_legacy() -> None:
    """When PRE-FLIGHT: appears before a legacy ## Rules Loaded heading, PRE-FLIGHT wins (RF4)."""
    text = """\
PRE-FLIGHT:
- [x] Gate 3: Rules loaded:
  - rules/000-global-core.md (foundation) — 263 lines

Some prose.

## Rules Loaded
- rules/000-global-core.md (foundation) — 263 lines
"""
    extracted = extract_contract_text(text)
    # RF4: now starts at PRE-FLIGHT:, which is earlier than Gate 3
    assert extracted.startswith("PRE-FLIGHT:")
    assert "- [x] Gate 3:" in extracted


@pytest.mark.unit
def test_extract_contract_text_preserves_gate3_checkbox_prefix() -> None:
    """Regression: extraction must keep the '- [x] ' checkbox so the Gate 3
    anchor regex still matches downstream (live-eval failure mode).
    """
    text = """\
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — 268 lines
- [x] Gate 2: Searched: python
- [x] Gate 3: Rules loaded:
  - rules/000-global-core.md (foundation) — 268 lines
  - rules/200-python-core.md (for .py extension) — 454 lines

SEED_FIXTURE_COMPLETE
"""
    extracted = extract_contract_text(text)
    # RF4: starts at PRE-FLIGHT: now; Gate 3 checkbox is preserved within
    assert extracted.startswith("PRE-FLIGHT:")
    assert "- [x] Gate 3:" in extracted
    assert validate_output_shape(extracted, loaded_count=2) == ()


# ---------------------------------------------------------------------------
# New Gate-1-only shape tests (added 2026-07-10)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_validate_output_shape_accepts_gate3_none_matched() -> None:
    """New sentinel '- [x] Gate 3: none matched' is accepted by validate_output_shape."""
    text = """\
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — 268 lines
- [x] Gate 2: Searched: python
- [x] Gate 3: none matched

Task Switch: FIRST
"""
    violations = validate_output_shape(text, loaded_count=0)
    assert violations == ()


@pytest.mark.unit
def test_validate_output_shape_gate1_only_foundation() -> None:
    """Gate-1-only shape (foundation on Gate 1, domain rules in Gate 3) passes shape check."""
    text = """\
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — 268 lines
- [x] Gate 2: Searched: python
- [x] Gate 3: +1 domain rule:
  - rules/200-python-core.md (file extension: .py) — 453 lines

Task Switch: FIRST
"""
    violations = validate_output_shape(text, loaded_count=1)
    assert violations == ()


# ---------------------------------------------------------------------------
# Phase 2: on-disk results/ contract from a mocked (non-live) run
# ---------------------------------------------------------------------------
#
# These tests assert the streaming ``results/<run_dir>/`` layout defined in
# plan sections 5.1-5.6. They drive the writer directly (no live SDK, no
# ProgressTracker) so the on-disk contract is validated deterministically in
# CI. When Phase 3 removes ``ProgressTracker`` and rewires ``_run_single_eval``
# to call the writer through non-tracker seams, these tests do not need to
# change - they cover the artifact contract, not the wiring.


def _mk_run_result(fixture_id: str, *, passed: bool = True) -> RunResult:
    """Build a minimal ``RunResult`` sufficient to serialize (no live SDK)."""
    events = (
        _TurnEvent(t_ms=10, kind="tool_use", detail="read foundation"),
        _TurnEvent(t_ms=20, kind="assistant_text", detail="preflight header"),
        _TurnEvent(t_ms=30, kind="result", detail="end_turn"),
    )
    run = _AgentRun(
        fixture_id=fixture_id,
        loaded=("rules/000-global-core.md",),
        loaded_via_reads=("rules/000-global-core.md",),
        loaded_via_reads_performed=(),
        loaded_via_section=("rules/000-global-core.md",),
        turns=3,
        duration_ms=1234,
        model="claude-opus-4-7",
        final_text="ok",
        stop_reason="end_turn",
        events=events,
        input_tokens=100,
        output_tokens=50,
        total_cost_usd=0.001,
    )
    match = _MatchResult(
        missing_required=(),
        missing_dependencies=(),
        forbidden_present=(),
        optional_loaded=(),
        passed=passed,
    )
    return RunResult(
        fixture_id=fixture_id,
        run=run,
        match=match,
        signal_report=SignalReport(ok=True, disagreements=()),
    )


def _drive_mocked_run(root: Path) -> Path:
    """Simulate what ``eval_cmd`` writes to ``results/`` for one 1-pass run."""
    ctx = _make_run_context(
        model_requested="auto",
        effort="medium",
        max_turns=25,
        strict_forbidden=False,
        concurrency=1,
        runs_requested=1,
        label=None,
        connection="default",
        ai_rules_version="test",
        fixture_selection=("fx-alpha",),
        fixture_count=1,
        run_id="run-id-0abcd0",
        started_at=_datetime(2026, 7, 12, 10, 15, 30, tzinfo=_UTC),
    )
    started_dt = _datetime.fromisoformat(ctx.started_at)
    run_dir_name = _build_run_dir_name(
        ctx.model_requested, ctx.runs_requested, started_dt, run_id=ctx.run_id
    )
    writer = _ResultsRunWriter(root=root, run_dir_name=run_dir_name, context=ctx)
    pw = writer.start_pass(1)
    fixture_id = "fx-alpha"
    pw.mark_fixture_started(fixture_id)
    rr = _mk_run_result(fixture_id, passed=True)
    pw.write_transcript_from_events(fixture_id, rr.run.events)
    pw.write_fixture_result(rr)
    pw.write_pass_summary(
        total=1,
        passed=1,
        failed=0,
        errors=0,
        totals={
            "turns": 3,
            "input_tokens": 100,
            "output_tokens": 50,
            "duration_ms": 1234,
            "total_cost_usd": 0.001,
        },
        failures=[],
    )
    pw.finalize_pass(status="completed")
    writer.write_aggregate_summary(
        {  # type: ignore[arg-type]
            "schema_version": _AGG_SCHEMA,
            "runs": 1,
            "fixture_count": 1,
            "per_fixture": {
                fixture_id: {
                    "n_runs": 1,
                    "passes": 1,
                    "fails": 0,
                    "flake_score": 0.0,
                    "pass_rate": 1.0,
                    "deterministic_fail": False,
                }
            },
            "aggregate": {
                "mean_pass_rate": 1.0,
                "flaky_fixtures": [],
                "total_cost_usd": 0.001,
                "total_input_tokens": 100,
                "total_output_tokens": 50,
                "total_duration_ms": 1234,
                "total_signal_disagreements": 0,
                "total_citation_drifts": 0,
            },
        }
    )
    writer.finalize(status="completed")
    return writer.run_dir


@pytest.mark.unit
def test_results_dir_contract_files_exist(tmp_path: Path) -> None:
    """All five §5 file classes exist on disk after a mocked run."""
    run_dir = _drive_mocked_run(tmp_path)

    assert (run_dir / "manifest.json").is_file(), "manifest.json missing"
    assert (run_dir / "summary.json").is_file(), "run-root summary.json missing"

    pass_dir = run_dir / "run-01"
    assert pass_dir.is_dir(), "run-01/ missing"
    assert (pass_dir / "run_meta.json").is_file(), "run_meta.json missing"
    assert (pass_dir / "summary.json").is_file(), "per-pass summary.json missing"

    fixtures_dir = pass_dir / "fixtures"
    assert fixtures_dir.is_dir(), "fixtures/ missing"
    assert (fixtures_dir / "fx-alpha.json").is_file(), "fixture <id>.json missing"
    assert (fixtures_dir / "fx-alpha.transcript.jsonl").is_file(), (
        "fixture <id>.transcript.jsonl missing"
    )


@pytest.mark.unit
def test_results_dir_contract_schema_versions(tmp_path: Path) -> None:
    """Every artifact carries the expected schema_version constant (sections 5.1-5.5)."""
    run_dir = _drive_mocked_run(tmp_path)

    manifest = _json.loads((run_dir / "manifest.json").read_text())
    assert manifest["schema_version"] == _MANIFEST_SCHEMA

    summary_root = _json.loads((run_dir / "summary.json").read_text())
    assert summary_root["schema_version"] == _AGG_SCHEMA

    pass_dir = run_dir / "run-01"
    run_meta = _json.loads((pass_dir / "run_meta.json").read_text())
    assert run_meta["schema_version"] == _RUNMETA_SCHEMA

    summary_pass = _json.loads((pass_dir / "summary.json").read_text())
    assert summary_pass["schema_version"] == _SUMMARY_SCHEMA

    fixture_doc = _json.loads((pass_dir / "fixtures" / "fx-alpha.json").read_text())
    assert fixture_doc["schema_version"] == _FIX_SCHEMA


@pytest.mark.unit
def test_results_dir_contract_manifest_required_fields(tmp_path: Path) -> None:
    """Manifest carries every non-null §5.1 field with expected types."""
    run_dir = _drive_mocked_run(tmp_path)
    manifest = _json.loads((run_dir / "manifest.json").read_text())

    for key in (
        "run_id",
        "run_dir_name",
        "started_at",
        "updated_at",
        "model_requested",
        "effort",
        "max_turns",
        "strict_forbidden",
        "concurrency",
        "runs_requested",
        "connection",
        "ai_rules_version",
        "fixture_count",
        "git",
        "passes",
        "aggregate_status",
    ):
        assert key in manifest, f"manifest missing required key: {key}"
    assert manifest["aggregate_status"] == "completed"
    assert manifest["completed_at"] is not None
    # model_resolved is set by the writer once the first fixture reports a
    # non-empty model — the mocked run reports "claude-opus-4-7".
    assert manifest["model_resolved"] == "claude-opus-4-7"
    assert isinstance(manifest["passes"], list)
    assert manifest["passes"][0]["run_number"] == 1
    assert manifest["passes"][0]["status"] == "completed"


@pytest.mark.unit
def test_results_dir_contract_fixture_json_required_fields(tmp_path: Path) -> None:
    """Per-fixture <id>.json carries every §5.5 required field."""
    run_dir = _drive_mocked_run(tmp_path)
    doc = _json.loads((run_dir / "run-01" / "fixtures" / "fx-alpha.json").read_text())

    for key in (
        "fixture_id",
        "run_number",
        "model",
        "passed",
        "result",
        "match",
        "signal_report",
        "citation_drifts",
        "depends_violations",
        "depends_ok",
        "effective_loaded",
        "output_violations",
        "turns",
        "input_tokens",
        "output_tokens",
        "total_cost_usd",
        "duration_ms",
        "final_text",
        "stop_reason",
        "is_infra_error",
        "infra_error_detail",
        "skill_invocations",
        "loaded",
        "loaded_via_reads",
    ):
        assert key in doc, f"fixture doc missing required key: {key}"

    assert doc["fixture_id"] == "fx-alpha"
    assert doc["run_number"] == 1
    assert doc["passed"] is True
    assert doc["result"] == "pass"
    assert doc["is_infra_error"] is False
    assert doc["infra_error_detail"] is None
    for match_key in (
        "missing_required",
        "missing_dependencies",
        "forbidden_present",
        "extra_loaded",
    ):
        assert match_key in doc["match"], f"match missing key: {match_key}"


@pytest.mark.unit
def test_results_dir_contract_transcript_line_shape(tmp_path: Path) -> None:
    """Each transcript line has exactly 5 keys (§5.6) with expected types."""
    run_dir = _drive_mocked_run(tmp_path)
    lines = (run_dir / "run-01" / "fixtures" / "fx-alpha.transcript.jsonl").read_text().splitlines()
    assert len(lines) == 3, "expected one JSONL line per TurnEvent"

    seqs: list[int] = []
    for line in lines:
        record = _json.loads(line)
        assert set(record) == {"seq", "ts", "t_ms", "kind", "detail"}, (
            f"unexpected transcript keys: {sorted(record)}"
        )
        assert isinstance(record["seq"], int)
        assert isinstance(record["ts"], str)
        assert isinstance(record["t_ms"], int)
        assert isinstance(record["kind"], str)
        assert isinstance(record["detail"], str)
        seqs.append(record["seq"])
    assert seqs == sorted(seqs), "seq must be monotonic per fixture"


@pytest.mark.unit
def test_results_dir_contract_run_meta_and_summary(tmp_path: Path) -> None:
    """run_meta.json flips to completed; per-pass + aggregate summaries match."""
    run_dir = _drive_mocked_run(tmp_path)

    run_meta = _json.loads((run_dir / "run-01" / "run_meta.json").read_text())
    assert run_meta["run_number"] == 1
    assert run_meta["completed_at"] is not None
    fx_entry = run_meta["fixtures"]["fx-alpha"]
    assert fx_entry["status"] == "completed"
    assert fx_entry["result"] == "pass"
    assert fx_entry["started_at"] is not None
    assert fx_entry["completed_at"] is not None

    pass_summary = _json.loads((run_dir / "run-01" / "summary.json").read_text())
    for key in (
        "run_number",
        "total",
        "passed",
        "failed",
        "errors",
        "pass_rate",
        "totals",
        "failures",
    ):
        assert key in pass_summary, f"pass summary missing key: {key}"
    assert pass_summary["total"] == 1
    assert pass_summary["passed"] == 1
    assert pass_summary["pass_rate"] == 1.0

    agg = _json.loads((run_dir / "summary.json").read_text())
    assert agg["runs"] == 1
    assert agg["fixture_count"] == 1
    assert "fx-alpha" in agg["per_fixture"]
    assert agg["aggregate"]["mean_pass_rate"] == 1.0
    assert agg["aggregate"]["flaky_fixtures"] == []
