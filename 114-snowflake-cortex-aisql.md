**Description:** Best practices for Snowflake Cortex AISQL functions with cost, performance, security, and observability guidance, including SQL and Snowpark Python examples.
**AppliesTo:** `**/*.sql`, `**/*.py`
**AutoAttach:** false
**Type:** Agent Requested
**Keywords:** Cortex AISQL, AI_COMPLETE, AI_CLASSIFY, AI_EXTRACT, AI_SENTIMENT, AI_TRANSCRIBE, TO_FILE, embeddings, LLM functions, batching AI, token costs, audio transcription
**Version:** 1.2
**LastUpdated:** 2025-10-15

**TokenBudget:** ~500
**ContextTier:** Medium

# Snowflake Cortex AISQL Best Practices

## Purpose
Provide pragmatic, production-focused patterns for using Snowflake Cortex AISQL functions for classification, extraction, summarization, translation, embeddings, transcriptions, document parsing, and aggregation—optimized for cost, throughput, security, and governance.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** AISQL functions (`AI_COMPLETE`, `AI_CLASSIFY`, `AI_FILTER`, `AI_AGG`, `AI_SUMMARIZE_AGG`, `AI_EMBED`, `AI_EXTRACT`, `AI_SENTIMENT`, `AI_SIMILARITY`, `AI_TRANSCRIBE`, `AI_PARSE_DOCUMENT`, `AI_TRANSLATE`) and helper functions (`PROMPT`, `AI_COUNT_TOKENS`, `TO_FILE`), SQL and Snowpark Python usage, governance (CORTEX_USER), and observability.

## Contract
- **Inputs/Prereqs:**
  - Snowflake account with required RBAC; `SNOWFLAKE.CORTEX_USER` privileges granted to intended roles (avoid PUBLIC if not desired)
  - Appropriate warehouses sized for batch throughput with auto-suspend
  - Staged files where applicable (audio/images/documents) and stage privileges
  - Model allowlists per org policy
- **Allowed Tools:** SQL AISQL functions; Snowpark Python; Snowflake CLI (`snow cortex` older-style); Snowsight; AI Observability
- **Forbidden Tools:**
  - `SELECT *` in production queries
  - Unbounded per-row LLM calls without batching or guardrails
  - Storing sensitive content in prompts/logs without masking/tagging
- **Required Steps:**
  1. Choose the smallest viable model and enable caching/batching where applicable
  2. Control tokens using `AI_COUNT_TOKENS` and concise prompts; prefer templates via `PROMPT`
  3. Use `TO_FILE` for file references; store files in internal stages
  4. Batch over tables using `AI_AGG` / `AI_SUMMARIZE_AGG` for cross-row context
  5. Prefer AISQL for high-throughput batch processing; prefer REST for low-latency interactive needs
  6. Enforce RBAC with `SNOWFLAKE.CORTEX_USER` and apply masking/row access policies to sensitive data
  7. Track costs and performance; integrate with AI Observability where applicable
- **Output Format:** SQL/Snowpark examples with explicit columns and prompts
- **Validation Steps:** Query profile shows efficient scans; token counts within model limits; costs measured; governance/privileges verified; examples run in dev with sample data/stages

## Key Principles
- Choose the smallest sufficient model; scale only when quality demands it
- Batch inputs and push AISQL to process columns directly; avoid per-row chat loops
- Keep prompts short and specific; use `PROMPT` for dynamic parameterization
- Use `AI_COUNT_TOKENS` preflight for long inputs; truncate or segment when needed
- Use `AI_AGG`/`AI_SUMMARIZE_AGG` for multi-row aggregation to avoid context window limits
- Use internal stages and `TO_FILE` for images/audio/documents; avoid raw binary in-line
- Apply governance: restrict `SNOWFLAKE.CORTEX_USER`, revoke from PUBLIC as needed
- Measure and observe: record costs, latency, and output quality; add guard/filters

## 1. Privileges and Governance
- The `SNOWFLAKE.CORTEX_USER` database role permits use of Cortex AI functions. Revoke from `PUBLIC` and grant least privilege:
```sql
USE ROLE ACCOUNTADMIN;

REVOKE DATABASE ROLE SNOWFLAKE.CORTEX_USER FROM ROLE PUBLIC;
REVOKE IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE FROM ROLE PUBLIC;

CREATE ROLE cortex_user_role;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE cortex_user_role;
GRANT ROLE cortex_user_role TO USER some_user;
```

## 2. Token and Cost Control
- Preflight with `AI_COUNT_TOKENS` and cap output tokens via function options (where supported):
```sql
SELECT AI_COUNT_TOKENS('llama3.1-8b', 'Summarize this: ' || LEFT(long_text, 2000)) AS tokens
FROM SRC_DB.RAW.ARTICLES;
```

## 3. Batch-friendly Patterns
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

## 4. Row-level Tasks (use explicit columns)
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

## 5. Embeddings & Similarity
```sql
-- Create embeddings for search/cluster/classify
CREATE OR REPLACE TABLE WORK.EMB AS
SELECT id, AI_EMBED(text) AS embedding
FROM SRC_DB.RAW.DOCS;

-- Similarity score between two inputs
SELECT AI_SIMILARITY(AI_EMBED('snowflake cortex'), AI_EMBED('enterprise llm platform')) AS sim;
```

## 6. Files: Images, Audio, and Documents

### 6.1 AI_TRANSCRIBE - Audio Transcription (CRITICAL SYNTAX)

**✅ CORRECT Pattern - TO_FILE with two arguments:**

```sql
-- Pattern 1: Direct file reference (recommended)
SELECT 
    RELATIVE_PATH AS audio_file,
    AI_TRANSCRIBE(TO_FILE('@STAGE_NAME', RELATIVE_PATH)) AS transcription
FROM DIRECTORY('@STAGE_NAME')
WHERE RELATIVE_PATH LIKE '%.mp3';

-- Pattern 2: Inline stage and file path
SELECT AI_TRANSCRIBE(TO_FILE('@financial_consultation', 'consultation.wav')) AS transcript;
```

**❌ INCORRECT Patterns (will cause type errors):**

```sql
-- ❌ WRONG: Using GET_PRESIGNED_URL (returns VARCHAR, not FILE type)
SELECT AI_TRANSCRIBE(GET_PRESIGNED_URL('@stage', 'file.mp3'));
-- Error: Invalid argument types for function 'AI_TRANSCRIBE': (VARCHAR)

-- ❌ WRONG: Using BUILD_SCOPED_FILE_URL without TO_FILE wrapper
SELECT AI_TRANSCRIBE(BUILD_SCOPED_FILE_URL(@stage, path));
-- Error: Invalid argument types for function 'AI_TRANSCRIBE': (VARCHAR)

-- ❌ WRONG: Wrapping BUILD_SCOPED_FILE_URL result with TO_FILE (single arg)
SELECT AI_TRANSCRIBE(TO_FILE(BUILD_SCOPED_FILE_URL(@stage, path)));
-- Error: TO_FILE expects 2 arguments (stage, path), not 1
```

**Why TO_FILE('@stage', 'path') is Required:**
- `AI_TRANSCRIBE` expects a FILE reference type, not a VARCHAR string
- `TO_FILE()` takes **two separate arguments**: stage name and file path
- `GET_PRESIGNED_URL()` and `BUILD_SCOPED_FILE_URL()` return VARCHAR strings (HTTP URLs)
- Only `TO_FILE('@stage', 'path')` creates the proper FILE type

**Complete Working Example:**

```sql
-- Transcribe audio files from directory listing
WITH audio_files AS (
    SELECT RELATIVE_PATH
    FROM DIRECTORY('@UTILITY_DEMO.CUSTOMER_DATA.AUDIO_FILES')
    WHERE RELATIVE_PATH LIKE '%.mp3'
    LIMIT 10
)
SELECT 
    RELATIVE_PATH AS audio_file,
    AI_TRANSCRIBE(
        TO_FILE('@UTILITY_DEMO.CUSTOMER_DATA.AUDIO_FILES', RELATIVE_PATH)
    ) AS transcription_json,
    transcription_json:text::VARCHAR AS transcription_text,
    transcription_json:audio_duration::FLOAT AS duration_seconds
FROM audio_files;
```

### 6.2 Other File Functions (Images, Documents)

```sql
-- Reference staged files for multimodal tasks
SELECT 
  AI_COMPLETE('Describe this image in 20 words', 
              TO_FILE('@INT_DB.STAGE.IMAGES', 'cat.png')) AS img_desc,
  AI_PARSE_DOCUMENT(
              TO_FILE('@INT_DB.STAGE.DOCS', 'form.pdf'), 'LAYOUT') AS parsed
FROM (SELECT 1);  -- Dummy table for demonstration
```

## 7. Snowpark Python Examples
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

## 8. Performance and Warehouse Sizing
- AISQL functions are optimized for throughput—batch workloads perform best.
- Use modest warehouses with auto-suspend; scale up only if queueing is sustained.
- Prefer `AI_AGG`/`AI_SUMMARIZE_AGG` to bypass context window limits for multi-row summaries.

## 9. Security & Data Handling
- Avoid including secrets or PII in prompts. Apply masking/row access policies per `107-snowflake-security-governance.md`.
- Use internal stages; avoid externalizing sensitive content. Tag resources for lineage/cost tracking.

## 10. Observability
- Track credit consumption for AISQL workloads; evaluate output quality and latency.
- Use Snowflake AI Observability to trace and evaluate LLM workflows and compare variants.

## Quick Compliance Checklist
- [ ] `SNOWFLAKE.CORTEX_USER` restricted to least-privilege roles (not PUBLIC)
- [ ] Token budget verified with `AI_COUNT_TOKENS`; prompts concise and templated
- [ ] Batch strategy in place; `AI_AGG` / `AI_SUMMARIZE_AGG` used where appropriate
- [ ] Files referenced via `TO_FILE` from internal stages
- [ ] Explicit columns only (no `SELECT *`); governance policies applied
- [ ] Costs measured; warehouse auto-suspend configured; observability enabled

## Validation
- **Success checks:**
  - AISQL jobs complete within token limits; outputs are well-formed
  - Query profile shows efficient scans and minimal re-materialization
  - Costs align with expectations; observability captures traces/metrics
- **Negative tests:**
  - Excess token counts reject before execution; prompts truncated/segmented
  - Missing privileges raise authorization errors; governance policies enforced

## Response Template
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

## References

### External Documentation
- [Snowflake Cortex AISQL](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql) - Functions, privileges, cost, performance
- [Cortex AI Audio (AI_TRANSCRIBE)](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-audio) - Audio transcription, speaker diarization, timestamp extraction with TO_FILE syntax
- [AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability) - Evaluate, compare, and trace generative AI applications in Snowflake

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **SQL Best Practices**: `102-snowflake-sql-best-practices.md`
- **Cost Governance**: `105-snowflake-cost-governance.md`
- **Semantic Views**: `106-snowflake-semantic-views.md`
- **Observability**: `111-snowflake-observability.md`
- **Snowflake CLI**: `112-snowflake-snowcli.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`


