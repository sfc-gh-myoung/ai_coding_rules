"""Generate and integrity-check reviewed SQL bundles for the evaluation identity."""

from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

import typer

from ai_rules.commands.rule_loader.setup import identifier, render_setup

OPERATIONS = {
    "setup",
    "identity",
    "verify",
    "create-pat",
    "rotate-pat",
    "revoke-pat",
    "teardown",
    "network-policy",
}
REQUIRED = ("user", "role", "pat_name", "account", "output_dir", "days", "overlap")
OPTIONAL = ("network_policy", "network_rule", "allowed_networks")


def settings(values: dict) -> dict:
    """Validate settings. The Makefile owns defaults and always supplies required values."""
    data = {key: values[key] for key in (*REQUIRED, *OPTIONAL) if values.get(key) is not None}
    for key in REQUIRED:
        if key not in data:
            raise ValueError(f"{key} is required.")
    for key in OPTIONAL:
        data.setdefault(key, "")
    for key in ("days", "overlap"):
        if type(data[key]) is not int:
            raise ValueError(f"{key} must be an integer.")
    for key in (*REQUIRED[:5], *OPTIONAL):
        if not isinstance(data[key], str):
            raise ValueError(f"{key} must be a string.")
    for key in ("user", "role", "pat_name"):
        data[key] = identifier(data[key])
    if data["network_policy"]:
        data["network_policy"] = identifier(data["network_policy"])
    return data


def generate(operation: str, data: dict, *, confirm: bool = False) -> Path:
    """Create a new hashed bundle; never update a global latest pointer."""
    if operation in {"create-pat", "rotate-pat"} and not data["network_policy"]:
        raise ValueError("Token issuance/rotation requires an explicit approved network policy.")
    operations = ["identity", "verify", "create-pat"] if operation == "setup" else [operation]
    rendered = {}
    for index, name in enumerate(operations, 1):
        sql = render_setup(
            name,
            user=data["user"],
            role=data["role"],
            token=data["pat_name"],
            account=data["account"],
            network_policy=data["network_policy"] or None,
            network_rule=data["network_rule"] or None,
            allowed_networks=data["allowed_networks"].split(",")
            if data["allowed_networks"]
            else None,
            days=data["days"],
            overlap=data["overlap"],
            confirm_destructive=confirm,
        )
        rendered[f"{index:02}-{name}.sql"] = sql
    root = Path(data["output_dir"]).resolve()
    root.mkdir(parents=True, exist_ok=True)
    bundle = root / f"{data['user'].lower()}-{operation}-{uuid.uuid4().hex[:12]}"
    bundle.mkdir()
    manifest = {
        "schema": "ai-rules-setup/v1",
        "operation": operation,
        "settings": data,
        "files": [
            {"name": name, "sha256": hashlib.sha256(sql.encode()).hexdigest()}
            for name, sql in rendered.items()
        ],
    }
    for name, sql in rendered.items():
        (bundle / name).write_text(sql)
    (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return bundle


def read_bundle(bundle: Path) -> tuple[dict, list[str]]:
    """Validate hashes and canonical renderer output before allowing execution."""
    manifest = json.loads((bundle / "manifest.json").read_text())
    if manifest.get("schema") != "ai-rules-setup/v1":
        raise ValueError("Unsupported bundle schema.")
    data = settings(manifest["settings"])
    operation = manifest["operation"]
    operations = ["identity", "verify", "create-pat"] if operation == "setup" else [operation]
    if len(manifest["files"]) != len(operations):
        raise ValueError("Invalid bundle file inventory.")
    sql_files = []
    for index, (entry, name) in enumerate(zip(manifest["files"], operations, strict=True), 1):
        expected_name = f"{index:02}-{name}.sql"
        if entry["name"] != expected_name:
            raise ValueError("Invalid bundle file path/order.")
        sql = (bundle / expected_name).read_text()
        if hashlib.sha256(sql.encode()).hexdigest() != entry["sha256"]:
            raise ValueError("Bundle SQL changed after generation.")
        expected = render_setup(
            name,
            user=data["user"],
            role=data["role"],
            token=data["pat_name"],
            account=data["account"],
            network_policy=data["network_policy"] or None,
            network_rule=data["network_rule"] or None,
            allowed_networks=data["allowed_networks"].split(",")
            if data["allowed_networks"]
            else None,
            days=data["days"],
            overlap=data["overlap"],
            confirm_destructive=True,
        )
        if sql != expected:
            raise ValueError("Bundle SQL does not match reviewed templates.")
        sql_files.append(sql)
    return manifest, sql_files


def workflow_cmd(
    action: str,
    bundle: Path | None = None,
    user: str | None = None,
    role: str | None = None,
    token: str | None = None,
    network_policy: str | None = None,
    network_rule: str | None = None,
    allowed_networks: str | None = None,
    account: str | None = None,
    output_dir: str | None = None,
    confirm: bool = False,
    days: int | None = None,
    overlap: int | None = None,
) -> None:
    """Generate a reviewed SQL bundle, or verify an existing bundle is unmodified."""
    try:
        if action == "check-bundle":
            if not bundle:
                raise ValueError("BUNDLE is required.")
            read_bundle(bundle)
            typer.echo(f"Bundle is unmodified: {bundle}")
            return
        data = settings(
            {
                "user": user,
                "role": role,
                "pat_name": token,
                "network_policy": network_policy,
                "network_rule": network_rule,
                "allowed_networks": allowed_networks,
                "account": account,
                "output_dir": output_dir,
                "days": days,
                "overlap": overlap,
            }
        )
        if action not in OPERATIONS:
            raise ValueError("Unknown action.")
        generated = generate(action, data, confirm=confirm)
    except ValueError as exc:
        typer.echo(f"Refused: {exc}", err=True)
        raise typer.Exit(2) from None
    typer.echo(f"SQL bundle generated (no account changes): {generated}")
    typer.echo(
        f"Review it, then run: make eval-setup-apply BUNDLE={generated} ADMIN_CONNECTION=<name> ADMIN_ROLE=<role>"
    )
