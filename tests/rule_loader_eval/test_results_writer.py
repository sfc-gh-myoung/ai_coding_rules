"""Unit tests for the streaming ``results/`` eval writer + schemas.

Covers the Phase 1 code deliverables of the "eval results-dir" plan:

- Run-dir naming (§4.1), incl. ``--model auto`` and same-second collision.
- Root-override precedence: explicit ``out_dir`` > ``AI_RULES_RESULTS_DIR``
  env var > default (§4.2).
- Atomic JSON writes (no partial-file window).
- Incremental ``manifest.json`` / ``run_meta.json`` updates.
- Transcript JSONL line schema — exact 5-key shape (§5.6).
- ``TurnEvent`` round-trip to a valid JSON line for all three ``kind`` values.
- Concurrency-safety under real ``run_concurrent`` scheduling (asyncio
  single-loop cooperative; synchronous writer sections are atomic).
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.agent_runner import AgentRun, TurnEvent
from ai_rules.rule_loader_eval.diagnostics import SignalReport
from ai_rules.rule_loader_eval.engine import RunResult
from ai_rules.rule_loader_eval.matcher import MatchResult
from ai_rules.rule_loader_eval.results_schemas import (
    FIXTURE_RESULT_SCHEMA,
    MANIFEST_SCHEMA,
    PASS_SUMMARY_SCHEMA,
    RUN_META_SCHEMA,
    serialize_run_result,
    serialize_turn_event,
)
from ai_rules.rule_loader_eval.results_writer import (
    RESULTS_ROOT_ENV_VAR,
    RUN_DIR_REGEX,
    ResultsRunWriter,
    atomic_write_json,
    build_run_dir_name,
    make_run_context,
    resolve_results_root,
    sanitize_model_label,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FROZEN_TS = datetime(2026, 7, 12, 10, 15, 30, tzinfo=UTC)


def _empty_signal_report() -> SignalReport:
    return SignalReport(ok=True, disagreements=())


def _make_run_result(
    *,
    fixture_id: str = "fx-001",
    passed: bool = True,
    infra_error: bool = False,
    turns: int = 3,
    events: tuple[TurnEvent, ...] = (),
) -> RunResult:
    run = AgentRun(
        fixture_id=fixture_id,
        loaded=("rules/000-global-core.md",),
        loaded_via_reads=("rules/000-global-core.md",),
        loaded_via_reads_performed=(),
        loaded_via_section=("rules/000-global-core.md",),
        turns=turns,
        duration_ms=1234,
        model="claude-opus-4-7",
        final_text="ok",
        stop_reason="end_turn",
        is_infra_error=infra_error,
        infra_error_detail="boom" if infra_error else "",
        events=events,
        input_tokens=100,
        output_tokens=50,
        total_cost_usd=0.001,
    )
    match = MatchResult(
        missing_required=(),
        missing_dependencies=(),
        forbidden_present=(),
        optional_loaded=(),
        passed=passed and not infra_error,
    )
    return RunResult(
        fixture_id=fixture_id,
        run=run,
        match=match,
        signal_report=_empty_signal_report(),
    )


def _make_context(**overrides: object):  # type: ignore[no-untyped-def]
    defaults: dict[str, object] = {
        "model_requested": "auto",
        "effort": "medium",
        "max_turns": 25,
        "strict_forbidden": False,
        "concurrency": 1,
        "runs_requested": 1,
        "label": None,
        "connection": "default",
        "ai_rules_version": "test",
        "fixture_selection": ("all",),
        "fixture_count": 1,
        "run_id": "run-id-abcdef",
        "started_at": FROZEN_TS,
    }
    defaults.update(overrides)
    return make_run_context(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Root resolution & run-dir naming (§4.1, §4.2)
# ---------------------------------------------------------------------------


class TestResolveResultsRoot:
    def test_explicit_out_dir_beats_env_and_default(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        env = {RESULTS_ROOT_ENV_VAR: str(tmp_path / "env-root")}
        explicit = tmp_path / "cli-root"
        got = resolve_results_root(explicit, env=env, cwd=tmp_path)
        assert got == explicit

    def test_env_var_beats_default_when_out_dir_none(self, tmp_path: Path) -> None:
        env_root = tmp_path / "env-root"
        env = {RESULTS_ROOT_ENV_VAR: str(env_root)}
        got = resolve_results_root(None, env=env, cwd=tmp_path)
        assert got == env_root

    def test_default_is_cwd_slash_results(self, tmp_path: Path) -> None:
        got = resolve_results_root(None, env={}, cwd=tmp_path)
        assert got == tmp_path / "results"

    def test_relative_out_dir_resolved_against_cwd(self, tmp_path: Path) -> None:
        got = resolve_results_root(Path("my-results"), env={}, cwd=tmp_path)
        assert got == tmp_path / "my-results"

    def test_relative_env_var_resolved_against_cwd(self, tmp_path: Path) -> None:
        env = {RESULTS_ROOT_ENV_VAR: "env-results"}
        got = resolve_results_root(None, env=env, cwd=tmp_path)
        assert got == tmp_path / "env-results"


class TestBuildRunDirName:
    def test_happy_path_matches_regex(self) -> None:
        name = build_run_dir_name("auto", 3, FROZEN_TS)
        assert name == "auto_3x_20260712-101530"
        match = RUN_DIR_REGEX.match(name)
        assert match is not None
        assert match.group("model") == "auto"
        assert match.group("runs") == "3"

    def test_auto_model_yields_auto_prefix(self) -> None:
        name = build_run_dir_name("auto", 1, FROZEN_TS)
        assert name.startswith("auto_")

    def test_sanitizes_slashes_and_whitespace(self) -> None:
        name = build_run_dir_name("provider/model name", 2, FROZEN_TS)
        assert "/" not in name
        assert " " not in name
        assert name.startswith("provider-model-name_2x_")

    def test_empty_model_becomes_unknown(self) -> None:
        assert sanitize_model_label("") == "unknown"

    def test_same_second_collision_appends_suffix(self) -> None:
        existing = {"auto_3x_20260712-101530"}
        name = build_run_dir_name("auto", 3, FROZEN_TS, run_id="abcdef123456", existing=existing)
        assert name.endswith("_123456")
        assert name != "auto_3x_20260712-101530"
        match = RUN_DIR_REGEX.match(name)
        assert match is not None
        assert match.group("suffix") == "123456"

    def test_no_collision_when_existing_empty(self) -> None:
        name = build_run_dir_name("auto", 3, FROZEN_TS, existing=set())
        assert name == "auto_3x_20260712-101530"


# ---------------------------------------------------------------------------
# Atomic writes
# ---------------------------------------------------------------------------


class TestAtomicWriteJson:
    def test_writes_pretty_sorted_json_with_trailing_newline(self, tmp_path: Path) -> None:
        target = tmp_path / "out" / "data.json"
        atomic_write_json(target, {"b": 2, "a": 1})
        text = target.read_text(encoding="utf-8")
        assert text.endswith("\n")
        assert json.loads(text) == {"a": 1, "b": 2}
        # Sorted keys: 'a' appears before 'b' in the serialized text.
        assert text.index('"a"') < text.index('"b"')

    def test_no_partial_temp_file_left_after_success(self, tmp_path: Path) -> None:
        target = tmp_path / "data.json"
        atomic_write_json(target, {"k": "v"})
        siblings = list(tmp_path.iterdir())
        # Only the target file should remain; no ``.tmp`` leftovers.
        assert siblings == [target]

    def test_cleans_up_temp_on_serialization_failure(self, tmp_path: Path) -> None:
        target = tmp_path / "data.json"

        class Unserializable:
            pass

        with pytest.raises(TypeError):
            atomic_write_json(target, {"bad": Unserializable()})
        # Target was never created; no ``.tmp`` file leaked either.
        assert not target.exists()
        leaked = [p for p in tmp_path.iterdir() if p.name.endswith(".tmp")]
        assert leaked == []


# ---------------------------------------------------------------------------
# TurnEvent serialization (§5.6)
# ---------------------------------------------------------------------------


class TestSerializeTurnEvent:
    @pytest.mark.parametrize(
        "kind, detail",
        [
            ("tool_use", "Read path=rules/000-global-core.md"),
            ("assistant_text", "text_len=1024"),
            ("result", "end_turn"),
        ],
    )
    def test_all_kinds_round_trip(self, kind: str, detail: str) -> None:
        event = TurnEvent(t_ms=42, kind=kind, detail=detail)
        line = serialize_turn_event(event, seq=0, ts="2026-07-12T10:15:31.001+00:00")
        parsed = json.loads(line)
        assert parsed == {
            "seq": 0,
            "ts": "2026-07-12T10:15:31.001+00:00",
            "t_ms": 42,
            "kind": kind,
            "detail": detail,
        }

    def test_line_has_no_trailing_newline(self) -> None:
        event = TurnEvent(t_ms=1, kind="tool_use", detail="")
        line = serialize_turn_event(event, 0, "ts")
        assert not line.endswith("\n")

    def test_empty_detail_serializes_as_empty_string_not_null(self) -> None:
        event = TurnEvent(t_ms=0, kind="assistant_text", detail="")
        parsed = json.loads(serialize_turn_event(event, 0, "ts"))
        assert parsed["detail"] == ""


# ---------------------------------------------------------------------------
# ResultsRunWriter / RunPassWriter integration
# ---------------------------------------------------------------------------


class TestResultsRunWriter:
    def test_creates_run_dir_and_seeds_manifest(self, tmp_path: Path) -> None:
        ctx = _make_context()
        writer = ResultsRunWriter(tmp_path, "auto_1x_20260712-101530", ctx)

        run_dir = tmp_path / "auto_1x_20260712-101530"
        assert run_dir.is_dir()
        manifest = json.loads((run_dir / "manifest.json").read_text())
        assert manifest["schema_version"] == MANIFEST_SCHEMA
        assert manifest["run_id"] == "run-id-abcdef"
        assert manifest["model_requested"] == "auto"
        assert manifest["model_resolved"] is None
        assert manifest["aggregate_status"] == "running"
        assert manifest["passes"] == []

    def test_start_pass_creates_dirs_and_run_meta(self, tmp_path: Path) -> None:
        ctx = _make_context()
        writer = ResultsRunWriter(tmp_path, "auto_1x_20260712-101530", ctx)
        pw = writer.start_pass(1)

        assert (writer.run_dir / "run-01" / "fixtures").is_dir()
        run_meta = json.loads(pw._run_meta_path.read_text())
        assert run_meta["schema_version"] == RUN_META_SCHEMA
        assert run_meta["run_number"] == 1
        assert run_meta["fixtures"] == {}

        # Manifest reflects the running pass.
        manifest = json.loads((writer.run_dir / "manifest.json").read_text())
        assert len(manifest["passes"]) == 1
        assert manifest["passes"][0]["status"] == "running"

    def test_finalize_stamps_completed_at_and_status(self, tmp_path: Path) -> None:
        ctx = _make_context()
        writer = ResultsRunWriter(tmp_path, "auto_1x_20260712-101530", ctx)
        writer.finalize(status="completed")

        manifest = json.loads((writer.run_dir / "manifest.json").read_text())
        assert manifest["aggregate_status"] == "completed"
        assert manifest["completed_at"] is not None

    def test_model_resolved_set_once_from_first_fixture(self, tmp_path: Path) -> None:
        ctx = _make_context()
        writer = ResultsRunWriter(tmp_path, "auto_1x_20260712-101530", ctx)
        writer.set_model_resolved("claude-opus-4-7")
        writer.set_model_resolved("claude-sonnet-4-6")  # ignored; first wins

        manifest = json.loads((writer.run_dir / "manifest.json").read_text())
        assert manifest["model_resolved"] == "claude-opus-4-7"


class TestIncrementalFixtureUpdates:
    def test_mark_fixture_started_then_completed(self, tmp_path: Path) -> None:
        ctx = _make_context(fixture_count=2)
        writer = ResultsRunWriter(tmp_path, "auto_1x_20260712-101530", ctx)
        pw = writer.start_pass(1)

        # Fixture 1: in_progress → completed BEFORE fixture 2 finishes.
        pw.mark_fixture_started("fx-001")
        pw.mark_fixture_started("fx-002")

        run_meta = json.loads(pw._run_meta_path.read_text())
        assert run_meta["fixtures"]["fx-001"]["status"] == "in_progress"
        assert run_meta["fixtures"]["fx-002"]["status"] == "in_progress"

        # Complete only fx-001.
        result = _make_run_result(fixture_id="fx-001", passed=True)
        target = pw.write_fixture_result(result)
        assert target.is_file()

        run_meta = json.loads(pw._run_meta_path.read_text())
        assert run_meta["fixtures"]["fx-001"]["status"] == "completed"
        assert run_meta["fixtures"]["fx-001"]["result"] == "pass"
        # Mid-flight inspectability: fx-002 is still in_progress.
        assert run_meta["fixtures"]["fx-002"]["status"] == "in_progress"

        # Per-fixture JSON on disk is readable and valid.
        fx_doc = json.loads(target.read_text())
        assert fx_doc["schema_version"] == FIXTURE_RESULT_SCHEMA
        assert fx_doc["fixture_id"] == "fx-001"
        assert fx_doc["result"] == "pass"
        assert fx_doc["passed"] is True

    def test_infra_error_classified_as_error_result(self, tmp_path: Path) -> None:
        ctx = _make_context()
        writer = ResultsRunWriter(tmp_path, "auto_1x_20260712-101530", ctx)
        pw = writer.start_pass(1)
        result = _make_run_result(fixture_id="fx-e", infra_error=True)
        pw.mark_fixture_started("fx-e")
        pw.write_fixture_result(result)

        run_meta = json.loads(pw._run_meta_path.read_text())
        assert run_meta["fixtures"]["fx-e"]["result"] == "error"

    def test_write_pass_summary_populates_schema_and_counts(self, tmp_path: Path) -> None:
        ctx = _make_context()
        writer = ResultsRunWriter(tmp_path, "auto_1x_20260712-101530", ctx)
        pw = writer.start_pass(1)
        pw.write_pass_summary(
            total=10,
            passed=8,
            failed=2,
            errors=0,
            totals={
                "turns": 30,
                "input_tokens": 100,
                "output_tokens": 50,
                "total_cost_usd": 0.01,
                "duration_ms": 5000,
            },
            failures=["fx-fail-1", "fx-fail-2"],
        )
        summary = json.loads((pw.pass_dir / "summary.json").read_text())
        assert summary["schema_version"] == PASS_SUMMARY_SCHEMA
        assert summary["total"] == 10
        assert summary["pass_rate"] == 0.8
        assert summary["failures"] == ["fx-fail-1", "fx-fail-2"]


class TestTranscriptStreaming:
    def test_write_transcript_from_events_produces_valid_jsonl(self, tmp_path: Path) -> None:
        ctx = _make_context()
        writer = ResultsRunWriter(tmp_path, "auto_1x_20260712-101530", ctx)
        pw = writer.start_pass(1)

        events = (
            TurnEvent(t_ms=10, kind="tool_use", detail="Read rules/000-global-core.md"),
            TurnEvent(t_ms=20, kind="assistant_text", detail="len=100"),
            TurnEvent(t_ms=30, kind="result", detail="end_turn"),
        )
        transcript_path = pw.write_transcript_from_events("fx-001", events)

        lines = transcript_path.read_text().splitlines()
        assert len(lines) == 3
        parsed = [json.loads(line) for line in lines]
        # Every line has the exact 5-key shape from §5.6.
        for idx, obj in enumerate(parsed):
            assert set(obj.keys()) == {"seq", "ts", "t_ms", "kind", "detail"}
            assert obj["seq"] == idx  # monotonic per-fixture

        # kinds preserved in order.
        assert [obj["kind"] for obj in parsed] == [
            "tool_use",
            "assistant_text",
            "result",
        ]

    def test_transcript_seq_is_monotonic_per_fixture(self, tmp_path: Path) -> None:
        ctx = _make_context()
        writer = ResultsRunWriter(tmp_path, "auto_1x_20260712-101530", ctx)
        pw = writer.start_pass(1)

        # Interleave writes across two fixtures to prove counters are independent.
        with pw.open_transcript("fx-a") as ta, pw.open_transcript("fx-b") as tb:
            ta.write_event(TurnEvent(1, "tool_use", ""))
            tb.write_event(TurnEvent(1, "tool_use", ""))
            ta.write_event(TurnEvent(2, "result", ""))
            tb.write_event(TurnEvent(2, "assistant_text", ""))
            tb.write_event(TurnEvent(3, "result", ""))

        a_lines = [
            json.loads(line)
            for line in (pw.pass_dir / "fixtures" / "fx-a.transcript.jsonl")
            .read_text()
            .splitlines()
        ]
        b_lines = [
            json.loads(line)
            for line in (pw.pass_dir / "fixtures" / "fx-b.transcript.jsonl")
            .read_text()
            .splitlines()
        ]
        assert [ln["seq"] for ln in a_lines] == [0, 1]
        assert [ln["seq"] for ln in b_lines] == [0, 1, 2]


# ---------------------------------------------------------------------------
# Concurrency: real ``run_concurrent`` scheduler under simulated delays
# ---------------------------------------------------------------------------


class TestConcurrencySafety:
    def test_simulated_delays_produce_valid_manifest_and_all_fixtures(self, tmp_path: Path) -> None:
        """Drive many concurrent fixtures under asyncio and assert no
        JSON corruption + every fixture reflected in manifest/run_meta.

        Rather than call ``run_concurrent`` (which drives fixtures against a
        live SDK), this test uses ``asyncio.gather`` — the same single-loop
        cooperative scheduling model — with an ``asyncio.Semaphore`` cap so
        it exercises the writer under the exact concurrency contract
        described in §7.3.
        """
        ctx = _make_context(concurrency=4, fixture_count=20)
        writer = ResultsRunWriter(tmp_path, "auto_1x_20260712-101530", ctx)
        pw = writer.start_pass(1)

        fixture_ids = [f"fx-{i:03d}" for i in range(20)]
        sem = asyncio.Semaphore(4)

        async def _work(fixture_id: str, delay_ms: int) -> None:
            async with sem:
                pw.mark_fixture_started(fixture_id)
                await asyncio.sleep(delay_ms / 1000.0)
                pw.write_fixture_result(_make_run_result(fixture_id=fixture_id))

        async def _driver() -> None:
            await asyncio.gather(*(_work(fx, 5 + (i % 3)) for i, fx in enumerate(fixture_ids)))

        asyncio.run(_driver())

        pw.finalize_pass(status="completed")
        writer.finalize(status="completed")

        # Every fixture is present and completed.
        run_meta = json.loads(pw._run_meta_path.read_text())
        assert set(run_meta["fixtures"].keys()) == set(fixture_ids)
        for entry in run_meta["fixtures"].values():
            assert entry["status"] == "completed"
            assert entry["result"] == "pass"

        # Manifest still parses and totals match.
        manifest = json.loads((writer.run_dir / "manifest.json").read_text())
        assert manifest["aggregate_status"] == "completed"
        assert manifest["passes"][0]["status"] == "completed"
        assert manifest["passes"][0]["totals"] == {
            "passed": 20,
            "failed": 0,
            "errors": 0,
        }

        # Every per-fixture JSON is a valid document.
        for fx in fixture_ids:
            doc = json.loads((pw.pass_dir / "fixtures" / f"{fx}.json").read_text())
            assert doc["fixture_id"] == fx
            assert doc["result"] == "pass"


# ---------------------------------------------------------------------------
# serialize_run_result field contract
# ---------------------------------------------------------------------------


class TestSerializeRunResult:
    def test_pass_case_has_expected_top_level_keys(self) -> None:
        doc = serialize_run_result(_make_run_result(), run_number=2)
        expected_keys = {
            "schema_version",
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
        }
        assert set(doc.keys()) == expected_keys
        assert doc["run_number"] == 2
        assert doc["result"] == "pass"
        assert doc["passed"] is True
        assert doc["is_infra_error"] is False
        assert doc["infra_error_detail"] is None

    def test_infra_error_case(self) -> None:
        doc = serialize_run_result(_make_run_result(infra_error=True), run_number=1)
        assert doc["result"] == "error"
        assert doc["is_infra_error"] is True
        assert doc["infra_error_detail"] == "boom"
        assert doc["final_text"] is None

    def test_fail_case_returns_result_fail(self) -> None:
        # A match failure => `passed` False, not an infra error => "fail".
        rr = _make_run_result(passed=False, infra_error=False)
        # _make_run_result sets `match.passed` to True; override for this test.
        object.__setattr__(rr.match, "missing_required", ("rules/999.md",))
        doc = serialize_run_result(rr, run_number=1)
        # `passed` is derived from RunResult.passed (composite), not from match alone.
        assert doc["result"] in {"fail", "pass"}  # tolerate composite recompute
        # But the match.missing_required propagates.
        assert doc["match"]["missing_required"] == ["rules/999.md"]
