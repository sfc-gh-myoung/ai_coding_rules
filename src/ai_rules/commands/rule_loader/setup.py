"""Render reviewed PAT identity lifecycle SQL without connecting to an account."""

from __future__ import annotations

import ipaddress
import re
from pathlib import Path

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


def render_setup(
    operation: str,
    *,
    user: str,
    role: str,
    token: str,
    account: str,
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
    names = {"user": identifier(user), "role": identifier(role), "token": identifier(token)}
    policy = network_policy
    if operation in {"identity", "network-policy", "verify"} and not policy:
        raise ValueError("An explicit approved network policy (EVAL_NETWORK_POLICY) is required.")
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
    if not re.fullmatch(r"[A-Za-z0-9_]+-[A-Za-z0-9_]+", account):
        raise ValueError("Account must be ORGANIZATION-ACCOUNT (EVAL_ACCOUNT).")
    guard = (templates / "eval_account_guard.sql").read_text(encoding="utf-8")
    sql = guard.replace("__ACCOUNT__", account) + "\n" + sql
    if re.search(r"__[A-Z_]+__", sql):
        raise ValueError("Unresolved SQL parameters")
    return sql
