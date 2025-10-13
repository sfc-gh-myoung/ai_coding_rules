**Description:** Best practices for Snowflake Cortex Agents covering agent design, grounding, tools/functions, RBAC, latency/cost trade-offs, and observability.
**AppliesTo:** `**/*.sql`, `**/*.py`
**AutoAttach:** false
**Type:** Agent Requested
**Keywords:** Cortex Agents, AI agents, agent design, grounding, tools, functions, agent RBAC, agent observability
**Version:** 1.1
**LastUpdated:** 2025-10-13

**TokenBudget:** ~350
**ContextTier:** Medium

# Snowflake Cortex Agents Best Practices

## Purpose
Provide pragmatic patterns to design, secure, and operate Cortex Agents: grounding with enterprise data, tool execution, prompt hygiene, RBAC, observability, and quality evaluation, optimized for reliability and cost.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Cortex Agents creation and operation, tool design, memory/grounding, prompt templates, RBAC/allowlists, evaluation and tracing, cost/latency trade-offs

## Contract
- **Inputs/Prereqs:**
  - Snowflake account with Cortex Agents availability; role strategy defined
  - Grounding sources (tables, views, Cortex Search indices, semantic views)
  - Tool catalog (SQL procedures, UDFs, external actions) with least-privilege permissions
- **Allowed Tools:** Cortex Agents (Snowsight/SQL/Python), AI Observability, semantic views, Cortex Search
- **Forbidden Tools:**
  - Unbounded tool execution without guardrails or allowlists
  - Prompts containing secrets/PII, or enabling escalation of privileges
- **Required Steps:**
  1. Define agent objectives and non-goals; select smallest model and temperature that meet quality
  2. Ground with high-signal sources (semantic views, curated indices); avoid raw ungoverned tables
  3. Define a minimal tool surface with deterministic behaviors and input validation
  4. Enforce RBAC and allowlists for models, tools, and data; add content filters if needed
  5. Add evaluation (gold questions, assertions) and tracing via AI Observability
  6. Monitor costs and latency; introduce caching and retrieval filters
- **Output Format:** Agent configs/patterns, SQL/Python snippets
- **Validation Steps:** Evaluation scores meet thresholds; traces show bounded tool calls; RBAC enforced; cost objectives met

## Key Principles
- Smallest sufficient model and minimal tool surface reduce cost and risk
- Ground with curated, up-to-date, governed sources; prefer semantic views
- Deterministic tools with strict validation; idempotent, bounded side-effects
- Add allowlists/deny lists for models, tools, and tables/views
- Log/trace agent steps and evaluate quality regularly

## 1. Agent Design
- Specify clear system prompts with constraints and style; keep under token limits
- Use retrieval via Cortex Search or semantic views; provide explicit instructions on when to call tools

## 2. Tooling Strategy
- Tools should be:
  - Deterministic, side-effect aware, and idempotent
  - Validating inputs (types/ranges) and returning structured outputs
  - Bounded by RBAC and schema-level allowlists

## 3. RBAC and Allowlists
```sql
-- Example: restrict model/tool access
-- Pseudocode illustrating allowlist patterns (subject to product capabilities)
ALTER ACCOUNT SET CORTEX_ALLOWED_MODELS = ('llama3.1-8b','mixtral-8x7b');
ALTER ROLE agent_runner SET ALLOWED_TOOLS = ('run_sql_proc','lookup_customer');
```

## 4. Observability and Evaluation
- Use AI Observability to capture traces of agent reasoning, tool invocations, and outcomes
- Employ golden questions and assertions; compare model/tool variants and track regression

## 5. Cost and Latency
- Prefer cached retrieval; restrict tool invocations per turn
- Control token budgets and cap output tokens; fail fast on oversized requests

## 6. Example Patterns
### 6.1 Prompt scaffolding for tool gating
```text
You are an enterprise agent. Only call tools when necessary. Prefer answering from retrieved context.
Constraints: Never expose secrets; follow RBAC; cite sources with table/view names.
```

### 6.2 SQL callable tool (design sketch)
```sql
CREATE OR REPLACE PROCEDURE APP.CUSTOMER.lookup_customer(p_email STRING)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
  SELECT OBJECT_CONSTRUCT('id', id, 'status', status)
  FROM APP_DB.CORE.CUSTOMERS
  WHERE email = p_email
  LIMIT 1;
$$;
```

## Quick Compliance Checklist
- [ ] Agent objectives defined; smallest sufficient model chosen
- [ ] Grounding uses governed sources (semantic views or indices)
- [ ] Tools are deterministic, validated, and least-privilege
- [ ] Model/tool/table allowlists configured; secrets/PII excluded from prompts
- [ ] Tracing and evaluation enabled; thresholds monitored
- [ ] Token/output caps set; cost/latency tracked

## Validation
- **Success checks:** Evaluation meets targets; traces show bounded tool use; costs stable
- **Negative tests:** Prompt injections fail; unauthorized tool/data access blocked; oversized prompts rejected

## Response Template
```markdown
## Cortex Agent Plan
- Objective: <clear objective>
- Model: <smallest sufficient model>
- Grounding: <semantic views / indices>
- Tools (allowlist): [tool_a, tool_b]
- RBAC: <roles/allowed objects>
- Cost/Latency: <budgets, caps>
- Evaluation: <gold Qs, assertions>

## Agent Changes
- System prompt: <summary>
- Tool schema updates: <diff/highlights>
- Observability: <traces/metrics enabled>

## Validation
- Eval score >= <threshold>; tool calls bounded; costs within budget
```

## References

### External Documentation
- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents) - Agent concepts, tools, and setup
- [AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability) - Tracing, evaluations, comparisons

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Semantic Views**: `106-snowflake-semantic-views.md`
- **Cost Governance**: `105-snowflake-cost-governance.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
- **Observability**: `111-snowflake-observability.md`


