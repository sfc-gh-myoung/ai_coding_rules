# 116 Example: Cortex Search Service

> **EXAMPLE FILE** - Reference implementation for `116-snowflake-cortex-search.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 116-snowflake-cortex-search.md
**Demonstrates:** Creating and using a Cortex Search service for document retrieval
**Use When:** Setting up semantic search for documents, knowledge bases, or as a Cortex Agent tool
**Version:** 1.0
**Last Validated:** 2026-01-23

## Prerequisites

- [ ] Snowflake account with Cortex Search feature enabled
- [ ] ACCOUNTADMIN or role with CREATE CORTEX SEARCH SERVICE privilege
- [ ] Source table with text content to index
- [ ] Understanding of chunking strategy for your content

## Implementation

```sql
-- Step 1: Create source table with chunked documents
CREATE OR REPLACE TABLE my_db.my_schema.document_chunks (
    chunk_id VARCHAR PRIMARY KEY,
    document_id VARCHAR NOT NULL,
    document_title VARCHAR,
    chunk_text VARCHAR NOT NULL,  -- The searchable content
    chunk_index NUMBER,           -- Order within document
    metadata VARIANT,             -- Additional metadata (author, date, etc.)
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Step 2: Insert sample data (in production, use a chunking pipeline)
INSERT INTO my_db.my_schema.document_chunks (chunk_id, document_id, document_title, chunk_text, chunk_index, metadata)
VALUES
    ('doc1_chunk1', 'DOC001', 'Return Policy', 
     'Our return policy allows customers to return items within 30 days of purchase for a full refund. Items must be in original condition with tags attached.',
     1, PARSE_JSON('{"category": "policy", "department": "customer_service"}')),
    ('doc1_chunk2', 'DOC001', 'Return Policy',
     'For damaged items, customers may request a replacement or refund within 60 days. Photo evidence of damage is required for processing.',
     2, PARSE_JSON('{"category": "policy", "department": "customer_service"}')),
    ('doc2_chunk1', 'DOC002', 'Shipping Guidelines',
     'Standard shipping takes 5-7 business days. Express shipping is available for an additional fee and delivers within 2-3 business days.',
     1, PARSE_JSON('{"category": "operations", "department": "logistics"}'));

-- Step 3: Create Cortex Search service
CREATE OR REPLACE CORTEX SEARCH SERVICE my_db.my_schema.docs_search_service
  ON chunk_text                    -- Primary search column
  ATTRIBUTES document_title, metadata  -- Filterable/returnable columns
  WAREHOUSE = compute_wh
  TARGET_LAG = '1 hour'            -- Sync frequency
  COMMENT = 'Document search for policies and procedures'
AS (
    SELECT 
        chunk_id,
        document_id,
        document_title,
        chunk_text,
        chunk_index,
        metadata
    FROM my_db.my_schema.document_chunks
);

-- Step 4: Grant access
GRANT USAGE ON CORTEX SEARCH SERVICE my_db.my_schema.docs_search_service 
    TO ROLE analyst_role;

-- Step 5: Test basic search
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'my_db.my_schema.docs_search_service',
    '{
        "query": "return policy for damaged items",
        "columns": ["chunk_text", "document_title"],
        "limit": 5
    }'
);

-- Step 6: Search with metadata filter
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'my_db.my_schema.docs_search_service',
    '{
        "query": "shipping time",
        "columns": ["chunk_text", "document_title"],
        "filter": {"@eq": {"metadata:category": "operations"}},
        "limit": 3
    }'
);
```

## Advanced: Using with Cortex Agent

```sql
-- Create agent that uses Cortex Search as a tool
CREATE OR REPLACE CORTEX AGENT docs_assistant
  MODEL = 'claude-3-5-sonnet'
  TOOLS = (my_db.my_schema.docs_search_service)
  PLANNING_INSTRUCTIONS = $$
## Tool Usage

Use docs_search_service to find relevant documentation when users ask about:
- Company policies (returns, refunds, warranties)
- Procedures and guidelines
- How-to questions
- Definitions and reference materials

**Search Strategy:**
1. Extract key terms from the question
2. Search for the most specific terms first
3. If no results, broaden the search
4. Return relevant chunks with context
$$
  RESPONSE_INSTRUCTIONS = $$
## Response Format

When answering from documents:
1. Quote the relevant passage
2. Cite the document title
3. Summarize the key point
4. Note if the information may be outdated

If no relevant documents found:
- Clearly state "I couldn't find information about X in the documentation"
- Do NOT make up answers
$$;

-- Test agent with document search
SELECT SNOWFLAKE.CORTEX.AGENT(
    'docs_assistant',
    'What is the return policy for damaged items?'
);
```

## Validation

```sql
-- Verify search service exists
SHOW CORTEX SEARCH SERVICES LIKE 'docs_search_service' IN SCHEMA my_db.my_schema;

-- Test search relevance
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'my_db.my_schema.docs_search_service',
    '{"query": "refund damaged", "columns": ["chunk_text", "document_title"], "limit": 3}'
);
-- Expected: Return Policy chunks about damaged items should rank highest

-- Test filter functionality
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'my_db.my_schema.docs_search_service',
    '{"query": "policy", "columns": ["chunk_text"], "filter": {"@eq": {"metadata:department": "customer_service"}}, "limit": 5}'
);
-- Expected: Only customer_service department documents returned

-- Verify sync status
SELECT SYSTEM$CORTEX_SEARCH_SERVICE_STATUS('my_db.my_schema.docs_search_service');

-- Check grants
SHOW GRANTS ON CORTEX SEARCH SERVICE my_db.my_schema.docs_search_service;
```

**Expected Result:**
- Cortex Search service created and synced
- Semantic search returns relevant chunks ranked by relevance
- Metadata filters work correctly
- Service can be used as Cortex Agent tool
- Only authorized roles have access
