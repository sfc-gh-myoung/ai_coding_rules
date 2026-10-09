---
name: show-rules
description: Display the PRE-FLIGHT diagnostic block showing which rules are loaded. Triggered explicitly by $show-rules for session debugging.
version: 1.0.1
---

# show-rules

> User-invocable skill: `$show-rules`

## Purpose

Display the PRE-FLIGHT diagnostic block showing which rules are currently loaded for this session. This is useful for debugging rule matching, verifying that the correct domain rules were selected, and confirming foundation rule versions.

## Use this skill when

- Triggered explicitly by the user via `$show-rules`
- Used during debugging to inspect which rules the hook injected

## Output Format

When invoked, output the full PRE-FLIGHT block:

```markdown
PRE-FLIGHT:
- [x] Gate 1: Foundation <path>/rules/000-global-core.md - vX.Y.Z
- [x] Gate 2: Manifest provided (hook injection)
- [x] Gate 3: +N domain rule(s):
  - <path>/rules/<name>.md (<reason>) - vX.Y.Z
  (or: none matched)

Task Switch: [FIRST | NO | YES (reason)]
```

## Instructions

1. List all rules that were injected by the hook in the current system context (from the `## Matched Rules for This Request` section).
2. For each rule, read it to obtain the `rule_version` from frontmatter.
3. Render each matched rule using the path form present in the hook-injected context: use absolute plugin paths when the injected absolute-path list is non-empty; use `rules/<name>.md` relative form in a repo-root workflow or when no injected absolute path exists. Join match reasons to paths by filename, not by list position. Apply markdown-safe rendering to any path containing markdown-significant characters: backslash, `|`, `*`, `_`, `[`, `]`, and backtick.
4. Format the PRE-FLIGHT block with accurate Gate 3 entries.
5. If no rules were matched, report `none matched` under Gate 3.

## Notes

- This skill only produces diagnostic output. It does not modify files or execute tasks.
- The PRE-FLIGHT block is not shown by default in normal responses: it is only emitted when this skill is invoked or when explicitly requested by an eval harness.

## Version History

- 1.0.1: Added canonical skill metadata and section naming while preserving the explicit diagnostic-only trigger and path-rendering contract.
