# Snowflake Native Semantic Views: Core DDL

> **CORE RULE:** Essential Semantic Views patterns for DDL creation and validation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-27
**Keywords:** TABLES, RELATIONSHIPS, PRIMARY KEY, semantic view, create semantic view, SQL, YAML, NLQ, mapping syntax
**TokenBudget:** ~2250
**ContextTier:** High
**Depends:** 100-snowflake-core.md
**LoadTrigger:** kw:semantic-view, kw:semantic-model

## Scope

**What This Rule Covers:**
Creating Snowflake Native Semantic Views using `CREATE SEMANTIC VIEW` DDL: structure, components, and validation.

**When to Load:**
- Creating semantic views with DDL
- Defining TABLES, RELATIONSHIPS, PRIMARY KEY
- Debugging semantic view creation errors

**Related Rules:**
- **106a** - Advanced patterns, validation rules
- **106b** - Query patterns, SEMANTIC_VIEW() function
- **106c** - Cortex Analyst/Agent integration

## References

### Dependencies
**Must Load First:**
- **100-snowflake-core.md** - Snowflake SQL patterns

### Related Examples

- **examples/106-semantic-view-ddl-example.md** - Complete DDL creation workflow
- **examples/106-semantic-view-yaml-vqr-example.md** - YAML with verified queries
- **examples/106-semantic-view-workarounds-example.md** - Dimension transformation workarounds

### External Documentation
- [Snowflake Semantic Views](https://docs.snowflake.com/en/user-guide/semantic-views)
- [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)

## Contract

### Inputs and Prerequisites
- Target DATABASE.SCHEMA with privileges
- Physical base tables with defined structure
- Business glossary for naming

### Mandatory
- `CREATE SEMANTIC VIEW` DDL
- `SHOW SEMANTIC VIEWS/DIMENSIONS/METRICS`

### Forbidden
- CAST, DATE_TRUNC in DIMENSIONS (use simple columns)
- Verified queries in DDL (use YAML files)

### Approach Selection
**SQL (Preferred):** Use `CREATE SEMANTIC VIEW` for structure, synonyms, relationships.

**YAML (Alternative):** Use for verified queries (VQR), file-based CI/CD, or `semantic_model_file` parameter.

### Execution Steps
1. Define TABLES with PRIMARY KEY
2. Declare FACTS (numeric at row level)
3. Declare DIMENSIONS (simple columns only)
4. Define METRICS (aggregations)
5. Add SYNONYMS for NLQ accuracy
6. Add COMMENT clauses (use `=` syntax)
7. Validate with SHOW commands

### Output Format
Minimal, runnable `CREATE SEMANTIC VIEW` DDL with TABLES, FACTS, DIMENSIONS, METRICS blocks

### Validation
DDL compiles; SHOW commands confirm creation; validation rules pass

### Design Principles
- **Clause ordering:** TABLES, then FACTS, then DIMENSIONS, then METRICS
- **Simple expressions:** DIMENSIONS use simple columns only
- **Comment syntax:** Use `COMMENT = 'text'` (with equals)
- **Physical columns:** Verify with DESCRIBE TABLE before creating

> **STOP Gate:** Before creating semantic views:
> - [ ] Base tables exist with data
> - [ ] User has CREATE SEMANTIC VIEW privilege
> - [ ] Physical column names verified via DESCRIBE TABLE
>
> **CRITICAL:** Run `DESCRIBE TABLE <base_table>` and use exact column names in DDL.

### Post-Execution Checklist
- [ ] All mapping syntax: `alias.physical_column AS logical_name`
- [ ] Physical columns verified against base table
- [ ] COMMENT uses equals sign
- [ ] DIMENSIONS use simple columns only
- [ ] At least one dimension or metric defined
- [ ] Test with Cortex Analyst NLQ query

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Wrong Clause Order
```sql
-- WRONG: DIMENSIONS before TABLES
CREATE SEMANTIC VIEW v AS DIMENSIONS (...) TABLES (...);
```
**Problem:** Syntax error - clauses out of order.

**Correct Pattern:** Order: TABLES, FACTS, DIMENSIONS, METRICS

### Anti-Pattern 2: Complex Expressions in DIMENSIONS
```sql
-- WRONG: DATE_TRUNC in dimensions
DIMENSIONS (sale_month AS DATE_TRUNC('MONTH', order_date))
```
**Problem:** Functions not allowed in dimensions.

**Correct Pattern:** Use simple column references; pre-compute in base view if needed.

### Anti-Pattern 3: Missing Equals in COMMENT
```sql
-- WRONG
COMMENT 'text'
-- CORRECT
COMMENT = 'text'
```

### Anti-Pattern 4: Referencing Non-Existent Columns
```sql
-- WRONG: Using invented column names
FACTS (tfm.load_kilowatts AS load_kw)  -- "load_kilowatts" doesn't exist!
```
**Problem:** DDL may compile but Cortex Analyst queries fail.

**Correct Pattern:**
```sql
DESCRIBE TABLE PROD.GRID_DATA.TRANSFORMER_DATA;
-- Use exact column names from output
FACTS (tfm.load_kw AS load_kw)  -- Matches actual column
```

### Anti-Pattern 5: Template Characters in SYNONYMS
```sql
-- WRONG: & causes CLI issues
SYNONYMS ('R&D', 'Sales & Marketing')
-- CORRECT
SYNONYMS ('R and D', 'Sales and Marketing')
```
**Problem:** CLI interprets `&` as template variable.

## Implementation Details

### Complete DDL Structure
```sql
CREATE [OR REPLACE] SEMANTIC VIEW <db>.<schema>.<view>
  TABLES (
    <alias> AS <db>.<schema>.<table>
      PRIMARY KEY (<col>)
      [WITH SYNONYMS ('<syn>')]
      [COMMENT = '<desc>']
  )
  FACTS (
    <alias>.<logical_name> AS <physical_col>
      [WITH SYNONYMS ('<syn>')]
      [COMMENT = '<desc>']
  )
  DIMENSIONS (
    <alias>.<logical_name> AS <physical_col>
      [WITH SYNONYMS ('<syn>')]
      [COMMENT = '<desc>']
  )
  METRICS (
    <alias>.<metric_name> AS <aggregate>(<expr>)
      [WITH SYNONYMS ('<syn>')]
      [COMMENT = '<desc>']
  );
```

### Minimal Example
```sql
CREATE OR REPLACE SEMANTIC VIEW PROD.DATA.SEM_INVENTORY
  TABLES (
    asset AS PROD.DATA.ASSETS PRIMARY KEY (asset_id)
  )
  FACTS (
    asset.rated_capacity AS rated_capacity
  )
  DIMENSIONS (
    asset.asset_id AS asset_id,
    asset.asset_type AS asset_type
  )
  METRICS (
    asset.asset_count AS COUNT(DISTINCT asset_id)
  );
```

### Multi-Table with Relationships
```sql
CREATE OR REPLACE SEMANTIC VIEW PROD.SALES.SEM_ORDERS
  TABLES (
    customer PRIMARY KEY (c_custkey),
    orders PRIMARY KEY (o_orderkey)
  )
  RELATIONSHIPS (
    orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey)
  )
  FACTS (
    orders.amount AS o_totalprice
  )
  DIMENSIONS (
    customer.name AS c_name WITH SYNONYMS ('customer name'),
    orders.date AS o_orderdate WITH SYNONYMS ('order date')
  )
  METRICS (
    orders.total_revenue AS SUM(o_totalprice) WITH SYNONYMS ('revenue', 'sales')
  );
```

### Component Rules

**TABLES Block:**
- One TABLES block per view
- PRIMARY KEY required for relationships
- Composite keys supported: `PRIMARY KEY (col1, col2)`

**FACTS Block:**
- Numeric measures at row level
- Simple expressions: `physical_column`, `col1 * col2`
- Mapping: `alias.physical_col AS logical_name`

**DIMENSIONS Block:**
- Categorical/temporal attributes
- **Simple columns only** - no CAST, DATE_TRUNC
- Mapping: `alias.physical_col AS logical_name`
- For temporal granularity (TIME_GRAIN), pre-compute in base view:

```sql
-- Base view with pre-computed time grains
CREATE VIEW sales_base AS
SELECT *, DATE_TRUNC('MONTH', order_date) AS order_month,
         DATE_TRUNC('QUARTER', order_date) AS order_quarter
FROM raw_sales;

-- Semantic view uses simple columns
DIMENSIONS (
  s.order_date AS order_date,
  s.order_month AS order_month WITH SYNONYMS ('month', 'monthly'),
  s.order_quarter AS order_quarter WITH SYNONYMS ('quarter', 'quarterly')
)
```

**METRICS Block:**
- Aggregations: COUNT, SUM, AVG, MIN, MAX
- Mapping: `metric_name AS aggregate(expression)`

### YAML Verified Queries (VQR)

VQR only supported in YAML files (not DDL). Table references use `__logical_name`:

```yaml
verified_queries:
  - name: monthly_revenue
    question: "What is total revenue by month?"
    sql: |
      SELECT DATE_TRUNC('MONTH', sale_date) AS month, SUM(total_revenue) AS revenue
      FROM __sales_data  -- Double underscore + logical table name
      GROUP BY month
```

**Common VQR Mistake:**
```yaml
# WRONG: Using physical table name
sql: SELECT * FROM PROD.SALES.SALES_FACT
# CORRECT: Double underscore + logical name
sql: SELECT * FROM __sales_data
```

### Prerequisites Verification
```sql
SHOW TABLES LIKE '%table_name%';
DESCRIBE TABLE db.schema.table;
SHOW GRANTS ON SCHEMA db.schema;
SELECT CURRENT_WAREHOUSE();
```

### Post-Creation Validation
```sql
SHOW SEMANTIC VIEWS LIKE '%view_name%';
SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW db.schema.view;
SHOW SEMANTIC METRICS IN SEMANTIC VIEW db.schema.view;
SELECT GET_DDL('SEMANTIC_VIEW', 'db.schema.view');
```
