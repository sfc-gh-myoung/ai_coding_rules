**Description:** Best practices for Snowflake Cortex Search: indexing, embeddings, filters, hybrid retrieval, agent integration, and query patterns with governance, observability, prerequisites validation, and error troubleshooting.
**Type:** Agent Requested
**AppliesTo:** `**/*.sql`, `**/*.py`
**AutoAttach:** false
**Keywords:** Cortex Search, vector search, embeddings, search index, RAG, semantic search, agent tools, retrieval, troubleshooting, AI_EMBED, create search service, search service error, document retrieval, cortex search setup, search index creation, hybrid search, search service debug, vector similarity
**TokenBudget:** ~4000
**ContextTier:** Medium
**Version:** 1.4
**LastUpdated:** 2025-11-07
**Depends:** 100-snowflake-core, 105-snowflake-cost-governance, 111-snowflake-observability, 114-snowflake-cortex-aisql

# Snowflake Cortex Search Best Practices

## Purpose
Provide reliable patterns for building and querying Cortex Search indices, including data preparation, embedding hygiene, metadata filters, hybrid retrieval, agent tool configuration, and cost/latency considerations.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Cortex Search indexing and querying; embedding creation; metadata and security filters; agent tool integration; observability and cost control

## Quick Start TL;DR (Essential Patterns Reference)

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Clean and chunk data** - Normalize, remove boilerplate, chunk long docs with overlap
- **Add metadata columns** - Source, author, timestamp, access tier for filtering
- **Create search index** - Use CREATE CORTEX SEARCH INDEX with explicit columns
- **Use metadata filters** - Filter by source, date, access level in queries
- **Configure for agents** - Clear tool descriptions, when-to-use guidance
- **Monitor costs** - Track embedding and query costs, prune outdated content
- **Never index raw PII** - Apply masking/tagging before indexing

**Quick Checklist:**
- [ ] Data cleaned and chunked (if long documents)
- [ ] Metadata columns added (source, timestamp, etc.)
- [ ] Search index created and refreshed
- [ ] Sample queries validated
- [ ] Metadata filters configured
- [ ] Agent tool descriptions written
- [ ] Cost/latency monitoring enabled

## Contract
- **Inputs/Prereqs:**
  - Cleaned source data with explicit columns; minimal sensitive content
  - Embeddings available via `AI_EMBED` or created during indexing
  - RBAC and tagging for index/table access
- **Allowed Tools:** SQL (Cortex Search), Snowpark Python, AISQL embeddings, AI Observability, Cortex Agents
- **Forbidden Tools:**
  - Indexing raw PII without masking/tagging
  - Overly long documents without chunking/normalization
- **Required Steps:**
  1. Normalize/clean data; remove boilerplate; chunk long documents with overlap
  2. Attach metadata (source, author, timestamp, access tier) for filtering
  3. Create or refresh indices; validate document counts and sample retrieval
  4. Configure search tools with clear descriptions and when-to-use guidance
  5. Query with metadata filters; tune top_k and hybrid weights
  6. Test search tools independently before agent integration
  7. Monitor costs/latency; prune outdated content
- **Output Format:** SQL patterns for indexing and querying; agent tool configurations; Snowpark examples
- **Validation Steps:** Index contains expected docs; retrieval quality validated; filters enforce access; tool descriptions are clear; costs within budget

## Key Principles
- High-quality retrieval requires clean text, consistent chunking, and rich metadata
- Use metadata filters to enforce RBAC-like scoping; never rely on client-side filtering only
- Clear tool descriptions with document type and when-to-use guidance for agents
- Periodically rebuild or refresh indices; remove stale/duplicative content
- Evaluate retrieval with gold queries and measure relevance

## 0. Prerequisites Validation

Before implementing Cortex Search, verify your environment meets requirements:

### 0.1 Prerequisites Checklist

- [ ] Snowflake account has Cortex Search capability enabled
- [ ] Source data cleaned and prepared for indexing
- [ ] Required permissions granted (CREATE, USAGE, SELECT)
- [ ] Warehouse available for index creation and queries
- [ ] Understanding of metadata schema for filtering

### 0.2 Verification Commands

**Check Cortex Search Availability:**
```sql
-- Verify Cortex Search is available
SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;

-- Check if schema has appropriate privileges
SHOW GRANTS ON SCHEMA {DATABASE}.{SCHEMA};
```

**Verify Source Data:**
```sql
-- Check source data exists and has required columns
SELECT 
    COUNT(*) AS total_rows,
    COUNT(DISTINCT content_column) AS unique_docs
FROM {DATABASE}.{SCHEMA}.{SOURCE_TABLE};

-- Example:
SELECT 
    COUNT(*) AS total_rows,
    COUNT(DISTINCT document_id) AS unique_docs
FROM DOCS.RAW.research_reports;
```

**Test Search Service Creation Permissions:**
```sql
-- Verify you can create Cortex Search services
SHOW GRANTS ON SCHEMA {DATABASE}.{SCHEMA};

-- Required grants:
-- - CREATE CORTEX SEARCH SERVICE on schema
-- - USAGE on warehouse
-- - SELECT on source tables/views
```

**Verify Warehouse Access:**
```sql
-- Check warehouse exists and is accessible
SHOW WAREHOUSES LIKE '{WAREHOUSE_NAME}';

-- Test warehouse usage
USE WAREHOUSE {WAREHOUSE_NAME};
SELECT CURRENT_WAREHOUSE();
```

### 0.3 Pre-Implementation Validation

Run this comprehensive check before creating search services:

```sql
-- 1. Verify Cortex availability
SHOW PARAMETERS LIKE 'CORTEX%' IN ACCOUNT;

-- 2. Check source data quality
SELECT 
    'Source Data Check' AS validation_step,
    COUNT(*) AS row_count,
    COUNT(DISTINCT doc_id) AS unique_docs,
    AVG(LENGTH(content)) AS avg_content_length
FROM {DATABASE}.{SCHEMA}.{SOURCE_TABLE};

-- 3. Verify schema permissions
SELECT 'Permission Check' AS validation_step,
       COUNT(*) AS grant_count
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));

-- 4. Test warehouse
SELECT 'Warehouse Check' AS validation_step,
       CURRENT_WAREHOUSE() AS warehouse_name;
```

**All checks should return non-zero counts and valid results.** If any fail, address prerequisites before proceeding.

## 1. Data Preparation
- Lowercase, strip boilerplate, normalize whitespace; remove navigation/UI fragments
- Chunk long docs (e.g., 500–1000 tokens) with overlap ~10–15%

## 2. Creating Cortex Search Services

### 2.1 Prepare Search-Ready View

First, create a view with clean content and metadata:

```sql
-- Prepare view with required columns for search
CREATE OR REPLACE VIEW DOCS.PREPARED.research_reports_ready AS
SELECT 
  doc_id,
  content_clean,  -- Main searchable content
  source,         -- Metadata for filtering
  author,         -- Metadata for filtering
  published_at,   -- Metadata for filtering
  access_tier     -- Metadata for filtering
FROM DOCS.RAW.research_reports_chunked
WHERE content_clean IS NOT NULL 
  AND LENGTH(content_clean) > 50;  -- Filter out empty/tiny chunks
```

### 2.2 Create Cortex Search Service

```sql
-- Create search service with complete working syntax
CREATE CORTEX SEARCH SERVICE IF NOT EXISTS DOCS.SEARCH.research_reports_service
ON content_clean                                    -- Column to search
ATTRIBUTES doc_id, source, author, published_at, access_tier  -- Metadata columns
WAREHOUSE = COMPUTE_WH                              -- Warehouse for index creation
TARGET_LAG = '1 day'                                -- Refresh frequency
AS (
  SELECT 
    doc_id,
  content_clean,
  source,
  author,
  published_at,
  access_tier
  FROM DOCS.PREPARED.research_reports_ready
);
```

### 2.3 Verify Service Creation

```sql
-- Check service was created successfully
SHOW CORTEX SEARCH SERVICES IN SCHEMA DOCS.SEARCH;

-- View service details
DESC CORTEX SEARCH SERVICE DOCS.SEARCH.research_reports_service;

-- Test service responds to queries
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
  'DOCS.SEARCH.research_reports_service',
  '{"query": "test", "limit": 5}'
) AS search_results;
```

### 2.4 Grant Access to Service

```sql
-- Grant USAGE to roles that will query the service
GRANT USAGE ON CORTEX SEARCH SERVICE DOCS.SEARCH.research_reports_service TO ROLE agent_runner;
GRANT USAGE ON CORTEX SEARCH SERVICE DOCS.SEARCH.research_reports_service TO ROLE analyst_role;

-- Verify grants
SHOW GRANTS ON CORTEX SEARCH SERVICE DOCS.SEARCH.research_reports_service;
```

## 3. Embedding Hygiene
- If embedding externally, store vectors in a dedicated column; ensure consistent model/version
- Consider re-embedding only when content or model materially changes

## 4. Querying Cortex Search Services

### 4.1 Basic Query Pattern

```sql
-- Query search service with SEARCH_PREVIEW function
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',  -- Service name (fully qualified)
    '{
        "query": "warehouse performance optimization",
        "limit": 10
    }'
) AS search_results;
```

### 4.2 Query with Metadata Filters

```sql
-- Filter by metadata attributes (access_tier, source, author, etc.)
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{
        "query": "investment strategy",
        "limit": 10,
        "filter": {
            "access_tier": "public",
            "source": "Goldman Sachs"
        }
    }'
) AS filtered_results;
```

### 4.3 Query with Date Range Filters

```sql
-- Filter by date range using metadata
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{
        "query": "market outlook",
        "limit": 10,
        "filter": {
            "published_at": {
                "$gte": "2025-01-01",
                "$lte": "2025-12-31"
            }
        }
    }'
) AS date_filtered_results;
```

### 4.4 Extract Results from JSON Response

```sql
-- Parse search results from JSON response
WITH search AS (
    SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'DOCS.SEARCH.research_reports_service',
        '{"query": "ESG ratings", "limit": 10}'
    ) AS results
)
SELECT 
    r.value:doc_id::STRING AS doc_id,
    r.value:score::FLOAT AS relevance_score,
    r.value:content::STRING AS content_snippet,
    r.value:source::STRING AS source,
    r.value:author::STRING AS author,
    r.value:published_at::DATE AS published_date
FROM search,
LATERAL FLATTEN(input => results:results) r
ORDER BY relevance_score DESC;
```

### 4.5 Common Filter Patterns

**Filter by Multiple Values (OR logic):**
```sql
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{
        "query": "technology sector",
        "limit": 10,
        "filter": {
            "source": ["Goldman Sachs", "Morgan Stanley", "JP Morgan"]
        }
    }'
);
```

**Filter by Multiple Conditions (AND logic):**
```sql
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{
        "query": "cloud computing",
        "limit": 10,
        "filter": {
            "access_tier": "public",
            "source": "Goldman Sachs",
            "published_at": {"$gte": "2025-01-01"}
        }
    }'
);
```

## 5. Cortex Search as Agent Tool

### 5.1 Tool Configuration Pattern

When using Cortex Search as a tool within Cortex Agents, configure with explicit document type and when-to-use guidance:

```yaml
Tool Name: search_{document_type}          # e.g., search_research_reports, search_policies
Type: Cortex Search
Service: {DATABASE}.{SCHEMA}.{SERVICE}     # e.g., DOCS.SEARCH.RESEARCH_REPORTS_SERVICE
ID Column: DOCUMENT_ID                     # Must match service configuration
Title Column: DOCUMENT_TITLE               # Must match service configuration
Description: "Search {document_type} for {specific_use_case}. Use for questions about {when_to_use_guidance}."

# Example: Research Reports Search Tool
Tool Name: search_research_reports
Type: Cortex Search
Service: DOCS.SEARCH.RESEARCH_REPORTS_SERVICE
ID Column: DOCUMENT_ID
Title Column: DOCUMENT_TITLE
Description: "Search investment research reports for analyst opinions, ratings, price targets, and market commentary. Use for questions about analyst views, investment recommendations, and qualitative research insights."
```

### 5.2 Tool Description Best Practices

**Clear Document Type Selection:**
```yaml
# GOOD - Explicit document type and use cases
Description: "Search earnings call transcripts for management commentary, guidance updates, and forward-looking statements. Use for questions about company strategy, management outlook, and qualitative earnings insights."

# BAD - Too vague
Description: "Searches documents"
```

**When-to-Use Guidance:**
```yaml
# GOOD - Explicit trigger words
Description: "Search regulatory filings for compliance policies, legal requirements, and governance standards. Use for questions containing 'policy', 'requirement', 'compliance', 'regulation', or 'legal'."

# BAD - No guidance on when appropriate
Description: "Search all company documents"
```

**Avoiding Overlapping Tools:**
```yaml
# GOOD - Distinct document types
Tool A: "Search investment research reports (analyst opinions, ratings)"
Tool B: "Search earnings transcripts (management commentary, guidance)"

# BAD - Overlapping document types
Tool A: "Search financial documents"
Tool B: "Search company reports"  # Too similar!
```

### 5.3 Citation Requirements in Agent Context

When Cortex Search is used in agents, proper citation is critical:

**Agent Response Instructions Should Include:**
```yaml
Response Instructions: |
  Always cite document sources with:
  1. Document type (e.g., "Research Report", "Earnings Transcript")
  2. Document title or identifier
  3. Publication or recording date
  
  Format: "According to {document_type} '{title}' from {date}..."
  
  Example: "According to Goldman Sachs Research Report 'Tech Sector Outlook' from 2025-01-15, the analyst recommends..."
```

**Why This Matters:**
- Users need to verify claims against original sources
- Different document types have different authority/recency requirements
- Proper citations enable traceability and compliance

### 5.4 Testing Cortex Search Tools

**Component Testing Pattern:**
```python
def test_search_tool(session: Session, service_name: str):
    """Test Cortex Search tool independently"""
    
    # Simple search query to verify tool responds
    result = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
            '{service_name}',
            '{{"query": "test", "limit": 1}}'
        )
    """).collect()
    
    assert len(result) > 0, f"Search tool {service_name} returned no results"
    print(f"Search tool test passed: {service_name}")
    return True
```

**Integration Testing:**
After component tests pass, test agent's tool selection logic:
- Qualitative queries should route to appropriate Cortex Search tool
- Verify correct search tool selected when multiple available
- Confirm citations are properly formatted

**Test Query Examples:**
```python
# Test Cortex Search tool selection
"What does recent research say about {company}?"     # Should use search tool
"Find compliance policies for {topic}"               # Should use search tool
"Show analyst opinions on {security}"                # Should use search tool
```

### 5.5 Research-Focused Agents (Search Only)

For agents using ONLY Cortex Search tools (no Cortex Analyst):

**Use Cases:**
- Document synthesis and literature review
- Policy research and compliance checking
- Qualitative information retrieval

**Planning Instructions Pattern:**
```
1. Analyze query to identify relevant document types and search terms
2. Choose appropriate search tool based on information type:
   - search_research_reports: Analyst opinions, ratings, market commentary
   - search_transcripts: Management commentary, earnings guidance
   - search_policies: Compliance requirements, governance standards
3. For multi-faceted queries, search across multiple document types
4. Synthesize findings with proper citations (document type, title, date)
5. If no relevant documents found, suggest alternative search terms
```

**See Also:** `115-snowflake-cortex-agents-core.md` Section 1.3 for comprehensive research agent patterns

### 5.6 Hybrid Agents (Search + Analyst)

For agents combining Cortex Search with Cortex Analyst tools:

**Query Classification:**
- QUANTITATIVE → Use Cortex Analyst (numbers, calculations, metrics)
- QUALITATIVE → Use Cortex Search (opinions, context, explanations)
- MIXED → Use Cortex Analyst first, then Search for supporting context

**Planning Instructions Pattern:**
```
1. Classify query by type (quantitative, qualitative, or mixed)
2. For quantitative: Use appropriate Cortex Analyst tool
3. For qualitative: Use appropriate Cortex Search tool  
4. For mixed: Use Analyst for numbers, Search for supporting research
5. Synthesize across tool types into coherent response
```

**See Also:** `115-snowflake-cortex-agents-core.md` Section 1.4 for comprehensive hybrid agent patterns

### 5.7 Cross-Reference to Agent Configuration

For complete agent configuration including Cortex Search tools:
- **Research-Focused Agents:** `115-snowflake-cortex-agents-core.md` Section 1.3
- **Hybrid Agents:** `115-snowflake-cortex-agents-core.md` Section 1.4
- **Planning Instructions:** `115-snowflake-cortex-agents-core.md` Section 4.4
- **Response Instructions:** `115-snowflake-cortex-agents-core.md` Section 5.4
- **Testing Patterns:** `115-snowflake-cortex-agents-core.md` Section 6

## 6. Hybrid Retrieval
- Blend dense vector search with sparse/text signals when supported; tune weights empirically
- Keep top_k small initially (e.g., 10–20) and increase only if recall is insufficient

## 7. Evaluation and Observability
- Maintain a gold set of query→expected passage mappings; measure precision@k and MRR
- Use AI Observability to log search queries and downstream answer quality

## 8. Cost and Operations
- Limit index rebuilds; prefer incremental updates where supported
- Archive or delete stale content from indices; partition by recency/source if needed

## 9. Common Errors and Solutions

### Error: "Service not found" or "Object does not exist"

**Cause:** Search service doesn't exist or role lacks USAGE permission

**Solutions:**
```sql
-- 1. Verify service exists
SHOW CORTEX SEARCH SERVICES IN SCHEMA {DATABASE}.{SCHEMA};

-- Example:
SHOW CORTEX SEARCH SERVICES IN SCHEMA DOCS.SEARCH;

-- 2. Check service details
DESC CORTEX SEARCH SERVICE {DATABASE}.{SCHEMA}.{SERVICE_NAME};

-- 3. Grant USAGE to role
GRANT USAGE ON CORTEX SEARCH SERVICE {DATABASE}.{SCHEMA}.{SERVICE_NAME} TO ROLE {ROLE_NAME};

-- Example:
GRANT USAGE ON CORTEX SEARCH SERVICE DOCS.SEARCH.research_reports_service TO ROLE agent_runner;

-- 4. Verify grant
SHOW GRANTS TO ROLE agent_runner;
```

### Error: "No results returned" or "Empty search response"

**Cause:** Service empty, query doesn't match indexed content, or filters too restrictive

**Solutions:**
```sql
-- 1. Check service has data
DESC CORTEX SEARCH SERVICE DOCS.SEARCH.research_reports_service;
-- Look at row count in description

-- 2. Test with broad query (no filters)
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{"query": "test", "limit": 10}'
);

-- 3. Verify source view has data
SELECT COUNT(*) FROM DOCS.PREPARED.research_reports_ready;

-- 4. Test with simpler filters
-- Start with no filters, then add one at a time
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{"query": "investment", "limit": 10}'  -- No filters
);
```

### Error: "Permission denied" on CORTEX.SEARCH_PREVIEW

**Cause:** Missing USAGE grant on SNOWFLAKE.CORTEX.SEARCH_PREVIEW function

**Solutions:**
```sql
-- Grant function access
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.SEARCH_PREVIEW TO ROLE agent_runner;

-- Verify grant
SHOW GRANTS TO ROLE agent_runner;

-- Test function access
USE ROLE agent_runner;
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{"query": "test", "limit": 1}'
);
```

### Error: "Invalid filter syntax" or "JSON parse error"

**Cause:** Malformed JSON in query parameter or invalid filter structure

**Solutions:**
```sql
-- INCORRECT - Invalid JSON (single quotes around keys)
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'service_name',
    "{'query': 'test', 'limit': 10}"  -- WRONG: Uses single quotes
);

-- CORRECT - Valid JSON with proper double quotes
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{"query": "test", "limit": 10}'  -- RIGHT: Uses double quotes
);

-- INCORRECT - Invalid filter structure
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'service_name',
    '{
        "query": "test",
        "filter": "public"  -- WRONG: filter must be object
    }'
);

-- CORRECT - Valid filter object
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'DOCS.SEARCH.research_reports_service',
    '{
        "query": "test",
        "filter": {"access_tier": "public"}  -- RIGHT: filter is object
    }'
);
```

### Error: "Warehouse required" or "No active warehouse"

**Cause:** No warehouse set or role lacks USAGE on warehouse

**Solutions:**
```sql
-- 1. Set warehouse for session
USE WAREHOUSE COMPUTE_WH;

-- 2. Grant warehouse access to role
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE agent_runner;

-- 3. Verify warehouse is running
SHOW WAREHOUSES LIKE 'COMPUTE_WH';

-- 4. Resume warehouse if suspended
ALTER WAREHOUSE COMPUTE_WH RESUME;
```

## Quick Compliance Checklist
- [ ] Documents cleaned/normalized; long docs chunked appropriately
      Verify: Check document lengths in source table - look for >4000 token docs that need chunking
- [ ] Metadata enriched (source, author, timestamp, access tier)
      Verify: `SELECT DISTINCT metadata_columns FROM source_table` - ensure all required fields populated
- [ ] Index validated: counts and sample retrievals correct
      Verify: `SHOW CORTEX SEARCH SERVICES;` then test retrieval with sample query
- [ ] Tool descriptions include clear document type and when-to-use guidance
      Verify: Review agent config - tool description should specify document corpus and use cases
- [ ] Tool use cases are distinct (no overlaps with other search tools)
      Verify: Compare tool descriptions across all search tools in agent config
- [ ] Citation requirements documented in agent response instructions
      Verify: Check agent response instructions include citation format and source attribution
- [ ] Component testing completed for search tools
      Verify: Test search tool independently with SEARCH_PREVIEW before agent integration
- [ ] Queries use metadata filters and tuned top_k
      Verify: Review query patterns - check for filter usage and appropriate top_k values
- [ ] Costs/latency monitored; stale docs pruned
      Verify: Query SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY for search service usage patterns

## Validation
- **Success checks:** Retrieval returns relevant, access-compliant results; evaluation metrics meet targets; tool descriptions are clear; component tests pass; citations properly formatted
- **Negative tests:** Queries without filters fail access checks; stale content removed from results after refresh; overlapping tool descriptions flagged in review

> **Investigation Required**  
> When applying this rule:
> 1. **Read existing search indices BEFORE creating new ones** - Check what indices exist, their structure, columns
> 2. **Verify data source** - Check tables/views for content quality, metadata availability
> 3. **Never assume index structure** - Query existing indices to understand schema
> 4. **Check embedding costs** - Review AI Observability for existing embedding usage patterns
> 5. **Test queries** - Validate search results before agent integration
>
> **Anti-Pattern:**
> "Creating Cortex Search index... (without checking existing indices)"
> "Indexing all columns... (without data quality check)"
>
> **Correct Pattern:**
> "Let me check your existing Cortex Search setup first."
> [reads existing indices, checks source data, reviews metadata columns]
> "I see you have doc_library indexed. Creating new index for product_docs following same metadata pattern..."

## Response Template
```sql
-- Prepare search-ready view with metadata (no SELECT *)
CREATE OR REPLACE VIEW <DB>.<SCHEMA>.docs_prepared AS
SELECT doc_id, chunk_id, content_clean, source, author, published_at, access_tier
FROM <DB>.<SCHEMA>.docs_chunked;

-- Example query with filters and tuned top_k
SELECT doc_id, chunk_id, score
FROM <DB>.<SCHEMA>.docs_index
WHERE QUERY = :query
  AND FILTERS = OBJECT_CONSTRUCT('access_tier', 'public')
ORDER BY score DESC
LIMIT 10;
```

```yaml
# Agent Search Tool Configuration
Tool Name: search_{document_type}
Type: Cortex Search
Service: <DB>.<SCHEMA>.<SERVICE>
ID Column: DOCUMENT_ID
Title Column: DOCUMENT_TITLE
Description: "Search {document_type} for {specific_use_case}. Use for questions about {when_to_use_guidance}."
```

## References

### External Documentation
- [Cortex Search Overview](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview) - Indexing and retrieval concepts
- [Snowflake Cortex AISQL](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql) - Embeddings via `AI_EMBED`
- [AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability) - Logging and evaluation
- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents) - Agent tool configuration

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **AISQL**: `114-snowflake-cortex-aisql.md`
- **Cortex Agents**: `115-snowflake-cortex-agents-core.md` - Agent archetypes, configuration templates, planning instructions, testing patterns
- **Cortex Analyst**: `117-snowflake-cortex-analyst.md` - Analyst tool configuration for hybrid agents
- **Cost Governance**: `105-snowflake-cost-governance.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
- **Observability**: `111-snowflake-observability-core.md`

## Related Rules

**Closely Related** (consider loading together):
- `115-snowflake-cortex-agents-core` - When using Cortex Search as an agent tool for document retrieval
- `114-snowflake-cortex-aisql` - For using AI_EMBED function to create embeddings

**Sometimes Related** (load if specific scenario):
- `117-snowflake-cortex-analyst` - When combining document search with quantitative analysis
- `108-snowflake-data-loading` - When loading documents into Snowflake for indexing
- `111-snowflake-observability-core` - When monitoring search service performance and costs

**Complementary** (different aspects of same domain):
- `107-snowflake-security-governance` - For access control on search services and documents
- `105-snowflake-cost-governance` - For monitoring search service and embedding costs
