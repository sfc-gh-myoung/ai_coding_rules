"""Core evaluation logic for prompt scoring."""

from collections.abc import Callable

from .cortex import CortexClient, CortexConfig, CortexError
from .dimensions import (
    DimensionConfig,
    calculate_points,
    detect_blocking_issues,
    get_all_dimensions,
    get_max_score,
    score_from_issues,
)
from .models import (
    DEFAULT_MODEL,
    DimensionScore,
    EvaluationResult,
    Issue,
    Severity,
    calculate_grade,
)

SYSTEM_PROMPT = """You are a prompt engineering expert evaluating prompts for autonomous AI agent execution.

DESIGN PRIORITIES (Strictly Enforced):
1. P1 CRITICAL: Agent understanding and execution reliability - unambiguous, unequivocal wording
2. P2 HIGH: Rule discovery efficacy and determinism
3. P3 HIGH: Context window and token utilization efficiency
4. P4 LOW: Human developer maintainability (P1-3 significantly outweigh P4)

UNIVERSAL APPLICABILITY:
Your evaluation must ensure consistent behavior across ALL agents:
- GPT (OpenAI)
- Claude (Anthropic)
- Gemini (Google)
- Cursor
- Cline
- Claude Code
- Gemini CLI
- GitHub Copilot

You MUST respond with valid JSON only. No markdown, no explanation outside JSON."""


class PromptEvaluator:
    """Evaluates prompts across multiple dimensions using LLM analysis."""

    def __init__(
        self,
        client: CortexClient | None = None,
        model: str = DEFAULT_MODEL,
        connection_name: str = "default",
    ):
        """Initialize evaluator.

        Args:
            client: Cortex client (created if not provided).
            model: Model to use for evaluation.
            connection_name: Snowflake connection name.
        """
        self.model = model
        if client:
            self.client = client
            self._owns_client = False
        else:
            config = CortexConfig(connection_name=connection_name, model=model)
            self.client = CortexClient(config)
            self._owns_client = True

    def evaluate(
        self,
        prompt: str,
        include_bonus: bool = True,
        on_progress: "Callable[[str, str, float | None], None] | None" = None,
    ) -> EvaluationResult:
        """Evaluate a prompt across all dimensions.

        Args:
            prompt: The prompt text to evaluate.
            include_bonus: Whether to include bonus dimension.
            on_progress: Optional callback(dimension_name, status, elapsed_seconds)
                called when each dimension starts/finishes scoring.

        Returns:
            Complete evaluation result with scores.
        """
        dimension_scores: list[DimensionScore] = []
        all_issues: list[Issue] = []

        dimensions = get_all_dimensions(include_bonus=include_bonus)

        for dim_config in dimensions:
            if on_progress:
                on_progress(dim_config.name, "started", None)
            t0 = __import__("time").time()
            score = self._score_dimension(prompt, dim_config)
            elapsed = __import__("time").time() - t0
            if on_progress:
                on_progress(dim_config.name, "done", elapsed)
            dimension_scores.append(score)
            all_issues.extend(score.issues)

        total_score = sum(ds.points for ds in dimension_scores)
        max_score = get_max_score(include_bonus=include_bonus)
        grade = calculate_grade(total_score, max_score)

        return EvaluationResult(
            original_prompt=prompt,
            total_score=total_score,
            max_score=max_score,
            grade=grade,
            dimension_scores=dimension_scores,
            all_issues=all_issues,
            model_used=self.model,
        )

    def _score_dimension(
        self,
        prompt: str,
        dim_config: DimensionConfig,
    ) -> DimensionScore:
        """Score a prompt on a single dimension.

        Uses regex patterns for automatic detection, then LLM for deeper analysis.
        """
        # First, detect issues using regex patterns
        auto_issues = detect_blocking_issues(prompt, dim_config.dimension_type)

        # Build evaluation prompt for LLM
        eval_prompt = self._build_evaluation_prompt(prompt, dim_config)

        try:
            # Get LLM analysis
            response = self.client.complete_json(
                prompt=eval_prompt,
                system_prompt=SYSTEM_PROMPT,
                model=self.model,
            )

            # Parse response
            raw_score, issues, recommendations = self._parse_dimension_response(
                response, dim_config
            )

        except CortexError:
            # Fallback to regex-only scoring if LLM fails
            raw_score = score_from_issues(len(auto_issues))
            issues = [
                Issue(
                    quote=match,
                    problem=f"Pattern match: {pattern[:50]}...",
                    severity=Severity.MEDIUM,
                    dimension=dim_config.name,
                )
                for match, pattern in auto_issues
            ]
            recommendations = ["LLM analysis unavailable - using pattern matching only"]

        points = calculate_points(raw_score, dim_config.weight)

        return DimensionScore(
            dimension=dim_config.name,
            raw_score=raw_score,
            weight=dim_config.weight,
            max_points=dim_config.max_points,
            points=points,
            issues=issues,
            recommendations=recommendations,
        )

    def _build_evaluation_prompt(
        self,
        prompt: str,
        dim_config: DimensionConfig,
    ) -> str:
        """Build the evaluation prompt for a specific dimension."""
        return f"""{dim_config.llm_prompt}

SCORING GUIDE:
{dim_config.scoring_guide}

PROMPT TO EVALUATE:
\"\"\"
{prompt}
\"\"\"

Respond with JSON:
{{
  "score": <0-10>,
  "issues": [
    {{"quote": "exact text from prompt", "problem": "description", "severity": "critical|high|medium|low"}}
  ],
  "recommendations": ["specific improvement suggestion"]
}}"""

    def _parse_dimension_response(
        self,
        response: dict,
        dim_config: DimensionConfig,
    ) -> tuple[int, list[Issue], list[str]]:
        """Parse LLM response for dimension scoring."""
        raw_score = int(response.get("score", 5))
        raw_score = max(0, min(10, raw_score))  # Clamp to 0-10

        issues = []
        for issue_data in response.get("issues", []):
            severity_str = issue_data.get("severity", "medium").lower()
            try:
                severity = Severity(severity_str)
            except ValueError:
                severity = Severity.MEDIUM

            issues.append(
                Issue(
                    quote=issue_data.get("quote", ""),
                    problem=issue_data.get("problem", ""),
                    severity=severity,
                    dimension=dim_config.name,
                )
            )

        recommendations = response.get("recommendations", [])

        return raw_score, issues, recommendations

    def close(self):
        """Close the client if we own it."""
        if self._owns_client and self.client:
            self.client.close()

    def __enter__(self) -> "PromptEvaluator":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and close resources."""
        self.close()
