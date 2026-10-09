# 002a Example: V4 Rule Template

> **EXAMPLE FILE** - Reference implementation for `002a-rule-creation.md`
> This companion documents the generator; it is not an operational rule.

## Context

**Parent Rule:** 002a-rule-creation.md
**Demonstrates:** Generate and populate a v4 rule scaffold
**Use When:** Creating a new rule without copying obsolete structure
**Version:** 3.0
**Last Validated:** 2026-09-30

## Prerequisites

- Read the parent rule and `schemas/rule-schema.yml`.
- Choose an unused filename in the correct domain range.
- Use the project's configured CLI and an authorized output directory.

## Implementation

Replace the filename placeholder before executing:

```bash
uv run ai-rules new <NNN-technology-aspect> --context-tier High
```

The generator emits YAML frontmatter with schema_version v4.0, rule_version v1.0.0, a current last_updated date, 5-11 typed keyword entries, token_budget, context_tier, and required dependencies. Replace generated content with task-specific requirements and measure the final token estimate.

The required body layout is:

```markdown
## Scope

**What This Rule Covers:**
State the task this rule governs.

**When to Load This Rule:**
- State the applicable task and exclusions.

## Contract

### Inputs and Prerequisites

Name the required inputs, permissions, and initial state.

### Mandatory

State task-specific constraints and preserve safety requirements not already owned by a required dependency.

### Execution Steps

1. Perform the required action after checking its prerequisite.
2. Verify the result and report failed or uncertain outcomes.

### Validation

- [ ] Record the actual check, expected result, and completion evidence.

## References

Link focused sources for external claims, or state None when no source applies.
```

This excerpt describes the body; it is not a complete standalone rule. For a complete synthetic rule, read `002-rule-governance-structure-example.md` in this directory.

Do not add a second completion checklist or a fixed number of examples. Preserve distinct prohibitions and output requirements under Mandatory, Validation, or an optional subsection. Show correct executable examples only.

Keep dependency justifications in YAML comments. Use the foundation/domain importance marker only when its documented role applies. Do not introduce inline legacy metadata or a prose Dependencies inventory.

## Validation

After replacing all scaffold placeholders, validate the generated rule:

```bash
uv run ai-rules validate rules/<NNN-technology-aspect>.md --verbose
```

Expected result: zero CRITICAL and HIGH findings. Review keyword relevance, dependency closure, token estimates, and technical accuracy separately; a scaffold can pass structural checks before its placeholders are meaningfully populated.

Validate this companion through the example entrypoint:

```bash
uv run ai-rules validate rules/examples/ --examples
```
