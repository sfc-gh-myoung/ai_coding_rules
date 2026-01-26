# 106 Example: Semantic View with Verified Queries (YAML)

> **EXAMPLE FILE** - Reference implementation for `106-snowflake-semantic-views-core.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 106-snowflake-semantic-views-core.md
**Demonstrates:** YAML-based semantic model with verified queries (VQRs) for improved accuracy
**Use When:** Creating semantic views with complex business logic or requiring verified query responses
**Version:** 1.0
**Last Validated:** 2026-01-23

## Prerequisites

- [ ] Snowflake account with Cortex Analyst feature enabled
- [ ] Base tables exist with data
- [ ] Stage for storing YAML file (or use inline YAML)
- [ ] Understanding of verified query patterns

## Implementation

```yaml
# File: sales_semantic_model.yaml
# Upload to stage: PUT file://sales_semantic_model.yaml @my_db.my_schema.my_stage

name: sales_semantic_model
description: |
  Sales analytics semantic model for Cortex Analyst.
  Covers order metrics, customer analysis, and product performance.
  
tables:
  - name: orders
    base_table: my_db.my_schema.orders
    description: Order transactions with amounts and dates
    columns:
      - name: order_id
        description: Unique order identifier
        data_type: VARCHAR
        
      - name: order_date
        description: Date the order was placed
        data_type: DATE
        
      - name: customer_id
        description: Foreign key to customers table
        data_type: VARCHAR
        
      - name: product_id
        description: Foreign key to products table
        data_type: VARCHAR
        
      - name: quantity
        description: Number of units ordered
        data_type: NUMBER
        
      - name: total_amount
        description: Total order amount in USD
        data_type: NUMBER
        aggregations:
          - SUM
          - AVG
          - COUNT
          
      - name: profit
        description: Profit = total_amount - cost
        data_type: NUMBER
        aggregations:
          - SUM
          - AVG

  - name: customers
    base_table: my_db.my_schema.customers
    description: Customer master data
    columns:
      - name: customer_id
        description: Unique customer identifier
        data_type: VARCHAR
        
      - name: customer_name
        description: Full name of customer
        data_type: VARCHAR
        
      - name: region
        description: Geographic region (East, West, Central, South)
        data_type: VARCHAR
        synonyms:
          - area
          - territory
          
      - name: customer_segment
        description: Customer segment (Consumer, Corporate, Home Office)
        data_type: VARCHAR
        synonyms:
          - segment
          - type

  - name: products
    base_table: my_db.my_schema.products
    description: Product catalog
    columns:
      - name: product_id
        description: Unique product identifier
        data_type: VARCHAR
        
      - name: product_name
        description: Product display name
        data_type: VARCHAR
        
      - name: category
        description: Product category (Furniture, Office Supplies, Technology)
        data_type: VARCHAR

relationships:
  - name: orders_to_customers
    left_table: orders
    right_table: customers
    relationship_columns:
      - left_column: customer_id
        right_column: customer_id
    join_type: left_outer
    
  - name: orders_to_products
    left_table: orders
    right_table: products
    relationship_columns:
      - left_column: product_id
        right_column: product_id
    join_type: left_outer

# Verified Queries (VQRs) - Gold standard for testing and accuracy
verified_queries:
  - name: total_revenue_by_region
    question: What is total revenue by region?
    verified_query: |
      SELECT c.region, SUM(o.total_amount) AS revenue
      FROM orders o
      LEFT JOIN customers c ON o.customer_id = c.customer_id
      GROUP BY c.region
      ORDER BY revenue DESC
    verified_answer: |
      Total revenue by region:
      - West: $X
      - East: $Y
      - Central: $Z
      - South: $W
      
  - name: top_customers
    question: Who are our top 10 customers by revenue?
    verified_query: |
      SELECT c.customer_name, SUM(o.total_amount) AS total_revenue
      FROM orders o
      LEFT JOIN customers c ON o.customer_id = c.customer_id
      GROUP BY c.customer_name
      ORDER BY total_revenue DESC
      LIMIT 10
      
  - name: q4_revenue
    question: What was Q4 2025 revenue?
    question_variations:
      - What is Q4 revenue?
      - How much did we make in Q4?
      - Fourth quarter revenue
    verified_query: |
      SELECT SUM(total_amount) AS q4_revenue
      FROM orders
      WHERE DATE_TRUNC('quarter', order_date) = '2025-10-01'
      
  - name: monthly_trend
    question: What is the monthly revenue trend for 2025?
    verified_query: |
      SELECT 
        DATE_TRUNC('month', order_date) AS month,
        SUM(total_amount) AS revenue
      FROM orders
      WHERE YEAR(order_date) = 2025
      GROUP BY month
      ORDER BY month
```

```sql
-- Step 1: Upload YAML to stage
-- Run from local machine:
-- snowflake put file://sales_semantic_model.yaml @my_db.my_schema.my_stage

-- Step 2: Create semantic view from YAML
CREATE OR REPLACE SEMANTIC VIEW my_db.my_schema.sales_semantic_view
  FROM '@my_db.my_schema.my_stage/sales_semantic_model.yaml'
  COMMENT = 'Sales analytics with verified queries';

-- Step 3: Grant access
GRANT USAGE ON SEMANTIC VIEW my_db.my_schema.sales_semantic_view TO ROLE analyst_role;
```

## Validation

```sql
-- Verify semantic view exists
SHOW SEMANTIC VIEWS LIKE 'sales_semantic_view' IN SCHEMA my_db.my_schema;

-- Test a verified query question
SELECT SNOWFLAKE.CORTEX.ANALYST(
    'my_db.my_schema.sales_semantic_view',
    'What is total revenue by region?'
);

-- Compare Analyst output with verified query
-- The SQL generated should match or be semantically equivalent to verified_query
SELECT c.region, SUM(o.total_amount) AS revenue
FROM my_db.my_schema.orders o
LEFT JOIN my_db.my_schema.customers c ON o.customer_id = c.customer_id
GROUP BY c.region
ORDER BY revenue DESC;

-- Test question variation
SELECT SNOWFLAKE.CORTEX.ANALYST(
    'my_db.my_schema.sales_semantic_view',
    'How much did we make in Q4?'  -- Should match q4_revenue VQR
);

-- Verify VQRs are loaded (check metadata)
DESCRIBE SEMANTIC VIEW my_db.my_schema.sales_semantic_view;
```

**Expected Result:**
- Semantic view created from YAML file
- Cortex Analyst uses verified queries for matching questions
- Question variations map to the correct VQR
- SQL generated matches or is semantically equivalent to verified_query
- Analyst provides consistent, accurate responses for VQR questions
