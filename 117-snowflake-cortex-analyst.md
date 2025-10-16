**Description:** Best practices for Snowflake Cortex Analyst and Semantic Views, including modeling guidance, governance, agent integration, usage patterns, prerequisites validation, and error troubleshooting.
**AppliesTo:** `**/*.sql`, `**/*.py`
**AutoAttach:** false
**Type:** Agent Requested
**Keywords:** Cortex Analyst, natural language queries, NL2SQL, semantic layer, text-to-SQL, business intelligence, agent tool configuration, analyst tools, semantic view design, prerequisites validation, working SQL examples, error troubleshooting, permission configuration
**Version:** 1.3
**LastUpdated:** 2025-10-16

**TokenBudget:** ~500
**ContextTier:** Medium

# Snowflake Cortex Analyst & Semantic Views Best Practices

## Purpose
Define reliable patterns for designing and operating Semantic Views and Cortex Analyst experiences: semantic modeling, object governance, prompt templates, agent tool configuration, and integration with retrieval/agents.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Semantic Views modeling; Cortex Analyst configuration and usage; agent tool integration; integration with AISQL/Agents/Search; governance

## Contract
- **Inputs/Prereqs:**
  - Curated semantic layer with stable dimensions/measures; naming conventions established
  - Access roles and data masking policies aligned to business domains
  - Reference documentation for business definitions
- **Allowed Tools:** Semantic Views, Cortex Analyst, AISQL for enrichment, Cortex Search for retrieval, Cortex Agents
- **Forbidden Tools:**
  - Ad-hoc views masquerading as semantic views without definitions and comments
  - Ambiguous measures without aggregation rules or grain
  - Flagging/threshold logic in semantic views (belongs in agent instructions)
- **Required Steps:**
  1. Define business entities, measures, and conformed dimensions with clear grain and join keys
  2. Implement Semantic Views with comments on columns/measures; avoid `SELECT *`
  3. Use consistent naming conventions and fully qualified object names
  4. Apply masking/row access policies; tag sensitive fields
  5. Keep semantic views pure for calculations (NO flagging/threshold logic)
  6. Configure Cortex Analyst tools with clear descriptions and when-to-use guidance
  7. Document prompt templates and usage guidelines for Cortex Analyst
- **Output Format:** Semantic view definitions, agent tool configurations, usage patterns
- **Validation Steps:** Views compile; definitions align to business glossary; access rules enforced; analyst prompts produce consistent answers; tool descriptions are clear

## Key Principles
- Explicit measures and dimensions with clear grain and aggregation
- Consistent naming and comments; avoid nested view chains
- 🔥 **CRITICAL:** Semantic views calculate data accurately; flagging logic belongs in agent instructions
- Governed access with masking and row-level security
- Reuse semantic views across agents, AISQL, and Analyst to ensure consistency
- Clear tool descriptions with when-to-use guidance for agent integration

## 0. Prerequisites Validation

Before implementing Cortex Analyst and Semantic Views, verify your environment meets requirements:

### 0.1 Prerequisites Checklist

- [ ] Snowflake account has Cortex Analyst capability enabled
- [ ] Base tables/views for semantic layer exist and are populated
- [ ] Required permissions granted (CREATE VIEW, SELECT on source tables)
- [ ] Understanding of business metrics and grain for semantic modeling
- [ ] Warehouse available for query execution

### 0.2 Verification Commands

**Check Cortex Analyst Availability:**
```sql
-- Verify Cortex features available
SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;

-- Check if Analyst function is accessible
SELECT SNOWFLAKE.CORTEX.ANALYST(
    'What is Cortex Analyst?'
) AS test_response;
```

**Verify Base Tables:**
```sql
-- Check source tables exist and have data
SELECT 
    TABLE_CATALOG,
    TABLE_SCHEMA,
    TABLE_NAME,
    ROW_COUNT
FROM {DATABASE}.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = '{SCHEMA}'
  AND TABLE_TYPE = 'BASE TABLE';

-- Example:
SELECT 
    TABLE_CATALOG,
    TABLE_SCHEMA,
    TABLE_NAME,
    ROW_COUNT
FROM ANALYTICS.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'CORE'
  AND TABLE_TYPE = 'BASE TABLE';
```

**Verify Semantic View Creation Permissions:**
```sql
-- Check you can create views in target schema
SHOW GRANTS ON SCHEMA {DATABASE}.{SCHEMA};

-- Required grants:
-- - CREATE VIEW on schema
-- - SELECT on source tables
-- - USAGE on database and schema
```

**Test Semantic View Query:**
```sql
-- Verify existing semantic view is accessible
SELECT * FROM {DATABASE}.{SCHEMA}.{SEMANTIC_VIEW} LIMIT 5;

-- Example:
SELECT * FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW LIMIT 5;

-- Verify view structure includes measures and dimensions
DESC VIEW ANALYTICS.SEMANTIC.PORTFOLIO_VIEW;
```

### 0.3 Pre-Implementation Validation

Run this comprehensive check before creating semantic views:

```sql
-- 1. Check Cortex availability
SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;

-- 2. Verify base table data quality
SELECT 
    'Data Quality Check' AS validation_step,
    COUNT(*) AS total_rows,
    COUNT(DISTINCT primary_key_column) AS unique_keys,
    SUM(CASE WHEN critical_column IS NULL THEN 1 ELSE 0 END) AS null_count
FROM {DATABASE}.{SCHEMA}.{SOURCE_TABLE};

-- 3. Check schema permissions
SELECT 'Permission Check' AS validation_step,
       COUNT(*) AS grant_count
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));

-- 4. Test warehouse
SELECT 'Warehouse Check' AS validation_step,
       CURRENT_WAREHOUSE() AS warehouse_name;
```

**All checks should return valid results.** If any fail, address prerequisites before proceeding.

## 1. Semantic View Authoring
```sql
-- Example: explicit columns and comments; avoid SELECT *
CREATE OR REPLACE VIEW ANALYTICS.SEMANTIC.customer_orders
COMMENT = 'Customer order facts with conformed customer dimension keys'
AS
SELECT 
  o.order_id COMMENT 'Surrogate key of order',
  o.customer_id,
  c.customer_name,
  o.order_date,
  o.total_amount,
  -- Explicit measure with aggregation rule documented
  o.total_amount AS measure_total_amount
FROM ANALYTICS.CORE.orders o
JOIN ANALYTICS.DIM.customers c ON c.customer_id = o.customer_id;
```

## 2. Governance
- Apply masking policies to PII columns; use row access policies for data domain restrictions
- Tag semantic objects with ownership and data classification
- Keep governance separate from business rule flagging (flagging belongs in agents)

## 3. Prompt Templates for Analyst
```text
Answer using the semantic definitions in ANALYTICS.SEMANTIC.*. Prefer measures ending with measure_*.
Include time grain in results when summarizing over time.
```

## 4. Integration Patterns
- Use Semantic Views as the authoritative layer for Cortex Agents and AISQL to ensure consistent definitions
- For retrieval, index explanations and column comments to improve grounding quality
- Semantic views should be domain-focused and reusable across multiple agents

## 5. Cortex Analyst as Agent Tool

### 5.1 Tool Configuration Pattern

When using Cortex Analyst as a tool within Cortex Agents, configure with explicit when-to-use guidance:

```yaml
Tool Name: {analyst_tool_name}              # e.g., portfolio_analyzer, risk_analyzer
Type: Cortex Analyst
Semantic View: {DATABASE}.{SCHEMA}.{VIEW}   # Fully qualified semantic view name
Description: "Use this tool for {specific_analysis_type}. It can {capabilities_list}. Use for questions about {when_to_use_guidance}."

# Example: Portfolio Analytics Tool
Tool Name: portfolio_analyzer
Type: Cortex Analyst
Semantic View: ANALYTICS.SEMANTIC.PORTFOLIO_VIEW
Description: "Use this tool for quantitative portfolio analysis including holdings, exposures, sector breakdowns, and performance metrics. It can calculate weights, generate securities lists, perform aggregations, and create charts. Use for questions about numbers, percentages, rankings, comparisons, and visualizations."
```

### 5.2 Single-Tool vs Multi-Tool Agents

**Single Cortex Analyst Agent:**
- Use when queries focus on one analytical domain (e.g., portfolio analysis only)
- Simple tool selection logic (always use the one analyst tool)
- Deep analytical capabilities within domain
- Examples: Portfolio analyzer, risk monitor, performance tracker

**Multiple Cortex Analyst Agents:**
- Use when queries span multiple analytical domains (portfolio + risk + performance)
- Requires explicit planning instructions for domain-based tool selection
- Each tool has distinct semantic view modeling different domain
- Examples: Comprehensive investment analyst, multi-domain portfolio manager

**Hybrid Agents (Analyst + Search):**
- Use when queries mix quantitative analysis with document research
- Requires query classification (quantitative vs qualitative)
- Cortex Analyst for numbers/calculations, Cortex Search for opinions/context
- Examples: Portfolio copilot, investment advisor

### 5.3 Tool Description Best Practices

**Clear When-to-Use Guidance:**
```yaml
# ✅ GOOD - Explicit capabilities and use cases
Description: "Use for portfolio holdings, weight calculations, sector breakdowns, and concentration analysis. Use for questions about 'how much', 'what percentage', 'top N holdings', and when visualizations are needed."

# ❌ BAD - Too vague
Description: "Analyzes portfolio data"
```

**Avoiding Overlapping Tools:**
```yaml
# ✅ GOOD - Distinct domains
Tool A: "Portfolio holdings, weights, and exposure analysis"
Tool B: "Risk metrics, volatility, and correlation analysis"

# ❌ BAD - Overlapping use cases
Tool A: "Portfolio analysis"
Tool B: "Investment analysis"  # Too similar to Tool A
```

### 5.4 Testing Cortex Analyst Tools

**Component Testing Pattern:**
```python
def test_analyst_tool(session: Session, semantic_view: str):
    """Test Cortex Analyst tool independently"""
    
    # Simple query to verify tool responds
    result = session.sql(f"""
        SELECT * FROM TABLE(
            {semantic_view}(
                METRICS total_value,
                DIMENSIONS category
            )
        ) LIMIT 5
    """).collect()
    
    assert len(result) > 0, f"Analyst tool {semantic_view} returned no results"
    print(f"✅ Analyst tool test passed: {semantic_view}")
    return True
```

**Integration Testing:**
After component tests pass, test agent's tool selection logic:
- Quantitative queries should route to appropriate Cortex Analyst tool
- Verify correct tool selected when multiple analyst tools available
- Confirm charts/visualizations generate appropriately

**Test Query Examples:**
```python
# Test Cortex Analyst tool selection
"What are the top 10 holdings by weight?"          # Should use analyst tool
"Calculate sector allocation breakdown"             # Should use analyst tool
"Show me a chart of performance over time"          # Should use analyst tool + viz
```

### 5.5 Cross-Reference to Agent Archetypes

For comprehensive agent configuration patterns including Cortex Analyst tools, see:
- **Single-Domain Analytics Agents:** `115-snowflake-cortex-agents.md` Section 1.2
- **Multi-Domain Analytics Agents:** `115-snowflake-cortex-agents.md` Section 1.1
- **Hybrid Agents:** `115-snowflake-cortex-agents.md` Section 1.4
- **Planning Instructions:** `115-snowflake-cortex-agents.md` Section 4
- **Testing Patterns:** `115-snowflake-cortex-agents.md` Section 6

## 7. Common Errors and Solutions

### Error: "View not accessible" or "SELECT command denied"

**Cause:** Agent role lacks SELECT permission on semantic view

**Solutions:**
```sql
-- 1. Verify view exists
SHOW VIEWS LIKE '{VIEW_NAME}' IN SCHEMA {DATABASE}.{SCHEMA};

-- Example:
SHOW VIEWS LIKE 'PORTFOLIO_VIEW' IN SCHEMA ANALYTICS.SEMANTIC;

-- 2. Grant SELECT to agent role
GRANT SELECT ON VIEW {DATABASE}.{SCHEMA}.{VIEW_NAME} TO ROLE agent_runner;

-- Example:
GRANT SELECT ON VIEW ANALYTICS.SEMANTIC.PORTFOLIO_VIEW TO ROLE agent_runner;

-- 3. Verify grant applied
SHOW GRANTS TO ROLE agent_runner;

-- 4. Test access with agent role
USE ROLE agent_runner;
SELECT * FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW LIMIT 1;
```

### Error: "No data returned from Analyst" or "Empty results"

**Cause:** Semantic view empty, query doesn't match available data, or grain mismatch

**Solutions:**
```sql
-- 1. Verify view has data
SELECT COUNT(*) AS row_count
FROM {DATABASE}.{SCHEMA}.{SEMANTIC_VIEW};

-- Example:
SELECT COUNT(*) AS row_count
FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW;

-- 2. Check view structure
DESC VIEW ANALYTICS.SEMANTIC.PORTFOLIO_VIEW;

-- 3. Test with simple query first
SELECT * FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW LIMIT 10;

-- 4. Verify measures and dimensions are populated
SELECT 
    COUNT(*) AS total_rows,
    COUNT(DISTINCT dimension_column) AS unique_dimensions,
    SUM(measure_column) AS total_measure
FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW;
```

### Error: "Invalid semantic view structure"

**Cause:** View missing required columns, comments, or proper grain definition

**Solutions:**
```sql
-- ❌ INCORRECT - Using SELECT *
CREATE VIEW semantic_sales AS
SELECT * FROM raw_sales;

-- ✅ CORRECT - Explicit columns with comments
CREATE OR REPLACE VIEW ANALYTICS.SEMANTIC.semantic_sales
COMMENT = 'Sales facts with customer dimension'
AS
SELECT
  sale_id COMMENT 'Surrogate key',
  customer_id COMMENT 'Foreign key to customers',
  sale_date COMMENT 'Transaction date',
  amount AS measure_amount COMMENT 'Sales amount for aggregation'
FROM ANALYTICS.CORE.sales
WHERE sale_date IS NOT NULL
  AND amount > 0;

-- Verify structure
DESC VIEW ANALYTICS.SEMANTIC.semantic_sales;
```

### Error: "Tool configuration failed" or "Analyst tool not working"

**Cause:** Semantic view name incorrect, tool description missing, or insufficient permissions

**Solutions:**
```sql
-- 1. Verify semantic view name is fully qualified
-- ❌ INCORRECT
Tool: portfolio_view  -- Missing database and schema

-- ✅ CORRECT
Tool: ANALYTICS.SEMANTIC.PORTFOLIO_VIEW  -- Fully qualified

-- 2. Test semantic view directly
SELECT * FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW LIMIT 5;

-- 3. Verify role has all required permissions
SHOW GRANTS TO ROLE agent_runner;

-- Required grants:
-- - USAGE on database
-- - USAGE on schema
-- - SELECT on semantic view
-- - USAGE on warehouse
-- - USAGE on Cortex functions
```

### Error: "Flagging logic not applied" when using semantic view

**Cause:** Flagging logic placed in semantic view instead of agent instructions

**Solution:**
- **Review:** Section 5.1 in this rule - flagging belongs in agent instructions
- **NEVER:** Add threshold/flagging logic to semantic view or its comments
- **Correct Approach:**
  1. Semantic View: Calculate metrics accurately (e.g., `position_weight`)
  2. Agent Response Instructions: "When `position_weight` > 6.5%, flag with WARNING"
  3. Reuse semantic view across multiple agents with different thresholds

### Error: "Permission denied on CORTEX.ANALYST function"

**Cause:** Missing USAGE grant on Cortex Analyst function

**Solutions:**
```sql
-- Grant Cortex Analyst function access
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.ANALYST TO ROLE agent_runner;

-- Verify grant
SHOW GRANTS TO ROLE agent_runner;

-- Test function access
USE ROLE agent_runner;
SELECT SNOWFLAKE.CORTEX.ANALYST('Test query');
```

## Anti-Patterns and Common Mistakes

❌ **Anti-Pattern 1: Flagging Logic in Semantic Views**
```sql
-- In semantic view or custom instructions:
"Flag positions exceeding 6.5% as concentration risks"
"Highlight when threshold exceeded"
```
**Problem:** Semantic views should be reusable across agents with different thresholds. Business rules and flagging belong in agent response instructions, not in data models.

✅ **Correct Pattern:**
```yaml
# In Agent Response Instructions:
"When position weights exceed 6.5%, flag with '⚠️  CONCENTRATION WARNING: {security} at {exact %}'"

# In Semantic View:
Just calculate position_weight accurately (no flagging, no thresholds, no highlighting)
```
**Benefits:** Semantic view remains reusable; different agents can apply different thresholds; business rules centralized in agent config.

❌ **Anti-Pattern 2: Vague Tool Descriptions**
```yaml
Tool Description: "Analyzes data"
```
**Problem:** Agent doesn't know WHEN to use this tool vs others.

✅ **Correct Pattern:**
```yaml
Tool Description: "Use for portfolio holdings, weight calculations, and sector allocations. Use when questions ask about 'how much', 'what percentage', 'top N', or request visualizations."
```

❌ **Anti-Pattern 3: SELECT * in Semantic Views**
```sql
CREATE VIEW semantic_sales AS
SELECT * FROM raw_sales;  -- BAD!
```
**Problem:** Unclear what columns represent; no documentation; includes unnecessary columns.

✅ **Correct Pattern:**
```sql
CREATE VIEW semantic_sales
COMMENT = 'Sales facts with customer dimension'
AS
SELECT
  sale_id COMMENT 'Surrogate key',
  customer_id,
  sale_date,
  amount AS measure_amount COMMENT 'Sales amount for aggregation'
FROM raw_sales;
```

## Quick Compliance Checklist
- [ ] Semantic Views define explicit measures/dimensions and grain
- [ ] No `SELECT *`; comments present for non-obvious fields
- [ ] NO flagging/threshold logic in semantic views (belongs in agent instructions)
- [ ] Masking and row access policies applied where needed
- [ ] Naming conventions and fully qualified names used
- [ ] Tool descriptions include clear when-to-use guidance
- [ ] Tool use cases are distinct (no overlaps with other tools)
- [ ] Prompt templates documented for Cortex Analyst
- [ ] Component testing completed for analyst tools

## Validation
- **Success checks:** Analyst answers align with business definitions; joins respect grain; access rules enforced; flagging logic in agent layer only; tool descriptions are clear; component tests pass
- **Negative tests:** Ambiguous measures cause rejected PRs; missing comments or SELECT * flagged by review; flagging logic in semantic views rejected in code review

## Response Template
```sql
-- Semantic View (explicit columns, comments; COMMENT before AS)
CREATE OR REPLACE VIEW <DB>.<SCHEMA>.semantic_sales
COMMENT = 'Sales facts with conformed customer dimension keys'
AS
SELECT
  f.sale_id COMMENT 'Surrogate key',
  f.customer_id,
  d.customer_name,
  f.sale_date,
  f.amount AS measure_amount
FROM <DB>.CORE.sales f
JOIN <DB>.DIM.customers d ON d.customer_id = f.customer_id;
```

```text
# Analyst Prompt Template
Answer using the semantic definitions in <DB>.<SCHEMA>.semantic_*. Prefer measure_* fields. Include time grain when summarizing.
```

```yaml
# Agent Tool Configuration
Tool Name: {analyst_tool_name}
Type: Cortex Analyst
Semantic View: <DB>.<SCHEMA>.<VIEW>
Description: "Use this tool for {specific domain}. It can {list capabilities}. Use for questions about {when-to-use examples}."
```

## References

### External Documentation
- [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) - Natural language to SQL with semantic models
- [Semantic Views](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) (see semantic model guidance)
- [Snowflake Cortex AISQL](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql) - AI SQL functions
- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents) - Agent tool configuration

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Semantic Views**: `106-snowflake-semantic-views.md`
- **AISQL**: `114-snowflake-cortex-aisql.md`
- **Cortex Agents**: `115-snowflake-cortex-agents.md` - Agent archetypes, configuration templates, planning instructions, testing patterns
- **Cortex Search**: `116-snowflake-cortex-search.md` - Search tool configuration for hybrid agents
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
