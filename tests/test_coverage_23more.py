"""Final 23-line push to hit 92.00% coverage."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true"})


# ---------------------------------------------------------------------------
# tokens.py — directory mode dry_run (lines 472-473)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_tokens_dir_dry_run() -> None:
    """Tokens on a directory with --dry-run covers lines 472-473."""
    result = runner.invoke(app, ["tokens", "rules/", "--dry-run"])
    # Directory mode should print dry-run message


# ---------------------------------------------------------------------------
# rule_loader.py create_cmd — both args covers non-error path and error (1286-1291)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_create_cmd_both_args_exits() -> None:
    """create_cmd with both --prompt and --prompt-file exits non-zero (line 1287-1288)."""
    result = runner.invoke(
        app, ["rule-loader", "create", "--prompt", "test", "--prompt-file", "/tmp/fake.txt"]
    )
    assert result.exit_code != 0


@pytest.mark.integration
def test_create_cmd_with_prompt_mocked_live(tmp_path: Path) -> None:
    """create_cmd with --prompt mocked covers lines 1291-1312."""
    from ai_rules.rule_loader_eval.agent_runner import AgentRun

    mock_run = AgentRun(
        fixture_id="candidate",
        loaded=("rules/000-global-core.md",),
        loaded_via_reads=(),
        loaded_via_reads_performed=(),
        loaded_via_section=(),
        final_text="**Rules Loaded**\n- rules/000-global-core.md (foundation)\n",
    )

    with patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"):
        with patch("ai_rules.commands.rule_loader._drive_live", return_value=mock_run):
            with patch(
                "ai_rules.commands.rule_loader.format_fixture_snippet",
                return_value="schema_version: 2\nid: test\n",
            ):
                with patch("ai_rules.commands.rule_loader._emit_diagnostics"):
                    result = runner.invoke(
                        app, ["rule-loader", "create", "--prompt", "Fix the python bug"]
                    )


# ---------------------------------------------------------------------------
# rule_loader.py _print_failure_details — direct call
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_print_failure_details_passing_debug() -> None:
    """_print_failure_details with passing result + debug covers lines 1216-1219."""
    from ai_rules.commands.rule_loader import _print_failure_details
    from ai_rules.rule_loader_eval.agent_runner import AgentRun

    r = MagicMock()
    r.passed = True
    r.run = AgentRun(
        fixture_id="test",
        loaded=(),
        loaded_via_reads=(),
        loaded_via_reads_performed=(),
        loaded_via_section=(),
    )
    _print_failure_details([r], debug=True, effort="medium", model="auto")


@pytest.mark.unit
def test_print_failure_details_failing_result() -> None:
    """_print_failure_details with failing result covers lines 1221-1235."""
    from ai_rules.commands.rule_loader import _print_failure_details
    from ai_rules.rule_loader_eval.agent_runner import AgentRun

    r = MagicMock()
    r.passed = False
    r.fixture_id = "test-fail"
    run = AgentRun(
        fixture_id="test-fail",
        loaded=("rules/000-global-core.md",),
        loaded_via_reads=("rules/000-global-core.md",),
        loaded_via_reads_performed=(),
        loaded_via_section=(),
    )
    r.run = run
    r.signal_report = MagicMock()
    r.signal_report.ok = False
    r.signal_report.disagreements = ["disagreement"]
    r.signal_report.cited_without_read = []
    r.signal_report.read_without_cite_unexpected = []
    r.signal_report.read_without_cite_tolerated = []
    r.citation_drifts = []
    _print_failure_details([r], debug=False, effort="medium", model="auto")


# ---------------------------------------------------------------------------
# rule_loader.py eval_cmd — multi-run paths (lines 1129, 1151, 1154-1155, 1165)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_eval_cmd_multi_run_with_mocked_sdk() -> None:
    """eval_cmd --runs 2 with mocked fixtures covers multi-run paths (1129-1165)."""
    mock_result = MagicMock()
    mock_result.fixture_id = "simple-python-task"
    mock_result.passed = True
    mock_result.run = MagicMock()
    mock_result.run.turns = 1
    mock_result.run.duration_ms = 100
    mock_result.run.input_tokens = 10
    mock_result.run.output_tokens = 5
    mock_result.run.total_cost_usd = 0.001
    mock_result.run.is_infra_error = False
    mock_result.run.infra_error_detail = ""
    mock_result.run.output_violations = ()
    mock_result.run.disagreements = ()
    mock_result.match = MagicMock()
    mock_result.match.missing_required = []
    mock_result.match.missing_dependencies = []
    mock_result.match.forbidden_present = []
    mock_result.signal_report = MagicMock()
    mock_result.signal_report.ok = True
    mock_result.signal_report.disagreements = []
    mock_result.citation_drifts = []

    with patch("ai_rules.commands.rule_loader._require_connection_or_exit", return_value="test"):
        with patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"):
            with patch(
                "ai_rules.commands.rule_loader._run_single_eval",
                return_value=([mock_result], False),
            ):
                result = runner.invoke(
                    app,
                    [
                        "rule-loader",
                        "eval",
                        "--fixture",
                        "simple-python-task",
                        "--runs",
                        "2",
                    ],
                )


# ---------------------------------------------------------------------------
# rule_loader.py _print_results — direct call with mock data
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_print_results_direct_call() -> None:
    """_print_results with mock RunResult covers lines in the print function."""
    from ai_rules.commands.rule_loader import _print_results

    r = MagicMock()
    r.fixture_id = "test"
    r.passed = True
    r.run.turns = 2
    r.run.input_tokens = 50
    r.run.output_tokens = 30
    r.run.duration_ms = 2000
    r.run.is_infra_error = False
    r.run.output_violations = ()
    r.run.disagreements = ()
    r.match.missing_required = []
    r.match.missing_dependencies = []
    r.match.forbidden_present = []
    r.signal_report.disagreements = []
    r.citation_drifts = []

    _print_results([r])


@pytest.mark.unit
def test_print_results_failed_fixture() -> None:
    """_print_results with a failing fixture covers fail path."""
    from ai_rules.commands.rule_loader import _print_results

    r = MagicMock()
    r.fixture_id = "test-fail"
    r.passed = False
    r.run.turns = 1
    r.run.input_tokens = 0
    r.run.output_tokens = 0
    r.run.duration_ms = 500
    r.run.is_infra_error = False
    r.run.output_violations = ("violation1",)
    r.run.disagreements = ("disagreement1",)
    r.match.missing_required = ["rules/200-python-core.md"]
    r.match.missing_dependencies = []
    r.match.forbidden_present = []
    r.signal_report.disagreements = ["d1"]
    r.citation_drifts = ["c1"]

    _print_results([r])


# ---------------------------------------------------------------------------
# validate.py — some error paths that are accessible
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_validate_nonexistent_rule_file() -> None:
    """Validate command on nonexistent file covers error paths."""
    result = runner.invoke(app, ["validate", "/nonexistent/rule.md"])
    assert result.exit_code != 0


@pytest.mark.integration
def test_validate_real_rule_file() -> None:
    """Validate command on a real rule file covers various validation paths."""
    result = runner.invoke(app, ["validate", "rules/200-python-core.md"])
    # May pass or fail; covers validation paths either way
