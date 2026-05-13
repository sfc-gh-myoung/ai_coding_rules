"""Integration test for rule-reviewer → skill-timing per-dimension timing round-trip.

Verifies that the Quick Reference from skills/rule-reviewer/SKILL.md produces a review-style
output file containing:
    - A `### Per-Dimension Timing` subsection
    - A 6-row dimension table
    - A non-zero total duration
    - PER_DIMENSION_STATUS=derived in the timing-end stdout

This simulates the minimum contract that Quality Gate 7 depends on.
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
    "actionability",
    "rule_size",
    "parsability",
    "completeness",
    "consistency",
    "cross_agent",
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


def test_rule_reviewer_quick_reference_roundtrip(tmp_path):
    """Simulate SKILL.md Quick Reference verbatim and assert Gate 7 requirements."""
    target = "rules/100-snowflake-core.md"
    output_file = tmp_path / "reviews" / "rule-reviews" / "mock-review.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("# Mock Review placeholder — timing will be appended\n")

    # 1. Start
    r = sh(
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
    assert r.returncode == 0
    match = re.search(r"TIMING_RUN_ID=([a-f0-9]{16})", r.stdout)
    assert match is not None, "TIMING_RUN_ID not found in output"
    run_id = match.group(1)

    # 2. Bootstrap checkpoint
    sh(["checkpoint", "--run-id", run_id, "--name", "skill_loaded"], cwd=tmp_path)

    # 3. Per-dimension checkpoint pairs
    for dim in SCORED_DIMENSIONS:
        sh(["checkpoint", "--run-id", run_id, "--name", f"dim_{dim}_start"], cwd=tmp_path)
        time.sleep(0.05)
        sh(["checkpoint", "--run-id", run_id, "--name", f"dim_{dim}_end"], cwd=tmp_path)

    # 4. Aggregate checkpoint
    sh(["checkpoint", "--run-id", run_id, "--name", "review_complete"], cwd=tmp_path)

    # 5. End with --auto-dimension-timings + markdown format
    time.sleep(1.1)
    r = sh(
        [
            "end",
            "--run-id",
            run_id,
            "--output-file",
            str(output_file),
            "--skill",
            "rule-reviewer",
            "--format",
            "markdown",
            "--auto-dimension-timings",
        ],
        cwd=tmp_path,
    )
    assert r.returncode in (0, 2, 3), r.stderr  # 2/3 = alert exit codes, not script errors

    # Append the generated markdown table to the output file (what the agent would do).
    output_file.write_text(output_file.read_text() + "\n" + r.stdout)

    # --- Assertions covering Gate 7 contract ---
    content = output_file.read_text()
    assert "### Per-Dimension Timing" in content, "Gate 7: heading missing"

    # 6 dimension rows: each should appear as a table row
    for dim in SCORED_DIMENSIONS:
        assert re.search(rf"^\| {dim} \|", content, re.MULTILINE), f"Gate 7: row for {dim} missing"

    # Total row should carry a non-zero duration
    total_match = re.search(
        r"\| \*\*Total \(dimension work\)\*\* \| \*\*(\d+\.\d+)s\*\* \|", content
    )
    assert total_match is not None, "Gate 7: total row missing or malformed"
    total_seconds = float(total_match.group(1))
    assert total_seconds > 0, f"Gate 7: total duration not positive ({total_seconds})"

    # Completed JSON should record derived status
    completed = tmp_path / "reviews" / ".timing-data" / f"skill-timing-{run_id}-complete.json"
    assert completed.exists()
    data = json.loads(completed.read_text())
    assert data["per_dimension_status"] == "derived"
    assert len(data["dimension_timings"]) == 6
