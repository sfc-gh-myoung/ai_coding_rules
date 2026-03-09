# Streamlit Core: Setup, Navigation, and State Management

**CRITICAL: Load for ALL Streamlit tasks. Specialized rules (101a-101e) depend on this.**

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v4.1.0
**LastUpdated:** 2026-03-09
**Keywords:** Streamlit, Container Runtime, Warehouse Runtime, navigation, multipage, session state, config.toml, theming, st.connection
**TokenBudget:** ~2050
**ContextTier:** High
**Depends:** 100-snowflake-core.md
**LoadTrigger:** kw:streamlit, kw:dashboard

## Scope

**What This Rule Covers:**
Foundational Streamlit setup: navigation, state management, runtime selection (Container vs Warehouse), theming via config.toml.

**When to Load:**
- Building Streamlit applications on Snowflake
- Implementing multipage apps
- Configuring navigation and themes
- Selecting between Container Runtime and Warehouse Runtime

## References

### Dependencies
**Must Load First:** 100-snowflake-core.md

**Related:** 101a (visualization), 101b (performance), 101c (security), 101l (deployment)

### External Documentation
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Runtime Environments](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/runtime-environments)
- [Streamlit Navigation](https://docs.streamlit.io/develop/api-reference/navigation)

## Contract

### Inputs and Prerequisites
- Python 3.11+ with Streamlit 1.50+
- Snowflake connection configured
- Runtime selected (Container Runtime recommended, see 101l)

### Mandatory
- **Runtime selection:** Choose Container or Warehouse Runtime (see 101l-snowflake-streamlit-deployment)
- **Connection:** Use `st.connection("snowflake")` for both runtimes
- **Theming:** Use .streamlit/config.toml ONLY
- **Navigation:** st.navigation() OR pages/ (never both)
  - `pages/` directory approach (auto-discovered):
    ```
    app.py          # entrypoint
    pages/1_Home.py
    pages/2_Dashboard.py
    ```
- **Page config:** st.set_page_config() ONCE in entrypoint only
- **State:** Initialize st.session_state at top level
- **Secrets:** Use st.secrets (never hardcode)

### Forbidden
- Custom CSS/HTML injection via unsafe_allow_html=True
- Buttons for navigation
- Hardcoded secrets
- Mixing st.navigation() with pages/
- Multiple st.set_page_config() calls

### Execution Steps
1. Verify deployment mode (SiS vs SPCS)
2. Set page config once in entrypoint
3. Configure .streamlit/config.toml for theming
4. Initialize session state at top level
5. Implement navigation (st.navigation() recommended)
6. Use native layout components
7. Configure secrets management

### Output Format
```python
# app.py (entrypoint)
import streamlit as st

st.set_page_config(page_title="App", page_icon="🏔️", layout="wide")

if "user_id" not in st.session_state:
    st.session_state.user_id = None

pg = st.navigation([
    st.Page("pages/home.py", title="Home", icon="🏠"),
    st.Page("pages/dashboard.py", title="Dashboard", icon="📊"),
])
pg.run()
```

### Validation
- st.set_page_config() called once
- Theme via config.toml
- Navigation works
- Session state persists
- Secrets loading securely

### Post-Execution Checklist
- [ ] st.set_page_config() ONCE in entrypoint
- [ ] Theme in config.toml
- [ ] Secrets via st.secrets
- [ ] Navigation implemented
- [ ] Session state initialized
- [ ] No custom CSS injection

## Error Recovery

- **Navigation failure (page file not found):** Verify file exists in pages/ directory with `LIST @STAGE`. Check filename matches exactly (case-sensitive).
- **Session state corruption:** Clear with `del st.session_state[key]` or full reset by clearing all keys in a loop.
- **Stage upload compressed files:** Detect with `LIST @STAGE PATTERN='.*\\.gz'`; re-upload with `--no-auto-compress`.

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Buttons for Navigation
```python
# WRONG
if st.button("Go to Settings"):
    st.switch_page("pages/settings.py")
```
**Problem:** Buttons don't persist state; causes navigation issues.

**Correct Pattern:**
```python
pg = st.navigation([home, settings])
pg.run()
# Or inline: st.page_link("pages/settings.py", label="Settings")
```

### Anti-Pattern 2: Custom CSS Injection
```python
# WRONG
st.markdown("<style>.my-class { color: red; }</style>", unsafe_allow_html=True)
```
**Problem:** Unreliable across versions and deployment modes.

**Correct Pattern:** Use .streamlit/config.toml for all theming.

## Runtime Selection

**See 101l-snowflake-streamlit-deployment.md for complete deployment guidance.**

Use Container Runtime when you need custom Python packages, external API access, or Streamlit 1.50+ features. Use Warehouse Runtime for simple apps that only need Snowflake-bundled Anaconda packages and no external network access.

### Container Runtime (Recommended)
- Long-running service with shared instance
- Uses `pyproject.toml` with PyPI packages via `uv`
- Requires External Access Integration (EAI)
- Python 3.11, Streamlit 1.50+
- Best for: Custom packages, external APIs, production apps

### Warehouse Runtime
- On-demand, per-viewer instances
- Uses `environment.yml` with Snowflake Anaconda Channel
- No EAI required (no external network access)
- Python 3.9-3.11
- Best for: Rapid prototyping, internal dashboards, no external dependencies

### Connection Pattern (Both Runtimes)
```python
# Recommended - works in both runtimes
conn = st.connection("snowflake")
df = conn.query("SELECT col1, col2 FROM my_table")
```

**Connection errors:** Wrap `st.connection()` in try/except for production apps. See 100f-snowflake-connection-errors.md for error classification and retry patterns.

### Stage Upload Requirements
**All `.py` and config files uploaded to a Streamlit stage MUST disable compression.**

```bash
# CLI: --no-auto-compress is MANDATORY
snow stage copy streamlit/ @STAGE --recursive --no-auto-compress --overwrite
```

```sql
-- SQL: AUTO_COMPRESS=FALSE is MANDATORY
PUT file://streamlit_app.py @STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```

Without this, Snowflake compresses files to `.py.gz`, causing silent import failures.

## Navigation

### st.navigation() (Recommended)
```python
home = st.Page("pages/home.py", title="Home", icon="🏠", default=True)
settings = st.Page("pages/settings.py", title="Settings", icon=":gear:")

pg = st.navigation([home, settings])
pg.run()
```

### Grouped Navigation
```python
pages = {
    "Account": [st.Page("create.py"), st.Page("manage.py")],
    "Resources": [st.Page("learn.py")],
}
pg = st.navigation(pages, position="sidebar")
pg.run()
```

### Navigation Position Options
- `position="sidebar"` (default)
- `position="top"` - horizontal
- `position="hidden"` - programmatic only

## Configuration and Theming

```toml
# .streamlit/config.toml
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
```

## State Management

```python
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login_callback():
    st.session_state.authenticated = True

st.button("Login", on_click=login_callback)
```

**Multi-user isolation:** Each user gets isolated session state. Do not use module-level variables for user-specific data — they are shared across all users in Container Runtime.

## Layout Components

```python
# Columns
col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Revenue", "$1.2M", "+12%")

# Container
with st.container(border=True):
    st.markdown("### Section")

# Sidebar
with st.sidebar:
    st.selectbox("Filter", ["All", "Active"])
```

## Secrets Management

```python
try:
    api_key = st.secrets["api"]["key"]
except KeyError as e:
    st.error(f"Missing secret: {e}")
    st.stop()
```

## Pandas NULL Handling

**Critical:** Snowflake NULL becomes pandas NaN, NOT Python None.

```python
# WRONG
if file_size is not None:
    display = f"{file_size:.1f}"  # Crashes on NaN!

# CORRECT
import pandas as pd
if pd.notna(file_size):
    display = f"{file_size:.1f}"  # Safe
```

Use `pd.notna(value)` or `pd.isna(value)` for DataFrame values.
