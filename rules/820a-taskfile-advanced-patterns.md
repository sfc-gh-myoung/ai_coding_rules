# Taskfile Advanced Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-01-27
**LoadTrigger:** kw:taskfile-includes, kw:taskfile-help, kw:categorized-help
**Keywords:** categorized help, subtask files, includes, AI agent, machine-readable, cross-platform, task namespaces, portable tasks, task discovery
**TokenBudget:** ~2350
**ContextTier:** Low
**Depends:** 820-taskfile-automation.md

## Scope

**What This Rule Covers:**
Advanced Taskfile patterns including categorized help output, subtask file organization, cross-platform patterns, and AI agent integration considerations.

**When to Load This Rule:**
- Implementing categorized help for 8+ task Taskfiles
- Organizing tasks into subtask files/modules
- Building cross-platform task automation
- Designing tasks for AI agent consumption

**For core Taskfile patterns, see `820-taskfile-automation.md`.**

## References

### Dependencies

**Must Load First:**
- **820-taskfile-automation.md** - Core Taskfile patterns

### External Documentation
- [Taskfile Includes](https://taskfile.dev/usage/#including-other-taskfiles) - Namespacing and modules
- [Taskfile Variables](https://taskfile.dev/usage/#variables) - Dynamic resolution

## Contract

### Inputs and Prerequisites
- Task CLI installed (v3.45+)
- Understanding of core Taskfile patterns (820)
- For cross-platform: target platforms identified

### Mandatory
- Namespace convention: `namespace:action` pattern
- Categorized help for Taskfiles with 8+ tasks
- Preconditions for tool availability

### Forbidden
- OS-specific commands without `platforms:` guards
- Hard-coded paths in portable tasks
- Missing `desc:` on public tasks

### Execution Steps
1. Identify if Taskfile has 8+ tasks (categorized help threshold)
2. Determine need for subtask files (150+ lines)
3. Implement patterns from sections below
4. Validate with `task --list`

### Output Format
- Categorized help output for default task
- Subtask files in `task/` directory
- Machine-readable output options

### Validation
- Categorized help displays correctly
- Includes resolve without errors
- Cross-platform tasks work on target platforms

### Post-Execution Checklist
- [ ] Categorized help implemented for 8+ tasks
- [ ] Subtask files use namespaces
- [ ] Cross-platform compatibility verified
- [ ] AI-consumable output options provided

## Subtask Files and Includes

### When to Create Subtask Files

Use 2+ of these signals:
- Root Taskfile exceeds 150-200 lines
- Clear domain separation (dev, db, docker, ci)
- Tasks reused across repos
- OS/toolchain-specific variants needed

### Include Patterns

```yaml
version: '3.45'
set: [pipefail]

includes:
  dev:
    dir: ./task/dev              # uses ./task/dev/Taskfile.yml
  db:
    taskfile: ./task/db.yml      # explicit file include
    optional: true               # safe if file absent
  ci:
    dir: ./task/ci
    aliases: [pipeline]
  docker:
    dir: ./task/docker
```

**Requirements:**
- Use `includes` with explicit namespaces
- Prefer directory-based modules with `dir:`
- Avoid `flatten` unless collision-free API curated
- Use `optional: true` for environment-specific modules
- Mark non-CLI tasks as `internal: true`

**Invocation examples:**
- `task db:migrate` runs `migrate` from `task/db.yml`
- `task dev:setup` runs `setup` from `task/dev/Taskfile.yml`

## Cross-Platform Task Patterns

### Platform Detection

```yaml
vars:
  OS:
    sh: uname -s 2>/dev/null || echo "Windows"
  ARCH:
    sh: uname -m 2>/dev/null || echo "unknown"
```

### Platform-Specific Tasks

```yaml
tasks:
  install:deps:
    desc: "Install system dependencies"
    cmds:
      - task: install:deps:{{.OS}}

  install:deps:Darwin:
    internal: true
    cmds:
      - brew install libpq postgresql

  install:deps:Linux:
    internal: true
    cmds:
      - sudo apt-get install -y libpq-dev
```

### Platform Guards

```yaml
tasks:
  open:coverage:
    desc: "Open coverage report (macOS)"
    platforms: [darwin]
    cmds:
      - open htmlcov/index.html

  open:coverage:linux:
    desc: "Open coverage report (Linux)"
    platforms: [linux]
    cmds:
      - xdg-open htmlcov/index.html
```

## Categorized Help Output

### When to Use

**Threshold:** 8+ tasks in Taskfile

**Benefits:**
- 30% faster task discovery through logical grouping
- Improved onboarding with quickstart section
- Better scannability with visual hierarchy

### Visual Design Standards

**Border Characters:**
- Major sections: Double-line `════` (U+2550)
- Category separators: Single-line `────` (U+2500)

**Alignment:**
- Task names: Left-aligned
- Descriptions: Start at column 30

**Terminal Width:** 72-80 characters

### Standard Category Names

**Core Categories:**
- **Quickstart** - 5-8 most frequently used commands
- **Setup/Environment** - Configuration, dependencies
- **Code Quality** - Linting, formatting
- **Testing** - Unit, integration, coverage
- **Build/Generation** - Compilation, artifacts
- **Deployment** - Deploy to environments
- **Validation** - Pre-commit, CI/CD gates
- **Cleanup** - Remove generated files

### Implementation Example

```yaml
tasks:
  default:
    desc: "Show categorized task list"
    silent: true
    cmds:
      - |
        echo "════════════════════════════════════════════════════════════════════════"
        echo "Project Name - Task Automation"
        echo "════════════════════════════════════════════════════════════════════════"
        echo
        echo "🚀 QUICKSTART"
        echo "────────────────────────────────────────────────────────────────────────"
        echo "  task quality:fix              Fix all code quality issues"
        echo "  task test                     Run all tests"
        echo "  task validate                 Run all validation checks"
        echo
        echo "🔍 CODE QUALITY"
        echo "────────────────────────────────────────────────────────────────────────"
        echo "  task lint                     Run linter"
        echo "  task format                   Run formatter"
        echo
        echo "════════════════════════════════════════════════════════════════════════"
        echo "For standard task list{{":"}} task -l"
        echo "════════════════════════════════════════════════════════════════════════"
```

**Key Details:**
- `silent: true` prevents command echoing
- `{{":"}}` template syntax for colons in output
- Multiline string (`|`) for clean formatting

### Project-Type Templates

**Python Projects:**
```
Categories: Quickstart, Code Quality, Testing, Dependencies, Build, Deployment, Cleanup
```

**Docker Projects:**
```
Categories: Quickstart, Build, Run, Testing, Deployment, Network, Cleanup
```

**Data Pipeline Projects:**
```
Categories: Quickstart, Setup, Extract, Transform, Load, Validation, Cleanup
```

## AI Agent Considerations

### Machine-Readable Output

```yaml
tasks:
  quality:lint:
    desc: "Run linter (supports JSON=true for machine output)"
    cmds:
      - "{{.UVX}} ruff check . {{if .JSON}}--output-format json{{end}}"
    vars:
      JSON: '{{.JSON | default ""}}'
```

### Predictable Task Discovery

Requirements for AI agents:
- All public tasks have `desc:` fields
- Internal tasks marked `internal: true`
- Task names follow `namespace:action` pattern
- Stable canonical namespace with ergonomic aliases

```yaml
tasks:
  quality:lint:        # namespace:action pattern
    aliases: [lint]    # ergonomic alias
  quality:format:
    aliases: [format, fmt]
```

### Idempotent Task Design

```yaml
tasks:
  setup:
    desc: "Setup environment (idempotent)"
    status:
      - test -d .venv
      - test -f .venv/pyvenv.cfg
    cmds:
      - uv venv
      - uv sync
```

### Error Messages for Agents

```yaml
tasks:
  build:
    preconditions:
      - sh: test -f pyproject.toml
        msg: "ERROR: pyproject.toml not found. Run from project root."
      - sh: command -v uv
        msg: "ERROR: uv not installed. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
```

### Agent Workflow Integration

**Pre-flight Checks:**
```yaml
tasks:
  preflight:
    desc: "Verify environment ready for agent operations"
    preconditions:
      - sh: command -v uv
        msg: "uv required"
      - sh: test -f Taskfile.yml
        msg: "Taskfile.yml required"
    cmds:
      - echo "Environment ready"
```

**Batch Operations:**
```yaml
tasks:
  agent:validate:
    desc: "Run all validation (for CI/CD and agent workflows)"
    cmds:
      - task: quality:lint
      - task: quality:format
      - task: test
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: OS-Specific Commands Without Platform Guards

**Problem:** Using platform-specific commands (e.g., `open`, `xdg-open`, `brew`) without `platforms:` guards.

**Why It Fails:** Tasks fail silently or with confusing errors on unsupported platforms. CI/CD pipelines break when run on different OS than development machines.

**Correct Pattern:**
```yaml
# WRONG: macOS-only command without guard
tasks:
  open:docs:
    cmds:
      - open docs/index.html  # Fails on Linux/Windows

# CORRECT: Platform-guarded with alternatives
tasks:
  open:docs:
    platforms: [darwin]
    cmds:
      - open docs/index.html

  open:docs:linux:
    platforms: [linux]
    cmds:
      - xdg-open docs/index.html
```

### Anti-Pattern 2: Missing Descriptions on Public Tasks

**Problem:** Omitting `desc:` fields on tasks intended for user invocation.

**Why It Fails:** `task --list` shows empty descriptions, making task discovery impossible. AI agents cannot determine task purpose without descriptions.

**Correct Pattern:**
```yaml
# WRONG: No description
tasks:
  lint:
    cmds:
      - ruff check .

# CORRECT: Clear description for discovery
tasks:
  lint:
    desc: "Run Ruff linter on all Python files"
    cmds:
      - ruff check .
```

## Example Portable Taskfile

```yaml
version: '3.45'
set: [pipefail]

vars:
  UV:
    sh: command -v uv || echo "uv"
  UVX:
    sh: command -v uvx || echo "uvx"
  PYTHON: "{{.UV}} run python"
  OS:
    sh: uname -s 2>/dev/null || echo "Windows"

tasks:
  default:
    desc: "Show available tasks"
    silent: true
    cmds:
      - task --list

  env:setup:
    desc: "Setup development environment (idempotent)"
    status:
      - test -d .venv
    cmds:
      - "{{.UV}} venv"
      - "{{.UV}} sync --all-groups"

  quality:lint:
    desc: "Run Ruff linter"
    preconditions:
      - sh: command -v uvx
        msg: "uvx not found. Install uv first."
    cmds:
      - "{{.UVX}} ruff check ."

  quality:fix:
    desc: "Fix all quality issues"
    cmds:
      - "{{.UVX}} ruff check --fix ."
      - "{{.UVX}} ruff format ."

  test:
    desc: "Run all tests"
    deps: [env:setup]
    cmds:
      - "{{.UV}} run pytest tests/ --tb=short"

  validate:all:
    desc: "Run all validation checks (CI gate)"
    cmds:
      - task: quality:lint
      - task: quality:format
      - task: test

  clean:
    desc: "Remove generated files"
    cmds:
      - rm -rf .venv __pycache__ .pytest_cache htmlcov .coverage dist
```
