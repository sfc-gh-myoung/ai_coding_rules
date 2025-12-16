# Example Prompt 06: Snowflake Cortex Agent (Hybrid)

## The Prompt

```
Task: Create a Cortex Agent that combines quantitative analysis with document search
Semantic View: ANALYTICS.SEMANTIC.SEM_SALES_METRICS
Search Service: DOCS.SEARCH.PRODUCT_DOCS_SERVICE
```

## What This Helps

AI assistants will automatically:
- Detect "Cortex Agent" keyword → Load `rules/115-snowflake-cortex-agents-core.md`
- Detect "Semantic View" keyword → Load `rules/106-snowflake-semantic-views-core.md`
- Detect "Search Service" keyword → Load `rules/116-snowflake-cortex-search.md`
- Understand hybrid agent pattern requiring multiple tool types
- Apply correct CREATE CORTEX AGENT syntax with TOOLS, PLANNING_INSTRUCTIONS, RESPONSE_INSTRUCTIONS

## Why It's Good

**Technology clear (Snowflake):** Explicitly mentions Cortex Agent with both tool types, triggering all relevant AI rules

**Tools specified:** Provides exact semantic view and search service names, enabling accurate agent configuration

**Hybrid pattern implied:** Two different tool types signals need for planning instructions that handle both quantitative and qualitative queries

**Minimal yet complete:** Provides exactly enough information for AI to generate valid Cortex Agent DDL

## Expected Output Structure

The AI should generate DDL following this pattern:

```sql
-- Create hybrid Cortex Agent with both Analyst and Search tools
CREATE OR REPLACE CORTEX AGENT ANALYTICS.AGENTS.SALES_INSIGHTS_AGENT
  COMMENT = 'Hybrid agent combining sales metrics analysis with product documentation search'
  AS
    TOOLS = [
      'ANALYTICS.SEMANTIC.SEM_SALES_METRICS',
      'DOCS.SEARCH.PRODUCT_DOCS_SERVICE'
    ]
    PLANNING_INSTRUCTIONS = $$
    You are a sales insights analyst with access to both quantitative data and product documentation.

    Query Classification:
    1. QUANTITATIVE queries (numbers, metrics, calculations) → Use SEM_SALES_METRICS
       Examples: "What was Q4 revenue?", "Top 10 customers by sales", "Revenue trend"
    2. QUALITATIVE queries (documentation, explanations, how-to) → Use PRODUCT_DOCS_SERVICE
       Examples: "How does the pricing model work?", "What features are in the enterprise tier?"
    3. MIXED queries → Use SEM_SALES_METRICS first for data, then PRODUCT_DOCS_SERVICE for context

    Tool Selection Rules:
    - Numbers, percentages, rankings, trends → Semantic View (Cortex Analyst)
    - Explanations, policies, documentation → Search Service (Cortex Search)
    - "Why" questions about data → Use both: get data first, then search for context
    $$
    RESPONSE_INSTRUCTIONS = $$
    Format your response as follows:

    **Summary:** [1-2 sentence direct answer]

    **Details:**
    - [Key finding or information with specific data]
    - [Supporting context from documentation if applicable]

    **Sources:**
    - Data: [Semantic view queried, time period]
    - Documentation: [Document title, date] (if used)

    When combining data and documentation:
    1. Present quantitative findings first
    2. Add qualitative context from documentation
    3. Clearly distinguish between data facts and documentation references
    $$;

-- Verify agent creation
SHOW CORTEX AGENTS IN SCHEMA ANALYTICS.AGENTS;

-- Test with quantitative query
SELECT *
FROM TABLE(AGENT_QUERY(
  'ANALYTICS.AGENTS.SALES_INSIGHTS_AGENT',
  'What was the total revenue last quarter?'
));

-- Test with qualitative query
SELECT *
FROM TABLE(AGENT_QUERY(
  'ANALYTICS.AGENTS.SALES_INSIGHTS_AGENT',
  'How does our pricing model work?'
));

-- Test with mixed query
SELECT *
FROM TABLE(AGENT_QUERY(
  'ANALYTICS.AGENTS.SALES_INSIGHTS_AGENT',
  'Why did enterprise tier revenue increase? What features drive adoption?'
));

-- Grant access
GRANT USAGE ON CORTEX AGENT ANALYTICS.AGENTS.SALES_INSIGHTS_AGENT TO ROLE analyst_role;
```

## Key Rules Applied

1. **TOOLS array:** Lists both semantic view and search service as tools
2. **PLANNING_INSTRUCTIONS:** Guides tool selection based on query type (quantitative vs qualitative)
3. **RESPONSE_INSTRUCTIONS:** Formats output with clear source attribution
4. **Query classification:** Explicit rules for routing queries to correct tool
5. **Mixed query handling:** Instructions for combining both tools
6. **Verify and test:** Test all three query types (quantitative, qualitative, mixed)

