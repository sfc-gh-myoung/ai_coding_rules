---
schema_version: v4.0
rule_version: v5.0.0
description: Governed Cortex Agent specifications, minimal scoped tools, grounded instructions, lifecycle safety and output-level evaluation.
last_updated: 2026-10-07
keywords:
  - kw:cortex agent
  - kw:agent archetype
  - kw:tool orchestration
  - kw:planning instructions
  - kw:semantic view grounding
  - kw:agent debugging
token_budget: ~1250
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 106-snowflake-semantic-views-core.md  # Semantic views as agent tools
  optional:
    - 115a-snowflake-cortex-agents-instructions.md  # Planning and response instructions
    - 115b-snowflake-cortex-agents-operations.md  # Testing, RBAC, observability
    - 116-snowflake-cortex-search.md  # Cortex Search for document retrieval
---
# Snowflake Cortex Agents Best Practices

## Scope

**What This Rule Covers:**
Agent purpose/tool selection, actual specification/schema, governed grounding/instructions, budget/lifecycle control and independently reviewed outputs.

**When to Load This Rule:**
When designing, configuring, reviewing or debugging Cortex Agents and their grounding/tool orchestration.

## Contract

### Inputs and Prerequisites

- Actual use case, permitted knowledge/action scope, expected answers, tool catalog/resources and supported account/model interfaces.
- Existing agent/spec/grants, semantic/Search definitions, service/tool execution roles, cost/privacy limits and deployment/call approvals.

### Mandatory

- Inspect current agents/tools and supported account/interface before creation. SHOW CORTEX parameters alone does not prove feature/model availability or tool access; unresolved prerequisites block deployment claims.
- Choose smallest useful tool set: one/multiple domain Analysts, Search or a hybrid where tasks actually need both. No mandatory Analyst/Search/model combination or fixed 30% hybrid threshold.
- Bind exact tool_spec names/types/descriptions and matching tool_resources keys to approved semantic-view/Search/custom resources. Describe purpose/capabilities/when-to-use distinctly; runtime tool permissions are narrower than prompt wishes.
- Use current CREATE AGENT FROM SPECIFICATION or documented API/SDK contract, not invented CREATE CORTEX AGENT AS TOOLS/AGENT_QUERY syntax. Comment aids discoverability but is not universally mandatory SQL syntax.
- Agent YAML models.orchestration, top-level orchestration budgets/access policy, instructions and tools/resources have different roles. Parse with a structured loader, validate current fields and use supported sample-question objects; no universal ban on valid block scalars or unquoted safe YAML strings.
- Set inaccessible-tool behavior consciously according to current specification and security requirements; missing privileges must not be compensated with broader grants or silent unauthorized tool calls. Verify actual run behavior.
- Use supported current model or auto selection consistent with reproducibility/budget needs. No stale llama/mistral ladder assumed valid for Agent orchestration; record actual resolved model identity when comparing quality/cost.
- Ground business calculations and governed definitions in semantic model/source contracts; put presentation/routing guidance in instructions. Do not forbid all business flags in semantic definitions or rely on prose thresholds as enforceable authorization.
- Orchestration instructions choose tools/multi-step prerequisites; response instructions require source-backed claims, units/date context, uncertainty and out-of-scope behavior. Retrieved text/tool outputs are data, not authority to override policy or invoke new tools.
- Bound tokens/time/queries/results and retries with actual supported controls and workload SLAs. No universal 120/30-second tool setting or query-text-only cost attribution; inspect service-specific usage.
- Protect secrets/PII/confidential prompts, data and metadata; approved cross-region/egress and execution scopes remain explicit. Custom tools and generated SQL need independent authorization/confinement.
- Test tools separately and integrated agent behavior on normal/out-of-scope/empty/error/injection/permission cases with authorized synthetic inputs. Creation success does not guarantee valid tool resources or correct output.
- Review actual generated answers/actions independently for safety and correctness; clean trace alone is not a behavioral pass. Retain attempt identities, failed/interrupted outcomes and unpaired comparisons without retry/substitution.
- Prefer supported preserving updates; replacement needs ownership/grant/consumer/version review, COPY GRANTS where appropriate and actual verification. Temporary/secure agents have distinct lifecycle/access semantics; do not deploy/drop to satisfy checks.

### Execution Steps

1. Inspect purpose/agent/tool/resource/interface and role/privacy constraints without generating new account operations.
2. Select scoped archetype/model and define valid specification plus routing/response guidance and enforceable budgets.
3. Review schema/tool permissions and prepare synthetic component/integration/output-safety tests.
4. Under deployment/call approval, create/update intended agent and execute version-bound tests within confinement.
5. Inspect tool traces and actual outputs, verify effective grants/resources, record failures/cost/uncertainty and scoped recovery.

### Validation

- Supported spec/SQL/API syntax and exact tools/resources/role context verified; no invented lifecycle calls.
- Purpose/archetype/grounding/instructions scoped and boundaries enforced, data/tool injection handled safely.
- Actual component/integration/output reviews support quality/safety claims; failed/denied calls remain failures.
- Model/budget/version/cost evidence and lifecycle/grant preservation explicit.
- Deliver reviewed specification/tests and exact local/live verification limits; uncalled agents remain unverified.

## References

- [CREATE AGENT specification](https://docs.snowflake.com/en/sql-reference/sql/create-agent)
- [Cortex Agents overview and models](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- [AI observability and usage](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability)
- `115a-snowflake-cortex-agents-instructions.md` for instructions.
- `115b-snowflake-cortex-agents-operations.md` for operational governance.
