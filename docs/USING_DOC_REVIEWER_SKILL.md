# Using the Doc Reviewer Skill

**Last Updated:** 2026-03-07

The Doc Reviewer Skill automates comprehensive documentation reviews for your project. It evaluates `README.md`, `CONTRIBUTING.md`, and files in `docs/` against six quality dimensions using a 100-point scoring system.


## Quick Start

### 1. Load the skill

```text
Load skills/doc-reviewer/SKILL.md
```

### 2. Request a review

```text
Use the doc-reviewer skill.

target_files: README.md
review_date: 2026-03-08
review_mode: FULL
model: claude-sonnet-45
```

The skill will evaluate all 6 dimensions and write a scored review.

### 3. Check the output

Reviews are written to `reviews/doc-reviews/<name>-<model>-<date>.md`

On success:

```text
✓ Review complete

OUTPUT_FILE: reviews/doc-reviews/README-claude-sonnet-45-2026-03-08.md
Overall: 85/100
Verdict: GOOD
```


## Review Modes

| Mode | Purpose | When to Use |
|------|---------|-------------|
| **FULL** | Comprehensive 6-dimension evaluation | New docs, major revisions, quarterly audits |
| **FOCUSED** | Targeted dimension review | Post-refactoring, specific feedback |
| **STALENESS** | Accuracy, Staleness, Consistency only | Monthly maintenance, link rot detection |

### FULL Mode

```text
review_mode: FULL
```

### FOCUSED Mode

```text
review_mode: FOCUSED
focus_dimensions: Accuracy, Staleness
```

**Available Focus Areas:**
- `accuracy` - Cross-reference verification
- `completeness` - Coverage analysis
- `clarity` - Readability assessment
- `consistency` - Style compliance
- `staleness` - Link and version checking
- `structure` - Organization review

### STALENESS Mode

```text
review_mode: STALENESS
```


## Understanding Your Results

### Verdicts

| Score | Verdict | Action |
|-------|---------|--------|
| 90-100 | **EXCELLENT** | Publication-ready |
| 80-89 | **GOOD** | Minor improvements recommended |
| 60-79 | **NEEDS_WORK** | Significant gaps; major revision needed |
| <60 | **POOR** | Substantial rework required |

### Scoring Dimensions

Documentation is scored across 6 dimensions with weighted points:

**Critical Dimensions (50 points)** — Factual accuracy and coverage:

| Dimension | Points | Key Question |
|-----------|--------|--------------|
| Accuracy | 25 | Do code references exist? Are examples executable? |
| Completeness | 25 | Are all essential topics covered? |

**Important Dimensions (35 points)** — Readability and organization:

| Dimension | Points | Key Question |
|-----------|--------|--------------|
| Clarity | 20 | Is language accessible? Is jargon defined? |
| Structure | 15 | Is organization logical? Is navigation easy? |

**Standard Dimensions (15 points)** — Maintenance and consistency:

| Dimension | Points | Key Question |
|-----------|--------|--------------|
| Staleness | 10 | Are links valid? Are versions current? |
| Consistency | 5 | Does it follow project style guide? |

**Scoring Formula:** `Raw (0-10) × (Weight / 2) = Points`

### Verification Tables

Reviews include audit tables to support scoring:

| Table | Purpose |
|-------|---------|
| **Accuracy Verification** | Code references (file paths, commands, functions) verified against codebase |
| **Completeness Table** | Features documented vs undocumented |
| **Clarity Table** | Jargon audit, concept order, new user accessibility |
| **Structure Table** | Section order, heading hierarchy, navigation |
| **Staleness Table** | Link validation, tool versions, deprecated patterns |
| **Consistency Table** | Formatting, terminology, code style compliance |

**Cross-Reference Verification Example:**

```markdown
| Reference | Type | Location | Exists? | Notes |
|-----------|------|----------|---------|-------|
| `scripts/deploy.py` | file | README:45 | Yes | — |
| `utils.parse()` | function | docs/API:23 | No | Not found |
```

**Link Validation Example:**

```markdown
| Link | Type | Source | Status | Notes |
|------|------|--------|--------|-------|
| `./docs/API.md` | internal | README:12 | Valid | — |
| `https://example.com` | external | README:89 | Manual | Manual check required |
| `./missing.md` | internal | CONTRIB:34 | Invalid | Not found |
```


## Advanced Usage

### Custom Output Directory

```text
output_root: quarterly-audit/
```

Writes to `quarterly-audit/doc-reviews/` instead of default `reviews/doc-reviews/`. The skill auto-creates directories and normalizes trailing slashes. Relative paths including `../` are supported.

### Execution Timing

```text
timing_enabled: true
```

Adds timing metadata to output (duration, token usage, cost estimation).

**Timing thresholds:**
- <30 seconds: Warning (unusually fast for thorough review)
- <60 seconds: Warning (may indicate shortcuts)
- >1200 seconds: Warning (possible issue)

**Example timing metadata in output:**

```markdown
## Timing Metadata

| Metric | Value |
|--------|-------|
| Run ID | `a1b2c3d4e5f67890` |
| Duration | 2m 30s (150.5s) |
| Model | claude-sonnet-45 |
| Tokens | 12,300 (8,500 in / 3,800 out) |
| Cost | ~$0.03 |
```

**See:** `docs/USING_SKILL_TIMING_SKILL.md` for full documentation on timing features, baseline comparison, and analysis tools.

### Execution Modes

Unlike plan-reviewer which uses parallel sub-agents, doc-reviewer runs sequentially through each dimension. This is by design—documentation review requires cross-referencing between sections that benefits from sequential analysis.

| Mode | Speed | Use Case |
|------|-------|----------|
| **sequential** (default) | ~2-20 min | All reviews (varies by file count) |

### Review Scope Options

| Scope | Output | Use Case |
|-------|--------|----------|
| `single` | One review per file | Detailed per-file analysis |
| `collection` | One consolidated review | Project-wide documentation audit |

**Collection scope example:**

```text
target_files: README.md, CONTRIBUTING.md, docs/ARCHITECTURE.md
review_scope: collection
```

Output: `reviews/summaries/_docs-collection-<model>-<date>.md`

### Default Target Files

When `target_files` is not specified:
- `README.md`
- `CONTRIBUTING.md`
- All `.md` files in `docs/`

### Example Workflows

#### New Project Setup

```text
target_files: README.md, CONTRIBUTING.md
review_mode: FULL
review_scope: single
```

Review each file individually to establish baseline quality.

#### Quarterly Audit

```text
review_mode: STALENESS
review_scope: collection
```

Run staleness checks across all project documentation.

#### Post-Refactoring Check

```text
target_files: docs/ARCHITECTURE.md, docs/API.md
review_mode: FOCUSED
focus_dimensions: Accuracy
```

Verify code references are still valid after major refactoring.


## FAQ

### What happens if the output file already exists?

The skill uses no-overwrite safety. It appends suffixes (`-01.md`, `-02.md`, etc.) to avoid overwriting existing reviews.

### What should I pass for `model`?

Prefer a slug like `claude-sonnet-45`. If you provide a raw model name, the skill normalizes it to a slug before writing the file.

### Can I review non-markdown files?

No, the skill is designed for `.md` files only. For other documentation formats, convert to Markdown first or use the rubric manually.

### How are code references verified?

The skill scans documentation for references to functions, classes, files, and commands. It checks if these exist in the codebase and reports discrepancies in the Accuracy Verification Table.

### Can I customize the review dimensions?

In FOCUSED mode, specify which dimensions to evaluate. The rubric files in `skills/doc-reviewer/rubrics/` can be customized for project-specific needs.

### How long does a FULL review take?

| Scope | Duration |
|-------|----------|
| Single small file (README) | 2-5 minutes |
| Collection of 5-10 files | 10-20 minutes |
| Large documentation set | 20-40 minutes |

### Where does the rubric come from?

The skill uses rubric files in `skills/doc-reviewer/rubrics/` (accuracy.md, completeness.md, clarity.md, structure.md, staleness.md, consistency.md) plus `_overlap-resolution.md` for deterministic scoring.

### What's the difference between doc-reviewer and plan-reviewer?

- **doc-reviewer**: Human readability, accuracy, link validation, style consistency
- **plan-reviewer**: Agent executability, task completeness, scope clarity

Use doc-reviewer for documentation humans will read. Use plan-reviewer for plans an agent will execute.


## Reference

### Architecture

```
User Request
│
├── Phase 1: Parameter Collection
│   ├── Validate target_files
│   ├── Determine review_mode
│   └── Compute output path
│
├── Phase 2: Rubric Loading
│   ├── Load dimension rubrics
│   └── Load overlap resolution
│
├── Phase 3: Document Analysis
│   ├── Scan for code references
│   ├── Validate internal links
│   └── Flag external URLs
│
├── Phase 4: Dimension Scoring
│   ├── Accuracy (25pts)
│   ├── Completeness (25pts)
│   ├── Clarity (20pts)
│   ├── Structure (15pts)
│   ├── Staleness (10pts)
│   └── Consistency (5pts)
│
└── Phase 5: Report Generation
    ├── Create verification tables
    ├── Calculate weighted score
    └── Write review file
```

### Key Workflows

| Workflow | File | Purpose |
|----------|------|---------|
| Parameter collection | `workflows/parameter-collection.md` | Interactive input handling |
| Score aggregation | `workflows/score-aggregation.md` | Combine dimension results |
| Overlap validation | `workflows/overlap-validator.md` | Prevent double-counting |
| Error handling | `workflows/error-handling.md` | Recovery and troubleshooting |

### File Structure

```text
skills/doc-reviewer/
├── SKILL.md               # Main skill (entrypoint)
├── rubrics/               # Dimension scoring criteria
│   ├── accuracy.md
│   ├── completeness.md
│   ├── clarity.md
│   ├── structure.md
│   ├── staleness.md
│   ├── consistency.md
│   └── _overlap-resolution.md
├── examples/              # Workflow examples
├── tests/                 # Test cases
├── testing/               # Skill maintenance guides
└── workflows/             # Step-by-step guides
```

### Integration with Other Skills

| Skill | Relationship |
|-------|--------------|
| **plan-reviewer** | doc-reviewer for human docs, plan-reviewer for agent-executable plans |
| **rule-reviewer** | Review rule files for accuracy |
| **skill-timing** | Track review duration metrics |

### Output Paths

| Mode/Scope | Output Path |
|------------|-------------|
| Single file | `reviews/doc-reviews/<name>-<model>-<date>.md` |
| Collection | `reviews/summaries/_docs-collection-<model>-<date>.md` |
| Custom root | `<output_root>/doc-reviews/<name>-<model>-<date>.md` |

### Integration with Project Rules

The skill checks documentation against these project rules if they exist:

- `rules/801-project-readme.md` — README structure and content guidelines
- `rules/802-project-contributing.md` — CONTRIBUTING file standards

If these rules don't exist, the skill uses standard documentation templates.

### Deployment

This skill is **deployable** (included when running `task deploy`). After deployment to a project, users can review that project's documentation.

### Support

- **Workflow guides:** `skills/doc-reviewer/workflows/*.md`
- **Examples:** `skills/doc-reviewer/examples/*.md`
- **Validation tests:** `skills/doc-reviewer/tests/*.md`
- **Troubleshooting:** `skills/doc-reviewer/workflows/error-handling.md`
- **Skill maintenance:** `skills/doc-reviewer/testing/TESTING.md`
