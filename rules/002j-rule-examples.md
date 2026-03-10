# Rule Examples Guidelines

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> Extracted from 002-rule-governance.md for token efficiency.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2026-03-09
**Keywords:** rule examples, example files, example schema, reference implementations, example discovery, example validation
**TokenBudget:** ~1550
**ContextTier:** Medium
**Depends:** 002-rule-governance.md

## Scope

**What This Rule Covers:**
Guidelines for creating and maintaining validated example files that accompany complex rule files in the `rules/examples/` directory.

**When to Load This Rule:**
- Creating example files for complex rules
- Reviewing or maintaining existing examples
- Understanding example file structure and discovery

## References

### Dependencies

**Must Load First:**
- **002-rule-governance.md** - Parent rule for schema standards

**Related:**
- **002a-rule-creation.md** - Rule creation workflow

## Contract

### Inputs and Prerequisites

- A complex rule that needs companion examples
- Access to `rules/examples/` directory

### Mandatory

- Example files follow the lightweight schema below
- Example naming follows pattern: `{rule-number}-{topic}-{variant}-example.md`

### Forbidden

- Validating examples against `schemas/rule-schema.yml` (use `schemas/example-schema.yml` instead)

### Execution Steps

1. Determine if a rule needs examples (see criteria below)
2. Create example file using the template structure
3. Validate structure matches `schemas/example-schema.yml`
4. Verify discovery path matches naming convention

### Output Format

Markdown file in `rules/examples/` following the example schema.

### Validation

**Pre-Task-Completion Checks:**
1. Parent rule exists at `rules/{rule-number}-*.md`
2. `rules/examples/` directory is writable
3. Naming convention doesn't conflict with existing files (`ls rules/examples/{rule-number}-*`)

**Success Criteria:**
- Example file follows naming convention
- Example validates against `schemas/example-schema.yml`

**Negative Tests:**
- Example file missing Context section should fail validation
- Example file with wrong naming convention should be flagged
- Example file referencing non-existent parent rule should warn

### Error Recovery

- **Validation fails:** Fix reported errors in example structure and re-run validation:
  - **YAML snippets:** Run `python3 -c "import yaml; yaml.safe_load(open('file.yaml'))"` — must not raise
  - **JSON snippets:** Run `python3 -c "import json; json.load(open('file.json'))"` — must not raise
  - **Markdown:** Run `uv run ai-rules validate examples/<rule-name>-example.md` — exit code 0
  - **Code blocks:** Verify syntax highlighting language identifier matches content language
- **`example-schema.yml` not found:** Verify schema file exists at `schemas/example-schema.yml`
- **Example references non-existent parent rule:** Verify parent rule exists at `rules/{rule-number}-*.md`
- **Naming convention conflict:** Check existing files with `ls rules/examples/{rule-number}-*` and use a unique variant name

### Post-Execution Checklist

- [ ] Example file created in `rules/examples/`
- [ ] Naming follows `{rule-number}-{topic}-{variant}-example.md`
- [ ] Validated against `schemas/example-schema.yml`

## When Examples Are Needed

**Add examples for:**
- Configurations requiring >3 tools or >5 sequential steps
- Workflows with 4+ sequential steps (Semantic Views with VQRs). Shorter workflows (1-3 steps) can use inline examples without full sequence demonstration.
- Language-variant patterns (SQL DDL vs Python SDK)

**Skip examples for:**
- Rules with 3 or fewer inline code blocks totaling 30 lines or less
- Rules where all code examples are self-contained single-block snippets under 15 lines

## Example File Structure

Example files follow a lightweight schema different from rule files:

````markdown
# NNN Example: Topic (Language)

> **EXAMPLE FILE** - Reference implementation for `NNN-rule-name.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** NNN-rule-name.md
**Demonstrates:** What pattern this shows
**Use When:** Activation scenario
**Version:** 1.0
**Last Validated:** YYYY-MM-DD

## Prerequisites

- [ ] Requirement 1
- [ ] Requirement 2

## Implementation

```python
# Use appropriate language identifier: sql, python, yaml, bash, etc.
-- Complete, runnable code
```

## Validation

```bash
-- Verification commands
```

**Expected Result:** What success looks like
````

## Example Discovery

**For agents:** When loading a rule with complex patterns, check for companion examples:

```
rules/examples/NNN-topic-variant-example.md
```

Example naming follows pattern: `{rule-number}-{topic}-{variant}-example.md`

**Discovery:** Check `rules/examples/` for `{rule-number}-*-example.md` files.

## Example Validation

Example files are validated separately from rule files:

```bash
# Validate example structure against schema
uv run python -c "import yaml; yaml.safe_load(open('schemas/example-schema.yml').read())"

# Verify example file has required sections
grep -c '## Context\|## Prerequisites\|## Implementation\|## Validation' rules/examples/<example>.md
```

Examples are validated against `schemas/example-schema.yml`, not `schemas/rule-schema.yml`.

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Examples Without Context

**Problem:** Providing code examples without explaining when to use them.

```markdown
## Example
\`\`\`python
result = process(data)
\`\`\`
```

**Correct Pattern:**
```markdown
## Example: Processing User Input

**When to use:** When validating and transforming user-submitted data.

\`\`\`python
result = process(data)
\`\`\`
```

### Anti-Pattern 2: Inconsistent Example Naming

**Problem:** Example files that don't follow the naming convention.

```
# WRONG
my-example.md
example_rule.md
```

**Correct Pattern:**
```
# CORRECT: {rule-number}-{topic}-{variant}-example.md
002a-rule-creation-basic-example.md
101-streamlit-dashboard-example.md
```

## Example Staleness

Examples should be reviewed when:

1. **Parent rule updated:** If the parent rule's Contract section changes, verify examples
   still demonstrate current behavior (check `LastUpdated` dates)
2. **Schema version bump:** After any schema version change (v3.1 to v3.2), verify all examples
   use current metadata format
3. **Tool changes:** If referenced tools (`uv run ai-rules`, etc.) change flags or output
   format, update example output accordingly
4. **Quarterly check:** Review examples every 90 days for accuracy — add to project
   maintenance checklist

**Staleness indicators:**
- Example uses deprecated field names
- Example output format doesn't match current tool output
- Example references removed or renamed sections
