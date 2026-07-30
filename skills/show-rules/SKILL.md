# show-rules

> User-invocable skill: `$show-rules`

## Purpose

Display the PRE-FLIGHT diagnostic block showing which rules are currently loaded for this session. This is useful for debugging rule matching, verifying that the correct domain rules were selected, and confirming foundation rule versions.

## When to Use

- Triggered explicitly by the user via `$show-rules`
- Used during debugging to inspect which rules the hook injected

## Output Format

When invoked, output the full PRE-FLIGHT block:

```markdown
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — vX.Y.Z
- [x] Gate 2: Manifest provided (hook injection)
- [x] Gate 3: +N domain rule(s):
  - rules/<name>.md (<reason>) — vX.Y.Z
  (or: none matched)

Task Switch: [FIRST | NO | YES (reason)]
```

## Instructions

1. List all rules that were injected by the hook in the current system context (from the `## Matched Rules for This Request` section).
2. For each rule, read it to obtain the `rule_version` from frontmatter.
3. Format the PRE-FLIGHT block with accurate Gate 3 entries.
4. If no rules were matched, report `none matched` under Gate 3.

## Notes

- This skill only produces diagnostic output. It does not modify files or execute tasks.
- The PRE-FLIGHT block is not shown by default in normal responses — it is only emitted when this skill is invoked or when explicitly requested by an eval harness.
