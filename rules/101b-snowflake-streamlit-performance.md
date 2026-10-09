---
schema_version: v4.0
rule_version: v5.0.0
description: "Streamlit performance on Snowflake: runtime-aware caching that never leaks or caches writes, set-based queries, explicit column handling, user feedback and measured load times."
last_updated: 2026-10-07
keywords:
  - kw:@st.cache_data decorator
  - kw:@st.cache_resource decorator
  - kw:Snowflake column normalization
  - kw:st.spinner progress feedback
  - kw:query loop aggregation
  - kw:ttl cache expiration
token_budget: ~950
context_tier: High
depends:
  required:
    - 103-snowflake-performance-tuning.md  # Snowflake query optimization
---
# Streamlit Performance

## Scope

**What This Rule Covers:**
Streamlit-in-Snowflake and local app performance: `st.cache_data`/`st.cache_resource`, TTL and invalidation, session/connection reuse, Snowflake column-name casing, query consolidation, progress feedback, fragments and profiling.

**When to Load This Rule:**
When an app is slow, hits the database repeatedly, mishandles cached data or needs progress feedback; load `101g-snowflake-streamlit-fragments.md` for partial reruns.

## Contract

### Inputs and Prerequisites

- App code, runtime (warehouse runtime has per-viewer instances and no cross-session cache; container runtime shares one server and cache across viewers), data freshness needs and volumes.
- Query warehouse, query profiles or timings, rights model (owner's or restricted caller's rights) and performance targets.

### Mandatory

- Read data-loading code, decorators and TTLs before recommending changes; measure where time goes (Query Profile, timings, reruns) before optimizing.
- Cache read-only query results with `st.cache_data` keyed on all inputs and a TTL matching data freshness; never cache functions that perform DML/DDL or other side effects.
- Container runtime caches are shared across viewers: never cache results whose content depends on viewer identity or caller's-rights privileges unless the user identity is part of the cache key, and never cache secrets in data caches.
- Use `st.connection("snowflake")` (which manages its own resources) or cache a session factory with `st.cache_resource`; do not use `get_active_session()` in container runtime. Treat cached resources as shared and thread-unsafe unless documented otherwise.
- Push filters, joins and aggregation into one parameterized query instead of per-item query loops; select only needed columns and avoid pulling large raw tables into pandas.
- Snowflake returns unquoted identifiers in uppercase; normalize column names once in the loader (or alias explicitly in SQL) so UI code uses consistent names, and keep quoted mixed-case identifiers deliberate.
- Provide feedback for noticeable waits (`st.spinner`, `st.status`, `st.progress`) and keep long work out of tight rerun paths; use forms, callbacks or fragments to avoid unnecessary reruns.
- Offer explicit refresh via `cache_data.clear()` or function-specific `.clear()` where users need fresh data, and handle stale data visibly.
- Bound memory: paginate or aggregate large results and watch container memory; choose limits from observed usage, not fixed numbers.
- Show user-safe errors and log details; do not dump raw exception text to viewers.
- Verify cache hits, invalidation, cross-user isolation and load time with production-like data in the target runtime; do not claim speedups without before/after measurements.

### Execution Steps

1. Read loaders, caching, connection usage and rerun triggers; measure query and render time.
2. Consolidate queries, add correctly keyed caches and column normalization, and add feedback for slow paths.
3. Test cache behavior, invalidation, user isolation and errors with realistic data.
4. Report changes, measurements before and after and remaining bottlenecks.

### Validation

- Only read-only, non-sensitive results cached with appropriate keys and TTLs.
- No per-item query loops; queries parameterized and column-selective.
- Column names consistent; slow operations show feedback; errors sanitized.
- Measured improvement and isolation verified in the target runtime.

## References

- [Streamlit caching](https://docs.streamlit.io/develop/concepts/architecture/caching)
- [st.cache_data](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data)
- [st.cache_resource](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource)
- [Runtime environments](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/runtime-environments)
- [Query Profile](https://docs.snowflake.com/en/user-guide/ui-query-profile)
