"""v2.0.0 robustness tests for skill-timer.

Consolidates the test cases originally planned across:
- test_plausibility_validators.py
- test_wrap_subcommand.py
- test_finalize_stages.py
- test_replay_subcommand.py
- test_mode_enum_semantics.py

Coverage targets:
- Distribution validator: each of 11 alerts triggered independently
- wrap: explicit start_epoch, implicit chaining, evidence too small, mode validation
- finalize: pre_write requires --review-artifact, post_write records, deprecation path
- replay: bad fixture exits 4, good fixture exits 0
- mode enum: not-requested / unavailable / failed / self-report-flagged semantics
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "skill_timer.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
BAD_FIXTURE = FIXTURES / "run_f92f9d72f408a356.json"


# ---- Direct-call helpers (avoid subprocess overhead for validator tests) ----

sys.path.insert(0, str(SCRIPT.parent))
from skill_timer import (  # type: ignore[import-not-found]  # noqa: E402  # ty:ignore[unresolved-import]
    VALID_MODES,
    annotate_validation_status,
    escalate_status,
    resolve_work_window,
    validate_dimension_distribution,
    validate_timing_data,
)


def _base_run(skill: str = "plan-reviewer", run_total: float = 100.0) -> dict:
    return {
        "run_id": "0123456789abcdef",
        "skill_name": skill,
        "model": "claude-opus-4",
        "review_mode": "FULL",
        "start_iso": "2026-05-17T00:00:00+00:00",
        "end_iso": "2026-05-17T00:01:40+00:00",
        "start_epoch": 1000.0,
        "end_epoch": 1000.0 + run_total,
        "duration_seconds": run_total,
        "status": "completed",
        "checkpoints": [],
        "dimension_timings": [],
    }


def _wrap_dim(name: str, dur: float, mode: str = "checkpoint") -> dict:
    entry: dict = {
        "dimension": name,
        "duration_seconds": dur,
        "mode": mode,
    }
    if dur >= 0:
        entry["start_epoch"] = 1010.0
        entry["end_epoch"] = 1010.0 + dur
    return entry


# ============================================================================
# Distribution validator
# ============================================================================


def test_dim_uniformity_suspect_fires_on_uniform_short_durations():
    data = _base_run()
    data["dimension_timings"] = [_wrap_dim(f"d{i}", 1.10) for i in range(8)]
    alerts = validate_dimension_distribution(data)
    types = {a["type"] for a in alerts}
    assert "dim_uniformity_suspect" in types


def test_dim_uniformity_does_not_fire_when_above_max_mean():
    data = _base_run()
    data["dimension_timings"] = [_wrap_dim(f"d{i}", 7.0) for i in range(8)]  # > 5s
    alerts = validate_dimension_distribution(data)
    assert "dim_uniformity_suspect" not in {a["type"] for a in alerts}


def test_dim_floor_violation_fires_per_skill_floor():
    data = _base_run("plan-reviewer")
    data["dimension_timings"] = [_wrap_dim("executability", 2.0)]  # floor 5s
    alerts = validate_dimension_distribution(data)
    assert "dim_floor_violation" in {a["type"] for a in alerts}


def test_dim_coverage_severe_replay_against_legacy_fixture():
    data = json.loads(BAD_FIXTURE.read_text())
    alerts = validate_dimension_distribution(data)
    types = {a["type"] for a in alerts}
    # The fixture trips at minimum: uniformity, floor, post_review_gap.
    assert "dim_uniformity_suspect" in types
    assert "dim_floor_violation" in types
    # status escalates because of >=3 warnings
    assert escalate_status(data, alerts) == "instrumentation_failed"


def test_test_mode_bypasses_floor_and_uniformity():
    os.environ["TIMING_TEST_MODE"] = "1"
    try:
        data = _base_run()
        data["dimension_timings"] = [_wrap_dim(f"d{i}", 0.05) for i in range(8)]
        alerts = validate_dimension_distribution(data)
        types = {a["type"] for a in alerts}
        assert "dim_floor_violation" not in types
        assert "dim_uniformity_suspect" not in types
    finally:
        del os.environ["TIMING_TEST_MODE"]


def test_disable_distribution_validator_returns_empty():
    os.environ["TIMING_DISABLE_DISTRIBUTION_VALIDATOR"] = "1"
    try:
        data = _base_run()
        data["dimension_timings"] = [_wrap_dim(f"d{i}", 0.05) for i in range(8)]
        alerts = validate_dimension_distribution(data)
        assert alerts == []
    finally:
        del os.environ["TIMING_DISABLE_DISTRIBUTION_VALIDATOR"]


def test_resolve_work_window_falls_back_through_hierarchy():
    data = _base_run(run_total=200.0)
    data["checkpoints"] = [
        {"name": "skill_loaded", "elapsed_seconds": 10.0},
        {"name": "review_complete", "elapsed_seconds": 60.0},
    ]
    seconds, source = resolve_work_window(data)
    assert source == "skill_loaded_to_review_complete"
    assert seconds == pytest.approx(50.0)


def test_resolve_work_window_prefers_finalize_pre_write():
    data = _base_run(run_total=200.0)
    data["checkpoints"] = [{"name": "skill_loaded", "elapsed_seconds": 10.0}]
    data["finalize"] = {"pre_write_epoch": 1000.0 + 80.0}
    seconds, source = resolve_work_window(data)
    assert source == "skill_loaded_to_finalize_pre_write"
    assert seconds == pytest.approx(70.0)


# ============================================================================
# Mode enum semantics
# ============================================================================


def test_validate_timing_data_rejects_unknown_mode():
    data = _base_run()
    data["dimension_timings"] = [_wrap_dim("d1", 1.0, mode="bogus")]
    ok, errors = validate_timing_data(data)
    assert not ok
    assert any("unknown mode" in e for e in errors)


def test_unavailable_mode_allows_negative_duration():
    data = _base_run()
    data["dimension_timings"] = [_wrap_dim("d1", -1.0, mode="unavailable")]
    ok, errors = validate_timing_data(data)
    assert ok, errors


def test_not_requested_excluded_from_counted_total():
    data = _base_run()
    data["dimension_timings"] = [
        _wrap_dim("counted", 10.0, mode="checkpoint"),
        _wrap_dim("skipped", 0.0, mode="not-requested"),
    ]
    alerts = validate_dimension_distribution(data)
    annotate_validation_status(data, alerts)
    not_req = next(d for d in data["dimension_timings"] if d["dimension"] == "skipped")
    assert not_req["validation_status"] == "not_requested"


def test_failed_mode_marked_failed():
    data = _base_run()
    data["dimension_timings"] = [_wrap_dim("d1", -1.0, mode="failed")]
    alerts = validate_dimension_distribution(data)
    annotate_validation_status(data, alerts)
    assert data["dimension_timings"][0]["validation_status"] == "failed"


def test_valid_modes_table_complete():
    expected = {
        "checkpoint",
        "self-report",
        "self-report-flagged",
        "coordinator",
        "inline",
        "wrap",
        "failed",
        "validation-failed",
        "unavailable",
        "not-requested",
    }
    assert set(VALID_MODES.keys()) == expected


# ============================================================================
# wrap / finalize / replay subcommands (subprocess)
# ============================================================================


def _run(
    args: list[str], cwd: Path, env_extra: dict | None = None, test_mode: bool = True
) -> subprocess.CompletedProcess[str]:
    env = {**os.environ}
    if test_mode:
        env["TIMING_TEST_MODE"] = "1"
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _start_run(tmp: Path, skill: str = "plan-reviewer") -> str:
    res = _run(
        [
            "start",
            "--skill",
            skill,
            "--target",
            "x.md",
            "--model",
            "claude-opus-4",
            "--mode",
            "FULL",
        ],
        cwd=tmp,
    )
    assert res.returncode == 0, res.stderr
    m = re.search(r"TIMING_RUN_ID=([a-f0-9]{16})", res.stdout)
    assert m, res.stdout
    return m.group(1)


def test_wrap_records_dimension_with_evidence(tmp_path: Path):
    rid = _start_run(tmp_path)
    evidence = tmp_path / "ev.txt"
    evidence.write_text("x" * 200)
    res = _run(
        ["wrap", "--run-id", rid, "--dimension", "executability", "--evidence", str(evidence)],
        cwd=tmp_path,
    )
    assert res.returncode == 0, res.stderr
    assert "WRAP_STATUS=recorded" in res.stdout
    timing_file = tmp_path / "reviews" / ".timing-data" / f"skill-timer-{rid}.json"
    data = json.loads(timing_file.read_text())
    assert any(
        d["mode"] == "wrap" and d["dimension"] == "executability" for d in data["dimension_timings"]
    )


def test_wrap_rejects_undersized_evidence(tmp_path: Path):
    rid = _start_run(tmp_path)
    tiny = tmp_path / "tiny.txt"
    tiny.write_text("nope")
    res = _run(
        ["wrap", "--run-id", rid, "--dimension", "d1", "--evidence", str(tiny)], cwd=tmp_path
    )
    assert res.returncode == 4
    assert "evidence_too_small" in res.stdout


def test_wrap_chains_start_from_previous_wrap(tmp_path: Path):
    rid = _start_run(tmp_path)
    ev = tmp_path / "ev.txt"
    ev.write_text("x" * 200)
    _run(["wrap", "--run-id", rid, "--dimension", "a", "--evidence", str(ev)], cwd=tmp_path)
    _run(["wrap", "--run-id", rid, "--dimension", "b", "--evidence", str(ev)], cwd=tmp_path)
    timing_file = tmp_path / "reviews" / ".timing-data" / f"skill-timer-{rid}.json"
    data = json.loads(timing_file.read_text())
    a_end = data["dimension_timings"][0]["end_epoch"]
    b_start = data["dimension_timings"][1]["start_epoch"]
    assert b_start == pytest.approx(a_end, abs=0.01)


def test_finalize_pre_write_requires_review_artifact(tmp_path: Path):
    rid = _start_run(tmp_path)
    res = _run(["finalize", "--run-id", rid, "--stage", "pre_write"], cwd=tmp_path)
    assert res.returncode == 1
    assert "review-artifact" in res.stderr


def test_finalize_records_pre_and_post_write(tmp_path: Path):
    rid = _start_run(tmp_path)
    artifact = tmp_path / "out.md"
    res = _run(
        ["finalize", "--run-id", rid, "--stage", "pre_write", "--review-artifact", str(artifact)],
        cwd=tmp_path,
    )
    assert res.returncode == 0, res.stderr
    res = _run(["finalize", "--run-id", rid, "--stage", "post_write"], cwd=tmp_path)
    assert res.returncode == 0, res.stderr
    timing_file = tmp_path / "reviews" / ".timing-data" / f"skill-timer-{rid}.json"
    data = json.loads(timing_file.read_text())
    assert "pre_write_epoch" in data["finalize"]
    assert "post_write_epoch" in data["finalize"]
    assert data["finalize"]["post_write_epoch"] >= data["finalize"]["pre_write_epoch"]


def test_replay_against_bad_fixture_exits_4(tmp_path: Path):
    # Replay must run WITHOUT TIMING_TEST_MODE so distribution validators fire.
    res = _run(["replay", "--fixture", str(BAD_FIXTURE)], cwd=tmp_path, test_mode=False)
    assert res.returncode == 4
    assert "instrumentation_failed" in res.stdout


def test_replay_against_good_fixture_exits_0(tmp_path: Path):
    good = tmp_path / "good.json"
    payload = _base_run(run_total=300.0)
    payload["dimension_timings"] = [
        _wrap_dim(name, dur, mode="wrap")
        for name, dur in [
            ("executability", 18.0),
            ("completeness", 22.0),
            ("success_criteria", 17.0),
            ("scope", 16.0),
            ("dependencies", 19.0),
            ("decomposition", 24.0),
            ("context", 21.0),
            ("risk_awareness", 20.0),
        ]
    ]
    good.write_text(json.dumps(payload))
    res = _run(["replay", "--fixture", str(good)], cwd=tmp_path)
    assert res.returncode == 0, f"stdout={res.stdout}\nstderr={res.stderr}"
