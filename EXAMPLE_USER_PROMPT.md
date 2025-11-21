# Example User Prompt Templates

This file provides prompt templates for users to get better results from AI assistants using the AI Coding Rules framework.

## Why Use These Templates?

AI assistants work best when you provide:
1. **Clear task description** - What you want to accomplish
2. **File type context** - Which files/languages are involved
3. **Activity keywords** - Type of work (linting, testing, optimization, etc.)

These templates help AI assistants automatically load the correct rules from the 84+ specialized rules in this framework.

---

## Template 1: Basic Task (Most Common)

```
Task: [Your task in 1-2 sentences]
Files: [File paths or types, e.g., app.py, tests/test_api.py, Dockerfile]
```

**Example:**
```
Task: Fix the linting errors reported by Ruff in the validation script
Files: scripts/validate_agent_rules.py, scripts/generate_rules_index.py
```

**What this helps:** AI will detect `.py` files → load Python core + linting rules

---

## Template 2: Performance/Optimization Task

```
Task: [Describe performance issue]
Files: [File paths]
Current behavior: [What's slow/inefficient]
Expected: [What you want to achieve]
```

**Example:**
```
Task: Optimize the Streamlit dashboard's query performance
Files: app.py, utils/queries.py
Current behavior: Page takes 15+ seconds to load, runs same query multiple times
Expected: Sub-2 second load time with proper caching
```

**What this helps:** AI will load Streamlit performance rules + caching patterns

---

## Template 3: Bug Fix/Debugging Task

```
Task: [Describe the bug]
Files: [Affected files]
Error message: [Paste error if available]
Context: [What triggers the bug]
```

**Example:**
```
Task: Fix SettingWithCopyWarning in pandas data processing
Files: src/data_processor.py
Error message: SettingWithCopyWarning: A value is trying to be set on a copy of a slice from a DataFrame
Context: Happens when filtering and updating dataframe in process_sales_data()
```

**What this helps:** AI will load pandas best practices rules + copy/view patterns

---

## Template 4: Feature Implementation

```
Task: [Feature description]
Files: [Files to create/modify]
Requirements:
- [Requirement 1]
- [Requirement 2]
Technology: [Framework/library, e.g., FastAPI, Streamlit, pytest]
```

**Example:**
```
Task: Add user authentication to the FastAPI application
Files: src/api/auth.py (new), src/main.py (modify)
Requirements:
- JWT token-based authentication
- Password hashing with bcrypt
- Login and registration endpoints
Technology: FastAPI, Pydantic, python-jose
```

**What this helps:** AI will load FastAPI core + security rules + Pydantic patterns

---

## Template 5: Testing Task

```
Task: [Testing goal]
Files: [Test files and code under test]
Test type: [unit/integration/end-to-end]
Coverage target: [Optional, e.g., "95%+ coverage"]
```

**Example:**
```
Task: Write pytest unit tests for the data validation module
Files: tests/test_validators.py (new), src/validators.py
Test type: unit tests with fixtures and parametrization
Coverage target: 100% coverage of validator functions
```

**What this helps:** AI will load pytest rules + fixture patterns + testing best practices

---

## Template 6: Documentation Task

```
Task: [Documentation goal]
Files: [Files to document]
Style: [docstring style preference, e.g., Google, NumPy]
```

**Example:**
```
Task: Add comprehensive docstrings to all public functions
Files: src/utils/helpers.py, src/models/user.py
Style: Google-style docstrings with type hints
```

**What this helps:** AI will load documentation rules + docstring standards

---

## Template 7: Refactoring Task

```
Task: [Refactoring goal]
Files: [Files to refactor]
Current issues: [What's wrong with current code]
Constraints: [What must stay the same, e.g., API compatibility]
```

**Example:**
```
Task: Refactor data loading logic to use caching and reduce database queries
Files: src/data/loader.py
Current issues: Multiple redundant database queries, no caching, tight coupling
Constraints: Must maintain existing function signatures for backward compatibility
```

**What this helps:** AI will load performance rules + design pattern rules

---

## Template 8: Security Review/Fix

```
Task: [Security task]
Files: [Files to review/fix]
Concerns: [Specific security concerns if known]
```

**Example:**
```
Task: Security review of user input handling and SQL query construction
Files: src/api/endpoints.py, src/database/queries.py
Concerns: Possible SQL injection, XSS vulnerabilities in Streamlit forms
```

**What this helps:** AI will load security rules + input validation patterns

---

## Template 9: Deployment/CI-CD Task

```
Task: [Deployment goal]
Files: [Config files, Dockerfiles, CI/CD configs]
Target: [Deployment target, e.g., Docker, Kubernetes, Cloud Run]
```

**Example:**
```
Task: Create multi-stage Docker build for production deployment
Files: Dockerfile (new), docker-compose.yml (modify), .dockerignore (new)
Target: Cloud Run deployment with minimal image size
```

**What this helps:** AI will load Docker best practices + deployment patterns

---

## Template 10: Session Continuation

```
Task: Continue from previous session
Previous work: [Brief summary of what was done]
Files: [Files that were being edited]
Next step: [What to do next]
```

**Example:**
```
Task: Continue from previous session
Previous work: Implemented user authentication endpoints, added JWT token generation
Files: src/api/auth.py, src/models/user.py, tests/test_auth.py
Next step: Add password reset functionality and email verification
```

**What this helps:** AI will re-load appropriate rules even after context loss

---

## Quick Reference: Keywords that Trigger Specialized Rules

Use these keywords in your task description to help AI load the right rules:

| Keyword in Task | Triggers Loading |
|----------------|------------------|
| "lint", "format", "code quality" | Linting/formatting rules (e.g., 201-python-lint-format) |
| "test", "pytest", "coverage" | Testing rules (e.g., 206-python-pytest) |
| "optimize", "performance", "slow" | Performance rules (e.g., 103-snowflake-performance-tuning) |
| "security", "authentication", "validate input" | Security rules (e.g., 101c-snowflake-streamlit-security) |
| "deploy", "Docker", "CI/CD" | Deployment rules (e.g., 400-docker-best-practices) |
| "Streamlit", "dashboard", "st." | Streamlit rules (e.g., 101-snowflake-streamlit-core) |
| "FastAPI", "REST API", "endpoint" | FastAPI rules (e.g., 210-python-fastapi-core) |
| "pandas", "DataFrame" | Pandas rules (e.g., 252-pandas-best-practices) |
| "SQL", "query", "Snowflake" | Snowflake SQL rules (e.g., 100-snowflake-core) |
| "document", "docstring", "comment" | Documentation rules (e.g., 204-python-docs-comments) |

---

## Tips for Better Results

### 1. Be Specific About File Types
✅ **Good:** "Fix linting in scripts/validate_agent_rules.py"
❌ **Vague:** "Fix the validation script"

### 2. Include Activity Keywords
✅ **Good:** "Optimize query performance in the Streamlit dashboard"
❌ **Vague:** "Make the app faster"

### 3. Mention Frameworks/Libraries
✅ **Good:** "Add pytest fixtures for FastAPI endpoint testing"
❌ **Vague:** "Add tests"

### 4. Provide Error Messages
✅ **Good:** "Fix F841 error: Local variable 'table_end_idx' is assigned but never used"
❌ **Vague:** "Fix the linting error"

### 5. State Constraints/Requirements
✅ **Good:** "Refactor using @st.cache_data, must maintain backward compatibility"
❌ **Vague:** "Refactor the caching"

---

## Examples of Actual Good Prompts

### Example 1: Clear and Complete
```
Task: Fix all Ruff linting errors in Python validation scripts
Files: scripts/validate_agent_rules.py, scripts/generate_rules_index.py
Errors: 9 total (F841 unused variables, UP037 quoted type annotations, W293 whitespace)
```

**Why it's good:** File types clear (.py), activity clear (linting), specific errors listed

### Example 2: Context-Rich
```
Task: Optimize the semantic view validation performance in the compliance reporting feature
Files: scripts/validate_agent_rules.py (methods: parse_boilerplate_structure, compare_against_boilerplate)
Current behavior: 84 templates validated in ~25 seconds
Expected: Sub-15 second validation time
Constraints: Maintain singleton caching pattern, must support all 8 compliance criteria
```

**Why it's good:** Performance goal clear, files/methods specified, constraints stated

### Example 3: Minimal but Effective
```
Task: Add type hints to the data processor functions
Files: src/data_processor.py
```

**Why it's good:** Simple task, clear file, AI can infer Python typing rules needed

---

## What NOT to Do

### ❌ Too Vague
```
Task: Fix it
```
**Problem:** No file, no context, no activity type

### ❌ Missing File Context
```
Task: Add caching to improve performance
```
**Problem:** What files? What language? Streamlit? API? Database?

### ❌ No Activity Keywords
```
Task: Update the files
```
**Problem:** Update how? Refactor? Fix bugs? Add features? Optimize?

### ❌ Assumes AI Remembers Everything
```
Task: Continue
```
**Problem:** AI loses context between sessions, needs file/task context

---

## Integration with AI Assistants

### For Cursor/Copilot/Cline Users
These AI assistants should automatically detect file types, but you can help by:
1. Mentioning file paths in your prompt
2. Including activity keywords (lint, test, optimize, etc.)
3. Stating frameworks/libraries being used

### For Custom AI Assistants
Include this in your system prompt:
```
When user provides a task, analyze their prompt for:
1. File extensions mentioned → Load language core rules
2. Activity keywords → Search RULES_INDEX.md Keywords column
3. Framework names → Load framework-specific rules
```

---

## Quick Start: Your First Prompt

**If unsure, use this universal template:**

```
Task: [One sentence description]
Files: [File paths or "*.py" or "Dockerfile" etc.]
Context: [Optional: Framework, error message, or constraint]
```

**The AI will:**
1. Detect file types from "Files:" field
2. Extract keywords from "Task:" field
3. Load appropriate rules automatically
4. List loaded rules before starting work

---

## Need Help?

If the AI isn't loading the right rules, you can:
1. **Be more explicit:** "Please load 200-python-core and 201-python-lint-format rules"
2. **Reference the index:** "Check RULES_INDEX.md for pytest-related rules"
3. **Ask first:** "What rules should be loaded for this task?"

The AI should always list loaded rules at the start of its response like:
```
MODE: PLAN

## Rules Loaded
- .cursor/rules/000-global-core.mdc
- .cursor/rules/200-python-core.mdc
- .cursor/rules/201-python-lint-format.mdc
```
