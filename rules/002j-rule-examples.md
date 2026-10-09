---
schema_version: v4.0
rule_version: v3.0.0
description: "Create and maintain focused companion examples with prerequisites, correct implementations, explicit load conditions, and separate schema validation."
last_updated: 2026-09-30
keywords:
  - kw:rule examples
  - kw:example schema
  - kw:example-schema.yml
  - kw:example discovery
  - kw:reference implementations
  - kw:example staleness
token_budget: ~850
context_tier: Medium
depends:
  required:
    - 002-rule-governance.md  # Parent rule for schema standards
  optional:
    - 002a-rule-creation.md  # Rule creation workflow
---
# Rule Examples Guidelines

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**

## Scope

**What This Rule Covers:**
Provide companion examples that resolve a specific ambiguity without duplicating a rule's active contract.

**When to Load This Rule:**
- Create, review, or update a file in `rules/examples/`.
- Check examples after a parent contract, schema, or referenced tool changes.

## Contract

### Inputs and Prerequisites

- Read the parent rule and `schemas/example-schema.yml`.
- Identify the ambiguity or language/runtime variant the example must demonstrate.
- Confirm the target filename is available and the output directory is authorized.

### Mandatory

- Use the companion schema, not `schemas/rule-schema.yml`, for example files.
- Name new examples `{rule-number}-{topic}-{variant}-example.md` and link them from the parent with a load condition. Preserve existing referenced names unless a rename is approved.
- Include Context, Prerequisites, Implementation, and Validation. Identify the parent, demonstrated behavior, use condition, example version, and last validation date.
- Show correct code only. Specify inputs, setup, permissions, and expected outcomes. Label substitutions and unexecuted runtime assumptions explicitly.
- Keep essential safety instructions in the parent contract; optional examples cannot be their only owner.
- Add a companion only when it resolves a distinct ambiguity or keeps nonessential detail off the active read path. Do not pad to an example or step quota.
- Do not execute cloud, database, or destructive examples just to validate the Markdown. Obtain authorization for runtime verification separately.

### Execution Steps

1. Check existing companions and decide whether the needed example already exists.
2. Write the focused example with its parent, prerequisites, implementation, and verification instructions.
3. Validate the companion structure and syntax of applicable extracted snippets using tools appropriate to their language.
4. Verify parent links, filenames, and expected outcomes. Distinguish structural checks from runtime execution in the report.
5. Update the example version and validation date only to reflect work actually performed. Recheck the parent if its contract changed.

### Validation

- [ ] Parent and referenced local files exist; naming does not collide with another example.
- [ ] The parent names when to load the example and retains all essential safety requirements.
- [ ] `uv run ai-rules validate rules/examples/ --examples` reports no invalid examples.
- [ ] Snippets use matching language tags, valid nesting, clear substitutions, and complete prerequisites.
- [ ] Expected results are stated; runtime verification is either evidenced or explicitly unverified.

If a schema or parent is missing, report it before editing. If a filename conflicts, choose a distinct approved variant rather than overwrite. Fix structural or snippet errors and rerun the relevant check; parsing the schema YAML alone does not validate an example.

## References

- `schemas/example-schema.yml`: lightweight companion structure.
- `002-rule-governance.md`: v4 positive-example policy and required-owner safety constraints.

## Maintenance

Review companions when a parent's Contract changes, a schema migration changes demonstrated structure, or a referenced command changes. Compare actual current output before updating expected results. Deprecated field names, removed sections, and mismatched output are evidence of staleness; an old date alone is not proof of a defect.

Example validation is structural. Code syntax checks do not establish successful authenticated execution, correct business semantics, or safe behavior against production data. Report these limits rather than marking a full workflow validated after a Markdown check.
