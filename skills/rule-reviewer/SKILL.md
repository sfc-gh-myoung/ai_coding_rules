---
name: rule-reviewer
description: Execute agent-centric rule reviews (FULL/FOCUSED/STALENESS modes) using the PROMPT.md rubric and write results to reviews/ with no-overwrite safety. Triggers on keywords like "review rule", "audit rule", "check rule quality", "rule staleness", "rule compliance".
version: 1.3.0
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