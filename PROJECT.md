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

This project demonstrates modern Python best practices using Astral's toolchain (uv, ruff, ty). Rules deployed to other projects are more flexible and respect existing toolchains (poetry, pip, black, mypy, etc.).

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

# Code quality (most common)
task quality:fix               # Fix all linting/formatting issues
task quality:check             # Run all quality checks
task test                      # Run test suite
task validate                  # Run full CI/CD validation

# Rule management
task rules:validate            # Validate all rules against schema
task index:generate            # Regenerate RULES_INDEX.md
task rule:new FILENAME=XXX-name # Create new rule from template

# Deployment
task deploy DEST=~/project     # Deploy rules to project
task deploy:dry DEST=~/project # Preview deployment
```

### Direct Script Usage (without Task)

```bash
# Rule validation
uv run python scripts/schema_validator.py rules/
uv run python scripts/schema_validator.py rules/XXX-rule.md --verbose

# Index generation
uv run python scripts/index_generator.py

# Deployment
uv run python scripts/rule_deployer.py --dest ~/project
uv run python scripts/rule_deployer.py --dest ~/project --dry-run

# Token budget management
uv run python scripts/token_validator.py rules/
uv run python scripts/token_validator.py rules/XXX-rule.md

# Template generation
uv run python scripts/template_generator.py XXX-rule-name
```

## High-Level Architecture

### Production-Ready Rules System

The system uses **direct rule editing** with no generation step. All rules in `rules/` are production-ready and deploy directly to projects.

**Key Components:**

1. **rules/** - Production-ready rule files (121 total)
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

4. **RULES_INDEX.md** - Searchable catalog (project root)
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
2. Searching RULES_INDEX.md by keywords
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
# 2. Copies AGENTS.md and RULES_INDEX.md to DEST/
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
git add rules/XXX-new-rule.md RULES_INDEX.md
git commit -m "feat: add XXX rule for [technology]"
```

### Updating an Existing Rule

```bash
# 1. Edit the rule file
vim rules/XXX-rule.md

# 2. Validate changes
uv run python scripts/schema_validator.py rules/XXX-rule.md --verbose

# 3. Update token budget if content changed significantly
uv run python scripts/token_validator.py rules/XXX-rule.md

# 4. Regenerate index if metadata changed
task index:generate

# 5. Commit changes (only after validation passes!)
git add rules/XXX-rule.md RULES_INDEX.md
git commit -m "fix: update XXX rule with [improvement]"
```

### Running Quality Checks

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
   task validate  # MUST pass before any commit
   ```

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

- **Project Version** (v3.5.0): Release version
  - Appears in pyproject.toml and README badges
  - Follows semantic versioning
  - Independent of schema version

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
