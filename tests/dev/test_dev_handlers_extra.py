"""Extra unit tests for dev/ command handlers.

Covers:
- commands/dev/test.py: run_tests() function (lines 84-96)
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# dev/test.py — run_tests()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_run_tests_no_coverage_calls_pytest_with_tb_short(tmp_path: Path) -> None:
    """run_tests(coverage=False) calls pytest with --tb=short."""
    from ai_rules.commands.dev.test import run_tests

    calls: list = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    with patch("ai_rules.commands.dev.test.run", side_effect=fake_run):
        exit_code = run_tests(tmp_path, coverage=False)

    assert exit_code == 0
    assert len(calls) == 1
    assert "--tb=short" in calls[0]
    assert "--cov=src/ai_rules" not in calls[0]


@pytest.mark.unit
def test_run_tests_with_coverage_passes_cov_flags(tmp_path: Path) -> None:
    """run_tests(coverage=True) includes coverage flags in the pytest invocation."""
    from ai_rules.commands.dev.test import run_tests

    calls: list = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    with patch("ai_rules.commands.dev.test.run", side_effect=fake_run):
        exit_code = run_tests(tmp_path, coverage=True)

    assert exit_code == 0
    assert len(calls) == 1
    assert "--cov=src/ai_rules" in calls[0]
    assert "--cov-report=term-missing" in calls[0]


@pytest.mark.unit
def test_run_tests_returns_non_zero_exit_code_on_failure(tmp_path: Path) -> None:
    """run_tests propagates non-zero exit codes from pytest."""
    from ai_rules.commands.dev.test import run_tests

    def fake_run_fail(cmd, **kwargs):
        return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="")

    with patch("ai_rules.commands.dev.test.run", side_effect=fake_run_fail):
        exit_code = run_tests(tmp_path, coverage=False)

    assert exit_code == 1
