# Streamlit Fragments: Real-Time Progress Tracking

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-01-12
**Keywords:** st.fragment, run_every, real-time progress, polling, live updates, fragment pattern, auto-refresh, streaming, monitoring dashboard
**TokenBudget:** ~2300
**ContextTier:** Medium
**Depends:** 101-snowflake-streamlit-core.md, 101b-snowflake-streamlit-performance.md

## Scope

**What This Rule Covers:**
Advanced Streamlit fragment patterns for real-time progress tracking, live polling, and automatic UI updates without full page reruns.

**When to Load This Rule:**
- Implementing long-running operations (>30s) with live progress
- Building real-time monitoring dashboards
- Polling database or API for status updates
- Streaming data visualization
- Any pattern requiring `@st.fragment(run_every=...)`

## References

### Dependencies

**Must Load First:**
- **101-snowflake-streamlit-core.md** - Core Streamlit patterns
- **101b-snowflake-streamlit-performance.md** - Caching and performance basics

### External Documentation

- **API Reference:** https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment
- **Architecture Guide:** https://docs.streamlit.io/develop/concepts/architecture/fragments

## Contract

### Inputs and Prerequisites

- Streamlit app with long-running operation (>30s)
- Database table or API endpoint for progress tracking
- Understanding of st.session_state

### When to Use Fragments

- Database operations with progress table tracking (Snowflake stored procedures, Cortex AI functions)
- API polling for job status (external services, batch processing)
- Streaming data updates (real-time analytics, monitoring)
- Real-time monitoring dashboards (live metrics, status boards)

### Mandatory

- **Session State Persistence:** Store active operation state in `st.session_state` for cross-rerun tracking
- **Conditional Rendering:** Fragment MUST be called outside button's `if` block to persist across reruns
- **Cleanup on Completion:** Clear session state variables when operation completes to stop fragment
- **Use `st.stop()`:** Call `st.stop()` inside fragment to halt auto-refresh when done
- **Read-Only Display:** Fragment body should only contain display elements (no widgets)

### Forbidden

- Creating fragments inside button blocks
- Using widgets (st.text_input, st.button, etc.) inside fragment body
- Fragments without termination conditions (infinite polling)

### Execution Steps

1. Define fragment function at module level with `@st.fragment(run_every="...")`
2. Store operation state in `st.session_state` when starting
3. Render fragment conditionally based on session state (outside button block)
4. Poll progress source inside fragment
5. Clear session state and call `st.stop()` when operation completes

### Output Format

Working fragment with live progress updates that terminates cleanly.

### Validation

- Fragment continues polling after button click
- Progress updates display in real-time
- Fragment stops when operation completes
- No infinite polling loops

### Post-Execution Checklist

- [ ] Fragment defined at module level (not inside button block)
- [ ] Session state used for operation tracking
- [ ] Termination condition implemented with st.stop()
- [ ] No widgets inside fragment body

## Complete Working Example

**From Call Center Analytics:**

```python
import streamlit as st
import time
from concurrent.futures import ThreadPoolExecutor

# ========================================================================
# STREAMLIT FRAGMENT PATTERN: Live Progress Tracking
# ========================================================================
# Key Components:
# 1. st.session_state - Persists active operation state across reruns
# 2. @st.fragment(run_every="0.5s") - Auto-refreshing fragment that polls progress
# 3. Conditional rendering - Fragment called outside button's if block
# 4. ThreadPoolExecutor - Non-blocking stored procedure execution
# 5. st.stop() - Halts fragment auto-refresh when operation completes
#
# Reference: https://docs.streamlit.io/develop/concepts/architecture/fragments
# ========================================================================

def initialize_analysis_progress(audio_file: str):
    """Initialize progress tracking in database table"""
    session.sql(f"""
        INSERT INTO UTILITY_DEMO_V2.CUSTOMER_DATA.ANALYSIS_PROGRESS
        (AUDIO_FILE_NAME, STATUS, CURRENT_STEP, TOTAL_STEPS)
        VALUES ('{audio_file}', 'in_progress', 0, 18)
    """).collect()

def call_stored_procedure_async(proc_name: str, *args):
    """Execute stored procedure in background thread"""
    executor = ThreadPoolExecutor(max_workers=1)
    def run_proc():
        return session.call(proc_name, *args)
    return executor.submit(run_proc)

@st.fragment(run_every="0.5s")
def show_analysis_progress_live(audio_file):
    """
    Auto-refreshing fragment that polls ANALYSIS_PROGRESS table.

    Fragment Pattern (Streamlit Best Practice):
    - Decorated with @st.fragment(run_every="0.5s") for automatic polling
    - Called conditionally based on st.session_state.active_analysis_file
    - Uses st.stop() to halt auto-refresh when operation completes
    - Clears session state to prevent re-triggering on subsequent reruns
    """
    # Query current progress from database
    progress_result = session.sql(f"""
        SELECT STATUS, CURRENT_STEP, TOTAL_STEPS, STEP_DESCRIPTION, LAST_UPDATED
        FROM UTILITY_DEMO_V2.CUSTOMER_DATA.ANALYSIS_PROGRESS
        WHERE AUDIO_FILE_NAME = '{audio_file}'
        ORDER BY LAST_UPDATED DESC
        LIMIT 1
    """).collect()

    if not progress_result:
        st.warning("Initializing analysis...")
        return

    p = progress_result[0].as_dict()

    # Show live progress bar and status
    if p["STATUS"] == "in_progress" and p["TOTAL_STEPS"] > 0:
        progress_pct = p["CURRENT_STEP"] / p["TOTAL_STEPS"]
        st.progress(progress_pct, text=f"Step {p['CURRENT_STEP']}/{p['TOTAL_STEPS']}")
        st.info(f"{p['STEP_DESCRIPTION']}")

        # Show elapsed time
        if "analysis_start_time" in st.session_state:
            elapsed = time.time() - st.session_state.analysis_start_time
            st.caption(f"Elapsed: {int(elapsed)}s")

    # Stop polling when complete
    if p["STATUS"] in ["completed", "partial", "failed"]:
        if p["STATUS"] == "completed":
            st.success(f"Analysis complete! Processed {p['CURRENT_STEP']}/{p['TOTAL_STEPS']} steps")
        elif p["STATUS"] == "partial":
            st.warning(f"Partial completion: {p['CURRENT_STEP']}/{p['TOTAL_STEPS']} steps")
        else:  # failed
            st.error(f"Analysis failed at step {p['CURRENT_STEP']}: {p['STEP_DESCRIPTION']}")

        # Clear session state to stop fragment
        if "active_analysis_file" in st.session_state:
            del st.session_state.active_analysis_file
        if "analysis_in_progress" in st.session_state:
            st.session_state.analysis_in_progress = False
        if "analysis_start_time" in st.session_state:
            del st.session_state.analysis_start_time
        if "analysis_future" in st.session_state:
            del st.session_state.analysis_future

        st.stop()  # Stop fragment auto-refresh

# Main app code
st.title("Call Center Analytics")

# CRITICAL: Conditional fragment rendering (outside button block)
if st.session_state.get("active_analysis_file"):
    st.info(f"Analyzing: {st.session_state.active_analysis_file}")
    show_analysis_progress_live(st.session_state.active_analysis_file)

# Button handler (only runs when button is clicked)
if st.button(
    "Analyze Transcription",
    type="primary",
    disabled=st.session_state.get("analysis_in_progress", False),
):
    selected_file = "call_de_20250924_003.mp3"

    # Set session state to trigger fragment
    st.session_state.active_analysis_file = selected_file
    st.session_state.analysis_in_progress = True
    st.session_state.analysis_start_time = time.time()

    # Initialize progress tracking
    with st.spinner("Launching analysis..."):
        initialize_analysis_progress(selected_file)
        future = call_stored_procedure_async(
            "UTILITY_DEMO_V2.CUSTOMER_DATA.SP_ANALYZE_CALL_TRANSCRIPTION_PROGRESSIVE",
            selected_file,
        )
        st.session_state.analysis_future = future

    st.rerun()  # Trigger rerun to show fragment
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Creating Fragment Inside Button Block

**Problem:**
```python
if st.button("Start"):
    @st.fragment(run_every="1s")
    def show_progress():
        st.write("Progress...")
    show_progress()
```

**Why It Fails:** Fragment won't persist after button resets. Fragments must be defined at module level, not inside conditional blocks.

**Correct Pattern:**
```python
@st.fragment(run_every="1s")
def show_progress():
    if st.session_state.get("active"):
        st.write("Progress...")

if st.session_state.get("active"):
    show_progress()

if st.button("Start"):
    st.session_state.active = True
    st.rerun()
```

### Anti-Pattern 2: Using Widgets Inside Fragments

**Problem:**
```python
@st.fragment(run_every="1s")
def fragment_with_widgets():
    user_input = st.text_input("Name")
    st.write(f"Hello {user_input}")
```

**Why It Fails:** Widgets are forbidden in fragment body. Fragments support display-only elements, not interactive inputs.

**Correct Pattern:**
```python
user_input = st.text_input("Name")

@st.fragment(run_every="1s")
def display_only_fragment():
    st.write(f"Hello {user_input}")
```

### Anti-Pattern 3: No Termination Condition

**Problem:**
```python
@st.fragment(run_every="1s")
def infinite_polling():
    st.write("Polling forever...")
```

**Why It Fails:** Fragment runs indefinitely, wasting resources and database connections. Always include a termination condition.

**Correct Pattern:**
```python
@st.fragment(run_every="1s")
def polling_with_termination():
    status = check_operation_status()
    st.write(f"Status: {status}")

    if status == "complete":
        del st.session_state.active_operation
        st.stop()
```

## Performance Considerations

- **Polling Frequency:** Balance between responsiveness and database load (0.5s-2s typical)
- **Scoped Reruns:** Only fragment reruns, not entire app (preserves user inputs, scroll position)
- **Database Load:** Each auto-refresh queries database; ensure queries are indexed and fast (<100ms)
- **Connection Pooling:** Use Streamlit's `st.connection()` for efficient connection management
