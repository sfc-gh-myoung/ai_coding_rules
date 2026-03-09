# Parameter Collection Workflow

## Overview

This workflow handles interactive parameter collection when the user invokes the doc-reviewer skill without providing all required parameters. It uses the `ask_user_question` tool when available for better UX.

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
| `review_date` | All modes | Today's date |
| `review_mode` | All modes | `FULL` |
| `model` | All modes | Auto-detect from session |

---

## Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `target_files` | List of file paths | README.md, CONTRIBUTING.md, docs/*.md |
| `review_scope` | `single` or `collection` | `single` |
| `focus_area` | Required if FOCUSED mode | None |
| `output_root` | Output directory | `reviews/` |
| `overwrite` | Replace existing files | `false` |
| `timing_enabled` | Enable timing metadata | `false` |
| `execution_mode` | `parallel` or `sequential` | `parallel` |

---

## Interactive Collection (ask_user_question)

### Question Set 1: Review Mode

```python
mode_question = {
    "header": "Mode",
    "question": "Which review mode do you want to use?",
    "multiSelect": False,
    "options": [
        {
            "label": "FULL",
            "description": "Complete review of all 6 dimensions (default)"
        },
        {
            "label": "FOCUSED",
            "description": "Review specific dimension(s) only"
        },
        {
            "label": "STALENESS",
            "description": "Quick check for outdated content"
        }
    ]
}
```

### Question Set 2: Target Files

```python
target_question = {
    "header": "Target Files",
    "question": "Which documentation files should be reviewed?",
    "multiSelect": False,
    "options": [
        {
            "label": "Project defaults",
            "description": "README.md, CONTRIBUTING.md, docs/*.md"
        },
        {
            "label": "README only",
            "description": "Just README.md"
        },
        {
            "label": "All docs/",
            "description": "Everything in docs/ directory"
        }
    ]
}
# Note: User can select "Something else" to specify custom paths
```

### Question Set 3: Review Scope

```python
scope_question = {
    "header": "Scope",
    "question": "Review files individually or as a collection?",
    "multiSelect": False,
    "options": [
        {
            "label": "single",
            "description": "One review file per documentation file (default)"
        },
        {
            "label": "collection",
            "description": "One consolidated review for all files"
        }
    ]
}
```

### Question Set 4: Focus Area (FOCUSED mode only)

```python
focus_question = {
    "header": "Focus Area",
    "question": "Which dimension(s) to evaluate?",
    "multiSelect": True,
    "options": [
        {"label": "Accuracy", "description": "Documentation matches codebase"},
        {"label": "Completeness", "description": "All features documented"},
        {"label": "Clarity", "description": "User-friendly content"},
        {"label": "Structure", "description": "Logical organization"}
    ]
}
```

### Question Set 5: Optional Parameters

**MANDATORY:** Always prompt for ALL optional parameters. Do NOT silently apply defaults.

```python
optional_questions = [
    {
        "header": "Execution",
        "question": "Which execution mode?",
        "multiSelect": False,
        "options": [
            {"label": "parallel", "description": "Use 6 sub-agents (faster, default)"},
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
def collect_parameters_interactively(missing_params: list, current_mode: str = None) -> dict:
    """Use ask_user_question to collect missing parameters.
    
    Args:
        missing_params: List of parameter names that need to be collected
        current_mode: If known, the review mode (affects which questions to ask)
        
    Returns:
        dict of collected parameter values
    """
    
    collected = {}
    questions = []
    
    # Always ask review mode first (determines other questions)
    if 'review_mode' in missing_params:
        questions.append({
            "header": "Mode",
            "question": "Which review mode do you want to use?",
            "multiSelect": False,
            "options": [
                {"label": "FULL", "description": "Complete review of all 6 dimensions"},
                {"label": "FOCUSED", "description": "Review specific dimension(s) only"},
                {"label": "STALENESS", "description": "Quick check for outdated content"}
            ]
        })
    
    # Ask target files
    if 'target_files' in missing_params or True:  # Always ask
        questions.append({
            "header": "Target Files",
            "question": "Which documentation files should be reviewed?",
            "multiSelect": False,
            "options": [
                {"label": "Project defaults", "description": "README.md, CONTRIBUTING.md, docs/*.md"},
                {"label": "README only", "description": "Just README.md"},
                {"label": "All docs/", "description": "Everything in docs/ directory"}
            ]
        })
    
    # Ask review scope
    questions.append({
        "header": "Scope",
        "question": "Review files individually or as a collection?",
        "multiSelect": False,
        "options": [
            {"label": "single", "description": "One review file per documentation file (default)"},
            {"label": "collection", "description": "One consolidated review for all files"}
        ]
    })
    
    # ALWAYS ask ALL optional parameters - never silently default
    questions.append({
        "header": "Execution",
        "question": "Which execution mode?",
        "multiSelect": False,
        "options": [
            {"label": "parallel", "description": "Use 6 sub-agents (faster, default)"},
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
    # Batch 1: Mode, Target Files, Scope, Execution
    # Batch 2: Timing, Overwrite, Output Dir, (Focus Area if FOCUSED)
    
    return collected


def header_to_param(header: str) -> str:
    """Map question header to parameter name."""
    mapping = {
        "Mode": "review_mode",
        "Target Files": "target_files",
        "Scope": "review_scope",
        "Focus Area": "focus_area",
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
    
    if 'review_mode' in missing_params:
        print("**Review Mode:**")
        print("  - FULL: Complete review of all 6 dimensions")
        print("  - FOCUSED: Review specific dimension(s) only")
        print("  - STALENESS: Quick check for outdated content")
        print()
        print("Please specify: review_mode=<MODE>")
        print()
    
    if 'target_files' in missing_params:
        print("**Target Files:**")
        print("  Comma-separated paths to documentation files")
        print("  Default: README.md, CONTRIBUTING.md, docs/*.md")
        print()
        print("Please specify: target_files=<PATHS>")
        print()
    
    print("**Optional Parameters:**")
    print("  - review_scope: single (default) | collection")
    print("  - focus_area: Required if FOCUSED mode (accuracy, completeness, clarity, structure, staleness, consistency)")
    print("  - execution_mode: parallel (default) | sequential")
    print("  - timing_enabled: false (default) | true")
    print("  - overwrite: false (default) | true")
    print("  - output_root: reviews/ (default)")
    print()
    
    return {}  # Empty - user must re-invoke with params
```

---

## Usage Flow

1. User invokes: `doc-reviewer` (or "review docs")
2. System detects missing parameters
3. System calls `ask_user_question` with relevant questions (batched, max 4 per call)
4. User answers questions interactively
5. If FOCUSED mode selected, prompt for focus_area
6. System proceeds with review using collected parameters

**Example interaction:**

```
User: review docs

System: [ask_user_question tool - Batch 1]
  - Mode? [FULL / FOCUSED / STALENESS]
  - Target Files? [Project defaults / README only / All docs/ / Something else]
  - Scope? [single / collection]
  - Execution? [parallel / sequential]

User: FULL, Project defaults, single, parallel

System: [ask_user_question tool - Batch 2]
  - Timing? [No / Yes]
  - Overwrite? [No / Yes]
  - Output Dir? [reviews/ / ../reviews/ / Something else]

User: No, No, reviews/

System: Starting FULL review of README.md, CONTRIBUTING.md, docs/*.md...
```

---

## Integration Point

Parameter collection executes as Step 2 in the workflow, before input validation:

```
Skill Invocation
    ↓
1. Validate inputs (initial check)
    ↓
2. PARAMETER COLLECTION (this workflow)
    ↓
3. Model Slugging
    ↓
4. [Optional] Timing Start
    ↓
5. Review Execution
    ...
```
