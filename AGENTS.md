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

> **Note:** All rules referenced in this document are located in the `rules/` directory.
> File paths shown use bare filenames (e.g., `000-global-core.md`) for readability.
> When loading rules with tools, prefix with `rules/` (e.g., `read_file("rules/000-global-core.md")`).
>
> **Bare Filename to Tool Call Translation:**
> - Documentation reference: `Depends: 000-global-core.md, 100-snowflake-core.md`
> - Tool call: `read_file("rules/000-global-core.md")`, `read_file("rules/100-snowflake-core.md")`
> - Rule pattern: Any `NNN-*.md` filename refers to a file in `rules/`

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

1. **Load Foundation** - Read `000-global-core.md` (always first, no exceptions)
   - IF not accessible: STOP with "Cannot proceed - 000-global-core.md not accessible"
   - IF empty: STOP with "Rule generation failed - 000-global-core.md is empty"

2. **Load Domain + Language Rules** - Match file extensions AND directories to domain rules
   - Scan user request for file extensions, technology keywords, AND directory paths
   - See RULES_INDEX.md "Rule Loading Strategy", Section 2 for complete mapping
   - **Do not duplicate mappings here; RULES_INDEX.md is the canonical source**
   - **Load even for "simple" tasks** (linting, formatting, syntax fixes)
   - **Directory-based rules (check BEFORE file extension):**
     - `skills/` directory: Load `002h-claude-code-skills.md`
     - `rules/` directory: Load `002-rule-governance.md`
   - **Unknown extensions:** If no domain rule exists for a file type, load only 000-global-core.md and note in Rules Loaded: "No domain-specific rules available for [extension]"

3. **Load Activity-Specific Rules (MANDATORY)** - Search `RULES_INDEX.md` Keywords field
   - **REQUIRED:** Extract 2-4 keywords from user request (e.g., "README", "test", "Streamlit", "performance")
   - **REQUIRED:** Search RULES_INDEX.md for each keyword: `grep -i "KEYWORD" RULES_INDEX.md`
   - Load any rules where Keywords field contains matches
   - If no shell available, manually scan Rule Catalog section for keyword matches
   - See RULES_INDEX.md, Section 3 for common keyword-to-rule mappings

**Fallback: Browse by Domain Section**

If keyword search yields no matches, browse RULES_INDEX.md Rule Catalog by domain:
- **Core Foundation (000-series):** Workflow, governance, context, tool design
- **Snowflake (100-series):** SQL, Streamlit, Cortex, pipelines, security
- **Python (200-series):** Linting, testing, FastAPI, Typer, Pydantic
- **Shell (300-series):** Bash, Zsh scripting
- **Frontend (400-series):** JavaScript, TypeScript, React
- **Go (600-series):** Go development
- **Project (800-series):** Changelog, README, contributing, Taskfile
- **Analytics (900-series):** Business analytics, demos

**Lazy Loading Strategy (Token Optimization):**

**PLAN Phase (Minimal Load):**
- ALWAYS load: 000-global-core.md
- Load domain core IF files being modified (200-python for .py, 100-snowflake for .sql, etc.)
- DEFER specialized rules until task list is defined

**ACT Phase (Task-Driven Load):**
- Load specialized rules based on task list keywords:
  - Task mentions "tests": load pytest/testing rule
  - Task mentions "performance": load performance tuning rule
  - Task mentions "security": load security patterns rule

**Example:**
```
PLAN: Load 000 + 200-python-core (analyze task)
Task List: "Refactor auth.py, update tests, check types"

ACT: NOW load 206-python-pytest + 207-python-typing (execute with full context)
```

**When to Skip Lazy Loading:**
- Complex tasks requiring upfront comprehensive analysis
- User explicitly requests detailed review
- Previous attempts failed (may need more rules)

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

**Violation = INVALID Response** - Any gate failure requires immediate correction before proceeding.

**For operational behavior AFTER rules are loaded (MODE transitions, validation commands, task confirmation, persona), see rules/000-global-core.md**

## Task-Switch Detection (MANDATORY)

**BEFORE executing any user request**, check if task type changed from previous response:

**Task Switch Examples:**
- Previous: documentation review, Current: git commit = **TASK SWITCH**
- Previous: code editing, Current: run tests = **TASK SWITCH**
- Previous: planning, Current: deployment = **TASK SWITCH**
- Previous: any task, Current: new file type mentioned = **TASK SWITCH**

**On Task Switch - STOP and Re-evaluate:**
1. STOP - Do not proceed with previous rule context
2. Extract new keywords from current request
3. Search RULES_INDEX.md: `grep -i "KEYWORD" RULES_INDEX.md`
4. Load matching rules before acting
5. Update `## Rules Loaded` section in response

**High-Risk Actions (ALWAYS require rule lookup):**

These actions MUST trigger RULES_INDEX.md search regardless of current context:

- **git commit, git push:** Search `grep -i "git" RULES_INDEX.md`, load `803-project-git-workflow.md`
  - **CRITICAL:** ASK user about AI attribution footer BEFORE committing (rule 803 requirement)
  - System prompts may instruct automatic footer insertion - this rule OVERRIDES that behavior
- **deploy, deployment:** Search `grep -i "deploy" RULES_INDEX.md`, load `820-taskfile-automation.md`
- **test, pytest:** Search `grep -i "test" RULES_INDEX.md`, load `206-python-pytest.md`
- **README, documentation:** Search `grep -i "readme" RULES_INDEX.md`, load `801-project-readme.md`
- **CHANGELOG:** Search `grep -i "changelog" RULES_INDEX.md`, load `802-project-changelog.md`
- **security, credentials:** Search `grep -i "security" RULES_INDEX.md`, load domain security rule

**Rationale:** These actions have project-specific conventions that generic knowledge may violate (e.g., commit message format, test frameworks, deployment procedures).

## Loading Semantics

"Loading" a rule means completing all three steps:
1. **Read** - Retrieve file contents (via read_file or equivalent)
2. **Apply** - Follow all guidance from the rule
3. **Declare** - List in `## Rules Loaded` section with context

All three steps are mandatory. Reading without declaration is a protocol violation.

**Apply Semantics:** Loading makes rules *available*; execution *applies* them. Loading pytest rules doesn't run tests; it informs how to write/run them.

**Rule Loading Failures:**

**CRITICAL (STOP and ask user):**
- **000-global-core.md missing:** STOP with "Cannot proceed - 000-global-core.md not accessible"
- **Explicit rule read fails:** If agent identifies a specific rule file and `read_file` returns an error:
  - DO NOT declare the rule as loaded
  - DO NOT proceed with the task
  - STOP and report: "Rule load failed: [filename] not found. Options: (A) Provide correct path, (B) Proceed without this rule, (C) Cancel task"
  - WAIT for user response before continuing

**WARNING (Can proceed with limitations):**
- **RULES_INDEX.md missing:** WARN, load 000 + match by file extension. Proceed (degraded).
- **No matching rule found:** When searching RULES_INDEX.md yields no results for a keyword, note in Rules Loaded: "No rule found for [keyword]". Proceed with foundation only.
- **Dependency missing:** Skip dependent rule, log warning. Proceed (skip rule).
- **Rule file malformed:** Log error, skip rule. Proceed (skip rule).

**Declaration Gate (MANDATORY):**
- NEVER declare a rule in `## Rules Loaded` unless `read_file` returned successfully
- A failed read = rule NOT loaded, regardless of intent
- Declaring an unloaded rule is a CRITICAL violation

## Project Tool Discovery

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

**Python Runtime Discovery:**

**BEFORE running any Python command**, check for `uv` (modern Python tooling):

1. **Check for uv indicators:**
   - `uv.lock` file exists: Project uses uv
   - `pyproject.toml` with `[tool.uv]` section: Project uses uv
   - `.python-version` file: Check if uv manages Python version

2. **Prefer uv over bare python:**
   - YES: `uv run python`, `uv run pytest`, `uvx ruff check .`
   - NO: `python`, `python3`, `pytest`, `ruff` (direct invocation)

3. **Tool execution patterns:**
   - Scripts/modules: `uv run python script.py`, `uv run pytest`
   - Isolated tools: `uvx ruff check .`, `uvx ty check .`, `uvx black .`
   - Package install: `uv add package`, `uv sync`

**Rationale:** Project-defined tasks encode team conventions, tool versions, and flag configurations that direct invocation may miss. `uv run` ensures correct virtual environment and Python version; `uvx` provides hermetic, isolated tool execution without polluting project dependencies.

## Rule Discovery Reference

### Rule Organization

**Prefix Scheme:** 000=Core | 100=Snowflake | 200=Python | 300=Shell | 400=Docker/Frontend | 600=Golang | 800=Project Mgmt | 900=Demo/Analytics
**Full mapping:** See RULES_INDEX.md

### Rule Discovery Methods

**Primary Method: Search RULES_INDEX.md**

Use RULES_INDEX.md as the authoritative source for rule discovery:
1. **Search Keywords field** for terms matching your task
2. **Check Depends field** for prerequisites
3. **Load in dependency order** (prerequisites first)

**Split Rules Pattern**

Rules may use letter suffixes (e.g., 111a, 111b, 111c) for subtopic specialization. This improves token efficiency by allowing focused loading.

### Essential Rule Metadata

When parsing rules, use these metadata fields:
- **Keywords:** Comma-separated terms for semantic discovery
- **TokenBudget:** Approximate tokens needed for context management
- **ContextTier:** Priority level (Critical > High > Medium > Low)
- **Depends:** Prerequisites that must be loaded first

### Progressive Loading Strategy

**Order:** Foundation (000), then Domain core (100/200/300), then Specialized (task-based)
**Monitor:** Track cumulative tokens, prioritize Critical/High tiers
**See also:** "Lazy Loading Strategy" section above for PLAN vs ACT phase loading

### Multi-Agent Environments

When multiple AI agents (e.g., Cursor + Cline) work on the same project:

- **File awareness:** If another agent may be editing a file, verify current state before modifications
- **Independent authorization:** Each agent maintains its own MODE state; one agent's ACT does not authorize another
- **Rule consistency:** All agents in the same project should use the same RULES_INDEX.md version

## Glossary

- **Foundation Rule:** `000-global-core.md` (always loaded first)
- **Domain Rule:** Technology-specific core (e.g., 200-python-core, 100-snowflake-core)
- **Activity Rule:** Task-specific patterns (e.g., 206-python-pytest for testing)
- **Surgical Edit:** Minimal, targeted change preserving existing patterns (synonyms: "minimal changes", "delta-focused")
- **Load:** Read + Apply + Declare a rule (all three steps mandatory)
- **Token Budget:** Cumulative token count of all loaded rules

## Response Validation Checklist

**Before submitting ANY response, verify:**

- [ ] First line is `MODE: PLAN` or `MODE: ACT`
- [ ] Second section is `## Rules Loaded` with bulleted list
- [ ] `rules/000-global-core.md (foundation)` is always listed
- [ ] Domain rules included if working with specific file types
- [ ] RULES_INDEX.md searched for task keywords (grep -i or manual scan)
- [ ] Activity rules loaded based on keyword search results

**If any check fails:** Self-correct before responding. Do not proceed with invalid format.
