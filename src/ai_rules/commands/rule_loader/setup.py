"""Preview reviewed PAT identity lifecycle SQL without connecting to an account."""

from __future__ import annotations

import ipaddress
import os
import re
from pathlib import Path
from typing import Annotated

import typer

from ai_rules._shared.console import log_error, log_success

DEFAULTS = {
    "user": "AI_RULES_EVAL_USER",
    "role": "AI_RULES_EVAL_ROLE",
    "token": "AI_RULES_EVAL_PAT",
}
OPERATIONS = {
    "identity": "eval_identity.sql",
    "network-policy": "eval_network_policy.sql",
    "create-pat": "eval_pat_create.sql",
    "rotate-pat": "eval_pat_rotate.sql",
    "revoke-pat": "eval_pat_revoke.sql",
    "verify": "eval_verify.sql",
    "teardown": "eval_teardown.sql",
}


def identifier(value: str, *, qualified: bool = False) -> str:
    """Accept only conservative unquoted identifiers, never arbitrary SQL."""
    parts = value.split(".")
    if len(parts) != (3 if qualified else 1) or any(
        not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,254}", part) for part in parts
    ):
        raise ValueError(
            "Use unquoted letters/digits/underscores for identifiers; network rules require DB.SCHEMA.NAME."
        )
    return value.upper()


def identity_names(user: str | None, role: str | None, token: str | None) -> dict[str, str]:
    """Resolve parameters before environment before defaults consistently."""
    return {
        name: identifier(
            explicit
            if explicit is not None
            else os.environ.get(
                "AI_RULES_EVAL_PAT" if name == "token" else f"AI_RULES_EVAL_{name.upper()}", default
            )
        )
        for name, explicit, default in (
            ("user", user, DEFAULTS["user"]),
            ("role", role, DEFAULTS["role"]),
            ("token", token, DEFAULTS["token"]),
        )
    }


def render_setup(
    operation: str,
    *,
    user: str | None = None,
    role: str | None = None,
    token: str | None = None,
    network_policy: str | None = None,
    network_rule: str | None = None,
    allowed_networks: list[str] | None = None,
    days: int = 15,
    overlap: int = 24,
    confirm_destructive: bool = False,
) -> str:
    """Render account-facing SQL for separate administrator review/execution."""
    if operation not in OPERATIONS:
        raise ValueError("Unknown setup operation")
    if (
        type(days) is not int
        or not 1 <= days <= 365
        or type(overlap) is not int
        or not 0 <= overlap <= 24
    ):
        raise ValueError("PAT lifetime must be 1-365 days; rotation overlap must be 0-24 hours.")
    if operation in {"revoke-pat", "teardown"} and not confirm_destructive:
        raise ValueError(
            "Destructive preview requires --confirm-destructive; execution is still a separate administrator action."
        )
    names = identity_names(user, role, token)
    policy = (
        network_policy
        if network_policy is not None
        else os.environ.get("AI_RULES_EVAL_NETWORK_POLICY")
    )
    if operation in {"identity", "network-policy", "verify"} and not policy:
        raise ValueError(
            "An explicit approved --network-policy or AI_RULES_EVAL_NETWORK_POLICY is required."
        )
    replacements = {
        "__USER__": names["user"],
        "__ROLE__": names["role"],
        "__TOKEN__": names["token"],
        "__DAYS__": str(days),
        "__OVERLAP__": str(overlap),
    }
    if policy:
        replacements["__NETWORK_POLICY__"] = identifier(policy)
    if operation == "network-policy":
        if not network_rule or not allowed_networks:
            raise ValueError(
                "Optional policy creation requires --network-rule DB.SCHEMA.NAME and approved --allowed-network values."
            )
        values = []
        for value in allowed_networks:
            network = ipaddress.ip_network(value, strict=True)
            if network.version != 4 or network.prefixlen == 0:
                raise ValueError(
                    "Only approved IPv4 networks are supported; unrestricted /0 is rejected."
                )
            values.append(f"'{network}'")
        replacements["__NETWORK_RULE__"] = identifier(network_rule, qualified=True)
        replacements["__ALLOWED_NETWORKS__"] = ", ".join(values)
    templates = Path(__file__).resolve().parents[4] / "setup"
    sql = (templates / OPERATIONS[operation]).read_text(encoding="utf-8")
    if operation in {"create-pat", "rotate-pat", "revoke-pat"}:
        sql = (templates / "eval_identity_check.sql").read_text(encoding="utf-8") + "\n" + sql
    for placeholder, value in replacements.items():
        sql = sql.replace(placeholder, value)
    if re.search(r"__[A-Z_]+__", sql):
        raise ValueError("Unresolved SQL parameters")
    return sql


def setup_preview_cmd(
    operation: Annotated[
        str,
        typer.Argument(
            help="identity|network-policy|create-pat|rotate-pat|revoke-pat|verify|teardown"
        ),
    ],
    output: Annotated[
        Path, typer.Option("--output", help="New nonsecret SQL preview file; never overwritten.")
    ],
    user: Annotated[
        str | None,
        typer.Option("--user", help="Overrides AI_RULES_EVAL_USER; default AI_RULES_EVAL_USER."),
    ] = None,
    role: Annotated[
        str | None, typer.Option("--role", help="Overrides AI_RULES_EVAL_ROLE.")
    ] = None,
    token: Annotated[
        str | None,
        typer.Option("--token", help="PAT name, never a token value; overrides AI_RULES_EVAL_PAT."),
    ] = None,
    network_policy: Annotated[str | None, typer.Option("--network-policy")] = None,
    network_rule: Annotated[str | None, typer.Option("--network-rule")] = None,
    allowed_network: Annotated[list[str] | None, typer.Option("--allowed-network")] = None,
    days_to_expiry: Annotated[int, typer.Option("--days-to-expiry", min=1, max=365)] = 15,
    rotation_overlap_hours: Annotated[
        int, typer.Option("--rotation-overlap-hours", min=0, max=24)
    ] = 24,
    confirm_destructive: Annotated[bool, typer.Option("--confirm-destructive")] = False,
) -> None:
    """Render setup SQL only; never connect, issue a PAT or print its secret."""
    try:
        sql = render_setup(
            operation,
            user=user,
            role=role,
            token=token,
            network_policy=network_policy,
            network_rule=network_rule,
            allowed_networks=allowed_network,
            days=days_to_expiry,
            overlap=rotation_overlap_hours,
            confirm_destructive=confirm_destructive,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            stream.write(sql)
    except (OSError, ValueError) as exc:
        log_error(str(exc))
        raise typer.Exit(4) from exc
    log_success(f"SQL preview written: {output}. No account changes executed.")
    if operation in {"create-pat", "rotate-pat"}:
        typer.echo(
            "Execute only in a private administrator UI: one-time token_secret output must not enter agent transcripts or logs."
        )
