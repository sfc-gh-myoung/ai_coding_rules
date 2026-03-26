# Using the Doc Reviewer Skill

**Last Updated:** 2026-03-26

The Doc Reviewer Skill reviews project documentation for user-facing quality and
accuracy. Use it to audit README and CONTRIBUTING files, review `docs/*.md`,
validate references against the codebase, and run focused maintenance checks for
staleness or specific documentation concerns.

## Quick Start

### 1. Load the skill

```text
Load skills/doc-reviewer/SKILL.md
```

### 2. Run a minimal FULL review

```text
Use the doc-reviewer skill.

review_mode: FULL
target_files: README.md
review_date: 2026-03-26
model: claude-sonnet-45
```

The skill validates inputs, collects missing parameters, and runs the dimension
review in parallel by default.

### 3. Check the output

Single-file reviews are written to:
`reviews/doc-reviews/<doc-name>-<model>-<date>.md`

Example success output:

```text
✓ Review complete

OUTPUT_FILE: reviews/doc-reviews/README-claude-sonnet-45-2026-03-26.md
Overall: 85/100
Verdict: GOOD
```

## Review Modes

| Mode | Purpose | Required Inputs | Typical Use Case | Output Location |
|------|---------|-----------------|------------------|-----------------|
| **FULL** | Comprehensive 6-dimension review | `review_date`, `review_mode`, `model` | New documentation, major rewrites, periodic audits | `reviews/doc-reviews/<name>-<model>-<date>.md` or collection summary |
| **FOCUSED** | Targeted review of a specific area | FULL inputs plus `focus_area` | Accuracy-only or clarity-only review after changes | Same as FULL, based on scope |
| **STALENESS** | Fast maintenance review for currency and drift | `review_date`, `review_mode`, `model` | Link rot, outdated commands, deprecated patterns | Same as FULL, based on scope |

### FULL

Use FULL mode for the standard comprehensive review.

```text
review_mode: FULL
target_files: README.md, CONTRIBUTING.md
```

### FOCUSED

FOCUSED mode requires `focus_area`.

```text
review_mode: FOCUSED
target_files: docs/ARCHITECTURE.md
focus_area: accuracy
```

Current skill behavior uses `focus_area`, not `focus_dimensions`.

### STALENESS

Use STALENESS mode for lighter-weight maintenance checks.

```text
review_mode: STALENESS
target_files: README.md, docs/SETUP.md
```

## Understanding Your Results

### Verdicts

The current skill materials use this verdict scale:

| Score | Verdict | Meaning |
|------:|---------|---------|
| 90-100 | **EXCELLENT** | High-quality documentation |
| 80-89 | **GOOD** | Minor improvements recommended |
| 60-79 | **NEEDS_IMPROVEMENT** | Significant updates required |
| 40-59 | **POOR** | Major revision needed |
| <40 | **INADEQUATE** | Rewrite-level issues |

### Scoring Dimensions

#### Critical dimensions (50 points)

| Dimension | Max Points | Core Question |
|-----------|-----------:|---------------|
| Accuracy | 25 | Does the documentation match the codebase and commands? |
| Completeness | 25 | Are the necessary topics and steps covered? |

#### Important dimensions (35 points)

| Dimension | Max Points | Core Question |
|-----------|-----------:|---------------|
| Clarity | 20 | Can the intended audience follow the content? |
| Structure | 15 | Is the information organized and easy to navigate? |

#### Standard dimensions (15 points)

| Dimension | Max Points | Core Question |
|-----------|-----------:|---------------|
| Staleness | 10 | Are links, versions, and patterns current? |
| Consistency | 5 | Does the content follow project conventions? |

Scoring formula: `Raw (0-10) × (Weight / 2) = Points`

### Verification Tables

Reviews should include evidence tables that justify the score.

| Table | Purpose |
|-------|---------|
| Cross-Reference Verification | Confirms referenced files, commands, functions, and paths |
| Link Validation | Records link status, redirects, or manual follow-up |
| Coverage Checklist | Tracks documented versus undocumented areas |

### Critical Override Behavior

Low accuracy or completeness can force a worse overall outcome than the numeric
score alone suggests. If core references are wrong or critical setup guidance is
missing, treat that as a high-priority fix regardless of the headline score.

### How to Interpret Low Scores

For low-scoring documentation:

1. fix factual accuracy first
2. close major coverage gaps second
3. improve clarity and structure next
4. clean up staleness and consistency last

That ordering matches the weighting and the real user impact.

## Advanced Usage

### Optional Inputs

| Input | Default | Purpose |
|-------|---------|---------|
| `target_files` | Default project docs | Specify one or more Markdown files |
| `review_scope` | `single` | Review files individually or as one collection |
| `focus_area` | none | Required for `FOCUSED` mode |
| `output_root` | `reviews/` | Change the output root directory |
| `overwrite` | `false` | Replace an existing output file |
| `timing_enabled` | `false` | Add timing metadata |
| `execution_mode` | `parallel` | Choose `parallel` or `sequential` execution |

### Default Target Files

When `target_files` is omitted, the skill defaults to reviewing:

- `README.md`
- `CONTRIBUTING.md`
- all Markdown files under `docs/`

### Review Scope

| Scope | Output Behavior | Use Case |
|-------|-----------------|----------|
| `single` | One review file per target document | Detailed file-by-file analysis |
| `collection` | One consolidated review | Portfolio-level documentation audit |

Collection output is written to:
`reviews/summaries/_docs-collection-<model>-<date>.md`

### Execution Mode

The current skill defaults to `parallel`, not sequential.

| Mode | Characteristics | When to Use |
|------|-----------------|-------------|
| `parallel` | Uses 6 sub-agents for dimension review | Standard path and current default |
| `sequential` | Single-agent fallback path | Debugging or constrained environments |

```text
execution_mode: sequential
```

### Output Root

```text
output_root: quarterly-audit/
```

Examples:

- single scope: `quarterly-audit/doc-reviews/...`
- collection scope: `quarterly-audit/summaries/...`

### No-overwrite Safety

By default, existing outputs are preserved and the skill appends `-01`, `-02`,
and so on.

To intentionally replace an existing file:

```text
overwrite: true
```

### Timing Behavior

```text
timing_enabled: true
```

When enabled, the skill starts a timing run, records checkpoints, and embeds
metadata in the review output after execution completes.

### Determinism and Operational Notes

The skill’s workflow emphasizes consistency:

- load rubrics before reviewing targets
- create verification structures before scoring
- read target documentation end to end
- check non-issues and overlap rules before assigning findings
- include verification tables in the final output

Those constraints are there to reduce score drift across repeated runs.

## FAQ

### Which files are reviewed by default?

If you do not provide `target_files`, the skill reviews `README.md`,
`CONTRIBUTING.md`, and all Markdown files in `docs/`.

### How does `focus_area` work?

`focus_area` narrows a FOCUSED review to a specific concern such as accuracy,
clarity, or staleness. It is required when `review_mode` is `FOCUSED`.

### What is the difference between `single` and `collection` scope?

`single` produces one review per file. `collection` produces one consolidated
summary across the selected files.

### When should I use doc-reviewer instead of plan-reviewer?

Use `doc-reviewer` for human-facing documentation. Use `plan-reviewer` for plans
that an autonomous agent is expected to execute.

### What happens if the output file already exists?

Unless `overwrite: true` is set, the skill preserves the existing file and writes
a suffixed filename instead.

### How are code references and links verified?

The skill checks documented file paths, commands, and references against the
project where possible, validates internal links directly, and records external
links for validation or manual follow-up.

## Reference

### Architecture Overview

```text
Coordinator
│
├── Phase 1: Input validation and parameter collection
├── Phase 2: Model slugging and optional timing start
├── Phase 3: Review execution
│   ├── parallel: 6 dimension sub-agents
│   └── sequential: single review path
├── Phase 4: Score aggregation and output assembly
└── Phase 5: File write and error handling
```

### Key Workflows

| Workflow | File | Purpose |
|----------|------|---------|
| Input validation | `skills/doc-reviewer/workflows/input-validation.md` | Validate parameters and mode-specific requirements |
| Parameter collection | `skills/doc-reviewer/workflows/parameter-collection.md` | Gather required and optional inputs |
| Parallel execution | `skills/doc-reviewer/workflows/parallel-execution.md` | Default 6-sub-agent review path |
| Sequential review | `skills/doc-reviewer/workflows/review-execution.md` | Single-agent fallback path |
| File writing | `skills/doc-reviewer/workflows/file-write.md` | Output naming and write behavior |
| Error handling | `skills/doc-reviewer/workflows/error-handling.md` | Recovery behavior |

### File Structure

```text
skills/doc-reviewer/
├── SKILL.md
├── rubrics/
│   ├── accuracy.md
│   ├── completeness.md
│   ├── clarity.md
│   ├── structure.md
│   ├── staleness.md
│   ├── consistency.md
│   └── _overlap-resolution.md
├── examples/
├── tests/
├── testing/
└── workflows/
```

### Related Skills

| Skill | Relationship |
|-------|--------------|
| `plan-reviewer` | Reviews agent-executable plans rather than user documentation |
| `rule-reviewer` | Reviews rule files instead of project documentation |
| `skill-timing` | Provides the optional timing workflow |

### Output Path Summary

| Scope | Output Pattern |
|-------|----------------|
| single | `reviews/doc-reviews/<name>-<model>-<date>.md` |
| collection | `reviews/summaries/_docs-collection-<model>-<date>.md` |

### Source of Truth

Prefer these files when behavior details matter:

- `skills/doc-reviewer/SKILL.md`
- `skills/doc-reviewer/rubrics/`
- `skills/doc-reviewer/workflows/`
