"""Prompt evaluation tool for improving LLM/agent prompts.

Evaluates prompts across 6 dimensions and generates improved versions
optimized for cross-agent compatibility and execution reliability.
"""

__version__ = "1.0.0"

from .cli import app as cli_app
from .cortex import (
    CortexClient,
    CortexConfig,
    CortexError,
)
from .dimensions import (
    DIMENSIONS,
    DimensionConfig,
    DimensionType,
    calculate_points,
    detect_blocking_issues,
    get_all_dimensions,
    get_dimension,
    get_max_score,
    score_from_issues,
)
from .evaluator import (
    PromptEvaluator,
)
from .formatters import (
    format_html,
    format_json,
    format_markdown,
)
from .models import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT,
    SUPPORTED_MODELS,
    DimensionScore,
    EvaluationReport,
    EvaluationResult,
    ImprovedPrompt,
    Issue,
    Severity,
    calculate_grade,
)
from .rewriter import (
    PromptRewriter,
)

__all__ = [
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_MODEL",
    "DEFAULT_TIMEOUT",
    "DIMENSIONS",
    "SUPPORTED_MODELS",
    "CortexClient",
    # Cortex
    "CortexConfig",
    "CortexError",
    "DimensionConfig",
    "DimensionScore",
    # Dimensions
    "DimensionType",
    "EvaluationReport",
    "EvaluationResult",
    "ImprovedPrompt",
    "Issue",
    # Evaluator
    "PromptEvaluator",
    # Rewriter
    "PromptRewriter",
    # Models
    "Severity",
    # Version
    "__version__",
    "calculate_grade",
    "calculate_points",
    # CLI
    "cli_app",
    "detect_blocking_issues",
    "format_html",
    "format_json",
    # Formatters
    "format_markdown",
    "get_all_dimensions",
    "get_dimension",
    "get_max_score",
    "score_from_issues",
]
