**Description:** Directives for creating modern, performant, and maintainable Streamlit applications for Snowflake.
**Applies to:** `**/*.py`, `streamlit/**/*`
**Auto-attach:** false

# Streamlit UI/UX Directives

## TL;DR
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