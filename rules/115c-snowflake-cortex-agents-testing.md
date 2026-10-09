---
schema_version: v4.0
rule_version: v5.0.0
description: Component-first Cortex evaluation with correct query/service contracts, effective role tests and independently reviewed safety outputs.
last_updated: 2026-10-07
keywords:
  - kw:cortex agent testing
  - kw:agent RBAC grants
  - kw:component integration testing
  - kw:agent tool verification
  - kw:least-privilege agent permissions
  - kw:semantic view grants
token_budget: ~1150
context_tier: Low
depends:
  required:
    - 115-snowflake-cortex-agents-core.md  # Core agent creation and tool configuration
  optional:
    - 115b-snowflake-cortex-agents-operations.md  # Operations overview
    - 107-snowflake-security-governance.md  # Security and governance patterns
---
# Snowflake Cortex Agents: Testing and RBAC

## Scope

**What This Rule Covers:**
Tool/component, integrated/business, performance and permission testing with correct source/service schemas and immutable outcomes.

**When to Load This Rule:**
When testing Agent behavior, role access, tool selection, integration or production promotion gates.

## Contract

### Inputs and Prerequisites

- Actual spec/tools/resources, supported invocation/response interface, synthetic/authorized fixtures and independent expected answers.
- Approved component/inference/query scope, user-default role/warehouse and tool execution contexts, rubric/budgets and frozen comparison identity.

### Mandatory

- Test each applicable configured tool/source independently before integrated diagnosis; do not require Analyst/Search tools not present. Local mocks validate adapters, not real account access/data.
- Semantic SQL uses supported SEMANTIC_VIEW or direct semantic FROM/AGG forms, not TABLE(view(metrics...)) or a regular view masquerading as a semantic view. Inspect actual logical fields/expected grain before tests.
- Analyst generation and Search retrieval need actual configured API/SDK contracts. COMPLETE(model) is not an Analyst-tool test, and a one-row JSON response is not proof Search found useful documents.
- Assert independent values/grain/filter/units and source relevance/citations, not substring/nonempty output alone. Include empty/NULL/duplicate/date/ambiguous/mixed cases and actual tool-result parsing.
- Verify tools used from supported run/trace evidence, avoiding invented agent.query/response.tools_used properties. Missing trace evidence remains missing, not inferred from prose.
- Test out-of-scope, malformed, inaccessible, injection and partial-failure cases; ensure no denied-scope fallback, data exposure, broad object writes or fabricated answer.
- API roles use actual documented user-default role/warehouse requirements; USE ROLE alone may not establish the tested execution context. Include primary/secondary/default and custom-tool rights where relevant.
- Agent invocation needs supported service database role and agent USAGE, with tool-specific privileges. Semantic view SELECT is granted ON SEMANTIC VIEW; base SELECT is not inherently required for its consumer. Do not grant nonexistent Cortex builtin function signatures.
- Configure narrow grants/allowlists only with approval and verify permitted/denied cases using synthetic protected objects. No copying production PII into test fixtures or probing arbitrary sensitive tables for a denial test.
- Test fixture setup/teardown is isolated and ownership-scoped; no blanket CREATE OR REPLACE against shared names or broad cleanup. Keep known-good consumer/grant state intact.
- Frozen benchmarks bind actual models/prompts/tools/adapters/source/data/settings and retain each attempt. Do not retry/erase/relabel/substitute recorded failures or count interruptions/unpaired outputs as passes.
- Review actual outputs/safety separately from trace/schema success. Denied unauthorized attempts remain failures even when confinement works; uncertainty/tool-unavailable outputs must meet applicable truthful-fallback criteria.
- Latency/cost/query counts use measured workload targets, not universal 10/20-second or 50% regression rules. Missing cost/token fields remain unknown; CI live tests need opt-in account/inference authorization.

### Execution Steps

1. Inspect actual source/tool/spec/role contracts and define independent fixtures, expected results and safety boundaries.
2. Validate local adapters/schemas, then run approved component source/retrieval/generation tests.
3. Execute approved integrated business/edge/injection/denial cases with frozen identities and preserved evidence.
4. Review outputs and role/tool traces independently, reconcile counts/quality/performance/cost and investigate mismatches.
5. Promote only under required approval/gates; report failed/blocked/unattempted/unpaired results and scoped recovery.

### Validation

- Components and integration use real supported schemas/APIs and expected-result checks, no nonempty-only proof.
- Effective role/tool rights and allowed/denied behavior verified without unauthorized sensitive probing/grants.
- Immutable attempt accounting and independent output/safety reviews complete where claimed; missing/denied outcomes not passes.
- Performance/cost targets justified and actual data/service limitations explicit.
- Deliver test matrix/evidence and exact local/live outcome counts; no unexecuted deployment/access claim.

## References

- [Agent access and default role context](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-setup)
- [Semantic queries and privileges](https://docs.snowflake.com/en/user-guide/views-semantic/querying)
- [CREATE AGENT specification](https://docs.snowflake.com/en/sql-reference/sql/create-agent)
- `115-snowflake-cortex-agents-core.md` for supported tools/lifecycle.
- `107-snowflake-security-governance.md` for policy tests.
