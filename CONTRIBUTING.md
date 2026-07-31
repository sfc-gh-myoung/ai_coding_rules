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
- [ ] **Run** `uv run ai-rules dev quality all --fix` to fix any quality issues
- [ ] **Build** the plugin with `uv run ai-rules plugin build` and validate it
- [ ] **Run** `uv run ai-rules dev validate` to run all CI/CD checks
- [ ] **Update** documentation if needed
- [ ] **Add** yourself to contributors if first contribution

### CI/CD Pipeline

The GitHub Actions CI workflow runs automatically on pushes and PRs to `main`:

| Job | Purpose | Details |
|-----|---------|---------|
| `quality` | Code quality | ruff lint, ruff format, ty type check |
| `markdown` | Markdown linting | pymarkdownlnt for rules/ and docs/ |
| `test` | Unit tests | pytest with Python 3.12, 3.13 matrix |
| `validate` | Rules validation | schema validation, `rule-loader-validate` (trigger-evidence invariant; pure-Python) |

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

- `ai-coding-rules-plugin/` - built plugin: rules, skills, and the discovery hook
- `hooks/user-prompt-submit` - injects matched rules on every prompt

**Key Principle:** All rules in `rules/` are production-ready and ship directly in the plugin - no generation step required.

## Development Workflow

### Environment Setup

We use modern Python tooling for consistent development:

- **Python 3.12+** - Language runtime
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

The project uses the unified `ai-rules` CLI for task automation. Run `uv run ai-rules --help` for the top-level command list, or `uv run ai-rules dev --help` for development commands.

**Common commands:**

```bash
uv run ai-rules dev quality all --fix    # Fix all code quality issues
uv run ai-rules dev test run             # Run all pytest tests
uv run ai-rules dev validate             # Run all CI/CD checks
uv run ai-rules validate rules/          # Validate rules against schema
uv run ai-rules plugin build             # Build the distributable plugin
```

**See [docs/USING_DEV_CLI.md](docs/USING_DEV_CLI.md) for the complete `ai-rules dev` reference.**

### Code Quality and Linting

```bash
# Run all quality checks at once
uv run ai-rules dev quality all          # check only
uv run ai-rules dev quality all --fix    # fix all auto-fixable issues

# Or run individual checks
uv run ai-rules dev quality lint         # ruff linter (check only)
uv run ai-rules dev quality lint --fix   # apply lint fixes
uv run ai-rules dev quality format       # ruff formatter (check only)
uv run ai-rules dev quality format --fix # apply formatting
uv run ai-rules dev quality typecheck    # ty type checker
uv run ai-rules dev quality markdown     # pymarkdownlnt
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

# 3. Rebuild and validate the plugin
uv run ai-rules plugin build
cortex plugin validate ./ai-coding-rules-plugin

# 5. Run test suite
uv run ai-rules dev test run

# 6. Run all quality checks
uv run ai-rules dev quality all --fix
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
uv run ai-rules new 300-example-rule --context-tier High

# Overwrite existing file (use with caution)
uv run ai-rules new 300-example-rule --force
```

**After generation:**

1. Edit the generated file and replace placeholders with actual content
2. Validate: `uv run ai-rules validate rules/`
3. Rebuild the plugin: `uv run ai-rules plugin build`

### Rule Structure

All rules must follow the v3.5 schema defined in [rules/002-rule-governance.md](rules/002-rule-governance.md).

**Quick reference:**

- **Required metadata:** SchemaVersion, RuleVersion, LastUpdated, Keywords (5-7), TokenBudget, ContextTier, Depends (each entry uses `required:`/`optional:` bucket prefix; see `rules/002-rule-governance.md` "Depends Bucket Semantics")
- **Required sections:** Scope, References, Contract, Anti-Patterns, Post-Execution Checklist
- **Contract must appear before line 200**

For complete structure requirements, see [002-rule-governance.md](rules/002-rule-governance.md).

### Rule Versioning

Rule files use [Semantic Versioning](https://semver.org) for the `RuleVersion` field. When modifying any rule file in `rules/`, you must update both the version and date:

**Version Increment Criteria:**

| Change Type | Version | Examples |
|-------------|---------|----------|
| **MAJOR** (vX.0.0) | Breaking changes | Removed sections, renamed keywords, schema upgrades, changed contract requirements |
| **MINOR** (vX.Y.0) | Additive changes | New keywords, examples, anti-patterns, new sections, expanded guidance |
| **PATCH** (vX.Y.Z) | Non-functional fixes | Typos, formatting, broken links, updated references, clarifications |

**Required Updates:**

1. **RuleVersion**: Increment per semantic versioning criteria above
2. **LastUpdated**: Set to current date in `YYYY-MM-DD` format

For the full versioning policy and edge cases, see [002b-rule-update.md](rules/002b-rule-update.md).

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
uv run ai-rules new 450-terraform-best-practices --context-tier High

# 3. Edit the generated file and fill in content
vim rules/450-terraform-best-practices.md

# 4. Validate the rule
uv run ai-rules validate rules/

# 5. Rebuild the plugin
uv run ai-rules plugin build

# 6. Run quality checks
uv run ai-rules dev quality all --fix

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
uv run ai-rules dev quality all --fix

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
git add rules/450-new-rule.md ai-coding-rules-plugin/
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

- **6-point scoring** - Actionability, Completeness, Consistency, Parsability, Token Efficiency, Staleness
- **Three review modes** - FULL, FOCUSED (targeted), STALENESS (periodic maintenance)
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
- **`rules/000-global-core.md`** - Rule loading contract and execution protocols
- **docs/ARCHITECTURE.md** - System architecture and design decisions

### Community Support

- **GitHub Issues:** [File an issue](https://github.com/sfc-gh-myoung/ai_coding_rules/issues) for bugs, features, or rule suggestions
- **GitHub Discussions:** [Join the discussion](https://github.com/sfc-gh-myoung/ai_coding_rules/discussions) for questions and community support

## Rule Quality Standards

All rules follow **Section 11: Universal Compatibility Standards** from `002-rule-governance.md`, ensuring consistent behavior across all AI agents and LLMs.

**Key Standards:**

- Standardized metadata order - Consistent parsing across agents
- Investigation-First protocols - Prevents hallucinations
- Complete response templates - Working code examples
- Accurate token budgets - Reliable context planning
- Explicit dependency declarations - Automated rule loading
- Standardized code block tags - Consistent syntax highlighting

**For Contributors:**

- **Validate rules:** `uv run ai-rules validate rules/`
- **Run all CI checks:** `uv run ai-rules dev validate`
- **Complete standards:** See `rules/002-rule-governance.md` Section 11

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

**Pre-commit hook.** A local hook (`rule-loader-eval`) runs five
representative fixtures through the live SDK
(`uv run ai-rules rule-loader eval --fixture <id>`). Commits without
Snowflake credentials should bypass it explicitly:

```bash
SKIP=rule-loader-eval git commit -m "..."
```

CI does not run the live agent; it only runs the trigger-evidence
invariant via `uv run ai-rules rule-loader validate` (called
from `uv run ai-rules dev validate`).

**The trigger-evidence invariant** (enforced via
`uv run ai-rules rule-loader validate`) requires every fixture's
`prompt` to contain a literal token for each `ext:` / `file:` /
`dir:` trigger declared by a required rule:

- `ext:.py` -> prompt MUST contain a filename ending in `.py`
  (e.g., `analytics/etl_pipeline.py`).
- `ext:.sh` -> prompt MUST contain a filename ending in `.sh`
  (e.g., `scripts/deploy.sh`).
- `file:snowflake.yml` -> prompt MUST contain `snowflake.yml`.
- `dir:skills/` -> prompt MUST contain `skills/`.

A fixture that declares `ext:.py` but lacks any `.py` filename in the
prompt is rejected at fixture-load time (exit 4).

**Required vs dependencies.** Each fixture's `expected` block has two
lists. `expected.required` lists rules the prompt directly should
match (these are also the rules the trigger-evidence invariant
checks). `expected.dependencies` lists rules that should be loaded
because a required rule declares them (`Depends:` /
`## References → Must Load First`). The matcher checks the agent's
loaded set against the union and reports gaps separately for each
list. The evaluator does not parse rule-file dependency metadata;
rules own that information and the agent loads + reports it in
its `**Bootstrap:**` line and `**Rules Loaded**` section per the
Rule Loading Contract (R1-R8 in `rules/000-global-core.md`).

**Authoring a new fixture.** Use `create` to capture the live agent's loaded set
for your prompt. The default `--effort low --max-turns 15` gives the live agent
enough budget to complete the bootstrap protocol, run the citation gate, and emit
structured output reliably for most fixtures. For difficult fixtures, use the
exhaustive fallback:

```bash
uv sync --group live-agent
ai-rules rule-loader create \
    --prompt 'How do I build a streamlit dashboard?' \
    --id new-fixture --variant simple \
    --write fixtures/rule_loader_eval/new-fixture.yaml

# Exhaustive fallback for difficult fixtures:
ai-rules rule-loader create \
    --prompt 'How do I build a streamlit dashboard?' \
    --id new-fixture --variant simple \
    --effort high --max-turns 50 \
    --write fixtures/rule_loader_eval/new-fixture.yaml
```

**Batch-refreshing.** When authoring or refreshing multiple fixtures at once,
use `refresh-all`. It runs all matched fixtures concurrently and writes
candidate YAMLs to an output directory:

```bash
# Refresh all fixtures at once:
uv run ai-rules rule-loader refresh-all --all \
    --concurrency 4 \
    --out-dir out/seeds/

# Exhaustive fallback (difficult fixtures or reliability investigations):
ai-rules rule-loader refresh-all --all --max-turns 50 --effort high

# Lower concurrency if you hit rate limits:
ai-rules rule-loader refresh-all --all --concurrency 1
```

See `docs/EVALUATING_RULE_LOADER.md` for full batch documentation.

**Refreshing or iterating on an existing fixture.** Use `refresh` to
re-run a fixture's prompt through the live SDK and detect drift:

```bash
# Refresh: re-run and diff against the on-disk YAML.
ai-rules rule-loader refresh \
    fixtures/rule_loader_eval/simple-cortex-search.yaml

# Accept the regenerated skeleton (snapshot-style write-back):
ai-rules rule-loader refresh \
    fixtures/rule_loader_eval/simple-cortex-search.yaml --write
```

The `create` and `refresh` commands compare two primary signals of which rules the agent loaded (per Rule Loading Contract R1-R8), with an optional legacy 3rd signal:

1. **Tool reads** - `read_file` calls captured via PreToolUse hook (ground truth).
2. **`**Rules Loaded**`** - the agent's declared loaded section (R1).
3. **`## Reads Performed`** - (legacy) only checked when present; v3.9+ agents do not emit it.

When the primary signals agree, the captured loaded set is trustworthy. When they disagree, a structured warning explains which signals diverge and points at likely causes (especially Anti-Pattern 3: fabricated gate compliance). A separate warning surfaces citation drift — declared line counts that don't match actual rule file line counts (R3/R5 fabrication signal).

When trusting the generated `expected.required`:
- If signals agree -> trust the captured set; split into `required` and `dependencies` as before.
- If `**Rules Loaded**` lists rules not in tool reads -> treat as fabrication; verify each rule was actually needed for the prompt before including it.
- If tool reads contain rules not in the declared section -> the agent read but did not declare; usually safe to include but worth investigating.
- If citation drift is reported -> the agent likely cited values from pretraining; re-run the seeder until citations match.

Then split the captured `expected.required` list manually between
`required` (direct matches) and `dependencies` (transitively pulled
in), fill in `trigger_evidence`, and commit.

**Forbidden-rule violations are warn-only by default.** Use
`--strict-forbidden` to opt into hard-fail.
