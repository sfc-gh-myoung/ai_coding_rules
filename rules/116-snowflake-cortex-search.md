# Snowflake Cortex Search Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:search, kw:cortex-search
**Keywords:** embeddings, search index, RAG, agent tools, retrieval, AI_EMBED, search service, document retrieval, hybrid search, vector similarity
**TokenBudget:** ~3100
**ContextTier:** Medium
**Depends:** 100-snowflake-core.md, 105-snowflake-cost-governance.md, 114-snowflake-cortex-aisql.md

## Scope

**What This Rule Covers:**
Patterns for building and querying Cortex Search indices: data preparation, embedding hygiene, metadata filters, agent tool configuration, and cost/latency optimization.

**When to Load:**
- Creating Cortex Search indices
- Querying search services with metadata filters
- Integrating Cortex Search as agent tools
- Troubleshooting search service errors

> **STOP Gate - Prerequisites Check:**
> Before creating Cortex Search services, verify ALL conditions:
> - [ ] Source table exists with non-zero rows
> - [ ] Search column contains text data
> - [ ] Metadata columns exist if using filters
> - [ ] User has CREATE CORTEX SEARCH SERVICE privilege
> - [ ] Warehouse is sized appropriately (MEDIUM+ for large indices)
>
> IF ANY condition fails, STOP and report to user.

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake SQL and warehouse fundamentals
- **114-snowflake-cortex-aisql.md** - AI_EMBED function for embeddings

**Related:**
- **115-snowflake-cortex-agents-core.md** - Agent archetypes
- **106c-snowflake-semantic-views-integration.md** - Analyst tool configuration

### External Documentation
- [Cortex Search Overview](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview)
- [Snowflake Cortex AISQL](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql)

## Contract

### Inputs and Prerequisites
- Cleaned source data with explicit columns; minimal sensitive content
- RBAC and tagging for index/table access
- Warehouse for index creation and queries

### Mandatory
- SQL (Cortex Search DDL), Snowpark Python, AISQL embeddings, AI Observability

### Forbidden
- Indexing raw PII without masking
- Long documents without chunking (>4000 tokens)
- Missing metadata columns (prevents filtering)
- Vague tool descriptions in agent configuration

### Execution Steps
1. **Data Prep:** Normalize/clean data; chunk long docs (500-1000 tokens) with overlap
2. **Metadata Enrichment:** Attach metadata (source, author, timestamp, access tier)
3. **Index Creation:** Create search service; validate document counts
4. **Validation:** Test sample queries and filters; verify retrieval quality
5. **Tool Config:** Configure tools with clear descriptions and when-to-use guidance
6. **Monitoring:** Monitor costs/latency; prune stale content

### Output Format
```sql
CREATE CORTEX SEARCH SERVICE {DB}.{SCHEMA}.{SERVICE}
ON {SEARCH_COLUMN}
ATTRIBUTES {METADATA_COLUMNS}
WAREHOUSE = {WH}
AS (SELECT * FROM {SOURCE_VIEW});
```

### Validation
**Pre-Task-Completion Checks:** Source data cleaned, metadata populated, service status = READY, sample queries return relevant results

**Success Criteria:** Index contains expected document count, retrieval validated, costs within budget

### Design Principles
- **High-Quality Retrieval:** Clean text, consistent chunking, rich metadata
- **Metadata-Driven Filtering:** Use filters to enforce RBAC-like scoping
- **Clear Tool Descriptions:** Include document type and when-to-use guidance
- **Regular Maintenance:** Rebuild indices; remove stale content

### Post-Execution Checklist
- [ ] Documents chunked appropriately (500-1000 tokens)
- [ ] Metadata enriched (source, author, timestamp, access tier)
- [ ] Search service created and status verified (READY)
- [ ] Sample queries return relevant results
- [ ] Tool descriptions include document type and when-to-use guidance

## Anti-Patterns and Common Mistakes

### SEARCH vs SEARCH_PREVIEW

- **`SEARCH_PREVIEW`:** Use for testing and validation — returns results directly in SQL with no agent context needed
- **`SEARCH` (via Cortex Agent tools):** Used by agents at runtime for RAG — requires a Cortex Agent with a search tool configured
- **Rule:** Always validate with `SEARCH_PREVIEW` before wiring into an agent

### Python SDK Example

```python
from snowflake.core import Root

root = Root(session)
search_service = root.databases["DB"].schemas["SCHEMA"].cortex_search_services["MY_SERVICE"]
results = search_service.search(query="revenue trends", columns=["chunk_text", "source"], limit=5)
for r in results.results:
    print(r["chunk_text"])
```

### Index Rebuild for Stale Content

- **Rule:** If search results are stale after source data changes, force a refresh:
  ```sql
  ALTER CORTEX SEARCH SERVICE db.schema.docs_search SUSPEND;
  ALTER CORTEX SEARCH SERVICE db.schema.docs_search RESUME;
  -- This triggers a full re-index from the source query
  ```

### Anti-Pattern 1: Not Chunking Long Documents
```sql
-- Bad: 50,000 token document
CREATE CORTEX SEARCH SERVICE docs_search ON full_document_text ...
```
**Problem:** Poor retrieval quality; semantic search ineffective.

**Correct Pattern:**
```sql
CREATE OR REPLACE VIEW chunked_documents AS
SELECT doc_id, SUBSTR(full_text, (chunk_num * 1000) + 1, 1000) as chunk_text
FROM docs CROSS JOIN TABLE(GENERATOR(ROWCOUNT => 100))
WHERE LENGTH(full_text) > chunk_num * 1000;

CREATE CORTEX SEARCH SERVICE docs_search ON chunk_text ...
```

### Anti-Pattern 2: Missing Metadata for Filtering
```sql
-- Bad: No metadata
CREATE CORTEX SEARCH SERVICE product_docs ON content AS (SELECT doc_id, content FROM docs);
```
**Problem:** No filtering capability; irrelevant results; security gaps.

**Correct Pattern:**
```sql
CREATE CORTEX SEARCH SERVICE product_docs ON content
ATTRIBUTES metadata
AS (SELECT doc_id, content, OBJECT_CONSTRUCT('source', source, 'access_tier', tier) as metadata FROM docs);
```

### Anti-Pattern 3: Vague Tool Descriptions
```python
# Bad
tools = [{"name": "search_docs", "description": "Search documents"}]
```
**Problem:** Agent doesn't know when to use tool.

**Correct Pattern:**
```python
tools = [{"name": "product_api_docs_search",
          "description": "Search product API documentation: endpoints, auth, code examples. Use for technical API questions. NOT for: billing, account management."}]
```

### Anti-Pattern 4: No Post-Creation Validation
**Problem:** Silent failures; production issues.

**Correct Pattern:**
```sql
SHOW CORTEX SEARCH SERVICES LIKE 'docs_search';  -- Verify READY
DESC CORTEX SEARCH SERVICE db.schema.docs_search;  -- Check row count
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW('service', '{"query": "test", "limit": 5}');  -- Test retrieval
```

## Implementation Details

### Document Chunking Strategy

Split long documents into 500-1000 token chunks with 10-20% overlap for optimal retrieval:

```sql
-- Chunk documents before indexing for better retrieval quality
-- Use a chunking UDF or view that splits text at paragraph boundaries
CREATE OR REPLACE VIEW chunked_documents AS
SELECT
  doc_id,
  chunk_index,
  chunk_text,
  source,
  author,
  published_at
FROM raw.documents,
  LATERAL FLATTEN(input => SPLIT_TO_TABLE(full_text, '\n\n')) chunks
WHERE LENGTH(chunks.value::STRING) > 50;

CREATE CORTEX SEARCH SERVICE docs_search
ON chunk_text
ATTRIBUTES doc_id, source, author
WAREHOUSE = COMPUTE_WH
TARGET_LAG = '1 day'
AS (SELECT * FROM chunked_documents);
```

### PII Handling in Search Content

Apply masking or redaction to PII columns before creating search services. Search results bypass row access policies. Use projection policies on sensitive columns or pre-filter PII from source views before indexing.

### Creating Search Services
```sql
CREATE OR REPLACE VIEW docs_ready AS
SELECT doc_id, content_clean, source, author, published_at, access_tier
FROM raw.docs_chunked WHERE content_clean IS NOT NULL AND LENGTH(content_clean) > 50;

CREATE CORTEX SEARCH SERVICE IF NOT EXISTS DOCS.SEARCH.reports_service
ON content_clean
ATTRIBUTES doc_id, source, author, published_at, access_tier
WAREHOUSE = COMPUTE_WH
TARGET_LAG = '1 day'
AS (SELECT * FROM docs_ready);

-- Verify and grant access
SHOW CORTEX SEARCH SERVICES IN SCHEMA DOCS.SEARCH;
GRANT USAGE ON CORTEX SEARCH SERVICE DOCS.SEARCH.reports_service TO ROLE agent_runner;
```

### Querying Search Services
```sql
-- Basic query
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW('DOCS.SEARCH.reports_service',
    '{"query": "warehouse performance", "limit": 10}');

-- With metadata filters
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW('DOCS.SEARCH.reports_service',
    '{"query": "strategy", "limit": 10, "filter": {"access_tier": "public", "source": "Goldman Sachs"}}');

-- Parse results
WITH search AS (
    SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW('service', '{"query": "ESG", "limit": 10}') AS results
)
SELECT r.value:doc_id::STRING, r.value:score::FLOAT, r.value:content::STRING
FROM search, LATERAL FLATTEN(input => results:results) r ORDER BY 2 DESC;
```

### Agent Tool Configuration
```yaml
Tool Name: search_research_reports
Type: Cortex Search
Service: DOCS.SEARCH.REPORTS_SERVICE
Description: "Search investment research reports for analyst opinions, ratings, price targets. Use for questions about analyst views and recommendations."
```

**Best Practices:**
- Explicit document type and use cases
- When-to-use guidance with trigger words
- Distinct tools (avoid overlapping descriptions)

### Citation Requirements
```yaml
Response Instructions: |
  Always cite sources with: Document type, title/identifier, date.
  Format: "According to {type} '{title}' from {date}..."
```

## Common Errors and Solutions

### "Service not found"
```sql
SHOW CORTEX SEARCH SERVICES IN SCHEMA {DB}.{SCHEMA};
GRANT USAGE ON CORTEX SEARCH SERVICE {service} TO ROLE {role};
```

### "No results returned"
```sql
DESC CORTEX SEARCH SERVICE {service};  -- Check row count
SELECT COUNT(*) FROM {source_view};  -- Verify source data
-- Test with no filters first, then add incrementally
```

### "Invalid filter syntax"
```sql
-- WRONG: single quotes around keys
"{'query': 'test'}"
-- CORRECT: double quotes
'{"query": "test", "filter": {"access_tier": "public"}}'
```

### "No active warehouse"
```sql
USE WAREHOUSE COMPUTE_WH;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE agent_runner;
```

## Search Service Lifecycle Management

```sql
-- Refresh a search service (rebuild index from source data)
ALTER CORTEX SEARCH SERVICE db.schema.docs_search RESUME;

-- Suspend a search service (stop refresh, retain index)
ALTER CORTEX SEARCH SERVICE db.schema.docs_search SUSPEND;

-- Change target lag for refresh frequency
ALTER CORTEX SEARCH SERVICE db.schema.docs_search SET TARGET_LAG = '1 hour';

-- Change the warehouse used for refresh
ALTER CORTEX SEARCH SERVICE db.schema.docs_search SET WAREHOUSE = LARGER_WH;

-- Drop a search service permanently
DROP CORTEX SEARCH SERVICE IF EXISTS db.schema.docs_search;

-- List all search services
SHOW CORTEX SEARCH SERVICES IN SCHEMA db.schema;

-- Describe a specific service (row count, columns, status)
DESC CORTEX SEARCH SERVICE db.schema.docs_search;
```

## Search Quality Tuning

**Adjusting result quality:**

- **max_results:** Start with 5-10 for agent tools; use 20-50 for comprehensive retrieval
- **filter expressions:** Use metadata filters to narrow scope before semantic matching
- **Score thresholds:** Post-filter results by score to remove low-relevance matches

```sql
-- Tuned query with score filtering
WITH search AS (
    SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW('DOCS.SEARCH.reports_service',
        '{"query": "quarterly earnings", "limit": 20, "filter": {"source": "SEC"}}') AS results
)
SELECT r.value:doc_id::STRING AS doc_id,
       r.value:score::FLOAT AS score,
       r.value:content::STRING AS content
FROM search, LATERAL FLATTEN(input => results:results) r
WHERE r.value:score::FLOAT > 0.5  -- Filter low-relevance results
ORDER BY score DESC
LIMIT 10;
```

## Cost and Performance Guidance

- **Warehouse sizing:** Use MEDIUM+ for initial index creation on large datasets (>1M docs). SMALL is sufficient for queries.
- **TARGET_LAG:** Use '1 day' for static content; '1 hour' for frequently updated data. Shorter lags increase credit consumption.
- **Credit consumption:** Index creation is the main cost driver. Queries are lightweight. Monitor with:

```sql
SELECT query_type, COUNT(*) AS query_count, SUM(credits_used_cloud_services) AS credits
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE query_type LIKE '%SEARCH%'
  AND start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY query_type;
```

- **Large document sets:** Chunk documents to 500-1000 tokens. Use metadata filters to reduce search scope. Consider separate services per document category for better relevance.
