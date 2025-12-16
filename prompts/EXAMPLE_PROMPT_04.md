# Example Prompt 04: Snowflake Semantic View for Cortex Analyst

## The Prompt

```
Task: Create a semantic view for sales analytics to use with Cortex Analyst
Tables: PROD.SALES.ORDERS (order_id, customer_id, order_date, amount), PROD.SALES.CUSTOMERS (customer_id, customer_name, region)
```

## What This Helps

AI assistants will automatically:
- Detect "semantic view" keyword → Load `rules/106-snowflake-semantic-views-core.md`
- Detect "Cortex Analyst" keyword → Load `rules/115-snowflake-cortex-agents-core.md`
- Detect Snowflake context → Load `rules/100-snowflake-core.md`
- Understand multi-table structure requiring RELATIONSHIPS block
- Apply correct DDL syntax: TABLES → RELATIONSHIPS → DIMENSIONS → METRICS

## Why It's Good

**Technology clear (Snowflake):** Explicitly mentions semantic view and Cortex Analyst, triggering specialized Snowflake AI rules

**Tables specified with columns:** Provides exact table paths and column names, enabling accurate DDL generation without guesswork

**Multi-table structure implied:** Two tables with shared `customer_id` signals need for RELATIONSHIPS block and proper join definition

**Minimal yet complete:** Provides exactly enough information for AI to generate valid semantic view DDL following Snowflake's strict clause ordering

## Expected Output Structure

The AI should generate DDL following this pattern:

```sql
CREATE OR REPLACE SEMANTIC VIEW PROD.SALES.SEM_SALES_ANALYTICS
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
      WITH SYNONYMS ('customer', 'client name', 'buyer')
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
      WITH SYNONYMS ('number of orders', 'total orders', 'order volume')
      COMMENT = 'Count of orders'
  )
  COMMENT = 'Sales analytics semantic view for Cortex Analyst natural language queries';
```

## Key Rules Applied

1. **Clause order:** TABLES → RELATIONSHIPS → DIMENSIONS → METRICS (strict sequence)
2. **PRIMARY KEY defined:** Required for RELATIONSHIPS to work
3. **RELATIONSHIPS syntax:** `alias(fk_column) REFERENCES alias(pk_column)`
4. **COMMENT uses equals sign:** `COMMENT = 'text'` (not `COMMENT 'text'`)
5. **SYNONYMS for NLQ:** Multiple synonyms per dimension/metric improve Cortex Analyst accuracy
6. **Simple DIMENSIONS:** No CAST, DATE_TRUNC, or complex expressions
