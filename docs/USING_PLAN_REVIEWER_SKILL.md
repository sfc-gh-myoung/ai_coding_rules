# Using the Plan Reviewer Skill

**Last Updated:** 2026-01-21

The Plan Reviewer Skill evaluates LLM-generated plans to ensure autonomous agents can execute them successfully. It scores plans across 8 dimensions optimized for agent executability using a 100-point scoring system.

## Background

The plan-reviewer skill runs Agent-Centric Plan Reviews (reviews optimized for AI agent understanding and executability) using the rubrics in `skills/plan-reviewer/rubrics/*.md` and writes results to `reviews/`.

Key behaviors:

- **100-point scoring system** using 0-10 raw scores with weighted dimensions: Formula `Raw (0-10) × (Weight / 2) = Points` (Executability 20, Completeness 20, Success Criteria 20, Scope 15, Dependencies 10, Decomposition 5, Context 5, Risk Awareness 5)
- **Priority Compliance Gate** — Evaluates plans against Design Priority Hierarchy before scoring
- **Agent Execution Test** — First gate counts blocking issues (ambiguous phrases, implicit commands, missing branches, undefined thresholds)
- Reviews plans against 8 dimensions: Executability, Completeness, Success Criteria, Scope, Dependencies, Decomposition, Context, Risk Awareness
- Supports four review modes: FULL, COMPARISON, META-REVIEW, DELTA
- Computes `OUTPUT_FILE` as:
  - FULL mode: `{output_root}plan-reviews/plan-<plan-name>-<model>-<YYYY-MM-DD>.md`
  - COMPARISON mode: `{output_root}summaries/_comparison-<model>-<YYYY-MM-DD>.md`
  - META-REVIEW mode: `{output_root}summaries/_meta-<document-name>-<model>-<YYYY-MM-DD>.md`
  - Default `output_root`: `reviews/`
- **No-overwrite safety:** If file exists, uses suffix `-01.md`, `-02.md`, etc.
- Detects ambiguous phrases that require human judgment
- Verifies success criteria are agent-verifiable

## Design Priority Hierarchy

Reviews evaluate plans against the priority order defined in `000-global-core.md`:

1. **Priority 1 (CRITICAL):** Agent Understanding and Execution Reliability
2. **Priority 2 (HIGH):** Rule Discovery Efficacy and Determinism
3. **Priority 3 (HIGH):** Context Window and Token Utilization Efficiency
4. **Priority 4 (LOW):** Human Developer Maintainability

**Scoring Impact (Priority 1 Gate):**
- ≥10 blocking issues: Overall score capped at 60/100 (NEEDS_WORK)
- ≥20 blocking issues: Overall score capped at 40/100 (POOR_PLAN)

## Quick Start

### 1. Load the skill

```text
Load skills/plan-reviewer/SKILL.md
```

### 2. Request a review

**FULL mode (single plan):**

```text
Use the plan-reviewer skill.

target_file: plans/IMPROVE_RULE_LOADING.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

**With execution timing:**

```text
Use the plan-reviewer skill.

target_file: plans/IMPROVE_RULE_LOADING.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
timing_enabled: true
```

**With custom output directory:**

```text
Use the plan-reviewer skill.

target_file: plans/IMPROVE_RULE_LOADING.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
output_root: quarterly-audit/
```

**COMPARISON mode (multiple plans):**

```text
Use the plan-reviewer skill.

target_files: plans/auth-plan-claude.md, plans/auth-plan-gpt.md
task_description: Implement OAuth2 authentication
review_date: 2026-01-06
review_mode: COMPARISON
model: claude-sonnet-45
```

**META-REVIEW mode (review consistency):**

```text
Use the plan-reviewer skill.

review_files: reviews/plan-X-sonnet-2026-01-06.md, reviews/plan-X-gpt-2026-01-06.md
original_document: plans/X.md
review_date: 2026-01-06
review_mode: META-REVIEW
model: claude-sonnet-45
```

**DELTA mode (track issue resolution):**

```text
Use the plan-reviewer skill.

target_file: plans/IMPROVE_RULE_LOADING.md
baseline_review: reviews/plan-reviews/IMPROVE_RULE_LOADING-claude-sonnet-45-2026-01-01.md
review_date: 2026-01-06
review_mode: DELTA
model: claude-sonnet-45
```

### 3. Output location

The skill writes reviews to the output directory:

- Default FULL: `reviews/plan-reviews/IMPROVE_RULE_LOADING-claude-sonnet-45-2026-01-06.md`
- Default COMPARISON: `reviews/summaries/_comparison-<plan-set-id>-claude-sonnet-45-2026-01-06.md`
- Default META-REVIEW: `reviews/summaries/_meta-IMPROVE_RULE_LOADING-2026-01-06.md`
- Default DELTA: `reviews/plan-reviews/IMPROVE_RULE_LOADING-delta-2026-01-01-to-2026-01-06-claude-sonnet-45.md`
- With `output_root: quarterly-audit/`: `quarterly-audit/plan-reviews/...`

If the file already exists, suffixes are appended: `-01.md`, `-02.md`, etc.

When `timing_enabled: true`, the output includes a Timing Metadata section with duration, token usage, and cost estimation.

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

### DELTA Mode (Track Issue Resolution)

Use after applying fixes from a prior review. Compares current plan against baseline review to track issue resolution and detect regressions.

```text
review_mode: DELTA
```

**Best for:**
- Tracking improvement progress after fixes
- Verifying issues from prior review are resolved
- Understanding score changes between versions

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
- Can agent verify completion programmatically? (Agent-verifiable criteria can be checked via exit codes, file existence, etc. without human judgment)
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
- **90-100 (EXCELLENT_PLAN):** Ready for execution
- **80-89 (GOOD_PLAN):** Minor refinements needed
- **60-79 (NEEDS_WORK):** Significant refinement required
- **40-59 (POOR_PLAN):** Not executable, major revision needed
- **<40 (INADEQUATE_PLAN):** Rewrite from scratch

**Critical Dimension Overrides:**
- Executability ≤4/10 → Minimum NEEDS_WORK
- Completeness ≤4/10 → Minimum NEEDS_WORK
- Success Criteria ≤4/10 → Minimum NEEDS_WORK
- 2+ critical dimensions ≤4/10 → POOR_PLAN

**Blocking Issue Caps:**
- ≥10 blocking issues: Score capped at 60/100 (NEEDS_WORK)
- ≥20 blocking issues: Score capped at 40/100 (POOR_PLAN)

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
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

Validate a plan before handing it to an autonomous agent.

### Choosing Best Plan

```text
Use the plan-reviewer skill.

target_files: plans/approach-a.md, plans/approach-b.md, plans/approach-c.md
task_description: Migrate database to new schema
review_date: 2026-01-06
review_mode: COMPARISON
model: claude-sonnet-45
```

Compare multiple approaches and get a recommendation.

### Validating Review Quality

```text
Use the plan-reviewer skill.

review_files: reviews/plan-X-claude-2026-01-06.md, reviews/plan-X-gpt-2026-01-06.md
original_document: plans/X.md
review_date: 2026-01-06
review_mode: META-REVIEW
model: claude-sonnet-45
```

After multiple models review the same plan, analyze consistency.

### Tracking Plan Improvements

```text
Use the plan-reviewer skill.

target_file: plans/X.md
baseline_review: reviews/plan-reviews/X-claude-sonnet-45-2026-01-01.md
review_date: 2026-01-06
review_mode: DELTA
model: claude-sonnet-45
```

After applying fixes from a prior review, track issue resolution.

## FAQ

### Q: What happens if the output file already exists?

**A:** The skill uses no-overwrite safety. It appends suffixes (`-01.md`, `-02.md`, etc.) to avoid overwriting existing reviews.

### Q: What should I pass for `model`?

**A:** Prefer a slug like `claude-sonnet-45`. If you provide a raw model name, the skill normalizes it to a slug before writing the file.

### Q: Can I customize the output directory?

**A:** Yes, use the `output_root` parameter:
```text
output_root: quarterly-audit/
```
This writes reviews to `quarterly-audit/plan-reviews/` instead of `reviews/plan-reviews/`. The skill auto-creates directories and normalizes trailing slashes. Relative paths including `../` are supported.

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

**A:** Depends on plan size and model:
- Small plan (<100 lines): 30-60 seconds
- Medium plan (100-500 lines): 60-120 seconds
- Large plan (>500 lines): 2-5 minutes

**Timing thresholds** (with `timing_enabled: true`):
- Error threshold: <15 seconds (possible shortcut detected)
- Warning threshold: <30 seconds (unusually fast)
- Long threshold: >720 seconds (possible issue)

### Q: Where does the rubric come from?

**A:** The skill uses rubric files in `skills/plan-reviewer/rubrics/` (executability.md, completeness.md, success-criteria.md, scope.md, dependencies.md, decomposition.md, context.md, risk-awareness.md) plus `_overlap-resolution.md` as the rubric. Each rubric includes a Mandatory Worksheet template and Non-Issues section for deterministic scoring.

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
- **Skill README:** `skills/plan-reviewer/README.md`
- **Workflow guides:** `skills/plan-reviewer/workflows/*.md` (includes `delta-review.md` for DELTA mode)
- **Examples:** `skills/plan-reviewer/examples/*.md`
- **Validation tests:** `skills/plan-reviewer/tests/*.md`
- **Timing system:** `skills/skill-timing/README.md`

