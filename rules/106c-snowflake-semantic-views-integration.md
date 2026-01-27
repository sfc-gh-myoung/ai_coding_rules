# Snowflake Semantic Views: Integration and Governance

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-01-27
**LoadTrigger:** kw:semantic-integration
**Keywords:** RBAC, masking policy, row access policy, cortex analyst, agent integration, semantic view security, analyst troubleshooting, fix analyst, debug analyst, synonyms, natural language queries
**TokenBudget:** ~2800
**ContextTier:** Medium
**Depends:** 106-snowflake-semantic-views-core.md, 106b-snowflake-semantic-views-querying.md

## Scope

**What This Rule Covers:**
Integrating Snowflake Semantic Views with Cortex Analyst and Cortex Agent, applying governance and security controls, and troubleshooting integration issues.

**When to Load This Rule:**
- Integrating semantic views with Cortex Analyst
- Using semantic views with Cortex Agent
- Applying security policies to semantic views
- Troubleshooting Cortex Analyst integration

**For development workflows and VQR, see `106d-snowflake-semantic-views-development.md`.**

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule
- **106-snowflake-semantic-views-core.md** - DDL fundamentals
- **106b-snowflake-semantic-views-querying.md** - Query patterns

### External Documentation
- [Cortex Analyst Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- [Cortex Agent Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- [Masking Policies](https://docs.snowflake.com/en/user-guide/security-column-ddm)
- [Row Access Policies](https://docs.snowflake.com/en/user-guide/security-row)

### Related Rules
- **106d-snowflake-semantic-views-development.md** - VQR, Generator workflow
- **115-snowflake-cortex-agents-core.md** - Agent design and configuration
- **107-snowflake-security-governance.md** - Security policies

## Contract

### Inputs and Prerequisites

- Semantic view exists (created via `CREATE SEMANTIC VIEW`)
- Cortex Analyst/Agent access enabled
- Governance policies defined (masking, row access)

### Mandatory

- Cortex Analyst REST API with `semantic_view` parameter
- Cortex Agent Python SDK (`snowflake.core.cortex.Agent`)
- Standard Snowflake governance via base tables

### Forbidden

- Direct policy application to semantic views (apply to base tables)
- Hardcoded credentials in scripts

### Execution Steps

1. Create semantic view with synonyms and comments
2. Test with Cortex Analyst REST API or SnowCLI
3. Apply governance policies to base tables
4. Validate natural language query accuracy
5. Configure Cortex Agent grounding (if applicable)

### Output Format

- REST API payloads with `semantic_view` parameter
- Cortex Agent Python code with grounding sources
- SQL governance policy definitions

### Validation

- Cortex Analyst returns valid responses
- Natural language queries match business logic
- Governance policies enforce correctly

### Design Principles

- **Dual approach support**: `semantic_view` for DDL-based; `semantic_model_file` for YAML with VQR
- **Governance via base tables**: Apply policies to underlying tables
- **Security inheritance**: Semantic views inherit RBAC from base tables

### Post-Execution Checklist

- [ ] Cortex Analyst tested with `semantic_view` parameter
- [ ] Natural language queries return expected results
- [ ] Governance policies applied to base tables
- [ ] Synonyms added for key business terms

## Approach Selection: SQL DDL vs YAML

**Use CREATE SEMANTIC VIEW (SQL DDL) when:**
- Simple to moderate complexity views
- No verified queries (VQRs) required
- SQL-based version control preferred

**Use YAML Semantic Model Files when:**
- **Verified queries (VQRs) required** (YAML-only feature)
- Complex custom instructions needed
- Integration with YAML-based CI/CD

**CRITICAL:** VQRs are ONLY available in YAML format. See `106d-snowflake-semantic-views-development.md` for VQR patterns.

## Cortex Analyst Integration

### REST API Usage

```python
import requests

url = f"https://{account}.snowflakecomputing.com/api/v2/cortex/analyst/message"

headers = {
    "Authorization": f"Bearer {snowflake_token}",
    "Content-Type": "application/json"
}

# Native semantic view (no YAML needed)
payload = {
    "semantic_view": "PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH",
    "messages": [
        {"role": "user", "content": "Which transformers have the highest load?"}
    ]
}

response = requests.post(url, headers=headers, json=payload)
print(response.json()["message"]["content"])
```

**Key Differences:**
- **Native views:** `"semantic_view": "DB.SCHEMA.VIEW_NAME"`
- **YAML (with VQR):** `"semantic_model_file": "@DB.SCHEMA.STAGE/model.yaml"`

### Cortex Agent Integration

```python
from snowflake.core import Root
from snowflake.core.cortex import Agent

root = Root(session)

agent = root.databases["PROD"].schemas["GRID_DATA"].cortex_agents.create(
    Agent(
        name="grid_ops_assistant",
        grounding_sources=[
            "PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH",
            "PROD.GRID_DATA.SEM_ASSET_INVENTORY"
        ],
        instructions="Answer questions about transformer health and assets.",
        model="mistral-large2"
    )
)

response = agent.invoke("Show me transformers at risk of failure")
```

### SnowCLI Testing

```bash
snow cortex analyst query \
  --semantic-view "PROD.GRID_DATA.SEM_TRANSFORMER_HEALTH" \
  --question "What is the average load for transformers?"

# Test synonym effectiveness
snow cortex analyst query \
  --semantic-view "SAMPLE_DATA.TPCDS_SF10TCL.TPCDS_SEMANTIC_VIEW_SM" \
  --question "Show me revenue by product category"
```

### Synonym Design for NLQ

```sql
CREATE OR REPLACE SEMANTIC VIEW SAMPLE_DATA.TPCDS_SF10TCL.SEM_CUSTOMER
  TABLES (
    customer AS SAMPLE_DATA.TPCDS_SF10TCL.CUSTOMER
      PRIMARY KEY (C_CUSTOMER_SK)
      WITH SYNONYMS ('customers', 'buyers', 'clients')
  )
  DIMENSIONS (
    customer.C_BIRTH_COUNTRY AS c_birth_country
      WITH SYNONYMS ('country', 'birth country', 'nationality')
      COMMENT = 'Country where customer was born'
  )
  METRICS (
    customer.customer_count AS COUNT(DISTINCT C_CUSTOMER_SK)
      WITH SYNONYMS ('total customers', 'number of customers', 'how many customers')
  );
```

**Synonym Best Practices:**
- Include common business terms users actually say
- Add plural and singular forms
- Include abbreviations and acronyms
- Test with actual user questions

## Governance and Security

### Access Control (RBAC)

Semantic views inherit RBAC from base tables:

```sql
-- Grant SELECT on base table (semantic view inherits)
GRANT SELECT ON TABLE PROD.GRID_DATA.GRID_ASSETS TO ROLE BI_ANALYST;
GRANT USAGE ON SCHEMA PROD.GRID_DATA TO ROLE BI_ANALYST;

-- Role hierarchy pattern
CREATE ROLE IF NOT EXISTS DATA_ANALYST;
GRANT USAGE ON SCHEMA PROD.ANALYTICS TO ROLE DATA_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA PROD.RAW_DATA TO ROLE DATA_ANALYST;
```

### Data Masking

Apply masking to base tables (semantic views reflect masked data):

```sql
CREATE OR REPLACE MASKING POLICY PROD.GOVERNANCE.MASK_PII 
  AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val
    ELSE '***MASKED***'
  END;

-- Apply to base table
ALTER TABLE PROD.CUSTOMER_DATA.CUSTOMERS
  MODIFY COLUMN customer_email SET MASKING POLICY PROD.GOVERNANCE.MASK_PII;

-- Masking applies automatically through semantic view
```

### Row Access Policies

Apply row-level security to base tables:

```sql
CREATE OR REPLACE ROW ACCESS POLICY PROD.GOVERNANCE.RESTRICT_REGION 
  AS (region STRING) RETURNS BOOLEAN ->
  CASE
    WHEN CURRENT_ROLE() = 'ADMIN' THEN TRUE
    WHEN CURRENT_ROLE() = 'ANALYST_WEST' AND region = 'WEST' THEN TRUE
    ELSE FALSE
  END;

ALTER TABLE PROD.GRID_DATA.GRID_ASSETS
  ADD ROW ACCESS POLICY PROD.GOVERNANCE.RESTRICT_REGION ON (region);
```

### Governance Checklist

- [ ] RBAC configured via base table privileges
- [ ] Masking policies applied to base tables
- [ ] Row access policies applied to base tables
- [ ] Schema privileges granted (USAGE on schema)
- [ ] Audit logging enabled
- [ ] **No direct policies on semantic views**

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Applying Policies to Semantic Views Directly

**Problem:** Attempting to add governance policies (masking, row access) directly to semantic views.

**Why It Fails:** Semantic views don't support direct policy attachment. Policies applied to semantic views are silently ignored, creating false security assumptions.

**Correct Pattern:**
```sql
-- WRONG: Policy on semantic view (silently ignored)
ALTER SEMANTIC VIEW SEM_SALES
  ADD ROW ACCESS POLICY rap_region ON (region);

-- CORRECT: Policy on base table (inherited by semantic view)
ALTER TABLE SALES_FACT
  ADD ROW ACCESS POLICY rap_region ON (region);
```

### Anti-Pattern 2: Skipping Synonyms for Business Terms

**Problem:** Creating semantic views without synonyms, expecting Cortex Analyst to understand business terminology.

**Why It Fails:** Cortex Analyst cannot infer that "revenue" means `amount` or "Q1" refers to `fiscal_quarter`. Natural language queries fail to match columns without explicit synonyms.

**Correct Pattern:**
```sql
-- WRONG: No synonyms (NLQ fails on business terms)
CREATE SEMANTIC VIEW SEM_SALES
  FACTS (sales.amount AS amount);

-- CORRECT: Comprehensive synonyms for NLQ matching
CREATE SEMANTIC VIEW SEM_SALES
  FACTS (
    sales.amount AS amount
      WITH SYNONYMS ('revenue', 'sales', 'income', 'total')
      COMMENT = 'Transaction amount in USD'
  );
```

## Troubleshooting

### Error: "View not accessible" or "SELECT denied"

```sql
-- 1. Verify view exists
SHOW SEMANTIC VIEWS LIKE '{VIEW_NAME}' IN SCHEMA {DATABASE}.{SCHEMA};

-- 2. Grant SELECT
GRANT SELECT ON SEMANTIC VIEW {DATABASE}.{SCHEMA}.{VIEW_NAME} TO ROLE agent_runner;

-- 3. Test access
USE ROLE agent_runner;
SELECT * FROM SEMANTIC_VIEW({DATABASE}.{SCHEMA}.{VIEW_NAME} DIMENSIONS dim1) LIMIT 1;
```

### Error: "No data returned" or "Empty results"

```sql
-- 1. Verify view has data
SELECT COUNT(*) FROM SEMANTIC_VIEW({DATABASE}.{SCHEMA}.{VIEW} DIMENSIONS dim1);

-- 2. Check structure
SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW {DATABASE}.{SCHEMA}.{VIEW};
SHOW SEMANTIC METRICS IN SEMANTIC VIEW {DATABASE}.{SCHEMA}.{VIEW};
```

### Error: "Invalid semantic view structure"

```sql
-- WRONG: Using SELECT *
CREATE VIEW semantic_sales AS SELECT * FROM raw_sales;

-- CORRECT: Use CREATE SEMANTIC VIEW with explicit structure
CREATE OR REPLACE SEMANTIC VIEW {DATABASE}.{SCHEMA}.semantic_sales
  TABLES (sales AS {DATABASE}.{SCHEMA}.sales PRIMARY KEY (sale_id))
  FACTS (sales.amount AS amount COMMENT = 'Sales amount')
  DIMENSIONS (sales.sale_date AS sale_date COMMENT = 'Transaction date')
  METRICS (sales.total_revenue AS SUM(amount) COMMENT = 'Total revenue');
```

### Error: "Tool configuration failed"

```sql
-- 1. Verify semantic view name is fully qualified
-- WRONG: portfolio_view
-- CORRECT: ANALYTICS.SEMANTIC.PORTFOLIO_VIEW

-- 2. Test semantic view directly
SELECT * FROM SEMANTIC_VIEW(ANALYTICS.SEMANTIC.PORTFOLIO_VIEW DIMENSIONS dim1) LIMIT 5;

-- 3. Verify role permissions
SHOW GRANTS TO ROLE agent_runner;
```

## Output Format Examples

```python
# Complete Cortex Analyst integration pattern
import requests
import snowflake.connector

# Step 1: Verify semantic view
conn = snowflake.connector.connect(...)
cursor = conn.cursor()
cursor.execute("SHOW SEMANTIC VIEWS LIKE 'SEM_SALES'")
print(cursor.fetchall())

# Step 2: Test direct query
cursor.execute("""
  SELECT dimension_1, metric_1
  FROM SEMANTIC_VIEW(PROD.ANALYTICS.SEM_SALES)
  LIMIT 10
""")

# Step 3: Call Cortex Analyst
url = f"https://{account}.snowflakecomputing.com/api/v2/cortex/analyst/message"
payload = {
    "messages": [{"role": "user", "content": "Top 5 products by revenue?"}],
    "semantic_view": f"{database}.{schema}.{view_name}"
}
response = requests.post(url, headers=headers, json=payload)

# Step 4: Verify governance
cursor.execute("SELECT CURRENT_ROLE(), CURRENT_USER()")
```
