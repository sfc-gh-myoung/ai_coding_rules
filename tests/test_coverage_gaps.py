"""Thin coverage tests for small remaining gaps in various modules."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# rule_loader.py: ProgressTracker helpers were removed in Phase 3; tests
# migrated / deleted.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# agent_runner.py: empty-text early returns + _project_root
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_parse_reads_performed_section_empty_text() -> None:
    """parse_reads_performed_section returns () for empty text (early return)."""
    from ai_rules.rule_loader_eval.agent_runner import parse_reads_performed_section

    result = parse_reads_performed_section("")
    assert result == ()


@pytest.mark.unit
def test_parse_bootstrap_line_empty_text_returns_not_found() -> None:
    """parse_bootstrap_line returns found=False for empty text (early return)."""
    from ai_rules.rule_loader_eval.agent_runner import parse_bootstrap_line

    result = parse_bootstrap_line("")
    assert result["found"] is False
    assert result["n_loaded"] == 0
    assert result["n_failed"] == 0


@pytest.mark.unit
def test_project_root_returns_path_with_pyproject() -> None:
    """_project_root() returns the directory containing pyproject.toml."""
    from ai_rules.rule_loader_eval.agent_runner import _project_root

    result = _project_root()
    assert isinstance(result, Path)
    assert (result / "pyproject.toml").exists()


# ---------------------------------------------------------------------------
# rules_meta.py: empty payload paths in split_depends_buckets and _split_depends
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_split_depends_buckets_empty_payload_skipped() -> None:
    """split_depends_buckets skips entries whose payload is empty after split."""
    from ai_rules.rule_loader_eval.rules_meta import split_depends_buckets

    required, optional = split_depends_buckets("optional: , 200-python-core.md")
    assert "200-python-core.md" in required
    assert all(r for r in required)
    assert all(o for o in optional)


@pytest.mark.unit
def test_split_depends_empty_payload_in_private_function() -> None:
    """_split_depends skips entries whose payload is empty after split."""
    from ai_rules.rule_loader_eval.rules_meta import _split_depends

    # "required: " → payload is empty after strip → skipped
    required, _optional = _split_depends("required: , optional:200-python-core")
    # The empty required: entry is skipped; the optional one is included
    assert all(r for r in required)


# ---------------------------------------------------------------------------
# snapshot.py: git helper functions
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_git_short_sha_non_git_dir_returns_empty(tmp_path: Path) -> None:
    """_git_short_sha returns '' in a non-git directory."""
    from ai_rules.rule_loader_eval.snapshot import _git_short_sha

    result = _git_short_sha(tmp_path)
    assert result == ""


@pytest.mark.unit
def test_git_branch_non_git_dir_returns_empty(tmp_path: Path) -> None:
    """_git_branch returns '' in a non-git directory."""
    from ai_rules.rule_loader_eval.snapshot import _git_branch

    result = _git_branch(tmp_path)
    assert result == ""


@pytest.mark.unit
def test_git_short_sha_oserror_returns_empty() -> None:
    """_git_short_sha returns '' when subprocess.run raises OSError."""
    from ai_rules.rule_loader_eval.snapshot import _git_short_sha

    with patch("subprocess.run", side_effect=OSError("no git")):
        result = _git_short_sha(Path("/fake"))
    assert result == ""


@pytest.mark.unit
def test_git_branch_oserror_returns_empty() -> None:
    """_git_branch returns '' when subprocess.run raises OSError."""
    from ai_rules.rule_loader_eval.snapshot import _git_branch

    with patch("subprocess.run", side_effect=OSError("no git")):
        result = _git_branch(Path("/fake"))
    assert result == ""


# ---------------------------------------------------------------------------
# matcher.py: the elif strict_forbidden branch is dead code; skip line 114
# ---------------------------------------------------------------------------

# NOTE: matcher.py line 114 is an `elif strict_forbidden and forbidden_present:`
# clause that is UNREACHABLE because the preceding `if forbidden_present:` already
# fires when forbidden_present is True. Coverage tool correctly marks it uncovered.


# ---------------------------------------------------------------------------
# rule_loader.py validate_cmd: single fixture error + success
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_validate_cmd_single_fixture_not_found_exits_nonzero() -> None:
    """validate_cmd exits non-zero when a specific fixture is not found."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    runner = CliRunner(env={"NO_COLOR": "1", "CI": "true"})
    result = runner.invoke(
        app,
        [
            "rule-loader",
            "validate",
            "--fixture",
            "completely-nonexistent-fixture-id-xyz",
        ],
    )
    assert result.exit_code != 0


@pytest.mark.integration
def test_validate_cmd_single_fixture_not_found_with_debug() -> None:
    """validate_cmd with --debug covers the debug traceback path (line 569)."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    runner = CliRunner(env={"NO_COLOR": "1", "CI": "true"})
    result = runner.invoke(
        app,
        [
            "rule-loader",
            "validate",
            "--fixture",
            "completely-nonexistent-fixture-id-xyz",
            "--debug",
        ],
    )
    assert result.exit_code != 0


@pytest.mark.integration
def test_validate_cmd_single_valid_fixture_succeeds() -> None:
    """validate_cmd with a valid fixture id exits 0 (covers success path lines 571-572)."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    # Use a known-good fixture from the project
    runner = CliRunner(env={"NO_COLOR": "1", "CI": "true"})
    result = runner.invoke(
        app,
        ["rule-loader", "validate", "--fixture", "simple-python-task"],
    )
    assert result.exit_code == 0


@pytest.mark.integration
def test_validate_cmd_bulk_no_fixture_id_succeeds() -> None:
    """validate_cmd in bulk mode (no --fixture) exits 0 when all fixtures pass."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    runner = CliRunner(env={"NO_COLOR": "1", "CI": "true"})
    result = runner.invoke(app, ["rule-loader", "validate"])
    assert result.exit_code == 0


@pytest.mark.integration
def test_validate_cmd_bulk_with_invalid_fixture_exits_nonzero(tmp_path: Path) -> None:
    """validate_cmd bulk mode exits non-zero when a fixture fails validation."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    fixtures_dir = tmp_path / "fixtures" / "rule_loader_eval"
    fixtures_dir.mkdir(parents=True)
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    # Write a fixture that fails schema validation (missing required keys)
    (fixtures_dir / "bad-fixture.yaml").write_text(
        "id: bad-fixture\nprompt: test\n",
        encoding="utf-8",
    )

    runner = CliRunner(env={"NO_COLOR": "1", "CI": "true"})
    with patch("ai_rules.commands.rule_loader.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["rule-loader", "validate"])
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# rule_loader.py eval_cmd: fixture not found before SDK check
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_eval_cmd_fixture_not_found_with_mocked_connection() -> None:
    """eval_cmd exits non-zero for nonexistent fixture (mocking connection check)."""
    from typer.testing import CliRunner

    from ai_rules.cli import app

    runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "SNOWFLAKE_CONNECTION_NAME": "test"})
    with patch("ai_rules.commands.rule_loader._require_connection_or_exit", return_value="test"):
        result = runner.invoke(
            app,
            [
                "rule-loader",
                "eval",
                "--fixture",
                "completely-nonexistent-xyz-abc",
            ],
        )
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# batch.py: run_batch (synchronous wrapper): fix import path
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_run_batch_covers_synchronous_wrapper(tmp_path: Path) -> None:
    """run_batch calls asyncio.run(run_batch_async(...)): covers line 295."""
    from unittest.mock import patch as _patch

    from ai_rules.rule_loader_eval.agent_runner import AgentRun
    from ai_rules.rule_loader_eval.batch import BatchItem, BatchSummary, run_batch

    item = BatchItem(
        id="test-fixture",
        safe_id="test-fixture",
        path=tmp_path / "test.yaml",
        prompt="Fix the bug in auth.py",
    )

    mock_run = AgentRun(
        fixture_id="test-fixture",
        loaded=("rules/000-global-core.md",),
        loaded_via_reads=(),
        loaded_via_reads_performed=(),
        loaded_via_section=(),
    )

    async def fake_run_live_async(*args, **kwargs):
        return mock_run

    with _patch(
        "ai_rules.rule_loader_eval.agent_runner.run_live_async",
        side_effect=fake_run_live_async,
    ):
        summary = run_batch([item], concurrency=1)

    assert isinstance(summary, BatchSummary)
    assert summary.total == 1
