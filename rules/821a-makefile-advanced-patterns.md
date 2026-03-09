# Makefile Advanced Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:makefile-includes, kw:makefile-help, kw:makefile-conditional
**Keywords:** categorized help, Makefile includes, conditional logic, ifdef, ifeq, variable assignment, simply expanded, recursively expanded, platform detection, multi-target, AI agent, make patterns
**TokenBudget:** ~3050
**ContextTier:** Low
**Depends:** 821-makefile-automation.md

## Scope

**What This Rule Covers:**
Advanced Makefile patterns including categorized help output, conditional logic, variable assignment types, include directives, platform detection, and AI agent integration considerations.

**When to Load This Rule:**
- Implementing categorized help for Makefiles with 8+ targets
- Using conditional logic (`ifdef`, `ifeq`, `ifneq`) in Makefiles
- Organizing targets across multiple included Makefiles
- Designing make targets for AI agent consumption

**For core Makefile patterns, see `821-makefile-automation.md`.**

## References

### Dependencies

**Must Load First:**
- **821-makefile-automation.md** - Core Makefile patterns

**Related:**
- **820a-taskfile-advanced-patterns.md** - Equivalent patterns for Taskfile
- **300-bash-scripting-core.md** - Shell patterns used in recipes

### External Documentation
- [GNU Make Manual - Conditionals](https://www.gnu.org/software/make/manual/make.html#Conditionals)
- [GNU Make Manual - Include](https://www.gnu.org/software/make/manual/make.html#Include)
- [GNU Make Manual - Variables](https://www.gnu.org/software/make/manual/make.html#Using-Variables)

## Contract

### Inputs and Prerequisites
- GNU Make installed (3.81+)
- Understanding of core Makefile patterns (821)
- For cross-platform: target platforms identified

### Mandatory
- MUST implement categorized help for Makefiles with 8+ targets
- Variable assignment type MUST be appropriate to use case (`:=` for shell, `?=` for overridable, `=` for late-binding)
- MUST use platform guards for OS-specific commands
- Each non-internal target MUST include a `## Description` help comment
- Variables MUST use SCREAMING_SNAKE_CASE

### Forbidden
- OS-specific commands without conditional guards
- Recursive `$(MAKE)` calls without explicit target
- `include` without `-include` fallback for optional files

### Execution Steps
1. Identify if Makefile has 8+ targets (categorized help threshold)
2. Determine need for included Makefiles (200+ lines)
3. Implement patterns from sections below
4. Validate with `make help` and `make -n TARGET`

### Output Format
- Categorized help output for `help` target
- Included Makefiles in `mk/` directory (if splitting)
- Platform-conditional targets where needed

### Validation
**Pre-Task-Completion Checks:**
- Categorized help displays correctly
- Includes resolve without errors
- Conditional logic evaluates correctly on target platform

**Success Criteria:**
- `make help` displays categorized output with section headers
- `make -n TARGET` expands correctly for conditional targets
- Included files parse without errors

### Post-Execution Checklist
- [ ] Categorized help implemented for 8+ targets
- [ ] Variable assignment types correct (`:=` for shell, `?=` for overridable)
- [ ] Platform guards on OS-specific targets
- [ ] Includes use `-include` for optional files

## Variable Assignment Types

### Assignment Operators

```makefile
# Simply expanded (:=) - evaluated once at parse time
# Use for: shell commands, computed values, tool paths
UV := $(shell command -v uv 2>/dev/null || echo "uv")

# Recursively expanded (=) - evaluated each time the variable is used
# Use for: variables referencing other variables that may change
PYTHON = $(UV) run python

# Conditional assignment (?=) - set only if not already defined
# Use for: user-overridable defaults
DEST ?= /tmp/default-destination

# Append (+=) - add to existing value
# Use for: building up flags, file lists
LINT_FLAGS += --fix
```

### Selection Guide

- **Tool paths:** Use `:=` (resolve once at parse time, avoid repeated shell calls)
- **Compound commands:** Use `=` (allow late binding to other variables)
- **User defaults:** Use `?=` (allow override via command line or environment)
- **Flag accumulation:** Use `+=` (append to existing value)

**Command-line override:** `make deploy DEST=/opt/app` overrides any assignment type except `override` directive.

## Conditional Logic

### Variable-Based Conditionals

```makefile
# Check if variable is defined
ifdef VERBOSE
  PYTEST_FLAGS := -v --tb=long
else
  PYTEST_FLAGS := --tb=short
endif

# Check if variable is empty
ifndef DEST
  $(error DEST is required. Usage: make deploy DEST=/path)
endif
```

### String Comparison

```makefile
# Compare variable to string value
ifeq ($(OS),Darwin)
  OPEN_CMD := open
else ifeq ($(OS),Linux)
  OPEN_CMD := xdg-open
else
  OPEN_CMD := echo "Open not supported on $(OS). File:"
endif

# Negate comparison
ifneq ($(CI),)
  # Running in CI - stricter checks
  LINT_FLAGS := --no-fix
endif
```

### Conditional Target Recipes

```makefile
.PHONY: test-cov-open
test-cov-open: test-cov ## Coverage + open in browser
	@if [ "$$(uname)" = "Darwin" ]; then \
		open htmlcov/index.html; \
	elif [ "$$(uname)" = "Linux" ]; then \
		xdg-open htmlcov/index.html; \
	else \
		echo "Coverage report generated at htmlcov/index.html"; \
	fi
```

**When to use Make conditionals vs shell conditionals:**
- **Make conditionals (`ifdef`, `ifeq`):** For compile-time decisions that affect variable values or which recipes to use. Evaluated at Makefile parse time.
- **Shell conditionals (`if [ ... ]`):** For runtime decisions within a recipe. Evaluated when the target executes.

## Categorized Help Output

### When to Use

**Threshold:** 8+ public targets in Makefile.

**Benefits:**
- Faster target discovery through logical grouping
- Improved onboarding with quickstart section
- Better scannability with visual hierarchy

### Implementation Pattern

```makefile
.PHONY: help
help: ## Show this help message
  @echo "========================================"
  @echo "Project Name -- Development Commands"
  @echo "========================================"
  @echo ""
  @echo "QUICKSTART"
  @echo "  make quality-fix    Fix all code quality issues"
  @echo "  make test           Run all pytest tests"
  @echo ""
  @echo "CODE QUALITY"
  @echo "  make lint           Run ruff linter (check only)"
  @echo "  make lint-fix       Fix lint issues"
  # ... additional categories follow same pattern
```

### Auto-Generated Help Alternative

For simpler Makefiles, use `grep`-based help that extracts `##` comments. See `821-makefile-automation.md` for the auto-generated help pattern.

**Decision Framework — Manual vs Auto-Generated Help:**

- **Maintenance:** Manual requires updating help text with each target change. Auto-generated stays current automatically.
- **Organization:** Manual supports logical grouping, quickstart sections, and visual hierarchy. Auto-generated produces a flat alphabetical list.
- **Consistency:** Manual depends on discipline to keep in sync. Auto-generated always matches actual targets.
- **Discoverability:** Manual can highlight key workflows in a quickstart section. Auto-generated treats all targets equally.
- **Multi-file support:** Manual requires effort to cover included Makefiles. Auto-generated uses `MAKEFILE_LIST` to cover all includes automatically.

**Recommendation:** Use manual categorized help when 8+ targets AND the project has clear workflow categories. Use `grep`-based when targets are few, change frequently, or span many included files where manual sync is costly.

## Include Directives

### When to Split Makefiles

Split when 2+ of these signals are present:
- Root Makefile exceeds 200 lines
- Clear domain separation (quality, deploy, docker)
- Targets reused across repositories
- Platform-specific target variants needed

### Include Pattern

```makefile
# Required includes (error if missing)
include mk/quality.mk
include mk/deploy.mk

# Optional includes (silent if missing)
-include mk/local.mk
-include mk/platform-$(shell uname -s).mk
```

**Conventions:**
- Place included Makefiles in `mk/` directory
- Name files by domain: `mk/quality.mk`, `mk/deploy.mk`, `mk/docker.mk`
- Use `-include` (with dash prefix) for optional or environment-specific files
- Use `include` (no dash) for required files that must exist

### Variable Sharing

Variables defined before `include` are available in included files:

```makefile
# Root Makefile
UV := $(shell command -v uv 2>/dev/null || echo "uv")
include mk/quality.mk

# mk/quality.mk can use $(UV)
.PHONY: lint
lint: ## Run linter
	$(UV) run ruff check .
```

## Platform Detection

### OS Detection Variable

```makefile
OS := $(shell uname -s 2>/dev/null || echo "Windows")
ARCH := $(shell uname -m 2>/dev/null || echo "unknown")
```

### Platform-Conditional Recipes

```makefile
.PHONY: install-deps
install-deps: ## Install system dependencies
ifeq ($(OS),Darwin)
	brew install libpq postgresql
else ifeq ($(OS),Linux)
	sudo apt-get install -y libpq-dev
else
	@echo "ERROR: Unsupported platform $(OS). Install libpq manually."
	@exit 1
endif
```

## AI Agent Considerations

### Predictable Target Discovery

Requirements for AI agents:
- All public targets have `## Description` comments
- Target names follow `category-action` pattern
- `make help` provides complete target listing
- `make -n TARGET` shows command expansion without execution

### Machine-Readable Output

```makefile
.PHONY: lint
lint: ## Run linter (check only)
ifdef JSON
	$(UV) run ruff check . --output-format json
else
	$(UV) run ruff check .
endif
```

**Invocation:** `make lint JSON=1`

### Idempotent Targets

```makefile
.PHONY: env-sync
env-sync: ## Sync dependencies (idempotent)
	$(UV) sync --all-groups
```

Design targets to be safe to run multiple times without side effects.

### Error Messages for Agents

```makefile
.PHONY: preflight
preflight: ## Verify environment is ready
	@command -v $(UV) >/dev/null 2>&1 || { echo "ERROR: uv not found. Install: https://docs.astral.sh/uv/"; exit 1; }
	@test -f pyproject.toml || { echo "ERROR: pyproject.toml not found. Run from project root."; exit 1; }
	@echo "Environment ready"
```

**Pattern:** Prefix error messages with `ERROR:` for reliable parsing by agents.

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Wrong Variable Assignment Type

**Problem:** Using `=` (recursively expanded) for shell commands, causing repeated execution.

**Why It Fails:** Each reference to the variable re-executes the shell command, degrading performance and producing inconsistent results if the command output changes.

**Correct Pattern:**
```makefile
# WRONG: Shell command re-executes on every use
UV = $(shell command -v uv 2>/dev/null || echo "uv")

# CORRECT: Simply expanded, evaluated once at parse time
UV := $(shell command -v uv 2>/dev/null || echo "uv")
```

### Anti-Pattern 2: Include Without Fallback

**Problem:** Using `include` for optional files that may not exist.

**Why It Fails:** `include` produces a fatal error if the file is missing. This breaks `make` in environments where the optional file is not present (CI, fresh clones).

**Correct Pattern:**
```makefile
# WRONG: Fatal error if local.mk doesn't exist
include mk/local.mk

# CORRECT: Silent skip if missing
-include mk/local.mk
```

### Anti-Pattern 3: Unquoted Variables in Shell Commands

**Problem:** Using Make variables in shell commands without quoting.

**Why It Fails:** Values with spaces, special characters, or empty values cause word splitting and unexpected behavior in shell recipes.

**Correct Pattern:**
```makefile
# WRONG: Breaks if DEST contains spaces
deploy:
  deploy-tool $(DEST)

# CORRECT: Quoted for shell safety
deploy:
  deploy-tool "$(DEST)"
```

## Avoiding Recursive Make

Recursive `$(MAKE) -C subdir/` is a well-documented anti-pattern ("Recursive Make Considered Harmful"). It breaks cross-directory dependency tracking.

SHOULD use include-based alternatives instead:

```makefile
# Instead of recursive $(MAKE) -C subdir/
# Use includes:
include src/module.mk
include tests/tests.mk
```

**Why:** Recursive Make prevents Make from seeing the full dependency graph across directories, leading to incorrect builds and missed rebuilds.

## CI/CD Entry Point

SHOULD provide a single CI target:

```makefile
.PHONY: ci
ci: lint test build  ## CI pipeline entry point
	@echo "CI pipeline complete"
```

Use `make ci` as the sole CI command for consistent local and CI behavior.
