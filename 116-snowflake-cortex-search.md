**Description:** Best practices for Snowflake Cortex Search: indexing, embeddings, filters, hybrid retrieval, and query patterns with governance and observability.
**AppliesTo:** `**/*.sql`, `**/*.py`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-10-03

# Snowflake Cortex Search Best Practices

## Purpose
Provide reliable patterns for building and querying Cortex Search indices, including data preparation, embedding hygiene, metadata filters, hybrid retrieval, and cost/latency considerations.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Cortex Search indexing and querying; embedding creation; metadata and security filters; observability and cost control

## Contract
- **Inputs/Prereqs:**
  - Cleaned source data with explicit columns; minimal sensitive content
  - Embeddings available via `AI_EMBED` or created during indexing
  - RBAC and tagging for index/table access
- **Allowed Tools:** SQL (Cortex Search), Snowpark Python, AISQL embeddings, AI Observability
- **Forbidden Tools:**
  - Indexing raw PII without masking/tagging
  - Overly long documents without chunking/normalization
- **Required Steps:**
  1. Normalize/clean data; remove boilerplate; chunk long documents with overlap
  2. Attach metadata (source, author, timestamp, access tier) for filtering
  3. Create or refresh indices; validate document counts and sample retrieval
  4. Query with metadata filters; tune top_k and hybrid weights
  5. Monitor costs/latency; prune outdated content
- **Output Format:** SQL patterns for indexing and querying; Snowpark examples
- **Validation Steps:** Index contains expected docs; retrieval quality validated; filters enforce access; costs within budget

## Key Principles
- High-quality retrieval requires clean text, consistent chunking, and rich metadata
- Use metadata filters to enforce RBAC-like scoping; never rely on client-side filtering only
- Periodically rebuild or refresh indices; remove stale/duplicative content
- Evaluate retrieval with gold queries and measure relevance

## 1. Data Preparation
- Lowercase, strip boilerplate, normalize whitespace; remove navigation/UI fragments
- Chunk long docs (e.g., 500–1000 tokens) with overlap ~10–15%

## 2. Indexing Pattern (sketch)
```sql
-- Example sketch: prepare a search-ready view with metadata
CREATE OR REPLACE VIEW APP.SEARCH.docs_prepared AS
SELECT 
  doc_id,
  chunk_id,
  content_clean,
  source,
  author,
  published_at,
  access_tier
FROM APP.RAW.docs_chunked;
```

## 3. Embedding Hygiene
- If embedding externally, store vectors in a dedicated column; ensure consistent model/version
- Consider re-embedding only when content or model materially changes

## 4. Querying with Filters (sketch)
```sql
-- Pseudocode pattern; replace with the actual Cortex Search query syntax when executing
SELECT 
  doc_id,
  chunk_id,
  score,
  source
FROM APP.SEARCH.docs_index
WHERE QUERY = 'how to configure warehouses optimally'
  AND FILTERS = OBJECT_CONSTRUCT('access_tier','public')
ORDER BY score DESC
LIMIT 10;
```

## 5. Hybrid Retrieval
- Blend dense vector search with sparse/text signals when supported; tune weights empirically
- Keep top_k small initially (e.g., 10–20) and increase only if recall is insufficient

## 6. Evaluation and Observability
- Maintain a gold set of query→expected passage mappings; measure precision@k and MRR
- Use AI Observability to log search queries and downstream answer quality

## 7. Cost and Operations
- Limit index rebuilds; prefer incremental updates where supported
- Archive or delete stale content from indices; partition by recency/source if needed

## Quick Compliance Checklist
- [ ] Documents cleaned/normalized; long docs chunked appropriately
- [ ] Metadata enriched (source, author, timestamp, access tier)
- [ ] Index validated: counts and sample retrievals correct
- [ ] Queries use metadata filters and tuned top_k
- [ ] Costs/latency monitored; stale docs pruned

## Validation
- **Success checks:** Retrieval returns relevant, access-compliant results; evaluation metrics meet targets
- **Negative tests:** Queries without filters fail access checks; stale content removed from results after refresh

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

## References

### External Documentation
- [Cortex Search Overview](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview) - Indexing and retrieval concepts
- [Snowflake Cortex AISQL](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql) - Embeddings via `AI_EMBED`
- [AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability)

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **AISQL**: `114-snowflake-cortex-aisql.md`
- **Cost Governance**: `105-snowflake-cost-governance.md`
- **Observability**: `111-snowflake-observability.md`


