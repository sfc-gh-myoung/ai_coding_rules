# Python DateTime Integration Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:datetime-sql, kw:streamlit-datetime, kw:plotly-datetime
**Keywords:** datetime SQL, parameterized queries, Streamlit date input, Plotly datetime, datetime display, date formatting, SQL injection
**TokenBudget:** ~2500
**ContextTier:** Medium
**Depends:** 251-python-datetime-core.md

## Scope

**What This Rule Covers:**
Datetime integration with SQL databases, Streamlit, and Plotly including SQL safety (parameterized queries), date input widgets, and display formatting.

**When to Load This Rule:**
- Using datetime values in SQL queries
- Building Streamlit date input widgets
- Formatting datetime for display
- Integrating datetime data with Plotly charts

## References

### Dependencies

**Must Load First:**
- **251-python-datetime-core.md** - Core datetime types and timezone handling

**Related:**
- **251a-python-datetime-advanced.md** - Date arithmetic and performance
- **101a-snowflake-streamlit-visualization.md** - Plotly visualization patterns

## Contract

### Inputs and Prerequisites

- Pandas datetime columns (from 251 core)
- Streamlit for UI integration (optional)
- Database connection for SQL integration (optional)

### Mandatory

- **Critical:** Always use parameterized queries for datetime values in SQL (never f-strings)
- **Always:** Use database-native datetime types, not string columns
- **Rule:** Convert pd.Timestamp to Python datetime for Streamlit widgets
- **Rule:** Use strftime for display formatting

### Forbidden

- F-string or string concatenation for SQL queries with datetime values
- Storing datetime as strings in database columns
- Mixing tz-aware and tz-naive datetime in SQL parameters

### Execution Steps

1. Use parameterized queries for all datetime SQL operations
2. Convert datetime types for Streamlit compatibility
3. Format dates for display using strftime
4. Validate datetime columns before visualization

### Output Format

Parameterized SQL queries, Streamlit date widgets, formatted datetime display.

### Validation

**Pre-Task-Completion Checks:**
- [ ] All SQL queries use parameterized datetime values
- [ ] No f-strings in SQL construction
- [ ] Streamlit date inputs convert types correctly
- [ ] Display formatting uses strftime

### Investigation Required

Before modifying datetime integration code, agents MUST check:

- [ ] **Database adapter**: Identify which adapter is in use (psycopg2, SQLAlchemy, snowflake-connector-python) — placeholder syntax differs (%s, :param, ?)
- [ ] **Streamlit presence**: Check `pyproject.toml` for `streamlit` — skip Streamlit sections if not used
- [ ] **Existing datetime formatting**: Search for `strftime` and `dt.tz_convert` to match existing display patterns
- [ ] **Database column types**: Check schema for TIMESTAMP vs VARCHAR date columns — VARCHAR requires parsing before use
- [ ] **Plotly version**: Check for `plotly` in dependencies — `use_container_width` requires Streamlit >=1.18

### Design Principles

- **SQL Safety:** Always parameterize datetime values
- **Type Compatibility:** Convert types at integration boundaries
- **User-Friendly Display:** Format dates for readability

### Post-Execution Checklist

- [ ] SQL queries parameterized
- [ ] No f-string SQL patterns
- [ ] Streamlit date inputs working correctly
- [ ] Display formatting applied
- [ ] Cross-library types compatible

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: F-String SQL with DateTime Values

**Problem:** Using f-strings to construct SQL queries with datetime values creates SQL injection vulnerabilities and timezone handling bugs.

**Correct Pattern:** Use parameterized queries for datetime values. For SQL keywords like granularity, use allowlist validation.

```python
# Wrong: SQL injection risk with datetime value
query = f"SELECT * FROM events WHERE created_at > '{start_date}'"

# Correct: Parameterized query
cursor.execute(
    "SELECT * FROM events WHERE created_at > %s",
    (start_date,)
)
```

### Anti-Pattern 2: Storing Datetime as Strings in Database

**Problem:** String datetime columns prevent database-level date functions, indexing, and range queries.

**Correct Pattern:** Use database-native datetime types and pass datetime objects directly.

```python
# Wrong: Storing as string
cursor.execute("INSERT INTO events (created_at) VALUES (%s)", (str(now),))

# Correct: Use database-native datetime type
cursor.execute("INSERT INTO events (created_at) VALUES (%s)", (now,))
# Ensure column is TIMESTAMP/DATETIME type in schema
```

## SQL Safety for DateTime

### Key Principles

- **Always:** Use parameterized queries for datetime values
- **Always:** Be aware of timezone coercion by databases (e.g., PostgreSQL `TIMESTAMP WITH TIME ZONE` converts to UTC)
- **Always:** Use database-native datetime types, not string columns
- **Exception:** SQL keywords like `DATE_TRUNC` granularity cannot be parameterized; use allowlist validation instead

### Parameterized Query Examples

```python
# Standard DB-API (psycopg2, sqlite3)
cursor.execute(
    "SELECT * FROM events WHERE created_at BETWEEN %s AND %s",
    (start_date, end_date),
)

# SQLAlchemy
from sqlalchemy import select, text
stmt = select(events).where(events.c.created_at > start_date)
result = session.execute(stmt)

# Snowpark
df = session.sql(
    "SELECT * FROM events WHERE created_at > ?", params=[start_date]
)
```

### SQL Keyword Allowlist Validation

SQL keywords (table names, column names, ORDER BY direction) cannot be parameterized.
Use allowlist validation instead:

```python
# Allowlist for time granularity in DATE_TRUNC:
VALID_GRANULARITIES = {"day", "week", "month", "quarter", "year"}

def get_aggregated_data(cursor, granularity: str, start_date):
    if granularity not in VALID_GRANULARITIES:
        raise ValueError(f"Invalid granularity: {granularity}. Must be one of {VALID_GRANULARITIES}")

    # Safe: granularity is validated against allowlist
    query = f"SELECT DATE_TRUNC('{granularity}', created_at) AS period, COUNT(*) FROM events WHERE created_at > %s GROUP BY 1"
    cursor.execute(query, (start_date,))

# Allowlist for sort direction:
VALID_DIRECTIONS = {"ASC", "DESC"}

def get_sorted_events(cursor, direction: str = "DESC"):
    if direction.upper() not in VALID_DIRECTIONS:
        raise ValueError(f"Invalid sort direction: {direction}")
    query = f"SELECT * FROM events ORDER BY created_at {direction.upper()}"
    cursor.execute(query)
```

## Streamlit Integration

### Date Input Widgets

```python
import streamlit as st
import pandas as pd

# Date range selection
start_date = st.date_input("Start Date", value=pd.to_datetime("2024-01-01"))
end_date = st.date_input("End Date", value=pd.Timestamp.now())

# Convert to pandas Timestamp for filtering
start_ts = pd.Timestamp(start_date)
end_ts = pd.Timestamp(end_date)

# Filter DataFrame
filtered_df = df[(df["date"] >= start_ts) & (df["date"] <= end_ts)]
```

### Time Input Widget

```python
import streamlit as st
from datetime import time, datetime

# Time input for filtering:
start_time = st.time_input("Start time", value=time(9, 0))
end_time = st.time_input("End time", value=time(17, 0))

# Combine date and time:
selected_date = st.date_input("Date")
start_dt = datetime.combine(selected_date, start_time)

# Filter DataFrame by time range:
mask = (df['timestamp'].dt.time >= start_time) & (df['timestamp'].dt.time <= end_time)
filtered = df[mask]
```

### Timezone Display

```python
# User selects timezone
user_tz = st.selectbox("Timezone", ["UTC", "US/Eastern", "US/Pacific", "Europe/London"])

# Convert for display
df_display = df.copy()
df_display["date"] = df_display["date"].dt.tz_convert(user_tz)
st.dataframe(df_display)
```

### DateTime Display Formatting

```python
# Format dates for display
df_display = df.copy()
df_display["date"] = df_display["date"].dt.strftime("%B %d, %Y")  # "October 23, 2024"
st.dataframe(df_display)

# Or use styling
st.dataframe(
    df.style.format({"date": lambda x: x.strftime("%Y-%m-%d") if pd.notna(x) else "N/A"})
)
```

## JSON Datetime Serialization

Use ISO 8601 format for JSON interchange:

```python
from datetime import datetime, UTC
import json

# Serialize to ISO 8601:
dt = datetime.now(UTC)
json_str = dt.isoformat()  # "2024-03-09T14:30:00+00:00"

# Parse from ISO 8601 (Python 3.11+):
dt = datetime.fromisoformat("2024-03-09T14:30:00+00:00")

# In JSON responses (FastAPI/Flask):
response = {
    "created_at": dt.isoformat(),
    "updated_at": dt.isoformat(),
}

# Pandas DataFrame to JSON:
df['date_str'] = df['datetime_col'].dt.strftime('%Y-%m-%dT%H:%M:%S%z')
json_data = df.to_json(orient='records', date_format='iso')

# Custom JSON encoder for datetime:
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

json.dumps({"event_time": dt}, cls=DateTimeEncoder)
```

## Plotly Datetime Visualization

Configure datetime axes in Plotly charts:

```python
import plotly.express as px
import pandas as pd

# Line chart with datetime x-axis:
fig = px.line(df, x='date', y='value', title='Daily Metrics')

# Customize datetime axis formatting:
fig.update_xaxes(
    dtick="M1",                    # Tick every month
    tickformat="%b %Y",           # "Jan 2024" format
    ticklabelmode="period",       # Center labels on period
    rangeslider_visible=True,     # Date range slider
)

# Date range selection buttons:
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1w", step="day"),
                dict(count=1, label="1m", step="month"),
                dict(count=6, label="6m", step="month"),
                dict(step="all", label="All"),
            ])
        ),
    )
)

# In Streamlit:
st.plotly_chart(fig, use_container_width=True)
```

### Aggregated Time Series for Plotly

```python
# Always aggregate before plotting large datasets:
daily = df.resample('D', on='timestamp').agg(
    avg_value=('value', 'mean'),
    record_count=('value', 'count'),
)
fig = px.line(daily, y='avg_value', title='Daily Average')
```
