# Contributing to AI Coding Rules

Thank you for your interest in contributing to AI Coding Rules! This project provides universal AI coding rules for consistent, reliable software engineering across LLMs and IDEs.

## 🚀 Quick Start

1. **Fork** the repository on your preferred platform

2. **Clone** your fork locally (choose one):

   ```bash
   # GitHub:
   git clone https://github.com/sfc-gh-myoung/ai_coding_rules.git
   
   cd ai_coding_rules
   ```

3. **Set up** the development environment:

   ```bash
   task env:deps
   ```

4. **Create** a feature branch:

   ```bash
   git checkout -b feature/my-new-rule
   ```

## 📁 Project Structure (v3.0)

The project uses a **production-ready rules architecture** where rules are authored once in universal Markdown format and work everywhere without transformation.

```ascii
ai_coding_rules/
├── rules/                  ← Production-ready rules (103 files)
│   ├── 000-global-core.md
│   ├── 001-coding-agent-operations.md
│   ├── 100-snowflake-core.md
│   └── ...
├── AGENTS.md               ← Minimal bootstrap protocol (project root)
├── RULES_INDEX.md          ← Rule catalog with loading strategy (project root)
├── scripts/                ← Validation and deployment tools
│   ├── index_generator.py      ← Generate RULES_INDEX.md
│   ├── rule_deployer.py        ← Deploy rules to projects
│   ├── schema_validator.py     ← Validate rule structure
│   ├── template_generator.py   ← Create new rule templates
│   └── token_validator.py      ← Validate token budgets
├── docs/                   ← Documentation
├── tests/                  ← Test suite
└── schemas/                ← JSON schemas for rule validation
```

**Key Principle:** All rules in `rules/` are production-ready and deploy directly—no generation step required.

### File Locations

| What You're Editing | Where to Edit | What Happens |
|---------------------|---------------|--------------|
| Rule content | `rules/XXX-rule-name.md` | Validate with `task rules:validate` |
| Bootstrap protocol | `AGENTS.md` (project root) | Minimal rule loading sequence |
| Execution protocols | `rules/000-global-core.md` | MODE transitions, validation, workflows |
| Rule catalog | `RULES_INDEX.md` (project root) | Regenerate with `task index:generate` |
| Deployment script | `scripts/rule_deployer.py` | Test with `--dry-run` flag |

## 📋 Development Workflow

### Environment Setup

We use modern Python tooling for consistent development:

- **Python 3.11+** - Language runtime
- **uv** - Fast Python package installer and resolver
- **Ruff** - Lightning-fast linting and formatting
- **ty** - Fast type checker (Astral toolchain)
- **Task** - Simple task runner for automation

```bash
# Python environment with uv (recommended)
task env:sync              # Sync dev dependencies (fast)
task env:python            # Pin Python version and create venv
task env:deps              # Lock and sync dependencies

# Alternative with pip (fallback)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Code Quality & Linting

```bash
# Quality tasks (recommended)
task quality:check        # Run all quality checks (lint, format, type, markdown)
task quality:fix          # Fix all quality issues (alias: fix, qf)
task quality:lint         # Run ruff linter (check only)
task quality:format       # Run ruff formatter (check only)
task quality:typecheck    # Run ty type checker (aliases: type, type-check)
task quality:markdown     # Run pymarkdownlnt Markdown linter
task quality:lint:fix     # Auto-fix linting issues
task quality:format:fix   # Apply formatting

# Manual commands (if task unavailable)
uv sync --all-groups         # Ensure dev deps installed (ruff, ty, pytest, ...)
uv run ruff check .          # Check linting
uv run ruff format --check . # Check formatting
uv run ruff format .         # Apply formatting
uv run ty check .            # Type check
```

### Rule Deployment

```bash
# Deploy rules to a project
python scripts/rule_deployer.py --dest ~/my-project

# Preview deployment without copying
python scripts/rule_deployer.py --dest ~/my-project --dry-run
```

### Rule Validation

The project supports two validation systems:

**Schema Validation (v3.0+)**

```bash
# Validate single rule
python scripts/schema_validator.py rules/100-snowflake-core.md

# Validate all rules
python scripts/schema_validator.py rules/

# Strict mode (fail on warnings)
python scripts/schema_validator.py rules/ --strict

# Verbose output with detailed errors
python scripts/schema_validator.py rules/100-snowflake-core.md --verbose

# Custom schema
python scripts/schema_validator.py rules/ --schema custom-schema.yml
```

See `docs/SCHEMA_VALIDATION_MIGRATION.md` for detailed migration guide.

**Other Validation Tools**

```bash
# Regenerate RULES_INDEX.md from rule files
python scripts/index_generator.py

# Preview index generation without writing
python scripts/index_generator.py --dry-run
```

### Utilities

```bash
task clean:cache         # Remove Python cache files
task clean:venv          # Remove virtual environment
task clean:all           # Remove all generated files
task status              # Show project status summary
task preflight           # Verify environment is ready
task -l                  # List all available tasks (standard view)
task                     # Show categorized task list with quickstart
```

### Configuration Safety Guidelines

- **YAML Safety**: Avoid Unicode characters (bullets, checkmarks) that cause parsing errors
- **Shell Quoting**: Quote arguments with special characters: `".[dev]"` not `.[dev]`
- **Taskfile Validation**: Always test with `task --list` after YAML changes
- **Python Packaging**: Ensure `__init__.py` files exist before `uv pip install -e .`

### Testing Your Changes

Before submitting a PR, ensure your changes work correctly:

```bash
# 1. Validate all rules with schema
python scripts/schema_validator.py rules/

# 2. Validate specific rule you modified
python scripts/schema_validator.py rules/XXX-rule-name.md --verbose

# 3. Regenerate RULES_INDEX.md if metadata changed
python scripts/index_generator.py

# 4. Test deployment
python scripts/rule_deployer.py --dest /tmp/test --dry-run

# 5. Run test suite
task test

# 6. Run all quality checks
task quality:check
```

**Important:** Commit your rule changes:

```bash
git add rules/XXX-rule-name.md
git add RULES_INDEX.md  # If you regenerated it
git commit -m "feat: update XXX rule"
```

## 📝 Rule Authoring Guidelines

### File Naming Convention

Follow the established 3-digit numbering system:

- **000-099**: Core foundation rules
- **100-199**: Data platform rules (Snowflake)
- **200-299**: Software engineering rules (Python)
  - **210-219**: FastAPI framework subsection
- **300-399**: Software engineering rules (JavaScript/TypeScript)
- **400-499**: Software engineering rules (Go)
- **500-599**: Data science and analytics
- **600-699**: Data governance
- **700-799**: Business intelligence
- **800-899**: Project management
- **900-999**: Demo and synthetic data

Use format: `XXX-topic-description.md` (3-digit number)

**Location:** All rule files go in `rules/` directory.

Example: `rules/250-python-flask.md`

### Creating New Rules with Template Generator

Use the template generator to create v3.0 compliant rule files:

```bash
# Using Task (recommended - includes automatic validation)
task rule:new FILENAME=100-snowflake-example
task rule:new FILENAME=200-python-example TIER=High
task rule:new FILENAME=300-react-hooks KEYWORDS="react, hooks, state, effects, custom hooks, lifecycle, functional components, useState, useEffect, optimization, performance, patterns, best practices, debugging, testing"

# Overwrite existing file
task rule:new:force FILENAME=100-example TIER=High

# Using Python script directly
python scripts/template_generator.py 100-snowflake-example
python scripts/template_generator.py 200-python-example --context-tier High
python scripts/template_generator.py 300-react-hooks --keywords "react, hooks, state, effects, custom hooks, lifecycle, functional components, useState, useEffect, optimization, performance, patterns, best practices, debugging, testing"
python scripts/template_generator.py 100-example --force
python scripts/template_generator.py 100-example --output-dir custom/
```

**Template Features:**

- ✅ **v3.0 Schema Compliant** - Passes schema validation out of the box
- ✅ **Auto-generated Keywords** - Smart keyword generation based on rule number and slug
- ✅ **Complete Structure** - All required sections with placeholders
- ✅ **Inline Guidance** - Comments explaining each section's purpose
- ✅ **Automatic Validation** - Task version validates immediately after generation

**Next Steps After Generation:**

1. Edit the generated file and replace placeholders with actual content
2. Validation: Already done if using `task rule:new`, otherwise run `task rules:validate:verbose`
3. Add to RULES_INDEX.md: `task index:generate`

### Rule Structure (v3.0+)

Each rule file (in `rules/`) must follow the v3.0 structure defined in `002-rule-governance.md`:

```markdown
# Rule Title

**Keywords:** keyword1, keyword2, ... (10-15 semantic terms)
**TokenBudget:** ~1500
**ContextTier:** Critical|High|Medium|Low
**Depends:** rules/000-global-core.md

## Purpose
Brief description of the rule's purpose (1-2 sentences).

## Rule Scope
**Applies to:** What this rule covers
**Does NOT apply to:** Explicit exclusions

## Quick Start TL;DR
**MANDATORY:**
**Essential Patterns:**
- **[Pattern 1]:** Description
- **[Pattern 2]:** Description
- **[Pattern 3]:** Description
- **[Pattern 4]:** Description
- **[Pattern 5]:** Description
- **[Pattern 6]:** Description

**Quick Checklist:**
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3
- [ ] Item 4
- [ ] Item 5

## Contract
- **Inputs/Prereqs:** What the rule needs
- **Allowed Tools:** Tools that can be used
- **Forbidden Tools:** Tools that must not be used
- **Required Steps:**
  1. Step 1
  2. Step 2
  3. Step 3
  4. Step 4
  5. Step 5
- **Output Format:** Expected output
- **Validation Steps:** How to verify success

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Description**

```language
# Bad example
code here
```

**Problem:** Why this fails

**Correct Pattern:**

```language
# Good example
code here
```

**Benefits:** Why this works

## Quick Compliance Checklist

- [ ] Compliance item 1
- [ ] Compliance item 2
- [ ] Compliance item 3
- [ ] Compliance item 4
- [ ] Compliance item 5

## Validation

- **Success Checks:** How to verify success
- **Negative Tests:** What should fail

## Response Template

```bash
# Command or code template
echo "Example output"
```

## References

### External Documentation

- [Official Docs](https://example.com)

### Related Rules

- `rules/000-global-core.md` - Foundation rule

```markdown

**Key Requirements:**
- **10-15 Keywords** for semantic search
- **TokenBudget** in ~NUMBER format
- **ContextTier** enum: Critical, High, Medium, Low
- **Quick Start TL;DR** with 6-7 Essential Patterns
- **Anti-Patterns** with 2+ code examples
- **No emojis** - text-only markup
- **Contract before line 160** for progressive disclosure

See `rules/002-rule-governance.md` for complete structure requirements.

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

## 🐛 Issue Reporting

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

## 🔍 Pull Request Guidelines

### Before Submitting

- [ ] **Test** your changes locally
- [ ] **Run** `task quality:check` and fix any issues (or `task quality:fix`)
- [ ] **Test** rule deployment with `task deploy:dry DEST=/tmp/test`
- [ ] **Run** `task validate` to run all CI/CD checks
- [ ] **Update** documentation if needed
- [ ] **Add** yourself to contributors if first contribution

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
   ```
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

### Changelog and Release Notes Policy

**IMPORTANT:** This project follows industry best practices for release documentation:

- **CHANGELOG.md is the single source of truth** - All changes are documented here per [Keep a Changelog](https://keepachangelog.com) standards
- **No separate release notes files** - Individual version files duplicate CHANGELOG.md content (anti-pattern)
- **Update CHANGELOG.md for all PRs** - Add entry under `## [Unreleased]` section
- **Use Conventional Commits format** - `type(scope): description` (see rules/800-project-changelog.md)

**Historical Note:** Individual release notes files (v2.x) have been removed. Current practice is CHANGELOG.md only.

**Note for AI Agents:** See [rules/803-project-git-workflow.md](rules/803-project-git-workflow.md) for detailed validation protocols and automated compliance checks.

## 🎯 Types of Contributions

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
- Translate content (future feature)

### Infrastructure
- Improve CI/CD pipelines
- Add automated testing
- Enhance development tooling
- Optimize performance

## 🔄 Complete Contribution Workflow Example

### Adding a New Rule

```bash
# 1. Create feature branch
git checkout -b feature/add-terraform-rules

# 2. Generate template using Task (includes automatic validation)
task rule:new FILENAME=450-terraform-best-practices TIER=High
# Or use Python script directly:
# python scripts/template_generator.py 450-terraform-best-practices --context-tier High

# 3. Edit the generated file and fill in content
vim rules/450-terraform-best-practices.md
# Replace all placeholders with actual content

# 4. Validate the rule again after editing
task rules:validate:verbose
# Or: python scripts/schema_validator.py rules/450-terraform-best-practices.md --verbose

# 5. Regenerate RULES_INDEX.md
task index:generate

# 6. Run quality checks
task quality:check

# 7. Commit the new rule and updated index
git add rules/450-terraform-best-practices.md
git add RULES_INDEX.md
git commit -m "feat: add Terraform best practices rule

- Comprehensive Terraform IaC guidelines
- State management best practices
- Security and compliance patterns
- Resource naming conventions"

# Example with breaking change
# git commit -m "feat!: update Python core rule with type hints guidance
#
# BREAKING CHANGE: Type hints now required for all public functions"

# 8. Push and create PR
git push origin feature/add-terraform-rules
```

### Updating an Existing Rule

```bash
# 1. Create feature branch
git checkout -b fix/update-python-core

# 2. Edit the rule file
vim rules/200-python-core.md
# Make your changes...

# 3. Validate changes with schema validator
python scripts/schema_validator.py rules/200-python-core.md --verbose

# 4. Update index if metadata changed
task index:generate

# 5. Run quality checks
task quality:lint
task quality:format

# 6. Commit changes
git add rules/200-python-core.md
git add RULES_INDEX.md  # If metadata changed
git commit -m "fix: update Python core rule with type hints guidance"

# 7. Push and create PR
git push origin fix/update-python-core
```

### Common Mistakes to Avoid

❌ **Don't skip template generator for new rules**
```bash
vim rules/450-new-rule.md  # WRONG - manual creation error-prone
```

✅ **Always use template generator**
```bash
python scripts/template_generator.py 450-new-rule  # CORRECT
vim rules/450-new-rule.md  # Then edit generated template
```

❌ **Don't skip schema validation**
```bash
git add rules/450-new-rule.md
git commit  # WRONG - may have validation errors
```

✅ **Always validate before committing**
```bash
python scripts/schema_validator.py rules/450-new-rule.md --verbose
git add rules/450-new-rule.md
git commit  # CORRECT
```

❌ **Don't forget to regenerate index**
```bash
vim rules/450-new-rule.md
git add rules/450-new-rule.md
git commit  # WRONG - RULES_INDEX.md not updated
```

✅ **Always regenerate index after rule changes**
```bash
vim rules/450-new-rule.md
task index:generate
git add rules/450-new-rule.md RULES_INDEX.md
git commit  # CORRECT
```

❌ **Don't use non-standard commit formats**
```bash
git commit -m "Updated the python rule file"  # WRONG - no type
git commit -m "fixed bug"  # WRONG - no scope, vague description
git checkout -b johns-updates  # WRONG - no type prefix
```

✅ **Always follow Conventional Commits and Branches**
```bash
git commit -m "fix(python): resolve type annotation validation error"
git commit -m "docs(readme): clarify installation steps for Windows"
git checkout -b fix/type-annotation-validation
git checkout -b docs/windows-installation-guide
```

## 🏷️ Code of Conduct

We are committed to fostering an open and welcoming environment. Please:

- **Be respectful** in all interactions
- **Be collaborative** and help others learn
- **Be patient** with newcomers and different perspectives
- **Be constructive** in feedback and criticism
- **Be inclusive** and welcome diverse contributors

## 📞 Getting Help

- **GitHub Discussions**: Ask questions and share ideas
- **GitHub Issues**: Report bugs and request features  
- **README**: Check installation and usage instructions
- **Rules**: Each rule file includes relevant documentation links

## 🙏 Recognition

Contributors are recognized in several ways:

- **Contributors section** in README (automatic via GitHub)
- **Special mentions** in release notes for significant contributions
- **Maintainer status** for consistent, high-quality contributions
- **Community spotlights** in discussions

---

## 💡 Improving Existing Rules

It is not unexpected to run into a scenario where an agent or LLM fails to follow one or more of the rules you are using. In these scenarios, the best approach is to prompt the agent/llm within the same session the following:

```
MODE PLAN:

My rule files should have prevented this behavior or outcome. Thoroughly review all rule files in the project and the currently selected rule files for this session. Determine what specific improvements I can make to the rules to ensure this does not happen again.
```

For this to be effective, you should have a copy of this project repo `ai_coding_rules/` within your project directory. You can then edit the rule files directly in `rules/` and deploy them to test your improvements. It is also important to verify that `002-rule-governance.md` is an actively selected rule in the project. It should be auto attached, but it never hurts to verify. This will ensure any rule changes will follow best practices and structure laid out for the `ai_coding_rules/` project.

Available LLMs are always evolving and improving in their capabilities. You should periodically ask your LLM of choice to review and make recommendations on rule improvements.

**Recommended: Use the Agent-Centric Rule Review Prompt**

For systematic, cross-model compatible reviews, use the prompt template in [prompts/RULE_REVIEW_PROMPT.md](prompts/RULE_REVIEW_PROMPT.md).

For a short usage guide (modes, examples, cadence), see
[docs/USING_RULE_REVIEW_PROMPT.md](docs/USING_RULE_REVIEW_PROMPT.md).

```
Review rules/XXX-rule-name.md using the Agent-Centric Rule Review criteria.
Review Date: YYYY-MM-DD
Review Mode: STALENESS
```

This prompt provides:
- **6-point scoring** — Actionability, Completeness, Consistency, Parsability, Token Efficiency, Staleness
- **Three review modes** — FULL (comprehensive), FOCUSED (targeted), STALENESS (periodic maintenance)
- **Staleness detection** — Identifies outdated tool versions, deprecated patterns, API changes
- **Cross-model compatibility** — Tested on GPT-4o, GPT-5.1, GPT-5.2, Claude Sonnet 4.5, Claude Opus 4.5, Gemini 2.5 Pro, Gemini 3 Pro

**Alternative: Quick Review Prompt**

For a simpler review without structured scoring:

```
MODE PLAN:

Thoroughly review all of the rule files in the project directory. Ensure all of the rules are consistent with 002-rule-governance.md and follow the prescribed rule structure and format. Determine if there are any improvements that can be made to any rule files which will improve rule effectiveness while ensuring good management of context size with an emphasis on reducing duplicate and/or conflicting guidance.
```

Using `MODE PLAN:` is a best practice and directly uses the functionality from `000-global-core.md` to reduce the chances of the agent from making unverified or unapproved changes. This ensures that you have an opportunity to review the proposed task list and suggest changes in plan before the changes are implemented. In most scenarios, the agent/llm should move forward with implementing the plan when you type `ACT`.

## 🆕 Generating New Rules

There will be times when you determine that you need to add a new rule to follow best practices for a specific framework or library, often when you introduce new frameworks or libraries. In these scenarios, the best approach is to prompt the agent/llm with the following:

```
MODE PLAN:

Create a rule for <INSERT FEATURE/FRAMEWORK/LIBRARY> best practices consistent with my rule repository in `ai_coding_rules/`. Determine if a single rule file is the best approach, or if there should be multiple rule files. Use the following documentation as primary points of reference:
@URL1
@URL2
@URL3
```

In my experience, you will get consistently better results when you provide live reference links to documentation and any reference links that specifically cover best practices, syntax, etc. If you let the agent/llm try to determine their own references, you are likely to incorporate inaccurate or dated reference information that results in less than ideal rules being generated.

---

## Getting Help

### Self-Service Resources

1. **README.md:** Comprehensive documentation
   - Architecture details
   - Advanced configuration
   - Troubleshooting guide

2. **RULES_INDEX.md (project root):** Find rules by keyword
   - Search by technology
   - Browse by category (000-900)
   - Check dependencies

3. **AGENTS.md:** Rule loading protocol
   - Decision trees
   - Integration patterns
   - Best practices

### Community Support

1. **GitHub Issues:** [File an issue](https://github.com/sfc-gh-myoung/ai_coding_rules/issues)
   - Bug reports
   - Feature requests
   - Rule suggestions

2. **GitHub Discussions:** [Join the discussion](https://github.com/sfc-gh-myoung/ai_coding_rules/discussions)
   - Questions and answers
   - Tips and tricks
   - Community support

### Snowflake Internal Support

*For Snowflake employees only:*

1. **GitHub Issues:** [File an issue](https://github.com/sfc-gh-myoung/ai_coding_rules/issues)
   - Internal bug reports
   - Feature requests specific to Snowflake workflows

2. **Team Channels:**
   - **Slack:** #ai-coding-rules (quick questions, tips, community support)
   - **Teams:** AI Coding Rules Channel
   - **Email List:** Subscribe to rule update notifications

3. **Team Lead:** Contact your manager
   - Access issues
   - Strategic questions
   - Process clarifications

---

## Team Collaboration (Snowflake Internal)

*This section is for Snowflake team members.*

### Bookmark Key Resources

- [ ] [AI Coding Rules Repository](https://github.com/sfc-gh-myoung/ai_coding_rules)
- [ ] [RULES_INDEX.md](https://github.com/sfc-gh-myoung/ai_coding_rules/blob/main/RULES_INDEX.md)
- [ ] [Project Issues](https://github.com/sfc-gh-myoung/ai_coding_rules/issues)

### Schedule Rule Updates

**Monthly:** Check for rule updates
```bash
# With Task:
cd /tmp/ai-rules && git pull
task deploy DEST=~/my-project

# Without Task (Python script):
cd /tmp/ai-rules && git pull
uv sync --all-groups
uv run python scripts/rule_deployer.py --dest ~/my-project
```

**Quarterly:** Run STALENESS reviews on critical rules
```
# Use the Agent-Centric Rule Review prompt (prompts/RULE_REVIEW_PROMPT.md)
Review rules/000-global-core.md using Agent-Centric Rule Review.
Review Date: YYYY-MM-DD
Review Mode: STALENESS
```

**Recommended Review Cadence:**
| Rule Type | Frequency | Mode |
|-----------|-----------|------|
| Foundation (000-*) | Quarterly | FULL |
| Domain Cores (1XX, 2XX, etc.) | Quarterly | STALENESS |
| Specialized/Activity Rules | Semi-annually | STALENESS |
| Reference Rules (>5000 tokens) | Annually | STALENESS |

**Yearly:** Suggest new rules for your domain

### Rule Quality Standards (v3.1)

All rules in this repository follow **Section 11: Universal Compatibility Standards** from `002-rule-governance.md`, ensuring consistent behavior across all AI agents and LLMs.

**Key Standards:**
- ✅ **Quick Start TL;DR sections** - Essential patterns in 30 seconds
- ✅ **Standardized metadata order** - Consistent parsing across agents
- ✅ **Investigation-First protocols** - Prevents hallucinations
- ✅ **Complete response templates** - Working code examples
- ✅ **Accurate token budgets** - Reliable context planning
- ✅ **Explicit dependency declarations** - Automated rule loading
- ✅ **Standardized code block tags** - Consistent syntax highlighting

**For Contributors:**
- **Validate rules:** `task rules:validate` - Check all rules against schema
- **Run all CI checks:** `task validate` - Run quality, tests, rules validation
- **Complete standards:** See `rules/002-rule-governance.md` Section 11

**Validation Tools:**
- `scripts/schema_validator.py` - Schema-based validation with detailed errors
- Validates: metadata order, TL;DR presence, Contract placement, Investigation protocols, token budgets, Section 11 compliance, and more

---

Thank you for helping make AI Coding Rules better for everyone! 🚀
