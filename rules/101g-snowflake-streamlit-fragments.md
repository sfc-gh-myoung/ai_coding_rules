---
schema_version: v4.0
rule_version: v3.0.0
description: "Streamlit fragments: scoped reruns for interactive sections and run_every polling with session-state lifecycle, bounded termination, safe background work and tested cleanup."
last_updated: 2026-10-07
keywords:
  - kw:st.fragment
  - kw:run_every auto-refresh
  - kw:live progress polling
  - kw:session state persistence
  - kw:fragment termination st.stop
  - kw:conditional fragment rendering
token_budget: ~900
context_tier: Medium
depends:
  required:
    - 101-snowflake-streamlit-core.md  # Core Streamlit patterns
  optional:
    - 101b-snowflake-streamlit-performance.md  # Caching and performance basics
---
# Streamlit Fragments

## Scope

**What This Rule Covers:**
`st.fragment` for partial reruns of interactive sections and `run_every` auto-refresh for live status, progress polling and monitoring, including session-state lifecycle, stopping polling, background job tracking and error handling.

**When to Load This Rule:**
When part of an app should rerun independently or poll for updates; load `101b-snowflake-streamlit-performance.md` for caching interplay.

## Contract

### Inputs and Prerequisites

- Installed Streamlit version (fragments are GA from 1.37; earlier versions used experimental APIs), runtime and the section to isolate.
- Progress or status source (table, query history, API), its cost per poll, and how long-running work is started and owned.

### Mandatory

- Define fragment functions at module level and call them during the full-script run; use them to isolate widgets and outputs that should rerun without the whole app. Widgets belong in the fragment's main body, not in containers created outside it.
- Pass dynamic inputs through `st.session_state` (fragments do not detect argument changes) and do not combine caching decorators with the fragment function.
- Drive polling from session state: render the `run_every` fragment only while an operation is active; on completion, update state and call `st.rerun(scope="app")` (or stop calling the fragment) so polling ends. `st.stop()` ends only the current run.
- Every polling fragment has a termination condition and a timeout, and surfaces errors once instead of retrying silently forever.
- Choose intervals from status-update needs and per-poll cost; each poll may run a warehouse query, so keep status queries narrow and avoid tight intervals on warehouse-billed sources.
- Start long-running Snowflake work as asynchronous queries, tasks or stored procedures that record status in a table the app can read; do not call Streamlit APIs from background threads, and do not share a non-thread-safe session across threads.
- Writing progress or status rows and creating tables or tasks are approved mutations; scope status rows to the user or job ID and clean up per retention policy.
- Disable or guard start buttons while a job for that user is running to prevent duplicate submissions.
- Test start, progress, completion, failure, timeout and page reload paths; do not claim polling stops or cleans up without observing it.

### Execution Steps

1. Read app flow, Streamlit version, operation source and runtime; decide what the fragment isolates or polls.
2. Implement module-level fragments with session-state lifecycle, termination, timeout and error handling.
3. Exercise interactive and polling paths, including failure and reload, in the target runtime.
4. Report fragment behavior, polling cost, evidence and remaining gaps.

### Validation

- Fragments defined at module level; inputs via session state; no cached fragment functions.
- Polling bounded with termination, timeout and full-app rerun on completion.
- Long work runs outside Streamlit threads with job-scoped status.
- Lifecycle paths tested in the target runtime.

## References

- [st.fragment](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment)
- [Working with fragments](https://docs.streamlit.io/develop/concepts/architecture/fragments)
- [st.rerun](https://docs.streamlit.io/develop/api-reference/execution-flow/st.rerun)
- [Snowpark DataFrames and async jobs](https://docs.snowflake.com/en/developer-guide/snowpark/python/working-with-dataframes)
