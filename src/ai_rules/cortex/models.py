"""Data models, defaults, and JSON schemas for the Cortex client.

This module is the stable contract surface of :mod:`ai_rules.cortex`. Callers
that only need a response type, the default model id, or a structured-output
schema can import from here without pulling in the transport layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

#: Default Cortex model used by all callers unless overridden.
DEFAULT_MODEL: str = "claude-sonnet-4-5"

#: Default per-request HTTP/AI_COMPLETE timeout in seconds.
DEFAULT_TIMEOUT_SECONDS: float = 30.0

#: Default maximum claim attempts on transient failures.
DEFAULT_MAX_RETRIES: int = 3

#: Default ``max_tokens`` parameter passed to the model.
DEFAULT_MAX_TOKENS: int = 500

#: Default sampling temperature. ``0.0`` keeps outputs deterministic.
DEFAULT_TEMPERATURE: float = 0.0

#: Default chunk size for :func:`ai_rules.cortex.complete_batch`. Each chunk
#: becomes one ``SELECT ... FROM (VALUES ...)`` statement against AI_COMPLETE.
DEFAULT_BATCH_CHUNK_SIZE: int = 20


# ---------------------------------------------------------------------------
# Curated supported models
# ---------------------------------------------------------------------------

#: Curated allowlist of Cortex models this client has been validated against.
#: Snowflake supports more; callers may pass any model id at runtime — this
#: list is used by :func:`ai_rules.cortex.list_models` for discovery only.
SUPPORTED_MODELS: tuple[str, ...] = (
    "claude-sonnet-4-5",
    "claude-opus-4-7",
    "claude-3-5-sonnet",
    "mistral-large2",
    "llama3.1-70b",
    "llama3.1-405b",
    "snowflake-arctic",
)


# ---------------------------------------------------------------------------
# Structured output schemas
# ---------------------------------------------------------------------------

#: AI_COMPLETE ``response_format`` schema for keyword-extraction prompts.
#:
#: Passing this as ``response_schema`` to :func:`ai_rules.cortex.complete`
#: forces the model to return a JSON object of the form
#: ``{"keywords": ["…", "…"]}``, eliminating the need for downstream regex
#: parsing of free-form responses.
KEYWORDS_SCHEMA: dict[str, Any] = {
    "type": "json",
    "schema": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
            }
        },
        "required": ["keywords"],
    },
}


# ---------------------------------------------------------------------------
# Response type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CortexResponse:
    """Normalized response from a single Cortex completion.

    Attributes:
        text: The model's textual output. When a ``response_schema`` was
            supplied the text is the raw JSON string conforming to that
            schema; callers are responsible for ``json.loads``.
        request_id: The Snowflake query id (``cur.sfqid``) for AI_COMPLETE
            requests, or ``None`` for REST-transport responses where no
            query id is exposed.
    """

    text: str
    request_id: str | None = None
