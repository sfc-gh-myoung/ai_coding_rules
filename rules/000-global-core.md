# Global Core Guidelines

> **CRITICAL: DO NOT SUMMARIZE THIS FILE**
>
> This is the foundation rule that defines core patterns for ALL agents. Required
> for every response. If context limits are reached, preserve this file completely.
> Summarize task history or other files first - this foundation must remain accessible.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-02-06
**Keywords:** workflow, safety, confirmation, validation, surgical edits, minimal changes, prompt engineering, task list, context window, professional communication
**TokenBudget:** ~3800
**ContextTier:** Critical
**Depends:** None

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
> AGENTS.md defines the MODE:PLAN/ACT framework. This rule defines operational behavior:
> validation commands, surgical edits, communication standards, and context management.

## References

### Dependencies

**Must Load First:**
- None (this IS the foundation)

**Related:**
- **AGENTS.md** - Bootstrap protocol, MODE:PLAN/ACT framework, and rule discovery
- **001-memory-bank.md** - Context continuity across sessions
- **002-rule-governance.md** - Rule authoring standards
- **002a-rule-creation.md** - Creating new rules
- **002b-rule-update.md** - Updating existing rules
- **003-context-engineering.md** - Attention budget management

### External Documentation

**Best Practices Guides:**
- [Claude Documentation](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) - Prompt engineering techniques
- [Technical Writing Standards](https://developers.google.com/tech-writing) - Professional documentation
- [Conventional Commits](https://www.conventionalcommits.org/) - Standardized commit messages

## Contract

### Inputs and Prerequisites

- Project workspace access
- Tool availability (read_file, list_dir, grep, and project-specific tools)
- Up-to-date rule files (from current branch HEAD)
- User requirements

### Mandatory

- **Rules loaded:** List all loaded rules in response
- **Task list:** Present task list before any modifications
- **Validation:** Run language-specific validation (see Validation Command Reference) before marking complete
- **Surgical edits:** Make minimal, targeted changes only

### Forbidden

- **File modifications without authorization:** See AGENTS.md for MODE:PLAN/ACT protocol
- **False rule declaration:** Never declare rule as loaded when `read_file` failed

### Execution Steps

1. List all loaded rules in `## Rules Loaded` section
2. Present clear task list for user confirmation
3. Perform surgical edits (see Mandatory section above)
4. Validate changes immediately (lint, test, format)
5. Update relevant documentation

### Output Format

**Required Response Structure:**

See AGENTS.md for complete response format including MODE declaration.

```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/[domain-core].md (technology domain)
- rules/[specialized].md (activity-specific)

[Response content: analysis, task list, implementation, or code]
```

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

Reference: See `AGENTS.md` for complete MODE validation and authorization protocol.

**Rules Validation:**
- **CRITICAL:** Rules loaded section present with all loaded rules
- **CRITICAL:** Never declare rule as loaded when `read_file` failed

**Task Confirmation:**
- **CRITICAL:** Task list presented before modifications
- **CRITICAL:** User authorization obtained before changes (see AGENTS.md)

**Code Quality:**
- **CRITICAL:** Surgical edits only (minimal changes)
- **CRITICAL:** Validation executed (lint, format, test)
- **CRITICAL:** Language-specific rules loaded for domain work

**Success Criteria:**
- Minimal edits applied
- Validation passes
- Documentation current

**Validation Protocol:**
- **Rule:** Run validation immediately after modifications
- **Rule:** Do not mark tasks complete if ANY check fails

**Validation Error Message Format:**

When validation fails, agents must report errors using this format:

```
Validation Failed: [Tool Name]

Severity: [CRITICAL|HIGH|MEDIUM|LOW]
Location: [file:line or component name]
Error: [exact error message from tool]
Fix: [specific action to resolve]

[full tool output if helpful for debugging]
```

**Examples:**

```
Validation Failed: ruff

Severity: HIGH
Location: src/auth.py:42
Error: F401 'os' imported but unused
Fix: Remove unused import or use os module

src/auth.py:42:1: F401 'os' imported but unused
```

```
Validation Failed: pytest

Severity: CRITICAL
Location: tests/test_api.py::test_login
Error: AssertionError: expected 200, got 401
Fix: Update authentication test credentials or fix auth logic

=== FAILURES ===
tests/test_api.py::test_login - AssertionError: assert 401 == 200
```

**Rule:** Always include Severity, Location, Error, and Fix fields.

**Investigation Required:**
1. **Search rules/RULES_INDEX.md for task keywords** - Extract keywords from user request, search Keywords field for matching rules
2. **Read project files BEFORE making recommendations** - Check existing structure, patterns, conventions
3. **List loaded rules explicitly** - Always state which rules informed analysis
4. **Never speculate about project organization** - Use list_dir, read_file to understand actual structure
5. **Verify tool availability** - Check what tools are accessible before proposing solutions
6. **Make grounded recommendations** - Don't assume standard patterns without verification

**Anti-Pattern Examples:**
- "Based on typical projects, you probably have this file structure..."
- "Let me modify this file - it should work..."
- File edits without presenting task list

**Correct Pattern:**
- "Let me check your project structure first."
- [reads directory structure, examines key files]
- "I see you're using [specific pattern]. Here's my task list..."
- [awaits authorization per AGENTS.md]

### Design Principles

- **Task Confirmation:** Always present task list before modifications (see AGENTS.md for authorization protocol)
- **Surgical Editing:** Make minimal, targeted changes - preserve existing patterns
- **Professional Communication:** Concise, code-first solutions with technical tone
- **Validation First:** Test, lint, and verify all changes before completion

### Post-Execution Checklist

**Before Starting:**
- [ ] Foundation rule loaded (000-global-core.md)
- [ ] Understanding of AGENTS.md authorization protocol
- [ ] Awareness of validation requirements

**After Completion:**
- [ ] **CRITICAL:** Listed loaded rules explicitly (## Rules Loaded format)
- [ ] **CRITICAL:** Presented clear task list
- [ ] **CRITICAL:** Disclosed loaded rule filenames
- [ ] Made minimal, surgical edits
- [ ] Validated changes work correctly
- [ ] Updated relevant documentation
- [ ] No unauthorized modifications made

## Key Principles

### Surgical Editing Principle

- Make only the minimal changes required
- Preserve existing code patterns and style
- Show deltas, not entire files
- Maintain backward compatibility unless task explicitly requires breaking changes
- **Update LastUpdated field:** If edited file contains `LastUpdated:`, `**LastUpdated:**`, or `**Last Updated:**`, set value to current date in YYYY-MM-DD format

### Multi-File Task Protocol

**Atomic Changes:** Tightly coupled files (refactoring, API contracts, schema) require single authorization
**Progressive Changes:** Loosely coupled files (independent features) allow multiple authorizations

**Rollback:** If validation fails, revert ALL files to original state

**Details:** See 002d-advanced-rule-patterns.md, section "Multi-File Task Patterns"

### Professional Communication

- Act as a senior, pragmatic software engineer
- Be concise and provide code-first solutions
- No emojis unless explicitly requested
- Technical tone consistent with engineering standards

### Validation First

- Validate all changes before marking tasks complete
- Run appropriate tests and lints for the technology
- Update documentation when changes affect usage
- Ensure no regressions introduced via the validation sequence (Syntax, Linting, Formatting, Type Checking, Tests)
- **Taskfile-first (project standards):** If the project provides an automation entrypoint (prefer
  `Taskfile.yml`), run validation via project-defined tasks:
  - **If task exits 0:** Success, continue to next validation step
  - **If task exits non-zero:** Report failure with task output, STOP
  - **If Taskfile.yml missing OR task not found:** Fall back to direct tool commands
  - **Common tasks:** `task validate`, `task check`, `task ci`, `task lint`, `task test`

**Validation Strategies:**
- **Fast-fail:** Chain with `&&` for final checks (stops at first failure)
- **Diagnostic:** Run separately with `|| echo` for debugging (collects all errors)

### Validation Command Reference

**Preferred:** Use project-defined tasks (`task validate`, `task check`, `task ci`, `task lint`, `task test`)

**Fallback:** Load language-specific rule for technology commands:
- **Python:** Load 200-python-core.md (ruff, pytest)
- **SQL:** Load 100-snowflake-core.md (compile checks)
- **Shell:** Load 300-bash-scripting-core.md (shellcheck)
- **JS/TS:** Load 420-javascript-core.md / 430-typescript-core.md (tsc, biome)
- **Go:** Load 600-golang-core.md (go fmt, vet, test)

**Rule Discovery:** See rules/RULES_INDEX.md Rule Catalog for complete domain mappings.

**Validation Sequence:**

1. **Syntax** — Ensure code parses correctly
2. **Linting** — Check for code quality issues
3. **Formatting** — Verify code style compliance
4. **Type Checking** — Validate type correctness (if applicable)
5. **Unit Tests** — Run automated test suite
6. **Integration Tests** — Test component interactions (if applicable)

## Anti-Patterns and Common Mistakes

### Critical Violations

**Critical Violations (see AGENTS.md for MODE-related violations):**
- **Rules not listed:** Missing `## Rules Loaded` section - Add section listing all loaded rules
- **False rule declaration:** Declared rule as loaded when `read_file` failed - STOP, remove false declaration, report failure to user with options (A) Provide correct path, (B) Proceed without rule, (C) Cancel task

**High Priority Violations:**
- **Skipped validation:** Changes made without lint/test - Execute validation before marking complete
- **Language rules missing:** Working with .py/.sql/.sh/.go without domain rules - Load appropriate domain rules

**Language Rule Loading Requirements:**
- **MUST load:** Modifying files, running language-specific tools (pytest, ruff, shellcheck), or making code recommendations
- **MAY skip:** Reading files for context only, listing directories, language-agnostic operations (git, file moves)

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

When approaching context limits, agents must preserve rules in priority order to
maintain consistent behavior. This protocol works across all LLM providers.

### Preservation Priority Order

**ALWAYS PRESERVE (Never Summarize):**

1. **AGENTS.md** - Bootstrap protocol and MODE/ACT framework
2. **000-global-core.md** - This file (foundation patterns)
3. **Active domain -core.md file** - The primary domain rule for current task
   - Examples: 200-python-core.md (Python tasks), 100-snowflake-core.md (Snowflake tasks),
     420-javascript-core.md (JavaScript tasks)

**PRESERVE WHEN RELEVANT:**

4. **Specialized rules for current task** - Task-specific patterns you're actively using
   - Examples: 206-python-pytest.md (if writing tests), 115-snowflake-cortex-agents-core.md (if building Cortex agents)
5. **Dependency rules** - Rules listed in "Depends" metadata of currently loaded rules

**SUMMARIZE IN THIS ORDER (When Context Pressure Occurs):**

1. **Task history** - Previous conversation turns that are no longer relevant
2. **File contents** - Code/files you've already fully analyzed and finished modifying
3. **Reference rules** - Large guides (>4000 tokens) used for lookup, not active application
4. **Specialized rules** - Not currently relevant to the active task
5. **Example sections** - Keep patterns/requirements, condense lengthy examples

**NEVER:**

- Summarize or compact AGENTS.md (breaks bootstrap and authorization protocol)
- Summarize or compact 000-global-core.md (breaks foundation patterns)
- Drop the active domain -core.md file while working in that domain
- Forget the rule loading protocol

### Context Management Decision Tree

**When context limit is approaching:**

1. **Are you in middle of a task?**
   - If YES: Preserve AGENTS.md, 000-global-core.md, domain-core, specialized rules for task. Summarize completed file analysis and old conversation turns.
   - If NO: Preserve AGENTS.md, 000-global-core.md. Summarize everything else, reload rules as needed for next task.

2. **What if you must drop rules?**
   - Drop in reverse priority order: specialized first, then reference, then secondary domain cores
   - Keep at minimum: AGENTS.md + 000-global-core.md + primary domain-core

### Recognition of -core.md Files

All rules following the naming pattern `NNN-*-core.md` are domain foundation rules and
should be preserved in context while working in that domain. Examples:

- `100-snowflake-core.md` - Snowflake domain
- `200-python-core.md` - Python domain
- `300-bash-scripting-core.md` - Shell scripting domain
- `420-javascript-core.md` - JavaScript domain
- `430-typescript-core.md` - TypeScript domain
- `600-golang-core.md` - Go domain

See rules/RULES_INDEX.md for the complete list of domain cores and their specializations.

### Relationship to ContextTier Metadata

The `ContextTier` metadata field (Critical/High/Medium/Low) provides a **secondary signal**
for context priority but is NOT the primary mechanism. The natural language instructions
in this protocol take precedence because they work universally across all LLM providers.

**Usage:**
- **ContextTier metadata:** Helps agents make fine-grained decisions within priority tiers
- **Natural language protocol:** Provides explicit preservation hierarchy that any LLM can follow
- **Together:** Belt-and-suspenders approach ensures consistent behavior

## Task Definition Structure

Every task should define:
1. **Inputs/Prerequisites** - What must exist before starting
2. **Allowed Tools** - Tools permitted for this task
3. **Forbidden Tools** - Tools that must not be used
4. **Required Steps** - Sequential steps to complete task
5. **Output Format** - Expected format of results
6. **Validation Steps** - How to verify success
