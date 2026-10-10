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


@dataclass(frozen=True)
class CortexModel:
    """One tracked Snowflake CoCo model and its Table 6(e) rates.

    Rates are ``None`` when the model appears in the CoCo model picker but has no
    Table 6(e) row; cost estimates for such models are reported as unavailable.
    """

    model_id: str
    provider: str
    lifecycle: str
    input_credits_per_million: float | None
    output_credits_per_million: float | None
    cache_write_credits_per_million: float | None
    cache_read_credits_per_million: float | None


#: Effective date of the attached Snowflake Service Consumption Table 6(e).
#: Rates are AI Credits per one million tokens, not vendor API dollar prices.
CONSUMPTION_TABLE_EFFECTIVE_DATE = "2026-10-09"

#: Canonical CoCo benchmark catalog: exactly the concrete models in the CoCo
#: model picker (2026-10-08), priced from Table 6(e) where a row exists. Models
#: with no Table 6(e) row as of 2026-10-09 carry ``None`` rates. Auto routing
#: modes are not models and are excluded (see ``AUTO_MODES``).
COCO_BENCHMARK_MODELS: tuple[CortexModel, ...] = (
    CortexModel("claude-opus-4-5", "Anthropic", "GA", 2.75, 13.75, 3.44, 0.28),
    CortexModel("claude-opus-4-6", "Anthropic", "GA", 2.75, 13.75, 3.44, 0.28),
    CortexModel("claude-opus-4-7", "Anthropic", "GA", 2.75, 13.75, 3.44, 0.28),
    CortexModel("claude-opus-4-8", "Anthropic", "GA", 2.75, 13.75, 3.44, 0.28),
    CortexModel("claude-opus-5", "Anthropic", "GA", 2.75, 13.75, 3.44, 0.28),
    CortexModel("claude-opus-5-5", "Anthropic", "Preview", 2.20, 11.00, 2.75, 0.11),
    CortexModel("claude-sonnet-4-5", "Anthropic", "GA", 1.65, 8.25, 2.07, 0.17),
    CortexModel("claude-sonnet-4-6", "Anthropic", "GA", 1.65, 8.25, 2.07, 0.17),
    CortexModel("claude-sonnet-5", "Anthropic", "GA", 1.10, 5.50, 1.375, 0.11),
    CortexModel("claude-sonnet-5-5", "Anthropic", "Preview", 1.10, 5.50, 1.375, 0.055),
    CortexModel("deepseek-v4-flash", "DeepSeek", "Preview", 0.242, 0.726, None, 0.008),
    CortexModel("gemini-3.1-pro", "Google", "Preview", None, None, None, None),
    CortexModel("gemini-3.7-flash", "Google", "Preview", 0.413, 2.063, None, 0.041),
    CortexModel("gemini-3.8-flash", "Google", "Preview", 0.413, 2.063, None, 0.041),
    CortexModel("glm-5.2", "Z.ai", "Preview", None, None, None, None),
    CortexModel("glm-5.3", "Z.ai", "Preview", 0.77, 2.42, None, 0.143),
    CortexModel("grok-4.6", "xAI", "Preview", 1.10, 3.30, None, 0.275),
    CortexModel("kimi-k3", "Moonshot AI", "Preview", 1.65, 8.25, 2.063, 0.165),
    CortexModel("openai-gpt-5.2", "OpenAI", "GA", 0.97, 7.70, None, 0.10),
    CortexModel("openai-gpt-5.4", "OpenAI", "Preview", 1.38, 8.25, None, 0.14),
    CortexModel("openai-gpt-5.5", "OpenAI", "Preview", 2.75, 16.50, None, 0.28),
    CortexModel("openai-gpt-5.6-luna", "OpenAI", "GA", 0.11, 0.66, 0.138, 0.011),
    CortexModel("openai-gpt-5.6-sol", "OpenAI", "GA", 2.20, 11.00, 2.75, 0.22),
    CortexModel("openai-gpt-5.6-terra", "OpenAI", "GA", 1.10, 6.60, 1.375, 0.11),
    CortexModel("openai-gpt-6-astra", "OpenAI", "Preview", 5.50, 27.50, 6.875, 0.55),
    CortexModel("openai-gpt-6-luna", "OpenAI", "Preview", 0.055, 0.275, 0.069, 0.006),
    CortexModel("openai-gpt-6-sol", "OpenAI", "Preview", 1.10, 5.50, 1.375, 0.11),
    CortexModel("openai-gpt-6.1-sol", "OpenAI", "Preview", 1.10, 5.50, 1.375, 0.055),
)

#: Curated model IDs for client discovery. Callers may still pass any model ID
#: directly to ``complete``; this list does not impose a runtime restriction.
SUPPORTED_MODELS: tuple[str, ...] = tuple(model.model_id for model in COCO_BENCHMARK_MODELS)

#: CoCo routing modes accepted by ``--model``. They pick a concrete model at run
#: time, so they carry no Table 6(e) rates and are not part of ``--all-models``.
AUTO_MODES: tuple[str, ...] = ("auto", "auto-intelligent", "auto-efficient")


def get_benchmark_model(model_id: str) -> CortexModel | None:
    """Return benchmark metadata for ``model_id``, or ``None`` if unlisted."""
    return next((model for model in COCO_BENCHMARK_MODELS if model.model_id == model_id), None)


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
