# Parameter Collection Workflow

## Overview

This workflow handles interactive parameter collection when the user invokes the rule-reviewer skill without providing all required parameters. It uses the `ask_user_question` tool when available for better UX.

---

## Detection Flow

```
IF required parameters missing:
    IF ask_user_question tool available:
        → Use interactive question prompts
    ELSE:
        → Fall back to text-based prompting
```

---

## Required Parameters

| Parameter | Required For | Default |
|-----------|--------------|---------|
| `target_file` | All modes | None (must provide) |
| `review_date` | All modes | Today's date |
| `review_mode` | All modes | `FULL` |
| `model` | All modes | Auto-detect from session |

---

## Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `output_root` | Output directory | `reviews/` |
| `overwrite` | Replace existing files | `false` |
| `timing_enabled` | Enable timing metadata | `false` |
| `execution_mode` | `parallel` or `sequential` | `parallel` |

---

## Interactive Collection (ask_user_question)

### Question Set 1: Target File

```python
target_question = {
    "header": "Target File",
    "question": "Which rule file do you want to review?",
    "multiSelect": False,
    "options": [
        {
            "label": "rules/*.md",
            "description": "Select a specific rule file"
        },
        {
            "label": "AGENTS.md",
            "description": "Review the AGENTS.md bootstrap file"
        },
        {
            "label": "PROJECT.md",
            "description": "Review the PROJECT.md configuration"
        }
    ]
}
# Note: User can select "Something else" to specify custom path
```

### Question Set 2: Review Mode

```python
mode_question = {
    "header": "Mode",
    "question": "Which review mode do you want to use?",
    "multiSelect": False,
    "options": [
        {
            "label": "FULL",
            "description": "Complete review of all 6 scored dimensions (default)"
        },
        {
            "label": "FOCUSED",
            "description": "Review Actionability + Completeness only"
        },
        {
            "label": "STALENESS",
            "description": "Quick check for outdated content"
        }
    ]
}
```

### Question Set 3: Optional Parameters

**MANDATORY:** Always prompt for ALL optional parameters. Do NOT silently apply defaults.

```python
optional_questions = [
    {
        "header": "Execution",
        "question": "Which execution mode?",
        "multiSelect": False,
        "options": [
            {"label": "parallel", "description": "Use 5 sub-agents (faster, default)"},
            {"label": "sequential", "description": "Single-agent (for debugging)"}
        ]
    },
    {
        "header": "Timing",
        "question": "Enable execution timing?",
        "multiSelect": False,
        "options": [
            {"label": "No", "description": "Skip timing metadata (default)"},
            {"label": "Yes", "description": "Record and embed execution duration"}
        ]
    },
    {
        "header": "Overwrite",
        "question": "Overwrite existing review file if present?",
        "multiSelect": False,
        "options": [
            {"label": "No", "description": "Use sequential numbering (-01, -02, etc.) if file exists (default)"},
            {"label": "Yes", "description": "Replace existing file"}
        ]
    },
    {
        "header": "Output Dir",
        "question": "Output directory for review files",
        "multiSelect": False,
        "options": [
            {"label": "reviews/", "description": "Default output directory"},
            {"label": "../reviews/", "description": "Parent directory"}
        ]
    }
]
```

---

## Implementation Note

Use `ask_user_question` with the Question Sets above, batching max 5 questions per call:
- **Batch 1:** Target File, Mode, Execution, Timing
- **Batch 2:** Overwrite, Output Dir

If `ask_user_question` is unavailable, prompt for each parameter as text, listing the options and defaults shown in the Question Sets above.

**Header-to-parameter mapping:** Target File → `target_file`, Mode → `review_mode`, Execution → `execution_mode`, Timing → `timing_enabled`, Overwrite → `overwrite`, Output Dir → `output_root`

---

## Usage Flow

1. User invokes: `rule-reviewer` (or "review rule")
2. System detects missing parameters
3. System calls `ask_user_question` with relevant questions (batched, max 4 per call)
4. User answers questions interactively
5. System proceeds with review using collected parameters

**Example interaction:**

```
User: review rule

System: [ask_user_question tool - Batch 1]
  - Target File? [rules/*.md / AGENTS.md / PROJECT.md / Something else]
  - Mode? [FULL / FOCUSED / STALENESS]
  - Execution? [parallel / sequential]
  - Timing? [No / Yes]

User: rules/200-python-core.md, FULL, parallel, No

System: [ask_user_question tool - Batch 2]
  - Overwrite? [No / Yes]
  - Output Dir? [reviews/ / ../reviews/ / Something else]

User: No, reviews/

System: Starting FULL review of rules/200-python-core.md...
```

---

## Integration Point

Parameter collection executes as Step 2 in the workflow, after initial validation:

```
Skill Invocation
    ↓
1. Validate inputs (initial check)
    ↓
2. PARAMETER COLLECTION (this workflow)
    ↓
3. [Optional] Timing Start
    ↓
4. Review Execution
    ...
```
