"""Pydantic models for test cases and results."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CortexResponse:
    """Response from Cortex REST API."""

    text: str
    request_id: str | None = None


@dataclass
class CriterionResult:
    """Result of evaluating a single criterion."""

    criterion: str
    met: bool


@dataclass
class TestResult:
    """Result of evaluating a single test case."""

    test_id: str
    name: str
    category: str
    priority: str
    result: str  # PASS, FAIL, ERROR
    score: int = 0
    max_score: int = 0
    score_percent: float = 0.0
    criteria_results: list[CriterionResult] = field(default_factory=list)
    model_response: str = ""
    error: str | None = None
    duration_seconds: float = 0.0
    turns_count: int | None = None
    request_id: str | None = None


@dataclass
class EvaluationSummary:
    """Summary statistics for an evaluation run."""

    total_tests: int
    passed: int
    failed: int
    pass_rate: float


@dataclass
class EvaluationMetadata:
    """Metadata about an evaluation run."""

    timestamp: str
    agents_file: str
    agents_md_hash: str
    evaluator: str
    model: str
    total_duration_seconds: float = 0.0
    parallel_workers: int = 0


@dataclass
class EvaluationReport:
    """Complete evaluation report."""

    metadata: EvaluationMetadata
    summary: EvaluationSummary
    results: list[TestResult]


@dataclass
class ComparisonResult:
    """Result of comparing two evaluation runs."""

    baseline_pass_rate: float
    current_pass_rate: float
    delta: float
    regressions: list[dict[str, str]]
    improvements: list[dict[str, str]]
    maintained: list[dict[str, str]]
    persistent_failures: list[dict[str, str]]


@dataclass
class State:
    """Global state for CLI options."""

    connection: str = "default"
    verbose: bool = False
    agents_file: Path = field(default_factory=lambda: Path("AGENTS.md"))
    timing_stats: dict[str, float] = field(default_factory=dict)


DEFAULT_MODEL = "claude-sonnet-4-5"
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_MAX_RETRIES = 3
DEFAULT_RESPONSE_TRUNCATE_LENGTH = 500
DEFAULT_PARALLEL_WORKERS = 5

SUPPORTED_MODELS = [
    # Anthropic
    "claude-sonnet-4-5",
    "claude-opus-4-5",
    "claude-haiku-4-5",
    "claude-4-sonnet",
    "claude-4-opus",
    "claude-3-7-sonnet",
    "claude-3-5-sonnet",
    # OpenAI
    "openai-gpt-4.1",
    "openai-gpt-5",
    "openai-gpt-5-mini",
    "openai-gpt-5-nano",
    "openai-gpt-5-chat",
    "openai-gpt-oss-120b",
    # Meta
    "llama4-maverick",
    "llama3.1-405b",
    "llama3.1-70b",
    "llama3.1-8b",
    # Mistral
    "mistral-large2",
    "mistral-large",
    "mistral-7b",
    # Snowflake
    "snowflake-llama-3.3-70b",
    # DeepSeek
    "deepseek-r1",
]
