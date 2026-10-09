# Rule Loader Manifest Contract Reference

After the v3 cutover, rule discovery uses three layered stages with distinct schemas.
See `skills/shared/runtime-capabilities.md` for runtime vocabulary.

## Stage 1 — Matcher artifact (`rule-loader-matcher/v1`)

The deterministic output of `match_rules.py`. Scans YAML frontmatter from
`rules/` directly; contains no agent-authored or runtime fields.

**Required fields:** `schema_version`, `candidate_rules`, `load_sequence`, `deferred_rules`.

Each `candidate_rules` and `load_sequence` entry:

```json
{
  "rule_path": "rules/<filename>.md",
  "layer": "HARD | SOFT",
  "context_tier": "Critical | High | Medium | Low",
  "description": "one-line description (optional)",
  "token_budget": 2600
}
```

Each `deferred_rules` entry:

```json
{
  "rule_path": "rules/<filename>.md",
  "reason": "entry_cap | token_budget"
}
```

**Completeness invariant:** every `candidate_rules[*].rule_path` appears in exactly one
of `load_sequence[*].rule_path` or `deferred_rules[*].rule_path`.

**Schema file:** `schemas/rule-loader-matcher-v1.schema.json`

## Stage 2 — Semantic briefing (`rule-loader-semantic-briefing/v1`)

Input to the semantic worker. Binds the briefing to the matcher artifact SHA-256,
includes at most eight bounded SOFT candidate excerpts, enumerates HARD passthrough
rules, and supplies retry and unsupported-runtime behavior.

**Schema file:** `schemas/rule-loader-semantic-briefing-v1.schema.json`

## Stage 3 — Semantic result (`rule-loader-semantic/v1`)

Output of the semantic worker. Contains a `selected` decision for every SOFT
candidate in the briefing scope. Must not contain runtime-attestation fields.

**Schema file:** `schemas/rule-loader-semantic-v1.schema.json`

## Stage 4 — Final manifest (`rule-loader-manifest/v3`)

Coordinator-owned output. Attaches runtime evidence and produces the final
load/defer partition. `load_sequence` is a list of strings (rule paths);
HARD paths lead in briefing order.

**Required fields:** `schema_version`, `matcher_sha256`, `scope_sha256`,
`load_sequence`, `deferred_rules`, `runtime_evidence`.

**Schema file:** `schemas/rule-loader-manifest-v3.schema.json`

## Legacy schemas (rejected)

`rule-loader-manifest/v1` and `rule-loader-manifest/v2` are unsupported. Any input
with these schema versions is rejected with `"unsupported schema version"`. Use the
matcher-stage output (`rule-loader-matcher/v1`) from `match_rules.py` instead.
