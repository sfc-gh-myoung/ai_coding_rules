**Description:** Directives for creating, modifying, and maintaining project automation using `Taskfile.yml`.
**AppliesTo:** `**/*.yml`, `Taskfile.yml`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.2
**LastUpdated:** 2025-09-16

# ️Automation Directives (Taskfile-first, with equivalents)

## Purpose
Provide directives for creating, modifying, and maintaining project automation using Taskfile.yml as the primary orchestrator, ensuring consistent, portable, and well-documented task management across development workflows.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Project automation using Taskfile.yml for consistent development workflows


## 1. Core Principles
- **Requirement:** Prefer a single source of truth for automation (`Taskfile.yml` recommended). Acceptable equivalents: `Makefile`, `npm scripts`, `justfile`.
- **Requirement:** Do not hard-code commands in docs or scripts if they can be run via the orchestrator.
- **Always:** Define a `default`/`help` task that explains how to get started.
- **Requirement:** Ensure tasks are portable and not OS-specific unless explicitly scoped.

## 2. Structure and Syntax
- **Requirement:** Give all tasks a clear, descriptive name.
- **Requirement:** Provide a human-readable description for public tasks.
- **Requirement:** Define explicit dependencies/ordering.
- **Requirement:** Specify clear shell commands to execute.
- **Always:** Use variables to make tasks reusable and reduce repetition.

## 3. YAML Syntax and Shell Safety
- **Critical:** Add `silent: true` to tasks that contain informational echo commands to prevent verbose output showing command execution.
- **Critical:** Avoid special Unicode characters (bullets, checkmarks, etc.) in echo strings as they can cause YAML parsing errors.
- **Critical:** **COLON HANDLING:** Avoid colons (`:`) in echo statements as they cause YAML parsing errors. Use alternatives:
  - Replace `"Step 1: Creating database"` with `"Step 1 - Creating database"`
  - Replace `"Status: Connected"` with `"Status - Connected"`
  - Replace `"Error: Connection failed"` with `"Error - Connection failed"`
  - Use `{{":"}}` template syntax only when colons are absolutely required in output
- **Critical:** Use proper shell quoting for complex arguments, especially with brackets: `".[dev]"` not `.[dev]`.
- **Critical:** For multi-line echo output, avoid YAML conflicts by using simple text without dashes or colons.
- **Always:** Test YAML syntax with `task --list` immediately after changes.
- **Always:** Use double quotes for echo strings containing special characters or variables.

## 4. Best Practices
- **Requirement:** Keep tasks single-purpose; break complex processes into smaller, composable tasks.
- **Always:** On changes, validate `Taskfile.yml` via `task --list` or `task --dry-run <task_name>`.
- **Requirement:** For multi-line commands, use YAML pipe (`|`) or chevron (`>`) for readability.
- **Always:** Remove unneeded tasks to avoid clutter.
- **Always:** Use `silent: true` for tasks with multiple echo statements to provide clean user output.

## 5. Shell Command Guidelines
- **Critical:** Quote shell arguments that contain special characters: `uv pip install -e ".[dev]"`
- **Always:** Use `{{.VARIABLE}}` syntax for Taskfile variables in commands.
- **Always:** Test shell commands independently before adding to Taskfile.
- **Requirement:** Use `&&` for command chaining when subsequent commands depend on previous success.

## 6. Common YAML Parsing Issues and Solutions

### Colon Problems
```yaml
# WRONG - Causes "invalid keys in command" error
cmds:
  - echo "Step 1: Creating database"
  - echo "Status: Connected"

# CORRECT - Use dashes instead
cmds:
  - echo "Step 1 - Creating database" 
  - echo "Status - Connected"

# ALTERNATIVE - Use template syntax when colons needed
cmds:
  - echo "Next steps{{":"}} task spcs-setup"
```

### Unicode Character Problems
```yaml
# WRONG - Unicode can cause parsing errors
cmds:
  - echo "Setup complete"
  - echo "Step 1 complete"

# CORRECT - Use ASCII alternatives
cmds:
  - echo "Setup complete"
  - echo "- Step 1 complete"
```

### Troubleshooting YAML Errors
- **Error:** `invalid keys in command` - Check for unescaped colons in echo statements
- **Error:** `yaml: line X: mapping values are not allowed` - Check for unquoted special characters
- **Always:** Run `task --list` after any Taskfile changes to validate syntax
- **Always:** Use `task --dry <task-name>` to test individual task parsing

## 7. Documentation
- **Always:** Reference Taskfile docs: https://taskfile.dev/

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Response Template
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [Taskfile Documentation](https://taskfile.dev/) - Official Task runner documentation and syntax guide
- [YAML Specification](https://yaml.org/spec/) - YAML syntax reference for Taskfile configuration
- [Make Documentation](https://www.gnu.org/software/make/manual/) - GNU Make manual for Makefile alternatives

### Related Rules
- **YAML Config**: `202-yaml-config-best-practices.md`
- **Bash Core**: `300-bash-scripting-core.md`
- **Python Core**: `200-python-core.md`
