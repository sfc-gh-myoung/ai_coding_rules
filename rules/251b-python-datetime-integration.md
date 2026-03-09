# Python DateTime Integration Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:datetime-sql, kw:streamlit-datetime, kw:plotly-datetime
**Keywords:** datetime SQL, parameterized queries, Streamlit date input, Plotly datetime, datetime display, date formatting, SQL injection
**TokenBudget:** ~1350
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
