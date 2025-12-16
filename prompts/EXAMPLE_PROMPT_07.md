# Example Prompt 07: Snowflake Cortex AI Stack (End-to-End)

## The Prompt

```
Task: Create complete Cortex AI stack with semantic view, search service, and hybrid agent
Source Tables:
  - PROD.SALES.ORDERS (order_id, customer_id, order_date, amount, product_id)
  - PROD.SALES.CUSTOMERS (customer_id, customer_name, region)
  - DOCS.RAW.PRODUCT_DOCS (doc_id, content, category, author, published_date)
Target Schema: ANALYTICS.AI
```

## What This Helps

AI assistants will automatically:
- Detect "semantic view" → Load `rules/106-snowflake-semantic-views-core.md`
- Detect "search service" → Load `rules/116-snowflake-cortex-search.md`
- Detect "agent" → Load `rules/115-snowflake-cortex-agents-core.md`
- Detect Snowflake context → Load `rules/100-snowflake-core.md`
- Understand end-to-end stack requiring all three components
- Apply correct DDL syntax for each component in dependency order

## Why It's Good

**Complete stack specified:** All three components (semantic view, search, agent) in one request

**Source tables with columns:** Exact table paths and columns for both quantitative and document data

**Target schema defined:** Clear deployment location for all objects

**Dependency order implied:** AI understands semantic view and search must exist before agent

## Expected Output Structure

The AI should generate DDL in dependency order:

```sql
--------------------------------------------------------------------------------
-- STEP 1: Create Semantic View for Cortex Analyst (quantitative data)
--------------------------------------------------------------------------------
CREATE OR REPLACE SEMANTIC VIEW ANALYTICS.AI.SEM_SALES_ANALYTICS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id),
    customers AS PROD.SALES.CUSTOMERS
      PRIMARY KEY (customer_id)
  )
  RELATIONSHIPS (
    orders_to_customers AS orders(customer_id) REFERENCES customers(customer_id)
  )
  DIMENSIONS (
    orders.order_date AS order_date
      WITH SYNONYMS ('date', 'sale date', 'transaction date')
      COMMENT = 'Date of the order',
    customers.customer_name AS customer_name
      WITH SYNONYMS ('customer', 'client', 'buyer')
      COMMENT = 'Customer full name',
    customers.region AS region
      WITH SYNONYMS ('area', 'territory', 'location')
      COMMENT = 'Customer geographic region'
  )
  METRICS (
    orders.total_revenue AS SUM(amount)
      WITH SYNONYMS ('revenue', 'sales', 'income')
      COMMENT = 'Total sales revenue',
    orders.order_count AS COUNT(*)
      WITH SYNONYMS ('number of orders', 'total orders')
      COMMENT = 'Count of orders',
    orders.avg_order_value AS AVG(amount)
      WITH SYNONYMS ('average order', 'AOV', 'mean order value')
      COMMENT = 'Average order value'
  )
  COMMENT = 'Sales analytics semantic view for Cortex Analyst';

-- Verify semantic view
SHOW SEMANTIC VIEWS IN SCHEMA ANALYTICS.AI;

--------------------------------------------------------------------------------
-- STEP 2: Create Cortex Search Service (document retrieval)
--------------------------------------------------------------------------------
CREATE CORTEX SEARCH SERVICE IF NOT EXISTS ANALYTICS.AI.PRODUCT_DOCS_SEARCH
ON content
ATTRIBUTES doc_id, category, author, published_date
WAREHOUSE = COMPUTE_WH
TARGET_LAG = '1 day'
AS (
  SELECT
    doc_id,
    content,
    category,
    author,
    published_date
  FROM DOCS.RAW.PRODUCT_DOCS
  WHERE content IS NOT NULL
    AND LENGTH(content) > 50
);

-- Verify search service
SHOW CORTEX SEARCH SERVICES IN SCHEMA ANALYTICS.AI;

-- Test search
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
  'ANALYTICS.AI.PRODUCT_DOCS_SEARCH',
  '{"query": "pricing", "limit": 3}'
);

--------------------------------------------------------------------------------
-- STEP 3: Create Hybrid Cortex Agent (combines both tools)
--------------------------------------------------------------------------------
CREATE OR REPLACE CORTEX AGENT ANALYTICS.AI.SALES_INSIGHTS_AGENT
  COMMENT = 'Hybrid agent for sales analytics and product documentation'
  AS
    TOOLS = [
      'ANALYTICS.AI.SEM_SALES_ANALYTICS',
      'ANALYTICS.AI.PRODUCT_DOCS_SEARCH'
    ]
    PLANNING_INSTRUCTIONS = $$
    You are a sales insights analyst with access to quantitative sales data and product documentation.

    TOOL SELECTION:
    1. SEM_SALES_ANALYTICS (Cortex Analyst) - Use for:
       - Revenue, sales metrics, order counts
       - Customer analysis, regional breakdowns
       - Trends, rankings, calculations
       - Questions with numbers, percentages, comparisons

    2. PRODUCT_DOCS_SEARCH (Cortex Search) - Use for:
       - Product features, pricing information
       - How-to guides, documentation
       - Policy explanations, procedures
       - Questions about "how", "what is", "explain"

    3. BOTH TOOLS - Use together for:
       - "Why" questions (get data, then context)
       - Analysis requiring business context
       - Recommendations needing data + documentation

    EXECUTION ORDER:
    - For mixed queries: Run Analyst first (get numbers), then Search (get context)
    - Always cite which tool provided which information
    $$
    RESPONSE_INSTRUCTIONS = $$
    **Answer:** [Direct 1-2 sentence response]

    **Details:**
    - [Finding with specific data or documentation reference]
    - [Additional supporting information]

    **Sources:**
    - Data: SEM_SALES_ANALYTICS [time period if applicable]
    - Docs: [Document title] (if used)

    RULES:
    - Distinguish data facts from documentation references
    - Include specific numbers when available
    - Cite document sources by title
    $$;

-- Verify agent
SHOW CORTEX AGENTS IN SCHEMA ANALYTICS.AI;

--------------------------------------------------------------------------------
-- STEP 4: Grant Access
--------------------------------------------------------------------------------
-- Grant semantic view access
GRANT SELECT ON SEMANTIC VIEW ANALYTICS.AI.SEM_SALES_ANALYTICS TO ROLE analyst_role;

-- Grant search service access
GRANT USAGE ON CORTEX SEARCH SERVICE ANALYTICS.AI.PRODUCT_DOCS_SEARCH TO ROLE analyst_role;

-- Grant agent access
GRANT USAGE ON CORTEX AGENT ANALYTICS.AI.SALES_INSIGHTS_AGENT TO ROLE analyst_role;

--------------------------------------------------------------------------------
-- STEP 5: Test Agent with All Query Types
--------------------------------------------------------------------------------
-- Test quantitative query
SELECT * FROM TABLE(AGENT_QUERY(
  'ANALYTICS.AI.SALES_INSIGHTS_AGENT',
  'What was total revenue by region last quarter?'
));

-- Test qualitative query
SELECT * FROM TABLE(AGENT_QUERY(
  'ANALYTICS.AI.SALES_INSIGHTS_AGENT',
  'How does our enterprise pricing work?'
));

-- Test mixed query
SELECT * FROM TABLE(AGENT_QUERY(
  'ANALYTICS.AI.SALES_INSIGHTS_AGENT',
  'Why is the West region performing better? What products are driving growth?'
));
```

## Key Rules Applied

1. **Dependency order:** Semantic view → Search service → Agent (tools must exist first)
2. **Semantic view patterns:** TABLES, RELATIONSHIPS, DIMENSIONS, METRICS with SYNONYMS
3. **Search service patterns:** ON clause, ATTRIBUTES, TARGET_LAG, content validation
4. **Agent patterns:** TOOLS array, PLANNING_INSTRUCTIONS, RESPONSE_INSTRUCTIONS
5. **Tool selection logic:** Clear routing rules for quantitative vs qualitative queries
6. **Verification steps:** SHOW commands and test queries after each component
7. **Access grants:** Permissions for all three object types

