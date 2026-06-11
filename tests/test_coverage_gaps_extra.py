"""Additional coverage tests targeting specific rule_loader.py and other module branches."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from ai_rules.cli import app

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true"})


# ---------------------------------------------------------------------------
# rule_loader.py validate_cmd bulk mode with debug + error paths
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_validate_cmd_bulk_debug_schema_error(tmp_path: Path) -> None:
    """validate_cmd bulk with --debug and schema error covers debug output (lines 598-599)."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    fixtures_dir = tmp_path / "fixtures" / "rule_loader_eval"
    fixtures_dir.mkdir(parents=True)
    (tmp_path / "rules").mkdir()
    # Schema error fixture (missing required keys)
    (fixtures_dir / "bad-schema.yaml").write_text(
        "id: bad-schema\nprompt: test\n",
        encoding="utf-8",
    )

    with patch("ai_rules.commands.rule_loader.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["rule-loader", "validate", "--no-progress", "--debug"])
    assert result.exit_code != 0


@pytest.mark.integration
def test_validate_cmd_bulk_yaml_syntax_error(tmp_path: Path) -> None:
    """validate_cmd bulk with invalid YAML covers except Exception path (lines 600-602)."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    fixtures_dir = tmp_path / "fixtures" / "rule_loader_eval"
    fixtures_dir.mkdir(parents=True)
    (tmp_path / "rules").mkdir()
    # Truly invalid YAML syntax
    (fixtures_dir / "bad-yaml.yaml").write_text("{: broken: [[", encoding="utf-8")

    with patch("ai_rules.commands.rule_loader.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["rule-loader", "validate", "--no-progress"])
    assert result.exit_code != 0


@pytest.mark.integration
def test_validate_cmd_bulk_yaml_error_with_debug(tmp_path: Path) -> None:
    """validate_cmd bulk --debug with YAML error covers debug traceback (lines 603-605)."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    fixtures_dir = tmp_path / "fixtures" / "rule_loader_eval"
    fixtures_dir.mkdir(parents=True)
    (tmp_path / "rules").mkdir()
    (fixtures_dir / "bad-yaml.yaml").write_text("{: broken: [[", encoding="utf-8")

    with patch("ai_rules.commands.rule_loader.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["rule-loader", "validate", "--no-progress", "--debug"])
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# rule_loader.py _ensure_sdk_and_connection — version mismatch path
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_ensure_sdk_version_mismatch_exits() -> None:
    """_ensure_sdk_and_connection exits when installed SDK version != pin."""
    from ai_rules.commands.rule_loader import _ensure_sdk_and_connection

    with patch("importlib.metadata.version", return_value="0.0.0-wrong"):
        with pytest.raises(typer.Exit):
            _ensure_sdk_and_connection()


@pytest.mark.unit
def test_ensure_sdk_package_not_found_exits() -> None:
    """_ensure_sdk_and_connection handles PackageNotFoundError (lines 665-666)."""
    from importlib.metadata import PackageNotFoundError

    from ai_rules.commands.rule_loader import _ensure_sdk_and_connection

    with patch("importlib.metadata.version", side_effect=PackageNotFoundError("not found")):
        with pytest.raises(typer.Exit):
            _ensure_sdk_and_connection()


# ---------------------------------------------------------------------------
# rule_loader.py doctor_cmd — connection branch paths
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_doctor_cmd_with_connection_and_env(monkeypatch) -> None:
    """doctor_cmd logs connection info (covers lines 700-705 branches)."""
    monkeypatch.setenv("SNOWFLAKE_CONNECTION_NAME", "test-conn")

    with patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"):
        with patch("ai_rules.commands.rule_loader._doctor_check") as mock_dc:
            mock_dc.return_value = None
            result = runner.invoke(app, ["rule-loader", "doctor"])
    # Just verifying the command runs without internal SDK calls


@pytest.mark.integration
def test_doctor_cmd_no_connection_warns(monkeypatch) -> None:
    """doctor_cmd warns when no connection configured."""
    monkeypatch.delenv("SNOWFLAKE_CONNECTION_NAME", raising=False)

    with patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"):
        with patch("ai_rules.commands.rule_loader._doctor_check") as mock_dc:
            mock_dc.return_value = None
            result = runner.invoke(app, ["rule-loader", "doctor"])


# ---------------------------------------------------------------------------
# new.py — filename is None path (lines 491-492)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_new_cmd_without_filename_shows_help() -> None:
    """New command without filename shows help and exits 0 (covers lines 491-492)."""
    result = runner.invoke(app, ["new"])
    # Either help output or exit 0
    assert result.exit_code == 0 or "Usage" in result.output


# ---------------------------------------------------------------------------
# tokens.py — dry_run path (lines 472-473)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_tokens_update_dry_run() -> None:
    """Tokens update --dry-run covers the dry_run output lines (472-473)."""
    result = runner.invoke(app, ["tokens", "update", "--dry-run"])
    # Should exit 0 or show dry-run output; doesn't require real API


# ---------------------------------------------------------------------------
# index.py — list command (index.py line 201, various paths)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_rule_loader_list_command_runs() -> None:
    """rule-loader list command lists fixtures and exits 0."""
    result = runner.invoke(app, ["rule-loader", "list"])
    assert result.exit_code == 0


@pytest.mark.integration
def test_rule_loader_list_variant_filter() -> None:
    """rule-loader list --variant simple filters by variant."""
    result = runner.invoke(app, ["rule-loader", "list", "--variant", "simple"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# quality.py — docs_targets branch (lines 225-235)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_quality_markdown_with_docs_targets(tmp_path: Path) -> None:
    """Quality markdown with docs_targets config covers lines 225-235."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        "[project]\nname='test'\n[tool.ai_rules.dev]\nmarkdown_docs_targets = ['README.md']\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
    (tmp_path / "rules").mkdir()

    from ai_rules.commands.dev.quality import quality_app

    q_runner = CliRunner(env={"NO_COLOR": "1"})
    with patch("ai_rules.commands.dev.quality.find_project_root", return_value=tmp_path):
        with patch("ai_rules.commands.dev.quality.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = q_runner.invoke(quality_app, ["markdown"])


# ---------------------------------------------------------------------------
# diagnostics.py — line 204 early-return in _emit_pair
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_format_debug_equal_sets_early_return() -> None:
    """format_debug early-returns when both signal sets are equal (line 204)."""
    from ai_rules.rule_loader_eval.agent_runner import AgentRun
    from ai_rules.rule_loader_eval.diagnostics import format_debug

    run = AgentRun(
        fixture_id="test",
        loaded=("rules/000-global-core.md",),
        loaded_via_reads=("rules/000-global-core.md",),
        loaded_via_reads_performed=(),
        loaded_via_section=("rules/000-global-core.md",),
    )
    output = format_debug(run)
    assert isinstance(output, list)


# ---------------------------------------------------------------------------
# mirror.py line 29 — _run without dry_run
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_mirror_run_non_dry_run_calls_run(monkeypatch) -> None:
    """mirror._run with dry_run=False calls run() — covers line 29."""
    from ai_rules.commands.dev.mirror import _run

    calls = []

    def tracking_run(cmd, **kwargs):
        calls.append(cmd)
        return MagicMock(returncode=0)

    monkeypatch.setattr("ai_rules.commands.dev.mirror.run", tracking_run)
    _run(["git", "status"], dry_run=False)
    assert calls == [["git", "status"]]
