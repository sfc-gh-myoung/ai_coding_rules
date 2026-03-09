# Markup and Configuration File Validation

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**Keywords:** YAML, configuration files, YAML syntax, parsing errors, indentation, anchors, aliases, Markdown, markdown linting, pymarkdownlnt, markup validation, TOML, environment files
**TokenBudget:** ~3500
**ContextTier:** Medium
**Depends:** None
**LoadTrigger:** ext:.yml, ext:.yaml, ext:.toml, file:Taskfile.yml

## Scope

**What This Rule Covers:**
Safe markup and configuration file practices to prevent parsing errors and maintain consistency across YAML, TOML, environment files, and Markdown documentation. Covers YAML syntax safety, quoting rules, indentation standards, shell command safety, Taskfile patterns, TOML validation, Markdown linting with pymarkdownlnt, and security considerations for configuration files.

**When to Load This Rule:**
- Writing or editing YAML configuration files
- Creating or modifying Taskfile.yml
- Troubleshooting YAML parsing errors
- Validating TOML configuration (pyproject.toml, etc.)
- Linting Markdown documentation
- Setting up configuration file validation
- Preventing secrets in version control
- Encountering "mapping values not allowed" errors

## References

### Dependencies

**Must Load First:**
- None (standalone rule)

**Related:**
- **202a-markdown-linting.md** - Markdown linting patterns and pymarkdownlnt configuration (Recommended)
- **203-python-project-setup.md** - pyproject.toml configuration
- **820-taskfile-automation.md** - Taskfile patterns

### External Documentation

- [YAML Specification](https://yaml.org/spec/) - Official YAML spec
- [yamllint](https://yamllint.readthedocs.io/) - YAML linter
- [pymarkdownlnt](https://github.com/jackdewinter/pymarkdown) - Markdown linter
- [TOML Specification](https://toml.io/) - TOML format spec

## Contract

### Inputs and Prerequisites

- Project configuration files (YAML, TOML, .env, Markdown)
- uv/uvx available for running linters
- Basic understanding of YAML/TOML syntax

### Mandatory

- **Quote YAML strings with colons** - `description: "API at: http://..."` prevents parsing errors
- **Avoid Unicode bullets in YAML** - Use ASCII characters only (-, *, +)
- **Consistent indentation** - 2 spaces for YAML, 4 for TOML
- **Validate before commit** - Run yamllint, check TOML parsing
- **No secrets in configs** - Use .env files with .gitignore
- **Never commit .env files** - Always add to .gitignore

### Forbidden

- Direct file modification without validation
- Unicode bullet/special characters in YAML structural contexts (i18n strings in values are valid)
- Secrets in version-controlled config files
- Inconsistent indentation
- Unquoted strings containing colons in YAML

### Execution Steps

1. Run appropriate linter for file type (yamllint, pymarkdownlnt, TOML validator)
2. Review errors and warnings
3. Fix issues following rule guidelines
4. Re-run validation to confirm
5. Document any rule exceptions with inline comments

### Output Format

Validation produces:
- Clean linter output with zero errors
- Properly formatted YAML, TOML, Markdown files
- Configuration files that parse successfully
- No secrets exposed in version control

### Validation

**Pre-Task-Completion Checks:**
- [ ] Ran yamllint on all modified YAML files
- [ ] Ran TOML validation on modified `.toml` files
- [ ] Ran pymarkdownlnt on modified Markdown files (or delegated to 202a)
- [ ] Verified no secrets present in committed config files
- [ ] Confirmed all config files parse without errors

**Success Criteria:**
- yamllint returns 0 errors
- TOML files parse without errors
- Markdown passes pymarkdownlnt checks
- No secrets detected in version control
- All config files load successfully

**Negative Tests:**
- Unquoted colons should trigger YAML parsing errors
- Unicode bullets should be flagged by linters
- Invalid TOML syntax should fail parsing

### Design Principles

- **Validation-first:** Run linters before committing config changes
- **Consistency:** Use standard indentation and formatting
- **Safety:** Quote strings, avoid Unicode, validate syntax
- **Security:** Never commit secrets or sensitive data
- **Automation:** Integrate linting into CI/CD pipelines

### Post-Execution Checklist

- [ ] All YAML strings with colons are properly quoted
- [ ] No Unicode characters used in YAML structural contexts
- [ ] Consistent indentation (2-space YAML, 4-space TOML) throughout
- [ ] .env files excluded via .gitignore; .env.example provided
- [ ] TOML arrays use consistent formatting
- [ ] Configuration documentation updated if structure changed

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

## Output Format Examples

```bash
# yamllint output (clean)
$ uvx yamllint config.yml
$

# yamllint output (errors)
$ uvx yamllint config.yml
config.yml
  3:1       error    wrong indentation: expected 2 but found 4  (indentation)
  7:12      error    too many spaces after colon  (colons)

# pymarkdownlnt output (clean)
$ uvx pymarkdownlnt scan README.md
No issues found.

# pymarkdownlnt output (errors)
$ uvx pymarkdownlnt scan README.md
README.md:5:1: MD022: Headings should be surrounded by blank lines [Expected: 1; Actual: 0]
README.md:12:81: MD013: Line length [Expected: 80; Actual: 120]
```

## YAML Syntax Safety

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

### yamllint Configuration

Create `.yamllint.yml` in project root for consistent YAML validation:

```yaml
extends: default
rules:
  line-length:
    max: 120
    allow-non-breakable-inline-mappings: true
  truthy:
    check-keys: false
  comments:
    min-spaces-from-content: 1
  indentation:
    spaces: 2
    indent-sequences: true
  document-start: disable
```

- **Always:** Run `uvx yamllint .` to validate all YAML files in a project
- **Rule:** Customize `.yamllint.yml` per project — disable `document-start` for Taskfiles, adjust `line-length` for readability

## Shell Command Safety in YAML

### Argument Quoting
- **Critical:** Quote shell arguments with brackets: `".[dev]"` not `.[dev]`
- **Critical:** Quote arguments with special characters: `"--cov-report=term-missing"`
- **Always:** Use double quotes for consistency in YAML context.

### Command Chaining
- **Consider:** Use `&&` for dependent commands: `cmd1 && cmd2`
- **Always:** Test complex shell commands outside YAML first.
- **Critical:** Escape quotes properly in nested contexts: `"echo \"Hello World\""`

## Taskfile-Specific Guidelines

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

## Configuration File Patterns

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

#### TOML Validation

Validate TOML files before committing to catch syntax errors early:

```bash
# Validate pyproject.toml using Python's built-in tomllib (3.11+)
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

# Validate any TOML file
python -c "import tomllib, sys; tomllib.load(open(sys.argv[1], 'rb'))" config.toml
```

**Common TOML errors:**
- Missing closing brackets in section headers: `[tool.ruff` should be `[tool.ruff]`
- Using single quotes for multi-line strings: use `"""triple quotes"""`
- Duplicate section headers: TOML forbids redefining the same table
- Incorrect array-of-tables syntax: use `[[tool.mypy.overrides]]` not `[tool.mypy.overrides]` for repeated sections

## Common Parsing Errors and Solutions

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

## YAML Anchors and Aliases

### Safe Patterns
```yaml
# Define anchor with &, reference with *
defaults: &defaults
  adapter: postgres
  host: localhost

development:
  <<: *defaults        # Merge anchor into mapping
  database: app_dev

production:
  <<: *defaults
  database: app_prod
  host: db.example.com  # Override specific keys
```

### Common Pitfalls
- **Critical:** Anchors must be defined before use — YAML is parsed top-to-bottom
- **Critical:** `<<: *anchor` only works for mappings, not sequences
- **Always:** Keep anchor definitions near the top of the file for readability
- **Never:** Use deeply nested anchor chains (A to B to C) -- they are hard to debug
- **Never:** Use anchors for secrets — the value is duplicated in memory and may appear in logs

## Documentation and Comments

### YAML Comments
- **Always:** Use `#` for comments in YAML files.
- **Always:** Document complex configurations with inline comments.
- **Consider:** Add header comments explaining file purpose.

### Configuration Documentation
- **Always:** Document required environment variables.
- **Always:** Provide example configurations.
- **Critical:** Document any non-obvious configuration interactions.

## Security Considerations

### Sensitive Data
- **Never:** Include secrets or passwords in configuration files.
- **Always:** Use environment variables for sensitive data.
- **Always:** Document required environment variables without exposing defaults.
- **Critical:** Use .gitignore to exclude sensitive configuration files.

### Configuration Validation
- **Always:** Validate configuration values at application startup.
- **Always:** Provide clear error messages for missing required configuration.
- **Consider:** Use configuration schemas for validation (e.g., Pydantic Settings).

## Markdown Linting

For Markdown linting patterns, tool configuration (pymarkdownlnt), and integration with Taskfile, see **202a-markdown-linting.md**.

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
