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

## 3. Best Practices
- **Requirement:** Keep tasks single-purpose; break complex processes into smaller, composable tasks.
- **Always:** On changes, validate `Taskfile.yml` via `task --list` or `task --dry-run <task_name>`.
- **Requirement:** For multi-line commands, use YAML pipe (`|`) or chevron (`>`) for readability.
- **Always:** Remove unneeded tasks to avoid clutter.

## 4. Documentation
- **Always:** Reference Taskfile docs: https://taskfile.dev/