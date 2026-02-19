"""FastAPI server for prompt evaluation."""

import asyncio
import logging
import time
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from . import __version__
from .cortex import CortexError
from .dimensions import DIMENSIONS
from .evaluator import PromptEvaluator
from .formatters import format_html, format_markdown
from .models import (
    DEFAULT_MODEL,
    SUPPORTED_MODELS,
    EvaluationReport,
    EvaluationResult,
    ImprovedPrompt,
    Severity,
)
from .rewriter import PromptRewriter

logger = logging.getLogger("prompt_eval.api")

# =============================================================================
# Paths
# =============================================================================

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# =============================================================================
# Pydantic Models for API
# =============================================================================


class OutputFormat(StrEnum):
    """Output format options."""

    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"


class EvaluateRequest(BaseModel):
    """Request model for prompt evaluation."""

    prompt: str = Field(
        ...,
        description="The prompt text to evaluate",
        min_length=1,
        max_length=100000,
        examples=["Write a Python function that calculates the factorial of a number"],
    )
    model: str = Field(
        default=DEFAULT_MODEL,
        description="Cortex model to use for evaluation",
        examples=["claude-sonnet-4-5", "openai-gpt-5"],
    )
    connection: str = Field(
        default="default",
        description="Snowflake connection name",
    )
    rewrite: bool = Field(
        default=True,
        description="Whether to generate an improved version of the prompt",
    )
    format: OutputFormat = Field(
        default=OutputFormat.JSON,
        description="Output format for the response",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "Write code that does something useful",
                    "model": "claude-sonnet-4-5",
                    "rewrite": True,
                    "format": "json",
                }
            ]
        }
    }


class IssueResponse(BaseModel):
    """Issue found during evaluation."""

    quote: str = Field(description="The problematic text")
    problem: str = Field(description="Description of the issue")
    severity: str = Field(description="Issue severity: low, medium, high, critical")
    dimension: str = Field(description="The dimension this issue affects")


class DimensionScoreResponse(BaseModel):
    """Score for a single dimension."""

    dimension: str = Field(description="Dimension name")
    raw_score: int = Field(description="Raw score (0-10)")
    weight: int = Field(description="Weight multiplier")
    max_points: int = Field(description="Maximum possible points")
    points: float = Field(description="Calculated points")
    issues: list[IssueResponse] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class EvaluationResponse(BaseModel):
    """Evaluation results."""

    original_prompt: str = Field(description="The original prompt text")
    total_score: float = Field(description="Total score")
    max_score: int | float = Field(description="Maximum possible score")
    grade: str = Field(description="Letter grade (A-F)")
    dimension_scores: list[DimensionScoreResponse] = Field(description="Scores for each dimension")
    model: str = Field(description="Model used for evaluation")
    timestamp: str = Field(description="Evaluation timestamp")


class ImprovedPromptResponse(BaseModel):
    """Improved prompt suggestion."""

    improved_text: str = Field(description="The improved prompt text")
    changes_made: list[str] = Field(description="List of changes made")
    priority_alignment: dict[str, list[str]] = Field(
        default_factory=dict, description="Changes aligned to priority levels"
    )
    explanation: str = Field(default="", description="Explanation of improvements")


class EvaluateResponse(BaseModel):
    """Complete evaluation response."""

    evaluation: EvaluationResponse
    improved: ImprovedPromptResponse | None = Field(
        default=None, description="Improved prompt if rewrite was requested"
    )
    formatted: str | None = Field(
        default=None,
        description="Formatted output (markdown or HTML) if requested",
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="ok", description="Service status")
    version: str = Field(description="API version")
    timestamp: str = Field(description="Current timestamp")


class ModelsResponse(BaseModel):
    """Available models response."""

    models: list[str] = Field(description="List of available model names")
    default: str = Field(description="Default model name")
    count: int = Field(description="Number of available models")


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(description="Error message")
    detail: str | None = Field(default=None, description="Detailed error information")


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="Prompt Evaluation API",
    description=(
        "Universal Prompt Evaluation Tool API\n\n"
        "Evaluates prompts across 6 dimensions for LLM/agent execution quality:\n"
        "- **Actionability** (25 pts): Clear, unambiguous instructions\n"
        "- **Completeness** (25 pts): All necessary context included\n"
        "- **Token Efficiency** (10 pts): Concise without redundancy\n"
        "- **Cross-Agent Consistency** (10 pts): Works across different LLMs\n"
        "- **Consistency** (10 pts): Internal consistency and coherence\n"
        "- **Parsability** (10 pts): Structured and easy to parse\n"
        "- **Context Grounding** (10 pts bonus): References concrete context"
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# =============================================================================
# Helper: run evaluation and build response objects
# =============================================================================


def _run_evaluation(
    prompt: str,
    model: str,
    connection: str,
    do_rewrite: bool,
) -> tuple[
    EvaluationResponse,
    ImprovedPromptResponse | None,
    EvaluationResult,
    ImprovedPrompt | None,
    str,
    list[dict[str, str | float]],
]:
    """Run evaluation and optional rewrite.

    Returns (eval_response, improved_response, raw_evaluation, raw_improved, rewrite_warning, timings).
    """
    logger.info(
        "Evaluation started: prompt_length=%d, model=%s, rewrite=%s",
        len(prompt),
        model,
        do_rewrite,
    )
    t0 = time.time()
    timings: list[dict[str, str | float]] = []

    with PromptEvaluator(model=model, connection_name=connection) as evaluator:
        evaluation = evaluator.evaluate(prompt)

    eval_elapsed = time.time() - t0
    timings.append({"step": "Evaluate prompt", "elapsed": round(eval_elapsed, 1)})
    logger.info(
        "Evaluation complete: score=%.0f/%d, grade=%s, elapsed=%.1fs",
        evaluation.total_score,
        evaluation.max_score,
        evaluation.grade,
        eval_elapsed,
    )

    improved = None
    improved_raw = None
    rewrite_warning = ""
    if do_rewrite:
        t1 = time.time()
        logger.info("Rewrite started: model=%s", model)
        with PromptRewriter(model=model, connection_name=connection) as rewriter:
            improved_raw = rewriter.rewrite(prompt, evaluation)

            # Detect rewrite failure: rewriter returns original prompt unchanged
            if not improved_raw.changes_made and improved_raw.explanation.startswith(
                "Rewriting failed"
            ):
                rewrite_warning = improved_raw.explanation
                logger.warning("Rewrite failed: %s", rewrite_warning)
                improved_raw = None
                rewrite_elapsed = time.time() - t1
                timings.append(
                    {"step": "Rewrite prompt (failed)", "elapsed": round(rewrite_elapsed, 1)}
                )
            else:
                rewrite_elapsed = time.time() - t1
                timings.append({"step": "Rewrite prompt", "elapsed": round(rewrite_elapsed, 1)})
                logger.info(
                    "Rewrite complete: changes=%d, elapsed=%.1fs",
                    len(improved_raw.changes_made),
                    rewrite_elapsed,
                )
                improved = ImprovedPromptResponse(
                    improved_text=improved_raw.improved_text,
                    changes_made=improved_raw.changes_made,
                    priority_alignment=improved_raw.priority_alignment,
                    explanation=improved_raw.explanation,
                )

    total_elapsed = time.time() - t0
    timings.append({"step": "Total", "elapsed": round(total_elapsed, 1)})

    dimension_scores = []
    for ds in evaluation.dimension_scores:
        issues = [
            IssueResponse(
                quote=i.quote,
                problem=i.problem,
                severity=i.severity.value if isinstance(i.severity, Severity) else i.severity,
                dimension=i.dimension,
            )
            for i in ds.issues
        ]
        dimension_scores.append(
            DimensionScoreResponse(
                dimension=ds.dimension,
                raw_score=ds.raw_score,
                weight=ds.weight,
                max_points=ds.max_points,
                points=ds.points,
                issues=issues,
                recommendations=ds.recommendations,
            )
        )

    eval_response = EvaluationResponse(
        original_prompt=evaluation.original_prompt,
        total_score=evaluation.total_score,
        max_score=evaluation.max_score,
        grade=evaluation.grade,
        dimension_scores=dimension_scores,
        model=model,
        timestamp=datetime.now().isoformat(),
    )

    return eval_response, improved, evaluation, improved_raw, rewrite_warning, timings


# =============================================================================
# API Endpoints
# =============================================================================


@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
    description="Check if the API is running and responsive",
)
async def health_check() -> HealthResponse:
    """Return health status."""
    return HealthResponse(
        status="ok",
        version=__version__,
        timestamp=datetime.now().isoformat(),
    )


@app.get(
    "/api/models",
    response_model=ModelsResponse,
    tags=["System"],
    summary="List available models",
    description="Get list of supported Cortex models for evaluation",
)
async def list_models() -> ModelsResponse:
    """Return available models."""
    return ModelsResponse(
        models=list(SUPPORTED_MODELS),
        default=DEFAULT_MODEL,
        count=len(SUPPORTED_MODELS),
    )


@app.post(
    "/api/evaluate",
    response_model=EvaluateResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Evaluation failed"},
    },
    tags=["Evaluation"],
    summary="Evaluate a prompt",
    description="Evaluate a prompt across 6 dimensions and optionally generate an improved version",
)
async def evaluate_prompt(request: EvaluateRequest) -> EvaluateResponse:
    """Evaluate a prompt and optionally rewrite it."""
    logger.info(
        "API evaluation requested: model=%s, rewrite=%s, format=%s, prompt_length=%d",
        request.model,
        request.rewrite,
        request.format,
        len(request.prompt),
    )
    try:
        if request.model not in SUPPORTED_MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model: {request.model}. Valid: {', '.join(SUPPORTED_MODELS)}",
            )

        (
            eval_response,
            improved,
            evaluation,
            improved_raw,
            _warn,
            _timings,
        ) = await asyncio.to_thread(
            _run_evaluation, request.prompt, request.model, request.connection, request.rewrite
        )

        formatted = None
        if request.format != OutputFormat.JSON:
            report = EvaluationReport(
                evaluation=evaluation,
                improved=improved_raw if request.rewrite else None,
            )
            if request.format == OutputFormat.MARKDOWN:
                formatted = format_markdown(report)
            elif request.format == OutputFormat.HTML:
                formatted = format_html(report)

        return EvaluateResponse(
            evaluation=eval_response,
            improved=improved,
            formatted=formatted,
        )

    except CortexError as e:
        raise HTTPException(status_code=500, detail=f"Cortex error: {e}") from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}") from e


# =============================================================================
# Web UI Routes
# =============================================================================


@app.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def root(request: Request):
    """Redirect to web UI."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "version": __version__,
            "models": SUPPORTED_MODELS,
            "default_model": DEFAULT_MODEL,
        },
    )


@app.get(
    "/ui",
    response_class=HTMLResponse,
    tags=["Web UI"],
    summary="Interactive evaluation UI",
    include_in_schema=False,
)
async def web_ui(request: Request):
    """Render the evaluation form."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "version": __version__,
            "models": SUPPORTED_MODELS,
            "default_model": DEFAULT_MODEL,
        },
    )


@app.post(
    "/ui/evaluate",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def ui_evaluate(request: Request):
    """Handle HTMX form submission and return results partial."""
    try:
        body = await request.json()
        prompt = body.get("prompt", "").strip()
        model = body.get("model", DEFAULT_MODEL)
        connection = body.get("connection", "default")
        do_rewrite = body.get("rewrite", True)

        logger.info(
            "UI evaluation requested: model=%s, rewrite=%s, prompt_length=%d",
            model,
            do_rewrite,
            len(prompt),
        )

        if not prompt:
            return templates.TemplateResponse(
                "partials/error.html",
                {"request": request, "message": "Prompt cannot be empty."},
            )

        if model not in SUPPORTED_MODELS:
            return templates.TemplateResponse(
                "partials/error.html",
                {"request": request, "message": f"Invalid model: {model}"},
            )

        (
            eval_response,
            improved,
            _raw_eval,
            _raw_improved,
            rewrite_warning,
            timings,
        ) = await asyncio.to_thread(_run_evaluation, prompt, model, connection, do_rewrite)

        total_issues = sum(len(d.issues) for d in eval_response.dimension_scores)

        # Build name-keyed lookup for rubric criteria in the template
        dim_configs = {cfg.name: cfg for cfg in DIMENSIONS.values()}

        return templates.TemplateResponse(
            "partials/results.html",
            {
                "request": request,
                "evaluation": eval_response,
                "improved": improved,
                "model": model,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "grade_lower": eval_response.grade.lower(),
                "total_issues": total_issues,
                "rewrite_warning": rewrite_warning,
                "timings": timings,
                "dim_configs": dim_configs,
            },
        )

    except CortexError as e:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "message": "Cortex error", "detail": str(e)},
        )
    except Exception as e:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "message": "Evaluation failed", "detail": str(e)},
        )
