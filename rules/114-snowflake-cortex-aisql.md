# Snowflake Cortex AISQL Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Cortex AISQL, AI_COMPLETE, AI_CLASSIFY, AI_EXTRACT, AI_SENTIMENT, AI_SUMMARIZE, embeddings, LLM functions, batching, token costs, text generation, classification, sentiment analysis, summarization, AI function error
**TokenBudget:** ~3200
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md, rules/105-snowflake-cost-governance.md

## Purpose
Provide pragmatic, production-focused patterns for using Snowflake Cortex AISQL functions for classification, extraction, summarization, translation, embeddings, transcriptions, document parsing, and aggregation—optimized for cost, throughput, security, and governance.

## Rule Scope

AISQL functions (`AI_COMPLETE`, `AI_CLASSIFY`, `AI_FILTER`, `AI_AGG`, `AI_SUMMARIZE_AGG`, `AI_EMBED`, `AI_EXTRACT`, `AI_SENTIMENT`, `AI_SIMILARITY`, `AI_TRANSCRIBE`, `AI_PARSE_DOCUMENT`, `AI_TRANSLATE`) and helper functions (`PROMPT`, `AI_COUNT_TOKENS`, `TO_FILE`), SQL and Snowpark Python usage, governance (CORTEX_USER), and observability.

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Grant SNOWFLAKE.CORTEX_USER role** - Required for all Cortex AI functions
- **Choose smallest viable model** - Start with llama3.1-8b, scale only if needed
- **Use AI_COUNT_TOKENS preflight** - Verify input size before expensive operations
- **Batch with AI_AGG/AI_SUMMARIZE_AGG** - Aggregate across rows for context
- **Use TO_FILE for media** - Reference staged files, not inline binary
- **Keep prompts concise** - Use PROMPT function for templates
- **Never use SELECT * with AI functions** - Specify exact columns needed

**Quick Checklist:**
- [ ] GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER
- [ ] Choose model (llama3.1-8b for most tasks)
- [ ] AI_COUNT_TOKENS for input validation
- [ ] Use AI_AGG for multi-row aggregation
- [ ] Stage files and use TO_FILE references
- [ ] Track costs in QUERY_HISTORY
- [ ] Apply masking/row access to sensitive data

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

## Contract

<contract>
<inputs_prereqs>
- Snowflake account with required RBAC; `SNOWFLAKE.CORTEX_USER` privileges granted to intended roles (avoid PUBLIC if not desired)
- Appropriate warehouses sized for batch throughput with auto-suspend
- Staged files where applicable (audio/images/documents) and stage privileges
- Model allowlists per org policy
</inputs_prereqs>

<mandatory>
SQL AISQL functions; Snowpark Python; Snowflake CLI (`snow cortex` older-style); Snowsight; AI Observability
</mandatory>

<forbidden>
- `SELECT *` in production queries
- Unbounded per-row LLM calls without batching or guardrails
- Storing sensitive content in prompts/logs without masking/tagging
</forbidden>

<steps>
1. Choose the smallest viable model and enable caching/batching where applicable
2. Control tokens using `AI_COUNT_TOKENS` and concise prompts; prefer templates via `PROMPT`
3. Use `TO_FILE` for file references; store files in internal stages
4. Batch over tables using `AI_AGG` / `AI_SUMMARIZE_AGG` for cross-row context
5. Prefer AISQL for high-throughput batch processing; prefer REST for low-latency interactive needs
6. Enforce RBAC with `SNOWFLAKE.CORTEX_USER` and apply masking/row access policies to sensitive data
7. Track costs and performance; integrate with AI Observability where applicable
</steps>

<output_format>
SQL/Snowpark examples with explicit columns and prompts
</output_format>

<validation>
Query profile shows efficient scans; token counts within model limits; costs measured; governance/privileges verified; examples run in dev with sample data/stages
</validation>

<design_principles>
- Choose the smallest sufficient model; scale only when quality demands it
- Batch inputs and push AISQL to process columns directly; avoid per-row chat loops
- Keep prompts short and specific; use `PROMPT` for dynamic parameterization
- Use `AI_COUNT_TOKENS` preflight for long inputs; truncate or segment when needed
- Use `AI_AGG`/`AI_SUMMARIZE_AGG` for multi-row aggregation to avoid context window limits
- Use internal stages and `TO_FILE` for images/audio/documents; avoid raw binary in-line
- Apply governance: restrict `SNOWFLAKE.CORTEX_USER`, revoke from PUBLIC as needed
- Measure and observe: record costs, latency, and output quality; add guard/filters
</design_principles>

</contract>

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

**Problem:** Defaulting to mistral-large or claude-3-opus for all AI tasks without testing smaller models first.

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

## Post-Execution Checklist
- [ ] `SNOWFLAKE.CORTEX_USER` restricted to least-privilege roles (not PUBLIC)
      Verify: `SHOW GRANTS TO DATABASE ROLE SNOWFLAKE.CORTEX_USER;` - check role membership
- [ ] Token budget verified with `AI_COUNT_TOKENS`; prompts concise and templated
      Verify: Run `SELECT AI_COUNT_TOKENS('<prompt>');` - should be under model limits
- [ ] Batch strategy in place; `AI_AGG` / `AI_SUMMARIZE_AGG` used where appropriate
      Verify: Check query for batch processing - single AI call per batch, not per row
- [ ] Files referenced via `TO_FILE` from internal stages
      Verify: Check queries use `@stage/file` syntax, not external URLs
- [ ] Explicit columns only (no `SELECT *`); governance policies applied
      Verify: Review queries - no "SELECT *", all columns explicitly named
- [ ] Costs measured; warehouse auto-suspend configured; observability enabled
      Verify: Query QUERY_HISTORY for AI function costs - check AUTO_SUSPEND is set

## Validation
- **Success checks:**
  - AISQL jobs complete within token limits; outputs are well-formed
  - Query profile shows efficient scans and minimal re-materialization
  - Costs align with expectations; observability captures traces/metrics
- **Negative tests:**
  - Excess token counts reject before execution; prompts truncated/segmented
  - Missing privileges raise authorization errors; governance policies enforced

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

## References

### External Documentation
- [Snowflake Cortex AISQL](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql) - Functions, privileges, cost, performance
- [Cortex AI Audio (AI_TRANSCRIBE)](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-audio) - Audio transcription, speaker diarization, timestamp extraction with TO_FILE syntax
- [AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability) - Evaluate, compare, and trace generative AI applications in Snowflake

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **SQL Demo Engineering**: `rules/102-snowflake-sql-demo-engineering.md`
- **Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **Semantic Views**: `rules/106-snowflake-semantic-views-core.md`
- **Observability**: `rules/111-snowflake-observability-core.md`
- **Snowflake CLI**: `rules/112-snowflake-snowcli.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`

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

**CORRECT Pattern - TO_FILE with two arguments:**

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

**INCORRECT Patterns (will cause type errors):**

```sql
-- WRONG: Using GET_PRESIGNED_URL (returns VARCHAR, not FILE type)
SELECT AI_TRANSCRIBE(GET_PRESIGNED_URL('@stage', 'file.mp3'));
-- Error: Invalid argument types for function 'AI_TRANSCRIBE': (VARCHAR)

-- WRONG: Using BUILD_SCOPED_FILE_URL without TO_FILE wrapper
SELECT AI_TRANSCRIBE(BUILD_SCOPED_FILE_URL(@stage, path));
-- Error: Invalid argument types for function 'AI_TRANSCRIBE': (VARCHAR)

-- WRONG: Wrapping BUILD_SCOPED_FILE_URL result with TO_FILE (single arg)
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

**Speaker Recognition (Diarization) with timestamp_granularity:**

```sql
-- AI_TRANSCRIBE with native speaker identification
WITH audio_files AS (
    SELECT RELATIVE_PATH
    FROM DIRECTORY('@CALL_CENTER.AUDIO.RECORDINGS')
    WHERE RELATIVE_PATH LIKE '%.mp3'
    LIMIT 1
),
transcribed_with_speakers AS (
    SELECT
        RELATIVE_PATH AS audio_file,
        -- timestamp_granularity: 'speaker' returns structured segments
        AI_TRANSCRIBE(
            TO_FILE('@CALL_CENTER.AUDIO.RECORDINGS', RELATIVE_PATH),
            {'timestamp_granularity': 'speaker'}
        ) AS transcription_json
    FROM audio_files
),
-- Flatten segments array to get individual speaker turns
speaker_segments AS (
    SELECT
        audio_file,
        transcription_json:text::VARCHAR AS full_transcript,
        transcription_json:audio_duration::FLOAT AS audio_duration,
        seg.value:speaker_label::VARCHAR AS speaker,  -- SPEAKER_01, SPEAKER_02, etc.
        seg.value:start::FLOAT AS start_time,
        seg.value:end::FLOAT AS end_time,
        seg.value:text::VARCHAR AS segment_text
    FROM transcribed_with_speakers,
    LATERAL FLATTEN(input => transcription_json:segments) seg
)
SELECT
    audio_file,
    speaker,
    ROUND(start_time, 2) AS start_sec,
    ROUND(end_time, 2) AS end_sec,
    ROUND(end_time - start_time, 2) AS duration_sec,
    segment_text
FROM speaker_segments
ORDER BY start_time;
```

**Speaker Recognition Notes:**
- `timestamp_granularity: 'speaker'` returns structured segments with speaker changes
- Speaker labels are generic: SPEAKER_01, SPEAKER_02, etc. (not semantic roles like "agent", "customer")
- Each segment includes: `speaker_label`, `start`, `end`, `text`
- Use LATERAL FLATTEN to extract individual speaker turns
- For semantic role identification (e.g., "Representative" vs "Customer"), chain with AI_COMPLETE
- Supported file types: FLAC, MP3, OGG, WAV, WebM (up to 60 minutes for speaker mode)

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

## Related Rules

**Closely Related** (consider loading together):
- `116-snowflake-cortex-search` - For document embedding and semantic search with AI_EMBED
- `115-snowflake-cortex-agents-core` - When using Cortex AI functions within agent tools

**Sometimes Related** (load if specific scenario):
- `106c-snowflake-semantic-views-integration` - Cortex Analyst approach (semantic views vs direct SQL functions)
- `101-snowflake-streamlit-core` - When using Cortex AI functions in Streamlit applications
- `109-snowflake-notebooks` - When using Cortex AI functions in notebook workflows

**Complementary** (different aspects of same domain):
- `105-snowflake-cost-governance` - For monitoring Cortex AI function costs (token usage)
- `103-snowflake-performance-tuning` - For optimizing queries that call Cortex AI functions
