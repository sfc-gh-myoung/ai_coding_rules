"""Unit tests for ai_rules.cortex.models.

Tests the public schema/defaults that other code depends on. Heavy on shape
checks because callers serialize ``KEYWORDS_SCHEMA`` directly to AI_COMPLETE.
"""

from __future__ import annotations

import json

import pytest

from ai_rules.cortex.models import (
    DEFAULT_BATCH_CHUNK_SIZE,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT_SECONDS,
    KEYWORDS_SCHEMA,
    SUPPORTED_MODELS,
    CortexResponse,
)


class TestDefaults:
    """Sanity checks on the public default values."""

    @pytest.mark.unit
    def test_default_model_is_a_supported_model(self):
        """DEFAULT_MODEL is present in the curated SUPPORTED_MODELS allowlist."""
        assert DEFAULT_MODEL in SUPPORTED_MODELS

    @pytest.mark.unit
    def test_numeric_defaults_are_sensible(self):
        """Numeric defaults are within reasonable bounds."""
        assert DEFAULT_MAX_RETRIES >= 1
        assert DEFAULT_MAX_TOKENS > 0
        assert DEFAULT_BATCH_CHUNK_SIZE > 0
        assert DEFAULT_TIMEOUT_SECONDS > 0
        assert 0.0 <= DEFAULT_TEMPERATURE <= 2.0


class TestSupportedModels:
    """Curated allowlist must include the models we have validated."""

    @pytest.mark.unit
    def test_includes_claude_family(self):
        """The Claude family is the primary validated model set."""
        assert "claude-sonnet-4-5" in SUPPORTED_MODELS
        assert "claude-opus-4-7" in SUPPORTED_MODELS

    @pytest.mark.unit
    def test_no_duplicate_entries(self):
        """The list must not contain duplicate model ids."""
        assert len(SUPPORTED_MODELS) == len(set(SUPPORTED_MODELS))

    @pytest.mark.unit
    def test_is_immutable_tuple(self):
        """Tuples prevent accidental in-place mutation by callers."""
        assert isinstance(SUPPORTED_MODELS, tuple)


class TestKeywordsSchema:
    """KEYWORDS_SCHEMA must be a valid AI_COMPLETE response_format payload."""

    @pytest.mark.unit
    def test_top_level_shape(self):
        """Schema declares ``type='json'`` and contains an inner schema."""
        assert KEYWORDS_SCHEMA["type"] == "json"
        assert "schema" in KEYWORDS_SCHEMA

    @pytest.mark.unit
    def test_inner_schema_requires_keywords_array(self):
        """Inner schema constrains output to ``{"keywords": [str]}``."""
        schema = KEYWORDS_SCHEMA["schema"]
        assert schema["type"] == "object"
        assert "keywords" in schema["required"]
        assert schema["properties"]["keywords"]["type"] == "array"
        assert schema["properties"]["keywords"]["items"]["type"] == "string"

    @pytest.mark.unit
    def test_round_trips_through_json(self):
        """Serialized schema is what gets passed to PARSE_JSON in SQL."""
        rendered = json.dumps(KEYWORDS_SCHEMA)
        assert json.loads(rendered) == KEYWORDS_SCHEMA


class TestCortexResponse:
    """Frozen-dataclass invariants."""

    @pytest.mark.unit
    def test_default_request_id_is_none(self):
        """``request_id`` defaults to None for transports without query ids."""
        resp = CortexResponse(text="hello")
        assert resp.text == "hello"
        assert resp.request_id is None

    @pytest.mark.unit
    def test_is_frozen(self):
        """Frozen dataclass disallows attribute mutation."""
        resp = CortexResponse(text="x")
        with pytest.raises(Exception, match="cannot assign"):
            resp.text = "y"  # type: ignore[misc]

    @pytest.mark.unit
    def test_equality_by_value(self):
        """Two responses with identical fields compare equal."""
        a = CortexResponse(text="x", request_id="01b")
        b = CortexResponse(text="x", request_id="01b")
        assert a == b
