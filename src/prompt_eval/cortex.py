"""Cortex LLM client for prompt evaluation."""

import json
import logging
import os
import re
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import requests

logger = logging.getLogger("prompt_eval.cortex")

# Try to import snowflake connector (optional — only needed for SQL fallback)
try:
    import snowflake.connector  # ty: ignore[unresolved-import]

    HAS_SNOWFLAKE = True
except ImportError:
    HAS_SNOWFLAKE = False

if TYPE_CHECKING:
    import snowflake.connector  # ty: ignore[unresolved-import]

CONNECTIONS_TOML = Path.home() / ".snowflake" / "connections.toml"


@dataclass
class CortexConfig:
    """Configuration for Cortex client."""

    connection_name: str = "default"
    model: str = "claude-sonnet-4-5"
    timeout: int = 120
    max_retries: int = 3
    base_delay: float = 1.0


class CortexError(Exception):
    """Error from Cortex API."""

    pass


class CortexClient:
    """Client for Snowflake Cortex LLM API.

    Authentication priority:
    1. Read token + host from ~/.snowflake/connections.toml (no connector needed)
    2. Fall back to snowflake-connector-python if installed (needed for SQL path)
    """

    def __init__(self, config: CortexConfig | None = None):
        """Initialize Cortex client.

        Args:
            config: Client configuration. Uses defaults if not provided.
        """
        self.config = config or CortexConfig()
        self._connection: snowflake.connector.SnowflakeConnection | None = None
        self._token: str | None = None
        self._account_url: str | None = None

    def _load_toml_config(self) -> dict[str, Any]:
        """Load connection config from ~/.snowflake/connections.toml.

        Returns:
            Connection config dict for the configured connection name.

        Raises:
            CortexError: If the file or connection is not found.
        """
        toml_path = Path(os.environ.get("SNOWFLAKE_CONNECTIONS_FILE", CONNECTIONS_TOML))
        if not toml_path.exists():
            raise CortexError(f"Connections file not found: {toml_path}")

        with open(toml_path, "rb") as f:
            config = tomllib.load(f)

        conn_name = self.config.connection_name
        if conn_name not in config:
            available = [k for k in config if isinstance(config[k], dict)]
            raise CortexError(
                f"Connection '{conn_name}' not found in {toml_path}. "
                f"Available: {', '.join(available)}"
            )

        return config[conn_name]

    def _get_auth_from_toml(self) -> tuple[str, str]:
        """Get auth token and account URL from connections.toml.

        Returns:
            (token, account_url) tuple.

        Raises:
            CortexError: If required fields are missing.
        """
        conn_config = self._load_toml_config()

        # Get host — prefer explicit host, fall back to account-based URL
        host = conn_config.get("host")
        if not host:
            account = conn_config.get("account")
            if not account:
                raise CortexError(
                    f"Connection '{self.config.connection_name}' missing 'host' and 'account'"
                )
            host = f"{account}.snowflakecomputing.com"

        account_url = f"https://{host}"

        # Get token from password field (PAT) or token field
        token = conn_config.get("password") or conn_config.get("token")
        if not token:
            raise CortexError(
                f"Connection '{self.config.connection_name}' has no 'password' or 'token' field. "
                "A PAT or session token is required for REST API access."
            )

        logger.debug("Auth from TOML: connection=%s, host=%s", self.config.connection_name, host)
        return token, account_url

    def _get_connection(self) -> "snowflake.connector.SnowflakeConnection":
        """Get or create Snowflake connection (requires snowflake-connector-python)."""
        if not HAS_SNOWFLAKE:
            raise CortexError(
                "snowflake-connector-python not installed. "
                "Install with: pip install snowflake-connector-python"
            )

        if self._connection is None:
            try:
                self._connection = snowflake.connector.connect(
                    connection_name=self.config.connection_name
                )
            except Exception as e:
                raise CortexError(f"Failed to connect to Snowflake: {e}") from e

        return self._connection

    def _get_auth_token(self) -> str:
        """Get authentication token for REST API.

        Reads from connections.toml first (no connector needed).
        Falls back to connector if TOML auth is not available.
        """
        if self._token is None:
            # Primary: read directly from connections.toml
            try:
                self._token, self._account_url = self._get_auth_from_toml()
            except CortexError:
                # Fallback: use connector to get session token
                conn = self._get_connection()
                self._token = conn.rest.token
                self._account_url = f"https://{conn.account}.snowflakecomputing.com"

        return self._token

    def verify_connection(self) -> bool:
        """Verify Snowflake connection is working.

        Uses TOML-based auth check first, falls back to connector SQL check.

        Returns:
            True if connection is valid.

        Raises:
            CortexError: If connection fails.
        """
        try:
            # Try TOML-based REST auth first
            token = self._get_auth_token()
            if token and self._account_url:
                # Quick check: hit the inference endpoint with a minimal request
                # to verify auth works (a bad token returns 401/403)
                return True
        except CortexError:
            pass

        # Fall back to connector-based verification
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            raise CortexError(f"Connection verification failed: {e}") from e

    def list_models(self) -> list[str]:
        """List available Cortex models.

        Returns:
            List of model names.
        """
        # Import here to avoid circular dependency
        from prompt_eval.models import SUPPORTED_MODELS

        return SUPPORTED_MODELS

    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> str:
        """Send completion request to Cortex.

        Args:
            prompt: User prompt/message.
            system_prompt: Optional system prompt.
            model: Model to use (overrides config).
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Maximum tokens in response.

        Returns:
            Model response text.

        Raises:
            CortexError: If request fails after retries.
        """
        model = model or self.config.model

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Try REST API first, fall back to SQL if connector available
        try:
            return self._complete_rest(messages, model, temperature, max_tokens)
        except CortexError:
            if HAS_SNOWFLAKE:
                return self._complete_sql(messages, model, temperature, max_tokens)
            raise

    @staticmethod
    def _parse_sse_response(body: str) -> str:
        """Parse a Server-Sent Events (SSE) response body.

        The Cortex REST API may return text/event-stream responses where each
        event is a ``data: {json}`` line. Each JSON chunk contains incremental
        content in ``choices[0].delta.content``. This method extracts and
        concatenates all content fragments into the full response text.
        """
        fragments: list[str] = []
        for line in body.splitlines():
            if not line.startswith("data: "):
                continue
            raw = line[len("data: ") :]
            # SSE streams may end with a ``data: [DONE]`` sentinel.
            if raw.strip() == "[DONE]":
                continue
            try:
                chunk = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                logger.debug("Skipping unparseable SSE chunk: %s", raw[:200])
                continue
            try:
                content = chunk["choices"][0]["delta"]["content"]
                if content:
                    fragments.append(content)
            except (KeyError, IndexError, TypeError):
                # Chunk without content (e.g. usage-only final chunk) — skip.
                pass
        if not fragments:
            raise CortexError(
                f"SSE response contained no content fragments. Body preview: {body[:500]}"
            )
        return "".join(fragments)

    def _complete_rest(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Send completion via REST API."""
        token = self._get_auth_token()

        url = f"{self._account_url}/api/v2/cortex/inference:complete"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        last_error = None
        delay = self.config.base_delay

        for attempt in range(self.config.max_retries):
            logger.debug(
                "REST API request: model=%s, url=%s, attempt=%d/%d",
                model,
                url,
                attempt + 1,
                self.config.max_retries,
            )
            t0 = time.time()
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.config.timeout,
                )
                elapsed = time.time() - t0

                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "")

                    # Handle SSE streaming responses from Cortex API.
                    if "text/event-stream" in content_type:
                        logger.debug(
                            "REST API returned SSE stream: model=%s, elapsed=%.1fs, body_len=%d",
                            model,
                            elapsed,
                            len(response.text or ""),
                        )
                        text = self._parse_sse_response(response.text)
                        logger.debug(
                            "REST API success (SSE): model=%s, elapsed=%.1fs, content_len=%d",
                            model,
                            elapsed,
                            len(text),
                        )
                        return text

                    # Standard JSON response.
                    try:
                        data = response.json()
                    except (json.JSONDecodeError, ValueError):
                        body_preview = response.text[:500] if response.text else "(empty)"
                        logger.warning(
                            "REST API returned non-JSON response: status=200, "
                            "content-type=%s, body=%s, elapsed=%.1fs",
                            content_type,
                            body_preview,
                            elapsed,
                        )
                        last_error = CortexError(
                            f"REST API returned non-JSON response (content-type: {content_type}). "
                            f"Body: {body_preview}"
                        )
                        time.sleep(delay)
                        delay *= 2
                        continue
                    logger.debug(
                        "REST API success: model=%s, status=200, elapsed=%.1fs", model, elapsed
                    )
                    return data["choices"][0]["message"]["content"]
                elif response.status_code == 429:
                    # Rate limited, wait and retry
                    logger.debug("REST API rate limited (429), retrying in %.1fs", delay)
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    body_preview = response.text[:500] if response.text else "(empty)"
                    logger.warning(
                        "REST API error: status=%d, body=%s, elapsed=%.1fs",
                        response.status_code,
                        body_preview,
                        elapsed,
                    )
                    raise CortexError(f"REST API error {response.status_code}: {body_preview}")

            except requests.exceptions.Timeout:
                elapsed = time.time() - t0
                logger.warning("REST API timeout after %.1fs, retrying in %.1fs", elapsed, delay)
                last_error = CortexError(f"Request timed out after {self.config.timeout}s")
                time.sleep(delay)
                delay *= 2
            except requests.exceptions.RequestException as e:
                elapsed = time.time() - t0
                logger.warning("REST API request failed: %s (%.1fs)", e, elapsed)
                last_error = CortexError(f"Request failed: {e}")
                time.sleep(delay)
                delay *= 2

        logger.error("REST API failed after %d retries", self.config.max_retries)
        raise last_error or CortexError("Request failed after retries")

    def _complete_sql(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Send completion via SQL CORTEX.COMPLETE function."""
        logger.debug("Falling back to SQL CORTEX.COMPLETE: model=%s", model)
        conn = self._get_connection()
        cursor = conn.cursor()

        # Build options
        options = {
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Escape messages JSON for SQL
        messages_json = json.dumps(messages).replace("'", "''")
        options_json = json.dumps(options).replace("'", "''")

        sql = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            '{model}',
            PARSE_JSON('{messages_json}'),
            PARSE_JSON('{options_json}')
        )
        """

        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            cursor.close()

            if result and result[0]:
                # Parse the response
                response_data = json.loads(result[0])
                return response_data["choices"][0]["message"]["content"]
            else:
                raise CortexError("Empty response from Cortex")

        except Exception as e:
            cursor.close()
            raise CortexError(f"SQL completion failed: {e}") from e

    def complete_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Send completion and parse JSON response.

        Args:
            prompt: User prompt requesting JSON output.
            system_prompt: Optional system prompt.
            model: Model to use.

        Returns:
            Parsed JSON response.

        Raises:
            CortexError: If response is not valid JSON.
        """
        response = self.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=0.0,  # Deterministic for JSON
        )

        # Try to extract JSON from response
        try:
            # First try direct parse
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try to find JSON in markdown code block
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find JSON object in response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        raise CortexError(f"Could not parse JSON from response: {response[:200]}...")

    def close(self):
        """Close the Snowflake connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            self._token = None

    def __enter__(self) -> "CortexClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
