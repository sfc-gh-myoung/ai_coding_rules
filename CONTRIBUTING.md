# Contributing to AI Coding Rules

Thank you for your interest in contributing to AI Coding Rules! This project provides universal AI coding rules for consistent, reliable software engineering across LLMs and IDEs.

## Quick Start

1. **Fork** the repository on GitHub

2. **Clone** your fork locally:

   ```bash
   git clone https://github.com/sfc-gh-myoung/ai_coding_rules.git
   cd ai_coding_rules
   ```

3. **Set up** the development environment:

   ```bash
   uv sync --all-groups
   ```

4. **Create** a feature branch:

   ```bash
   git checkout -b feature/my-new-rule
   ```

## Who Should Read What

| I want to... | Start here |
|--------------|------------|
| Report a bug or suggest a feature | [Issue Reporting](#issue-reporting) |
| Fix a typo or small error | [Quick Start](#quick-start) then [PR Guidelines](#pull-request-guidelines) |
| Improve an existing rule | [Development Workflow](#development-workflow) |
| Create a new rule | [Rule Authoring Guidelines](#rule-authoring-guidelines) |
| Understand the architecture | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Find available commands | Run `make help` or see [Development Commands](#development-commands) |

## Types of Contributions

### New Rules

- Research and write new domain-specific rules
- Follow the established naming and structure conventions
- Include relevant examples and documentation links
- Test with multiple LLMs/IDEs when possible

### Rule Improvements

- Enhance existing rules with better examples
- Add missing best practices or anti-patterns
- Update references to current documentation
- Improve clarity and actionability

### Generator Enhancements

- Add support for new IDEs or tools
- Improve metadata parsing
- Enhance output formatting
- Add validation and error handling

### Documentation

- Improve README or contributing guidelines
- Add usage examples and tutorials
- Create video demonstrations

### Infrastructure

- Improve CI/CD pipelines
- Add automated testing
- Enhance development tooling
- Optimize performance

## Issue Reporting

When reporting issues, please include:

- **Rule file(s)** affected
- **IDE/LLM** you're using
- **Expected behavior** vs actual behavior
- **Steps to reproduce**
- **Environment details** (Python version, OS, etc.)

Use our issue templates:

- **Bug Report**: For problems with existing rules
- **Feature Request**: For new rule suggestions
- **IDE Support**: For new IDE integration requests

## Pull Request Guidelines

### Before Submitting

- [ ] **Test** your changes locally
- [ ] **Run** `make quality-fix` to fix any quality issues
- [ ] **Test** rule deployment with `make deploy-dry DEST=/tmp/test`
- [ ] **Run** `make validate` to run all CI/CD checks
- [ ] **Update** documentation if needed
- [ ] **Add** yourself to contributors if first contribution

### CI/CD Pipeline

The GitHub Actions CI workflow runs automatically on pushes and PRs to `main`:

| Job | Purpose | Details |
|-----|---------|---------|
| `quality` | Code quality | ruff lint, ruff format, ty type check |
| `markdown` | Markdown linting | pymarkdownlnt for rules/ and docs/ |
| `test` | Unit tests | pytest with Python 3.11, 3.12, 3.13 matrix |
| `validate` | Rules validation | schema validation, RULES_INDEX.md check |

All jobs run in parallel for fast feedback. Ensure all checks pass before requesting review.

### Commit and Branch Standards

This project follows industry standards for Git workflow:

- **Conventional Commits v1.0.0** - [Official Specification](https://www.conventionalcommits.org/en/v1.0.0/#specification)
  - Required format: `type(scope): description`
  - Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
  - Breaking changes: Append `!` after type or use `BREAKING CHANGE:` footer

- **Conventional Branch** - [Official Specification](https://conventional-branch.github.io/#specification)
  - Required format: `type/description-in-kebab-case`
  - Supported types: `feature/`, `fix/`, `docs/`, `refactor/`, `chore/`
  - Keep branch names descriptive and concise (3-5 words)

**Why These Standards Matter:**

- Automated changelog generation
- Semantic versioning automation
- Clear project history
- Better collaboration
- CI/CD integration

### PR Requirements

1. **Title**: Use Conventional Commits format

   ```text
   feat(snowflake): add clustering optimization rule
   fix(python): update ruff configuration patterns
   docs(readme): improve installation instructions
   ```

2. **Description**: Include:
   - What changes you made
   - Why the changes were needed
   - How to test the changes
   - Any breaking changes or considerations

3. **Scope**: Keep PRs focused on a single feature or fix

4. **Tests**: Ensure rule generation still works correctly

### Review Process

1. **Automated checks** must pass (linting, formatting, generation tests)
2. **Maintainer review** for content quality and consistency
3. **Community feedback** for significant changes
4. **Documentation update** if the change affects user workflows

### Changelog Policy

**IMPORTANT:** This project follows industry best practices for release documentation:

- **CHANGELOG.md is the single source of truth** - All changes are documented here per [Keep a Changelog](https://keepachangelog.com) standards
- **No separate release notes files** - Individual version files duplicate CHANGELOG.md content (anti-pattern)
- **Update CHANGELOG.md for all PRs** - Add entry under `## [Unreleased]` section
- **Use Conventional Commits format** - `type(scope): description` (see rules/800-project-changelog.md)

**Note for AI Agents:** See [rules/803-project-git-workflow.md](rules/803-project-git-workflow.md) for detailed validation protocols and automated compliance checks.

## Project Structure

The project uses a production-ready rules architecture. For complete details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#directory-structure).

**Key directories:**

- `rules/` - Production-ready rule files (edit here)
- `src/ai_rules/` - CLI tool source code
- `schemas/` - Validation schema definitions
- `tests/` - Test suite

**Key files:**

- `AGENTS.md` - AI agent bootstrap protocol
- `RULES_INDEX.md` - Searchable rule catalog

**Key Principle:** All rules in `rules/` are production-ready and deploy directly - no generation step required.

## Development Workflow

### Environment Setup

We use modern Python tooling for consistent development:

- **Python 3.11+** - Language runtime
- **uv** - Fast Python package installer and resolver
- **Ruff** - Lightning-fast linting and formatting
- **ty** - Fast type checker (Astral toolchain)
- **make** - Task automation

```bash
# Python environment with uv (recommended)
uv sync --all-groups         # Sync all dependencies

# Alternative with pip (fallback)
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Development Commands

The project uses a Makefile for task automation. Run `make help` for a categorized command list.

**Common commands:**

```bash
make quality-fix    # Fix all code quality issues
make test           # Run all pytest tests
make validate       # Run all CI/CD checks
make rules-validate # Validate rules against schema
make index-generate # Regenerate RULES_INDEX.md
make deploy DEST=~  # Deploy rules to project
```

**See [docs/ARCHITECTURE.md#makefile-architecture](docs/ARCHITECTURE.md#makefile-architecture) for complete command reference.**

### Code Quality and Linting

```bash
# Quality tasks (recommended)
make quality-fix      # Fix all quality issues (lint, format)
make lint             # Run ruff linter (check only)
make format           # Run ruff formatter (check only)
make typecheck        # Run ty type checker

# Manual commands (if make unavailable)
uv run ruff check .          # Check linting
uv run ruff format --check . # Check formatting
uv run ruff format .         # Apply formatting
uv run ty check .            # Type check
```

### Rule Validation

```bash
# Validate rules
make rules-validate                                    # Validate all rules
uv run ai-rules validate rules/100-snowflake-core.md  # Validate single rule
uv run ai-rules validate rules/ --verbose             # Verbose output

# Regenerate index
make index-generate                                    # Regenerate RULES_INDEX.md
```

### Testing Your Changes

Before submitting a PR, ensure your changes work correctly:

```bash
# 1. Validate all rules
make rules-validate

# 2. Validate specific rule you modified
uv run ai-rules validate rules/XXX-rule-name.md --verbose

# 3. Regenerate RULES_INDEX.md if metadata changed
make index-generate

# 4. Test deployment
make deploy-dry DEST=/tmp/test

# 5. Run test suite
make test

# 6. Run all quality checks
make quality-fix
```

**Commit your changes:**

```bash
git add rules/XXX-rule-name.md
git add RULES_INDEX.md  # If you regenerated it
git commit -m "feat: update XXX rule"
```

### Configuration Safety Guidelines

- **YAML Safety**: Avoid Unicode characters (bullets, checkmarks) that cause parsing errors
- **Shell Quoting**: Quote arguments with special characters: `".[dev]"` not `.[dev]`
- **Python Packaging**: Ensure `__init__.py` files exist before `uv pip install -e .`

## Rule Authoring Guidelines

### File Naming Convention

Follow the established 3-digit numbering system:

- **000-099**: Core foundation rules
- **100-199**: Data platform rules (Snowflake)
- **200-299**: Software engineering rules (Python)
  - **210-219**: FastAPI framework subsection
- **300-399**: Shell/Containers
- **400-499**: Frontend (JavaScript/TypeScript)
- **500-599**: Frontend (HTMX)
- **600-699**: Systems/Backend (Go)
- **800-899**: Project management
- **900-999**: Analytics and governance

Use format: `XXX-topic-description.md` (3-digit number)

**Location:** All rule files go in `rules/` directory.

### Creating New Rules

Use the template generator to create schema-compliant rule files:

```bash
# Generate new rule template
make rule-new FILENAME=300-example-rule TIER=High

# Or use CLI directly
uv run ai-rules new 300-example-rule --context-tier High

# Overwrite existing file (use with caution)
make rule-new-force FILENAME=300-example-rule
```

**After generation:**

1. Edit the generated file and replace placeholders with actual content
2. Validate: `make rules-validate`
3. Update index: `make index-generate`

### Rule Structure

All rules must follow the v3.2 schema defined in [rules/002-rule-governance.md](rules/002-rule-governance.md).

**Quick reference:**

- **Required metadata:** SchemaVersion, RuleVersion, LastUpdated, Keywords (5-20), TokenBudget, ContextTier, Depends
- **Required sections:** Scope, References, Contract, Anti-Patterns, Post-Execution Checklist
- **Contract must appear before line 200**

For complete structure requirements, see [002-rule-governance.md](rules/002-rule-governance.md).

### Directive Language

Use explicit, actionable language:

- **Requirement:** Non-negotiable must-dos
- **Always:** Best practices to follow consistently
- **Rule:** Specific directives or standards
- **Avoid:** Anti-patterns to prevent
- **Consider:** Recommendations for specific scenarios

### Content Guidelines

- **Length**: Keep rules focused (target 150-300 lines, max 500)
- **Clarity**: Use clear, unambiguous language
- **Examples**: Include concrete code examples where helpful
- **Links**: Reference official documentation
- **Modularity**: Avoid duplicating content across rules

## Complete Workflow Examples

### Adding a New Rule

```bash
# 1. Create feature branch
git checkout -b feature/add-terraform-rules

# 2. Generate template
make rule-new FILENAME=450-terraform-best-practices TIER=High

# 3. Edit the generated file and fill in content
vim rules/450-terraform-best-practices.md

# 4. Validate the rule
make rules-validate

# 5. Regenerate RULES_INDEX.md
make index-generate

# 6. Run quality checks
make quality-fix

# 7. Commit the new rule and updated index
git add rules/450-terraform-best-practices.md RULES_INDEX.md
git commit -m "feat(rules): add Terraform best practices rule

- Comprehensive Terraform IaC guidelines
- State management best practices
- Security and compliance patterns"

# 8. Push and create PR
git push origin feature/add-terraform-rules
```

### Updating an Existing Rule

```bash
# 1. Create feature branch
git checkout -b fix/update-python-core

# 2. Edit the rule file
vim rules/200-python-core.md

# 3. Validate changes
uv run ai-rules validate rules/200-python-core.md --verbose

# 4. Update index if metadata changed
make index-generate

# 5. Run quality checks
make quality-fix

# 6. Commit changes
git add rules/200-python-core.md RULES_INDEX.md
git commit -m "fix(python): update core rule with type hints guidance"

# 7. Push and create PR
git push origin fix/update-python-core
```

### Common Mistakes to Avoid

**Don't skip template generator for new rules:**

```bash
vim rules/450-new-rule.md  # WRONG - manual creation error-prone
```

**Always use template generator:**

```bash
make rule-new FILENAME=450-new-rule  # CORRECT
vim rules/450-new-rule.md            # Then edit generated template
```

**Don't skip validation:**

```bash
git add rules/450-new-rule.md
git commit  # WRONG - may have validation errors
```

**Always validate before committing:**

```bash
make rules-validate
git add rules/450-new-rule.md
git commit  # CORRECT
```

**Don't forget to regenerate index:**

```bash
vim rules/450-new-rule.md
git add rules/450-new-rule.md
git commit  # WRONG - RULES_INDEX.md not updated
```

**Always regenerate index after rule changes:**

```bash
vim rules/450-new-rule.md
make index-generate
git add rules/450-new-rule.md RULES_INDEX.md
git commit  # CORRECT
```

**Follow Conventional Commits:**

```bash
# WRONG
git commit -m "Updated the python rule file"
git checkout -b johns-updates

# CORRECT
git commit -m "fix(python): resolve type annotation validation error"
git checkout -b fix/type-annotation-validation
```

## Improving Existing Rules

When an agent or LLM fails to follow rules correctly, prompt it to analyze the gap:

```text
MODE PLAN:

My rule files should have prevented this behavior or outcome. Thoroughly review
all rule files in the project and the currently selected rule files for this
session. Determine what specific improvements I can make to the rules to ensure
this does not happen again.
```

**Recommended: Use the Agent-Centric Rule Review Skill**

For systematic, cross-model compatible reviews, use the skill at [skills/rule-reviewer/SKILL.md](skills/rule-reviewer/SKILL.md).

For usage guide, see [docs/USING_RULE_REVIEW_SKILL.md](docs/USING_RULE_REVIEW_SKILL.md).

```text
Review rules/XXX-rule-name.md using the Agent-Centric Rule Review criteria.
Review Date: YYYY-MM-DD
Review Mode: STALENESS
```

This provides:

- **6-point scoring** - Actionability, Completeness, Consistency, Parsability, Token Efficiency, Staleness
- **Three review modes** - FULL (comprehensive), FOCUSED (targeted), STALENESS (periodic maintenance)
- **Staleness detection** - Identifies outdated tool versions, deprecated patterns, API changes
- **Cross-model compatibility** - Tested on GPT-4o, GPT-5.1, GPT-5.2, Claude Sonnet 4.5, Claude Opus 4.5, Gemini 2.5 Pro, Gemini 3 Pro

## Code of Conduct

We are committed to fostering an open and welcoming environment. Please:

- **Be respectful** in all interactions
- **Be collaborative** and help others learn
- **Be patient** with newcomers and different perspectives
- **Be constructive** in feedback and criticism
- **Be inclusive** and welcome diverse contributors

## Getting Help

### Self-Service Resources

- **README.md** - Project overview, setup, troubleshooting
- **RULES_INDEX.md** - Find rules by keyword or category
- **AGENTS.md** - Rule loading protocol details
- **docs/ARCHITECTURE.md** - System architecture and design decisions

### Community Support

- **GitHub Issues:** [File an issue](https://github.com/sfc-gh-myoung/ai_coding_rules/issues) for bugs, features, or rule suggestions
- **GitHub Discussions:** [Join the discussion](https://github.com/sfc-gh-myoung/ai_coding_rules/discussions) for questions and community support

## Rule Quality Standards

All rules follow **Section 11: Universal Compatibility Standards** from `002-rule-governance.md`, ensuring consistent behavior across all AI agents and LLMs.

**Key Standards:**

- Quick Start TL;DR sections - Essential patterns in 30 seconds
- Standardized metadata order - Consistent parsing across agents
- Investigation-First protocols - Prevents hallucinations
- Complete response templates - Working code examples
- Accurate token budgets - Reliable context planning
- Explicit dependency declarations - Automated rule loading
- Standardized code block tags - Consistent syntax highlighting

**For Contributors:**

- **Validate rules:** `make rules-validate`
- **Run all CI checks:** `make validate`
- **Complete standards:** See `rules/002-rule-governance.md` Section 11

## Recognition

Contributors are recognized in several ways:

- **Contributors section** in README (automatic via GitHub)
- **Special mentions** in release notes for significant contributions
- **Maintainer status** for consistent, high-quality contributions
- **Community spotlights** in discussions

Thank you for helping make AI Coding Rules better for everyone!
