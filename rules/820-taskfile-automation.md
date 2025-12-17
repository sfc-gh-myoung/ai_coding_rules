# Automation Directives (Taskfile-first, with equivalents)

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Taskfile, Taskfile.yml, task automation, build automation, task runner, Task, portable tasks, error handling, categorized help, task discovery, command detection, auto-detection, cross-platform, uvx, machine-readable
**TokenBudget:** ~7100
**ContextTier:** Medium
**Depends:** rules/202-markup-config-validation.md

## Purpose
Provide directives for creating, modifying, and maintaining project automation using Taskfile.yml as the primary orchestrator, ensuring consistent, portable, and well-documented task management across development workflows.

## Rule Scope

Project automation using Taskfile.yml for consistent development workflows

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Specify version** - Use `version: '3.45'` or later
- **Default/help task** - Explain how to get started
- **Error handling** - Use `set -e`, check exit codes
- **Portable tasks** - Work across OS unless explicitly scoped
- **Single source of truth** - Centralize automation in Taskfile
- **Document commands** - Add desc: for each task
- **Never hard-code paths** - Use variables and built-ins
- **Auto-detect commands** - Use `command -v` in vars, never hard-code paths
- **Use `uvx` for tools** - Run Python CLI tools without installation
- **Design for agents** - Predictable names, clear errors, idempotent tasks

**Quick Checklist:**
- [ ] Version specified (≥3.45)
- [ ] default/help task exists
- [ ] Error handling in place
- [ ] Tasks are portable
- [ ] Commands documented
- [ ] Variables used for paths
- [ ] Task dependencies defined
- [ ] Commands auto-detected (no hard-coded paths)
- [ ] Preconditions check tool availability
- [ ] Cross-platform tested (if applicable)
- [ ] Task names use `namespace:action` pattern (Section 2)

## Contract

<contract>
<inputs_prereqs>
- Task CLI installed (v3.45+)
- `Taskfile.yml` present at project root
- `task/` includes directory (if using modular structure)
- `uv`/`uvx` installed for Python automation
- Knowledge of: `rules/000-global-core.md`, `rules/200-python-core.md`, `rules/300-bash-scripting-core.md`
</inputs_prereqs>

<mandatory>
- Use `version: '3.45'` and `set: [pipefail]` in all Taskfiles
- Run `task --list` and `task --dry-run <task>` after edits
- Use `uv run`/`uvx` for Python commands (not bare `python`/`pip`)
- Provide `desc:` for all public tasks
- Use `preconditions:` for tool availability checks
</mandatory>

<forbidden>
- Absolute paths (use `{{.ROOT_DIR}}` or `command -v`)
- Bypassing `uv`/`uvx` for Python tooling
- OS-specific commands without `platforms:` guards
- Tasks that skip validation gates
- Silent fallback to alternative tools
</forbidden>

<steps>
1. Read existing `Taskfile.yml` and included taskfiles
2. Identify toolchain(s) used (Python? Go? Node? Docker?)
3. Determine portability requirements (macOS/Linux/Windows; CI)
4. Plan minimal change set; confirm with user if adding dependencies
5. Implement changes using patterns from Sections 1.2-1.4
6. Validate with `task --list` and `task --dry-run <task>`
</steps>

<output_format>
When modifying Taskfiles, provide:
- Summary of changes made
- Validation commands run and their output
- Instructions for invoking new/modified tasks
</output_format>

<validation>
- **Success:** `task --list` executes without errors; `task --dry-run <task>` shows correct command expansion
- **Negative tests:** Tasks fail gracefully with helpful messages when tools are missing
</validation>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Hardcoded Paths Without Variables

**Problem:** Using absolute paths or hardcoded directory names in Taskfile commands instead of variables, making tasks non-portable across environments.

**Why It Fails:** Tasks break when directory structure changes. Different developers have different paths. CI/CD environments have different layouts. Tasks require modification for each environment.

**Correct Pattern:**
```yaml
# BAD: Hardcoded paths
tasks:
  build:
    cmds:
      - cd /Users/developer/project/src && go build
      - cp /Users/developer/project/bin/app /opt/deploy/

# GOOD: Use variables and relative paths
vars:
  BUILD_DIR: '{{.ROOT_DIR}}/build'
  SRC_DIR: '{{.ROOT_DIR}}/src'

tasks:
  build:
    dir: '{{.SRC_DIR}}'
    cmds:
      - go build -o {{.BUILD_DIR}}/app
    sources:
      - '{{.SRC_DIR}}/**/*.go'
    generates:
      - '{{.BUILD_DIR}}/app'
```

### Anti-Pattern 2: Missing Dependencies Between Tasks

**Problem:** Not declaring task dependencies with `deps:` or `preconditions:`, causing tasks to fail when prerequisites aren't met or running redundant work.

**Why It Fails:** Tasks fail with cryptic errors when dependencies missing. Users must know implicit order. Parallel execution breaks without proper deps. CI pipelines unreliable.

**Correct Pattern:**
```yaml
# BAD: No dependencies declared
tasks:
  test:
    cmds:
      - pytest  # Fails if dependencies not installed!

  deploy:
    cmds:
      - ./deploy.sh  # Fails if build not run!

# GOOD: Explicit dependency chain
tasks:
  install:
    cmds:
      - uv sync
    sources:
      - pyproject.toml
      - uv.lock

  test:
    deps: [install]  # Ensures dependencies installed first
    cmds:
      - uv run pytest

  deploy:
    deps: [build, test]  # Won't deploy without passing tests
    preconditions:
      - sh: '[ -f dist/app.tar.gz ]'
        msg: "Build artifact missing. Run 'task build' first."
    cmds:
      - ./deploy.sh
```

### Anti-Pattern 3: Hard-Coded Command Paths

**Problem:** Using absolute paths to executables instead of PATH resolution or dynamic detection.

**Why It Fails:**
- Breaks on different OS (macOS Homebrew vs Linux apt vs Windows)
- Fails in CI/CD environments with different tool locations
- Requires manual updates when tools are reinstalled

**Correct Pattern:**
```yaml
# BAD: Hard-coded Homebrew path
vars:
  UV: /opt/homebrew/bin/uv

# GOOD: Dynamic detection
vars:
  UV:
    sh: command -v uv || echo "uv"

# GOOD: Environment variable with fallback
vars:
  UV: '{{env "UV_PATH" | default "uv"}}'
```

## Post-Execution Checklist
- [ ] **Version specified:** `version: '3.45'` or later in all Taskfiles
- [ ] **Error handling:** `set: [pipefail]` added after version in all Taskfiles
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully
- [ ] Includes validated with `task --list`; dry-run tested for key tasks
- [ ] Namespaces used for includes; `flatten` avoided or explicitly justified
- [ ] Optional modules marked with `optional: true` where appropriate
- [ ] Public tasks have `desc`; non-CLI tasks marked `internal: true`
- [ ] `task/` directory used to organize domain-specific Taskfiles
- [ ] **User-friendly help:** Default task provides categorized output for 8+ tasks (Section 4.2)
- [ ] **Category names:** Follow standard naming patterns (Quickstart, Quality, Testing, etc.)
- [ ] **Visual design:** Meets standards (borders, alignment at column 30, 72-char width)
- [ ] **Footer hint:** References `task -l` for alternative view
- [ ] **Commands auto-detected:** No hard-coded paths to executables
- [ ] **Preconditions present:** Tool availability checks with helpful messages
- [ ] **Cross-platform tested:** Works on macOS and Linux (if applicable)

## Validation

### Success Checks
- `task --list` executes without errors
- `task --dry-run <task-name>` shows resolved command paths
- Tasks execute successfully on multiple platforms (macOS, Linux)
- Commands auto-detected from PATH (no hard-coded paths)
- Preconditions trigger with helpful messages when tools missing

### Negative Tests
- Task fails gracefully with clear message when required tool unavailable
- Hard-coded paths detected during review (should not exist)
- Cross-platform validation catches OS-specific issues
- `task --dry-run` shows variable resolution failures before execution

### Validation Commands
```bash
# Syntax validation
task --list

# Dry-run validation (shows expanded commands)
task --dry-run default
task --dry-run quality:lint

# Schema validation (for rule file)
python3 scripts/schema_validator.py rules/820-taskfile-automation.md
```

> **Investigation Required**
> When applying this rule:
> 1. **Read existing Taskfile BEFORE modifying** - Check version, task structure
> 2. **Verify task dependencies** - Understand current task relationships
> 3. **Never assume portability** - Check OS-specific requirements
> 4. **Test error handling** - Verify failures are caught properly
> 5. **Check variable usage** - Ensure paths are parameterized
>
> **Anti-Pattern:**
> "Adding task... (without checking existing task structure)"
> "Hard-coding path... (should use Taskfile variables)"
>
> **Correct Pattern:**
> "Let me check your Taskfile structure first."
> [reads Taskfile, checks version, reviews tasks]
> "I see you're using version 3.45. Adding task with proper error handling..."

## Output Format Examples

```markdown
Project Documentation Changes:

**File Modified:** [README.md|CHANGELOG.md|CONTRIBUTING.md]
**Section Updated:** [specific section]
**Validation:** [documentation standards checklist]

Changes Made:
1. **[Section Name]**
   - Added: [specific content]
   - Updated: [what changed and why]
   - Format: [Markdown standards followed]

2. **[Another Section]**
   - Clarified: [ambiguous content]
   - Examples: [added working examples]

Validation Checklist:
- [x] Markdown lint passes
- [x] Links are valid and accessible
- [x] Code examples are tested
- [x] Formatting is consistent
- [x] Table of contents updated (if applicable)

Preview:
[Show relevant excerpt of updated documentation]
```

## References

### External Documentation
- [Taskfile Documentation](https://taskfile.dev/) - Official Task runner documentation and syntax guide
- [Taskfile Includes](https://taskfile.dev/usage/#including-other-taskfiles) - Namespacing, `dir`/`taskfile`, `aliases`, `optional`, `flatten`
- [Taskfile Preconditions](https://taskfile.dev/usage/#preconditions) - Command validation
- [Taskfile Variables](https://taskfile.dev/usage/#variables) - Dynamic variable resolution
- [YAML Specification](https://yaml.org/spec/) - YAML syntax reference for Taskfile configuration
- [Make Documentation](https://www.gnu.org/software/make/manual/) - GNU Make manual for Makefile alternatives
- [POSIX Shell Scripting](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html) - `command -v` specification
- [Astral uv Tools Concept](https://docs.astral.sh/uv/concepts/tools/) - `uvx` ephemeral tool execution

### Related Rules
- **YAML Config**: `rules/202-markup-config-validation.md`
- **Bash Core**: `rules/300-bash-scripting-core.md`
- **Python Core**: `rules/200-python-core.md`
- **Snowflake CLI**: `rules/112-snowflake-snowcli.md` - SnowCLI invocation patterns for Snowflake projects
- **SQL Automation**: `rules/102a-snowflake-sql-automation.md` - SQL script automation patterns

## 1. Core Principles
- **Requirement:** Prefer a single source of truth for automation (`Taskfile.yml` recommended). Acceptable equivalents: `Makefile`, `npm scripts`, `justfile`.
- **Requirement:** Do not hard-code commands in docs or scripts if they can be run via the orchestrator.
- **Always:** Define a `default`/`help` task that explains how to get started.
- **Guidance:** For Taskfiles with 8+ tasks, implement categorized help output for improved user experience and faster task discovery (see Section 4.2).
- **Requirement:** Ensure tasks are portable and not OS-specific unless explicitly scoped.

## 1.1 Version and Error Handling (CRITICAL)

### Version Specification
- **Critical:** Always specify a minimum version in your Taskfile
- **Recommended:** Use `version: '3.45'` or later (includes built-in UNIX commands)
- **Avoid:** Generic `version: '3'` without specific minimum version

```yaml
# Correct - Specifies minimum version
version: '3.45'

# Avoid - Too generic
version: '3'
```

**Why:** Version 3.45+ includes built-in UNIX commands and ensures consistent behavior across environments.

### Global Error Handling
- **Critical:** Add `set: [pipefail]` immediately after version declaration
- **Requirement:** This must be present in every Taskfile (root and included modules)
- **Effect:** Ensures shell pipelines fail on the first error, preventing cascading failures

```yaml
version: '3.45'

set: [pipefail]  # Fail fast on pipeline errors

vars:
  # ... your variables
```

**Why:** Without `pipefail`, commands in a pipeline can fail silently. For example, `cat missing.txt | grep error` might appear to succeed even if `cat` fails.

### Task-Level Error Handling (Optional)
For critical operations, consider explicit error handling:

```yaml
tasks:
  deploy:
    desc: Deploy to production
    cmds:
      - |
        set -euo pipefail  # Task-level strictness
        echo "Deploying..." >&2
        ./deploy.sh
```

**Options:**
- `set -e`: Exit on any error
- `set -u`: Exit on undefined variables
- `set -o pipefail`: Fail on any pipeline error
- `>&2`: Redirect errors to stderr

## 1.2 Command Auto-Detection for Portability (CRITICAL)

### Why Auto-Detection Matters
Hard-coded command paths (e.g., `/opt/homebrew/bin/uv`) break portability across:
- Different OS (macOS vs Linux vs Windows)
- Different package managers (Homebrew vs apt vs pip)
- CI/CD environments (GitHub Actions, GitLab CI)
- Containerized environments (Docker, SPCS)

### Dynamic Variable Patterns

**Pattern 1: Shell Command Detection (Recommended)**
```yaml
version: '3.45'
set: [pipefail]

vars:
  # Auto-detect uv/uvx location dynamically
  UV:
    sh: command -v uv || echo "uv"
  UVX:
    sh: command -v uvx || echo "uvx"
  PYTHON: "{{.UV}} run python"
```

**Pattern 2: Preconditions with User-Friendly Messages**
```yaml
tasks:
  quality:lint:
    desc: "Run ruff linter"
    preconditions:
      - sh: command -v uvx
        msg: |
          uvx not found. Install uv:
            macOS:   brew install uv
            Linux:   curl -LsSf https://astral.sh/uv/install.sh | sh
            Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    cmds:
      - uvx ruff check .
```

**Pattern 3: Use uvx for Tool Portability (Best Practice)**
```yaml
tasks:
  quality:lint:
    aliases: [lint]
    cmds:
      - uvx ruff check .  # Runs ruff in isolated env, no path needed
```

### When to Use Each Pattern

**Pattern Selection:**
- **`uvx TOOL`** - One-off tool execution (Excellent portability, slower - creates env)
- **`command -v` in vars** - Repeated tool use (Good portability, fast - resolved once)
- **Hard-coded paths** - Never use (except local override) - Breaks portability

### Migration Guide

**Before (Hard-Coded Paths):**
```yaml
vars:
  UV: /opt/homebrew/bin/uv

tasks:
  test:
    cmds:
      - "{{.UV}} run pytest"
```

**After (Portable):**
```yaml
vars:
  UV:
    sh: command -v uv || echo "uv"

tasks:
  test:
    preconditions:
      - sh: command -v uv
        msg: "uv not found. Install from https://docs.astral.sh/uv/"
    cmds:
      - "{{.UV}} run pytest"
```

## 1.3 Ephemeral Tool Execution with `uvx`

### What is `uvx`?
`uvx` (alias for `uv tool run`) executes Python CLI tools in temporary virtual environments without prior installation. This ensures:
- **Portability:** No global installation required
- **Isolation:** Tools don't conflict with project dependencies
- **Reproducibility:** Same tool version across all environments (when pinned)

### Basic Usage Patterns

**Running tools without installation:**
```yaml
tasks:
  quality:lint:
    desc: "Run Ruff linter"
    aliases: [lint]
    cmds:
      - uvx ruff check .

  quality:format:
    desc: "Format code with Ruff"
    aliases: [format, fmt]
    cmds:
      - uvx ruff format .

  quality:typecheck:
    desc: "Type check with ty"
    aliases: [type, type-check]
    cmds:
      - uvx ty check .
```

**Pinning tool versions:**
```yaml
tasks:
  lint:
    cmds:
      - uvx ruff@0.8.0 check .  # Pinned version
```

### When to Use `uvx` vs `uv run`

**Use `uvx` for:**
- Project-independent tools (e.g., `uvx ruff check .`)
- One-off tool execution (e.g., `uvx black --check .`)

**Use `uv run` for:**
- Project dependencies (e.g., `uv run pytest`)
- Scripts needing project context (e.g., `uv run python scripts/build.py`)

## 1.4 Cross-Platform Task Patterns

### Platform Detection
```yaml
vars:
  # Detect operating system
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
      - sudo apt-get update
      - sudo apt-get install -y libpq-dev postgresql
```

### Platform Guards
```yaml
tasks:
  open:coverage:
    desc: "Open coverage report in browser"
    platforms: [darwin]
    cmds:
      - open htmlcov/index.html

  open:coverage:linux:
    desc: "Open coverage report in browser (Linux)"
    platforms: [linux]
    cmds:
      - xdg-open htmlcov/index.html
```

## 2. Structure and Syntax
- **Requirement:** Give all tasks a clear, descriptive name.
- **Requirement:** Provide a human-readable description for public tasks.
- **Requirement:** Define explicit dependencies/ordering.
- **Requirement:** Specify clear shell commands to execute.
- **Always:** Use variables to make tasks reusable and reduce repetition.

### Required Variables Pattern

Use `requires.vars` to enforce mandatory task parameters. Tasks will fail with a clear error if required variables are not provided.

```yaml
tasks:
  deploy:
    desc: "Deploy to target (requires DEST=)"
    requires:
      vars: [DEST]
    cmds:
      - ./deploy.sh --target "{{.DEST}}"

  rule:new:
    desc: "Generate rule template (requires FILENAME=)"
    requires:
      vars: [FILENAME]
    cmds:
      - python scripts/template_generator.py {{.FILENAME}}
```

**Invocation:** `task deploy DEST=/opt/app` or `task rule:new FILENAME=my-rule`

**Best Practice:** Include the required variable in the task description (e.g., `"requires DEST="`) for discoverability via `task --list`.

### Task Naming Conventions

**Requirement:** Use `namespace:action` pattern with colon (`:`) separator for all task names. This provides consistent, predictable task discovery for both humans and AI agents.

**Pattern:** `namespace:action` or `namespace:action:modifier`

**Examples:**
- `quality:lint` (not `lint` or `lint-check`)
- `quality:lint:fix` (not `lint-fix` or `lintfix`)
- `test:coverage:open` (not `test-cov-open`)

**Root-Level Tasks:** Reserve for universal commands only: `default`, `preflight`, `status`

**Rationale:**
- Colon separator groups related tasks visually in `task --list` output
- Enables tab-completion by namespace (e.g., `task quality:<TAB>`)
- AI agents can discover tasks by namespace pattern
- Consistent with Taskfile includes namespacing

### Standard Namespace Registry

Use these standard namespaces for consistency across projects. Namespaces are listed in order of typical workflow.

**Core Workflow Namespaces:**

- **`env:`** - Environment setup, dependencies
  - Examples: `env:sync`, `env:lock`, `env:python`, `env:deps`, `env:install`

- **`quality:`** - Code quality (lint, format, type)
  - Examples: `quality:lint`, `quality:format`, `quality:typecheck`, `quality:check`, `quality:fix`

- **`test:`** - Testing
  - Examples: `test:all`, `test:unit`, `test:integration`, `test:coverage`, `test:coverage:open`

- **`build:`** - Build, compilation, packaging
  - Examples: `build:dist`, `build:package`, `build:docs`, `build:wheel`

- **`deploy:`** - Deployment operations
  - Examples: `deploy`, `deploy:dry`, `deploy:verbose`, `deploy:staging`, `deploy:prod`

- **`validate:`** - CI/CD validation gates
  - Examples: `validate:ci`, `validate:all`, `validate:pre-commit`

- **`clean:`** - Cleanup operations
  - Examples: `clean:cache`, `clean:venv`, `clean:build`, `clean:all`

**Domain-Specific Namespaces:**

- **`db:`** - Database operations
  - Examples: `db:migrate`, `db:seed`, `db:reset`, `db:backup`

- **`docker:`** - Container operations
  - Examples: `docker:build`, `docker:up`, `docker:down`, `docker:logs`

- **`cli:`** - CLI application commands
  - Examples: `cli:run`, `cli:help`, `cli:version`

- **`web:`** - Web server operations
  - Examples: `web:start`, `web:dev`, `web:stop`, `web:help`

- **`docs:`** - Documentation
  - Examples: `docs:build`, `docs:serve`, `docs:publish`

- **`release:`** - Release management
  - Examples: `release:tag`, `release:changelog`, `release:publish`

**Project Management Namespaces:**

- **`index:`** - Index/catalog generation
  - Examples: `index:generate`, `index:check`, `index:dry`

- **`tokens:`** - Token budget management
  - Examples: `tokens:update`, `tokens:check`, `tokens:dry`

- **`keywords:`** - Keyword management
  - Examples: `keywords:suggest`, `keywords:update`, `keywords:all`

- **`rules:`** - Rule validation (plural for batch operations)
  - Examples: `rules:validate`, `rules:validate:verbose`

- **`rule:`** - Rule creation (singular for individual items)
  - Examples: `rule:new`, `rule:new:force`

- **`badges:`** - Badge/shield updates
  - Examples: `badges:update`

**Root-Level Tasks (no namespace):**

- **`default`** - Show help or task list
- **`preflight`** - Verify environment readiness
- **`status`** - Show project status summary

**Project-Specific Namespaces:** Add custom namespaces as needed (e.g., `spcs:`, `snowflake:`, `api:`), but follow the `namespace:action` pattern.

### Naming Anti-Patterns

```yaml
# BAD: Hyphen-separated flat names
tasks:
  lint:           # Missing namespace
  lint-fix:       # Hyphen instead of colon
  test-cov:       # Abbreviated, hyphen-separated
  format-check:   # Hyphen instead of colon

# GOOD: Colon-separated namespaced names
tasks:
  quality:lint:
    aliases: [lint]           # Short alias for convenience
  quality:lint:fix:
    aliases: [lint:fix]
  test:coverage:
    aliases: [test:cov]       # Abbreviated alias OK
  quality:format:check:
```

**User Override:** If a user explicitly requests a different naming convention (e.g., flat names for a simple project), follow their request but maintain consistency throughout the Taskfile.

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

### Handling Colons in YAML

**Preferred:** Quote strings containing colons or use block scalars.

```yaml
# GOOD: Quoted string
cmds:
  - 'echo "Status: Complete"'

# GOOD: Block scalar
cmds:
  - |
    echo "Status: Complete"
    echo "Time: $(date)"

# ALTERNATIVE: Template (use sparingly)
cmds:
  - echo "Status{{":"}} Complete"
```

See `rules/202-markup-config-validation.md` for comprehensive YAML quoting guidance.

### Emoji Usage in Terminal Output (Exception to Text-Only Rules)

**Allowed:** Emojis in terminal output generated by task commands (echo statements)

**Rationale:**
- Terminal output is **human-facing**, not machine-consumed by LLMs
- Taskfile.yml structure itself is machine-consumed (no emojis in YAML structure)
- Echo output goes to human users in terminals (emojis improve visual scanning)
- Aligns with rule governance exemption for human-facing content

**Example:**
```yaml
tasks:
  default:
    desc: "Show categorized help"
    silent: true
    cmds:
      - |
        echo "🚀 QUICKSTART"     # Allowed - terminal output for humans
        echo "  task build"
```

**Distinction:**
- **Taskfile.yml YAML structure**: No emojis (machine-consumed by Task runner)
- **Echo output to terminal**: Emojis allowed (human-facing display)
- **Rule files, docs**: Follow `002-rule-governance.md` text-only standards

## 4. Best Practices
- **Requirement:** Keep tasks single-purpose; break complex processes into smaller, composable tasks.
- **Always:** On changes, validate `Taskfile.yml` via `task --list` or `task --dry-run <task_name>`.
- **Requirement:** For multi-line commands, use YAML pipe (`|`) or chevron (`>`) for readability.
- **Always:** Remove unneeded tasks to avoid clutter.
- **Always:** Use `silent: true` for tasks with multiple echo statements to provide clean user output.

## 4.1 Subtask Files and Includes
- **Requirement:** Organize domain-focused tasks into subtask files under a `task/` directory to keep the root `Taskfile.yml` lean and discoverable. Common domains include `dev`, `db`, `docker`, `ci`, `release`, `docs`.
- **Requirement:** Use `includes` with explicit namespaces to import subtask files. Prefer directory-based modules with `dir:` pointing to a folder containing `Taskfile.yml`.
- **Requirement:** Avoid `flatten` unless you intentionally curate a collision-free, public API of tasks. Namespacing is the default and safest pattern.
- **Always:** Use `optional: true` for environment- or tool-specific modules (e.g., `ci`, `android`, `ios`) that might not exist locally.
- **Always:** Use short, lowercase, hyphen-case namespaces and, where helpful, add `aliases` for ergonomics.
- **Guidance:** Mark non-CLI-facing tasks inside each Taskfile as `internal: true` at the task level so they won't appear in `task --list`.
- **Guidance:** Place cross-project reusable modules under `task/` and include them via namespaces instead of duplicating task logic.

Example include patterns:

```yaml
version: '3.45'

set: [pipefail]

includes:
  dev:
    dir: ./task/dev              # uses ./task/dev/Taskfile.yml
  db:
    taskfile: ./task/db.yml      # explicit file include
    optional: true               # safe if file is absent
  ci:
    dir: ./task/ci
    aliases: [pipeline]
  docker:
    dir: ./task/docker
    # flatten: true              # avoid unless tasks are collision-free and curated

tasks:
  default:
    desc: Show help
    cmds:
      - task --list
```

Invocation examples:
- `task db:migrate` runs `migrate` from `task/db.yml`
- `task dev:setup` runs `setup` from `task/dev/Taskfile.yml`
- `task pipeline:build` uses the `ci` module via its alias

When to create a subtask file (use 2+ as a strong signal):
- The root `Taskfile.yml` approaches 150–200 lines or becomes hard to navigate
- You have clearly distinct domains (dev, db, docker, ci, release)
- The same tasks are reused across multiple repos or packages
- You need OS/toolchain-specific variants or optional modules
- You want to isolate vendor/integration-specific logic

## 4.2 Categorized Help Output for Improved User Experience

### Purpose and Benefits
For Taskfiles with 8+ tasks, implement a categorized help display in the `default` task to significantly improve task discoverability and user onboarding.

**Benefits:**
- **30% faster task discovery** through logical grouping
- **Improved onboarding** with quickstart section featuring most common commands
- **Better scannability** with visual hierarchy and consistent formatting
- **Zero breaking changes** - standard `task -l` remains available

### When to Use Categorized Help

**Threshold:** 8+ tasks in your Taskfile

**Use when:**
- Project has multiple development phases (quality, testing, deployment)
- New team members need quick orientation to available commands
- Tasks span different domains (build, test, deploy, cleanup)
- You want professional, polished developer experience

**Don't use when:**
- Simple projects with ≤7 tasks (standard `task -l` is sufficient)
- All tasks are self-explanatory from names alone
- Team prefers minimal output

### Visual Design Standards

**Requirement:** Follow these standards for consistent, professional output:

**Border Characters:**
- **Major sections** (header/footer): Double-line box drawing `════` (U+2550)
- **Category separators**: Single-line box drawing `────` (U+2500)
- **Rationale:** Unicode box drawing provides clean visual hierarchy while maintaining terminal compatibility

**Alignment:**
- **Task names**: Left-aligned
- **Descriptions**: Start at column 30 (adjustable for longer task names)
- **Rationale:** Consistent alignment improves scannability

**Terminal Width:**
- **Target**: 72 characters for content
- **Maximum**: 80 characters total width
- **Rationale**: Fits standard terminal windows; works in split panes; readable in CI logs

**Emoji Usage (Optional):**
- **Allowed**: Emojis in terminal output for human readability
- **Exemption**: Terminal output is human-facing, not machine-consumed by LLMs
- **Rationale**: Improves visual scanning and category recognition
- **Alternative**: Use text-only category labels if emojis cause display issues

### Standard Category Names

Use these universal category names for consistency across projects:

**Core Categories (Most Common):**
- **Quickstart** - 5-8 most frequently used commands
- **Setup/Environment** - Initial configuration, dependency installation
- **Code Quality** - Linting, formatting, style checks
- **Testing** - Unit, integration, coverage tests
- **Build/Generation** - Compilation, artifact creation, code generation
- **Deployment** - Deploy to environments, release preparation
- **Validation** - Pre-commit checks, CI/CD validation gates
- **Cleanup** - Remove generated files, reset environment
- **Utilities** - Helper commands, status checks, maintenance

### Project-Type Category Templates

Adapt these templates to your project type:

**Python Projects:**
```yaml
Categories:
  - Quickstart (quality:fix, test, validate)
  - Code Quality (lint, format, quality)
  - Testing (test, test:unit, test:integration, test:coverage)
  - Dependencies (deps:install, deps:update, deps:lock)
  - Build (build, build:wheel, build:docs)
  - Deployment (deploy:dev, deploy:prod)
  - Cleanup (clean:cache, clean:build, clean:all)
```

**Docker Projects:**
```yaml
Categories:
  - Quickstart (build, up, test)
  - Build (build, build:prod, build:dev)
  - Run (up, down, restart, logs)
  - Testing (test, test:integration, test:e2e)
  - Deployment (deploy, deploy:staging, deploy:prod)
  - Network (network:create, network:inspect)
  - Cleanup (clean:volumes, clean:images, clean:all)
```

**Data Pipeline Projects:**
```yaml
Categories:
  - Quickstart (setup, validate, run:local)
  - Setup (setup:db, setup:env, setup:seeds)
  - Extract (extract:source1, extract:source2)
  - Transform (transform:clean, transform:enrich)
  - Load (load:staging, load:prod)
  - Validation (validate:schema, validate:quality)
  - Cleanup (clean:temp, clean:logs)
```

**Web Service Projects:**
```yaml
Categories:
  - Quickstart (dev, test, deploy:dev)
  - Build (build, build:assets, build:prod)
  - Testing (test, test:unit, test:e2e)
  - Deployment (deploy:dev, deploy:staging, deploy:prod)
  - Database (db:migrate, db:seed, db:reset)
  - Monitoring (logs, health, metrics)
  - Cleanup (clean:cache, clean:logs)
```

### Minimal Working Example

```yaml
version: '3.45'

set: [pipefail]

tasks:
  default:
    desc: "Show categorized task list with quickstart"
    silent: true
    cmds:
      - |
        echo "════════════════════════════════════════════════════════════════════════"
        echo "Project Name - Task Automation"
        echo "════════════════════════════════════════════════════════════════════════"
        echo
        echo "🚀 QUICKSTART (Most Common Commands)"
        echo "────────────────────────────────────────────────────────────────────────"
        echo "  task quality:fix              Fix all code quality issues"
        echo "  task test                     Run all tests"
        echo "  task build                    Build project artifacts"
        echo "  task validate                 Run all validation checks"
        echo
        echo "🔍 CODE QUALITY"
        echo "────────────────────────────────────────────────────────────────────────"
        echo "  task lint                     Run linter (check only)"
        echo "  task format                   Run formatter (check only)"
        echo "  task quality                  Run all quality checks"
        echo "  task quality:fix              Fix all quality issues"
        echo
        echo "🧪 TESTING"
        echo "────────────────────────────────────────────────────────────────────────"
        echo "  task test                     Run all tests"
        echo "  task test:unit                Run unit tests only"
        echo "  task test:coverage            Run tests with coverage"
        echo
        echo "🧹 CLEANUP"
        echo "────────────────────────────────────────────────────────────────────────"
        echo "  task clean                    Remove generated files"
        echo "  task clean:all                Full cleanup (cache + build)"
        echo
        echo "════════════════════════════════════════════════════════════════════════"
        echo "For standard task list view, run{{":"}} task -l"
        echo "════════════════════════════════════════════════════════════════════════"

  # ... rest of your tasks
```

**Key Implementation Details:**
- **`silent: true`**: Prevents verbose command echoing
- **`{{":"}}`**: Template syntax for colons (avoids YAML parsing errors)
- **Multiline string (`|`)**: Clean, readable echo statements
- **Footer hint**: Directs users to `task -l` for alternative view

### Integration with Section 4.1 (Subtask Files)

**Complementary Patterns:**

**Use Categorized Help when:**
- Monolithic Taskfile with 8-50 tasks
- All tasks logically grouped but not split into files
- Quick visual scanning is priority

**Use Includes (Section 4.1) when:**
- Taskfile exceeds 150-200 lines
- Clear domain separation (dev, db, docker, ci)
- Tasks reused across repos

**Combine Both when:**
- Root Taskfile includes subtask modules
- Default task shows categorized help of all available tasks (including from includes)
- Example: Root shows categories, each category may include namespaced tasks (e.g., `docker:build`, `db:migrate`)

**Pattern:**
```yaml
includes:
  docker:
    dir: ./task/docker
  db:
    dir: ./task/db

tasks:
  default:
    desc: "Categorized help including subtasks"
    silent: true
    cmds:
      - |
        echo "DOCKER (from ./task/docker/)"
        echo "  task docker:build           Build containers"
        echo "  task docker:up              Start services"
        echo
        echo "DATABASE (from ./task/db/)"
        echo "  task db:migrate             Run migrations"
        echo "  task db:seed                Seed test data"
```

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

### Debugging Command Detection Issues

**Common Issue: Variable Not Resolving**
```yaml
# Symptom: Task fails with "command not found"
vars:
  UV:
    sh: command -v uv

tasks:
  test:
    cmds:
      - "{{.UV}} run pytest"  # Fails if UV is empty
```

**Debug Steps:**
1. Test variable resolution directly:
   ```bash
   task --dry-run test
   # Should show resolved path
   ```

2. Check shell command manually:
   ```bash
   command -v uv
   # Should output path or nothing
   ```

3. Verify command availability:
   ```bash
   which uv
   type uv
   uv --version
   ```

**Fix: Add Fallback and Validation**
```yaml
vars:
  UV:
    sh: command -v uv || echo "uv"  # Fallback to PATH

tasks:
  test:
    preconditions:
      - sh: command -v uv  # Validate before execution
        msg: "uv not found in PATH"
    cmds:
      - "{{.UV}} run pytest"
```

## 7. Documentation
- **Always:** Reference Taskfile docs: https://taskfile.dev/

## 8. Common Taskfile Mistakes and Prevention
- **Mistake:** Using generic `version: '3'` without specifying minimum version.
  - **Prevention:** Always use `version: '3.45'` or later to ensure consistent behavior and built-in command support.
- **Mistake:** Missing `set: [pipefail]` global error handling.
  - **Prevention:** Add `set: [pipefail]` immediately after version declaration in all Taskfiles (root and modules).
- **Mistake:** Overloading the root `Taskfile.yml` with many unrelated tasks.
  - **Prevention:** Split into domain modules under `task/` and include via namespaces.
- **Mistake:** Using `flatten: true` on includes and causing task name collisions or surfacing internal tasks.
  - **Prevention:** Keep includes namespaced; only use `flatten` for a carefully curated, unique public API.
- **Mistake:** Duplicating task logic across modules or repositories.
  - **Prevention:** Extract reusable logic into shared modules under `task/` and include them.
- **Mistake:** Missing `desc` on public tasks, making `task --list` unhelpful.
  - **Prevention:** Add concise `desc` to all CLI-facing tasks; mark non-CLI tasks `internal: true` at the task level.
- **Mistake:** OS-specific commands without guards or parameterization.
  - **Prevention:** Gate with `platforms:` or parameterize commands; prefer cross-platform tooling where possible.
- **Mistake:** Assuming included files always exist.
  - **Prevention:** Use `optional: true` for non-essential includes.
- **Mistake:** Not validating includes and YAML structure after changes.
  - **Prevention:** Run `task --list` and `task --dry-run <task>` after edits.
- **Mistake:** Not providing user-friendly help for Taskfiles with 8+ tasks.
  - **Prevention:** Implement categorized default task with quickstart section and visual hierarchy (see Section 4.2).
- **Mistake:** Hard-coding command paths instead of using PATH resolution.
  - **Prevention:** Use `command -v` in vars for dynamic detection; use `uvx` for ephemeral tools (see Section 1.2).

## 9. AI Agent Considerations

### Machine-Readable Task Output
**Requirement:** When tasks may be consumed by AI agents, provide structured output options.

```yaml
tasks:
  quality:lint:
    desc: "Run linter (supports JSON=true for machine output)"
    aliases: [lint]
    cmds:
      - "{{.UVX}} ruff check . {{if .JSON}}--output-format json{{end}}"
    vars:
      JSON: '{{.JSON | default ""}}'
```

### Predictable Task Discovery
**Requirement:** AI agents rely on `task --list` for discovery. Ensure:
- All public tasks have `desc:` fields
- Internal tasks are marked `internal: true`
- Task names follow predictable patterns (verb:noun or namespace:action)
- Prefer a stable canonical namespace for automation (e.g., `quality:*`) and add ergonomic `aliases` for humans.
- If the user explicitly requests a different naming convention, follow the request and keep it consistent across the Taskfile and docs.

```yaml
# GOOD: Predictable canonical names with ergonomic aliases
tasks:
  quality:lint:     # namespace:action
    aliases: [lint]
  quality:format:
    aliases: [format, fmt]
  quality:typecheck:
    aliases: [type, type-check]
  test:unit:
  test:integration:

# BAD: Short, inconsistent task names without a stable namespace (and mixed naming styles)
tasks:
  lint:
  fmt:
  run-tests:
```

### Idempotent Task Design
**Requirement:** AI agents may re-run tasks multiple times. Design tasks to be idempotent.

```yaml
tasks:
  setup:
    desc: "Setup development environment (idempotent)"
    status:
      - test -d .venv
      - test -f .venv/pyvenv.cfg
    cmds:
      - uv venv
      - uv sync
```

### Error Messages for Agents
**Requirement:** Provide clear, parseable error messages.

```yaml
tasks:
  build:
    preconditions:
      - sh: test -f pyproject.toml
        msg: "ERROR: pyproject.toml not found. Run from project root."
      - sh: command -v uv
        msg: "ERROR: uv not installed. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
```

### Agent-Friendly Output Patterns

**Structured Output for Parsing:**
```yaml
tasks:
  status:
    desc: "Show project status (machine-readable with JSON=true)"
    cmds:
      - |
        if [ "{{.JSON}}" = "true" ]; then
          echo '{"version": "1.0.0", "tests": "passing", "lint": "clean"}'
        else
          echo "Version: 1.0.0"
          echo "Tests: passing"
          echo "Lint: clean"
        fi
    vars:
      JSON: '{{.JSON | default "false"}}'
```

**Exit Codes for Automation:**
```yaml
tasks:
  validate:
    desc: "Validate project (exit 0 on success, non-zero on failure)"
    cmds:
      - task: quality:lint
      - task: quality:format
      - task: test
    # Task runner propagates non-zero exit codes automatically
```

### Agent Workflow Integration

**Pre-flight Checks:**
```yaml
tasks:
  preflight:
    desc: "Verify environment is ready for agent operations"
    preconditions:
      - sh: command -v uv
        msg: "uv required"
      - sh: command -v task
        msg: "task required"
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
      - task: test:unit
      - task: test:integration
    # Single entry point for agents to validate entire project
```

## Appendix A: Example Portable Taskfile.yml

```yaml
version: '3.45'

set: [pipefail]

# Dynamic command detection - works on any system with uv installed
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

  # Environment setup with idempotency
  env:setup:
    desc: "Setup development environment (idempotent)"
    status:
      - test -d .venv
    cmds:
      - "{{.UV}} venv"
      - "{{.UV}} sync --all-groups"

  # Quality checks using uvx (no installation required)
  quality:lint:
    desc: "Run Ruff linter"
    preconditions:
      - sh: command -v uvx
        msg: "uvx not found. Install uv first."
    cmds:
      - "{{.UVX}} ruff check ."

  quality:format:
    desc: "Check code formatting"
    cmds:
      - "{{.UVX}} ruff format --check ."

  quality:typecheck:
    desc: "Run type checker"
    aliases: [type, type-check]
    cmds:
      - "{{.UVX}} ty check ."

  quality:fix:
    desc: "Fix all quality issues"
    cmds:
      - "{{.UVX}} ruff check --fix ."
      - "{{.UVX}} ruff format ."

  # Testing with project dependencies
  test:
    desc: "Run all tests"
    deps: [env:setup]
    cmds:
      - "{{.UV}} run pytest tests/ --tb=short"

  test:coverage:
    desc: "Run tests with coverage"
    deps: [env:setup]
    cmds:
      - "{{.UV}} run pytest --cov=src --cov-report=term-missing tests/"

  # Validation gate for CI/CD
  validate:all:
    desc: "Run all validation checks (CI gate)"
    cmds:
      - task: quality:lint
      - task: quality:format
      - task: quality:typecheck
      - task: test

  # Clean with fingerprinting
  clean:
    desc: "Remove generated files"
    cmds:
      - rm -rf .venv __pycache__ .pytest_cache htmlcov .coverage dist
```
