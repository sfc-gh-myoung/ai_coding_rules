# Foundation (micro-kernel)

## Mandatory Behaviors
- Present a task list before any file modifications
- Make surgical edits only (minimal, targeted changes)
- Run validation (lint, test, format) before marking tasks complete
- Never declare a rule as loaded without a successful read
- Load language-specific rules when modifying code files

## Validation Sequence
1. Detect project automation: Makefile → Taskfile.yml → package.json → direct commands
2. Run validation tools appropriate to the language
3. On failure: revert, report with exact error and fix

## Response Format
```
PRE-FLIGHT:
- [x] Gate 1: Foundation loaded
- [x] Gate 2: Discovery performed
- [x] Gate 3: +N domain rule(s):
  - rules/<name>.md (<reason>)
  (or: none matched)

Task Switch: [FIRST | NO | YES (reason)]
```

## Rule Loading
- The manifest is metadata only — each load_sequence entry with read_required=true MUST be loaded via read_file before citation
- Load domain rules matching file extensions being modified
- Cap: 3 domain rules per response (dependencies don't count against cap)
- If no rules match: proceed with foundation only, note "none matched"

## Communication
- Technical, concise, code-first
- No emojis unless requested
- Show deltas not entire files
