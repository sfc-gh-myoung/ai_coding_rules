"""Provisioning preview renders nonsecret SQL and never opens an account session."""

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands.rule_loader.setup import identity_names, render_setup


def test_defaults_and_override_precedence(monkeypatch):
    for key in ("USER", "ROLE", "PAT"):
        monkeypatch.delenv("AI_RULES_EVAL_" + key, raising=False)
    assert identity_names(None, None, None)["user"] == "AI_RULES_EVAL_USER"
    monkeypatch.setenv("AI_RULES_EVAL_USER", "environment_user")
    monkeypatch.setenv("AI_RULES_EVAL_PAT", "environment_pat")
    assert identity_names(None, None, None)["user"] == "ENVIRONMENT_USER"
    assert identity_names("explicit_user", None, None)["user"] == "EXPLICIT_USER"
    assert identity_names(None, None, None)["token"] == "ENVIRONMENT_PAT"


@pytest.mark.parametrize(
    "name", ["bad;DROP USER X", "'quoted'", "name.with.dot", "", "eyJ.secret.value"]
)
def test_identifier_injection_rejected(name):
    with pytest.raises(ValueError):
        identity_names(name, None, None)


@pytest.mark.parametrize(
    "operation", ["identity", "verify", "create-pat", "rotate-pat", "revoke-pat", "teardown"]
)
def test_consistent_names_and_safe_grants(operation):
    sql = render_setup(
        operation,
        user="custom_user",
        role="custom_role",
        token="custom_pat",
        network_policy="APPROVED_POLICY",
        confirm_destructive=True,
    )
    assert "CUSTOM_USER" in sql
    assert "__USER__" not in sql
    assert "CREATE DATABASE" not in sql
    assert "GRANT ACCOUNTADMIN" not in sql
    assert "MANAGE GRANTS ON ACCOUNT" not in sql
    if operation == "identity":
        assert "TYPE = SERVICE" in sql
        assert "SNOWFLAKE.CORTEX_AGENT_USER" in sql
        assert "COPILOT_USER" not in sql
        assert "ADD PROGRAMMATIC ACCESS TOKEN" not in sql
        assert "RAISE conflict" in sql
    if operation in {"create-pat", "rotate-pat", "revoke-pat"}:
        assert "verified project-managed identity" in sql
        assert "CUSTOM_PAT" in sql
    if operation == "teardown":
        assert "DROP USER CUSTOM_USER" in sql
        assert "DROP NETWORK" not in sql
        assert "RAISE conflict" in sql


def test_initial_token_does_not_replace_or_silently_rotate():
    sql = render_setup("create-pat", days=30)
    assert "DAYS_TO_EXPIRY = 30" in sql
    assert "REMOVE PROGRAMMATIC" not in sql
    assert "ROTATE PROGRAMMATIC" not in sql
    assert "ROLE_RESTRICTION = 'AI_RULES_EVAL_ROLE'" in sql


def test_identity_guard_metadata_contract_and_bindings():
    for operation in ("identity", "create-pat", "teardown"):
        sql = render_setup(operation, network_policy="APPROVED_POLICY", confirm_destructive=True)
        assert "WHERE \"name\" = 'AI_RULES_EVAL_USER'" in sql
        assert "COALESCE(\"comment\", '')" in sql
        assert "COALESCE(\"type\", '')" in sql
        assert "INTO :existing_count, :conflict_count" in sql
        assert "WHEN OTHER THEN" not in sql


def test_policy_requires_approved_networks():
    with pytest.raises(ValueError, match="explicit approved"):
        render_setup("identity")
    with pytest.raises(ValueError, match="requires"):
        render_setup("network-policy", network_policy="policy")
    with pytest.raises(ValueError, match="unrestricted"):
        render_setup(
            "network-policy",
            network_policy="policy",
            network_rule="DB.SECURITY.RULE",
            allowed_networks=["0.0.0.0/0"],
        )
    sql = render_setup(
        "network-policy",
        network_policy="policy",
        network_rule="DB.SECURITY.RULE",
        allowed_networks=["192.0.2.1/32"],
    )
    assert "CREATE NETWORK RULE DB.SECURITY.RULE" in sql
    assert "'192.0.2.1/32'" in sql
    assert "ALTER ACCOUNT" not in sql.split("-- Attach")[0]


def test_destructive_preview_requires_explicit_opt_in():
    with pytest.raises(ValueError, match="confirm-destructive"):
        render_setup("teardown")
    with pytest.raises(ValueError):
        render_setup("create-pat", days=366)
    with pytest.raises(ValueError):
        render_setup("rotate-pat", overlap=25)


def test_cli_preview_no_connection_and_no_overwrite(tmp_path, monkeypatch):
    import snowflake.connector

    def forbidden(*args, **kwargs):
        raise AssertionError("Preview must not connect")

    monkeypatch.setattr(snowflake.connector, "connect", forbidden)
    output = tmp_path / "setup.sql"
    args = [
        "rule-loader",
        "setup-preview",
        "identity",
        "--network-policy",
        "approved",
        "--user",
        "custom",
        "--output",
        str(output),
    ]
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0, result.output
    assert "No account changes executed" in result.output
    assert "CREATE USER IF NOT EXISTS CUSTOM" in output.read_text()
    assert CliRunner().invoke(app, args).exit_code == 4


def test_token_preview_has_no_credential_result(tmp_path):
    output = tmp_path / "create.sql"
    result = CliRunner().invoke(
        app, ["rule-loader", "setup-preview", "create-pat", "--output", str(output)]
    )
    assert result.exit_code == 0, result.output
    assert "private administrator UI" in result.output
    assert "RETURN v_secret" not in output.read_text()
