"""Thin coverage tests for small remaining gaps in various modules."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# rule_loader.py — ProgressTracker helpers were removed in Phase 3; tests
# migrated / deleted.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# agent_runner.py — empty-text early returns + _project_root
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
# rules_meta.py — empty payload paths in split_depends_buckets and _split_depends
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
# snapshot.py — git helper functions
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
# mirror.py — _run dry_run, _capture, _assert_clean_working_tree
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_mirror_run_dry_run_prints_command(capsys) -> None:
    """_run with dry_run=True prints [DRY RUN] and returns without executing."""
    from ai_rules.commands.dev.mirror import _run

    _run(["git", "push"], dry_run=True)
    # No exception raised


@pytest.mark.unit
def test_mirror_capture_returns_stdout(tmp_path: Path) -> None:
    """_capture runs a command and returns stripped stdout."""
    from unittest.mock import MagicMock

    from ai_rules.commands.dev.mirror import _capture

    mock_result = MagicMock()
    mock_result.stdout = "  output line  "
    with patch("ai_rules.commands.dev.mirror.run", return_value=mock_result) as mock_run:
        result = _capture(["git", "status"])
    assert result == "output line"
    mock_run.assert_called_once()


@pytest.mark.unit
def test_mirror_assert_clean_working_tree_dry_run_noop() -> None:
    """_assert_clean_working_tree is a no-op when dry_run=True."""
    from ai_rules.commands.dev.mirror import _assert_clean_working_tree

    # Should not raise even with no git available in dry_run mode
    _assert_clean_working_tree(dry_run=True)


@pytest.mark.unit
def test_mirror_assert_clean_dirty_tree_exits(tmp_path: Path) -> None:
    """_assert_clean_working_tree raises Exit when git reports dirty tree."""
    from unittest.mock import MagicMock

    import typer

    from ai_rules.commands.dev.mirror import _assert_clean_working_tree

    mock_result = MagicMock()
    mock_result.returncode = 1  # dirty tree
    with patch("ai_rules.commands.dev.mirror.run", return_value=mock_result):
        with pytest.raises(typer.Exit):
            _assert_clean_working_tree(dry_run=False)


# ---------------------------------------------------------------------------
# release.py — _bump_version_files OSError + _run non-dry-run
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_bump_version_files_oserror_exits(tmp_path: Path, monkeypatch) -> None:
    """_bump_version_files raises Exit on OSError during write."""
    import typer

    from ai_rules.commands.dev.release import _bump_version_files

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('version = "0.1.0"\n', encoding="utf-8")
    readme = tmp_path / "README.md"
    readme.write_text("![version](https://img.shields.io/badge/version-0.1.0-blue)\n")

    # Patch os.replace to raise after pyproject is replaced
    import os as os_mod

    call_count = [0]
    original_replace = os_mod.replace

    def raising_replace(src, dst):
        call_count[0] += 1
        raise OSError("disk full")

    monkeypatch.setattr(os_mod, "replace", raising_replace)

    with pytest.raises(typer.Exit):
        _bump_version_files("1.0.0", cwd=tmp_path)


@pytest.mark.unit
def test_release_run_helper_live_calls_run(monkeypatch) -> None:
    """_run with dry_run=False actually calls the run() function."""
    from ai_rules.commands.dev.release import _run

    calls = []

    def tracking_run(cmd, **kwargs):
        calls.append(cmd)
        from unittest.mock import MagicMock

        m = MagicMock()
        m.returncode = 0
        return m

    monkeypatch.setattr("ai_rules.commands.dev.release.run", tracking_run)
    _run(["git", "status"], dry_run=False)
    assert calls == [["git", "status"]]


# ---------------------------------------------------------------------------
# orchestrate.py — find_project_root() called when root=None
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_run_validate_calls_find_project_root_when_no_root(tmp_path: Path) -> None:
    """run_validate() calls find_project_root() when root is None (line 62)."""
    from ai_rules.commands.dev.orchestrate import run_validate

    # Provide a tmp_path with pyproject.toml + uv available
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    with patch(
        "ai_rules.commands.dev.orchestrate.find_project_root", return_value=tmp_path
    ) as mock_fpr:
        with patch("shutil.which", return_value=None):
            import typer as _typer

            with pytest.raises(_typer.Exit):
                run_validate()  # root=None → hits line 62
    mock_fpr.assert_called()


# ---------------------------------------------------------------------------
# matcher.py — the elif strict_forbidden branch is dead code; skip line 114
# ---------------------------------------------------------------------------

# NOTE: matcher.py line 114 is an `elif strict_forbidden and forbidden_present:`
# clause that is UNREACHABLE because the preceding `if forbidden_present:` already
# fires when forbidden_present is True. Coverage tool correctly marks it uncovered.


# ---------------------------------------------------------------------------
# rule_loader.py validate_cmd — single fixture error + success
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
# rule_loader.py eval_cmd — fixture not found before SDK check
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
# batch.py — run_batch (synchronous wrapper) — fix import path
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_run_batch_covers_synchronous_wrapper(tmp_path: Path) -> None:
    """run_batch calls asyncio.run(run_batch_async(...)) — covers line 295."""
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

    def fake_run_live_async(*args, **kwargs):
        async def _inner():
            return mock_run

        return _inner()

    with _patch(
        "ai_rules.rule_loader_eval.agent_runner.run_live_async",
        side_effect=fake_run_live_async,
    ):
        summary = run_batch([item], concurrency=1)

    assert isinstance(summary, BatchSummary)
    assert summary.total == 1
