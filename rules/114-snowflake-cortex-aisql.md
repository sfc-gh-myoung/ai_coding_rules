---
schema_version: v4.0
rule_version: v5.0.0
description: "Snowflake Cortex AI SQL functions: current signatures, approved model access, token/cost preflight, bounded batch execution, error-aware results and governed data handling."
last_updated: 2026-10-07
keywords:
  - kw:cortex aisql
  - kw:llm function batching
  - kw:model selection strategy
  - kw:token budget control
  - kw:TO_FILE stage references
  - kw:CORTEX_USER privilege governance
  - kw:ai_classify
token_budget: ~1350
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 105-snowflake-cost-governance.md  # Cost monitoring and optimization
  optional:
    - 114a-snowflake-cortex-ai-transcribe.md  # AI_TRANSCRIBE audio transcription patterns
    - 102-snowflake-sql-core.md  # General SQL file patterns
    - 119-snowflake-warehouse-management.md  # Warehouse sizing and management
---
# Snowflake Cortex AI Functions

## Scope

**What This Rule Covers:**
Cortex AI SQL functions (AI_COMPLETE, AI_CLASSIFY, AI_FILTER, AI_EXTRACT, AI_SENTIMENT, AI_SUMMARIZE, AI_AGG, AI_SUMMARIZE_AGG, AI_EMBED, AI_SIMILARITY, AI_TRANSLATE, AI_PARSE_DOCUMENT, AI_TRANSCRIBE) with PROMPT, TO_FILE and AI_COUNT_TOKENS, from SQL and Snowpark, plus privileges, cost and observability.

**When to Load This Rule:**
When writing, reviewing or costing Cortex AI function usage; load `114a-snowflake-cortex-ai-transcribe.md` for audio and `105-snowflake-cost-governance.md` for budgets.

## Contract

### Inputs and Prerequisites

- Task, input data (text, staged files), volume and quality requirements; existing AI function usage, prompts and evaluation sets.
- Account region and model availability, granted roles (SNOWFLAKE.CORTEX_USER or AI function privileges, model allowlist), warehouse, budget and data classification.

### Mandatory

- Use each function's current documented signature: AI_CLASSIFY(input, categories[, config]), AI_AGG(expr, instruction) and AI_SUMMARIZE_AGG(expr) take no model argument; AI_COMPLETE takes a model; AI_EXTRACT takes a responseFormat; AI_COUNT_TOKENS takes the target function name first, then model where applicable.
- Prefer the task-specific function (classify, extract, sentiment, summarize, translate) over free-form AI_COMPLETE prompts; pick AI_COMPLETE models from the current regional availability list and the account allowlist (`SHOW CORTEX BASE MODELS` where available) rather than hard-coded or deprecated names.
- Choose models by measured quality on a labeled sample against task-specific acceptance criteria, then cost and latency; do not assume smallest or largest is correct or invent accuracy thresholds.
- Running AI functions consumes credits per token; any query over real data needs an approved warehouse and budget. Preflight with AI_COUNT_TOKENS on a sample, estimate cost from the current consumption table, and run on bounded subsets before full batches.
- Process in set-based SQL over filtered columns, select only needed columns, truncate or chunk long inputs, and write results to a table incrementally keyed on unprocessed rows for large backfills; creating tables or tasks is an approved mutation, and tasks are created suspended.
- Use AI_AGG/AI_SUMMARIZE_AGG for cross-row aggregation; they summarize across rows and are not a substitute for per-row results.
- Treat outputs as non-deterministic and untrusted: parse structured outputs (AI_SENTIMENT returns an object with categorical values; AI_EXTRACT returns JSON), validate types and allowed values, and use `return_error_details` or NULL checks to separate failures from valid results instead of silently coalescing.
- Never interpolate untrusted values into dynamic SQL; use PROMPT templates and bind parameters, and treat document text as data, not instructions.
- Reference staged files with TO_FILE(stage, path) (FILE type), not presigned or scoped URLs; verify stage privileges and supported file formats.
- Govern access: grant SNOWFLAKE.CORTEX_USER (or narrower AI privileges) to least-privilege roles; revoking it from PUBLIC or changing model allowlists is an account-level change requiring approval and impact review.
- Do not send secrets or unnecessary sensitive data to AI functions; apply masking and row access policies and respect data residency and cross-region inference settings.
- Monitor cost and usage with CORTEX_AISQL_USAGE_HISTORY and related Account Usage views (noting latency), budgets and AI Observability for quality evaluation.
- Validate with real sampled runs and evaluation metrics; do not claim quality, cost or throughput from prompt design alone.

### Execution Steps

1. Read existing usage, privileges, model availability and data classification; define task, acceptance metric and labeled sample.
2. Draft the query with the task-specific function, explicit columns, prompts and output parsing; preflight tokens and cost.
3. With approval, run on a bounded sample, evaluate quality and errors, then scale incrementally with monitoring.
4. Report functions, models, measured quality, token/cost evidence, governance changes and remaining risks.

### Validation

- Signatures and models match current docs and regional availability.
- Token and cost preflight recorded; execution bounded and incremental.
- Outputs parsed and validated; failures distinguished from valid results.
- Least-privilege access, sensitive-data controls and usage monitoring in place.

## References

- [Cortex AI Functions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql)
- [AI_CLASSIFY](https://docs.snowflake.com/en/sql-reference/functions/ai_classify)
- [AI_COUNT_TOKENS](https://docs.snowflake.com/en/sql-reference/functions/ai_count_tokens)
- [AI_EXTRACT](https://docs.snowflake.com/en/sql-reference/functions/ai_extract)
- [Models and regional availability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql-regional-availability)
- [Privileges and model access](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql-privileges-and-access)
- [Cost management](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-func-cost-management)
