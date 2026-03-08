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
            "description": "Complete review of all 7 dimensions (default)"
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
            {"label": "parallel", "description": "Use 7 sub-agents (faster, default)"},
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

## Complete Collection Function

```python
def collect_parameters_interactively(missing_params: list) -> dict:
    """Use ask_user_question to collect missing parameters.
    
    Args:
        missing_params: List of parameter names that need to be collected
        
    Returns:
        dict of collected parameter values
    """
    
    collected = {}
    questions = []
    
    # Always ask target file first (required)
    if 'target_file' in missing_params:
        questions.append({
            "header": "Target File",
            "question": "Which rule file do you want to review?",
            "multiSelect": False,
            "options": [
                {"label": "rules/*.md", "description": "Select a specific rule file"},
                {"label": "AGENTS.md", "description": "Review the AGENTS.md bootstrap file"},
                {"label": "PROJECT.md", "description": "Review the PROJECT.md configuration"}
            ]
        })
    
    # Ask review mode
    if 'review_mode' in missing_params:
        questions.append({
            "header": "Mode",
            "question": "Which review mode do you want to use?",
            "multiSelect": False,
            "options": [
                {"label": "FULL", "description": "Complete review of all 7 dimensions"},
                {"label": "FOCUSED", "description": "Review Actionability + Completeness only"},
                {"label": "STALENESS", "description": "Quick check for outdated content"}
            ]
        })
    
    # ALWAYS ask ALL optional parameters - never silently default
    questions.append({
        "header": "Execution",
        "question": "Which execution mode?",
        "multiSelect": False,
        "options": [
            {"label": "parallel", "description": "Use 7 sub-agents (faster, default)"},
            {"label": "sequential", "description": "Single-agent (for debugging)"}
        ]
    })
    
    questions.append({
        "header": "Timing",
        "question": "Enable execution timing?",
        "multiSelect": False,
        "options": [
            {"label": "No", "description": "Skip timing metadata (default)"},
            {"label": "Yes", "description": "Record and embed execution duration"}
        ]
    })
    
    questions.append({
        "header": "Overwrite",
        "question": "Overwrite existing review file if present?",
        "multiSelect": False,
        "options": [
            {"label": "No", "description": "Use sequential numbering (-01, -02, etc.) if file exists (default)"},
            {"label": "Yes", "description": "Replace existing file"}
        ]
    })
    
    questions.append({
        "header": "Output Dir",
        "question": "Output directory for review files",
        "multiSelect": False,
        "options": [
            {"label": "reviews/", "description": "Default output directory"},
            {"label": "../reviews/", "description": "Parent directory"}
        ]
    })
    
    # Call ask_user_question tool (max 4 questions at a time)
    # Batch 1: Target File, Mode, Execution, Timing
    # Batch 2: Overwrite, Output Dir
    
    return collected


def header_to_param(header: str) -> str:
    """Map question header to parameter name."""
    mapping = {
        "Target File": "target_file",
        "Mode": "review_mode",
        "Execution": "execution_mode",
        "Timing": "timing_enabled",
        "Overwrite": "overwrite",
        "Output Dir": "output_root"
    }
    return mapping.get(header, header.lower().replace(' ', '_'))
```

---

## Text-Based Fallback

When `ask_user_question` is not available:

```python
def collect_parameters_text(missing_params: list) -> dict:
    """Prompt user for missing parameters via text output.
    
    This is used when ask_user_question tool is unavailable.
    """
    
    print("Missing required parameters. Please provide:")
    print()
    
    if 'target_file' in missing_params:
        print("**Target File:**")
        print("  Path to the rule file to review")
        print("  Examples: rules/200-python-core.md, AGENTS.md, PROJECT.md")
        print()
        print("Please specify: target_file=<PATH>")
        print()
    
    if 'review_mode' in missing_params:
        print("**Review Mode:**")
        print("  - FULL: Complete review of all 7 dimensions")
        print("  - FOCUSED: Review Actionability + Completeness only")
        print("  - STALENESS: Quick check for outdated content")
        print()
        print("Please specify: review_mode=<MODE>")
        print()
    
    print("**Optional Parameters:**")
    print("  - execution_mode: parallel (default) | sequential")
    print("  - timing_enabled: false (default) | true")
    print("  - overwrite: false (default) | true")
    print("  - output_root: reviews/ (default)")
    print()
    
    return {}  # Empty - user must re-invoke with params
```

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
