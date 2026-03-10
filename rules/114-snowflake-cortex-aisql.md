# Snowflake Cortex AISQL Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:aisql, kw:cortex-aisql
**Keywords:** Cortex AISQL, AI_COMPLETE, AI_CLASSIFY, AI_EXTRACT, AI_SENTIMENT, AI_SUMMARIZE, embeddings, LLM functions, batching, token costs, text generation, classification, sentiment analysis, summarization, AI function error
**TokenBudget:** ~4900
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 105-snowflake-cost-governance.md

## Scope

**What This Rule Covers:**
Pragmatic, production-focused patterns for using Snowflake Cortex AISQL functions for classification, extraction, summarization, translation, embeddings, transcriptions, document parsing, and aggregation—optimized for cost, throughput, security, and governance.

**When to Load This Rule:**
- Using AISQL functions (`AI_COMPLETE`, `AI_CLASSIFY`, `AI_FILTER`, `AI_AGG`, `AI_SUMMARIZE_AGG`, `AI_EMBED`, `AI_EXTRACT`, `AI_SENTIMENT`, `AI_SIMILARITY`, `AI_TRANSCRIBE`, `AI_PARSE_DOCUMENT`, `AI_TRANSLATE`)
- Using helper functions (`PROMPT`, `AI_COUNT_TOKENS`, `TO_FILE`)
- SQL and Snowpark Python usage for AI functions
- Governance (CORTEX_USER role management)
- AI function observability

### Quantification Standards

**Performance Thresholds:**
- **High-throughput batch processing:** >1000 rows/minute OR batch processing >10K rows total (context: AISQL for large-scale inference)
- **Low-latency interactive needs:** <500ms response time required OR single-row/few-row queries (context: REST API for real-time inference)
- **Batching threshold:** Process ≥100 rows at once to amortize function call overhead
- **Token budget per query:** Aim for <4000 tokens per prompt (model context limits: 8K-128K depending on model)

> **Investigation Required**
> When applying this rule:
> 1. **Check SNOWFLAKE.CORTEX_USER grants BEFORE recommending** - Verify role privileges
> 2. **Read existing AI function usage** - Check QUERY_HISTORY for patterns
> 3. **Never speculate about model requirements** - Test with smallest model first
> 4. **Verify stage access** - Check stages and file permissions for TO_FILE usage
> 5. **Make grounded recommendations based on investigated usage** - Match existing patterns
>
> **Anti-Pattern:**
> "Based on typical AI usage, you probably need mistral-large..."
> "Let me add AI_COMPLETE - it should work..."
>
> **Correct Pattern:**
> "Let me check your Cortex usage first."
> [checks QUERY_HISTORY for AI functions, verifies CORTEX_USER grants]
> "I see you're using llama3.1-8b for classification. Here's how to add sentiment analysis with AI_SENTIMENT following the same model choice..."

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **105-snowflake-cost-governance.md** - Cost monitoring and optimization

**Related:**
- **114a-snowflake-cortex-ai-transcribe.md** - AI_TRANSCRIBE audio transcription patterns
- **102-snowflake-sql-core.md** - General SQL file patterns
- **106-snowflake-semantic-views-core.md** - Semantic views for Cortex Analyst
- **111-snowflake-observability-core.md** - Observability and tracing
- **112-snowflake-snowcli.md** - Snowflake CLI patterns
- **119-snowflake-warehouse-management.md** - Warehouse sizing and management

### External Documentation

- [Snowflake Cortex AISQL](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql) - Functions, privileges, cost, performance
- [Cortex AI Audio (AI_TRANSCRIBE)](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-audio) - Audio transcription, speaker diarization, timestamp extraction with TO_FILE syntax
- [AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability) - Evaluate, compare, and trace generative AI applications in Snowflake

## Contract

### Inputs and Prerequisites

- Snowflake account with required RBAC; `SNOWFLAKE.CORTEX_USER` privileges granted to intended roles (avoid PUBLIC if not desired)
- MEDIUM warehouse (4 credits/hr) with AUTO_SUSPEND = 60 for batch throughput
- Staged files where applicable (audio/images/documents) and stage privileges
- Model allowlists per org policy

### Mandatory

SQL AISQL functions; Snowpark Python; Snowflake CLI (`snow cortex` older-style); Snowsight; AI Observability

### Forbidden

- `SELECT *` in production queries
- Unbounded per-row LLM calls without batching or guardrails
- Storing sensitive content in prompts/logs without masking/tagging

### Execution Steps

1. Choose the smallest viable model (llama3.1-8b for classification/extraction; scale to 70b only if accuracy <90% on labeled samples) and enable caching/batching where applicable
2. Control tokens using `AI_COUNT_TOKENS` and concise prompts; prefer templates via `PROMPT`
3. Use `TO_FILE` for file references; store files in internal stages
4. Batch over tables using `AI_AGG` / `AI_SUMMARIZE_AGG` for cross-row context
5. Prefer AISQL for high-throughput batch processing (>1000 rows/min OR >10K rows total); prefer REST for low-latency interactive needs (<500ms response time required)
6. Enforce RBAC with `SNOWFLAKE.CORTEX_USER` and apply masking/row access policies to sensitive data
7. Track costs and performance; integrate with AI Observability where applicable

### Output Format

SQL/Snowpark examples with explicit columns and prompts

### Validation

**Pre-Task-Completion Checks:**
- SNOWFLAKE.CORTEX_USER grants verified
- Model selected (smallest viable model first)
- Token counts checked with AI_COUNT_TOKENS
- Batch strategy defined (AI_AGG/AI_SUMMARIZE_AGG)
- Files staged for TO_FILE references
- Explicit columns specified (no SELECT *)

**Success Criteria:**
- Query profile shows efficient scans
- Token counts within model limits
- Costs measured via QUERY_HISTORY
- Governance/privileges verified
- Examples run in dev with sample data/stages

**Negative Tests:**
- Excess token counts reject before execution
- Missing privileges raise authorization errors
- Governance policies enforce masking/row access

### Design Principles

- Choose the smallest sufficient model using this guidance:
  - Text classification/sentiment: `llama3.1-8b` (fastest, lowest cost)
  - Simple extraction/filtering: `llama3.1-8b` or `mistral-7b`
  - Summarization/complex extraction: `llama3.1-70b` or `mistral-large2`
  - Complex reasoning/multi-step: `llama3.1-70b` (test 8b first; scale up only if accuracy <90% on labeled samples)
- Batch inputs and push AISQL to process columns directly; avoid per-row chat loops
- Keep prompts short and specific; use `PROMPT` for dynamic parameterization
- Use `AI_COUNT_TOKENS` preflight for long inputs; truncate or segment when needed
- Use `AI_AGG`/`AI_SUMMARIZE_AGG` for multi-row aggregation to avoid context window limits
- Use internal stages and `TO_FILE` for images/audio/documents; avoid raw binary in-line
- Apply governance: restrict `SNOWFLAKE.CORTEX_USER`, revoke from PUBLIC as needed
- Measure and observe: record costs, latency, and output quality; add guard/filters

### Post-Execution Checklist

- [ ] `SNOWFLAKE.CORTEX_USER` restricted to least-privilege roles (not PUBLIC)
      Verify: `SHOW GRANTS TO DATABASE ROLE SNOWFLAKE.CORTEX_USER;` - check role membership
- [ ] Token budget verified with `AI_COUNT_TOKENS`; prompts concise and templated
      Verify: Run `SELECT AI_COUNT_TOKENS('<prompt>');` - should be under model limits
- [ ] Batch strategy in place; `AI_AGG` / `AI_SUMMARIZE_AGG` used for multi-row operations (>100 rows)
      Verify: Check query for batch processing - single AI call per batch, not per row
- [ ] Files referenced via `TO_FILE` from internal stages
      Verify: Check queries use `@stage/file` syntax, not external URLs
- [ ] Explicit columns only (no `SELECT *`); governance policies applied
      Verify: Review queries - no "SELECT *", all columns explicitly named
- [ ] Costs measured; warehouse auto-suspend configured; observability enabled
      Verify: Query QUERY_HISTORY for AI function costs - check AUTO_SUSPEND is set

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Unbounded Per-Row LLM Calls

**Problem:** Calling AI_COMPLETE or other LLM functions on every row in a large table without batching, limits, or cost controls.

**Why It Fails:** LLM calls are expensive (tokens cost credits). Processing 1M rows with AI_COMPLETE can consume thousands of dollars in credits in minutes. No automatic throttling exists—queries run until completion or timeout.

**Correct Pattern:**
```sql
-- BAD: Unbounded per-row calls
SELECT id, AI_COMPLETE('llama3.1-8b', description) AS summary
FROM products;  -- 500K rows = massive credit consumption

-- GOOD: Batch with limits and sampling for development
SELECT id, AI_COMPLETE('llama3.1-8b', description) AS summary
FROM products
WHERE needs_summary = TRUE
LIMIT 100;  -- Test on subset first

-- GOOD: Use AI_AGG for cross-row aggregation (single LLM call)
SELECT AI_AGG('llama3.1-8b',
  'Summarize these product descriptions',
  description) AS batch_summary
FROM products
WHERE category = 'electronics';
```

### Anti-Pattern 2: Using Large Models by Default

**Problem:** Defaulting to mistral-large or large models for all AI tasks without testing smaller models first.

**Why It Fails:** Larger models cost 10-50x more per token than smaller models. Most classification, extraction, and summarization tasks perform equally well with llama3.1-8b or mistral-7b. Starting large wastes credits without measurable quality improvement.

**Correct Pattern:**
```sql
-- BAD: Defaulting to expensive model
SELECT AI_CLASSIFY('mistral-large', feedback,
  ['positive', 'negative', 'neutral']) AS sentiment
FROM reviews;  -- Overkill for simple classification

-- GOOD: Start with smallest viable model
SELECT AI_CLASSIFY('llama3.1-8b', feedback,
  ['positive', 'negative', 'neutral']) AS sentiment
FROM reviews;

-- Scale up ONLY if accuracy is insufficient:
-- 1. Test llama3.1-8b on 1000 samples
-- 2. Measure accuracy against labeled data
-- 3. If <90% accuracy, try mistral-7b
-- 4. Only use large models for complex reasoning tasks
```

## Output Format Examples

```sql
-- Batch summarization pattern with token control and explicit columns
WITH src AS (
  SELECT id, LEFT(content, 4000) AS content
  FROM SRC_DB.RAW.MESSAGES
  WHERE created_at >= DATEADD(day, -1, CURRENT_DATE())
)
SELECT id, AI_SUMMARIZE_AGG(content) AS day_summary
FROM src;
```

## Privileges and Governance
- The `SNOWFLAKE.CORTEX_USER` database role permits use of Cortex AI functions. Revoke from `PUBLIC` and grant least privilege:
```sql
USE ROLE ACCOUNTADMIN;

REVOKE DATABASE ROLE SNOWFLAKE.CORTEX_USER FROM ROLE PUBLIC;
REVOKE IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE FROM ROLE PUBLIC;

CREATE ROLE cortex_user_role;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE cortex_user_role;
GRANT ROLE cortex_user_role TO USER some_user;
```

## Token and Cost Control
- Preflight with `AI_COUNT_TOKENS` and cap output tokens via function options (where supported):
```sql
SELECT AI_COUNT_TOKENS('llama3.1-8b', 'Summarize this: ' || LEFT(long_text, 2000)) AS tokens
FROM SRC_DB.RAW.ARTICLES;
```

## Batch-friendly Patterns

Process in batches of 10,000 rows per query. For tables >1M rows, use a TASK with LIMIT/OFFSET pagination to avoid warehouse timeouts and control credit consumption.

```sql
-- TASK-based pagination for >1M rows
CREATE OR REPLACE TASK ai_batch_process
  WAREHOUSE = AI_WH
  SCHEDULE = '1 MINUTE'
  ALLOW_OVERLAPPING_EXECUTION = FALSE
AS
  INSERT INTO results_table
  SELECT id, AI_CLASSIFY('llama3.1-8b', text_col, ['pos','neg','neutral']) AS label
  FROM source_table
  WHERE id > (SELECT COALESCE(MAX(id), 0) FROM results_table)
  ORDER BY id
  LIMIT 10000;
-- Resume task: ALTER TASK ai_batch_process RESUME;
-- Monitor: SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY()) WHERE NAME='AI_BATCH_PROCESS';
```

### 3.1 Summarize across many rows
```sql
SELECT AI_SUMMARIZE_AGG(abstract_text) AS abstract_summary
FROM SRC_DB.RAW.ARTICLES
WHERE PUBLISHED_AT >= DATEADD(day, -7, CURRENT_DATE());
```

### 3.2 Aggregate insights across rows
```sql
SELECT AI_AGG(abstract_text, 'List top 5 themes with brief evidence') AS top_themes
FROM SRC_DB.RAW.ARTICLES
WHERE CATEGORY = 'science';
```

## Row-level Tasks (use explicit columns)
### 4.1 Classification
```sql
SELECT
  id,
  AI_CLASSIFY(text, ARRAY_CONSTRUCT('travel','cooking','finance')) AS classification
FROM SRC_DB.RAW.POSTS;
```

### 4.2 Conditional filtering in SQL
```sql
SELECT country
FROM SRC_DB.REF.COUNTRIES
QUALIFY AI_FILTER(PROMPT('Is {0} in Asia?', country)) = TRUE;
```

### 4.3 Extraction
```sql
SELECT id,
       AI_EXTRACT(text, 'Return all person names and company names as JSON.') AS entities
FROM SRC_DB.RAW.DOCS;
```

### 4.4 Summarization (Single Text)
```sql
-- Summarize individual documents or conversations
SELECT
    conversation_id,
    AI_SUMMARIZE(full_transcript) AS summary
FROM SRC_DB.RAW.CALL_TRANSCRIPTS
WHERE call_date = CURRENT_DATE();
```

### 4.5 Sentiment Analysis (CRITICAL: Returns JSON, Not Numeric)

**CORRECT Pattern - Extract categorical sentiment from JSON:**

```sql
-- AI_SENTIMENT returns JSON with categorical values
WITH transcribed AS (
    SELECT
        call_id,
        transcript_text
    FROM SRC_DB.RAW.CALL_TRANSCRIPTS
)
SELECT
    call_id,
    -- AI_SENTIMENT with explicit category
    AI_SENTIMENT(transcript_text, ['overall']) AS sentiment_json,

    -- Extract categorical sentiment value
    sentiment_json:categories[0]:sentiment::VARCHAR AS sentiment,

    -- Sentiment values: 'positive', 'negative', 'neutral', 'unknown'
    CASE
        WHEN sentiment_json:categories[0]:sentiment::VARCHAR = 'negative'
        THEN 'Escalate'
        ELSE 'Standard'
    END AS routing_priority
FROM transcribed;
```

**INCORRECT Pattern - Treating as numeric score:**

```sql
-- WRONG: Expecting numeric sentiment score
SELECT AI_SENTIMENT(text) AS sentiment_score
WHERE sentiment_score >= 0.3;
-- Error: Can not convert parameter '0.3' into expected type [OBJECT]
```

**Why This Matters:**
- AI_SENTIMENT returns JSON object: `{"categories": [{"name": "overall", "sentiment": "positive"}]}`
- Sentiment values are categorical strings: 'positive', 'negative', 'neutral', 'unknown'
- Must extract using: `sentiment_json:categories[0]:sentiment::VARCHAR`
- Cannot compare directly with numeric values (causes type mismatch errors)

**Multiple Categories Example:**

```sql
-- Analyze sentiment across multiple dimensions
SELECT
    call_id,
    AI_SENTIMENT(transcript, ['overall', 'agent_performance', 'resolution']) AS sentiment_json,
    sentiment_json:categories[0]:sentiment::VARCHAR AS overall_sentiment,
    sentiment_json:categories[1]:sentiment::VARCHAR AS agent_sentiment,
    sentiment_json:categories[2]:sentiment::VARCHAR AS resolution_sentiment
FROM SRC_DB.RAW.CALL_TRANSCRIPTS;
```

## Embeddings & Similarity
```sql
-- Create embeddings for search/cluster/classify
CREATE OR REPLACE TABLE WORK.EMB AS
SELECT id, AI_EMBED(text) AS embedding
FROM SRC_DB.RAW.DOCS;

-- Similarity score between two inputs
SELECT AI_SIMILARITY(AI_EMBED('snowflake cortex'), AI_EMBED('enterprise llm platform')) AS sim;
```

## Files: Images, Audio, and Documents

### Audio Transcription (AI_TRANSCRIBE)

For complete AI_TRANSCRIBE patterns including TO_FILE syntax, speaker diarization, and common type errors, see **114a-snowflake-cortex-ai-transcribe.md**.

**Quick Reference - CRITICAL:** AI_TRANSCRIBE requires `TO_FILE('@stage', 'path')` with two arguments. Do NOT use GET_PRESIGNED_URL or BUILD_SCOPED_FILE_URL (they return VARCHAR, not FILE type).

### Other File Functions (Images, Documents)

```sql
-- Reference staged files for multimodal tasks
SELECT
  AI_COMPLETE('Describe this image in 20 words',
              TO_FILE('@INT_DB.STAGE.IMAGES', 'cat.png')) AS img_desc,
  AI_PARSE_DOCUMENT(
              TO_FILE('@INT_DB.STAGE.DOCS', 'form.pdf'), 'LAYOUT') AS parsed
FROM (SELECT 1);  -- Dummy table for demonstration
```

## Snowpark Python Examples
```python
from snowflake.snowpark.functions import ai_classify, ai_filter, prompt, col

df = session.create_dataframe([
    ["I dream of backpacking across South America."],
    ["I made the best pasta yesterday."],
], schema=["sentence"])

classified = df.select(
    col("sentence"),
    ai_classify(col("sentence"), ["travel", "cooking"]).alias("classification")
)

filtered = classified.select(
    col("sentence"),
    ai_filter(prompt("Is {0} about food?", col("sentence"))).alias("is_food")
)
```

## Performance and Warehouse Sizing
- AISQL functions are optimized for throughput -- batch workloads perform best.
- Use `llama3.1-8b` when p95 latency must be <2s; use `llama3.1-70b` when accuracy is critical and latency up to 10s is acceptable.
- Start with a MEDIUM warehouse (4 credits/hr) with AUTO_SUSPEND = 60. Scale to LARGE only if query queue time exceeds 30 seconds consistently.
- Prefer `AI_AGG`/`AI_SUMMARIZE_AGG` to bypass context window limits for multi-row summaries.
- **Timeout/Retry:** If an AI function returns NULL due to a transient LLM timeout, retry with a smaller LIMIT or a smaller model. For batch jobs, wrap in a TASK with automatic retry on failure.

## Security & Data Handling
- Avoid including secrets or PII in prompts. Apply masking/row access policies per `107-snowflake-security-governance.md`.
- Use internal stages; avoid externalizing sensitive content. Tag resources for lineage/cost tracking.

## Observability

- Set warehouse AUTO_SUSPEND to 60 seconds for AI workloads. Monitor AI service credit consumption:
```sql
SELECT
  DATE_TRUNC('day', START_TIME) AS day,
  SUM(CREDITS_USED) AS daily_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
WHERE SERVICE_TYPE = 'AI_SERVICES'
  AND START_TIME >= DATEADD(day, -7, CURRENT_DATE())
GROUP BY day
ORDER BY day;
```
- Alert when daily AI spend exceeds $50 (adjust threshold to your budget). Create a resource monitor or task-based check.
- Use Snowflake AI Observability to trace and evaluate LLM workflows and compare variants.

## NULL Handling for AI Functions

AI functions can return NULL on processing failures (empty input, model timeout, content policy violations). Always wrap AI function calls with NULL handling:

```sql
-- Classification with NULL fallback
SELECT id,
  COALESCE(AI_CLASSIFY(text, ['positive', 'negative', 'neutral']), 'UNKNOWN') AS sentiment
FROM reviews
WHERE text IS NOT NULL AND LENGTH(text) > 0;

-- Extraction with NULL check
SELECT id,
  CASE
    WHEN AI_EXTRACT(text, 'Extract person names as JSON') IS NULL THEN '{"names": []}'
    ELSE AI_EXTRACT(text, 'Extract person names as JSON')
  END AS entities
FROM documents;

-- Summarization with input validation
SELECT id,
  AI_SUMMARIZE(NULLIF(TRIM(content), '')) AS summary
FROM articles
WHERE content IS NOT NULL AND AI_COUNT_TOKENS('llama3.1-8b', content) > 10;
```

## Model Availability and Error Handling

Not all models support all functions. If you get `Function not supported for model` error, verify the model-function combination with `SHOW CORTEX MODELS` and check the Snowflake Cortex AI function-model compatibility matrix in the documentation. Common incompatibilities: embedding models cannot do classification; small models may not support AI_AGG.

```sql
-- Check available models before use
SHOW CORTEX MODELS;

-- In stored procedures, handle model unavailability
CREATE OR REPLACE PROCEDURE classify_batch(model_name VARCHAR)
RETURNS VARCHAR
LANGUAGE SQL
AS
BEGIN
  BEGIN
    EXECUTE IMMEDIATE 'SELECT AI_CLASSIFY(''' || :model_name || ''', ''test'', [''a'',''b''])';
  EXCEPTION
    WHEN OTHER THEN
      -- Fall back to alternative model
      model_name := 'llama3.1-8b';
  END;

  EXECUTE IMMEDIATE '
    INSERT INTO results
    SELECT id, AI_CLASSIFY(''' || :model_name || ''', text, [''positive'',''negative'',''neutral''])
    FROM source_data WHERE processed = FALSE LIMIT 1000';

  RETURN 'Completed with model: ' || :model_name;
END;
```

**Cost estimation before batch operations:**

```sql
-- Estimate token cost before running batch
SELECT
  COUNT(*) AS row_count,
  SUM(AI_COUNT_TOKENS('llama3.1-8b', LEFT(content, 4000))) AS total_input_tokens,
  total_input_tokens / 1000000 * 0.15 AS estimated_credits  -- Approximate
FROM source_data
WHERE needs_processing = TRUE;
```
