---
name: plan-reviewer
description: Review LLM-generated plans for autonomous agent executability. Supports FULL (single plan), COMPARISON (multiple plans ranked), and META-REVIEW (review consistency analysis) modes. Triggers on keywords like "review plan", "compare plans", "plan quality", "meta-review", "plan executability".
version: 2.1.0
---

# Plan Reviewer

## Overview

Review LLM-generated plans for autonomous agent executability using an 8-dimension rubric optimized for Priority 1 compliance (Agent Understanding).

### Design Priority Hierarchy

Evaluates plans against the priority order from `000-global-core.md`:
1. **Priority 1 (CRITICAL):** Agent Understanding and Execution Reliability
2. **Priority 2 (HIGH):** Rule Discovery Efficacy and Determinism
3. **Priority 3 (HIGH):** Context Window and Token Utilization Efficiency
4. **Priority 4 (LOW):** Human Developer Maintainability

Plans are scored on whether autonomous agents can execute them without judgment calls or clarification requests.

### When to Use

- Review a plan file for agent executability
- Compare multiple plans for the same task (choose winner)
- Conduct meta-review to analyze consistency across reviews
- Verify plan meets Priority 1 compliance before execution

### Inputs

**Required:**
- **review_date**: `YYYY-MM-DD`
- **review_mode**: `FULL` | `COMPARISON` | `META-REVIEW`
- **model**: Model slug (e.g., `claude-sonnet-45`)

**Mode-specific (REQUIRED for each mode):**
- **FULL mode**: `target_file` - Single plan file path. If missing: STOP, report error `Missing required input: target_file for FULL mode`
- **COMPARISON mode**: `target_files` - List of plan file paths. If missing: STOP, report error `Missing required input: target_files for COMPARISON mode`
- **META-REVIEW mode**: `review_files` - List of review file paths. If missing: STOP, report error `Missing required input: review_files for META-REVIEW mode`

**Optional:**
- **output_root**: Root directory for output files (default: `reviews/`). Subdirectories `plan-reviews/` or `summaries/` appended automatically. Supports relative paths including `../`.
- **overwrite**: `true` | `false` (default: `false`) - If true, overwrite existing review file. If false, use sequential numbering (-01, -02, etc.)
- **timing_enabled**: `true` | `false` (default: `false`) - Enable execution timing

### Output

**FULL mode:** `{output_root}/plan-reviews/<plan-name>-<model>-<date>.md`

**COMPARISON mode:** `{output_root}/summaries/_comparison-<plan-set-id>-<model>-<date>.md` with ranked plans and winner declaration

**META-REVIEW mode:** `{output_root}/summaries/_meta-<doc-name>-<date>.md` with consistency analysis

(Default `output_root: reviews/`. With `output_root: mytest/` → `mytest/plan-reviews/...`)

## Review Modes

**FULL Mode (default):**
- Comprehensive single-plan review
- All 8 dimensions evaluated
- When: Default; evaluating one plan

**COMPARISON Mode:**
- Rank multiple plans for same task
- Declare winner with justification
- When: Choosing between competing plans

**META-REVIEW Mode:**
- Analyze review consistency across LLMs
- Identify score variance and agreement
- When: After multiple LLMs review same document

## Review Rubric

### Scoring Formula

**Raw Score Range:** 0-10 per dimension
**Formula:** Raw (0-10) × (Weight / 2) = Points

**Total: 100 points weighted across 8 dimensions:**

**Critical Dimensions (75 points - agent must execute without human intervention):**
- **Executability** - Raw: X/10, Weight: 4, Points: Y/20
- **Completeness** - Raw: X/10, Weight: 4, Points: Y/20
- **Success Criteria** - Raw: X/10, Weight: 4, Points: Y/20
- **Scope** - Raw: X/10, Weight: 3, Points: Y/15

**Standard Dimensions (25 points - important but recoverable):**
- **Dependencies** - Raw: X/10, Weight: 2, Points: Y/10
- **Decomposition** - Raw: X/10, Weight: 1, Points: Y/5
- **Context** - Raw: X/10, Weight: 1, Points: Y/5
- **Risk Awareness** - Raw: X/10, Weight: 1, Points: Y/5

### Dimension Summaries

**1. Executability (20 points) - Can agent execute each step?**
- Measures: Explicit commands, ambiguous phrases, undefined thresholds
- Key gate: >15 ambiguous phrases caps at 2/10

**2. Completeness (20 points) - Are all steps covered?**
- Measures: Setup, validation, cleanup, error recovery
- Key gate: No error recovery caps at 4/10

**3. Success Criteria (20 points) - Are completion signals clear?**
- Measures: Verifiable outputs, measurable criteria, agent-testable
- Key gate: <50% tasks with criteria caps at 4/10 (Count: Tasks with verifiable success criteria / Total tasks in plan)

**4. Scope (15 points) - Is work bounded?**
- Measures: Scope definition, exclusions, termination conditions
- Key gate: Unbounded scope caps at 4/10

**5. Dependencies (10 points) - Are prerequisites clear?**
- Measures: Tool/package requirements, ordering, access needs

**6. Decomposition (5 points) - Are tasks right-sized?**
- Measures: Task granularity, parallelizable steps

**7. Context (5 points) - Does plan explain why?**
- Measures: Rationale provided, context preserved

**8. Risk Awareness (5 points) - Are risks documented?**
- Measures: Failure scenarios, mitigation strategies

**Detailed rubrics:** See `rubrics/[dimension].md` for complete scoring criteria:
- `rubrics/executability.md` - Ambiguous phrases, explicit commands
- `rubrics/completeness.md` - Setup, validation, error recovery, cleanup
- `rubrics/success-criteria.md` - Measurable, agent-testable criteria
- `rubrics/scope.md` - Boundaries, termination conditions
- `rubrics/dependencies.md` - Prerequisites, ordering, access
- `rubrics/decomposition.md` - Task sizing, parallelization
- `rubrics/context.md` - Rationale, assumptions, tradeoffs
- `rubrics/risk-awareness.md` - Failure scenarios, mitigations, rollback

**Progressive disclosure:** Read each rubric only when scoring that dimension.

### Agent Execution Test (Pre-Scoring Gate)

Before scoring, answer: **"Can an autonomous agent execute this plan end-to-end without asking for clarification?"**

Count blocking issues:
1. Ambiguous phrases ("consider", "if appropriate", "as needed")
2. Implicit commands (described not specified)
3. Missing branches (no explicit else/default/error handling)
4. Undefined thresholds ("large", "significant", "appropriate")

**Impact:**
- Blocking issues ≥10: Max score = 60/100 (NEEDS_REFINEMENT)
- Blocking issues ≥20: Max score = 40/100 (NOT_EXECUTABLE)

**See:** `rubrics/executability.md` for blocking issue criteria

### Verdict Thresholds

**Score Ranges:**
- **90-100** - EXCELLENT_PLAN - Ready for execution
- **80-89** - GOOD_PLAN - Minor refinements needed
- **60-79** - NEEDS_WORK - Significant refinement required
- **40-59** - POOR_PLAN - Not executable, major revision
- **<40** - INADEQUATE_PLAN - Rewrite from scratch

**Critical dimension overrides:**
- Executability ≤4/10 → Minimum NEEDS_WORK
- Completeness ≤4/10 → Minimum NEEDS_WORK
- Success Criteria ≤4/10 → Minimum NEEDS_WORK
- 2+ critical dimensions ≤4/10 → POOR_PLAN

## Workflow

### 1. Input Validation

Validate review_date, review_mode, model, target files.

**See:** `workflows/input-validation.md`

### 2. Model Slugging

Convert model name to lowercase-hyphenated slug for filenames.

**See:** `workflows/model-slugging.md`

### 3. [OPTIONAL] Timing Start

**When:** Only if `timing_enabled: true` in inputs  
**MODE:** Safe in PLAN mode

**See:** `../skill-timing/workflows/timing-start.md`

**Action:** Capture `run_id` in working memory for later use.

### 4. [OPTIONAL] Checkpoint: skill_loaded

**When:** Only if timing was started  
**Checkpoint name:** `skill_loaded`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### 5. Review Execution

Execute complete review per rubric. This is the core workflow.

**FULL mode:** Score 8 dimensions, generate recommendations
**COMPARISON mode:** Review each plan, rank by score, declare winner
**META-REVIEW mode:** Analyze score variance, identify agreement/disagreement

**See:** `workflows/review-execution.md` (detailed rubric, scoring criteria, mode-specific instructions)

### 6. [OPTIONAL] Checkpoint: review_complete

**When:** Only if timing was started  
**Checkpoint name:** `review_complete`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### 7. [OPTIONAL] Timing End (Compute)

**When:** Only if timing was started  
**MODE:** Safe in PLAN mode (outputs to STDOUT only)

**See:** `../skill-timing/workflows/timing-end.md` (Step 1)

**Action:** Capture STDOUT output for metadata embedding.

### 8. [MODE TRANSITION: PLAN → ACT]

Request user ACT authorization before file modifications.

### 9. File Write

Write review to `reviews/plan-reviews/` (FULL) or `reviews/summaries/` (COMPARISON/META-REVIEW) with appropriate filename.

**See:** `workflows/file-write.md`

### 10. [OPTIONAL] Timing End (Embed)

**When:** Only if timing was started  
**MODE:** Requires ACT mode (appends metadata to file)

**See:** `../skill-timing/workflows/timing-end.md` (Step 2)

**Action:** Parse STDOUT from step 7, append timing metadata section to output file.

### 11. Error Handling

Handle validation failures, file write errors, mode-specific issues.

**See:** `workflows/error-handling.md`

## COMPARISON Mode Details

Reviews each plan independently, ranks by score, declares winner with justification. Provides integration recommendations combining best elements from all plans.

**See:** `examples/comparison-review.md` for complete walkthrough.

## META-REVIEW Mode Details

Analyzes consistency across multiple reviews of same plan. Calculates score variance, identifies agreement/disagreement areas, analyzes verdict consensus.

**See:** `examples/meta-review.md` for complete walkthrough.

## Hard Requirements

- Do NOT ask user to manually copy/paste review
- Do NOT print entire review if file writing succeeds
- Count blocking issues accurately (Agent Execution Test)
- Apply weighted scoring formula correctly
- Include specific recommendations with examples
- If file write fails: Print `OUTPUT_FILE: <path>` then full review

## Examples

- `examples/full-review.md` - Complete FULL mode walkthrough
- `examples/comparison-review.md` - COMPARISON mode with 3 plans
- `examples/meta-review.md` - META-REVIEW analyzing consistency
- `examples/edge-cases.md` - Handling unusual scenarios

## Related Skills

- **rule-creator** - Create rules (plans use similar executability criteria)
- **doc-reviewer** - Review documentation (complementary)

## References

### Rules

- `rules/000-global-core.md` - Priority hierarchy definition
- `rules/002h-claude-code-skills.md` - Skill best practices
