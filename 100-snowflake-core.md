**Description:** Comprehensive rules for all Snowflake tasks, ensuring consistent, performant, and secure solutions.
**AppliesTo:** `**/*.sql`, `**/*.scl`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-09-10

# Snowflake Core Directives

## Purpose
Establish comprehensive foundational practices for all Snowflake development work, ensuring cost-effective, performant, and secure solutions through proper SQL authoring, object naming, security policies, and architectural patterns.

## TL;DR
- Cost-first; fully qualify objects; prefer set-based SQL with clear CTEs and explicit joins.
- Push filters early, minimize data movement; parse VARIANT at the edge.
- Enforce security policies; never use SELECT *; avoid deep view nesting and DISTINCT as a band-aid.
- Use Streams + Tasks for incremental pipelines; avoid unnecessary full reloads.
- Validate with the provided checklist before shipping.

## 1. General Principles
- **Always:** Apply a "cost-first" mindset.
- **Rule:** Always fully qualify objects (DATABASE.SCHEMA.OBJECT) in shared code.
- **Rule:** Prefer declarative set-based operations over procedural row loops.
- **Rule:** Use CTEs for logical segmentation.
- **Rule:** Avoid accidental cross joins by using explicit join predicates and aliases.

## 2. Optimization and Performance
- **Always:** Push filtering and partition pruning as early as possible in queries.
- **Rule:** Minimize data movement by avoiding unnecessary re-materialization.
- **Always:** Use semi-structured data types (VARIANT) only at the ingestion edge; normalize critical fields.
- **Always:** Use Snowflake's query profile to diagnose performance issues and propose optimizations.
- **Always:** Reference Snowflake performance documentation for query tuning guidance: https://docs.snowflake.com/en/user-guide/performance-overview

## 3. Security and Governance
- **Rule:** Enforce governance with masking policies, row access policies, and tagging, especially for sensitive data.
- **Rule:** Never use `SELECT *` in production code. Explicitly project required columns.
- **Always:** Use Time Travel and Cloning for safe development, testing, and dev/test isolation.
- **Always:** Reference Snowflake security and governance documentation for best practices: https://docs.snowflake.com/en/user-guide/data-governance-intro

## 4. Anti-Patterns
- **Rule:** Avoid deep view nesting (>5 layers).
- **Rule:** Do not use `DISTINCT` to fix duplicates; solve the root cause upstream.
- **Rule:** Avoid repeated casting of `VARIANT` fields; parse them once in a CTE.
- **Rule:** Avoid recomputing large fact tables from scratch daily unless a high change rate is necessary.

## 5. Incremental Patterns
- **Always:** Use **Streams** and **Tasks** for incremental data pipelines instead of full reloads or ad-hoc MERGE loops.
- **Always:** Reference Snowflake Streams and Tasks documentation for implementation details: https://docs.snowflake.com/en/sql-reference-commands

## 6. Common Tasks & Checklists
- **Always:** Before any action, apply the following checks:
  - Are objects fully qualified?
  - Are joins explicit?
  - Is `SELECT *` removed?
  - Is an incremental pattern used for mutable, large tables?
  - Are security policies or masks applied where needed?
  - Are anti-patterns absent?

## 7. Related Specialized Rules
- **Rule:** For deeper guidance, reference the following specialized rules:
  - `101-snowflake-streamlit-ui.md`: Modern, performant, and maintainable Streamlit UIs
  - `102-snowflake-sql-best-practices.md`: Advanced SQL authoring patterns (CTEs, VARIANT extraction, cardinality control).
  - `103-snowflake-performance-tuning.md`: Profiling, pruning, warehouse sizing, clustering justification.
  - `104-snowflake-streams-tasks.md`: Incremental pipelines with Streams + Tasks, idempotency, monitoring.
  - `105-snowflake-cost-governance.md`: Workload isolation, resource monitors, right-sizing, anomaly detection.
  - `106-snowflake-semantic-views.md`: Layering (staging/core/semantic), naming conventions, and slim views.
  - `107-snowflake-security-governance.md`: Masking policies, row access, tagging, and role strategies.
  - `108-snowflake-data-loading.md`: Stages, `COPY INTO`, and Snowpipe best practices.
  - `109-snowflake-notebooks.md`: Jupyter Notebooks in Snowflake best practices.
