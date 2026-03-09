# Makefile Automation Directives

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** file:Makefile, kw:makefile, kw:make
**Keywords:** Makefile, GNU Make, make, build automation, make target, phony, make help, portable make, make variables, uv, uvx, make dependencies, make error handling, make cleanup
**TokenBudget:** ~3250
**ContextTier:** Medium
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Core directives for creating and maintaining project automation using Makefiles, ensuring consistent, portable, and well-documented target management with GNU Make.

**When to Load This Rule:**
- Creating or modifying Makefile files
- Implementing project automation with GNU Make
- Setting up portable make-based build systems
- Reviewing Makefile best practices

**For advanced patterns (categorized help, conditional logic, variable assignment types), see `821a-makefile-advanced-patterns.md`.**

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules

**Related:**
- **821a-makefile-advanced-patterns.md** - Advanced patterns (conditionals, categorized help, platform detection)
- **820-taskfile-automation.md** - Alternative task runner (Taskfile.yml)
- **300-bash-scripting-core.md** - Shell scripting patterns used in targets

### External Documentation
- [GNU Make Manual](https://www.gnu.org/software/make/manual/make.html)
- [POSIX Make Specification](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/make.html)
- [Astral uv Tools Concept](https://docs.astral.sh/uv/concepts/tools/)

## Contract

### Inputs and Prerequisites
- GNU Make installed (3.81+ recommended, 4.0+ for extended features)
- `Makefile` present at project root
- `uv`/`uvx` installed for Python automation (if Python project)

### Mandatory
- Declare `SHELL := /bin/bash` at top of Makefile
- Set `.DEFAULT_GOAL := help` for discoverability
- Mark all non-file targets with `.PHONY`
- Provide a `help` target as the default
- Use `$(shell command -v TOOL 2>/dev/null || echo "TOOL")` for tool auto-detection
- Add `## Description` comments on targets for self-documenting help
- Use `ifndef VAR` guards for required user-supplied parameters

### Forbidden
- Absolute paths to executables (use `$(shell command -v ...)` or variables)
- Bare `python`/`pip` commands (use `$(UV) run`/`$(UVX)` for Python tooling)
- Targets without `.PHONY` that do not produce files
- Tabs replaced with spaces in recipes (Make requires tabs)
- Silent failures without error messages in parameter guards

### Execution Steps
1. Read existing `Makefile` if present
2. Verify `SHELL` and `.DEFAULT_GOAL` declarations at top
3. Identify toolchain(s) used and add auto-detection variables
4. Implement or update targets using patterns below
5. Add `.PHONY` declarations for all non-file targets
6. Ensure `help` target documents all public targets
7. Validate with `make help` and `make -n TARGET` (dry run)

### Output Format
- Summary of changes made
- Validation commands run (`make help`, `make -n TARGET`)
- Instructions for invoking targets

### Validation
**Pre-Task-Completion Checks:**
- `make help` executes without errors
- `make -n TARGET` shows correct command expansion for key targets
- All `.PHONY` declarations present
- No hardcoded tool paths

**Success Criteria:**
- `make` (no arguments) displays help text
- All public targets have descriptions in help output
- Parameter-required targets fail with clear error messages when parameters are missing
- Targets execute correctly on the development platform

**Error Recovery:**
- **make: command not found:** Install GNU Make via system package manager
- **Missing separator error:** Recipe lines must use tabs, not spaces
- **Recursive variable expansion:** Use `:=` (simply expanded) instead of `=` (recursively expanded) for shell commands

### Design Principles
- **Discoverability** - `make` with no arguments shows help
- **Portability** - Use POSIX-compatible constructs where possible
- **Auto-Detection** - Use `$(shell command -v ...)` for dynamic tool resolution
- **Fail-Fast** - Use `ifndef`/`$(error ...)` for required parameters
- **Documentation** - Add `## Comment` after target for self-documenting help

### Post-Execution Checklist
- [ ] `SHELL := /bin/bash` declared at top
- [ ] `.DEFAULT_GOAL := help` set
- [ ] `help` target present and lists all public targets
- [ ] All non-file targets have `.PHONY` declarations
- [ ] Tool paths auto-detected (no hardcoded paths)
- [ ] Required parameters guarded with `ifndef`/`$(error ...)`
- [ ] Python commands use `$(UV)`/`$(UVX)` wrappers
- [ ] Validated with `make help` and `make -n`

## Makefile Structure

> **CI/CD & Agent Integration:** For CI/CD pipeline targets and agent-driven automation patterns, see `821a-makefile-advanced-patterns.md`.

### File Header

```makefile
# ============================================================================
# Project Name -- Makefile
# ============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help
```

**Why:**
- `SHELL := /bin/bash` ensures bash features (pipefail, arrays) are available in recipes
- `.DEFAULT_GOAL := help` makes `make` with no arguments show help

### Tool Auto-Detection

```makefile
UV := $(shell command -v uv 2>/dev/null || echo "uv")
UVX := $(shell command -v uvx 2>/dev/null || echo "uvx")
PROJECT_VERSION := $(shell awk -F'"' '/^version = "/ {print $$2; exit}' pyproject.toml 2>/dev/null || echo "unknown")
```

**Pattern:** `VAR := $(shell command -v TOOL 2>/dev/null || echo "TOOL")`

- Resolves tool path at parse time (`:=` prevents re-evaluation)
- Falls back to bare command name if not found (defers error to invocation)
- `2>/dev/null` suppresses stderr when tool is missing

### .PHONY Declarations

```makefile
.PHONY: help
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'
```

**Rules:**
- Declare `.PHONY` for every target that does not produce a file with the same name
- Place `.PHONY` immediately before the target declaration
- Group related `.PHONY` declarations together

### Required Parameter Guards

```makefile
.PHONY: deploy
deploy: ## Deploy rules (DEST=... required)
ifndef DEST
	$(error DEST is required. Usage: make deploy DEST=/path/to/project)
endif
	$(UV) run deploy-tool $(DEST)
```

**Invocation:** `make deploy DEST=/opt/app`

**Pattern:**
- Use `ifndef VAR` to check for required variables
- Use `$(error ...)` to produce a clear error message and stop execution
- Document required parameters in the `##` comment

## Target Naming and Organization

### Naming Convention

Use `category-action` with hyphens. Group related targets with shared prefixes.

```makefile
.PHONY: lint
lint: ## Run linter (check only)
	$(UV) run ruff check .

.PHONY: lint-fix
lint-fix: ## Fix lint issues
	$(UV) run ruff check --fix .

.PHONY: quality-check
quality-check: lint format typecheck ## Run all quality checks

.PHONY: quality-fix
quality-fix: lint-fix format-fix ## Fix all quality issues
```

**Conventions:**
- Use hyphens between words (not underscores): `lint-fix` not `lint_fix`
- Suffix `-fix` for auto-fix variants
- Suffix `-check` for read-only checks
- Suffix `-verbose` for verbose output variants
- Use composite targets to group related operations

### Target Sections

Organize targets into commented sections:

```makefile
# ============================================================================
# Code Quality
# ============================================================================

.PHONY: lint
lint: ## Run ruff linter (check only)
	$(UV) run ruff check .

# ============================================================================
# Testing
# ============================================================================

.PHONY: test
test: ## Run all pytest tests
	$(UV) run pytest tests/ --tb=short
```

### Dependency Chains

```makefile
.PHONY: validate
validate: quality-check test rules-validate examples-validate index-check ## Run all CI/CD checks
	@echo "All validation checks passed!"
```

**Pattern:**
- List dependencies after the colon (executed left-to-right)
- Composite targets combine multiple subtargets
- Add a confirmation message as the final recipe line

## Preflight and Environment Targets

### Preflight Check

```makefile
.PHONY: preflight
preflight: ## Verify environment is ready
	@command -v $(UV) >/dev/null 2>&1 || { echo "ERROR: uv not found. Install: https://docs.astral.sh/uv/"; exit 1; }
	@test -f pyproject.toml || { echo "ERROR: pyproject.toml not found. Run from project root."; exit 1; }
	@echo "Environment ready"
```

### Environment Setup

```makefile
.PHONY: env-sync
env-sync: ## Sync dev dependencies
	$(UV) sync --all-groups

.PHONY: env-deps
env-deps: ## Lock and sync dependencies
	$(UV) lock
	$(UV) sync --all-groups
```

## Cleanup Targets

```makefile
.PHONY: clean-cache
clean-cache: ## Remove Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

.PHONY: clean-venv
clean-venv: ## Remove virtual environment
	rm -rf .venv

.PHONY: clean
clean: clean-cache clean-venv ## Remove all generated files
	rm -rf htmlcov .coverage .ruff_cache
```

**Pattern:**
- Suppress errors with `2>/dev/null || true` for idempotent cleanup
- Use composite `clean` target that depends on specific cleanup targets
- Always use `find ... -exec` instead of globbing for reliable cache removal

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Missing .PHONY Declarations

**Problem:** Omitting `.PHONY` on targets that do not produce files.

**Why It Fails:** If a file or directory with the same name as the target exists, Make skips the target because it considers it "up to date." For example, a `test` target without `.PHONY` will not run if a `test/` directory exists.

**Correct Pattern:**
```makefile
# WRONG: Missing .PHONY
test:
	$(UV) run pytest

# CORRECT: .PHONY declared
.PHONY: test
test: ## Run tests
	$(UV) run pytest tests/ --tb=short
```

### Anti-Pattern 2: Hardcoded Tool Paths

**Problem:** Using absolute or assumed paths for tools.

**Why It Fails:** Breaks portability across machines, CI/CD environments, and different OS configurations.

**Correct Pattern:** Use the auto-detection pattern from [Tool Auto-Detection](#tool-auto-detection) above.
```makefile
# WRONG: Hardcoded path
lint:
  /usr/local/bin/ruff check .

# WRONG: Bare command assumes global install
lint:
  ruff check .

# CORRECT: Use auto-detected variable (see Tool Auto-Detection)
.PHONY: lint
lint: ## Run linter
  $(UVX) ruff check .
```

### Anti-Pattern 3: Spaces Instead of Tabs

**Problem:** Using spaces for recipe indentation.

**Why It Fails:** GNU Make requires literal tab characters for recipe lines. Spaces produce `*** missing separator. Stop.` errors.

**Correct Pattern:**
```makefile
# WRONG: Indented with spaces (invisible but fatal)
test:
    $(UV) run pytest

# CORRECT: Indented with tab character
test:
	$(UV) run pytest
```

### Anti-Pattern 4: Missing Parameter Validation

**Problem:** Targets that require parameters but do not validate them.

**Why It Fails:** Produces confusing errors deep in the recipe instead of a clear message at the start.

**Correct Pattern:**
```makefile
# WRONG: No validation, cryptic error
deploy:
	deploy-tool $(DEST)

# CORRECT: Guard with clear error message
.PHONY: deploy
deploy: ## Deploy (DEST=... required)
ifndef DEST
  $(error DEST is required. Usage: make deploy DEST=/path/to/project)
endif
  deploy-tool $(DEST)
```

## Parallel Builds

Use `make -j` for parallel target execution:

```makefile
# Detect available cores and build in parallel
NPROCS := $(shell nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 1)

.PHONY: parallel-build
parallel-build: ## Build with parallel jobs
	$(MAKE) -j$(NPROCS) build
```

**Note:** Use `.NOTPARALLEL:` for order-dependent targets that must not run in parallel.

## CI/CD Integration

SHOULD provide a single `ci` target as the CI pipeline entry point:

```makefile
.PHONY: ci
ci: lint test build ## CI pipeline entry point
	@echo "CI pipeline complete"
```

```yaml
# GitHub Actions example
# - name: Build and test
#   run: make ci
```

## .ONESHELL Directive

`.ONESHELL` runs all recipe lines in a single shell invocation (GNU Make 3.82+):

```makefile
.ONESHELL:

.PHONY: deploy
deploy: ## Package and deploy
	cd build/
	tar czf release.tar.gz .
	scp release.tar.gz server:/opt/app/
```

Without `.ONESHELL`, each line runs in a separate shell, so `cd` does not persist between lines.
