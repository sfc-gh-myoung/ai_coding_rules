---
name: plan-reviewer
description: Review LLM-generated plans for autonomous agent executability using 8-dimension rubric. Triggers: "review plan", "compare plans", "plan quality", "meta-review".
version: 2.3.0
---

# Plan Reviewer

## Quick Start

```text
target_file: plans/my-plan.md
review_mode: FULL
```
Output: `reviews/plan-reviews/<plan-name>-<model>-<date>.md`

## Overview

Review LLM-generated plans for autonomous agent executability using an 8-dimension rubric optimized for Priority 1 compliance (Agent Understanding).

Plans are scored on whether autonomous agents can execute them without judgment calls or clarification requests.

### When to Use

- Review a plan file for agent executability
- Compare multiple plans for the same task (choose winner)
- Conduct meta-review to analyze consistency across reviews
- Verify plan meets Priority 1 compliance before execution

### What NOT to Use This For

- **General documentation review** → Use `doc-reviewer` instead
- **Rule file validation** → Use `rule-reviewer` instead
- **Code review** → Use standard code review tools
- **Task execution** → This skill evaluates plans, it doesn't execute them

## Inputs

**Required:**
- **review_mode**: `FULL` | `COMPARISON` | `META-REVIEW` | `DELTA`
- **target_file(s)**: Path(s) to plan file(s) - varies by mode

**Mode-specific:**
| Mode | Required Input | Description |
|------|---------------|-------------|
| FULL | `target_file` | Single plan file path |
| COMPARISON | `target_files` | List of plan file paths |
| META-REVIEW | `review_files` | List of review file paths |
| DELTA | `target_file` + `baseline_review` | Current plan + prior review |

**Optional:**
- `output_root`: Output directory (default: `reviews/`)
- `execution_mode`: `parallel` (default, 8 sub-agents) or `sequential`
- `timing_enabled`: Enable execution timing (default: `false`)
- `overwrite`: Overwrite existing files (default: `false`)

## Review Modes

| Mode | Purpose | Output Location |
|------|---------|-----------------|
| **FULL** | Comprehensive single-plan review | `{root}/plan-reviews/<name>-<model>-<date>.md` |
| **COMPARISON** | Rank multiple plans, declare winner | `{root}/summaries/_comparison-*.md` |
| **META-REVIEW** | Analyze consistency across reviews | `{root}/summaries/_meta-*.md` |
| **DELTA** | Track issue resolution from baseline | `{root}/plan-reviews/<name>-delta-*.md` |

**See:** `examples/` for complete walkthroughs of each mode.

## Review Rubric

**See:** `rubrics/SCORING.md` for complete scoring formula and verdict thresholds.

**Quick Reference:**
- **Critical (75 pts):** Executability (20), Completeness (20), Success Criteria (20), Scope (15)
- **Standard (25 pts):** Dependencies (10), Decomposition (5), Context (5), Risk Awareness (5)
- **Verdicts:** 90-100 EXCELLENT, 80-89 GOOD, 60-79 NEEDS_WORK, 40-59 POOR, <40 INADEQUATE

**Detailed rubrics:** `rubrics/[dimension].md`

## Workflow

1. **Validate inputs** → `workflows/input-validation.md`
2. **Collect ALL parameters** (use `ask_user_question`) → `workflows/parameter-collection.md`
   - **MANDATORY:** Prompt for ALL parameters (required AND optional) in a single question batch
   - Do NOT silently apply defaults for optional parameters
   - User must explicitly confirm each setting
3. **Slug model name** → `workflows/model-slugging.md`
4. **[Optional] Start timing** if `timing_enabled: true`
5. **Execute review** per `execution_mode`:
   - `parallel`: 8 sub-agents → `workflows/parallel-execution.md`
   - `sequential`: Single agent → `workflows/review-execution.md`
6. **[Optional] End timing** and embed metadata
7. **Write output** → `workflows/file-write.md`
8. **Handle errors** → `workflows/error-handling.md`

**CRITICAL:** Default to `parallel` execution. Do NOT silently use sequential.

## Determinism

**See:** `workflows/determinism.md` for complete determinism requirements.

**Key rules:**
- Batch load ALL 9 rubric files BEFORE reading plan
- Create ALL 8 worksheets BEFORE scoring
- Read plan line 1 to END (no skipping)
- Include worksheets in output for audit trail
- Expected variance: ±2 points max

## Parallel Execution

**See:** `workflows/parallel-specs.md` for timeout handling, aggregation schema, edge cases, and rollback procedures.

## Hard Requirements

- Do NOT ask user to copy/paste review
- Do NOT print entire review if file write succeeds
- Count blocking issues accurately
- Apply weighted scoring formula correctly
- If file write fails: Print `OUTPUT_FILE: <path>` then full review

## Examples

- `examples/full-review.md` - FULL mode walkthrough
- `examples/comparison-review.md` - COMPARISON mode
- `examples/meta-review.md` - META-REVIEW mode
- `examples/edge-cases.md` - Edge case handling

## Related Skills

- **rule-creator** - Create rules (similar executability criteria)
- **doc-reviewer** - Review documentation (complementary)

## References

- `rules/000-global-core.md` - Priority hierarchy definition
- `rules/002h-claude-code-skills.md` - Skill best practices
