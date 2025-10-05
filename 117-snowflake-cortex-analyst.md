**Description:** Best practices for Snowflake Cortex Analyst and Semantic Views, including modeling guidance, governance, and usage patterns.
**AppliesTo:** `**/*.sql`, `**/*.py`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-10-03

# Snowflake Cortex Analyst & Semantic Views Best Practices

## Purpose
Define reliable patterns for designing and operating Semantic Views and Cortex Analyst experiences: semantic modeling, object governance, prompt templates, and integration with retrieval/agents.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Semantic Views modeling; Cortex Analyst configuration and usage; integration with AISQL/Agents/Search; governance

## Contract
- **Inputs/Prereqs:**
  - Curated semantic layer with stable dimensions/measures; naming conventions established
  - Access roles and data masking policies aligned to business domains
  - Reference documentation for business definitions
- **Allowed Tools:** Semantic Views, Cortex Analyst, AISQL for enrichment, Cortex Search for retrieval
- **Forbidden Tools:**
  - Ad-hoc views masquerading as semantic views without definitions and comments
  - Ambiguous measures without aggregation rules or grain
- **Required Steps:**
  1. Define business entities, measures, and conformed dimensions with clear grain and join keys
  2. Implement Semantic Views with comments on columns/measures; avoid `SELECT *`
  3. Use consistent naming conventions and fully qualified object names
  4. Apply masking/row access policies; tag sensitive fields
  5. Document prompt templates and usage guidelines for Cortex Analyst
- **Output Format:** Semantic view definitions and usage patterns
- **Validation Steps:** Views compile; definitions align to business glossary; access rules enforced; analyst prompts produce consistent answers

## Key Principles
- Explicit measures and dimensions with clear grain and aggregation
- Consistent naming and comments; avoid nested view chains
- Governed access with masking and row-level security
- Reuse semantic views across agents, AISQL, and Analyst to ensure consistency

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

## 3. Prompt Templates for Analyst
```text
Answer using the semantic definitions in ANALYTICS.SEMANTIC.*. Prefer measures ending with measure_*.
Include time grain in results when summarizing over time.
```

## 4. Integration Patterns
- Use Semantic Views as the authoritative layer for Cortex Agents and AISQL to ensure consistent definitions
- For retrieval, index explanations and column comments to improve grounding quality

## Quick Compliance Checklist
- [ ] Semantic Views define explicit measures/dimensions and grain
- [ ] No `SELECT *`; comments present for non-obvious fields
- [ ] Masking and row access policies applied where needed
- [ ] Naming conventions and fully qualified names used
- [ ] Prompt templates documented for Cortex Analyst

## Validation
- **Success checks:** Analyst answers align with business definitions; joins respect grain; access rules enforced
- **Negative tests:** Ambiguous measures cause rejected PRs; missing comments or SELECT * flagged by review

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

## References

### External Documentation
- [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- [Semantic Views](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) (see semantic model guidance)
- [Snowflake Cortex AISQL](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql)

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Semantic Views**: `106-snowflake-semantic-views.md`
- **AISQL**: `114-snowflake-cortex-aisql.md`
- **Agents**: `115-snowflake-cortex-agents.md`


