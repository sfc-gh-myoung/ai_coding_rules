**Description:** YAML and configuration file syntax best practices to prevent parsing errors and ensure reliability.
**AppliesTo:** `**/*.yml`, `**/*.yaml`, `**/pyproject.toml`, `**/.env*`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-09-10

# YAML and Configuration Best Practices

## Purpose
Establish safe YAML and configuration file practices to prevent parsing errors, ensure reliability, and maintain consistency across project configuration files including YAML, TOML, and environment files.

## 1. YAML Syntax Safety

### Critical Character Restrictions
- **Critical:** Avoid Unicode bullet characters (•, ✓, ★) in YAML strings as they cause parsing errors.
- **Critical:** Avoid using `-` or `:` at the start of multi-line text that could be interpreted as YAML syntax.
- **Critical:** Quote strings containing special characters: `description: "API docs at: http://localhost:8000/docs"`.
- **Always:** Use consistent indentation (2 spaces recommended for YAML).

### Safe String Formatting
```yaml
# Problematic - Unicode and YAML conflicts
cmds:
  - echo "• Item 1"
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
