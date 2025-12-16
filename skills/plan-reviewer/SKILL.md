---
name: plan-reviewer
description: Review LLM-generated plans for autonomous agent executability. Supports FULL (single plan), COMPARISON (multiple plans ranked), and META-REVIEW (review consistency analysis) modes. Triggers on keywords like "review plan", "compare plans", "plan quality", "meta-review", "plan executability".
version: 1.0.0
author: AI Coding Rules Project
tags: [plan-review, agent-executability, comparison, meta-review, quality-audit, deployable]
dependencies: []
---

# Plan Reviewer

## Purpose

Review LLM-generated plans using `PROMPT.md` (colocated in this skill folder) to ensure autonomous agents can execute them successfully. Evaluates plans across 8 dimensions with weighted scoring optimized for agent executability.

## Use this skill when

- The user asks to **review a plan** file for agent executability
- The user wants to **compare multiple plans** for the same task
- The user wants a **meta-review** to analyze consistency across reviews
- The user asks if a plan is **executable by an autonomous agent**

## Review Modes

| Mode | Purpose | When to Use |
|------|---------|-------------|
| **FULL** | Comprehensive single-plan review | Default; evaluating one plan |
| **COMPARISON** | Rank multiple plans, declare winner | Choosing between competing plans |
| **META-REVIEW** | Analyze review consistency | After multiple LLMs review same document |

## Inputs

### Required (all modes)

- `review_date`: `YYYY-MM-DD`
- `review_mode`: `FULL` | `COMPARISON` | `META-REVIEW`
- `model`: preferred slug (e.g., `claude-sonnet45`)

### Mode-specific

**FULL mode:**
- `target_file`: path to plan file (e.g., `plans/IMPROVE_RULE_LOADING.md`)

**COMPARISON mode:**
- `target_files`: list of 2+ plan file paths
- `task_description`: brief description of what plans should accomplish

**META-REVIEW mode:**
- `target_files`: list of 2+ review files for same document
- `original_document`: (optional) path to the document being reviewed

## Output (required)

Write the full review to `reviews/` using these formats:

**FULL mode:**
`reviews/plan-<plan-name>-<model>-<YYYY-MM-DD>.md`

**COMPARISON mode:**
`reviews/plan-comparison-<model>-<YYYY-MM-DD>.md`

**META-REVIEW mode:**
`reviews/meta-<document-name>-<model>-<YYYY-MM-DD>.md`

**No overwrites:** if file exists, use `-01.md`, `-02.md`, etc.

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
- For COMPARISON mode: All plans must be for the same task.
- For META-REVIEW mode: All reviews must be for the same document.

## Review Dimensions

### Critical Dimensions (75 points)
| Dimension | Points | Focus |
|-----------|--------|-------|
| **Executability** | /20 | Can agent execute without human judgment? |
| **Completeness** | /20 | Are all steps (setup, validation, cleanup) present? |
| **Success Criteria** | /20 | Can agent verify completion programmatically? |
| **Scope** | /15 | Are boundaries and end state explicit? |

### Standard Dimensions (25 points)
| Dimension | Points | Focus |
|-----------|--------|-------|
| Dependencies | /10 | Is execution order explicit? |
| Decomposition | /5 | Is task granularity appropriate? |
| Context | /5 | Is necessary background provided? |
| Risk Awareness | /5 | Are fallbacks documented? |

**Total: /100**

## Agent Executability Verdicts

| Score Range | Verdict | Meaning |
|-------------|---------|---------|
| 90-100 | EXECUTABLE | Agent can execute as-is |
| 80-89 | EXECUTABLE_WITH_REFINEMENTS | Minor refinements recommended |
| 60-79 | NEEDS_REFINEMENT | Significant gaps; agent may fail |
| <60 | NOT_EXECUTABLE | Major rework required |

## Examples

- `examples/full-review.md` - FULL mode walkthrough
- `examples/comparison-review.md` - COMPARISON mode walkthrough
- `examples/meta-review.md` - META-REVIEW mode walkthrough
- `examples/edge-cases.md` - Ambiguous scenarios and resolutions

## Quick Validation Snippets

```python
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

# Validate target_file(s) exist and are markdown
def check_target_files(paths: list[str]) -> tuple[bool, list[str]]:
    """Returns (all_valid, list of error messages)"""
    errors = []
    for path in paths:
        p = Path(path)
        if not p.exists():
            errors.append(f"File not found: {path}")
        elif not path.endswith('.md'):
            errors.append(f"Not a markdown file: {path}")
    return (len(errors) == 0, errors)

# Validate review_date format
def check_date(date_str: str) -> bool:
    """Must be YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Validate review_mode
VALID_MODES = {'FULL', 'COMPARISON', 'META-REVIEW'}
def check_mode(mode: str) -> bool:
    return mode.upper() in VALID_MODES

# Generate output filename (no-overwrite)
def get_output_path(mode: str, name: str, model: str, date: str) -> str:
    """Returns next available filename based on mode"""
    if mode == 'COMPARISON':
        base = f"reviews/plan-comparison-{model}-{date}"
    elif mode == 'META-REVIEW':
        base = f"reviews/meta-{name}-{model}-{date}"
    else:  # FULL
        base = f"reviews/plan-{name}-{model}-{date}"
    
    if not Path(f"{base}.md").exists():
        return f"{base}.md"
    i = 1
    while Path(f"{base}-{i:02d}.md").exists():
        i += 1
    return f"{base}-{i:02d}.md"

# Count ambiguous phrases in plan content
def count_ambiguous_phrases(content: str) -> int:
    """Count phrases requiring human interpretation"""
    patterns = [
        r'\bconsider\b', r'\bif appropriate\b', r'\bas needed\b',
        r'\bwhen necessary\b', r'\bmay need to\b', r'\bshould consider\b',
        r'\bif required\b', r'\bas applicable\b', r'\boptionally\b',
        r'\bmight need\b', r'\bcould be\b', r'\bpossibly\b'
    ]
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, content, re.IGNORECASE))
    return count

# Extract plan name from path
def get_plan_name(path: str) -> str:
    """Extract base name without extension"""
    return Path(path).stem
```

## Related Skills

### Integration with doc-reviewer

Plan files can also be reviewed as documentation using **doc-reviewer**:
- Use doc-reviewer for: accuracy of file references, link validation, general clarity
- Use plan-reviewer for: agent executability, task completeness, scope clarity

### Integration with rule-reviewer

If a plan references rules, use **rule-reviewer** to validate those rules are agent-executable.

## Version History

- **v1.1.0** (2025-12-16): 100-point scoring system
  - Updated to 100-point scale (from /60 weighted)
  - Point allocation: 20/20/20/15/10/5/5/5
  - Updated verdict thresholds for /100 scale

- **v1.0.0** (2025-12-16): Initial release
  - 8-dimension plan review rubric (4 critical, 4 standard)
  - FULL mode for single-plan reviews
  - COMPARISON mode for multi-plan ranking
  - META-REVIEW mode for review consistency analysis
  - Agent Executability Verdicts (EXECUTABLE, NEEDS_REFINEMENT, NOT_EXECUTABLE)
  - Deployable to other projects

