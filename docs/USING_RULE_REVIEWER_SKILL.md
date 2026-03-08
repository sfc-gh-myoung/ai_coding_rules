# Using the Rule Reviewer Skill

**Last Updated:** 2026-03-07

The Rule Reviewer Skill evaluates rule files to ensure autonomous agents can execute them successfully. It scores rules across 8 dimensions using a weighted scoring system optimized for agent executability.


## Quick Start

### 1. Load the skill

```text
Load skills/rule-reviewer/SKILL.md
```

### 2. Request a review

```text
Use the rule-reviewer skill.

target_file: rules/200-python-core.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

The skill validates inputs and prompts for any missing parameters.

### 3. Check the output

Reviews are written to `reviews/rule-reviews/<rule-name>-<model>-<date>.md`

On success:

```text
✓ Review complete

OUTPUT_FILE: reviews/rule-reviews/200-python-core-claude-sonnet-45-2026-01-06.md
Target: rules/200-python-core.md
Mode: FULL
Model: claude-sonnet-45
```


## Review Modes

| Mode | Purpose | When to Use |
|------|---------|-------------|
| **FULL** | Comprehensive evaluation | Validate rules before deployment |
| **FOCUSED** | Deep-dive on critical areas | Quick check on Actionability + Completeness only |
| **STALENESS** | Check for outdated content | Periodic currency audits |

### FULL Mode

Scores all 8 dimensions for a complete quality assessment.

```text
target_file: rules/200-python-core.md
review_mode: FULL
```

### FOCUSED Mode

Evaluates only Actionability and Completeness (50 points max). Use for rapid validation.

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
| 94-105 | **EXECUTABLE** | Production-ready |
| 84-93 | **EXECUTABLE_WITH_REFINEMENTS** | Good, minor fixes needed |
| 63-83 | **NEEDS_REFINEMENT** | Significant refinement required |
| <63 | **NOT_EXECUTABLE** | Major revision needed |

**Critical dimension override:** If both Actionability ≤4/10 AND Completeness ≤4/10 → NOT_EXECUTABLE regardless of total score.

### Scoring Dimensions

Rules are scored across 8 dimensions with weighted points:

**Critical Dimensions (65 points)** — Agent must execute without judgment calls:

| Dimension | Weight | Max Points | Key Question |
|-----------|--------|------------|--------------|
| Actionability | 5 | 25 | Can agents execute without judgment? |
| Completeness | 5 | 25 | Are all scenarios covered? |
| Consistency | 3 | 15 | Is internal alignment correct? |

**Standard Dimensions (50 points)** — Important for quality:

| Dimension | Weight | Max Points | Key Question |
|-----------|--------|------------|--------------|
| Parsability | 3 | 15 | Is metadata/schema valid? |
| Token Efficiency | 2 | 10 | Within ±5% of TokenBudget? |
| Rule Size | 2 | 10 | Within 500-line target? |
| Staleness | 2 | 10 | Are patterns current? |
| Cross-Agent Consistency | 1 | 5 | Works across all agents? |

**Scoring Formula:** `Raw (0-10) × (Weight / 2) = Points`

**Example (Actionability):**
- Raw score: 8/10
- Weight: 5
- Points: 8 × (5/2) = 8 × 2.5 = **20 points**

### Rule Size Flags

The Rule Size dimension includes deployment flags:

| Line Count | Flag | Action |
|------------|------|--------|
| ≤500 | — | Optimal |
| 501-600 | `OPTIMIZATION_RECOMMENDED` | Suggest consolidation |
| 601-800 | `SPLITTING_REQUIRED` | Block deployment, require split plan |
| >800 | `NOT_DEPLOYABLE` | Fail review, mandatory remediation |

### Blocking Issues

The skill counts issues that prevent autonomous execution:
- Ambiguous phrases ("consider", "if appropriate", "as needed")
- Undefined thresholds ("large", "significant", "appropriate")
- Missing conditional branches (no explicit else)
- Visual formatting (ASCII art, arrows, diagrams)

**Impact on score:** ≥10 blocking issues → Score capped at 60


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

**Example timing metadata:**

```markdown
## Timing Metadata

| Metric | Value |
|--------|-------|
| Run ID | `a1b2c3d4e5f67890` |
| Duration | 3m 45s (225.5s) |
| Model | claude-sonnet-45 |
| Tokens | 16,700 (12,500 in / 4,200 out) |
| Cost | ~$0.04 |
```

**Timing thresholds:**
- <60 seconds: Warning (possible shortcut)
- >180 seconds: Warning (possible issue)

### Execution Modes

| Mode | Speed | Use Case |
|------|-------|----------|
| **parallel** (default) | ~90-120 sec | Production reviews (7 sub-agents) |
| **sequential** | ~2-3 min | Debugging, low-resource environments |

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
- All 8 dimensions scored
- TokenBudget variance check applies

**Project Files (AGENTS.md, PROJECT.md):**
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

### What's the difference between rule-reviewer and plan-reviewer?

- **rule-reviewer**: Validates rule files for agent executability, schema compliance, token efficiency
- **plan-reviewer**: Validates implementation plans for task completeness, success criteria, scope clarity

Use rule-reviewer for rule files agents will load. Use plan-reviewer for plans agents will execute.

### Why does my review take 90-120 seconds?

This is expected and required. The skill performs comprehensive analysis including:
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
├── Phase 2: Parallel Evaluation (7 sub-agents)
│   ├── SA-1: Actionability (25pts)
│   ├── SA-2: Completeness (25pts)
│   ├── SA-3: Consistency (15pts)
│   ├── SA-4: Parsability (15pts)
│   ├── SA-5: Token Efficiency (10pts)
│   ├── SA-6: Rule Size (10pts)
│   └── SA-7: Staleness + Cross-Agent (15pts)
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
│   └── _overlap-resolution.md
├── examples/              # Mode walkthroughs
│   ├── full-review.md
│   ├── focused-review.md
│   ├── staleness-review.md
│   ├── project-file-review.md
│   └── edge-cases.md
├── tests/                 # Test cases
│   ├── README.md
│   ├── test-inputs.md
│   ├── test-modes.md
│   └── test-outputs.md
└── workflows/             # Step-by-step guides
    ├── input-validation.md
    ├── model-slugging.md
    ├── review-execution.md
    ├── schema-validation.md
    ├── file-write.md
    └── error-handling.md
```

### Integration with Other Skills

**With bulk-rule-reviewer:** Orchestrates batch reviews across all rules in `rules/` directory.

**With rule-creator:** Validate rules after creation:
1. Create rule using rule-creator skill
2. Run FULL review on the created rule
3. Verify: score ≥75/100, no CRITICAL issues

**With skill-timing:** Adds execution timing when `timing_enabled: true`.

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
- **Timing system:** `skills/skill-timing/README.    
