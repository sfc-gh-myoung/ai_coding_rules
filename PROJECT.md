# PROJECT.md

This file provides project-specific guidance for AI coding assistants working with code in this repository. It is automatically loaded by AI assistants that support project configuration files (e.g., Cursor, Claude Code, GitHub Copilot, VS Code extensions).

## Critical Validation Requirements

**CRITICAL VIOLATION: Committing code without passing ALL validation checks.**

AI assistants MUST NOT commit code unless ALL of the following pass:

1. **Linting** - Code passes all lint checks
2. **Formatting** - Code passes format verification
3. **Type Checking** - Code passes type checker (if applicable)
4. **Compilation** - Code compiles without errors (if applicable)
5. **Tests** - All tests pass

Committing code that fails any validation check is a **critical violation** of project standards. Always run the full validation suite before any commit.

## ai_coding_rules Project Requirements

**CRITICAL: This project mandates specific tooling. Other projects using these rules may choose different tools.**

### Mandatory Tooling for ai_coding_rules

**Python Runtime:**
- **uv** for all Python execution (required)
- **uvx** for isolated tool execution (required)
- **NO** bare `python`, `pip`, `pytest` commands

**Code Quality:**
- `uvx ruff check .` for linting (required)
- `uvx ruff format .` for formatting (required)
- `uvx ty check .` for type checking (required)

**Validation Gates:**

All of the following MUST pass before any commit:

```bash
uvx ruff check .          # Linting
uvx ruff format --check . # Format verification
uvx ty check .            # Type checking
uv run pytest             # Tests
```

**Shortcut command:**
```bash
task validate             # Runs all checks
```

**Project Structure:**
- `pyproject.toml` with uv configuration
- `uv.lock` for dependency locking
- `Taskfile.yml` for automation

**Why These Requirements:**

This project demonstrates modern Python best practices using Astral's toolchain:
- **uv:** Fast Python package installer and resolver (replaces pip/pip-tools)
- **ruff:** Extremely fast Python linter and formatter (replaces flake8/black/isort)
- **ty:** Fast Python type checker (alternative to mypy)

Rules deployed to other projects are more flexible and respect existing toolchains (poetry, pip, black, mypy, etc.).

**Rules Are Not Mandates:**

The rules in `rules/` directory provide **recommendations** and **preferences** for modern Python development. They allow projects to use alternative toolchains (poetry, pip, black, mypy) when appropriate. Only THIS project (ai_coding_rules) mandates uv/uvx/ruff/ty.

## Project Overview

This is the **ai_coding_rules** project - a universal AI coding rule system that provides production-ready rules for consistent software engineering across all AI assistants and IDEs. The system uses a direct rule editing architecture where rules are stored in their final, deployable form.

**Core Architecture:**
- Production-ready rules in `rules/` (no generation step)
- Universal Markdown format with embedded metadata
- Schema validation ensures quality and consistency
- Simple deployment: `task deploy DEST=~/project`

## Common Commands

### Development Workflow

```bash
# Environment setup
task env:deps                  # Install all dependencies
task env:sync                  # Quick dependency sync

# Code quality (most common - used in >80% of development sessions)
task quality:fix               # Fix all linting/formatting issues
task quality:check             # Run all quality checks before commits
task test                      # Run test suite
task validate                  # Run full CI/CD validation

# Rule management
task rules:validate            # Validate all rules against schema
task index:generate            # Regenerate rules/RULES_INDEX.md
task rule:new FILENAME=XXX-name # Create new rule from template

# Deployment
task deploy DEST=~/project     # Deploy rules to project
task deploy:dry DEST=~/project # Preview deployment
```

**Advanced:** For direct script usage without Task, see "Appendix: Direct Script Usage (Advanced)" at end of document.

## High-Level Architecture

### Production-Ready Rules System

The system uses **direct rule editing** with no generation step. All rules in `rules/` are production-ready and deploy directly to projects.

**Key Components:**

1. **rules/** - Production-ready rule files (122 total)
   - All rules use universal Markdown format
   - Embedded metadata enables intelligent discovery
   - Validated against `schemas/rule-schema.yml`
   - Organized by 3-digit prefix (000-999)

2. **AGENTS.md** - Bootstrap protocol (project root)
   - Minimal rule loading sequence
   - MODE/ACT framework initialization
   - Always loaded with rules/000-global-core.md

3. **rules/000-global-core.md** - Foundation rule
   - MODE transitions (PLAN/ACT workflow)
   - Task confirmation protocols
   - Validation requirements
   - Always loaded first

4. **rules/RULES_INDEX.md** - Searchable catalog (project root)
   - Generated from rule metadata
   - Enables keyword-based discovery
   - Shows dependencies and token budgets

5. **scripts/** - Validation and deployment tools
   - All scripts follow schema-driven validation
   - Comprehensive test coverage (98%)
   - Direct execution without build step

### Rule Organization by Domain

Rules use 3-digit numbering for domain organization:

- **000-099:** Core Foundation (12 rules)
  - Operating principles, memory bank, governance, context engineering, skills
- **100-199:** Snowflake (58 rules)
  - SQL, Streamlit, Cortex AI, security, notebooks, pipelines, demo creation
- **200-299:** Python (27 rules)
  - Core patterns, FastAPI, Flask, Typer CLI, Pydantic, pytest, HTMX
- **300-399:** Shell Scripts (7 rules)
  - Bash/Zsh scripting, security, testing
- **400-499:** Frontend/Containers (5 rules)
  - Docker, JavaScript, TypeScript, React
- **500-599:** Frontend Core (2 rules)
  - HTMX core, browser globals
- **600-699:** Go/Golang (1 rule)
  - Core patterns, error handling, concurrency
- **800-899:** Project Management (5 rules)
  - Git workflow, changelog, README, Taskfile
- **900-999:** Analytics & Governance (4 rules)
  - Data science, data governance, business analytics, semantic views

### Rule Discovery and Loading

Rules use metadata for intelligent discovery:

```markdown
**Keywords:** python, fastapi, async, api, rest, validation
**TokenBudget:** ~1500
**ContextTier:** High
**Depends:** rules/000-global-core.md, rules/200-python-core.md
```

AI assistants discover rules by:
1. Reading AGENTS.md (bootstrap protocol)
2. Searching rules/RULES_INDEX.md by keywords
3. Loading dependencies in correct order
4. Applying rules to generate code

### Validation System

Schema validation ensures rule quality:

```bash
# Single file validation
uv run python scripts/schema_validator.py rules/XXX-rule.md --verbose

# All rules validation
uv run python scripts/schema_validator.py rules/

# What it validates:
# - Metadata order and completeness
# - Section structure and placement
# - Quick Start TL;DR presence
# - Token budget accuracy
# - Dependency declarations
# - Contract section placement (before line 160)
```

Schema location: `schemas/rule-schema.yml`

### Deployment System

The rule deployer copies rules to target projects:

```bash
# Basic deployment (rules + skills)
task deploy DEST=~/project

# What happens:
# 1. Copies rules/ directory to DEST/rules/
# 2. Copies AGENTS.md and rules/RULES_INDEX.md to DEST/
# 3. Copies skills/ (excludes internal-only skills)
# 4. Reports: Rules copied (count of .md files), Skills copied (count of skill directories), Files copied (total files)
# 5. Ready to use immediately

# Skills-only deployment
task deploy:only-skills DEST=~/.claude/skills

# Rules-only deployment
task deploy:no-skills DEST=~/project
```

Internal-only skills (excluded from deployment):
- rule-creator/ - Rule creation tool
- rule-reviewer/ - Rule review tool
- bulk-rule-reviewer/ - Bulk review orchestrator

### Skills System

6 AI Agent Skills following best practices:

**Deployed Skills (available in target projects):**
- doc-reviewer - Documentation quality reviews
- plan-reviewer - Implementation plan evaluation
- skill-timing - Performance measurement and timing

**Internal-Only Skills (ai_coding_rules project only):**
- rule-creator - Generate new rule templates
- rule-reviewer - Automate rule quality reviews
- bulk-rule-reviewer - Orchestrate bulk reviews

## Required Permissions

AI assistants must verify they have necessary permissions before performing operations.

### Filesystem Permissions

**Read permissions required:**
- `rules/` directory and all .md files (for validation, deployment)
- `schemas/rule-schema.yml` (for schema validation)
- `rules/RULES_INDEX.md` (for index verification)
- `AGENTS.md` (for deployment)
- `scripts/` directory and all .py files (for running validation)
- `tests/` directory and all test files (for testing)

**Write permissions required:**
- `rules/` directory (for creating/editing rules)
- `rules/RULES_INDEX.md` (for index regeneration)
- `.pytest_cache/`, `__pycache__/` (for test execution)
- `reviews/` directory (for review output, if using review skills)
- `plans/` directory (for plan documents, if using plan-reviewer skill)

**Execute permissions required:**
- Python scripts in `scripts/` directory
- Task binary (for running Taskfile commands)

**Verification commands:**
```bash
# Check read access
test -r rules/000-global-core.md && echo "✓ Can read rules" || echo "✗ Cannot read rules"
test -r schemas/rule-schema.yml && echo "✓ Can read schema" || echo "✗ Cannot read schema"

# Check write access
touch rules/.write-test && rm rules/.write-test && echo "✓ Can write rules" || echo "✗ Cannot write rules"
touch rules/RULES_INDEX.md.test && rm RULES_INDEX.md.test && echo "✓ Can write index" || echo "✗ Cannot write index"

# Check execute access
test -x scripts/schema_validator.py && echo "✓ Can execute scripts" || echo "✗ Cannot execute scripts"
command -v task >/dev/null && echo "✓ Task available" || echo "✗ Task not available"
```

### Git Permissions

**Required for commits:**
- Write access to repository
- Configured git user.name and user.email
- SSH key (if using SSH) or personal access token (if using HTTPS)

**Required for branches:**
- Create branch permission
- Push to remote permission (if pushing branches)

**Required for deployment:**
- Read access to source repository
- Write access to destination directory

**Verification commands:**
```bash
# Check git configuration
git config user.name || echo "✗ Git user.name not set"
git config user.email || echo "✗ Git user.email not set"

# Check repository access
git status >/dev/null 2>&1 && echo "✓ Git repository accessible" || echo "✗ Not a git repository"

# Check commit access (dry-run)
git commit --dry-run --allow-empty -m "test" 2>/dev/null && echo "✓ Can commit" || echo "✗ Cannot commit"

# Check SSH key (if using SSH)
ssh -T git@github.com 2>&1 | grep -q "successfully authenticated" && echo "✓ SSH key works" || echo "! Check SSH key"

# Check remote access
git ls-remote origin >/dev/null 2>&1 && echo "✓ Can access remote" || echo "✗ Cannot access remote"
```

**Common permission issues:**
- Missing git config: Run `git config --global user.name "Your Name"` and `git config --global user.email "you@example.com"`
- SSH key not added: Run `ssh-add ~/.ssh/id_rsa` (or your key path)
- No write access to destination: Check directory permissions with `ls -la /destination/path`
- Repository in detached HEAD: Run `git checkout main` to restore branch

## Key Workflows

### Creating a New Rule

```bash
# 1. Generate template with validation
task rule:new FILENAME=XXX-new-rule TIER=High

# 2. Edit the generated file (replace placeholders)
vim rules/XXX-new-rule.md

# 3. Validate your changes
task rules:validate:verbose

# 4. Update index
task index:generate

# 5. Commit changes (only after validation passes!)
git add rules/XXX-new-rule.md rules/RULES_INDEX.md
git commit -m "feat: add XXX rule for [technology]"
```

### Updating an Existing Rule

```bash
# 1. Edit the rule file
vim rules/XXX-rule.md

# 2. Validate changes
uv run python scripts/schema_validator.py rules/XXX-rule.md --verbose

# 3. Update token budget if content changed by >20% (e.g., declared 5000 tokens, actual 6100 tokens)
#    Check variance: |actual - declared| / declared > 0.20
uv run python scripts/token_validator.py rules/XXX-rule.md

# 4. Regenerate index if metadata changed
task index:generate

# 5. Commit changes (only after validation passes!)
git add rules/XXX-rule.md rules/RULES_INDEX.md
git commit -m "fix: update XXX rule with [improvement]"
```

### Running Validation

```bash
# Fix all quality issues (recommended)
task quality:fix

# Individual checks
task quality:lint         # Ruff linting
task quality:format       # Ruff formatting
task quality:typecheck    # Type checking with ty
task quality:markdown     # Markdown linting

# Full CI/CD validation (REQUIRED before commits)
task validate             # Runs: quality:check, test, rules:validate, index:check
```

### Monitoring Execution Progress

AI assistants should monitor long-running operations and report progress.

**Watch test execution:**
```bash
# Run with verbose output
uv run pytest -v

# Monitor for failures
# Output format: tests/test_file.py::test_function PASSED/FAILED
# Look for lines marked `FAILED` - these require attention
```

**Progress indicators:**
- Total tests: Look for header "collected X items"
- Current progress: Count PASSED/FAILED lines vs total
- Failures: Note test names marked FAILED for investigation

**Example output:**
```
collected 42 items

tests/test_schema_validator.py::test_valid_rule PASSED           [ 2%]
tests/test_schema_validator.py::test_invalid_rule PASSED         [ 4%]
...
tests/test_token_validator.py::test_budget_variance FAILED       [95%]
tests/test_index_generator.py::test_generate PASSED             [100%]

========================= 41 passed, 1 failed in 12.5s =========================
```

**During execution:**
1. Watch for FAILED markers
2. Note which test file has failures
3. After completion, investigate failed tests: `uv run pytest tests/test_X.py -v`
4. Fix issues, re-run: `uv run pytest`

**Success criteria:** All tests PASSED, 0 FAILED

**Watch validation execution:**
```bash
# Run full validation with output
task validate

# Individual check monitoring
task quality:lint      # Watch for ruff linting errors
task quality:format    # Watch for formatting violations
task quality:typecheck # Watch for type errors
task rules:validate    # Watch for schema violations
```

**Progress indicators:**
- Each check reports: ✓ Passed OR ✗ Failed
- Error count: "Found N errors"
- Affected files: Lists files with issues

**Example validation output:**
```
task: [quality:lint] uvx ruff check .
All checks passed!

task: [quality:format] uvx ruff format --check .
All checks passed!

task: [quality:typecheck] uvx ty check .
error: incompatible type [line 45 in scripts/validator.py]
Found 1 error

task: [test] uv run pytest
41 passed in 12.5s

task: [rules:validate] uv run python scripts/schema_validator.py rules/
Validating 122 files...
Found 3 validation errors
```

**During execution:**
1. Note which checks fail (in example above: typecheck, rules:validate)
2. Address failures in order: typecheck first, then rules:validate
3. Re-run `task validate` after fixes
4. Repeat until all checks pass

**Success criteria:** "All checks passed" for every validation step

**Watch deployment execution:**
```bash
# Run deployment with progress
task deploy DEST=/path/to/project

# Or with script directly
uv run python scripts/rule_deployer.py --dest /path/to/project
```

**Progress indicators:**
- Phase 1: "Copying rules/ → /path/rules/"
- Phase 2: "Copying skills/ → /path/skills/"
- Phase 3: "Copying AGENTS.md, rules/RULES_INDEX.md → /path/"
- Completion: "Deployment complete: X rules, Y skills"

**Example deployment output:**
```
Starting deployment to /Users/dev/my-project

Copying rules/ → /Users/dev/my-project/rules/
- Copied 122 rule files (.md)

Copying skills/ → /Users/dev/my-project/skills/
- Copied doc-reviewer/
- Copied plan-reviewer/
- Copied skill-timing/
- Skipped rule-creator/ (internal-only)
- Skipped rule-reviewer/ (internal-only)
- Skipped bulk-rule-reviewer/ (internal-only)

Copying bootstrap files → /Users/dev/my-project/
- Copied AGENTS.md
- Copied RULES_INDEX.md

Deployment complete: 122 rules, 3 skills
```

**During execution:**
1. Verify phase 1 completes (122 rules copied)
2. Verify phase 2 completes (3 deployed skills, 3 internal skipped)
3. Verify phase 3 completes (2 bootstrap files)
4. Note any errors or warnings

**Post-deployment verification:**
```bash
# Verify deployment
ls /path/rules/*.md | wc -l           # Should show 122
ls -d /path/skills/*/ | wc -l        # Should show 3
ls /path/AGENTS.md /path/RULES_INDEX.md  # Should exist
```

**Success criteria:**
- 122 rules deployed
- 3 skills deployed (doc-reviewer, plan-reviewer, skill-timing)
- 2 bootstrap files deployed (AGENTS.md, RULES_INDEX.md)
- No errors in deployment output

### Testing Changes

```bash
# Run all tests
task test

# Run with coverage
task test:coverage

# Run specific test file
uv run pytest tests/test_schema_validator.py -v

# Test deployment without copying
task deploy:dry DEST=/tmp/test-project
```

## Edge Cases and Special Scenarios

AI assistants must handle these edge cases according to documented procedures.

### Empty/Zero-State Scenarios

**Empty rules/:**
- **Detection:** `ls rules/ | wc -l` returns 0 OR rules/000-global-core.md missing
- **Action:** Run `task rule:new FILENAME=000-global-core TIER=Critical` to create foundation rule
- **Validation:** Verify `rules/000-global-core.md` exists and passes schema validation
- **Minimum requirement:** Must have rules/000-global-core.md before deployment

**Zero test cases:**
- **Detection:** `find tests/ -name "test_*.py" | wc -l` returns 0
- **Action:** Create smoke test: `tests/test_smoke.py` with basic import checks
- **Behavior:** `task test` will pass but warn "no tests collected"
- **Minimum requirement:** At least 1 test required for CI/CD validation
- **Example smoke test:**
  ```python
  def test_imports():
      """Verify critical modules can be imported."""
      import scripts.schema_validator
      import scripts.token_validator
      import scripts.index_generator
      assert True
  ```

**Empty RULES_INDEX.md:**
- **Detection:** File missing OR file <100 bytes
- **Action:** Run `task index:generate` to regenerate from rule metadata
- **Validation:** Verify file >1KB and contains "## Rule Catalog" header

### Concurrent Modifications

**Git conflict on rule file:**
- **Detection:** `git status` shows "both modified: rules/XXX-rule.md"
- **Action:** Manual merge required (rules are atomic documents)
- **Procedure:**
  1. Run `git diff rules/XXX-rule.md` to see both versions
  2. Edit file to resolve conflicts (remove <<<<<<< ======= >>>>>>> markers)
  3. Validate merged result: `uv run python scripts/schema_validator.py rules/XXX-rule.md`
  4. If validation fails: Revert and re-merge carefully
  5. Stage resolved file: `git add rules/XXX-rule.md`
  6. Continue: `git commit` (conflict resolved)
- **Prevention:** Use git branches per agent, merge sequentially

**Multiple agents editing same rule:**
- **Detection:** Awareness of concurrent sessions
- **Action:** Coordinate via git branches
- **Procedure:**
  1. Each agent creates branch: `git checkout -b agent-<name>-<task>`
  2. Make changes in separate branches
  3. Merge sequentially (one at a time) to avoid conflicts
  4. First merge: Direct to main
  5. Subsequent merges: Rebase on main first (`git rebase main`)

**RULES_INDEX.md out of sync:**
- **Detection:** `task index:check` fails with "Index out of sync" error
- **Action:** Regenerate index: `task index:generate`
- **Cause:** Rule metadata changed but index not updated
- **Prevention:** Always run `task index:generate` after changing rule metadata

### Dependency Resolution Conflicts

**uv dependency resolution fails:**
- **Detection:** `uv pip install` fails with "Could not find a version that satisfies"
- **Action:**
  1. Check Python version: `python --version` (require 3.11+)
  2. Update uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  3. Clear cache: `uv cache clean`
  4. Try again: `uv pip install -r requirements.txt`
  5. If still fails: Check pyproject.toml for incompatible constraints

**Missing rule dependencies:**
- **Detection:** Schema validator reports "Dependency not found: rules/XXX-rule.md"
- **Action:**
  1. Verify file exists: `ls -la rules/XXX-rule.md`
  2. If missing: Create rule OR update Depends field to remove reference
  3. If filename wrong: Correct Depends field to match actual filename
- **Validation:** Run `task rules:validate` after fix

**Circular dependencies:**
- **Detection:** Schema validator reports "Circular dependency detected"
- **Action:**
  1. Review dependency chain in error message
  2. Identify cycle: A → B → C → A
  3. Break cycle: Remove one dependency (usually the "upward" reference)
  4. Document relationship in rule content instead of Depends field
- **Best practice:** Dependencies should form a DAG (directed acyclic graph)

### Large File/Bulk Operations

**Bulk rule validation (>50 rules):**
- **Command:** `uv run python scripts/schema_validator.py rules/`
- **Progress:** Shows "Validating N files..." with progress counter
- **Timeout:** Allow 5 seconds per rule (50 rules = ~250 seconds = 4 minutes)
- **If timeout:** Process in batches: `rules/0*.md`, `rules/1*.md`, etc.

**Deployment with >100 rules:**
- **Command:** `task deploy DEST=/path`
- **Expected duration:** ~30 seconds for 122 rules + 6 skills
- **Progress monitoring:** Watch output for "Copying rules/" and "Copying skills/"
- **Verification:** Check destination has correct count: `ls /path/rules/*.md | wc -l`

**Index generation with >100 rules:**
- **Command:** `task index:generate`
- **Expected duration:** ~15 seconds for 122 rules
- **Progress:** Shows "Processing rules..." with count
- **Output:** RULES_INDEX.md regenerated (~50KB for 122 rules)

## Important File Locations

- **rules/** - Edit rule content here (production-ready)
- **AGENTS.md** - Bootstrap protocol (project root)
- **PROJECT.md** - Project-specific configuration (this file)
- **rules/000-global-core.md** - Execution protocols and MODE framework
- **RULES_INDEX.md** - Generated catalog (don't edit directly)
- **schemas/rule-schema.yml** - Schema definition for validation
- **scripts/** - Validation and deployment tools
- **tests/** - Comprehensive test suite (98% coverage)
- **skills/** - AI Agent Skills (6 total)
- **docs/** - Architecture and usage documentation

## Critical Development Rules

1. **CRITICAL: Validate before committing:**
   ```bash
   task validate  # MUST pass (exit code 0) before any commit
   # All checks must succeed: linting, formatting, type checking, tests, schema validation
   # If any check fails (exit code != 0), DO NOT commit
   ```

   **Enforcement mechanisms:**

   **Manual enforcement (current):**
   - AI assistants must run `task validate` before committing
   - Check exit code: 0 = success, non-zero = failure
   - Block commit if validation fails
   - Re-run validation after fixing issues

   **Automated enforcement (optional, recommended for teams):**

   *Pre-commit hook (local enforcement):*
   ```bash
   # Install pre-commit hook (one-time setup)
   # Note: This project uses Entro Secret Scan pre-commit hook already
   # To add validation enforcement, create .git/hooks/pre-commit:

   cat > .git/hooks/pre-commit << 'EOF'
   #!/bin/bash
   set -e
   echo "Running validation before commit..."
   task validate
   if [ $? -ne 0 ]; then
       echo "❌ Validation failed. Commit blocked."
       echo "Fix errors and try again."
       exit 1
   fi
   echo "✓ Validation passed. Proceeding with commit."
   EOF

   chmod +x .git/hooks/pre-commit
   ```

   *CI/CD enforcement (remote enforcement):*
   ```yaml
   # Example GitHub Actions workflow (.github/workflows/validate.yml)
   name: Validate
   on: [push, pull_request]
   jobs:
     validate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Install Task
           run: sh -c "$(curl -sSfL https://taskfile.dev/install.sh)"
         - name: Install uv
           run: curl -LsSf https://astral.sh/uv/install.sh | sh
         - name: Run validation
           run: task validate
         - name: Block merge if validation fails
           if: failure()
           run: exit 1
   ```

   **Validation enforcement benefits:**
   - Pre-commit: Prevents committing invalid code locally
   - CI/CD: Prevents merging invalid code to main branch
   - Consistent: All contributors follow same quality standards
   - Fast feedback: Errors caught immediately, not in code review

   **Note:** Current project uses manual enforcement for flexibility. Add automated enforcement when working in teams or when strict quality gates are required.

2. **Use template generator for new rules:**
   ```bash
   task rule:new FILENAME=XXX-name
   # Don't create rules manually - schema compliance is critical
   ```

3. **Update index after metadata changes:**
   ```bash
   task index:generate
   git add RULES_INDEX.md
   ```

4. **Follow Conventional Commits:**
   ```bash
   git commit -m "feat(domain): add new feature"
   git commit -m "fix(rules): correct validation issue"
   git commit -m "docs(readme): improve installation guide"
   ```

5. **Run full validation before PR:**
   ```bash
   task validate  # Runs all CI/CD checks
   ```

## Schema Version vs Project Version

- **SchemaVersion** (v3.2): Rule metadata format version
  - Appears in rule files: `**SchemaVersion:** v3.2`
  - Changes when rule structure evolves
  - All rules must use same schema version

- **Project Version** (v3.5.1): Release version
  - Appears in pyproject.toml and README badges
  - Follows semantic versioning
  - Independent of schema version

## Quantification Standards

**Threshold definitions for consistent interpretation:**

- **Significant change:** >20% deviation from baseline (e.g., token budget variance, test coverage)
- **Most common:** >80% frequency in typical usage patterns
- **Large file/rule:** >500 lines OR >10KB
- **Many instances:** >10 occurrences
- **Validation success:** Exit code 0 (zero errors, zero warnings for critical checks)
- **Critical requirement:** Must-have for commit (blocks merge if violated)

## Terminology Standards

**Consistent term usage throughout documentation:**

- **Validation** (not "quality checks"): Process of verifying code correctness
- **rules/** (not "rules directory" or "rules folder"): Directory containing rule files
- **scripts/** (not "script directory"): Directory containing Python automation tools
- **Task** (capitalized, not "task runner"): Taskfile automation tool
- **Schema validation** (not "schema check"): Rule file validation against schemas/rule-schema.yml
- **Token budget** (not "token count"): Declared token allocation in rule metadata
- **Deployment** (not "copying" or "installing"): Process of distributing rules to target project

## Common Patterns

### Investigation-First Protocol

Always investigate before making changes:

```bash
# Read files before editing
uv run python scripts/schema_validator.py rules/XXX-rule.md --verbose

# Check dependencies
grep "**Depends:**" rules/XXX-rule.md

# Verify rule exists in index
grep "XXX-rule" RULES_INDEX.md
```

### Token Budget Management

Token budgets track context window usage:

```bash
# Check single file
uv run python scripts/token_validator.py rules/XXX-rule.md --dry-run --detailed

# Update all budgets
task tokens:update

# Check all budgets
task tokens:check
```

### Keyword Generation

Keywords enable semantic rule discovery:

```bash
# Suggest keywords for a rule
task keywords:suggest FILE=rules/XXX-rule.md

# Show diff of current vs suggested
task keywords:diff FILE=rules/XXX-rule.md

# Update keywords in-place
task keywords:update FILE=rules/XXX-rule.md
```

## Testing Philosophy

The project maintains 98% test coverage with comprehensive test suites:

- **Unit tests:** All validation scripts (schema_validator, token_validator, etc.)
- **Integration tests:** Rule deployment, index generation
- **Validation tests:** Schema compliance, metadata accuracy

Run tests frequently during development:

```bash
task test                  # Quick test run
task test:coverage         # Full coverage report
uv run pytest tests/test_schema_validator.py -v  # Specific test
```

## Documentation Structure

- **README.md** - User-facing documentation, setup, usage
- **CONTRIBUTING.md** - Development guidelines, PR process
- **AGENTS.md** - Bootstrap protocol for AI agents
- **PROJECT.md** - Project-specific configuration (this file)
- **CHANGELOG.md** - Version history (single source of truth)
- **docs/ARCHITECTURE.md** - System design, technical decisions
- **docs/MEMORY_BANK.md** - Context continuity system (optional)
- **docs/USING_*_SKILL.md** - Individual skill usage guides

## Troubleshooting

### Common Issues

1. **Schema validation fails:**
   ```bash
   # Run verbose validation to see detailed errors
   uv run python scripts/schema_validator.py rules/XXX-rule.md --verbose
   ```

2. **Index out of date:**
   ```bash
   # Regenerate index
   task index:generate
   ```

3. **Token budget mismatch:**
   ```bash
   # Check and update token budget
   task tokens:update:file FILE=rules/XXX-rule.md
   ```

4. **Dependency errors:**
   ```bash
   # Clean and reinstall
   task clean:venv
   task env:deps
   ```

## Error Handling and Recovery

AI assistants should handle these common error scenarios autonomously using the documented recovery steps.

### Network/Connectivity Errors

**If git operations fail with network timeout:**
1. Check connection: `ping github.com`
2. Verify SSH key: `ssh -T git@github.com`
3. If timeout persists: Wait 60 seconds, retry operation
4. If still fails: Work offline, commit locally, push when network restored

**If package downloads fail (uv, uvx):**
1. Check DNS resolution: `nslookup pypi.org`
2. Try alternative mirror: `uv pip install --index-url https://pypi.org/simple/`
3. If still fails: Download wheels manually, install from local cache

**Recovery verification:**
- Run `uv pip list` to verify packages installed
- Run `git status` to verify repository state

### Permission Denied Errors

**If filesystem write fails:**
1. Check permissions: `ls -la [path]`
2. Verify ownership: `stat [path]`
3. Check parent directory permissions: `ls -la $(dirname [path])`
4. If incorrect owner: Request access from system admin
5. If incorrect permissions: Document required access (read/write on rules/, reviews/, scripts/)

**If git commit fails with permission error:**
1. Check git config: `git config --list | grep user`
2. Verify SSH key permissions: `ls -la ~/.ssh/id_*`
3. If key permissions wrong: `chmod 600 ~/.ssh/id_rsa`
4. If still fails: Check repository ownership

**Recovery verification:**
- Create test file: `touch /path/test.txt && rm /path/test.txt`
- Run git test: `git status`

### Tool Availability Errors

**If `uv` not found:**
1. Check installation: `which uv || echo "uv not found"`
2. If missing: Install via `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. Reload shell: `source ~/.bashrc` (or `~/.zshrc`)
4. Verify version: `uv --version` (require 0.1.0+)
5. If wrong version: Update via `curl -LsSf https://astral.sh/uv/install.sh | sh`

**If `ruff` not found:**
1. Install via uv: `uvx ruff --version` (auto-installs if missing)
2. If uvx fails: Install globally: `uv tool install ruff`
3. Verify: `uvx ruff --version`

**If `ty` not found:**
1. Install via uv: `uvx ty --version` (auto-installs if missing)
2. If uvx fails: Install globally: `uv tool install ty`
3. Verify: `uvx ty --version`

**If `task` not found:**
1. Check installation: `which task`
2. If missing: Install via package manager:
   - macOS: `brew install go-task`
   - Linux: `sh -c "$(curl -sSfL https://taskfile.dev/install.sh)"`
3. Verify: `task --version` (require 3.0.0+)

**Recovery verification:**
- Run `task validate` to verify all tools available

### Resource Exhaustion

**If disk space exhausted during tests:**
1. Check available space: `df -h .`
2. If <1GB free: Clean pytest cache: `rm -rf .pytest_cache __pycache__`
3. Clean Python cache: `find . -type d -name __pycache__ -exec rm -rf {} +`
4. Clean uv cache: `uv cache clean`
5. If still insufficient: Report minimum 2GB required for development

**If memory exhausted during large operations:**
1. Check memory usage: `free -h` (Linux) or `vm_stat` (macOS)
2. Close other applications
3. If processing large files: Process in batches (<1000 rules at once)
4. Minimum requirement: 4GB RAM for development

**If too many open files error:**
1. Check limit: `ulimit -n`
2. If <1024: Increase temporarily: `ulimit -n 4096`
3. If persistent: Add to `~/.bashrc`: `ulimit -n 4096`

**Recovery verification:**
- Check disk space: `df -h .` (verify >1GB free)
- Run test suite: `task test`

### Validation Failures

**If `task validate` fails:**
1. Run individual checks to identify failure:
   ```bash
   task quality:lint      # Check linting
   task quality:format    # Check formatting
   task quality:typecheck # Check types
   task test              # Check tests
   task rules:validate    # Check rule schemas
   task index:check       # Check index sync
   ```
2. Fix reported issues in order shown
3. Re-run `task validate` after each fix
4. If all pass individually but `validate` fails: Check Taskfile.yml for task dependencies

**If schema validation fails:**
1. Run verbose validation: `uv run python scripts/schema_validator.py rules/XXX-rule.md --verbose`
2. Fix errors in priority order: CRITICAL → HIGH → MEDIUM → LOW
3. Re-validate after each fix
4. If unclear: Compare against working rule (e.g., rules/000-global-core.md)

**Recovery verification:**
- Run `task validate` - all checks must pass (exit code 0)
- Run `git status` - verify no unexpected changes

## Best Practices for AI Assistants

1. **Read before editing:** Always read rule files before proposing changes
2. **Use templates:** Never create rules manually - use template generator
3. **Validate early:** Run validation after each change
4. **Update index:** Regenerate RULES_INDEX.md after metadata changes
5. **Test deployment:** Use --dry-run to preview deployment
6. **Surgical edits:** Make minimal, focused changes to existing rules
7. **Follow schema:** All rules must validate against schemas/rule-schema.yml
8. **Commit atomically:** Each commit should be self-contained and validated
9. **CRITICAL:** Never commit without passing all validation checks

---

## Appendix: Direct Script Usage (Advanced)

**Recommendation:** Use Task commands for standard workflows (shown in Development Workflow section). Direct script usage is for advanced scenarios where Task overhead is not desired or when integrating into custom automation.

### Direct Script Commands

**Rule validation:**
```bash
# Validate all rules
uv run python scripts/schema_validator.py rules/

# Validate specific rule with verbose output
uv run python scripts/schema_validator.py rules/XXX-rule.md --verbose

# Task equivalent (recommended)
task rules:validate
```

**Index generation:**
```bash
# Regenerate RULES_INDEX.md
uv run python scripts/index_generator.py

# Task equivalent (recommended)
task index:generate
```

**Deployment:**
```bash
# Deploy to project
uv run python scripts/rule_deployer.py --dest ~/project

# Dry-run (preview)
uv run python scripts/rule_deployer.py --dest ~/project --dry-run

# Task equivalent (recommended)
task deploy DEST=~/project
task deploy:dry DEST=~/project
```

**Token budget management:**
```bash
# Check all rules
uv run python scripts/token_validator.py rules/

# Check specific rule
uv run python scripts/token_validator.py rules/XXX-rule.md

# Task equivalent (recommended)
task tokens:check
task tokens:update:file FILE=rules/XXX-rule.md
```

**Template generation:**
```bash
# Create new rule from template
uv run python scripts/template_generator.py XXX-rule-name

# Task equivalent (recommended)
task rule:new FILENAME=XXX-rule-name TIER=High
```

**Badge management:**
```bash
# Update README badges
uv run python scripts/badge_updater.py

# Task equivalent (recommended)
task badge:update
```

**When to use direct scripts:**
- Custom CI/CD pipelines requiring direct control
- Integration with non-Task automation systems
- Debugging script behavior without Task wrapper
- Performance-critical batch operations

**When to use Task (recommended):**
- Interactive development (faster, memorizable)
- Standard workflows (validation, deployment)
- Multi-step operations (Task handles dependencies)
- Team collaboration (consistent interface)
