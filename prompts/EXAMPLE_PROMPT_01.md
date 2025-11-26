# Example Prompt 01: Clear and Complete

## The Prompt

```
Task: Fix all Ruff linting errors in Python validation scripts
Files: scripts/rule_validator.py, scripts/index_generator.py
Errors: 9 total (F841 unused variables, UP037 quoted type annotations, W293 whitespace)
```

## What This Helps

AI assistants will automatically:
- Detect `.py` file extensions → Load `rules/200-python-core.md`
- Detect "linting" keyword → Load `rules/201-python-lint-format.md`
- Detect "Ruff" tool → Apply Ruff-specific validation patterns
- Understand exact error types to fix (F841, UP037, W293)

## Why It's Good

**File types clear (.py):** Explicitly lists Python files, triggering Python core rules and linting rules

**Activity clear (linting):** "Fix all Ruff linting errors" keyword triggers specialized linting/formatting rules

**Specific errors listed:** Provides exact error codes (F841, UP037, W293), enabling focused fixes without guesswork

**Actionable scope:** AI knows exactly which files and how many errors to address (9 total across 2 files)
