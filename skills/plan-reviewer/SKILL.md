---
name: plan-reviewer
description: Review LLM-generated plans for autonomous agent executability using 8-dimension rubric. Triggers: "review plan", "compare plans", "plan quality", "meta-review".
version: 2.5.0
---

# Plan Reviewer

## Quick Start

```text
target_file: plans/my-plan.md
review_mode: FULL
```
Output: `reviews/plan-reviews/<plan-name>-<model>-<date>.md`

## Purpose

Review LLM-generated plans for autonomous agent executability using an 8-dimension rubric optimized for Priority 1 compliance (Agent Understanding).

Plans are scored on whether autonomous agents can execute them without judgment calls or clarification requests.

## Use this skill when

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
- `timing_enabled`: Enable execution timing (default: `true` — v2.5.0 universal default; set `false` to opt out with `not-requested` row)
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
4. **[Optional] Start timing** if `timing_enabled: true` (see **Timing** section below for full Quick Reference)
4a. **(If `timing_enabled: true`) Bracket EACH of the 8 dimensions with a checkpoint pair.**

    Required checkpoint names (exact spelling; `dim_<name>_start` / `dim_<name>_end`):
    - dim_executability_start / dim_executability_end
    - dim_completeness_start / dim_completeness_end
    - dim_success_criteria_start / dim_success_criteria_end
    - dim_scope_start / dim_scope_end
    - dim_dependencies_start / dim_dependencies_end
    - dim_decomposition_start / dim_decomposition_end
    - dim_context_start / dim_context_end
    - dim_risk_awareness_start / dim_risk_awareness_end

    On `timing-end`, pass `--auto-dimension-timings` (preferred) or assemble
    `--dimension-timings` JSON manually. FAILURE MODE: the Per-Dimension Timing
    section will be silently absent from the review; the post-write **Gate 7**
    in `workflows/file-write.md` will REJECT the review.

5. **Execute review** per `execution_mode`:
   - `parallel`: 8 sub-agents → `workflows/parallel-execution.md`
   - `sequential`: Single agent → `workflows/review-execution.md`
6. **[Optional] End timing** and embed metadata. Include `--auto-dimension-timings` when `timing_enabled: true`.
7. **Write output** → `workflows/file-write.md` (Gate 7 enforces Per-Dimension Timing presence)
8. **Handle errors** → `workflows/error-handling.md`

**CRITICAL:** Default to `parallel` execution. Do NOT silently use sequential.

## Timing (When `timing_enabled: true`)

**You capture, skill-timer validates and formats.** Passing no dimension data
results in a silently-omitted Per-Dimension Timing section unless Gate 7
catches it. Do not rely on skill-timer to "handle all" capture — it only
validates and formats what you provide.

### Quick Reference (copy-paste)

```bash
PYTHON=$(bash skills/skill-timer/scripts/find_python.sh)

# Start
$PYTHON skills/skill-timer/scripts/skill_timer.py start \
    --skill plan-reviewer --target plans/my-plan.md --model {{model}} --mode FULL
# → capture run_id from stdout as {{_timing_run_id}}

$PYTHON skills/skill-timer/scripts/skill_timer.py checkpoint \
    --run-id {{_timing_run_id}} --name skill_loaded

# For EACH of the 8 dimensions (executability, completeness, success_criteria,
# scope, dependencies, decomposition, context, risk_awareness):
$PYTHON skills/skill-timer/scripts/skill_timer.py checkpoint \
    --run-id {{_timing_run_id}} --name dim_{name}_start
# ... score the dimension ...
$PYTHON skills/skill-timer/scripts/skill_timer.py checkpoint \
    --run-id {{_timing_run_id}} --name dim_{name}_end

$PYTHON skills/skill-timer/scripts/skill_timer.py checkpoint \
    --run-id {{_timing_run_id}} --name review_complete

# End — --auto-dimension-timings derives dimension_timings from dim_*_start/end pairs
$PYTHON skills/skill-timer/scripts/skill_timer.py end \
    --run-id {{_timing_run_id}} \
    --output-file reviews/plan-reviews/{{plan}}-{{model}}-{{date}}.md \
    --skill plan-reviewer --format markdown --auto-dimension-timings
```

**Verify:** `end` stdout must contain `PER_DIMENSION_STATUS=present` or
`PER_DIMENSION_STATUS=derived`. `missing` triggers Gate 7 rejection.

### Common Timing Mistakes (Anti-Patterns)

1. **Fabricated epochs — DO NOT invent timestamps.**
   - WRONG: Hand-writing `--dimension-timings '[{"dimension":"scope","start_epoch":1700000000,...}]'` with guessed numbers.
   - Correct: Emit real `checkpoint` calls and pass `--auto-dimension-timings`.

2. **Missing required fields in manual `--dimension-timings`.**
   - WRONG: `[{"dimension":"scope","duration_seconds":1.2}]` (no epochs, no mode).
   - Correct: See `skills/skill-timer/schemas/` for required fields (`dimension`, `start_epoch`, `end_epoch`, `duration_seconds`, `mode`).

3. **Ignoring `VALIDATION ERROR` from skill-timer.**
   - WRONG: Seeing `VALIDATION ERROR: dimension_timings rejected` and proceeding anyway.
   - Correct: Treat as a hard failure; re-run `end` with corrected data.

4. **Omitting `--auto-dimension-timings` / `--dimension-timings` entirely.**
   - WRONG: Capturing `dim_*_start/end` checkpoints but calling `end` without either flag.
   - Correct: Always pass `--auto-dimension-timings` when `timing_enabled: true`.

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

## Gate 8 — Per-Dimension Timing rejection (skill-timer v2.0.0+)

After `skill_timer.py end` returns, check the run-level `status` field:

- If `status ∈ {dimension_invalid, instrumentation_failed}`: **DO NOT
  publish** the "Per-Dimension Timing" markdown table. Instead emit:

  ```
  > **Per-Dimension Timing rejected**
  >
  > Per-dimension timing data was rejected by skill-timer v2.0.0 due to
  > alerts: <comma-separated alert types>. See
  > `reviews/.timing-data/skill-timer-{run_id}-complete.json` for details.
  ```

- If `status ∈ {completed, warning}`: publish the table as before.

This gate is mirrored in rule-reviewer, doc-reviewer, and bulk-rule-reviewer
SKILL.md files.

## Examples

- `examples/full-review.md` - FULL mode walkthrough
- `examples/comparison-review.md` - COMPARISON mode
- `examples/meta-review.md` - META-REVIEW mode
- `examples/edge-cases.md` - Edge case handling

## Related Skills

- **rule-creator** - Create rules (similar executability criteria)
- **doc-reviewer** - Review documentation (complementary)
- **skill-timer** (≥ v1.5.0) - Provides `--auto-dimension-timings` used by Step 4a and Gate 7.

## References

- `rules/000-global-core.md` - Priority hierarchy definition
- `rules/002h-claude-code-skills.md` - Skill best practices

## Version History

See `CHANGELOG.md`.
