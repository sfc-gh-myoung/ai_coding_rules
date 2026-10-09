"""Snowflake Cortex completion client.

Public API:

* :func:`complete`: single-prompt completion.
* :func:`complete_batch`: batched multi-prompt completion.
* :func:`verify_connection`: sanity check the underlying Snowflake session.
* :func:`list_models`: curated model allowlist.
* :class:`CortexResponse`: normalized response dataclass.
* :data:`DEFAULT_MODEL`, :data:`KEYWORDS_SCHEMA`, :data:`SUPPORTED_MODELS`:
  shared defaults / schemas.

Transport selection: ``transport="aisql"`` (default) issues
``SELECT AI_COMPLETE(...)`` via :mod:`snowflake.connector`; ``transport="rest"``
calls the HTTP inference endpoint with PAT auth and is intended as a fallback.
"""

from __future__ import annotations

from .client import (
    Transport,
    complete,
    complete_batch,
    list_models,
    verify_connection,
)
from .models import (
    AUTO_MODES,
    COCO_BENCHMARK_MODELS,
    CONSUMPTION_TABLE_EFFECTIVE_DATE,
    DEFAULT_BATCH_CHUNK_SIZE,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT_SECONDS,
    KEYWORDS_SCHEMA,
    SUPPORTED_MODELS,
    CortexModel,
    CortexResponse,
    get_benchmark_model,
)

__all__ = [
    "AUTO_MODES",
    "COCO_BENCHMARK_MODELS",
    "CONSUMPTION_TABLE_EFFECTIVE_DATE",
    "DEFAULT_BATCH_CHUNK_SIZE",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_MODEL",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_TIMEOUT_SECONDS",
    "KEYWORDS_SCHEMA",
    "SUPPORTED_MODELS",
    "CortexModel",
    "CortexResponse",
    "Transport",
    "complete",
    "complete_batch",
    "get_benchmark_model",
    "list_models",
    "verify_connection",
]
