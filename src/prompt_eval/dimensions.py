"""Evaluation dimensions for prompt scoring."""

import re
from dataclasses import dataclass
from enum import Enum


class DimensionType(Enum):
    """Evaluation dimension types."""

    ACTIONABILITY = "actionability"
    COMPLETENESS = "completeness"
    TOKEN_EFFICIENCY = "token_efficiency"
    CROSS_AGENT_CONSISTENCY = "cross_agent_consistency"
    CONSISTENCY = "consistency"
    PARSABILITY = "parsability"
    CONTEXT_GROUNDING = "context_grounding"  # Bonus


@dataclass
class DimensionConfig:
    """Configuration for an evaluation dimension."""

    name: str
    dimension_type: DimensionType
    weight: int
    max_points: int
    is_bonus: bool
    description: str
    criteria: list[str]
    blocking_patterns: list[str]  # Regex patterns for automatic issue detection
    scoring_guide: str
    llm_prompt: str


# Blocking issue patterns for automatic detection
ACTIONABILITY_PATTERNS = [
    r"\b(large|small|significant|appropriate|reasonable|adequate|sufficient)\b",  # Undefined thresholds
    r"\b(consider|you may want to|optionally|perhaps|might)\b",  # Ambiguous actions
    r"\bif\b(?!.*\belse\b).*(?:\.|$)",  # If without else (simplified)
    r"\bshould be\b",  # Passive voice
    r"\b(some|many|few|several|various)\b",  # Vague quantifiers
]

CROSS_AGENT_PATTERNS = [
    r"\b(claude|gpt|gemini|copilot|cursor|cline)\s*(\'s|code|artifacts?)\b",  # Agent-specific references
    r"\b(artifacts?|canvas|workspace)\b",  # Platform-specific features
    r"\bcontext window\b",  # Capability assumptions
    r"\b(tool|function)\s*call(ing|s)?\b",  # Implementation-specific
]

TOKEN_EFFICIENCY_PATTERNS = [
    r"(\b\w+\b)(?:\s+\w+){0,3}\s+\1\b",  # Repeated words nearby
    r"\b(please|kindly|basically|actually|really|very|quite)\b",  # Filler words
    r"\b(in order to|for the purpose of|with the aim of)\b",  # Verbose phrases
]


def calculate_points(raw_score: int, weight: int) -> float:
    """Calculate points from raw score and weight."""
    return raw_score * (weight / 2)


def score_from_issues(issue_count: int) -> int:
    """Calculate raw score (0-10) based on blocking issue count."""
    if issue_count == 0:
        return 10
    elif issue_count <= 3:
        return 8
    elif issue_count <= 7:
        return 6
    elif issue_count <= 11:
        return 4
    else:
        return 2


DIMENSIONS: dict[DimensionType, DimensionConfig] = {
    DimensionType.ACTIONABILITY: DimensionConfig(
        name="Actionability",
        dimension_type=DimensionType.ACTIONABILITY,
        weight=5,
        max_points=25,
        is_bonus=False,
        description="Can agents execute without judgment calls?",
        criteria=[
            "No undefined thresholds (large, significant, appropriate)",
            "All conditionals have explicit branches (if X then Y; else Z)",
            "No ambiguous actions (consider, may want to, optionally)",
            "Uses imperative voice (validate X, not X should be validated)",
            "Quantified requirements where applicable",
        ],
        blocking_patterns=ACTIONABILITY_PATTERNS,
        scoring_guide="""
0 blocking issues → 10/10 (25 pts)
1-3 issues → 8/10 (20 pts)
4-7 issues → 6/10 (15 pts)
8-11 issues → 4/10 (10 pts)
12+ issues → 2/10 (5 pts)
""",
        llm_prompt="""Evaluate this prompt for ACTIONABILITY - can an autonomous agent execute it without making judgment calls?

Check for:
1. Undefined thresholds: "large", "significant", "appropriate", "reasonable"
2. Missing conditional branches: "if X" without "else"
3. Ambiguous actions: "consider", "you may want to", "optionally"
4. Passive voice: "should be validated" instead of "validate"
5. Vague quantifiers: "some", "many", "few", "several"

For each issue found, quote the exact problematic text.""",
    ),
    DimensionType.COMPLETENESS: DimensionConfig(
        name="Completeness",
        dimension_type=DimensionType.COMPLETENESS,
        weight=5,
        max_points=25,
        is_bonus=False,
        description="Are all scenarios and edge cases covered?",
        criteria=[
            "All conditional branches have explicit outcomes",
            "Error and edge cases are addressed",
            "Input constraints are specified",
            "Output format is defined",
            "Success criteria are stated",
        ],
        blocking_patterns=[],  # Requires LLM analysis
        scoring_guide="""
All 5 criteria met → 10/10 (25 pts)
4 criteria met → 8/10 (20 pts)
3 criteria met → 6/10 (15 pts)
2 criteria met → 4/10 (10 pts)
0-1 criteria met → 2/10 (5 pts)
""",
        llm_prompt="""Evaluate this prompt for COMPLETENESS - are all scenarios and edge cases covered?

Check for:
1. Do all conditional paths have explicit outcomes?
2. Are error cases and edge cases addressed?
3. Are input constraints clearly specified?
4. Is the expected output format defined?
5. Are success criteria explicitly stated?

Identify any gaps or missing specifications.""",
    ),
    DimensionType.TOKEN_EFFICIENCY: DimensionConfig(
        name="Token Efficiency",
        dimension_type=DimensionType.TOKEN_EFFICIENCY,
        weight=2,
        max_points=10,
        is_bonus=False,
        description="Is the prompt concise without redundancy?",
        criteria=[
            "No redundant phrases or repeated instructions",
            "Uses structured lists over verbose prose",
            "No unnecessary context or background",
            "Critical information is front-loaded",
            "No filler words (please, kindly, basically)",
        ],
        blocking_patterns=TOKEN_EFFICIENCY_PATTERNS,
        scoring_guide="""
Highly efficient, no redundancy → 10/10 (10 pts)
Minor redundancy, good structure → 8/10 (8 pts)
Some verbose sections → 6/10 (6 pts)
Significant redundancy → 4/10 (4 pts)
Very verbose, poor structure → 2/10 (2 pts)
""",
        llm_prompt="""Evaluate this prompt for TOKEN EFFICIENCY - is it concise without redundancy?

Check for:
1. Redundant phrases or repeated instructions
2. Verbose prose that could be structured lists
3. Unnecessary context or background information
4. Is critical information front-loaded?
5. Filler words: "please", "kindly", "basically", "actually"

Identify specific areas where tokens could be saved.""",
    ),
    DimensionType.CROSS_AGENT_CONSISTENCY: DimensionConfig(
        name="Cross-Agent Consistency",
        dimension_type=DimensionType.CROSS_AGENT_CONSISTENCY,
        weight=2,
        max_points=10,
        is_bonus=False,
        description="Will all LLMs interpret this the same way?",
        criteria=[
            "No agent-specific tool references (Claude artifacts, GPT canvas)",
            "No capability assumptions (context window, multimodal)",
            "No model-specific terminology",
            "All conditionals have explicit defaults",
            "Compatible with: GPT, Claude, Gemini, Cursor, Cline, Claude Code, Gemini CLI, GitHub Copilot",
        ],
        blocking_patterns=CROSS_AGENT_PATTERNS,
        scoring_guide="""
Fully universal, no agent-specific content → 10/10 (10 pts)
Minor agent-specific terms, easily portable → 8/10 (8 pts)
Some platform assumptions → 6/10 (6 pts)
Significant agent dependencies → 4/10 (4 pts)
Heavily agent-specific → 2/10 (2 pts)
""",
        llm_prompt="""Evaluate this prompt for CROSS-AGENT CONSISTENCY - will ALL LLMs interpret it the same way?

Must work consistently across: GPT, Claude, Gemini, Cursor, Cline, Claude Code, Gemini CLI, GitHub Copilot

Check for:
1. Agent-specific references: "use Claude's artifacts", "GPT canvas"
2. Capability assumptions: context window size, multimodal features
3. Model-specific terminology or features
4. Conditionals without explicit defaults
5. Platform-specific tool or function references

Identify anything that would behave differently across agents.""",
    ),
    DimensionType.CONSISTENCY: DimensionConfig(
        name="Consistency",
        dimension_type=DimensionType.CONSISTENCY,
        weight=2,
        max_points=10,
        is_bonus=False,
        description="No internal contradictions?",
        criteria=[
            "No contradictory instructions",
            "No conflicting constraints",
            "No incompatible requirements",
            "Consistent terminology throughout",
            "Aligned priorities and goals",
        ],
        blocking_patterns=[],  # Requires LLM semantic analysis
        scoring_guide="""
No contradictions, fully coherent → 10/10 (10 pts)
Minor terminology inconsistency → 8/10 (8 pts)
One small contradiction → 6/10 (6 pts)
Multiple minor contradictions → 4/10 (4 pts)
Major contradictions → 2/10 (2 pts)
""",
        llm_prompt="""Evaluate this prompt for CONSISTENCY - are there any internal contradictions?

Check for:
1. Contradictory instructions (do X, but also don't do X)
2. Conflicting constraints (must be fast AND thorough)
3. Incompatible requirements
4. Inconsistent terminology (same concept, different names)
5. Misaligned priorities or goals

Quote any contradictory passages found.""",
    ),
    DimensionType.PARSABILITY: DimensionConfig(
        name="Parsability",
        dimension_type=DimensionType.PARSABILITY,
        weight=2,
        max_points=10,
        is_bonus=False,
        description="Well-structured with clear sections?",
        criteria=[
            "Clear section structure with headers",
            "Appropriate use of markdown formatting",
            "Logical information hierarchy",
            "Scannable format (lists, bullets)",
            "Consistent formatting patterns",
        ],
        blocking_patterns=[],  # Requires structural analysis
        scoring_guide="""
Excellent structure, highly scannable → 10/10 (10 pts)
Good structure, minor improvements possible → 8/10 (8 pts)
Adequate structure, some wall-of-text → 6/10 (6 pts)
Poor structure, hard to scan → 4/10 (4 pts)
No structure, dense prose → 2/10 (2 pts)
""",
        llm_prompt="""Evaluate this prompt for PARSABILITY - is it well-structured and easy to parse?

Check for:
1. Clear section headers and structure
2. Appropriate markdown formatting
3. Logical information hierarchy (general → specific)
4. Scannable format (lists, bullets, numbered steps)
5. Consistent formatting patterns throughout

Identify structural improvements that would aid comprehension.""",
    ),
    DimensionType.CONTEXT_GROUNDING: DimensionConfig(
        name="Context Grounding",
        dimension_type=DimensionType.CONTEXT_GROUNDING,
        weight=1,
        max_points=10,
        is_bonus=True,
        description="Does it provide sufficient context? (BONUS)",
        criteria=[
            "Sufficient background for the task",
            "Clear scope boundaries defined",
            "Relevant constraints provided",
            "Domain context included where needed",
            "Assumptions explicitly stated",
        ],
        blocking_patterns=[],  # Requires semantic analysis
        scoring_guide="""
BONUS DIMENSION (0-10 extra points)
Excellent context, fully grounded → 10/10 (10 pts bonus)
Good context, minor gaps → 7/10 (7 pts bonus)
Adequate context → 5/10 (5 pts bonus)
Minimal context → 2/10 (2 pts bonus)
No context provided → 0/10 (0 pts bonus)
""",
        llm_prompt="""Evaluate this prompt for CONTEXT GROUNDING - does it provide sufficient context?

This is a BONUS dimension worth up to 10 extra points.

Check for:
1. Is there sufficient background for the task?
2. Are scope boundaries clearly defined?
3. Are relevant constraints provided?
4. Is domain-specific context included where needed?
5. Are assumptions explicitly stated?

Identify what context is missing or would improve agent understanding.""",
    ),
}


def get_dimension(dimension_type: DimensionType) -> DimensionConfig:
    """Get dimension configuration by type."""
    return DIMENSIONS[dimension_type]


def get_all_dimensions(include_bonus: bool = True) -> list[DimensionConfig]:
    """Get all dimension configurations."""
    dims = list(DIMENSIONS.values())
    if not include_bonus:
        dims = [d for d in dims if not d.is_bonus]
    return dims


def get_max_score(include_bonus: bool = True) -> int:
    """Get maximum possible score."""
    dims = get_all_dimensions(include_bonus)
    return sum(d.max_points for d in dims)


def detect_blocking_issues(text: str, dimension_type: DimensionType) -> list[tuple[str, str]]:
    """Detect blocking issues using regex patterns.

    Returns list of (matched_text, pattern_description) tuples.
    """
    config = DIMENSIONS[dimension_type]
    issues = []

    for pattern in config.blocking_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            issues.append((match.group(0), pattern))

    return issues
