# Automation Directives (Taskfile-first)

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-03-09
**Keywords:** Taskfile, Taskfile.yml, task automation, build automation, task runner, Task, portable tasks, error handling, command detection, auto-detection, cross-platform, uvx
**TokenBudget:** ~2500
**ContextTier:** Medium
**Depends:** 202-markup-config-validation.md
**LoadTrigger:** file:Taskfile.yml, kw:deploy, kw:automation, kw:ci

## Scope

**What This Rule Covers:**
Core directives for creating and maintaining project automation using Taskfile.yml, ensuring consistent, portable, and well-documented task management.

**When to Load This Rule:**
- Creating or modifying Taskfile.yml files
- Implementing project automation
- Setting up portable task runners
- Configuring cross-platform build automation

**For advanced patterns (categorized help, subtask files, AI agent considerations), see `820a-taskfile-advanced-patterns.md`.**

## References

### Dependencies

**Must Load First:**
- **202-markup-config-validation.md** - YAML validation patterns

**Related:**
- **820a-taskfile-advanced-patterns.md** - Advanced patterns
- **200-python-core.md** - Python automation patterns
- **300-bash-scripting-core.md** - Shell scripting patterns

### External Documentation
- [Taskfile Documentation](https://taskfile.dev/)
- [Taskfile Variables](https://taskfile.dev/usage/#variables)
- [POSIX Shell Scripting](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- [Astral uv Tools Concept](https://docs.astral.sh/uv/concepts/tools/)

## Contract

### Inputs and Prerequisites
- Task CLI installed (v3.45+)
- `Taskfile.yml` present at project root
- `uv`/`uvx` installed for Python automation

### Mandatory
- Use `version: '3.45'` and `set: [pipefail]` in all Taskfiles
- Run `task --list` and `task --dry-run <task>` after edits
- Use `uv run`/`uvx` for Python commands (not bare `python`/`pip`)
- Provide `desc:` for all public tasks
- Use `preconditions:` for tool availability checks

### Forbidden
- Absolute paths (use `{{.ROOT_DIR}}` or `command -v`)
- Bypassing `uv`/`uvx` for Python tooling
- OS-specific commands without `platforms:` guards
- Silent fallback to alternative tools

### Execution Steps
1. Read existing `Taskfile.yml`
2. Identify toolchain(s) used
3. Determine portability requirements
4. Implement changes using patterns below
5. Validate with `task --list` and `task --dry-run`

### Output Format
- Summary of changes made
- Validation commands run
- Instructions for invoking tasks

### Validation
- `task --list` executes without errors
- `task --dry-run <task>` shows correct expansion
- Tasks execute on multiple platforms

### Design Principles
- **Taskfile-First** - Centralize automation in Taskfile.yml
- **Portability** - Work across OS unless explicitly scoped
- **Auto-Detection** - Use `command -v` for dynamic command resolution
- **Error Handling** - Use `set: [pipefail]` and proper error messages
- **Documentation** - Add `desc:` for all public tasks

### Post-Execution Checklist
- [ ] Version and `pipefail` set (see [Version Specification](#version-specification))
- [ ] Public tasks have `desc`
- [ ] Non-CLI tasks marked `internal: true`
- [ ] Commands auto-detected (see [Command Auto-Detection](#command-auto-detection))
- [ ] Preconditions present with helpful messages
- [ ] Validated with `task --list`

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Hardcoded Paths

**Problem:** Using absolute paths for directories or executables instead of variables and auto-detection.

**Correct Pattern:**
```yaml
vars:
  BUILD_DIR: '{{.ROOT_DIR}}/build'
  SRC_DIR: '{{.ROOT_DIR}}/src'
  UV:
    sh: command -v uv || echo "uv"

tasks:
  build:
    dir: '{{.SRC_DIR}}'
    cmds:
      - go build -o {{.BUILD_DIR}}/app

  test:
    preconditions:
      - sh: command -v uv
        msg: "uv not found. Install from https://docs.astral.sh/uv/"
    cmds:
      - "{{.UV}} run pytest"
```

Use `{{.ROOT_DIR}}` for directory paths; use `command -v` in vars for executable resolution (see [Command Auto-Detection](#command-auto-detection)).

### Anti-Pattern 2: Missing Dependencies

**Problem:** Not declaring task dependencies.

**Correct Pattern:**
```yaml
tasks:
  install:
    cmds:
      - uv sync

  test:
    deps: [install]
    cmds:
      - uv run pytest

  deploy:
    deps: [build, test]
    preconditions:
      - sh: '[ -f dist/app.tar.gz ]'
        msg: "Build artifact missing. Run 'task build' first."
    cmds:
      - ./deploy.sh
```

## Version and Error Handling

### Version Specification

```yaml
version: '3.45'   # Specifies minimum version
set: [pipefail]   # Fail fast on pipeline errors

vars:
  # ... your variables
```

**Why:** Version 3.45+ includes built-in UNIX commands. `pipefail` ensures pipelines fail on first error.

### Task-Level Error Handling

```yaml
tasks:
  deploy:
    desc: Deploy to production
    cmds:
      - |
        set -euo pipefail
        echo "Deploying..." >&2
        ./deploy.sh
```

## Command Auto-Detection

Use `command -v` to resolve executables dynamically. Define once in `vars:`, then reference via `{{.VAR}}`:

```yaml
vars:
  UV:
    sh: command -v uv || echo "uv"
  UVX:
    sh: command -v uvx || echo "uvx"
  PYTHON: "{{.UV}} run python"

tasks:
  quality:lint:
    desc: "Run ruff linter"
    preconditions:
      - sh: command -v uvx
        msg: |
          uvx not found. Install uv:
            macOS:   brew install uv
            Linux:   curl -LsSf https://astral.sh/uv/install.sh | sh
    cmds:
      - uvx ruff check .
```

### Pattern Selection

- **`uvx TOOL`** - One-off tool execution (excellent portability)
- **`command -v` in vars** - Repeated tool use (resolved once)
- **Hard-coded paths** - Never use

## Ephemeral Tool Execution with `uvx`

### Basic Usage

```yaml
tasks:
  quality:lint:
    desc: "Run Ruff linter"
    cmds:
      - uvx ruff check .

  quality:format:
    desc: "Format code"
    cmds:
      - uvx ruff format .

  quality:typecheck:
    desc: "Type check"
    cmds:
      - uvx ty check .
```

### When to Use

- **`uvx`** - Project-independent tools
- **`uv run`** - Project dependencies, scripts needing project context

## Task Structure and Naming

### Task Naming Convention

Use `namespace:action` pattern with colon separator.

```yaml
tasks:
  quality:lint:        # namespace:action
    aliases: [lint]
  quality:lint:fix:    # namespace:action:modifier
  test:coverage:open:
```

**Root-Level Tasks:** Reserve for universal commands: `default`, `preflight`, `status`

### Standard Namespaces

**Core Workflow:**
- `env:` - Environment setup (`env:sync`, `env:install`)
- `quality:` - Code quality (`quality:lint`, `quality:format`)
- `test:` - Testing (`test:all`, `test:coverage`)
- `build:` - Building (`build:dist`, `build:docs`)
- `deploy:` - Deployment (`deploy:staging`, `deploy:prod`)
- `validate:` - CI/CD gates (`validate:ci`, `validate:all`)
- `clean:` - Cleanup (`clean:cache`, `clean:all`)

### Required Variables

```yaml
tasks:
  deploy:
    desc: "Deploy to target (requires DEST=)"
    requires:
      vars: [DEST]
    cmds:
      - ./deploy.sh --target "{{.DEST}}"
```

**Invocation:** `task deploy DEST=/opt/app`

## YAML Syntax and Shell Safety

### Critical Rules

- Add `silent: true` to tasks with informational echo
- Avoid colons in echo - use dashes or `{{":"}}`
- Use proper shell quoting: `".[dev]"` not `.[dev]`

### Colon Handling

```yaml
# GOOD: Quoted string
cmds:
  - 'echo "Status: Complete"'

# GOOD: Block scalar
cmds:
  - |
    echo "Status: Complete"

# ALTERNATIVE: Template
cmds:
  - echo "Status{{":"}} Complete"
```

### Common YAML Issues

```yaml
# WRONG - Causes parsing error
cmds:
  - echo "Step 1: Creating database"

# CORRECT - Use dashes
cmds:
  - echo "Step 1 - Creating database"
```

### Debugging Command Detection

```bash
# Test variable resolution
task --dry-run test

# Check shell command
command -v uv

# Verify command
which uv && uv --version
```

## Documentation
- Reference: https://taskfile.dev/

## Task Fingerprinting for Incremental Builds

Use `sources` and `generates` to skip tasks when inputs haven't changed:

```yaml
build:
    cmds:
        - go build -o bin/app .
    sources:
        - "**/*.go"
    generates:
        - bin/app
```

Taskfile uses checksums to detect changes. If sources haven't changed since last run, the task is skipped.

## CI/CD Integration

```yaml
# GitHub Actions example
# - name: Install Task
#   uses: arduino/setup-task@v2
# - name: Run tests
#   run: task test
```

SHOULD provide a single `ci` or `validate:ci` task as the CI entry point:

```yaml
ci:
    desc: "Run all CI checks"
    cmds:
        - task: quality:lint
        - task: test
        - task: build
```

Adapt for your CI platform (GitHub Actions, GitLab CI, CircleCI).

## Conditional Task Execution

Use `preconditions` and `status` for environment-aware tasks:

```yaml
deploy:
    desc: "Deploy application (CI only)"
    cmds:
        - echo "Deploying..."
    preconditions:
        - sh: "[ \"$CI\" = 'true' ]"
          msg: "deploy can only run in CI environment"
    status:
        - test -f deployed.flag
```

- **`preconditions`** — Fail with a message if condition is not met (pre-flight check)
- **`status`** — Skip task if all status commands succeed (already done check)
