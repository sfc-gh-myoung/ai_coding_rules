# Snowflake Cortex Agents: Operations & Security

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:agent-operations
**Keywords:** agent operations, agent security, agent monitoring, agent evaluation, agent costs, debug agent, agent troubleshooting, agent security policies
**TokenBudget:** ~2800
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 115-snowflake-cortex-agents-core.md, 111-snowflake-observability-core.md
**Companions:** 115c-snowflake-cortex-agents-testing.md, 115d-snowflake-cortex-agents-observability.md

## Scope

**What This Rule Covers:**
Operational patterns for Cortex Agents: investigation protocol, output format examples, agent plan/configuration templates, and anti-patterns for RBAC, testing, and cost management.

**When to Load This Rule:**
- Planning and configuring Cortex Agents
- Reviewing agent anti-patterns (RBAC, testing, cost)
- Using agent plan and configuration templates
- For testing and RBAC details, see **115c-snowflake-cortex-agents-testing.md**
- For observability, cost monitoring, and error troubleshooting, see **115d-snowflake-cortex-agents-observability.md**

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

Investigation protocol, output format examples, agent plan/configuration templates, anti-patterns

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

See Anti-Patterns section below for detailed patterns covering RBAC (Anti-Pattern 1), component testing (Anti-Pattern 2), and cost/latency budgets (Anti-Pattern 3).

**Quick Reference - Common Mistakes:**
- Putting flagging/threshold logic in semantic views instead of agent instructions
- Overlapping tool descriptions that confuse tool selection
- Missing when-to-use guidance in tool descriptions
- Testing only end-to-end without component testing first
- Vague planning instructions like "use the best tool"

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

## Testing, RBAC, Observability, Cost Management, and Troubleshooting

> **See companion rules for detailed operational patterns:**
> - **115c-snowflake-cortex-agents-testing.md** — Component testing, integration testing, business scenario testing, validation checklists, RBAC grants, verification queries, and least-privilege patterns
> - **115d-snowflake-cortex-agents-observability.md** — AI Observability, agent health checks, evaluation frameworks, cost/latency management, dedicated warehouses, cost monitoring queries, and common error solutions (semantic view not found, empty response, wrong tool selection, permission denied, search service errors, flagging logic issues)

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

**Why It Fails:** Violates data governance; exposes confidential information to unauthorized users; creates audit and security risks.

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

**Why It Fails:** When integration tests fail, impossible to determine which component is broken. Wastes debugging time.

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

**Why It Fails:** Agents can generate expensive queries that consume credits rapidly; queries may hang indefinitely causing poor UX.

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
