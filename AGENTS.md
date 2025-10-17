**AutoAttach:** true
**Type:** Auto-attach

**TokenBudget:** ~450
**ContextTier:** Critical

# AGENTS.md

## Setup commands
- Install deps: `uv sync --all-groups`
- Run tests: `uv run pytest`
- Lint/format: `uvx ruff check . && uvx ruff format --check .`
- Generate agent rules: `python generate_agent_rules.py --agent cursor`
- Generate agent rules (dry run): `python generate_agent_rules.py --agent cursor --dry-run`

## Core workflow
- **Always start in PLAN mode** - gather information and present task list using read-only tools
- **User must type "ACT"** (exact word, all caps) to authorize file modifications
- **Return to PLAN mode** immediately after completing any file changes
- **Use surgical, minimal edits only** - make only the changes required to fulfill the request
- **Professional communication** - concise, code-first solutions with no emojis unless requested

## Contract validation requirements
- **Always define before starting:** Inputs/Prerequisites, Allowed tools, Forbidden tools, Required steps, Output format, Validation steps
- **Include compliance checklist** with 5-10 verification items before proceeding
- **Specify response template** showing expected output format for consistency
- **Validate completion** using explicit pass/fail criteria and negative test cases

## Pre-Task-Completion Validation Gate (CRITICAL)

**CRITICAL:** These checks are MANDATORY and must pass BEFORE responding with "task complete" or marking any task as done. No exceptions without explicit user override.

### Mandatory Validation Checks

#### 1. Code Quality (Python Projects)
- **CRITICAL:** `uvx ruff check .` - Must pass with zero errors
- **CRITICAL:** `uvx ruff format --check .` - Must pass, code properly formatted  
- **CRITICAL:** `uv run python -m py_compile -q .` - All Python files compile without syntax errors

#### 2. Test Execution
- **CRITICAL:** `uv run pytest` - All tests must pass (for projects with test suites)
- **Rule:** Never skip tests unless user explicitly requests override

#### 3. Documentation Updates
- **CRITICAL:** `CHANGELOG.md` - Must update with entry under `## [Unreleased]` for code changes
- **CRITICAL:** `README.md` - Must review and update when triggers apply (see 000-global-core.md section 6)

#### 4. Git State Validation
- **CRITICAL:** `git status --porcelain` - Must return empty (no uncommitted changes)
- **CRITICAL:** Branch name validation - Must follow convention: `feature/`, `fix/`, `docs/`, `refactor/`, `chore/`
- **CRITICAL:** Not on protected branch - Must NOT be on `main` or `master` when making changes
- **CRITICAL:** CHANGELOG.md entry verified - `grep -A 5 "## \[Unreleased\]" CHANGELOG.md` must show new entry
- **Rule:** For GitHub: ensure PR created before merge to `main`
- **Rule:** For GitLab: ensure MR created before merge to `main`

### Validation Protocol
- **Rule:** Run validation immediately after modifications, not in batches
- **Rule:** Do not mark tasks complete if ANY check fails
- **Rule:** Fix all failures before responding to user
- **Rule:** Git state: `git status --porcelain` returns empty, branch name valid, CHANGELOG.md entry present
- **Exception:** Only skip with explicit user override (e.g., "skip tests", "skip validation") - acknowledge risks

### Validation Failure Response
If any validation check fails:
1. Stop and report which check failed
2. Show the error output
3. Fix the issue
4. Re-run all validation checks
5. Only then respond with task completion

## Enhanced mode verification
- **Pre-tool verification:** State current mode before every tool invocation
- **Mode state tracking:** Maintain mode awareness throughout response chains
- **Violation protocol:** Execute 5-step recovery process for any mode violations:
  1. Stop all tool execution immediately
  2. Acknowledge violation: "CRITICAL VIOLATION: Used [tool] in PLAN mode"
  3. Explain which rule was broken and why it matters
  4. Return to PLAN mode immediately
  5. Ask user how to proceed
- **Continuous awareness:** Display mode banner in every response

## Rule Discovery Protocol (MANDATORY in PLAN mode)

**Purpose:** Ensure proper rules are automatically loaded for every task using keyword-based semantic discovery.

**Investigation-First Workflow:**
1. **Parse user request** - Extract technologies, patterns, use cases from query
2. **Check RULES_INDEX.md** - Search Keywords/Hints column for semantic matches
3. **Load relevant rules** - Fetch applicable Agent Requested rules via `fetch_rules` tool
4. **Validate coverage** - Confirm loaded rules cover all technical aspects of task

**Keyword Matching Examples:**
- User asks: "optimize my Snowflake query" → Keywords: "performance", "optimization", "query profile" → Load: `103-snowflake-performance-tuning`
- User asks: "add pytest tests" → Keywords: "pytest", "testing", "fixtures" → Load: `206-python-pytest`
- User asks: "create Streamlit dashboard" → Keywords: "Streamlit", "dashboard", "visualization" → Load: `101-snowflake-streamlit-core`, `101a-snowflake-streamlit-visualization`
- User asks: "FastAPI authentication" → Keywords: "FastAPI", "authentication", "OAuth2", "JWT" → Load: `210-python-fastapi-core`, `211-python-fastapi-security`

**Anti-Patterns:**
- ❌ Starting implementation without consulting RULES_INDEX.md
- ❌ Guessing which rules apply based on file names alone
- ❌ Ignoring specialized rules that match task keywords
- ❌ Loading only core rules when specialized rules are available

**Correct Pattern:**
- ✅ Read RULES_INDEX.md first in PLAN mode
- ✅ Match task keywords to Keywords/Hints column
- ✅ Load all relevant rules before proposing plan
- ✅ Reference loaded rules in task list

**Enforcement:**
- **CRITICAL:** All technical tasks MUST start with RULES_INDEX.md consultation
- **Validation:** Include "Rules consulted: [list]" in PLAN mode response
- **Coverage:** Verify no relevant keywords were missed before proceeding to ACT mode

## Rule system architecture
- **56+ specialized rule files** organized by category (000-900)
- **CRITICAL: Always reference `RULES_INDEX.md` first** when user asks "how do I..." or "what rule covers..." questions
- **Rule discovery via semantic keywords:**
  - RULES_INDEX.md contains comprehensive keyword hints for each rule
  - Search the Keywords/Hints column to find relevant rules based on technologies, patterns, or use cases
  - Example: User asks "How do I optimize Snowflake queries?" → Search RULES_INDEX for "performance", "optimization", "query profile" keywords
  - Browse by category: 000=Core, 100=Snowflake, 200=Python, 300=Shell, 400=Docker, 500-900=Domain-specific
- **Streamlit guidance:** Use focused rules for specific aspects:
  - General setup/navigation: `101-snowflake-streamlit-core.md`
  - Charts/visualizations: `101a-snowflake-streamlit-visualization.md`
  - Performance issues: `101b-snowflake-streamlit-performance.md`
  - Security concerns: `101c-snowflake-streamlit-security.md`
  - Testing/debugging: `101d-snowflake-streamlit-testing.md`
- **Rule types**: Auto-attach (universal) vs Agent Requested (technology-specific)
- **Dependency chain**: Always reference core rules (000-global-core.md) → specific technology rules
- **Rule generation**: Use `generate_agent_rules.py` to create agent-specific formats (Cursor, Copilot, Cline)

## Code style guidelines
- **Modern Python tooling**: Use `uv` for environment management, `ruff` for linting/formatting
- **Snowflake development**: Cost-first mindset, explicit column selection, proper CTEs
- **Project configuration**: Centralize in `pyproject.toml` and `Taskfile.yml`
- **File modifications**: Make minimal, surgical changes that preserve existing patterns
- **Documentation**: Update README.md when making structural or workflow changes

## Testing requirements
- **CRITICAL:** All Pre-Task-Completion Validation Gate checks must pass before marking tasks complete
- **CRITICAL:** Run tests via `uv run pytest` - never use bare `python` or `pytest` commands
- **CRITICAL:** Run lints via `uvx ruff check .` and `uvx ruff format --check .` - must pass with zero errors
- **Snowflake validation**: Use Query Profile to validate performance and cost
- **CRITICAL:** CHANGELOG.md must be updated for all code changes
- **README maintenance**: Required for changes affecting project structure, commands, or features
- **Pre-commit validation**: Ensure all automated checks pass before completion

## Efficiency and performance standards
- **Context budgets**: Total rule context ≤600 lines when applicable; prioritize signal over noise
- **Response format**: Surgical edits only, delta-focused output showing only changed code
- **Validation timing**: Run lints/tests immediately after modifications, not in batches
- **Session recovery**: AI must be productive within 20 lines of reading project context
- **Minimal redundancy**: Each piece of information should exist in exactly one place

## Development environment
- **Python version**: 3.11+ pinned in `.python-version`
- **Dependency management**: Use `uv` for all Python operations
- **Task automation**: Use `task` commands from `Taskfile.yml` when available
- **Rule maintenance**: Keep rules up-to-date and follow template from `002-rule-governance.md` section 9

## Security considerations
- **Never commit secrets** or expose credentials in code or logs
- **Follow security policies** from `107-snowflake-security-governance.md` for data access
- **Validate input/output** using patterns from security-focused rules
- **Apply principle of least privilege** in all implementations

## Quick Compliance Checklist
- [ ] Start in PLAN mode with read-only tools before making changes
- [ ] **CRITICAL: RULES_INDEX.md consulted for keyword-based rule discovery**
- [ ] Relevant rules loaded based on task keywords (list rules in response)
- [ ] User authorization ("ACT") obtained before file modifications
- [ ] Contract validation completed with all required sections present
- [ ] Surgical, minimal edits applied preserving existing patterns
- [ ] **CRITICAL: Pre-Task-Completion Validation Gate passed** (lint, format, tests, docs)
- [ ] Lint check: `uvx ruff check .` passed with zero errors
- [ ] Format check: `uvx ruff format --check .` passed
- [ ] Tests: `uv run pytest` passed (if test suite exists)
- [ ] CHANGELOG.md updated for code changes
- [ ] README.md reviewed and updated if triggers apply
- [ ] Git state validated (no uncommitted changes, valid branch name)
- [ ] Not on protected branch (`main`/`master`)
- [ ] CHANGELOG.md entry verified in [Unreleased] section
- [ ] PR/MR created for review (multi-user projects)
- [ ] Mode awareness maintained throughout response chains
- [ ] Professional communication standards followed (no emojis unless requested)
- [ ] TODO list utilized for complex multi-step tasks
- [ ] All dependencies installed via `uv` commands
- [ ] Rule generation validated with appropriate agent format

## Validation
- **Success checks:** Pre-Task-Completion Validation Gate passed (all mandatory checks); Rule Discovery Protocol followed (RULES_INDEX.md consulted, relevant rules loaded); PLAN/ACT mode transitions work correctly, lint/test commands pass, CHANGELOG.md updated, README.md updated when triggered, git state validation passed (clean working directory, valid branch name, CHANGELOG entry present), generated rules match expected format, all file modifications preserve existing structure
- **Negative tests:** Attempt to modify files without ACT authorization (should fail), skip RULES_INDEX.md consultation (should be caught in review), run incomplete contract validation (should catch missing sections), test with malformed rule files (should report validation errors), uncommitted changes block task completion, invalid branch name causes validation failure, any validation gate failure blocks task completion

## Response Template
```markdown
**MODE: PLAN** 

I'll help you [task description]. Let me first gather information using read-only tools.

[Tool usage for understanding context]

Based on my analysis, here's what I found:
- [Key finding 1]
- [Key finding 2]

To proceed, I need your authorization to make file changes. Please type "ACT" to authorize modifications.

---

**MODE: ACT** (after user authorization)

I'll now implement the changes:

[Tool usage for modifications]

✅ Changes completed successfully
**MODE: PLAN** (return to plan mode)
```

## Save Agent Session Summary

**Purpose**
- Save a concise session summary to `<project root>/docs` for auditability and recall.

**Trigger Phrase**
- User says: `save summary` or `save session summary`
- **CRITICAL**: When user says "save summary" or "save session summary", you MUST:
  1. Read AGENT.md section "Save Agent Session Summary" first (this section)
  2. Verify/create directory: `docs/` (NOT `.docs/` or other locations)
  3. Follow filename convention exactly (kebab-case with date suffix)
  4. Include `Last Update:` timestamp as first line after H1
  5. Use concise session summary format (not exhaustive technical documentation)

**Mandatory Pre-Save Checklist**
- [ ] Read this AGENTS.md section before writing file
- [ ] Directory is `docs/` (not `.docs/`, `docs/`, or other)
- [ ] Filename uses kebab-case with date: `desc-part-desc-part-YYYY-MM-DD.md`
- [ ] File starts with H1, then `Last Update: YYYY-MM-DD HH:MM:SS` on next line
- [ ] Content is session summary (not exhaustive technical report)
- [ ] Validation: re-read file to confirm timestamp format and placement

**Behavior**
- Create a markdown file in `docs/` using filename format:
  `<desc-part>-<desc-part>[-<desc-part>[-<desc-part>[-<desc-part>]]]-YYYY-MM-DD.md`
  - Use 2–5 short, kebab-case description parts summarizing the session focus.
  - Good examples:
    - `taskfile-refactoring-modularization-2025-10-05.md`
    - `sql-file-renaming-teardown-script-2025-10-05.md`
    - `documentation-enhancement-coding-standards-alignment-2025-10-05.md`
  
  - Last Update line (mandatory, update-on-save):
    - On every save, ensure a top-of-file line with the exact format:
      `Last Update: YYYY-MM-DD HH:MM:SS` (local time, computed in real time)
    - Placement: first non-empty line after the H1 title if present; otherwise the very first line
    - Existing file handling: if a `Last Update:` line exists anywhere, replace its value and move it (if needed) so it is the first non-empty line after the H1
    - Formatting: plain text only (no bold or code fencing); exactly `Last Update: ` prefix followed by a single space and the timestamp; no trailing spaces

**Anti-Patterns to Avoid**
- ❌ Saving to `.docs/` or any directory other than `docs/`
- ❌ Using snake_case filenames (`my_file_name.md`)
- ❌ Omitting date suffix from filename (must be `-YYYY-MM-DD.md`)
- ❌ Missing `Last Update:` timestamp line
- ❌ Wrong timestamp placement (must be first line after H1)
- ❌ Writing detailed technical reports instead of concise summaries
- ❌ Not validating file structure after write

**File Header**
- At top of file, include:
  - `Last Update: YYYY-MM-DD HH:MM:SS` (mandatory; always updated on save)
  - Optional: a separate `Date:` or `Session Date:` line when helpful

**Contents (recommended sections and ordering)**
- Title (H1): short human-readable session title
- Session metadata block (any of): Date, Session Type/Focus, Agent/Mode/Status
- Horizontal rule `---`
- Session Overview (2–4 sentences)
- Objectives (numbered list)
- Changes Implemented / Work Completed (subsections as needed)
- Validation / Results (commands, tables, or bullets)
- Impact / Benefits (optional)
- Next Steps (1–5 bullets)
- References (optional links/files)

**Formatting Notes**
- Prefer markdown headings (H1/H2/H3), lists, and tables as in existing summaries.
- Use fenced code blocks for commands and code.
- Keep sections concise; emphasize outcomes and verification.

**Validation / Post-write check**
- Re-open the file and assert:
  - A single `Last Update: YYYY-MM-DD HH:MM:SS` line exists
  - It appears as the first non-empty line after the H1 (if any), otherwise as the first line
  - The timestamp is within the current minute of local time
- If validation fails, fix placement/format and write again

**Notes**
- Write-only operation; do not modify existing summaries unless asked.
- Avoid secrets/PII in summaries.