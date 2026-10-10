"""Unit tests for ai_rules.cortex.models.

Tests the public schema/defaults that other code depends on. Heavy on shape
checks because callers serialize ``KEYWORDS_SCHEMA`` directly to AI_COMPLETE.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from ai_rules.cortex.models import (
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
    CortexResponse,
    get_benchmark_model,
)

#: The concrete models in the CoCo model picker (2026-10-08), excluding Auto modes.
TRACKED_MODELS = {
    "openai-gpt-6-astra",
    "claude-opus-5-5",
    "openai-gpt-6-sol",
    "claude-opus-5",
    "claude-opus-4-8",
    "claude-opus-4-7",
    "claude-opus-4-6",
    "claude-sonnet-5-5",
    "claude-opus-4-5",
    "claude-sonnet-5",
    "claude-sonnet-4-6",
    "claude-sonnet-4-5",
    "openai-gpt-5.6-sol",
    "openai-gpt-5.5",
    "openai-gpt-5.4",
    "openai-gpt-5.2",
    "gemini-3.1-pro",
    "gemini-3.8-flash",
    "openai-gpt-6-luna",
    "kimi-k3",
    "deepseek-v4-flash",
    "glm-5.2",
    "glm-5.3",
    "openai-gpt-5.6-terra",
    "openai-gpt-5.6-luna",
    "openai-gpt-6.1-sol",
    "grok-4.6",
    "gemini-3.7-flash",
}

#: Table 6(e) rates (input, output, cache write, cache read) per catalog model.
#: Rows for models whose Table 6(e) rows did not change between the 2026-09-25
#: and 2026-10-09 revisions must stay exactly as they were.
EXPECTED_RATES = {
    "claude-opus-4-5": (2.75, 13.75, 3.44, 0.28),
    "claude-opus-4-6": (2.75, 13.75, 3.44, 0.28),
    "claude-opus-4-7": (2.75, 13.75, 3.44, 0.28),
    "claude-opus-4-8": (2.75, 13.75, 3.44, 0.28),
    "claude-opus-5": (2.75, 13.75, 3.44, 0.28),
    "claude-opus-5-5": (2.20, 11.00, 2.75, 0.11),
    "claude-sonnet-4-5": (1.65, 8.25, 2.07, 0.17),
    "claude-sonnet-4-6": (1.65, 8.25, 2.07, 0.17),
    "claude-sonnet-5": (1.10, 5.50, 1.375, 0.11),
    "claude-sonnet-5-5": (1.10, 5.50, 1.375, 0.055),
    "deepseek-v4-flash": (0.242, 0.726, None, 0.008),
    "gemini-3.1-pro": (None, None, None, None),
    "gemini-3.7-flash": (0.413, 2.063, None, 0.041),
    "gemini-3.8-flash": (0.413, 2.063, None, 0.041),
    "glm-5.2": (None, None, None, None),
    "glm-5.3": (0.77, 2.42, None, 0.143),
    "grok-4.6": (1.10, 3.30, None, 0.275),
    "kimi-k3": (1.65, 8.25, 2.063, 0.165),
    "openai-gpt-5.2": (0.97, 7.70, None, 0.10),
    "openai-gpt-5.4": (1.38, 8.25, None, 0.14),
    "openai-gpt-5.5": (2.75, 16.50, None, 0.28),
    "openai-gpt-5.6-luna": (0.11, 0.66, 0.138, 0.011),
    "openai-gpt-5.6-sol": (2.20, 11.00, 2.75, 0.22),
    "openai-gpt-5.6-terra": (1.10, 6.60, 1.375, 0.11),
    "openai-gpt-6-astra": (5.50, 27.50, 6.875, 0.55),
    "openai-gpt-6-luna": (0.055, 0.275, 0.069, 0.006),
    "openai-gpt-6-sol": (1.10, 5.50, 1.375, 0.11),
    "openai-gpt-6.1-sol": (1.10, 5.50, 1.375, 0.055),
}

RUN_EVAL_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "run-eval.sh"
EVAL_DOC = Path(__file__).resolve().parents[3] / "docs" / "EVALUATING_RULE_LOADER.md"


def _script_models() -> list[str]:
    """Return the entries of the ``MODELS`` array in ``scripts/run-eval.sh``."""
    text = RUN_EVAL_SCRIPT.read_text(encoding="utf-8")
    match = re.search(r"^readonly MODELS=\(\n(.*?)^\)", text, re.MULTILINE | re.DOTALL)
    assert match is not None, "MODELS array not found in run-eval.sh"
    return [line.strip() for line in match.group(1).splitlines() if line.strip()]


def _documented_models() -> list[str]:
    """Return the model IDs listed under "Benchmark model catalog" in the eval doc."""
    text = EVAL_DOC.read_text(encoding="utf-8")
    match = re.search(r"model picker as of [\d-]+:\n\n(.*?)\n\n", text, re.DOTALL)
    assert match is not None, "model list not found in EVALUATING_RULE_LOADER.md"
    return re.findall(r"`([^`]+)`", match.group(1))


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
        assert "claude-sonnet-5" in SUPPORTED_MODELS
        assert "claude-opus-5" in SUPPORTED_MODELS
        assert "openai-gpt-5.6-terra" in SUPPORTED_MODELS

    @pytest.mark.unit
    def test_excludes_legacy_and_end_of_life_models(self):
        """Only current GA and preview Table 6(e) models are benchmarked."""
        assert "claude-3-5-sonnet" not in SUPPORTED_MODELS
        assert "mistral-large2" not in SUPPORTED_MODELS
        assert "llama3.1-70b" not in SUPPORTED_MODELS
        assert "snowflake-arctic" not in SUPPORTED_MODELS

    @pytest.mark.unit
    def test_table_6e_rates_are_available_for_each_model(self):
        """Every benchmark model carries the canonical input and output rates."""
        assert CONSUMPTION_TABLE_EFFECTIVE_DATE == "2026-10-09"
        assert len(COCO_BENCHMARK_MODELS) == len(SUPPORTED_MODELS)
        sonnet = get_benchmark_model("claude-sonnet-5")
        terra = get_benchmark_model("openai-gpt-5.6-terra")
        assert sonnet is not None
        assert terra is not None
        assert sonnet.input_credits_per_million == 1.10
        assert terra.output_credits_per_million == 6.60
        assert get_benchmark_model("claude-3-5-sonnet") is None

    @pytest.mark.unit
    def test_tracks_exactly_the_coco_picker_models(self):
        """The catalog is the tracked CoCo picker set; unpriced models carry no rates."""
        assert set(SUPPORTED_MODELS) == TRACKED_MODELS
        opus = get_benchmark_model("claude-opus-5-5")
        assert opus is not None
        assert (opus.input_credits_per_million, opus.output_credits_per_million) == (2.20, 11.00)
        for model_id in ("gemini-3.1-pro", "glm-5.2"):
            model = get_benchmark_model(model_id)
            assert model is not None
            assert model.input_credits_per_million is None
            assert model.output_credits_per_million is None
            assert model.cache_write_credits_per_million is None
            assert model.cache_read_credits_per_million is None

    @pytest.mark.unit
    def test_rates_match_table_6e(self):
        """Every catalog row carries exactly its Table 6(e) rates, or None if unlisted."""
        actual = {
            m.model_id: (
                m.input_credits_per_million,
                m.output_credits_per_million,
                m.cache_write_credits_per_million,
                m.cache_read_credits_per_million,
            )
            for m in COCO_BENCHMARK_MODELS
        }
        assert actual == EXPECTED_RATES

    @pytest.mark.unit
    def test_run_eval_script_lists_exactly_the_catalog(self):
        """scripts/run-eval.sh runs every catalog model once and no Auto modes."""
        script_models = _script_models()
        assert len(script_models) == len(set(script_models))
        assert set(script_models) == set(SUPPORTED_MODELS)
        assert not set(script_models) & set(AUTO_MODES)
        assert not [m for m in script_models if m.startswith("auto")]

    @pytest.mark.unit
    def test_eval_doc_lists_exactly_the_catalog(self):
        """docs/EVALUATING_RULE_LOADER.md names every catalog model once."""
        documented = _documented_models()
        assert len(documented) == len(set(documented))
        assert set(documented) == set(SUPPORTED_MODELS)

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
