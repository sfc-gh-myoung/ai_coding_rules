# 106 Example: Semantic View (SQL DDL)

> **EXAMPLE FILE** - Reference implementation for `106-snowflake-semantic-views-core.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 106-snowflake-semantic-views-core.md
**Demonstrates:** Creating a semantic view using SQL DDL with comprehensive metadata
**Use When:** Setting up a semantic view for Cortex Analyst or as a Cortex Agent tool
**Version:** 1.0
**Last Validated:** 2026-01-23

## Prerequisites

- [ ] Snowflake account with Cortex Analyst feature enabled
- [ ] ACCOUNTADMIN or role with CREATE SEMANTIC VIEW privilege
- [ ] Base tables exist with data
- [ ] Understanding of business metrics and dimensions

## Implementation

```sql
-- Step 1: Verify source tables exist
SELECT COUNT(*) FROM my_db.my_schema.orders;
SELECT COUNT(*) FROM my_db.my_schema.customers;
SELECT COUNT(*) FROM my_db.my_schema.products;

-- Step 2: Create semantic view with comprehensive metadata
CREATE OR REPLACE SEMANTIC VIEW my_db.my_schema.sales_semantic_view
  COMMENT = 'Sales analytics semantic model for Cortex Analyst'
AS
SELECT
    -- Dimensions (GROUP BY candidates)
    o.order_id,
    o.order_date,
    DATE_TRUNC('month', o.order_date) AS order_month,
    DATE_TRUNC('quarter', o.order_date) AS order_quarter,
    DATE_TRUNC('year', o.order_date) AS order_year,
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.region,
    c.country,
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    
    -- Measures (aggregatable values)
    o.quantity,
    o.unit_price,
    o.discount,
    o.total_amount,
    o.total_amount - o.cost AS profit,
    o.cost
FROM my_db.my_schema.orders o
JOIN my_db.my_schema.customers c ON o.customer_id = c.customer_id
JOIN my_db.my_schema.products p ON o.product_id = p.product_id

-- Dimension definitions with semantic metadata
DIMENSIONS (
    order_id COMMENT 'Unique order identifier',
    order_date COMMENT 'Date the order was placed',
    order_month COMMENT 'Month of order (use for monthly aggregations)',
    order_quarter COMMENT 'Quarter of order (Q1, Q2, Q3, Q4)',
    order_year COMMENT 'Year of order',
    customer_id COMMENT 'Unique customer identifier',
    customer_name COMMENT 'Full name of customer',
    customer_segment COMMENT 'Customer segment: Consumer, Corporate, Home Office',
    region COMMENT 'Geographic region: East, West, Central, South',
    country COMMENT 'Country name',
    product_id COMMENT 'Unique product identifier',
    product_name COMMENT 'Product display name',
    category COMMENT 'Product category: Furniture, Office Supplies, Technology',
    subcategory COMMENT 'Product subcategory'
)

-- Measure definitions with aggregation hints
MEASURES (
    quantity COMMENT 'Number of units ordered' AGGREGATIONS (SUM, AVG),
    unit_price COMMENT 'Price per unit in USD' AGGREGATIONS (AVG),
    discount COMMENT 'Discount percentage applied (0-1 scale)' AGGREGATIONS (AVG),
    total_amount COMMENT 'Total order amount in USD' AGGREGATIONS (SUM, AVG, COUNT),
    profit COMMENT 'Profit = total_amount - cost' AGGREGATIONS (SUM, AVG),
    cost COMMENT 'Total cost of goods sold' AGGREGATIONS (SUM)
)

-- Semantic relationships
RELATIONSHIPS (
    orders_to_customers: orders.customer_id = customers.customer_id,
    orders_to_products: orders.product_id = products.product_id
)

-- Example verified queries (gold standard for testing)
VERIFIED_QUERIES (
    'What is total revenue by region?' AS $$
        SELECT region, SUM(total_amount) AS revenue
        FROM sales_semantic_view
        GROUP BY region
        ORDER BY revenue DESC
    $$,
    'Who are our top 10 customers by revenue?' AS $$
        SELECT customer_name, SUM(total_amount) AS total_revenue
        FROM sales_semantic_view
        GROUP BY customer_name
        ORDER BY total_revenue DESC
        LIMIT 10
    $$,
    'What was Q4 2025 revenue?' AS $$
        SELECT SUM(total_amount) AS q4_revenue
        FROM sales_semantic_view
        WHERE order_quarter = '2025-Q4'
    $$
);

-- Step 3: Grant appropriate access
GRANT USAGE ON SEMANTIC VIEW my_db.my_schema.sales_semantic_view TO ROLE analyst_role;

-- Step 4: Test semantic view
SELECT * FROM TABLE(SEMANTIC_VIEW('my_db.my_schema.sales_semantic_view')) LIMIT 5;
```

## Validation

```sql
-- Verify semantic view exists
SHOW SEMANTIC VIEWS LIKE 'sales_semantic_view' IN SCHEMA my_db.my_schema;

-- Test Cortex Analyst query
SELECT SNOWFLAKE.CORTEX.ANALYST(
    'my_db.my_schema.sales_semantic_view',
    'What is total revenue by region?'
);

-- Test verified query accuracy
-- Run the verified query directly and compare with Analyst result
SELECT region, SUM(total_amount) AS revenue
FROM my_db.my_schema.sales_semantic_view
GROUP BY region
ORDER BY revenue DESC;

-- Verify grants
SHOW GRANTS ON SEMANTIC VIEW my_db.my_schema.sales_semantic_view;
```

**Expected Result:**
- Semantic view created successfully with all metadata
- Cortex Analyst can answer questions using natural language
- Verified queries match expected SQL output
- Only authorized roles have access
