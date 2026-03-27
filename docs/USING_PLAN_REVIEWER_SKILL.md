# Using the Plan Reviewer Skill

**Last Updated:** 2026-03-27

The Plan Reviewer Skill evaluates LLM-generated plans for autonomous agent
executability. Use it to score a single plan, compare competing plans,
meta-review prior review outputs, or measure whether a revised plan actually
resolved earlier issues.

## Examples

### Minimal Required Example

```text
Use the plan-reviewer skill.

review_mode: FULL                    # Required
target_file: plans/deploy-feature.md # Required
review_date: 2026-03-27             # Required
model: claude-sonnet-45             # Required
```

### FULL With All Optional Settings

```text
Use the plan-reviewer skill.

review_mode: FULL                    # Required
target_file: plans/my-plan.md       # Required
review_date: 2026-03-27             # Required
model: claude-sonnet-45             # Required
output_root: quarterly-audit/       # Optional (default: reviews/) — custom output directory
execution_mode: sequential          # Optional (default: parallel) — use for debugging
timing_enabled: true                # Optional (default: false) — adds timing metadata
overwrite: true                     # Optional (default: false) — replaces existing file
```

### COMPARISON Example

```text
Use the plan-reviewer skill.

review_mode: COMPARISON             # Required
target_files: plans/approach-a.md, plans/approach-b.md  # Required (COMPARISON only)
review_date: 2026-03-27             # Required
model: claude-sonnet-45             # Required
```

Do not combine `target_file` with `target_files` — use `target_file` for FULL/DELTA, `target_files` for COMPARISON.

### META-REVIEW Example

```text
Use the plan-reviewer skill.

review_mode: META-REVIEW            # Required
review_files: reviews/plan-reviews/plan-a-claude-sonnet-45-2026-03-20.md, reviews/plan-reviews/plan-a-gpt-5-2026-03-20.md  # Required (META-REVIEW only)
review_date: 2026-03-27             # Required
model: claude-sonnet-45             # Required
```

Do not combine `review_files` with `target_file` or `target_files` — `review_files` is META-REVIEW only.

### DELTA Example

```text
Use the plan-reviewer skill.

review_mode: DELTA                  # Required
target_file: plans/my-plan-v2.md   # Required
baseline_review: reviews/plan-reviews/my-plan-claude-sonnet-45-2026-03-20.md  # Required (DELTA only)
review_date: 2026-03-27             # Required
model: claude-sonnet-45             # Required
```

Do not combine `baseline_review` with COMPARISON or META-REVIEW modes.

## Review Modes

| Mode | Purpose | Required Inputs | Typical Use Case | Output Location |
|------|---------|-----------------|------------------|-----------------|
| **FULL** | Comprehensive single-plan review | `target_file`, `review_date`, `model` | Validate a plan before execution | `reviews/plan-reviews/<name>-<model>-<date>.md` |
| **COMPARISON** | Rank multiple plans and declare a winner | `target_files`, `review_date`, `model` | Choose between alternate approaches | `reviews/summaries/_comparison-*.md` |
| **META-REVIEW** | Analyze consistency across review outputs | `review_files`, `review_date`, `model` | Audit reviewer agreement or review quality | `reviews/summaries/_meta-*.md` |
| **DELTA** | Measure improvement versus a prior review | `target_file`, `baseline_review`, `review_date`, `model` | Verify a revised plan fixed earlier issues | `reviews/plan-reviews/<name>-delta-*.md` |

### FULL

Use FULL mode for the standard 8-dimension review.

```text
review_mode: FULL
target_file: plans/deploy-feature.md
```

### COMPARISON

Use COMPARISON mode when you want a ranked result across multiple plans.

```text
review_mode: COMPARISON
target_files: plans/approach-a.md, plans/approach-b.md
```

### META-REVIEW

Use META-REVIEW when the inputs are review files rather than plans.

```text
review_mode: META-REVIEW
review_files: reviews/plan-reviews/plan-a-claude-sonnet-45-2026-03-20.md, reviews/plan-reviews/plan-a-gpt-5-2026-03-20.md
```

### DELTA

Use DELTA mode to compare a revised plan against a baseline review.

```text
review_mode: DELTA
target_file: plans/my-plan-v2.md
baseline_review: reviews/plan-reviews/my-plan-claude-sonnet-45-2026-03-20.md
```

## Understanding Your Results

### Verdicts

The skill’s current quick-reference verdict scale is:

| Score | Verdict | Meaning |
|------:|---------|---------|
| 90-100 | **EXCELLENT** | Strong agent-executable plan |
| 80-89 | **GOOD** | Usable with minor refinements |
| 60-79 | **NEEDS_WORK** | Significant revision still needed |
| 40-59 | **POOR** | Major gaps block reliable execution |
| <40 | **INADEQUATE** | Rewrite recommended |

### Scoring Dimensions and Weights

Plans are scored across 8 weighted dimensions.

#### Critical dimensions (75 points)

| Dimension | Max Points | Core Question |
|-----------|-----------:|---------------|
| Executability | 20 | Can an agent execute the plan without judgment calls? |
| Completeness | 20 | Are setup, execution, validation, cleanup, and recovery covered? |
| Success Criteria | 20 | Can completion be verified programmatically? |
| Scope | 15 | Are boundaries, assumptions, and end states explicit? |

#### Standard dimensions (25 points)

| Dimension | Max Points | Core Question |
|-----------|-----------:|---------------|
| Dependencies | 10 | Is ordering and blocking logic explicit? |
| Decomposition | 5 | Are steps split at the right level of detail? |
| Context | 5 | Does the plan provide the needed background and terminology? |
| Risk Awareness | 5 | Are fallbacks, failure modes, and recovery paths addressed? |

Scoring formula: `Raw (0-10) × (Weight / 2) = Points`

### Blocking Issues

The review calls out problems that directly reduce autonomous executability, such
as:

- ambiguous phrases like `consider`, `if appropriate`, or `as needed`
- implicit actions instead of explicit commands
- missing else/default/error branches
- undefined thresholds such as `large` or `significant`

High blocking-issue counts can cap the effective score even if other sections
look strong.

### Audit Trail and Worksheets

The skill is designed to be auditable. It expects dimension worksheets and
supporting evidence in the output so users can trace how the score was reached,
not just see a final verdict.

If a plan scores poorly, treat the dimension tables as the remediation backlog:
start with critical dimensions first, then reduce blocking issues, then improve
supporting dimensions.

## Advanced Usage

### Optional Inputs

| Input | Type | Default | Purpose |
|-------|------|---------|---------|
| `output_root` | Optional | `reviews/` | Change the root directory for output files |
| `execution_mode` | Optional | `parallel` | Choose `parallel` (Recommended) or `sequential` (debugging) |
| `timing_enabled` | Optional | `false` | Add timing metadata to the output |
| `overwrite` | Optional | `false` | Replace an existing output file instead of suffixing |

### Execution Mode

Parallel is the default and expected mode.

| Mode | Characteristics | When to Use |
|------|-----------------|-------------|
| `parallel` | Uses 8 sub-agents for dimension evaluation | Standard production review path |
| `sequential` | Single-agent review path | Debugging or constrained environments |

```text
execution_mode: sequential
```

### Output Root

```text
output_root: quarterly-audit/
```

This changes the root while preserving mode-specific subdirectories.

Examples:

- FULL: `quarterly-audit/plan-reviews/...`
- COMPARISON: `quarterly-audit/summaries/...`
- META-REVIEW: `quarterly-audit/summaries/...`
- DELTA: `quarterly-audit/plan-reviews/...`

### No-overwrite Safety

By default, existing outputs are preserved. If a target filename already exists,
the skill appends `-01`, `-02`, and so on.

To intentionally replace an existing file:

```text
overwrite: true
```

### Timing Behavior

```text
timing_enabled: true
```

When enabled, the skill starts timing before execution, records checkpoints, and
embeds timing metadata into the final review.

### Determinism Requirements

The skill is explicitly designed to reduce run-to-run variance.

Key operational requirements include:

- batch-load all rubric files before reading the plan
- create all worksheets before scoring
- read the plan from line 1 to end
- apply overlap rules instead of double-counting issues
- include worksheets in the output for auditability

Expected variance target: about ±2 points overall. If repeated runs vary more
than that, treat it as a signal to inspect worksheet completeness and overlap
handling.

## FAQ

### What makes a plan executable for an autonomous agent?

A strong plan uses explicit commands, clear thresholds, complete lifecycle
coverage, and verifiable success criteria. The less interpretation the agent
must invent, the better the score.

### What should I pass for `model`?

Use a lowercase hyphenated slug such as `claude-sonnet-45`. If you pass a raw
model name, the skill normalizes it before generating filenames.

### When should I use plan-reviewer instead of doc-reviewer?

Use `plan-reviewer` for executable task plans. Use `doc-reviewer` for user-facing
documentation such as README, CONTRIBUTING, or files in `docs/`.

### Why can reviews take several minutes?

The skill can load many rubrics, create worksheets, evaluate 8 dimensions, and
assemble an auditable report. Parallel mode speeds this up, but thorough review
still takes time.

### Where do the scoring rules come from?

The scoring system comes from the rubric files under
`skills/plan-reviewer/rubrics/` and the supporting workflow documents in
`skills/plan-reviewer/workflows/`.

### What does DELTA mode actually tell me?

DELTA mode answers whether the revised plan resolved issues identified by a
baseline review. It is the best mode for verifying revision quality rather than
re-scoring from scratch alone.

## Reference

### Architecture Overview

```text
Coordinator
│
├── Phase 1: Input validation and parameter collection
├── Phase 2: Model slugging and optional timing start
├── Phase 3: Review execution
│   ├── parallel: 8 dimension sub-agents
│   └── sequential: single review path
├── Phase 4: Aggregation and output assembly
└── Phase 5: File write and error handling
```

### Key Workflows

| Workflow | File | Purpose |
|----------|------|---------|
| Input validation | `skills/plan-reviewer/workflows/input-validation.md` | Validate mode-specific parameters |
| Parameter collection | `skills/plan-reviewer/workflows/parameter-collection.md` | Gather required and optional inputs |
| Parallel execution | `skills/plan-reviewer/workflows/parallel-execution.md` | Coordinator logic for 8 sub-agents |
| Sequential review | `skills/plan-reviewer/workflows/review-execution.md` | Single-agent fallback path |
| File writing | `skills/plan-reviewer/workflows/file-write.md` | Output path and write behavior |
| Error handling | `skills/plan-reviewer/workflows/error-handling.md` | Recovery behavior |
| Determinism | `skills/plan-reviewer/workflows/determinism.md` | Worksheet-first consistency requirements |

### File Structure

```text
skills/plan-reviewer/
├── SKILL.md
├── rubrics/
│   ├── executability.md
│   ├── completeness.md
│   ├── success-criteria.md
│   ├── scope.md
│   ├── dependencies.md
│   ├── decomposition.md
│   ├── context.md
│   └── risk-awareness.md
├── examples/
├── tests/
└── workflows/
```

### Related Skills

| Skill | Relationship |
|-------|--------------|
| `doc-reviewer` | Reviews human-facing documentation rather than executable plans |
| `rule-reviewer` | Reviews rule files for agent executability and compliance |
| `skill-timing` | Provides the optional timing workflow used when timing is enabled |

### Output Path Summary

| Mode | Output Pattern |
|------|----------------|
| FULL | `reviews/plan-reviews/<name>-<model>-<date>.md` |
| COMPARISON | `reviews/summaries/_comparison-*.md` |
| META-REVIEW | `reviews/summaries/_meta-*.md` |
| DELTA | `reviews/plan-reviews/<name>-delta-*.md` |

### Source of Truth

For behavior details, prefer these files over older examples or copied notes:

- `skills/plan-reviewer/SKILL.md`
- `skills/plan-reviewer/rubrics/`
- `skills/plan-reviewer/workflows/`
