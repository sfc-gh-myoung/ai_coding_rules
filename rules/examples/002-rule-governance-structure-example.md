# 002 Example: Rule Governance Structure (Markdown)

> **EXAMPLE FILE** - Reference implementation for `002-rule-governance.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 002-rule-governance.md
**Demonstrates:** Minimal and full rule structure examples
**Use When:** Creating or updating rule files
**Version:** v1.0.0
**Last Validated:** 2026-03-10

## Prerequisites

- [ ] Understanding of rule schema v3.2
- [ ] Familiarity with 002-rule-governance.md parent rule

## Implementation

### Minimal Rule Example

```markdown
# Rule Name

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-01-15
**Keywords:** keyword1, keyword2, keyword3, keyword4, keyword5
**TokenBudget:** ~1500
**ContextTier:** Medium
**Depends:** 000-global-core.md

## Scope
...

## Contract
...
```

### Full Rule Structure Example

```markdown
# Rule Name

## Metadata
[7 required fields]

## Scope
[What/When]

## References
[Dependencies/Related/External]

## Contract
[Inputs/Mandatory/Forbidden/Steps/Output/Validation]

## Key Principles
[Design guidance]

## Anti-Patterns
[Problem/Correct patterns]
```

## Validation

After creating a rule file:

```bash
# Validate rule structure against schema
uv run ai-rules validate rules/<your-rule>.md
```

**Expected Results:**
- All 7 required metadata fields present
- Scope section defines What and When
- Contract section includes at minimum Mandatory and Forbidden subsections
- No CRITICAL or HIGH severity validation errors
