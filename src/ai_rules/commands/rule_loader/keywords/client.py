"""Cortex API client for keyword generation."""

from __future__ import annotations

import time
import tomllib
from pathlib import Path
from typing import Any

from ai_rules._shared.console import err_console
from ai_rules.commands.rule_loader.keywords.prompts import (
    ParseResult,
    _parse_keyword_response,
)
from ai_rules.commands.rule_loader.keywords.stoplist import STOP_TERMS


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


def _parse_cortex_sse_response(raw: str) -> str:
    """Parse a Cortex streaming SSE response into the full text."""
    import json as _json

    parts: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        payload = line[len("data:") :].strip()
        if payload == "[DONE]":
            break
        try:
            chunk = _json.loads(payload)
            choices = chunk.get("choices", [])
            if choices:
                delta = choices[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    parts.append(content)
        except (_json.JSONDecodeError, IndexError, KeyError):
            continue
    return "".join(parts)


class CortexClient:
    """Encapsulates Cortex REST API auth, URL construction, and retry logic.

    Constructor:
        connection_name: Snowflake connection name from ~/.snowflake/connections.toml.
        model: LLM model name (default: ``claude-sonnet-4-5``).
    """

    def __init__(
        self,
        connection_name: str = "default",
        model: str = "claude-sonnet-4-5",
    ) -> None:
        """Initialize the client.

        Args:
            connection_name: Snowflake connection name from ~/.snowflake/connections.toml.
            model: LLM model name (default: ``claude-sonnet-4-5``).
        """
        self.connection_name = connection_name
        self.model = model

    def generate_keywords(
        self,
        content: str,
        count: int,
        *,
        debug: bool = False,
    ) -> ParseResult:
        """Call Cortex REST API and return a ParseResult(keywords, rationale_map).

        Args:
            content: The rule file content.
            count: Maximum number of keywords requested.
            debug: Enable debug output.

        Returns:
            ParseResult with keywords and per-keyword rationale.

        Raises:
            RuntimeError: If API call fails after retries.
        """
        import requests  # local import — optional dep

        config = load_snowflake_config(self.connection_name)
        account = config.get("account", config.get("accountname", ""))
        token = config.get("token") or config.get("password", "")

        if not account or not token:
            raise RuntimeError(
                f"Snowflake connection '{self.connection_name}' is missing 'account' or "
                f"'token'/'password'. Check ~/.snowflake/connections.toml."
            )

        stop_terms_list = ", ".join(sorted(STOP_TERMS))
        max_count = min(max(count, 5), 7)

        prompt = f"""You are a senior technical writer summarizing AI coding rule files into discovery keywords.

Your task: Read the rule file below, understand its core purpose and distinguishing concepts, then distill that understanding into EXACTLY 5 to {max_count} keywords or short phrases. Never return fewer than 5 or more than {max_count}.

These keywords populate the **Keywords:** metadata field used by the deterministic rule matcher to discover which rules to load for a given request.

Step 1 — Understand the rule:
- What specific technology, framework, or tool does this rule govern?
- What actions, patterns, or workflows does it prescribe?
- What distinguishes this rule from other rules in the same domain?
- Is this a sub-domain rule (e.g. a rule about pytest fixtures WITHIN the Python ecosystem, or a rule about masking policies WITHIN Snowflake)? If so, the bare parent technology name is FORBIDDEN as a keyword.

Step 2 — Generate keywords that:
- Capture the core concepts, technologies, and actionable patterns in this rule
- Prefer COMPOUND phrases (2+ tokens) over single tokens. At least 60% of keywords must be compound phrases.
- Include proper nouns with correct casing (e.g., "Snowflake", "FastAPI", "RBAC") ONLY when the rule is the top-level rule for that technology; sub-domain rules must use compound qualifications instead.
- Include compound phrases where meaningful (e.g., "cortex agent", "masking policy", "session state")
- Use lowercase for multi-word descriptive terms (e.g., "error handling", "dynamic table")
- Would help an AI agent searching for rules relevant to a specific task
- Are specific enough to distinguish THIS rule from other rules

Do NOT include any of these generic terms (they appear in every rule and have no discovery value):
{stop_terms_list}

CRITICAL — Never use bare single-word domain terms. Always qualify with the specific aspect this rule covers:
- BAD:  "SQL", "testing", "performance", "validation", "security", "python", "snowflake", "docker", "react", "yaml", "json"
- GOOD: "SQL file formatting", "pytest fixtures", "query partition pruning", "schema compliance validation", "RBAC role grants"
Each keyword must be specific enough that an agent could identify THIS rule from the keyword alone, without needing the rule filename.

CRITICAL — Sub-domain rule prohibition: If this rule is a specialization within a broader technology domain (e.g. `206-python-pytest.md` within Python; `106a-snowflake-semantic-views-advanced.md` within Snowflake), you MUST NOT emit the bare parent technology token (`python`, `snowflake`, etc.) as a keyword. Emit qualified compounds instead.

CRITICAL — Rationale required: For EACH keyword, emit a one-sentence rationale explaining WHY this token uniquely identifies the rule (what distinguishes it from sibling rules in the same domain). Rationale must be non-empty.

Return ONLY a JSON array of 5 to {max_count} objects. Each object has this exact shape:
  {{"keyword": "<kw string>", "rationale": "<one-sentence justification>"}}
No explanation, no markdown, no other text outside the JSON array.

Rule file content:
---
{content[:32000]}
---"""

        if ".snowflakecomputing.com" in account:
            url = f"https://{account}/api/v2/cortex/inference:complete"
        else:
            url = f"https://{account}.snowflakecomputing.com/api/v2/cortex/inference:complete"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.1,
        }

        max_retries = 3
        base_delay = 1.0
        last_error = None

        for attempt in range(max_retries):
            try:
                if debug:
                    err_console.print(
                        f"[dim][DEBUG] Cortex API attempt {attempt + 1}/{max_retries}[/dim]"
                    )

                resp = requests.post(url, headers=headers, json=payload, timeout=30)

                if resp.status_code == 200:
                    text = _parse_cortex_sse_response(resp.text)
                    if debug:
                        err_console.print(f"[dim][DEBUG] LLM response text: {text[:200]}[/dim]")
                    result = _parse_keyword_response(text, count)
                    return result

                elif resp.status_code in (429, 503, 504):
                    delay = base_delay * (2**attempt)
                    if debug:
                        err_console.print(
                            f"[dim][DEBUG] Retryable error {resp.status_code}, "
                            f"waiting {delay:.1f}s[/dim]"
                        )
                    time.sleep(delay)
                    last_error = RuntimeError(
                        f"Cortex API returned {resp.status_code}: {resp.text[:200]}"
                    )
                else:
                    raise RuntimeError(f"Cortex API returned {resp.status_code}: {resp.text[:200]}")

            except requests.exceptions.RequestException as e:
                last_error = RuntimeError(f"Cortex API request failed: {e}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2**attempt)
                    time.sleep(delay)

        raise last_error or RuntimeError("Cortex API call failed after retries")


def _call_cortex_complete(
    content: str,
    connection_name: str = "default",
    count: int = 15,
    debug: bool = False,
) -> list[str]:
    """Backward-compat wrapper around CortexClient.generate_keywords.

    Returns keyword list only (rationale available via get_last_rationale_map()).
    """
    client = CortexClient(connection_name=connection_name)
    result = client.generate_keywords(content, count=count, debug=debug)
    return result.keywords
