"""Synthetic workflow tests: no account changes and no real credentials."""

import json
import os
import subprocess
from pathlib import Path

import pytest

from ai_rules.commands.rule_loader.workflow import generate, read_bundle
from ai_rules.commands.rule_loader.workflow import settings as _settings

BASE = {
    "user": "AI_RULES_EVAL_USER",
    "role": "AI_RULES_EVAL_ROLE",
    "pat_name": "AI_RULES_EVAL_PAT",
    "account": "MYORG-MYACCOUNT",
    "output_dir": "setup/sql",
    "days": 15,
    "overlap": 24,
}


def settings(values=None):
    return _settings({**BASE, **(values or {})})


def test_bundle_integrity_no_overwrite(tmp_path):
    data = settings({"network_policy": "APPROVED_POLICY", "output_dir": str(tmp_path)})
    first = generate("setup", data)
    second = generate("setup", data)
    assert first != second
    manifest, statements = read_bundle(first)
    assert len(statements) == 3
    assert manifest["settings"]["user"] == "AI_RULES_EVAL_USER"
    (first / "01-identity.sql").write_text("SELECT 1;")
    with pytest.raises(ValueError, match="changed"):
        read_bundle(first)


def test_bundle_manifest_path_traversal_rejected(tmp_path):
    data = settings({"network_policy": "POLICY", "output_dir": str(tmp_path)})
    bundle = generate("identity", data)
    path = bundle / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["files"][0]["name"] = "../escape.sql"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="path/order"):
        read_bundle(bundle)


def test_network_policy_generation(tmp_path):
    data = settings(
        {
            "network_policy": "POLICY",
            "network_rule": "DB.SECURITY.RULE",
            "allowed_networks": "192.0.2.1/32",
            "output_dir": str(tmp_path),
        },
    )
    bundle = generate("network-policy", data)
    _, sql = read_bundle(bundle)
    assert "CREATE NETWORK RULE DB.SECURITY.RULE" in sql[0]


def test_settings_require_values_and_types():
    with pytest.raises(ValueError, match="user is required"):
        _settings({})
    with pytest.raises(ValueError, match="must be an integer"):
        settings({"days": "fifteen"})


def _make(target, *args, env=None):
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        ["make", "-n", "-C", str(root), "EVAL_LOCAL=/dev/null", target, *args],
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
    )
    return result


@pytest.mark.parametrize(
    "target,expected",
    [
        ("eval-setup", "rule-loader workflow setup"),
        ("eval-check", "rule-loader doctor --require-pat"),
        ("eval-smoke", "--with-smoke"),
        ("eval-run", "rule-loader eval --require-pat"),
        ("eval-all-models", "--all-models"),
    ],
)
def test_make_targets_call_existing_commands_with_project_defaults(target, expected):
    out = _make(target, "EVAL_ACCOUNT=a").stdout
    assert expected in out
    assert "'ai_rules_eval'" in out or "workflow setup" in out


def test_make_override_precedence_cli_over_env_over_default():
    assert "--role 'AI_RULES_EVAL_ROLE'" in _make("eval-setup").stdout
    assert "--role 'FROM_ENV'" in _make("eval-setup", env={"EVAL_ROLE": "FROM_ENV"}).stdout
    cli = _make("eval-setup", "EVAL_ROLE=FROM_CLI", env={"EVAL_ROLE": "FROM_ENV"})
    assert "--role 'FROM_CLI'" in cli.stdout


def test_connection_add_requires_account_and_passes_no_secret():
    assert _make("eval-connection-add").returncode != 0
    out = _make(
        "eval-connection-add", "EVAL_ACCOUNT=org-acct", "EVAL_AUTHENTICATOR=snowflake"
    ).stdout
    assert "snow connection add --no-interactive" in out
    assert "--authenticator 'snowflake'" in out
    assert "--password" not in out


def test_every_generated_file_starts_with_account_guard(tmp_path):
    bundle = generate("setup", settings({"network_policy": "POLICY", "output_dir": str(tmp_path)}))
    for sql_file in sorted(bundle.glob("*.sql")):
        text = sql_file.read_text()
        assert text.index("wrong_account") < text.index("CREATE") if "CREATE" in text else True
        assert "UPPER('MYORG-MYACCOUNT')" in text


def test_account_must_be_org_account(tmp_path):
    with pytest.raises(ValueError, match="ORGANIZATION-ACCOUNT"):
        generate(
            "identity",
            settings({"account": "x", "network_policy": "P", "output_dir": str(tmp_path)}),
        )


def test_check_bundle_detects_edits(tmp_path):
    from typer.testing import CliRunner

    from ai_rules.cli import app

    bundle = generate(
        "identity", settings({"network_policy": "POLICY", "output_dir": str(tmp_path)})
    )

    def run():
        return CliRunner().invoke(
            app, ["rule-loader", "workflow", "check-bundle", "--bundle", str(bundle)]
        )

    assert run().exit_code == 0
    (bundle / "01-identity.sql").write_text("DROP USER X;")
    assert run().exit_code == 2


def test_apply_runs_each_bundle_file_with_snow_sql(tmp_path):
    bundle = generate("setup", settings({"network_policy": "POLICY", "output_dir": str(tmp_path)}))
    args = [f"BUNDLE={bundle}", "ADMIN_CONNECTION=adm", "ADMIN_ROLE=ACCOUNTADMIN", "CONFIRM=1"]
    full = _make("eval-setup-apply", *args).stdout
    assert (
        full.count("--filename") == 3
        and "snow sql --connection 'adm' --role 'ACCOUNTADMIN'" in full
    )
    identity = _make("eval-setup-apply", *args, "PHASE=identity").stdout
    assert identity.count("--filename") == 2 and "create-pat" not in identity.split("snow sql")[1]
    assert _make("eval-setup-apply").returncode != 0


def test_connection_account_defaults_to_eval_account_and_can_differ():
    base = _make("eval-connection-add", "EVAL_ACCOUNT=ORG-ACCT").stdout
    assert "--account 'ORG-ACCT'" in base
    split = _make(
        "eval-connection-add", "EVAL_ACCOUNT=ORG-ACCT", "EVAL_CONNECTION_ACCOUNT=loc.us-east-1"
    ).stdout
    assert "--account 'loc.us-east-1'" in split
