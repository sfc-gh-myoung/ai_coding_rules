"""Transport layer for Cortex completions.

Two transports are supported:

* :func:`_complete_via_aisql` — primary path. Issues a ``SELECT AI_COMPLETE(...)``
  query against an authenticated Snowflake session managed by
  :mod:`snowflake.connector`. Returns the model's response (or, when a
  ``response_schema`` is supplied, a JSON string conforming to it).
* :func:`_complete_via_rest` — fallback. Calls the
  ``/api/v2/cortex/inference:complete`` HTTP endpoint with PAT auth and parses
  the SSE stream into a single string. Used only when the caller explicitly
  requests ``transport="rest"``.

All public entry points live in :mod:`ai_rules.cortex.client`; this module is
intentionally private.
"""

from __future__ import annotations

import json
import time
import tomllib
from functools import cache
from pathlib import Path
from typing import Any

import requests
import snowflake.connector
from snowflake.connector.errors import (
    DatabaseError,
    InterfaceError,
    OperationalError,
)

from .models import (
    DEFAULT_BATCH_CHUNK_SIZE,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT_SECONDS,
    CortexResponse,
)

# Status codes worth retrying for the REST transport.
_RETRYABLE_HTTP_STATUSES = frozenset({429, 503, 504})

# Connector exception types that represent transient failures.
_TRANSIENT_CONNECTOR_ERRORS = (OperationalError, InterfaceError)

# Base delay (seconds) for exponential backoff on retry.
_BASE_BACKOFF_SECONDS = 1.0


# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------


@cache
def _get_connection(connection_name: str | None):
    """Return a cached :class:`snowflake.connector.SnowflakeConnection`.

    When ``connection_name`` is ``None`` the connector resolves which
    connection to use in this order: the ``connection_name`` keyword argument
    to ``connect()`` (none), then the ``SNOWFLAKE_DEFAULT_CONNECTION_NAME``
    environment variable, then the ``default_connection_name`` field in
    ``~/.snowflake/config.toml``, then the connection literally named
    ``"default"``. Letting the connector own that resolution avoids
    re-implementing it here.
    """
    if connection_name is None:
        return snowflake.connector.connect()
    return snowflake.connector.connect(connection_name=connection_name)


def _build_model_parameters(
    *,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    """Build the ``model_parameters`` object passed to AI_COMPLETE."""
    return {"temperature": temperature, "max_tokens": max_tokens}


# ---------------------------------------------------------------------------
# AI_COMPLETE (SQL) transport
# ---------------------------------------------------------------------------


def _complete_via_aisql(
    prompt: str,
    *,
    model: str,
    connection_name: str | None,
    response_schema: dict[str, Any] | None,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> CortexResponse:
    """Run a single AI_COMPLETE call via the SQL transport.

    Args:
        prompt: The user prompt sent to the model.
        model: Cortex model id (e.g. ``"claude-sonnet-4-5"``).
        connection_name: Snowflake connection name, or ``None`` to let the
            connector resolve via ``SNOWFLAKE_DEFAULT_CONNECTION_NAME`` /
            ``config.toml``.
        response_schema: Optional structured-output schema (see
            :data:`ai_rules.cortex.models.KEYWORDS_SCHEMA`). When provided
            the returned ``text`` is a JSON string conforming to the schema.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens to generate.
        max_retries: Total claim attempts before giving up.

    Returns:
        :class:`CortexResponse` with ``text`` and ``request_id`` (the
        Snowflake query id).

    Raises:
        RuntimeError: If all retry attempts fail.
    """
    conn = _get_connection(connection_name)
    model_params = _build_model_parameters(temperature=temperature, max_tokens=max_tokens)

    sql_parts = [
        "SELECT AI_COMPLETE(",
        "    model => %s,",
        "    prompt => %s,",
        "    model_parameters => PARSE_JSON(%s)",
    ]
    bindings: list[Any] = [model, prompt, json.dumps(model_params)]
    if response_schema is not None:
        sql_parts.append(",    response_format => PARSE_JSON(%s)")
        bindings.append(json.dumps(response_schema))
    sql_parts.append(")")
    sql = "\n".join(sql_parts)

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            with conn.cursor() as cur:
                cur.execute(sql, bindings)
                row = cur.fetchone()
                if not row or row[0] is None:
                    raise RuntimeError("AI_COMPLETE returned no rows")
                return CortexResponse(text=str(row[0]), request_id=cur.sfqid)
        except _TRANSIENT_CONNECTOR_ERRORS as exc:
            last_error = exc
            if attempt < max_retries - 1:
                time.sleep(_BASE_BACKOFF_SECONDS * (2**attempt))
        except DatabaseError as exc:
            raise RuntimeError(f"AI_COMPLETE failed: {exc}") from exc

    raise RuntimeError(
        f"AI_COMPLETE failed after {max_retries} attempts: {last_error}"
    ) from last_error


def _complete_batch_via_aisql(
    prompts: list[tuple[str, str]],
    *,
    model: str,
    connection_name: str | None,
    response_schema: dict[str, Any] | None,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    chunk_size: int = DEFAULT_BATCH_CHUNK_SIZE,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> dict[str, CortexResponse]:
    """Run AI_COMPLETE for many prompts in chunks.

    Each chunk emits a single
    ``SELECT t.file_key, AI_COMPLETE(...) FROM (VALUES (?,?), ...) t(file_key, prompt)``
    query so the round-trip cost is amortized across many rule files.
    """
    if not prompts:
        return {}
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    conn = _get_connection(connection_name)
    model_params = _build_model_parameters(temperature=temperature, max_tokens=max_tokens)
    model_params_json = json.dumps(model_params)
    schema_json = json.dumps(response_schema) if response_schema is not None else None

    results: dict[str, CortexResponse] = {}
    for start in range(0, len(prompts), chunk_size):
        chunk = prompts[start : start + chunk_size]

        # Build the VALUES clause: (%s, %s), (%s, %s), ...
        values_clause = ", ".join(["(%s, %s)"] * len(chunk))
        sql_parts = [
            "SELECT t.file_key, AI_COMPLETE(",
            "    model => %s,",
            "    prompt => t.prompt,",
            "    model_parameters => PARSE_JSON(%s)",
        ]
        bindings: list[Any] = [model, model_params_json]
        if schema_json is not None:
            sql_parts.append(",    response_format => PARSE_JSON(%s)")
            bindings.append(schema_json)
        sql_parts.append(") AS resp")
        sql_parts.append(f"FROM (VALUES {values_clause}) AS t(file_key, prompt)")
        sql = "\n".join(sql_parts)
        for file_key, prompt in chunk:
            bindings.extend([file_key, prompt])

        last_error: Exception | None = None
        request_id: str | None = None
        rows: list[tuple[Any, Any]] | None = None
        for attempt in range(max_retries):
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, bindings)
                    rows = cur.fetchall()
                    request_id = cur.sfqid
                break
            except _TRANSIENT_CONNECTOR_ERRORS as exc:
                last_error = exc
                if attempt < max_retries - 1:
                    time.sleep(_BASE_BACKOFF_SECONDS * (2**attempt))
            except DatabaseError as exc:
                raise RuntimeError(f"AI_COMPLETE batch failed: {exc}") from exc

        if rows is None:
            raise RuntimeError(
                f"AI_COMPLETE batch failed after {max_retries} attempts: {last_error}"
            ) from last_error

        for file_key, resp_text in rows:
            if resp_text is None:
                continue
            results[str(file_key)] = CortexResponse(text=str(resp_text), request_id=request_id)

    return results


# ---------------------------------------------------------------------------
# REST transport (fallback)
# ---------------------------------------------------------------------------


def _read_rest_credentials(connection_name: str | None) -> tuple[str, str]:
    """Read ``(account, token)`` for the REST transport.

    Mirrors the connector's resolution order without instantiating a real
    connection: explicit ``connection_name`` → ``SNOWFLAKE_DEFAULT_CONNECTION_NAME``
    env var → ``default_connection_name`` in ``config.toml`` → literal ``"default"``.

    Raises:
        FileNotFoundError: If neither ``connections.toml`` nor ``config.toml``
            exists in ``~/.snowflake``.
        ValueError: If the resolved connection name is missing from the file
            or lacks ``account``/``token`` (or ``password``).
    """
    import os

    snowflake_dir = Path.home() / ".snowflake"
    connections_path = snowflake_dir / "connections.toml"
    config_path = snowflake_dir / "config.toml"

    config_file = (
        connections_path
        if connections_path.exists()
        else (config_path if config_path.exists() else None)
    )
    if config_file is None:
        raise FileNotFoundError(
            f"No Snowflake config found. Expected:\n  - {connections_path}\n  - {config_path}"
        )

    with open(config_file, "rb") as fh:
        config = tomllib.load(fh)

    resolved = (
        connection_name
        or os.environ.get("SNOWFLAKE_DEFAULT_CONNECTION_NAME")
        or config.get("default_connection_name")
        or "default"
    )

    if resolved not in config:
        available = [k for k in config if not k.startswith("default_")]
        raise ValueError(
            f"Connection '{resolved}' not found in {config_file.name}. Available: {available}"
        )

    section = config[resolved]
    account = section.get("account") or section.get("accountname") or ""
    token = section.get("token") or section.get("password") or ""
    if not account or not token:
        raise ValueError(f"Connection '{resolved}' is missing 'account' or 'token'/'password'.")
    return account, token


def _parse_cortex_sse_response(raw: str) -> str:
    """Concatenate ``data:`` chunks of a Cortex SSE response into one string."""
    parts: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        payload = line[len("data:") :].strip()
        if payload == "[DONE]":
            break
        try:
            chunk = json.loads(payload)
            choices = chunk.get("choices", [])
            if choices:
                content = choices[0].get("delta", {}).get("content", "")
                if content:
                    parts.append(content)
        except (json.JSONDecodeError, IndexError, KeyError):
            continue
    return "".join(parts)


def _complete_via_rest(
    prompt: str,
    *,
    model: str,
    connection_name: str | None,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    max_retries: int = DEFAULT_MAX_RETRIES,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> CortexResponse:
    """Run a single completion via the Cortex REST inference endpoint.

    Notes:
        Structured outputs (``response_format``) are not currently exposed by
        the REST inference endpoint in the same way as AI_COMPLETE; this
        transport always returns the model's free-form text. Callers that
        need a JSON contract should prefer the AISQL transport.
    """
    account, token = _read_rest_credentials(connection_name)

    if ".snowflakecomputing.com" in account:
        url = f"https://{account}/api/v2/cortex/inference:complete"
    else:
        url = f"https://{account}.snowflakecomputing.com/api/v2/cortex/inference:complete"

    headers: dict[str, str | bytes] = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)

            if resp.status_code == 200:
                text = _parse_cortex_sse_response(resp.text)
                return CortexResponse(text=text, request_id=None)

            if resp.status_code in _RETRYABLE_HTTP_STATUSES:
                last_error = RuntimeError(
                    f"Cortex REST returned {resp.status_code}: {resp.text[:200]}"
                )
                if attempt < max_retries - 1:
                    time.sleep(_BASE_BACKOFF_SECONDS * (2**attempt))
                continue

            raise RuntimeError(f"Cortex REST returned {resp.status_code}: {resp.text[:200]}")

        except requests.exceptions.RequestException as exc:
            last_error = RuntimeError(f"Cortex REST request failed: {exc}")
            if attempt < max_retries - 1:
                time.sleep(_BASE_BACKOFF_SECONDS * (2**attempt))

    raise last_error or RuntimeError("Cortex REST call failed after retries")
