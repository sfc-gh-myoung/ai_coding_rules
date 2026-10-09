# 002 Example: V4 Rule Governance Structure

> **EXAMPLE FILE** - Reference implementation for `002-rule-governance.md`
> Not an operational rule. Validate this wrapper with the example schema.

## Context

**Parent Rule:** 002-rule-governance.md
**Demonstrates:** A complete v4 rule with four meaningful Contract subsections
**Use When:** Checking the structure of a new or migrated operational rule
**Version:** 2.0
**Last Validated:** 2026-09-30

## Prerequisites

- Read `002-rule-governance.md` and the active rule schema.
- Save the embedded rule under an unused filename when testing it; do not overwrite a real rule.
- Use the project's configured `ai-rules` environment.

## Implementation

This synthetic rule demonstrates structure, not a new production workflow. Its dependency is the existing foundation rule.

```markdown
---
schema_version: v4.0
rule_version: v1.0.0
last_updated: 2026-09-30
keywords:
  - kw:rule validation
  - kw:validation result
  - kw:source preservation
  - kw:failure reporting
  - kw:read-only inspection
token_budget: ~350
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Shared authorization and validation requirements
---
# 999-example-rule: Inspect a Rule

## Scope

**What This Rule Covers:**
Inspect a supplied rule without modifying it.

**When to Load This Rule:**
- A user requests read-only rule validation.

## Contract

### Inputs and Prerequisites

- A readable rule path and the project validator.

### Mandatory

- Preserve the source file. Do not convert a validation request into authorization to repair it.
- Report missing inputs and failed checks rather than inventing success.

### Execution Steps

1. Read the supplied rule and run the configured validator on that file.
2. Report its exit code and diagnostics without applying changes.

### Validation

- [ ] The validator ran against the supplied path.
- [ ] The source is unchanged and all diagnostics are reported accurately.

## References

- `schemas/rule-schema.yml`: structure checked by the validator.
```

Forbidden and Output Format subsections are optional when needed. Keep unique restrictions in Mandatory and the completion checklist in Validation. Do not add an anti-pattern gallery or duplicate checklist solely to increase section count.

## Validation

Validate this companion wrapper separately:

```bash
uv run ai-rules validate rules/examples/ --examples
```

Extract the embedded Markdown into an unused temporary `.md` file, then pass that file to `uv run ai-rules validate`. Expected result: zero CRITICAL and HIGH findings, with required sections ordered Scope, Contract, References. Structural validation does not demonstrate that an agent followed the read-only behavior.
