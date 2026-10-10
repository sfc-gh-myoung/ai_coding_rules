# Using the Rule Reviewer Skill

**Last Updated:** 2026-08-18

The Rule Reviewer Skill evaluates rule files to ensure autonomous agents can execute them successfully. It scores rules across 6 dimensions using a weighted scoring system optimized for agent executability.

## Examples

### Minimal Required Example

```text
Use the rule-reviewer skill.

target_file: rules/200-python-core.md  # Required: rule to evaluate
review_date: 2026-03-27              # Required: date stamp for output
review_mode: FULL                    # Required: review depth
model: claude-sonnet-45              # Required: model slug for naming
```

### FULL With All Optional Settings

```text
Use the rule-reviewer skill.

target_file: rules/200-python-core.md  # Required
review_date: 2026-03-27              # Required
review_mode: FULL                    # Required
model: claude-sonnet-45              # Required
output_root: quarterly-audit/        # Optional (default: reviews/): custom output directory
execution_mode: sequential           # Optional (default: parallel): sequential is also valid for production
timing_enabled: true                 # Optional (default: true as of v2.9.0): adds timing metadata
overwrite: true                      # Optional (default: false): replaces existing file
```

### FOCUSED Mode Example

```text
Use the rule-reviewer skill.

target_file: rules/200-python-core.md  # Required
review_mode: FOCUSED                 # Required: Actionability + Completeness only
review_date: 2026-03-27              # Required
model: claude-sonnet-45              # Required
```

### STALENESS Mode Example

```text
Use the rule-reviewer skill.

target_file: rules/200-python-core.md  # Required
review_mode: STALENESS               # Required: Staleness dimension only
review_date: 2026-03-27              # Required
model: claude-sonnet-45              # Required
```


## Review Modes

| Mode | Purpose | When to Use |
|------|---------|-------------|
| **FULL** | Full 6-dimension review | Validate rules before deployment |
| **FOCUSED** | Actionability + Completeness only | Quick check on the two scored dimensions |
| **STALENESS** | Check for outdated content | Periodic currency audits |

### FULL Mode

Scores all 6 dimensions for a complete quality assessment.

```text
target_file: rules/200-python-core.md
review_mode: FULL
```

### FOCUSED Mode

Evaluates only Actionability and Completeness (45 points max). Use for rapid validation.

```text
target_file: rules/200-python-core.md
review_mode: FOCUSED
```

### STALENESS Mode

Evaluates only the Staleness dimension (10 points max). Use for detecting outdated patterns.

```text
target_file: rules/200-python-core.md
review_mode: STALENESS
```


## Understanding Your Results

### Verdicts

| Score | Verdict | Action |
|-------|---------|--------|
| 90-100 | **EXECUTABLE** | Production-ready |
| 80-89 | **EXECUTABLE_WITH_REFINEMENTS** | Good, minor fixes needed |
| 60-79 | **NEEDS_REFINEMENT** | Significant refinement required |
| <60 | **NOT_EXECUTABLE** | Major revision needed |

**Critical dimension override:** If both Actionability ≤4/10 AND Completeness ≤4/10 → NOT_EXECUTABLE regardless of total score.

### Scoring Dimensions

Rules are scored across 6 dimensions with weighted points:

| Dimension | Weight | Max Points | Key Question |
|-----------|--------|------------|--------------|
| Actionability | 3.0 | 30 | Can agents execute without judgment? |
| Rule Size | 2.5 | 25 | Within the 250-line limit? (deterministic) |
| Parsability | 1.5 | 15 | Is metadata/schema valid? |
| Completeness | 1.5 | 15 | Are all scenarios covered? |
| Consistency | 1.0 | 10 | Is internal alignment correct? |
| Cross-Agent Consistency | 0.5 | 5 | Works across all agents? |

**Informational Only (Not Scored):**
- **Token Efficiency**: Merged into Rule Size; findings in recommendations
- **Staleness**: Flagged in recommendations; not scored

**Scoring Formula:** `Raw (0-10) × Weight = Points`

**Example (Actionability):**
- Raw score: 8/10
- Weight: 3.0
- Points: 8 × 3.0 = **24 points**

### Rule Size Flags

The Rule Size scale matches the project limit: rules should be no more than 250 lines, and `ai-rules validate` reports a HIGH finding for any rule over 250 lines (see [CONTRIBUTING.md → Content Guidelines](../CONTRIBUTING.md#content-guidelines)). A rule over 250 lines scores at most 5/10 on Rule Size, so it cannot receive full Rule Size points or an EXECUTABLE verdict.

The Rule Size dimension includes deployment flags:

| Line Count | Flag | Action |
|------------|------|--------|
| ≤250 | None | Optimal or at limit |
| 251-275 | `SPLIT_RECOMMENDED` | Review for split |
| 276-300 | `SPLIT_REQUIRED` | Mandatory split plan |
| 301-350 | `NOT_DEPLOYABLE` | Block deployment; score capped at 70/100 |
| >350 | `BLOCKED` | Reject review; score capped at 50/100 |

Source of truth: [`references/reviewer-defaults.yml`](../skills/rule-reviewer/references/reviewer-defaults.yml) for the numbers, and [`rubrics/rule-size.md`](../skills/rule-reviewer/rubrics/rule-size.md) for how to apply them.

### Blocking Issues

The skill counts issues that prevent autonomous execution:
- Ambiguous phrases ("consider", "if appropriate", "as needed")
- Undefined thresholds ("large", "significant", "appropriate")
- Missing conditional branches (no explicit else)
- Visual formatting (ASCII art, arrows, diagrams)

**Impact on score:** Six or more blocking issues cap the total score at 80/100. Ten or more blocking issues force the `NOT_EXECUTABLE` verdict. See [`skills/rule-reviewer/rubrics/scoring.md`](../skills/rule-reviewer/rubrics/scoring.md) for the full hard-cap rules.


## Advanced Usage

### Custom Output Directory

```text
output_root: quarterly-audit/
```

Writes to `quarterly-audit/rule-reviews/` instead of default `reviews/rule-reviews/`.

### Execution Timing

```text
timing_enabled: true
```

Adds timing metadata to output (duration, token usage, cost estimation).

For the current timing metadata format, threshold definitions, and cost calculation, see [Using the Skill Timer Skill](USING_SKILL_TIMER_SKILL.md). The timer implementation is the source of truth for those volatile values.

### Execution Modes

| Mode | Characteristics | When to Use |
|------|-----------------|-------------|
| **parallel** (default) | 5 sub-agents, each with isolated context per dimension | Recommended when context isolation between dimensions is important |
| **sequential** | Single-agent evaluates all dimensions in sequence | Valid for production; useful when debugging or in constrained environments |

Parallel mode's primary benefit is **context isolation**: each sub-agent receives only its assigned rubric and the target rule, preventing cross-dimension contamination. Performance is not guaranteed to be faster than sequential due to coordination overhead and sub-agent variability.

```text
execution_mode: sequential
```

### No-Overwrite Safety

If the output file exists, suffixes are appended: `-01.md`, `-02.md`, etc.

To intentionally replace an existing review:

```text
overwrite: true
```

### Supported File Types

**Rule Files (rules/*.md):**
- Full schema validation against `schemas/rule-schema.yml`
- All 6 dimensions scored
- TokenBudget variance check applies

**Project Files (PROJECT.md):**
- Schema validation skipped (different structure)
- All dimensions scored except schema-specific checks
- TokenBudget variance skipped


## FAQ

### What makes a rule "executable" by an agent?

An executable rule has:
- Explicit commands (no "consider" or "if appropriate")
- Complete coverage (all scenarios addressed)
- Clear thresholds (no "large" or "significant")
- Valid schema (correct metadata structure)

### What should I pass for `model`?

Use a lowercase-hyphenated slug like `claude-sonnet-45`. Raw model names are normalized automatically.

### What should I use for implementation plan review?

Use `rule-reviewer` for rule files agents will load. Implementation plan review is handled by the external portable-skills repository, not by a local skill in this project.

### Why does my review take 90-120 seconds?

This is expected and required. The skill performs detailed analysis including:
- Schema validation
- Agent execution testing (counting blocking issues)
- Rubric-based scoring for each dimension
- Specific recommendations with line numbers

Reviews completing in under 60 seconds may indicate incomplete analysis.

### Where do the rubrics come from?

The skill uses rubric files in `skills/rule-reviewer/rubrics/` for each dimension, plus `_overlap-resolution.md` to prevent double-counting issues across dimensions.


## Reference

### Architecture

```
Coordinator (Main Agent)
│
├── Phase 1: Setup
│   ├── Validate inputs
│   ├── Detect file type (rule vs project)
│   └── Run schema validation
│
├── Phase 2: Dimension Evaluation (parallel: 5 sub-agents, or sequential)
│   ├── Actionability (30pts)
│   ├── Rule Size (25pts): computed inline
│   ├── Parsability (15pts)
│   ├── Completeness (15pts)
│   ├── Consistency (10pts)
│   └── Cross-Agent Consistency (5pts)
│
├── Phase 3: Collect & Validate
│   ├── Gather dimension worksheets
│   └── Verify no overlap violations
│
└── Phase 4: Aggregate & Report
    ├── Apply scoring formula
    └── Generate unified review
```

### File Structure

Representative layout (see `skills/rule-reviewer/` for the complete current inventory):

```text
skills/rule-reviewer/
├── SKILL.md               # Main skill (entrypoint)
├── rubrics/               # Dimension scoring criteria
│   ├── actionability.md
│   ├── completeness.md
│   ├── consistency.md
│   ├── parsability.md
│   ├── token-efficiency.md
│   ├── rule-size.md
│   ├── staleness.md
│   ├── cross-agent-consistency.md
│   ├── scoring.md
│   └── _overlap-resolution.md
├── examples/              # Mode walkthroughs
│   ├── full-review.md
│   ├── focused-review.md
│   ├── staleness-review.md
│   ├── project-file-review.md
│   └── edge-cases.md
├── tests/                 # Test cases
│   ├── TESTING.md
│   ├── test-inputs.md
│   ├── test-modes.md
│   └── test-outputs.md
└── workflows/             # Step-by-step guides
    ├── input-validation.md
    ├── model-slugging.md
    ├── review-execution.md
    ├── schema-validation.md
    ├── file-write.md
    ├── error-handling.md
    ├── execution-discipline.md
    └── validation-checklists.md
```

### Integration with Other Skills

**With bulk-rule-reviewer:** Orchestrates batch reviews across all rules in `rules/` directory.

**With rule-creator:** Validate rules after creation:
1. Create rule using rule-creator skill
2. Run FULL review on the created rule
3. Verify: score ≥80/100, no CRITICAL issues

**With skill-timer:** Adds execution timing when `timing_enabled: true`.

### Output Paths

| Mode | Output Path |
|------|-------------|
| FULL | `reviews/rule-reviews/<name>-<model>-<date>.md` |
| FOCUSED | `reviews/rule-reviews/<name>-<model>-<date>.md` |
| STALENESS | `reviews/rule-reviews/<name>-<model>-<date>.md` |

### Support

- **Workflow guides:** `skills/rule-reviewer/workflows/*.md`
- **Examples:** `skills/rule-reviewer/examples/*.md`
- **Tests:** `skills/rule-reviewer/tests/*.md`
- **Troubleshooting:** `workflows/error-handling.md`
- **Timing system:** `docs/USING_SKILL_TIMER_SKILL.md`
