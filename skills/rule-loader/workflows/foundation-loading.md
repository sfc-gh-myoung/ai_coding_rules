# Phase 1: Foundation Loading

## Purpose

Load the foundation rule (`000-global-core.md`) which is required for every agent response.

## Algorithm

```
1. Execute: read_file("{rules_path}/000-global-core.md")
2. IF file_not_found OR empty_content:
     OUTPUT "CRITICAL ERROR: Cannot proceed - {rules_path}/000-global-core.md not accessible"
     STOP (do not proceed to Phase 2)
3. IF success:
     Record: "000-global-core.md" in loaded rules list
     Continue to Phase 2
```

## Rules

- Foundation is **always** loaded, regardless of user request content
- Foundation is **never** deferred for token budget reasons (ContextTier: Critical)
- Foundation must be loaded **before** any other rule
- If foundation fails to load, the entire rule-loading process stops

## Token Cost

~4,050 tokens (per 000-global-core.md TokenBudget metadata)

## Failure Modes

| Condition | Action |
|-----------|--------|
| File not found | STOP with critical error |
| Empty content | STOP with critical error |
| read_file tool unavailable | STOP with critical error |

There are no fallback or degraded modes for foundation loading. It is a hard dependency.
