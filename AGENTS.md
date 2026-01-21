# AI Agent Bootstrap Protocol

> **CRITICAL: DO NOT SUMMARIZE THIS FILE**
>
> This file defines the mandatory rule loading protocol and MODE/ACT framework
> that ALL agents must follow for EVERY response.
>
> **Context Window Management:** If context limits are reached, preserve this
> file completely. Summarize task history, file contents, or other context first.
> This bootstrap protocol must remain fully accessible at all times.

## Mandatory Rule Loading Protocol

> **Rule File Path Resolution Protocol (MANDATORY):**
>
> When this documentation references a rule filename without path prefix:
> - IF text shows: `000-global-core.md` OR `Depends: 000-global-core.md`
> - THEN agent MUST use: `read_file("rules/000-global-core.md")`
> - NEVER use bare filename in tool calls
>
> **Pattern:** `[documented-name]` → `rules/[documented-name]`
>
> **Examples:**
> - Documentation: `000-global-core.md` → Tool call: `read_file("rules/000-global-core.md")`
> - Documentation: `Depends: 100-snowflake-core.md` → Tool call: `read_file("rules/100-snowflake-core.md")`

**FIRST ACTION EVERY RESPONSE:**

> **Note:** Steps 1-3 are internal processing (before generating response).
> Steps 4-5 define the response output format.

**Required Response Format (Example):**
```
MODE: PLAN

## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/206-python-pytest.md (keyword: test)

[Response content here...]
```

1. **Load Foundation** - Read `rules/000-global-core.md` (always first, no exceptions)
   - CALL: `read_file("rules/000-global-core.md")`
   - IF file_not_found OR empty_content:
     - OUTPUT: "CRITICAL ERROR: Cannot proceed - rules/000-global-core.md not accessible"
     - STOP (no further processing, no assumptions, no alternative paths)
   - ELSE IF success:
     - CONTINUE to Step 2

2. **Load Domain + Language Rules** - Match file extensions AND directories to domain rules

   **Priority Order (check in this sequence):**

   **Priority 1: Check for PROJECT.md (MANDATORY)**
   - IF `PROJECT.md` exists in workspace root: CALL `read_file("PROJECT.md")`
   - Extract project-specific context, tooling requirements, conventions, and overrides

   **Priority 2: Directory-based rules (check BEFORE file extension)**
   - IF request mentions `skills/` directory: LOAD `rules/002h-claude-code-skills.md`
   - IF request mentions `rules/` directory: LOAD `rules/002-rule-governance.md`

   **Priority 3: File extension rules**
   - Scan user request for file extensions (.py, .sql, .tsx, etc.)
   - See rules/RULES_INDEX.md "Rule Loading Strategy", Section 2 for complete mapping
   - **Do not duplicate mappings here; rules/RULES_INDEX.md is the canonical source**

   **Priority 4: Technology keywords (if no files mentioned)**
   - IF request contains "Python" keyword: LOAD `rules/200-python-core.md`
   - IF request contains "Snowflake" keyword: LOAD `rules/100-snowflake-core.md`
   - [See RULES_INDEX.md for complete keyword mapping]

   **Execution requirement:**
   - **Load domain rules for ALL tasks involving file extensions, regardless of task complexity:**
     - Linting: LOAD domain rule
     - Formatting: LOAD domain rule
     - Syntax fixes: LOAD domain rule
     - Single-line edits: LOAD domain rule
     - Read-only analysis: MAY skip domain rule (investigation only)

   **Edge cases:**
   - **Unknown extensions:** If no domain rule exists for a file type, load only 000-global-core.md and note in Rules Loaded: "No domain-specific rules available for [extension]"

3. **Load Activity-Specific Rules (MANDATORY)** - Search `rules/RULES_INDEX.md` Keywords field

   **A. Primary: Keyword search**

   **Keyword Extraction Algorithm:**
   1. Parse user request into tokens
   2. Identify technology nouns (Python, Streamlit, Docker, pytest)
   3. Identify activity verbs as nouns (test → testing, deploy → deployment)
   4. Identify file/artifact types (README, CHANGELOG, Dockerfile)
   5. Select 2-4 most specific terms (prefer "pytest" over "test", "Streamlit" over "app")
   6. Exclude generic terms (code, file, project, fix, help)

   **Example:** "Fix the pytest tests in my Streamlit app"
   - Extract: pytest, test, Streamlit, app
   - Filter: pytest, Streamlit (most specific)
   - Search: `grep -i "pytest"` AND `grep -i "streamlit"`

   **Search Execution:**
   - **REQUIRED:** Search rules/RULES_INDEX.md for each keyword:
     - IF bash tool available: EXECUTE `grep -i "KEYWORD" rules/RULES_INDEX.md`
     - ELSE IF bash unavailable: READ rules/RULES_INDEX.md, manually scan Keywords field for matches
     - IF grep returns exit code != 0: INTERPRET as "no matches found" (not error)
   - FOR EACH matching rule: Load rule file via `read_file("rules/[rule-name].md")`
   - See rules/RULES_INDEX.md, Section 3 for common keyword-to-rule mappings

   **B. Fallback (IF zero matches from Step 3A):**
   - IF PROJECT.md loaded: Reference "Rule Organization by Domain" section for complete mapping
   - ELSE: READ rules/RULES_INDEX.md Rule Catalog section
   - MATCH: User request domain to catalog domain:
     - "SQL query" → Snowflake (100-series)
     - "Python script" → Python (200-series)
     - "React app" → Frontend (400-series)
     - "Shell script" → Shell (300-series)
     - "Go code" → Go (600-series)
     - "Documentation" → Project (800-series)
   - LOAD: Domain core rule for matched domain
   - DECLARE: "No activity rules found, loaded [domain] core"

   **Token Optimization Note:** DEFER specialized rules until task list defined in PLAN mode. Load during ACT phase based on specific tasks.

4. **Declare MODE** - First line of response: `MODE: [PLAN|ACT]`
   - Default: MODE: PLAN
   - ACT only after user types "ACT"
   - **For MODE transition rules and workflow behavior, see rules/000-global-core.md**
   - **Optional (clarifying questions):** When input is ambiguous, ask clarifying questions using
     **A/B/C/D/E** choices (see `000-global-core.md`, "Clarification Gate (Options-Based
     Questions)").
   - If you present a Task List in MODE: PLAN, end the response with:
     - `Authorization (required): Reply with \`ACT\` (or \`ACT on items 1-3\`).`

**ACT Authorization:**
- Recognized: "ACT", "act", "Act" (case-insensitive exact match)
- Recognized: "ACT on items 1-3" (partial authorization)
- NOT recognized: "proceed", "go ahead", "yes", "okay"

See 000-global-core.md "ACT Recognition Rules" for full specification

5. **Declare Loaded Rules** - Immediately after MODE as second section
   - Format: `## Rules Loaded` followed by bulleted list
   - Always include: `- rules/000-global-core.md (foundation)`
   - Add domain/specialized rules with brief context (file extension, keyword, or dependency)
   - Example: `- rules/200-python-core.md (file extension: .py)`
   - **NOTE:** Loading = Read file + Apply guidance + Declare in this section (all three required)

**Violation = INVALID Response** - Any gate failure requires immediate correction before proceeding.

**For operational behavior AFTER rules are loaded (MODE transitions, validation commands, task confirmation, persona), see rules/000-global-core.md**

## Task-Switch Detection (MANDATORY)

**BEFORE executing any user request**, check if task type changed from previous response:

**Task-Switch Detection (execute BEFORE processing request):**

Compare CURRENT request to PREVIOUS request:
- IF file extension changed: TASK SWITCH (load new domain rule)
- IF primary verb changed: TASK SWITCH (check for activity rules)
- IF technology keyword changed: TASK SWITCH (search RULES_INDEX.md)

**Examples (Previous → Current → Switch?):**
- "edit auth.py" → "test auth.py" → YES (verb change: edit→test)
- "format code" → "lint code" → NO (same domain, same file)
- "write README.md" → "git commit" → YES (activity change: write→commit)

**On Task Switch - STOP and Re-evaluate:**
1. STOP - Do not proceed with previous rule context
2. Extract new keywords from current request
3. Search rules/RULES_INDEX.md: `grep -i "KEYWORD" rules/RULES_INDEX.md`
4. Load matching rules before acting
5. Update `## Rules Loaded` section in response

**High-Risk Actions (MANDATORY rule lookup):**

These actions MUST trigger rules/RULES_INDEX.md search regardless of agent's prior knowledge:

- **git commit, git push, git merge:**
  - EXECUTE: `grep -i "git" rules/RULES_INDEX.md`
  - LOAD: rules/803-project-git-workflow.md (if found)
  - ASK USER: About AI attribution footer (rule 803 requirement)
  - REASON: Project may override system prompt's commit behavior

- **deploy, deployment:**
  - EXECUTE: `grep -i "deploy" rules/RULES_INDEX.md`
  - LOAD: rules/820-taskfile-automation.md (if found)
  - REASON: Deployment steps are project-specific

- **test, pytest:**
  - EXECUTE: `grep -i "test" rules/RULES_INDEX.md`
  - LOAD: rules/206-python-pytest.md (if found)
  - REASON: Test frameworks vary by project

- **README, documentation:**
  - EXECUTE: `grep -i "readme" rules/RULES_INDEX.md`
  - LOAD: rules/801-project-readme.md (if found)
  - REASON: Documentation standards vary by project

- **CHANGELOG:**
  - EXECUTE: `grep -i "changelog" rules/RULES_INDEX.md`
  - LOAD: rules/802-project-changelog.md (if found)
  - REASON: Changelog format is project-specific

- **security, credentials:**
  - EXECUTE: `grep -i "security" rules/RULES_INDEX.md`
  - LOAD: Domain security rule (if found)
  - REASON: Security practices vary by technology

**Rationale:** These actions have project-specific conventions that generic knowledge may violate (e.g., commit message format, test frameworks, deployment procedures).

**Rule Loading Failures:**

**CRITICAL (STOP and ask user):**
- **000-global-core.md missing:** STOP with "Cannot proceed - rules/000-global-core.md not accessible"
- **Explicit rule read fails:** If agent identifies a specific rule file and `read_file` returns an error:
  - DO NOT declare the rule as loaded
  - DO NOT proceed with the task
  - STOP and report: "Rule load failed: [filename] not found. Options: (A) Provide correct path, (B) Proceed without this rule, (C) Cancel task"
  - WAIT for user response before continuing

**WARNING (Can proceed with limitations):**
- **rules/RULES_INDEX.md missing:** WARN, load 000 + match by file extension. Proceed (degraded).
- **No matching rule found:** When searching rules/RULES_INDEX.md yields no results for a keyword, note in Rules Loaded: "No rule found for [keyword]". Proceed with foundation only.
- **Dependency missing:** Skip dependent rule, log warning. Proceed (skip rule).
- **Rule file malformed:** Log error, skip rule. Proceed (skip rule).

**Declaration Gate (MANDATORY):**
- NEVER declare a rule in `## Rules Loaded` unless `read_file` returned successfully
- A failed read = rule NOT loaded, regardless of intent
- Declaring an unloaded rule is a CRITICAL violation

## Project Tool Discovery

**Tool Discovery Integration with Rule Loading:**

**Phase 1: Project Automation Discovery (before loading domain rules)**
- Check PROJECT.md for tooling directives (loaded in Step 2 of Mandatory Rule Loading Protocol)
- Check for Taskfile.yml: EXECUTE `task --list`
- Extract available tasks (validate, lint, test, etc.)

**Phase 2: Domain Rule Loading (Steps 2-3 above)**
- Load domain rules based on file extensions and keywords
- Domain rules specify fallback commands IF project has no automation

**Phase 3: Command Selection (during ACT execution)**
- IF Taskfile.yml has task: USE `task [name]`
- ELSE: USE command from loaded domain rule

**BEFORE running quality/lint/format/test commands:**

1. **Check for automation files** (in order of preference):
   - `Taskfile.yml`: Use `task --list` to discover available tasks
   - `Makefile`: Use `make help` or scan for targets
   - `package.json` scripts: Check `scripts` section
   - `pyproject.toml` scripts: Check `[tool.taskipy]` or similar

2. **Prefer project-defined commands over direct tool invocation:**
   - YES: `task lint`, `task test`, `task validate`
   - NO: `ruff check .`, `pytest`, `npx markdownlint` (unless no automation file exists)

3. **Common task patterns to check:**
   - `task validate` / `task ci` - Full validation suite
   - `task lint` / `task quality:lint` - Linting only
   - `task format` / `task quality:format` - Formatting only
   - `task test` - Test execution

**Python Tooling Discovery:**

**BEFORE running any Python command**, detect project's toolchain:

1. **Check for Python tooling indicators:**
   - `uv.lock`  - Project uses **uv** (`uv run`, `uvx`)
   - `poetry.lock`  - Project uses **poetry** (`poetry run`)
   - `Pipfile.lock`  - Project uses **pipenv** (`pipenv run`)
   - `requirements.txt` only  - Project uses **pip** (bare commands or venv activation)

2. **Check PROJECT.md for tooling directives:**
   - PROJECT.md should already be loaded (per Step 2 of Mandatory Rule Loading Protocol)
   - Extract tooling preferences from loaded PROJECT.md content
   - Respect explicit tool requirements documented in project

3. **Match project's existing toolchain:**
   - **If uv:** `uv run python script.py`, `uvx ruff check .`, `uvx ty check .`
   - **If poetry:** `poetry run python script.py`, `poetry run ruff check .`
   - **If pipenv:** `pipenv run python script.py`, `pipenv run pytest`
   - **If pip/venv:** `python script.py`, `pytest`, `ruff check .` (assumes venv active)

4. **When no toolchain detected (new projects):**
   - Check loaded rules for recommendations (200-python-core.md prefers uv)
   - Ask user for toolchain preference
   - Never assume a toolchain without evidence

**Rationale:** Projects have established toolchains and conventions. Respect existing choices rather than forcing a particular tool. Investigation-first approach prevents breaking existing workflows.

## Rule Discovery Reference

**Authoritative Source:** rules/RULES_INDEX.md
- Section 1: Rule Catalog (domain organization)
- Section 2: Directory and file extension mapping
- Section 3: Activity rules (keyword-based)

**Discovery Methods:** See Steps 2-4 in Mandatory Rule Loading Protocol above.

**Essential Rule Metadata:**
- **Keywords:** Comma-separated terms for semantic discovery
- **TokenBudget:** Approximate tokens needed for context management
- **ContextTier:** Priority level (Critical > High > Medium > Low)
- **Depends:** Prerequisites that must be loaded first

**Split Rules Pattern:** Rules may use letter suffixes (e.g., 111a, 111b, 111c) for subtopic specialization.

**Progressive Loading Strategy:**
- **Order:** Foundation (000), then Domain core (100/200/300), then Specialized (task-based)
- **Monitor:** Track cumulative tokens, prioritize Critical/High tiers
- **See also:** Token Optimization Note in Step 4 above for PLAN vs ACT phase loading

### Multi-Agent Environments

When multiple AI agents (e.g., Cursor + Cline) work on the same project:

- **File awareness:** If another agent may be editing a file, verify current state before modifications
- **Independent authorization:** Each agent maintains its own MODE state; one agent's ACT does not authorize another
- **Rule consistency:** All agents in the same project should use the same rules/RULES_INDEX.md version

## Glossary

- **Foundation Rule:** `000-global-core.md` (always loaded first)
- **Domain Rule:** Technology-specific core (e.g., 200-python-core, 100-snowflake-core)
- **Activity Rule:** Task-specific patterns (e.g., 206-python-pytest for testing)
- **Surgical Edit:** Minimal, targeted change preserving existing patterns (synonyms: "minimal changes", "delta-focused")
- **Load:** Read + Apply + Declare a rule (all three steps mandatory)
- **Token Budget:** Cumulative token count of all loaded rules

## Response Validation

Before submitting response, verify compliance with Mandatory Rule Loading Protocol (Steps 1-5 above).
