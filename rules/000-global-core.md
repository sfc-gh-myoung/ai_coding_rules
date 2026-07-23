---
schema_version: v3.5
rule_version: v4.0.0
description: "Foundational operating contract: PRE-FLIGHT gates, surgical edits, validation sequences, and communication standards for all AI agents."
last_updated: 2026-07-15
keywords:
  - kw:surgical edits
  - kw:pre-flight gates
  - kw:validation command sequence
  - kw:context preservation hierarchy
  - kw:foundation operating contract
  - kw:task list confirmation
  - kw:pytest
token_budget: ~2550
context_tier: Critical
depends:
  optional:
    - 001-memory-bank.md  # Context continuity across sessions
    - 002-rule-governance.md  # Rule authoring standards
    - 003-context-engineering.md  # Attention budget management
---
# Global Core Guidelines

> **CRITICAL: DO NOT SUMMARIZE THIS FILE**
>
> This is the foundation rule that defines core patterns for ALL agents. Required
> for every response. If context limits are reached, preserve this file completely.
> Summarize task history or other files first - this foundation must remain accessible.

## Scope

**What This Rule Covers:**
Foundational operating contract for all AI coding assistants, ensuring reliable, safe, and consistent workflows through validation protocols, surgical editing principles, and professional communication standards.

**When to Load This Rule:**
- **ALWAYS** - This is the foundation rule loaded by all agents for every response
- Establishes validation requirements
- Sets professional communication standards
- Guides context window management
- Defines surgical editing principles

> **Note:** This rule assumes the AGENTS.md bootstrap protocol has been completed.
> AGENTS.md defines the bootstrap sequence and task authorization model.
> This rule defines operational behavior: validation commands, surgical edits,
> communication standards, and context management.

## References

### External Documentation

**Best Practices Guides:**
- [Claude Documentation](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) - Prompt engineering techniques
- [Technical Writing Standards](https://developers.google.com/tech-writing) - Professional documentation
- [Conventional Commits](https://www.conventionalcommits.org/) - Standardized commit messages

## Contract

### Inputs and Prerequisites

- Project workspace access
- **Permissions:** File read/write access, shell command execution, tool invocation within workspace scope
- Tool availability (read_file, list_dir, grep, and project-specific tools (as defined in Taskfile.yml, Makefile, or package.json scripts)). If tool discovery fails, list available tools and ask user for guidance.
- Up-to-date rule files (from current branch HEAD)
- User requirements

**Edge Cases:**
- If user request is empty or unclear: Ask for clarification before proceeding
- If no rules match keywords in RULES_INDEX.md (or the discovery manifest is empty): Proceed with foundation rule only, note "No domain rules matched" under Gate 3
- If no files require validation (e.g., documentation-only change): Skip validation sequence, note "No code changes to validate"
- If a rule has already been loaded in this session: Skip re-loading, note "already loaded" under Gate 3

### Mandatory

- **Rules loaded:** List all loaded rules in response
- **Task list:** Present task list before any modifications
- **Validation:** Run language-specific validation (see Validation Command Reference) before marking complete
- **Surgical edits:** Make minimal, targeted changes only

### Forbidden

- **File modifications without presenting task list:** Always present a task list before making changes
- **False rule declaration:** Never declare rule as loaded when `read_file` failed

### Execution Steps

1. Cite foundation on Gate 1 (`— N lines`); list domain/activity rules as Gate 3 sub-bullets (or `none matched`)
2. Present clear task list for user confirmation
3. Perform surgical edits (see Mandatory section above)
4. Validate changes immediately (lint, test, format)
5. Update documentation files that import or reference the modified API, config, or interface (search for imports and usages)

### Output Format

**Required Response Structure:**

See AGENTS.md for complete response header format (PRE-FLIGHT gates).

```markdown
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — N lines
- [x] Gate 2: Searched: [keywords]
- [x] Gate 3: +N domain rule(s):
  - rules/[domain-core].md (technology domain) — N lines
  - rules/[specialized].md (activity-specific) — N lines
  (or: `- [x] Gate 3: none matched`)

Task Switch: [FIRST | NO | YES (reason)]

[Response content: analysis, task list, implementation, or code]
```

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

**Rules Validation:**
- **CRITICAL:** Gate 1 foundation citation present with `— N lines`; domain/activity rules listed as Gate 3 sub-bullets (or `none matched`)
- **CRITICAL:** Never declare rule as loaded when `read_file` failed

**Gate 2 attestation (delegated or inline):** Gate 2 passes when discovery was
performed by EITHER (a) a discovery sub-agent running the rule-loader skill — cite
the runtime-visible spawn evidence, sub-agent `agent_id`, and fenced JSON manifest
with `schema_version: rule-loader-manifest/v1`; OR (b) an inline `grep`/`read_file`
call against `RULES_INDEX.md` you can cite (Step 2B). A Gate 2 claim with
NEITHER spawn evidence + manifest + agent_id NOR a citable inline call is INVALID.
Never claim Gate 2 from prior session context or a summary.

**Code Quality:**
- **CRITICAL:** Surgical edits only (minimal changes)
- **CRITICAL:** Validation executed (lint, format, test) before marking complete
- **CRITICAL:** Language-specific rules loaded for domain work

**Validation error format (on failure):**
```
Validation Failed: [Tool] | Severity: [CRITICAL|HIGH|MEDIUM|LOW] | Location: [file:line]
Error: [exact message] | Fix: [specific action]
```

### Post-Execution Checklist

- [ ] Rules listed explicitly under PRE-FLIGHT Gate 3
- [ ] Task list presented before modifications
- [ ] Surgical edits only
- [ ] Validation executed (lint, test, format)
- [ ] Documentation updated for changed APIs or behavior

## Key Principles

### Surgical Editing Principle (also referred to as "minimal changes")

- Make only the minimal changes required
- Preserve existing code patterns and style (match indentation, naming conventions, import ordering, and formatting of surrounding code within the same file)
- Show deltas, not entire files
- Maintain backward compatibility unless task explicitly requires breaking changes
- **Update version fields (rule files only):** When editing files in `rules/`:
  - Update `RuleVersion` per semantic versioning (MAJOR/MINOR/PATCH per 002b-rule-update.md)
  - Update `LastUpdated` to current date (YYYY-MM-DD format)
- **Update LastUpdated field (other files):** If edited file contains `LastUpdated:`, `**LastUpdated:**`, or `**Last Updated:**`, set value to current date in YYYY-MM-DD format

### Multi-File Task Protocol

**Atomic Changes:** Tightly coupled files (changes that break compilation or tests if applied partially) must be modified together
**Progressive Changes:** Loosely coupled files (independently compilable and testable) may be modified in separate steps

**Rollback:** If validation fails, revert ALL files to original state

**Details:** See 002d-advanced-rule-patterns.md, section "Multi-File Task Patterns"

### Professional Communication

- Act as a senior, pragmatic software engineer
- Be concise and provide code-first solutions
- No emojis unless explicitly requested
- Technical tone consistent with engineering standards

### Validation First

- Validate all changes before marking tasks complete
- Run syntax, linting, formatting, type checking, and unit tests in sequence
- **Automation-first:** Detect project entrypoint: `Makefile` then `Taskfile.yml` then `package.json` scripts then direct commands

### Validation Command Reference

**Preferred:** Use project automation (`validate`, `check`, `ci`, `lint`, `test`) via Makefile/Taskfile.yml/package.json.

**Fallback:** Load language-specific rule:
- **Python:** Load 200-python-core.md
- **SQL:** Load 100-snowflake-core.md
- **Shell:** Load 300-bash-scripting-core.md
- **JS/TS:** Load 420-javascript-core.md / 430-typescript-core.md
- **Go:** Load 600-golang-core.md

## Anti-Patterns and Common Mistakes

### Critical Violations

**Critical Violations:**
- **Rules not listed:** Missing PRE-FLIGHT Gate 3 rule list - Add Gate 3 sub-bullets listing all loaded rules
- **False rule declaration:** Declared rule as loaded when `read_file` failed - STOP, remove false declaration, report failure to user with options (A) Provide correct path, (B) Proceed without rule, (C) Cancel task

**High Priority Violations:**
- **Skipped validation:** Changes made without lint/test - Execute validation before marking complete
- **Language rules missing:** Working with .py/.sql/.sh/.go without domain rules - Load appropriate domain rules

**Language Rule Loading Requirements:**
- **MUST load:** Modifying files, running language-specific tools (pytest, ruff, shellcheck), or making code recommendations
- **MAY skip:** Reading files for context only, listing directories, language-agnostic operations (git, file moves)
- **Cap:** Load at most 3 domain/activity rules per response (ContextTier-priority deferral). `required:` dependency closure is loaded in addition to — and does not count against — the 3 domain/activity-selection cap (this cap counts only LEAF/domain selections), and a `required:` parent is never deferred for token pressure. If loading a mandatory closure would exceed the 20,000-token R4 ceiling, defer LEAF/optional selections first; a still-over-budget mandatory closure is escalated (see Q3-resolution in the rule-loader skill's `workflows/token-budget.md`), never silently trimmed. See the rule-loader skill's `workflows/token-budget.md`.

**Examples:**
- Requires rules: "Run pytest", "Lint this file", "Fix the bug in auth.py"
- No rules needed: "Show project structure", "What files changed?", "Move this folder"

### Common Anti-Patterns

**Anti-Pattern 1: Broad rewrites instead of surgical edits**

**Problem:** Rewriting entire files or functions when only a small change is needed.

**Why It Fails:** Increases risk of introducing bugs; makes diffs hard to review; wastes tokens and time.

**Correct Pattern:**
```python
# Using edit tool for surgical change:
old_string: "    result = old_logic()"
new_string: "    result = new_logic()"
```

**Anti-Pattern 2: No recovery strategy for resource exhaustion**

**Problem:** Tool failures due to resource limits (context overflow, timeout, rate limiting) with no recovery path.

**Why It Fails:** Agent blocks on errors without actionable recovery; user left without guidance.

**Correct Pattern:**

```markdown
Context Overflow:
  Action: Summarize task history, preserve rules (per Context Window Protocol)
  Report: "Context limit reached. Summarizing history, preserving rules."

Tool Timeout:
  Action: Retry once with longer timeout, then report with workaround
  Report: "Tool X timed out. Retrying with 5min timeout. If persistent, try [alternative]."

Rate Limit:
  Action: Wait suggested duration, then retry
  Report: "Rate limited. Waiting 60s before retry."

Memory/Disk Full:
  Action: Report with cleanup suggestions
  Report: "Disk full. Consider: (A) Clear temp files, (B) Reduce output scope."
```

## Context Window Management Protocol

When approaching context limits, preserve rules in this priority order:

**ALWAYS PRESERVE (never summarize):**
1. **AGENTS.md** — Bootstrap protocol
2. **000-global-core.md** — This file (foundation)
3. **Active domain -core.md** — Primary domain rule for current task

**PRESERVE WHEN RELEVANT:** Specialized rules for current task; dependency rules.

**SUMMARIZE FIRST (when context pressure occurs):**
1. Task history (old conversation turns)
2. File contents already analyzed and finished
3. Reference rules (>4000 tokens, lookup-only)
4. Specialized rules not relevant to active task

**NEVER:** Summarize AGENTS.md or 000-global-core.md. Drop active domain -core.md while working in that domain.

For decision tree, -core.md recognition patterns, and ContextTier relationship, see `rules/003-context-engineering.md`.
