# Contributing to AI Coding Rules

Thank you for your interest in contributing to AI Coding Rules! This project provides universal AI coding rules for consistent, reliable software engineering across LLMs and IDEs.

## 🚀 Quick Start

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git
   cd ai_coding_rules
   ```
3. **Set up** the development environment:
   ```bash
   task deps:dev
   ```
4. **Create** a feature branch:
   ```bash
   git checkout -b feature/my-new-rule
   ```

## 📋 Development Workflow

### Environment Setup

We use modern Python tooling for consistent development:

- **Python 3.11+** - Language runtime
- **uv** - Fast Python package installer and resolver
- **Ruff** - Lightning-fast linting and formatting
- **Task** - Simple task runner for automation

```bash
# Install dependencies and set up environment
task deps:dev

# Run linting and formatting checks
task lint
task format

# Auto-fix issues
task lint:fix
task format:fix
```

### Testing Your Changes

Before submitting a PR, ensure your changes work correctly:

```bash
# Test rule generation
task rule:cursor --dry-run
task rule:copilot --dry-run

# Check for linting issues
task lint

# Validate formatting
task format
```

## 📝 Rule Authoring Guidelines

### File Naming Convention

Follow the established numbering system:

- **00-09**: Core foundation rules
- **10-19**: Data platform rules (Snowflake)
- **20-29**: Software engineering rules (Python)
- **30-39**: Data science and analytics
- **40-49**: Data governance
- **50-59**: Business intelligence
- **60-79**: Project management
- **80-89**: Demo and synthetic data

Use format: `XX-topic-description.md`

### Rule Structure

Each rule file must follow this structure:

```markdown
**Description:** Brief description of the rule's purpose
**Applies to:** `**/*.py`, `**/*.sql` (optional file patterns)
**Auto-attach:** false (optional, defaults to false)
**Version:** 1.0 (optional)
**Last updated:** 2024-01-15 (optional)

# Rule Title

## TL;DR
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
- [ ] **Run** `task lint` and fix any issues
- [ ] **Run** `task format` and ensure consistency
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

Thank you for helping make AI Coding Rules better for everyone! 🚀
