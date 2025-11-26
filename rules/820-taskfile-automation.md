# Automation Directives (Taskfile-first, with equivalents)

## Metadata

**SchemaVersion:** v3.0
**Keywords:** Taskfile, task automation, Taskfile.yml, build automation, task runner, Task, portable tasks, error handling, categorized help, user experience, task discovery
**TokenBudget:** ~4050
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

**Quick Checklist:**
- [ ] Version specified (≥3.45)
- [ ] default/help task exists
- [ ] Error handling in place
- [ ] Tasks are portable
- [ ] Commands documented
- [ ] Variables used for paths
- [ ] Task dependencies defined


## Contract

<contract>
<inputs_prereqs>
[Context, files, dependencies needed]
</inputs_prereqs>

<mandatory>
[Tools permitted for this domain]
</mandatory>

<forbidden>
[Tools not allowed for this domain]
</forbidden>

<steps>
[Ordered steps the agent must follow]
</steps>

<output_format>
[Expected output format]
</output_format>

<validation>
[Checks to confirm success]
</validation>

</contract>


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


## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

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
- [YAML Specification](https://yaml.org/spec/) - YAML syntax reference for Taskfile configuration
- [Make Documentation](https://www.gnu.org/software/make/manual/) - GNU Make manual for Makefile alternatives

### Related Rules
- **YAML Config**: `rules/202-markup-config-validation.md`
- **Bash Core**: `rules/300-bash-scripting-core.md`
- **Python Core**: `rules/200-python-core.md`


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
        echo "🚀 QUICKSTART"     # ✓ Allowed - terminal output for humans
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

