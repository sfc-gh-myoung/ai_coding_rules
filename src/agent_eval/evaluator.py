"""Core evaluator logic for AGENTS.md compliance testing."""

import time
from pathlib import Path
from typing import Any

from agent_eval.cortex import CortexClient
from agent_eval.models import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_RESPONSE_TRUNCATE_LENGTH,
    DEFAULT_TIMEOUT_SECONDS,
    State,
)
from agent_eval.parsers import score_response


class CortexEvaluator:
    """Automated test evaluation using Snowflake Cortex REST API."""

    def __init__(
        self,
        model: str,
        connection_name: str = "default",
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        truncate_length: int = DEFAULT_RESPONSE_TRUNCATE_LENGTH,
        agents_file: Path | None = None,
        state: State | None = None,
    ) -> None:
        """Initialize evaluator.

        Args:
            model: Cortex model name.
            connection_name: Snowflake connection name.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for transient failures.
            truncate_length: Max length for stored response text.
            agents_file: Path to AGENTS.md file.
            state: Global state object.
        """
        self.model = model
        self.connection_name = connection_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.truncate_length = truncate_length
        self.state = state or State()
        self.agents_file = agents_file or self.state.agents_file
        self.agents_md_content = self.agents_file.read_text()
        self.client: CortexClient | None = None
        self.quiet: bool = False

    def __enter__(self) -> "CortexEvaluator":
        """Context manager entry - connect to Cortex."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - disconnect from Cortex."""
        self.disconnect()

    def connect(self) -> None:
        """Initialize Cortex client."""
        self.client = CortexClient(
            model=self.model,
            connection_name=self.connection_name,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )
        self.client.quiet = self.quiet
        self.client.connect()

    def disconnect(self) -> None:
        """Disconnect from Cortex."""
        if self.client:
            self.client.disconnect()
            self.client = None

    def build_system_prompt(self) -> str:
        """Build system prompt that includes AGENTS.md protocol."""
        return f"""You are an AI agent that MUST follow the bootstrap protocol defined below.

CRITICAL: You must follow this protocol exactly. Your response will be evaluated for compliance.

=== AGENTS.md BOOTSTRAP PROTOCOL ===

{self.agents_md_content}

=== END PROTOCOL ===

SIMULATION CONTEXT:
- You are simulating an AI agent that has access to a rules/ directory
- Assume you CAN read files from rules/ directory
- When you would call read_file("rules/X.md"), assume it succeeds
- Include the PRE-FLIGHT checklist in your response
- Follow the Required Response Format exactly

IMPORTANT:
- Always include PRE-FLIGHT: section with [x] checkboxes
- Always include MODE: PLAN or MODE: ACT
- Always include Task Switch: FIRST (this is a new conversation)
- Always include ## Rules Loaded section
- Simulate having loaded rules/000-global-core.md

Now respond to the user's request following this protocol exactly."""

    def call_cortex_complete(
        self,
        user_message: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> tuple[str, str | None]:
        """Call Snowflake Cortex REST API.

        Args:
            user_message: The test input to send to the model.
            conversation_history: Optional list of prior messages for multi-turn tests.

        Returns:
            Tuple of (response_text, request_id).
        """
        if not self.client:
            self.connect()

        system_prompt = self.build_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        result = self.client.complete(messages)  # type: ignore[union-attr]
        return result.text, result.request_id

    def evaluate_test(self, test_case: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a single test case using Cortex REST API.

        Supports both single-turn and multi-turn tests.
        Multi-turn tests use 'turns' array; only the final turn is evaluated.

        Args:
            test_case: Test case definition from YAML.

        Returns:
            Scored result dict.
        """
        test_start = time.perf_counter()
        turns = test_case.get("turns")

        if turns:
            conversation_history: list[dict[str, str]] = []
            request_id: str | None = None

            for i, turn in enumerate(turns):
                turn_input = turn["input"]
                is_final = i == len(turns) - 1

                response, req_id = self.call_cortex_complete(
                    turn_input, conversation_history if conversation_history else None
                )
                if req_id:
                    request_id = req_id

                conversation_history.append({"role": "user", "content": turn_input})
                conversation_history.append({"role": "assistant", "content": response})

                if is_final:
                    result = score_response(test_case, response)
                    if len(response) > self.truncate_length:
                        result["model_response"] = response[: self.truncate_length] + "..."
                    else:
                        result["model_response"] = response
                    result["turns_count"] = len(turns)
                    result["request_id"] = request_id
                    duration = time.perf_counter() - test_start
                    result["duration_seconds"] = round(duration, 2)
                    if self.state:
                        self.state.timing_stats[test_case["test_id"]] = duration
                    return result

        test_input = test_case["test_input"]
        response, request_id = self.call_cortex_complete(test_input)

        result = score_response(test_case, response)

        if len(response) > self.truncate_length:
            result["model_response"] = response[: self.truncate_length] + "..."
        else:
            result["model_response"] = response

        result["request_id"] = request_id
        duration = time.perf_counter() - test_start
        result["duration_seconds"] = round(duration, 2)
        if self.state:
            self.state.timing_stats[test_case["test_id"]] = duration

        return result
