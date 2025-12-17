# Snowflake Semantic Views: Integration and Development

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** RBAC, masking policy, row access policy, Generator workflow, iterative development, synonyms, natural language queries, cortex analyst, agent integration, semantic view security, analyst troubleshooting, fix analyst, debug analyst
**TokenBudget:** ~5650
**ContextTier:** Medium
**Depends:** rules/106-snowflake-semantic-views-core.md, rules/106b-snowflake-semantic-views-querying.md

## Purpose
Provide comprehensive guidance for integrating Snowflake Semantic Views with Cortex Analyst and Cortex Agent, applying governance and security controls, and following production-ready development workflows including the Semantic View Generator tool.

## Rule Scope

Cortex integration, governance patterns, development workflows, Generator usage

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Cortex Analyst integration** - Use `semantic_view` parameter in REST API (native views, not YAML)
- **Cortex Agent grounding** - List semantic view fully qualified names in `grounding_sources`
- **Apply governance to base tables** - Masking policies, row access policies on underlying tables (not semantic views)
- **Use Generator for initial structure** - Accelerate development, then refine with synonyms and comments
- **Iterative workflow** - Generate, then Validate, then Add synonyms, then Test NLQ, then Refine, then Deploy
- **Comprehensive synonyms** - Add WITH SYNONYMS for natural language query matching
- **Test with SnowCLI** - `snow cortex analyst query --semantic-view "DB.SCHEMA.VIEW"`

**Quick Checklist:**
- [ ] Semantic view includes WITH SYNONYMS for key business terms
- [ ] COMMENT clauses provide business definitions
- [ ] Cortex Analyst REST API tested with `semantic_view` parameter
- [ ] Governance policies applied to base tables (not semantic views)
- [ ] Generator output validated before execution
- [ ] Natural language queries tested and refined
- [ ] Security inheritance verified (RBAC, masking, row access)

## Contract

<contract>
<inputs_prereqs>
- Semantic view exists in DATABASE.SCHEMA (created via `CREATE SEMANTIC VIEW`)
- Cortex Analyst/Agent access enabled in account
- Governance policies defined (masking, row access)
- Snowflake CLI configured (for testing)
</inputs_prereqs>

<mandatory>
- Cortex Analyst REST API with `semantic_view` parameter
- Cortex Agent Python SDK (`snowflake.core.cortex.Agent`)
- Semantic View Generator (Snowsight UI or API)
- SnowCLI cortex analyst commands
- Standard Snowflake governance (masking policies, row access policies, RBAC)
</mandatory>

<forbidden>
- Legacy YAML semantic models (use native views instead)
- Direct policy application to semantic views (apply to base tables)
- Hardcoded credentials in scripts
</forbidden>

<steps>
1. Create semantic view with comprehensive synonyms and comments
2. Test with Cortex Analyst REST API or SnowCLI
3. Apply governance policies to base tables (not semantic views)
4. Use Generator for initial structure, refine iteratively
5. Validate natural language query accuracy
6. Document business context and usage patterns
</steps>

<output_format>
- REST API payloads with `semantic_view` parameter
- Cortex Agent Python code with grounding sources
- SQL governance policy definitions
</output_format>

<validation>
- Cortex Analyst accepts semantic view and returns valid responses
- Natural language queries match expected business logic
- Governance policies enforce security correctly
- Generator output produces valid DDL
- Iterative refinements improve query accuracy
</validation>

<design_principles>
- **Native integration**: Prefer semantic views via `semantic_view` (or `semantic_models` containing `semantic_view`) in Cortex Analyst REST API; avoid staged YAML unless required (`semantic_model_file`)
- **Governance via base tables**: Apply masking and row access policies to underlying tables
- **Iterative refinement**: Start with Generator, enhance with synonyms and comments
- **Natural language focus**: Optimize for business user queries, not technical SQL
- **Security inheritance**: Semantic views inherit RBAC and policies from base tables
- **Development workflow**: Generate, then Validate, then Enhance, then Test, then Deploy
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Applying Governance Policies to Semantic Views Directly

**Problem:** Creating masking policies or row access policies on the semantic view itself instead of the underlying base tables.

**Why It Fails:** Semantic views are metadata layers, not data containers. Policies applied directly to semantic views don't enforce at query time. Users bypass security controls when querying through Cortex Analyst.

**Correct Pattern:**
```sql
-- BAD: Policy on semantic view (doesn't work)
ALTER SEMANTIC VIEW SEM_SALES
  ADD ROW ACCESS POLICY rap_region ON (region);

-- GOOD: Policy on base table (enforced correctly)
ALTER TABLE SALES_FACT
  ADD ROW ACCESS POLICY rap_region ON (region);

-- Semantic view inherits security from base tables automatically
-- Cortex Analyst queries respect policies on underlying data
```

### Anti-Pattern 2: Skipping Synonyms for Business Terms

**Problem:** Creating semantic views with only technical column names, without adding WITH SYNONYMS for business terminology variations.

**Why It Fails:** Business users ask "What are our Q4 revenues?" not "What is the sum of amount where fiscal_quarter = 4?". Without synonyms, Cortex Analyst fails to match natural language to schema, returning errors or incorrect results.

**Correct Pattern:**
```sql
-- BAD: No synonyms, poor NLQ matching
CREATE SEMANTIC VIEW SEM_SALES AS
  SELECT amount, fiscal_quarter, region FROM SALES_FACT;

-- GOOD: Comprehensive synonyms for natural language
CREATE SEMANTIC VIEW SEM_SALES AS
  SELECT
    amount WITH SYNONYMS = ('revenue', 'sales', 'income', 'total'),
    fiscal_quarter WITH SYNONYMS = ('quarter', 'Q1', 'Q2', 'Q3', 'Q4', 'period'),
    region WITH SYNONYMS = ('territory', 'area', 'market', 'geography')
  FROM SALES_FACT;
```

## Post-Execution Checklist

**Integration:**
- [ ] Cortex Analyst tested with `semantic_view` parameter in REST API
- [ ] Cortex Agent grounding sources include fully qualified semantic view names
- [ ] Natural language queries tested with SnowCLI
- [ ] Synonym effectiveness validated with business user queries
- [ ] No legacy YAML semantic models used

**Governance:**
- [ ] RBAC configured via base table privileges
- [ ] Masking policies applied to base tables (not semantic views)
- [ ] Row access policies applied to base tables (not semantic views)
- [ ] Security inheritance tested and verified
- [ ] Audit logging enabled for compliance
- [ ] No direct governance policies on semantic views

**Development:**
- [ ] Generator used for initial structure (if applicable)
- [ ] Generator output validated before execution
- [ ] Iterative workflow followed (Generate, then Validate, then Enhance, then Test)
- [ ] WITH SYNONYMS added for all key fields
- [ ] COMMENT clauses include business definitions
- [ ] Natural language queries tested and refined
- [ ] Performance validated via Query Profile
- [ ] Documentation created for business users

## Validation
- **Success Checks:**
  - Cortex Analyst REST API accepts `semantic_view` parameter and returns valid responses
  - Cortex Agent successfully grounds on semantic views
  - Natural language queries return expected business results
  - Synonyms map correctly to underlying columns
  - Masking policies apply through semantic views
  - Row access policies filter correctly through semantic views
  - Generator produces valid DDL
  - Iterative refinements improve query accuracy
  - SnowCLI testing succeeds
  - Security inheritance verified
- **Negative Tests:**
  - Cortex Analyst rejects invalid semantic view names
  - Direct policy application to semantic views fails (must use base tables)
  - Missing synonyms cause natural language query failures
  - Incorrect RBAC prevents unauthorized access
  - Generator output requires validation (may misclassify columns)
  - Governance gaps expose sensitive data

## Output Format Examples

```python
# Cortex Analyst Integration with Semantic View
# Purpose: <integration objective>
# Semantic View: <view_name>
# Use Case: <business use case>

import requests
import snowflake.connector

# Step 1: Verify semantic view is accessible
conn = snowflake.connector.connect(...)
cursor = conn.cursor()
cursor.execute("SHOW SEMANTIC VIEWS LIKE '<view_name>'")
print(cursor.fetchall())

# Step 2: Test semantic view query directly
cursor.execute("""
  SELECT dimension_1, metric_1
  FROM SEMANTIC_VIEW(<database>.<schema>.<view_name>)
  LIMIT 10
""")
print(cursor.fetchall())

# Step 3: Call Cortex Analyst REST API
url = f"https://{account}.snowflakecomputing.com/api/v2/cortex/analyst/message"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
payload = {
    "messages": [
        {"role": "user", "content": "What are the top 5 <metrics> by <dimension>?"}
    ],
    "semantic_view": f"{database}.{schema}.{view_name}"
}
response = requests.post(url, headers=headers, json=payload)
print(response.json())

# Step 4: Verify governance (masking, row access)
cursor.execute("SELECT CURRENT_ROLE(), CURRENT_USER()")
print(cursor.fetchall())
```

> **Investigation Required**
> When applying this rule:
> 1. **Verify semantic view exists and is accessible BEFORE integrating** - Run `SHOW SEMANTIC VIEWS` and test queries
> 2. **Check RBAC grants** - Confirm role has SELECT on semantic view and USAGE on database/schema
> 3. **Never assume security policies exist** - Query `INFORMATION_SCHEMA.POLICY_REFERENCES` to verify masking/row access policies
> 4. **Test Cortex Analyst queries** - Use REST API or Snowsight UI to validate natural language queries work
> 5. **Validate Generator output** - Always review and test generated DDL before deploying
> 6. **Make grounded recommendations based on investigated permissions and policies** - Don't suggest integrations without verifying access
>
> **Anti-Pattern:**
> "Just connect Cortex Analyst to this semantic view..."
> "The governance policies should automatically apply..."
>
> **Correct Pattern:**
> "Let me verify the semantic view is accessible and properly secured."
> [runs SHOW SEMANTIC VIEWS and checks POLICY_REFERENCES]
> "I see the view exists and has masking policies on <columns>. Let me verify your role has the necessary grants..."
> [runs SHOW GRANTS]
> "Your role has SELECT access. Here's the Cortex Analyst integration code with proper error handling..."

## References

### External Documentation
- [Cortex Analyst Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) - REST API usage and integration
- [Cortex Analyst REST API](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst#rest-api) - API endpoint reference
- [Cortex Agent Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents) - Agent grounding patterns
- [Semantic View Generator](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/semantic-model-generator) - Automated view creation tool
- [Masking Policies](https://docs.snowflake.com/en/user-guide/security-column-ddm) - Data masking documentation
- [Row Access Policies](https://docs.snowflake.com/en/user-guide/security-row) - Row-level security documentation
- [RBAC Overview](https://docs.snowflake.com/en/user-guide/security-access-control-overview) - Role-based access control

### Related Rules
- **Semantic Views Core**: `rules/106-snowflake-semantic-views-core.md` - DDL creation, validation rules, components
- **Semantic Views Querying**: `rules/106b-snowflake-semantic-views-querying.md` - Query patterns and testing
- **Snowflake Core**: `rules/100-snowflake-core.md` - Foundational Snowflake practices
- **Cortex AI/SQL**: `rules/114-snowflake-cortex-aisql.md` - Cortex functions and patterns
- **Cortex Agents**: `rules/115-snowflake-cortex-agents-core.md` - Agent design and configuration
- **Security Governance**: `rules/107-snowflake-security-governance.md` - Security policies and governance

## 1) Cortex Analyst Integration

### 1.1 REST API Usage (Native Semantic Views)

```python
import requests
import json

# Cortex Analyst with NATIVE semantic view (no YAML needed)
url = f"https://{account}.snowflakecomputing.com/api/v2/cortex/analyst/message"

headers = {
    "Authorization": f"Bearer {snowflake_token}",
    "Content-Type": "application/json"
}

payload = {
    "semantic_view": "PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH",  # Native semantic view
    "messages": [
        {
            "role": "user",
            "content": "Which transformers have the highest average load this month?"
        }
    ]
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()
print(result["message"]["content"])  # Natural language response
```

**Key Differences from YAML Approach:**
- **Native views:** Use `"semantic_view": "DB.SCHEMA.VIEW_NAME"`
- **Legacy YAML (staged file):** Use `"semantic_model_file": "@DB.SCHEMA.STAGE/path/model.yaml"`
- **No staging:** No need to upload files to internal stages
- **Version control:** DDL changes tracked via SQL migrations

### 1.2 Cortex Agent Integration

```python
from snowflake.core import Root
from snowflake.core.cortex import Agent

# Initialize Snowflake connection
root = Root(session)

# Create agent grounded on native semantic views
agent = root.databases["PROD"].schemas["GRID_DATA"].cortex_agents.create(
    Agent(
        name="grid_ops_assistant",
        grounding_sources=[
            "PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH",
            "PROD.GRID_DATA.SEM_ASSET_INVENTORY",
            "PROD.GRID_DATA.SEM_CUSTOMER_OUTAGE_IMPACT"
        ],
        instructions="You are a grid operations expert. Answer questions about transformer health, asset inventory, and customer impact.",
        model="mistral-large2"
    )
)

# Query the agent
response = agent.invoke("Show me transformers at risk of failure")
print(response["content"])
```

### 1.3 SnowCLI Testing Pattern

```bash
# Test semantic view with Cortex Analyst via SnowCLI
snow cortex analyst query \
  --semantic-view "PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH" \
  --question "What is the average load for transformers in the last 24 hours?"

# Test synonym effectiveness
snow cortex analyst query \
  --semantic-view "SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM" \
  --question "Show me revenue by product category for last year"

# Test multi-dimensional queries
snow cortex analyst query \
  --semantic-view "SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM" \
  --question "Compare sales in California vs Texas for electronics"
```

### 1.4 Synonym Design for Natural Language Queries

**Purpose:** Synonyms map business terminology to technical column names for accurate natural language query resolution.

**Effective Synonym Patterns:**

```sql
CREATE OR REPLACE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_CUSTOMER
  TABLES (
    customer AS SAMPLE_DATA.TPCDS_SF10TCL.CUSTOMER
      PRIMARY KEY (C_CUSTOMER_SK)
      WITH SYNONYMS ('customers', 'buyers', 'clients')
  )
  DIMENSIONS (
    customer.C_BIRTH_COUNTRY AS c_birth_country
      WITH SYNONYMS (
        'country',               -- Common term
        'birth country',         -- Explicit
        'nationality',           -- Business term
        'nation',                -- Alternative
        'country of origin'      -- Descriptive
      )
      COMMENT = 'Country where customer was born',

    customer.C_BIRTH_YEAR AS c_birth_year
      WITH SYNONYMS (
        'birth year',
        'year of birth',
        'year born',
        'age cohort'
      )
      COMMENT = 'Year customer was born (for demographic analysis)'
  )
  METRICS (
    customer.customer_count AS COUNT(DISTINCT C_CUSTOMER_SK)
      WITH SYNONYMS (
        'total customers',
        'number of customers',
        'customer count',
        'count of customers',
        'how many customers'
      ),

    customer.unique_countries AS COUNT(DISTINCT C_BIRTH_COUNTRY)
      WITH SYNONYMS (
        'countries represented',
        'country diversity',
        'countries',
        'number of countries'
      )
  );
```

**Synonym Best Practices:**
- Include common business terms users actually say
- Add plural and singular forms
- Include abbreviations and acronyms
- Add descriptive phrases ("how many X")
- Test with actual user questions

## 2) Governance and Security

### 2.1 Access Control

**Semantic views inherit RBAC from base tables:**

```sql
-- Grant SELECT on base table (semantic view inherits)
GRANT SELECT ON TABLE PROD.GRID_DATA.GRID_ASSETS TO ROLE BI_ANALYST;

-- Grant USAGE on semantic view schema
GRANT USAGE ON SCHEMA PROD.GRID_DATA TO ROLE BI_ANALYST;

-- No special semantic view privilege needed - standard Snowflake RBAC
```

**Role-Based Access Pattern:**

```sql
-- Create role hierarchy for semantic view access
CREATE ROLE IF NOT EXISTS DATA_ANALYST;
CREATE ROLE IF NOT EXISTS DATA_SCIENTIST;
CREATE ROLE IF NOT EXISTS BUSINESS_USER;

-- Grant access to semantic view schema
GRANT USAGE ON SCHEMA PROD.ANALYTICS TO ROLE DATA_ANALYST;
GRANT USAGE ON SCHEMA PROD.ANALYTICS TO ROLE DATA_SCIENTIST;
GRANT USAGE ON SCHEMA PROD.ANALYTICS TO ROLE BUSINESS_USER;

-- Grant access to underlying tables (semantic views inherit)
GRANT SELECT ON ALL TABLES IN SCHEMA PROD.RAW_DATA TO ROLE DATA_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA PROD.RAW_DATA TO ROLE DATA_SCIENTIST;

-- Business users only access via semantic views (no direct table access)
-- They get access through semantic view inheritance only
```

### 2.2 Data Masking

**Apply masking to base tables (semantic views reflect masked data):**

```sql
-- Create masking policy
CREATE OR REPLACE MASKING POLICY PROD.GOVERNANCE.MASK_PII AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val
    ELSE '***MASKED***'
  END;

-- Apply to base table (semantic view automatically uses masked data)
ALTER TABLE PROD.CUSTOMER_DATA.CUSTOMERS
  MODIFY COLUMN customer_email SET MASKING POLICY PROD.GOVERNANCE.MASK_PII;

-- When querying semantic view, masking applies automatically
SELECT * FROM SEMANTIC_VIEW(
  PROD.ANALYTICS.SEM_CUSTOMERS
  DIMENSIONS customer_name, customer_email
  METRICS customer_count
);
-- Output: customer_email shows '***MASKED***' for non-privileged roles
```

**Conditional Masking Pattern:**

```sql
-- Partial masking based on role
CREATE OR REPLACE MASKING POLICY PROD.GOVERNANCE.MASK_SSN AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() = 'ADMIN' THEN val                    -- Full access
    WHEN CURRENT_ROLE() = 'DATA_ANALYST' THEN CONCAT('XXX-XX-', RIGHT(val, 4))  -- Last 4 digits
    ELSE 'XXX-XX-XXXX'                                        -- Fully masked
  END;

ALTER TABLE PROD.CUSTOMER_DATA.CUSTOMERS
  MODIFY COLUMN customer_ssn SET MASKING POLICY PROD.GOVERNANCE.MASK_SSN;
```

### 2.3 Row Access Policies

**Apply row-level security to base tables:**

```sql
-- Create row access policy
CREATE OR REPLACE ROW ACCESS POLICY PROD.GOVERNANCE.RESTRICT_REGION AS (region STRING) RETURNS BOOLEAN ->
  CASE
    WHEN CURRENT_ROLE() = 'ADMIN' THEN TRUE
    WHEN CURRENT_ROLE() = 'ANALYST_WEST' AND region = 'WEST' THEN TRUE
    WHEN CURRENT_ROLE() = 'ANALYST_EAST' AND region = 'EAST' THEN TRUE
    ELSE FALSE
  END;

-- Apply to base table
ALTER TABLE PROD.GRID_DATA.GRID_ASSETS
  ADD ROW ACCESS POLICY PROD.GOVERNANCE.RESTRICT_REGION ON (region);

-- When querying semantic view, row filtering applies automatically
SELECT * FROM SEMANTIC_VIEW(
  PROD.ANALYTICS.SEM_GRID_ASSETS
  DIMENSIONS region, asset_type
  METRICS asset_count
);
-- Output: Only shows rows for user's assigned region
```

**Multi-Condition Row Access:**

```sql
-- Row access based on multiple conditions
CREATE OR REPLACE ROW ACCESS POLICY PROD.GOVERNANCE.RESTRICT_SALES_ACCESS
  AS (region STRING, department STRING) RETURNS BOOLEAN ->
  CASE
    WHEN CURRENT_ROLE() = 'ADMIN' THEN TRUE
    WHEN CURRENT_ROLE() = 'REGIONAL_MANAGER' AND region IN (
      SELECT region FROM PROD.HR.MANAGER_ASSIGNMENTS WHERE manager_user = CURRENT_USER()
    ) THEN TRUE
    WHEN CURRENT_ROLE() = 'DEPT_ANALYST' AND department IN (
      SELECT department FROM PROD.HR.DEPT_ASSIGNMENTS WHERE analyst_user = CURRENT_USER()
    ) THEN TRUE
    ELSE FALSE
  END;

ALTER TABLE PROD.SALES.DAILY_SALES
  ADD ROW ACCESS POLICY PROD.GOVERNANCE.RESTRICT_SALES_ACCESS ON (region, department);
```

### 2.4 Governance Checklist

**Before deploying semantic views to production:**

- [ ] **RBAC configured** - Roles have appropriate base table privileges
- [ ] **Masking policies applied** - PII/sensitive columns masked on base tables
- [ ] **Row access policies applied** - Row-level security enforced on base tables
- [ ] **Schema privileges granted** - Users have USAGE on semantic view schema
- [ ] **Warehouse access configured** - Users assigned to appropriate warehouses
- [ ] **Audit logging enabled** - Query history captured for compliance
- [ ] **No direct policy on semantic views** - All governance via base tables
- [ ] **Security inheritance tested** - Verified policies apply through semantic views

## 3) Development Best Practices

### 3.1 Semantic View Generator Tool

**Purpose:** Automate initial semantic view creation from existing tables to accelerate development.

**When to Use:**
- Starting new semantic view from scratch
- Exploring unfamiliar database schemas
- Creating baseline views for iterative refinement
- Rapid prototyping for Cortex Analyst testing

**Generator Workflow:**

```sql
-- Step 1: Verify Generator availability (requires ACCOUNTADMIN or appropriate role)
SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;

-- Step 2: Use Generator to create semantic view from base table
-- The Generator analyzes table structure and suggests semantic view DDL
-- (Generator UI available in Snowsight or via API)

-- Step 3: Review generated DDL before execution
-- Generator produces CREATE SEMANTIC VIEW statement with:
-- - Inferred PRIMARY KEY from table constraints
-- - Numeric columns as FACTS
-- - String/date columns as DIMENSIONS
-- - Common aggregations as METRICS

-- Step 4: Execute generated DDL
CREATE OR REPLACE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_CUSTOMER
  TABLES (
    customer AS SAMPLE_DATA.TPCDS_SF10TCL.CUSTOMER
      PRIMARY KEY (C_CUSTOMER_SK)
  )
  FACTS (
    customer.C_BIRTH_YEAR AS c_birth_year
  )
  DIMENSIONS (
    customer.C_CUSTOMER_SK AS c_customer_sk,
    customer.C_CUSTOMER_ID AS c_customer_id,
    customer.C_FIRST_NAME AS c_first_name,
    customer.C_LAST_NAME AS c_last_name,
    customer.C_BIRTH_COUNTRY AS c_birth_country
  )
  METRICS (
    customer.customer_count AS COUNT(DISTINCT C_CUSTOMER_SK)
  );

-- Step 5: Validate creation
SHOW SEMANTIC VIEWS IN SCHEMA SAMPLE_DATA.TPCDS_SF10TCL;
```

**Generator Limitations:**
- Cannot infer complex business logic (e.g., calculated facts)
- May misclassify columns (review FACTS vs DIMENSIONS)
- Does not add synonyms or comments automatically
- Cannot create relationships between semantic views

**Post-Generation Refinement Checklist:**
- [ ] Verify PRIMARY KEY is correct for business grain
- [ ] Review FACTS classification (should be numeric measures)
- [ ] Review DIMENSIONS classification (should be categorical/temporal)
- [ ] Add WITH SYNONYMS for natural language query matching
- [ ] Add COMMENT clauses for business definitions
- [ ] Test with sample Cortex Analyst queries

### 3.2 Iterative Development Workflow

**MANDATORY:**
**Follow this workflow for production-ready semantic views:**

**Phase 1: Generate and Validate Base Structure**

```sql
-- 1. Read base table structure BEFORE generating
DESCRIBE TABLE SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES;

-- 2. Generate or write minimal semantic view
CREATE OR REPLACE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES
  TABLES (
    sales AS SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES
      PRIMARY KEY (SS_SOLD_DATE_SK, SS_ITEM_SK, SS_CUSTOMER_SK)
  )
  FACTS (
    sales.sales_price AS SS_SALES_PRICE,
    sales.quantity AS SS_QUANTITY
  )
  DIMENSIONS (
    sales.item_sk AS SS_ITEM_SK,
    sales.customer_sk AS SS_CUSTOMER_SK,
    sales.sold_date_sk AS SS_SOLD_DATE_SK
  )
  METRICS (
    sales.total_sales AS SUM(SS_SALES_PRICE),
    sales.total_quantity AS SUM(SS_QUANTITY)
  );

-- 3. Verify structure
SHOW SEMANTIC VIEWS LIKE 'SEM_STORE_SALES' IN SCHEMA SAMPLE_DATA.TPCDS_SF10TCL;
SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES;
SHOW SEMANTIC METRICS IN SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES;

-- 4. Test basic query
SELECT * FROM SEMANTIC_VIEW (
  SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES
  METRICS total_sales, total_quantity
  DIMENSIONS SS_ITEM_SK
) LIMIT 10;
```

**Phase 2: Add Business Context**

```sql
-- 5. Add synonyms for natural language querying
CREATE OR REPLACE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES
  TABLES (
    sales AS SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES
      PRIMARY KEY (SS_SOLD_DATE_SK, SS_ITEM_SK, SS_CUSTOMER_SK)
      WITH SYNONYMS ('store sales', 'retail transactions', 'sales data')
  )
  FACTS (
    sales.sales_price AS SS_SALES_PRICE
      WITH SYNONYMS ('price', 'revenue', 'amount'),
    sales.quantity AS SS_QUANTITY
      WITH SYNONYMS ('qty', 'units sold', 'volume')
  )
  DIMENSIONS (
    sales.item_sk AS SS_ITEM_SK
      WITH SYNONYMS ('item', 'product', 'SKU'),
    sales.customer_sk AS SS_CUSTOMER_SK
      WITH SYNONYMS ('customer', 'buyer'),
    sales.sold_date_sk AS SS_SOLD_DATE_SK
      WITH SYNONYMS ('date', 'transaction date', 'sale date')
  )
  METRICS (
    sales.total_sales AS SUM(SS_SALES_PRICE)
      WITH SYNONYMS ('total revenue', 'gross sales'),
    sales.total_quantity AS SUM(SS_QUANTITY)
      WITH SYNONYMS ('total units', 'total volume')
  );

-- 6. Add comments for business definitions
CREATE OR REPLACE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES
  TABLES (
    sales AS SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES
      PRIMARY KEY (SS_SOLD_DATE_SK, SS_ITEM_SK, SS_CUSTOMER_SK)
      WITH SYNONYMS ('store sales', 'retail transactions')
      COMMENT = 'Retail store sales transactions from TPC-DS dataset'
  )
  FACTS (
    sales.sales_price AS SS_SALES_PRICE
      WITH SYNONYMS ('price', 'revenue', 'amount')
      COMMENT = 'Sales price per item (excludes tax)',
    sales.quantity AS SS_QUANTITY
      WITH SYNONYMS ('qty', 'units sold')
      COMMENT = 'Quantity of items sold'
  )
  DIMENSIONS (
    sales.item_sk AS SS_ITEM_SK
      WITH SYNONYMS ('item', 'product')
      COMMENT = 'Surrogate key for item dimension',
    sales.customer_sk AS SS_CUSTOMER_SK
      WITH SYNONYMS ('customer', 'buyer')
      COMMENT = 'Surrogate key for customer dimension',
    sales.sold_date_sk AS SS_SOLD_DATE_SK
      WITH SYNONYMS ('date', 'transaction date')
      COMMENT = 'Surrogate key for date dimension'
  )
  METRICS (
    sales.total_sales AS SUM(SS_SALES_PRICE)
      WITH SYNONYMS ('total revenue', 'gross sales')
      COMMENT = 'Sum of all sales prices',
    sales.total_quantity AS SUM(SS_QUANTITY)
      WITH SYNONYMS ('total units')
      COMMENT = 'Sum of quantities sold'
  )
  COMMENT = 'Store sales semantic view for Cortex Analyst natural language queries';
```

**Phase 3: Test with Cortex Analyst**

```python
# 7. Test natural language queries
import requests

url = f"https://{account}.snowflakecomputing.com/api/v2/cortex/analyst/message"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test queries demonstrating synonyms
test_queries = [
    "What are the top 10 items by revenue?",  # Tests 'revenue' synonym
    "Show me total units sold by customer",    # Tests 'units' synonym
    "Which products have the highest volume?", # Tests 'product' and 'volume' synonyms
]

for query in test_queries:
    payload = {
        "semantic_view": "SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES",
        "messages": [{"role": "user", "content": query}]
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Query: {query}")
    print(f"Response: {response.json()}\n")
```

**Phase 4: Performance Validation**

```sql
-- 8. Verify base table performance (semantic views are metadata only)
-- Check clustering and partitioning on base table
SHOW CLUSTERING KEYS IN TABLE SAMPLE_DATA.TPCDS_SF10TCL.STORE_SALES;

-- Test query performance with filters
SELECT * FROM SEMANTIC_VIEW (
  SAMPLE_DATA.TPCDS_SF10TCL.SEM_STORE_SALES
  METRICS total_sales
  DIMENSIONS SS_SOLD_DATE_SK
)
WHERE SS_SOLD_DATE_SK >= 2451545  -- Date filter for partition pruning
  AND SS_SOLD_DATE_SK <= 2451910
ORDER BY total_sales DESC
LIMIT 100;

-- Review Query Profile for pruning efficiency
-- (Use Snowsight Query History > Query Profile)
```

### 3.3 Common Development Patterns

**Pattern 1: Time-Based Analysis Views**

```sql
-- Optimized for temporal queries with date dimension
CREATE OR REPLACE SEMANTIC VIEW ANALYTICS.SEMANTIC.SALES_TEMPORAL
  TABLES (
    sales AS ANALYTICS.CORE.DAILY_SALES
      PRIMARY KEY (sale_date, product_id)
      WITH SYNONYMS ('sales', 'transactions')
  )
  FACTS (
    sales.revenue AS revenue,
    sales.cost AS cost,
    sales.profit AS profit  -- Pre-calculated: revenue - cost
  )
  DIMENSIONS (
    sales.sale_date AS sale_date
      WITH SYNONYMS ('date', 'transaction date', 'day')
      COMMENT = 'Date of sale transaction',
    sales.product_id AS product_id
      WITH SYNONYMS ('product', 'item', 'SKU'),
    sales.region AS region
      WITH SYNONYMS ('location', 'territory')
  )
  METRICS (
    sales.total_revenue AS SUM(revenue)
      WITH SYNONYMS ('total sales', 'gross revenue'),
    sales.total_profit AS SUM(profit)
      WITH SYNONYMS ('net profit', 'earnings'),
    sales.avg_revenue AS AVG(revenue)
      WITH SYNONYMS ('average sale', 'mean revenue')
  )
  COMMENT = 'Daily sales semantic view optimized for temporal analysis';
```

**Pattern 2: Aggregated Fact Views**

```sql
-- Pre-aggregated facts for performance
CREATE OR REPLACE SEMANTIC VIEW ANALYTICS.SEMANTIC.MONTHLY_SALES
  TABLES (
    monthly AS ANALYTICS.AGGREGATE.MONTHLY_SALES_AGG  -- Pre-aggregated base
      PRIMARY KEY (year_month, product_category)
  )
  FACTS (
    monthly.sales_amount AS sales_amount,
    monthly.units_sold AS units_sold,
    monthly.customer_count AS customer_count  -- Already aggregated
  )
  DIMENSIONS (
    monthly.year_month AS year_month
      WITH SYNONYMS ('month', 'period', 'year-month')
      COMMENT = 'Year-month in YYYY-MM format',
    monthly.product_category AS product_category
      WITH SYNONYMS ('category', 'product type')
  )
  METRICS (
    monthly.total_sales AS SUM(sales_amount),
    monthly.total_units AS SUM(units_sold),
    monthly.avg_monthly_sales AS AVG(sales_amount)
      WITH SYNONYMS ('average monthly revenue')
  )
  COMMENT = 'Monthly aggregated sales for trend analysis';
```

**Pattern 3: Multi-Dimensional Views**

```sql
-- Complex dimensional analysis
CREATE OR REPLACE SEMANTIC VIEW ANALYTICS.SEMANTIC.SALES_CUBE
  TABLES (
    sales AS ANALYTICS.CORE.SALES_FACT
      PRIMARY KEY (sale_id)
  )
  FACTS (
    sales.amount AS amount,
    sales.quantity AS quantity,
    sales.discount AS discount
  )
  DIMENSIONS (
    sales.product_id AS product_id
      WITH SYNONYMS ('product', 'item'),
    sales.customer_id AS customer_id
      WITH SYNONYMS ('customer', 'buyer'),
    sales.store_id AS store_id
      WITH SYNONYMS ('store', 'location'),
    sales.sale_date AS sale_date
      WITH SYNONYMS ('date', 'transaction date'),
    sales.channel AS channel
      WITH SYNONYMS ('sales channel', 'channel type')
      COMMENT = 'Online, In-Store, Mobile'
  )
  METRICS (
    sales.revenue AS SUM(amount),
    sales.total_quantity AS SUM(quantity),
    sales.avg_discount AS AVG(discount)
      WITH SYNONYMS ('average discount rate'),
    sales.transaction_count AS COUNT(*)
      WITH SYNONYMS ('number of sales', 'sale count')
  )
  COMMENT = 'Multi-dimensional sales cube for slice-and-dice analysis';
```

### 3.4 Development Checklist for AI Agents

**MANDATORY:**
**Before creating semantic view, verify:**
- [ ] Read base table structure with DESCRIBE TABLE
- [ ] Understand business grain and primary key
- [ ] Identify numeric columns for FACTS
- [ ] Identify categorical/temporal columns for DIMENSIONS
- [ ] Document intended metrics and aggregations

**During semantic view creation:**
- [ ] Use correct mapping syntax: `logical_name AS physical_column`
- [ ] Follow clause order: TABLES, then FACTS, then DIMENSIONS, then METRICS
- [ ] Add WITH SYNONYMS for all business-critical fields
- [ ] Include COMMENT clauses with business definitions
- [ ] Use equals sign in COMMENT syntax: `COMMENT = 'text'`

**After semantic view creation:**
- [ ] Verify with SHOW SEMANTIC VIEWS
- [ ] Test basic query with SEMANTIC_VIEW()
- [ ] Validate metric calculations against base table
- [ ] Test Cortex Analyst natural language queries
- [ ] Review Query Profile for performance
- [ ] Document view purpose and usage examples

## 4) Cortex Analyst Troubleshooting

Common errors when using semantic views with Cortex Analyst and their solutions.

### Error: "View not accessible" or "SELECT command denied"

**Cause:** Agent role lacks SELECT permission on semantic view

**Solutions:**
```sql
-- 1. Verify view exists
SHOW SEMANTIC VIEWS LIKE '{VIEW_NAME}' IN SCHEMA {DATABASE}.{SCHEMA};

-- 2. Grant SELECT to agent role
GRANT SELECT ON SEMANTIC VIEW {DATABASE}.{SCHEMA}.{VIEW_NAME} TO ROLE agent_runner;

-- 3. Verify grant applied
SHOW GRANTS TO ROLE agent_runner;

-- 4. Test access with agent role
USE ROLE agent_runner;
SELECT * FROM SEMANTIC_VIEW({DATABASE}.{SCHEMA}.{VIEW_NAME} DIMENSIONS dim1) LIMIT 1;
```

### Error: "No data returned from Analyst" or "Empty results"

**Cause:** Semantic view empty, query doesn't match available data, or grain mismatch

**Solutions:**
```sql
-- 1. Verify view has data
SELECT COUNT(*) AS row_count
FROM SEMANTIC_VIEW({DATABASE}.{SCHEMA}.{SEMANTIC_VIEW} DIMENSIONS dim1);

-- 2. Check view structure
SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW {DATABASE}.{SCHEMA}.{VIEW_NAME};
SHOW SEMANTIC METRICS IN SEMANTIC VIEW {DATABASE}.{SCHEMA}.{VIEW_NAME};

-- 3. Test with simple query first
SELECT * FROM SEMANTIC_VIEW({DATABASE}.{SCHEMA}.{VIEW_NAME} DIMENSIONS dim1 METRICS metric1) LIMIT 10;

-- 4. Verify measures and dimensions are populated
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT dimension_column) AS unique_dimensions
FROM SEMANTIC_VIEW({DATABASE}.{SCHEMA}.{VIEW_NAME} DIMENSIONS dimension_column);
```

### Error: "Invalid semantic view structure"

**Cause:** View missing required columns, comments, or proper grain definition

**Solutions:**
```sql
-- INCORRECT - Using SELECT *
CREATE VIEW semantic_sales AS
SELECT * FROM raw_sales;

-- CORRECT - Explicit columns with comments (use CREATE SEMANTIC VIEW)
CREATE OR REPLACE SEMANTIC VIEW {DATABASE}.{SCHEMA}.semantic_sales
  TABLES (
    sales AS {DATABASE}.{SCHEMA}.sales
      PRIMARY KEY (sale_id)
  )
  FACTS (
    sales.amount AS amount
      COMMENT = 'Sales amount for aggregation'
  )
  DIMENSIONS (
    sales.sale_id AS sale_id
      COMMENT = 'Surrogate key',
    sales.customer_id AS customer_id
      COMMENT = 'Foreign key to customers',
    sales.sale_date AS sale_date
      COMMENT = 'Transaction date'
  )
  METRICS (
    sales.total_revenue AS SUM(amount)
      COMMENT = 'Total sales revenue'
  );

-- Verify structure
SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW {DATABASE}.{SCHEMA}.semantic_sales;
SHOW SEMANTIC METRICS IN SEMANTIC VIEW {DATABASE}.{SCHEMA}.semantic_sales;
```

### Error: "Tool configuration failed" or "Analyst tool not working"

**Cause:** Semantic view name incorrect, tool description missing, or insufficient permissions

**Solutions:**
```sql
-- 1. Verify semantic view name is fully qualified
-- INCORRECT
Tool: portfolio_view  -- Missing database and schema

-- CORRECT
Tool: ANALYTICS.SEMANTIC.PORTFOLIO_VIEW  -- Fully qualified

-- 2. Test semantic view directly
SELECT * FROM SEMANTIC_VIEW(ANALYTICS.SEMANTIC.PORTFOLIO_VIEW DIMENSIONS dim1) LIMIT 5;

-- 3. Verify role has all required permissions
SHOW GRANTS TO ROLE agent_runner;

-- Required grants:
-- - USAGE on database
-- - USAGE on schema
-- - SELECT on semantic view
-- - USAGE on warehouse
```

### Error: "Permission denied on CORTEX.ANALYST function"

**Cause:** Missing USAGE grant on Cortex functions

**Solutions:**
```sql
-- Grant Cortex function access (if required by your account setup)
-- Note: Cortex functions are typically available by default

-- Verify current role
SELECT CURRENT_ROLE(), CURRENT_USER();

-- Test Cortex function access
SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', 'Test query');
```
