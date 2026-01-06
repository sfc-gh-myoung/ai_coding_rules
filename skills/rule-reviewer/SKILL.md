---
name: rule-reviewer
description: Execute agent-centric rule reviews (FULL/FOCUSED/STALENESS modes) using the PROMPT.md rubric and write results to reviews/ with no-overwrite safety. Triggers on keywords like "review rule", "audit rule", "check rule quality", "rule staleness", "rule compliance".
version: 1.4.0
author: AI Coding Rules Project
tags: [rule-review, quality-audit, compliance, staleness-check, rubric-based, automated-review]
dependencies: []
---

# Rule Reviewer

## Purpose

Run the Agent-Centric Rule Review using `PROMPT.md` (colocated in this skill folder) and write the full review output to `reviews/`.

**Design Priority Hierarchy:** This skill evaluates rules against the priority order defined in `000-global-core.md`:
1. **Priority 1:** Agent Understanding and Execution Reliability (CRITICAL)
2. **Priority 2:** Token and Context Window Efficiency (HIGH)
3. **Priority 3:** Human Readability (TERTIARY)

Rules are scored primarily on whether autonomous agents can execute them without judgment calls.

## Execution Contract (CRITICAL - NON-NEGOTIABLE)

**MANDATORY ENFORCEMENT:**

This skill MUST follow the complete review workflow defined in `PROMPT.md`. The agent executing rule-reviewer is **FORBIDDEN** from:

❌ **FORBIDDEN ACTIONS (Protocol Violations):**
1. **Skipping dimensions** - Do NOT skip any of the 6 dimensions in FULL mode
2. **Abbreviated scoring** - Do NOT use quick estimates instead of proper rubric evaluation
3. **Skipping priority compliance** - Do NOT skip Priority 1/2/3 compliance checks
4. **Incomplete recommendations** - Do NOT generate generic recommendations without specific examples
5. **Token-saving shortcuts** - Do NOT skip reading full rule file to save tokens
6. **Summary-only reviews** - Do NOT create high-level summaries instead of detailed dimension analysis
7. **Skipping validation** - Do NOT skip Agent Execution Test or blocking issues count

✅ **REQUIRED ACTIONS (Protocol Compliance):**
1. **Read complete rule file** - Load entire rule content before evaluation
2. **Execute Agent Execution Test** - Answer blocking issue questions before scoring
3. **Score all 6 dimensions** - Actionability, Completeness, Consistency, Parsability, Token Efficiency, Staleness
4. **Apply weighted scoring** - Use point allocations (25+25+15+15+10+10 = 100)
5. **Generate specific recommendations** - Include actionable fixes with examples
6. **Write complete output** - All sections required per PROMPT.md format
7. **Validate output** - Confirm review file contains all required sections

**Enforcement Mechanism:**

Each review MUST include:
- Agent Execution Test results (blocking issues count)
- All 6 dimension scores with rationales
- Overall score calculation showing weighted formula
- Agent Executability Verdict (EXECUTABLE | EXECUTABLE_WITH_REFINEMENTS | NEEDS_REFINEMENT | NOT_EXECUTABLE)
- Critical issues list with specific examples
- Recommendations with actionable fixes

**Verification:** Review file must be 3000-8000 bytes for typical rules (< 2000 bytes indicates abbreviated review)

**Violation Consequences:**
- Invalid reviews must be regenerated
- User notified of shortcut attempt
- Quality threshold violations (score < 75 for new rules) require full re-review

**Why This Matters:**
- PROMPT.md contains specialized rubric with nuanced scoring criteria
- Dimension weighting reflects Priority 1 > Priority 2 > Priority 3
- Abbreviated reviews lose accuracy and consistency
- Each rule deserves thorough evaluation per established rubric

## Use this skill when

- The user asks to **review** a rule file under `rules/`.
- The user asks for a **FULL / FOCUSED / STALENESS** review using the repository's rubric.
- The user wants to verify a rule is **agent-executable** before deployment.

## Inputs (required)

- `target_file`: path to the `.md` rule file to review (e.g., `rules/801-project-readme.md`)
- `review_date`: `YYYY-MM-DD`
- `review_mode`: `FULL` | `FOCUSED` | `STALENESS`
- `model`: preferred slug (e.g., `claude-sonnet45`)

## Output (required)

Write the full review to:

`reviews/<rule-name>-<model>-<YYYY-MM-DD>.md`

**No overwrites:** if that file already exists, write to:

`reviews/<rule-name>-<model>-<YYYY-MM-DD>-01.md`, then `-02.md`, etc.

## Procedure (progressive disclosure)

Follow these workflows in order:

1. Input validation → `workflows/input-validation.md`
2. Model slugging → `workflows/model-slugging.md`
3. Review execution → `workflows/review-execution.md`
4. File write (no-overwrite) → `workflows/file-write.md`
5. Error handling → `workflows/error-handling.md`

## Hard requirements

- Do not ask the user to manually copy/paste the review into a file.
- Do not print the entire review in chat if file writing succeeds.
- If file writing fails unexpectedly, print:
  - `OUTPUT_FILE: <path>`
  - then the full Markdown review content.

## Examples

- `examples/full-review.md` - FULL review mode walkthrough
- `examples/focused-review.md` - FOCUSED review mode walkthrough
- `examples/staleness-review.md` - STALENESS review mode walkthrough

## Quick Validation Snippets

These inline checks can be run without external dependencies for input validation:

```python
import re
from pathlib import Path
from datetime import datetime

# Validate target_file exists and is a rule
def check_target_file(path: str) -> tuple[bool, str]:
    """Returns (is_valid, error_message)"""
    p = Path(path)
    if not p.exists():
        return (False, f"File not found: {path}")
    if not path.startswith('rules/') and '/rules/' not in path:
        return (False, "Target must be under rules/ directory")
    if not path.endswith('.md'):
        return (False, "Target must be a .md file")
    return (True, "")

# Validate review_date format
def check_date(date_str: str) -> bool:
    """Must be YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Validate review_mode
VALID_MODES = {'FULL', 'FOCUSED', 'STALENESS'}
def check_mode(mode: str) -> bool:
    return mode.upper() in VALID_MODES

# Generate output filename (no-overwrite)
def get_output_path(rule_name: str, model: str, date: str) -> str:
    """Returns next available filename"""
    base = f"reviews/{rule_name}-{model}-{date}"
    if not Path(f"{base}.md").exists():
        return f"{base}.md"
    i = 1
    while Path(f"{base}-{i:02d}.md").exists():
        i += 1
    return f"{base}-{i:02d}.md"
```

## Review Mode Requirements

**FULL Mode (default):**
- All 6 dimensions evaluated
- Complete scoring with weighted formula
- Full recommendations section
- Minimum review time: 3-5 minutes

**FOCUSED Mode:**
- 2 dimensions evaluated (Actionability + Completeness)
- Partial scoring (50 points max)
- Targeted recommendations for specified dimensions only

**STALENESS Mode:**
- 1 dimension evaluated (Staleness only)
- Fast check for outdated content
- Focused on version drift and deprecated patterns

**Mode Switching FORBIDDEN:** Do NOT automatically downgrade FULL to FOCUSED to save time

## Related Skills

### Validating rule-creator Output

This skill integrates with **rule-creator** for end-to-end quality assurance:

**Workflow:**
1. Create rule using rule-creator skill
2. Verify schema validation passed: `python scripts/schema_validator.py rules/<file>.md`
3. Run FULL review using this skill
4. Verify quality threshold met

**Quality threshold for new rules:**
- Overall score: ≥ 75/100
- No CRITICAL issues
- No HIGH issues in Actionability or Completeness dimensions
- Priority 1 violations < 6 (otherwise score capped at 60/100)

See: `skills/rule-creator/SKILL.md`