---
schema_version: v4.0
rule_version: v6.0.0
description: "Streamlit in Snowflake foundations: runtime choice, owner's-rights connections, navigation, session state, config.toml theming and Snowflake-managed secrets."
last_updated: 2026-10-07
keywords:
  - kw:Streamlit
  - kw:st.navigation
  - kw:session state
  - kw:Container Runtime
  - kw:config.toml theming
  - kw:st.connection snowflake
token_budget: ~1150
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake connection and query execution fundamentals
  optional:
    - 101b-snowflake-streamlit-performance.md  # Caching and query optimization patterns
    - 101c-snowflake-streamlit-security.md  # Input validation and secrets management
    - 101l-snowflake-streamlit-deployment.md  # Container and Warehouse Runtime deployment
---
# Streamlit in Snowflake Core

## Scope

**What This Rule Covers:**
Foundations for Streamlit apps in Snowflake and local development: container vs warehouse runtime, `st.connection("snowflake")`, multipage navigation, page config, session state, layout, config.toml theming, secrets and stage file handling.

**When to Load This Rule:**
For any Streamlit-in-Snowflake task before specialized 101a–101n rules; load `101l-snowflake-streamlit-deployment.md` for deployment and `101c-snowflake-streamlit-security.md` for security.

## Contract

### Inputs and Prerequisites

- Existing app files, Streamlit object definition (FROM vs legacy ROOT_LOCATION), runtime, Python/Streamlit versions and dependency file (`environment.yml` or `pyproject.toml`/`requirements.txt`).
- Owner role, query warehouse, compute pool and external access integrations, data privileges, target users and region support.

### Mandatory

- Identify the actual runtime before designing: container runtime (compute pool, shared server, Python 3.11, Streamlit 1.50+, PyPI packages via EAI, cross-session caching) or warehouse runtime (per-viewer instance, Python 3.9–3.11, Snowflake Conda packages, no cross-session cache). Container runtime is unavailable in some regions; ROOT_LOCATION objects are warehouse-only.
- Queries run with the app owner's rights by default (restricted caller's rights is a container-runtime preview option); scope the owner role to least privilege and never expose data viewers should not see.
- Use `st.connection("snowflake")` (or the established session helper) consistently; handle connection and query errors with user-safe messages and logged detail.
- Call `st.set_page_config()` once, in the entrypoint, before other Streamlit output.
- Choose one navigation model: `st.navigation()` with `st.Page` entries (which disables `pages/` auto-discovery) or `pages/` auto-discovery; use `st.page_link`/`st.switch_page` for in-app links rather than ad hoc rerun tricks.
- Initialize `st.session_state` keys with defaults before use and update via callbacks; never keep per-user data in module-level globals, which are shared across viewers in container runtime. Persist durable state in Snowflake tables with approval.
- Theme through `.streamlit/config.toml`; avoid `unsafe_allow_html` and CSS injection, and never render untrusted content as HTML.
- In Snowflake, use Snowflake SECRET objects with external access integrations; locally use `st.secrets`/secrets.toml excluded from version control. Never hard-code credentials or display secret values.
- Handle Snowflake NULLs from pandas with `pd.isna`/`pd.notna`, not `is None`.
- Upload app files without compression (`--no-auto-compress` or `AUTO_COMPRESS=FALSE`) when using stage-based deploys, preserving directory layout; deployment and stage writes are approved mutations.
- Verify locally and in the target runtime: pages load, state persists across reruns, errors render safely and no console exceptions; do not claim runtime behavior from local runs alone.

### Execution Steps

1. Read app files, Streamlit object, runtime, dependencies, owner role and data access.
2. Implement minimal entrypoint, navigation, state, theme and connection changes for that runtime.
3. Run available lint/tests and exercise the app locally, then in the target runtime with approval.
4. Report runtime, files, privileges, verification evidence and runtime-specific gaps.

### Validation

- Runtime constraints respected (packages, Python/Streamlit versions, caching, region).
- Single page config; one navigation model; state initialized and user-isolated.
- Owner role least-privilege; secrets managed by Snowflake or excluded local files.
- App verified in the target runtime or explicitly marked unverified.

## References

- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Runtime environments](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/runtime-environments)
- [Restricted caller's rights](https://docs.snowflake.com/en/developer-guide/streamlit/features/restricted-callers-rights)
- [st.navigation](https://docs.streamlit.io/develop/api-reference/navigation/st.navigation)
- [Session state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)
- [Theming](https://docs.streamlit.io/develop/concepts/configuration/theming)
