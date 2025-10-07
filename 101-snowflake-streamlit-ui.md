**Description:** Directives for creating modern, performant, and maintainable Streamlit applications for Snowflake.
**AppliesTo:** `**/*.py`, `streamlit/**/*`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.6
**LastUpdated:** 2025-10-01

**TokenBudget:** ~1700
**ContextTier:** Medium

# Streamlit UI/UX Directives

## Purpose
Provide comprehensive guidance for building modern, performant, and maintainable Streamlit applications within the Snowflake ecosystem, focusing on user experience, performance optimization, and modular architecture patterns.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Snowflake Streamlit application development, UI/UX patterns, and performance optimization

## Contract
- **Inputs/Prereqs:** Python 3.11+, Streamlit 1.46+, Snowflake connection, project structure with pages/ and components/, deployment mode identified (SiS vs OSS on SPCS), .streamlit/config.toml for theming, virtual environment for dependency management, secrets configured for sensitive data
- **Allowed Tools:** st.cache_data, st.cache_resource, st.session_state, st.set_page_config, config.toml, theme configuration, Snowflake connector, pandas/polars, Plotly (preferred for charts), Pydeck (preferred for maps), Altair (fallback), st.chat_message, st.chat_input, st.image, st.video, st.audio, st.secrets, pytest for testing
- **Forbidden Tools:** raw SQL loops, inline custom CSS blocks, unhandled exceptions in UI, hardcoded theme values, hardcoded secrets/credentials, buttons for navigation
- **Required Steps:** 1) Set page config with theme-aware settings, 2) Configure .streamlit/config.toml if needed, 3) Initialize session state, 4) Cache data operations, 5) Implement error handling, 6) Validate and sanitize user inputs, 7) Normalize column names from Snowflake, 8) Write unit tests for data processing functions, 9) Configure secrets management
- **Output Format:** Streamlit app with <2s load time, modular architecture, accessible UI, consistent theming, validated inputs, secure secrets handling, comprehensive error messages, passing tests
- **Validation Steps:** Test caching behavior, verify responsive design and theming, check error handling, validate accessibility, confirm configuration loading, test input validation, verify secrets loading, run unit tests, test with production-like data volumes, validate media asset loading, test chat persistence

## Key Principles
- **Performance:** Fast First Paint (<2s), modular architecture, deterministic state; cache data/resources appropriately.
- **Architecture:** Use page config, pages/ structure, components/ for reuse; avoid raw loops and re-creating connections.
- **Configuration:** Centralized configuration via config.toml; consistent theming across deployment modes (SiS vs SPCS).
- **User Experience:** Clear help text, responsive layouts, no raw exception traces; appropriate status feedback.
- **Security:** Validate all inputs, use st.secrets for credentials, never hardcode sensitive data.
- **Testing:** Write unit tests for data processing, test edge cases, validate with production-like data.
- **Documentation:** Inline help, tooltips, clear error messages; reference official docs and tutorial series.
- **Data Handling:** Normalize Snowflake column names, implement proper error handling, optimize media assets.

## Deployment Modes: Streamlit in Snowflake (SiS) vs Open-source (SPCS)
- **Streamlit in Snowflake (SiS):** Runs inside Snowflake with a managed runtime and security context. Use the Snowflake Streamlit docs for capabilities, limitations, auth, and secrets handling. Packaging and deployment differ from open-source.
- **Open-source Streamlit on SPCS:** Deployed as a containerized app via Snowpark Container Services (SPCS). Follow SPCS deployment, networking, image build, and secrets guidance. Configuration, environment, and recommended patterns can differ from SiS.
- **Always verify the deployment mode first** and apply the correct configuration, best practices, and documentation. Do not mix SiS and open-source Streamlit recommendations.

## 1. Setup and Structure
- **Always:** Call `st.set_page_config` in the entry point to set title, icon, and wide layout.
- **Always:** Initialize session state once at the top level to keep state consistent across re-runs.
- **Always:** Organize multi-page applications using the `pages/` directory structure ([Multipage Apps tutorial](https://docs.streamlit.io/get-started/tutorials/create-a-multipage-app)).
- **Always:** Place reusable UI elements (charts, forms) in a `components/` directory.

## 2. Performance and Caching
- **Requirement:** Cache database queries and data fetches with `@st.cache_data` and an appropriate `ttl`.
- **Requirement:** Cache expensive objects and connections (e.g., Snowflake connections) using `@st.cache_resource`.
- **Always:** Show user feedback for operations that may take time:
  - **2-5 seconds:** Use `st.spinner()` with descriptive message
  - **>5 seconds:** Use `st.progress()` with `st.status()` for detailed progress tracking
- **Requirement:** Avoid raw database query loops; fetch all needed data at once and cache it.

## 3. Configuration and Theming
- **Requirement:** Use `.streamlit/config.toml` for centralized configuration management and theme customization.
- **Requirement:** Define theme colors consistently using `[theme]` section: `primaryColor`, `backgroundColor`, `secondaryBackgroundColor`, `textColor`.
- **Requirement:** Configure fonts via `font` option ("sans serif", "serif", "monospace") for consistent typography.
- **Requirement:** Set `base` theme ("light" or "dark") as foundation before customizations.
- **Always:** For SiS deployments, verify theme configuration compatibility and limitations with Snowflake runtime.
- **Always:** For SPCS deployments, ensure config.toml is properly included in container image.
- **Avoid:** Hardcoding theme values in Python code; use centralized configuration instead.

## 4. UI/UX Design and State Management
- **Requirement:** Use `st.page_link` for navigation and `st.button` for actions; do not use buttons for navigation.
- **Requirement:** Centralize design tokens (colors, icons) in config.toml rather than hard-coding values.
- **Requirement:** Provide clear help text (`help="..."`) for complex widgets.
- **Requirement:** Manage state predictably with `st.session_state` and callbacks for complex updates.
- **Requirement:** Use responsive layouts with `st.columns`, `st.sidebar`, and `use_container_width=True` for charts.

## 5. Data Loading from Snowflake - Critical Column Name Gotcha

### Column Name Normalization
- **Critical:** Snowflake returns column names in **UPPERCASE** by default, which causes `KeyError` when accessing with lowercase.
- **Always:** Normalize column names to lowercase immediately after loading data from Snowflake.
- **Rule:** Apply normalization in data loader functions, not in UI code, to ensure consistency.

**Problem:**
```python
# ❌ This will fail with KeyError: 'asset_type'
df = session.table('GRID_ASSETS').to_pandas()
transformers = df[df['asset_type'] == 'TRANSFORMER']  # KeyError!
```

**Solution:**
```python
# ✓ Correct - Normalize column names to lowercase
df = session.table('UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS').to_pandas()
df.columns = [col.lower() for col in df.columns]  # Critical!
transformers = df[df['asset_type'] == 'TRANSFORMER']  # Works!
```

### Best Practices for Data Loaders
- **Always:** Normalize column names in cached data loader functions:
  ```python
  @st.cache_data(ttl=600)
  def load_grid_assets() -> pd.DataFrame:
      session = get_snowflake_session()
      df = session.table('UTILITY_DEMO_V2.GRID_DATA.GRID_ASSETS').to_pandas()
      # Normalize to lowercase for consistency
      df.columns = [col.lower() for col in df.columns]
      return df
  ```

- **Always:** Use fully qualified table names (`DATABASE.SCHEMA.TABLE`) to avoid context issues
- **Always:** Apply normalization to both `session.table().to_pandas()` and `session.sql(query).to_pandas()` results
- **Rule:** Document this normalization in function docstrings to inform other developers

### Why This Matters
- **Consistency:** Python code conventionally uses lowercase for column names (snake_case)
- **Portability:** Local dev environments may use lowercase; Snowflake uses uppercase
- **Error Prevention:** Prevents `KeyError` exceptions that are hard to debug in production
- **Best Practice:** Single normalization point in data loaders vs. scattered `.upper()` calls in UI code

## 6. Data Visualization

### Preferred Libraries
- **Charts and Graphs:** Use **Plotly** as the primary visualization library for interactive charts
- **Maps:** Use **Pydeck** as the primary library for geospatial visualizations
- **Fallback:** Altair and Matplotlib are acceptable alternatives when Plotly/Pydeck don't meet specific needs

### Plotly for Charts
- **Requirement:** Use Plotly Express (`plotly.express`) for most chart types (line, bar, scatter, histogram, box, etc.)
- **Always:** Use `st.plotly_chart(fig, use_container_width=True)` for responsive charts
- **Always:** Configure charts with clear titles, axis labels, and legends
- **Consider:** Use Plotly Graph Objects (`plotly.graph_objects`) for complex custom visualizations

**Plotly Best Practices:**
```python
import plotly.express as px
import plotly.graph_objects as go

# ✓ Simple interactive chart with Plotly Express
df = load_data()
fig = px.line(
    df, 
    x='date', 
    y='value',
    title='Time Series Analysis',
    labels={'value': 'Metric Value', 'date': 'Date'},
    hover_data=['category']
)
st.plotly_chart(fig, use_container_width=True)

# ✓ Customized chart with Graph Objects
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['date'],
    y=df['value'],
    mode='lines+markers',
    name='Actual'
))
fig.update_layout(
    title='Custom Visualization',
    xaxis_title='Date',
    yaxis_title='Value',
    hovermode='x unified'
)
st.plotly_chart(fig, use_container_width=True)
```

**Why Plotly:**
- **Interactivity:** Built-in hover, zoom, pan, and selection tools
- **Performance:** Efficient rendering for large datasets
- **Consistency:** Uniform API across chart types
- **Compatibility:** Works seamlessly in both SiS and SPCS deployments
- **Customization:** Extensive styling and configuration options

### Pydeck for Maps
- **Requirement:** Use Pydeck for all geospatial visualizations (points, heatmaps, hexagons, paths)
- **Always:** Pass minimal data to layers (only required columns: latitude, longitude, and needed attributes)
- **Always:** Use explicit color arrays rather than DataFrame columns with list values
- **Always:** Reset DataFrame index before passing to Pydeck layers

**Pydeck Best Practices:**
```python
import pydeck as pdk

# ✓ Minimal data structure for Pydeck
assets = load_grid_assets()
map_data = assets[['latitude', 'longitude', 'asset_type']].copy()
map_data = map_data.reset_index(drop=True)

# ✓ ScatterplotLayer with explicit colors
layer = pdk.Layer(
    'ScatterplotLayer',
    data=map_data,
    get_position='[longitude, latitude]',
    get_color=[255, 0, 0, 200],  # Explicit RGBA
    get_radius=100,
    pickable=True
)

# ✓ Multiple layers with conditional styling
normal_assets = map_data[map_data['asset_type'] == 'NORMAL'][['latitude', 'longitude']]
critical_assets = map_data[map_data['asset_type'] == 'CRITICAL'][['latitude', 'longitude']]

view_state = pdk.ViewState(
    latitude=map_data['latitude'].mean(),
    longitude=map_data['longitude'].mean(),
    zoom=10,
    pitch=0
)

deck = pdk.Deck(
    layers=[
        pdk.Layer('ScatterplotLayer', data=normal_assets, 
                  get_position='[longitude, latitude]',
                  get_color=[100, 100, 255, 180], get_radius=50),
        pdk.Layer('ScatterplotLayer', data=critical_assets,
                  get_position='[longitude, latitude]',
                  get_color=[255, 0, 0, 200], get_radius=100)
    ],
    initial_view_state=view_state,
    tooltip={"text": "Asset Location"}
)
st.pydeck_chart(deck)
```

**Why Pydeck:**
- **Performance:** GPU-accelerated rendering for large geospatial datasets
- **Layer Support:** Rich set of layer types (scatter, hexagon, heatmap, arc, path)
- **3D Capabilities:** Support for elevation and 3D visualizations
- **Deck.gl Integration:** Built on Uber's powerful deck.gl framework
- **Snowflake Integration:** Native support in Streamlit for Snowflake deployments

### Visualization Anti-Patterns
- **Avoid:** Using Altair or Matplotlib for new charts when Plotly meets requirements
- **Avoid:** Passing full DataFrames with many columns to Pydeck layers
- **Avoid:** Using DataFrame columns with list values for Pydeck colors (causes serialization errors in SiS)
- **Avoid:** Creating maps without proper error handling for missing coordinates
- **Avoid:** Static charts when interactivity would improve user experience

## 7. Streamlit in Snowflake (SiS) Feature Compatibility

### Current SiS Support
- **Streamlit Version:** 1.46 (GA as of August 12, 2025) - [Release Notes](https://docs.snowflake.com/en/release-notes/streamlit-in-snowflake)
- **Python Versions:** 3.8, 3.9, 3.10, 3.11 (default: 3.11 since 2024_08 bundle) - [BCR-1804](https://docs.snowflake.com/en/release-notes/bcr-bundles/2024_08/bcr-1804)
- **Recommendation:** Pin versions in `environment.yml` for consistency

**Supported Features (Streamlit 1.26+):**
- ✅ `st.column_config.*` - Available since Streamlit 1.26.0 (March 2024)
- ✅ `st.data_editor` - Available since 1.26.0
- ✅ `st.chat_message` / `st.chat_input` - Available since 1.26.0
- ✅ `st.file_uploader` - GA as of March 12, 2025
- ✅ Custom components - Preview as of August 6, 2025

**Features with Compatibility Notes:**
- ⚠️ `st.page_link()` - Verify availability in your SiS version
- ⚠️ `hide_index` parameter - May not be supported in all versions
- ⚠️ Some newer Streamlit 1.46+ features may have delayed availability in SiS

### Version Pinning Best Practice
- **Critical:** Do NOT pin Python version in environment.yml (causes SQL compilation error)
- **Rule:** Python version is managed by Snowflake (default: 3.11), set via Snowsight UI if needed
- **Always:** CAN pin Streamlit version in environment.yml for consistency

```yaml
# environment.yml - Correct version pinning for SiS
name: utility_streamlit
channels:
  - snowflake
dependencies:
  # ✓ Streamlit version CAN be pinned
  - streamlit=1.46
  
  # ✓ Other packages can be pinned
  - snowflake-snowpark-python
  - pandas
  - altair
  
  # ❌ Do NOT pin Python version here
  # Python managed by Snowflake (default: 3.11)
  # Set via Snowsight UI if different version needed
```

**Error if Python pinned:**
```
Error: [391546] SQL compilation error: Cannot create a Python function 
with the specified packages. Packages not found: - python==3.11
```

**Solution:** Remove `python=X.XX` from dependencies; let Snowflake manage Python version.

### PyDeck Compatibility Issues
- **Critical:** PyDeck in SiS has strict DataFrame serialization requirements
- **Always:** Pass only minimal columns (`[['latitude', 'longitude']]`) to PyDeck layers
- **Always:** Use explicit color arrays, not DataFrame columns with list values
- **Avoid:** Passing full DataFrames with many columns to PyDeck layers

**Problem:**
```python
# ❌ Causes TypeError: vars() error during serialization
assets['color_rgb'] = assets['status'].apply(get_color_function)  # Column with lists
layer = pdk.Layer('ScatterplotLayer', data=assets, get_color='color_rgb')
```

**Solution:**
```python
# ✓ Works - Minimal data, explicit colors
minimal_data = assets[['latitude', 'longitude']].reset_index(drop=True)
layer = pdk.Layer('ScatterplotLayer', data=minimal_data, get_color=[255, 0, 0, 200])
```

## 7. Media Elements

### Images, Videos, and Audio
- **Always:** Use `st.image()` for displaying images with proper sizing parameters (`width`, `use_column_width`)
- **Always:** Use `st.video()` and `st.audio()` for media playback with appropriate controls
- **Requirement:** Optimize media assets before deployment to reduce load times
- **Requirement:** Provide alt text for images to improve accessibility
- **Consider:** Use `st.logo()` for consistent branding across pages (Streamlit 1.29+)

**Best Practices:**
```python
# ✓ Optimized image display
st.image(
    "assets/logo.png",
    width=200,
    caption="Company Logo"
)

# ✓ Video with start time
st.video("https://example.com/video.mp4", start_time=10)

# ✓ Audio with loop option
st.audio("assets/background.mp3", loop=True)
```

### Asset Management
- **Requirement:** Store static assets in dedicated `assets/` or `static/` directory
- **Always:** For SiS deployments, ensure assets are included in deployment package
- **Always:** For SPCS deployments, include assets in container image with proper paths
- **Consider:** Use CDN for large media files to improve performance

## 8. Chat Interfaces

### Building Conversational UIs
- **Requirement:** Use `st.chat_message()` to display messages with avatar and role
- **Requirement:** Use `st.chat_input()` for user message entry
- **Requirement:** Store conversation history in `st.session_state` for persistence
- **Always:** Show typing indicators during processing with `st.spinner()` or `st.status()`

**Basic Chat Pattern:**
```python
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Handle user input
if prompt := st.chat_input("Ask a question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate and display response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt)
            st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
```

### Chat Best Practices
- **Requirement:** Limit conversation history size to prevent memory issues (e.g., last 50 messages)
- **Always:** Clear conversation history with explicit user action (button with confirmation)
- **Consider:** Add export functionality for chat transcripts
- **Always:** Validate and sanitize user inputs before processing
- **Consider:** Implement rate limiting for API-backed chat responses

## 9. Status and Feedback Elements

### User Feedback Patterns
- **Requirement:** Use appropriate status elements for different message types:
  - `st.success()` - Successful operations
  - `st.error()` - Errors requiring user attention
  - `st.warning()` - Warnings or cautionary messages
  - `st.info()` - Informational messages
- **Requirement:** Use `st.spinner()` for operations taking 2-5 seconds
- **Requirement:** Use `st.progress()` with `st.status()` for operations taking >5 seconds
- **Always:** Provide clear, actionable messages in all status elements

**Effective Status Usage:**
```python
# ✓ Clear feedback for operations
with st.spinner("Loading data from Snowflake..."):
    data = load_data()
st.success(f"Loaded {len(data):,} records successfully!")

# ✓ Progress tracking for long operations
progress_bar = st.progress(0)
status_text = st.empty()
for i, batch in enumerate(data_batches):
    status_text.text(f"Processing batch {i+1}/{len(data_batches)}...")
    process_batch(batch)
    progress_bar.progress((i + 1) / len(data_batches))
status_text.empty()
progress_bar.empty()
st.success("All batches processed!")

# ✓ Error with actionable guidance
try:
    result = risky_operation()
except Exception as e:
    st.error("Operation failed. Please check your input and try again.")
    with st.expander("Technical details"):
        st.code(str(e))
```

## 10. Testing and Debugging

### Testing Strategies
- **Requirement:** Write unit tests for data processing functions using pytest
- **Requirement:** Test cached functions to ensure proper cache invalidation
- **Consider:** Use Streamlit's AppTest for end-to-end UI testing (Streamlit 1.28+)
- **Always:** Test with various input combinations and edge cases

**Testing Pattern:**
```python
# test_app.py
import pytest
from your_app import load_data, process_data

def test_load_data_returns_dataframe():
    result = load_data()
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

def test_process_data_handles_empty_input():
    result = process_data(pd.DataFrame())
    assert result is not None
```

### Common Debugging Issues
- **App Crashes or Freezes:**
  - Avoid infinite loops in widget callbacks
  - Use `@st.cache_data` to prevent redundant data loading
  - Check for blocking operations without feedback
  
- **Slow Performance:**
  - Profile with `st.write(st.experimental_get_query_params())` to check rerun frequency
  - Optimize expensive operations with proper caching
  - Use lazy loading for large datasets
  - Sample data for development/testing
  
- **Widget State Issues:**
  - Initialize all session state variables explicitly
  - Use widget keys for stable identity across reruns
  - Avoid overwriting session state in widget callbacks
  
- **Memory Issues:**
  - Clear large cached objects when no longer needed
  - Limit conversation history and data in session state
  - Use pagination for large result sets

### Performance Profiling
- **Always:** Monitor rerun frequency and identify unnecessary reruns
- **Consider:** Use Python profilers (cProfile, line_profiler) for computational bottlenecks
- **Always:** Test with production-like data volumes during development

## 11. Security and Input Validation

### Input Validation
- **Mandatory:** Validate and sanitize all user inputs before processing
- **Mandatory:** Use type hints and validation for structured inputs
- **Always:** Set reasonable bounds on numeric inputs (min, max values)
- **Always:** Validate file uploads for type, size, and content

**Input Validation Pattern:**
```python
# ✓ Validated numeric input
age = st.number_input("Age", min_value=0, max_value=120, value=25)

# ✓ File upload validation
uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
if uploaded_file:
    if uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
        st.error("File too large. Maximum size is 10MB.")
    else:
        df = pd.read_csv(uploaded_file)

# ✓ Text input sanitization
import re
user_input = st.text_input("Enter name")
if user_input:
    # Remove special characters
    sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', user_input)
    if sanitized != user_input:
        st.warning("Special characters were removed from input.")
```

### Secrets Management
- **Mandatory:** Use `st.secrets` for all sensitive configuration (API keys, passwords, tokens)
- **Mandatory:** Never hardcode credentials in source code
- **Always:** For SiS, use Snowflake secrets management
- **Always:** For SPCS, use Kubernetes secrets or environment variables
- **Always:** Validate that required secrets exist before use

**Secrets Pattern:**
```python
# ✓ Proper secrets usage
try:
    api_key = st.secrets["api"]["key"]
    db_password = st.secrets["database"]["password"]
except KeyError as e:
    st.error(f"Missing required secret: {e}")
    st.stop()

# ❌ Never do this
api_key = "sk-1234567890abcdef"  # Hardcoded secret!
```

### Deployment Security
- **Always:** Deploy production apps using HTTPS
- **Consider:** Implement authentication for sensitive applications
- **Always:** Use Snowflake's role-based access control (RBAC) for data access
- **Consider:** Add audit logging for sensitive operations
- **Always:** Keep dependencies updated for security patches

## 12. Documentation and User Guidance

### Inline Documentation
- **Requirement:** Provide clear instructions within the app using `st.markdown()` or `st.write()`
- **Always:** Use `help` parameter in widgets to provide quick guidance
- **Consider:** Add tooltips and expanders for detailed explanations
- **Always:** Include examples for complex inputs

**Documentation Pattern:**
```python
# ✓ Clear guidance
st.markdown("""
### Data Upload
Upload a CSV file with the following columns:
- `date` (YYYY-MM-DD format)
- `value` (numeric)
- `category` (text)
""")

uploaded_file = st.file_uploader(
    "Choose a file",
    type=['csv'],
    help="Maximum file size: 10MB"
)

# ✓ Contextual help
with st.expander("ℹ️ How to interpret this chart"):
    st.write("""
    - **Blue line**: Actual values
    - **Red line**: Predicted values
    - **Gray area**: Confidence interval
    """)
```

### User Manuals and Help Sections
- **Consider:** Add dedicated help page for complex applications
- **Always:** Provide contact information or support links
- **Consider:** Include sample data or templates for download
- **Always:** Document known limitations or browser requirements

## 13. Development Workflow

### Environment Management
- **Requirement:** Use virtual environments (venv, conda) for dependency isolation
- **Always:** Pin dependency versions in `requirements.txt` or `environment.yml`
- **Always:** For SiS, use `environment.yml` with Snowflake-managed channels
- **Always:** Test with production Python version locally before deployment

**Environment Setup:**
```bash
# ✓ Create isolated environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# ✓ For conda
conda env create -f environment.yml
conda activate your_env_name
```

### Code Organization Best Practices
- **Requirement:** Separate concerns into distinct modules:
  - `data_loaders.py` - Data fetching and caching
  - `transformations.py` - Data processing logic
  - `visualizations.py` - Chart and plot functions
  - `utils.py` - Helper functions
- **Always:** Use consistent naming conventions (snake_case for functions/variables)
- **Always:** Add docstrings to functions with complex logic
- **Consider:** Use type hints for better IDE support and validation

### Staying Current
- **Always:** Review Streamlit changelog for new features and deprecations
- **Consider:** Participate in Streamlit community forums for best practices
- **Always:** Update dependencies periodically for performance and security improvements
- **Always:** Test thoroughly after updating major dependencies

## 14. Anti-Patterns
- **Avoid:** Mixing business logic and UI rendering in a single large function.
- **Mandatory:** Never show raw exception traces to users. Use `st.error()` with a clear, actionable message.
- **Avoid:** Recreating database connections on every interaction.
- **Avoid:** Embedding custom CSS or HTML style blocks in Python code; use config.toml for theming instead.
- **Avoid:** Mixing SiS and open-source Streamlit (SPCS) configurations, best practices, and deployment guidance.
- **Avoid:** Accessing DataFrame columns without normalizing Snowflake's UPPERCASE column names first.
- **Avoid:** Using buttons for navigation; use `st.page_link()` or `st.switch_page()` instead.
- **Avoid:** Storing large objects in session state without cleanup strategy.
- **Avoid:** Ignoring user input validation; always validate and sanitize.
- **Avoid:** Hardcoding secrets or credentials in source code.

## 15. Documentation and Learning Resources
- **Always:** Reference the official documentation:
  - **Configuration**: https://docs.streamlit.io/develop/concepts/configuration
  - **Configuration and Theming Tutorial**: https://docs.streamlit.io/develop/tutorials/configuration-and-theming
  - **Caching**: https://docs.streamlit.io/develop/concepts/architecture/caching
  - **Session State**: https://docs.streamlit.io/develop/concepts/architecture/session-state
  - **Layouts**: https://docs.streamlit.io/develop/api-reference/layout
  - **API Reference**: https://docs.streamlit.io/develop/api-reference
- **Requirement:** When building for Snowflake, cross-reference Streamlit in Snowflake docs for differences in behavior, security context, and supported features: https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit
- **Requirement:** When deploying open-source Streamlit via SPCS, follow SPCS docs for container build, networking, and runtime specifics: https://docs.snowflake.com/en/developer-guide/snowpark-container-services
- **Consider:** Review the [Streamlit 101 Tutorial Series](https://dev.to/jamesbmour/series/28657) for comprehensive, practical examples covering text elements, data display, input widgets, media, visualizations, layouts, chat interfaces, status elements, and page navigation

## Quick Compliance Checklist

### Performance & Setup
- [ ] App loads in under 2 seconds (Fast First Paint achieved)
- [ ] Page config set with title, icon, and layout
- [ ] Session state initialized explicitly at app start
- [ ] Database queries cached with appropriate TTL
- [ ] Column names normalized to lowercase after loading from Snowflake
- [ ] Virtual environment used for dependency isolation

### Configuration & Theming
- [ ] Theme configuration defined in .streamlit/config.toml when customization needed
- [ ] Consistent color scheme using primaryColor, backgroundColor, secondaryBackgroundColor, textColor
- [ ] Font selection appropriate for application context (sans serif, serif, monospace)
- [ ] Configuration compatibility verified for deployment target (SiS vs SPCS)

### Architecture & Code Organization
- [ ] Modular structure with pages/ and components/ directories
- [ ] Business logic separated from UI rendering
- [ ] Reusable functions extracted to separate modules (data_loaders, visualizations, utils)
- [ ] Consistent naming conventions followed (snake_case)

### User Experience
- [ ] Error handling implemented with user-friendly messages
- [ ] No raw exception traces shown to users
- [ ] Help text provided for complex widgets
- [ ] Responsive layout using st.columns and container_width=True
- [ ] Appropriate status elements used (success, error, warning, info)
- [ ] Progress indicators shown for operations 2-5s (spinner) and >5s (progress bar)

### Media & Assets
- [ ] Images include alt text for accessibility
- [ ] Media assets optimized before deployment
- [ ] Assets stored in dedicated directory (assets/ or static/)

### Visualization & Data Display
- [ ] Plotly used for interactive charts and graphs
- [ ] Pydeck used for geospatial visualizations and maps
- [ ] Charts configured with clear titles, axis labels, and legends
- [ ] Charts use use_container_width=True for responsive design
- [ ] Map data prepared with minimal columns (latitude, longitude, attributes)
- [ ] Pydeck layers use explicit color arrays (not DataFrame columns with lists)
- [ ] Visualizations tested with production-like data volumes

### Security & Validation
- [ ] All user inputs validated and sanitized
- [ ] Secrets managed via st.secrets (never hardcoded)
- [ ] File uploads validated for type and size
- [ ] Numeric inputs have reasonable bounds (min/max)

### Testing & Debugging
- [ ] Unit tests written for data processing functions
- [ ] Cache invalidation tested
- [ ] App tested with edge cases and error conditions
- [ ] Performance tested with production-like data volumes

### Documentation
- [ ] Inline instructions provided for complex features
- [ ] Help parameter used in widgets
- [ ] Known limitations documented

### Deployment
- [ ] Deployment type verified (SiS vs open-source on SPCS)
- [ ] Correct documentation followed for deployment target
- [ ] Dependencies pinned in requirements.txt or environment.yml
- [ ] Navigation uses st.page_link or st.switch_page, not buttons

## Validation
- **Success checks:** App loads <2s, caching reduces query time, responsive on mobile/desktop, error states handled gracefully, theme applied consistently, configuration loaded properly, media assets load correctly, chat history persists across interactions, input validation prevents invalid data, user feedback clear and actionable, unit tests pass for data processing functions, secrets loaded without errors
- **Negative tests:** Break database connection (should show user-friendly error), disable cache (should show performance impact), test with malformed data (should not crash), test with invalid config.toml (should use defaults gracefully), submit invalid file uploads (should reject with clear message), test missing secrets (should fail gracefully), test with oversized inputs (should enforce limits), test chat with history overflow (should truncate properly)

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
- [Streamlit 101 Tutorial Series](https://dev.to/jamesbmour/series/28657) - Comprehensive tutorial series covering text elements, data display, input widgets, media elements, data visualization, layouts, chat interfaces, status elements, and page navigation with practical examples
- [Plotly Documentation](https://plotly.com/python/) - Official Plotly Python graphing library documentation
- [Plotly Express API](https://plotly.com/python-api-reference/plotly.express.html) - Plotly Express high-level API reference
- [Pydeck Documentation](https://deckgl.readthedocs.io/) - Official Pydeck documentation for geospatial visualizations
- [Pydeck Layer Catalog](https://deckgl.readthedocs.io/en/latest/layer.html) - Complete layer types reference for Pydeck
- [Snowflake Streamlit Guide](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit) - Snowflake-specific Streamlit integration documentation
- [Snowpark Container Services (SPCS)](https://docs.snowflake.com/en/developer-guide/snowpark-container-services) - Deploying and operating containerized apps (open-source Streamlit) on Snowflake

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Snowflake Notebooks**: `109-snowflake-notebooks.md`
- **Python Core**: `200-python-core.md`
- **Snowpark Container Services**: `120-snowflake-spcs.md`
