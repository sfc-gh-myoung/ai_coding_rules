---
schema_version: v4.0
rule_version: v5.0.0
description: Governed semantic-view integration with Cortex Analyst and Agents, accurate payloads, and scoped troubleshooting.
last_updated: 2026-10-07
keywords:
  - kw:Cortex Analyst
  - kw:Cortex Agent grounding
  - kw:semantic view governance
  - kw:natural language query synonyms
  - kw:analyst troubleshooting
  - kw:policy inheritance base tables
token_budget: ~1150
context_tier: Medium
depends:
  required:
    - 106-snowflake-semantic-views-core.md  # DDL fundamentals
    - 106b-snowflake-semantic-views-querying.md  # Query patterns
---
# Snowflake Semantic Views: Integration and Governance

## Scope

**What This Rule Covers:**
Cortex grounding, current Analyst request/response contracts, semantic-view access, data-policy testing, and integration diagnostics.

**When to Load This Rule:**
When connecting semantic views to Analyst/Agents or reviewing their accuracy, access, and governance.

## Contract

### Inputs and Prerequisites

- Reviewed semantic definition, representative business questions/expected results, configured service/tool versions, approved account endpoint, and execution scope.
- Current service access roles and semantic-view SELECT with parent/compute privileges as applicable. Verify stage permissions for staged YAML and tool-specific Agent privileges; do not automatically elevate to CORTEX_USER or grant all base tables.

### Mandatory

- Distinguish native semantic_view FQN from staged semantic_model_file path and supported semantic_models collections. Choose actual project workflow; verified queries are not YAML-only in current native DDL.
- Analyst messages use role plus a content array of typed text blocks, not a bare content string. Validate supported fields against current API/installed SDK; do not invent Agent grounding_sources/SDK invoke methods or CLI commands.
- Use approved Snowflake account authentication with secrets managed outside source/logs. Verify host, TLS, account and role before sending prompts; do not upload confidential data to external helpers or change cross-region settings implicitly.
- Parse response blocks by type (text, sql, suggestion) and handle errors, ambiguity, unknown types, and streaming termination. A generated SQL block is not evidence of executed SQL or correct results.
- Review generated SQL scope, object access, business grain/units, time bounds, joins, and cost before separately authorized execution. Preserve request/query identifiers without logging secrets or unapproved sensitive prompts/results.
- Configure Agent tools/resources using the supported current specification and explicit semantic-view names. Verify caller/tool execution context and privileges; model/instructions do not confer data authorization. No fixed legacy-model recommendation.
- Semantic-view SELECT is distinct from base-table SELECT; granting base access alone does not grant view access. Preserve least privilege for users/service roles and avoid broad future grants without approval.
- Apply masking/row-access controls at supported source objects and validate effective behavior through the semantic view and service execution context. Do not assert unsupported policy attachment is silently ignored; inspect actual supported syntax and fail closed on uncertainty.
- Do not exempt Analyst service roles from masking or create unmasked copies merely to fix aggregation. Masking types must match policy signatures; choose approved type-compatible behavior and test permitted/denied results and aggregate inference risks.
- Add precise business synonyms/comments and test ambiguity; missing synonyms do not guarantee failure and synonyms do not guarantee accuracy. Verify generated query/results against independent business expectations.
- On source-schema changes, inspect actual references and consumers before approved semantic evolution. Preserve grants/materializations and recovery; replacement is not a generic troubleshooting command.
- Diagnose inaccessible/empty/error outputs using existing definitions, role grants, filters, policies, source availability, and tool bindings. Reads do not authorize grants, policy changes, uploads, model calls, or deployment.

### Execution Steps

1. Inspect model, service/tool configuration, current authentication/role context, and policy attachments through authorized reads.
2. Prepare correct request/tool bindings and business-question tests with explicit expected SQL/result meanings.
3. Under service-call approval, test representative questions, suggestions, errors, and response parsing; retain failed outcomes.
4. Execute reviewed generated queries only within approved scope and compare independent results under permitted/denied role contexts.
5. Report accuracy/security findings and scoped remediation; inspect state before retrying requests with uncertain effects.

### Validation

- Correct native/staged source and payload schema, approved endpoint, secure credentials, and typed response/error handling.
- Actual service/tool role access and policy behavior verified without granting unnecessary source access or bypassing masking.
- Query/result grain, units, joins, time bounds, and ambiguity meet business expectations; no response-only accuracy claim.
- Deliver configuration/payload design, role/policy test matrix, request/query evidence, and recovery prerequisites.
- Uncalled services, unexecuted SQL, unavailable policy evidence, and unverified SDK/CLI capabilities remain explicit gaps.

## References

- [Cortex Analyst REST contract](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/rest-api)
- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- [Semantic-view SQL and access](https://docs.snowflake.com/en/user-guide/views-semantic/sql)
- [Dynamic masking](https://docs.snowflake.com/en/user-guide/security-column-ddm-intro)
- [Row access policies](https://docs.snowflake.com/en/user-guide/security-row-intro)
- `106d-snowflake-semantic-views-development.md` for verified-query refinement.
