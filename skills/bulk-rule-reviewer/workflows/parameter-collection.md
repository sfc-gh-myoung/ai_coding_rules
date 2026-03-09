# Parameter Collection Workflow

## Overview

This workflow handles interactive parameter collection when the user invokes the bulk-rule-reviewer skill without providing all required parameters. It uses the `ask_user_question` tool when available for better UX.

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
| `filter_pattern` | Glob pattern for rules | `rules/*.md` |
| `skip_existing` | Resume capability | `true` |
| `overwrite` | Replace existing files | `false` |
| `max_parallel` | Concurrent workers (1-10) | `5` |
| `output_root` | Output directory | `reviews/` |
| `timing_enabled` | Enable timing metadata | `false` |

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

### Question Set 2: Filter Pattern

```python
filter_question = {
    "header": "Filter",
    "question": "Which rules should be reviewed?",
    "multiSelect": False,
    "options": [
        {
            "label": "rules/*.md",
            "description": "All rules (default)"
        },
        {
            "label": "rules/1*.md",
            "description": "Snowflake domain only (100-199)"
        },
        {
            "label": "rules/2*.md",
            "description": "Python domain only (200-299)"
        },
        {
            "label": "rules/*-core.md",
            "description": "Core rules only"
        }
    ]
}
# Note: User can select "Something else" to specify custom pattern
```

### Question Set 3: Execution Options

```python
execution_questions = [
    {
        "header": "Skip Existing",
        "question": "Skip rules that already have reviews?",
        "multiSelect": False,
        "options": [
            {"label": "Yes", "description": "Resume capability - skip already reviewed (default)"},
            {"label": "No", "description": "Re-review all rules"}
        ]
    },
    {
        "header": "Parallel",
        "question": "How many parallel workers?",
        "multiSelect": False,
        "options": [
            {"label": "5", "description": "Default - good balance (default)"},
            {"label": "1", "description": "Sequential - for debugging"},
            {"label": "10", "description": "Maximum parallelism"}
        ]
    }
]
```

### Question Set 4: Output Options

**MANDATORY:** Always prompt for ALL optional parameters. Do NOT silently apply defaults.

```python
output_questions = [
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
        "question": "Overwrite existing review files?",
        "multiSelect": False,
        "options": [
            {"label": "No", "description": "Use sequential numbering (-01, -02, etc.) if file exists (default)"},
            {"label": "Yes", "description": "Replace existing files"}
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
    
    # Ask filter pattern
    questions.append({
        "header": "Filter",
        "question": "Which rules should be reviewed?",
        "multiSelect": False,
        "options": [
            {"label": "rules/*.md", "description": "All rules (default)"},
            {"label": "rules/1*.md", "description": "Snowflake domain only (100-199)"},
            {"label": "rules/2*.md", "description": "Python domain only (200-299)"},
            {"label": "rules/*-core.md", "description": "Core rules only"}
        ]
    })
    
    # Ask skip_existing
    questions.append({
        "header": "Skip Existing",
        "question": "Skip rules that already have reviews?",
        "multiSelect": False,
        "options": [
            {"label": "Yes", "description": "Resume capability - skip already reviewed (default)"},
            {"label": "No", "description": "Re-review all rules"}
        ]
    })
    
    # Ask max_parallel
    questions.append({
        "header": "Parallel",
        "question": "How many parallel workers?",
        "multiSelect": False,
        "options": [
            {"label": "5", "description": "Default - good balance (default)"},
            {"label": "1", "description": "Sequential - for debugging"},
            {"label": "10", "description": "Maximum parallelism"}
        ]
    })
    
    # Call ask_user_question tool (Batch 1: Mode, Filter, Skip Existing, Parallel)
    
    # Batch 2: Timing, Overwrite, Output Dir
    batch2_questions = [
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
            "question": "Overwrite existing review files?",
            "multiSelect": False,
            "options": [
                {"label": "No", "description": "Use sequential numbering (-01, -02, etc.) if file exists (default)"},
                {"label": "Yes", "description": "Replace existing files"}
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
    
    return collected


def header_to_param(header: str) -> str:
    """Map question header to parameter name."""
    mapping = {
        "Mode": "review_mode",
        "Filter": "filter_pattern",
        "Skip Existing": "skip_existing",
        "Parallel": "max_parallel",
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
        print("  - FULL: Complete review of all 7 dimensions")
        print("  - FOCUSED: Review Actionability + Completeness only")
        print("  - STALENESS: Quick check for outdated content")
        print()
        print("Please specify: review_mode=<MODE>")
        print()
    
    print("**Optional Parameters:**")
    print("  - filter_pattern: rules/*.md (default) - glob pattern for rule files")
    print("  - skip_existing: true (default) | false - resume capability")
    print("  - max_parallel: 5 (default) - concurrent workers (1-10)")
    print("  - timing_enabled: false (default) | true")
    print("  - overwrite: false (default) | true")
    print("  - output_root: reviews/ (default)")
    print()
    
    return {}  # Empty - user must re-invoke with params
```

---

## Usage Flow

1. User invokes: `bulk-rule-reviewer` (or "review all rules")
2. System detects missing parameters
3. System calls `ask_user_question` with relevant questions (batched, max 4 per call)
4. User answers questions interactively
5. System proceeds with bulk review using collected parameters

**Example interaction:**

```
User: review all rules

System: [ask_user_question tool - Batch 1]
  - Mode? [FULL / FOCUSED / STALENESS]
  - Filter? [rules/*.md / rules/1*.md / rules/2*.md / rules/*-core.md / Something else]
  - Skip Existing? [Yes / No]
  - Parallel? [5 / 1 / 10 / Something else]

User: FULL, rules/*.md, Yes, 5

System: [ask_user_question tool - Batch 2]
  - Timing? [No / Yes]
  - Overwrite? [No / Yes]
  - Output Dir? [reviews/ / ../reviews/ / Something else]

User: No, No, reviews/

System: Starting FULL bulk review of 129 rules with 5 parallel workers...
```

---

## Integration Point

Parameter collection executes before Stage 1 (Discovery):

```
Skill Invocation
    ↓
PARAMETER COLLECTION (this workflow)
    ↓
[Optional] Timing Start
    ↓
Stage 1: Discovery
    ↓
Stage 2: Review Execution
    ↓
Stage 3: Aggregation
    ↓
Stage 4: Summary Report
```
