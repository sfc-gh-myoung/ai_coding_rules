# Using the Plan Reviewer Skill

**Last Updated:** 2026-03-07

The Plan Reviewer Skill evaluates LLM-generated plans to ensure autonomous agents can execute them successfully. It scores plans across 8 dimensions using a 100-point scoring system optimized for agent executability.


## Quick Start

### 1. Load the skill

```text
Load skills/plan-reviewer/SKILL.md
```

### 2. Request a review

```text
Use the plan-reviewer skill.

target_file: plans/my-plan.md
review_mode: FULL
```

The skill will prompt for any missing parameters (date, model).

### 3. Check the output

Reviews are written to `reviews/plan-reviews/<plan-name>-<model>-<date>.md`

On success:

```text
✓ Review complete

OUTPUT_FILE: reviews/plan-reviews/my-plan-claude-sonnet-45-2026-03-08.md
Overall: 81/100
Verdict: GOOD_PLAN
```


## Review Modes

| Mode | Purpose | When to Use |
|------|---------|-------------|
| **FULL** | Comprehensive single-plan review | Validate before agent execution |
| **COMPARISON** | Rank multiple plans, declare winner | Choose between competing approaches |
| **META-REVIEW** | Analyze consistency across reviews | Validate reviewer agreement |
| **DELTA** | Track issue resolution from baseline | Verify fixes after revision |

### FULL Mode

```text
target_file: plans/deploy-feature.md
review_mode: FULL
```

### COMPARISON Mode

```text
target_files: plans/approach-a.md, plans/approach-b.md
task_description: Migrate database to new schema
review_mode: COMPARISON
```

### META-REVIEW Mode

```text
review_files: reviews/plan-X-claude.md, reviews/plan-X-gpt.md
original_document: plans/X.md
review_mode: META-REVIEW
```

### DELTA Mode

```text
target_file: plans/X.md
baseline_review: reviews/plan-reviews/X-claude-2026-01-01.md
review_mode: DELTA
```


## Understanding Your Results

### Verdicts

| Score | Verdict | Action |
|-------|---------|--------|
| 90-100 | **EXCELLENT_PLAN** | Ready for execution |
| 80-89 | **GOOD_PLAN** | Minor refinements needed |
| 60-79 | **NEEDS_WORK** | Significant refinement required |
| 40-59 | **POOR_PLAN** | Major revision needed |
| <40 | **INADEQUATE_PLAN** | Rewrite from scratch |

### Scoring Dimensions

Plans are scored across 8 dimensions with weighted points:

**Critical Dimensions (75 points)** — Agent must execute without human intervention:

| Dimension | Points | Key Question |
|-----------|--------|--------------|
| Executability | 20 | Can agent execute without judgment calls? |
| Completeness | 20 | Are all steps present (setup, validation, cleanup, error recovery)? |
| Success Criteria | 20 | Can agent verify completion programmatically? |
| Scope | 15 | Are boundaries and start/end states explicit? |

**Standard Dimensions (25 points)** — Important but recoverable:

| Dimension | Points | Key Question |
|-----------|--------|--------------|
| Dependencies | 10 | Is execution order and blocking explicit? |
| Decomposition | 5 | Are tasks appropriately granular? |
| Context | 5 | Is background and domain terminology provided? |
| Risk Awareness | 5 | Are fallbacks and recovery paths documented? |

**Scoring Formula:** `Raw (0-10) × (Weight / 2) = Points`

### Blocking Issues

The skill counts issues that prevent autonomous execution:
- Ambiguous phrases ("consider", "if appropriate", "as needed")
- Implicit commands (descriptions instead of explicit commands)
- Missing branches (no else/default/error handling)
- Undefined thresholds ("large", "significant", "appropriate")

**Impact on score:**
- ≥10 blocking issues → Score capped at 60 (NEEDS_WORK)
- ≥20 blocking issues → Score capped at 40 (POOR_PLAN)

### Verification Tables

Reviews include audit tables to support scoring:
1. **Executability Audit** — Ambiguous phrases with line numbers and fixes
2. **Completeness Audit** — Phase coverage (Setup, Validation, Cleanup, Error Recovery)
3. **Success Criteria Audit** — Task-by-task criteria presence
4. **Priority Compliance Summary** — Blocking issue counts


## Advanced Usage

### Custom Output Directory

```text
output_root: quarterly-audit/
```

Writes to `quarterly-audit/plan-reviews/` instead of default `reviews/plan-reviews/`.

### Execution Timing

```text
timing_enabled: true
```

Adds timing metadata to output (duration, token usage, cost estimation).

**Timing thresholds:**
- <15 seconds: Error (possible shortcut)
- <30 seconds: Warning (unusually fast)
- >720 seconds: Warning (possible issue)

### Execution Modes

| Mode | Speed | Use Case |
|------|-------|----------|
| **parallel** (default) | ~3-5 min | Production reviews (8 sub-agents) |
| **sequential** | ~15-20 min | Debugging, low-resource environments |

```text
execution_mode: sequential
```

### No-Overwrite Safety

If the output file exists, suffixes are appended: `-01.md`, `-02.md`, etc.


## FAQ

### What makes a plan "executable" by an agent?

An executable plan has:
- Explicit commands (no "consider" or "if appropriate")
- Verifiable success criteria (exit codes, file existence checks)
- Complete steps (setup, validation, cleanup, error recovery)
- Clear scope boundaries (defined start/end states)

### What should I pass for `model`?

Prefer a slug like `claude-sonnet-45`. Raw model names are normalized automatically.

### What's the difference between plan-reviewer and doc-reviewer?

- **plan-reviewer**: Agent executability, task completeness, scope clarity
- **doc-reviewer**: Human readability, accuracy, link validation

Use plan-reviewer for plans an agent will execute. Use doc-reviewer for documentation humans will read.

### Where does the rubric come from?

The skill uses rubric files in `skills/plan-reviewer/rubrics/` plus `_overlap-resolution.md` to prevent double-counting issues across dimensions.


## Reference

### Architecture

```
Coordinator (Main Agent)
│
├── Phase 1: Setup
│   ├── Load plan content
│   ├── Load overlap resolution rules
│   └── Prepare shared context
│
├── Phase 2: Parallel Evaluation (8 sub-agents)
│   ├── SA-1: Executability (20pts)
│   ├── SA-2: Completeness (20pts)
│   ├── SA-3: Success Criteria (20pts)
│   ├── SA-4: Scope (15pts)
│   ├── SA-5: Dependencies (10pts)
│   ├── SA-6: Decomposition (5pts)
│   ├── SA-7: Context (5pts)
│   └── SA-8: Risk Awareness (5pts)
│
├── Phase 3: Collect & Validate
│   ├── Gather dimension worksheets
│   └── Verify no overlap violations
│
└── Phase 4: Aggregate & Report
    ├── Apply scoring formula
    └── Generate unified review
```

### Key Workflows

| Workflow | File | Purpose |
|----------|------|---------|
| Parallel execution | `workflows/parallel-execution.md` | Coordinator logic |
| Sub-agent template | `workflows/dimension-subagent-template.md` | Dimension evaluation prompt |
| Score aggregation | `workflows/score-aggregation.md` | Combine results |
| Overlap validation | `workflows/overlap-validator.md` | Prevent double-counting |
| Parameter collection | `workflows/parameter-collection.md` | Interactive input |

### File Structure

```text
skills/plan-reviewer/
├── SKILL.md               # Main skill (entrypoint)
├── rubrics/               # Dimension scoring criteria
│   ├── executability.md
│   ├── completeness.md
│   ├── success-criteria.md
│   ├── scope.md
│   ├── dependencies.md
│   ├── decomposition.md
│   ├── context.md
│   └── risk-awareness.md
├── examples/              # Mode walkthroughs
├── tests/                 # Test cases
└── workflows/             # Step-by-step guides
```

### Integration with Other Skills

**With rule-reviewer:** Validate rules are agent-executable before reviewing plans that reference them.

### Output Paths

| Mode | Output Path |
|------|-------------|
| FULL | `reviews/plan-reviews/<name>-<model>-<date>.md` |
| COMPARISON | `reviews/summaries/_comparison-<id>-<model>-<date>.md` |
| META-REVIEW | `reviews/summaries/_meta-<name>-<date>.md` |
| DELTA | `reviews/plan-reviews/<name>-delta-<baseline>-to-<current>-<model>.md` |

### Deployment

This skill is deployable via `task deploy` for use in other projects.

### Support

- **Workflow guides:** `skills/plan-reviewer/workflows/*.md`
- **Examples:** `skills/plan-reviewer/examples/*.md`
- **Tests:** `skills/plan-reviewer/tests/*.md`
- **Timing system:** `skills/skill-timing/README.md`
