"""Noninteractive metadata guards without real credentials or network calls."""

import pytest

from ai_rules.rule_loader_eval.connections import (
    ConnectionPreflightError,
    redact_auth_error,
    require_pat_connection,
    resolve_connection,
)


def test_precedence(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_CONNECTION_NAME", "environment")
    assert resolve_connection("explicit") == "explicit"
    assert resolve_connection(None) == "environment"


def test_auth_diagnostics_redact_credentials():
    text = "password=secret-sentinel token_secret: other-sentinel eyJtest.payload.signature"
    result = redact_auth_error(text)
    assert "secret-sentinel" not in result
    assert "other-sentinel" not in result
    assert "eyJtest" not in result


@pytest.mark.parametrize("auth", ["externalbrowser", "oauth", "https://idp.invalid"])
def test_interactive_and_other_auth_rejected(tmp_path, auth):
    (tmp_path / "connections.toml").write_text(
        f'[pat]\naccount="test"\nuser="test"\nauthenticator="{auth}"\npassword="secret-sentinel"\n'
    )
    with pytest.raises(ConnectionPreflightError) as error:
        require_pat_connection("pat", home=tmp_path)
    assert "secret-sentinel" not in str(error.value)
    assert "not PAT" in str(error.value)


def test_explicit_pat_connection(tmp_path):
    (tmp_path / "connections.toml").write_text(
        '[pat]\naccount="test"\nuser="test"\nauthenticator="PROGRAMMATIC_ACCESS_TOKEN"\npassword="test-only-placeholder"\n'
    )
    assert require_pat_connection("pat", home=tmp_path) == "pat"


def test_default_auth_requires_pat_candidate(tmp_path):
    (tmp_path / "connections.toml").write_text(
        '[pat]\naccount="test"\nuser="test"\npassword="ordinary-test-password"\n'
    )
    with pytest.raises(ConnectionPreflightError, match="PAT candidate"):
        require_pat_connection("pat", home=tmp_path)


def test_missing_identity_and_config_errors(tmp_path):
    with pytest.raises(ConnectionPreflightError, match="explicit named"):
        require_pat_connection(None, home=tmp_path)
    with pytest.raises(ConnectionPreflightError, match="not found"):
        require_pat_connection("pat", home=tmp_path)
    (tmp_path / "connections.toml").write_text('not valid TOML "secret-sentinel"')
    with pytest.raises(ConnectionPreflightError) as error:
        require_pat_connection("pat", home=tmp_path)
    assert "secret-sentinel" not in str(error.value)


def test_doctor_smoke_forwards_environment_connection(monkeypatch):
    from types import SimpleNamespace
    from unittest.mock import Mock

    from ai_rules.commands import rule_loader
    from ai_rules.rule_loader_eval import agent_runner

    monkeypatch.setenv("SNOWFLAKE_CONNECTION_NAME", "environment-pat")
    monkeypatch.setattr(rule_loader, "_ensure_sdk_and_connection", lambda: None)
    smoke = Mock(return_value=SimpleNamespace(is_infra_error=False, duration_ms=1, turns=2))
    monkeypatch.setattr(agent_runner, "run_live", smoke)
    rule_loader._doctor_check(with_smoke=True)
    assert smoke.call_args.kwargs["connection"] == "environment-pat"


def test_missing_pat_credential_and_nested_config(tmp_path):
    (tmp_path / "config.toml").write_text(
        '[connections.pat]\naccount="test"\nuser="test"\nauthenticator="PROGRAMMATIC_ACCESS_TOKEN"\n'
    )
    with pytest.raises(ConnectionPreflightError, match="no configured"):
        require_pat_connection("pat", home=tmp_path)
    with (tmp_path / "config.toml").open("a") as stream:
        stream.write('password="test-only-placeholder"\n')
    assert require_pat_connection("pat", home=tmp_path) == "pat"


def test_shell_connection_argument_precedence(tmp_path, monkeypatch):
    import os
    import subprocess
    from pathlib import Path

    fake = tmp_path / "ai-rules"
    log = tmp_path / "args.log"
    fake.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$ARG_LOG"\n')
    fake.chmod(0o700)
    monkeypatch.setenv("ARG_LOG", str(log))
    monkeypatch.setenv("SNOWFLAKE_CONNECTION_NAME", "environment")
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    script = Path(__file__).resolve().parents[2] / "scripts" / "run-eval.sh"
    result = subprocess.run(
        ["bash", str(script), "--connection", "explicit", "--require-pat"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    lines = log.read_text().splitlines()
    assert len(lines) == 29
    assert all("--connection explicit" in line and "--require-pat" in line for line in lines)
    assert "environment" not in log.read_text()


@pytest.mark.parametrize("args", [["--connection"], ["--max-turns", "0"], ["--effort", "invalid"]])
def test_shell_rejects_invalid_options(args):
    import subprocess
    from pathlib import Path

    script = Path(__file__).resolve().parents[2] / "scripts" / "run-eval.sh"
    result = subprocess.run(["bash", str(script), *args], capture_output=True, text=True)
    assert result.returncode == 2
    assert "ERROR:" in result.stderr
