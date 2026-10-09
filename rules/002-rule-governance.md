---
schema_version: v4.0
rule_version: v5.0.0
description: "Authoring and validation contract for AI coding rules: v4 structure, typed discovery metadata, dependencies, safety requirements, and evidence."
last_updated: 2026-09-30
keywords:
  - kw:rule schema compliance
  - kw:metadata field requirements
  - kw:Contract Markdown subsections
  - kw:semantic discovery keywords
  - kw:ai-rules validate
  - kw:agent-first design priorities
  - dir:rules/
token_budget: ~1800
context_tier: Critical
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 002a-rule-creation.md  # Step-by-step guide for creating new rules
    - 002b-rule-update.md  # Updating and maintaining existing rules, versioning policy
    - 002e-schema-validator-usage.md  # Detailed validator commands, error interpretation, CI/CD integration
---
# Rule Governance: Schema Standards

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> Load when creating, reviewing, or maintaining rules.

## Scope

**What This Rule Covers:**
The v4 authoring contract for operational rules. Structural validation and semantic review are separate requirements.

**When to Load This Rule:**
- Create or update a rule, review its schema compliance, or change authoring guidance.
- For creation steps, read `002a-rule-creation.md`; for maintenance and versioning, read `002b-rule-update.md`.
- Companion examples use `schemas/example-schema.yml`, not the operational rule schema.

## Contract

### Inputs and Prerequisites

- Read the current `schemas/rule-schema.yml` and the rule being changed.
- Identify the intended task, existing rules covering it, dependencies, and available validation commands.
- Establish which files the user authorized you to change. Preserve unrelated edits.

### Mandatory

- Use YAML frontmatter for new and migrated rules. Set `schema_version: v4.0` only after migrating the body and reviewing semantic requirements.
- Keep required H2 sections in this order: Scope, Contract, References. Put the Contract early; the schema's placement limit is 200 lines with its configured allowance.
- Provide four non-empty Contract subsections: Inputs and Prerequisites, Mandatory, Execution Steps, Validation. Forbidden and Output Format are optional when they add distinct information.
- Keep one completion checklist under Validation. Move unique checks from duplicate checklists before removing them.
- State applicability once. Write conditions, actions, and observable outcomes. Specify recovery or escalation where failure affects correctness or safety.
- Preserve authorization, confidentiality, required reads, ownership-scoped recovery, and uncertain-outcome handling when shortening a rule.
- Use exact constraints from the product specification or project configuration. Label local policy and its rationale; do not invent numerical thresholds for subjective terms.
- Keep every operational `rules/*.md` file within 250 physical lines and at most three correct examples. Explain defects in prose, never an executable incorrect implementation. Add an example only for a distinct ambiguity; primary product documentation belongs in References.
- Keep required dependencies explicit and acyclic. Put shared constraints in their required owner; never remove a dependency merely to reduce tokens.
- Never skip validation or treat structural success as proof of behavioral equivalence. CRITICAL and HIGH findings block completion under the active schema.
- Use descriptive, unnumbered H2 headings and Markdown Contract subsections, not legacy XML tags. Keep rule prose free of emojis.

### Execution Steps

1. Read the schema and relevant dependency contracts. For a new rule, generate a scaffold with `uv run ai-rules new`; do not copy obsolete structures from existing files.
2. Fill metadata and the task-specific contract. Follow the metadata reference below and `002b-rule-update.md` for version changes.
3. Review each requirement for applicability, evidence, and an observable result. Preserve safety boundaries and map any moved instruction to its owner.
4. Validate the rule and related examples. Inspect each diagnostic rather than adding exemptions to make a gate pass.
5. Check discovery and plugin fidelity after changing metadata or content. Record changes under Unreleased in CHANGELOG.md. Commit or publish only when authorized.

### Validation

- [ ] The rule has valid frontmatter, a compliant filename, one H1, ordered H2 sections, and the four non-empty Contract subsections.
- [ ] `uv run ai-rules validate` on the changed rule reports zero CRITICAL and HIGH findings. Review lesser findings; report any remaining limitations.
- [ ] Version and date reflect the change; `token_budget` reflects a token estimate of the final text.
- [ ] Keywords remain within the combined 5-11 bound and match real task language; dependencies resolve and do not introduce cycles or lost required reads.
- [ ] `uv run ai-rules rule-loader validate`, `uv run ai-rules rule-loader validate-trigger-contract`, and `task plugin:verify` pass for the integrated change.
- [ ] Safety and behavior requirements survive review. Material instruction rewrites have the approved task-level comparison evidence; static checks alone do not establish equivalence.
- [ ] CHANGELOG.md describes the change, and no unrelated work was overwritten.

If a tool or schema is unavailable, report the missing path or dependency and the checks not run. Manual inspection can identify problems but is not a passing automated gate. Request needed access; do not elevate privileges or install tools without authorization.

## References

- `schemas/rule-schema.yml`: structural enforcement and the separately reviewed `authoring_contract` requirements.
- [CommonMark specification](https://spec.commonmark.org/): Markdown syntax and fenced-code behavior.
- `rules/examples/002-rule-governance-structure-example.md`: load when authoring a concrete v4 example.
- `002j-rule-examples.md`: load when creating or maintaining a companion example.

## Metadata reference

Required frontmatter fields, in order:

- `schema_version`: the schema target, `v4.0` for migrated rules.
- `rule_version`: semantic `vMAJOR.MINOR.PATCH`.
- `last_updated`: current change date as `YYYY-MM-DD`.
- `keywords`: 5-11 combined typed entries. Use `kw:` for task language, `ext:` for extensions, `file:` for filenames, and `dir:` for directories.
- `token_budget`: `~NUMBER`, based on the final text, not a size label or a line-count guess.
- `context_tier`: Critical, High, Medium, or Low.
- `depends`: `required` and `optional` filename lists, with short YAML comment justifications. An empty dependency set is valid for a foundation that has no prerequisites.

The optional description summarizes the rule. Inline legacy metadata remains readable during migration; do not reintroduce it in new rules. `LoadTrigger`, `## Metadata`, and a duplicate prose Dependencies section are not part of the canonical format.

Keep filenames in `<NNN>[<letter>]-<technology>-<aspect>.md` form: three digits, at most one lowercase suffix letter, and hyphenated lowercase words. Select the domain range from the current README category map rather than an old example list.

### Discovery and dependency ownership

Use specific keywords found in real task descriptions, not filler to reach the minimum. Avoid redundant variants and unrelated generic terms. The advisory mix of structural and semantic triggers is subordinate to the total bound and actual applicability; foundation rules may use semantic terms only.

The matcher reads current frontmatter. There is no separate index to regenerate. Keyword generation changes metadata; use it intentionally and inspect its diff before accepting it. Recheck recall and corpus-audit results after edits. Reconcile stale audit identities only after verifying the underlying reviewed decisions still apply.

Keep every required edge needed to interpret the rule. Optional references must name when to read them. Do not replace required edges with optional links to save space, duplicate dependencies in a second prose inventory, or claim a dependency-count limit that the active checks do not enforce.

## Formatting and review priorities

Use one H1, descriptive ATX headings, and fenced code with a language tag. The outer fence must be longer than any enclosed fence. Use consistent list markers and two-space indentation for nested bullets. Avoid indented code blocks and ambiguous separator syntax.

Prioritize correct agent execution and safety, then discovery reliability, then context efficiency and maintainability. Prefer the structure that communicates the requirement accurately; formatting policy is not proof of universal model limitations. Keep terminology consistent. Do not promise identical model behavior from deterministic matcher output.

Use importance markers according to `000-global-core.md`. When splitting a rule, retain its marker on the owning core; specialized children need not inherit a core marker. ContextTier provides priority metadata, not permission to drop required instructions.
