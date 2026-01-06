---
name: plan-reviewer
description: Review LLM-generated plans for autonomous agent executability. Supports FULL (single plan), COMPARISON (multiple plans ranked), and META-REVIEW (review consistency analysis) modes. Triggers on keywords like "review plan", "compare plans", "plan quality", "meta-review", "plan executability".
version: 1.2.0
---

# Plan Reviewer

## Overview

Review LLM-generated plans for autonomous agent executability using an 8-dimension rubric optimized for Priority 1 compliance (Agent Understanding).

### Design Priority Hierarchy

Evaluates plans against the priority order from `000-global-core.md`:
1. **Priority 1:** Agent Understanding and Execution Reliability (CRITICAL)
2. **Priority 2:** Token and Context Window Efficiency (HIGH)
3. **Priority 3:** Human Readability (TERTIARY)

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

**Mode-specific:**
- **FULL mode**: `target_file` - Single plan file path
- **COMPARISON mode**: `target_files` - List of plan file paths
- **META-REVIEW mode**: `review_files` - List of review file paths

### Output

**FULL mode:** `reviews/<plan-name>-<model>-<date>.md`

**COMPARISON mode:** `reviews/_comparison-<plan-set-id>-<model>-<date>.md` with ranked plans and winner declaration

**META-REVIEW mode:** `reviews/_meta-<doc-name>-<date>.md` with consistency analysis

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

**Total: 100 points weighted across 8 dimensions:**

| Dimension | Raw | Weight | Points | Category |
|-----------|-----|--------|--------|----------|
| Executability | X/5 | ×4 | Y/20 | Critical |
| Completeness | X/5 | ×4 | Y/20 | Critical |
| Success Criteria | X/5 | ×4 | Y/20 | Critical |
| Scope | X/5 | ×3 | Y/15 | Critical |
| Dependencies | X/5 | ×2 | Y/10 | Standard |
| Decomposition | X/5 | ×1 | Y/5 | Standard |
| Context | X/5 | ×1 | Y/5 | Standard |
| Risk Awareness | X/5 | ×1 | Y/5 | Standard |

**Critical dimensions:** 75 points (agent must execute without human intervention)
**Standard dimensions:** 25 points (important but recoverable)

### Dimension Summaries

**1. Executability (20 points) - Can agent execute each step?**
- Measures: Explicit commands, ambiguous phrases, undefined thresholds
- Key gate: >15 ambiguous phrases caps at 1/5

**2. Completeness (20 points) - Are all steps covered?**
- Measures: Setup, validation, cleanup, error recovery
- Key gate: No error recovery caps at 2/5

**3. Success Criteria (20 points) - Are completion signals clear?**
- Measures: Verifiable outputs, measurable criteria, agent-testable
- Key gate: <50% tasks with criteria caps at 2/5

**4. Scope (15 points) - Is work bounded?**
- Measures: Scope definition, exclusions, termination conditions
- Key gate: Unbounded scope caps at 2/5

**5. Dependencies (10 points) - Are prerequisites clear?**
- Measures: Tool/package requirements, ordering, access needs

**6. Decomposition (5 points) - Are tasks right-sized?**
- Measures: Task granularity, parallelizable steps

**7. Context (5 points) - Does plan explain why?**
- Measures: Rationale provided, context preserved

**8. Risk Awareness (5 points) - Are risks documented?**
- Measures: Failure scenarios, mitigation strategies

**See:** `workflows/review-execution.md` for complete rubric details, scoring criteria, and calibration examples.

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

**See:** `workflows/review-execution.md` section "Agent Execution Test"

### Verdict Thresholds

| Score | Verdict | Meaning |
|-------|---------|---------|
| 90-100 | EXCELLENT_PLAN | Ready for execution |
| 80-89 | GOOD_PLAN | Minor refinements needed |
| 60-79 | NEEDS_WORK | Significant refinement required |
| 40-59 | POOR_PLAN | Not executable, major revision |
| <40 | INADEQUATE_PLAN | Rewrite from scratch |

**Critical dimension overrides:**
- Executability ≤2/5 → Minimum NEEDS_WORK
- Completeness ≤2/5 → Minimum NEEDS_WORK
- Success Criteria ≤2/5 → Minimum NEEDS_WORK
- 2+ critical dimensions ≤2/5 → POOR_PLAN

## Workflow

### 1. Input Validation

Validate review_date, review_mode, model, target files.

**See:** `workflows/input-validation.md`

### 2. Model Slugging

Convert model name to lowercase-hyphenated slug for filenames.

**See:** `workflows/model-slugging.md`

### 3. Review Execution

Execute complete review per rubric. This is the core workflow.

**FULL mode:** Score 8 dimensions, generate recommendations
**COMPARISON mode:** Review each plan, rank by score, declare winner
**META-REVIEW mode:** Analyze score variance, identify agreement/disagreement

**See:** `workflows/review-execution.md` (detailed rubric, scoring criteria, mode-specific instructions)

### 4. File Write

Write review to `reviews/` with appropriate filename per mode.

**See:** `workflows/file-write.md`

### 5. Error Handling

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
- `rules/002f-claude-code-skills.md` - Skill best practices
