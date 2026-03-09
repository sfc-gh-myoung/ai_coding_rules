# Snowflake Cortex Agents: Observability & Cost Management

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:agent-observability, kw:agent-costs
**Keywords:** agent observability, agent evaluation, agent cost management, agent monitoring, agent latency, agent health, agent errors, debug agent, agent logs, agent trace, cortex agent troubleshooting, agent cost tracking
**TokenBudget:** ~3600
**ContextTier:** Low
**Depends:** 100-snowflake-core.md, 115-snowflake-cortex-agents-core.md, 115b-snowflake-cortex-agents-operations.md, 111-snowflake-observability-core.md

## Scope

**What This Rule Covers:**
Observability, evaluation, cost management, dedicated warehouse patterns, and error troubleshooting for Snowflake Cortex Agents.

**When to Load This Rule:**
- Setting up observability and evaluation for agents
- Managing agent costs and monitoring latency
- Troubleshooting agent errors (permissions, tool selection, empty results)
- Configuring dedicated warehouses for agent workloads

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **115-snowflake-cortex-agents-core.md** - Core agent creation
- **115b-snowflake-cortex-agents-operations.md** - Operations overview
- **111-snowflake-observability-core.md** - Observability patterns

**Related:**
- **105-snowflake-cost-governance.md** - Cost monitoring and governance

### External Documentation

- [AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability) - Tracing, evaluations, comparisons

## Contract

### Inputs and Prerequisites

- Agent created and configured with tools
- RBAC configured (see 115c-snowflake-cortex-agents-testing.md)
- Access to ACCOUNT_USAGE for monitoring queries

### Mandatory

- Use AI Observability to capture agent traces
- Monitor agent costs by warehouse attribution
- Implement health checks for production agents

### Forbidden

- Deploying agents without cost or latency controls
- Unbounded tool execution without timeouts
- Ignoring agent error patterns in production

### Execution Steps

1. Enable AI Observability tracing for agents
2. Set up evaluation with golden questions and assertions
3. Configure dedicated warehouses for cost attribution
4. Implement health check queries
5. Document error troubleshooting runbooks

### Output Format

- Observability queries and evaluation patterns
- Cost monitoring SQL queries
- Error troubleshooting steps with solutions

### Validation

- Traces captured in AI Observability
- Cost queries returning expected data
- Health checks running on schedule
- Error handling tested for common scenarios

### Design Principles

- Monitor costs, latency, and quality continuously
- Use AI Observability for debugging and optimization
- Prefer cached retrieval; restrict tool invocations per turn
- Fail fast on oversized requests

### Post-Execution Checklist

- [ ] AI Observability tracing enabled
- [ ] Evaluation framework configured (golden questions, assertions)
- [ ] Dedicated warehouses created for cost attribution
- [ ] Health check queries scheduled
- [ ] Error troubleshooting runbook documented

## Observability and Evaluation

- **Rule:** Use AI Observability to capture traces of agent reasoning, tool invocations, and outcomes
- **Rule:** Employ golden questions and assertions; compare model/tool variants and track regression
- **Always:** Monitor tool selection accuracy (is agent picking right tool?)
- **Always:** Track flagging accuracy (are thresholds applied correctly?)

### Agent Health Checks

**Periodic health check pattern:**

> **Investigation Required**
> The `CORTEX_AGENT_HISTORY` view may not be available in all Snowflake versions. Verify availability before using. If unavailable, use `QUERY_HISTORY` with query text filters to track agent queries.

```sql
-- Check agent availability and recent performance
-- NOTE: Verify CORTEX_AGENT_HISTORY exists in your account
SELECT
    agent_name,
    COUNT(*) as total_queries_24h,
    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as successful,
    COUNT(CASE WHEN status = 'ERROR' THEN 1 END) as errors,
    ROUND(successful / NULLIF(total_queries_24h, 0) * 100, 1) as success_rate_pct,
    AVG(latency_ms) as avg_latency_ms,
    MAX(latency_ms) as max_latency_ms
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_HISTORY
WHERE start_time >= DATEADD('hour', -24, CURRENT_TIMESTAMP())
GROUP BY agent_name
ORDER BY errors DESC;
```

## Cost and Latency Management

- **Rule:** Prefer cached retrieval; restrict tool invocations per turn
- **Rule:** Control token budgets and cap output tokens; fail fast on oversized requests
- **Always:** Monitor costs by agent and by tool type

### Dedicated Warehouses for Cortex Analyst Tools

**Rule:** Configure a dedicated warehouse for each agent's Cortex Analyst tools:

```sql
CREATE WAREHOUSE IF NOT EXISTS AGENT_ANALYTICS_WH
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Dedicated warehouse for analytics agent Cortex Analyst tools';

GRANT USAGE ON WAREHOUSE AGENT_ANALYTICS_WH TO ROLE AGENT_RUNNER;
```

**Benefits:**
- **Cost Attribution:** Track compute costs per agent in Account Usage
- **Performance Isolation:** Queries don't compete with other workloads
- **Sizing Control:** Right-size warehouse per agent's query complexity
- **Auto-Suspend:** Configure aggressive auto-suspend (60s) for cost savings

### Cost Monitoring Query

```sql
SELECT
    warehouse_name,
    DATE_TRUNC('day', start_time) AS usage_date,
    SUM(credits_used) AS daily_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE warehouse_name LIKE 'AGENT_%'
  AND start_time >= DATEADD('day', -30, CURRENT_DATE())
GROUP BY 1, 2
ORDER BY 2 DESC, 3 DESC;
```

## Common Errors and Solutions

### Error: "Semantic view not found" or "Object does not exist"

**Cause:** Agent role lacks SELECT permission on semantic view, or view doesn't exist

**Solutions:**
```sql
-- 1. Verify view exists
SHOW VIEWS LIKE '{VIEW_NAME}' IN SCHEMA {DATABASE}.{SCHEMA};

-- 2. Grant SELECT access to agent role
GRANT SELECT ON VIEW {DATABASE}.{SCHEMA}.{VIEW_NAME} TO ROLE agent_runner;

-- 3. Verify grant was applied
SHOW GRANTS TO ROLE agent_runner;

-- 4. Test access
USE ROLE agent_runner;
SELECT * FROM {DATABASE}.{SCHEMA}.{VIEW_NAME} LIMIT 1;
```

### Error: "Tool returned no results" or "Empty response"

**Cause:** Tool configured but underlying data empty, filters too restrictive, or query logic incorrect

**Solutions:**
```sql
-- 1. Test tool independently (component testing)
SELECT * FROM {SEMANTIC_VIEW} LIMIT 10;

-- 2. For Cortex Search tool:
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    '{SERVICE_NAME}',
    '{"query": "test", "limit": 10}'
);

-- 3. Verify data exists in underlying tables
SELECT COUNT(*) FROM {SEMANTIC_VIEW};

-- 4. Test with broader query, then add filters incrementally
```

### Error: "Agent selected wrong tool"

**Cause:** Overlapping tool descriptions, vague when-to-use guidance, or unclear planning instructions

**Solutions:**
1. Ensure each tool has distinct use case with explicit trigger words
2. Add clearer tool selection classification logic to planning instructions
3. Test tool selection with validation script:

```python
test_queries = [
    ("What are my top 10 holdings?", "portfolio_analyzer"),
    ("What does research say about AAPL?", "search_research_reports"),
    ("Show sector allocation", "portfolio_analyzer")
]

for query, expected_tool in test_queries:
    result = agent.query(query)
    print(f"Query: {query}")
    print(f"Tool used: {result.tool_used}, Expected: {expected_tool}")
    assert result.tool_used == expected_tool
```

### Error: "Permission denied" on Cortex function

**Cause:** Missing USAGE grants on Cortex functions

**Solutions:**
```sql
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.SEARCH_PREVIEW TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.ANALYST TO ROLE agent_runner;

-- Verify and test
SHOW GRANTS TO ROLE agent_runner;
USE ROLE agent_runner;
SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', 'test');
```

### Error: "Search service not found"

**Cause:** Missing USAGE grant on Cortex Search service

**Solutions:**
```sql
-- 1. Verify service exists
SHOW CORTEX SEARCH SERVICES IN SCHEMA {DATABASE}.{SCHEMA};

-- 2. Grant USAGE on service
GRANT USAGE ON CORTEX SEARCH SERVICE {DATABASE}.{SCHEMA}.{SERVICE_NAME} TO ROLE agent_runner;

-- 3. Verify and test
SHOW GRANTS TO ROLE agent_runner;
USE ROLE agent_runner;
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW('{SERVICE_NAME}', '{"query": "test", "limit": 1}');
```

### Error: "Flagging logic not working"

**Cause:** Flagging logic placed in semantic view instead of agent response instructions

**Solution:**
- **Rule:** Ensure flagging logic is in Agent Response Instructions, never in semantic views
- Semantic View: Calculate accurate `position_weight`
- Agent Response Instructions: "When position_weight > 6.5%, flag with WARNING"

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using a Shared Warehouse for All Agent Workloads**

**Problem:** Running multiple agents on the same shared warehouse (e.g., the default `COMPUTE_WH`). When costs spike, there is no way to attribute compute charges to a specific agent since `WAREHOUSE_METERING_HISTORY` only reports at the warehouse level. Performance also degrades unpredictably as agents compete for resources, and you cannot right-size capacity per agent since one warehouse must serve all workload profiles.

**Correct Pattern:** Create a dedicated X-SMALL warehouse per agent (or per agent group) with aggressive auto-suspend (60 seconds). This enables per-agent cost attribution via `WAREHOUSE_METERING_HISTORY`, performance isolation, and independent sizing. Name warehouses with an `AGENT_` prefix (e.g., `AGENT_PORTFOLIO_WH`) for easy filtering in cost queries.

```sql
-- Wrong: All agents share a single warehouse — no cost attribution
CREATE CORTEX AGENT my_portfolio_agent ...
    WAREHOUSE = 'COMPUTE_WH';  -- Shared with ETL, dashboards, and other agents

CREATE CORTEX AGENT my_research_agent ...
    WAREHOUSE = 'COMPUTE_WH';  -- Same warehouse — which agent caused the cost spike?

-- Correct: Dedicated warehouse per agent for cost isolation
CREATE WAREHOUSE IF NOT EXISTS AGENT_PORTFOLIO_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

CREATE WAREHOUSE IF NOT EXISTS AGENT_RESEARCH_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

-- Now cost queries can pinpoint the expensive agent
SELECT warehouse_name, SUM(credits_used) AS credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE warehouse_name LIKE 'AGENT_%'
  AND start_time >= DATEADD('day', -7, CURRENT_DATE())
GROUP BY warehouse_name
ORDER BY credits DESC;
```

**Anti-Pattern 2: Deploying Agents Without Health Checks or Alerting**

**Problem:** Agents are deployed to production with no ongoing monitoring. Failures surface only when end users report that "the agent stopped working" or "answers are wrong." By that point, the agent may have been broken for hours or days due to an expired search service, a dropped semantic view, or a revoked grant. There is no error rate tracking, no latency baseline, and no alerting.

**Correct Pattern:** Implement periodic health checks that run a set of known-good "golden questions" against each production agent. Track success rate, latency percentiles, and tool invocation counts over time. Set alerts on success rate drops (e.g., below 95%) and latency spikes (e.g., p95 exceeds 2x baseline). Use `CORTEX_AGENT_HISTORY` (or `QUERY_HISTORY` with filters) to monitor agent query patterns and error rates.

```python
# Wrong: Deploy and forget — no health monitoring
def deploy_agent():
    session.sql("CREATE CORTEX AGENT ...").collect()
    print("Agent deployed!")  # No monitoring, no alerting

# Correct: Periodic health checks with golden questions
GOLDEN_QUESTIONS = [
    {"query": "What are the top 5 holdings?", "expect_tool": "portfolio_analyzer"},
    {"query": "Find research on AAPL", "expect_tool": "search_research_reports"},
]

def run_agent_health_check(session, agent_name):
    """Run golden questions and report health metrics."""
    results = {"passed": 0, "failed": 0, "latencies": []}

    for test in GOLDEN_QUESTIONS:
        start = time.time()
        try:
            response = call_agent(session, agent_name, test["query"])
            latency_ms = (time.time() - start) * 1000
            results["latencies"].append(latency_ms)

            if response and len(response) > 0:
                results["passed"] += 1
            else:
                results["failed"] += 1
                log.error(f"Empty response for: {test['query']}")
        except Exception as e:
            results["failed"] += 1
            log.error(f"Health check failed: {test['query']} — {e}")

    success_rate = results["passed"] / len(GOLDEN_QUESTIONS) * 100
    p95_latency = sorted(results["latencies"])[int(len(results["latencies"]) * 0.95)]

    if success_rate < 95:
        send_alert(f"Agent {agent_name} health degraded: {success_rate}% success")
    if p95_latency > 5000:
        send_alert(f"Agent {agent_name} slow: p95={p95_latency}ms")
```

**Anti-Pattern 3: Ignoring Token Budget Controls Until Costs Explode**

**Problem:** Agents are deployed with no `max_tokens` limits or tool invocation caps. A single poorly-phrased user query can trigger multiple expensive model calls, lengthy chain-of-thought reasoning, or repeated tool invocations that consume excessive tokens. The issue only becomes visible at the end of the month when the credit bill arrives.

**Correct Pattern:** Set explicit `max_tokens` on agent responses from day one. Monitor token consumption per query using AI Observability traces and set per-query cost thresholds. Implement guardrails that fail fast on oversized requests (e.g., reject input prompts exceeding a token limit). Review token usage trends weekly during the first month after deployment, then shift to alerting on anomalies.

```python
# Wrong: No token limits — unbounded cost per query
response = call_cortex_agent(
    agent_name="ANALYTICS.AI.PORTFOLIO_AGENT",
    question=user_input,
    # No max_tokens, no input validation — could cost $$$
)

# Correct: Enforce token budgets and input guardrails
MAX_INPUT_LENGTH = 2000   # Reject oversized prompts
MAX_OUTPUT_TOKENS = 1024  # Cap response generation cost

def call_agent_with_guardrails(agent_name, user_input):
    # Guardrail: reject oversized input before calling the model
    if len(user_input) > MAX_INPUT_LENGTH:
        raise ValueError(
            f"Input too long ({len(user_input)} chars). "
            f"Max allowed: {MAX_INPUT_LENGTH}"
        )

    response = call_cortex_agent(
        agent_name=agent_name,
        question=user_input,
        max_tokens=MAX_OUTPUT_TOKENS,  # Always set explicit cap
    )
    return response
```
