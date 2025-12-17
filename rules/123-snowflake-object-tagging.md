# Snowflake Object Tagging Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** cost attribution, resource tagging, governance tags, masking policies, row access policies, tag lineage, create tags, apply tags, tag strategy, tag policies, tag compliance, tag hierarchy, tag discovery, tag management
**TokenBudget:** ~5550
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md, rules/105-snowflake-cost-governance.md, rules/107-snowflake-security-governance.md

## Purpose
Establish comprehensive best practices for Snowflake object tagging to enable effective data governance, cost attribution, security classification, and resource monitoring through consistent metadata management across all supported Snowflake objects.

## Rule Scope

Snowflake object tagging for governance, cost tracking, data classification, policy enforcement, and metadata management

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Tag-based policies** - Masking, row access driven by tags
- **Tag hierarchy** - Project, Cost Center, Environment, Owner
- **Tag at schema level** - Inheritance propagates to objects
- **Cost attribution tags** - Required for tracking/chargebacks
- **Document definitions** - Clear meaning, allowed values
- **Query tag lineage** - Understand propagation/coverage
- **Never tag inconsistently** - Use standard names across account

**Quick Checklist:**
- [ ] Tag hierarchy defined
- [ ] Tags created at account level
- [ ] Schema-level tags applied
- [ ] Tag-based policies configured
- [ ] Cost attribution tags on warehouses
- [ ] Tag lineage queries working
- [ ] Tag governance documented

## Contract

<contract>
<inputs_prereqs>
Snowflake account with tag creation privileges (`CREATE TAG`); governance requirements; cost allocation strategy; security classification taxonomy
</inputs_prereqs>

<mandatory>
SQL DDL for tag creation; tag assignment statements; TAG_REFERENCES functions; INFORMATION_SCHEMA and ACCOUNT_USAGE views
</mandatory>

<forbidden>
Creating more than 50 tags per object; creating tags without documented taxonomy; uncontrolled tag proliferation; tags without clear ownership
</forbidden>

<steps>
1. Define tag taxonomy aligned with governance and business requirements
2. Create tags with appropriate ALLOWED_VALUES constraints where applicable
3. Establish tag ownership and management approach (centralized vs decentralized)
4. Apply tags consistently across object hierarchy to leverage inheritance
5. Document tag purposes, allowed values, and responsible teams
6. Monitor tag usage and coverage using TAG_REFERENCES functions
7. Integrate tags with masking policies and cost monitoring systems
</steps>

<output_format>
Tag DDL with documentation; tag assignment statements; monitoring queries; governance reports
</output_format>

<validation>
- Verify tags created successfully with correct privileges
- Confirm tag assignments appear in TAG_REFERENCES views
- Validate tag inheritance working as expected
- Check tag-based policies functioning correctly
- Ensure cost attribution queries returning accurate results
</validation>

<design_principles>
- **Define Once, Apply Many:** Create tags in a centralized schema and apply across multiple object types
- **Leverage Inheritance:** Set tags on parent objects (databases, schemas, tables) to automatically apply to children (columns, views)
- **Control with Constraints:** Use ALLOWED_VALUES to enforce consistent tag values across the organization
- **Integrate with Policies:** Combine tags with masking policies, row access policies, and resource monitors for automated governance
- **Monitor Coverage:** Regularly audit tag usage to ensure governance policies are enforced
- **Document Taxonomy:** Maintain clear documentation of tag purposes, ownership, and allowed values
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Tag Proliferation Without Governance**
```sql
-- Different teams creating inconsistent tags
CREATE TAG ANALYTICS.TAG.SENSITIVE_DATA;
CREATE TAG FINANCE.TAG.SENSITIVE;
CREATE TAG SALES.TAG.IS_SENSITIVE;
CREATE TAG MARKETING.TAG.CONFIDENTIAL;
-- Result: 4 tags for the same concept, no consistency
```
**Problem:** Uncontrolled tag creation leads to duplicate concepts, inconsistent naming, and inability to query/enforce governance consistently.

**Correct Pattern:**
```sql
-- Centralized tag definition with clear taxonomy
CREATE TAG GOVERNANCE.TAGS.DATA_CLASSIFICATION
  ALLOWED_VALUES 'PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED'
  COMMENT = 'Standard data classification per InfoSec policy SEC-001';

-- All teams use the same tag
GRANT APPLY ON TAG GOVERNANCE.TAGS.DATA_CLASSIFICATION TO ROLE ANALYTICS_TEAM;
GRANT APPLY ON TAG GOVERNANCE.TAGS.DATA_CLASSIFICATION TO ROLE FINANCE_TEAM;
```
**Benefits:** Consistent taxonomy, enforceable governance, accurate reporting, simplified policy management.

**Anti-Pattern 2: Not Leveraging Tag Inheritance**
```sql
-- Manually tagging every column in every table
ALTER TABLE ANALYTICS.SENSITIVE.TABLE1 MODIFY COLUMN col1 SET TAG TAG1='val';
ALTER TABLE ANALYTICS.SENSITIVE.TABLE1 MODIFY COLUMN col2 SET TAG TAG1='val';
ALTER TABLE ANALYTICS.SENSITIVE.TABLE1 MODIFY COLUMN col3 SET TAG TAG1='val';
-- ... hundreds more columns
ALTER TABLE ANALYTICS.SENSITIVE.TABLE2 MODIFY COLUMN col1 SET TAG TAG1='val';
-- ... endless repetition
```
**Problem:** Massive maintenance overhead, high error rate, inconsistent coverage, difficult auditing.

**Correct Pattern:**
```sql
-- Tag at schema level for broad inheritance
ALTER SCHEMA ANALYTICS.SENSITIVE SET TAG
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = 'CONFIDENTIAL',
  GOVERNANCE.TAGS.COST_CENTER = 'ANALYTICS';

-- All tables and columns automatically inherit
-- Override only when specific objects need different classification
ALTER TABLE ANALYTICS.SENSITIVE.PUBLIC_SUMMARY SET TAG
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = 'INTERNAL';  -- Exception to rule
```
**Benefits:** Minimal maintenance, consistent coverage, inheritance ensures no objects missed, easy to audit.

**Anti-Pattern 3: Tags Without ALLOWED_VALUES**
```sql
-- Tag without constraints
CREATE TAG GOVERNANCE.TAGS.ENVIRONMENT;

-- Teams apply inconsistent values
ALTER DATABASE DB1 SET TAG GOVERNANCE.TAGS.ENVIRONMENT = 'prod';
ALTER DATABASE DB2 SET TAG GOVERNANCE.TAGS.ENVIRONMENT = 'PROD';
ALTER DATABASE DB3 SET TAG GOVERNANCE.TAGS.ENVIRONMENT = 'Production';
ALTER DATABASE DB4 SET TAG GOVERNANCE.TAGS.ENVIRONMENT = 'prd';
-- Query results become unreliable
```
**Problem:** Inconsistent tag values break reporting, cost attribution fails, policy enforcement unreliable.

**Correct Pattern:**
```sql
-- Tag with explicit allowed values
CREATE TAG GOVERNANCE.TAGS.ENVIRONMENT
  ALLOWED_VALUES 'DEV', 'QA', 'STAGING', 'PROD'
  COMMENT = 'Deployment environment - must match SDLC stages';

-- Only valid values accepted
ALTER DATABASE DB1 SET TAG GOVERNANCE.TAGS.ENVIRONMENT = 'PROD';  -- Works
ALTER DATABASE DB2 SET TAG GOVERNANCE.TAGS.ENVIRONMENT = 'Production';  -- Fails
```
**Benefits:** Data quality enforced at creation time, reliable reporting, consistent governance, self-documenting taxonomy.

**Anti-Pattern 4: Missing Cost Attribution Tags on Warehouses**
```sql
-- Warehouse created without cost tracking tags
CREATE WAREHOUSE WH_ANALYTICS
  WAREHOUSE_SIZE = 'LARGE'
  AUTO_SUSPEND = 300;
-- No way to attribute costs to business unit or project
```
**Problem:** Cannot perform chargeback, no accountability for costs, budget overruns without responsible party, inability to optimize spend by team/project.

**Correct Pattern:**
```sql
-- See 119-snowflake-warehouse-management.md for complete pattern
CREATE WAREHOUSE WH_ANALYTICS
  WAREHOUSE_SIZE = 'LARGE'
  AUTO_SUSPEND = 300;

-- Apply mandatory cost attribution tags
ALTER WAREHOUSE WH_ANALYTICS SET TAG
  GOVERNANCE.TAGS.COST_CENTER = 'ANALYTICS',
  GOVERNANCE.TAGS.WORKLOAD_TYPE = 'BI_INTERACTIVE',
  GOVERNANCE.TAGS.ENVIRONMENT = 'PROD',
  GOVERNANCE.TAGS.OWNER_TEAM = 'ANALYTICS_PLATFORM';

-- Cost queries now work accurately
SELECT tag_value, SUM(credits_used) AS total_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY wh
JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES tr
  ON tr.object_name = wh.warehouse_name
WHERE tr.tag_name = 'COST_CENTER'
GROUP BY tag_value;
```
**Benefits:** Accurate cost attribution, chargeback capability, accountability, cost optimization by team/project.

**Anti-Pattern 5: Not Monitoring Tag Coverage**
```sql
-- Tags created but never monitored
CREATE TAG GOVERNANCE.TAGS.PII_LEVEL
  ALLOWED_VALUES 'NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL';

-- No auditing of which tables are tagged
-- Governance policies ineffective if objects aren't tagged
```
**Problem:** False sense of security, governance gaps, compliance failures, unprotected sensitive data.

**Correct Pattern:**
```sql
-- Create tag with governance requirements
CREATE TAG GOVERNANCE.TAGS.PII_LEVEL
  ALLOWED_VALUES 'NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL';

-- Establish monitoring query
CREATE VIEW GOVERNANCE.MONITORING.VW_UNTAGGED_TABLES AS
SELECT
  table_catalog,
  table_schema,
  table_name,
  'Missing PII_LEVEL tag' AS issue
FROM INFORMATION_SCHEMA.TABLES t
WHERE table_schema NOT IN ('INFORMATION_SCHEMA', 'ACCOUNT_USAGE')
  AND NOT EXISTS (
    SELECT 1
    FROM SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES tr
    WHERE tr.object_database = t.table_catalog
      AND tr.object_schema = t.table_schema
      AND tr.object_name = t.table_name
      AND tr.tag_name = 'PII_LEVEL'
  );

-- Schedule regular review
-- Set up alerts when untagged objects appear
```
**Benefits:** Continuous compliance, proactive governance, early detection of gaps, audit readiness.

## Post-Execution Checklist

- [ ] Tag taxonomy defined and documented with clear ownership
- [ ] Tags created in centralized governance schema (e.g., GOVERNANCE.TAGS)
- [ ] ALLOWED_VALUES constraints applied to tags requiring consistency
- [ ] Tag creation privileges restricted to TAG_ADMIN or equivalent role
- [ ] APPLY TAG privileges granted to functional roles appropriately
- [ ] Tag inheritance leveraged at schema/database level where applicable
- [ ] Warehouse tagging follows `119-snowflake-warehouse-management.md` requirements
- [ ] Tag-based masking policies configured for sensitive data categories
- [ ] Cost attribution tags applied to all warehouses (COST_CENTER minimum)
- [ ] Monitoring queries established for tag coverage auditing
- [ ] TAG_REFERENCES views queried regularly to verify governance
- [ ] Tag quota limits understood and monitored (<50 per object)
- [ ] Replication behavior documented for replicated databases
- [ ] Management approach (centralized/decentralized/hybrid) documented and enforced

## Validation

- **Success Checks:**
  - Tags created successfully with appropriate privileges and ALLOWED_VALUES
  - Tag assignments visible in TAG_REFERENCES functions and views
  - Tag inheritance working correctly (child objects show inherited tags)
  - Tag-based masking policies automatically protecting tagged columns
  - Cost attribution queries returning accurate results by tag values
  - Coverage monitoring queries identifying untagged objects correctly
  - Warehouse tags present and accurate per `119-snowflake-warehouse-management.md`
  - Tag quotas not exceeded (< 50 per object, < 50 for columns)

- **Negative Tests:**
  - Assigning invalid tag value (not in ALLOWED_VALUES) fails with clear error
  - Non-privileged role attempting to create tag fails
  - Attempting to exceed 50 tag limit per object fails gracefully
  - Querying TAG_REFERENCES with invalid object name returns empty set (not error)
  - Tag removal (UNSET TAG) works correctly without affecting other tags
  - Dropped tags no longer appear in TAG_REFERENCES views

> **Investigation Required**
> When applying this rule:
> 1. **Read actual tag definitions BEFORE recommending tag applications**
> 2. **Query TAG_REFERENCES to verify existing tag coverage before creating duplicates**
> 3. **Never assume tag taxonomy—check INFORMATION_SCHEMA.TAGS or ACCOUNT_USAGE views**
> 4. **Verify ALLOWED_VALUES constraints before recommending tag values**
> 5. **Check object hierarchy to determine optimal tagging level (database vs schema vs table)**
>
> **Anti-Pattern:**
> "You should tag this table with COST_CENTER = 'ANALYTICS'..."
> "Typically tags are created in the PUBLIC schema..."
>
> **Correct Pattern:**
> "Let me check existing tags first:"
> ```sql
> SHOW TAGS IN SCHEMA GOVERNANCE.TAGS;
> SELECT * FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES('YOUR_TABLE', 'TABLE'));
> ```
> "After reviewing the existing tag taxonomy, I found [specific tags]. Here's my recommendation based on what I observed..."

## Output Format Examples

```sql
-- Filename: tag_implementation.sql
-- Description: [Tag governance implementation for specific use case]
-- Tags: [Tag names being implemented]
-- Purpose: [Cost attribution | Data classification | Policy enforcement]

-- Step 1: Create or verify tag definitions
SHOW TAGS IN SCHEMA GOVERNANCE.TAGS;

CREATE TAG IF NOT EXISTS GOVERNANCE.TAGS.TAG_NAME
  ALLOWED_VALUES 'VALUE1', 'VALUE2', 'VALUE3'
  COMMENT = 'Clear description of tag purpose and usage';

-- Step 2: Grant privileges
GRANT APPLY ON TAG GOVERNANCE.TAGS.TAG_NAME TO ROLE FUNCTIONAL_ROLE;

-- Step 3: Apply tags at appropriate hierarchy level
ALTER [OBJECT_TYPE] [OBJECT_NAME] SET TAG
  GOVERNANCE.TAGS.TAG_NAME = 'VALUE',
  GOVERNANCE.TAGS.TAG_NAME2 = 'VALUE2';

-- Step 4: Verify tag assignments
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES(
  '[OBJECT_NAME]',
  '[OBJECT_TYPE]'
));

-- Step 5: Monitor coverage
-- [Coverage monitoring query specific to use case]
```

## References

### External Documentation
- [Object Tagging Introduction](https://docs.snowflake.com/en/user-guide/object-tagging/introduction) - Complete overview of Snowflake object tagging concepts and capabilities
- [Tag Inheritance](https://docs.snowflake.com/en/user-guide/object-tagging/tag-inheritance) - How tags inherit through object hierarchies
- [Automatic Tag Propagation](https://docs.snowflake.com/en/user-guide/object-tagging/tag-propagation) - Tag propagation through views, CTAS, and lineage
- [Working with Object Tags](https://docs.snowflake.com/en/user-guide/object-tagging/work-with-tags) - Create, assign, and manage tags
- [Monitor Object Tags](https://docs.snowflake.com/en/user-guide/object-tagging/monitor-tags) - Query and audit tag usage
- [Tag-Based Masking Policies](https://docs.snowflake.com/en/user-guide/security-column-ext) - Automated data protection using tags
- [TAG_REFERENCES Function](https://docs.snowflake.com/en/sql-reference/info-schema/tag_references) - Query tag assignments
- [Setting up object tags for cost attribution](https://docs.snowflake.com/en/user-guide/cost-attribution-tags) - Cost tracking patterns with tags

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **Security Governance**: `rules/107-snowflake-security-governance.md`
- **Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`
- **Data Governance**: `rules/930-data-governance-quality.md`

> **[AI] Claude 4 Specific Guidance**
> **Claude 4 Optimizations:**
> - Use parallel tool calls to check existing tags and object state simultaneously
> - Investigation-first: Always query INFORMATION_SCHEMA.TAGS before recommending tag creation
> - Verify tag inheritance by querying TAG_REFERENCES with level column
> - When analyzing coverage gaps, read actual tag assignments before recommending fixes

## 1. Tag Fundamentals

### What is a Tag?

**MANDATORY:**
A tag is a schema-level object that can be assigned to Snowflake objects as a key-value pair. Tags enable metadata-driven governance, cost attribution, and policy automation.

**Key Characteristics:**
- Tags are schema-level objects (must be fully qualified: `DATABASE.SCHEMA.TAG_NAME`)
- Each tag assignment consists of a tag name and a string value
- An object can have multiple tags simultaneously (up to 50 unique tags)
- A single tag can be assigned to different object types
- Tag values can be constrained using ALLOWED_VALUES for consistency

**Tag Naming Convention:**
```sql
-- Recommended: UPPERCASE with underscores for clarity
CREATE TAG GOVERNANCE.TAGS.COST_CENTER;
CREATE TAG GOVERNANCE.TAGS.DATA_CLASSIFICATION;
CREATE TAG GOVERNANCE.TAGS.PII_LEVEL;
```

### Tag Creation

**RECOMMENDED:**
Create tags in a dedicated governance schema for centralized management.

**Basic Tag Creation:**
```sql
-- Create dedicated schema for tags
CREATE SCHEMA IF NOT EXISTS GOVERNANCE.TAGS;

-- Simple tag without constraints
CREATE TAG GOVERNANCE.TAGS.PROJECT_NAME
  COMMENT = 'Project or initiative associated with this object';

-- Tag with allowed values (enforced constraints)
CREATE TAG GOVERNANCE.TAGS.ENVIRONMENT
  ALLOWED_VALUES 'DEV', 'QA', 'STAGING', 'PROD'
  COMMENT = 'Deployment environment classification';

-- Tag for cost allocation
CREATE TAG GOVERNANCE.TAGS.COST_CENTER
  ALLOWED_VALUES 'FINANCE', 'MARKETING', 'DATA_SCIENCE', 'ENGINEERING', 'OPERATIONS'
  COMMENT = 'Business unit for cost attribution';

-- Tag for data classification
CREATE TAG GOVERNANCE.TAGS.DATA_CLASSIFICATION
  ALLOWED_VALUES 'PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED'
  COMMENT = 'Data sensitivity classification level';
```

### Tag Assignment

**MANDATORY:**
Assign tags at the appropriate level in the object hierarchy to maximize inheritance benefits.

**Assignment Patterns:**
```sql
-- Assign tags during object creation
CREATE DATABASE ANALYTICS
  WITH TAG (
    GOVERNANCE.TAGS.COST_CENTER = 'DATA_SCIENCE',
    GOVERNANCE.TAGS.ENVIRONMENT = 'PROD'
  );

-- Assign tags to existing objects
ALTER TABLE CUSTOMERS SET TAG
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = 'CONFIDENTIAL',
  GOVERNANCE.TAGS.PII_LEVEL = 'HIGH';

-- Assign tags to columns
ALTER TABLE CUSTOMERS MODIFY COLUMN email SET TAG
  GOVERNANCE.TAGS.PII_LEVEL = 'MEDIUM';

-- Assign multiple tags in one statement
ALTER WAREHOUSE WH_ANALYTICS SET TAG
  GOVERNANCE.TAGS.COST_CENTER = 'ANALYTICS',
  GOVERNANCE.TAGS.WORKLOAD_TYPE = 'BI_INTERACTIVE',
  GOVERNANCE.TAGS.ENVIRONMENT = 'PROD',
  GOVERNANCE.TAGS.OWNER_TEAM = 'ANALYTICS_PLATFORM';
```

### Tag Removal

**Unset Tags:**
```sql
-- Remove a specific tag from an object
ALTER TABLE CUSTOMERS UNSET TAG GOVERNANCE.TAGS.PROJECT_NAME;

-- Remove multiple tags
ALTER TABLE CUSTOMERS UNSET TAG
  GOVERNANCE.TAGS.PROJECT_NAME,
  GOVERNANCE.TAGS.LEGACY_SYSTEM;

-- Drop a tag entirely (requires ownership)
DROP TAG IF EXISTS GOVERNANCE.TAGS.DEPRECATED_TAG;
```

## 2. Tag Inheritance

**RECOMMENDED:**
**CRITICAL:** Leverage tag inheritance to minimize manual tagging and ensure consistent governance across object hierarchies.

### Inheritance Rules

**Snowflake Object Hierarchy:**

Tag inheritance flows top-down:
- **Account** (root)
  - **Database** - tags inherit to schemas, tables, columns
    - **Schema** - tags inherit to tables, views, columns
      - **Table** - tags inherit to columns
      - **View** - tags inherit to columns
  - **Warehouse** - standalone, no inheritance

**How Inheritance Works:**
- Tags set on a database automatically apply to all schemas, tables, and columns within
- Tags set on a schema apply to all tables, views, and columns within
- Tags set on a table apply to all columns in that table
- Child objects can override inherited tags with explicit assignments

**Example:**
```sql
-- Set tag at database level
ALTER DATABASE ANALYTICS SET TAG
  GOVERNANCE.TAGS.COST_CENTER = 'DATA_SCIENCE',
  GOVERNANCE.TAGS.ENVIRONMENT = 'PROD';

-- All schemas, tables, and columns inherit these tags automatically

-- Query to verify inheritance
SELECT
  tag_database,
  tag_schema,
  tag_name,
  tag_value,
  object_database,
  object_schema,
  object_name,
  column_name,
  level  -- Shows inheritance level: DATABASE, SCHEMA, TABLE, COLUMN
FROM SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES
WHERE tag_database = 'GOVERNANCE'
  AND tag_schema = 'TAGS'
ORDER BY object_database, object_schema, object_name, column_name;
```

### Overriding Inherited Tags

**RECOMMENDED:**
Override inherited tags at lower levels when specific objects require different classifications.

**Example:**
```sql
-- Database-level tag (inherited by all objects)
ALTER DATABASE ANALYTICS SET TAG
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = 'INTERNAL';

-- Override for specific table with higher sensitivity
ALTER TABLE ANALYTICS.SENSITIVE.CUSTOMER_PII SET TAG
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = 'RESTRICTED';

-- Column-level override for especially sensitive field
ALTER TABLE ANALYTICS.SENSITIVE.CUSTOMER_PII MODIFY COLUMN ssn SET TAG
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = 'RESTRICTED',
  GOVERNANCE.TAGS.PII_LEVEL = 'CRITICAL';
```

## 3. Automatic Tag Propagation

**RECOMMENDED:**
**ENTERPRISE EDITION REQUIRED:** Automatic tag propagation is an Enterprise Edition feature.

### Propagation Scenarios

**1. View-Based Propagation:**
Tags automatically propagate from base tables to views when configured.

```sql
-- Enable propagation on source table tag
CREATE TAG GOVERNANCE.TAGS.SENSITIVE_DATA
  ALLOWED_VALUES 'YES', 'NO';

-- Tag the source table
ALTER TABLE SOURCE_TABLE SET TAG
  GOVERNANCE.TAGS.SENSITIVE_DATA = 'YES';

-- Views created from this table can inherit the tag automatically
-- (Configure propagation policy via ACCOUNTADMIN)
```

**2. CTAS (Create Table As Select) Propagation:**
Tags propagate from source tables to newly created tables via CTAS.

```sql
-- Source table has tags
ALTER TABLE SOURCE_ORDERS SET TAG
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = 'INTERNAL';

-- CTAS inherits tags from source
CREATE TABLE ORDERS_ARCHIVE AS
SELECT * FROM SOURCE_ORDERS;

-- Verify propagation
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES('ORDERS_ARCHIVE', 'TABLE'));
```

**3. Lineage-Based Propagation:**
Configure tags to follow data lineage through transformations.

### Propagation Configuration

**Check Propagation Method:**
```sql
-- The apply_method column shows how a tag was associated
SELECT
  tag_name,
  tag_value,
  apply_method,  -- VALUES: MANUAL, INHERITED, PROPAGATED, CLASSIFICATION
  object_name,
  column_name,
  level
FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(
  'MY_DATABASE.MY_SCHEMA.MY_TABLE'
));
```

## 4. Tag-Based Masking Policies

**MANDATORY:**
**CRITICAL:** Combine tags with masking policies for scalable, automated data protection.

### Tag-Based Masking Pattern

**Benefits:**
- Assign masking policy once to a tag
- Tag automatically applies masking to all matching columns
- Reduces manual policy assignments
- Ensures consistent protection across data estate

**Implementation:**
```sql
-- Step 1: Create data classification tag
CREATE TAG GOVERNANCE.TAGS.SEMANTIC_CATEGORY
  ALLOWED_VALUES 'EMAIL', 'PHONE', 'SSN', 'NAME', 'ADDRESS'
  COMMENT = 'Semantic data type for automated masking';

-- Step 2: Create masking policy for each category
CREATE MASKING POLICY GOVERNANCE.POLICIES.MASK_EMAIL AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val
    ELSE REGEXP_REPLACE(val, '.+@', '***@')
  END
  COMMENT = 'Mask email addresses for non-privileged users';

CREATE MASKING POLICY GOVERNANCE.POLICIES.MASK_SSN AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('ADMIN', 'COMPLIANCE') THEN val
    ELSE 'XXX-XX-' || RIGHT(val, 4)
  END
  COMMENT = 'Mask SSN, show last 4 digits only';

-- Step 3: Associate masking policies with tags
ALTER TAG GOVERNANCE.TAGS.SEMANTIC_CATEGORY SET
  MASKING POLICY GOVERNANCE.POLICIES.MASK_EMAIL;

-- When SEMANTIC_CATEGORY = 'SSN', use SSN masking
ALTER TAG GOVERNANCE.TAGS.SEMANTIC_CATEGORY SET
  MASKING POLICY GOVERNANCE.POLICIES.MASK_SSN;

-- Step 4: Tag columns for automatic masking
ALTER TABLE CUSTOMERS MODIFY COLUMN email SET TAG
  GOVERNANCE.TAGS.SEMANTIC_CATEGORY = 'EMAIL';

ALTER TABLE EMPLOYEES MODIFY COLUMN ssn SET TAG
  GOVERNANCE.TAGS.SEMANTIC_CATEGORY = 'SSN';

-- Columns are now automatically masked based on tag value
```

### Verify Tag-Based Masking

```sql
-- Check which masking policies are associated with tags
SELECT
  tag_database,
  tag_schema,
  tag_name,
  policy_database,
  policy_schema,
  policy_name,
  policy_kind
FROM SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES
WHERE policy_kind = 'MASKING_POLICY';

-- Check columns protected by tag-based masking
SELECT
  t.table_catalog,
  t.table_schema,
  t.table_name,
  t.column_name,
  tr.tag_name,
  tr.tag_value,
  pr.policy_name
FROM INFORMATION_SCHEMA.COLUMNS t
JOIN TABLE(INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(
  t.table_catalog || '.' || t.table_schema || '.' || t.table_name
)) tr
  ON tr.column_name = t.column_name
LEFT JOIN INFORMATION_SCHEMA.POLICY_REFERENCES pr
  ON pr.ref_entity_name = t.table_catalog || '.' || t.table_schema || '.' || t.table_name
  AND pr.ref_column_name = t.column_name
WHERE tr.tag_name = 'SEMANTIC_CATEGORY';
```

## 5. Cost Attribution with Tags

**MANDATORY:**
**BEST PRACTICE:** Use tags on warehouses and other resources for granular cost tracking and chargeback.

### Warehouse Tagging for Cost Attribution

**Mandatory Warehouse Tags:**
See `119-snowflake-warehouse-management.md` for comprehensive warehouse tagging requirements.

**Cost Attribution Query:**
```sql
-- Aggregate warehouse costs by tag values
SELECT
  tr.tag_name,
  tr.tag_value,
  w.warehouse_name,
  SUM(wh.credits_used) AS total_credits,
  SUM(wh.credits_used_compute) AS compute_credits,
  SUM(wh.credits_used_cloud_services) AS cloud_services_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY wh
JOIN SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSES w
  ON w.warehouse_id = wh.warehouse_id
JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES tr
  ON tr.object_name = w.warehouse_name
  AND tr.object_domain = 'WAREHOUSE'
WHERE wh.start_time >= DATEADD(month, -1, CURRENT_TIMESTAMP())
  AND tr.tag_name = 'COST_CENTER'
GROUP BY tr.tag_name, tr.tag_value, w.warehouse_name
ORDER BY total_credits DESC;
```

### Database and Table Cost Tracking

**Tag databases and tables for storage cost attribution:**
```sql
-- Tag database for cost allocation
ALTER DATABASE ANALYTICS SET TAG
  GOVERNANCE.TAGS.COST_CENTER = 'DATA_SCIENCE',
  GOVERNANCE.TAGS.PROJECT_NAME = 'ML_PLATFORM_2024';

-- Query storage costs by tag
SELECT
  tr.tag_name,
  tr.tag_value,
  ts.table_catalog,
  ts.table_schema,
  SUM(ts.active_bytes) / POWER(1024, 3) AS active_storage_gb,
  SUM(ts.time_travel_bytes) / POWER(1024, 3) AS time_travel_gb,
  SUM(ts.failsafe_bytes) / POWER(1024, 3) AS failsafe_gb
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS ts
JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES tr
  ON tr.object_name = ts.table_catalog
  AND tr.object_domain = 'DATABASE'
WHERE ts.deleted IS NULL
  AND tr.tag_name IN ('COST_CENTER', 'PROJECT_NAME')
GROUP BY tr.tag_name, tr.tag_value, ts.table_catalog, ts.table_schema
ORDER BY active_storage_gb DESC;
```

## 6. Tag Quotas and Limitations

**MANDATORY:**
**QUOTA LIMITS:** Understand and plan for tag quotas to avoid hitting limits.

### Object-Level Quotas

**Maximum Tags Per Object:**
- **50 unique tags** per object (table, view, warehouse, etc.)
- This is a limit on different tag names, not tag/value combinations

**Examples:**
```sql
-- One tag on object (count: 1)
ALTER TABLE t1 SET TAG GOVERNANCE.TAGS.TAG1 = 'val1';

-- Two tags on object (count: 2)
ALTER TABLE t1 SET TAG
  GOVERNANCE.TAGS.TAG1 = 'val1',
  GOVERNANCE.TAGS.TAG2 = 'val1';

-- Exceeding 50 unique tags will fail
-- ALTER TABLE t1 SET TAG TAG1='v1', TAG2='v2', ..., TAG51='v51';  -- FAILS
```

### Column-Level Quotas

**Additional Quota for Table/View Columns:**
- Maximum 50 tags on the table/view itself
- PLUS maximum 50 total tags across ALL columns in the table/view

**Example:**
```sql
-- Table has 2 tags
CREATE TABLE t1 (
  col1 INT WITH TAG (GOVERNANCE.TAGS.TAG1='val1', GOVERNANCE.TAGS.TAG2='val2')
) WITH TAG (GOVERNANCE.TAGS.TAG3='val3', GOVERNANCE.TAGS.TAG4='val4');

-- Result: 2 tags on table + 2 tags on column = within limits
-- If col1 has 10 tags, 40 more tags can be added to columns in this table
```

### Batch Operation Limits

**Maximum 100 tags in single statement:**
When executing multiple CREATE/ALTER statements in a single batch, limit to 100 total tag assignments.

## 7. Management Approaches

### Centralized Management

**RECOMMENDED:**
**Best for:** Strict governance requirements, regulated industries, consistent taxonomy enforcement.

**Pattern:**
```sql
-- Create tag_admin custom role
CREATE ROLE TAG_ADMIN;
GRANT CREATE TAG ON SCHEMA GOVERNANCE.TAGS TO ROLE TAG_ADMIN;

-- Tag admin creates and manages all tags
USE ROLE TAG_ADMIN;

CREATE TAG GOVERNANCE.TAGS.DATA_CLASSIFICATION
  ALLOWED_VALUES 'PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED';

CREATE TAG GOVERNANCE.TAGS.RETENTION_PERIOD
  ALLOWED_VALUES '30_DAYS', '1_YEAR', '7_YEARS', 'INDEFINITE';

-- Grant APPLY privilege to functional roles
GRANT APPLY ON TAG GOVERNANCE.TAGS.DATA_CLASSIFICATION
  TO ROLE DATA_ENGINEER;

GRANT APPLY ON TAG GOVERNANCE.TAGS.RETENTION_PERIOD
  TO ROLE DATA_ENGINEER;

-- Data engineers can now apply tags but not create new ones
USE ROLE DATA_ENGINEER;
ALTER TABLE CUSTOMERS SET TAG
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = 'CONFIDENTIAL';
```

### Decentralized Management

**RECOMMENDED:**
**Best for:** Agile teams, self-service analytics, domain-driven governance.

**Pattern:**
```sql
-- Each team can create tags in their own schema
USE ROLE ANALYTICS_TEAM;

CREATE TAG ANALYTICS.METADATA.MODEL_VERSION;
CREATE TAG ANALYTICS.METADATA.UPDATE_FREQUENCY
  ALLOWED_VALUES 'REAL_TIME', 'HOURLY', 'DAILY', 'WEEKLY';

-- Central governance team creates shared tags
USE ROLE TAG_ADMIN;

CREATE TAG GOVERNANCE.TAGS.GLOBAL_CLASSIFICATION
  ALLOWED_VALUES 'PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED';

-- Both team-specific and global tags can coexist
USE ROLE ANALYTICS_TEAM;
ALTER TABLE ANALYTICS.MODELS.FORECAST_V2 SET TAG
  ANALYTICS.METADATA.MODEL_VERSION = 'v2.1.0',
  ANALYTICS.METADATA.UPDATE_FREQUENCY = 'HOURLY',
  GOVERNANCE.TAGS.GLOBAL_CLASSIFICATION = 'INTERNAL';
```

### Hybrid Approach

**RECOMMENDED:**
**Best for:** Most organizations balancing governance and agility.

```sql
-- Core governance tags managed centrally
USE ROLE TAG_ADMIN;
CREATE TAG GOVERNANCE.TAGS.DATA_CLASSIFICATION [...];
CREATE TAG GOVERNANCE.TAGS.COST_CENTER [...];

-- Domain-specific tags managed by teams
USE ROLE ANALYTICS_LEAD;
CREATE TAG ANALYTICS.METADATA.DASHBOARD_TIER [...];

USE ROLE ML_LEAD;
CREATE TAG ML.METADATA.MODEL_ACCURACY_SCORE;
```

## 8. Monitoring and Querying Tags

### TAG_REFERENCES Functions

**MANDATORY:**
Use TAG_REFERENCES functions to query tag assignments and verify governance coverage.

**INFORMATION_SCHEMA Functions (Current Permissions):**
```sql
-- Get tags for a specific object
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES(
  'MY_DATABASE.MY_SCHEMA.MY_TABLE',
  'TABLE'
));

-- Get tags for all columns in a table (includes inherited)
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(
  'MY_DATABASE.MY_SCHEMA.MY_TABLE'
));

-- With lineage tracking (shows tag origin)
SELECT *
FROM TABLE(ACCOUNT_USAGE.TAG_REFERENCES_WITH_LINEAGE(
  'MY_DATABASE.MY_SCHEMA.MY_TABLE'
));
```

**ACCOUNT_USAGE View (Historical, All Objects):**
```sql
-- All tag assignments in account (last 365 days)
SELECT
  tag_database,
  tag_schema,
  tag_name,
  tag_value,
  object_database,
  object_schema,
  object_name,
  object_domain,  -- TABLE, VIEW, WAREHOUSE, DATABASE, etc.
  column_name,
  apply_method    -- MANUAL, INHERITED, PROPAGATED, CLASSIFICATION
FROM SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES
WHERE tag_database = 'GOVERNANCE'
  AND tag_schema = 'TAGS'
ORDER BY object_database, object_schema, object_name;
```

### Tag Coverage Analysis

**Find untagged objects:**
```sql
-- Tables without required tags
WITH required_tags AS (
  SELECT 'DATA_CLASSIFICATION' AS tag_name UNION ALL
  SELECT 'COST_CENTER' UNION ALL
  SELECT 'OWNER_TEAM'
)
SELECT
  t.table_catalog,
  t.table_schema,
  t.table_name,
  rt.tag_name AS missing_tag
FROM INFORMATION_SCHEMA.TABLES t
CROSS JOIN required_tags rt
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES tr
  ON tr.object_database = t.table_catalog
  AND tr.object_schema = t.table_schema
  AND tr.object_name = t.table_name
  AND tr.object_domain = 'TABLE'
  AND tr.tag_name = rt.tag_name
WHERE t.table_schema NOT IN ('INFORMATION_SCHEMA', 'ACCOUNT_USAGE')
  AND tr.tag_name IS NULL
ORDER BY t.table_catalog, t.table_schema, t.table_name, rt.tag_name;
```

**Tag usage statistics:**
```sql
-- Count objects by tag value
SELECT
  tag_name,
  tag_value,
  object_domain,
  COUNT(*) AS object_count
FROM SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES
WHERE tag_database = 'GOVERNANCE'
  AND tag_schema = 'TAGS'
  AND deleted IS NULL
GROUP BY tag_name, tag_value, object_domain
ORDER BY tag_name, object_count DESC;
```

## 9. Supported Objects

**MANDATORY:**
Tags can be applied to the following Snowflake objects (partial list of most common):

**Taggable Object Types:**
- **Account** - Requires APPLY TAG privilege globally
- **Database** - Tags inherit to all child objects
- **Schema** - Tags inherit to tables, views, columns
- **Table** - Tags inherit to columns; includes event tables
- **View** - Tags inherit to columns
- **Materialized View** - Supports tagging
- **Dynamic Table** - Supports tagging
- **External Table** - Use ALTER TABLE to manage tags
| Iceberg Table | Supports tagging |
| Stream | Supports tagging |
| Task | Use ALTER TASK to set tags |
| Pipe | Use ALTER PIPE to set tags |
| Stage | Use ALTER STAGE to set tags |
| Warehouse | Critical for cost attribution |
| User | Supports tagging |
| Role | Supports tagging |
| Integration | All types supported via ALTER INTEGRATION |
| Function/Procedure | Use ALTER FUNCTION/PROCEDURE |
| Masking Policy | Supports tagging |
| Row Access Policy | Supports tagging |
| Notebook | Supports tagging |

**Full list:** See [official documentation](https://docs.snowflake.com/en/user-guide/object-tagging/introduction#supported-objects) for complete supported objects table.

## 10. Replication and Cloning

### Tag Replication

**MANDATORY:**
Tags and their assignments replicate within primary database to secondary database in database replication.

**Behavior:**
- Tag definitions replicate to secondary
- Tag assignments replicate to secondary
- Changes in primary automatically sync to secondary

### Cloning with Tags

**CREATE TABLE … CLONE:**
```sql
-- Source table with tags
ALTER TABLE SOURCE_TABLE SET TAG
  GOVERNANCE.TAGS.DATA_CLASSIFICATION = 'CONFIDENTIAL',
  GOVERNANCE.TAGS.PROJECT_NAME = 'ML_2024';

-- Clone inherits all tags
CREATE TABLE CLONED_TABLE CLONE SOURCE_TABLE;

-- Verify tags cloned
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES('CLONED_TABLE', 'TABLE'));
```

**CREATE TABLE … LIKE:**
```sql
-- Table structure and tags are copied (not data)
CREATE TABLE LIKE_TABLE LIKE SOURCE_TABLE;

-- Tags are preserved in LIKE operation
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES('LIKE_TABLE', 'TABLE'));
```
