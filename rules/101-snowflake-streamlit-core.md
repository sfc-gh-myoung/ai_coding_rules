# Streamlit Core: Setup, Navigation, and State Management

**CRITICAL: Load for ALL Streamlit tasks. Specialized rules (101a-101e) depend on this.**

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.1
**LastUpdated:** 2026-01-27
**Keywords:** Streamlit, SiS, SPCS, navigation, multipage, session state, config.toml, theming
**TokenBudget:** ~1600
**ContextTier:** High
**Depends:** 100-snowflake-core.md
**LoadTrigger:** kw:streamlit, kw:dashboard

## Scope

**What This Rule Covers:**
Foundational Streamlit setup: navigation, state management, deployment (SiS vs SPCS), theming via config.toml.

**When to Load:**
- Building Streamlit applications on Snowflake
- Implementing multipage apps
- Configuring navigation and themes
- Deploying to SiS or SPCS

## References

### Dependencies
**Must Load First:** 100-snowflake-core.md

**Related:** 101a (visualization), 101b (performance), 101c (security)

### External Documentation
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Streamlit Navigation](https://docs.streamlit.io/develop/api-reference/navigation)

## Contract

### Inputs and Prerequisites
- Python 3.11+ with Streamlit 1.46+
- Snowflake connection configured
- Deployment mode identified (SiS vs SPCS)

### Mandatory
- **Deployment mode:** Verify SiS vs SPCS first
- **Theming:** Use .streamlit/config.toml ONLY
- **Navigation:** st.navigation() OR pages/ (never both)
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

## Deployment Mode Selection

### When to Use SiS
- Rapid prototyping, internal dashboards
- Snowflake-integrated apps (no external APIs)
- Teams without containerization expertise
- Zero infrastructure management

**Limitations:** Limited packages, managed Streamlit version, no custom system deps.

### When to Use SPCS
- Custom packages needed
- External API integrations
- Full runtime control

**Requirements:** Docker expertise, higher operational overhead.

### SiS environment.yml (CRITICAL)
**Forbidden in SiS:**
- `python=X.Y` declarations
- Version specifiers (`>=`, `==`)
- Non-snowflake channels

```yaml
# CORRECT
name: my_app
channels:
  - snowflake
dependencies:
  - streamlit
  - pandas
  - plotly
```

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
