# 002a Example: Rule Template v3.5 Structure (YAML frontmatter)

> **EXAMPLE FILE** - Reference implementation for `002a-rule-creation.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 002a-rule-creation.md
**Demonstrates:** Complete v3.5 rule file structure for creating new rules
**Use When:** Creating a new rule file from scratch
**Version:** 2.0
**Last Validated:** 2026-07-14

## Prerequisites

- Familiarity with rule schema v3.5 (YAML frontmatter canonical; inline dual-parse fallback still accepted)
- Understanding of rule naming conventions (NNN-technology-aspect.md)

## Implementation

```markdown
---
schema_version: v3.5
rule_version: v1.0.0
last_updated: [YYYY-MM-DD]
keywords:
  - kw:[semantic keyword one]
  - kw:[semantic keyword two]
  - ext:.[file extension]
  - file:[specific filename]
  - dir:[specific directory prefix]
token_budget: ~[estimate]
context_tier: [Critical|High|Medium|Low]
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns and validation gates
  optional:
    - [related-rule].md  # [Brief description of why this rule is optional context]
---

# [NNN]-[technology]-[aspect]

## Scope

**What This Rule Covers:**
[1-2 sentence description of what this rule accomplishes]

**When to Load This Rule:**
- [Condition 1]
- [Condition 2]
- [Condition 3]

## References

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

## Migration note (v3.4 → v3.5)

- The `## Metadata` H2 header is no longer required; a YAML frontmatter block at top-of-file replaces it.
- The `### Dependencies` prose subsection is no longer required; dependency data lives in the frontmatter `depends:` field with per-item YAML comment justifications (Option B — see the v5 refactor plan).
- Keywords count bound narrowed to **5-7** total typed entries (mix of `kw:`, `ext:`, `file:`, `dir:`). The old 5-25 range is retired.
- Inline `**Field:**` format is still accepted as a dual-parse fallback during migration, but new rules should use YAML frontmatter.

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
- [ ] YAML frontmatter block at top-of-file (or inline `**Field:**` fallback with `## Metadata` header for pre-v3.5 legacy rules)
- [ ] All required sections present (Scope, References with `### External Documentation`, Contract, optional Anti-Patterns)
- [ ] `schema_version: v3.5`
- [ ] `depends:` references appropriate parent rules with YAML comment justifications
- [ ] `token_budget` is within limits (500 advisory, 600 hard cap)
- [ ] `keywords:` contains 5-7 typed entries
