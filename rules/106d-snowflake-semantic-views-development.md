---
schema_version: v4.0
rule_version: v3.0.0
description: Reviewed semantic generation, verified-question repositories, versioned deployment, and iterative business validation.
last_updated: 2026-10-07
keywords:
  - kw:semantic view generator
  - kw:verified query repository
  - kw:VQR logical table naming
  - kw:YAML semantic model
  - kw:iterative refinement workflow
  - kw:onboarding questions
token_budget: ~1150
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation rule
    - 106-snowflake-semantic-views-core.md  # DDL fundamentals
---
# Snowflake Semantic Views: Development Workflows

## Scope

**What This Rule Covers:**
Generator-assisted modeling, native/YAML verified queries, expected-result tests, onboarding questions, and controlled iterative deployment.

**When to Load This Rule:**
When building/refining semantic models, reviewing generated definitions, or maintaining verified question-SQL pairs.

## Contract

### Inputs and Prerequisites

- Actual source metadata/data availability, glossary, grain/keys/units, representative business questions, and expected calculations.
- Existing native/YAML workflow and schema version, configured generator/service interface, approved deployment scope, and relevant creation/source/stage privileges.

### Mandatory

- Generator assistance is optional. Inspect the actual installed/Snowsight/open-source interface and supported capabilities instead of claiming a universal Snowsight-only/API workflow or inferred-key guarantee.
- Treat generated DDL/YAML and suggested verified queries as untrusted drafts. Review columns, numeric identifiers versus measures, grain/key uniqueness, relationships, aggregations, time zones, units, security, synonyms, and comments before deployment.
- Use alias.logical_name AS expression in native DDL. Follow current clause/validation rules and do not require every key/block or fabricate schema names from examples.
- Native SQL supports AI_VERIFIED_QUERIES; YAML semantic models use verified_queries. Do not label VQR YAML-only, conflate their formats, or promise guaranteed accuracy/direct reuse for every similar question.
- For legacy YAML VQR SQL, use `__logical_table` names and logical column names defined in that model. Do not substitute physical column names or aggregate an already-aggregated logical metric blindly. Native verified-query SQL follows its documented native workflow, not an automatic `__` prefix rule.
- Each verified query must answer its stated question with independently checked grain, filters, aggregation, joins, date boundaries, NULL behavior, and access context. A model-generated suggestion is not verified until reviewed and tested.
- Add questions that cover important/repeated business needs, ambiguity, synonyms, and complex logic; onboarding questions must be meaningful for intended users. More variants do not automatically improve accuracy.
- Verification timestamps/verifier metadata represent actual review, not a fabricated name or current date after an untested edit. Revalidate after relevant schema, policy, metric, or business-definition changes; data arrival alone does not prove a definition invalid.
- Validate YAML parsing and schema field names with the actual consumer. Preserve multiline SQL with suitable block scalars/indentation; reject unsupported fields and do not copy malformed documentation examples.
- Maintain definitions and expected-result tests in project version control, but commit only with explicit user approval. Stage upload/overwrite and native deployment are separate authorized mutations; inspect existing versions, ownership, grants, consumers, and recovery before replacing.
- Analyst tests need the current typed-message API contract and authorized endpoint. Capture generated SQL and compare actual results, including unavailable/ambiguous cases; no paid/API call simply to satisfy an authoring checklist.
- Preserve immutable failed test evidence and identify exact source/model/service versions. Promotion requires reviewed artifact identity and applicable tests, not generator success or a saved-query label.

### Execution Steps

1. Inspect existing models/sources and establish business definitions and test expectations; use a configured generator only when useful and authorized.
2. Review/refine logical structure, expressions, synonyms/comments, and security before writing deployable definitions.
3. Add native or YAML verified-query entries in the correct format; validate parsing/schema and independently review each SQL/question pair.
4. Execute tests only with account/service authorization; update verification metadata from actual results, not anticipated outcomes.
5. Deploy/upload the reviewed version only in approved scope, verify effective identity, test consumers, and record scoped recovery steps.

### Validation

- Generated mappings/keys/metrics and YAML/native fields match actual source and consumer contracts.
- Verified queries use correct logical naming and answer their questions under independently checked result/role/time semantics.
- Onboarding/synonym coverage and test failures reviewed without accuracy guarantees or fabricated verification metadata.
- Version/deployment identity, permissions, stage overwrite scope, and recovery are explicit.
- Deliver definition, verified-query repository, expected tests, change rationale, and actual verification gaps; unexecuted SQL/services remain unverified.

## References

- [Verified Query Repository](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/verified-query-repository)
- [Native SQL verified queries](https://docs.snowflake.com/en/user-guide/views-semantic/sql)
- [CREATE SEMANTIC VIEW](https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view)
- [Analyst API request/response](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/rest-api)
- [Verified-query suggestions](https://docs.snowflake.com/en/user-guide/views-semantic/verified-query-suggestions)
- `106c-snowflake-semantic-views-integration.md` for service/policy testing.
