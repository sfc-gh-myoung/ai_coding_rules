# 115 Example: Cortex Agent Hybrid (SQL DDL)

> **EXAMPLE FILE** - Reference implementation for `115-snowflake-cortex-agents-core.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 115-snowflake-cortex-agents-core.md
**Demonstrates:** Hybrid agent combining Semantic View (Cortex Analyst) + Cortex Search for multi-tool orchestration
**Use When:** Building a Cortex Agent that requires both structured data queries and document search
**Version:** 1.0
**Last Validated:** 2026-01-23

## Prerequisites

- [ ] Snowflake account with Cortex features enabled
- [ ] ACCOUNTADMIN or role with CREATE CORTEX AGENT privilege
- [ ] Existing semantic view (see 106-semantic-view-ddl-example.md)
- [ ] Existing Cortex Search service (see 116-cortex-search-service-example.md)
- [ ] Verified role permissions: `SHOW GRANTS TO ROLE agent_role`

## Implementation

```sql
-- Step 1: Verify prerequisites (MANDATORY before agent creation)
SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;
-- Confirm: CORTEX_ENABLED_CROSS_REGION = true

-- Step 2: Test semantic view independently
SELECT * FROM TABLE(SEMANTIC_VIEW('my_db.my_schema.sales_semantic_view')) LIMIT 1;

-- Step 3: Test Cortex Search independently
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'my_db.my_schema.docs_search_service',
    '{"query": "test query", "columns": ["chunk"], "limit": 1}'
);

-- Step 4: Create the hybrid agent
CREATE OR REPLACE CORTEX AGENT my_hybrid_agent
  COMMENT = 'Sales analytics with document search'
  MODEL = 'claude-3-5-sonnet'
  TOOLS = (
    -- Tool 1: Structured data via Semantic View
    my_db.my_schema.sales_semantic_view,
    -- Tool 2: Document search via Cortex Search
    my_db.my_schema.docs_search_service
  )
  PLANNING_INSTRUCTIONS = $$
## Tool Selection Guidelines

**When to use sales_semantic_view:**
- Questions about sales metrics, revenue, customer counts
- Aggregations over time periods
- Comparisons between regions, products, or customer segments
- Any question requiring numerical analysis of business data

**When to use docs_search_service:**
- Questions about policies, procedures, or guidelines
- Searching for specific document content
- Finding reference materials or definitions
- Questions about "how to" or "what is the policy for"

**Orchestration Rules:**
1. Start with the most specific tool for the question
2. If structured data query returns no results, check if docs might have relevant context
3. Never call both tools simultaneously - sequential execution only
4. For compound questions, break into sub-questions and route appropriately

**Error Handling:**
- If a tool returns an error, report clearly and do not retry
- If results are empty, state "No data found" rather than guessing
$$
  RESPONSE_INSTRUCTIONS = $$
## Response Format

**For numerical answers:**
- Lead with the key metric or number
- Include time period and scope
- Add context from supporting data

**For document search:**
- Quote relevant passages with attribution
- Summarize key points
- Note if information may be outdated

**Flagging Rules:**
- Flag responses as APPROXIMATE if based on partial data
- Flag as POLICY_REFERENCE if citing company documents
- Never include raw SQL or internal identifiers in responses
$$;

-- Step 5: Grant usage to appropriate role
GRANT USAGE ON CORTEX AGENT my_hybrid_agent TO ROLE analyst_role;

-- Step 6: Test the agent
SELECT SNOWFLAKE.CORTEX.AGENT(
    'my_hybrid_agent',
    'What were total sales last quarter and what is our return policy?'
);
```

## Validation

```sql
-- Verify agent exists
SHOW CORTEX AGENTS LIKE 'my_hybrid_agent';

-- Test tool routing (structured data)
SELECT SNOWFLAKE.CORTEX.AGENT(
    'my_hybrid_agent',
    'What was revenue in Q4 2025?'
);

-- Test tool routing (document search)
SELECT SNOWFLAKE.CORTEX.AGENT(
    'my_hybrid_agent',
    'What is our refund policy for damaged items?'
);

-- Verify RBAC
SHOW GRANTS ON CORTEX AGENT my_hybrid_agent;
```

**Expected Result:**
- Agent responds to structured data questions using semantic view
- Agent responds to policy questions using Cortex Search
- Agent declines out-of-scope questions gracefully
- Grants show only intended roles have access
