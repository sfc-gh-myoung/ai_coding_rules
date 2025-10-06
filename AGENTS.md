**AutoAttach:** true
**Type:** Auto-attach

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

## Rule system architecture
- **49+ specialized rule files** organized by category (000-900)
- **Use `RULES_INDEX.md`** to quickly find relevant rules for specific technologies
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
- **All lint checks must pass** before marking tasks complete
- **Run tests via `uv run`** - never use bare `python` or `pytest` commands
- **Snowflake validation**: Use Query Profile to validate performance and cost
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
- [ ] User authorization ("ACT") obtained before file modifications
- [ ] Contract validation completed with all required sections present
- [ ] Surgical, minimal edits applied preserving existing patterns
- [ ] Lint and typecheck commands executed successfully
- [ ] Mode awareness maintained throughout response chains
- [ ] Professional communication standards followed (no emojis unless requested)
- [ ] TODO list utilized for complex multi-step tasks
- [ ] All dependencies installed via `uv` commands
- [ ] Rule generation validated with appropriate agent format

## Validation
- **Success checks:** PLAN/ACT mode transitions work correctly, lint/test commands pass, generated rules match expected format, all file modifications preserve existing structure
- **Negative tests:** Attempt to modify files without ACT authorization (should fail), run incomplete contract validation (should catch missing sections), test with malformed rule files (should report validation errors)

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
- Save a concise session summary to `<project root>/agent/summaries` for auditability and recall.

**Trigger Phrase**
- User says: `save summary` or `save session summary`
- **CRITICAL**: When user says "save summary" or "save session summary", you MUST:
  1. Read AGENT.md section "Save Agent Session Summary" first (this section)
  2. Verify/create directory: `agent/summaries/` (NOT `.agent/` or other locations)
  3. Follow filename convention exactly (kebab-case with date suffix)
  4. Include `Last Update:` timestamp as first line after H1
  5. Use concise session summary format (not exhaustive technical documentation)

**Mandatory Pre-Save Checklist**
- [ ] Read this AGENTS.md section before writing file
- [ ] Directory is `agent/summaries/` (not `.agent/`, `docs/`, or other)
- [ ] Filename uses kebab-case with date: `desc-part-desc-part-YYYY-MM-DD.md`
- [ ] File starts with H1, then `Last Update: YYYY-MM-DD HH:MM:SS` on next line
- [ ] Content is session summary (not exhaustive technical report)
- [ ] Validation: re-read file to confirm timestamp format and placement

**Behavior**
- Create a markdown file in `agent/summaries` using filename format:
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
- ❌ Saving to `.agent/`, `docs/`, or any directory other than `agent/summaries/`
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