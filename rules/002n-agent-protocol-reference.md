# 002n-agent-protocol-reference: Agent Protocol Reference

## Metadata

**SchemaVersion:** v3.4
**RuleVersion:** v1.0.5
**LastUpdated:** 2026-07-10
**Keywords:** kw:anti-patterns, kw:quality gates, kw:task switch, kw:rule loading, kw:failure modes, kw:protocol reference, kw:term definitions, kw:gate compliance
**TokenBudget:** ~4900
**ContextTier:** Medium
**Depends:** required:000-global-core.md

## Scope

Agent protocol reference: anti-patterns, quality gates, task-switch examples, failure modes, project tool discovery, and term definitions. Load this rule when the main AGENTS.md EXECUTION SEQUENCE does not address your specific situation.

**When to Load This Rule:**
- When encountering an edge case not covered by the EXECUTION SEQUENCE in AGENTS.md
- When debugging protocol compliance failures
- When uncertain about quality gate requirements or term definitions
- When facing rule loading failures beyond standard handling

**What This Rule Covers:**
Reference material for the AGENTS.md agent bootstrap protocol — anti-patterns, quality gates, task-switch examples, failure modes, project tool discovery, and term definitions.


## References

- AGENTS.md: The main bootstrap protocol that this rule supplements
- rules/000-global-core.md: Foundation rule loaded before this reference rule
- rules/RULES_INDEX.md: Flat discovery table (grep-based rule lookup)

### External Documentation

_None._

### Dependencies

**Must Load First:**
- [000-global-core.md](000-global-core.md)



## Contract

### Inputs and Prerequisites

- Foundation rule `rules/000-global-core.md` loaded in current response cycle
- User request that requires protocol edge-case guidance not covered by AGENTS.md EXECUTION SEQUENCE

### Mandatory

- Load `rules/000-global-core.md` (foundation) before consulting this reference rule
- Use `read_file` to read any rule file; never assume file contents
- Cite foundation on Gate 1 (`— N lines`); list domain/activity rules as Gate 3 sub-bullets (or `none matched`) in the response
- Execute actual grep or read_file for Gate 2; never fabricate gate compliance

### Forbidden

- Fabricating gate compliance based on session summaries
- Skipping validation gates before marking tasks complete
- Guessing rule filenames; always use RULES_INDEX_COMPACT.md grep to find authoritative names
- Loading this rule to bypass the EXECUTION SEQUENCE; it supplements, not replaces

### Execution Steps

1. Identify the specific edge case or gap in AGENTS.md EXECUTION SEQUENCE
2. Navigate to the relevant section in this reference file
3. Apply the guidance to the current situation
4. Return to the EXECUTION SEQUENCE main flow

### Output Format

No special output format required. Apply guidance inline within the current response structure (PRE-FLIGHT Gate 1 foundation citation + Gate 3 domain sub-bullets, task execution).

### Validation

Before considering guidance applied, confirm:
- Relevant section was read and understood, not skimmed
- Guidance was applied in the context of the current task
- Any examples adapted to the actual task domain

### Post-Execution Checklist

- [ ] PRE-FLIGHT section present with all three gates
- [ ] 002n-agent-protocol-reference.md listed as a Gate 3 sub-bullet
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
- Rules in Gate 3 were not read via read_file in the current response cycle (foundation should not appear in Gate 3; it belongs on Gate 1)

**Correct Pattern:**
```markdown
[Agent executes: grep -iwE "sql|streamlit" rules/RULES_INDEX_COMPACT.md]
[Actual grep output: 102-snowflake-sql-core.md | tier:High | ~1400 | ...]

PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — N lines
- [x] Gate 2: RULES_INDEX.md searched for: sql, streamlit
  (grep matched: 102-snowflake-sql-core.md, 101-snowflake-streamlit-core.md)
- [x] Gate 3: +2 domain rules:
  - rules/102-snowflake-sql-core.md (sql match) — N lines
  - rules/101-snowflake-streamlit-core.md (streamlit match) — N lines
```

## Anti-Pattern: Symptom-Only Rule Loading

**Problem:** Loading rules for the *error symptom* but not the *fix implementation*. Example: CREATE TASK fails, agent loads task rules (104), but fix requires a wrapper procedure, and agent never loads procedure rules (102b).

**Correct Pattern:** Before implementing a fix, ask: "What object types will I create or modify?" Load rules for BOTH the error domain AND the solution domain.

## Search Triggers

**ALWAYS search RULES_INDEX_COMPACT.md when user request contains ANY of:**

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
3. Search `rules/RULES_INDEX_COMPACT.md`
4. Load matching rules before acting
5. Cite foundation on Gate 1 with `— N lines`; list domain/activity rules as Gate 3 sub-bullets (or `none matched`) in response

## Rule Loading Failures

**CRITICAL (STOP and ask user):**
- **000-global-core.md missing:** STOP with "Cannot proceed — rules/000-global-core.md not accessible"
- **Explicit rule read fails:** STOP and report with options (A) Provide correct path, (B) Proceed without this rule, (C) Cancel task

**WARNING (Can proceed with limitations):**
- **RULES_INDEX_COMPACT.md missing:** WARN, load 000 + grep by extension. Proceed (degraded).
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

**Primary agent discovery index:** `rules/RULES_INDEX_COMPACT.md`. This is the ONLY
index agents grep for discovery. The full `rules/RULES_INDEX.md` is a human-only
reference (~4x larger); reading it into agent context is a token-bloat anti-pattern.

**COMPACT format:** one space-separated row per rule:
```
<filename> tier=<Critical|High|Medium|Low> [ext=<csv>] [file=<csv>] [dir=<csv>] kw=<w1> <w2> ...
```

**Grep recipe:**
```bash
grep -iwE "python|streamlit|ext=\.py" rules/RULES_INDEX_COMPACT.md
```

**Full-index format (human reference only):** one Markdown table row per rule:
```
| Rule | Tier | Tokens | Ext triggers | File triggers | Dir triggers | Keywords |
| <filename> | tier:<...> | ~<tokens> | ext:<csv|-> | file:<csv|-> | dir:<csv|-> | kw:<csv> |
```
The COMPACT index carries every discovery trigger the full index has (verified 1:1),
so COMPACT is sufficient for all agent discovery.

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

- **"Load a rule"**: Execute `read_file()` + Apply guidance + Declare as Gate 3 sub-bullet.
  Domain/activity rules only; foundation belongs on Gate 1. All three steps required.
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
[Agent executes: grep -iwE "sql|streamlit" rules/RULES_INDEX_COMPACT.md]
[Actual grep output received and read]

PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — N lines
- [x] Gate 2: RULES_INDEX.md searched for: sql, streamlit
- [x] Gate 3: +1 domain rule:
  - rules/102-snowflake-sql-core.md (sql match) — N lines
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

## High-Risk Action Rule Map

High-risk actions require an additional targeted search beyond the normal keyword grep. Load the mapped rule when the request involves:

- git/commit/push/merge: Search "git", expect 803-project-git-workflow.md
- deploy/deployment: Search "deploy", expect 821-makefile-automation.md
- test/pytest: Search "test", expect 206-python-pytest.md
- README/documentation: Search "readme", expect 801-project-readme.md
- CHANGELOG: Search "changelog", expect 800-project-changelog.md
- Modifying files in rules/: Load 002-rule-governance.md

## Keyword Extraction Heuristic

When a user request contains multiple technologies (joined by `+`, `and`, `with`, `,`, or `using`):

1. Split request on delimiters to identify individual technologies
2. Technical terms (capitalized, hyphenated, acronyms like SSE/API/SPCS) are almost always keywords
3. Each technology should be included in the grep OR pattern

**Example:** "FastAPI + HTMX + SSE in SPCS" produces `grep -iwE "fastapi|htmx|sse|spcs" rules/RULES_INDEX_COMPACT.md` (4 keywords)

## Gate Failure Message Catalog

Exact per-gate failure messages used by the bootstrap PRE-FLIGHT header (AGENTS.md Step 4).

Gate 1 failures:
- "rules/000-global-core.md not found"
- "rules/000-global-core.md returned empty content"
- "read_file tool not available"

Gate 2 failures:
- "rules/RULES_INDEX_COMPACT.md not found"
- "grep tool unavailable" -> **AUTO-FALLBACK:** Read RULES_INDEX_COMPACT.md directly and scan manually. Do NOT mark as FAILED if fallback succeeds.
- "No keywords extracted from user request"

Gate 3 failures:
- "Rule file [name] not found"
- "Dependency [name] could not be loaded"
- "All matched rules failed to load"

## Partial Rule Loading

**CRITICAL - READ CAREFULLY:**
- If SOME rules load and SOME fail: Gate 3 = PASS (mark `[x]`) and CONTINUE with task
- **DO NOT STOP** when partial failure occurs - proceed with successfully loaded rules
- List loaded rules + note failures as Gate 3 sub-bullets
- Only mark Gate 3 as FAILED (`[ ]`) when **ALL** matched rules fail to load
- "Partial failure" means CONTINUE, not STOP

**Example - Partial Success:**
```markdown
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — N lines
- [x] Gate 2: RULES_INDEX_COMPACT.md searched for: python, sql
- [x] Gate 3: +1 domain rule:
  - rules/102-snowflake-sql-core.md (for .sql extension) — N lines
  - ⚠️ Rule load failed: 200-python-core.md not found
```
Note: Gate 3 shows `[x]` because SQL rule loaded successfully. Continue with available rules.

## ACT Authorization Recognition (MODE)

Applies only in MODE-enabled deployments.

**MANDATORY PRE-PROCESSING (execute BEFORE checking for ACT):**
```
Step 1: Get user message
Step 2: Strip leading/trailing whitespace
Step 3: Strip trailing punctuation: remove any `.`, `!`, `?` from END of string
Step 4: NOW check if result equals "ACT" (case-insensitive) or starts with "ACT on"
```

**Examples of VALID ACT authorization (all MUST trigger MODE: ACT):**

- `ACT` / `act` / `Act` (after strip) -> VALID, MODE: ACT
- `ACT.` / `ACT!` / `ACT?` / `act.` (after strip: `ACT`/`act`) -> VALID, MODE: ACT
- `ACT on items 1-2` (after strip) -> VALID, MODE: ACT (scoped)

**Examples of INVALID (must NOT trigger MODE: ACT):**

- `proceed`, `go ahead`, `yes`, `okay`, `do it`, `make the changes`, `sounds good` - Not "ACT"
- `Yes I want you to ACT` - "ACT" embedded in sentence
- `ATC`, `AC`, `ACTT` - Typos

**When the user sends a typo (e.g., "ATC", "AC", "ACTT"):**
- You MUST still include the full PRE-FLIGHT header with MODE: PLAN
- You MUST NOT skip the response structure even when correcting user input
- Respond helpfully but maintain protocol compliance, then ask: `Did you mean "ACT"? Please reply with \`ACT\` to proceed.`

**Recognition rules:**
- **Exact match required:** ACT must be the ENTIRE message (after stripping punctuation) OR start with "ACT on"
- **Embedded ACT is NOT valid:** "I think you should act on this" contains "act" but is NOT authorization
- **Partial authorization:** "ACT on items 1-N" MUST trigger MODE: ACT (scoped to specified items)
- **Authorization prompt REQUIRED for file modifications:** Even when asking clarifying questions, include "Authorization (required): Reply with `ACT` once clarification is provided"

## Step 2B Fallback Details

The bootstrap's Step 2B runs ONLY when the rule-loader skill (Step 2) is unavailable. The condensed grep command lives inline in AGENTS.md; the supporting detail is here.

**A. Keyword extraction:**
1. Identify the PRIMARY VERB (test, deploy, lint, commit, help, fix, create, etc.)
2. Identify the PRIMARY TECHNOLOGY (Python, Docker, Snowflake, etc.)
3. Identify any FILE EXTENSIONS mentioned (.py, .sql, .tsx, etc.)

**CRITICAL:** If ANY word in the request could be a keyword, extract it. Gate 2 should ONLY fail if the grep tool is unavailable OR the request is truly empty. **DO NOT fail Gate 2** for vague requests — always extract at least the verb or noun.

**C. Grep sanity check:** Zero results is almost always an anomaly. RULES_INDEX_COMPACT.md has one row per rule (~200 rules); common keywords (python, sql, docker, deploy, test, streamlit, fastapi, snowflake) should ALWAYS match. On zero results for a common keyword: (1) re-execute grep once, (2) if still zero, use the read_file fallback immediately, (3) note "Grep returned unexpectedly empty — used fallback". Expected volume: 2–15 lines (multi-tech), 1–5 (single-tech); zero for reasonable keywords = ANOMALY.

**D. Gate 2 verification:** Gate 2 passes ONLY if the agent invoked the rule-loader skill (Step 2) OR executed grep / the read_file fallback (Step 2B) AND can cite specific matched lines or rule names. A Gate 2 claim without a corresponding tool call in the same response is INVALID. Claiming Gate 2 from prior session context or summaries is an anti-pattern — re-execute per the Step 0 decision tree. Consistency: if Gate 2 lists keywords, Gate 3 MUST list specific rule filenames OR state "no rules found for [keyword]".

## PRE-FLIGHT Gate Checklist Rules

- Use `[x]` only for completed gates (read_file succeeded); `[ ]` for incomplete (triggers INVALID response).
- List actual keywords searched in Gate 2.
- List domain/activity rules as Gate 3 sub-bullets, or `none matched`; the foundation is cited only on Gate 1.

**Rule Loading Definition:** Loading = Read file + Apply guidance + Declare as Gate 3 sub-bullet. All three required. NEVER declare a rule loaded unless `read_file` returned successfully.

**Citation format (for eval compatibility):** When listing rules as Gate 3 sub-bullets, prefer `<path> (<reason>) — N lines` where `N` is the `wc -l` output. Example: `- [x] Gate 1: Foundation rules/000-global-core.md — 267 lines`. The `— N lines` suffix enables citation-drift detection by the rule-loader evaluator.
