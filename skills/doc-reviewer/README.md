# Documentation Reviewer Skill

A Claude skill for reviewing project documentation against 6 quality dimensions, with cross-reference verification, link validation, and rule-aware baseline compliance checking.

## Overview

This skill automates the complete documentation review workflow:

- Validates inputs (target files, date, mode, scope)
- Discovers default documentation files if none specified
- Executes review using `PROMPT.md` rubric (colocated in this skill folder)
- Verifies code references exist in the codebase
- Validates internal links and flags external URLs
- Checks compliance with project documentation rules (if present)
- Writes results to `reviews/` with automatic suffix for duplicates
- Supports FULL, FOCUSED, and STALENESS review modes
- Supports single (per-file) and collection (consolidated) review scopes

## Quick Start

### Step 1: Load the Skill

Open:

```text
skills/doc-reviewer/SKILL.md
```

### Step 2: Trigger Review

**Basic review (uses defaults):**

```text
Use the doc-reviewer skill.

review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Review specific files:**

```text
Use the doc-reviewer skill.

target_files: [README.md, CONTRIBUTING.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Collection review (consolidated output):**

```text
Use the doc-reviewer skill.

target_files: [README.md, CONTRIBUTING.md, docs/ARCHITECTURE.md]
review_date: 2025-12-16
review_mode: FULL
review_scope: collection
model: claude-sonnet45
```

### Step 3: Verify Output

Check the generated review file:

```bash
ls reviews/README-claude-sonnet45-2025-12-16.md
# Or for collection:
ls reviews/docs-collection-claude-sonnet45-2025-12-16.md
```

## File Structure

```text
skills/doc-reviewer/
├── SKILL.md               # Main skill instructions (Claude Code entrypoint)
├── PROMPT.md              # Review rubric and output format template
├── README.md              # This file - usage documentation
├── VALIDATION.md          # Skill self-validation procedures
├── examples/              # Review mode examples
│   ├── full-review.md         # FULL mode walkthrough
│   ├── focused-review.md      # FOCUSED mode walkthrough
│   ├── staleness-review.md    # STALENESS mode walkthrough
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

| Dimension | Focus | Key Questions |
|-----------|-------|---------------|
| **Accuracy** | Codebase alignment | Do file paths exist? Do commands work? |
| **Completeness** | Coverage | Are all features documented? |
| **Clarity** | User experience | Can new users follow this? |
| **Consistency** | Style compliance | Does it follow project conventions? |
| **Staleness** | Currency | Are versions and links current? |
| **Structure** | Organization | Is navigation logical? |

## Review Modes

| Mode | Purpose | Output |
|------|---------|--------|
| **FULL** | Comprehensive evaluation | All 6 dimensions scored, full verification tables |
| **FOCUSED** | Deep-dive on specific area | Single dimension analysis |
| **STALENESS** | Check for outdated content | Link validation, version drift |

### Focus Areas (for FOCUSED mode)

- `accuracy` - Cross-reference verification
- `completeness` - Coverage analysis
- `clarity` - Readability assessment
- `consistency` - Style compliance
- `staleness` - Link and version checking
- `structure` - Organization review

## Review Scopes

| Scope | Output | Use When |
|-------|--------|----------|
| **single** (default) | One review file per document | Detailed per-file feedback |
| **collection** | One consolidated review | Overall documentation health |

## Output Format

Reviews are written to:

```text
reviews/<doc-name>-<model>-<YYYY-MM-DD>.md
```

**No-overwrite safety:** If file exists, uses suffixes:

```text
reviews/<doc-name>-<model>-<YYYY-MM-DD>-01.md
reviews/<doc-name>-<model>-<YYYY-MM-DD>-02.md
```

## Verification Tables

### Cross-Reference Verification

Lists all code references found in documentation and verifies they exist:

```markdown
| Reference | Type | Location | Exists? | Notes |
|-----------|------|----------|---------|-------|
| `scripts/deploy.py` | file | README:45 | ✅ | — |
| `utils.parse()` | function | docs/API:23 | ❌ | Not found |
```

### Link Validation

Verifies internal links and flags external URLs:

```markdown
| Link | Type | Source | Status | Notes |
|------|------|--------|--------|-------|
| `./docs/API.md` | internal | README:12 | ✅ | — |
| `https://example.com` | external | README:89 | ⚠️ | Manual check |
| `./missing.md` | internal | CONTRIB:34 | ❌ | Not found |
```

## Baseline Compliance

The skill checks for project documentation rules:

1. **`rules/801-project-readme.md`** - README standards
2. **`rules/802-project-contributing.md`** - CONTRIBUTING standards

If found, the review verifies compliance with those rules. Otherwise, uses general best practices.

## Confirmation Message

On success:

```text
✓ Review complete

OUTPUT_FILE: reviews/README-claude-sonnet45-2025-12-16.md
Target: README.md
Mode: FULL
Scope: single
Model: claude-sonnet45

Summary:
- Accuracy: 20/25
- Completeness: 25/25
- Clarity: 16/20
- Structure: 15/15
- Staleness: 6/10
- Consistency: 5/5
Overall: 87/100
Verdict: PUBLISHABLE_WITH_EDITS
```

## Default Target Files

When no `target_files` specified, the skill reviews:

- `./README.md` - Project overview
- `./CONTRIBUTING.md` - Contribution guidelines
- `./docs/*.md` - All docs in docs/ folder

## Deployment

This skill is **deployable** (included when running `task deploy`). After deployment to a project, users can review that project's documentation.

## Version History

- **v1.1.0** (2025-12-16): 100-point scoring system
  - Updated to 100-point scale (from /30)
  - Point allocation: 25/25/20/15/10/5
  - Added PUBLISHABLE verdicts for score interpretation

- **v1.0.0** (2025-12-16): Initial release
  - 6-dimension documentation review rubric
  - Cross-reference verification (code refs in docs)
  - Link validation (internal verified, external flagged)
  - Rule-aware baselines (801, 802 rules when present)
  - Configurable target files with sensible defaults
  - Single and collection review scopes
  - FULL/FOCUSED/STALENESS review modes
  - No-overwrite file safety

## Troubleshooting

See `workflows/error-handling.md` for common issues and resolutions.

## Validation

See `VALIDATION.md` for skill health checks and regression testing.

