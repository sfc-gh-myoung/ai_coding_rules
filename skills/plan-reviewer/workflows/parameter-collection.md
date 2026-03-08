# Parameter Collection Workflow

## Overview

This workflow handles interactive parameter collection when the user invokes the plan-reviewer skill without providing all required parameters. It uses the `ask_user_question` tool when available for better UX.

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
| `review_mode` | All modes | `FULL` |
| `target_file` | FULL, DELTA | None (must provide) |
| `target_files` | COMPARISON | None (must provide) |
| `review_files` | META-REVIEW | None (must provide) |
| `baseline_review` | DELTA | None (must provide) |
| `model` | All modes | Auto-detect from session |
| `review_date` | All modes | Today's date |
| `execution_mode` | All modes | `parallel` |

---

## Interactive Collection (ask_user_question)

### Question Set 1: Review Mode

```python
mode_question = {
    "header": "Mode",
    "question": "Which review mode do you want to use?",
    "type": "options",
    "multiSelect": False,
    "options": [
        {
            "label": "FULL",
            "description": "Complete review of a single plan (default)"
        },
        {
            "label": "COMPARISON",
            "description": "Compare and rank multiple plans"
        },
        {
            "label": "META-REVIEW",
            "description": "Analyze consistency across multiple reviews"
        },
        {
            "label": "DELTA",
            "description": "Track changes from a prior review"
        }
    ]
}
```

### Question Set 2: Target Files (Mode-Specific)

**For FULL mode:**
```python
target_question_full = {
    "header": "Plan File",
    "question": "Enter the path to the plan file to review",
    "type": "text",
    "defaultValue": "plans/"
}
```

**For COMPARISON mode:**
```python
target_question_comparison = {
    "header": "Plan Files",
    "question": "Enter paths to plan files to compare (comma-separated)",
    "type": "text",
    "defaultValue": "plans/plan1.md, plans/plan2.md"
}
```

**For META-REVIEW mode:**
```python
target_question_meta = {
    "header": "Review Files",
    "question": "Enter paths to review files to analyze (comma-separated)",
    "type": "text",
    "defaultValue": "reviews/plan-reviews/"
}
```

**For DELTA mode:**
```python
target_question_delta = [
    {
        "header": "Current Plan",
        "question": "Enter the path to the current plan file",
        "type": "text",
        "defaultValue": "plans/"
    },
    {
        "header": "Baseline",
        "question": "Enter the path to the prior review file",
        "type": "text",
        "defaultValue": "reviews/plan-reviews/"
    }
]
```

### Question Set 3: Optional Parameters

**MANDATORY:** Always prompt for ALL optional parameters. Do NOT silently apply defaults.

```python
optional_questions = [
    {
        "header": "Execution",
        "question": "Which execution mode?",
        "type": "options",
        "multiSelect": False,
        "options": [
            {"label": "parallel", "description": "Use 8 sub-agents (faster, default)"},
            {"label": "sequential", "description": "Single-agent (for debugging)"}
        ]
    },
    {
        "header": "Timing",
        "question": "Enable execution timing?",
        "type": "options",
        "multiSelect": False,
        "options": [
            {"label": "No", "description": "Skip timing metadata (default)"},
            {"label": "Yes", "description": "Record and embed execution duration"}
        ]
    },
    {
        "header": "Overwrite",
        "question": "Overwrite existing review file if present?",
        "type": "options",
        "multiSelect": False,
        "options": [
            {"label": "No", "description": "Use sequential numbering (-01, -02, etc.) if file exists (default)"},
            {"label": "Yes", "description": "Replace existing file"}
        ]
    },
    {
        "header": "Output Dir",
        "question": "Output directory for review files",
        "type": "text",
        "defaultValue": "reviews/"
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
    
    # Always ask review mode first (determines other questions)
    if 'review_mode' in missing_params:
        questions.append({
            "header": "Mode",
            "question": "Which review mode do you want to use?",
            "type": "options",
            "multiSelect": False,
            "options": [
                {"label": "FULL", "description": "Complete review of a single plan"},
                {"label": "COMPARISON", "description": "Compare and rank multiple plans"},
                {"label": "META-REVIEW", "description": "Analyze consistency across reviews"},
                {"label": "DELTA", "description": "Track changes from prior review"}
            ]
        })
    
    # Ask target file(s) based on mode
    if 'target_file' in missing_params:
        questions.append({
            "header": "Plan File",
            "question": "Enter the path to the plan file to review",
            "type": "text",
            "defaultValue": "plans/"
        })
    
    # ALWAYS ask ALL optional parameters - never silently default
    questions.append({
        "header": "Execution",
        "question": "Which execution mode?",
        "type": "options",
        "multiSelect": False,
        "options": [
            {"label": "parallel", "description": "Use 8 sub-agents (faster, default)"},
            {"label": "sequential", "description": "Single-agent (for debugging)"}
        ]
    })
    
    questions.append({
        "header": "Timing",
        "question": "Enable execution timing?",
        "type": "options",
        "multiSelect": False,
        "options": [
            {"label": "No", "description": "Skip timing metadata (default)"},
            {"label": "Yes", "description": "Record and embed execution duration"}
        ]
    })
    
    questions.append({
        "header": "Overwrite",
        "question": "Overwrite existing review file if present?",
        "type": "options",
        "multiSelect": False,
        "options": [
            {"label": "No", "description": "Use sequential numbering (-01, -02, etc.) if file exists (default)"},
            {"label": "Yes", "description": "Replace existing file"}
        ]
    })
    
    questions.append({
        "header": "Output Dir",
        "question": "Output directory for review files",
        "type": "text",
        "defaultValue": "reviews/"
    })
    
    # Call ask_user_question tool
    if questions:
        responses = ask_user_question(questions=questions)
        
        # Parse responses into collected dict
        for q, r in zip(questions, responses):
            param_name = header_to_param(q['header'])
            collected[param_name] = r
    
    return collected


def header_to_param(header: str) -> str:
    """Map question header to parameter name."""
    mapping = {
        "Mode": "review_mode",
        "Plan File": "target_file",
        "Plan Files": "target_files",
        "Review Files": "review_files",
        "Current Plan": "target_file",
        "Baseline": "baseline_review",
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
    
    collected = {}
    
    print("Missing required parameters. Please provide:")
    print()
    
    if 'review_mode' in missing_params:
        print("**Review Mode:**")
        print("  - FULL: Complete review of a single plan")
        print("  - COMPARISON: Compare and rank multiple plans")
        print("  - META-REVIEW: Analyze consistency across reviews")
        print("  - DELTA: Track changes from prior review")
        print()
        print("Please specify: review_mode=<MODE>")
        print()
    
    if 'target_file' in missing_params:
        print("**Target File:**")
        print("  Path to the plan file to review")
        print("  Example: plans/my-plan.md")
        print()
        print("Please specify: target_file=<PATH>")
        print()
    
    if 'execution_mode' in missing_params:
        print("**Execution Mode (optional):**")
        print("  - parallel: Use 8 sub-agents (default, faster)")
        print("  - sequential: Legacy single-agent")
        print()
        print("Please specify: execution_mode=<MODE>")
        print()
    
    return collected  # Empty - user must re-invoke with params
```

---

## Integration Example

```python
def prepare_review_parameters(user_input: dict) -> dict:
    """Prepare complete parameter set for review execution.
    
    Collects missing parameters interactively or via text prompts.
    """
    
    # Default values
    defaults = {
        'review_date': datetime.today().strftime('%Y-%m-%d'),
        'execution_mode': 'parallel',
        'output_root': 'reviews/',
        'overwrite': False,
        'timing_enabled': False
    }
    
    # Merge user input with defaults
    params = {**defaults, **user_input}
    
    # Determine required params based on mode
    mode = params.get('review_mode', 'FULL')
    required = get_required_params_for_mode(mode)
    
    # Find missing required params
    missing = [p for p in required if p not in params or not params[p]]
    
    if missing:
        # Try interactive collection
        try:
            collected = collect_parameters_interactively(missing)
            params.update(collected)
        except ToolNotAvailableError:
            # Fall back to text prompts
            collect_parameters_text(missing)
            raise ValueError(f"Missing required parameters: {missing}")
    
    return params


def get_required_params_for_mode(mode: str) -> list:
    """Return required parameters for review mode."""
    
    base = ['review_mode', 'model']
    
    mode_specific = {
        'FULL': ['target_file'],
        'COMPARISON': ['target_files'],
        'META-REVIEW': ['review_files'],
        'DELTA': ['target_file', 'baseline_review']
    }
    
    return base + mode_specific.get(mode, [])
```

---

## Usage Flow

1. User invokes: `/plan-reviewer`
2. System detects missing parameters
3. System calls `ask_user_question` with relevant questions
4. User answers questions interactively
5. System proceeds with review using collected parameters

**Example interaction:**

```
User: review plan

System: [ask_user_question tool]
  - Mode? [FULL / COMPARISON / META-REVIEW / DELTA]
  - Plan File? [text input: plans/]
  - Execution? [parallel / sequential]

User: FULL, plans/my-plan.md, parallel

System: Starting FULL review of plans/my-plan.md with parallel execution...
```
