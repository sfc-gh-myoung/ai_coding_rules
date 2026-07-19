"""Tests for the ai-rules rule-loader CLI sub-app."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})


@pytest.fixture(scope="module")
def project_root() -> Path:
    """Return the repo root."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("project root not found")


def test_cli_help() -> None:
    """Sub-app help lists current commands."""
    result = runner.invoke(app, ["rule-loader", "--help"])
    assert result.exit_code == 0
    # Help lists `validate` (verb only). Use a regex word boundary check
    # to avoid spurious matches against substrings like 'validates' or other rows.
    import re

    assert re.search(r"\bvalidate\b", result.output)
    assert "eval" in result.output
    assert "create" in result.output
    assert "refresh" in result.output
    assert "doctor" in result.output
    # The retired single-fixture seed command must NOT appear
    assert "seed-fixture" not in result.output


@pytest.mark.integration
def test_validate_fixtures_passes(project_root: Path) -> None:
    """`validate` runs the invariant against committed fixtures."""
    result = runner.invoke(app, ["rule-loader", "validate"])
    assert result.exit_code == 0, result.output


@pytest.mark.integration
def test_validate_help_omits_progress_flag() -> None:
    """`validate --help` no longer exposes --progress/-P/--no-progress (Phase 3)."""
    result = runner.invoke(app, ["rule-loader", "validate", "--help"])
    assert result.exit_code == 0
    assert "--progress" not in result.output
    assert "--no-progress" not in result.output


@pytest.mark.integration
def test_refresh_all_help_omits_progress_flag() -> None:
    """`refresh-all --help` no longer exposes --progress/-P/--no-progress (Phase 3)."""
    result = runner.invoke(app, ["rule-loader", "refresh-all", "--help"])
    assert result.exit_code == 0
    assert "--progress" not in result.output
    assert "--no-progress" not in result.output


@pytest.mark.unit
def test_refresh_all_out_dir_help_mentions_env_var_and_precedence() -> None:
    """`refresh-all --help` documents AI_RULES_RESULTS_DIR and CLI > env precedence."""
    result = runner.invoke(app, ["rule-loader", "refresh-all", "--help"])
    assert result.exit_code == 0
    assert "AI_RULES_RESULTS_DIR" in result.output
    assert "CLI" in result.output or ">" in result.output


@pytest.mark.integration
def test_eval_help_omits_progress_flag() -> None:
    """`eval --help` no longer exposes --progress/-P/--no-progress (Phase 3).

    Note: --progressive is a DIFFERENT flag (progressive rule loading) and is expected.
    """
    result = runner.invoke(app, ["rule-loader", "eval", "--help"])
    assert result.exit_code == 0
    # Check the exact old flags, not substring of --progressive
    assert "--progress " not in result.output  # trailing space distinguishes from --progressive
    assert "--no-progress" not in result.output
    assert "-P " not in result.output or "--progressive" in result.output


@pytest.mark.integration
def test_refresh_help_omits_progress_flag() -> None:
    """`refresh --help` no longer exposes --progress/-P/--no-progress (Phase 3)."""
    result = runner.invoke(app, ["rule-loader", "refresh", "--help"])
    assert result.exit_code == 0
    assert "--progress" not in result.output
    assert "--no-progress" not in result.output


@pytest.mark.unit
def test_progress_symbols_removed_from_rule_loader_module() -> None:
    """ProgressTracker/ProgressMode/resolve_progress_mode are deleted (Phase 3)."""
    import ai_rules.commands.rule_loader as _rl

    assert not hasattr(_rl, "ProgressTracker")
    assert not hasattr(_rl, "ProgressMode")
    assert not hasattr(_rl, "resolve_progress_mode")


@pytest.mark.integration
def test_list_fixtures_renders_table(project_root: Path) -> None:
    """`list` prints a table including a Deps column."""
    result = runner.invoke(app, ["rule-loader", "list"])
    assert result.exit_code == 0, result.output
    assert "ID" in result.output
    assert "Deps" in result.output


@pytest.mark.integration
def test_doctor_runs(project_root: Path) -> None:
    """Doctor exits cleanly when SDK matches pin (or 3 on mismatch)."""
    result = runner.invoke(app, ["rule-loader", "doctor"])
    assert result.exit_code in {0, 3}, result.output


# ---------------------------------------------------------------------------
# create / refresh prompt extraction
# ---------------------------------------------------------------------------


def test_read_prompt_happy_path(tmp_path: Path) -> None:
    """`read_prompt` returns the prompt string from a fully-validated fixture YAML."""
    from ai_rules.rule_loader_eval.fixtures import read_prompt

    fixture = tmp_path / "refresh.yaml"
    fixture.write_text(
        "schema_version: 2\n"
        "updated: 2026-05-16T12:00:00-07:00\n"
        "id: simple-test\n"
        "description: A test fixture\n"
        "variant: simple\n"
        "prompt: |\n"
        "  Set up a cortex-search service over our document corpus.\n"
        "expected:\n"
        "  required: [rules/999-test-core.md, rules/116-snowflake-cortex-search.md]\n"
        "  dependencies: [rules/100-snowflake-core.md]\n"
        "  forbidden: []\n"
        "  optional: []\n"
        "trigger_evidence:\n"
        "  kw: [cortex-search]\n",
        encoding="utf-8",
    )
    assert "cortex-search service" in read_prompt(fixture)


def test_read_prompt_partial_fixture(tmp_path: Path) -> None:
    """`read_prompt` succeeds when only `prompt:` is present."""
    from ai_rules.rule_loader_eval.fixtures import read_prompt

    fixture = tmp_path / "iterate.yaml"
    fixture.write_text(
        "prompt: |\n  Build a Streamlit dashboard for billing telemetry.\n",
        encoding="utf-8",
    )
    assert "Streamlit dashboard" in read_prompt(fixture)


def test_create_requires_prompt_or_prompt_file() -> None:
    """`create` rejects calls without --prompt or --prompt-file."""
    result = runner.invoke(app, ["rule-loader", "create"])
    assert result.exit_code != 0
    assert "exactly one" in result.output


def test_create_mutual_exclusion(tmp_path: Path) -> None:
    """`create --prompt` and `--prompt-file` together are rejected."""
    f = tmp_path / "p.txt"
    f.write_text("hi", encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "rule-loader",
            "create",
            "--prompt",
            "hi",
            "--prompt-file",
            str(f),
        ],
    )
    assert result.exit_code != 0


def test_refresh_missing_file(tmp_path: Path) -> None:
    """`refresh` on a non-existent fixture errors cleanly."""
    missing = tmp_path / "does-not-exist.yaml"
    result = runner.invoke(app, ["rule-loader", "refresh", str(missing)])
    assert result.exit_code != 0
    assert "fixture file not found" in result.output


# ---------------------------------------------------------------------------
# refresh-all (batch)
# ---------------------------------------------------------------------------


def _make_fixture_yaml(path: Path, fixture_id: str, prompt: str) -> None:
    path.write_text(
        f"id: {fixture_id}\nprompt: |\n  {prompt}\n",
        encoding="utf-8",
    )


def _make_summary(items, concurrency=1, wall=1.0):
    """Build a BatchSummary with a successful AgentRun per item."""
    from ai_rules.rule_loader_eval.agent_runner import AgentRun
    from ai_rules.rule_loader_eval.batch import BatchOutcome, BatchSummary

    outcomes = []
    for item in items:
        run = AgentRun(
            fixture_id=item.id,
            loaded=("rules/999-test-core.md",),
            loaded_via_reads=("rules/999-test-core.md",),
            loaded_via_reads_performed=(),
            loaded_via_section=("rules/999-test-core.md",),
            turns=3,
            duration_ms=500,
            model="auto",
            stop_reason="end_turn",
        )
        outcomes.append(BatchOutcome(item=item, run=run, error_type=None, error_message=None))
    return BatchSummary(concurrency=concurrency, outcomes=tuple(outcomes), wall_seconds=wall)


def test_refresh_all_defaults_to_all_when_neither_flag_given(
    tmp_path: Path, project_root: Path
) -> None:
    """Omitting both --glob and --all now defaults to --all (R6)."""
    from unittest.mock import patch

    # Mock the SDK + run_batch so we don't actually call the live agent. The
    # point of the test is the flag-resolution behavior, not the run.
    fx_path = tmp_path / "simple-test.yaml"
    _make_fixture_yaml(fx_path, "simple-test", "Set up a search service.")

    def _fake_run_batch(items, **kwargs):
        summary = _make_summary(items, wall=0.1)
        on_outcome = kwargs.get("on_outcome")
        if on_outcome is not None:
            for i, outcome in enumerate(summary.outcomes, start=1):
                on_outcome(outcome, i)
        return summary

    with (
        patch("ai_rules.rule_loader_eval.batch.run_batch", side_effect=_fake_run_batch),
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch(
            "ai_rules.commands.rule_loader.find_project_root",
            return_value=project_root,
        ),
        patch(
            "ai_rules.rule_loader_eval.batch.expand_glob",
            return_value=[fx_path],
        ),
    ):
        result = runner.invoke(app, ["rule-loader", "refresh-all"])
    # The legacy "provide exactly one of --glob or --all" error must NOT
    # appear; the new info line about defaulting must appear.
    assert "provide exactly one" not in result.output.lower()
    assert "no --glob or --all given" in result.output


def test_refresh_all_rejects_both_glob_and_all(tmp_path: Path) -> None:
    """Providing both --glob and --all exits with an error."""
    result = runner.invoke(
        app,
        [
            "rule-loader",
            "refresh-all",
            "--glob",
            "*.yaml",
            "--all",
        ],
    )
    assert result.exit_code != 0


def test_refresh_all_rejects_invalid_concurrency() -> None:
    """``--concurrency 0`` is rejected before SDK calls."""
    result = runner.invoke(
        app,
        ["rule-loader", "refresh-all", "--all", "--concurrency", "0"],
    )
    assert result.exit_code != 0


def test_refresh_all_help_lists_defaults() -> None:
    """``refresh-all --help`` lists the command and key defaults."""
    result = runner.invoke(app, ["rule-loader", "refresh-all", "--help"])
    assert result.exit_code == 0
    assert "refresh-all" in result.output or "Batch-capture" in result.output
    assert "25" in result.output
    assert "medium" in result.output
    assert "2" in result.output  # default concurrency


def test_refresh_all_help_listed_in_rule_loader_help() -> None:
    """``rule-loader --help`` lists the ``refresh-all`` command."""
    result = runner.invoke(app, ["rule-loader", "--help"])
    assert result.exit_code == 0
    assert "refresh-all" in result.output


def test_refresh_all_writes_files_and_summary(tmp_path: Path, project_root: Path) -> None:
    """Out-dir mode writes candidate YAML and summary.json for each succeeded fixture."""
    from unittest.mock import patch

    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir()
    fx_path = fixtures_dir / "simple-test.yaml"
    _make_fixture_yaml(fx_path, "simple-test", "Set up a search service.")

    out_dir = tmp_path / "out"
    items_captured = []

    def _fake_run_batch(items, **kwargs):
        items_captured.extend(items)
        summary = _make_summary(items, wall=1.5)
        on_outcome = kwargs.get("on_outcome")
        if on_outcome is not None:
            for i, outcome in enumerate(summary.outcomes, start=1):
                on_outcome(outcome, i)
        return summary

    with (
        patch("ai_rules.rule_loader_eval.batch.run_batch", side_effect=_fake_run_batch),
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch(
            "ai_rules.commands.rule_loader.find_project_root",
            return_value=project_root,
        ),
        patch(
            "ai_rules.rule_loader_eval.batch.expand_glob",
            return_value=[fx_path],
        ),
    ):
        result = runner.invoke(
            app,
            [
                "rule-loader",
                "refresh-all",
                "--all",
                "--concurrency",
                "1",
                "--out-dir",
                str(out_dir),
            ],
        )

    assert result.exit_code == 0, result.output
    assert (out_dir / "summary.json").exists()
    assert any(p.suffix == ".yaml" for p in out_dir.iterdir())


def test_refresh_all_stdout_stream_no_outdir(tmp_path: Path, project_root: Path) -> None:
    """Stdout mode prints YAML snippets; summary and failures go to stderr."""
    from unittest.mock import patch

    fx_path = tmp_path / "simple-test.yaml"
    _make_fixture_yaml(fx_path, "simple-test", "Set up a search service.")

    def _fake_run_batch(items, **kwargs):
        summary = _make_summary(items, wall=0.5)
        on_outcome = kwargs.get("on_outcome")
        if on_outcome is not None:
            for i, outcome in enumerate(summary.outcomes, start=1):
                on_outcome(outcome, i)
        return summary

    with (
        patch("ai_rules.rule_loader_eval.batch.run_batch", side_effect=_fake_run_batch),
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch(
            "ai_rules.commands.rule_loader.find_project_root",
            return_value=project_root,
        ),
        patch(
            "ai_rules.rule_loader_eval.batch.expand_glob",
            return_value=[fx_path],
        ),
    ):
        result = runner.invoke(
            app,
            ["rule-loader", "refresh-all", "--all"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0, result.output
    assert "# fixture:" in result.output or "schema_version" in result.output


def test_refresh_all_exit_one_on_partial_failure(tmp_path: Path, project_root: Path) -> None:
    """Exit code 1 when at least one fixture failed."""
    from unittest.mock import patch

    from ai_rules.rule_loader_eval.batch import BatchItem, BatchOutcome, BatchSummary

    fx_path = tmp_path / "simple-test.yaml"
    _make_fixture_yaml(fx_path, "simple-test", "Setup search.")

    item = BatchItem(id="simple-test", safe_id="simple-test", path=fx_path, prompt="Setup search.")
    failed_outcome = BatchOutcome(
        item=item,
        run=None,
        error_type="RuntimeError",
        error_message="SDK exploded",
    )
    summary = BatchSummary(
        concurrency=1,
        outcomes=(failed_outcome,),
        wall_seconds=0.1,
    )

    with (
        patch("ai_rules.rule_loader_eval.batch.run_batch", return_value=summary),
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch(
            "ai_rules.commands.rule_loader.find_project_root",
            return_value=project_root,
        ),
        patch(
            "ai_rules.rule_loader_eval.batch.expand_glob",
            return_value=[fx_path],
        ),
    ):
        result = runner.invoke(
            app,
            ["rule-loader", "refresh-all", "--all"],
        )

    assert result.exit_code == 1


def test_refresh_all_sdk_failure_exits_three(tmp_path: Path, project_root: Path) -> None:
    """A RuntimeError from run_batch exits with EXIT_SDK_OR_CONN (3)."""
    from unittest.mock import patch

    fx_path = tmp_path / "simple-test.yaml"
    _make_fixture_yaml(fx_path, "simple-test", "Setup search.")

    with (
        patch(
            "ai_rules.rule_loader_eval.batch.run_batch",
            side_effect=RuntimeError("SDK not installed"),
        ),
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch(
            "ai_rules.commands.rule_loader.find_project_root",
            return_value=project_root,
        ),
        patch(
            "ai_rules.rule_loader_eval.batch.expand_glob",
            return_value=[fx_path],
        ),
    ):
        result = runner.invoke(
            app,
            ["rule-loader", "refresh-all", "--all"],
        )

    assert result.exit_code == 3


def test_refresh_all_sigint_exits_130(tmp_path: Path, project_root: Path) -> None:
    """KeyboardInterrupt from run_batch causes a clean exit with code 130 (POSIX SIGINT)."""
    from unittest.mock import patch

    fx_path = tmp_path / "simple-test.yaml"
    _make_fixture_yaml(fx_path, "simple-test", "Setup search.")

    with (
        patch(
            "ai_rules.rule_loader_eval.batch.run_batch",
            side_effect=KeyboardInterrupt,
        ),
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch(
            "ai_rules.commands.rule_loader.find_project_root",
            return_value=project_root,
        ),
        patch(
            "ai_rules.rule_loader_eval.batch.expand_glob",
            return_value=[fx_path],
        ),
    ):
        result = runner.invoke(
            app,
            ["rule-loader", "refresh-all", "--all"],
        )

    assert result.exit_code == 130
    assert "interrupted" in result.output.lower() or "interrupted" in (result.stderr or "")


# ---------------------------------------------------------------------------
# eval --fixture isolation regression
# ---------------------------------------------------------------------------

_VALID_FIXTURE_YAML = """\
schema_version: 2
updated: 2026-05-16T12:00:00-07:00
id: target-fixture
description: a valid fixture for isolation test
variant: simple
prompt: |
  Build a streamlit dashboard for data analysis.
expected:
  required:
    - rules/999-test-core.md
  dependencies: []
  forbidden: []
  optional: []
trigger_evidence:
  kw: [streamlit, dashboard]
"""

_BROKEN_SCHEMA_YAML = """\
schema_version: 99
updated: 2026-05-16T12:00:00-07:00
id: broken-fixture
description: unsupported schema version
variant: simple
prompt: |
  Some unrelated prompt.
expected:
  required:
    - rules/999-test-core.md
  dependencies: []
  forbidden: []
  optional: []
trigger_evidence:
  kw: [unrelated]
"""


@pytest.mark.unit
def test_eval_fixture_id_isolates_from_broken_sibling(tmp_path: Path) -> None:
    """``eval --fixture X`` succeeds even when an unrelated fixture in the same dir is broken."""
    from unittest.mock import patch

    (tmp_path / "target-fixture.yaml").write_text(_VALID_FIXTURE_YAML, encoding="utf-8")
    (tmp_path / "broken-fixture.yaml").write_text(_BROKEN_SCHEMA_YAML, encoding="utf-8")

    with (
        patch("ai_rules.commands.rule_loader._fixtures_dir", return_value=tmp_path),
        patch("ai_rules.commands.rule_loader.load_rules_metadata", return_value={}),
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch("ai_rules.commands.rule_loader._run_single_eval", return_value=([], False)),
        patch.dict("os.environ", {"SNOWFLAKE_CONNECTION_NAME": "test_conn"}, clear=False),
    ):
        result = runner.invoke(app, ["rule-loader", "eval", "--fixture", "target-fixture"])

    assert result.exit_code == 0, (
        f"Expected exit 0 (isolation fix), got {result.exit_code}.\n{result.output}"
    )
