# Snowflake Semantic Views: Advanced Patterns & Validation

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:semantic-view-advanced
**Keywords:** validation rules, semantic model quality, semantic view pitfalls, debug semantic view, validation failures, relationship errors
**TokenBudget:** ~1900
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 106-snowflake-semantic-views-core.md

## Scope

**What This Rule Covers:**
Advanced semantic view patterns: anti-patterns, validation rules, quality checks, compliance.

**When to Load:**
- Avoiding common semantic view mistakes
- Implementing validation rules
- Debugging semantic view errors

## References

### External Documentation
- [CREATE SEMANTIC VIEW DDL](https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view)
- [Validation Rules](https://docs.snowflake.com/en/user-guide/views-semantic/validation-rules)

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake SQL patterns
- **106-snowflake-semantic-views-core.md** - Semantic Views DDL fundamentals

**Related:**
- **106b-snowflake-semantic-views-querying.md** - Query patterns, SEMANTIC_VIEW() function
- **106c-snowflake-semantic-views-integration.md** - Cortex Analyst/Agent integration

## Contract

### Inputs and Prerequisites
- Understanding of semantic view basics (from 106-snowflake-semantic-views-core)
- Role with CREATE SEMANTIC VIEW privilege on target schema
- USAGE privilege on referenced tables/views
- Semantic view created and accessible

### Mandatory
- Run `DESCRIBE TABLE` to verify physical column names before any semantic view DDL
- Use `alias.physical_column AS logical_name` mapping syntax consistently
- Validate with `SHOW SEMANTIC VIEWS/DIMENSIONS/METRICS` after creation
- Follow clause order: TABLES, FACTS, DIMENSIONS, METRICS

### Forbidden
- Circular or self-referencing relationships
- Expression reference cycles between metrics
- Template characters (`&`, `<%`, `{{`) in SYNONYMS or COMMENT values
- Window function metrics referenced from other metrics or dimensions

### Conditional
- PRIMARY KEY required only when relationships are defined
- Composite keys when table grain requires multiple columns

### Execution Steps
1) Review anti-patterns 2) Apply validation rules 3) Run quality checks 4) Verify compliance

### Output Format
Validation queries, compliance checklists, quality reports

### Validation
No anti-patterns detected; validation passes; compliant with requirements

### Design Principles
- Avoid anti-patterns for maintainability and performance
- Apply comprehensive validation rules before deployment

### Post-Execution Checklist
- [ ] Anti-patterns reviewed and avoided
- [ ] Validation rules applied
- [ ] Physical column names verified against base table (DESCRIBE TABLE)
- [ ] Quality checks passed

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Reversed Mapping Syntax
```sql
-- WRONG
FACTS (orders.order_amount AS total_amount)  -- Reversed!
```
**Problem:** Syntax error: "invalid identifier"

**Correct Pattern:**
```sql
FACTS (orders.total_amount AS order_amount)  -- logical_name AS physical_column
```

### Anti-Pattern 2: Complex Expressions in DIMENSIONS

**Problem:** Using CAST, DATE_TRUNC, or other transformations directly in DIMENSIONS.
```sql
-- WRONG: Complex expression in DIMENSIONS
DIMENSIONS (orders.DATE_TRUNC('month', order_date) AS order_month)
```

**Why It Fails:** DIMENSIONS must be direct column references. Complex expressions cause syntax errors.

**Correct Pattern:**
```sql
-- Use a derived column in the base table or a view
DIMENSIONS (orders.order_month AS order_month)  -- Pre-computed column
```

### Additional Reference

See `106-snowflake-semantic-views-core.md` for additional anti-patterns:
- **Missing Equals Sign in COMMENT** - use `COMMENT = 'text'`
- **Wrong Clause Order** - must be TABLES, FACTS, DIMENSIONS, METRICS
- **Referencing Non-Existent Columns** - always verify with `DESCRIBE TABLE` first

## Validation Rules

### General Rules

**Required Elements:** Must have at least one dimension or metric.
```sql
-- ERROR: No dimensions or metrics
CREATE SEMANTIC VIEW my_view TABLES (...);  -- Fails
```

**Table Alias References:** Use defined alias, not physical table name.
```sql
TABLES (orders AS db.schema.orders_table ...)
DIMENSIONS (orders.order_id AS id)  -- Use 'orders', not 'orders_table'
```

### Relationship Rules

**Many-to-One Relationships:**
```sql
RELATIONSHIPS (orders_to_customer AS orders(o_custkey) REFERENCES customer(c_custkey))
-- c_custkey must be PRIMARY KEY
```

**FORBIDDEN:**
- Circular relationships
- Self-references (table cannot reference itself)
- Expression reference cycles

### Expression Rules

**Table Association Required:**
```sql
-- WRONG
DIMENSIONS (customer_name AS c_name)  -- Missing table prefix
-- CORRECT
DIMENSIONS (customer.customer_name AS c_name)
```

**Granularity Rules:**
- Row-level expressions can reference same or lower granularity directly
- Higher granularity requires aggregation

```sql
-- customer is lower granularity than orders (one customer = many orders)
DIMENSIONS (
  customer.name AS c_name,
  orders.customer_name AS customer.name  -- Lower granularity: OK
)

-- Must aggregate when referencing higher granularity
DIMENSIONS (
  customer.total_orders AS COUNT(orders.order_key)  -- Must aggregate
)
```

**Window Function Restrictions:**
- Cannot use in dimensions or facts
- Cannot use in other metrics

### Template Character Validation (CLI Compatibility)

**Forbidden in SYNONYMS and COMMENT:**
- `&` - CLI template variable prefix
- `<%` `%>` - SnowSQL variables
- `{{` `}}` - Jinja/dbt templates

```sql
-- WRONG (fails via CLI)
SYNONYMS ('R&D', 'Sales & Marketing')
-- CORRECT
SYNONYMS ('R and D', 'Sales and Marketing')
```

## Post-Creation Validation

**Step 1: Extract DDL**
```sql
SELECT GET_DDL('SEMANTIC_VIEW', 'DB.SCHEMA.SEM_VIEW_NAME');
```

**Step 2: Verify columns exist in base table**
```sql
DESCRIBE TABLE DB.SCHEMA.BASE_TABLE;
-- Cross-reference each column in DDL
```

**Step 3: Test columns directly**
```sql
SELECT DISTINCT equipment_id FROM DB.SCHEMA.TABLE LIMIT 1;  -- If fails, column wrong
```

**Step 4: Test with Cortex Analyst** (ultimate validation)

**Automated Validation Query:**
```sql
WITH semantic_columns AS (
  SELECT 'equipment_id' AS column_name UNION ALL SELECT 'load_kw'
),
actual_columns AS (
  SELECT COLUMN_NAME FROM DB.INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = 'SCHEMA' AND TABLE_NAME = 'TABLE'
)
SELECT s.column_name,
  CASE WHEN a.COLUMN_NAME IS NOT NULL THEN 'EXISTS' ELSE 'MISSING' END AS status
FROM semantic_columns s
LEFT JOIN actual_columns a ON UPPER(s.column_name) = UPPER(a.COLUMN_NAME);
```

### Pre-Creation Checklist
- [ ] At least one dimension or metric defined
- [ ] PRIMARY KEY uses physical columns only
- [ ] Relationships are many-to-one (no circular, no self-ref)
- [ ] Table aliases used consistently
- [ ] No circular expression or table references
- [ ] Row-level expressions respect granularity rules
- [ ] Metrics use proper aggregation
- [ ] Window function metrics not used in other expressions
- [ ] Only scalar functions in dimensions (no table functions)
- [ ] No template characters in SYNONYMS or COMMENT
- [ ] **CRITICAL: All physical column names verified against base table**

### Post-Creation Validation
```sql
SHOW SEMANTIC VIEWS IN SCHEMA my_schema;
DESCRIBE SEMANTIC VIEW my_schema.my_view;
SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW my_schema.my_view;
SHOW SEMANTIC METRICS IN SEMANTIC VIEW my_schema.my_view;
```

> **Investigation Required:**
> 1. **Read existing semantic views BEFORE creating new ones**
> 2. **Verify base table schemas** - Use DESCRIBE TABLE to confirm column names
> 3. **Never assume table structures** - Query INFORMATION_SCHEMA.COLUMNS
> 4. **Check existing relationships** between tables
> 5. **Validate granularity assumptions** - fact tables vs dimension tables
