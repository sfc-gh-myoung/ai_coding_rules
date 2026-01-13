# Using the Rule Reviewer Skill (Internal Only)

**Note:** The Rule Reviewer Skill is **not deployed** to team projects. It remains in the ai_coding_rules source repository for internal use only.

**Last Updated:** 2026-01-13

## Background

The rule-reviewer skill automates running the Agent-Centric Rule Review (review optimized for AI agent understanding and executability) prompt against
a target rule file and writing the results to `reviews/` using the required filename
format from `skills/rule-reviewer/rubrics/*.md`.

Key behaviors:

- Uses the rubric and required output structure from `skills/rule-reviewer/rubrics/*.md`
- **100-point scoring system** using 0-10 raw scores with weighted dimensions: Formula `Raw (0-10) × (Weight / 2) = Points` (Actionability 25, Completeness 25, Consistency 15, Parsability 15, Token Efficiency 5, Staleness 10, Cross-Agent Consistency 5)
- **Priority Compliance Gate** — Evaluates rules against Design Priority Hierarchy before scoring
  - Evaluates rules against the Design Priority Hierarchy from 000-global-core.md before scoring
- **Agent Execution Test** — First gate counts blocking issues (undefined thresholds, missing branches, ambiguous actions)
- Computes `OUTPUT_FILE` as:
  - `reviews/<rule-name>-<model>-<YYYY-MM-DD>.md`
- **No-overwrite safety:** If file exists, uses suffix `-01.md`, `-02.md`, etc.
- Supports three review modes: FULL, FOCUSED, STALENESS

## Design Priority Hierarchy

Reviews evaluate rules against the priority order defined in `000-global-core.md`:

1. **Priority 1:** Agent Understanding and Execution Reliability (CRITICAL)
2. **Priority 2:** Token and Context Window Efficiency (HIGH)
3. **Priority 3:** Human Readability (TERTIARY)

**Scoring Impact:**
- 3-5 Priority 1 violations: Actionability capped at 15/25 (3/5)
- 6+ Priority 1 violations: Overall score capped at 60/100 (NEEDS_REFINEMENT)

## Review Dimensions

### Critical Dimensions (50 points)

**Actionability (25 points):**
- Can agent execute rule instructions without ambiguity?
- Detects vague phrases ("consider", "as appropriate", "if needed")
- Verifies explicit commands vs implicit suggestions

**Completeness (25 points):**
- All required sections present (Metadata, Scope, References, Contract)
- Error handling documented
- Edge cases covered

### Standard Dimensions (50 points)

**Consistency (15 points):**
- Follows schema conventions
- Terminology matches project standards
- Formatting uniform throughout

**Parsability (15 points):**
- Structure supports automated parsing
- Metadata in correct format
- Section headers at correct levels

**Token Efficiency (5 points):**
- Content density appropriate
- No redundant explanations
- TokenBudget accurate (within ±5% threshold)

**Staleness (10 points):**
- References current
- Links valid
- Examples up-to-date

**Cross-Agent Consistency (5 points):**
- Works across all agent types (Claude, GPT, Gemini, etc.)
- No agent-specific syntax or assumptions
- Universal conditionals without tool-specific branches

## Quality Verdicts

**Score Ranges:**
- **90-100 (EXECUTABLE):** Agent can execute as-is
- **80-89 (EXECUTABLE_WITH_REFINEMENTS):** Minor refinements recommended
- **60-79 (NEEDS_REFINEMENT):** Significant gaps; agent may fail
- **<60 (NOT_EXECUTABLE):** Major rework required

## Why Not Deployed?

The rule-reviewer skill is designed for **rule maintainers** working in the source
ai_coding_rules repository. It:

1. **Requires the rubric files** — `skills/rule-reviewer/rubrics/*.md` (colocated with skill)
2. **Writes to reviews/** — A directory structure specific to rule maintenance
3. **Targets rule files** — Most useful for rule authors validating their work

For deployed projects, teams should reference the skill's rubric files in `skills/rule-reviewer/rubrics/` directly if they need to review rules.

## Configuration

Both skills are excluded from deployment in [`pyproject.toml`](../pyproject.toml):

```toml
[tool.rule_deployer]
exclude_skills = [
    "rule-creator/",
    "rule-reviewer/",
]
```

## For ai_coding_rules Contributors

If you're working in the ai_coding_rules repository and want to run rule reviews:

### 1. Load the skill

```text
Load skills/rule-reviewer/SKILL.md
```

### 2. Request a review

```text
Use the rule-reviewer skill.

target_file: rules/801-project-readme.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

**With execution timing:**

```text
Use the rule-reviewer skill.

target_file: rules/801-project-readme.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
timing_enabled: true
```

### 3. Output location

The skill will write the review to:

`reviews/801-project-readme-claude-sonnet-45-2026-01-06.md`

If the file already exists, it uses suffixes: `-01.md`, `-02.md`, etc.

When `timing_enabled: true`, the output includes a Timing Metadata section with duration, token usage, and cost estimation.

## FAQ

### Q: What happens if the output file already exists?

**A:** The rule-reviewer skill uses no-overwrite safety. It appends suffixes (`-01.md`, `-02.md`, etc.) to avoid overwriting existing reviews.

### Q: What should I pass for `model`?

**A:** Prefer a slug like `claude-sonnet-45`. If you provide a raw model name, the
skill will normalize it to a slug before writing the file.

### Q: Does `target_file` have to be under `rules/`?

**A:** The expected use case is reviewing files under `rules/`, but the skill can
review any readable `.md` file path you provide.
The output filename always uses the base filename (without extension) of `target_file`.

### Q: Where does the rubric come from?

**A:** The skill uses rubric files in `skills/rule-reviewer/rubrics/` (actionability.md, completeness.md, consistency.md, parsability.md, token-efficiency.md, staleness.md, cross-agent-consistency.md) as the rubric and required
output format and writes the final review to `reviews/`.

### Q: Can I use rule-reviewer in a deployed project?

**A:** No, this skill is internal-only. For deployed projects, reference the
skill's rubric files in `skills/rule-reviewer/rubrics/` directly for the review rubric.
