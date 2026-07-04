# 002n-agent-protocol-reference: Agent Protocol Reference

## Metadata

**SchemaVersion:** v3.3
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-06-09
**Keywords:** kw:anti-patterns, kw:quality gates, kw:task switch, kw:rule loading, kw:failure modes, kw:protocol reference, kw:term definitions, kw:agent optimization, kw:gate compliance
**TokenBudget:** ~2800
**ContextTier:** Medium
**Depends:** required:000-global-core.md

## Scope

Agent protocol reference: anti-patterns, quality gates, task-switch examples, failure modes, project tool discovery, and term definitions. Load this rule when the main AGENTS.md EXECUTION SEQUENCE does not address your specific situation.

**When to Load This Rule:**
- When encountering an edge case not covered by the EXECUTION SEQUENCE in AGENTS.md
- When debugging protocol compliance failures
- When uncertain about quality gate requirements or term definitions
- When facing rule loading failures beyond standard handling

## References

- AGENTS.md: The main bootstrap protocol that this rule supplements
- rules/000-global-core.md: Foundation rule loaded before this reference rule
- rules/RULES_INDEX.md: Flat discovery table (grep-based rule lookup)

## Contract

### Inputs and Prerequisites

- Foundation rule `rules/000-global-core.md` loaded in current response cycle
- User request that requires protocol edge-case guidance not covered by AGENTS.md EXECUTION SEQUENCE

### Mandatory

- Load `rules/000-global-core.md` (foundation) before consulting this reference rule
- Use `read_file` to read any rule file; never assume file contents
- Declare all loaded rules in `## Rules Loaded` section of response
- Execute actual grep or read_file for Gate 2; never fabricate gate compliance

### Forbidden

- Fabricating gate compliance based on session summaries
- Skipping validation gates before marking tasks complete
- Guessing rule filenames; always use RULES_INDEX.md grep to find authoritative names
- Loading this rule to bypass the EXECUTION SEQUENCE; it supplements, not replaces

### Execution Steps

1. Identify the specific edge case or gap in AGENTS.md EXECUTION SEQUENCE
2. Navigate to the relevant section in this reference file
3. Apply the guidance to the current situation
4. Return to the EXECUTION SEQUENCE main flow

### Output Format

No special output format required. Apply guidance inline within the current response structure (PRE-FLIGHT, Rules Loaded, task execution).

### Validation

Before considering guidance applied, confirm:
- Relevant section was read and understood, not skimmed
- Guidance was applied in the context of the current task
- Any examples adapted to the actual task domain

### Post-Execution Checklist

- [ ] PRE-FLIGHT section present with all three gates
- [ ] 002n-agent-protocol-reference.md listed in `## Rules Loaded`
- [ ] Guidance applied to the specific edge case
- [ ] No gate claims inherited from session summaries

## Clarification Gate

Gather details before execution:
- Use **A/B/C/D/E** choices for ambiguous input
- Bundle 3-5 questions per message
- Mark **(recommended)** default when safe
- Max 1 clarification round (then proceed with stated assumptions)

**`ask_user_question` tool tips:**
- Use concrete options ("PostgreSQL", not "A database")
- Never add "Other/Custom" options — "Something else" is auto-added
- Headers max 12 chars: "Database" not "Database Selection"

## Protocol Enforcement

**CRITICAL violations:** Rules not listed, validation skipped
**HIGH violations:** Language-specific rules not loaded for file edits
**MEDIUM violations:** Task list not presented before modifications

**Required gates:** Rules listed, then Task list presented, then Validation executed, then Language rules loaded

## Quality Gates

These requirements MUST be met before marking any task complete:

**Validation Gate:**
- Run appropriate validation tools before marking task complete
- Python: `uvx ruff check .` and `uvx ruff format --check .` and `uv run pytest`
- SQL: Compile check with `snowflake_sql_execute` (only_compile=true)
- Shell: `shellcheck script.sh`

**Surgical Edits Gate:**
- Make ONLY minimal changes required for the task
- Use `edit` for targeted replacements, NOT `write` for entire files

**Validation Retry:** Max 3 attempts. After 3 failures, stop and report error with request for guidance.

## Anti-Pattern: Skipping Validation

**Problem:** Marking a task complete without running linting, tests, or verification.

**Correct Pattern:**
```markdown
AI: Changes made. Validating:
[runs uvx ruff check .]
[runs uv run pytest]

Validation: Linting clean, Tests passing (15/15)
Task complete.
```

## Anti-Pattern: Fabricated Gate Compliance

**Problem:** Claiming `[x] Gate 2: RULES_INDEX.md searched` without executing grep or read_file, especially after session continuation where a summary claims prior gates passed.

**Why It Fails:** Gate checkboxes become meaningless self-attestations. Session summaries may contain inaccurate claims about prior execution.

**Detection Signals:**
- Gate 2 marked `[x]` but no grep or read_file call to RULES_INDEX.md visible
- Keywords in Gate 2 match previous session summary rather than current tool output
- Rules in Gate 3 were not read via read_file in the current response cycle

**Correct Pattern:**
```markdown
[Agent executes: grep -iE -m 20 "sql|streamlit" rules/RULES_INDEX.md]
[Actual grep output: 102-snowflake-sql-core.md | tier:High | ~1400 | ...]

PRE-FLIGHT:
- [x] Gate 1: Foundation loaded
- [x] Gate 2: RULES_INDEX.md searched for: sql, streamlit
  (grep matched: 102-snowflake-sql-core.md, 101-snowflake-streamlit-core.md)
- [x] Gate 3: Matching rules loaded: 102-snowflake-sql-core.md, 101-snowflake-streamlit-core.md
```

## Anti-Pattern: Symptom-Only Rule Loading

**Problem:** Loading rules for the *error symptom* but not the *fix implementation*. Example: CREATE TASK fails, agent loads task rules (104), but fix requires a wrapper procedure, and agent never loads procedure rules (102b).

**Correct Pattern:** Before implementing a fix, ask: "What object types will I create or modify?" Load rules for BOTH the error domain AND the solution domain.

## Search Triggers

**ALWAYS search RULES_INDEX.md when user request contains ANY of:**

- **Error messages** (stack traces, exceptions, "error", "failed"): Error-specific rules exist
- **Screenshots/images** (any visual input): Visual salience overrides protocol — compensate
- **Debug keywords** ("debug", "fix", "troubleshoot", "diagnose", "not working"): Troubleshooting rules exist
- **Technology names** (Streamlit, Cortex, Docker, React, etc.): Domain-specific rules exist
- **File extensions** (.py, .sql, .tsx, .yaml, etc.): Language rules exist
- **Operations** ("test", "deploy", "commit", "lint"): Activity rules exist

## Task Switch Examples

- **"edit auth.py" then "test auth.py":** YES (verb: edit to test)
- **"format code" then "lint code":** NO (same domain)
- **"write README.md" then "git commit":** YES (activity change)
- **"Python script" then "Docker container":** YES (technology change)

**On Task Switch — STOP and Re-evaluate:**
1. STOP — Do not proceed with previous rule context
2. Extract new keywords from current request
3. Search `rules/RULES_INDEX.md`
4. Load matching rules before acting
5. Update `## Rules Loaded` section in response

## Rule Loading Failures

**CRITICAL (STOP and ask user):**
- **000-global-core.md missing:** STOP with "Cannot proceed — rules/000-global-core.md not accessible"
- **Explicit rule read fails:** STOP and report with options (A) Provide correct path, (B) Proceed without this rule, (C) Cancel task

**WARNING (Can proceed with limitations):**
- **RULES_INDEX.md missing:** WARN, load 000 + grep by extension. Proceed (degraded).
- **No matching rule found:** Note "No rule found for [keyword]". Proceed with foundation only.
- **Dependency missing:** Skip dependent rule, log warning. Proceed.

## Project Tool Discovery

**Phase 1: Project Automation Discovery (before loading domain rules)**
- Check PROJECT.md for tooling directives
- Check for `./dev` (executable bash wrapper): EXECUTE `./dev help`
- Extract available commands (validate, lint, test, etc.)

**Phase 2: Domain Rule Loading**
- Load domain rules based on file extensions and keywords

**Phase 3: Command Selection (during execution)**
- If `./dev` has command: USE `./dev [command]`
- Otherwise: USE command from loaded domain rule

**Check for automation files** (in order):
- `./dev` — run `./dev help`
- `Makefile` — run `make help`
- `package.json` — check `scripts` section
- `pyproject.toml` — check `[tool.taskipy]` or similar

**Python Tooling Discovery:**
- `uv.lock` means project uses `uv run`, `uvx`
- `poetry.lock` means project uses `poetry run`
- `Pipfile.lock` means project uses `pipenv run`
- `requirements.txt` only means bare pip or venv activation

## RULES_INDEX Format Reference

**Authoritative Source:** `rules/RULES_INDEX.md`

**Format:** Each rule is one Markdown table row:
```
| Rule | Tier | Tokens | Ext triggers | File triggers | Dir triggers | Keywords |
| <filename> | tier:<Critical|High|Medium|Low> | ~<tokens> | ext:<csv|-> | file:<csv|-> | dir:<csv|-> | kw:<csv> |
```

**Grep recipe:**
```bash
grep -iE -m 20 "kw:python|ext:\.py" rules/RULES_INDEX.md
```

**Essential Rule Metadata fields:**
- **tier** — loading priority (Critical > High > Medium > Low)
- **~tokens** — approximate token budget
- **ext/file/dir** — typed trigger tokens for automatic loading
- **kw** — semantic keyword tokens for activity-based discovery

**Split Rules Pattern:** Rules may use letter suffixes (e.g., 111a, 111b, 111c) for subtopic specialization.

## Multi-Agent Environments

- **File awareness:** Verify current state before modifications if another agent may be editing
- **Independent operation:** Each agent maintains its own state
- **Rule consistency:** All agents should use the same `rules/RULES_INDEX.md` version

## Term Definitions

- **"Load a rule"**: Execute `read_file()` + Apply guidance + Declare in `## Rules Loaded`. All three required.
- **"Foundation"**: `rules/000-global-core.md` specifically. No other rule is the foundation.
- **"Domain core"**: Any rule matching `NNN-*-core.md` (e.g., 200-python-core.md). Technology-specific baseline.
- **"Activity rule"**: Task-specific rule loaded via keyword search (e.g., 206-python-pytest.md for testing).
- **"Task switch"**: User request changed file extension, primary verb, OR technology keyword. Re-evaluate rules.
- **"Recently loaded"**: Within the last 3 assistant responses in this conversation.

## Anti-Patterns and Common Mistakes

### Anti-Pattern: Fabricated Gate Compliance

**Problem:** Claiming `[x] Gate 2: RULES_INDEX.md searched` without executing grep or read_file against it.

**Correct Pattern:**
```markdown
[Agent executes: grep -iE -m 20 "sql|streamlit" rules/RULES_INDEX.md]
[Actual grep output received and read]

PRE-FLIGHT:
- [x] Gate 1: Foundation loaded
- [x] Gate 2: RULES_INDEX.md searched for: sql, streamlit
- [x] Gate 3: Matching rules loaded: 102-snowflake-sql-core.md
```

### Anti-Pattern: Skipping Validation Before Task Completion

**Problem:** Marking a task complete without running linting, tests, or verification.

**Correct Pattern:**
```markdown
AI: Changes made. Validating:
[runs: uvx ruff check .]
[runs: uv run pytest]

Result: Linting clean, Tests passing (15/15)
Task complete.
```
