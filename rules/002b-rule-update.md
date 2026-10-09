---
schema_version: v4.0
rule_version: v3.0.0
description: "Update existing rules with semantic versioning, current dates, preserved safety and dependency requirements, scoped recovery, and validation evidence."
last_updated: 2026-09-30
keywords:
  - kw:rule versioning
  - kw:RuleVersion increment
  - kw:LastUpdated field
  - kw:rule modification workflow
  - kw:MAJOR MINOR PATCH semantics
  - kw:schema migration checklist
token_budget: ~1400
context_tier: High
depends:
  required:
    - 002-rule-governance.md  # Schema requirements and standards
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 002a-rule-creation.md  # Creating new rules from scratch
    - 002e-schema-validator-usage.md  # Validation commands and error resolution
    - 002c-rule-optimization.md  # Token budget optimization
---
# Rule Update and Maintenance Guide

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> Load when updating, modifying, or maintaining existing rules.

## Scope

**What This Rule Covers:**
Change an existing rule without losing its requirements, discovery behavior, or change history. Create a separate rule when the new task has a distinct owner or scope.

**When to Load This Rule:**
- Change rule content, metadata, examples, schema version, or dependencies.
- Decide whether a change requires a MAJOR, MINOR, or PATCH rule version.

## Contract

### Inputs and Prerequisites

- Read the current file, `schemas/rule-schema.yml`, and its required dependencies.
- Inspect the worktree and index for pre-existing edits; capture a beforeimage of the authorized file state.
- Identify intended behavior changes and available validation commands before editing.

### Mandatory

- Change only the requested behavior and necessary references. Preserve unrelated edits and unique safety, authorization, recovery, and required-read instructions.
- Increment `rule_version` for a rule modification and update `last_updated` to the current date. Use the policy below; a schema migration is a MAJOR change.
- Update YAML frontmatter in place. Do not reintroduce inline legacy metadata or a duplicate prose dependency inventory.
- Preserve keywords unless discovery changes are intentional. Keep the combined 5-11 bound and inspect keyword-generator output before accepting it.
- Recalculate `token_budget` when content changes. Use a tokenizer estimate, not a line count, and label estimates accurately.
- Require zero CRITICAL and HIGH validation findings. Do not bypass checks or describe an unexecuted check as passed.
- Record the change under Unreleased in CHANGELOG.md. Updating a rule does not authorize a commit, branch, push, or publication.

### Execution Steps

1. Read the complete rule and compare its current bytes with the captured baseline. Resolve conflicting concurrent changes before writing.
2. Identify the smallest content change and its version increment. For structural migrations, map old safety and behavioral requirements to their new locations.
3. Edit the rule, then update its version and date. Keep dependencies and discovery terms unchanged unless explicitly part of the correction.
4. Check the final token estimate and update its budget. Validate the changed rule and any coupled examples.
5. Run discovery, trigger-contract, and plugin checks. Inspect audit reconciliation when content hashes invalidate existing dispositions.
6. Update the changelog and report the changed paths, behavior, checks, and limitations. Leave source-control operations to the user's authorization.

### Validation

- [ ] The filename and scope remain appropriate; distinct new domains have not been folded into an unrelated rule.
- [ ] Version increment matches the change and last_updated reflects this revision.
- [ ] Every old safety and required-read constraint is preserved or corrected with explicit evidence.
- [ ] Metadata parses, the keyword bound holds, and the final token estimate is recorded.
- [ ] `uv run ai-rules validate` on the changed rule returns zero CRITICAL and HIGH findings.
- [ ] Coupled example validation, loader recall, trigger-contract checks, and plugin verification pass.
- [ ] CHANGELOG.md describes the change and any compatibility impact.
- [ ] Existing staged and concurrent work is preserved; no unauthorized commit or publication occurred.

## References

- `schemas/rule-schema.yml`: active v4 structure and validation severities.
- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html): version meaning; the mapping to rule contracts below is repository policy.
- `002a-rule-creation.md`: load when the change belongs in a new rule.
- `002e-schema-validator-usage.md`: load to diagnose a failed validation command.

## Rule versioning policy

Use `vMAJOR.MINOR.PATCH`:

- MAJOR: schema upgrades, removed or renamed required sections, incompatible execution changes, removed mandatory tools or dependencies, or removed discovery terms that callers rely on.
- MINOR: new guidance, meaningful examples, new keywords, wider applicability within the same scope, or optional subsections that preserve existing behavior.
- PATCH: spelling, formatting, corrected links, token-budget corrections, or schema-conformance repairs that do not change the contract.

For example, migrating a v2.5.0 rule to the v4 schema makes its rule version v3.0.0. Adding an optional example to v3.0.0 makes it v3.1.0. Correcting a typo in v3.1.0 makes it v3.1.1. A published version number is not reused after a rollback.

## Schema migration

Move the rule to Scope, Contract, References and set schema_version to v4.0 after reviewing the body. Provide four non-empty required Contract subsections. Consolidate completion checks under Validation and preserve any distinct Forbidden or Output Format content where it remains useful.

Keep YAML dependency comments, required/optional classifications, and typed discovery entries. Replace negative executable examples with correct code and explain the avoided failure in prose. Do not pad steps or invent numerical limits to make language look precise.

For a multi-file migration, capture baseline diagnostics and expected changes before each batch. Run the approved behavioral pilot before wider instruction rewrites. A schema pass alone is not a semantic migration sign-off.

## Recovery and concurrent changes

On validation failure, retain the diagnostic and fix the affected change. If reverting your edits is necessary, restore only your own changes from the beforeimage. Do not restore an old commit over another author's work or reuse a published version.

If a file changed after you read it, re-read it before patching. Preserve compatible edits; ask about conflicting intent rather than selecting whichever version sounds more specific. Revalidate the combined result and document any revert in the changelog. Do not create branches or perform destructive Git operations without authorization.
