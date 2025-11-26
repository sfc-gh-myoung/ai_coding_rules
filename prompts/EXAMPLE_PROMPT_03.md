# Example Prompt 03: Minimal but Effective

## The Prompt

```
Task: Add type hints to the data processor functions
Files: src/data_processor.py
```

## What This Helps

AI assistants will automatically:
- Detect `.py` file extension → Load `rules/200-python-core.md`
- Detect "type hints" keyword → Apply Python typing best practices
- Understand this is a code quality improvement task
- Focus on functions in the specified file only

## Why It's Good

**Simple task, clear file:** No ambiguity about what needs to be done or where

**AI can infer Python typing rules needed:** The term "type hints" is specific enough to trigger appropriate typing standards and patterns

**Minimal yet complete:** Provides exactly enough information for AI to execute without over-specifying implementation details

**Single focus:** One file, one improvement type - easy to validate and review
