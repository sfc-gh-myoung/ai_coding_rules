# Snowflake Cortex Agents: Operations & Security

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** observability, evaluation, cost management, error troubleshooting, agent security, test agent, agent permissions, agent monitoring, agent evaluation, agent costs, debug agent, agent logs, agent trace, agent security policies
**TokenBudget:** ~3650
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md, rules/115-snowflake-cortex-agents-core.md, rules/111-snowflake-observability-core.md

## Purpose
Provide comprehensive operational patterns for Cortex Agents including testing strategies, RBAC configuration, observability, cost management, and error troubleshooting.

## Rule Scope

Testing, RBAC, allowlists, observability, evaluation, cost optimization, error resolution

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Test components independently** - Tools before agents
- **Enforce RBAC and allowlists** - Least-privilege access
- **Add evaluation framework** - Gold questions, assertions
- **Monitor costs and latency** - Track token usage
- **Trace agent execution** - Use AI Observability

**Quick Checklist:**
- [ ] Component tests pass (tools work independently)
- [ ] Integration tests pass (agent orchestration works)
- [ ] RBAC configured with least privilege
- [ ] Allowlists enforced (models, tools, data)
- [ ] Evaluation framework in place
- [ ] Observability enabled (tracing, metrics)
- [ ] Cost monitoring active

## Contract

<contract>
<inputs_prereqs>
Agent created and configured, tools defined, role strategy established
</inputs_prereqs>

<mandatory>
Testing frameworks, RBAC commands, AI Observability, evaluation tools
</mandatory>

<forbidden>
Unbounded tool execution, privilege escalation
</forbidden>

<steps>
1) Component testing 2) Integration testing 3) RBAC enforcement 4) Add observability 5) Monitor costs
</steps>

<output_format>
Test patterns, RBAC configs, observability queries, troubleshooting steps
</output_format>

<validation>
Tests pass; RBAC enforced; traces captured; costs within budget
</validation>

<design_principles>
- Test tools independently before integration
- Enforce least-privilege RBAC and allowlists
- Add evaluation (gold questions, assertions) and tracing
- Monitor costs, latency, and quality continuously
- Use AI Observability for debugging and optimization
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

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

## Post-Execution Checklist
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

## Validation
- **Success checks:** Component tests pass; integration tests pass; evaluation meets targets; tool selection logic works correctly; flagging applies consistently; traces show bounded tool use; costs stable
- **Negative tests:** Prompt injections fail; unauthorized tool/data access blocked; oversized prompts rejected; overlapping tools don't confuse agent; flagging in semantic views flagged in code review

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

## References

### External Documentation
- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents) - Agent concepts, tools, and setup
- [AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability) - Tracing, evaluations, comparisons
- [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) - Natural language to SQL
- [Cortex Search](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search) - Semantic search service

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **Semantic Views Integration**: `rules/106c-snowflake-semantic-views-integration.md` - Semantic view design and Analyst tool configuration
- **Cortex Search**: `rules/116-snowflake-cortex-search.md` - Search service setup and tool integration
- **Semantic Views**: `rules/106-snowflake-semantic-views-core.md`
- **Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`
- **Observability**: `rules/111-snowflake-observability-core.md`

## 6. Testing & Validation Patterns

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

## 7. RBAC and Permissions

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

## 8. Observability and Evaluation

- Use AI Observability to capture traces of agent reasoning, tool invocations, and outcomes
- Employ golden questions and assertions; compare model/tool variants and track regression
- Monitor tool selection accuracy (is agent picking right tool?)
- Track flagging accuracy (are thresholds applied correctly?)

## 9. Cost and Latency

- Prefer cached retrieval; restrict tool invocations per turn
- Control token budgets and cap output tokens; fail fast on oversized requests
- Monitor costs by agent and by tool type
- Optimize expensive tools (multiple Cortex Analyst calls) vs cheaper alternatives

## 10. Common Errors and Solutions

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
