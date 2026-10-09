---
schema_version: v4.0
rule_version: v5.0.0
description: "Write agent-facing rules with explicit actions, consistent terminology, preserved safety requirements, and evidence-based formatting choices."
last_updated: 2026-09-30
keywords:
  - kw:agent-first design
  - kw:ASCII table prohibition
  - kw:imperative voice instructions
  - kw:sequential processing model
  - kw:terminology consistency enforcement
  - kw:arrow character replacement
  - kw:llm
token_budget: ~1100
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
    - 002-rule-governance.md  # Schema requirements and active standards
  optional:
    - 002a-rule-creation.md  # Step-by-step rule creation with agent optimization
    - 002c-rule-optimization.md  # Token budgets and performance
    - 002d-advanced-rule-patterns.md  # System prompt altitude and investigation-first
---
# Agent Optimization Principles

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**

## Scope

**What This Rule Covers:**
Make agent-facing instructions executable without relying on unstated context or sacrificing safety for shorter text.

**When to Load This Rule:**
- Write or review operational rules, prompts, skills, or injected instructions.
- Do not impose rule-only formatting restrictions on human-facing README, CONTRIBUTING, CHANGELOG, or docs pages.

## Contract

### Inputs and Prerequisites

- Read the target document, its audience, current schema, and required owners.
- Identify the actions, decisions, safety boundaries, and intended execution environment.
- Use representative tasks when judging behavioral effects of a rewrite.

### Mandatory

- Put critical prerequisites and restrictions before the action they constrain. Write actions in imperative voice and identify the responsible actor.
- Use consistent terms for the same concept and exact code identifiers for commands, fields, and paths. Do not force distinct concepts into one synonym.
- State the condition, required action, and observable result. Specify fallback where ambiguity affects safety or correctness; do not manufacture a branch for a harmless no-op.
- Use thresholds from specifications or project configuration. Label local defaults and rationale instead of inventing numbers to make a subjective term appear precise.
- Keep essential authorization, confidentiality, required reads, and recovery instructions in the active contract. Optional links cannot carry indispensable safety rules.
- Follow the v4 sections and four non-empty required Contract subsections. Use one completion checklist and positive executable examples only.
- Prefer lists for procedures and explicit relationships. Use Markdown structures that preserve meaning; formatting preference is repository policy, not proof that every model cannot read a table or diagram.
- Keep rules text-based. Reference necessary visual material rather than embedding binary content. Preserve real external output inside properly labeled code fences.
- Optimize context only after correctness and discovery. Deterministic selection does not establish deterministic model behavior.

### Execution Steps

1. Separate rule instructions from human documentation and quoted external formats.
2. Find vague actions, buried constraints, inconsistent terms, and duplicated requirements. Confirm the intended behavior before rewriting.
3. Rewrite the affected instructions with named inputs and outcomes. Retain useful distinctions and required dependency ownership.
4. Choose lists, prose, or a compact Markdown table according to the relationship being expressed and the applicable schema. Do not apply character bans to unrelated content.
5. Validate structure, inspect requirement preservation, and run the approved task comparisons for material behavior changes.

### Validation

- [ ] Instructions identify the action and actor, with prerequisites and safety limits stated first.
- [ ] Terms and identifiers are consistent without conflating different concepts.
- [ ] Every removed duplicate has a retained owner; no required instruction became optional.
- [ ] Formatting preserves relationships and respects the document's audience.
- [ ] Schema validation passes and behavior claims are limited to actual evaluation evidence.
- [ ] Token budgets use current estimates rather than claimed universal savings.

If a format conversion loses meaning, retain the meaningful structure and flag the conflict rather than adding a completion placeholder. For inconsistent terminology across owners, inspect their definitions and resolve the conflict before changing dependents. Restore only task-owned edits if a failed rewrite cannot be repaired.

## References

- `schemas/rule-schema.yml`: structural requirements and manual authoring contract.
- `002-rule-governance.md`: priority, metadata, and formatting policy.
- `002m-agent-format-antipatterns.md`: load for concrete instruction-rewrite examples.

## Audience and evidence boundaries

Mechanical Markdown lint applies according to the configured target. Rule-only checks do not automatically apply to human documentation. Tables, diagrams, directory trees, and arrows may be useful in human docs; do not report their presence as an agent-execution defect.

For agent instructions, replace an ambiguous arrow with a verb naming the relationship, such as "depends on" or "writes to". Replace a visual decision tree with explicit conditions when that makes the action clearer. Do not alter code, API responses, SQL results, or terminal output merely because they contain those characters.

Keep complete examples when they resolve a real ambiguity. An instruction such as "lint the code" loses necessary detail if the tool and scope are not otherwise defined; retain the verified project command rather than shortening away its meaning.
