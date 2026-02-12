"""Data models for prompt evaluation."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Severity(Enum):
    """Issue severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Issue:
    """A specific issue found in a prompt."""

    quote: str
    problem: str
    severity: Severity
    dimension: str


@dataclass
class DimensionScore:
    """Score for a single evaluation dimension."""

    dimension: str
    raw_score: int  # 0-10
    weight: int  # multiplier
    max_points: int
    points: float  # raw_score * (weight / 2)
    issues: list[Issue] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Complete evaluation result for a prompt."""

    original_prompt: str
    total_score: float  # 0-100
    max_score: float  # typically 100, 110 with bonus
    grade: str  # A, B, C, D, F
    dimension_scores: list[DimensionScore] = field(default_factory=list)
    all_issues: list[Issue] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    model_used: str = ""


@dataclass
class ImprovedPrompt:
    """An improved version of the original prompt."""

    improved_text: str
    changes_made: list[str] = field(default_factory=list)
    priority_alignment: dict[str, list[str]] = field(default_factory=dict)
    explanation: str = ""


@dataclass
class EvaluationReport:
    """Full evaluation report with original, scores, and improved prompt."""

    evaluation: EvaluationResult
    improved: ImprovedPrompt | None = None
    id: str = ""  # UUID for saved reports


def calculate_grade(score: float, max_score: float = 100) -> str:
    """Calculate letter grade from score."""
    percentage = (score / max_score) * 100
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    elif percentage >= 70:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"


# Supported Cortex models
SUPPORTED_MODELS = [
    # Anthropic
    "claude-sonnet-4-5",
    "claude-opus-4-5",
    "claude-haiku-4-5",
    # OpenAI
    "openai-gpt-5",
    "openai-gpt-5-mini",
    "openai-gpt-5-nano",
    # Meta
    "llama4-maverick",
    "llama3.1-405b",
    "llama3.1-70b",
    "llama3.1-8b",
    # Mistral
    "mistral-large2",
    "mistral-large",
]

DEFAULT_MODEL = "claude-sonnet-4-5"
DEFAULT_TIMEOUT = 120
DEFAULT_MAX_RETRIES = 3
