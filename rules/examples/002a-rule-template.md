# 002a Example: Rule Template v3.2 Structure (Markdown)

> **EXAMPLE FILE** - Reference implementation for `002a-rule-creation.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 002a-rule-creation.md
**Demonstrates:** Complete v3.2 rule file structure for creating new rules
**Use When:** Creating a new rule file from scratch
**Version:** 1.0
**Last Validated:** 2026-03-09

## Prerequisites

- Familiarity with rule schema v3.2
- Understanding of rule naming conventions (NNN-technology-aspect.md)

## Implementation

```markdown
# [NNN]-[technology]-[aspect]

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** [YYYY-MM-DD]
**Keywords:** [5-20 keywords here]
**TokenBudget:** ~[estimate]
**ContextTier:** [Critical|High|Medium|Low]
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
[1-2 sentence description of what this rule accomplishes]

**When to Load This Rule:**
- [Condition 1]
- [Condition 2]
- [Condition 3]

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules

**Related:**
- **[related-rule].md** - [Brief description]

### External Documentation

- **[Resource Name]:** [URL or path]

## Contract

### Inputs and Prerequisites
[Prerequisites here]

### Mandatory
[Required tools/libraries]

### Forbidden
[Prohibited actions]

### Execution Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Step 4]
5. [Step 5]

### Output Format
[Expected output description]

### Validation
**Pre-Task-Completion Checks:**
- [Check 1]

**Success Criteria:**
- [Criterion 1]

### Post-Execution Checklist
- [ ] Verification item 1
- [ ] Verification item 2

## Anti-Patterns and Common Mistakes
[Anti-patterns with code examples]
```

## Importance Markers

Add an importance marker after the title for foundation rules:

**When to use CORE FOUNDATION marker (domain cores only):**
- Rule name ends with `-core.md`
- Defines essential patterns for a technology domain
- Other rules in the domain depend on it

**When to use FOUNDATION marker (governance rules only):**
- Rule is in 002-series
- Defines rule creation/maintenance patterns
- Required for rule infrastructure work

**When to use no marker (most rules):**
- Standard specialized rules
- Can be summarized if context limits reached

## Validation

To verify the template was applied correctly:

```bash
# Validate the new rule file
uv run ai-rules validate rules/NNN-technology-aspect.md

# Expected output: 0 CRITICAL, 0 HIGH errors
```

**Checklist:**
- [ ] File name follows `NNN-technology-aspect.md` pattern
- [ ] All required sections present (Metadata, Scope, Contract, Anti-Patterns)
- [ ] SchemaVersion is v3.2
- [ ] Depends field references appropriate parent rules
- [ ] TokenBudget is within limits (500 advisory, 600 hard cap)
