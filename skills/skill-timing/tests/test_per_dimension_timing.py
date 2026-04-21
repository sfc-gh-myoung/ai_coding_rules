"""Regression tests for per-dimension timing enforcement.

Covers five acceptance cases from plans/per-dimension-timing-enforcement-plan.md
Phase 1 Task 1.5:

    (a) Explicit --dimension-timings path -> PER_DIMENSION_STATUS=present
    (b) Auto-derive path                  -> PER_DIMENSION_STATUS=derived
    (c) Silent-omission warning           -> WARNING + PER_DIMENSION_STATUS=missing
    (d) Both flags supplied               -> explicit wins, WARNING emitted
    (e) Malformed checkpoint names        -> ignored with WARNING
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "skills" / "skill-timing" / "scripts" / "skill_timing.py"

DIMENSIONS = [
    "actionability",
    "rule_size",
    "parsability",
    "completeness",
    "consistency",
    "cross_agent",
]


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Invoke the skill_timing.py CLI with given args."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def start_run(tmp_path: Path, target: str = "rules/test.md") -> str:
    """Start a timing run, return run_id."""
    result = run(
        [
            "start",
            "--skill",
            "rule-reviewer",
            "--target",
            target,
            "--model",
            "claude-opus-4-7",
            "--mode",
            "FULL",
        ],
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stderr
    m = re.search(r"TIMING_RUN_ID=([a-f0-9]{16})", result.stdout)
    assert m is not None, f"run_id not found in: {result.stdout}"
    return m.group(1)


def record_checkpoint(tmp_path: Path, run_id: str, name: str) -> None:
    result = run(["checkpoint", "--run-id", run_id, "--name", name], cwd=tmp_path)
    assert result.returncode == 0, result.stderr


def end_run(
    tmp_path: Path, run_id: str, extra_args: list[str] | None = None
) -> subprocess.CompletedProcess:
    output_file = tmp_path / "review.md"
    output_file.touch()
    args = [
        "end",
        "--run-id",
        run_id,
        "--output-file",
        str(output_file),
        "--skill",
        "rule-reviewer",
    ]
    if extra_args:
        args.extend(extra_args)
    return run(args, cwd=tmp_path)


def load_completed(tmp_path: Path, run_id: str) -> dict:
    path = tmp_path / "reviews" / ".timing-data" / f"skill-timing-{run_id}-complete.json"
    assert path.exists(), f"completed file missing: {path}"
    return json.loads(path.read_text())


@pytest.fixture(autouse=True)
def _cwd_isolation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    yield


# ---------------------------------------------------------------------------
# (a) explicit --dimension-timings
# ---------------------------------------------------------------------------
def test_explicit_dimension_timings_sets_present(tmp_path):
    run_id = start_run(tmp_path)
    time.sleep(1.1)
    payload = [
        {"dimension": d, "duration_seconds": 1.0 + i * 0.1, "mode": "self-report"}
        for i, d in enumerate(DIMENSIONS)
    ]
    result = end_run(tmp_path, run_id, ["--dimension-timings", json.dumps(payload)])
    assert "PER_DIMENSION_STATUS=present" in result.stdout
    data = load_completed(tmp_path, run_id)
    assert data["per_dimension_status"] == "present"
    assert len(data["dimension_timings"]) == 6


# ---------------------------------------------------------------------------
# (b) auto-derive from checkpoints
# ---------------------------------------------------------------------------
def test_auto_dimension_timings_derived(tmp_path):
    run_id = start_run(tmp_path)
    for d in DIMENSIONS:
        record_checkpoint(tmp_path, run_id, f"dim_{d}_start")
        time.sleep(0.05)
        record_checkpoint(tmp_path, run_id, f"dim_{d}_end")
    time.sleep(1.1)  # ensure total > 1s
    result = end_run(tmp_path, run_id, ["--auto-dimension-timings"])
    assert "PER_DIMENSION_STATUS=derived" in result.stdout
    data = load_completed(tmp_path, run_id)
    assert data["per_dimension_status"] == "derived"
    assert len(data["dimension_timings"]) == 6
    for dt in data["dimension_timings"]:
        assert dt["mode"] == "checkpoint"
        assert dt["duration_seconds"] > 0


# ---------------------------------------------------------------------------
# (c) silent-omission warning
# ---------------------------------------------------------------------------
def test_silent_omission_emits_warning(tmp_path):
    run_id = start_run(tmp_path)
    record_checkpoint(tmp_path, run_id, "dim_actionability_start")
    time.sleep(0.05)
    record_checkpoint(tmp_path, run_id, "dim_actionability_end")
    time.sleep(1.1)
    result = end_run(tmp_path, run_id)
    assert "WARNING" in result.stderr
    assert "dim_* checkpoints found" in result.stderr
    assert "PER_DIMENSION_STATUS=missing" in result.stdout
    data = load_completed(tmp_path, run_id)
    assert data["per_dimension_status"] == "missing"
    assert "dimension_timings" not in data or not data["dimension_timings"]


# ---------------------------------------------------------------------------
# (d) explicit + auto-derive -> explicit wins
# ---------------------------------------------------------------------------
def test_explicit_wins_over_auto(tmp_path):
    run_id = start_run(tmp_path)
    for d in DIMENSIONS:
        record_checkpoint(tmp_path, run_id, f"dim_{d}_start")
        time.sleep(0.02)
        record_checkpoint(tmp_path, run_id, f"dim_{d}_end")
    time.sleep(1.1)
    payload = [
        {"dimension": d, "duration_seconds": 9.99, "mode": "self-report"} for d in DIMENSIONS
    ]
    result = end_run(
        tmp_path,
        run_id,
        ["--dimension-timings", json.dumps(payload), "--auto-dimension-timings"],
    )
    assert "PER_DIMENSION_STATUS=present" in result.stdout
    assert "explicit --dimension-timings wins" in result.stderr
    data = load_completed(tmp_path, run_id)
    # explicit payload (9.99s) should be retained, not auto-derived value
    assert all(dt["duration_seconds"] == 9.99 for dt in data["dimension_timings"])


# ---------------------------------------------------------------------------
# (e) malformed checkpoint names -> ignored with WARNING
# ---------------------------------------------------------------------------
def test_malformed_checkpoint_names_warn(tmp_path):
    run_id = start_run(tmp_path)
    # Valid pair plus malformed name
    record_checkpoint(tmp_path, run_id, "dim_actionability_start")
    time.sleep(0.02)
    record_checkpoint(tmp_path, run_id, "dim_actionability_end")
    record_checkpoint(tmp_path, run_id, "dim_BADNAME")  # malformed - no phase suffix
    time.sleep(1.1)
    result = end_run(tmp_path, run_id, ["--auto-dimension-timings"])
    assert "PER_DIMENSION_STATUS=derived" in result.stdout
    assert "Malformed dim_* checkpoint" in result.stderr
    data = load_completed(tmp_path, run_id)
    # Only the valid pair should be derived
    assert len(data["dimension_timings"]) == 1
    assert data["dimension_timings"][0]["dimension"] == "actionability"
