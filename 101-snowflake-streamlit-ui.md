**Description:** Directives for creating modern, performant, and maintainable Streamlit applications for Snowflake.
**AppliesTo:** `**/*.py`, `streamlit/**/*`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.2
**LastUpdated:** 2025-09-16

# Streamlit UI/UX Directives

## Purpose
Provide comprehensive guidance for building modern, performant, and maintainable Streamlit applications within the Snowflake ecosystem, focusing on user experience, performance optimization, and modular architecture patterns.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake Streamlit application development, UI/UX patterns, and performance optimization

## Contract
- **Inputs/Prereqs:** Python 3.11+, Streamlit 1.28+, Snowflake connection, project structure with pages/ and components/
- **Allowed Tools:** st.cache_data, st.cache_resource, st.session_state, Snowflake connector, pandas/polars
- **Forbidden Tools:** raw SQL loops, custom CSS blocks, unhandled exceptions in UI
- **Required Steps:** 1) Set page config, 2) Initialize session state, 3) Cache data operations, 4) Implement error handling
- **Output Format:** Streamlit app with <2s load time, modular architecture, accessible UI
- **Validation Steps:** Test caching behavior, verify responsive design, check error handling, validate accessibility

## Key Principles
- Fast First Paint (<2s), modular architecture, deterministic state; cache data/resources appropriately.
- Use page config, pages/ structure, components/ for reuse; avoid raw loops and re-creating connections.
- Clear help text, responsive layouts, no raw exception traces; follow Streamlit/Snowflake docs.

## 1. Core Principles
- **Requirement:** Prioritize Fast First Paint and performant interactions (target <2s initial load).
- **Requirement:** Use a modular architecture separating UI components, business logic, and page navigation.
- **Requirement:** Ensure deterministic application state. Initialize session state explicitly and avoid hidden globals.
- **Requirement:** Design for accessibility (aim for WCAG AA compliance).

## 2. Setup and Structure
- **Always:** Call `st.set_page_config` in the entry point to set title, icon, and wide layout.
- **Always:** Initialize session state once at the top level to keep state consistent across re-runs.
- **Always:** Organize multi-page applications using the `pages/` directory structure.
- **Always:** Place reusable UI elements (charts, forms) in a `components/` directory.

## 3. Performance and Caching
- **Requirement:** Cache database queries and data fetches with `@st.cache_data` and an appropriate `ttl`.
- **Requirement:** Cache expensive objects and connections (e.g., Snowflake connections) using `@st.cache_resource`.
- **Always:** For slow operations (>1s), show user feedback via `st.spinner` or `st.status`.
- **Requirement:** Avoid raw database query loops; fetch all needed data at once and cache it.

## 4. UI/UX Design and State Management
- **Requirement:** Use `st.page_link` for navigation and `st.button` for actions; do not use buttons for navigation.
- **Requirement:** Centralize design tokens (colors, icons) rather than hard-coding values.
- **Requirement:** Provide clear help text (`help="..."`) for complex widgets.
- **Requirement:** Manage state predictably with `st.session_state` and callbacks for complex updates.
- **Requirement:** Use responsive layouts with `st.columns`, `st.sidebar`, and `use_container_width=True` for charts.

## 5. Anti-Patterns
- **Avoid:** Mixing business logic and UI rendering in a single large function.
- **Mandatory:** Never show raw exception traces to users. Use `st.error()` with a clear, actionable message.
- **Avoid:** Recreating database connections on every interaction.
- **Avoid:** Embedding custom CSS or HTML style blocks in Python code.

## 6. Documentation
- **Always:** Reference the official documentation:
  - **Caching**: https://docs.streamlit.io/develop/concepts/architecture/caching
  - **Session State**: https://docs.streamlit.com/develop/concepts/architecture/session-state
  - **Layouts**: https://docs.streamlit.io/develop/api-reference/layout
  - **API Reference**: https://docs.streamlit.io/develop/api-reference
- **Requirement:** When building for Snowflake, cross-reference Streamlit in Snowflake docs for differences in behavior, security context, and supported features: https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit

## Quick Compliance Checklist
- [ ] App loads in under 2 seconds (Fast First Paint achieved)
- [ ] Page config set with title, icon, and layout
- [ ] Session state initialized explicitly at app start
- [ ] Database queries cached with appropriate TTL
- [ ] Error handling implemented with user-friendly messages
- [ ] Responsive layout using st.columns and container_width=True
- [ ] Modular structure with pages/ and components/ directories
- [ ] No raw exception traces shown to users
- [ ] Help text provided for complex widgets
- [ ] Navigation uses st.page_link, not buttons

## Validation
- **Success checks:** App loads <2s, caching reduces query time, responsive on mobile/desktop, error states handled gracefully
- **Negative tests:** Break database connection (should show error message), disable cache (should show performance impact), test with malformed data (should not crash)

## Response Template
```python
import streamlit as st
from snowflake.connector import connect

# Page configuration
st.set_page_config(
    page_title="App Name",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

@st.cache_resource
def get_snowflake_connection():
    return connect(**st.secrets["snowflake"])

@st.cache_data(ttl=300)
def load_data():
    conn = get_snowflake_connection()
    return conn.cursor().execute("SELECT * FROM table").fetchall()

# Main app logic with error handling
try:
    with st.spinner("Loading data..."):
        data = load_data()
    st.success("Data loaded successfully!")
except Exception as e:
    st.error("Unable to load data. Please try again later.")
```

## References

### External Documentation
- [Streamlit Documentation](https://docs.streamlit.io/) - Official Streamlit application development guide
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference) - Complete API reference for all Streamlit components
- [Snowflake Streamlit Guide](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit) - Snowflake-specific Streamlit integration documentation
- [Streamlit Performance](https://docs.streamlit.io/library/advanced-features/caching) - Caching and performance optimization techniques

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Snowflake Notebooks**: `109-snowflake-notebooks.md`
- **Python Core**: `200-python-core.md`
