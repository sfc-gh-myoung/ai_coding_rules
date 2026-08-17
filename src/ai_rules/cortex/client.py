"""Public functional API for the Snowflake Cortex client.

Most callers should use :func:`complete` (single prompt) or
:func:`complete_batch` (many prompts in one round trip). Both default to the
``aisql`` transport which dispatches a ``SELECT AI_COMPLETE(...)`` query
through ``snowflake-connector-python``; pass ``transport="rest"`` to fall back
to the HTTP inference endpoint.

Example:
    >>> from ai_rules.cortex import complete, KEYWORDS_SCHEMA
    >>> resp = complete(
    ...     "Summarize this rule into 5-15 keywords as JSON.",
    ...     response_schema=KEYWORDS_SCHEMA,
    ... )
    >>> import json
    >>> json.loads(resp.text)["keywords"]
    ['snowflake', 'cortex', ...]
"""

from __future__ import annotations

from typing import Any, Literal

from .models import (
    DEFAULT_BATCH_CHUNK_SIZE,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    SUPPORTED_MODELS,
    CortexResponse,
)
from .transport import (
    _complete_batch_via_aisql,
    _complete_via_aisql,
    _complete_via_rest,
    _get_connection,
)

Transport = Literal["aisql", "rest"]


def complete(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    connection_name: str | None = None,
    transport: Transport = "aisql",
    response_schema: dict[str, Any] | None = None,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> CortexResponse:
    """Send a single prompt to Cortex and return the model's response.

    Args:
        prompt: User prompt text.
        model: Cortex model id. Defaults to
            :data:`ai_rules.cortex.models.DEFAULT_MODEL`.
        connection_name: Snowflake connection name. ``None`` means "let the
            connector resolve via ``SNOWFLAKE_DEFAULT_CONNECTION_NAME`` or
            ``config.toml``".
        transport: ``"aisql"`` (default, runs ``SELECT AI_COMPLETE(...)``) or
            ``"rest"`` (HTTP inference endpoint with PAT auth).
        response_schema: Optional JSON schema for structured outputs. Only
            honored by the ``aisql`` transport; ignored on REST.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens to generate.
        max_retries: Total claim attempts before giving up.

    Returns:
        A :class:`CortexResponse`.

    Raises:
        RuntimeError: On a transport-level failure or after exhausting retries.
        ValueError: On unknown ``transport``.
    """
    if transport == "aisql":
        return _complete_via_aisql(
            prompt,
            model=model,
            connection_name=connection_name,
            response_schema=response_schema,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
        )
    if transport == "rest":
        return _complete_via_rest(
            prompt,
            model=model,
            connection_name=connection_name,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
        )
    raise ValueError(f"Unknown transport: {transport!r}. Use 'aisql' or 'rest'.")


def complete_batch(
    prompts: list[tuple[str, str]],
    *,
    model: str = DEFAULT_MODEL,
    connection_name: str | None = None,
    transport: Transport = "aisql",
    response_schema: dict[str, Any] | None = None,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    chunk_size: int = DEFAULT_BATCH_CHUNK_SIZE,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> dict[str, CortexResponse]:
    """Send many prompts to Cortex, returning a mapping of file_key -> response.

    The ``aisql`` transport batches every ``chunk_size`` prompts into one
    SQL statement using ``SELECT ... FROM (VALUES ...)``, dramatically
    reducing round-trip overhead vs. per-prompt calls. The ``rest`` transport
    falls back to sequential per-prompt requests.

    Args:
        prompts: List of ``(file_key, prompt)`` tuples. ``file_key`` is an
            arbitrary caller-supplied identifier used as the dictionary key.
        model: Cortex model id (see :func:`complete`).
        connection_name: Snowflake connection name; ``None`` defers to the
            connector for resolution.
        transport: ``"aisql"`` (batched) or ``"rest"`` (sequential fallback).
        response_schema: Optional structured-output schema. Honored on AISQL
            only.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens per response.
        chunk_size: Maximum prompts per AISQL statement. Ignored for REST.
        max_retries: Total claim attempts per chunk before giving up.

    Returns:
        Dict mapping each ``file_key`` to its :class:`CortexResponse`. Keys
        for which the model returned ``NULL`` are omitted.
    """
    if not prompts:
        return {}

    if transport == "aisql":
        return _complete_batch_via_aisql(
            prompts,
            model=model,
            connection_name=connection_name,
            response_schema=response_schema,
            temperature=temperature,
            max_tokens=max_tokens,
            chunk_size=chunk_size,
            max_retries=max_retries,
        )
    if transport == "rest":
        results: dict[str, CortexResponse] = {}
        for file_key, prompt in prompts:
            results[file_key] = _complete_via_rest(
                prompt,
                model=model,
                connection_name=connection_name,
                temperature=temperature,
                max_tokens=max_tokens,
                max_retries=max_retries,
            )
        return results
    raise ValueError(f"Unknown transport: {transport!r}. Use 'aisql' or 'rest'.")


def verify_connection(connection_name: str | None = None) -> dict[str, str]:
    """Verify the underlying Snowflake connection and return identity info.

    Useful for ``ai-rules`` doctor-style commands and integration smoke tests.

    Args:
        connection_name: Snowflake connection name, or ``None`` for the
            connector-resolved default.

    Returns:
        Dict with keys ``account``, ``user``, ``role``, ``warehouse`` (each
        may be empty if the connector did not populate it).

    Raises:
        RuntimeError: If the underlying connection cannot be established or
            the verification query fails.
    """
    try:
        conn = _get_connection(connection_name)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()"
            )
            row = cur.fetchone() or ("", "", "", "")
        return {
            "account": str(row[0] or ""),
            "user": str(row[1] or ""),
            "role": str(row[2] or ""),
            "warehouse": str(row[3] or ""),
        }
    except Exception as exc:  # pragma: no cover - defensive boundary
        raise RuntimeError(f"Cortex connection verification failed: {exc}") from exc


def list_models() -> list[str]:
    """Return the curated list of validated Cortex model ids."""
    return list(SUPPORTED_MODELS)
