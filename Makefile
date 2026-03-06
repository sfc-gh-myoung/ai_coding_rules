# ============================================================================
# AI Coding Rules — Makefile
# Replaces ./dev with make targets
# ============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help

# Auto-detect tool paths
UV := $(shell command -v uv 2>/dev/null || echo "uv")
UVX := $(shell command -v uvx 2>/dev/null || echo "uvx")
PROJECT_VERSION := $(shell awk -F'"' '/^version = "/ {print $$2; exit}' pyproject.toml 2>/dev/null || echo "unknown")

# ============================================================================
# Help
# ============================================================================

.PHONY: help
help: ## Show this help message
	@echo "════════════════════════════════════════════════════════════════════════"
	@echo "AI Coding Rules v$(PROJECT_VERSION) — Development Commands"
	@echo "════════════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "QUICKSTART"
	@echo "────────────────────────────────────────────────────────────────────────"
	@echo "  make quality-fix              Fix all code quality issues"
	@echo "  make test                     Run all pytest tests"
	@echo "  make validate                 Run all CI/CD validation checks"
	@echo "  make index-generate           Regenerate rules/RULES_INDEX.md"
	@echo "  make deploy DEST=/path        Deploy rules to project"
	@echo ""
	@echo "ENVIRONMENT SETUP"
	@echo "────────────────────────────────────────────────────────────────────────"
	@echo "  make env-python               Pin Python 3.11 and create venv"
	@echo "  make env-sync                 Sync dev dependencies (fast)"
	@echo "  make env-deps                 Lock and sync dependencies"
	@echo ""
	@echo "CODE QUALITY"
	@echo "────────────────────────────────────────────────────────────────────────"
	@echo "  make lint                     Run ruff linter (check only)"
	@echo "  make format                   Run ruff formatter (check only)"
	@echo "  make lint-fix                 Fix lint issues"
	@echo "  make format-fix               Fix format issues"
	@echo "  make typecheck                Run ty type checker"
	@echo "  make markdown                 Run pymarkdownlnt Markdown linter"
	@echo "  make quality-check            Run all quality checks"
	@echo "  make quality-fix              Fix all quality issues"
	@echo ""
	@echo "TESTING"
	@echo "────────────────────────────────────────────────────────────────────────"
	@echo "  make test                     Run all pytest tests"
	@echo "  make test-cov                 Run tests with coverage report"
	@echo "  make test-cov-open            Coverage + open in browser (macOS)"
	@echo ""
	@echo "RULES MANAGEMENT"
	@echo "────────────────────────────────────────────────────────────────────────"
	@echo "  make rules-validate           Validate rules with schema validator"
	@echo "  make rules-validate-verbose   Validate rules (verbose output)"
	@echo "  make examples-validate        Validate example rules"
	@echo "  make examples-validate-verbose Validate examples (verbose)"
	@echo "  make index-generate           Generate rules/RULES_INDEX.md"
	@echo "  make index-check              Check if RULES_INDEX.md is current"
	@echo "  make index-dry                Preview index generation"
	@echo "  make rule-new FILENAME=...    Generate new rule template"
	@echo "  make rule-new-force FILENAME= Overwrite existing template"
	@echo ""
	@echo "DEPLOYMENT"
	@echo "────────────────────────────────────────────────────────────────────────"
	@echo "  make deploy DEST=...          Deploy production rules (unified)"
	@echo "  make deploy-dry DEST=...      Preview deployment"
	@echo "  make deploy-verbose DEST=...  Deploy with verbose output"
	@echo "  make deploy-no-skills DEST=   Deploy rules only (skip skills)"
	@echo "  make deploy-only-skills DEST= Deploy only skills"
	@echo "  make deploy-no-mode DEST=...  Deploy with AGENTS_NO_MODE.md"
	@echo "  make deploy-split AGENTS=...  Deploy to separate directories"
	@echo ""
	@echo "TOKEN MANAGEMENT"
	@echo "────────────────────────────────────────────────────────────────────────"
	@echo "  make tokens-update            Update token budgets in rules/"
	@echo "  make tokens-check             Check token budget accuracy"
	@echo "  make tokens-update-file FILE= Update single file token budget"
	@echo ""
	@echo "KEYWORD MANAGEMENT"
	@echo "────────────────────────────────────────────────────────────────────────"
	@echo "  make keywords-suggest FILE=   Suggest keywords for rule file"
	@echo "  make keywords-diff FILE=...   Show keyword diff for rule file"
	@echo "  make keywords-update FILE=... Update keywords in rule file"
	@echo "  make keywords-all             Suggest keywords for all rules"
	@echo ""
	@echo "VALIDATION & CI"
	@echo "────────────────────────────────────────────────────────────────────────"
	@echo "  make preflight                Verify environment is ready"
	@echo "  make validate                 Run all CI/CD validation checks"
	@echo "  make badges-update            Update README badges"
	@echo "  make refs-check               Validate index references"
	@echo ""
	@echo "CLEANUP"
	@echo "────────────────────────────────────────────────────────────────────────"
	@echo "  make clean-cache              Remove Python cache files"
	@echo "  make clean-venv               Remove virtual environment"
	@echo "  make clean                    Remove all generated files"
	@echo ""
	@echo "STATUS"
	@echo "────────────────────────────────────────────────────────────────────────"
	@echo "  make status                   Show project status summary"
	@echo "════════════════════════════════════════════════════════════════════════"

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

.PHONY: markdown
markdown: ## Run pymarkdownlnt Markdown linter
	$(UVX) pymarkdownlnt --config pymarkdown.rules.json scan rules/ templates/AGENTS_MODE.md.template templates/AGENTS_NO_MODE.md.template
	$(UVX) pymarkdownlnt --config pymarkdown.docs.json scan docs/ README.md CONTRIBUTING.md CHANGELOG.md

.PHONY: quality-check
quality-check: lint format typecheck markdown ## Run all quality checks

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
	$(UV) run pytest --cov=src/ai_rules --cov-report=term-missing --cov-report=html tests/

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
# Rules Management (delegates to ai-rules CLI)
# ============================================================================

.PHONY: rules-validate
rules-validate: ## Validate rules with schema validator
	$(UV) run ai-rules validate rules/

.PHONY: rules-validate-verbose
rules-validate-verbose: ## Validate rules (verbose output)
	$(UV) run ai-rules validate rules/ --verbose

.PHONY: examples-validate
examples-validate: ## Validate example rules
	$(UV) run ai-rules validate rules/examples/ --examples

.PHONY: examples-validate-verbose
examples-validate-verbose: ## Validate examples (verbose)
	$(UV) run ai-rules validate rules/examples/ --examples --verbose

.PHONY: index-generate
index-generate: ## Generate rules/RULES_INDEX.md from rules/
	$(UV) run ai-rules index generate

.PHONY: index-check
index-check: ## Check if RULES_INDEX.md is current
	$(UV) run ai-rules index check

.PHONY: index-dry
index-dry: ## Preview index generation
	$(UV) run ai-rules index generate --dry-run

.PHONY: rule-new
rule-new: ## Generate new rule template (FILENAME=... required)
ifndef FILENAME
	$(error FILENAME is required. Usage: make rule-new FILENAME=my-rule)
endif
	$(UV) run ai-rules new $(FILENAME) $(if $(TIER),--context-tier $(TIER)) $(if $(KEYWORDS),--keywords '$(KEYWORDS)') $(if $(OUTPUT_DIR),--output-dir $(OUTPUT_DIR))

.PHONY: rule-new-force
rule-new-force: ## Overwrite existing template (FILENAME=... required)
ifndef FILENAME
	$(error FILENAME is required. Usage: make rule-new-force FILENAME=my-rule)
endif
	$(UV) run ai-rules new $(FILENAME) --force $(if $(TIER),--context-tier $(TIER)) $(if $(KEYWORDS),--keywords '$(KEYWORDS)') $(if $(OUTPUT_DIR),--output-dir $(OUTPUT_DIR))

# ============================================================================
# Deployment (delegates to ai-rules CLI)
# ============================================================================

.PHONY: deploy
deploy: ## Deploy production rules (DEST=... required)
ifndef DEST
	$(error DEST is required. Usage: make deploy DEST=/path/to/project)
endif
	$(UV) run ai-rules deploy $(DEST) $(if $(NO_MODE),--no-mode)

.PHONY: deploy-dry
deploy-dry: ## Preview deployment (DEST=... required)
ifndef DEST
	$(error DEST is required. Usage: make deploy-dry DEST=/path/to/project)
endif
	$(UV) run ai-rules deploy $(DEST) --dry-run $(if $(NO_MODE),--no-mode)

.PHONY: deploy-verbose
deploy-verbose: ## Deploy with verbose output (DEST=... required)
ifndef DEST
	$(error DEST is required. Usage: make deploy-verbose DEST=/path/to/project)
endif
	$(UV) run ai-rules deploy $(DEST) --verbose $(if $(NO_MODE),--no-mode)

.PHONY: deploy-no-skills
deploy-no-skills: ## Deploy rules only, skip skills (DEST=... required)
ifndef DEST
	$(error DEST is required. Usage: make deploy-no-skills DEST=/path/to/project)
endif
	$(UV) run ai-rules deploy $(DEST) --skip-skills

.PHONY: deploy-only-skills
deploy-only-skills: ## Deploy only skills (DEST=... required)
ifndef DEST
	$(error DEST is required. Usage: make deploy-only-skills DEST=/path/to/project)
endif
	$(UV) run ai-rules deploy $(DEST) --only-skills

.PHONY: deploy-no-mode
deploy-no-mode: ## Deploy with AGENTS_NO_MODE.md (DEST=... required)
ifndef DEST
	$(error DEST is required. Usage: make deploy-no-mode DEST=/path/to/project)
endif
	$(UV) run ai-rules deploy $(DEST) --no-mode $(if $(DRY_RUN),--dry-run)

.PHONY: deploy-split
deploy-split: ## Deploy to separate directories (AGENTS=... required)
ifndef AGENTS
	$(error AGENTS is required. Usage: make deploy-split AGENTS=/path/to/agents)
endif
	$(UV) run ai-rules deploy --split --agents-dest $(AGENTS) $(if $(RULES),--rules-dest $(RULES)) $(if $(SKILLS),--skills-dest $(SKILLS)) $(if $(NO_MODE),--no-mode) $(if $(DRY_RUN),--dry-run) $(if $(FORCE),--force)

# ============================================================================
# Token Management (delegates to ai-rules CLI)
# ============================================================================

.PHONY: tokens-update
tokens-update: ## Update token budgets in rules/
	$(UV) run ai-rules tokens rules/

.PHONY: tokens-check
tokens-check: ## Check token budget accuracy
	$(UV) run ai-rules tokens rules/ --dry-run --detailed

.PHONY: tokens-update-file
tokens-update-file: ## Update single file token budget (FILE=... required)
ifndef FILE
	$(error FILE is required. Usage: make tokens-update-file FILE=rules/my-rule.md)
endif
	$(UV) run ai-rules tokens $(FILE)

# ============================================================================
# Keyword Management (delegates to ai-rules CLI)
# ============================================================================

.PHONY: keywords-suggest
keywords-suggest: ## Suggest keywords for rule file (FILE=... required)
ifndef FILE
	$(error FILE is required. Usage: make keywords-suggest FILE=rules/my-rule.md)
endif
	$(UV) run ai-rules keywords $(FILE) --corpus

.PHONY: keywords-diff
keywords-diff: ## Show keyword diff for rule file (FILE=... required)
ifndef FILE
	$(error FILE is required. Usage: make keywords-diff FILE=rules/my-rule.md)
endif
	$(UV) run ai-rules keywords $(FILE) --corpus --diff

.PHONY: keywords-update
keywords-update: ## Update keywords in rule file (FILE=... required)
ifndef FILE
	$(error FILE is required. Usage: make keywords-update FILE=rules/my-rule.md)
endif
	$(UV) run ai-rules keywords $(FILE) --corpus --update

.PHONY: keywords-all
keywords-all: ## Suggest keywords for all rules
	$(UV) run ai-rules keywords rules/ --corpus

# ============================================================================
# Badges & References (delegates to ai-rules CLI)
# ============================================================================

.PHONY: badges-update
badges-update: ## Update README badges
	$(UV) run pytest --cov=scripts --cov=src/ai_rules --cov-report=term-missing --cov-report=html --tb=no -q tests/ | tee .pytest-output.txt
	$(UV) run ai-rules badges update --pytest-output .pytest-output.txt
	@rm -f .pytest-output.txt

.PHONY: refs-check
refs-check: ## Validate index references
	$(UV) run ai-rules refs check

# ============================================================================
# Validation & CI
# ============================================================================

.PHONY: preflight
preflight: ## Verify environment is ready
	@command -v $(UV) >/dev/null 2>&1 || { echo "ERROR: uv not found. Install: https://docs.astral.sh/uv/"; exit 1; }
	@test -f pyproject.toml || { echo "ERROR: pyproject.toml not found. Run from project root."; exit 1; }
	@echo "Environment ready"

.PHONY: validate
validate: quality-check test rules-validate examples-validate index-check ## Run all CI/CD validation checks
	@echo "All validation checks passed!"

# ============================================================================
# Cleanup
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

# ============================================================================
# Status
# ============================================================================

.PHONY: status
status: ## Show project status summary
	@echo "════════════════════════════════════════════════════════════════════════"
	@echo "AI Coding Rules v$(PROJECT_VERSION) — Project Status"
	@echo "════════════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Rules:    $$(ls rules/*.md 2>/dev/null | wc -l | tr -d ' ') files in rules/"
	@echo "Examples: $$(ls rules/examples/*.md 2>/dev/null | wc -l | tr -d ' ') files in rules/examples/"
	@echo "Skills:   $$(ls skills/*.md 2>/dev/null | wc -l | tr -d ' ') files in skills/"
	@echo "Tests:    $$(find tests -name 'test_*.py' | wc -l | tr -d ' ') test files"

	@echo ""
	@echo "Python:   $$(python3 --version 2>/dev/null || echo 'not found')"
	@echo "UV:       $$($(UV) --version 2>/dev/null || echo 'not found')"
	@echo "Venv:     $$(test -d .venv && echo 'present' || echo 'missing')"
	@echo "════════════════════════════════════════════════════════════════════════"
