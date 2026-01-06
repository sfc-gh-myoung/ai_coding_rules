---
name: rule-reviewer
description: Execute agent-centric rule reviews (FULL/FOCUSED/STALENESS modes) using the PROMPT.md rubric and write results to reviews/ with no-overwrite safety. Triggers on keywords like "review rule", "audit rule", "check rule quality", "rule staleness", "rule compliance".
version: 1.4.0
---

# Rule Reviewer

## Overview

Execute agent-centric rule reviews that evaluate whether autonomous agents can execute rules without judgment calls. Reviews follow a 6-dimension rubric optimized for Priority 1 compliance (Agent Understanding).

### Design Priority Hierarchy

Evaluates rules per Priority 1 > 2 > 3 hierarchy from `000-global-core.md`.

### When to Use

- Review a rule file under `rules/`
- Verify rule is agent-executable before deployment
- Conduct FULL / FOCUSED / STALENESS review
- Validate rule-creator output for quality assurance

### Inputs

- **target_file**: Path to rule file (e.g., `rules/801-project-readme.md`)
- **review_date**: `YYYY-MM-DD`
- **review_mode**: `FULL` | `FOCUSED` | `STALENESS`
- **model**: Model slug (e.g., `claude-sonnet45`)

### Output

Write review to: `reviews/<rule-name>-<model>-<YYYY-MM-DD>.md`

**No overwrites:** If file exists, increment: `-01.md`, `-02.md`, etc.

## Critical Execution Protocol

### Protocol Violations (FORBIDDEN)

Agents commonly attempt these optimizations. **ALL ARE FORBIDDEN:**

- ❌ **Skipping dimensions** - Must score all 6 in FULL mode
- ❌ **Quick estimates** - Must use rubric, not estimates
- ❌ **Generic recommendations** - Must provide specific examples from rule
- ❌ **Skipping priority checks** - Must count Priority 1 violations
- ❌ **Token-saving shortcuts** - Must read entire rule file
- ❌ **Summary-only reviews** - Must provide detailed dimension analysis
- ❌ **Skipping Agent Execution Test** - Must count blocking issues

### Required Actions

- ✅ Read complete rule file before scoring
- ✅ Run `python scripts/schema_validator.py [target_file]` and parse output
- ✅ Execute Agent Execution Test (count blocking issues)
- ✅ Score all 6 dimensions using rubric
- ✅ Incorporate schema errors into Parsability scoring
- ✅ Apply weighted formula: (25+25+15+15+10+10 = 100)
- ✅ Generate specific recommendations with examples
- ✅ Write complete output with all required sections

### Enforcement

Each review MUST include:
- Schema validation results (CRITICAL/HIGH/MEDIUM counts)
- Agent Execution Test results (blocking issues count)
- All 6 dimension scores with rationales
- Overall score with weighted formula
- Agent Executability Verdict
- Critical issues list (including schema violations)
- Specific recommendations with line numbers

**Verification:** Review file should be 3000-8000 bytes (< 2000 bytes indicates abbreviated review).

**See:** `workflows/review-execution.md` for complete requirements.

## Review Rubric

### Scoring Formula

**Total: 100 points weighted across 6 dimensions:**

| Dimension | Raw | Weight | Points |
|-----------|-----|--------|--------|
| Actionability | X/5 | ×5 | Y/25 |
| Completeness | X/5 | ×5 | Y/25 |
| Consistency | X/5 | ×3 | Y/15 |
| Parsability | X/5 | ×3 | Y/15 |
| Token Efficiency | X/5 | ×2 | Y/10 |
| Staleness | X/5 | ×2 | Y/10 |

### Dimension Summaries

**Critical Dimensions (50 points):**
1. **Actionability (25):** Undefined thresholds, missing branches, ambiguous actions. Gate: >10 undefined thresholds → 1/5 max
2. **Completeness (25):** Error handling, recovery steps, assumptions. Gate: No error handling → 1/5 max

**Important Dimensions (30 points):**
3. **Consistency (15):** Internal/dependency conflicts, example alignment. Gate: Major violations → 1/5 max
4. **Parsability (15):** Schema errors, metadata, structure. Gate: CRITICAL errors ≥1 → 2/5 max

**Standard Dimensions (20 points):**
5. **Token Efficiency (10):** Budget accuracy (±15%), redundancy. Gate: Variance >25% → 2/5 max
6. **Staleness (10):** Tool versions, deprecated patterns, links. Gate: Deprecated recommendations → 1/5 max

**See:** `workflows/review-execution.md` for complete rubrics.

### Agent Execution Test (Pre-Scoring Gate)

Before scoring, answer: **"Can an autonomous agent execute this rule end-to-end without asking for clarification?"**

Count blocking issues:
1. Undefined thresholds ("large", "critical", "appropriate")
2. Missing conditional branches (no explicit else/default)
3. Ambiguous actions (multiple interpretations)
4. Visual formatting (ASCII tables, arrows, diagrams)

**Impact:**
- Blocking issues ≥10: Max score = 60/100 (NEEDS_REFINEMENT)
- Blocking issues ≥20: Max score = 40/100 (NOT_EXECUTABLE)

**See:** `workflows/review-execution.md` section "Agent Execution Test"

### Schema Validation Integration

Run before Parsability scoring:

```bash
python scripts/schema_validator.py [target_file]
```

Parse output for CRITICAL/HIGH/MEDIUM errors.

**Impact on Parsability:**
- CRITICAL errors ≥1: Max 2/5 (6/15)
- HIGH errors ≥3: Max 3/5 (9/15)

All schema errors must appear in review's "Critical Issues" section.

**See:** `workflows/schema-validation.md` for error categorization.

### Mandatory Verification Tables

**Required for scoring justification:**

1. **Threshold Audit** (Actionability) - List all undefined thresholds with proposed fixes
2. **Token Budget Verification** (Token Efficiency) - Compare declared vs actual using `scripts/token_validator.py`
3. **Example-Mandate Alignment** (Consistency) - Verify examples comply with rule's requirements

**See:** `workflows/review-execution.md` section "Verification Tables"

### Verdict Thresholds

| Score | Verdict | Meaning |
|-------|---------|---------|
| 90-100 | EXECUTABLE | Excellent quality |
| 80-89 | EXECUTABLE_WITH_REFINEMENTS | Good, minor fixes |
| 60-79 | NEEDS_REFINEMENT | Needs work |
| 40-59 | NOT_EXECUTABLE | Poor quality |
| <40 | NOT_EXECUTABLE | Rewrite required |

**Critical dimension overrides:**
- Actionability ≤2/5 → Minimum NEEDS_REFINEMENT
- Completeness ≤2/5 → Minimum NEEDS_REFINEMENT
- Both ≤2/5 → NOT_EXECUTABLE

## Workflow

### 1. Input Validation

Validate target_file, review_date, review_mode, model parameters.

**See:** `workflows/input-validation.md`

### 2. Model Slugging

Convert model name to lowercase-hyphenated slug for filenames.

**See:** `workflows/model-slugging.md`

### 3. Review Execution

Execute complete review per rubric. This is the core workflow.

**See:** `workflows/review-execution.md` (detailed rubric, scoring criteria, verification tables)

### 4. File Write (No-Overwrite)

Write review to `reviews/` with automatic incrementing for duplicates.

**See:** `workflows/file-write.md`

### 5. Error Handling

Handle validation failures, file write errors, schema validator failures.

**See:** `workflows/error-handling.md`

## Quick Validation

Input validation snippets (no external dependencies):

```python
import re
from pathlib import Path
from datetime import datetime

# Validate target_file
def check_target_file(path: str) -> tuple[bool, str]:
    p = Path(path)
    if not p.exists():
        return (False, f"File not found: {path}")
    if not path.startswith('rules/') and '/rules/' not in path:
        return (False, "Target must be under rules/")
    if not path.endswith('.md'):
        return (False, "Target must be .md file")
    return (True, "")

# Validate review_date
def check_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Validate review_mode
VALID_MODES = {'FULL', 'FOCUSED', 'STALENESS'}
def check_mode(mode: str) -> bool:
    return mode.upper() in VALID_MODES

# Generate no-overwrite path
def get_output_path(rule_name: str, model: str, date: str) -> str:
    base = f"reviews/{rule_name}-{model}-{date}"
    if not Path(f"{base}.md").exists():
        return f"{base}.md"
    i = 1
    while Path(f"{base}-{i:02d}.md").exists():
        i += 1
    return f"{base}-{i:02d}.md"
```

## Review Modes

**FULL Mode (default):**
- All 6 dimensions evaluated
- Complete weighted scoring
- Minimum 3-5 minutes per rule
- Use for new rules or major revisions

**FOCUSED Mode:**
- 2 dimensions only (Actionability + Completeness)
- 50 points maximum
- Use when specific areas need attention

**STALENESS Mode:**
- 1 dimension only (Staleness)
- Fast check for outdated content
- Use for quarterly/annual audits

**Mode switching FORBIDDEN:** Do NOT downgrade FULL to FOCUSED to save time.

## Examples

- `examples/full-review.md` - Complete FULL mode walkthrough
- `examples/focused-review.md` - Targeted FOCUSED mode
- `examples/staleness-review.md` - Maintenance STALENESS mode
- `examples/edge-cases.md` - Handling unusual scenarios

## Hard Requirements

- Do NOT ask user to manually copy/paste review
- Do NOT print entire review if file writing succeeds
- Run schema validation: `python scripts/schema_validator.py [target_file]`
- Parse validator output for CRITICAL/HIGH/MEDIUM counts
- Include schema errors in "Critical Issues" section
- If file write fails: Print `OUTPUT_FILE: <path>` then full review

## Related Skills

### Validating rule-creator Output

Integrates with **rule-creator** for end-to-end QA:

**Workflow:**
1. Create rule using rule-creator
2. Verify schema validation passed
3. Run FULL review using this skill
4. Verify quality threshold met

**Quality threshold for new rules:**
- Overall score: ≥ 75/100
- No CRITICAL issues
- No HIGH issues in Actionability/Completeness
- Priority 1 violations < 6

See: `skills/rule-creator/SKILL.md`

## References

### Scripts

- `scripts/schema_validator.py` - v3.2 schema validation
- `scripts/token_validator.py` - Accurate token counting (tiktoken)

### Rules

- `rules/000-global-core.md` - Priority hierarchy definition
- `rules/002-rule-governance.md` - Schema requirements
- `rules/002e-agent-optimization.md` - Agent-centric formatting

### Documentation

- `RULES_INDEX.md` - Rule discovery index
- `schemas/rule-schema.yml` - v3.2 schema specification
