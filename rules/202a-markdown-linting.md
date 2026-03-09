# Markdown Linting

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Markdown, markdown linting, pymarkdownlnt, documentation, markup validation
**TokenBudget:** ~1950
**ContextTier:** Low
**Depends:** 202-markup-config-validation.md
**LoadTrigger:** ext:.md, kw:markdown, kw:pymarkdownlnt

## Scope

**What This Rule Covers:**
Markdown linting patterns, tool configuration, and integration for consistent documentation quality. Uses pymarkdownlnt as the primary Python-native linter.

**When to Load This Rule:**
- Linting Markdown documentation files
- Setting up pymarkdownlnt configuration
- Integrating Markdown linting into Taskfile or CI/CD
- Fixing Markdown formatting issues

## References

### Dependencies

**Must Load First:**
- **202-markup-config-validation.md** - Parent rule for markup and config validation

**Related:**
- **820-taskfile-automation.md** - Taskfile integration patterns

### External Documentation

- [pymarkdownlnt](https://github.com/jackdewinter/pymarkdown) - Python-native Markdown linter

## Contract

### Inputs and Prerequisites

- Markdown files (`.md`) in the project
- uv/uvx available for running pymarkdownlnt
- Parent rule 202 loaded for general config validation context

### Mandatory

- **Always:** Lint Markdown files before marking task complete
- **Always:** Use pymarkdownlnt via uvx for consistency with Python tooling
- **Always:** Fix all linting errors before committing
- **Rule:** Use Taskfile lint task if available; fall back to direct uvx invocation

### Forbidden

- Committing Markdown files with known linting errors without documented justification
- Using incompatible linter configurations across the project

### Execution Steps

1. Check if `Taskfile.yml` provides a Markdown lint task (`task lint-markdown` or similar)
2. If Taskfile task exists, run it; otherwise run `uvx pymarkdownlnt scan "**/*.md"`
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
- **Automation:** Integrate linting into CI and Taskfile workflows
- **Python-native:** Use pymarkdownlnt for ecosystem consistency with uv/uvx

### Post-Execution Checklist

- [ ] All Markdown files pass pymarkdownlnt
- [ ] Linter configuration committed to repository
- [ ] Taskfile integration added if project uses Taskfile

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

### Integration with Taskfile

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

### Pre-Task-Completion Validation

- **Rule (Taskfile-first):** If `Taskfile.yml` exists and provides a Markdown lint task (commonly `task lint`, `task check`, `task validate`, or `task lint-markdown`), run the project-defined task instead of invoking the tool directly.
- **Rule (fallback):** If no Taskfile task exists, run `uvx pymarkdownlnt scan "**/*.md"` after modifying Markdown files.
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

**Correct Pattern:** Always run `uvx pymarkdownlnt scan "**/*.md"` (or Taskfile equivalent) after modifying any Markdown file.

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

**Correct Pattern:** Only disable rules that genuinely conflict with project needs (e.g., `line-length` for files with long URLs). Keep all structural rules enabled.

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
