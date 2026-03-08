# Rule Examples Guidelines

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> Extracted from 002-rule-governance.md for token efficiency.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-08
**Keywords:** rule examples, example files, example schema, reference implementations, example discovery, example validation
**TokenBudget:** ~1000
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
3. Validate with `task examples:validate`
4. Verify discovery path matches naming convention

### Output Format

Markdown file in `rules/examples/` following the example schema.

### Validation

**Success Criteria:**
- Example file follows naming convention
- Example validates against `schemas/example-schema.yml`

### Post-Execution Checklist

- [ ] Example file created in `rules/examples/`
- [ ] Naming follows `{rule-number}-{topic}-{variant}-example.md`
- [ ] Validated with `task examples:validate`

## When Examples Are Needed

**Add examples for:**
- Configurations requiring >3 tools or >5 sequential steps
- Multi-step configurations (Semantic Views with VQRs)
- Language-variant patterns (SQL DDL vs Python SDK)

**Skip examples for:**
- Rules with 3 or fewer inline code blocks totaling 30 lines or less
- Rules with inline code blocks that are sufficient

## Example File Structure

Example files follow a lightweight schema different from rule files:

```markdown
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

```sql|python|yaml
-- Complete, runnable code
```

## Validation

```bash
-- Verification commands
```

**Expected Result:** What success looks like
```

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
# Validate all examples
task examples:validate

# Validate examples (verbose)
task examples:validate:verbose
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
