---
schema_version: v4.0
rule_version: v3.0.0
description: "Repair ambiguous agent-facing prose with explicit actions, meaningful structure, consistent terms, and positive examples."
last_updated: 2026-09-30
keywords:
  - kw:agent-optimized formatting
  - kw:ASCII table violations
  - kw:arrow character replacement
  - kw:imperative voice instructions
  - kw:visual diagram prohibition
  - kw:nested conditional lists
  - kw:mermaid
token_budget: ~850
context_tier: Medium
depends:
  required:
    - 002g-agent-optimization.md
    - 000-global-core.md
---
# Agent Instruction Formatting Repairs

> **REFERENCE RULE: LOAD WHEN NEEDED**

## Scope

**What This Rule Covers:**
Concrete repairs for unclear agent instructions. Apply the audience and evidence boundaries in `002g-agent-optimization.md`, not a universal ban on visual syntax.

**When to Load This Rule:**
- Review rules, prompts, or skill instructions with ambiguous actions or relationships.
- Do not apply rule-only constraints to human documentation or literal external tool output.

## Contract

### Inputs and Prerequisites

- Read the affected instructions, their required owners, and applicable formatting configuration.
- Identify the intended action or relationship before choosing a replacement structure.

### Mandatory

- Preserve the instruction's scope, condition, actor, action, and outcome when reformatting.
- State restrictions before the affected action. Do not bury authorization or error handling in an example.
- Prefer explicit labels over meaning conveyed only by alignment, proximity, or an unlabeled arrow.
- Keep one term for one concept while preserving distinctions such as estimates versus observed usage.
- Use imperative voice for instructions and positive executable examples. Explain the failure being avoided in prose.
- Preserve meaningful tabular relationships and real code/output syntax. Do not alter data merely to remove a character.
- Keep YAML frontmatter fences intact. Decorative separators are not a substitute for descriptive headings.

### Execution Steps

1. Describe the ambiguity in the existing instruction and identify the actual required behavior.
2. Select a concise structure that preserves that behavior: prose for a condition, numbered steps for order, or a list for independent requirements.
3. Apply the smallest rewrite and compare prerequisites, permissions, and outcomes with the original.
4. Run schema and Markdown checks, then inspect whether a reader can follow the action without guessing.

### Validation

- [ ] The rewrite preserves every unique requirement and does not invent a new action.
- [ ] Conditions and responsible actors are explicit; terminology remains consistent.
- [ ] Code, external output, and metadata were not corrupted by prose formatting changes.
- [ ] Validation passes and any unresolved meaning conflict is reported, not hidden behind a placeholder.

If the meaning cannot be preserved in the proposed format, retain the original relationship and flag it for review. Correct only task-owned changes after a failed check.

## References

- `002g-agent-optimization.md`: canonical audience scope and review priorities.
- `002-rule-governance.md`: v4 structure and semantic review requirements.

## Positive rewrite patterns

For an action whose actor was unclear:

```text
Log the validation error before returning the failure result.
```

For a prerequisite that must precede a read:

```text
Verify that the input file exists and is readable. If it is missing, report the path and stop before processing.
```

For a condition with distinct outcomes:

```text
If the file is valid, process it and report the result.
If validation fails, preserve the original file and report the diagnostics.
```

For independent option descriptions, use a list rather than alignment-only columns. For a relationship, name the verb: "depends on", "writes to", or "runs after". Use an actual branch only when the alternative changes the result.

A Markdown table can preserve genuine comparisons; a prose conversion that loses row/column relationships is not an improvement. Human-facing diagrams and directory trees remain valid where they help the intended reader. Formatting policy alone does not establish a model limitation.
