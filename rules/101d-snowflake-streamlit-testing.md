---
schema_version: v4.0
rule_version: v5.0.0
description: "Streamlit testing: pytest unit tests for data logic, AppTest UI flows, isolated mocked Snowflake access, cache and error-path tests and project-defined coverage gates."
last_updated: 2026-10-07
keywords:
  - kw:AppTest
  - kw:streamlit ui testing
  - kw:cache behavior testing
  - kw:mock snowflake session
  - kw:widget interaction testing
  - kw:pytest coverage 80%
token_budget: ~900
context_tier: High
depends:
  required:
    - 206-python-pytest.md  # Python testing with pytest
  optional:
    - 101b-snowflake-streamlit-performance.md  # Cache behavior testing
---
# Streamlit Testing

## Scope

**What This Rule Covers:**
Automated testing and debugging of Streamlit apps: pytest unit tests for data and helper functions, `streamlit.testing.v1.AppTest` UI flows, mocking Snowflake sessions and connections, cache tests, error and edge cases, coverage and CI.

**When to Load This Rule:**
When adding or fixing tests for a Streamlit app or debugging app behavior; load `206-python-pytest.md` for general pytest conventions.

## Contract

### Inputs and Prerequisites

- App structure, entrypoint and pages, installed Streamlit version (AppTest API), existing tests, fixtures and coverage configuration.
- How the app reaches Snowflake (`st.connection`, Snowpark session helper), test environment access and the project's test command.

### Mandatory

- Separate data and business logic from UI so it can be unit tested with pytest; test valid, empty, NULL/NaN, malformed and boundary inputs with concrete assertions on values, not just non-None results.
- Use AppTest (`AppTest.from_file`, `from_function`) for UI flows: assert `not at.exception`, interact through widgets and assert rendered output and session state; give widgets stable `key=` values and access them by key.
- AppTest does not run multipage navigation through the browser; test each page file or switch pages with the API available in the installed version, and verify navigation manually in the target runtime.
- Patch Snowflake access at the app's actual boundary (the module path where it is used) so unit and AppTest runs never reach live accounts; integration tests against Snowflake use a dedicated non-production environment with explicit approval and never modify production data.
- Clear Streamlit caches between tests (`st.cache_data.clear()`, `st.cache_resource.clear()` or function `.clear()`) and verify hits by mock call counts and invalidation by parameter change or clear.
- Test error paths: SQL errors, missing secrets, invalid uploads and unauthorized states render sanitized messages and stop safely.
- Meet the project's configured coverage threshold (for example `--cov-fail-under`) rather than an invented universal number; coverage supplements, not replaces, meaningful assertions.
- Run the project's actual test command in CI; keep tests deterministic with fixed data, no sleeps and no network.
- Debug with logs, AppTest output and reproduction tests before changing code; remove temporary debug output.
- Report test results with commands and outcomes; do not claim behavior or coverage without running the suite.

### Execution Steps

1. Read app structure, Snowflake access path, existing tests and coverage configuration.
2. Extract testable logic where needed and write unit tests, AppTest flows, mocks and cache/error tests.
3. Run the suite with coverage locally and in CI, fixing failures or flakiness.
4. Report tests added, commands and results, coverage and untested runtime behavior.

### Validation

- Unit tests assert concrete results for normal and edge inputs.
- AppTest flows assert no exceptions, widget effects and rendered output.
- No live Snowflake or network access in unit/UI tests; caches isolated.
- Suite passes and meets the project coverage gate, or failures are reported.

## References

- [Streamlit app testing](https://docs.streamlit.io/develop/concepts/app-testing)
- [AppTest API](https://docs.streamlit.io/develop/api-reference/app-testing)
- [pytest](https://docs.pytest.org/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
