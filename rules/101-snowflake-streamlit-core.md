# Streamlit Core: Setup, Navigation, and State Management

> **CORE RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential Streamlit patterns. Load for Streamlit tasks.
> Specialized rules depend on this foundation.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Streamlit, SPCS, SiS, navigation, multipage, session state, st.connection, config.toml, theming, deployment, pandas, null handling, session management
**TokenBudget:** ~4500
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md

## Purpose
Provide foundational guidance for Streamlit application setup, navigation patterns, state management, deployment mode selection (SiS vs SPCS), and theming configuration using config.toml as the primary styling method.

## Rule Scope

Streamlit core application architecture, multipage navigation, deployment modes, configuration management

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Deployment mode:** Verify SiS vs SPCS first (different capabilities)
- **Theming:** Use .streamlit/config.toml ONLY (no custom CSS)
- **Navigation:** st.navigation() (recommended) or pages/ directory (never both)
- **Page config:** Call st.set_page_config() ONCE in entrypoint only
- **State:** Initialize st.session_state at top level
- **Secrets:** Use st.secrets (never hardcode credentials)
- **Layout:** Native components only (st.columns, st.container, st.sidebar)

## Contract

<contract>
<inputs_prereqs>
Python 3.11+, Streamlit 1.46+, Snowflake connection, project structure with pages/ and/or st.navigation(), .streamlit/config.toml for theming, deployment mode identified (SiS vs SPCS)
</inputs_prereqs>

<mandatory>
st.navigation(), st.Page(), st.page_link(), st.switch_page(), st.set_page_config(), st.session_state, st.sidebar, st.columns, st.container, config.toml theme configuration (PRIMARY styling method), st.secrets
</mandatory>

<forbidden>
Custom CSS/HTML injection via st.markdown(unsafe_allow_html=True), inline style attributes, JavaScript injection, buttons for navigation (use st.page_link or st.switch_page), hardcoded theme values, hardcoded secrets/credentials
</forbidden>

<steps>
1. Verify deployment mode (SiS vs SPCS) and apply correct configuration
2. Set page config once in entrypoint file (title, icon, layout)
3. Configure .streamlit/config.toml for all theming and styling
4. Initialize session state at top level
5. Implement navigation using st.navigation() (recommended) or pages/ directory
6. Use native Streamlit layout components (st.columns, st.container, st.sidebar)
7. Configure secrets management (st.secrets)
</steps>

<output_format>
Streamlit app with proper navigation, consistent theming via config.toml, secure configuration, responsive layout using native components
</output_format>

<validation>
Test navigation flow, verify theme loaded from config.toml, validate responsive design, check secrets loading, test multipage state persistence
</validation>

<design_principles>
- **Deployment First:** Verify SiS vs SPCS deployment mode before implementation
- **Configuration Over Code:** Use config.toml for all styling (no custom CSS/HTML)
- **Native Components:** Leverage Streamlit's built-in layout system
- **State Management:** Centralized session state initialization
- **Security:** Use st.secrets for all credentials, never hardcode
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using buttons for navigation**
```python
if st.button("Go to Settings"):
    st.switch_page("pages/settings.py")  # Unreliable UX
```
**Problem:** Buttons trigger on click but don't persist state; causes navigation issues

**Correct Pattern:**
```python
# Primary navigation in entrypoint
pg = st.navigation([home, settings])
pg.run()

# Or inline link in content
st.page_link("pages/settings.py", label="Settings", icon=":gear:")
```

**Anti-Pattern 2: Custom CSS injection**
```python
st.markdown("""
    <style>
    .my-custom-class {
        background-color: #FF6B6B;
        padding: 20px;
    }
    </style>
    <div class="my-custom-class">Content</div>
""", unsafe_allow_html=True)
```
**Problem:** Unreliable across Streamlit versions and deployment modes (especially SiS)

**Correct Pattern:**
```python
# In .streamlit/config.toml:
# [theme]
# primaryColor = "#FF6B6B"
# secondaryBackgroundColor = "#F0F2F6"

with st.container(border=True):
    st.markdown("Content")  # Styled via config.toml
```

**Anti-Pattern 3: Mixing st.navigation() with pages/ directory**
```python
pg = st.navigation([...])  # This disables pages/ directory!
```
**Problem:** When st.navigation() is used, pages/ directory is completely ignored

**Correct Pattern - Choose one:**
```python
# Recommended: st.navigation()
pg = st.navigation(pages)
pg.run()
```

**Anti-Pattern 4: Setting page config in child pages**
```python
# In pages/dashboard.py
st.set_page_config(...)  # Error - only in entrypoint!
```
**Problem:** st.set_page_config() can only be called once in the entrypoint file

**Correct Pattern:**
```python
# streamlit_app.py (entrypoint only)
st.set_page_config(title="My App", layout="wide")
pg = st.navigation([home, settings])
pg.run()  # Critical!
```

## Post-Execution Checklist
- [ ] Deployment mode verified (SiS vs SPCS) and correct configuration applied
- [ ] st.set_page_config() called ONCE in entrypoint only (never in page files)
- [ ] .streamlit/config.toml PRIMARY styling method (NO custom CSS/HTML)
- [ ] Navigation uses st.navigation() (recommended) or pages/ directory (never both)
- [ ] Session state initialized at top level with explicit variable names
- [ ] st.secrets used for ALL credentials (never hardcoded)
- [ ] Native layout components only (st.columns, st.container, st.sidebar)
- [ ] pg.run() called after st.navigation() to execute selected page
- [ ] Theme configuration tested and in version control
- [ ] Responsive design tested on mobile/tablet viewports

## Validation
- **Success Checks:** App loads <2s, navigation works correctly, theme applied from config.toml, secrets loaded without errors, responsive layout works on mobile/desktop, state persists across page changes
- **Negative Tests:** Try setting page config in child page (should error), test navigation without pg.run() (should not execute), verify custom CSS doesn't work in SiS deployment, test with missing secrets (should fail gracefully)

> **Investigation Required**
> When applying this rule:
> 1. Read Streamlit app files BEFORE making recommendations
> 2. Verify .streamlit/config.toml exists and check theme configuration
> 3. Check actual navigation pattern (st.navigation() vs pages/ directory)
> 4. Verify deployment mode (SiS vs SPCS) from project context or environment.yml
> 5. Never speculate about component usage - inspect the code
> 6. Check st.secrets configuration and usage patterns

## Output Format Examples
```python
# streamlit_app.py (entrypoint file)
import streamlit as st

# Page configuration (ONCE, entrypoint only)
st.set_page_config(
    page_title="My App",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Shared sidebar widgets
with st.sidebar:
    environment = st.selectbox(
        "Environment",
        ["Development", "Production"],
        key="env_filter"
    )
    st.divider()

# Define pages with customization
pages = {
    "Main": [
        st.Page("pages/home.py", title="Home", icon="🏠", default=True),
        st.Page("pages/dashboard.py", title="Dashboard", icon=""),
    ],
    "Account": [
        st.Page("pages/settings.py", title="Settings", icon=":gear:")
    ]
}

# Configure and run navigation
pg = st.navigation(pages, position="sidebar", expanded=True)
pg.run()
```

## References

### External Documentation

**Core Streamlit Documentation:**
- [Streamlit Documentation](https://docs.streamlit.io/) - Official Streamlit application development guide
- [App Design Concepts](https://docs.streamlit.io/develop/concepts/design) - Comprehensive UI/UX design patterns
- [Theming Overview](https://docs.streamlit.io/develop/concepts/configuration/theming) - Complete guide to theme customization using config.toml
- [Configuration Options](https://docs.streamlit.io/develop/concepts/configuration) - Complete configuration reference

**Navigation:**
- [Streamlit Navigation and Pages](https://docs.streamlit.io/develop/api-reference/navigation) - Modern multipage navigation API
- [st.navigation()](https://docs.streamlit.io/develop/api-reference/navigation/st.navigation) - Configure pages and navigation UI
- [st.Page()](https://docs.streamlit.io/develop/api-reference/navigation/st.page) - Define and customize individual pages
- [st.page_link()](https://docs.streamlit.io/develop/api-reference/navigation/st.page_link) - Create inline links between pages
- [st.switch_page()](https://docs.streamlit.io/develop/api-reference/navigation/st.switch_page) - Programmatic page navigation
- [Dynamic Navigation Tutorial](https://docs.streamlit.io/develop/tutorials/multipage/dynamic-navigation) - Advanced navigation patterns

**Layout:**
- [Layout API Reference](https://docs.streamlit.io/develop/api-reference/layout) - Complete layout component documentation
- [st.columns()](https://docs.streamlit.io/develop/api-reference/layout/st.columns) - Multi-column responsive layouts
- [st.container()](https://docs.streamlit.io/develop/api-reference/layout/st.container) - Content grouping and bordered sections
- [st.sidebar](https://docs.streamlit.io/develop/api-reference/layout/st.sidebar) - Persistent sidebar panel

**Snowflake Integration:**
- [Snowflake Streamlit Guide](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit) - Snowflake-specific Streamlit integration
- [Snowpark Container Services (SPCS)](https://docs.snowflake.com/en/developer-guide/snowpark-container-services) - Deploying containerized Streamlit apps

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **App Deployment**: `rules/109b-snowflake-app-deployment-core.md`
- **Streamlit Visualization**: `rules/101a-snowflake-streamlit-visualization.md`
- **Streamlit Performance**: `rules/101b-snowflake-streamlit-performance.md`
- **Streamlit Security**: `rules/101c-snowflake-streamlit-security.md`
- **Streamlit Testing**: `rules/101d-snowflake-streamlit-testing.md`
- **Python Core**: `rules/200-python-core.md`
- **Snowpark Container Services**: `rules/120-snowflake-spcs.md`

> **[AI] Claude 4 Specific Guidance**
> **Claude 4 Streamlit Core Optimizations:**
> - Parallel file reading: Load config.toml and all page files simultaneously when analyzing multipage apps
> - Context awareness: Efficiently manage token budget across multiple Streamlit rule files (core + specialized)
> - Investigation-first: Excel at discovering config.toml theme settings and navigation structure from filesystem
> - State discovery: Can track st.session_state usage patterns across multiple page files

## 1. Deployment Mode Selection: SiS vs SPCS

**MANDATORY:**
**Choosing the right deployment mode is critical for long-term success.**

### When to Use Streamlit in Snowflake (SiS)

**Best For:**
- Rapid prototyping and MVP development (minutes to first app)
- Internal BI dashboards for Snowflake users
- Applications tightly integrated with Snowflake (no external APIs)
- Teams without containerization/DevOps expertise
- Cost-sensitive projects (no external compute costs)

**Advantages:**
- Zero infrastructure management
- Instant deployment (CREATE STREAMLIT command)
- Native Snowflake authentication and authorization
- Direct access to Snowflake data without connectors

**Limitations:**
- Limited to Snowflake-approved packages (see package list)
- Streamlit version managed by Snowflake (may lag latest)
- Cannot use custom system dependencies (e.g., C libraries)
- Limited control over Python version and runtime
- No integration with external services requiring custom networking

### When to Use Open-Source Streamlit on SPCS

**Best For:**
- Production applications requiring custom packages
- Need for specific Python/system dependencies
- Fine-grained control over runtime environment
- Integration with external services/APIs
- Multi-tenant applications with custom isolation

**Advantages:**
- Full control over dependencies (any Python package)
- Custom system libraries and binaries
- Latest Streamlit version immediately available
- Integration with external services and APIs
- Advanced container orchestration options

**Requirements:**
- Docker/containerization expertise required
- Additional operational overhead (container management)
- More complex deployment pipeline
- Higher cost (compute services + Snowflake credits)

**MANDATORY:**
**Always verify the deployment mode first** and apply the correct configuration, best practices, and documentation. Do not mix SiS and open-source Streamlit recommendations.

### SiS Environment Configuration (environment.yml)

**CRITICAL for Streamlit in Snowflake (SiS) Deployments:**

The `environment.yml` file for SiS has **strict requirements** that differ from local Conda environments:

**Forbidden in SiS:**
- **Python version specification:** `python=3.11` or any `python=X.Y` declaration
- **Multiple channels:** Only `snowflake` channel is supported
- **Unsupported channels:** `conda-forge`, `defaults`, or any non-Snowflake channels
- **Version specifiers:** Cannot use `>=`, `==`, `>`, `<`, `<=`, `~=` operators
- **Package name format:** Must be lowercase with only `[.-_]` special characters

**Why These Restrictions Exist:**
- Python runtime is managed by Snowflake (version controlled at platform level)
- Package availability limited to Snowflake-approved packages in `snowflake` channel
- Package versions are managed by Snowflake (cannot be user-specified)
- Strict parser requirements for dependency name syntax
- Specifying unsupported channels, Python versions, or version operators causes deployment errors

**Common Errors:**
```
Error 1: Unsupported channel
An error occurred while loading the app. Error: Anaconda channel
conda-forge,defaults is not supported. Allowed channels are:
https://repo.anaconda.com/pkgs/snowflake,nodefaults,snowflake
```

```
Error 2: Version specifier syntax
An error occurred while loading the app. Error: Anaconda dependency names
must be lowercase characters, numbers or one of [.-_]. streamlit>=1.30.0
does not match this spec.
```

**Correct SiS environment.yml Pattern:**
```yaml
# Snowflake Streamlit Environment Configuration
# IMPORTANT: Python version is managed by Snowflake - do not specify python=X.Y
# IMPORTANT: Only 'snowflake' channel is supported in SiS environments
# IMPORTANT: No version specifiers allowed - list package names only

name: my_app

channels:
  - snowflake

dependencies:
  - streamlit
  - pandas
  - plotly
  # Package names only - no version specifiers
  # Versions managed by Snowflake's environment
```

**Incorrect Patterns (will fail deployment):**
```yaml
# BAD: Multiple channels and Python version
name: my_app

channels:
  - snowflake
  - conda-forge  # ✗ Not supported in SiS
  - defaults     # ✗ Not supported in SiS

dependencies:
  - python=3.11  # ✗ Cannot specify Python version in SiS
  - streamlit
```

```yaml
# BAD: Version specifiers not allowed
name: my_app

channels:
  - snowflake

dependencies:
  - streamlit>=1.30.0   # ✗ Version operators not supported
  - pandas==2.0.0       # ✗ Version pinning not supported
  - plotly>5.0          # ✗ Any version specifier fails
```

**Validation Checklist:**
- [ ] Remove any `python=X.Y` lines from dependencies
- [ ] Remove ALL version specifiers (`>=`, `==`, `>`, `<`, `<=`, `~=`)
- [ ] Ensure only `snowflake` channel is listed
- [ ] Verify package names are lowercase with only `[.-_]` special characters
- [ ] Confirm all packages exist in Snowflake's approved package list
- [ ] Reference: [Snowflake Third-Party Packages](https://repo.anaconda.com/pkgs/snowflake/)

**Key Takeaway:** SiS environment.yml files should contain **only package names** - no versions, no Python specification, no custom channels. Snowflake manages all versions automatically.

## 2. Setup and Project Structure

### Basic Setup
**MANDATORY:**
- **Always:** Call `st.set_page_config` in the entrypoint file to set title, icon, and layout (call only once, never in individual pages)
- **Always:** Initialize session state once at the top level to keep state consistent across re-runs
- **Always:** Place reusable UI elements (charts, forms) in a `components/` directory

**Example:**
```python
# streamlit_app.py (entrypoint file)
import streamlit as st

# Page configuration (ONCE, entrypoint only)
st.set_page_config(
    page_title="My App",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
```

## 3. Multipage Navigation (Streamlit 1.26+)

**MANDATORY:**
- **Requirement:** Use `st.navigation()` in your entrypoint file for dynamic multipage apps (**recommended pattern**)
- **Alternative:** Use `pages/` directory for very simple apps (legacy pattern with no customization)
- **Critical:** When `st.navigation()` is used, the `pages/` directory is ignored across all sessions
- **Always:** The entrypoint file (passed to `streamlit run`) acts as a router and executes on every rerun
- **Always:** Call `.run()` on the returned page object to execute the selected page

**Basic Navigation Example:**
```python
# streamlit_app.py (entrypoint)
import streamlit as st

st.set_page_config(page_title="My App", page_icon="", layout="wide")

# Define pages
home = st.Page("pages/home.py", title="Home", icon="🏠", default=True)
settings = st.Page("pages/settings.py", title="Settings", icon=":gear:")

# Configure and run
pg = st.navigation([home, settings])
pg.run()
```

**Grouped Navigation:**
```python
# Use dictionary for sections
pages = {
    "Account": [
        st.Page("create.py", title="Create Account"),
        st.Page("manage.py", title="Manage Account"),
    ],
    "Resources": [
        st.Page("learn.py", title="Learn"),
    ],
}
pg = st.navigation(pages, position="sidebar")  # or "top" or "hidden"
pg.run()
```

**Navigation Position Options:**
- `position="sidebar"` (default): Vertical sidebar navigation
- `position="top"`: Horizontal top navigation with collapsible sections
- `position="hidden"`: No UI (programmatic navigation only)
- `expanded=True/False`: Control sidebar expansion (sidebar only)

**Shared Widgets Across Pages:**
```python
# Define in entrypoint file with explicit keys
st.sidebar.selectbox("Environment", ["Dev", "Prod"], key="env_filter")

pg = st.navigation([page1, page2])
pg.run()

# Access in any page: st.session_state.env_filter
```

**Navigation Methods:**
- Use `st.page_link()` for inline links within page content
- Use `st.switch_page()` for programmatic navigation (e.g., after form submission)
- Never use `st.button()` for navigation (use for actions only)

## 4. Configuration and Theming

### Core Theming Philosophy
**FORBIDDEN:**
- **Critical:** `.streamlit/config.toml` is the PRIMARY and RECOMMENDED method for all layout and styling customization
- **Forbidden:** Custom CSS/HTML injection via `st.markdown()` with `unsafe_allow_html=True` - unreliable across Streamlit versions and deployment modes
- **Always:** Use native Streamlit components and configuration options for consistent, maintainable styling
- **Reference:** Official [Theming Documentation](https://docs.streamlit.io/develop/concepts/configuration/theming) for complete customization options

### Base Theme Configuration
```toml
# .streamlit/config.toml
[theme]
# Inherit from Streamlit's light or dark theme
base = "light"  # or "dark"
```

### Color and Border Customization
```toml
[theme]
primaryColor = "#FF6B6B"              # Interactive elements, highlights
backgroundColor = "#FFFFFF"            # Main app background
secondaryBackgroundColor = "#F0F2F6"  # Sidebar, widgets, code blocks
textColor = "#262730"                  # Body text

# Border configuration
borderColor = "#E6E6E6"        # Element borders
showWidgetBorder = true        # Widget border visibility
borderRadius = "0.5rem"        # Element roundness
```

### Font Configuration
```toml
[theme]
font = "sans serif"  # "sans serif", "serif", or "monospace"

# Advanced: separate control for body, heading, code
[[theme.fontFace]]
family = "Inter, sans-serif"
weight = 400
size = "1rem"
lineHeight = 1.6

[[theme.fontFace]]
family = "Inter, sans-serif"
weight = 700
size = "1.25rem"
target = "heading"

[[theme.fontFace]]
family = "JetBrains Mono, monospace"
weight = 400
size = "0.875rem"
target = "code"
```

### Chart Color Configuration
```toml
[theme]
# Chart series colors (applied in order)
chartColors = [
    "#FF6B6B",  # Series 1
    "#4ECDC4",  # Series 2
    "#45B7D1",  # Series 3
    "#FFA07A",  # Series 4
    "#98D8C8"   # Series 5
]
```

### Complete Theme Example
```toml
# .streamlit/config.toml - Complete theme configuration
[theme]
base = "light"
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

# Border configuration
borderColor = "#E6E6E6"
showWidgetBorder = true
borderRadius = "0.5rem"

# Chart colors
chartColors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"]

[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false
```

## 5. State Management

**MANDATORY:**
- **Requirement:** Manage state predictably with `st.session_state` and callbacks for complex updates
- **Always:** Initialize all session state variables explicitly at top level
- **Always:** Use widget keys for stable identity across reruns
- **Avoid:** Overwriting session state in widget callbacks

**Example:**
```python
# Initialize state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# Use callbacks for complex state updates
def login_callback():
    st.session_state.authenticated = True
    st.session_state.user_data = fetch_user_data()

st.button("Login", on_click=login_callback)
```

## 6. Layout Components

**MANDATORY:**
**Use native Streamlit layout components as primary layout tools:**

**st.columns() - Multi-column Layouts:**
```python
# Equal width columns
col1, col2, col3 = st.columns(3)

# Custom width ratios (1:2:1 ratio)
col1, col2, col3 = st.columns([1, 2, 1])

# Use columns for KPI cards
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Revenue", "$1.2M", "+12%")
with col2:
    st.metric("Users", "8,432", "+5%")
with col3:
    st.metric("Conversion", "3.2%", "-0.3%")
```

**st.container() - Grouped Content:**
```python
# Bordered container for grouped content
with st.container(border=True):
    st.markdown("### Section Title")
    st.write("Content grouped logically...")

# Containers for out-of-order rendering
container = st.container()
st.write("This appears second")
container.write("This appears first")
```

**st.sidebar - Persistent Side Panel:**
```python
# Sidebar filters
with st.sidebar:
    st.markdown("### Filters")
    date_range = st.date_input("Date Range", [start_date, end_date])
    status = st.selectbox("Status", ["All", "Active", "Inactive"])
```

## 7. Secrets Management

**MANDATORY:**
- **Mandatory:** Use `st.secrets` for all sensitive configuration (API keys, passwords, tokens)
- **Mandatory:** Never hardcode credentials in source code
- **Always:** For SiS, use Snowflake secrets management
- **Always:** For SPCS, use Kubernetes secrets or environment variables
- **Always:** Validate that required secrets exist before use

**Secrets Pattern:**
```python
# [PASS] Proper secrets usage
try:
    api_key = st.secrets["api"]["key"]
    db_password = st.secrets["database"]["password"]
except KeyError as e:
    st.error(f"Missing required secret: {e}")
    st.stop()

# Never do this
api_key = "sk-1234567890abcdef"  # Hardcoded secret!
```

## 8. Pandas NULL Handling: Snowflake NULL vs Python None

**MANDATORY:**

### Critical Difference: NaN vs None

When Snowflake returns NULL values, pandas converts them to NaN (Not a Number), NOT Python None. This requires pandas-aware null checking.

**Anti-Pattern (WILL CRASH):**
```python
# BAD: is not None doesn't catch pandas NaN
file_size = df["SIZE"].iloc[0]
if file_size is not None and file_size > 0:
    display = f"{file_size / 1024:.1f} KB"  # CRASHES if NaN
else:
    display = "Unknown"
```

**Correct Pattern:**
```python
# GOOD: pd.notna() correctly identifies NaN
import pandas as pd

file_size = df["SIZE"].iloc[0]
if pd.notna(file_size) and file_size > 0:
    display = f"{file_size / 1024:.1f} KB"  # Safe
else:
    display = "Unknown"
```

### Format String Safety Rules

**Rule**: Never apply format specifiers (`.1f`, `.0f`, `.2%`) to values that might be NULL/NaN without validation

**Rule**: Use pandas null-checking functions for DataFrame values:
- `pd.notna(value)` - True if NOT null/NaN
- `pd.isna(value)` - True if null/NaN
- `pd.isnull(value)` - Alias for pd.isna()

**Rule**: Create helper functions for repeated formatting patterns:

```python
def safe_format_duration(seconds, default="Unknown"):
    """Safely format duration with NULL handling."""
    if pd.isna(seconds) or seconds is None:
        return default
    return f"{seconds:.1f} seconds" if seconds < 60 else f"{int(seconds // 60)}m {seconds % 60:.0f}s"

def safe_format_file_size(bytes_value, default="Unknown"):
    """Safely format file size with pandas-aware NULL handling."""
    if pd.isna(bytes_value) or bytes_value is None or bytes_value <= 0:
        return default
    return f"{bytes_value / 1024:.1f} KB"
```

### Defense in Depth Pattern

**Rule**: Wrap database value display in try-except blocks:

```python
try:
    file_info = df[df["PATH"] == selected_file].iloc[0]
    size_display = safe_format_file_size(file_info.get("SIZE"))
    st.info(f"File: {selected_file} | Size: {size_display}")
except Exception as e:
    st.info(f"File: {selected_file} | Size: Unknown")
    st.caption(f"Could not retrieve file size: {str(e)}")
```

### Common NULL Sources in Snowflake

Values that commonly return NULL and require pandas-aware handling:
- DIRECTORY() function: SIZE, LAST_MODIFIED
- AI_TRANSCRIBE: duration_seconds (when audio format unsupported)
- Aggregate functions: AVG(), SUM() on empty sets
- External table metadata: FILE_SIZE, ROW_COUNT
- User-defined columns with missing data

### Quick Decision Guide

**Question**: Does this value come from a pandas DataFrame?
- Yes: Use `pd.notna()` or `pd.isna()`
- No: Use `is not None` or `is None`

**Question**: Am I applying format specifiers (`.1f`, `.0f`)?
- Yes: MUST validate not NULL/NaN first
- No: Still validate for display purposes

## Related Rules

**Closely Related** (consider loading together):
- `101b-snowflake-streamlit-performance` - For caching strategies, query optimization, error handling
- `101a-snowflake-streamlit-visualization` - For chart types, customization, and visualization best practices

**Sometimes Related** (load if specific scenario):
- `101c-snowflake-streamlit-security` - When implementing authentication, authorization, secure credentials
- `103-snowflake-performance-tuning` - When optimizing underlying Snowflake queries
- `109-snowflake-notebooks` - When combining notebook development with Streamlit deployment

**Complementary** (different aspects of same domain):
- `107-snowflake-security-governance` - For RBAC and security policies in Streamlit apps
- `111-snowflake-observability-core` - For monitoring Streamlit app performance and errors
