# Snowflake Semantic Views: Advanced Patterns & Validation

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** compliance, common mistakes, validation rules, semantic model quality, semantic view pitfalls, debug semantic view, fix semantic view errors, validation failures, relationship errors, mapping errors, quality assurance, semantic view testing, validation patterns
**TokenBudget:** ~5000
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md, rules/106-snowflake-semantic-views-core.md

## Purpose
Provide advanced patterns for semantic views including anti-patterns to avoid, comprehensive validation rules, quality checks, and compliance requirements.

## Rule Scope
Anti-patterns, validation rules, quality checks, compliance

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.
**MANDATORY:**
**Essential Patterns:**
- **Avoid common anti-patterns** - No business logic in views, no circular refs
- **Apply validation rules** - Check dimensions, measures, filters
- **Run quality checks** - Verify data quality and completeness
- **Ensure compliance** - Meet governance and security requirements

**Quick Checklist:**
- [ ] Anti-patterns reviewed and avoided
- [ ] Validation rules applied
- [ ] Quality checks passed
- [ ] Compliance verified

## Contract

<contract>
<inputs_prereqs>
Understanding of semantic view basics (from 106-core), semantic view created
</inputs_prereqs>

<mandatory>
Validation queries, compliance checks, quality tools
</mandatory>

<forbidden>
None specific
</forbidden>

<steps>
1) Review anti-patterns 2) Apply validation rules 3) Run quality checks 4) Verify compliance
</steps>

<output_format>
Validation queries, compliance checklists, quality reports
</output_format>

<validation>
No anti-patterns detected; validation passes; compliant with requirements
</validation>

<design_principles>
- Avoid anti-patterns for maintainability and performance
- Apply comprehensive validation rules before deployment
- Run quality checks to ensure data correctness
- Verify compliance with governance policies
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Reversed Mapping Syntax**
```sql
-- INCORRECT - Backwards mapping (will cause syntax error)
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  FACTS (
    orders.order_amount AS total_amount  -- Reversed!
  )
  DIMENSIONS (
    orders.order_id AS order_number      -- Reversed!
  );
```
**Problem:** Syntax error: "invalid identifier 'ORDER_AMOUNT'" - the mapping is backwards.

**Correct Pattern:**
```sql
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  FACTS (
    orders.total_amount AS order_amount  -- logical_name AS physical_column
  )
  DIMENSIONS (
    orders.order_number AS order_id      -- logical_name AS physical_column
  );
```
**Benefits:** Correct syntax compiles successfully.


**Anti-Pattern 2: Complex Expressions in DIMENSIONS**
```sql
-- INCORRECT - Complex functions in DIMENSIONS
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  FACTS (
    orders.order_amount AS order_amount
  )
  DIMENSIONS (
    orders.order_id AS order_id,
    orders.reading_date AS CAST(order_timestamp AS DATE),  -- CAST not allowed
    orders.order_hour AS DATE_TRUNC('hour', order_timestamp) -- DATE_TRUNC not allowed
  );
```
**Problem:** Syntax error: "unexpected 'CAST'" or "invalid expression" - dimensions must be simple columns.

**Correct Pattern:**
```sql
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  FACTS (
    orders.order_amount AS order_amount
  )
  DIMENSIONS (
    orders.order_id AS order_id,
    orders.order_timestamp AS order_timestamp  -- Use raw timestamp
    -- Add derived columns (date parts) to base table/view if needed
  );
```
**Benefits:** Clean dimensions that work with Cortex Analyst's temporal intelligence.


**Anti-Pattern 3: Missing Equals Sign in COMMENT**
```sql
-- INCORRECT - COMMENT without equals sign
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
      COMMENT 'Sales orders table'  -- Missing equals sign
  )
  FACTS (
    orders.order_amount AS order_amount
      COMMENT 'Total order value'   -- Missing equals sign
  );
```
**Problem:** Syntax error: "unexpected 'Sales'" - COMMENT requires equals sign.

**Correct Pattern:**
```sql
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
      COMMENT = 'Sales orders table'  -- Equals sign required
  )
  FACTS (
    orders.order_amount AS order_amount
      COMMENT = 'Total order value'   -- Equals sign required
  );
```
**Benefits:** Proper comment syntax compiles successfully.


**Anti-Pattern 4: Wrong Clause Order**
```sql
-- INCORRECT - Wrong clause ordering
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  DIMENSIONS (                        -- DIMENSIONS before FACTS
    orders.order_id AS order_id
  )
  FACTS (                             -- FACTS after DIMENSIONS
    orders.order_amount AS order_amount
  );
```
**Problem:** Syntax error or unexpected behavior - clause order matters.

**Correct Pattern:**
```sql
CREATE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    orders AS PROD.SALES.ORDERS
      PRIMARY KEY (order_id)
  )
  FACTS (                             -- FACTS first
    orders.order_amount AS order_amount
  )
  DIMENSIONS (                        -- DIMENSIONS after FACTS
    orders.order_id AS order_id
  )
  METRICS (                           -- METRICS last
    orders.order_count AS COUNT(*)
  );
```
**Benefits:** Correct clause order: TABLES, then FACTS, then DIMENSIONS, then METRICS.

## Post-Execution Checklist

**DDL Creation:**
- [ ] Use `CREATE SEMANTIC VIEW` (not `CREATE VIEW`)
- [ ] Clause order: TABLES, then FACTS, then DIMENSIONS, then METRICS
- [ ] Mapping syntax: `logical_name AS physical_column` (NOT reversed)
- [ ] PRIMARY KEY defined in TABLES block (uses physical columns only)
- [ ] COMMENT clauses use equals sign: `COMMENT = 'text'`
- [ ] DIMENSIONS use simple columns (no CAST, DATE_TRUNC)
- [ ] At least one dimension or metric defined
- [ ] Verified with `SHOW SEMANTIC VIEWS`

**Validation Rules:**
- [ ] Relationships are many-to-one (no circular, no self-ref, no multi-path)
- [ ] Table aliases used consistently in expressions
- [ ] No circular expression or table reference cycles
- [ ] Cross-table references use relationships (not direct column refs)
- [ ] Row-level expressions respect granularity rules (aggregate for higher granularity)
- [ ] Metrics use proper aggregation (nested when referencing higher granularity)
- [ ] Window function metrics not used in dimensions, facts, or other metrics
- [ ] Only scalar functions in dimensions (no table functions)
- [ ] No template characters (`&`, `<%`, `%>`, `{{`, `}}`) in SYNONYMS or COMMENT values

## Validation
- **Success Checks:**
  - DDL compiles without syntax errors
  - `SHOW SEMANTIC VIEWS` confirms object creation
  - `SHOW SEMANTIC DIMENSIONS/METRICS` returns expected structure
  - Validation rules pass (relationships, granularity, expressions)
  - Correct mapping syntax used (logical_name AS physical_expression)
  - Clause order correct (TABLES, then FACTS, then DIMENSIONS, then METRICS)
  - COMMENT syntax correct (uses equals sign)
  - PRIMARY KEY uses physical columns only
- **Negative Tests:**
  - Reversed mappings cause syntax error ("invalid identifier")
  - CAST/DATE_TRUNC in DIMENSIONS causes syntax error
  - Wrong COMMENT syntax (missing equals) causes syntax error
  - Wrong clause order causes syntax error or unexpected behavior
  - Missing PRIMARY KEY prevents relationships
  - Circular relationships cause error
  - Self-referencing relationships cause error
  - Direct cross-table references without relationships cause error
  - Dimension referencing metric (same granularity) causes error
  - Window function metric in dimension/fact/other metric causes error

## Output Format Examples

```sql
-- Semantic View: <logical_name>
-- Purpose: <business purpose>
-- Base Tables: <list tables>
-- Key Metrics: <primary metrics>

CREATE OR REPLACE SEMANTIC VIEW <database>.<schema>.<view_name>
COMMENT = 'Business-friendly description'
AS
  TABLES (
    <table_alias> AS <database>.<schema>.<table_name> (
      PRIMARY KEY (<physical_column>)
    ),
    <related_table_alias> AS <database>.<schema>.<related_table> (
      PRIMARY KEY (<physical_column>),
      FOREIGN KEY (<fk_column>) REFERENCES <table_alias>(<pk_column>)
    )
  )
  FACTS (
    <logical_fact> AS <table_alias>.<physical_column>
      COMMENT = 'Row-level measure description'
  )
  DIMENSIONS (
    <logical_dimension> AS <table_alias>.<physical_column>
      COMMENT = 'Grouping attribute description'
  )
  METRICS (
    <logical_metric> AS AGG_FUNCTION(<table_alias>.<physical_column>)
      COMMENT = 'Aggregated business metric description'
  );

-- Validation checks
SHOW SEMANTIC VIEWS LIKE '<view_name>';
SHOW SEMANTIC DIMENSIONS FOR SEMANTIC VIEW <view_name>;
SHOW SEMANTIC METRICS FOR SEMANTIC VIEW <view_name>;
```

> **Investigation Required**
> When applying this rule:
> 1. **Read existing semantic views BEFORE creating new ones** - Check for naming patterns, standards, and conventions
> 2. **Verify base table schemas** - Use `DESCRIBE TABLE` to confirm physical column names and types
> 3. **Never assume table structures** - Always query `INFORMATION_SCHEMA.COLUMNS` or use `SHOW COLUMNS`
> 4. **Check existing relationships** - Verify foreign key relationships between tables before defining semantic relationships
> 5. **Validate granularity assumptions** - Confirm whether tables are fact tables (many rows per entity) or dimension tables (one row per entity)
> 6. **Make grounded recommendations based on investigated schema** - Don't create mappings for columns that don't exist
>
> **Anti-Pattern:**
> "Based on typical data models, you probably have a customer_id column..."
> "Let me create a semantic view with standard dimension names..."
>
> **Correct Pattern:**
> "Let me check your table schema first."
> [runs DESCRIBE TABLE or queries INFORMATION_SCHEMA]
> "I see your table has these columns: [actual columns]. Here's a semantic view definition using your actual schema..."

## References

### External Documentation
- [CREATE SEMANTIC VIEW DDL](https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view) - Official DDL syntax reference
- [Semantic Views Overview](https://docs.snowflake.com/en/user-guide/views-semantic/overview) - Conceptual overview and use cases
- [Using SQL to create and manage views](https://docs.snowflake.com/en/user-guide/views-semantic/sql) - SQL workflow and examples
- [Validation Rules for Semantic Views](https://docs.snowflake.com/en/user-guide/views-semantic/validation-rules) - Complete validation rule reference

### Related Rules
- **Querying Semantic Views**: `rules/106b-snowflake-semantic-views-querying.md` - SEMANTIC_VIEW() query patterns and testing
- **Integration & Development**: `rules/106c-snowflake-semantic-views-integration.md` - Cortex Analyst, governance, workflows
- **Snowflake Core**: `rules/100-snowflake-core.md` - Foundational Snowflake practices
- **Cortex Analyst Integration**: `rules/106c-snowflake-semantic-views-integration.md` - Natural language query patterns

## 4) Validation Rules

### 4.1 General Validation Rules

**Purpose:** Understand Snowflake's validation rules to prevent errors during semantic view creation.

**Required Elements:**
```sql
-- CORRECT: Must have at least one dimension or metric
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders
      PRIMARY KEY (order_id)
  )
  DIMENSIONS (
    orders.order_id AS order_id
  );

-- ERROR: No dimensions or metrics defined
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders
      PRIMARY KEY (order_id)
  );
-- Error: A semantic view must define at least one dimension or metric
```

**Primary and Foreign Keys:**
```sql
-- CORRECT: Use physical base table columns in keys
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer
      PRIMARY KEY (c_custkey),      -- Physical column
    orders AS db.schema.orders
      PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
    -- Both o_custkey and c_custkey are physical columns
  )
  DIMENSIONS (
    customer.name AS c_name
  );
```

**Table Alias References:**
```sql
-- CORRECT: Use defined aliases in expressions
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders_table  -- Alias is 'orders'
      PRIMARY KEY (o_orderkey)
  )
  DIMENSIONS (
    orders.order_id AS o_orderkey     -- Use 'orders' alias, not 'orders_table'
  );

-- ERROR: Using physical table name instead of alias
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders_table
      PRIMARY KEY (o_orderkey)
  )
  DIMENSIONS (
    orders_table.order_id AS o_orderkey  -- Wrong: should use 'orders'
  );
-- Error: Invalid table reference 'orders_table'
```

### 4.2 Relationship Validation Rules

**Many-to-One Relationships:**
```sql
-- CORRECT: Many orders to one customer
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer
      PRIMARY KEY (c_custkey),
    orders AS db.schema.orders
      PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
    -- Many orders can belong to one customer (c_custkey must be PRIMARY KEY)
  )
  DIMENSIONS (
    customer.name AS c_name,
    orders.order_date AS o_orderdate
  );
```

**Transitive Relationships:**
```sql
-- Snowflake automatically derives indirect relationships
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey),
    line_items AS db.schema.lineitem PRIMARY KEY (l_orderkey, l_linenumber)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey),
    lineitem_to_orders AS line_items(l_orderkey) REFERENCES orders(o_orderkey)
    -- Snowflake automatically understands line_items relates to customer
  )
  DIMENSIONS (
    customer.name AS c_name,
    line_items.quantity AS l_quantity
    -- Can reference customer from line_items via transitive relationship
  );
```

**Circular Relationships (FORBIDDEN):**
```sql
-- ERROR: Circular relationship
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey),
    customer_to_orders AS customer(c_recent_order) REFERENCES orders(o_orderkey)
    -- Creates circular relationship between customer and orders
  );
-- Error: Circular relationships are not allowed
```

**Self-References (NOT SUPPORTED):**
```sql
-- ERROR: Self-referencing relationship
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    employee AS db.schema.employee PRIMARY KEY (emp_id)
  )
  RELATIONSHIPS (
    employee_manager AS employee(manager_id) REFERENCES employee(emp_id)
    -- Self-reference for employee-manager hierarchy not supported
  );
-- Error: A table cannot reference itself
```

**Multi-Path Relationship Restrictions:**
```sql
-- LIMITATION: Multiple paths between tables have restrictions
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders PRIMARY KEY (o_orderkey),
    line_items AS db.schema.lineitem PRIMARY KEY (l_orderkey, l_linenumber)
  )
  RELATIONSHIPS (
    lineitem_to_orders_key AS line_items(l_orderkey) REFERENCES orders(o_orderkey),
    lineitem_to_orders_alt AS line_items(l_alt_key) REFERENCES orders(o_alt_key)
    -- Multiple paths: these tables cannot refer to each other's semantic expressions
  );

-- SOLUTION: Define separate logical tables for different paths
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders PRIMARY KEY (o_orderkey),
    orders_alt AS db.schema.orders PRIMARY KEY (o_alt_key),  -- Separate logical table
    line_items AS db.schema.lineitem PRIMARY KEY (l_orderkey, l_linenumber)
  )
  RELATIONSHIPS (
    lineitem_to_orders AS line_items(l_orderkey) REFERENCES orders(o_orderkey),
    lineitem_to_orders_alt AS line_items(l_alt_key) REFERENCES orders_alt(o_alt_key)
  );
```

**One-to-One Relationship Restrictions:**
```sql
-- LIMITATION: One-to-one relationships have usage restrictions
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders PRIMARY KEY (o_orderkey),
    order_summary AS db.schema.order_summary
  )
  RELATIONSHIPS (
    orders_to_summary AS orders(o_orderkey) REFERENCES order_summary(summary_id)
    -- o_orderkey has unique values (one-to-one)
  )
  DIMENSIONS (
    orders.order_id AS o_orderkey
  )
  METRICS (
    orders.total AS SUM(order_summary.amount)  -- orders can refer to order_summary
    -- order_summary CANNOT refer to orders semantic expressions
  );
```

### 4.3 Expression Validation Rules

**Expression Types:**
```sql
-- Dimensions and facts are row-level (unaggregated)
DIMENSIONS (
  customer.customer_name AS c_name        -- Row-level
)
FACTS (
  orders.order_amount AS o_totalprice     -- Row-level
)

-- Metrics are aggregate-level (aggregated)
METRICS (
  orders.order_average AS AVG(o_totalprice)  -- Aggregate-level
)
```

**Table Association (MANDATORY):**
```sql
-- CORRECT: Every expression associated with table
DIMENSIONS (
  customer.customer_name AS c_name,       -- Associated with 'customer' table
  orders.order_date AS o_orderdate        -- Associated with 'orders' table
)

-- ERROR: Expression without table association
DIMENSIONS (
  customer_name AS c_name                 -- Missing table prefix
);
-- Error: Expression must be associated with a table
```

**Same-Table References:**
```sql
-- Both qualified and unqualified references allowed within same table
DIMENSIONS (
  orders.shipping_month AS MONTH(o_shipdate),           -- Unqualified column
  orders.shipping_year AS YEAR(orders.o_shipdate)       -- Qualified column
  -- Both work because referencing same table's column
)
```

**Cross-Table Limitations:**
```sql
-- ERROR: Direct reference to unrelated table column
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  -- No relationship defined
  DIMENSIONS (
    customer.order_count AS COUNT(orders.o_orderkey)  -- Cannot reference orders
  );
-- Error: Expression cannot refer to columns from unrelated tables

-- CORRECT: Use relationships and facts
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  FACTS (
    orders.order_key AS o_orderkey           -- Define fact on source table
  )
  DIMENSIONS (
    customer.order_count AS COUNT(orders.order_key)  -- Reference via relationship
  );
```

**Name Resolution:**
```sql
-- If semantic expression and column have same name, expression takes precedence
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer
      PRIMARY KEY (c_custkey)
  )
  DIMENSIONS (
    customer.region AS UPPER(c_region),      -- Define 'region' dimension
    customer.regional_id AS CONCAT(region, c_custkey)
    -- 'region' resolves to dimension, not column
  );

-- Exception: Self-referential definition
DIMENSIONS (
  customer.c_name AS customer.c_name       -- 'c_name' resolves to column, not itself
)
```

**Expression Reference Cycles (FORBIDDEN):**
```sql
-- ERROR: Circular expression references
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  METRICS (
    customer.total_value AS SUM(orders.customer_value),
    orders.customer_value AS AVG(customer.total_value)  -- Circular reference
  );
-- Error: Circular references between expressions not allowed
```

**Table Reference Cycles (FORBIDDEN):**
```sql
-- ERROR: Circular table references
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  DIMENSIONS (
    customer.total_value AS SUM(orders.customer_value),
    orders.customer_count AS COUNT(customer.c_custkey)  -- Circular table refs
  );
-- Error: Circular references between logical tables not allowed
```

**Function Usage:**
```sql
-- ALLOWED: Scalar functions in dimensions
DIMENSIONS (
  orders.order_year AS YEAR(o_orderdate),
  orders.order_month AS MONTH(o_orderdate),
  orders.order_quarter AS QUARTER(o_orderdate),
  orders.order_week AS WEEK(o_orderdate),
  orders.order_day AS DAY(o_orderdate)
)

-- FORBIDDEN: Table functions not allowed
DIMENSIONS (
  orders.flattened AS FLATTEN(o_json_column)  -- Table function not supported
);
-- Error: Table functions are not allowed in dimensions
```

### 4.4 Row-Level Expression Rules (Dimensions and Facts)

**Same-Table References:**
```sql
-- Row-level expression can directly refer to own table columns
DIMENSIONS (
  customer.customer_name AS c_name,           -- Direct column reference
  customer.full_name AS CONCAT(c_firstname, ' ', c_lastname)
)
```

**Equal or Lower Granularity:**
```sql
-- Can reference row-level expressions at same or lower granularity
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  DIMENSIONS (
    customer.name AS c_name,
    orders.customer_name AS customer.name  -- Lower granularity: OK
    -- One customer has many orders, so customer is lower granularity
  );
```

**Higher Granularity References (Requires Aggregation):**
```sql
-- Must use aggregation when referencing higher granularity
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  FACTS (
    orders.order_key AS o_orderkey
  )
  DIMENSIONS (
    customer.total_orders AS COUNT(orders.order_key)  -- Must aggregate
    -- Orders is higher granularity than customer (one customer = many orders)
  );
```

**Aggregate References (Restrictions):**
```sql
-- FORBIDDEN: Dimension cannot refer to metric
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  METRICS (
    orders.avg_value AS AVG(o_totalprice)
  )
  DIMENSIONS (
    orders.order_type AS CASE
      WHEN orders.avg_value > 1000 THEN 'Large'  -- Cannot reference metric
      ELSE 'Small'
    END
  );
-- Error: Dimensions cannot refer to metrics

-- ALLOWED: Lower granularity dimension can refer to higher granularity metric
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  METRICS (
    orders.avg_value AS AVG(o_totalprice)
  )
  DIMENSIONS (
    customer.segment AS CASE
      WHEN orders.avg_value > 1000 THEN 'Premium'  -- OK: customer lower granularity
      ELSE 'Standard'
    END
  );
```

### 4.5 Aggregate-Level Expression Rules (Metrics)

**Basic Aggregation (MANDATORY):**
```sql
-- CORRECT: Metric uses aggregate function
METRICS (
  orders.order_average AS AVG(o_totalprice),
  orders.order_total AS SUM(o_totalprice),
  orders.order_count AS COUNT(*)
)

-- ERROR: Metric without aggregation
METRICS (
  orders.order_amount AS o_totalprice  -- Missing aggregation
);
-- Error: Metrics must use aggregate functions
```

**Equal or Lower Granularity (Single Aggregate):**
```sql
-- Use single aggregate for equal or lower granularity references
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders PRIMARY KEY (o_orderkey),
    line_items AS db.schema.lineitem PRIMARY KEY (l_orderkey, l_linenumber)
  )
  RELATIONSHIPS (
    lineitem_to_orders AS line_items(l_orderkey) REFERENCES orders(o_orderkey)
  )
  FACTS (
    line_items.discounted_price AS l_extendedprice * (1 - l_discount)
  )
  METRICS (
    orders.total_value AS SUM(line_items.discounted_price)  -- Single aggregate
    -- line_items is lower granularity than orders (many line items per order)
  );
```

**Higher Granularity References (Nested Aggregation):**
```sql
-- Must use nested aggregation for higher granularity references
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  METRICS (
    customer.avg_order_value AS AVG(SUM(orders.o_totalprice))  -- Nested agg
    -- orders is higher granularity than customer (one customer = many orders)
    -- Inner SUM aggregates by order, outer AVG aggregates across orders
  );
```

**Metric-to-Metric References:**
```sql
-- Can reference other metrics at equal or lower granularity without aggregation
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  METRICS (
    orders.total_revenue AS SUM(o_totalprice),
    orders.total_cost AS SUM(o_cost),
    orders.profit_margin AS orders.total_revenue / orders.total_cost  -- No extra agg
    -- Both metrics at same granularity (orders level)
  );

-- Requires aggregation when referencing higher granularity metric
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    customer AS db.schema.customer PRIMARY KEY (c_custkey),
    orders AS db.schema.orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  METRICS (
    orders.total_value AS SUM(o_totalprice),
    customer.avg_order_value AS AVG(orders.total_value)  -- Aggregation required
    -- orders is higher granularity than customer
  );
```

### 4.6 Window Function Metric Restrictions

**Cannot Use in Row-Level Calculations:**
```sql
-- FORBIDDEN: Window function metric in dimension
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    sales AS db.schema.sales PRIMARY KEY (sale_id)
  )
  METRICS (
    sales.running_total AS SUM(SUM(amount)) OVER (ORDER BY sale_date)
  )
  DIMENSIONS (
    sales.is_high_sale AS CASE
      WHEN sales.running_total > 1000 THEN 'Yes'  -- Cannot use window metric
      ELSE 'No'
    END
  );
-- Error: Window function metrics cannot be used in dimensions

-- FORBIDDEN: Window function metric in fact
FACTS (
  sales.daily_rank AS RANK() OVER (PARTITION BY sale_date ORDER BY amount)
  -- Cannot use window functions in facts
);
```

**Cannot Use in Other Metrics:**
```sql
-- FORBIDDEN: Window function metric in another metric
CREATE OR REPLACE SEMANTIC VIEW my_view
  TABLES (
    sales AS db.schema.sales PRIMARY KEY (sale_id)
  )
  METRICS (
    sales.running_total AS SUM(SUM(amount)) OVER (ORDER BY sale_date),
    sales.pct_of_running AS amount / sales.running_total  -- Cannot reference
  );
-- Error: Window function metrics cannot be used in other metric definitions
```

### 4.7 Validation Best Practices

**Pre-Creation Checklist:**
```sql
-- Before creating semantic view, verify:
-- [ ] At least one dimension or metric defined
-- [ ] PRIMARY KEY uses physical columns only
-- [ ] All relationships are many-to-one (no circular, no self-ref)
-- [ ] Table aliases used consistently in expressions
-- [ ] No circular expression or table references
-- [ ] Row-level expressions respect granularity rules
-- [ ] Metrics use proper aggregation (nested when needed)
-- [ ] Window function metrics not used in other expressions
-- [ ] Only scalar functions in dimensions (no table functions)
-- [ ] No template characters in SYNONYMS or COMMENT (& <% %> {{ }})

-- Validate after creation:
SHOW SEMANTIC VIEWS IN SCHEMA my_schema;
DESCRIBE SEMANTIC VIEW my_schema.my_view;
SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW my_schema.my_view;
SHOW SEMANTIC METRICS IN SEMANTIC VIEW my_schema.my_view;
```

### 4.8 Template Character Validation (CLI Compatibility)

**Rule:** Avoid characters that Snowflake CLI or SnowSQL interpret as template variables.

**Forbidden Characters in SYNONYMS and COMMENT:**
- `&` - Snowflake CLI (`snow sql`) template variable prefix
- `<%` and `%>` - SnowSQL variable delimiters
- `{{` and `}}` - Common templating syntax (Jinja2, dbt)

**Validation Query:**
```sql
-- Check for problematic characters in semantic view DDL
-- Run GET_DDL and search for template characters
SELECT GET_DDL('SEMANTIC_VIEW', 'MY_DB.MY_SCHEMA.MY_SEMANTIC_VIEW') AS ddl;

-- Manual check: search DDL output for:
-- - '&' (ampersand)
-- - '<%' or '%>' (SnowSQL variables)
-- - '{{' or '}}' (Jinja/dbt templates)
```

**Why This Matters:**
```sql
-- This DDL works in Snowsight but FAILS via CLI:
SYNONYMS ('R&D', 'Sales & Marketing')
-- CLI error: "undefined variable 'D'" or similar

-- This DDL works everywhere:
SYNONYMS ('R and D', 'Research and Development', 'Sales and Marketing')
```

**Best Practice:** Always test semantic view DDL via Snowflake CLI (`snow sql -f file.sql`) before committing to ensure CI/CD compatibility.

## Related Rules

**Related Semantic View Rules:**
- **106b-snowflake-semantic-views-querying.mdc** - Query patterns, testing, SEMANTIC_VIEW() function, dimension compatibility, window function metrics, WHERE clause usage, performance optimization
- **106b-snowflake-semantic-views-integration.mdc** - Cortex Analyst/Agent integration, REST API usage, governance (RBAC, masking, row access), Generator workflow, iterative development, synonym design
