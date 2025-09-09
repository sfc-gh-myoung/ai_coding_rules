**Description:** Directives for creating, modifying, and maintaining project automation using `Taskfile.yml`.
**Applies to:** `**/*.yml`, `Taskfile.yml`
**Auto-attach:** false

# ️Automation Directives (Taskfile-first, with equivalents)

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
- **Critical:** Avoid special Unicode characters (•, ✓, etc.) in echo strings as they can cause YAML parsing errors.
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

## 6. Documentation
- **Always:** Reference Taskfile docs: https://taskfile.dev/
