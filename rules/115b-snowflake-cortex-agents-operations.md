---
schema_version: v4.0
rule_version: v5.0.0
description: Cortex Agent investigation, least-privilege execution context, lifecycle controls, evidence-based tests and cost monitoring.
last_updated: 2026-10-07
keywords:
  - kw:agent RBAC
  - kw:component testing agents
  - kw:agent cost budgets
  - kw:agent plan template
  - kw:agent investigation protocol
  - kw:agent flagging instructions
token_budget: ~1100
context_tier: High
depends:
  required:
    - 115-snowflake-cortex-agents-core.md  # Core agent creation and tool configuration
  optional:
    - 106c-snowflake-semantic-views-integration.md  # Semantic view design and Analyst tool configuration
---
# Snowflake Cortex Agents: Operations and Security

## Scope

**What This Rule Covers:**
Existing-agent investigation, deployment/test scope, user/tool roles, budgets, observability, and preservation of configuration/consumers.

**When to Load This Rule:**
When operating/reviewing Agents or preparing safe agent configuration, tests and monitoring.

## Contract

### Inputs and Prerequisites

- Actual existing spec/tool/grounding identities, user/default role/warehouse, current grants, account features and desired behavior.
- Approved model/tool/object scope, inference/deployment authorization, quality/safety rubric, budgets and recovery policy.

### Mandatory

- Read current configuration before proposals; verify actual tools/resources and supported models/interfaces. Do not assume agent architecture from examples or fabricate CREATE CORTEX AGENT/ALLOWED_OBJECTS fields.
- Record a concise design contract: purpose/archetype, model/version, tools/resources, routing/response policy, roles, budgets, tests and evaluation expectations. It is a review artifact, not mandatory new infrastructure.
- Current Agent API permissions use the querying user's default role/warehouse per setup docs; validate actual interface context, not just USE ROLE. Agent USAGE alone does not confer every tool/data privilege.
- Prefer narrow CORTEX_AGENT_USER service access where appropriate and exact agent/source/service/compute grants. No ACCOUNTADMIN application role, broad source grant or assumed database/schema SELECT.
- Inspect custom tool owner's/caller's rights and external effects; descriptions/instructions are not enforceable access controls. Apply runtime allowlists/validated inputs/egress and cost boundaries separately.
- Configure supported top-level orchestration token/time/access behavior deliberately; no invented MAX_CREDITS_PER_QUERY/QUERY_TIMEOUT SQL fields. Resource monitor limits do not universally cover agent/service inference spend.
- Separate authored design, local schema checks, authorized component calls, integrated inference and independent output review. Successful object creation or nonempty response does not establish correctness/safety.
- Evaluate normal/out-of-scope/ambiguous/empty/tool-error/denied/injection cases with approved inputs. Retain failed/interrupted identities, no benchmark retry/substitution and no passing denied unauthorized attempt.
- Monitor feature-specific usage/history and correlated traces with proper latency/completeness. Do not query invented CORTEX_AGENT_HISTORY or infer cost solely from QUERY_HISTORY/warehouse duration.
- Expected business flags/calculations need governed definitions and approved thresholds; presentation guidance can reference them. No universal ban on semantic flags or fabricated portfolio/cost policy.
- Preserve agent grants, configured resources, versions and consumers through approved lifecycle changes; replacement requires ownership/grant review and recovery. No deployment, grant, teardown or logging change merely to complete a checklist.
- Protect sensitive prompts/data/secrets and restrict evidence storage/export. Notifications and cross-region/model changes need scope approval; do not add external monitoring integrations silently.
- Diagnose failed/partial calls from actual tool/role/schema/request evidence, inspect uncertain effects before replay and recover only owned approved changes.

### Execution Steps

1. Inspect spec/tool/grant/user-default context and establish approved objective/operation boundaries.
2. Prepare scoped configuration and review model/tool/budget/security assumptions against current contracts.
3. Run appropriate local tests, then authorized component/integration tests with independent output/safety review.
4. Deploy/publish only approved configuration and verify effective grants/resources/consumer behavior.
5. Report quality/cost/trace/failure evidence and unverified limitations, with scoped recovery/monitoring ownership.

### Validation

- Actual spec/source/user/tool context and least privilege verified, no imagined allowlist/SQL function.
- Budget/privacy/security controls enforce actual scope; denied calls and incomplete evidence not labeled passes.
- Output tests and observed costs support claims, no invented hard per-request credit cap.
- Lifecycle/consumer/grant preservation and recovery explicit; no unapproved external evidence transmission.
- Deliver design/config/testing/operations evidence and precise local/live gaps.

## References

- [Agent access control/authentication](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-setup)
- [CREATE AGENT controls](https://docs.snowflake.com/en/sql-reference/sql/create-agent)
- [AI observability and billing](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability)
- `115c-snowflake-cortex-agents-testing.md` for evaluation/RBAC.
- `115d-snowflake-cortex-agents-observability.md` for monitoring/troubleshooting.
