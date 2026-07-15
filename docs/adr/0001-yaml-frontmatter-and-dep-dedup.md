# ADR-0001: YAML Frontmatter Migration + Dependency Dedup Strategy

**Status:** Accepted
**Date:** 2026-07-13
**Deciders:** Michael Young
**Related plan:** `.snowflake/cortex/plans/rules-keyword-schema-loader-refactor-v5.md`

## Context

The `ai_coding_rules` project ships rule files under `rules/*.md` with an inline `## Metadata` block plus a duplicative `### Dependencies -> Must Load First / Related` prose subsection. The rule-loader skill greps `RULES_INDEX.md` (regenerated from rule metadata by `ai-rules index generate`) to discover rules per-request. Three structural weaknesses drive this ADR: (1) many `Keywords` values are over-broad (bare `snowflake`, `python`, `sql`) degrading discovery precision; (2) the human-prose `### Dependencies` subsection duplicates the machine-readable `**Depends:**` field, creating drift risk; (3) the inline `## Metadata` format diverges from the YAML frontmatter used by `SKILL.md` and plan-orchestrator agent files, forcing bespoke line-regex parsers in `src/ai_rules/commands/index.py` and blocking reuse of standard YAML tooling. Additionally the schema at `schemas/rule-schema.yml:373` currently CRITICAL-bans YAML frontmatter.

## Decisions

### D1 — Sequencing: A → C → B

**Rationale.** Track A (keyword audit; data-only, index-regenerated) is independent and low-risk. Track C (rule-loader second-pass validator; reads rule `Scope` sections) is stable under Track A's keyword-only edits, so running C after A validates the improved keywords before layering second-pass on top. Track B (schema migration; touches schema, validator, generator, and every rule file) is the highest-risk step and must land on a green A+C baseline. Executing B last freezes schema churn before the mass migration runs.

### D2 — Keyword bound: 5–7 `kw:` tokens per production rule

Every production rule (non-tombstone) carries exactly 5–7 `kw:` semantic tokens. Anchor allowlist (`kw:snowflake`, `kw:python`, `kw:sql`) is permitted only when co-occurring with ≥3 discriminating (compound, hyphenated, or domain-specific) tokens. Enforced via the `ai-rules keywords collisions` post-filter and Phase 0.5 acceptance gate.

### D3 — Version policy

- **Track A (keyword edits):** MINOR bump (`RuleVersion`). MAJOR only when a relied-upon `kw:` is dropped (grep the corpus for load-trigger references before dropping).
- **Track B (schema migration to YAML frontmatter):** MAJOR bump on every migrated rule file.
- **CHANGELOG entries:** batched per migration run; the migrator script is authoritative for the batch entry.

### D4 — Justification preservation: Option B (inline YAML comments)

When the human-prose `### Dependencies -> Must Load First / Related` subsection is removed in Track B, its justification text is preserved as inline YAML comments on the corresponding `depends:` entries in the new frontmatter. Example:

```yaml
depends:
  - required: 200-python-core.md  # foundation for all python tasks; version bumps track upstream
  - optional: 204-python-docs.md  # docstring conventions used when authoring new modules
```

**Sign-off:** Explicit ADR approval (this document).

### D5 — SchemaVersion drift acceptance

The migrator accepts both `v3.3` and `v3.4` inputs and normalizes to `v3.5` on write (Track B). Baseline audit: 120 rules at v3.3, 77 at v3.4, 1 at v3.1 (outlier — surface in Phase 2 migrator run). See `.workbench/baselines/pre-track-a/schema_version_audit.txt`.

### D6 — Production-scope exclusion: tombstones in exclude list

`002i-rule-loadtrigger.md` and any future `DEPRECATED TOMBSTONE` files are NOT deleted; they are listed in `.workbench/config/exclude_list.txt` and excluded from Track A/B gates and §14 acceptance criteria. Rationale: audit history and inbound-link safety. Baseline: 1 tombstone (002i); no actual inbound `required:` edges detected.

## Consequences

**Positive.** Discriminating keywords sharply improve rule-loader precision. YAML frontmatter reduces custom parser surface in `index.py` (`extract_metadata`) and `validate.py`. Dependency edges live in one canonical location.

**Negative / risk-mitigated.** Mass rule-file rewrite for Track B is a large diff; mitigated by dual-parse window and canary-then-mass migration. Removal of the `### Dependencies` prose loses the human-authored rationale text unless the Option-B inline-comment migration preserves it — the migrator MUST carry each Related/Must-Load-First bullet into the YAML comment for the corresponding `depends:` entry.

**Neutral.** `RULES_INDEX.md` F4 grammar is unchanged; only the input parser changes. Byte-identity gate defends this invariant.

## References

- Plan v5 §5, §5.4, §5.5 — architecture
- Plan v5 §12 Phase 0.5, Phase 2 — task breakdown
- `schemas/rule-schema.yml:373,391` — current `no_yaml_frontmatter` CRITICAL ban (must be reversed in Phase 2)
- `src/ai_rules/commands/index.py:88-156` — `extract_metadata` to rewrite
- `src/ai_rules/commands/keywords.py:718-750,1122-1160` — prompt + heuristic merge to refine
