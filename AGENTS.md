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