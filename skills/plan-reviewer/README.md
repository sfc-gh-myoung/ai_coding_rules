# Plan Reviewer Skill

A Claude skill for reviewing LLM-generated plans to ensure autonomous agents can execute them successfully. Supports single-plan review, multi-plan comparison, and meta-review of review consistency.

## Overview

This skill automates the complete plan review workflow:

- Validates inputs (target files, date, mode, model)
- Executes review using `PROMPT.md` rubric (colocated in this skill folder)
- Evaluates plans across 8 dimensions optimized for agent executability
- Supports FULL, COMPARISON, and META-REVIEW modes
- Writes results to `reviews/` with automatic suffix for duplicates

## Quick Start

### Step 1: Load the Skill

Open:

```text
skills/plan-reviewer/SKILL.md
```

### Step 2: Trigger Review

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

target_files: [plans/plan-a.md, plans/plan-b.md]
task_description: Implement user authentication
review_date: 2025-12-16
review_mode: COMPARISON
model: claude-sonnet45
```

**META-REVIEW mode (review consistency):**

```text
Use the plan-reviewer skill.

target_files: [reviews/plan-X-sonnet-2025-12-16.md, reviews/plan-X-gpt-2025-12-16.md]
original_document: plans/X.md
review_date: 2025-12-16
review_mode: META-REVIEW
model: claude-sonnet45
```

### Step 3: Verify Output

Check the generated review file:

```bash
# FULL mode
ls reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md

# COMPARISON mode
ls reviews/plan-comparison-claude-sonnet45-2025-12-16.md

# META-REVIEW mode
ls reviews/meta-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md
```

## File Structure

```text
skills/plan-reviewer/
├── SKILL.md               # Main skill instructions (Claude Code entrypoint)
├── PROMPT.md              # Review rubric and output format template
├── README.md              # This file - usage documentation
├── VALIDATION.md          # Skill self-validation procedures
├── examples/              # Review mode examples
│   ├── full-review.md         # FULL mode walkthrough
│   ├── comparison-review.md   # COMPARISON mode walkthrough
│   ├── meta-review.md         # META-REVIEW mode walkthrough
│   └── edge-cases.md          # Ambiguous scenarios and resolutions
├── tests/                 # Skill test cases
│   ├── README.md              # Test overview and instructions
│   ├── test-inputs.md         # Input validation test cases
│   ├── test-modes.md          # Review mode test cases
│   └── test-outputs.md        # Output handling test cases
└── workflows/             # Step-by-step workflow guides
    ├── input-validation.md    # Input checking procedures
    ├── model-slugging.md      # Model name normalization
    ├── review-execution.md    # Review generation steps
    ├── file-write.md          # Output file handling
    └── error-handling.md      # Error recovery procedures
```

## Review Dimensions

### Critical Dimensions (2× weight)

| Dimension | Focus | Key Questions |
|-----------|-------|---------------|
| **Executability** | Agent can execute without judgment | Are commands explicit? Any ambiguous phrases? |
| **Completeness** | All steps present | Setup, validation, cleanup, error recovery included? |
| **Success Criteria** | Verifiable completion | Can agent determine "done" programmatically? |
| **Scope** | Bounded and measurable | Start/end state defined? Clear boundaries? |

### Standard Dimensions (1× weight)

| Dimension | Focus | Key Questions |
|-----------|-------|---------------|
| Decomposition | Task granularity | Single-action steps? Consistent sizing? |
| Dependencies | Execution order | Blocking relationships explicit? Parallel tasks noted? |
| Context | Background provided | Domain terms defined? Self-contained? |
| Risk Awareness | Fallback strategies | Risks identified? Recovery paths documented? |

## Review Modes

| Mode | Purpose | Output |
|------|---------|--------|
| **FULL** | Comprehensive single-plan review | All 8 dimensions scored, executability verdict |
| **COMPARISON** | Rank multiple plans | Side-by-side scoring, winner declared with rationale |
| **META-REVIEW** | Analyze review consistency | Variance analysis, calibration assessment, consensus score |

## Agent Executability Verdicts

| Score Range | Verdict | Action |
|-------------|---------|--------|
| 54-60/60 (90%+) | **EXECUTABLE** | Agent can execute as-is |
| 48-53/60 (80-89%) | **EXECUTABLE** | Minor refinements recommended |
| 36-47/60 (60-79%) | **NEEDS_REFINEMENT** | Fix critical issues before agent execution |
| <36/60 (<60%) | **NOT_EXECUTABLE** | Major rework required |

## Output Format

Reviews are written to:

**FULL mode:**
```text
reviews/plan-<plan-name>-<model>-<YYYY-MM-DD>.md
```

**COMPARISON mode:**
```text
reviews/plan-comparison-<model>-<YYYY-MM-DD>.md
```

**META-REVIEW mode:**
```text
reviews/meta-<document-name>-<model>-<YYYY-MM-DD>.md
```

**No-overwrite safety:** If file exists, uses suffixes:
```text
reviews/plan-<name>-<model>-<date>-01.md
reviews/plan-<name>-<model>-<date>-02.md
```

## Confirmation Message

On success:

```text
✓ Review complete

OUTPUT_FILE: reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md
Target: plans/IMPROVE_RULE_LOADING.md
Mode: FULL
Model: claude-sonnet45

Summary:
- Executability: 8/10
- Completeness: 9/10
- Success Criteria: 7/10
- Scope: 8/10
- Decomposition: 4/5
- Dependencies: 5/5
- Context: 4/5
- Risk Awareness: 3/5
Overall: 48/60
Verdict: EXECUTABLE
```

## Use Cases

### 1. Evaluating a Single Plan

Use FULL mode to get a comprehensive assessment:

```text
target_file: plans/my-feature-plan.md
review_mode: FULL
```

### 2. Choosing Between Competing Plans

Use COMPARISON mode when multiple LLMs or team members created plans:

```text
target_files: [plans/claude-plan.md, plans/gpt-plan.md]
task_description: Implement OAuth2 authentication
review_mode: COMPARISON
```

### 3. Validating Review Consistency

Use META-REVIEW mode after multiple LLMs review the same document:

```text
target_files: [
  reviews/plan-X-claude-sonnet45-2025-12-16.md,
  reviews/plan-X-gpt-52-2025-12-16.md,
  reviews/plan-X-claude-opus45-2025-12-16.md
]
review_mode: META-REVIEW
```

## Integration with Other Skills

### With docs-reviewer

Plan files can be reviewed as documentation:
- **docs-reviewer**: Accuracy, link validation, general clarity
- **plan-reviewer**: Agent executability, task completeness, scope

### With rule-reviewer

If a plan references rules:
- Use **rule-reviewer** to validate rules are agent-executable
- Use **plan-reviewer** to validate the plan using those rules

## Deployment

This skill is **deployable** (included when running `task deploy`). After deployment to a project, users can review that project's plans for agent executability.

## Version History

- **v1.0.0** (2025-12-16): Initial release
  - 8-dimension plan review rubric (4 critical, 4 standard)
  - FULL mode for single-plan reviews
  - COMPARISON mode for multi-plan ranking
  - META-REVIEW mode for review consistency analysis
  - Weighted scoring (/60 total)
  - Agent Executability Verdicts
  - Deployable to other projects

## Troubleshooting

See `workflows/error-handling.md` for common issues and resolutions.

## Validation

See `VALIDATION.md` for skill health checks and regression testing.

