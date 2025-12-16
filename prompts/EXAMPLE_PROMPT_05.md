# Example Prompt 05: Snowflake Cortex Search Service

## The Prompt

```
Task: Create a Cortex Search service for product documentation to use with Cortex Agents
Table: DOCS.RAW.PRODUCT_DOCS (doc_id, content, category, author, published_date, access_tier)
```

## What This Helps

AI assistants will automatically:
- Detect "Cortex Search" keyword → Load `rules/116-snowflake-cortex-search.md`
- Detect "Cortex Agents" keyword → Load `rules/115-snowflake-cortex-agents-core.md`
- Detect Snowflake context → Load `rules/100-snowflake-core.md`
- Understand metadata columns available for filtering (category, author, access_tier)
- Apply correct CREATE CORTEX SEARCH SERVICE syntax with ATTRIBUTES

## Why It's Good

**Technology clear (Snowflake):** Explicitly mentions Cortex Search and Cortex Agents, triggering specialized retrieval and agent rules

**Table specified with columns:** Provides exact table path and column names, enabling accurate service configuration without guesswork

**Metadata columns visible:** Lists filtering columns (category, author, access_tier), signaling need for ATTRIBUTES clause

**Minimal yet complete:** Provides exactly enough information for AI to generate valid Cortex Search service DDL

## Expected Output Structure

The AI should generate DDL following this pattern:

```sql
-- Step 1: Create search service with metadata attributes
CREATE CORTEX SEARCH SERVICE IF NOT EXISTS DOCS.SEARCH.PRODUCT_DOCS_SERVICE
ON content
ATTRIBUTES doc_id, category, author, published_date, access_tier
WAREHOUSE = COMPUTE_WH
TARGET_LAG = '1 day'
AS (
  SELECT
    doc_id,
    content,
    category,
    author,
    published_date,
    access_tier
  FROM DOCS.RAW.PRODUCT_DOCS
  WHERE content IS NOT NULL
    AND LENGTH(content) > 50
);

-- Step 2: Verify service creation
SHOW CORTEX SEARCH SERVICES IN SCHEMA DOCS.SEARCH;

-- Step 3: Test search with sample query
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
  'DOCS.SEARCH.PRODUCT_DOCS_SERVICE',
  '{"query": "API authentication", "limit": 5}'
) AS search_results;

-- Step 4: Test search with metadata filter
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
  'DOCS.SEARCH.PRODUCT_DOCS_SERVICE',
  '{
    "query": "getting started",
    "limit": 5,
    "filter": {"category": "tutorials", "access_tier": "public"}
  }'
) AS filtered_results;

-- Step 5: Grant access to agent role
GRANT USAGE ON CORTEX SEARCH SERVICE DOCS.SEARCH.PRODUCT_DOCS_SERVICE
TO ROLE agent_runner;
```

## Key Rules Applied

1. **ON clause:** Specifies the main searchable content column
2. **ATTRIBUTES clause:** Lists metadata columns for filtering
3. **TARGET_LAG:** Controls refresh frequency (1 day is typical)
4. **Content validation:** Filter out NULL or tiny content chunks
5. **Verify after creation:** Use SHOW and SEARCH_PREVIEW to validate
6. **Grant access:** Required for Cortex Agents to use the service

