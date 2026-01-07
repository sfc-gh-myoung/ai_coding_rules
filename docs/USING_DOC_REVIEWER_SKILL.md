# Using the Doc Reviewer Skill

**Last Updated:** 2026-01-07

The Doc Reviewer Skill automates comprehensive documentation reviews for your project. It evaluates `README.md`, `CONTRIBUTING.md`, and files in `docs/` against six quality dimensions.

## Background

The doc-reviewer skill runs Agent-Centric Documentation Reviews using the rubrics in `skills/doc-reviewer/rubrics/*.md` and writes results to `reviews/`.

Key behaviors:

- Reviews documentation against 6 dimensions: Accuracy, Completeness, Clarity, Consistency, Staleness, Structure
- Supports three review modes: FULL, FOCUSED, STALENESS
- Computes `OUTPUT_FILE` as:
  - Single scope: `reviews/<doc-name>-<model>-<YYYY-MM-DD>.md`
  - Collection scope: `reviews/project-docs-<model>-<YYYY-MM-DD>.md`
- **No-overwrite safety:** If file exists, uses suffix `-01.md`, `-02.md`, etc.
- Verifies code references exist in the codebase
- Validates internal links and flags external URLs for manual review

## Quick Start

### 1. Load the skill

```text
Load skills/doc-reviewer/SKILL.md
```

### 2. Request a review

**Single file review:**

```text
Use the doc-reviewer skill.

target_files: README.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
review_scope: single
```

**Project documentation collection:**

```text
Use the doc-reviewer skill.

target_files: README.md, CONTRIBUTING.md, docs/ARCHITECTURE.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
review_scope: collection
```

**With execution timing:**

```text
Use the doc-reviewer skill.

target_files: README.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
timing_enabled: true
```

### 3. Output location

The skill writes reviews to the `reviews/` directory:

- Single: `reviews/README-claude-sonnet-45-2026-01-06.md`
- Collection: `reviews/project-docs-claude-sonnet-45-2026-01-06.md`

If the file already exists, suffixes are appended: `-01.md`, `-02.md`, etc.

When `timing_enabled: true`, the output includes a Timing Metadata section with duration, token usage, and cost estimation.

## Review Modes

### FULL Mode (Comprehensive)

Use for new documentation or major revisions. Evaluates all 6 criteria with detailed recommendations.

```text
review_mode: FULL
```

**Best for:**
- Initial documentation setup
- Major version releases
- Quarterly documentation audits

### FOCUSED Mode (Targeted)

Use when specific areas need attention. Specify which criteria to evaluate.

```text
review_mode: FOCUSED
focus_dimensions: Accuracy, Staleness
```

**Best for:**
- Post-refactoring verification
- Addressing specific feedback
- Quick spot-checks

### STALENESS Mode (Periodic Maintenance)

Use for regular maintenance audits. Focuses on Accuracy, Staleness, and Consistency.

```text
review_mode: STALENESS
```

**Best for:**
- Monthly/quarterly maintenance
- Dependency update verification
- Link rot detection

## Review Dimensions

| Dimension | What It Checks |
|-----------|----------------|
| **Accuracy** | Code references exist, examples are executable, API docs match implementation |
| **Completeness** | All essential topics covered, prerequisites documented, error paths explained |
| **Clarity** | Language is accessible, jargon defined, formatting aids readability |
| **Consistency** | Follows project style guide, terminology standardized, patterns uniform |
| **Staleness** | Links valid, versions current, screenshots/examples up-to-date |
| **Structure** | Logical organization, clear hierarchy, easy navigation |

## Mandatory Verification Tables

Reviews include these verification tables to support scoring:

1. **Accuracy Check Table** — Lists code references and verifies they exist in the codebase
2. **Link Validation Table** — Checks internal links, flags external URLs
3. **Style Guide Compliance Check** — Compares against project rules (801, 802) and templates
4. **Readability Assessment** — Qualitative clarity evaluation for target audience

## Configuration

### Default Target Files

When `target_files` is not specified, the skill defaults to:

- `README.md`
- `CONTRIBUTING.md`
- All `.md` files in `docs/`

### Review Scope Options

| Scope | Output | Use Case |
|-------|--------|----------|
| `single` | One review per file | Detailed per-file analysis |
| `collection` | One consolidated review | Project-wide documentation audit |

## Integration with Project Rules

The doc-reviewer skill checks documentation against these project rules if they exist:

- `rules/801-project-readme.md` — README structure and content guidelines
- `rules/802-project-contributing.md` — CONTRIBUTING file standards

If these rules don't exist, the skill uses standard documentation templates as baselines.

## Example Workflows

### New Project Setup

```text
Use the doc-reviewer skill.

target_files: README.md, CONTRIBUTING.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
review_scope: single
```

Review each file individually to establish baseline quality.

### Quarterly Audit

```text
Use the doc-reviewer skill.

review_date: 2026-01-06
review_mode: STALENESS
model: claude-sonnet-45
review_scope: collection
```

Run staleness checks across all project documentation.

### Post-Refactoring Check

```text
Use the doc-reviewer skill.

target_files: docs/ARCHITECTURE.md, docs/API.md
review_date: 2026-01-06
review_mode: FOCUSED
focus_dimensions: Accuracy
model: claude-sonnet-45
review_scope: single
```

Verify code references are still valid after major refactoring.

## FAQ

### Q: What happens if the output file already exists?

**A:** The skill uses no-overwrite safety. It appends suffixes (`-01.md`, `-02.md`, etc.) to avoid overwriting existing reviews.

### Q: What should I pass for `model`?

**A:** Prefer a slug like `claude-sonnet-45`. If you provide a raw model name, the skill normalizes it to a slug before writing the file.

### Q: Can I review non-markdown files?

**A:** No, the skill is designed for `.md` files only. For other documentation formats, convert to Markdown first or use the rubric manually.

### Q: How are code references verified?

**A:** The skill scans documentation for references to functions, classes, files, and commands. It then checks if these exist in the codebase and reports discrepancies in the Accuracy Check Table.

### Q: What if my project doesn't have rules/801 or rules/802?

**A:** The skill falls back to standard documentation templates and best practices. Having project-specific rules improves consistency scoring but isn't required.

### Q: Can I customize the review dimensions?

**A:** In FOCUSED mode, you can specify which dimensions to evaluate. The rubric files in `skills/doc-reviewer/rubrics/` can be customized for project-specific needs.

### Q: How long does a FULL review take?

**A:** Depends on documentation size:
- Single small file (README): 2-5 minutes
- Collection of 5-10 files: 10-20 minutes
- Large documentation set: 20-40 minutes

### Q: Where does the rubric come from?

**A:** The skill uses rubric files in `skills/doc-reviewer/rubrics/` (accuracy.md, completeness.md, clarity.md, structure.md, staleness.md, consistency.md) as the rubric and required output format.

## Support

For detailed documentation:
- **Skill README:** `skills/doc-reviewer/README.md`
- **Workflow guides:** `skills/doc-reviewer/workflows/*.md`
- **Examples:** `skills/doc-reviewer/examples/*.md`
- **Validation tests:** `skills/doc-reviewer/tests/*.md`

