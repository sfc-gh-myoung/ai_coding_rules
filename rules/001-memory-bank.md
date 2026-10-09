---
schema_version: v4.0
rule_version: v5.0.0
description: "Memory bank patterns for AI context preservation across sessions. All writes scoped to memory-bank/ only."
last_updated: 2026-10-06
keywords:
  - kw:memory bank
  - kw:context preservation
  - kw:rapid recovery protocol
  - kw:aggressive pruning
  - kw:activeContext.md
  - kw:session initialization
token_budget: ~1000
context_tier: Critical
depends:
  required:
    - 000-global-core.md  # Foundation rule
  optional:
    - 002-rule-governance.md  # Rule authoring standards
    - 003-context-engineering.md  # Attention budget principles
---
# Universal Memory Bank System

## Scope

**What This Rule Covers:**
File-based project context preservation and recovery across sessions. Memory-bank maintenance writes are restricted to `memory-bank/`; this does not authorize changes to project source or external systems.

**When to Load This Rule:**
When the user requests memory-bank initialization or maintenance, or an established project memory bank is used for session recovery.

## Contract

### Inputs and Prerequisites

- User-authorized memory-bank workflow, project requirements and existing files.
- File read/write access within `memory-bank/`; list tools or known-path reads to establish initialization state.
- Current source evidence to verify remembered status and constraints before acting.

### Mandatory

- Read all active memory-bank files at session start when using this system. Load archives only when needed; do not treat historical notes as current authorization.
- Keep one authoritative location per information type. Use headings and actionable lists rather than a narrative diary.
- Scope every memory-bank write to `memory-bank/`. Never overwrite existing files during initialization or replace unrelated source work during recovery.
- Keep `activeContext.md` at most 100 lines, with Quick Start in its first 30 lines: objective, next three steps, blockers and validation signal.
- File budgets: `projectbrief.md` and `productContext.md` at most 120 lines each; `systemPatterns.md` and `techContext.md` at most 150 each; `progress.md` at most 140. Keep the active bank at most 600 lines total.
- Update on architectural decisions, new/resolved blockers, feature completion, three or more changed files, user request, or `activeContext.md` reaching 90 lines.
- Preserve core requirements, architectural decisions and unresolved blockers; do not prune them solely because of age.
- Condense completed work older than seven days to one line, archive completed work older than 30 days, and remove resolved blockers older than 14 days. Remove deleted references and duplicates; condense verbose explanations.
- For concurrent writers, inspect current contents and timestamps before merging. Do not blindly apply last-writer-wins or discard another writer's content.

### Execution Steps

1. Check whether `memory-bank/` and the six core files exist. On an authorized initialization request, create only missing files; never overwrite existing content.
2. Read the active bank and verify the current objective, constraints and blockers against current project evidence.
3. Present the maintenance scope, then update only triggered information in its authoritative file.
4. Archive historical content to `memory-bank/archive/YYYY-MM.md` before removing it from active files; validate the archive write succeeded.
5. Recheck file/total budgets, Quick Start placement, references and recovery usefulness. Report blocked writes or unresolved conflicts without claiming completion.

### Validation

- All maintenance writes stay under `memory-bank/`; existing and concurrent content is preserved.
- Six core files exist when initialization was authorized: activeContext, projectbrief, productContext, systemPatterns, techContext and progress.
- Quick Start is readable within the first 30 lines and states a concrete next action and validation criterion.
- Per-file/total budgets hold; information is nonduplicated and current evidence supports active status.
- Permission denial: report exact path and missing access; do not change permissions or request elevation without approval.
- Disk/write failure: report it and confirm successful persistence before pruning or retrying an uncertain write.
- Corruption: preserve a recoverable copy under `memory-bank/` before authorized repair; reconstruct from verified requirements, not invented history.

## References

- [Anthropic: Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- `003-context-engineering.md` for attention budgets and required-rule preservation.
