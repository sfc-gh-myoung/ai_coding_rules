---
schema_version: v4.0
rule_version: v5.0.0
description: "Create a v4 rule with a generated scaffold, task-specific instructions, discovery metadata, explicit dependencies, and validation evidence."
last_updated: 2026-09-30
keywords:
  - kw:rule creation workflow
  - kw:rule numbering ranges
  - kw:v3.4 schema compliance
  - kw:Contract Markdown subsections
  - kw:rule file naming convention
  - kw:metadata field setup
token_budget: ~1200
context_tier: High
depends:
  required:
    - 002-rule-governance.md  # Schema requirements and standards
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 002b-rule-update.md  # Updating and maintaining existing rules
    - 002e-schema-validator-usage.md  # Detailed validation commands and error resolution
    - 002c-rule-optimization.md  # Token budget optimization strategies
---
# Rule Creation Guide

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> Load when creating new rules.

## Scope

**What This Rule Covers:**
Create a discoverable v4 rule from the CLI scaffold. For an existing rule, use `002b-rule-update.md` instead.

**When to Load This Rule:**
- Assign a new rule name, populate its metadata, or write its initial contract.
- Use `rules/examples/002a-rule-template.md` when a concrete layout example is needed.

## Contract

### Inputs and Prerequisites

- A defined task and technology domain, with access to the current schema and existing rules.
- The `ai-rules new` and `ai-rules validate` commands in the project environment.
- Authorization to create the proposed file without overwriting another rule.

### Mandatory

- Check for an existing owner before adding a rule. Extend an existing rule if the new guidance fits its scope; separate distinct tasks without duplicating shared constraints.
- Choose a free number from the current README category map. Use `<NNN>[<letter>]-<technology>-<aspect>.md`; do not introduce multi-character suffixes.
- Generate the scaffold with `ai-rules new`. Replace placeholders before calling it production-ready. Existing files are reference material, not authority over the current schema.
- Follow `002-rule-governance.md` for metadata, section order, dependency ownership, formatting, and review requirements.
- Start `rule_version` at v1.0.0 and set `last_updated` to the creation date. Populate all seven required frontmatter fields.
- Use 5-11 combined typed keyword entries that describe real tasks. Preserve required reads in `depends.required`; give optional resources a load condition.
- Write only the procedure the task needs. Do not pad to a step count, repeat the scope, or duplicate the completion checklist.
- State safety restrictions directly; keep the operational file within 250 lines and at most three correct examples. Prefer focused best practices and relevant primary documentation; retain essential failure handling rather than hiding it in optional references.

### Execution Steps

1. Inspect neighboring rules and the current domain map. Resolve ownership and filename collisions before creating a file.
2. Run `uv run ai-rules new` with the chosen filename and context tier. Inspect the resulting YAML and Markdown.
3. Fill Scope, then the four required Contract subsections. Put References after Contract. Keep optional output guidance only when it adds a concrete requirement.
4. Replace generated keywords with specific typed entries or intentionally run the keyword command below. Inspect changes and resolve dependency references.
5. Estimate the final token count, validate the rule, check discovery, and verify the built plugin. Fix diagnostics before presenting the result.
6. Add an Unreleased changelog entry. Report the created path and executed checks; do not commit or publish without authorization.

### Validation

- [ ] The name is free, uses the correct domain range, and has at most one suffix letter.
- [ ] Frontmatter is complete, schema_version is v4.0, and no scaffold placeholders remain.
- [ ] Scope, Contract, References appear in order; each required Contract subsection has meaningful content.
- [ ] Safety boundaries, prerequisites, outputs, and failure handling are explicit without invented limits or unnecessary branches.
- [ ] `uv run ai-rules validate` reports zero CRITICAL and HIGH findings for the new rule.
- [ ] Discovery and trigger-contract checks pass, required dependencies are preserved, and `task plugin:verify` includes the new rule.
- [ ] Token estimate and changelog reflect the final content.

If file creation fails, report the path and error without changing permissions. If the validator is unavailable, report the unverified gate rather than claiming success. A conflicting existing file requires review, not an automatic `--force` retry.

## References

- `schemas/rule-schema.yml`: active v4 structure and authoring contract.
- `README.md`: current numbering categories.
- [CommonMark specification](https://spec.commonmark.org/): Markdown structure and fences.
- `002d-advanced-rule-patterns.md`: load for coupled multi-file changes and recovery.

## Command example

Replace the filename placeholder with an unused name before running these commands.

```bash
uv run ai-rules new <NNN-technology-aspect> --context-tier High
uv run ai-rules validate rules/<NNN-technology-aspect>.md --verbose
```

After filling the rule body, generate keyword suggestions only when a metadata update is intended:

```bash
uv run ai-rules rule-loader keywords run rules/<NNN-technology-aspect>.md --update
uv run ai-rules rule-loader validate
uv run ai-rules rule-loader validate-trigger-contract
task plugin:verify
```

Review generated metadata; these commands do not replace semantic review or authorize a commit.
