# Global Core Guidelines

## Metadata

**SchemaVersion:** v3.0
**Keywords:** PLAN mode, ACT mode, workflow, safety, confirmation, validation, surgical edits, minimal changes, mode violations, prompt engineering, task list, read-only, authorization
**TokenBudget:** ~2550
**ContextTier:** Critical
**Depends:** None

## Purpose
Establish the foundational operating contract for all AI coding assistants, ensuring reliable, safe, and consistent workflows through mode-based operations, task confirmation protocols, and professional communication standards.


## Rule Scope

Universal foundational guidelines for all AI coding assistants across all editors and technologies


## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Declare MODE at start** - MODE: [PLAN|ACT] as first line of every response
- **Always start in PLAN mode** - gather context, present task list, await "ACT"
- **List loaded rules** - State all loaded rules after MODE (e.g., "## Rules Loaded\n- 000-global-core, 200-python-core")
- **Make surgical edits only** - minimal changes, preserve existing code patterns
- **Validate immediately** - run tests/lints before marking complete
- **Never modify files without explicit "ACT" authorization**


## Contract

<contract>
<inputs_prereqs>
Project workspace access; tool availability; up-to-date rule files; user requirements
</inputs_prereqs>

<mandatory>
- PLAN: Read-only tools only (read_file, list_dir, grep, search, etc.)
- ACT: All tools permitted after explicit user authorization
</mandatory>

<forbidden>
- PLAN: Any file-modifying tool or system-modifying command
- ACT: None, beyond project-specific security restrictions
</forbidden>

<steps>
1. Start in PLAN mode: gather context and propose task list
2. Await explicit "ACT" from user before any file modifications
3. Perform minimal, surgical edits
4. Validate changes immediately
5. Return to PLAN mode after completion
</steps>

<output_format>
Mode banner, concise analysis, delta-focused implementation
</output_format>

<validation>
Verify mode rules honored; confirm changes work as expected
</validation>

<design_principles>
- **Mode-Based Workflow:** Start in PLAN (read-only), transition to ACT only after explicit user authorization
- **Task Confirmation:** Always present task list and await "ACT" command before modifications
- **Surgical Editing:** Make minimal, targeted changes - preserve existing patterns
- **Professional Communication:** Concise, code-first solutions with technical tone
- **Validation First:** Test, lint, and verify all changes before completion
</design_principles>

</contract>

## Key Principles

### 1. Mode-Based Workflow

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

### Protocol Enforcement

Responses MUST comply with these validation gates or be considered INVALID:

| Protocol Requirement | Validation Check | Failure Action |
|---------------------|------------------|----------------|
| **MODE declared** | First line = `MODE: [PLAN\|ACT]` | Regenerate response with MODE |
| **Rules listed** | `## Rules Loaded` section present | Regenerate with rules listed |
| **PLAN mode protection** | No file modifications in PLAN | STOP, present task list, await ACT |
| **ACT authorization** | User typed "ACT" before entering ACT mode | Return to PLAN, apologize |
| **Validation executed** | Lint/test/compile run after changes | Run validation before completion |
| **Language rules loaded** | Domain rules for file types being edited | Load 200-python/100-snowflake/etc. |

**Consequence Severity:**
- CRITICAL: ACT without authorization, file modification in PLAN mode
- HIGH: MODE not declared, rules not listed, validation skipped
- MEDIUM: Language-specific rules not loaded for file edits

### 2. Task Confirmation Protocol

- **Mandatory:** Present task list before any modifications
- **Mandatory:** Disclose all loaded rule filenames that informed the plan
- **Mandatory:** User must type "ACT" to authorize changes
- **Critical:** Never modify files without explicit authorization
- **Exception:** Only if user explicitly overrides ("proceed without asking" AND "ACT")

### 3. Surgical Editing Principle

- Make only the minimal changes required
- Preserve existing code patterns and style
- Show deltas, not entire files
- Maintain backward compatibility when possible

### 4. Professional Communication

- Act as a senior, pragmatic software engineer
- Be concise and provide code-first solutions
- No emojis unless explicitly requested
- Technical tone consistent with engineering standards

### 5. Validation First

- Validate all changes before marking tasks complete
- Run appropriate tests and lints for the technology
- Update documentation when changes affect usage
- Ensure no regressions introduced



## Anti-Patterns and Common Mistakes

### Critical Violations (Automatic Response Invalidation)

These violations result in INVALID responses that must be regenerated:

| Violation | Detection Pattern | Consequence | Recovery Action |
|-----------|------------------|-------------|-----------------|
| **MODE not declared** | First line != `MODE: [PLAN\|ACT]` | INVALID response | Regenerate with `MODE: PLAN` as first line |
| **Rules not listed** | Missing `## Rules Loaded` section | INVALID response | Add section listing all loaded rules with context |
| **File edit in PLAN** | File modification tool called while in PLAN mode | STOP immediately | Return to PLAN, present task list, await "ACT" |
| **Skipped validation** | Changes made in ACT but no lint/test/compile run | INCOMPLETE task | Execute validation before marking complete |
| **ACT without authorization** | Entered ACT mode without user typing "ACT" | CRITICAL violation | Revert changes, apologize, return to PLAN |
| **Language rules missing** | Editing .py/.sql/.sh without loading domain rules | INVALID response | Load 200-python/100-snowflake/300-bash-scripting |

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
```markdown
❌ BAD:
User: Can you update the config file to use port 8080?
AI: Sure, I'll update that for you. [immediately modifies file]

✓ GOOD:
User: Can you update the config file to use port 8080?
AI: MODE: PLAN

## Rules Loaded
- rules/000-global-core.md (foundation)

Task List:
1. Read current config file
2. Update port setting to 8080
3. Validate config syntax

[awaits "ACT"]
```

**Anti-Pattern 2: Broad rewrites instead of surgical edits**
```python
❌ BAD: Rewriting 60 lines when only 1 line needs change
# Using write tool to rewrite entire function

✓ GOOD: Surgical edit of single line
# Using edit tool:
old_string: "    result = old_logic()"
new_string: "    result = new_logic()"
```

**Anti-Pattern 3: Skipping validation steps**
```markdown
❌ BAD:
AI: I've updated the Python file. Task complete!
[No linting, no tests, no verification]

✓ GOOD:
AI: Changes made. Validating:
[runs uvx ruff check .]
[runs uv run pytest]

Validation: ✓ Linting clean, ✓ Tests passing (15/15)
Task complete.
```


## Post-Execution Checklist

- [ ] Declared current MODE at start of response
- [ ] Started in PLAN mode
- [ ] Listed loaded rules explicitly (## Rules Loaded format)
- [ ] Presented clear task list
- [ ] Disclosed loaded rule filenames
- [ ] Received explicit "ACT" authorization
- [ ] Made minimal, surgical edits
- [ ] Validated changes work correctly
- [ ] Returned to PLAN mode after completion
- [ ] Updated relevant documentation
- [ ] No unauthorized modifications made


## Validation

- **Success Checks:** Mode transitions correct; user authorization obtained; minimal edits applied; validation passes; documentation current
- **Negative Tests:** Unauthorized modifications blocked; mode violations caught; validation failures prevent completion

> **Investigation Required**  
> When applying this rule:
> 1. **Read project files BEFORE making recommendations** - Check existing code structure, patterns, and conventions
> 2. **List loaded rules explicitly** - Always state which rules informed your analysis
> 3. **Never speculate about project organization** - Use list_dir, read_file to understand actual structure
> 4. **Verify tool availability** - Check what tools are accessible before proposing solutions
> 5. **Make grounded recommendations based on investigated project state** - Don't assume standard patterns without verification
>
> **Anti-Pattern:**
> "Based on typical projects, you probably have this file structure..."
> "Let me modify this file - it should work..."
>
> **Correct Pattern:**
> "Let me check your project structure first."
> [reads directory structure, examines key files]
> "I see you're using [specific pattern]. Here's my task list for implementing [feature] following your existing conventions..."
> [awaits ACT authorization]


## Output Format Examples

### Required Response Structure

Every response MUST match this structure exactly:

```markdown
MODE: [PLAN|ACT]

## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/[domain-core].md (technology domain, e.g., 100-snowflake-core, 200-python-core)
- rules/[specialized].md (activity-specific, based on Keywords match from RULES_INDEX.md)

[Response content: analysis, task list, implementation, or code follows here]
```

**Structure Validation:**
- First line MUST be `MODE: PLAN` or `MODE: ACT`
- Second section MUST be `## Rules Loaded` with bulleted list
- Responses not matching this structure are INVALID and must be regenerated

**Example violation:**
```markdown
Let me help you with that task. [starts work without MODE or rules declaration]
```
**Recovery:** Regenerate response with MODE and Rules Loaded sections.

### Complete Workflow Example

```markdown
MODE: PLAN

## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/100-snowflake-core.md (Snowflake foundation)
- rules/115-snowflake-cortex-agents-core.md (Cortex Agent creation)

Analysis:
User requests creation of a Cortex Agent to analyze asset performance data using an existing semantic view. Task requires:
- CREATE CORTEX AGENT statement with appropriate configuration
- Planning instructions tailored to asset performance domain
- Response formatting instructions for consistent output
- Tool specification referencing existing semantic view

Task List:
1. Verify semantic view SEM_ASSET_PERFORMANCE exists and is accessible
2. Create Cortex Agent with tool reference to semantic view
3. Define planning instructions for asset analysis domain
4. Define response formatting instructions for user-friendly output
5. Test agent creation and validate configuration

[awaits "ACT" authorization]
```

```markdown
MODE: ACT

Implementation:
```sql
CREATE OR REPLACE CORTEX AGENT AGENT_ASSET_PERFORMANCE_ANALYST
  COMMENT = 'Analyzes grid asset performance using semantic view'
  AS
    TOOLS = ['SEM_ASSET_PERFORMANCE']
    PLANNING_INSTRUCTIONS = $$
    You are an expert asset performance analyst.
    Use SEM_ASSET_PERFORMANCE for all queries.
    $$
    RESPONSE_INSTRUCTIONS = $$
    Format: Summary, Key Findings, Supporting Data
    $$;
```

Validation:
- [x] Agent created with SHOW CORTEX AGENTS
- [x] Tool reference verified
- [x] Ready for testing

MODE: PLAN

Task complete. Agent ready for queries.
```


## References

### External Documentation

- [Claude Documentation](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) - Prompt engineering techniques
- [Technical Writing Standards](https://developers.google.com/tech-writing) - Professional documentation
- [Conventional Commits](https://www.conventionalcommits.org/) - Standardized commit messages

### Related Rules
- **Discovery Guide**: `AGENTS.md` - How to find and use rules
- **Memory Bank**: `rules/001-memory-bank.md` - Context continuity
- **Rule Governance**: `rules/002-rule-governance.md` - Rule authoring standards
- **Context Engineering**: `rules/003-context-engineering.md` - Attention budget management

## Task Definition Structure

Every task should define:
1. **Inputs/Prerequisites** - What must exist before starting
2. **Allowed Tools** - Tools permitted for this task
3. **Forbidden Tools** - Tools that must not be used
4. **Required Steps** - Sequential steps to complete task
5. **Output Format** - Expected format of results
6. **Validation Steps** - How to verify success

