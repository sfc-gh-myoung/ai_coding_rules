# Rule Reviewer Skill (Internal Only)

> **Note:** This skill is **internal-only** and is not deployed to team projects. It remains in the ai_coding_rules source repository for rule maintenance.

A Claude skill for executing agent-centric rule reviews using a standardized rubric and writing results to `reviews/` with no-overwrite safety.

## Overview

This skill automates the complete rule review workflow:
- Validates inputs (target file, date, mode, model)
- Executes review using `PROMPT.md` rubric (colocated in this skill folder)
- Writes results to `reviews/` with automatic suffix for duplicates
- Supports FULL, FOCUSED, and STALENESS review modes

## Quick Start

### Step 1: Load the Skill

Open:
```text
skills/rule-reviewer/SKILL.md
```

### Step 2: Trigger Review

```text
Use the rule-reviewer skill.

target_file: rules/810-project-readme.md
review_date: 2025-12-12
review_mode: FULL
model: claude-sonnet45
```

### Step 3: Verify Output

Check the generated review file:
```bash
ls reviews/810-project-readme-claude-sonnet45-2025-12-12.md
```

## File Structure

```
skills/rule-reviewer/
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

## Review Modes

| Mode | Purpose | Output |
|------|---------|--------|
| **FULL** | Comprehensive evaluation | All dimensions scored, full recommendations |
| **FOCUSED** | Deep-dive on specific area | Single dimension analysis |
| **STALENESS** | Check for outdated content | Version drift, deprecated patterns |

## Output Format

Reviews are written to:
```
reviews/<rule-name>-<model>-<YYYY-MM-DD>.md
```

**No-overwrite safety:** If file exists, uses suffixes:
```
reviews/<rule-name>-<model>-<YYYY-MM-DD>-01.md
reviews/<rule-name>-<model>-<YYYY-MM-DD>-02.md
```

## Confirmation Message

On success:
```
✓ Review complete

OUTPUT_FILE: reviews/810-project-readme-claude-sonnet45-2025-12-12.md
Target: rules/810-project-readme.md
Mode: FULL
Model: claude-sonnet45
```

## Integration with rule-creator

Use rule-reviewer to validate rule-creator output:

1. Create rule using rule-creator skill
2. Run FULL review:
   ```
   target_file: rules/<created-rule>.md
   review_mode: FULL
   ```
3. Verify: score ≥ 7.5/10, no CRITICAL issues

## Version History

- **v1.1.0** (2025-12-15): Enhanced skill structure
  - Added version, author, tags, dependencies to SKILL.md frontmatter
  - Improved description with trigger keywords
  - Added inline validation snippets for quick checks
  - Expanded error-handling.md with 10 error patterns
  - Added edge-cases.md with 10 documented scenarios
  - Added tests/ folder with input, mode, and output test cases
  - Added VALIDATION.md for skill self-validation
  - Cross-referenced with rule-creator for quality assurance
- **v1.0.0** (2024-12-11): Initial release
  - 5-workflow progressive disclosure structure
  - FULL/FOCUSED/STALENESS review modes
  - No-overwrite file safety
  - Model slug normalization

## Troubleshooting

See `workflows/error-handling.md` for common issues and resolutions.

## Validation

See `VALIDATION.md` for skill health checks and regression testing.
