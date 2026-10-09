# Rule Schema v4 Documentation

`rule-schema.yml` defines structural validation for operational rules. The validator is `src/ai_rules/commands/validate.py`, exposed through `uv run ai-rules validate`.

## Enforcement boundaries

The active structural checks apply even to files declaring an older schema version. Legacy metadata parsing remains available during migration; it does not exempt a rule from section-order or non-empty-subsection checks.

The schema's `authoring_contract` block documents requirements for manual review. `SchemaValidator` does not enforce that block. Structural success therefore does not prove technical accuracy, semantic preservation, or agent behavior.

## V4 contract

Operational rules use YAML frontmatter followed by a title and these required H2 sections in order:

1. Scope: What This Rule Covers and When to Load This Rule.
2. Contract: four non-empty H3 subsections, Inputs and Prerequisites, Mandatory, Execution Steps, Validation.
3. References: relevant sources and task-conditioned references.

Forbidden and Output Format are optional when they add distinct requirements. The manual contract calls for one completion checklist under Validation, concise applicability, and correct executable examples only. Describe incorrect behavior in prose; do not require a fixed number of steps or examples.

Required safety, authorization, confidentiality, recovery, and required-read instructions remain active. Optional references cannot become their sole owner.

## Metadata

The seven required YAML fields are:

| Field | Meaning |
|---|---|
| `schema_version` | Target schema, v4.0 for new and migrated rules |
| `rule_version` | Semantic `vMAJOR.MINOR.PATCH` version |
| `last_updated` | Change date, `YYYY-MM-DD` |
| `keywords` | 5-11 combined typed entries: `kw:`, `ext:`, `file:`, `dir:` |
| `token_budget` | Tilde-prefixed token estimate, such as `~1200` |
| `context_tier` | Critical, High, Medium, or Low |
| `depends` | Required and optional filename lists with explanatory YAML comments |

`description` is optional. New rules do not use inline legacy metadata or duplicate dependency prose. Keep dependencies needed for correct execution in the required bucket, and keep required edges acyclic. A foundation without prerequisites can have an empty dependency set.

The matcher reads frontmatter directly; no separate discovery index is generated. Token estimates are not observed model usage. Preview with `ai-rules tokens --dry-run` before authorizing metadata updates.

## Commands

Run from the configured repository environment:

```bash
uv run --locked ai-rules validate rules/002-rule-governance.md --verbose
uv run --locked ai-rules validate rules/ --json
uv run --locked ai-rules validate rules/ --strict
uv run --locked ai-rules validate rules/examples/ --examples
uv run --locked ai-rules validate-skills skills/
```

CRITICAL and HIGH findings block normal rule validation. Strict mode additionally treats warnings as errors. Preserve the command's exit status and distinguish tool failure from content failure. A zero-file run is not evidence that the intended inventory passed.

Companion examples use `example-schema.yml`. Skill entrypoints use `skill-schema.yml`. Neither is validated as an operational rule. Use the corresponding entrypoint and inspect which files were actually checked.

## Migration and repair

For a schema migration, update governance, scaffolds, authoring guidance, examples, and the corpus together. Increment migrated rule versions according to the MAJOR-change policy in [002b-rule-update.md](../rules/002b-rule-update.md). Preserve history and deliberate legacy test fixtures.

Move complete sections rather than dropping their content to fix order. An empty required subsection needs meaningful content; another sibling heading does not populate it. Keep checks for wrong order and empty subsections as negative controls.

If a validator diagnostic appears incorrect, compare it with the active schema and create a minimal reproducer. Do not waive HIGH errors or relax the checker just to make a corpus migration pass. Missing tooling remains an explicit validation gap.

## References

- [Rule governance](../rules/002-rule-governance.md)
- [Rule creation](../rules/002a-rule-creation.md)
- [Validator usage](../rules/002e-schema-validator-usage.md)
- [Complete v4 example](../rules/examples/002-rule-governance-structure-example.md)
- [Contribution workflow](../CONTRIBUTING.md)
