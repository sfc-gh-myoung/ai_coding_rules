**Description:** Directives for creating modern, performant, and maintainable Streamlit applications for Snowflake.
**AppliesTo:** `**/*.py`, `streamlit/**/*`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.5
**LastUpdated:** 2025-09-26

# Streamlit UI/UX Directives

## Purpose
Provide comprehensive guidance for building modern, performant, and maintainable Streamlit applications within the Snowflake ecosystem, focusing on user experience, performance optimization, and modular architecture patterns.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake Streamlit application development, UI/UX patterns, and performance optimization

## Contract
- **Inputs/Prereqs:** Python 3.11+, Streamlit 1.46+, Snowflake connection, project structure with pages/ and components/, deployment mode identified (SiS vs OSS on SPCS), .streamlit/config.toml for theming
- **Allowed Tools:** st.cache_data, st.cache_resource, st.session_state, st.set_page_config, config.toml, theme configuration, Snowflake connector, pandas/polars
- **Forbidden Tools:** raw SQL loops, inline custom CSS blocks, unhandled exceptions in UI, hardcoded theme values
- **Required Steps:** 1) Set page config with theme-aware settings, 2) Configure .streamlit/config.toml if needed, 3) Initialize session state, 4) Cache data operations, 5) Implement error handling
- **Output Format:** Streamlit app with <2s load time, modular architecture, accessible UI, consistent theming
- **Validation Steps:** Test caching behavior, verify responsive design and theming, check error handling, validate accessibility, confirm configuration loading

## Key Principles
- Fast First Paint (<2s), modular architecture, deterministic state; cache data/resources appropriately.
- Use page config, pages/ structure, components/ for reuse; avoid raw loops and re-creating connections.
- Centralized configuration via config.toml; consistent theming across deployment modes (SiS vs SPCS).
- Clear help text, responsive layouts, no raw exception traces; follow Streamlit/Snowflake docs.

## Deployment Modes: Streamlit in Snowflake (SiS) vs Open-source (SPCS)
- **Streamlit in Snowflake (SiS):** Runs inside Snowflake with a managed runtime and security context. Use the Snowflake Streamlit docs for capabilities, limitations, auth, and secrets handling. Packaging and deployment differ from open-source.
- **Open-source Streamlit on SPCS:** Deployed as a containerized app via Snowpark Container Services (SPCS). Follow SPCS deployment, networking, image build, and secrets guidance. Configuration, environment, and recommended patterns can differ from SiS.
- **Always verify the deployment mode first** and apply the correct configuration, best practices, and documentation. Do not mix SiS and open-source Streamlit recommendations.

## 1. Core Principles
- **Requirement:** Prioritize Fast First Paint and performant interactions (target <2s initial load).
- **Requirement:** Use a modular architecture separating UI components, business logic, and page navigation.
- **Requirement:** Ensure deterministic application state. Initialize session state explicitly and avoid hidden globals.
- **Requirement:** Design for accessibility (aim for WCAG AA compliance).

## 2. Setup and Structure
- **Always:** Call `st.set_page_config` in the entry point to set title, icon, and wide layout.
- **Always:** Initialize session state once at the top level to keep state consistent across re-runs.
- **Always:** Organize multi-page applications using the `pages/` directory structure ([Multipage Apps tutorial](https://docs.streamlit.io/get-started/tutorials/create-a-multipage-app)).
- **Always:** Place reusable UI elements (charts, forms) in a `components/` directory.

## 3. Performance and Caching
- **Requirement:** Cache database queries and data fetches with `@st.cache_data` and an appropriate `ttl`.
- **Requirement:** Cache expensive objects and connections (e.g., Snowflake connections) using `@st.cache_resource`.
- **Always:** For slow operations (>1s), show user feedback via `st.spinner` or `st.status`.
- **Requirement:** Avoid raw database query loops; fetch all needed data at once and cache it.

## 4. Configuration and Theming
- **Requirement:** Use `.streamlit/config.toml` for centralized configuration management and theme customization.
- **Requirement:** Define theme colors consistently using `[theme]` section: `primaryColor`, `backgroundColor`, `secondaryBackgroundColor`, `textColor`.
- **Requirement:** Configure fonts via `font` option ("sans serif", "serif", "monospace") for consistent typography.
- **Requirement:** Set `base` theme ("light" or "dark") as foundation before customizations.
- **Always:** For SiS deployments, verify theme configuration compatibility and limitations with Snowflake runtime.
- **Always:** For SPCS deployments, ensure config.toml is properly included in container image.
- **Avoid:** Hardcoding theme values in Python code; use centralized configuration instead.

## 5. UI/UX Design and State Management
- **Requirement:** Use `st.page_link` for navigation and `st.button` for actions; do not use buttons for navigation.
- **Requirement:** Centralize design tokens (colors, icons) in config.toml rather than hard-coding values.
- **Requirement:** Provide clear help text (`help="..."`) for complex widgets.
- **Requirement:** Manage state predictably with `st.session_state` and callbacks for complex updates.
- **Requirement:** Use responsive layouts with `st.columns`, `st.sidebar`, and `use_container_width=True` for charts.

## 6. Anti-Patterns
- **Avoid:** Mixing business logic and UI rendering in a single large function.
- **Mandatory:** Never show raw exception traces to users. Use `st.error()` with a clear, actionable message.
- **Avoid:** Recreating database connections on every interaction.
- **Avoid:** Embedding custom CSS or HTML style blocks in Python code; use config.toml for theming instead.
- **Avoid:** Mixing SiS and open-source Streamlit (SPCS) configurations, best practices, and deployment guidance.

## 7. Documentation
- **Always:** Reference the official documentation:
  - **Configuration**: https://docs.streamlit.io/develop/concepts/configuration
  - **Configuration and Theming Tutorial**: https://docs.streamlit.io/develop/tutorials/configuration-and-theming
  - **Caching**: https://docs.streamlit.io/develop/concepts/architecture/caching
  - **Session State**: https://docs.streamlit.io/develop/concepts/architecture/session-state
  - **Layouts**: https://docs.streamlit.io/develop/api-reference/layout
  - **API Reference**: https://docs.streamlit.io/develop/api-reference
- **Requirement:** When building for Snowflake, cross-reference Streamlit in Snowflake docs for differences in behavior, security context, and supported features: https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit
- **Requirement:** When deploying open-source Streamlit via SPCS, follow SPCS docs for container build, networking, and runtime specifics: https://docs.snowflake.com/en/developer-guide/snowpark-container-services

## Quick Compliance Checklist
- [ ] App loads in under 2 seconds (Fast First Paint achieved)
- [ ] Page config set with title, icon, and layout
- [ ] Theme configuration defined in .streamlit/config.toml when customization needed
- [ ] Consistent color scheme using primaryColor, backgroundColor, secondaryBackgroundColor, textColor
- [ ] Font selection appropriate for application context (sans serif, serif, monospace)
- [ ] Session state initialized explicitly at app start
- [ ] Database queries cached with appropriate TTL
- [ ] Error handling implemented with user-friendly messages
- [ ] Responsive layout using st.columns and container_width=True
- [ ] Modular structure with pages/ and components/ directories
- [ ] No raw exception traces shown to users
- [ ] Help text provided for complex widgets
- [ ] Navigation uses st.page_link, not buttons
- [ ] Deployment type verified (SiS vs open-source on SPCS) and correct docs followed
- [ ] Configuration compatibility verified for deployment target (SiS vs SPCS)

## Validation
- **Success checks:** App loads <2s, caching reduces query time, responsive on mobile/desktop, error states handled gracefully, theme applied consistently, configuration loaded properly
- **Negative tests:** Break database connection (should show error message), disable cache (should show performance impact), test with malformed data (should not crash), test with invalid config.toml (should use defaults gracefully)

## Response Template

### .streamlit/config.toml
```toml
[theme]
base = "light"
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false
```

### Main Application
```python
import streamlit as st
from snowflake.connector import connect

# Page configuration with theme awareness
st.set_page_config(
    page_title="App Name",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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
- [Streamlit Configuration](https://docs.streamlit.io/develop/concepts/configuration) - Complete guide to Streamlit configuration options and theming
- [Configuration and Theming Tutorial](https://docs.streamlit.io/develop/tutorials/configuration-and-theming) - Step-by-step tutorial on customizing app themes and configuration
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference) - Complete API reference for all Streamlit components
- [Streamlit Multipage Apps](https://docs.streamlit.io/get-started/tutorials/create-a-multipage-app) - Tutorial on multi-page structure, naming, and navigation
- [Snowflake Streamlit Guide](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit) - Snowflake-specific Streamlit integration documentation
- [Snowpark Container Services (SPCS)](https://docs.snowflake.com/en/developer-guide/snowpark-container-services) - Deploying and operating containerized apps (open-source Streamlit) on Snowflake

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Snowflake Notebooks**: `109-snowflake-notebooks.md`
- **Python Core**: `200-python-core.md`
- **Snowpark Container Services**: `120-snowflake-spcs.md`
