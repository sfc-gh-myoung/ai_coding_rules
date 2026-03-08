# Snowflake Object Tagging Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-01-27
**LoadTrigger:** kw:tag, kw:tagging, kw:metadata
**Keywords:** cost attribution, resource tagging, governance tags, masking policies, row access policies, tag lineage, tag management
**TokenBudget:** ~2850
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 105-snowflake-cost-governance.md, 107-snowflake-security-governance.md

## Scope

**What This Rule Covers:**
Comprehensive best practices for Snowflake object tagging to enable effective data governance, cost attribution, security classification, and policy automation. Covers tag taxonomy design, inheritance patterns, tag-based policies, cost attribution, and governance enforcement.

**When to Load This Rule:**
- Designing or implementing Snowflake object tagging strategy
- Setting up cost attribution and chargeback systems
- Implementing tag-based masking or row access policies
- Auditing tag coverage and compliance

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **105-snowflake-cost-governance.md** - Resource monitors and cost optimization
- **107-snowflake-security-governance.md** - Access control and security policies

### External Documentation

- [Snowflake Object Tagging](https://docs.snowflake.com/en/user-guide/object-tagging)
- [Tag-Based Masking Policies](https://docs.snowflake.com/en/user-guide/tag-based-masking-policies)
- [Tag-Based Row Access Policies](https://docs.snowflake.com/en/user-guide/tag-based-row-access-policies)

## Contract

### Inputs and Prerequisites

- Snowflake account with tag creation privileges (`CREATE TAG`)
- Governance requirements and compliance framework
- Cost allocation strategy
- Understanding of tag inheritance and lineage

### Mandatory

- SQL DDL for tag creation with ALLOWED_VALUES
- Tag assignment across object hierarchy
- TAG_REFERENCES functions for lineage tracking
- Documented tag taxonomy and governance policies

### Forbidden

- Creating more than 50 tags per object
- Creating tags without documented taxonomy
- Uncontrolled tag proliferation across teams
- Inconsistent tag naming conventions

### Execution Steps

1. Define tag taxonomy aligned with governance requirements
2. Create tags with ALLOWED_VALUES constraints
3. Establish tag ownership (centralized vs decentralized)
4. Apply tags at appropriate hierarchy level for inheritance
5. Document tag purposes and allowed values
6. Monitor tag coverage using TAG_REFERENCES functions
7. Integrate tags with masking policies and cost monitoring

### Output Format

- Tag DDL with documentation and ALLOWED_VALUES
- Tag assignment statements
- Monitoring queries for tag lineage and coverage

### Validation

**Success Criteria:**
- Tags appear in SHOW TAGS output
- Tag assignments visible in TAG_REFERENCES views
- Tag inheritance working (parent to child propagation)
- Tag-based policies functioning correctly
- Cost attribution queries returning accurate results
- Tag coverage >90% for critical objects

### Design Principles

- **Define Once, Apply Many:** Centralized tag creation, apply across objects
- **Leverage Inheritance:** Set tags on parent objects (databases, schemas) for automatic child propagation
- **Control with Constraints:** Use ALLOWED_VALUES for consistent values
- **Integrate with Policies:** Combine tags with masking and row access policies
- **Monitor Coverage:** Regularly audit tag usage

### Post-Execution Checklist

- [ ] Tag taxonomy defined and documented
- [ ] Tags created with ALLOWED_VALUES
- [ ] Tag ownership assigned
- [ ] Schema-level tags applied for inheritance
- [ ] Tag-based policies configured
- [ ] Cost attribution tags on warehouses
- [ ] Tag coverage monitoring automated

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Tag Proliferation Without Governance

```sql
-- BAD: Different teams creating inconsistent tags
CREATE TAG ANALYTICS.TAG.SENSITIVE_DATA;
CREATE TAG FINANCE.TAG.SENSITIVE;
CREATE TAG SALES.TAG.IS_SENSITIVE;
```

**Problem:** Duplicate concepts, inconsistent naming, broken governance.

**Correct Pattern:**
```sql
-- See Tag Fundamentals section for CREATE TAG with ALLOWED_VALUES
GRANT APPLY ON TAG GOVERNANCE.TAGS.DATA_CLASSIFICATION TO ROLE ANALYTICS_TEAM;
```

### Anti-Pattern 2: Not Leveraging Inheritance

```sql
-- BAD: Manually tagging every column
ALTER TABLE t1 MODIFY COLUMN col1 SET TAG TAG1='val';
ALTER TABLE t1 MODIFY COLUMN col2 SET TAG TAG1='val';
-- ... hundreds more
```

**Problem:** Massive maintenance overhead, inconsistent coverage.

**Correct Pattern:**
```sql
ALTER SCHEMA ANALYTICS.SENSITIVE SET TAG
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = 'CONFIDENTIAL';
-- All tables and columns inherit automatically
```

### Anti-Pattern 3: Tags Without ALLOWED_VALUES

```sql
-- BAD: Inconsistent values
ALTER DATABASE DB1 SET TAG ENVIRONMENT = 'prod';
ALTER DATABASE DB2 SET TAG ENVIRONMENT = 'PROD';
ALTER DATABASE DB3 SET TAG ENVIRONMENT = 'Production';
```

**Problem:** Broken reporting, unreliable policy enforcement.

**Correct Pattern:**
```sql
-- See Tag Fundamentals section for CREATE TAG with ALLOWED_VALUES
-- Use ALLOWED_VALUES to enforce consistency across all assignments
```

### Anti-Pattern 4: Missing Cost Attribution Tags

```sql
-- BAD: No cost tracking
CREATE WAREHOUSE WH_ANALYTICS WAREHOUSE_SIZE = 'LARGE';
```

**Problem:** No chargeback capability, no accountability.

**Correct Pattern:**
```sql
ALTER WAREHOUSE WH_ANALYTICS SET TAG
  GOVERNANCE.TAGS.COST_CENTER = 'ANALYTICS',
  GOVERNANCE.TAGS.OWNER_TEAM = 'ANALYTICS_PLATFORM';
```

### Anti-Pattern 5: Not Monitoring Coverage

```sql
-- BAD: Tags created but never audited
CREATE TAG GOVERNANCE.TAGS.PII_LEVEL ...;
-- No monitoring of which tables are tagged
```

**Problem:** False sense of security, governance gaps.

**Correct Pattern:**
```sql
SELECT t.table_name, 'Missing PII_LEVEL' AS issue
FROM INFORMATION_SCHEMA.TABLES t
WHERE NOT EXISTS (
  SELECT 1 FROM SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES tr
  WHERE tr.object_name = t.table_name AND tr.tag_name = 'PII_LEVEL'
);
```

## Tag Fundamentals

**Key Characteristics:**
- Schema-level objects (fully qualified: `DATABASE.SCHEMA.TAG_NAME`)
- Key-value pairs assigned to objects
- Up to 50 unique tags per object
- ALLOWED_VALUES constraints enforce consistency

**Tag Creation:**
```sql
CREATE SCHEMA IF NOT EXISTS GOVERNANCE.TAGS;

CREATE TAG GOVERNANCE.TAGS.ENVIRONMENT
  ALLOWED_VALUES 'DEV', 'QA', 'STAGING', 'PROD';

CREATE TAG GOVERNANCE.TAGS.DATA_CLASSIFICATION
  ALLOWED_VALUES 'PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED';
```

**Tag Assignment:**
```sql
-- During creation
CREATE DATABASE ANALYTICS WITH TAG (GOVERNANCE.TAGS.COST_CENTER = 'DATA_SCIENCE');

-- On existing objects
ALTER TABLE CUSTOMERS SET TAG
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = 'CONFIDENTIAL',
  GOVERNANCE.TAGS.PII_LEVEL = 'HIGH';

-- On columns
ALTER TABLE CUSTOMERS MODIFY COLUMN email SET TAG
  GOVERNANCE.TAGS.PII_LEVEL = 'MEDIUM';
```

## Tag Inheritance

**Hierarchy:** Account, then Database, then Schema, then Table, then Column

Tags flow top-down:
- Database tags inherit to schemas, tables, columns
- Schema tags inherit to tables, views, columns
- Table tags inherit to columns
- Child objects can override inherited tags

```sql
-- Set at database level
ALTER DATABASE ANALYTICS SET TAG GOVERNANCE.TAGS.COST_CENTER = 'DATA_SCIENCE';
-- All schemas, tables, columns inherit automatically

-- Override for specific table
ALTER TABLE ANALYTICS.SENSITIVE.PUBLIC_SUMMARY SET TAG
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = 'INTERNAL';  -- Exception
```

## Tag-Based Masking Policies

Assign masking policy once to a tag; automatically applies to all matching columns.

```sql
-- Create semantic category tag
CREATE TAG GOVERNANCE.TAGS.SEMANTIC_CATEGORY
  ALLOWED_VALUES 'EMAIL', 'PHONE', 'SSN', 'NAME';

-- Create masking policies
CREATE MASKING POLICY GOVERNANCE.POLICIES.MASK_EMAIL AS (val STRING) RETURNS STRING ->
  CASE WHEN CURRENT_ROLE() IN ('ADMIN') THEN val
       ELSE REGEXP_REPLACE(val, '.+@', '***@') END;

-- Associate masking policy with tag
ALTER TAG GOVERNANCE.TAGS.SEMANTIC_CATEGORY SET
  MASKING POLICY GOVERNANCE.POLICIES.MASK_EMAIL;

-- Tag columns for automatic masking
ALTER TABLE CUSTOMERS MODIFY COLUMN email SET TAG
  GOVERNANCE.TAGS.SEMANTIC_CATEGORY = 'EMAIL';
```

## Tag-Based Row Access Policies

Assign row access policy to a tag; automatically filters rows on all tagged tables.

```sql
-- Create row access policy based on tag value
CREATE ROW ACCESS POLICY GOVERNANCE.POLICIES.REGION_FILTER AS (region_val VARCHAR)
  RETURNS BOOLEAN ->
  CURRENT_ROLE() IN ('ADMIN') OR region_val = CURRENT_SESSION()::VARCHAR;

-- Associate row access policy with tag
ALTER TAG GOVERNANCE.TAGS.REGION SET
  ROW ACCESS POLICY GOVERNANCE.POLICIES.REGION_FILTER;

-- Tag tables — row access policy automatically applies
ALTER TABLE SALES SET TAG GOVERNANCE.TAGS.REGION = 'US';
ALTER TABLE ORDERS SET TAG GOVERNANCE.TAGS.REGION = 'EU';
```

## Tag Lifecycle Management

```sql
-- Remove tag from object
ALTER TABLE CUSTOMERS UNSET TAG GOVERNANCE.TAGS.DATA_CLASSIFICATION;
ALTER WAREHOUSE WH_ANALYTICS UNSET TAG GOVERNANCE.TAGS.COST_CENTER;

-- Drop tag definition (removes all assignments)
DROP TAG IF EXISTS GOVERNANCE.TAGS.DEPRECATED_TAG;

-- Modify allowed values
ALTER TAG GOVERNANCE.TAGS.ENVIRONMENT SET ALLOWED_VALUES 'DEV', 'QA', 'STAGING', 'PROD', 'DR';
```

**Error Handling:**
- **ALLOWED_VALUES violation:** Setting a tag to a value not in the allowed list returns an error. Fix: check allowed values with `SHOW TAGS LIKE 'TAG_NAME'` before assignment.
- **Tag quota exceeded:** Max 50 tags per object. Fix: audit with TAG_REFERENCES and consolidate redundant tags.

## Cost Attribution

**Warehouse tagging for chargeback:**
```sql
ALTER WAREHOUSE WH_ANALYTICS SET TAG
  GOVERNANCE.TAGS.COST_CENTER = 'ANALYTICS',
  GOVERNANCE.TAGS.ENVIRONMENT = 'PROD';

-- Cost attribution query
SELECT tr.tag_value, SUM(wh.credits_used) AS total_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY wh
JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES tr
  ON tr.object_name = wh.warehouse_name AND tr.object_domain = 'WAREHOUSE'
WHERE tr.tag_name = 'COST_CENTER'
GROUP BY tr.tag_value;
```

## Tag Quotas

- **50 unique tags** per object
- **50 total tags** across all columns in a table/view (plus 50 on table itself)
- **100 tag assignments** maximum per single statement

## Monitoring Tags

**TAG_REFERENCES: Function vs View**
- `TABLE(INFORMATION_SCHEMA.TAG_REFERENCES(...))` — real-time table function, scoped to current database
- `SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES` — account-level view with up to 120-minute latency

```sql
-- Get tags for specific object
SELECT * FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES('MY_DB.MY_SCHEMA.MY_TABLE', 'TABLE'));

-- All tag assignments in account
SELECT tag_name, tag_value, object_name, object_domain, apply_method
FROM SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES
WHERE tag_database = 'GOVERNANCE';

-- Find untagged tables
SELECT t.table_name, 'Missing DATA_CLASSIFICATION' AS issue
FROM INFORMATION_SCHEMA.TABLES t
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES tr
  ON tr.object_name = t.table_name AND tr.tag_name = 'DATA_CLASSIFICATION'
WHERE tr.tag_name IS NULL;

-- Tag usage statistics
SELECT tag_name, tag_value, object_domain, COUNT(*) AS count
FROM SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES
GROUP BY tag_name, tag_value, object_domain;
```

## Management Approaches

**Centralized:** Core governance team creates/manages all tags. Teams get APPLY privilege only.

**Decentralized:** Teams create tags in their schemas. Governance creates shared tags.

**Hybrid (Recommended):** Core governance tags centrally managed; domain-specific tags managed by teams.

```sql
-- Central governance
CREATE TAG GOVERNANCE.TAGS.DATA_CLASSIFICATION ...;
GRANT APPLY ON TAG ... TO ROLE DATA_ENGINEER;

-- Team-specific
CREATE TAG ANALYTICS.METADATA.MODEL_VERSION;
```

## Cloning and Replication

- **CLONE:** Tags are preserved on cloned objects
- **LIKE:** Tags are copied (not data)
- **Replication:** Tag definitions and assignments replicate to secondary databases
