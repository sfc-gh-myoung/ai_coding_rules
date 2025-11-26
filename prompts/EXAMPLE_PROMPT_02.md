# Example Prompt 02: Context-Rich

## The Prompt

```
Task: Optimize the semantic view validation performance in the compliance reporting feature
Files: scripts/rule_validator.py (methods: parse_boilerplate_structure, compare_against_boilerplate)
Current behavior: 84 templates validated in ~25 seconds
Expected: Sub-15 second validation time
Constraints: Maintain singleton caching pattern, must support all 8 compliance criteria
```

## What This Helps

AI assistants will automatically:
- Detect `.py` file extension → Load `rules/200-python-core.md`
- Detect "optimize" and "performance" keywords → Load performance optimization rules
- Understand specific methods to target for optimization
- Know exact performance goals (25s → <15s)
- Respect architectural constraints (singleton caching, compliance criteria)

## Why It's Good

**Performance goal clear:** Provides measurable baseline (25 seconds) and target (<15 seconds) for optimization success

**Files/methods specified:** Pinpoints exact file and methods (parse_boilerplate_structure, compare_against_boilerplate) needing optimization

**Constraints stated:** Explicitly preserves existing patterns (singleton caching) and requirements (8 compliance criteria), preventing breaking changes

**Quantifiable scope:** "84 templates validated" gives AI concrete understanding of workload scale for optimization strategies
