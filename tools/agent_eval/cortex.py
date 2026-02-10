"""Snowflake Cortex REST API client."""

import json
import time
from pathlib import Path
from typing import Any

try:
    import requests
    from requests.exceptions import ConnectionError, ReadTimeout, Timeout

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from tools.agent_eval.models import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT_SECONDS,
    SUPPORTED_MODELS,
    CortexResponse,
)


def load_snowflake_config(connection_name: str) -> dict[str, Any]:
    """Load connection config from ~/.snowflake/connections.toml or config.toml.

    Args:
        connection_name: Name of the connection in the config file.

    Returns:
        Dict with account, user, and authentication details.

    Raises:
        FileNotFoundError: If no config file exists.
        ValueError: If connection_name not found in config.
    """
    snowflake_dir = Path.home() / ".snowflake"
    connections_path = snowflake_dir / "connections.toml"
    config_path = snowflake_dir / "config.toml"

    config_file = None
    if connections_path.exists():
        config_file = connections_path
    elif config_path.exists():
        config_file = config_path
    else:
        raise FileNotFoundError(
            f"No Snowflake config found. Expected:\n  - {connections_path}\n  - {config_path}"
        )

    with open(config_file, "rb") as f:
        config = tomllib.load(f)

    if connection_name not in config:
        available = list(config.keys())
        raise ValueError(
            f"Connection '{connection_name}' not found in {config_file.name}. "
            f"Available: {available}"
        )

    return config[connection_name]


class CortexClient:
    """Snowflake Cortex REST API client."""

    def __init__(
        self,
        model: str,
        connection_name: str = "default",
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        """Initialize client.

        Args:
            model: Cortex model name.
            connection_name: Snowflake connection name.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for transient failures.

        Raises:
            RuntimeError: If requests library is not available.
        """
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("requests not installed. Install with: uv add requests")

        self.model = model
        self.connection_name = connection_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.config: dict[str, Any] | None = None
        self.token: str | None = None
        self.account_url: str | None = None
        self.session: requests.Session | None = None
        self.quiet: bool = False

    def __enter__(self) -> "CortexClient":
        """Context manager entry - connect to Cortex."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - disconnect from Cortex."""
        self.disconnect()

    def connect(self) -> None:
        """Load connection config and prepare for API calls.

        Raises:
            ValueError: If account or token not found in config.
        """
        self.config = load_snowflake_config(self.connection_name)

        account = self.config.get("account", self.config.get("accountname", ""))
        if not account:
            raise ValueError(f"No account found in connection '{self.connection_name}'")

        if ".snowflakecomputing.com" in account:
            self.account_url = f"https://{account}"
        else:
            self.account_url = f"https://{account}.snowflakecomputing.com"

        self.token = self.config.get("token") or self.config.get("password")
        if not self.token:
            raise ValueError(
                f"No token/password found in connection '{self.connection_name}'. "
                "Cortex REST API requires a PAT or password."
            )

        self.session = requests.Session()

    def disconnect(self) -> None:
        """Clear authentication token and close session."""
        if self.session:
            self.session.close()
            self.session = None
        self.token = None

    def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0,
        max_tokens: int = 4096,
    ) -> CortexResponse:
        """Call Snowflake Cortex REST API with retry logic.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            temperature: Sampling temperature (0 = deterministic).
            max_tokens: Maximum tokens in response.

        Returns:
            CortexResponse with text and request_id.

        Raises:
            RuntimeError: If API call fails after all retries.
        """
        if not self.token:
            self.connect()

        url = f"{self.account_url}/api/v2/cortex/inference:complete"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                if not self.session:
                    self.session = requests.Session()

                response = self.session.post(
                    url,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=self.timeout,
                )

                if response.status_code != 200:
                    error_msg = f"Cortex API error {response.status_code}: {response.text}"
                    if response.status_code >= 500:
                        last_error = RuntimeError(error_msg)
                        if attempt < self.max_retries:
                            wait_time = 2**attempt
                            time.sleep(wait_time)
                            continue
                    raise RuntimeError(error_msg)

                full_response = ""
                request_id: str | None = None
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode("utf-8")
                        if line_str.startswith("data:"):
                            try:
                                data = json.loads(line_str[5:].strip())
                                if request_id is None and "id" in data:
                                    request_id = data["id"]
                                if data.get("choices"):
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    full_response += content
                            except json.JSONDecodeError:
                                continue

                return CortexResponse(text=full_response, request_id=request_id)

            except (Timeout, ReadTimeout) as e:
                last_error = e
                if attempt < self.max_retries:
                    wait_time = 2**attempt
                    time.sleep(wait_time)
                    continue
                raise RuntimeError(f"Request timed out after {self.timeout}s") from e

            except ConnectionError as e:
                last_error = e
                if attempt < self.max_retries:
                    wait_time = 2**attempt
                    time.sleep(wait_time)
                    continue
                raise RuntimeError(f"Connection failed: {e}") from e

        raise RuntimeError(f"Failed after {self.max_retries} attempts: {last_error}")


def list_available_models(
    connection_name: str = "default",
) -> tuple[list[str], str | None]:
    """Return available Cortex REST API models.

    NOTE: There is no programmatic way to query available models for the
    Cortex REST API (/api/v2/cortex/inference:complete). The SHOW MODELS
    SQL command returns models for COMPLETE() SQL function, which has a
    different (larger) set than the REST API.

    This function returns SUPPORTED_MODELS, which is manually curated
    based on: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-rest-api

    Args:
        connection_name: Snowflake connection name (unused, kept for compatibility).

    Returns:
        Tuple of (model list, None).
    """
    return list(SUPPORTED_MODELS), None
