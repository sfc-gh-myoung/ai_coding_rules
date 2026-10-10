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
| Find available commands | Run `uv run ai-rules --help` or see [Development Commands](#development-commands) |

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
- [ ] **Run** `make quality-all-fix` to fix any quality issues
- [ ] **Build** the plugin with `uv run ai-rules plugin build` and validate it
- [ ] **Run** `make validate` to run the local validation pipeline
- [ ] **Update** documentation if needed
- [ ] **Add** yourself to contributors if first contribution

### CI/CD Pipeline

The GitHub Actions CI workflow runs automatically on pushes and PRs to `main`:

| Job | Purpose | Details |
|-----|---------|---------|
| `quality` | Code quality | ruff lint, ruff format, ty type check |
| `markdown` | Markdown linting | pymarkdownlnt for rules/ and docs/ |
| `test` | Unit tests | pytest with Python 3.12, 3.13 matrix |
| `coverage` | Coverage gate | pytest coverage report with the configured minimum |
| `validate` | Rules and plugin validation | rule schema, trigger evidence, corpus audit, trigger contract, and source-faithful plugin verification |

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

The project uses a production-ready rules architecture. For complete details, see [docs/ARCHITECTURE.md → System Components](docs/ARCHITECTURE.md#3-system-components).

**Key directories:**

- `rules/` - Production-ready rule files (edit here)
- `src/ai_rules/` - CLI tool source code
- `schemas/` - Validation schema definitions
- `tests/` - Test suite

**Key files:**

- `ai-coding-rules-plugin/` - built plugin: rules, skills, and the discovery hook
- `hooks/user-prompt-submit` - hook source; injects matched rules on every prompt (opt-in via `--with-hook`)

**Key Principle:** All rules in `rules/` are production-ready and ship directly in the plugin - no generation step required.

## Development Workflow

### Environment Setup

We use modern Python tooling for consistent development:

- **Python 3.12+** - Language runtime
- **uv** - Fast Python package installer and resolver
- **Ruff** - Lightning-fast linting and formatting
- **ty** - Fast type checker (Astral toolchain)
- **GNU Make 3.81+** - Development automation (root `Makefile`)

```bash
# Python environment with uv (recommended)
uv sync --all-groups         # Sync all dependencies

# Alternative with pip (fallback)
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install -e .
```

### Development Commands

The project uses a root `Makefile` for development automation. Run `make` for the categorized command list.

**Common commands:**

```bash
make quality-all-fix    # Fix all code quality issues
make test-run          # Run all pytest tests
make validate           # Run local quality, tests, schemas, and plugin verification
uv run ai-rules validate rules/          # Validate rules against schema
uv run ai-rules plugin build             # Build the distributable plugin
```

**See [docs/USING_DEV_CLI.md](docs/USING_DEV_CLI.md) for the complete command reference.**

For the complete Make target catalog and the distinction between local validation and hosted CI, see [docs/USING_DEV_CLI.md](docs/USING_DEV_CLI.md).

### Code Quality and Linting

```bash
# Run all quality checks at once
make quality-all          # check only
make quality-all-fix      # fix all auto-fixable issues

# Or run individual checks
make quality-lint         # ruff linter (check only)
make quality-lint-fix     # apply lint fixes
make quality-format       # ruff formatter (check only)
make quality-format-fix   # apply formatting
make quality-typecheck    # ty type checker
make quality-markdown     # pymarkdownlnt
```

### Pre-commit hooks

After cloning, install the hooks once:

```bash
uv run pre-commit install
```

This runs `ruff`, `ruff-format`, and `ty check` before each commit, matching CI.
The existing Entro secret-scan hook must also pass unless the team-approved skip
configuration (`git config entro.skipSecretScan true`) is set.

### Rule Validation

```bash
# Validate rules
uv run ai-rules validate rules/                       # Validate all rules
uv run ai-rules validate rules/100-snowflake-core.md  # Validate single rule
uv run ai-rules validate rules/ --verbose             # Verbose output
```

### Testing Your Changes

Before submitting a PR, ensure your changes work correctly:

```bash
# 1. Validate all rules
uv run ai-rules validate rules/

# 2. Validate specific rule you modified
uv run ai-rules validate rules/XXX-rule-name.md --verbose

# 3. Rebuild and verify the plugin
uv run ai-rules plugin build
uv run ai-rules plugin verify

# 4. Run test suite
make test-run

# 5. Run all quality checks
make quality-all-fix
```

**Commit your changes:**

```bash
git add rules/XXX-rule-name.md
git commit -m "feat: update XXX rule"
```

### Configuration Safety Guidelines

- **YAML Safety**: Avoid Unicode characters (bullets, checkmarks) that cause parsing errors
- **Shell Quoting**: Quote arguments with special characters: `".[dev]"` not `.[dev]`
- **Python Packaging**: Ensure `__init__.py` files exist before `uv pip install -e .`

## Rule Authoring Guidelines

### File Naming Convention

Use the canonical [README rule-category map](README.md#rule-categories) to select the 3-digit domain range. The FastAPI subsection remains 210-219.

Use format: `XXX-topic-description.md` (3-digit number)

**Location:** All rule files go in `rules/` directory.

### Creating New Rules

Use the template generator to create schema-compliant rule files:

```bash
# Generate new rule template
uv run ai-rules new 300-example-rule --context-tier High

# Overwrite existing file (use with caution)
uv run ai-rules new 300-example-rule --force
```

**After generation:**

1. Edit the generated file and replace placeholders with actual content
2. Validate: `uv run ai-rules validate rules/`
3. Rebuild the plugin: `uv run ai-rules plugin build`

### Rule Structure

New and migrated rules target v4 as defined in [schemas/rule-schema.yml](schemas/rule-schema.yml) and [rules/002-rule-governance.md](rules/002-rule-governance.md). Declaring v4 is not a substitute for migrating and reviewing the body.

**Quick reference:**

- **Required YAML frontmatter:** `schema_version`, `rule_version`, `last_updated`, `keywords` (5-11 combined typed entries), `token_budget`, `context_tier`, and `depends` with required/optional filename lists.
- **Required H2 order:** Scope, Contract, References.
- **Required Contract H3 sections:** Inputs and Prerequisites, Mandatory, Execution Steps, Validation; each must have meaningful content.
- **Manual authoring review:** Preserve safety and dependency ownership, use one completion checklist under Validation, and show correct executable examples only. No fixed step count or anti-pattern gallery is required.
- **Validation:** Zero CRITICAL and HIGH findings. A structural pass does not prove technical accuracy or behavioral equivalence. Apply the active schema's placement limits rather than a copied historical limit.

For complete structure requirements, see [002-rule-governance.md](rules/002-rule-governance.md).

### Rule Versioning

Rule files use [Semantic Versioning](https://semver.org) for the YAML `rule_version` field. When modifying any rule file in `rules/`, update both the version and date:

**Version Increment Criteria:**

| Change Type | Version | Examples |
|-------------|---------|----------|
| **MAJOR** (vX.0.0) | Breaking changes | Removed sections, renamed keywords, schema upgrades, changed contract requirements |
| **MINOR** (vX.Y.0) | Additive changes | New keywords, examples, anti-patterns, new sections, expanded guidance |
| **PATCH** (vX.Y.Z) | Non-functional fixes | Typos, formatting, broken links, updated references, clarifications |

**Required Updates:**

1. **rule_version**: Increment per semantic versioning criteria above; schema migration is MAJOR
2. **last_updated**: Set to current date in `YYYY-MM-DD` format

For the full versioning policy and edge cases, see [002b-rule-update.md](rules/002b-rule-update.md).

### Directive Language

Use explicit, actionable language:

- **Requirement:** Non-negotiable must-dos
- **Always:** Best practices to follow consistently
- **Rule:** Specific directives or standards
- **Avoid:** Anti-patterns to prevent
- **Consider:** Recommendations for specific scenarios

This vocabulary is canonical for the project. README and architecture documentation link here rather than define separate hierarchies.

### Content Guidelines

- **Length**: Rules and skills should ideally be no more than 250 lines. `ai-rules validate` reports a HIGH finding for any rule over 250 lines (`schemas/rule-schema.yml` `structure.max_lines`). `ai-rules validate-skills` fails a `SKILL.md` only above 500 lines, so for skills 250 is the target and 500 is the hard check. Move optional detail into a focused companion rule or a skill's `workflows/`, `references/`, or `examples/` files without dropping required dependencies or safety instructions. Size alone does not prove quality. This limit does not apply to project documentation such as `README.md`, `CONTRIBUTING.md`, or `docs/`.
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
uv run ai-rules new 450-terraform-best-practices --context-tier High

# 3. Edit the generated file and fill in content
vim rules/450-terraform-best-practices.md

# 4. Validate the rule
uv run ai-rules validate rules/

# 5. Rebuild the plugin
uv run ai-rules plugin build

# 6. Run quality checks
make quality-all-fix

# 7. Commit the new rule
git add rules/450-terraform-best-practices.md
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

# 4. Rebuild the plugin
uv run ai-rules plugin build

# 5. Run quality checks
make quality-all-fix

# 6. Commit changes
git add rules/200-python-core.md
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
uv run ai-rules new 450-new-rule  # CORRECT
vim rules/450-new-rule.md         # Then edit generated template
```

**Don't skip validation:**

```bash
git add rules/450-new-rule.md
git commit  # WRONG - may have validation errors
```

**Always validate before committing:**

```bash
uv run ai-rules validate rules/
git add rules/450-new-rule.md
git commit  # CORRECT
```

**Don't forget to regenerate index:**

```bash
vim rules/450-new-rule.md
git add rules/450-new-rule.md
git commit  # WRONG - plugin not rebuilt
```

**Always rebuild the plugin after rule changes:**

```bash
vim rules/450-new-rule.md
uv run ai-rules plugin build
make plugin-verify            # build fidelity against the sources
git add rules/450-new-rule.md # ai-coding-rules-plugin/ is gitignored build output
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

For usage guide, see [docs/USING_RULE_REVIEWER_SKILL.md](docs/USING_RULE_REVIEWER_SKILL.md).

```text
Review rules/XXX-rule-name.md using the Agent-Centric Rule Review criteria.
Review Date: YYYY-MM-DD
Review Mode: STALENESS
```

This provides:

- **100-point scoring** - Six scored dimensions with hard caps defined by the reviewer rubric
- **Three review modes** - FULL, FOCUSED (targeted), STALENESS (periodic maintenance)
- **Staleness detection** - Identifies outdated tool versions, deprecated patterns, API changes
- **Cross-model compatibility** - Review criteria are designed for consistent evaluation across supported agent families

## Code of Conduct

All contributors must follow the [Code of Conduct](CODE_OF_CONDUCT.md). Report conduct concerns privately through the repository owner's GitHub profile.

## Getting Help

### Self-Service Resources

- **README.md** - Project overview, setup, troubleshooting
- **`rules/000-global-core.md`** - Rule loading contract and execution protocols
- **docs/ARCHITECTURE.md** - System architecture and design decisions

### Community Support

- **GitHub Issues:** [File an issue](https://github.com/sfc-gh-myoung/ai_coding_rules/issues) for bugs, features, or rule suggestions
- **Issue templates:** [bug reports](.github/ISSUE_TEMPLATE/bug_report.yml) and [feature requests](.github/ISSUE_TEMPLATE/feature_request.yml) capture the required context
- **Security issues:** Follow the private reporting process in [SECURITY.md](SECURITY.md); do not file suspected vulnerabilities as public issues

## Rule Quality Standards

The v4 authoring contract in `002-rule-governance.md` governs rule structure and semantic review. Cross-model behavior requires evaluation; portable Markdown alone does not guarantee it.

**Key Standards:**

- Standardized metadata order - Consistent parsing across agents
- Investigation-First protocols - Prevents hallucinations
- Complete response templates - Working code examples
- Accurate token budgets - Reliable context planning
- Explicit dependency declarations - Automated rule loading
- Standardized code block tags - Consistent syntax highlighting

**For Contributors:**

- **Validate rules:** `uv run ai-rules validate rules/`
- **Run all CI checks:** `make validate`
- **Complete standards:** See `rules/002-rule-governance.md` and the active schema

## Recognition

Contributors are recognized in several ways:

- **Contributors section** in README (automatic via GitHub)
- **Special mentions** in release notes for significant contributions
- **Maintainer status** for consistent, high-quality contributions
- **Community spotlights** in discussions

Thank you for helping make AI Coding Rules better for everyone!

## Rule Loading Evaluator: authoring fixtures

The Rule Loading Evaluator is a live-agent sanity check that the
Cortex Code Agent SDK, given the injected rule context plus a fixture
prompt, loads the rules each fixture declares. See
[`docs/EVALUATING_RULE_LOADER.md`](docs/EVALUATING_RULE_LOADER.md) for
the full reference.

Two points matter when you commit:

- **Optional pre-commit hook.** `rule-loader-eval` is not in `.pre-commit-config.yaml`
  by default. If you add it (see [Adding the hook](docs/EVALUATING_RULE_LOADER.md#adding-the-hook)),
  bypass it on commits without Snowflake credentials with
  `SKIP=rule-loader-eval git commit -m "..."`.

- **CI does not run the live agent.** CI runs only the trigger-evidence invariant
  (`uv run ai-rules rule-loader validate`, called from `make validate`).

See [`docs/EVALUATING_RULE_LOADER.md`](docs/EVALUATING_RULE_LOADER.md) for the full
command reference (validate, eval, create, refresh, refresh-all, compare, and the
fixture schema) and
[`fixtures/rule_loader_eval/AUTHORING_GUIDE.md`](fixtures/rule_loader_eval/AUTHORING_GUIDE.md)
for prompt-writing guidance.
