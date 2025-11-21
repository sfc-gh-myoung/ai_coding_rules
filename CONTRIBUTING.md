# Contributing to AI Coding Rules

Thank you for your interest in contributing to AI Coding Rules! This project provides universal AI coding rules for consistent, reliable software engineering across LLMs and IDEs.

## 🚀 Quick Start

1. **Fork** the repository on your preferred platform
2. **Clone** your fork locally (choose one):
   ```bash
   # GitLab:
   git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git
   # GitHub:
   git clone https://github.com/Snowflake-Labs/ai_coding_rules.git
   
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

## 📁 Project Structure (v2.1.0+)

### Understanding the Template-Based System

The project uses a **template-based generation system** to maintain source templates and generate IDE-specific formats:

```
ai_coding_rules_gitlab/
├── templates/          ← Edit rule files here (SOURCE)
├── discovery/          ← Edit discovery files here
├── generated/          ← Generated outputs (DO NOT EDIT)
│   ├── universal/
│   ├── cursor/rules/
│   ├── copilot/instructions/
│   └── cline/
└── scripts/            ← Generation tools
```

**Golden Rule:** Always edit files in `templates/` or `discovery/`, never in `generated/`.

### File Locations

| What You're Editing | Where to Edit | What Happens |
|---------------------|---------------|--------------|
| Rule content | `templates/XXX-rule-name.md` | Regenerate with `task generate:rules:all` |
| Discovery guide | `discovery/AGENTS.md` | Copied to `generated/universal/` |
| Rule catalog | `discovery/RULES_INDEX.md` | Copied to `generated/universal/` |
| Generation script | `scripts/generate_agent_rules.py` | Test with `--dry-run` flag |

## 📋 Development Workflow

### Environment Setup

We use modern Python tooling for consistent development:

- **Python 3.11+** - Language runtime
- **uv** - Fast Python package installer and resolver
- **Ruff** - Lightning-fast linting and formatting
- **Task** - Simple task runner for automation

```bash
# Python environment with uv (recommended)
task env:deps              # Install development dependencies
task env:python           # Pin Python version and create venv

# Alternative with pip (fallback)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Code Quality & Linting

```bash
# Ruff (primary linter and formatter)
task quality:lint         # Check code with Ruff
task quality:format       # Check formatting
task quality:lint:fix     # Auto-fix linting issues
task quality:format:fix   # Apply formatting

# Manual commands (if task unavailable)
uvx ruff check .          # Check linting
uvx ruff format --check . # Check formatting
uvx ruff format .         # Apply formatting
```

### Rule Deployment

```bash
# Deploy rules with automatic path configuration
task deploy:universal DEST=~/my-project    # For any IDE/LLM (recommended)
task deploy:cursor DEST=~/my-project       # For Cursor IDE
task deploy:copilot DEST=~/my-project      # For GitHub Copilot
task deploy:cline DEST=~/my-project        # For Cline

# Deploy to current directory (omit DEST)
cd ~/my-project
task deploy:cursor
```

### Rule Generation & Validation

```bash
# Generate IDE-specific rules (advanced - use deployment instead for projects)
task generate:rules:cursor         # Generate Cursor rules to generated/cursor/rules/
task generate:rules:copilot        # Generate Copilot rules to generated/copilot/instructions/
task generate:rules:cline          # Generate Cline rules to generated/cline/
task generate:rules:universal      # Generate Universal rules to generated/universal/
task generate:rules:all            # Generate all IDE-specific rules (including universal)

# Optional DEST variable to change base output directory
task generate:rules:all DEST=/custom/output

# Validate rule structure (002-rule-governance.md v5.0 compliance)
task validate:rules         # Standard validation (fails on critical errors)
task validate:rules:verbose # Show all files including clean ones
task validate:rules:strict  # Strict mode (fail on warnings too)

# Boilerplate structural validation (deep validation with compliance scoring)
python3 scripts/validate_agent_rules.py --directory templates --check-boilerplate-structure
python3 scripts/validate_agent_rules.py --directory templates --check-boilerplate-structure --compliance-report

# Direct validation script usage
uv run python scripts/validate_agent_rules.py              # Standard validation
uv run python scripts/validate_agent_rules.py --verbose    # Verbose output
uv run python scripts/validate_agent_rules.py --fail-on-warnings  # Strict mode
uv run python scripts/validate_agent_rules.py --check-boilerplate-structure  # Deep validation
uv run python scripts/validate_agent_rules.py --check-boilerplate-structure --compliance-report  # With reports
uv run python scripts/validate_agent_rules.py --help       # Show all options

# Other validations
task --list              # Validate Taskfile syntax
uv run scripts/generate_agent_rules.py --source . --dry-run  # Test rule generation
```

### Utilities

```bash
task maintenance:clean:venv          # Remove virtual environment
task -l                  # List all available tasks
```

### Configuration Safety Guidelines

- **YAML Safety**: Avoid Unicode characters (bullets, checkmarks) that cause parsing errors
- **Shell Quoting**: Quote arguments with special characters: `".[dev]"` not `.[dev]`
- **Taskfile Validation**: Always test with `task --list` after YAML changes
- **Python Packaging**: Ensure `__init__.py` files exist before `uv pip install -e .`

### Testing Your Changes

Before submitting a PR, ensure your changes work correctly:

```bash
# 1. Regenerate all formats after editing templates
task generate:rules:all

# 2. Test rule generation (dry-run to preview)
task generate:rules:cursor:dry
task generate:rules:copilot:dry

# 3. Validate generated files are up-to-date
task generate:rules:cursor:check

# 4. Check for linting issues
task quality:lint

# 5. Validate formatting
task quality:format
```

**Important:** Always commit both the template changes AND the regenerated files:
```bash
git add templates/XXX-rule-name.md
git add generated/
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

**Location:** All rule files go in `templates/` directory.

Example: `templates/250-python-flask.md`

### Rule Structure

Each rule file (in `templates/`) must follow this structure:

```markdown
**Description:** Brief description of the rule's purpose
**Applies to:** `**/*.py`, `**/*.sql` (optional file patterns)
**Auto-attach:** false (optional, defaults to false)
**Version:** 1.0 (optional)
**Last updated:** 2024-01-15 (optional)

# Rule Title

## Key Principles
- Brief bullet points summarizing key concepts

## 1. Core Section
- **Requirement:** Must-do items
- **Always:** Best practices to follow
- **Rule:** Specific directives
- **Avoid:** Anti-patterns to prevent

## Documentation
- **Always:** Include links to official documentation
```

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

## 🔧 Rule Generator

The project includes `generate_agent_rules.py` that transforms universal Markdown rules into IDE-specific formats.

### Testing Generator Changes

```bash
# Test rule generation (dry run)
uv run generate_agent_rules.py --agent cursor --dry-run
uv run generate_agent_rules.py --agent copilot --dry-run

# Check if outputs are current
uv run generate_agent_rules.py --agent cursor --check
```

### Adding New IDE Support

To add support for a new IDE:

1. Extend the `AgentSpec` class in `generate_agent_rules.py`
2. Implement the IDE-specific header format
3. Add corresponding task in `Taskfile.yml`
4. Update the README compatibility matrix
5. Add tests and documentation

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
- [ ] **Run** `task quality:lint` and fix any issues
- [ ] **Run** `task quality:format` and ensure consistency
- [ ] **Test** rule generation with `task rule:cursor --dry-run`
- [ ] **Update** documentation if needed
- [ ] **Add** yourself to contributors if first contribution

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

# 2. Create template file in templates/
vim templates/450-terraform-best-practices.md

# 3. Add entry to discovery/RULES_INDEX.md
vim discovery/RULES_INDEX.md
# Add: | 450 | 450-terraform-best-practices | Terraform IaC best practices | terraform, iac, infrastructure |

# 4. Generate all formats
task generate:rules:all

# 5. Verify generation worked
ls -la generated/universal/450-terraform-best-practices.md
ls -la generated/cursor/rules/450-terraform-best-practices.mdc

# 6. Validate consistency
task generate:rules:cursor:check

# 7. Run quality checks
task quality:lint
task quality:format

# 8. Commit both template and generated files
git add templates/450-terraform-best-practices.md
git add discovery/RULES_INDEX.md
git add generated/
git commit -m "feat: add Terraform best practices rule

- Comprehensive Terraform IaC guidelines
- State management best practices
- Security and compliance patterns
- Resource naming conventions"

# 9. Push and create PR
git push origin feature/add-terraform-rules
```

### Updating an Existing Rule

```bash
# 1. Create feature branch
git checkout -b fix/update-python-core

# 2. Edit the template file (not generated files!)
vim templates/200-python-core.md
# Make your changes...

# 3. Regenerate all formats
task generate:rules:all

# 4. Verify changes propagated
git diff generated/universal/200-python-core.md
git diff generated/cursor/rules/200-python-core.mdc

# 5. Validate and test
task generate:rules:cursor:check
task quality:lint

# 6. Commit changes
git add templates/200-python-core.md generated/
git commit -m "fix: update Python core rule with type hints guidance"

# 7. Push and create PR
git push origin fix/update-python-core
```

### Common Mistakes to Avoid

❌ **Don't edit generated files directly**
```bash
vim generated/cursor/rules/200-python-core.mdc  # WRONG!
```

✅ **Always edit templates**
```bash
vim templates/200-python-core.md  # CORRECT
task generate:rules:all  # Then regenerate
```

❌ **Don't forget to regenerate**
```bash
git add templates/200-python-core.md
git commit  # WRONG - missing generated files!
```

✅ **Always regenerate and commit both**
```bash
task generate:rules:all
git add templates/200-python-core.md generated/
git commit  # CORRECT
```

❌ **Don't commit with stale generated files**
```bash
# Edit template but forget to regenerate
vim templates/200-python-core.md
git add templates/ generated/
git commit  # WRONG - generated files are stale!
```

✅ **Always validate before committing**
```bash
vim templates/200-python-core.md
task generate:rules:all  # Regenerate
task generate:rules:cursor:check  # Validate consistency
git add templates/ generated/
git commit  # CORRECT
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

For this to be effective, you should have a copy of this project repo `ai_coding_rules/` within your project directory, even if only temporarily to make changes to the rule file templates which are used to generate the final IDE-specific rule files. It is also important to verify that `002-rule-governance.md` is an actively selected rule in the project. It should be auto attached, but it never hurts to verify. This will ensure any rule changes will follow best practices and structure laid out for the `ai_coding_rules/` project.

Available LLMs are always evolving and improving in their capabilities. You should periodically ask your LLM of choice to review and make recommendations on rule improvements using the following prompt:

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

Thank you for helping make AI Coding Rules better for everyone! 🚀
