# Markdown Linting

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.1
**LastUpdated:** 2026-03-26
**Keywords:** Markdown, markdown linting, pymarkdownlnt, documentation, markup validation
**TokenBudget:** ~2800
**ContextTier:** Low
**Depends:** 202-markup-config-validation.md
**LoadTrigger:** ext:.md, kw:markdown, kw:pymarkdownlnt

## Scope

**What This Rule Covers:**
Markdown linting patterns, tool configuration, and integration for consistent documentation quality. Uses pymarkdownlnt as the primary Python-native linter.

**When to Load This Rule:**
- Linting Markdown documentation files
- Setting up pymarkdownlnt configuration
- Integrating Markdown linting into project automation (Makefile, Taskfile, or CI/CD)
- Fixing Markdown formatting issues

## References

### Dependencies

**Must Load First:**
- **202-markup-config-validation.md** - Parent rule for markup and config validation

**Related:**
- **820-taskfile-automation.md** / **821-makefile-automation.md** - Build automation patterns

### External Documentation

- [pymarkdownlnt](https://github.com/jackdewinter/pymarkdown) - Python-native Markdown linter

## Contract

### Inputs and Prerequisites

- Markdown files (`.md`) in the project
- uv/uvx available for running pymarkdownlnt
- Pin pymarkdownlnt version in `pyproject.toml` for reproducibility:
  ```toml
  [project.optional-dependencies]
  dev = [
      "pymarkdownlnt>=0.9.20",
  ]
  ```
- In pre-commit (if used):
  ```yaml
  - repo: local
    hooks:
      - id: markdown-lint
        name: Markdown Lint
        entry: uvx pymarkdownlnt scan
        language: system
        types: [markdown]
  ```
- Parent rule 202 loaded for general config validation context

### Mandatory

- **Always:** Lint Markdown files before marking task complete
- **Always:** Use pymarkdownlnt via uvx for consistency with Python tooling
- **Always:** Fix all linting errors before committing
- **Rule:** Use the project's automation lint target if available; fall back to direct uvx invocation

### Forbidden

- Committing Markdown files with known linting errors without documented justification
- Using incompatible linter configurations across the project

### Execution Steps

1. Check if the project's automation entrypoint provides a Markdown lint target (e.g., `make lint-markdown`, `task lint-markdown`, or similar)
2. If an automation target exists, run it; otherwise run `uvx pymarkdownlnt scan "**/*.md"`
3. Review and fix reported issues
4. Re-run linter to confirm zero errors
5. Document any rule exceptions with inline configuration or comments

### Output Format

```bash
# pymarkdownlnt output (clean)
$ uvx pymarkdownlnt scan README.md
No issues found.

# pymarkdownlnt output (errors)
$ uvx pymarkdownlnt scan README.md
README.md:5:1: MD022: Headings should be surrounded by blank lines [Expected: 1; Actual: 0]
README.md:12:81: MD013: Line length [Expected: 80; Actual: 120]
```

### Validation

**Pre-Task-Completion Checks:**
- [ ] Ran pymarkdownlnt on all modified Markdown files
- [ ] All reported issues resolved or documented as exceptions
- [ ] Configuration file (`.pymarkdown` or `pymarkdown.json`) exists if project uses non-default rules

**Success Criteria:**
- pymarkdownlnt returns zero errors on all project Markdown files
- Consistent formatting across all documentation

**Negative Tests:**
- Missing blank lines around headings should be flagged
- Inconsistent heading hierarchy should be reported
- Bare URLs should trigger warnings

### Design Principles

- **Consistency:** Uniform Markdown formatting across all documentation
- **Automation:** Integrate linting into CI and project automation workflows
- **Python-native:** Use pymarkdownlnt for ecosystem consistency with uv/uvx

### Error Handling

**pymarkdownlnt not installed:**
```bash
# Always available via uvx — no installation needed
uvx pymarkdownlnt scan path/to/file.md

# If uvx fails, install directly
uv add --group dev pymarkdownlnt
uv run pymarkdownlnt scan path/to/file.md
```

**Common errors and fixes:**

- **MD001 (Heading levels should increment by one):** Ensure H2 follows H1, H3 follows H2
- **MD009 (Trailing spaces):** Configure editor to trim trailing whitespace
- **MD012 (Multiple blank lines):** Remove extra blank lines (max 1 between sections)
- **MD013 (Line length exceeded):** Wrap text or configure line_length in `.pymarkdown.yml`
- **MD033 (Inline HTML):** Replace with Markdown equivalent or disable for badges
- **MD041 (First line not heading):** Add `# Title` as first line, or disable for included files

**Bulk fix workflow:**
```bash
# Scan all Markdown files
uvx pymarkdownlnt scan docs/ README.md

# Fix specific file
uvx pymarkdownlnt --fix scan path/to/file.md

# Scan with specific config
uvx pymarkdownlnt -c .pymarkdown.yml scan .
```

### Post-Execution Checklist

- [ ] All Markdown files pass pymarkdownlnt
- [ ] Linter configuration committed to repository
- [ ] Automation integration added if project uses Makefile, Taskfile, or similar

## Tool: pymarkdownlnt (Python-Native)

**Rationale:** Python-native linter that integrates with existing `uv`/`uvx` tooling.

### Installation and Usage

```bash
# Check Markdown files using uvx (no installation required)
uvx pymarkdownlnt scan "**/*.md"

# Check specific files
uvx pymarkdownlnt scan README.md CHANGELOG.md CONTRIBUTING.md

# Check with configuration file
uvx pymarkdownlnt --config pymarkdown.json scan .
```

### Configuration

Create `.pymarkdown` or `pymarkdown.json` in project root:

**Recommended base configuration:**
```yaml
# .pymarkdown.yml
mode:
  strict-config: true

plugins:
  md013:
    line_length: 120
    code_blocks: false
    tables: false
  md033:
    allowed_elements: "br,img,details,summary,sup,sub"
  md024:
    siblings_only: true  # Allow same heading in different sections
```

**Rule project configuration (for Cursor/AI rule files):**
```yaml
plugins:
  md013:
    line_length: 150  # Rules contain long code examples
    code_blocks: false
    tables: false
  md033:
    enabled: false  # Rules may use HTML for formatting
  md041:
    enabled: false  # Rules start with blockquote, not heading
```

**JSON format alternative:**

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
- `first-line-heading`: Defaults by context:
  - **Documentation projects** (README, docs/): 80 characters line length (readable in terminals)
  - **Code-adjacent Markdown** (inline docs, comments): Match project's Python line length (typically 88 or 120)
  - **Rule files** (rules/*.md): 120 characters (accommodates code examples)
  - Configure in `.pymarkdown.yml`:
    ```yaml
    plugins:
      md013:
        line_length: 120  # Match your project standard
        code_blocks: false  # Don't enforce in code blocks
        tables: false       # Don't enforce in tables
    ```

### Integration with Project Automation

Add Markdown linting to the project's automation entrypoint. For implementation examples:
- **Taskfile:** See `820-taskfile-automation.md`
- **Makefile:** See `821-makefile-automation.md`

**Target names to define:** `lint-markdown` (check only), `lint-markdown-fix` (auto-fix), and include in the aggregate `lint` target.

Example direct invocations for automation scripts:

```bash
# Check only
uvx pymarkdownlnt scan "**/*.md"

# Auto-fix where possible
uvx pymarkdownlnt --fix scan "**/*.md"
```

### Pre-Task-Completion Validation

- **Rule (automation-first):** If the project provides an automation lint target (e.g., `make lint-markdown`, `task lint-markdown`), run the project-defined target instead of invoking the tool directly.
- **Rule (fallback):** If no automation target exists, run `uvx pymarkdownlnt scan "**/*.md"` after modifying Markdown files.
- **Rule:** Fix all Markdown linting errors before marking task complete.
- **Exception:** Only skip validation if user explicitly requests override.

## Common Markdown Issues

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

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Skipping Markdown Linting

**Problem:** Modifying documentation files without running pymarkdownlnt, leading to inconsistent formatting that accumulates over time. Heading hierarchy breaks; formatting issues make docs harder to read and maintain.

**Correct Pattern:** Always run `uvx pymarkdownlnt scan "**/*.md"` (or the project's automation equivalent) after modifying any Markdown file.

```bash
# Wrong: Edit markdown and commit without linting
vim README.md
git add README.md && git commit -m "update docs"

# Correct: Lint after editing, fix issues, then commit
vim README.md
uvx pymarkdownlnt scan README.md
# Fix any reported issues, then:
git add README.md && git commit -m "update docs"
```

### Anti-Pattern 2: Disabling All Rules Instead of Configuring

**Problem:** Setting most pymarkdownlnt rules to `enabled: false` rather than configuring sensible thresholds. Linter becomes useless; real issues go undetected.

**Correct Pattern:** Only disable rules when ALL of these conditions are met:
1. The rule violation is intentional (not accidental formatting)
2. Fixing the violation would degrade documentation quality or readability
3. The violation occurs in ≥5 files (systematic, not isolated)
4. The rule is documented as disabled in `.pymarkdown.yml` with a comment:
   ```yaml
   plugins:
     md033:  # Allow inline HTML for badges, collapsible sections
       enabled: false
   ```
- **Common valid disables:** MD033 (inline HTML for badges), MD013 in tables, MD041 (first-line heading in included files)
- **Never disable:** MD001 (heading increment), MD009 (trailing spaces), MD012 (blank lines)

```json
// Wrong: Disabling everything defeats the purpose
{
  "plugins": {
    "line-length": { "enabled": false },
    "no-inline-html": { "enabled": false },
    "heading-style": { "enabled": false },
    "no-trailing-spaces": { "enabled": false },
    "blanks-around-headings": { "enabled": false }
  }
}

// Correct: Only disable rules that conflict with project needs
{
  "plugins": {
    "line-length": { "enabled": false },
    "no-inline-html": { "enabled": false }
  }
}
```

## Alternative: markdownlint (Node.js)

**Note:** If the team prefers Node.js tooling, `markdownlint-cli2` is the industry standard.

```bash
# Install globally
npm install -g markdownlint-cli2

# Check files
markdownlint-cli2 "**/*.md"
```

**Rationale for pymarkdownlnt:** Consistency with existing Python/`uv` tooling ecosystem.
