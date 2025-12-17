# Markup and Configuration File Validation

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** YAML, configuration files, YAML syntax, parsing errors, indentation, anchors, aliases, Markdown, markdown linting, pymarkdownlnt, markup validation, TOML, environment files
**TokenBudget:** ~2800
**ContextTier:** Medium
**Depends:** None

## Purpose
Establish safe markup and configuration file practices to prevent parsing errors, ensure reliability, and maintain consistency across YAML, TOML, environment files, and Markdown documentation.

## Rule Scope

Markup and configuration file validation best practices (YAML, TOML, environment files, Markdown)

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Quote YAML strings with colons** - `description: "API at: http://..."` prevents parsing errors
- **Avoid Unicode bullets in YAML** - Use ASCII characters only (-, *, +)
- **Consistent indentation** - 2 spaces for YAML, 4 for TOML
- **Validate before commit** - Run yamllint, check TOML parsing
- **No secrets in configs** - Use .env files with .gitignore
- **Never commit .env files** - Always add to .gitignore

**Quick Checklist:**
- [ ] All YAML files pass yamllint
- [ ] Strings with colons are quoted
- [ ] No Unicode characters in YAML values
- [ ] TOML arrays use consistent formatting
- [ ] .env files in .gitignore
- [ ] Markdown linted (if using pymarkdownlnt)
- [ ] All configs parse successfully

## Contract

<contract>
<inputs_prereqs>
Project files (YAML, TOML, .env, Markdown); `uv`/`uvx` available
</inputs_prereqs>

<mandatory>
`uvx pymarkdownlnt`, YAML parsers, TOML validators, IDE linters
</mandatory>

<forbidden>
Direct file modification without validation
</forbidden>

<steps>
1. Run appropriate linter for file type
2. Review errors and warnings
3. Fix issues following rule guidelines
4. Re-run validation to confirm
5. Document any rule exceptions
</steps>

<output_format>
Clean validation output with zero errors
</output_format>

<validation>
Run linters again to verify all issues resolved
</validation>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Inconsistent YAML Indentation**
```yaml
# Bad: Mixed 2-space and 4-space indentation
config:
  database:
      host: localhost  # 4 spaces
    port: 5432  # 2 spaces
  cache:
    enabled: true
```
**Problem:** Parsing errors; difficult to maintain; violates YAML specification; hard to spot visually.

**Correct Pattern:**
```yaml
# Good: Consistent 2-space indentation throughout
config:
  database:
    host: localhost
    port: 5432
  cache:
    enabled: true
```
**Benefits:** Predictable parsing; easy maintenance; follows YAML best practices; clear hierarchy.

**Anti-Pattern 2: Unquoted Strings with Special Characters**
```yaml
# Bad: Unquoted strings causing parsing issues
description: File contains: colons, [brackets], and {braces}
path: /home/user/*
```
**Problem:** Breaks YAML parsing; special characters treated as syntax; runtime failures; subtle bugs.

**Correct Pattern:**
```yaml
# Good: Properly quoted strings
description: "File contains: colons, [brackets], and {braces}"
path: "/home/user/*"
```
**Benefits:** Reliable parsing; explicit string boundaries; no special character conflicts; predictable behavior.

**Anti-Pattern 3: No Validation Before Deployment**
```bash
# Bad: Deploy config without validation
cp config.yml /etc/app/config.yml
systemctl restart app
```
**Problem:** Broken config deployed to production; service crashes; difficult rollback; downtime.

**Correct Pattern:**
```bash
# Good: Validate then deploy
uvx yamllint config.yml
python -c "import yaml; yaml.safe_load(open('config.yml'))"
# Only deploy if validation passes
cp config.yml /etc/app/config.yml
systemctl restart app
```
**Benefits:** Catch errors before deployment; prevent production outages; fast feedback; safe deployments.

## Post-Execution Checklist
- [ ] YAML files use consistent 2-space indentation
- [ ] Strings with special characters are properly quoted
- [ ] Taskfile syntax validated with `task --list`
- [ ] Environment files follow KEY=VALUE format
- [ ] TOML configuration uses proper section headers
- [ ] Markdown files pass `uvx pymarkdownlnt scan` with zero errors
- [ ] No secrets or sensitive data in configuration files
- [ ] Configuration validated at application startup
- [ ] Documentation includes setup and validation instructions

## Validation
- **Success checks:** All YAML files parse correctly; Taskfile syntax valid; TOML configuration loads without errors; Markdown files pass linting with zero errors; no parsing errors in any markup/config files
- **Negative tests:** Malformed YAML fails parsing; unquoted special characters cause errors; invalid TOML syntax detected; Markdown linting catches formatting issues; configuration with missing required values fails validation

## Output Format Examples

```python
# Investigation: Check current implementation
# Read existing files, understand patterns

# Implementation: Following uv + ruff + pytest standards
from typing import Protocol
from datetime import datetime, UTC

class ServiceProtocol(Protocol):
    """Clear contract for service implementations."""

    def process(self, data: dict) -> dict:
        """Process data following validation rules."""
        ...

def implementation_function(input_data: dict) -> dict:
    """
    Implement feature following project conventions.

    Args:
        input_data: Validated input following schema

    Returns:
        Processed result with metadata

    Raises:
        ValueError: If input validation fails
    """
    # Use datetime.now(UTC) not datetime.utcnow()
    timestamp = datetime.now(UTC)

    # Implement business logic
    result = {"status": "success", "timestamp": timestamp}
    return result

# Validation: Test the implementation
def test_implementation_function():
    """Test following AAA pattern."""
    # Arrange
    test_input = {"key": "value"}

    # Act
    result = implementation_function(test_input)

    # Assert
    assert result["status"] == "success"
    assert "timestamp" in result
```

```bash
# Validation commands
uvx ruff check .
uvx ruff format --check .
uv run pytest tests/
```

## References

### External Documentation
- [YAML Specification](https://yaml.org/spec/) - Official YAML specification and syntax reference
- [TOML Specification](https://toml.io/) - TOML format specification for configuration files
- [Python YAML Library](https://pyyaml.org/wiki/PyYAMLDocumentation) - PyYAML documentation for Python YAML processing
- [pymarkdownlnt Documentation](https://github.com/jackdewinter/pymarkdown) - Python-native Markdown linter documentation
- [Markdown Guide](https://www.markdownguide.org/) - Comprehensive Markdown syntax reference
- [CommonMark Specification](https://spec.commonmark.org/) - Official Markdown specification

### Related Rules
- **Python Core**: `rules/200-python-core.md`
- **Python Linting**: `rules/201-python-lint-format.md`
- **Project Setup**: `rules/203-python-project-setup.md`
- **Taskfile Automation**: `rules/820-taskfile-automation.md`
- **README Standards**: `rules/801-project-readme.md`

## 1. YAML Syntax Safety

### Critical Character Restrictions
- **Critical:** Avoid Unicode bullet characters (bullets, checkmarks, stars) in YAML strings as they cause parsing errors.
- **Critical:** Avoid using `-` or `:` at the start of multi-line text that could be interpreted as YAML syntax.
- **Critical:** Quote strings containing special characters: `description: "API docs at: http://localhost:8000/docs"`.
- **Always:** Use consistent indentation (2 spaces recommended for YAML).

### Safe String Formatting
```yaml
# Problematic - Unicode and YAML conflicts
cmds:
  - echo "- Item 1"
  - echo "- Sub-item"  # Conflicts with YAML list syntax

# Safe alternatives
cmds:
  - echo "* Item 1"
  - echo "  Sub-item"
  - echo "Item 1"
```

### Quote Usage Guidelines
- **Always:** Quote strings containing colons: `"Key: Value"`
- **Always:** Quote strings with leading/trailing spaces: `"  Indented text  "`
- **Always:** Quote strings with special shell characters: `"command --flag=\"value\""`
- **Critical:** Use double quotes for strings containing variables: `"{{.VARIABLE}}"`

## 2. Shell Command Safety in YAML

### Argument Quoting
- **Critical:** Quote shell arguments with brackets: `".[dev]"` not `.[dev]`
- **Critical:** Quote arguments with special characters: `"--cov-report=term-missing"`
- **Always:** Use double quotes for consistency in YAML context.

### Command Chaining
- **Consider:** Use `&&` for dependent commands: `cmd1 && cmd2`
- **Always:** Test complex shell commands outside YAML first.
- **Critical:** Escape quotes properly in nested contexts: `"echo \"Hello World\""`

## 3. Taskfile-Specific Guidelines

### Silent Mode Usage
- **Always:** Add `silent: true` to tasks with multiple echo statements.
- **Always:** Use `silent: true` for tasks that provide user-friendly output.
- **Critical:** Tasks with informational echo commands should be silent to prevent verbose output.

### Variable Usage
- **Always:** Use `{{.VARIABLE}}` syntax for Taskfile variables.
- **Always:** Define variables in `vars:` section at top level.
- **Critical:** Quote variable expansions in shell contexts: `"{{.APP_MODULE}}"`

### Task Dependencies
- **Always:** Use `deps: [task1, task2]` for task dependencies.
- **Always:** Use `preconditions:` for environment checks.
- **Critical:** Test dependency order to avoid circular dependencies.

## 4. Configuration File Patterns

### Environment Files (.env)
- **Always:** Use KEY=VALUE format without spaces around `=`.
- **Always:** Quote values with spaces: `DATABASE_URL="postgresql://user:pass@host/db"`
- **Never:** Include .env files in version control.
- **Always:** Provide .env.example template.

### TOML Configuration (pyproject.toml)
- **Always:** Use proper TOML section headers: `[tool.ruff.lint]`
- **Always:** Group related configurations logically.
- **Always:** Use arrays for multiple values: `select = ["E", "W", "F"]`
- **Reference:** See `201-python-lint-format.md` for complete Ruff configuration patterns.

## 5. Common Parsing Errors and Solutions

### YAML Parsing Issues
1. **"mapping values are not allowed"**: Usually caused by unquoted colons in strings.
   - Fix: Quote the entire string containing colons.

2. **"found undefined alias"**: Often caused by special characters.
   - Fix: Quote strings with special characters.

3. **"could not find expected"**: Usually indentation issues.
   - Fix: Use consistent 2-space indentation.

### Shell Escaping Issues
1. **"no matches found"**: Shell glob expansion issues.
   - Fix: Quote arguments with brackets or wildcards.

2. **"command not found"**: Variable expansion issues.
   - Fix: Use proper `{{.VARIABLE}}` syntax and quote expansions.

## 6. Validation and Testing

### YAML Validation
- **Always:** Test YAML syntax after changes: `task --list` for Taskfiles.
- **Always:** Use YAML linters in CI/CD pipelines.
- **Consider:** Use IDE extensions for real-time YAML validation.

### Configuration Testing
- **Always:** Test configuration loading in application startup.
- **Always:** Validate environment variable parsing.
- **Critical:** Test configuration with different environments (dev, test, prod).

## 7. Documentation and Comments

### YAML Comments
- **Always:** Use `#` for comments in YAML files.
- **Always:** Document complex configurations with inline comments.
- **Consider:** Add header comments explaining file purpose.

### Configuration Documentation
- **Always:** Document required environment variables.
- **Always:** Provide example configurations.
- **Critical:** Document any non-obvious configuration interactions.

## 8. Security Considerations

### Sensitive Data
- **Never:** Include secrets or passwords in configuration files.
- **Always:** Use environment variables for sensitive data.
- **Always:** Document required environment variables without exposing defaults.
- **Critical:** Use .gitignore to exclude sensitive configuration files.

### Configuration Validation
- **Always:** Validate configuration values at application startup.
- **Always:** Provide clear error messages for missing required configuration.
- **Consider:** Use configuration schemas for validation (e.g., Pydantic Settings).

## 9. Markdown Linting

### Purpose
Markdown linting ensures consistent syntax, formatting, and structure across all project documentation files.

### Tool: pymarkdownlnt (Python-Native)

**Rationale:** Python-native linter that integrates with existing `uv`/`uvx` tooling.

#### Installation and Usage
```bash
# Check Markdown files using uvx (no installation required)
uvx pymarkdownlnt scan "**/*.md"

# Check specific files
uvx pymarkdownlnt scan README.md CHANGELOG.md CONTRIBUTING.md

# Check with configuration file
uvx pymarkdownlnt --config pymarkdown.json scan .
```

#### Configuration

Create `.pymarkdown` or `pymarkdown.json` in project root:

```json
{
  "plugins": {
    "line-length": {
      "enabled": false
    },
    "no-inline-html": {
      "enabled": false
    }
  }
}
```

**Common rules to adjust:**
- `line-length`: Often disabled for long links and code blocks
- `no-inline-html`: Often disabled for badges and advanced formatting
- `first-line-heading`: Project-dependent (may require H1 as first line)

#### Integration with Taskfile

Add Markdown linting tasks to `Taskfile.yml`:

```yaml
lint-markdown:
  desc: "Lint Markdown files with pymarkdownlnt"
  cmds:
    - uvx pymarkdownlnt scan "**/*.md"

lint-markdown-fix:
  desc: "Lint Markdown files with auto-fix where possible"
  cmds:
    - uvx pymarkdownlnt --fix scan "**/*.md"

lint:
  desc: "Run all linting checks"
  cmds:
    - task: lint-ruff
    - task: lint-markdown
```

#### Pre-Task-Completion Validation

**CRITICAL:** Markdown linting is part of the Pre-Task-Completion Validation Gate.

- **Rule (Taskfile-first):** If `Taskfile.yml` exists and provides a Markdown lint task (commonly
  `task lint`, `task check`, `task validate`, or `task lint-markdown`), run the project-defined task
  instead of invoking the tool directly.
- **Rule (fallback):** If no Taskfile task exists, run `uvx pymarkdownlnt scan "**/*.md"` after
  modifying Markdown files
- **Rule:** Fix all Markdown linting errors before marking task complete
- **Exception:** Only skip validation if user explicitly requests override

#### Common Markdown Issues

1. **Inconsistent heading hierarchy**: H1 to H3 without H2
   - Fix: Use proper heading levels (H1, then H2, then H3)

2. **Missing blank lines**: No blank line before/after headings or code blocks
   - Fix: Add blank lines for readability

3. **Trailing spaces**: Unnecessary spaces at end of lines
   - Fix: Remove trailing whitespace

4. **Inconsistent list formatting**: Mixed bullet styles or indentation
   - Fix: Use consistent list markers and 2-space indentation

5. **Bare URLs**: URLs not wrapped in angle brackets or link syntax
   - Fix: Use `<https://example.com>` or `[text](https://example.com)`

### Alternative: markdownlint (Node.js)

**Note:** If team prefers Node.js tooling, `markdownlint-cli2` is the industry standard.

```bash
# Install globally
npm install -g markdownlint-cli2

# Check files
markdownlint-cli2 "**/*.md"
```

**Rationale for pymarkdownlnt:** Consistency with existing Python/`uv` tooling ecosystem.

## Validation Results

**Files Checked:**
- YAML: [list]
- TOML: [list]
- Markdown: [list]

**Issues Found:** [count]

**Actions Taken:**
1. [Fix description]
2. [Fix description]

**Validation Passed:** /
```

> **Investigation Required**
> When applying this rule:
> 1. **Read existing config files BEFORE making changes** - Check current YAML/TOML structure, indentation style
> 2. **Verify what validation tools are available** - Check for yamllint, toml parsers in project
> 3. **Never assume config structure** - Read files to understand existing patterns
> 4. **Check for existing validation tasks** - Look in Taskfile.yml for lint tasks
> 5. **Test config changes** - Parse files after modifications to ensure they're valid
>
> **Anti-Pattern:**
> "Adding YAML config... (without checking existing indentation)"
> "This should be valid... (without testing)"
>
> **Correct Pattern:**
> "Let me check your existing YAML configuration first."
> [reads file, checks indentation, validates structure]
> "I see you use 2-space indentation. Adding the new config section following this pattern..."
