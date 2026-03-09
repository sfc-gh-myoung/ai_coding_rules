# Snowflake Cortex Agents: Testing & RBAC

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:agent-testing, kw:agent-rbac
**Keywords:** agent testing, component testing, integration testing, agent RBAC, agent permissions, agent grants, cortex agent security, test agent, agent validation, agent role, agent access control
**TokenBudget:** ~3150
**ContextTier:** Low
**Depends:** 100-snowflake-core.md, 115-snowflake-cortex-agents-core.md, 115b-snowflake-cortex-agents-operations.md

## Scope

**What This Rule Covers:**
Testing strategies (component, integration, business scenario) and RBAC configuration for Snowflake Cortex Agents including grant patterns, verification queries, and least-privilege enforcement.

**When to Load This Rule:**
- Testing Cortex Agents (component and integration testing)
- Configuring RBAC and allowlists for agents
- Verifying agent permissions and grants
- Implementing least-privilege security for agents

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **115-snowflake-cortex-agents-core.md** - Core agent creation and tool configuration
- **115b-snowflake-cortex-agents-operations.md** - Operations overview

**Related:**
- **107-snowflake-security-governance.md** - Security and governance patterns

### External Documentation

- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents) - Agent concepts, tools, and setup

## Contract

### Inputs and Prerequisites

- Agent created and configured (see 115-snowflake-cortex-agents-core.md)
- Tools defined (Cortex Analyst, Cortex Search)
- Role strategy established

### Mandatory

- Component test each tool independently before integration testing
- Configure RBAC with least-privilege grants
- Verify grants with test queries before deployment

### Forbidden

- Testing only end-to-end without component testing first
- Deploying agents without role-based access control
- Granting broader permissions than required

### Execution Steps

1. Component test each tool independently
2. Integration test tool combinations
3. Run business scenario tests
4. Configure RBAC grants (database, schema, views, services, functions, warehouse)
5. Verify grants with test queries
6. Apply least-privilege principles

### Output Format

- Test patterns (Python and SQL)
- RBAC grant statements
- Verification queries

### Validation

- All component tests pass independently
- Integration tests pass for tool combinations
- RBAC grants verified with test queries
- Least-privilege enforced

### Design Principles

- Test tools independently before integration
- Enforce least-privilege RBAC and allowlists
- Verify all grants with test queries before deployment
- Separate testing phases: component, integration, business scenario

### Post-Execution Checklist

- [ ] Component tests pass for each tool
- [ ] Integration tests pass for tool combinations
- [ ] Business scenario tests pass
- [ ] RBAC grants configured
- [ ] Grants verified with test queries
- [ ] Least-privilege enforced

## Testing & Validation Patterns

### Component Testing (Test Tools Independently)

Before integration, verify each tool works correctly:

**Testing Cortex Analyst Tools:**
```python
def test_analyst_tool(session, semantic_view):
    """Verify Cortex Analyst tool responds correctly"""
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
def test_search_tool(session, service_name):
    """Verify Cortex Search tool responds correctly"""
    result = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
            '{service_name}',
            '{{"query": "test", "limit": 1}}'
        )
    """).collect()
    print(f"Search tool returned results")
    return len(result) > 0
```

### Integration Testing (Test Tool Combinations)

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

### Business Scenario Testing

Test with realistic end-user queries:

```
# Portfolio Management Scenarios
"What are my largest positions in the Global Growth fund?"
"Show me technology sector exposure across all portfolios"
"Are there any concentration warnings I should be aware of?"

# Compliance Scenarios
"Check if any positions violate our 7% concentration policy"
"Find engagement notes for companies with ESG controversies"
```

### Validation Checklist

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

Performance & Cost:
- [ ] Query response times are acceptable
- [ ] Token usage is within budget
- [ ] Tool invocation counts are reasonable

## RBAC and Permissions

### Required Grants for Cortex Agents

**Database and Schema Access:**
```sql
GRANT USAGE ON DATABASE {DATABASE} TO ROLE agent_runner;
GRANT USAGE ON SCHEMA {DATABASE}.{SCHEMA} TO ROLE agent_runner;
```

**Semantic View Access (for Cortex Analyst tools):**
```sql
GRANT SELECT ON VIEW {DATABASE}.{SCHEMA}.{VIEW_NAME} TO ROLE agent_runner;
-- Or grant on all views in schema
GRANT SELECT ON ALL VIEWS IN SCHEMA {DATABASE}.{SCHEMA} TO ROLE agent_runner;
```

**Cortex Search Service Access:**
```sql
GRANT USAGE ON CORTEX SEARCH SERVICE {DATABASE}.{SCHEMA}.{SERVICE_NAME} TO ROLE agent_runner;
```

**Cortex Function Access:**
```sql
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.SEARCH_PREVIEW TO ROLE agent_runner;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.ANALYST TO ROLE agent_runner;
```

**Warehouse Access:**
```sql
GRANT USAGE ON WAREHOUSE {WAREHOUSE_NAME} TO ROLE agent_runner;
```

### Verification Queries

```sql
-- Check all grants for agent role
SHOW GRANTS TO ROLE agent_runner;

-- Switch to agent role and test access
USE ROLE agent_runner;

-- Test semantic view access
SELECT COUNT(*) FROM {DATABASE}.{SCHEMA}.{VIEW_NAME};

-- Test Cortex Search service
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    '{SERVICE_NAME}',
    '{"query": "test", "limit": 1}'
);

-- Test Cortex function
SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', 'test');
```

### Principle of Least Privilege

- **Agents:** Only access tools needed for specific use case
- **Tools:** Only access data appropriate for their domain
- **Roles:** Grant minimum permissions required for functionality
- **Warehouses:** Use dedicated warehouses with auto-suspend for cost control

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Testing Only End-to-End Without Component Tests**

**Problem:** Developers skip component testing and go straight to asking the agent full natural-language questions. When the agent returns wrong answers, they cannot tell whether the issue is in the underlying data (semantic view returns no rows), the tool configuration (search service misconfigured), the tool selection logic (agent picked the wrong tool), or the response synthesis (agent hallucinated despite correct tool output). Debugging becomes trial-and-error prompt tweaking.

**Correct Pattern:** Test each tool independently first. Query the semantic view directly with SQL to confirm it returns expected data. Call `SEARCH_PREVIEW` on each Cortex Search service to verify document retrieval. Only after all component tests pass, move to integration testing where you verify the agent selects the correct tool for different query types (quantitative vs. qualitative vs. mixed). This layered approach isolates failures to a specific component.

```python
# Wrong: Jumping straight to end-to-end agent testing
def test_agent():
    response = agent.query("What are my top holdings?")
    assert "holdings" in response  # Fails — but WHY?
    # Is the semantic view empty? Search service down? Wrong tool picked?

# Correct: Component-first testing isolates failures
def test_semantic_view_returns_data(session):
    """Step 1: Verify the data source works independently."""
    rows = session.sql("""
        SELECT * FROM ANALYTICS.PORTFOLIO.HOLDINGS_VIEW
        ORDER BY position_weight DESC LIMIT 5
    """).collect()
    assert len(rows) > 0, "Semantic view returned no data"
    assert rows[0]["POSITION_WEIGHT"] > 0, "Weights should be positive"

def test_search_service_returns_docs(session):
    """Step 2: Verify search tool works independently."""
    result = session.sql("""
        SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
            'ANALYTICS.RESEARCH.REPORT_SEARCH',
            '{"query": "technology sector outlook", "limit": 3}'
        )
    """).collect()
    assert len(result) > 0, "Search service returned no results"

def test_agent_integration():
    """Step 3: Only after component tests pass, test the agent."""
    response = agent.query("What are my top holdings?")
    assert response.tool_used == "portfolio_analyzer"
    assert len(response.text) > 0
```

**Anti-Pattern 2: Granting ACCOUNTADMIN or Overly Broad Roles to Agents**

**Problem:** To "get things working quickly," developers run agents under ACCOUNTADMIN or grant `SELECT ON ALL TABLES IN DATABASE` to the agent role. This violates least-privilege, exposes sensitive data the agent should never access (PII tables, salary data, audit logs), and creates a security risk if agent prompts are manipulated to query unintended tables.

**Correct Pattern:** Create a dedicated `agent_runner` role with granular grants: `USAGE` on specific databases/schemas, `SELECT` on only the semantic views and tables the agent needs, and `USAGE` on specific Cortex Search services. Verify grants with test queries under the agent role before deployment. Review grants periodically and revoke any that are no longer needed.

```sql
-- Wrong: Overly broad access — agent can read ANY table
GRANT ROLE ACCOUNTADMIN TO USER agent_service_user;
-- Or almost as bad:
GRANT SELECT ON ALL TABLES IN DATABASE ANALYTICS TO ROLE agent_runner;

-- Correct: Granular least-privilege grants for specific resources
CREATE ROLE IF NOT EXISTS agent_portfolio_runner;

GRANT USAGE ON DATABASE ANALYTICS TO ROLE agent_portfolio_runner;
GRANT USAGE ON SCHEMA ANALYTICS.PORTFOLIO TO ROLE agent_portfolio_runner;

-- Only the specific views this agent needs
GRANT SELECT ON VIEW ANALYTICS.PORTFOLIO.HOLDINGS_VIEW TO ROLE agent_portfolio_runner;
GRANT SELECT ON VIEW ANALYTICS.PORTFOLIO.SECTOR_VIEW TO ROLE agent_portfolio_runner;

-- Only the specific search service this agent uses
GRANT USAGE ON CORTEX SEARCH SERVICE ANALYTICS.RESEARCH.REPORT_SEARCH
    TO ROLE agent_portfolio_runner;

GRANT USAGE ON WAREHOUSE AGENT_PORTFOLIO_WH TO ROLE agent_portfolio_runner;

-- Verify: test access under the restricted role
USE ROLE agent_portfolio_runner;
SELECT COUNT(*) FROM ANALYTICS.PORTFOLIO.HOLDINGS_VIEW;  -- Should succeed
SELECT COUNT(*) FROM HR.PRIVATE.SALARY_DATA;  -- Should fail (no grant)
```

**Anti-Pattern 3: Not Testing Tool Selection with Ambiguous Queries**

**Problem:** Developers only test with clearly quantitative queries ("show top 10 holdings") or clearly qualitative queries ("find research on AAPL") but never test with ambiguous or mixed queries. In production, users ask questions like "why is tech exposure so high?" which requires both data retrieval (Analyst) and contextual search (Search). The agent picks only one tool and returns an incomplete answer.

**Correct Pattern:** Include ambiguous and mixed-intent queries in your test suite. Test queries that require multiple tools working together, queries with implicit data needs, and queries that could reasonably map to more than one tool. Verify the agent uses the correct combination of tools and synthesizes a coherent response. Adjust tool descriptions and planning instructions until tool selection is reliable for edge cases.

```python
# Wrong: Only testing unambiguous single-tool queries
test_queries = [
    "What are the top 10 holdings?",       # Obviously Analyst
    "Find research reports on AAPL",        # Obviously Search
]

# Correct: Include ambiguous and mixed-intent queries
test_queries = [
    # Clear single-tool (baseline)
    ("What are the top 10 holdings by weight?", ["portfolio_analyzer"]),
    ("Find latest research on AAPL", ["search_research_reports"]),

    # Ambiguous — could use either tool
    ("Why is tech exposure so high?", ["portfolio_analyzer", "search_research_reports"]),

    # Mixed — requires BOTH tools for a complete answer
    ("Show top holdings and their latest analyst ratings",
     ["portfolio_analyzer", "search_research_reports"]),

    # Implicit data need — sounds qualitative but needs data
    ("Are there any concentration risks I should worry about?",
     ["portfolio_analyzer"]),
]

for query, expected_tools in test_queries:
    result = agent.query(query)
    tools_used = result.tools_used  # List of tools invoked
    for tool in expected_tools:
        assert tool in tools_used, (
            f"Query '{query}' expected tool '{tool}' "
            f"but agent used: {tools_used}"
        )
```
