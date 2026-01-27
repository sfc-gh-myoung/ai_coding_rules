# Universal Memory Bank System

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.2
**LastUpdated:** 2026-01-27
**Keywords:** memory bank, context, session recovery, progress tracking, compaction, rapid recovery
**TokenBudget:** ~5000
**ContextTier:** Critical
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Memory bank patterns for AI context preservation across sessions. All writes scoped to `memory-bank/` only.

**When to Load:**
- Implementing/maintaining memory bank systems
- Managing project context across session resets
- Setting up context preservation for AI agents

**Scope Boundary:** Write operations to `memory-bank/` directory ONLY.

## References

### Dependencies
**Must Load First:** 000-global-core.md

**Related:** 002-rule-governance.md, 003-context-engineering.md

### Related Examples

- **examples/001-memory-bank-templates-example.md** - Complete file templates with size budgets

### External Documentation
- [Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

## Contract

### Inputs and Prerequisites
- Project context files
- Clear documentation structure

### Mandatory
- Read ALL memory bank files at session start
- Single source of truth per information type
- ALL writes scoped to `memory-bank/` directory

### Forbidden
- Writing files outside `memory-bank/`
- Duplicating information across contexts
- Unstructured narrative documentation
- Skipping initialization check before first write

### Execution Steps
1. Initialize if needed (check `memory-bank/` exists)
2. Read ALL memory bank files at session start
3. Maintain single source of truth
4. Update when triggers met
5. Prune outdated content aggressively
6. Structure for rapid recovery

### Output Format
Structured documentation with clear sections, minimal redundancy, forward-looking focus.

### Validation
- `memory-bank/` exists
- No writes outside directory
- Quick Start in first 30 lines of activeContext.md
- AI can resume work effectively

### Design Principles
- **Rapid Recovery:** Productive within 20-30 lines
- **Signal Maximization:** Every line actionable
- **Zero Redundancy:** Each info in exactly one place
- **Aggressive Pruning:** Remove outdated content ruthlessly
- **Context Rot Awareness:** As context grows, attention degrades

### Post-Execution Checklist
- [ ] All files within size budgets
- [ ] All writes under `memory-bank/`
- [ ] activeContext.md updated
- [ ] No information duplication
- [ ] Quick start accessible

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Context Pollution
```markdown
# BAD: Verbose unfocused log
## Session Log
Yesterday we discussed auth. John suggested OAuth2...
[50 lines of narrative]
```
**Problem:** Context rot - as context grows, attention degrades.

**Correct Pattern:**
```markdown
# GOOD: Focused actionable
## Quick Start
- Primary: Implement user auth
- Blocked: Waiting on API keys
- Next: Write unit tests
```

### Anti-Pattern 2: Stale Memory Without Pruning
**Problem:** Memory becomes archaeological record, AI wastes tokens on irrelevant history.

**Correct Pattern:**
1. After task: Remove details, keep outcome summary
2. Weekly: Archive older content
3. Per session: Verify activeContext.md ≤100 lines

## Core Files and Size Budgets

**activeContext.md (≤100 lines) - MOST CRITICAL:**
- Quick Start (lines 1-30): objective, next 3 steps, blockers, validation
- Current work focus
- Session change log (≤5 entries)

**projectbrief.md (≤120 lines):** Foundation, scope, requirements

**productContext.md (≤120 lines):** Why project exists, user goals

**systemPatterns.md (≤150 lines):** Architecture, design patterns

**techContext.md (≤150 lines):** Stack, constraints, commands

**progress.md (≤140 lines):** Status, known issues, roadmap

**Total: ≤600 lines**

## Quick Start Template

```markdown
## Quick Start
**Current Objective:** [Concise statement]
**Next 3 Steps:**
1. [Action]
2. [Action]
3. [Action]
**Active Blockers:** [List or "None"]
**Validation Signal:** [Success criteria]
```

## Pruning Rules

**Temporal:**
- Completed work (>7 days): Condense to 1-line
- Completed work (>30 days): Archive to `archive/YYYY-MM.md`
- Resolved blockers (>14 days): Remove

**Content:**
- Deleted file references: Remove
- Duplicate updates: Keep most recent
- Verbose explanations (>5 lines): Condense to bullets

**Preservation Exceptions:**
- Architectural decisions: Keep in systemPatterns.md
- Core requirements: Keep in projectbrief.md
- Active unresolved blockers: Keep full details

## Context Update Triggers

Update when:
- ≥3 files modified in task
- Architecture decision made
- Blocker resolved/discovered
- Feature completed
- activeContext.md ≥90 lines
- User requests "update memory bank"

## Initialization Protocol

**Trigger:** User says "initialize memory bank"

**Creates:**
- `memory-bank/` directory
- Core template files (activeContext, projectbrief, productContext, systemPatterns, techContext, progress)
- `memory-bank/archive/` (optional)

**Idempotency:**
- If exists: Check missing files only
- Never overwrite existing content

## Session Start Protocol

1. Read ALL memory bank files
2. Check completeness, create missing
3. Verify current context
4. Present approach to user

## Failure Recovery

**Missing folder:** Run initialization protocol

**Corrupted file:** Rename to `.corrupted-TIMESTAMP`, create from template

**File exceeds budget:** Apply compaction, archive oldest content

**Archive Workflow:**
1. Create `memory-bank/archive/YYYY-MM.md`
2. Append content under date header
3. Remove from source
4. Validate source within budget
