---
schema_version: v4.0
rule_version: v5.0.0
description: "Foundational operating contract: PRE-FLIGHT gates, surgical edits, validation sequences, and communication standards for all AI agents."
last_updated: 2026-10-06
keywords:
  - kw:surgical edits
  - kw:pre-flight gates
  - kw:validation command sequence
  - kw:context preservation hierarchy
  - kw:foundation operating contract
  - kw:task list confirmation
  - kw:pytest
token_budget: ~1600
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
> Foundation rule for ALL agents. Preserve this file before summarizing task history.
> If context limits are reached, summarize old turns first; never drop this rule while working.

## Scope

**What This Rule Covers:**
Foundational operating contract for all AI coding agents: PRE-FLIGHT gates, surgical editing, validation sequences, context-window management, and professional communication standards.

**When to Load This Rule:**
- **ALWAYS** — loaded for every agent response
- Establishes validation requirements, surgical editing principles, and communication standards
- Guides context window management and language-rule loading

**Context preservation priority (when approaching context limits):**
1. Always preserve: injected foundation, `000-global-core.md`, active domain `-core.md`
2. Summarize first: old conversation turns, analyzed files no longer needed, lookup-only reference rules
3. Never summarize or drop `000-global-core.md` or the injected foundation while working

## Contract

### Inputs and Prerequisites

- Project workspace with file read/write access and shell execution
- Tool availability: `read_file`, `list_dir`, `grep`, project automation (Taskfile.yml, Makefile, package.json)
- Rule files from current branch HEAD; user requirements

**Edge cases:**
- Empty or unclear request: ask for clarification before proceeding
- No rules matched by discovery manifest: proceed with foundation only; note "No domain rules matched" under Gate 3
- Rule already loaded this session: skip re-loading; note "already loaded" under Gate 3
- File ownership conflict (permission denied or parallel-agent lock): report the conflict with the file path and offer options — (A) wait and retry, (B) proceed with read-only context, (C) cancel

### Mandatory

- **Rules read:** read all matched rules via `read_file` before applying them; a rule declared loaded when `read_file` failed is a CRITICAL violation — stop, remove the false declaration, report to user with options: (A) provide correct path, (B) proceed without rule, (C) cancel
- **Task list:** present a task list for user confirmation before any modifications
- **Surgical edits:** make only minimal, targeted changes; preserve existing style, indentation, naming, and import ordering of surrounding code
- **Tool authority:** an exposed tool is not permission to call it. Apply the current task's operation and path allowlist before every call; read-only design permits supplied-file reads, not state inspection, checks or writes unless specifically authorized. A denial is a failed attempt, not permission to try another route.
- **Confined workflows:** Generic language/skill-loading requirements do not authorize a forbidden skill, agent, shell or network call. When the task explicitly allows only named in-process tools, use those tools and supplied rule reads; report any unavailable workflow rather than invoking it. SQL in a read-only proposal is not permission to call a SQL-authoring skill outside that allowlist.
- **Design-only boundary:** when instructed to inspect supplied files and propose a design, use file reads only. Do not call `inspect_state` to discover target ownership or availability; report that state unverified. Reserve recovery-state inspection for explicitly authorized interrupted-write recovery, never ordinary design.
- **Language rules:** load the domain rule when modifying files or running language-specific tools
  - MUST load: modifying `.py`/`.sql`/`.sh`/`.go` files, running language tools (pytest, ruff, shellcheck), making code recommendations
  - MAY skip: reading for context only, language-agnostic operations (git, file moves, directory listing)
  - Cap: at most 3 domain/activity rules per response; `required:` closure counts separately and is never deferred for token pressure
- **Version fields:** when editing `rules/` files, increment `rule_version` (semantic versioning per `002b-rule-update.md`) and set `last_updated` to current date (YYYY-MM-DD); update `LastUpdated:`/`**Last Updated:**` in any other edited file similarly
- **Professional tone:** senior-engineer style, concise, code-first; no emojis unless explicitly requested

### Forbidden

- **False rule declaration:** never declare a rule loaded when `read_file` failed
- **Broad rollback:** never overwrite staged, unrelated, or concurrent edits, including within a file this task modified; recover only verified task-owned changes
- **Skip validation:** never skip validation (lint, format, test) because a change appears documentation-only — run well-formedness checks (markdown lint, link check) before marking complete
- **Modifications without task list:** always present task list before making any file changes

### Execution Steps

1. Read all matched rules via `read_file` before applying them
2. Present clear task list for user confirmation
3. Perform surgical edits — change only what is required; match surrounding code style
4. Validate all changes: project automation first, then language-specific fallback (see Validation)
5. Update documentation that references the modified API, config, or interface (search imports and usages)
6. **Recover if validation fails:** inspect the current diff and restore only this task's verified changes from a saved beforeimage when safe. Do not restore a whole file from Git when it also contains staged, unrelated, or concurrent work; report unresolved conflicts.

### Validation

**Automation-first:** detect project entrypoint — `Makefile` then `Taskfile.yml` then `package.json` scripts then direct commands.

**Fallback by language:**
- **Python:** load `200-python-core.md`
- **SQL:** load `100-snowflake-core.md`
- **Shell:** load `300-bash-scripting-core.md`
- **JS/TS:** load `420-javascript-core.md` / `430-typescript-core.md`
- **Go:** load `600-golang-core.md`

**Rules validation:** all rules must be read via `read_file` before being applied.

**PRE-FLIGHT block** (output only when explicitly requested via `$show-rules`):

```markdown
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md - v5.0.0
- [x] Gate 2: Manifest provided (hook injection)
- [x] Gate 3: +N domain rule(s):
  - rules/[domain-core].md (technology domain) - vX.Y.Z
  (or: - [x] Gate 3: none matched)
Task Switch: [FIRST | NO | YES (reason)]
```

**Validation error format:**
```
Validation Failed: [Tool] | Severity: [CRITICAL|HIGH|MEDIUM|LOW] | Location: [file:line]
Error: [exact message] | Fix: [specific action]
```

**Multi-file atomicity:** tightly coupled files (changes that break compilation if partially applied) must be validated and rolled back together; loosely coupled files may be validated independently.

## References

### External Documentation

- [Claude Documentation](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) — Prompt engineering techniques
- [Technical Writing Standards](https://developers.google.com/tech-writing) — Professional documentation
- [Conventional Commits](https://www.conventionalcommits.org/) — Standardized commit messages
- `rules/003-context-engineering.md` — ContextTier decision tree and `-core.md` recognition patterns
