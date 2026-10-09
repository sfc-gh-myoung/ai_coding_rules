---
schema_version: v4.0
rule_version: v5.0.0
description: "Streamlit SQL error handling: specific SnowparkSQLException handling outside caches, sanitized viewer messages with codes/query IDs, logged context, empty-result states and stop-on-failure."
last_updated: 2026-10-07
keywords:
  - kw:SnowparkSQLException
  - kw:streamlit sql error display
  - kw:error code display
  - kw:query context messaging
  - kw:st.stop cascade prevention
  - kw:empty dataframe warning
token_budget: ~1000
context_tier: Low
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns and validation gates
    - 100-snowflake-core.md  # Snowflake fundamentals
    - 101-snowflake-streamlit-core.md  # Core Streamlit patterns
  optional:
    - 100f-snowflake-connection-errors.md  # Connection error classification and handling
    - 101c-snowflake-streamlit-security.md  # Input validation for SQL injection prevention
---
# Streamlit SQL Error Handling

## Scope

**What This Rule Covers:**
Handling query failures and empty results in Streamlit apps on Snowflake: SnowparkSQLException and connector errors, viewer messages, logging, query identification, empty states, stopping dependent rendering and retries.

**When to Load This Rule:**
When adding or reviewing query error handling in Streamlit apps; load `100f-snowflake-connection-errors.md` for connection failures and `101c-snowflake-streamlit-security.md` for message sanitization.

## Contract

### Inputs and Prerequisites

- App query functions, their callers and caching, connection method (`st.connection` or Snowpark session) and logging/telemetry setup.
- Viewer audience (end users vs developers), support process and sensitivity of object names and data.

### Mandatory

- Catch the specific exception types raised by the client in use (`SnowparkSQLException` for Snowpark, connector `ProgrammingError`/`DatabaseError` for `st.connection().query`) before any generic handler, and never swallow errors silently.
- Keep cached loader functions free of UI calls: let them raise, and handle errors in the calling UI code, so failures are not cached or replayed and `st.stop()` is not invoked inside cached functions.
- Show viewers a concise, sanitized message identifying the failed operation plus the error code and query ID (`sfqid`) for support; reserve raw error text, SQL, object names and debugging hints for developer mode or logs when the audience allows.
- Log full context (operation, error code, query ID, sanitized parameters) through the app logger or event table telemetry, never secrets or sensitive data values.
- Label independent queries so the failing one is identifiable, and stop or skip only the rendering that depends on failed data (`st.stop()` for page-blocking failures, section-level fallbacks otherwise).
- Distinguish failures (`st.error`) from legitimately empty results (`st.info`/`st.warning` with the active filters), and never return an empty DataFrame to hide a failure.
- Retry only transient errors with bounded backoff; do not retry permission, syntax or object-not-found errors.
- Set statement timeouts on long queries through session or object parameters within approved scope and show progress for long waits.
- Test with forced failures (missing object, permission denied, invalid filter, empty result) and confirm messages, logging and stop behavior; do not claim handling from review alone.

### Execution Steps

1. Read query functions, caching, callers and logging; list each query and its dependents.
2. Implement specific exception handling at the UI layer with sanitized messages, logging and empty-state handling.
3. Exercise forced error and empty cases locally and in the target runtime.
4. Report handled paths, message content, log evidence and remaining gaps.

### Validation

- Specific exceptions caught first; no silent failures or cached error UI.
- Viewer messages sanitized with code and query ID; full context logged safely.
- Empty results distinct from failures; dependent rendering stopped or degraded intentionally.
- Retries limited to transient errors; forced-failure tests pass.

## References

- [SnowparkSQLException](https://docs.snowflake.com/en/developer-guide/snowpark/reference/python/latest/snowpark/api/snowflake.snowpark.exceptions.SnowparkSQLException)
- [Logging and tracing for Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/features/logging-tracing)
- [st.error](https://docs.streamlit.io/develop/api-reference/status/st.error)
- [st.stop](https://docs.streamlit.io/develop/api-reference/execution-flow/st.stop)
