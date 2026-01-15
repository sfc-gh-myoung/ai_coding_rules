# Rule Reviewer Skill (Internal Only)

> **Note:** This skill is **internal-only** and is not deployed to team projects. It remains in the ai_coding_rules source repository for rule maintenance.

A Claude skill for executing agent-centric rule reviews using a standardized rubric and writing results to `reviews/` with no-overwrite safety.

## ⚠️ Execution Integrity Warning

**CRITICAL:** Each review takes 3-5 minutes. This is EXPECTED and REQUIRED.

### Common Agent Shortcuts (ALL FORBIDDEN)

Agents executing this skill may attempt to optimize by:
- Skipping dimension scoring (FORBIDDEN)
- Using quick estimates instead of rubric criteria (FORBIDDEN)
- Generating generic recommendations without examples (FORBIDDEN)
- Skimming rule content to save tokens (FORBIDDEN)
- Abbreviating FULL mode to FOCUSED mode (FORBIDDEN)

**These shortcuts WILL compromise review quality.**

### How to Verify Faithful Execution

**During Execution:**
- Agent reads entire rule file
- All 6 dimensions scored (FULL mode)
- Specific recommendations with examples from rule content

**After Execution:**
- Review file should be 3000-8000 bytes (typical)
- All required sections present (see SKILL.md)
- Dimension scores show rationales (not just numbers)

**Red Flags:**
- ⚠️ Review completes in < 2 minutes
- ⚠️ Review file < 2000 bytes
- ⚠️ Generic recommendations without examples
- ⚠️ Missing dimension scores or rationales

---

## Overview

This skill automates the complete review workflow for agent-executable documents:
- Validates inputs (target file, date, mode, model)
- Executes review using 6-dimension rubric optimized for agent executability
- Writes results to `reviews/` with automatic suffix for duplicates
- Supports FULL, FOCUSED, and STALENESS review modes
- **Supports both rule files (rules/*.md) and project files (AGENTS.md, PROJECT.md)**

## Supported File Types

**Rule Files (rules/*.md):**
- Domain-specific patterns and guidelines
- Full schema validation against `schemas/rule-schema.yml`
- TokenBudget variance check applies

**Project Files (AGENTS.md, PROJECT.md):**
- Bootstrap and configuration documents
- Schema validation skipped (different structure)
- TokenBudget variance skipped (no declared budget)
- Still evaluated for actionability, completeness, consistency, markdown quality, and currency

**Both file types:** Max 100 points, same verdict thresholds

## Quick Start

### Step 1: Load the Skill

**Load the skill file to enable the agent/model to use it:**

```text
skills/rule-reviewer/SKILL.md
```

**How to load:**
- **Claude Code / Cortex Code:** Open or reference `skills/rule-reviewer/SKILL.md` in your conversation
- **Cursor / Other agents:** Load `skills/rule-reviewer/SKILL.md` file which allows the agent to use the skill without "installing" it
- **Manual load:** Use your agent's file reading capability to load the SKILL.md content

**Why this works:** The SKILL.md file contains the complete skill definition. Opening or referencing it makes the skill available to the agent for the current session.

### Step 2: Trigger Review

**Review a rule file:**
```text
Use the rule-reviewer skill.

target_file: rules/810-project-readme.md
review_date: 2025-12-12
review_mode: FULL
model: claude-sonnet-45
```

**Review a project file:**
```text
Use the rule-reviewer skill.

target_file: PROJECT.md
review_date: 2025-12-12
review_mode: FULL
model: claude-sonnet-45
```

### Step 3: Verify Output

Check the generated review file:
```bash
ls reviews/810-project-readme-claude-sonnet-45-2025-12-12.md
```

## Execution Timing

Enable execution timing to measure skill duration and track performance:

```text
Use the rule-reviewer skill.

target_file: rules/810-project-readme.md
review_date: 2025-12-12
review_mode: FULL
model: claude-sonnet-45
timing_enabled: true
```

When enabled, the output includes:
- **Timing Metadata section** in the review file
- **STDOUT summary** with duration, checkpoints, tokens, baseline comparison
- **Real-time anomaly alerts** if duration is suspicious (< 60s or > 600s)

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

**See:** `skills/skill-timing/README.md` for full documentation on timing features, baseline comparison, and analysis tools.

## File Structure

```
skills/rule-reviewer/
├── SKILL.md               # Main skill instructions (Claude Code entrypoint)
├── README.md              # This file - usage documentation
├── rubrics/               # Dimension-specific scoring criteria (progressive disclosure)
│   ├── actionability.md       # Agent executability criteria
│   ├── completeness.md        # Coverage and thoroughness
│   ├── consistency.md         # Style and terminology alignment
│   ├── parsability.md         # Metadata and structure validation
│   ├── staleness.md           # Currency and freshness checks
│   └── token-efficiency.md    # Context window optimization
├── testing/               # Testing and maintenance guides
│   └── TESTING.md             # Skill health checks (for maintainers)
├── examples/              # Review mode examples
│   ├── full-review.md         # FULL mode walkthrough
│   ├── focused-review.md      # FOCUSED mode walkthrough
│   ├── staleness-review.md    # STALENESS mode walkthrough
│   ├── project-file-review.md # Project file review example
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
    ├── schema-validation.md   # Schema error categorization
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

OUTPUT_FILE: reviews/810-project-readme-claude-sonnet-45-2025-12-12.md
Target: rules/810-project-readme.md
Mode: FULL
Model: claude-sonnet-45
```

## Integration with rule-creator

Use rule-reviewer to validate rule-creator output:

1. Create rule using rule-creator skill
2. Run FULL review:
   ```
   target_file: rules/<created-rule>.md
   review_mode: FULL
   ```
3. Verify: score ≥ 75/100, no CRITICAL issues

## Troubleshooting

See `workflows/error-handling.md` for common issues and resolutions.

## Testing

See `testing/TESTING.md` for skill health checks and regression testing (for skill maintainers).
