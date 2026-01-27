# 115 Example: Cortex Agent Prerequisites Validation

> **EXAMPLE FILE** - Reference implementation for `115-snowflake-cortex-agents-core.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 115-snowflake-cortex-agents-core.md
**Demonstrates:** Complete pre-flight validation workflow before creating Cortex Agents
**Use When:** Before creating any Cortex Agent to verify all prerequisites are met
**Version:** 1.0
**Last Validated:** 2026-01-27

## Prerequisites

- [ ] Snowflake account (Cortex features may need to be enabled)
- [ ] Role with appropriate Cortex privileges
- [ ] Semantic views and/or Cortex Search services planned for agent tools

## Implementation

### Prerequisites Checklist

Before creating any Cortex Agent, verify ALL of these conditions:

- [ ] Snowflake account has Cortex features enabled
- [ ] Required permissions granted (USAGE, SELECT, EXECUTE)
- [ ] Semantic views exist and are queryable (for Cortex Analyst tools)
- [ ] Cortex Search services created and accessible (for Search tools)
- [ ] **Warehouse explicitly specified** in all Cortex Analyst tool_resources
- [ ] Warehouse has appropriate size for expected query workload
- [ ] Warehouse usage grants configured for agent execution role
- [ ] Test queries return expected results before agent integration
- [ ] RBAC roles properly configured for agent execution

### Step 1: Check Cortex Availability

```sql
-- Verify Cortex features are available in your account
SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;

-- Expected: Parameters showing Cortex feature configuration
-- Look for: CORTEX_ENABLED_CROSS_REGION = true

-- If parameters not visible, contact Snowflake support to enable Cortex
```

### Step 2: Verify Semantic View Access (for Cortex Analyst tools)

```sql
-- Test semantic view is accessible and has data
-- Replace with your actual database, schema, and view name
SELECT * FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW LIMIT 5;

-- If using SEMANTIC_VIEW function:
SELECT * FROM TABLE(SEMANTIC_VIEW('ANALYTICS.SEMANTIC.PORTFOLIO_VIEW')) LIMIT 5;

-- Verify view structure
SHOW SEMANTIC VIEWS LIKE 'PORTFOLIO_VIEW' IN SCHEMA ANALYTICS.SEMANTIC;
SHOW SEMANTIC DIMENSIONS FOR SEMANTIC VIEW ANALYTICS.SEMANTIC.PORTFOLIO_VIEW;
SHOW SEMANTIC METRICS FOR SEMANTIC VIEW ANALYTICS.SEMANTIC.PORTFOLIO_VIEW;
```

### Step 3: Verify Cortex Search Service (for Search tools)

```sql
-- Check search service exists
SHOW CORTEX SEARCH SERVICES IN SCHEMA DOCS.SEARCH;

-- Test search service responds
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{"query": "test query", "columns": ["chunk"], "limit": 1}'
);

-- Expected: JSON response with search results
-- If error: Verify service name, schema, and permissions
```

### Step 4: Verify Role Permissions

```sql
-- Check current role's grants
SHOW GRANTS TO ROLE agent_runner;

-- Required grants should include:
-- - USAGE on databases and schemas
-- - SELECT on semantic views
-- - USAGE on Cortex Search services
-- - USAGE on Cortex functions (COMPLETE, SEARCH_PREVIEW, etc.)

-- Check specific object grants
SHOW GRANTS ON SEMANTIC VIEW ANALYTICS.SEMANTIC.PORTFOLIO_VIEW;
SHOW GRANTS ON CORTEX SEARCH SERVICE DOCS.SEARCH.research_reports_service;
```

### Step 5: Test Cortex Function Access

```sql
-- Verify Cortex functions are accessible
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3.1-8b',
    'What is 2+2?'
) AS test_response;

-- Expected: Returns JSON response from model
-- Example: {"choices":[{"message":"4",...}]}

-- Test with a more complex prompt
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'claude-3-5-sonnet',
    'Summarize this in one sentence: Snowflake is a cloud data platform.'
) AS test_response;
```

### Step 6: Comprehensive Pre-Implementation Validation Script

```sql
-- Run this complete validation before creating any agent
-- All checks should pass (non-zero counts, no errors)

-- 1. Check Cortex availability
SELECT 'Step 1: Cortex Parameters' AS check_name;
SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;

-- 2. Verify semantic views (replace with your views)
SELECT 'Step 2: Semantic View Access' AS check_name;
SELECT 'PORTFOLIO_VIEW' AS view_name, COUNT(*) AS row_count
FROM ANALYTICS.SEMANTIC.PORTFOLIO_VIEW;

-- 3. Verify search services (replace with your services)
SELECT 'Step 3: Cortex Search Services' AS check_name;
SHOW CORTEX SEARCH SERVICES IN SCHEMA DOCS.SEARCH;

-- 4. Check permissions
SELECT 'Step 4: Role Permissions' AS check_name;
SHOW GRANTS TO ROLE agent_runner;

-- 5. Test Cortex function
SELECT 'Step 5: Cortex Function Test' AS check_name;
SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', 'Reply with OK') AS response;

-- 6. Test warehouse access (for Cortex Analyst)
SELECT 'Step 6: Warehouse Access' AS check_name;
SELECT CURRENT_WAREHOUSE() AS current_warehouse;
USE WAREHOUSE ANALYTICS_WH;
SELECT CURRENT_WAREHOUSE() AS verified_warehouse;
```

## Validation Summary Template

After running all checks, document results:

```markdown
## Agent Prerequisites Validation Results

**Date:** YYYY-MM-DD
**Agent Name:** [planned agent name]
**Validated By:** [your name/role]

### Checklist Results

| Check | Status | Notes |
|-------|--------|-------|
| Cortex Parameters | ✅/❌ | |
| Semantic View Access | ✅/❌ | View: [name], Rows: [count] |
| Cortex Search Service | ✅/❌ | Service: [name] |
| Role Permissions | ✅/❌ | Role: [name] |
| Cortex Function Test | ✅/❌ | Model: [name] |
| Warehouse Access | ✅/❌ | Warehouse: [name] |

### Blockers Identified

- [ ] [List any failing checks]

### Ready to Proceed

- [ ] All checks passed - proceed with agent creation
- [ ] Blockers identified - resolve before proceeding
```

## Validation

Run the comprehensive script above. All steps should complete without errors.

**Expected Results:**
- Step 1: Cortex parameters visible (CORTEX_ENABLED_CROSS_REGION = true)
- Step 2: Semantic view returns data (row_count > 0)
- Step 3: Cortex Search services listed
- Step 4: Role grants include required permissions
- Step 5: Cortex function returns valid response
- Step 6: Warehouse accessible and can be used

**If Any Check Fails:**
- STOP - Do not create the agent
- Document the failing check
- Resolve the prerequisite issue first
- Re-run validation before proceeding
