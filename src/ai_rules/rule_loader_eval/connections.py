"""Named-connection metadata preflight; never exports or formats credentials."""

from __future__ import annotations

import os
import re
import tomllib
from pathlib import Path


class ConnectionPreflightError(ValueError):
    """The selected connection cannot satisfy an unattended PAT run."""


def normalize_authenticator(value: str) -> str:
    """Accept explicit PAT or standard Snowflake password-slot authentication."""
    if value.upper() == "PROGRAMMATIC_ACCESS_TOKEN":
        return "PROGRAMMATIC_ACCESS_TOKEN"
    if value.lower() == "snowflake":
        return "snowflake"
    raise ValueError("Authenticator must be PROGRAMMATIC_ACCESS_TOKEN or snowflake.")


def redact_auth_error(text: str) -> str:
    """Remove token-shaped strings and labeled credentials from SDK diagnostics."""
    text = re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", "[REDACTED]", text)
    return re.sub(
        r"(?i)(password|access_token|refresh_token|token_secret|authorization)(\s*[:=]\s*)([^\s,;]+)",
        r"\1\2[REDACTED]",
        text,
    )


def resolve_connection(explicit: str | None) -> str | None:
    """Resolve the evaluator's documented explicit-before-environment selection."""
    return explicit or os.environ.get("SNOWFLAKE_CONNECTION_NAME") or None


def require_pat_connection(name: str | None, *, home: Path | None = None) -> str:
    """Reject interactive or unverifiable credentials without opening a session.

    A JWT-shaped password is only a local PAT candidate, not proof of validity;
    the actual SDK smoke call remains the authoritative authentication test.
    """
    if not name:
        raise ConnectionPreflightError("PAT evaluation requires an explicit named connection.")
    directory = home or Path(os.environ.get("SNOWFLAKE_HOME", str(Path.home() / ".snowflake")))
    selected = None
    for path, nested in (
        (directory / "connections.toml", False),
        (directory / "config.toml", True),
    ):
        if not path.exists():
            continue
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ConnectionPreflightError(
                "Cannot read connection configuration; check local TOML and permissions."
            ) from exc
        connections = data.get("connections", {}) if nested else data
        if name in connections:
            selected = connections[name]
            break
    if not isinstance(selected, dict):
        raise ConnectionPreflightError(
            "Named connection not found; configure the selected connection before running."
        )
    authenticator = str(selected.get("authenticator", "snowflake")).lower()
    if authenticator not in {"snowflake", "programmatic_access_token"}:
        raise ConnectionPreflightError(
            "Selected connection is not PAT authentication. Choose a PAT-backed connection; interactive SSO is not allowed with --require-pat."
        )
    prefix = f"SNOWFLAKE_CONNECTIONS_{name.upper()}"
    credential = os.environ.get(f"{prefix}_PASSWORD") or selected.get("password")
    if authenticator == "programmatic_access_token":
        credential = (
            os.environ.get(f"{prefix}_TOKEN")
            or os.environ.get("SNOWFLAKE_TOKEN")
            or selected.get("token")
            or credential
        )
        if not credential and (
            selected.get("token_file_path") or os.environ.get("SNOWFLAKE_TOKEN_FILE_PATH")
        ):
            credential = "configured-token-provider"
    if not isinstance(credential, str) or not credential.strip():
        raise ConnectionPreflightError(
            "Selected PAT connection has no configured password credential. Use supported connection/secret management; do not pass tokens as command arguments."
        )
    if authenticator == "snowflake" and (
        not credential.startswith("eyJ") or len(credential.split(".")) != 3
    ):
        raise ConnectionPreflightError(
            "Password authentication is not verifiably a PAT candidate. Use an explicit PAT authenticator or a PAT-backed named connection."
        )
    if not selected.get("account") or not selected.get("user"):
        raise ConnectionPreflightError(
            "PAT connection must explicitly configure account and user; no identity fallback is permitted."
        )
    return name
