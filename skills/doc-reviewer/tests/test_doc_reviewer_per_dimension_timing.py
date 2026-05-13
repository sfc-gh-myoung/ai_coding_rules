"""Per-dimension timing coverage test for doc-reviewer.

Verifies that bracketing each of the 6 scored documentation dimensions with
`dim_<name>_start` / `dim_<name>_end` checkpoint pairs and calling
`skill_timing.py end --auto-dimension-timings` produces a completed JSON
record with 6 derived dimension timings.

Mirrors `skills/rule-reviewer/tests/test_gate7_integration.py` adapted for
doc-reviewer's dimension set.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "skills" / "skill-timing" / "scripts" / "skill_timing.py"

SCORED_DIMENSIONS = [
    "accuracy",
    "completeness",
    "clarity",
    "structure",
    "staleness",
    "consistency",
]


def sh(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run skill_timing.py with given args in specified directory."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture(autouse=True)
def _cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    yield


def test_per_dimension_timing_derived(tmp_path):
    """All 6 dimensions produce `derived` per-dimension timings."""
    target = "README.md"
    output_file = tmp_path / "reviews" / "doc-reviews" / "mock-review.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("# Mock Review placeholder\n")

    r = sh(
        [
            "start",
            "--skill",
            "doc-reviewer",
            "--target",
            target,
            "--model",
            "claude-sonnet-45",
            "--mode",
            "FULL",
        ],
        cwd=tmp_path,
    )
    assert r.returncode == 0, r.stderr
    match = re.search(r"TIMING_RUN_ID=([a-f0-9]{16})", r.stdout)
    assert match is not None, "TIMING_RUN_ID not found in output"
    run_id = match.group(1)

    sh(["checkpoint", "--run-id", run_id, "--name", "skill_loaded"], cwd=tmp_path)

    for dim in SCORED_DIMENSIONS:
        sh(["checkpoint", "--run-id", run_id, "--name", f"dim_{dim}_start"], cwd=tmp_path)
        time.sleep(0.05)
        sh(["checkpoint", "--run-id", run_id, "--name", f"dim_{dim}_end"], cwd=tmp_path)

    sh(["checkpoint", "--run-id", run_id, "--name", "review_complete"], cwd=tmp_path)

    time.sleep(1.1)
    r = sh(
        [
            "end",
            "--run-id",
            run_id,
            "--output-file",
            str(output_file),
            "--skill",
            "doc-reviewer",
            "--format",
            "markdown",
            "--auto-dimension-timings",
        ],
        cwd=tmp_path,
    )
    assert r.returncode in (0, 2, 3), r.stderr

    completed = tmp_path / "reviews" / ".timing-data" / f"skill-timing-{run_id}-complete.json"
    assert completed.exists(), "completed JSON not written"
    data = json.loads(completed.read_text())

    assert data["per_dimension_status"] == "derived"
    assert len(data["dimension_timings"]) == 6

    captured = {entry["dimension"] for entry in data["dimension_timings"]}
    assert captured == set(SCORED_DIMENSIONS), (
        f"Missing dimensions: {set(SCORED_DIMENSIONS) - captured}"
    )

    for entry in data["dimension_timings"]:
        assert entry["duration_seconds"] > 0
        assert entry["mode"] in {"checkpoint", "derived", "self-report"}
