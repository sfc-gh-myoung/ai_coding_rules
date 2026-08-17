"""Unit tests for ai_rules.cortex.client and transport.

These tests mock :mod:`snowflake.connector` and :mod:`requests` so they run
hermetically without a real Snowflake account or network access.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from ai_rules.cortex import (
    KEYWORDS_SCHEMA,
    SUPPORTED_MODELS,
    CortexResponse,
    complete,
    complete_batch,
    list_models,
)
from ai_rules.cortex import transport as transport_module


@pytest.fixture(autouse=True)
def _reset_connection_cache():
    """Clear the @cache on _get_connection between tests."""
    transport_module._get_connection.cache_clear()
    yield
    transport_module._get_connection.cache_clear()


def _make_fake_connection(rows: list[tuple[Any, ...]] | None = None, sfqid: str = "01abc"):
    """Build a fake snowflake connection whose cursor returns ``rows``."""
    rows = rows or [("response-text",)]
    cursor = MagicMock()
    cursor.fetchone.return_value = rows[0]
    cursor.fetchall.return_value = rows
    cursor.sfqid = sfqid
    cursor.__enter__ = lambda self: self
    cursor.__exit__ = lambda self, *exc: False
    cursor.execute = MagicMock()

    conn = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


class TestListModels:
    """Public list_models helper."""

    @pytest.mark.unit
    def test_returns_curated_list(self):
        """Returned list matches SUPPORTED_MODELS as a set."""
        models = list_models()
        assert "claude-sonnet-4-5" in models
        assert set(models) == set(SUPPORTED_MODELS)

    @pytest.mark.unit
    def test_returns_a_fresh_list_each_call(self):
        """Callers can mutate the returned list without affecting the source."""
        a = list_models()
        a.append("rogue")
        assert "rogue" not in list_models()


class TestCompleteAISQL:
    """complete() with the default AISQL transport."""

    @pytest.mark.unit
    def test_runs_select_aicomplete_and_returns_text(self):
        """SELECT AI_COMPLETE binds (model, prompt, params) and returns first row + sfqid."""
        conn, cursor = _make_fake_connection(rows=[("hello world",)], sfqid="01q")
        with patch.object(transport_module, "_get_connection", return_value=conn):
            resp = complete("a prompt", model="claude-sonnet-4-5", connection_name="myconn")

        assert isinstance(resp, CortexResponse)
        assert resp.text == "hello world"
        assert resp.request_id == "01q"

        sql, bindings = cursor.execute.call_args.args
        assert "AI_COMPLETE" in sql
        assert bindings[0] == "claude-sonnet-4-5"
        assert bindings[1] == "a prompt"
        params = json.loads(bindings[2])
        assert params["temperature"] == 0.0
        assert params["max_tokens"] > 0

    @pytest.mark.unit
    def test_response_schema_is_passed_to_sql(self):
        """A response_schema kwarg adds a response_format clause + binding."""
        conn, cursor = _make_fake_connection(rows=[('{"keywords": ["a"]}',)])
        with patch.object(transport_module, "_get_connection", return_value=conn):
            resp = complete(
                "p",
                response_schema=KEYWORDS_SCHEMA,
                connection_name="c",
            )

        sql, bindings = cursor.execute.call_args.args
        assert "response_format" in sql
        # Last binding is the JSON-serialized response schema.
        assert json.loads(bindings[-1]) == KEYWORDS_SCHEMA
        assert json.loads(resp.text) == {"keywords": ["a"]}

    @pytest.mark.unit
    def test_no_schema_omits_response_format_clause(self):
        """Without response_schema the SQL has no response_format binding."""
        conn, cursor = _make_fake_connection(rows=[("x",)])
        with patch.object(transport_module, "_get_connection", return_value=conn):
            complete("p", connection_name="c")

        sql, bindings = cursor.execute.call_args.args
        assert "response_format" not in sql
        # Without schema we get exactly 3 bindings: model, prompt, params.
        assert len(bindings) == 3

    @pytest.mark.unit
    def test_passes_explicit_connection_name_to_connector(self):
        """An explicit connection_name is forwarded as a kwarg."""
        conn, _ = _make_fake_connection()
        with patch("snowflake.connector.connect", return_value=conn) as mock_connect:
            complete("p", connection_name="snowhouse_sso")
        mock_connect.assert_called_once_with(connection_name="snowhouse_sso")

    @pytest.mark.unit
    def test_none_connection_name_defers_resolution_to_connector(self):
        """connection_name=None calls connect() with no kwargs (connector resolves)."""
        conn, _ = _make_fake_connection()
        with patch("snowflake.connector.connect", return_value=conn) as mock_connect:
            complete("p", connection_name=None)
        mock_connect.assert_called_once_with()

    @pytest.mark.unit
    def test_retries_on_transient_connector_error(self):
        """A transient OperationalError is retried with backoff and eventually succeeds."""
        from snowflake.connector.errors import OperationalError

        conn, cursor = _make_fake_connection(rows=[("recovered",)])
        cursor.execute.side_effect = [OperationalError("transient"), None]

        with (
            patch.object(transport_module, "_get_connection", return_value=conn),
            patch.object(transport_module.time, "sleep"),
        ):
            resp = complete("p", connection_name="c", max_retries=3)
        assert resp.text == "recovered"
        assert cursor.execute.call_count == 2

    @pytest.mark.unit
    def test_raises_after_exhausting_retries(self):
        """A persistent OperationalError raises RuntimeError once retries are exhausted."""
        from snowflake.connector.errors import OperationalError

        conn, cursor = _make_fake_connection()
        cursor.execute.side_effect = OperationalError("never recovers")

        with (
            patch.object(transport_module, "_get_connection", return_value=conn),
            patch.object(transport_module.time, "sleep"),
            pytest.raises(RuntimeError, match="AI_COMPLETE failed after"),
        ):
            complete("p", connection_name="c", max_retries=2)


class TestCompleteREST:
    """complete() with transport='rest'."""

    @pytest.mark.unit
    def test_parses_sse_response(self):
        """SSE deltas are concatenated into a single text body."""
        sse = (
            'data: {"choices":[{"delta":{"content":"hello"}}]}\n\n'
            'data: {"choices":[{"delta":{"content":" world"}}]}\n\n'
            "data: [DONE]\n\n"
        )
        fake_resp = MagicMock(status_code=200, text=sse)

        with (
            patch.object(
                transport_module,
                "_read_rest_credentials",
                return_value=("myacct", "tok"),
            ),
            patch.object(transport_module.requests, "post", return_value=fake_resp),
        ):
            resp = complete("p", transport="rest", connection_name="c")
        assert resp.text == "hello world"
        assert resp.request_id is None

    @pytest.mark.unit
    def test_full_url_account_passed_through(self):
        """Accounts containing snowflakecomputing.com are used verbatim."""
        captured: dict[str, Any] = {}

        def fake_post(url, **kwargs):
            captured["url"] = url
            return MagicMock(status_code=200, text="data: [DONE]\n\n")

        with (
            patch.object(
                transport_module,
                "_read_rest_credentials",
                return_value=("myorg.snowflakecomputing.com", "tok"),
            ),
            patch.object(transport_module.requests, "post", side_effect=fake_post),
        ):
            complete("p", transport="rest", connection_name="c")
        assert captured["url"] == (
            "https://myorg.snowflakecomputing.com/api/v2/cortex/inference:complete"
        )

    @pytest.mark.unit
    def test_retries_on_429_and_eventually_raises(self):
        """A persistent 429 retries up to max_retries times, then raises."""
        fake_resp = MagicMock(status_code=429, text="rate limited")
        with (
            patch.object(
                transport_module,
                "_read_rest_credentials",
                return_value=("acct", "tok"),
            ),
            patch.object(transport_module.requests, "post", return_value=fake_resp) as mp,
            patch.object(transport_module.time, "sleep"),
            pytest.raises(RuntimeError, match="429"),
        ):
            complete("p", transport="rest", connection_name="c", max_retries=3)
        assert mp.call_count == 3

    @pytest.mark.unit
    def test_unknown_transport_raises_value_error(self):
        """Anything other than aisql/rest is rejected up front."""
        with pytest.raises(ValueError, match="Unknown transport"):
            complete("p", transport="grpc")  # type: ignore[arg-type]


class TestCompleteBatchAISQL:
    """complete_batch() with the AISQL transport."""

    @pytest.mark.unit
    def test_empty_input_returns_empty_dict(self):
        """Empty prompt list short-circuits without contacting Snowflake."""
        assert complete_batch([], connection_name="c") == {}

    @pytest.mark.unit
    def test_single_chunk_returns_keyed_responses(self):
        """A single SQL execution produces one row per file_key."""
        rows = [("file1.md", "kws1"), ("file2.md", "kws2")]
        conn, cursor = _make_fake_connection(rows=rows, sfqid="01b")

        with patch.object(transport_module, "_get_connection", return_value=conn):
            out = complete_batch(
                [("file1.md", "p1"), ("file2.md", "p2")],
                connection_name="c",
            )

        assert set(out) == {"file1.md", "file2.md"}
        assert out["file1.md"].text == "kws1"
        assert out["file2.md"].request_id == "01b"
        # One SQL execution covers the whole chunk.
        assert cursor.execute.call_count == 1
        sql, _ = cursor.execute.call_args.args
        assert "FROM (VALUES" in sql

    @pytest.mark.unit
    def test_chunks_split_when_input_exceeds_chunk_size(self):
        """Five prompts at chunk_size=2 emit three SQL executions."""
        prompts = [(f"f{i}", f"p{i}") for i in range(5)]
        conn = MagicMock()
        cursor = MagicMock()
        cursor.__enter__ = lambda self: self
        cursor.__exit__ = lambda self, *exc: False
        cursor.fetchall.side_effect = [
            [("f0", "k0"), ("f1", "k1")],
            [("f2", "k2"), ("f3", "k3")],
            [("f4", "k4")],
        ]
        cursor.sfqid = "qid"
        conn.cursor.return_value = cursor

        with patch.object(transport_module, "_get_connection", return_value=conn):
            out = complete_batch(prompts, connection_name="c", chunk_size=2)

        assert len(out) == 5
        assert cursor.execute.call_count == 3

    @pytest.mark.unit
    def test_chunk_size_zero_raises(self):
        """Non-positive chunk_size is rejected before contacting Snowflake."""
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            complete_batch([("f", "p")], connection_name="c", chunk_size=0)

    @pytest.mark.unit
    def test_rest_transport_falls_back_to_sequential(self):
        """transport='rest' issues one HTTP call per prompt."""
        from ai_rules.cortex import client as client_module

        with patch.object(
            client_module,
            "_complete_via_rest",
            side_effect=[CortexResponse(text="r1"), CortexResponse(text="r2")],
        ) as mock_rest:
            out = complete_batch(
                [("f1", "p1"), ("f2", "p2")],
                transport="rest",
                connection_name="c",
            )
        assert out["f1"].text == "r1"
        assert out["f2"].text == "r2"
        assert mock_rest.call_count == 2


class TestReadRestCredentials:
    """Resolution of (account, token) for the REST transport."""

    @pytest.mark.unit
    def test_resolves_default_when_no_name_or_env_var(self, tmp_path, monkeypatch):
        """Without an explicit name or env var the literal 'default' is used."""
        snowflake_dir = tmp_path / ".snowflake"
        snowflake_dir.mkdir()
        (snowflake_dir / "connections.toml").write_text(
            '[default]\naccount = "acct"\ntoken = "tok"\n'
        )
        monkeypatch.setattr(transport_module.Path, "home", lambda: tmp_path)
        monkeypatch.delenv("SNOWFLAKE_DEFAULT_CONNECTION_NAME", raising=False)

        account, token = transport_module._read_rest_credentials(None)
        assert account == "acct"
        assert token == "tok"

    @pytest.mark.unit
    def test_env_var_overrides_default_when_no_explicit_name(self, tmp_path, monkeypatch):
        """SNOWFLAKE_DEFAULT_CONNECTION_NAME selects when no explicit name is passed."""
        snowflake_dir = tmp_path / ".snowflake"
        snowflake_dir.mkdir()
        (snowflake_dir / "connections.toml").write_text(
            '[default]\naccount = "x"\ntoken = "y"\n'
            '[other]\naccount = "envacct"\ntoken = "envtok"\n'
        )
        monkeypatch.setattr(transport_module.Path, "home", lambda: tmp_path)
        monkeypatch.setenv("SNOWFLAKE_DEFAULT_CONNECTION_NAME", "other")

        account, token = transport_module._read_rest_credentials(None)
        assert account == "envacct"
        assert token == "envtok"

    @pytest.mark.unit
    def test_explicit_name_wins_over_env_var(self, tmp_path, monkeypatch):
        """An explicit connection_name overrides the env var."""
        snowflake_dir = tmp_path / ".snowflake"
        snowflake_dir.mkdir()
        (snowflake_dir / "connections.toml").write_text(
            '[other]\naccount = "envacct"\ntoken = "envtok"\n'
            '[explicit]\naccount = "exacct"\ntoken = "extok"\n'
        )
        monkeypatch.setattr(transport_module.Path, "home", lambda: tmp_path)
        monkeypatch.setenv("SNOWFLAKE_DEFAULT_CONNECTION_NAME", "other")

        account, token = transport_module._read_rest_credentials("explicit")
        assert account == "exacct"
        assert token == "extok"

    @pytest.mark.unit
    def test_missing_files_raise_filenotfound(self, tmp_path, monkeypatch):
        """Neither connections.toml nor config.toml present raises FileNotFoundError."""
        snowflake_dir = tmp_path / ".snowflake"
        snowflake_dir.mkdir()
        monkeypatch.setattr(transport_module.Path, "home", lambda: tmp_path)
        with pytest.raises(FileNotFoundError):
            transport_module._read_rest_credentials("default")

    @pytest.mark.unit
    def test_unknown_connection_raises_valueerror(self, tmp_path, monkeypatch):
        """A name absent from the TOML file raises ValueError."""
        snowflake_dir = tmp_path / ".snowflake"
        snowflake_dir.mkdir()
        (snowflake_dir / "connections.toml").write_text('[other]\naccount = "x"\ntoken = "y"\n')
        monkeypatch.setattr(transport_module.Path, "home", lambda: tmp_path)
        with pytest.raises(ValueError, match="not found"):
            transport_module._read_rest_credentials("default")


class TestParseCortexSseResponse:
    """SSE response body parsing for the REST transport."""

    @pytest.mark.unit
    def test_concatenates_content_deltas(self):
        """Content deltas across multiple data frames are concatenated."""
        raw = (
            'data: {"choices":[{"delta":{"content":"[\\"hello"}}]}\n\n'
            'data: {"choices":[{"delta":{"content":"\\", \\"world"}}]}\n\n'
            'data: {"choices":[{"delta":{"content":"\\"]"}}]}\n\n'
            "data: [DONE]\n\n"
        )
        assert transport_module._parse_cortex_sse_response(raw) == '["hello", "world"]'

    @pytest.mark.unit
    def test_handles_empty_input(self):
        """An empty SSE body returns an empty string."""
        assert transport_module._parse_cortex_sse_response("") == ""

    @pytest.mark.unit
    def test_skips_malformed_chunks(self):
        """Malformed JSON inside data frames is silently skipped."""
        raw = 'data: not-json\n\ndata: {"choices":[{"delta":{"content":"ok"}}]}\n\ndata: [DONE]\n\n'
        assert transport_module._parse_cortex_sse_response(raw) == "ok"
