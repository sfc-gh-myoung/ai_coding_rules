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


# Operations whose bundle needs a network policy; per-file SQL only embeds it for the first three.
POLICY_OPERATIONS = {"setup", "identity", "network-policy", "verify", "create-pat", "rotate-pat"}
TEMPLATE_POLICY_OPERATIONS = {"identity", "network-policy", "verify"}
ORG_ACCOUNT = re.compile(r"[A-Za-z0-9_]+-[A-Za-z0-9_]+")
LOCATOR = re.compile(r"([A-Za-z0-9_]+)\.[A-Za-z0-9_.-]+")
ORG_EXPR = "CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME()"
ACCOUNT_HELP = (
    "EVAL_ACCOUNT names the Snowflake account the generated SQL is allowed to change; "
    "each file stops if you are connected to a different account. "
    "Use ORGANIZATION-ACCOUNT (<organization name>-<account name>, e.g. MYORG-MYACCOUNT) "
    "or an account locator with a dot (e.g. xy12345.us-east-1). "
    "A connections.toml connection name is not accepted. "
    "Find it with: SELECT CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME()"
)


def account_guard(account: str) -> tuple[str, str]:
    """Return (SQL expression, expected value) for the guard, or raise with the accepted formats."""
    if locator := LOCATOR.fullmatch(account):
        return "CURRENT_ACCOUNT()", locator.group(1)
    if ORG_ACCOUNT.fullmatch(account):
        return ORG_EXPR, account
    raise ValueError(f"Invalid EVAL_ACCOUNT '{account}'. {ACCOUNT_HELP}")


def check_inputs(
    operation: str,
    account: str | None,
    network_policy: str | None,
    policy_operations: set[str] = POLICY_OPERATIONS,
) -> None:
    """Report every missing required input in one error, then validate the account format."""
    missing = []
    if not account:
        missing.append(("EVAL_ACCOUNT", "ORGANIZATION-ACCOUNT or account locator"))
    if operation in policy_operations and not network_policy:
        missing.append(("EVAL_NETWORK_POLICY", "approved network policy name"))
    if missing:
        names = ", ".join(name for name, _ in missing)
        example = " ".join(f"{name}=<{what}>" for name, what in missing)
        raise ValueError(
            f"Missing required input(s): {names}. "
            f"Example: make eval-setup EVAL_ACCOUNT=MYORG-MYACCOUNT EVAL_NETWORK_POLICY=USER_NW_POLICY "
            f"(here: {example}). Set them once in setup/eval.local.mk to avoid repeating them. "
            f"{ACCOUNT_HELP if any(n == 'EVAL_ACCOUNT' for n, _ in missing) else ''}".rstrip()
        )
    if account:
        account_guard(account)


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
    check_inputs(operation, account, network_policy, TEMPLATE_POLICY_OPERATIONS)
    names = {"user": identifier(user), "role": identifier(role), "token": identifier(token)}
    policy = network_policy
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
    expr, expected = account_guard(account)
    guard = (templates / "eval_account_guard.sql").read_text(encoding="utf-8")
    sql = guard.replace("__ACCOUNT_EXPR__", expr).replace("__ACCOUNT__", expected) + "\n" + sql
    if re.search(r"__[A-Z_]+__", sql):
        raise ValueError("Unresolved SQL parameters")
    return sql
