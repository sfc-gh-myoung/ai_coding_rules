# Using the Plan Reviewer Skill

The Plan Reviewer Skill evaluates LLM-generated plans to ensure autonomous agents can execute them successfully. It scores plans across 8 dimensions optimized for agent executability using a 100-point scoring system.

## Background

The plan-reviewer skill runs Agent-Centric Plan Reviews using the rubric in `skills/plan-reviewer/PROMPT.md` and writes results to `reviews/`.

Key behaviors:

- **100-point scoring system** with weighted dimensions (Executability 20, Completeness 20, Success Criteria 20, Scope 15, Dependencies 10, Decomposition 5, Context 5, Risk Awareness 5)
- **Priority Compliance Gate** — Evaluates plans against Design Priority Hierarchy before scoring
- **Agent Execution Test** — First gate counts blocking issues (ambiguous phrases, implicit commands, missing branches, undefined thresholds)
- Reviews plans against 8 dimensions: Executability, Completeness, Success Criteria, Scope, Dependencies, Decomposition, Context, Risk Awareness
- Supports three review modes: FULL, COMPARISON, META-REVIEW
- Computes `OUTPUT_FILE` as:
  - FULL mode: `reviews/plan-<plan-name>-<model>-<YYYY-MM-DD>.md`
  - COMPARISON mode: `reviews/plan-comparison-<model>-<YYYY-MM-DD>.md`
  - META-REVIEW mode: `reviews/meta-<document-name>-<model>-<YYYY-MM-DD>.md`
- **No-overwrite safety:** If file exists, uses suffix `-01.md`, `-02.md`, etc.
- Detects ambiguous phrases that require human judgment
- Verifies success criteria are agent-verifiable

## Design Priority Hierarchy

Reviews evaluate plans against the priority order defined in `000-global-core.md`:

1. **Priority 1:** Agent Understanding and Execution Reliability (CRITICAL)
2. **Priority 2:** Token and Context Window Efficiency (HIGH)
3. **Priority 3:** Human Readability (TERTIARY)

**Scoring Impact (Priority 1 Gate):**
- ≥10 blocking issues: Overall score capped at 60/100 (NEEDS_REFINEMENT)
- ≥20 blocking issues: Overall score capped at 40/100 (NOT_EXECUTABLE)

## Quick Start

### 1. Load the skill

```text
@skills/plan-reviewer/SKILL.md
```

### 2. Request a review

**FULL mode (single plan):**

```text
Use the plan-reviewer skill.

target_file: plans/IMPROVE_RULE_LOADING.md
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**COMPARISON mode (multiple plans):**

```text
Use the plan-reviewer skill.

target_files: plans/auth-plan-claude.md, plans/auth-plan-gpt.md
task_description: Implement OAuth2 authentication
review_date: 2025-12-16
review_mode: COMPARISON
model: claude-sonnet45
```

**META-REVIEW mode (review consistency):**

```text
Use the plan-reviewer skill.

target_files: reviews/plan-X-sonnet-2025-12-16.md, reviews/plan-X-gpt-2025-12-16.md
original_document: plans/X.md
review_date: 2025-12-16
review_mode: META-REVIEW
model: claude-sonnet45
```

### 3. Output location

The skill writes reviews to the `reviews/` directory:

- FULL: `reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md`
- COMPARISON: `reviews/plan-comparison-claude-sonnet45-2025-12-16.md`
- META-REVIEW: `reviews/meta-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md`

If the file already exists, suffixes are appended: `-01.md`, `-02.md`, etc.

## Review Modes

### FULL Mode (Comprehensive)

Use for evaluating a single plan. Provides detailed scoring across all 8 dimensions with verification tables.

```text
review_mode: FULL
```

**Best for:**
- Validating a plan before agent execution
- Initial plan quality assessment
- Identifying specific improvements needed

### COMPARISON Mode (Multi-Plan Ranking)

Use when choosing between competing plans for the same task. Provides side-by-side scoring and declares a winner.

```text
review_mode: COMPARISON
```

**Best for:**
- Choosing between plans from different LLMs
- Selecting best plan from team alternatives
- A/B testing plan generation approaches

### META-REVIEW Mode (Review Consistency)

Use after multiple reviewers (LLMs or humans) have reviewed the same plan. Analyzes variance and identifies the most reliable review.

```text
review_mode: META-REVIEW
```

**Best for:**
- Validating review consistency across models
- Identifying calibration issues
- Building consensus score

## Review Dimensions

### Critical Dimensions (75 points)

**Executability (20 points):**
- Can agent execute without human judgment?
- Counts ambiguous phrases ("consider", "if appropriate", "as needed")
- Counts implicit commands (descriptions vs explicit commands)

**Completeness (20 points):**
- Are all steps present?
- Setup, validation, cleanup, error recovery coverage

**Success Criteria (20 points):**
- Can agent verify completion programmatically?
- Percentage of tasks with agent-verifiable criteria

**Scope (15 points):**
- Are boundaries explicit?
- Start/end state defined?

### Standard Dimensions (25 points)

**Dependencies (10 points):**
- Is execution order explicit?
- Blocking relationships documented?

**Decomposition (5 points):**
- Is task granularity appropriate?
- Single-action steps?

**Context (5 points):**
- Is necessary background provided?
- Domain terms defined?

**Risk Awareness (5 points):**
- Are fallbacks documented?
- Recovery paths defined?

## Agent Executability Verdicts

**Score Ranges:**
- **90-100 (EXECUTABLE):** Agent can execute as-is
- **80-89 (EXECUTABLE_WITH_REFINEMENTS):** Minor refinements recommended
- **60-79 (NEEDS_REFINEMENT):** Significant gaps; agent may fail
- **<60 (NOT_EXECUTABLE):** Major rework required

**Priority 1 Overrides:**
- ≥10 blocking issues: Verdict capped at NEEDS_REFINEMENT (max 60/100)
- ≥20 blocking issues: Verdict = NOT_EXECUTABLE (max 40/100)

## Mandatory Verification Tables

Reviews include these verification tables to support scoring:

1. **Executability Audit** — Lists ambiguous phrases and implicit commands with line numbers and proposed fixes
2. **Completeness Audit** — Phase-by-phase coverage (Setup, Validation, Cleanup, Error Recovery)
3. **Success Criteria Audit** — Task-by-task criteria presence and agent-verifiability
4. **Priority Compliance Summary** — Counts of Priority 1 and Priority 2 violations with score cap status

## Example Workflows

### Pre-Execution Validation

```text
Use the plan-reviewer skill.

target_file: plans/deploy-feature.md
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

Validate a plan before handing it to an autonomous agent.

### Choosing Best Plan

```text
Use the plan-reviewer skill.

target_files: plans/approach-a.md, plans/approach-b.md, plans/approach-c.md
task_description: Migrate database to new schema
review_date: 2025-12-16
review_mode: COMPARISON
model: claude-sonnet45
```

Compare multiple approaches and get a recommendation.

### Validating Review Quality

```text
Use the plan-reviewer skill.

target_files: reviews/plan-X-claude-2025-12-16.md, reviews/plan-X-gpt-2025-12-16.md
original_document: plans/X.md
review_date: 2025-12-16
review_mode: META-REVIEW
model: claude-sonnet45
```

After multiple models review the same plan, analyze consistency.

## FAQ

### Q: What happens if the output file already exists?

**A:** The skill uses no-overwrite safety. It appends suffixes (`-01.md`, `-02.md`, etc.) to avoid overwriting existing reviews.

### Q: What should I pass for `model`?

**A:** Prefer a slug like `claude-sonnet45`. If you provide a raw model name, the skill normalizes it to a slug before writing the file.

### Q: What makes a plan "executable" by an agent?

**A:** An executable plan has:
- Explicit commands (no "consider" or "if appropriate")
- Verifiable success criteria (exit codes, file existence checks)
- Complete steps (setup, validation, cleanup, error recovery)
- Clear scope boundaries (defined start/end states)

### Q: How are ambiguous phrases detected?

**A:** The skill scans for phrases like "consider", "if appropriate", "as needed", "when necessary" that require human judgment. Plans with >15 ambiguous phrases automatically score low on Executability.

### Q: What's the difference between plan-reviewer and doc-reviewer?

**A:**
- **plan-reviewer**: Optimized for agent executability, task completeness, scope clarity
- **doc-reviewer**: Optimized for human readability, accuracy, link validation

Use plan-reviewer for plans an agent will execute. Use doc-reviewer for documentation humans will read.

### Q: How long does a FULL review take?

**A:** Depends on plan size:
- Small plan (<100 lines): 2-5 minutes
- Medium plan (100-300 lines): 5-10 minutes
- Large plan (>300 lines): 10-20 minutes

### Q: Where does the rubric come from?

**A:** The skill uses `skills/plan-reviewer/PROMPT.md` as the rubric and required output format.

## Integration with Other Skills

### With doc-reviewer

Plan files can be reviewed as documentation:
- **doc-reviewer**: Accuracy, link validation, general clarity (for human readers)
- **plan-reviewer**: Agent executability, task completeness, scope (for autonomous agents)

### With rule-reviewer

If a plan references rules:
- Use **rule-reviewer** to validate rules are agent-executable
- Use **plan-reviewer** to validate the plan using those rules

## Support

For detailed documentation:
- **Skill README:** `@skills/plan-reviewer/README.md`
- **Workflow guides:** `@skills/plan-reviewer/workflows/*.md`
- **Examples:** `@skills/plan-reviewer/examples/*.md`
- **Validation tests:** `@skills/plan-reviewer/tests/*.md`

