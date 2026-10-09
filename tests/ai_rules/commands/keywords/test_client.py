"""Hermetic tests for the keyword Cortex client, response parsing and API branch.

No test reads the developer's real ``~/.snowflake`` configuration or makes a
network call: ``Path.home`` points at a temporary directory, ``requests.post``
is replaced with a fake, and ``time.sleep`` is a no-op.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import requests

from ai_rules.commands.rule_loader.keywords import KeywordExtractor
from ai_rules.commands.rule_loader.keywords import client as client_module
from ai_rules.commands.rule_loader.keywords.client import (
    CortexClient,
    _call_cortex_complete,
    _parse_cortex_sse_response,
    load_snowflake_config,
)
from ai_rules.commands.rule_loader.keywords.prompts import ParseResult, _parse_keyword_response

RULE_CONTENT = """\
---
keywords:
  - pytest fixtures
---

## Mandatory

- Use `pytest.fixture` for shared setup and `parametrize` for data-driven tests.
"""


def _sse(*chunks: str) -> str:
    lines = [
        "data: " + json.dumps({"choices": [{"delta": {"content": chunk}}]}) for chunk in chunks
    ]
    return "\n".join([*lines, "data: [DONE]"])


class _Response:
    def __init__(self, status_code: int, text: str) -> None:
        self.status_code = status_code
        self.text = text


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolated home directory with an empty .snowflake folder."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    (tmp_path / ".snowflake").mkdir()
    return tmp_path


@pytest.fixture
def connection(home: Path) -> Path:
    """connections.toml with a test connection that has an account and token."""
    path = home / ".snowflake" / "connections.toml"
    path.write_text('[test]\naccount = "acme-test"\ntoken = "fake-token"\n', encoding="utf-8")
    return path


@pytest.fixture
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record retry delays instead of sleeping."""
    delays: list[float] = []
    monkeypatch.setattr(client_module.time, "sleep", delays.append)
    return delays


def _fake_post(monkeypatch: pytest.MonkeyPatch, outcomes: list) -> list[dict]:
    """Replace requests.post with a fake returning or raising each outcome in turn."""
    calls: list[dict] = []
    queue = list(outcomes)

    def fake(url, headers, json, timeout):
        calls.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        outcome = queue.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    monkeypatch.setattr(requests, "post", fake)
    return calls


class TestLoadSnowflakeConfig:
    @pytest.mark.unit
    def test_reads_connections_toml(self, connection: Path) -> None:
        assert load_snowflake_config("test")["account"] == "acme-test"

    @pytest.mark.unit
    def test_falls_back_to_config_toml(self, home: Path) -> None:
        (home / ".snowflake" / "config.toml").write_text(
            '[other]\naccount = "acme-cfg"\n', encoding="utf-8"
        )
        assert load_snowflake_config("other") == {"account": "acme-cfg"}

    @pytest.mark.unit
    def test_missing_config_raises(self, home: Path) -> None:
        with pytest.raises(FileNotFoundError, match="No Snowflake config found"):
            load_snowflake_config("test")

    @pytest.mark.unit
    def test_unknown_connection_lists_available(self, connection: Path) -> None:
        with pytest.raises(ValueError, match=r"Available: \['test'\]"):
            load_snowflake_config("missing")


class TestParseCortexSseResponse:
    @pytest.mark.unit
    def test_joins_content_until_done_and_skips_noise(self) -> None:
        raw = "\n".join(
            [
                ": keep-alive",
                "data: not-json",
                'data: {"choices": []}',
                _sse("alpha ", "beta"),
                "data: " + json.dumps({"choices": [{"delta": {"content": "ignored"}}]}),
            ]
        )
        assert _parse_cortex_sse_response(raw) == "alpha beta"


class TestParseKeywordResponse:
    @pytest.mark.unit
    def test_object_shape_keeps_rationale_and_count(self) -> None:
        text = json.dumps(
            [
                {"keyword": "pytest fixtures", "rationale": "fixture setup"},
                {"keyword": " ", "rationale": "blank is dropped"},
                {"keyword": "parametrize cases", "rationale": "data-driven tests"},
                {"keyword": "third", "rationale": "over count"},
            ]
        )
        result = _parse_keyword_response(f"Here you go: {text}", count=2)
        assert result.keywords == ["pytest fixtures", "parametrize cases"]
        assert result.rationale_map == {
            "pytest fixtures": "fixture setup",
            "parametrize cases": "data-driven tests",
        }

    @pytest.mark.unit
    def test_string_list_shape(self) -> None:
        result = _parse_keyword_response('["a b", " ", "c d"]', count=5)
        assert result.keywords == ["a b", "c d"]
        assert result.rationale_map == {"a b": "", "c d": ""}

    @pytest.mark.unit
    def test_comma_fallback_after_invalid_json(self) -> None:
        result = _parse_keyword_response("[not json], \"cache ttl\", 'session state'", count=5)
        assert result.keywords == ["[not json]", "cache ttl", "session state"]

    @pytest.mark.unit
    def test_newline_fallback_strips_bullets(self) -> None:
        result = _parse_keyword_response("- cache ttl\n2. session state\n\n", count=5)
        assert result.keywords == ["cache ttl", "session state"]


class TestCortexClient:
    @pytest.mark.unit
    def test_missing_token_raises_before_request(
        self, home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (home / ".snowflake" / "connections.toml").write_text(
            '[test]\naccount = "acme-test"\n', encoding="utf-8"
        )
        calls = _fake_post(monkeypatch, [])
        with pytest.raises(RuntimeError, match="missing 'account' or 'token'"):
            CortexClient(connection_name="test").generate_keywords(RULE_CONTENT, count=5)
        assert calls == []

    @pytest.mark.unit
    def test_success_builds_request_and_parses(
        self, connection: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        body = json.dumps([{"keyword": "pytest fixtures", "rationale": "setup"}])
        calls = _fake_post(monkeypatch, [_Response(200, _sse(body))])

        result = CortexClient(connection_name="test", model="test-model").generate_keywords(
            RULE_CONTENT, count=9, debug=True
        )

        assert result.keywords == ["pytest fixtures"]
        call = calls[0]
        assert (
            call["url"]
            == "https://acme-test.snowflakecomputing.com/api/v2/cortex/inference:complete"
        )
        assert call["headers"]["Authorization"] == "Bearer fake-token"
        assert call["json"]["model"] == "test-model"
        assert "EXACTLY 5 to 7 keywords" in call["json"]["messages"][0]["content"]

    @pytest.mark.unit
    def test_full_host_account_is_used_verbatim(
        self, home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (home / ".snowflake" / "connections.toml").write_text(
            '[test]\naccount = "acme.snowflakecomputing.com"\npassword = "pw"\n',
            encoding="utf-8",
        )
        calls = _fake_post(monkeypatch, [_Response(200, _sse('["a b"]'))])
        CortexClient(connection_name="test").generate_keywords(RULE_CONTENT, count=3)
        assert (
            calls[0]["url"]
            == "https://acme.snowflakecomputing.com/api/v2/cortex/inference:complete"
        )

    @pytest.mark.unit
    def test_retryable_status_then_success(
        self, connection: Path, monkeypatch: pytest.MonkeyPatch, no_sleep: list[float]
    ) -> None:
        _fake_post(monkeypatch, [_Response(429, "slow down"), _Response(200, _sse('["a b"]'))])
        result = CortexClient(connection_name="test").generate_keywords(
            RULE_CONTENT, count=5, debug=True
        )
        assert result.keywords == ["a b"]
        assert no_sleep == [1.0]

    @pytest.mark.unit
    def test_retryable_status_exhausts_retries(
        self, connection: Path, monkeypatch: pytest.MonkeyPatch, no_sleep: list[float]
    ) -> None:
        _fake_post(monkeypatch, [_Response(503, "busy")] * 3)
        with pytest.raises(RuntimeError, match="returned 503"):
            CortexClient(connection_name="test").generate_keywords(RULE_CONTENT, count=5)
        assert no_sleep == [1.0, 2.0, 4.0]

    @pytest.mark.unit
    def test_non_retryable_status_raises_immediately(
        self, connection: Path, monkeypatch: pytest.MonkeyPatch, no_sleep: list[float]
    ) -> None:
        calls = _fake_post(monkeypatch, [_Response(401, "unauthorized")])
        with pytest.raises(RuntimeError, match="returned 401"):
            CortexClient(connection_name="test").generate_keywords(RULE_CONTENT, count=5)
        assert len(calls) == 1
        assert no_sleep == []

    @pytest.mark.unit
    def test_request_exceptions_retry_then_raise(
        self, connection: Path, monkeypatch: pytest.MonkeyPatch, no_sleep: list[float]
    ) -> None:
        error = requests.exceptions.ConnectionError("offline")
        _fake_post(monkeypatch, [error, error, error])
        with pytest.raises(RuntimeError, match="request failed: offline"):
            CortexClient(connection_name="test").generate_keywords(RULE_CONTENT, count=5)
        assert no_sleep == [1.0, 2.0]

    @pytest.mark.unit
    def test_compat_wrapper_returns_keywords(
        self, connection: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _fake_post(monkeypatch, [_Response(200, _sse('["a b", "c d"]'))])
        assert _call_cortex_complete(RULE_CONTENT, connection_name="test", count=5) == [
            "a b",
            "c d",
        ]


class TestExtractorApiBranch:
    @pytest.fixture
    def rule_file(self, tmp_path: Path) -> Path:
        path = tmp_path / "206-python-pytest.md"
        path.write_text(RULE_CONTENT, encoding="utf-8")
        return path

    @pytest.mark.unit
    def test_api_keywords_are_merged(
        self, rule_file: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        result_from_api = ParseResult(
            keywords=["pytest fixture scope"], rationale_map={"pytest fixture scope": "scope"}
        )
        monkeypatch.setattr(
            CortexClient, "generate_keywords", lambda self, content, count, debug: result_from_api
        )
        result = KeywordExtractor(connection_name="test").suggest_keywords(rule_file, count=5)
        assert "pytest fixture scope" in result.suggested_keywords

    @pytest.mark.unit
    def test_api_failure_falls_back_to_heuristics(
        self, rule_file: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fail(self, content, count, debug):
            raise RuntimeError("unavailable")

        monkeypatch.setattr(CortexClient, "generate_keywords", fail)
        api_result = KeywordExtractor(connection_name="test").suggest_keywords(rule_file, count=5)
        heuristic = KeywordExtractor(connection_name="test").suggest_keywords(
            rule_file, count=5, use_api=False
        )
        assert api_result.suggested_keywords == heuristic.suggested_keywords
