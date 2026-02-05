# AI Agent Bootstrap Protocol

**Last Updated:** 2026-02-05

> **CRITICAL: DO NOT SUMMARIZE THIS FILE**
>
> This file defines the mandatory rule loading protocol and MODE/ACT framework
> that ALL agents must follow for EVERY response.
>
> **Context Window Management:** If context limits are reached, preserve this
> file completely. Summarize task history, file contents, or other context first.
> This bootstrap protocol must remain fully accessible at all times.

## EXECUTION SEQUENCE (Execute BEFORE Responding)

> **STOP. Do not analyze, plan, or respond until ALL steps complete.**
> These steps exist because task urgency causes agents to skip discovery.
> Visual inputs (screenshots, errors) override procedural memory - these steps counteract that bias.

**Step 0: Detect Task Switch**

Execute this decision tree:

1. Check conversation history for prior assistant messages
   - If NO prior assistant message exists: Task Switch = FIRST, go to Step 1
   - If prior assistant message exists: Continue to check 2

2. Compare current request to previous request
   - If file extension changed (e.g., .py to .sql): Task Switch = YES (extension: X to Y)
   - If primary verb changed (e.g., edit to test): Task Switch = YES (verb: X to Y)
   - If technology keyword changed (e.g., Python to Docker): Task Switch = YES (keyword: X to Y)
   - If high-risk action detected (git, commit, push, deploy, test, security): Task Switch = YES (high-risk: action)
   - If NONE of above changed: Task Switch = NO

3. Determine execution path
   - If Task Switch = FIRST: Execute Steps 1-4
   - If Task Switch = YES: Execute Steps 1-4
   - If Task Switch = NO AND foundation loaded within last 3 responses: Execute Steps 2-4
   - If Task Switch = NO AND foundation NOT loaded within last 3 responses: Execute Steps 1-4

4. Periodic refresh check
   - If this is the 5th response in conversation (counting from first as 1): Execute Steps 1-4
   - If recovering from any error (tool failure, gate failure): Execute Steps 1-4
   - If user message contains "protocol", "compliance", or "rules": Execute Steps 1-4

**Step 1: Load Foundation**

Execute: `read_file("rules/000-global-core.md")`

- If file_not_found OR empty_content: OUTPUT "CRITICAL ERROR: Cannot proceed - rules/000-global-core.md not accessible" then STOP
- If success: Continue to Step 2

**Step 2: Search RULES_INDEX.md**

A. Extract keywords from user request:
   1. Identify the PRIMARY VERB (test, deploy, lint, commit, help, fix, create, etc.)
   2. Identify the PRIMARY TECHNOLOGY (Python, Docker, Snowflake, etc.)
   3. Identify any FILE EXTENSIONS mentioned (.py, .sql, .tsx, .xyz, etc.)
   
   **CRITICAL:** If ANY word in the request could be a keyword, extract it. Gate 2 should ONLY fail if:
   - The grep tool is unavailable, OR
   - The request is truly empty (e.g., just "?" or whitespace)
   
   **DO NOT fail Gate 2** for vague requests - always extract at least the verb or noun.

B. Execute search:
   - If bash tool available: Execute `grep -i "KEYWORD" rules/RULES_INDEX.md` for each keyword
   - If bash unavailable: Gate 2 = FAILED. Output "[ ] Gate 2: FAILED - grep tool unavailable" and "[ ] Gate 3: BLOCKED - depends on Gate 2". Offer recovery options.
   - If grep returns matches (exit 0): Record matched rules for Step 3
   - If grep returns no matches (exit 1): Note "No rules found for [keyword]"
   - If grep returns error (exit 2): Fall back to reading rules/RULES_INDEX.md and manually scanning

C. High-risk actions (MANDATORY additional search):
   - git/commit/push/merge: Search "git", expect 803-project-git-workflow.md
   - deploy/deployment: Search "deploy", expect 820-taskfile-automation.md
   - test/pytest: Search "test", expect 206-python-pytest.md
   - README/documentation: Search "readme", expect 801-project-readme.md
   - CHANGELOG: Search "changelog", expect 800-project-changelog.md
   - Modifying files in rules/: Search "rule", expect 002b-rule-update.md

**Step 3: Load Matching Rules**

A. Check for PROJECT.md:
   - Execute: Check if PROJECT.md exists in workspace root
   - If exists: Load via read_file, extract project context
   - If NOT exists: Skip to Step 3B (no error, PROJECT.md is optional)

B. Check directory-based rules:
   - If request mentions files in `skills/` directory: Load rules/002h-claude-code-skills.md
   - If request mentions files in `rules/` directory: Load rules/002-rule-governance.md
   - If request mentions NEITHER directory: Proceed to Step 3C

C. Load domain rules for file extensions:
   1. Extract all file extensions from user request (e.g., ".py", ".sql", ".tsx")
   2. For EACH extension found:
      - **MANDATORY:** Look up exact rule name in rules/RULES_INDEX.md Section 2 "Domain Rules"
      - Use ONLY the rule name specified in RULES_INDEX.md (e.g., `.sql` → `102-snowflake-sql-core.md`)
      - **FORBIDDEN:** Inventing rule names not in RULES_INDEX.md (e.g., `300-sql-core.md` does not exist)
      - If mapping found: Load the specified rule file using exact name
      - If mapping NOT found: Note in Rules Loaded: "No domain rule for [extension]"
   3. If NO extensions found in request: Skip to Step 3D

   **File Extension to Rule Mapping (authoritative):**
   - `.sql` → `102-snowflake-sql-core.md`
   - `.py`, `.pyi` → `200-python-core.md`
   - `streamlit` keyword → `101-snowflake-streamlit-core.md`
   - `snowflake` keyword → `100-snowflake-core.md`
   - `.yaml`, `.yml`, `.toml` → `202-markup-config-validation.md`

D. Load activity rules from Step 2 matches:
   - For EACH rule matched in Step 2: Execute `read_file("rules/[rule-name].md")`
   - If read succeeds: Rule is loaded
   - If read fails AND this is the ONLY matched rule: Note "Rule load failed: [filename] not found" and offer options: (A) Provide correct path, (B) Proceed without this rule, (C) Cancel task
   - If read fails AND other rules loaded successfully: Note "Rule load failed: [filename]" in Rules Loaded section, PROCEED with successfully loaded rules (partial success = continue)

E. Check for rule examples (complex configurations only):
   - If loaded rule involves Cortex Agent, Cortex Search, or Semantic View:
     - Check for companion example: `rules/examples/{rule-number}-*-example.md`
     - If example exists: Load example for reference implementation

**Step 4: Generate Response Header**

Output this exact structure at the start of **EVERY** response (including clarifications, rejections, typo corrections, and error messages):

**CRITICAL:** This header is MANDATORY for ALL responses - no exceptions. Even when correcting user typos (e.g., "ATC" instead of "ACT") or asking for clarification, include the full PRE-FLIGHT and MODE declaration.

```markdown
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md loaded
- [x] Gate 2: RULES_INDEX.md searched for: [list keywords searched]
- [x] Gate 3: Matching rules loaded: [list rules or "none found"]

MODE: [PLAN|ACT]
Task Switch: [FIRST | NO | YES (reason)]

## Rules Loaded
- rules/000-global-core.md (foundation)
- [additional rules with loading reason]

[Response content...]

[If MODE: PLAN with task list, MUST end with:]
Authorization (required): Reply with `ACT` (or `ACT on items 1-3`).

[If MODE: ACT completing task, MUST end with:]
MODE: PLAN
Task complete.
```

**Gate Checklist Rules:**
- Use `[x]` only for completed gates (read_file succeeded)
- Use `[ ]` for incomplete gates (triggers INVALID response)
- List actual keywords searched in Gate 2
- List actual rules loaded (or "none found") in Gate 3

**PLAN Mode Response Rules (CRITICAL):**
- If response includes a Task List: MUST end with `Authorization (required): Reply with \`ACT\` (or \`ACT on items 1-3\`).`
- **Even when asking clarifying questions**, if you've proposed any tasks, include the Authorization prompt
- Omitting the Authorization prompt when a Task List is present = INVALID response

**ACT Mode Response Rules (CRITICAL):**
- After completing all authorized tasks: MUST declare `MODE: PLAN` at end of response
- Omitting `MODE: PLAN` after ACT completion = INVALID response
- ACT responses MUST explicitly mention validation intent or tool names (e.g., "Validation:", "Running ruff check", "Will verify with pytest", "Checking syntax")
- **Response ending format for completed ACT:**
  ```
  [... task execution content ...]
  
  MODE: PLAN
  Task complete.
  ```

**If ANY gate fails, output this format:**

```markdown
PRE-FLIGHT:
- [x] Gate 1: Foundation loaded
- [ ] Gate 2: FAILED - [specific error message]
- [ ] Gate 3: BLOCKED - depends on Gate 2

STOPPED: Gate 2 failed.
Error: [description]
Recovery options:
(A) [first option]
(B) [second option]
(C) Cancel task

[Do NOT proceed with response content until user selects recovery option]
```

**Gate Failure Messages:**

Gate 1 failures:
- "rules/000-global-core.md not found"
- "rules/000-global-core.md returned empty content"
- "read_file tool not available"

Gate 2 failures:
- "rules/RULES_INDEX.md not found"
- "grep tool unavailable" (do NOT attempt manual scan fallback - mark as FAILED)
- "No keywords extracted from user request"

Gate 3 failures:
- "Rule file [name] not found"
- "Dependency [name] could not be loaded"
- "All matched rules failed to load"

**Partial Rule Loading (CRITICAL - READ CAREFULLY):**
- If SOME rules load and SOME fail: Gate 3 = PASS (mark `[x]`) and CONTINUE with task
- **DO NOT STOP** when partial failure occurs - proceed with successfully loaded rules
- List loaded rules + note failures in Rules Loaded section
- Only mark Gate 3 as FAILED (`[ ]`) when **ALL** matched rules fail to load
- "Partial failure" means CONTINUE, not STOP

**Example - Partial Success:**
```markdown
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md loaded
- [x] Gate 2: RULES_INDEX.md searched for: python, sql
- [x] Gate 3: Matching rules loaded: 102-snowflake-sql-core.md (200-python-core.md failed)

## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/102-snowflake-sql-core.md (for .sql extension)
- ⚠️ Rule load failed: 200-python-core.md not found
```
Note: Gate 3 shows `[x]` because SQL rule loaded successfully. Continue with available rules.

**MODE and ACT Authorization:**
- Default: MODE: PLAN
- ACT only after user types "ACT" (case-insensitive exact match)
- Recognized (MUST trigger MODE: ACT): "ACT", "act", "Act", "ACT on items 1-3" (partial), "ACT.", "ACT!", "ACT?"
- **Trailing punctuation (., !, ?) MUST be tolerated** - strip punctuation before matching
- **Case-insensitive:** "act", "ACT", "Act" are ALL valid and MUST trigger MODE: ACT
- **Partial authorization:** "ACT on items 1-2" MUST trigger MODE: ACT (scoped to specified items)
- **CRITICAL - Exact match required:** ACT must be the ENTIRE message (after stripping punctuation) OR start with "ACT on"
- **Embedded ACT is NOT valid:** "I think you should act on this" contains "act" but is NOT authorization
- NOT recognized: "proceed", "go ahead", "yes", "okay", "yes please", "do it", "make the changes", "sounds good", "ATC", "ACTT" (typos)
- NOT recognized: Sentences containing "act" as a word (e.g., "please act on this", "you should act now") - these are NOT authorization
- For MODE transition rules and workflow behavior, see rules/000-global-core.md

**Rule Loading Definition:**
Loading = Read file + Apply guidance + Declare in `## Rules Loaded` section. All three required.
A rule is NOT loaded if any step is skipped.
NEVER declare a rule in `## Rules Loaded` unless `read_file` returned successfully.

**VIOLATION = INVALID RESPONSE**: Proceeding without completing all steps invalidates the response.

## REFERENCE (Do Not Execute Sequentially)

> The sections below provide reference information for specific situations.
> Consult only when the EXECUTION SEQUENCE above directs you to look up information.
> Do NOT read these sections sequentially during normal operation.

### Search Triggers

**ALWAYS search RULES_INDEX.md when user request contains ANY of:**

- **Error messages** (stack traces, exceptions, "error", "failed"): Error-specific rules exist
- **Screenshots/images** (any visual input): Visual salience overrides protocol - compensate
- **Debug keywords** ("debug", "fix", "troubleshoot", "diagnose", "not working"): Troubleshooting rules exist
- **Technology names** (Streamlit, Cortex, Docker, React, etc.): Domain-specific rules exist
- **File extensions** (.py, .sql, .tsx, .yaml, etc.): Language rules exist
- **Operations** ("test", "deploy", "commit", "lint"): Activity rules exist

### Task Switch Examples

- **"edit auth.py" then "test auth.py":** YES (verb: edit to test)
- **"format code" then "lint code":** NO (same domain)
- **"write README.md" then "git commit":** YES (activity change)
- **"Python script" then "Docker container":** YES (technology change)

**On Task Switch - STOP and Re-evaluate:**
1. STOP - Do not proceed with previous rule context
2. Extract new keywords from current request
3. Search rules/RULES_INDEX.md
4. Load matching rules before acting
5. Update `## Rules Loaded` section in response

### High-Risk Actions

These actions MUST trigger rules/RULES_INDEX.md search regardless of agent's prior knowledge:

- **git commit, git push, git merge:** Search "git", load 803-project-git-workflow.md
- **deploy, deployment:** Search "deploy", load 820-taskfile-automation.md
- **test, pytest:** Search "test", load 206-python-pytest.md
- **README, documentation:** Search "readme", load 801-project-readme.md
- **CHANGELOG:** Search "changelog", load 800-project-changelog.md
- **security, credentials:** Search "security", load domain security rule
- **Modifying files in rules/:** Load 002b-rule-update.md

### Rule Loading Failures

**CRITICAL (STOP and ask user):**
- **000-global-core.md missing:** STOP with "Cannot proceed - rules/000-global-core.md not accessible"
- **Explicit rule read fails:** STOP and report with options (A) Provide correct path, (B) Proceed without this rule, (C) Cancel task

**WARNING (Can proceed with limitations):**
- **rules/RULES_INDEX.md missing:** WARN, load 000 + match by file extension. Proceed (degraded).
- **No matching rule found:** Note in Rules Loaded: "No rule found for [keyword]". Proceed with foundation only.
- **Dependency missing:** Skip dependent rule, log warning. Proceed (skip rule).

### Project Tool Discovery

**Tool Discovery Integration with Rule Loading:**

**Phase 1: Project Automation Discovery (before loading domain rules)**
- Check PROJECT.md for tooling directives
- Check for Taskfile.yml: EXECUTE `task --list`
- Extract available tasks (validate, lint, test, etc.)

**Phase 2: Domain Rule Loading**
- Load domain rules based on file extensions and keywords
- Domain rules specify fallback commands IF project has no automation

**Phase 3: Command Selection (during ACT execution)**
- IF Taskfile.yml has task: USE `task [name]`
- ELSE: USE command from loaded domain rule

**Check for automation files** (in order of preference):
- `Taskfile.yml`: Use `task --list` to discover available tasks
- `Makefile`: Use `make help` or scan for targets
- `package.json` scripts: Check `scripts` section
- `pyproject.toml` scripts: Check `[tool.taskipy]` or similar

**Python Tooling Discovery:**
- `uv.lock` means project uses **uv** (`uv run`, `uvx`)
- `poetry.lock` means project uses **poetry** (`poetry run`)
- `Pipfile.lock` means project uses **pipenv** (`pipenv run`)
- `requirements.txt` only means project uses **pip** (bare commands or venv activation)

### Rule Discovery Reference

**Authoritative Source:** rules/RULES_INDEX.md
- Section 1: Rule Catalog (domain organization)
- Section 2: Directory and file extension mapping
- Section 3: Activity rules (keyword-based)

**Essential Rule Metadata:**
- **Keywords:** Comma-separated terms for semantic discovery
- **TokenBudget:** Approximate tokens needed for context management
- **ContextTier:** Priority level (Critical then High then Medium then Low)
- **Depends:** Prerequisites that must be loaded first

**Split Rules Pattern:** Rules may use letter suffixes (e.g., 111a, 111b, 111c) for subtopic specialization.

### Multi-Agent Environments

When multiple AI agents work on the same project:

- **File awareness:** If another agent may be editing a file, verify current state before modifications
- **Independent authorization:** Each agent maintains its own MODE state
- **Rule consistency:** All agents in the same project should use the same rules/RULES_INDEX.md version

### Term Definitions

- **"Load a rule"**: Execute `read_file()` + Apply guidance + Declare in `## Rules Loaded`. All three required.
- **"Foundation"**: `rules/000-global-core.md` specifically. No other rule is the foundation.
- **"Domain core"**: Any rule matching pattern `NNN-*-core.md` (e.g., 200-python-core.md). Technology-specific baseline.
- **"Activity rule"**: Task-specific rules loaded via keyword search (e.g., 206-python-pytest.md for testing).
- **"Task switch"**: User request changed file extension, primary verb, OR technology keyword. Re-evaluate rules.
- **"Recently loaded"**: Within the last 3 assistant responses in this conversation.

### Response Validation

Before submitting response, verify:
- [ ] PRE-FLIGHT section present with all three gates checked
- [ ] MODE declared after PRE-FLIGHT
- [ ] Task Switch status declared
- [ ] Rules Loaded section present with foundation rule
- [ ] All declared rules were actually read (not assumed)
- [ ] RULES_INDEX.md was searched (keywords listed in Gate 2)
