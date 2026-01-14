# Snowflake Cortex Agents: Operations & Security

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-12
**Keywords:** observability, evaluation, cost management, error troubleshooting, agent security, test agent, agent permissions, agent monitoring, agent evaluation, agent costs, debug agent, agent logs, agent trace, agent security policies
**TokenBudget:** ~5950
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 115-snowflake-cortex-agents-core.md, 111-snowflake-observability-core.md

## Scope

**What This Rule Covers:**
Comprehensive operational patterns for Cortex Agents including testing strategies, RBAC configuration, observability, cost management, and error troubleshooting.

**When to Load This Rule:**
- Testing Cortex Agents (component and integration testing)
- Configuring RBAC and allowlists
- Setting up observability and evaluation frameworks
- Managing costs and monitoring latency
- Troubleshooting agent errors
- Implementing security policies for agents

> **Investigation Required**
> When applying this rule:
> 1. **Read existing agent configurations BEFORE making changes** - Check current grounding sources, tools, instructions
> 2. **Verify available Cortex features** - Check if Cortex Analyst, Search, semantic views are available
> 3. **Never assume agent architecture** - Read existing agents to understand patterns
> 4. **Check RBAC and permissions** - Verify what roles and objects are accessible
> 5. **Test after changes** - Run component and integration tests to verify behavior
>
> **Anti-Pattern:**
> "Creating a Cortex Agent with these tools... (without checking available features)"
> "Adding semantic view grounding... (without verifying semantic views exist)"
>
> **Correct Pattern:**
> "Let me check your Cortex setup first."
> [reads existing agents, checks Cortex Search indices, verifies semantic views]
> "I see you have semantic views for sales data and Cortex Search for docs. Creating agent with these grounding sources..."

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **115-snowflake-cortex-agents-core.md** - Core agent creation and tool configuration
- **111-snowflake-observability-core.md** - Observability patterns

**Related:**
- **106c-snowflake-semantic-views-integration.md** - Semantic view design and Analyst tool configuration
- **116-snowflake-cortex-search.md** - Search service setup and tool integration
- **106-snowflake-semantic-views-core.md** - Semantic views foundation
- **105-snowflake-cost-governance.md** - Cost monitoring and governance
- **119-snowflake-warehouse-management.md** - Warehouse sizing

### External Documentation

- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents) - Agent concepts, tools, and setup
- [AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability) - Tracing, evaluations, comparisons
- [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) - Natural language to SQL
- [Cortex Search](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search) - Semantic search service

## Contract

### Inputs and Prerequisites

Agent created and configured, tools defined, role strategy established

### Mandatory

Testing frameworks, RBAC commands, AI Observability, evaluation tools

### Forbidden

Unbounded tool execution, privilege escalation

### Execution Steps

1. Component testing
2. Integration testing
3. RBAC enforcement
4. Add observability
5. Monitor costs

### Output Format

Test patterns, RBAC configs, observability queries, troubleshooting steps

### Validation

**Pre-Task-Completion Checks:**
- Component tests defined
- Integration tests planned
- RBAC strategy documented
- Observability setup ready
- Cost monitoring configured

**Success Criteria:**
- Tests pass (component and integration)
- RBAC enforced (least privilege)
- Traces captured (AI Observability)
- Costs within budget
- Error handling graceful

**Negative Tests:**
- Unauthorized access blocked
- Invalid inputs rejected
- Out-of-scope queries handled

### Design Principles

- Test tools independently before integration
- Enforce least-privilege RBAC and allowlists
- Add evaluation (gold questions, assertions) and tracing
- Monitor costs, latency, and quality continuously
- Use AI Observability for debugging and optimization

### Post-Execution Checklist

- [ ] Agent archetype chosen based on use case and tool requirements
- [ ] Agent objectives defined; smallest sufficient model chosen
- [ ] Grounding uses governed sources (semantic views or indices)
- [ ] Tools have clear descriptions with when-to-use guidance
- [ ] Tool use cases are distinct (no overlaps)
- [ ] Planning instructions are explicit about tool selection logic
- [ ] Flagging logic is in AGENT instructions (NOT semantic views)
- [ ] Tools are deterministic, validated, and least-privilege
- [ ] Component testing completed before integration testing
- [ ] Model/tool/table allowlists configured; secrets/PII excluded from prompts
- [ ] Tracing and evaluation enabled; thresholds monitored
- [ ] Token/output caps set; cost/latency tracked

**Anti-Pattern 1: Flagging Logic in Semantic Views**
```yaml
# In Semantic View custom instructions:
"Flag positions exceeding 6.5% as concentration risks"
```
**Problem:** Semantic views should be reusable across agents with different thresholds. Business rules belong in agent instructions.

**Correct Pattern:**
```yaml
# In Agent Response Instructions:
"When position weights exceed 6.5%, flag with ' CONCENTRATION WARNING'"

# In Semantic View:
Just calculate position_weight accurately (no flagging logic)
```

**Anti-Pattern 2: Overlapping Tool Use Cases**
```yaml
Tool A: "Use for portfolio analysis"
Tool B: "Use for investment analysis"  # Too similar!
```
**Problem:** Agent won't know which tool to pick, leading to inconsistent behavior.

**Correct Pattern:**
```yaml
Tool A: "Use for portfolio holdings, weights, and sector breakdowns"
Tool B: "Use for risk metrics, volatility calculations, and correlations"
```

**Anti-Pattern 3: Missing When-to-Use Guidance**
```yaml
Tool Description: "Analyzes portfolio data"
```
**Problem:** Too vague. Agent doesn't know WHEN this tool is appropriate vs other tools.

**Correct Pattern:**
```yaml
Tool Description: "Use this tool for quantitative portfolio analysis including holdings lists, weight calculations, and sector allocations. Use for questions about 'how much', 'what percentage', 'top N', and data visualizations."
```

**Anti-Pattern 4: Testing Only End-to-End**
```python
# Only test complete agent workflows
test_full_agent_query("Show me everything about my portfolio")
```
**Problem:** When tests fail, you don't know which tool or component is broken.

**Correct Pattern:**
```python
# Test components first
test_analyst_tool_works()
test_search_tool_works()
# Then test integration
test_multi_tool_workflow()
```

**Anti-Pattern 5: Vague Planning Instructions**
```
"Use the best tool for each query"
```
**Problem:** Too ambiguous. Agent needs explicit tool selection logic.

**Correct Pattern:**
```
"For numerical questions (how much, what percentage, top N), use portfolio_analyzer. For opinions and research (what do analysts say, latest commentary), use search_research_reports."
```

## Output Format Examples

```sql
-- Analysis Query: Investigate current state
SELECT column_pattern, COUNT(*) as usage_count
FROM information_schema.columns
WHERE table_schema = 'TARGET_SCHEMA'
GROUP BY column_pattern;

-- Implementation: Apply Snowflake best practices
CREATE OR REPLACE VIEW schema.view_name
COMMENT = 'Business purpose following semantic model standards'
AS
SELECT
    -- Explicit column list with business context
    id COMMENT 'Surrogate key',
    name COMMENT 'Business entity name',
    created_at COMMENT 'Record creation timestamp'
FROM schema.source_table
WHERE is_active = TRUE;

-- Validation: Confirm implementation
SELECT * FROM schema.view_name LIMIT 5;
SHOW VIEWS LIKE '%view_name%';
```

## Testing & Validation Patterns

### 6.1 Component Testing (Test Tools Independently)

Before integration, verify each tool works correctly:

**Testing Cortex Analyst Tools:**
```python
def test_analyst_tool(session: Session, semantic_view: str):
    """Verify Cortex Analyst tool responds correctly"""

    # Test with simple query
    result = session.sql(f"""
        SELECT * FROM TABLE(
            {semantic_view}(
                METRICS total_value,
                DIMENSIONS category
            )
        ) LIMIT 5
    """).collect()

    print(f"Analyst tool returned {len(result)} results")
    return len(result) > 0
```

**Testing Cortex Search Tools:**
```python
def test_search_tool(session: Session, service_name: str):
    """Verify Cortex Search tool responds correctly"""

    # Test with simple search
    result = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
            '{service_name}',
            '{{"query": "test", "limit": 1}}'
        )
    """).collect()

    print(f"Search tool returned results")
    return len(result) > 0
```

### 6.2 Integration Testing (Test Tool Combinations)

After component tests pass, test realistic workflows:

**Multi-Tool Agent Testing:**
- Test quantitative query (should use Cortex Analyst)
- Test qualitative query (should use Cortex Search)
- Test mixed query (should use both tool types)
- Verify tool selection logic works correctly

**Example Test Queries:**
```python
# Quantitative (Analyst)
"What are the top 10 holdings by weight?"
"Calculate sector allocation breakdown"

# Qualitative (Search)
"What is the latest research on {company}?"
"Find compliance policies for {topic}"

# Mixed (Both)
"Show top holdings and their latest research ratings"
"Analyze sector exposure with supporting market commentary"
```

### 6.3 Business Scenario Testing

Test with realistic end-user queries:

**Portfolio Management Scenarios:**
```
"What are my largest positions in the Global Growth fund?"
"Show me technology sector exposure across all portfolios"
"Are there any concentration warnings I should be aware of?"
"What does recent research say about my top holdings?"
```

**Compliance Scenarios:**
```
"Check if any positions violate our 7% concentration policy"
"Find engagement notes for companies with ESG controversies"
"What does our policy say about environmental violations?"
```

### 6.4 Validation Checklist

Component Testing:
- [ ] All required AI components exist (semantic views, search services)
- [ ] Each Cortex Analyst tool returns data independently
- [ ] Each Cortex Search tool returns documents independently
- [ ] Tool descriptions are clear and non-overlapping

Integration Testing:
- [ ] Tool selection logic works for quantitative queries
- [ ] Tool selection logic works for qualitative queries
- [ ] Tool selection logic works for mixed queries
- [ ] Multi-tool synthesis produces coherent responses

Business Scenario Testing:
- [ ] Realistic queries return expected results
- [ ] Flagging logic applies correctly
- [ ] Citations are properly formatted
- [ ] Charts/visualizations generate appropriately

Performance & Cost:
- [ ] Query response times are acceptable
- [ ] Token usage is within budget
- [ ] Tool invocation counts are reasonable

## RBAC and Permissions

### 7.1 Required Grants for Cortex Agents

**Database and Schema Access:**
```sql
-- Grant database and schema usage to agent role
GRANT USAGE ON DATABASE {DATABASE} TO ROLE agent_runner;
GRANT USAGE ON SCHEMA {DATABASE}.{SCHEMA} TO ROLE agent_runner;

-- Example:
GRANT USAGE ON DATABASE ANALYTICS TO ROLE agent_runner;
GRANT USAGE ON SCHEMA ANALYTICS.SEMANTIC TO ROLE agent_runner;
```

**Semantic View Access (for Cortex Analyst tools):**
```sql
-- Grant SELECT on specific semantic views
GRANT SELECT ON VIEW {DATABASE}.{SCHEMA}.{VIEW_NAME} TO ROLE agent_runner;

-- Or grant on all views in schema
GRANT SELECT ON ALL VIEWS IN SCHEMA {DATABASE}.{SCHEMA} TO ROLE agent_runner;

-- Example:
GRANT SELECT ON VIEW ANALYTICS.SEMANTIC.PORTFOLIO_VIEW TO ROLE agent_runner;
GRANT SELECT ON VIEW ANALYTICS.SEMANTIC.RISK_VIEW TO ROLE agent_runner;
```

**Cortex Search Service Access:**
```sql
-- Grant USAGE on Cortex Search services
GRANT USAGE ON CORTEX SEARCH SERVICE {DATABASE}.{SCHEMA}.{SERVICE_NAME} TO ROLE agent_runner;

-- Example:
GRANT USAGE ON CORTEX SEARCH SERVICE DOCS.SEARCH.research_reports_service TO ROLE agent_runner;
GRANT USAGE ON CORTEX SEARCH SERVICE DOCS.SEARCH.policy_documents_service TO ROLE agent_runner;
```

**Cortex Function Access:**
```sql
-- Grant USAGE on Cortex AI functions
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.SEARCH_PREVIEW TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.SUMMARIZE TO ROLE agent_runner;

-- For Cortex Analyst (if using direct function access)
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.ANALYST TO ROLE agent_runner;
```

**Warehouse Access:**
```sql
-- Grant warehouse usage for query execution
GRANT USAGE ON WAREHOUSE {WAREHOUSE_NAME} TO ROLE agent_runner;

-- Example:
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE agent_runner;
```

### 7.2 Verification Queries

**Verify All Grants:**
```sql
-- Check all grants for agent role
SHOW GRANTS TO ROLE agent_runner;

-- Verify specific grant exists
SELECT *
FROM TABLE(INFORMATION_SCHEMA.APPLICABLE_ROLES())
WHERE grantee = 'AGENT_RUNNER';
```

**Test Access:**
```sql
-- Switch to agent role and test access
USE ROLE agent_runner;

-- Test semantic view access
SELECT COUNT(*) FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW;

-- Test Cortex Search service
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{"query": "test", "limit": 1}'
);

-- Test Cortex function
SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', 'test');
```

### 7.3 Principle of Least Privilege

Apply these security patterns:
- **Agents:** Only access tools needed for specific use case
- **Tools:** Only access data appropriate for their domain
- **Roles:** Grant minimum permissions required for functionality
- **Warehouses:** Use dedicated warehouses with auto-suspend for cost control

## Observability and Evaluation

- Use AI Observability to capture traces of agent reasoning, tool invocations, and outcomes
- Employ golden questions and assertions; compare model/tool variants and track regression
- Monitor tool selection accuracy (is agent picking right tool?)
- Track flagging accuracy (are thresholds applied correctly?)

## Cost and Latency

- Prefer cached retrieval; restrict tool invocations per turn
- Control token budgets and cap output tokens; fail fast on oversized requests
- Monitor costs by agent and by tool type
- Optimize expensive tools (multiple Cortex Analyst calls) vs cheaper alternatives

### Dedicated Warehouses for Cortex Analyst Tools

**Best Practice:** Configure a dedicated warehouse for each agent's Cortex Analyst tools:

```yaml
# Agent: Investment Analyst
Cortex Analyst Tool: portfolio_analyzer
Warehouse: AGENT_PORTFOLIO_WH    # Dedicated for cost tracking
Query Timeout: 120

# Agent: Risk Analyst  
Cortex Analyst Tool: risk_analyzer
Warehouse: AGENT_RISK_WH         # Separate warehouse for isolation
Query Timeout: 180
```

**Benefits:**
- **Cost Attribution:** Track compute costs per agent in Account Usage
- **Performance Isolation:** Queries don't compete with other workloads
- **Sizing Control:** Right-size warehouse per agent's query complexity
- **Auto-Suspend:** Configure aggressive auto-suspend (60s) for cost savings

**Warehouse Setup Pattern:**
```sql
CREATE WAREHOUSE IF NOT EXISTS AGENT_ANALYTICS_WH
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Dedicated warehouse for analytics agent Cortex Analyst tools';

GRANT USAGE ON WAREHOUSE AGENT_ANALYTICS_WH TO ROLE AGENT_RUNNER;
```

**Cost Monitoring Query:**
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

-- Example:
SHOW VIEWS LIKE 'PORTFOLIO_VIEW' IN SCHEMA ANALYTICS.SEMANTIC;

-- 2. Grant SELECT access to agent role
GRANT SELECT ON VIEW {DATABASE}.{SCHEMA}.{VIEW_NAME} TO ROLE agent_runner;

-- Example:
GRANT SELECT ON VIEW ANALYTICS.SEMANTIC.PORTFOLIO_VIEW TO ROLE agent_runner;

-- 3. Verify grant was applied
SHOW GRANTS TO ROLE agent_runner;

-- 4. Test access
USE ROLE agent_runner;
SELECT * FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW LIMIT 1;
```

### Error: "Tool returned no results" or "Empty response"

**Cause:** Tool configured but underlying data empty, filters too restrictive, or query logic incorrect

**Solutions:**
```sql
-- 1. Test tool independently (component testing)
-- For Cortex Analyst tool:
SELECT * FROM {SEMANTIC_VIEW} LIMIT 10;

-- For Cortex Search tool:
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    '{SERVICE_NAME}',
    '{"query": "test", "limit": 10}'
);

-- 2. Verify data exists in underlying tables
SELECT COUNT(*) FROM {SEMANTIC_VIEW};

-- 3. Check for overly restrictive filters
-- Review metadata filters in search queries
-- Review WHERE clauses in semantic views

-- 4. Test with broader query
-- Start with simple query, then add filters incrementally
```

### Error: "Agent selected wrong tool" or "Incorrect tool invocation"

**Cause:** Overlapping tool descriptions, vague when-to-use guidance, or unclear planning instructions

**Solutions:**
1. **Review Tool Descriptions** (see Section 2.4 - Avoiding Overlapping Tools)
   - Ensure each tool has distinct use case
   - Add explicit trigger words to descriptions
   - Example: "Use for quantitative analysis (numbers, percentages)" vs "Use for qualitative research (opinions, commentary)"

2. **Update Planning Instructions** (see Section 4)
   - Add clearer tool selection classification logic
   - Include explicit examples of which queries map to which tools
   - Test with example queries before deployment

3. **Validation Script:**
```python
# Test tool selection logic
test_queries = [
    ("What are my top 10 holdings?", "expected_tool: portfolio_analyzer"),
    ("What does research say about AAPL?", "expected_tool: search_research_reports"),
    ("Show sector allocation", "expected_tool: portfolio_analyzer")
]

for query, expected in test_queries:
    result = agent.query(query)
    print(f"Query: {query}")
    print(f"Tool used: {result.tool_used}")
    print(f"Expected: {expected}")
    assert result.tool_used == expected.split(": ")[1]
```

### Error: "Permission denied" on Cortex function

**Cause:** Missing USAGE grants on Cortex functions (COMPLETE, SEARCH_PREVIEW, ANALYST, etc.)

**Solutions:**
```sql
-- Grant USAGE on all required Cortex functions
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.SEARCH_PREVIEW TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.SUMMARIZE TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.ANALYST TO ROLE agent_runner;

-- Verify grants
SHOW GRANTS TO ROLE agent_runner;

-- Test function access
USE ROLE agent_runner;
SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', 'test');
```

### Error: "Search service not found" or "Service inaccessible"

**Cause:** Missing USAGE grant on Cortex Search service

**Solutions:**
```sql
-- 1. Verify service exists
SHOW CORTEX SEARCH SERVICES IN SCHEMA {DATABASE}.{SCHEMA};

-- Example:
SHOW CORTEX SEARCH SERVICES IN SCHEMA DOCS.SEARCH;

-- 2. Grant USAGE on service
GRANT USAGE ON CORTEX SEARCH SERVICE {DATABASE}.{SCHEMA}.{SERVICE_NAME} TO ROLE agent_runner;

-- Example:
GRANT USAGE ON CORTEX SEARCH SERVICE DOCS.SEARCH.research_reports_service TO ROLE agent_runner;

-- 3. Verify grant
SHOW GRANTS TO ROLE agent_runner;

-- 4. Test access
USE ROLE agent_runner;
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{"query": "test", "limit": 1}'
);
```

### Error: "Flagging logic not working" or "Thresholds not applied"

**Cause:** Flagging logic placed in semantic view instead of agent response instructions

**Solution:**
- **Review:** Ensure flagging logic is in Agent Response Instructions (see Section 5)
- **NEVER:** Put flagging/threshold logic in semantic view custom instructions
- **Correct Pattern:**
  - Semantic View: Calculate accurate position_weight
  - Agent Response Instructions: "When position_weight > 6.5%, flag with WARNING"

## Cortex Agent Plan
- Archetype: <Multi-Domain Analytics / Single-Domain / Research / Hybrid>
- Objective: <clear objective>
- Model: <smallest sufficient model>
- Grounding: <semantic views / indices>
- Tools (allowlist):
  - Cortex Analyst: [analyst_tool_1, analyst_tool_2]
  - Cortex Search: [search_tool_1, search_tool_2]
- Planning Logic: <tool selection strategy>
- Response Instructions: <flagging thresholds, tone, format>
- RBAC: <roles/allowed objects>
- Cost/Latency: <budgets, caps>
- Testing: <component + integration approach>
- Evaluation: <gold Qs, assertions>

## Agent Configuration
- System prompt: <summary>
- Tool descriptions: <when-to-use guidance>
- Planning instructions: <explicit tool selection logic>
- Response instructions: <flagging logic, formatting>
- Observability: <traces/metrics enabled>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Deploying Agents Without Role-Based Access Control

**Problem:** Creating agents with unrestricted access to all semantic views and search services, allowing any user to query sensitive data regardless of their role or permissions.

**Why It Fails:** Violates data governance and compliance requirements, exposes confidential information to unauthorized users, creates audit and security risks, and fails regulatory requirements for data access controls.

**Correct Pattern:**
```sql
-- BAD: No RBAC restrictions
CREATE CORTEX AGENT my_agent
  TOOLS = (portfolio_analyzer, risk_analyzer, search_all_docs);

-- GOOD: Role-based access with allowed objects
CREATE CORTEX AGENT portfolio_agent_restricted
  TOOLS = (portfolio_analyzer)
  ALLOWED_OBJECTS = (
    'DB.SCHEMA.PUBLIC_HOLDINGS_VIEW',
    'DB.SCHEMA.PUBLIC_PERFORMANCE_VIEW'
  )
  ALLOWED_ROLES = ('PORTFOLIO_VIEWER', 'ANALYST');

-- Users in PORTFOLIO_VIEWER role can only access public views
-- Sensitive PII and trading data remain restricted
```

### Anti-Pattern 2: Skipping Component Testing Before Integration Testing

**Problem:** Testing the full agent end-to-end without first validating individual tools (Cortex Analyst, Cortex Search) work correctly in isolation.

**Why It Fails:** When integration tests fail, impossible to determine if the issue is in the semantic view, search service, agent configuration, or tool integration. Wastes debugging time and makes root cause analysis difficult.

**Correct Pattern:**
```python
# BAD: Only integration testing
def test_agent():
    response = agent.query("What are top holdings?")
    assert "AAPL" in response  # Fails - but why?

# GOOD: Component testing first, then integration
def test_cortex_analyst_tool_directly():
    # Test semantic view + Cortex Analyst in isolation
    result = session.sql("""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'analyst_tool_name',
            'What are top 5 holdings?'
        )
    """).collect()
    assert "AAPL" in result[0][0]  # Validates tool works

def test_cortex_search_tool_directly():
    # Test search service in isolation
    result = session.sql("""
        SELECT SNOWFLAKE.CORTEX.SEARCH(
            'search_service_name',
            'portfolio strategy'
        )
    """).collect()
    assert len(result) > 0  # Validates search works

def test_agent_integration():
    # Now test full agent with known-good tools
    response = agent.query("What are top holdings?")
    assert "AAPL" in response  # If fails, issue is agent config
```

### Anti-Pattern 3: Ignoring Cost and Latency Budgets in Production

**Problem:** Deploying agents without query cost limits, timeout settings, or latency monitoring, allowing unbounded compute usage and slow user experiences.

**Why It Fails:** Agents can generate expensive queries that consume credits rapidly, queries may hang indefinitely causing poor UX, and lack of monitoring prevents identifying performance issues until users complain.

**Correct Pattern:**
```sql
-- BAD: No cost or latency controls
CREATE CORTEX AGENT expensive_agent
  TOOLS = (analyst_tool_1, analyst_tool_2, search_all);

-- GOOD: Cost and latency budgets with monitoring
CREATE CORTEX AGENT optimized_agent
  TOOLS = (analyst_tool_1, analyst_tool_2, search_docs)
  WAREHOUSE = AGENT_WH  -- Dedicated warehouse for cost tracking
  QUERY_TIMEOUT = 30    -- 30 second timeout
  MAX_CREDITS_PER_QUERY = 0.5;  -- Cost cap per query

-- Monitor performance
SELECT 
  agent_name,
  AVG(query_latency_ms) as avg_latency,
  SUM(credits_used) as total_credits,
  COUNT(*) as query_count
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_HISTORY
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY agent_name
HAVING avg_latency > 10000  -- Flag agents >10s avg latency
ORDER BY total_credits DESC;
```
