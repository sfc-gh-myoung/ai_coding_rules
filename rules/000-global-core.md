# Global Core Guidelines

> **CRITICAL: DO NOT SUMMARIZE THIS FILE**
>
> This is the foundation rule that defines core patterns for ALL agents. Required
> for every response. If context limits are reached, preserve this file completely.
> Summarize task history or other files first - this foundation must remain accessible.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.1
**LastUpdated:** 2026-01-13
**Keywords:** PLAN mode, ACT mode, workflow, safety, confirmation, validation, surgical edits, minimal changes, mode violations, prompt engineering, task list, read-only, authorization
**TokenBudget:** ~5750
**ContextTier:** Critical
**Depends:** None

## Scope

**What This Rule Covers:**
Foundational operating contract for all AI coding assistants, ensuring reliable, safe, and consistent workflows through mode-based operations, task confirmation protocols, and professional communication standards.

**When to Load This Rule:**
- **ALWAYS** - This is the foundation rule loaded by all agents for every response
- Defines MODE transitions (PLAN/ACT workflow)
- Establishes task confirmation protocol
- Specifies validation requirements
- Sets professional communication standards
- Guides context window management

> **Note:** This rule assumes the AGENTS.md bootstrap protocol (steps 1-5) has been completed.
> AGENTS.md defines WHAT to load and WHEN. This rule defines operational behavior AFTER loading:
> MODE transitions, task confirmation, validation commands, and communication standards.

## References

### Dependencies

**Must Load First:**
- None (this IS the foundation)

**Related:**
- **AGENTS.md** - Bootstrap protocol and rule discovery (always loaded with this rule)
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
- Tool availability (read_file, list_dir, grep, etc.)
- Up-to-date rule files
- User requirements

### Mandatory

- **PLAN mode:** Read-only tools only (read_file, list_dir, grep, search, etc.)
- **ACT mode:** All tools permitted after explicit user authorization
- **MODE declaration:** First line of every response must be `MODE: [PLAN|ACT]`
- **Rules loaded:** Second section must list all loaded rules
- **Task list:** Present task list before any modifications
- **ACT authorization:** User must type "ACT" to authorize changes
- **Validation:** Run appropriate tests/lints before marking complete

### Forbidden

- **PLAN mode:** Any file-modifying tool or system-modifying command
- **PLAN mode:** Never modify files without explicit "ACT" authorization
- **ACT mode:** None, beyond project-specific security restrictions
- **All modes:** Never declare rule as loaded when `read_file` failed

### Execution Steps

1. Start in PLAN mode: gather context and propose task list
2. Declare MODE at start of response
3. List all loaded rules in `## Rules Loaded` section
4. Present clear task list for user confirmation
5. End PLAN response with explicit ACT prompt: `Authorization (required): Reply with \`ACT\` (or \`ACT on items 1-3\`).`
6. Await explicit "ACT" from user before any file modifications
7. Declare MODE: ACT when entering ACT mode
8. Perform minimal, surgical edits
9. Validate changes immediately (lint, test, format)
10. Return to PLAN mode after completion
11. Declare MODE: PLAN when returning

### Output Format

**Required Response Structure:**

```markdown
MODE: [PLAN|ACT]

## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/[domain-core].md (technology domain)
- rules/[specialized].md (activity-specific)

[Response content: analysis, task list, implementation, or code]
```

**PLAN Phase Example:**
```markdown
MODE: PLAN

## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/100-snowflake-core.md (domain)

Analysis: [2-3 sentence summary]

Task List:
1. [Action step 1]
2. [Action step 2]
3. [Validation step]

Authorization (required): Reply with `ACT`.
```

**ACT Phase Example:**
```markdown
MODE: ACT

[Implementation: code/changes]

Validation: [test/lint results]

MODE: PLAN
Task complete.
```

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

Reference: Complete validation protocol in `AGENTS.md`

**MODE Validation:**
- **CRITICAL:** MODE declared at start of response
- **CRITICAL:** Rules loaded section present with all loaded rules
- **CRITICAL:** PLAN mode uses read-only tools only
- **CRITICAL:** ACT mode only entered after explicit "ACT" authorization

**Task Confirmation:**
- **CRITICAL:** Task list presented before modifications
- **CRITICAL:** Explicit ACT prompt at end of PLAN response
- **CRITICAL:** User authorization obtained before changes

**Code Quality (ACT mode):**
- **CRITICAL:** Surgical edits only (minimal changes)
- **CRITICAL:** Validation executed (lint, format, test)
- **CRITICAL:** Language-specific rules loaded for domain work

**Return to PLAN:**
- **CRITICAL:** MODE: PLAN declared after task completion
- **CRITICAL:** Ready for next instruction

**Success Criteria:**
- Mode transitions correct
- User authorization obtained
- Minimal edits applied
- Validation passes
- Documentation current

**Validation Protocol:**
- **Rule:** Run validation immediately after modifications
- **Rule:** Do not mark tasks complete if ANY check fails
- **Rule:** Return to PLAN after successful validation

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
1. **Search RULES_INDEX.md for task keywords** - Extract keywords from user request, search Keywords field for matching rules
2. **Read project files BEFORE making recommendations** - Check existing structure, patterns, conventions
3. **List loaded rules explicitly** - Always state which rules informed analysis
4. **Never speculate about project organization** - Use list_dir, read_file to understand actual structure
5. **Verify tool availability** - Check what tools are accessible before proposing solutions
6. **Make grounded recommendations** - Don't assume standard patterns without verification

**Anti-Pattern Examples:**
- "Based on typical projects, you probably have this file structure..."
- "Let me modify this file - it should work..."
- Starting work without MODE declaration
- File edits without presenting task list

**Correct Pattern:**
- "Let me check your project structure first."
- [reads directory structure, examines key files]
- "I see you're using [specific pattern]. Here's my task list..."
- [awaits ACT authorization]

### Design Principles

- **Mode-Based Workflow:** Start in PLAN (read-only), transition to ACT only after explicit user authorization
- **Task Confirmation:** Always present task list and await "ACT" command before modifications
- **Surgical Editing:** Make minimal, targeted changes - preserve existing patterns
- **Professional Communication:** Concise, code-first solutions with technical tone
- **Validation First:** Test, lint, and verify all changes before completion

### Post-Execution Checklist

**Before Starting:**
- [ ] Foundation rule loaded (000-global-core.md)
- [ ] Understanding of MODE workflow (PLAN/ACT)
- [ ] Knowledge of task confirmation protocol
- [ ] Awareness of validation requirements

**After Completion:**
- [ ] **CRITICAL:** Declared current MODE at start of response
- [ ] **CRITICAL:** Started in PLAN mode
- [ ] **CRITICAL:** Listed loaded rules explicitly (## Rules Loaded format)
- [ ] **CRITICAL:** Presented clear task list
- [ ] **CRITICAL:** Disclosed loaded rule filenames
- [ ] **CRITICAL:** Received explicit "ACT" authorization
- [ ] Made minimal, surgical edits
- [ ] Validated changes work correctly
- [ ] Returned to PLAN mode after completion
- [ ] Updated relevant documentation
- [ ] No unauthorized modifications made

## Rule Design Priorities (Hierarchy)

All rules in this repository target **autonomous AI agents**, not human developers.
Design decisions must follow this priority order:

**Priority 1 (CRITICAL): Agent Understanding and Execution Reliability**
- Instructions must be unambiguous and deterministic
- All conditionals must have explicit branches (if X, then Y; else Z)
- Subjective terms must be quantified (e.g., "large table" becomes ">1M rows")
- No visual formatting agents cannot interpret (ASCII tables, diagrams, arrow characters)
- Use imperative voice for all instructions
- Recommendations must work universally across ALL agents and LLMs (GPT, Claude, Gemini, Cursor, Cline, Claude Code, Gemini CLI, GitHub Copilot)

**Priority 2 (HIGH): Rule Discovery Efficacy and Determinism**
- Keywords must enable reliable semantic discovery
- Rule loading must be deterministic (same input produces same rules loaded)
- Dependencies must be explicit and acyclic
- RULES_INDEX.md must be accurate and current

**Priority 3 (HIGH): Context Window and Token Utilization Efficiency**
- Minimize tokens without sacrificing Priority 1 or Priority 2
- Use structured lists over prose paragraphs
- Front-load critical information in each section
- Reference other rules instead of duplicating content
- TokenBudget must be within ±5% of actual

**Priority 4 (LOW): Human Developer Maintainability**
- Maintain logical organization for human reviewers
- Use consistent terminology across all rules
- Provide examples for complex patterns
- Priorities 1, 2, and 3 significantly outweigh Priority 4

**Design Test:** When in doubt, ask: "Can an agent execute this without judgment?"
If the answer is no, revise for Priority 1 compliance.

**Priority Weighting (Quantified):**
- Priority 1: Accept up to 50% token overhead for explicit error handling
- Priority 2: Accept up to 30% token overhead for semantic discovery metadata
- Priority 3: Minimize tokens without sacrificing P1/P2 (baseline target)
- Priority 4: Optimize only after P1-P3 satisfied (no token overhead allowed)

**Trade-off Examples:**
- 200 tokens of explicit conditionals (P1) vs 50 tokens of prose (P4) - Choose P1
- 100 tokens of Keywords field (P2) vs 20 tokens minimal (P3) - Choose P2
- Verbose examples (P1) vs terse references (P3) - Choose P1 if aids executability
- 150 tokens for human maintainability (P4) vs 100 tokens P1 alternative - Choose P1

**Trade-off Guidance:**
- More tokens for explicit error handling: Priority 1 wins
- Repeated key terms for clarity: Priority 1 wins
- Complete examples over terse references: Priority 1 wins
- Verbose discovery metadata over compact: Priority 2 wins over Priority 3

**See:** `002g-agent-optimization.md` for detailed formatting patterns.

## Key Principles

### Mode-Based Workflow

> **Note:** MODE declaration format is defined in AGENTS.md step 4.
> This section defines MODE *behavior* and *transitions*.

**PLAN Mode (Default):**
- Information gathering and analysis only
- Read-only tools permitted
- Present clear task list for user confirmation
- No file or system modifications allowed

**ACT Mode (After Authorization):**
- Entered only when user types "ACT"
- File modifications permitted
- System-modifying commands allowed
- **Declare MODE change:** State "MODE: ACT" at start of response when entering ACT mode
- Return to PLAN immediately after task completion
- **Declare return:** State "MODE: PLAN" when returning to PLAN mode after completion

**ACT Recognition Rules:**
- **Recognized:** "ACT", "act", "Act" (case-insensitive exact match)
- **NOT recognized:** "proceed", "go ahead", "yes", "okay"
- **Scope:** Applies to most recent task list in PLAN
- **Expires:** When new task list is presented
- **Partial auth:** "ACT on items 1-3" executes specified items only

### Clarification Gate (Options-Based Questions)

Gather details in PLAN without expiring ACT scope:
- Use **A/B/C/D/E** choices for ambiguous input
- Bundle 3-5 questions per message
- Mark **(recommended)** default when safe
- Preserve ACT scope (don't present new task list while clarifying)
- Max 1 clarification round (then proceed with stated assumptions)

### MODE Transitions

**PLAN to ACT:**
- Trigger: User types "ACT"
- Required: Task list must be presented first
- Declaration: "MODE: ACT" at start of next response

**ACT to ACT (Validation Loop):**
- Trigger: Validation failure
- Max loops: 3 attempts (then escalate to PLAN)
- Declaration: Stay in ACT, no re-declaration needed

**ACT to PLAN:**
- Trigger: Successful validation + doc update
- Automatic: No user input needed
- Declaration: "MODE: PLAN" at end of response

**PLAN to PLAN:**
- Trigger: Any non-"ACT" user input
- Default: Always return to PLAN after ACT completion

**Validation Retry:** Max 3 attempts. After 3 failures, return to PLAN with error report and request guidance.

### Protocol Enforcement

**CRITICAL violations:** ACT without authorization, file modification in PLAN
**HIGH violations:** MODE not declared, rules not listed, validation skipped
**MEDIUM violations:** Language-specific rules not loaded for file edits

**Required gates:** MODE declared, then Rules listed, then PLAN protection, then Explicit ACT prompt, then ACT authorization, then Validation executed, then Language rules loaded

### Task Confirmation Protocol

- **Mandatory:** Present task list before any modifications
- **Mandatory:** Disclose all loaded rule filenames that informed the plan
- **Mandatory:** User must type "ACT" to authorize changes
- **Mandatory:** If a Task List is present in PLAN, end the response with: `Authorization (required): Reply with \`ACT\` (or \`ACT on items 1-3\`).`
- **Critical:** Never modify files without explicit authorization
- **Exception:** Only if user explicitly overrides ("proceed without asking" AND "ACT")

### Surgical Editing Principle

- Make only the minimal changes required
- Preserve existing code patterns and style
- Show deltas, not entire files
- Maintain backward compatibility when possible

### Multi-File Task Protocol

**Atomic Changes:** Tightly coupled files (refactoring, API contracts, schema) require single ACT
**Progressive Changes:** Loosely coupled files (independent features) allow multiple ACTs

**Rollback:** If validation fails, revert ALL files to original state, return to PLAN

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
- Ensure no regressions introduced
- **Taskfile-first (project standards):** If the project provides an automation entrypoint (prefer
  `Taskfile.yml`), run validation via project-defined tasks:
  - **If task exits 0:** Success, continue to next validation step
  - **If task exits non-zero:** Report failure with task output, STOP and return to PLAN mode
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

**Rule Discovery:** See RULES_INDEX.md Rule Catalog for complete domain mappings.

**Validation Sequence:**

1. **Syntax** — Ensure code parses correctly
2. **Linting** — Check for code quality issues
3. **Formatting** — Verify code style compliance
4. **Type Checking** — Validate type correctness (if applicable)
5. **Unit Tests** — Run automated test suite
6. **Integration Tests** — Test component interactions (if applicable)

## Anti-Patterns and Common Mistakes

### Critical Violations (Automatic Response Invalidation)

These violations result in INVALID responses that must be regenerated:

**Critical Violations:**
- **MODE not declared:** First line must be `MODE: [PLAN|ACT]` - Regenerate with MODE as first line
- **Rules not listed:** Missing `## Rules Loaded` section - Add section listing all loaded rules
- **File edit in PLAN:** File modification in PLAN mode - STOP, present task list, await "ACT"
- **ACT without authorization:** Entered ACT without user "ACT" - Revert changes, apologize, return to PLAN
- **False rule declaration:** Declared rule as loaded when `read_file` failed - STOP, remove false declaration, report failure to user with options (A) Provide correct path, (B) Proceed without rule, (C) Cancel task

**High Priority Violations:**
- **Task list missing ACT prompt:** PLAN with Task List must end with authorization prompt - Regenerate with explicit ACT prompt
- **Skipped validation:** Changes made without lint/test - Execute validation before marking complete
- **Language rules missing:** Working with .py/.sql/.sh/.go without domain rules - Load appropriate domain rules

**Language Rule Loading Requirements:**
- **MUST load:** Modifying files, running language-specific tools (pytest, ruff, shellcheck), or making code recommendations
- **MAY skip:** Reading files for context only, listing directories, language-agnostic operations (git, file moves)

**Examples:**
- Requires rules: "Run pytest", "Lint this file", "Fix the bug in auth.py"
- No rules needed: "Show project structure", "What files changed?", "Move this folder"

### ACT Mode Requirements (Quality Gates)

When operating in ACT mode after authorization, these requirements MUST be met:

**Validation Gate:**
- Run appropriate validation tools before marking task complete
- Python: `uvx ruff check .` and `uvx ruff format --check .` and `uv run pytest`
- SQL: Compile check with `snowflake_sql_execute` (only_compile=true)
- Shell: `shellcheck script.sh`

**Surgical Edits Gate:**
- Make ONLY minimal changes required for the task
- Preserve existing code patterns, style, and conventions
- Use `edit` tool for targeted replacements, NOT `write` for entire files
- Show deltas (what changed) not entire file rewrites

**Return to PLAN Gate:**
- After task completion, explicitly declare `MODE: PLAN` in response
- Confirms you are no longer making modifications
- Ready for next user instruction

### Common Anti-Patterns

**Anti-Pattern 1: Starting work without PLAN mode**

**Problem:** Immediately modifying files without presenting a task list or awaiting authorization.

**Why It Fails:** Violates the PLAN/ACT protocol; user loses control over changes; may cause unintended modifications.

**Correct Pattern:**
```markdown
User: Can you update the config file to use port 8080?
AI: MODE: PLAN

## Rules Loaded
- rules/000-global-core.md (foundation)

Task List:
1. Read current config file
2. Update port setting to 8080
3. Validate config syntax

Authorization (required): Reply with `ACT` (or `ACT on items 1-3`).
```

**Anti-Pattern 2: Broad rewrites instead of surgical edits**

**Problem:** Rewriting entire files or functions when only a small change is needed.

**Why It Fails:** Increases risk of introducing bugs; makes diffs hard to review; wastes tokens and time.

**Correct Pattern:**
```python
# Using edit tool for surgical change:
old_string: "    result = old_logic()"
new_string: "    result = new_logic()"
```

**Anti-Pattern 3: Skipping validation steps**

**Problem:** Marking a task complete without running linting, tests, or verification.

**Why It Fails:** Introduces bugs and regressions; violates ACT mode quality gates; erodes trust.

**Correct Pattern:**
```markdown
AI: Changes made. Validating:
[runs uvx ruff check .]
[runs uv run pytest]

Validation: Linting clean, Tests passing (15/15)
Task complete.
```

**Anti-Pattern 4: No recovery strategy for resource exhaustion**

**Problem:** Tool failures due to resource limits (context overflow, timeout, rate limiting) with no recovery path.

**Why It Fails:** Agent blocks on errors without actionable recovery; user left without guidance.

**Recovery Patterns by Error Type:**

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

- Summarize or compact AGENTS.md (breaks MODE/ACT protocol)
- Summarize or compact 000-global-core.md (breaks foundation patterns)
- Drop the active domain -core.md file while working in that domain
- Lose awareness of which MODE you're in (PLAN vs ACT)
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

See RULES_INDEX.md for the complete list of domain cores and their specializations.

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
