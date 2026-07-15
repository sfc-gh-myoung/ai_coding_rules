---
schema_version: v3.5
rule_version: v1.0.0
last_updated: 2026-07-14
keywords:
  - kw:frontmatter fixture
  - kw:schema v3.5 sample
  - kw:dual-parse validation
  - kw:yaml frontmatter rule
  - kw:fixture reference
token_budget: ~450
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation rule required for every response
---

# 999-frontmatter-sample-fixture

## Scope

**What This Rule Covers:**
Minimal fixture demonstrating a valid v3.5 YAML-frontmatter rule file for schema-parser tests.

**When to Load This Rule:**
- Never — this file is a test fixture, not a production rule.
- Loaded by the schema validator test suite to confirm frontmatter parsing succeeds.

## References

### External Documentation
- Schema: `schemas/rule-schema.yml`
- Plan: `.snowflake/cortex/plans/rules-keyword-schema-loader-refactor-v5.md`

## Contract

### Inputs and Prerequisites
Schema validator installed and importable.

### Mandatory
YAML frontmatter block at top-of-file with required fields.

### Forbidden
Inline `**Field:**` metadata mixed with frontmatter in the same file.

### Execution Steps
1. Parse the YAML frontmatter fence at the top of the file.
2. Extract the seven metadata fields from the parsed YAML mapping.
3. Validate each field against its schema entry (pattern, enum, min/max).
4. Walk the remaining Markdown body for required sections.
5. Confirm the Contract subsections and step count meet spec.

### Output Format
Schema validator emits zero CRITICAL and zero HIGH findings for this fixture.

### Validation
`uv run ai-rules validate tests/fixtures/frontmatter_sample.md` exits 0.

### Post-Execution Checklist
- [ ] Frontmatter parsed as YAML mapping.
- [ ] All seven metadata fields resolved.
- [ ] Scope, References, and Contract sections validated.
- [ ] Zero CRITICAL findings reported.
- [ ] Zero HIGH findings reported.
