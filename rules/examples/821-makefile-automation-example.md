# 821 Example: Makefile Automation (Python Project)

> **EXAMPLE FILE** - Reference implementation for `821-makefile-automation.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 821-makefile-automation.md
**Demonstrates:** Complete Makefile for a Python project with categorized help, tool auto-detection, parameter guards, dependency chains, and cleanup targets
**Use When:** Setting up GNU Make-based project automation for a Python project using uv/uvx
**Version:** 1.0
**Last Validated:** 2026-02-18

## Prerequisites

- [ ] GNU Make installed (3.81+)
- [ ] uv installed for Python dependency management
- [ ] pyproject.toml present at project root
- [ ] Python project with tests/ directory

## Implementation

```makefile
# ============================================================================
# My Python Project -- Makefile
# ============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help

# Auto-detect tool paths (simply expanded := to evaluate once)
UV := $(shell command -v uv 2>/dev/null || echo "uv")
UVX := $(shell command -v uvx 2>/dev/null || echo "uvx")
PROJECT_VERSION := $(shell awk -F'"' '/^version = "/ {print $$2; exit}' pyproject.toml 2>/dev/null || echo "unknown")

# ============================================================================
# Help (categorized for 8+ targets)
# ============================================================================

.PHONY: help
help: ## Show this help message
	@echo "========================================================================"
	@echo "My Python Project v$(PROJECT_VERSION) -- Development Commands"
	@echo "========================================================================"
	@echo ""
	@echo "QUICKSTART"
	@echo "------------------------------------------------------------------------"
	@echo "  make quality-fix              Fix all code quality issues"
	@echo "  make test                     Run all pytest tests"
	@echo "  make validate                 Run all CI/CD validation checks"
	@echo ""
	@echo "ENVIRONMENT SETUP"
	@echo "------------------------------------------------------------------------"
	@echo "  make env-python               Pin Python 3.11 and create venv"
	@echo "  make env-sync                 Sync dev dependencies (fast)"
	@echo "  make env-deps                 Lock and sync dependencies"
	@echo ""
	@echo "CODE QUALITY"
	@echo "------------------------------------------------------------------------"
	@echo "  make lint                     Run ruff linter (check only)"
	@echo "  make format                   Run ruff formatter (check only)"
	@echo "  make lint-fix                 Fix lint issues"
	@echo "  make format-fix               Fix format issues"
	@echo "  make typecheck                Run ty type checker"
	@echo "  make quality-check            Run all quality checks"
	@echo "  make quality-fix              Fix all quality issues"
	@echo ""
	@echo "TESTING"
	@echo "------------------------------------------------------------------------"
	@echo "  make test                     Run all pytest tests"
	@echo "  make test-cov                 Run tests with coverage report"
	@echo "  make test-cov-open            Coverage + open in browser (macOS)"
	@echo ""
	@echo "DEPLOYMENT"
	@echo "------------------------------------------------------------------------"
	@echo "  make deploy DEST=/path        Deploy to target (DEST required)"
	@echo "  make deploy-dry DEST=/path    Preview deployment"
	@echo ""
	@echo "VALIDATION & CI"
	@echo "------------------------------------------------------------------------"
	@echo "  make preflight                Verify environment is ready"
	@echo "  make validate                 Run all CI/CD validation checks"
	@echo ""
	@echo "CLEANUP"
	@echo "------------------------------------------------------------------------"
	@echo "  make clean-cache              Remove Python cache files"
	@echo "  make clean-venv               Remove virtual environment"
	@echo "  make clean                    Remove all generated files"
	@echo "========================================================================"

# ============================================================================
# Environment Setup
# ============================================================================

.PHONY: env-python
env-python: ## Pin Python 3.11 and create venv
	$(UV) python install 3.11
	$(UV) python pin 3.11
	$(UV) venv

.PHONY: env-sync
env-sync: ## Sync dev dependencies
	$(UV) sync --all-groups

.PHONY: env-deps
env-deps: ## Lock and sync dependencies
	$(UV) lock
	$(UV) sync --all-groups

# ============================================================================
# Code Quality
# ============================================================================

.PHONY: lint
lint: ## Run ruff linter (check only)
	$(UV) run ruff check .

.PHONY: format
format: ## Run ruff formatter (check only)
	$(UV) run ruff format --check .

.PHONY: lint-fix
lint-fix: ## Fix lint issues
	$(UV) run ruff check --fix .

.PHONY: format-fix
format-fix: ## Fix format issues
	$(UV) run ruff format .

.PHONY: typecheck
typecheck: ## Run ty type checker
	$(UV) run ty check .

.PHONY: quality-check
quality-check: lint format typecheck ## Run all quality checks

.PHONY: quality-fix
quality-fix: lint-fix format-fix ## Fix all quality issues

# ============================================================================
# Testing
# ============================================================================

.PHONY: test
test: ## Run all pytest tests
	$(UV) run pytest tests/ --tb=short

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	$(UV) run pytest --cov=src --cov-report=term-missing --cov-report=html tests/

.PHONY: test-cov-open
test-cov-open: test-cov ## Coverage + open in browser (macOS)
	@if [ "$$(uname)" = "Darwin" ]; then \
		open htmlcov/index.html; \
	elif [ "$$(uname)" = "Linux" ]; then \
		xdg-open htmlcov/index.html; \
	else \
		echo "Coverage report generated at htmlcov/index.html"; \
	fi

# ============================================================================
# Deployment (with parameter guards)
# ============================================================================

.PHONY: deploy
deploy: ## Deploy to target (DEST=... required)
ifndef DEST
	$(error DEST is required. Usage: make deploy DEST=/path/to/project)
endif
	$(UV) run deploy-tool $(DEST)

.PHONY: deploy-dry
deploy-dry: ## Preview deployment (DEST=... required)
ifndef DEST
	$(error DEST is required. Usage: make deploy-dry DEST=/path/to/project)
endif
	$(UV) run deploy-tool $(DEST) --dry-run

# ============================================================================
# Validation & CI
# ============================================================================

.PHONY: preflight
preflight: ## Verify environment is ready
	@command -v $(UV) >/dev/null 2>&1 || { echo "ERROR: uv not found. Install: https://docs.astral.sh/uv/"; exit 1; }
	@test -f pyproject.toml || { echo "ERROR: pyproject.toml not found. Run from project root."; exit 1; }
	@echo "Environment ready"

.PHONY: validate
validate: quality-check test ## Run all CI/CD validation checks
	@echo "All validation checks passed!"

# ============================================================================
# Cleanup (idempotent with error suppression)
# ============================================================================

.PHONY: clean-cache
clean-cache: ## Remove Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

.PHONY: clean-venv
clean-venv: ## Remove virtual environment
	rm -rf .venv

.PHONY: clean
clean: clean-cache clean-venv ## Remove all generated files
	rm -rf htmlcov .coverage .ruff_cache
```

## Key Patterns Demonstrated

**Tool Auto-Detection (line 8-10):**
- `:=` assignment evaluates `$(shell ...)` once at parse time
- Fallback to bare command name if tool is not in PATH

**Categorized Help (line 16-68):**
- `.DEFAULT_GOAL := help` makes `make` show help by default
- Manual categorized output for 15+ targets
- Visual hierarchy with section headers and consistent alignment

**Parameter Guards (line 127-137):**
- `ifndef DEST` checks for required variable before recipe executes
- `$(error ...)` stops Make with a clear usage message

**Dependency Chains (line 101, 147):**
- `quality-check: lint format typecheck` runs all three in order
- `validate: quality-check test` composes higher-level validations

**Idempotent Cleanup (line 153-165):**
- `2>/dev/null || true` suppresses errors when files do not exist
- Composite `clean` target depends on specific cleanup targets

**Cross-Platform Recipe (line 116-122):**
- Shell conditional in recipe for runtime platform detection
- Graceful fallback message for unsupported platforms

## Validation

```bash
# Verify help displays correctly
make help

# Dry-run key targets to verify command expansion
make -n lint
make -n test
make -n validate

# Verify parameter guard produces error
make deploy 2>&1 | grep "DEST is required"

# Verify preflight check
make preflight

# Run the full validation chain
make validate
```

**Expected Results:**
- `make help` displays categorized output with all sections
- `make -n lint` shows `uv run ruff check .`
- `make deploy` (without DEST) shows error: `DEST is required. Usage: make deploy DEST=/path/to/project`
- `make preflight` shows `Environment ready` when uv and pyproject.toml are present
- `make validate` runs quality checks and tests, ending with `All validation checks passed!`
