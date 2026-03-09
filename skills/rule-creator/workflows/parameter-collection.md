# Parameter Collection Workflow

## Overview

This workflow handles interactive parameter collection when the user invokes the rule-creator skill without providing all required parameters. It uses the `ask_user_question` tool when available for better UX.

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

| Parameter | Description | Default |
|-----------|-------------|---------|
| `technology_name` | Technology to document | None (must provide) |
| `aspect` | Rule aspect/focus | `core` |

---

## Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `research_mode` | Online or offline research | `online` |
| `context_tier` | Priority tier (Critical/High/Medium/Low) | Auto-determined |
| `timing_enabled` | Enable timing metadata | `false` |

---

## Interactive Collection (ask_user_question)

### Question Set 1: Technology Name

```python
tech_question = {
    "header": "Technology",
    "question": "What technology should the rule document?",
    "multiSelect": False,
    "options": [
        {
            "label": "Python library",
            "description": "e.g., pytest-mock, pandas, FastAPI"
        },
        {
            "label": "Snowflake feature",
            "description": "e.g., Hybrid Tables, Dynamic Tables, Cortex"
        },
        {
            "label": "JavaScript/TypeScript",
            "description": "e.g., React, Next.js, DaisyUI"
        },
        {
            "label": "DevOps/Infra",
            "description": "e.g., Docker, Terraform, GitHub Actions"
        }
    ]
}
# Note: User can select "Something else" to specify custom technology
```

### Question Set 2: Aspect

```python
aspect_question = {
    "header": "Aspect",
    "question": "Which aspect of the technology should the rule cover?",
    "multiSelect": False,
    "options": [
        {
            "label": "core",
            "description": "General best practices and patterns (default)"
        },
        {
            "label": "security",
            "description": "Security considerations and vulnerabilities"
        },
        {
            "label": "testing",
            "description": "Testing strategies and patterns"
        },
        {
            "label": "performance",
            "description": "Performance optimization techniques"
        }
    ]
}
```

### Question Set 3: Optional Parameters

**MANDATORY:** Always prompt for ALL optional parameters. Do NOT silently apply defaults.

```python
optional_questions = [
    {
        "header": "Research",
        "question": "How should research be conducted?",
        "multiSelect": False,
        "options": [
            {"label": "online", "description": "Use web search for current best practices (default)"},
            {"label": "offline", "description": "Use only local knowledge (faster, may be outdated)"}
        ]
    },
    {
        "header": "Context Tier",
        "question": "What priority tier for this rule?",
        "multiSelect": False,
        "options": [
            {"label": "Auto", "description": "Determine automatically based on domain (default)"},
            {"label": "Critical", "description": "Always load - foundational patterns"},
            {"label": "High", "description": "Load for related tasks"},
            {"label": "Medium", "description": "Load when explicitly relevant"}
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
    
    # Always ask technology name first (required)
    if 'technology_name' in missing_params:
        questions.append({
            "header": "Technology",
            "question": "What technology should the rule document?",
            "multiSelect": False,
            "options": [
                {"label": "Python library", "description": "e.g., pytest-mock, pandas, FastAPI"},
                {"label": "Snowflake feature", "description": "e.g., Hybrid Tables, Dynamic Tables, Cortex"},
                {"label": "JavaScript/TypeScript", "description": "e.g., React, Next.js, DaisyUI"},
                {"label": "DevOps/Infra", "description": "e.g., Docker, Terraform, GitHub Actions"}
            ]
        })
    
    # Ask aspect
    questions.append({
        "header": "Aspect",
        "question": "Which aspect of the technology should the rule cover?",
        "multiSelect": False,
        "options": [
            {"label": "core", "description": "General best practices and patterns (default)"},
            {"label": "security", "description": "Security considerations and vulnerabilities"},
            {"label": "testing", "description": "Testing strategies and patterns"},
            {"label": "performance", "description": "Performance optimization techniques"}
        ]
    })
    
    # ALWAYS ask ALL optional parameters - never silently default
    questions.append({
        "header": "Research",
        "question": "How should research be conducted?",
        "multiSelect": False,
        "options": [
            {"label": "online", "description": "Use web search for current best practices (default)"},
            {"label": "offline", "description": "Use only local knowledge (faster, may be outdated)"}
        ]
    })
    
    questions.append({
        "header": "Context Tier",
        "question": "What priority tier for this rule?",
        "multiSelect": False,
        "options": [
            {"label": "Auto", "description": "Determine automatically based on domain (default)"},
            {"label": "Critical", "description": "Always load - foundational patterns"},
            {"label": "High", "description": "Load for related tasks"},
            {"label": "Medium", "description": "Load when explicitly relevant"}
        ]
    })
    
    # Call ask_user_question tool (Batch 1: Technology, Aspect, Research, Context Tier)
    
    # Batch 2: Timing (if needed)
    batch2_questions = [
        {
            "header": "Timing",
            "question": "Enable execution timing?",
            "multiSelect": False,
            "options": [
                {"label": "No", "description": "Skip timing metadata (default)"},
                {"label": "Yes", "description": "Record and embed execution duration"}
            ]
        }
    ]
    
    return collected


def header_to_param(header: str) -> str:
    """Map question header to parameter name."""
    mapping = {
        "Technology": "technology_name",
        "Aspect": "aspect",
        "Research": "research_mode",
        "Context Tier": "context_tier",
        "Timing": "timing_enabled"
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
    
    if 'technology_name' in missing_params:
        print("**Technology Name:**")
        print("  The technology to document")
        print("  Examples: DaisyUI, pytest-mock, Snowflake Hybrid Tables")
        print()
        print("Please specify: technology_name=<NAME>")
        print()
    
    print("**Aspect (optional):**")
    print("  - core: General best practices (default)")
    print("  - security: Security considerations")
    print("  - testing: Testing strategies")
    print("  - performance: Performance optimization")
    print()
    print("Please specify: aspect=<ASPECT>")
    print()
    
    print("**Other Optional Parameters:**")
    print("  - research_mode: online (default) | offline")
    print("  - context_tier: Auto (default) | Critical | High | Medium | Low")
    print("  - timing_enabled: false (default) | true")
    print()
    
    return {}  # Empty - user must re-invoke with params
```

---

## Usage Flow

1. User invokes: `rule-creator` (or "create rule")
2. System detects missing parameters
3. System calls `ask_user_question` with relevant questions (batched, max 4 per call)
4. User answers questions interactively
5. System proceeds with rule creation using collected parameters

**Example interaction:**

```
User: create rule for pytest-mock

System: [ask_user_question tool - Batch 1]
  - Technology? [Confirmed: pytest-mock]
  - Aspect? [core / security / testing / performance]
  - Research? [online / offline]
  - Context Tier? [Auto / Critical / High / Medium]

User: core, online, Auto

System: [ask_user_question tool - Batch 2]
  - Timing? [No / Yes]

User: No

System: Creating rule for pytest-mock (core aspect)...
  - Domain: Python (200-299)
  - Next available: 209
  - Output: rules/209-python-pytest-mock.md
```

---

## Integration Point

Parameter collection executes before Phase 1 (Discovery & Research):

```
Skill Invocation
    ↓
PARAMETER COLLECTION (this workflow)
    ↓
[Optional] Timing Start
    ↓
Phase 1: Discovery & Research
    ↓
Phase 2: Template Generation
    ↓
Phase 3: Content Population
    ↓
Phase 4: Validation & Iteration
    ↓
Phase 5: Indexing
```
