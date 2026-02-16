"""LLM-powered prompt rewriting for improvement."""

from .cortex import CortexClient, CortexConfig, CortexError
from .models import (
    DEFAULT_MODEL,
    EvaluationResult,
    ImprovedPrompt,
)

REWRITE_SYSTEM_PROMPT = """You are a prompt engineering expert. Rewrite prompts to maximize autonomous agent execution reliability.

DESIGN PRIORITIES (Apply in strict order):
1. P1 CRITICAL: Agent understanding and execution reliability
   - Replace ALL vague terms with quantified thresholds
   - Make ALL conditionals explicit (if X then Y; else Z)
   - Use imperative voice exclusively
   - Eliminate ambiguous actions ("consider", "may want to", "optionally")

2. P2 HIGH: Rule discovery efficacy and determinism
   - Add clear keywords for searchability
   - Structure with consistent patterns
   - Use explicit section headers

3. P3 HIGH: Context window and token efficiency
   - Use structured lists over prose
   - Front-load critical information
   - Remove redundancy
   - Be concise without losing clarity

4. P4 LOW: Human developer maintainability
   - Only consider after P1-3 are satisfied
   - Readability is secondary to agent reliability

UNIVERSAL COMPATIBILITY:
The rewritten prompt MUST work identically across:
GPT, Claude, Gemini, Cursor, Cline, Claude Code, Gemini CLI, GitHub Copilot

You MUST respond with valid JSON only."""


class PromptRewriter:
    """Rewrites prompts to improve agent execution reliability."""

    def __init__(
        self,
        client: CortexClient | None = None,
        model: str = DEFAULT_MODEL,
        connection_name: str = "default",
    ):
        """Initialize rewriter.

        Args:
            client: Cortex client (created if not provided).
            model: Model to use for rewriting.
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

    def rewrite(
        self,
        original_prompt: str,
        evaluation: EvaluationResult | None = None,
    ) -> ImprovedPrompt:
        """Rewrite a prompt to improve it.

        Args:
            original_prompt: The original prompt text.
            evaluation: Optional evaluation results to guide rewriting.

        Returns:
            Improved prompt with explanation.
        """
        rewrite_prompt = self._build_rewrite_prompt(original_prompt, evaluation)

        try:
            response = self.client.complete_json(
                prompt=rewrite_prompt,
                system_prompt=REWRITE_SYSTEM_PROMPT,
                model=self.model,
            )

            return self._parse_rewrite_response(response)

        except CortexError as e:
            # Return original with error explanation
            return ImprovedPrompt(
                improved_text=original_prompt,
                changes_made=[],
                priority_alignment={},
                explanation=f"Rewriting failed: {e}",
            )

    def _build_rewrite_prompt(
        self,
        original_prompt: str,
        evaluation: EvaluationResult | None,
    ) -> str:
        """Build the rewrite prompt.

        Args:
            original_prompt: The original prompt to rewrite.
            evaluation: Optional evaluation results for context.

        Returns:
            Formatted prompt for the LLM.
        """
        eval_section = ""
        if evaluation:
            issues_summary = []
            for ds in evaluation.dimension_scores:
                if ds.issues:
                    issues_summary.append(f"- {ds.dimension}: {len(ds.issues)} issues")
                    for issue in ds.issues[:3]:  # Limit to top 3 per dimension
                        issues_summary.append(f'  - "{issue.quote}": {issue.problem}')

            if issues_summary:
                eval_section = f"""
EVALUATION RESULTS (Score: {evaluation.total_score}/{evaluation.max_score}, Grade: {evaluation.grade}):
{chr(10).join(issues_summary)}
"""

        return f"""ORIGINAL PROMPT:
\"\"\"
{original_prompt}
\"\"\"
{eval_section}
Rewrite this prompt following the design priorities. Provide:

1. IMPROVED PROMPT - Complete rewrite optimized for agent execution
2. CHANGES MADE - Bullet list of specific improvements
3. PRIORITY ALIGNMENT - How each major change maps to P1-P4

Respond with JSON:
{{
  "improved_prompt": "the complete rewritten prompt",
  "changes_made": ["change 1", "change 2", ...],
  "priority_alignment": {{
    "P1": ["change addressing P1", ...],
    "P2": ["change addressing P2", ...],
    "P3": ["change addressing P3", ...],
    "P4": ["change addressing P4", ...]
  }},
  "explanation": "Brief summary of why this version is better"
}}"""

    def _parse_rewrite_response(self, response: dict) -> ImprovedPrompt:
        """Parse LLM response for rewritten prompt.

        Args:
            response: Parsed JSON response from LLM.

        Returns:
            ImprovedPrompt with extracted data.
        """
        return ImprovedPrompt(
            improved_text=response.get("improved_prompt", ""),
            changes_made=response.get("changes_made", []),
            priority_alignment=response.get("priority_alignment", {}),
            explanation=response.get("explanation", ""),
        )

    def close(self):
        """Close the client if we own it."""
        if self._owns_client and self.client:
            self.client.close()

    def __enter__(self) -> "PromptRewriter":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
