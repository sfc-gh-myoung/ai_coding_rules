# Python DateTime Core Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v4.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:datetime, kw:timezone
**Keywords:** datetime, timezone, UTC, timedelta, tz_localize, tz_convert, datetime.now(UTC), pd.Timestamp, type conversion, zoneinfo
**TokenBudget:** ~3000
**ContextTier:** High
**Depends:** 200-python-core.md

## Scope

**What This Rule Covers:**
Core datetime handling in Python and Pandas: type system, conversions, parsing, timezone management, and anti-patterns for type-safe datetime operations.

**When to Load This Rule:**
- Working with datetime objects in Python or Pandas
- Converting between datetime types (Python datetime, pd.Timestamp, datetime64)
- Managing timezones in data processing
- Debugging datetime-related TypeErrors in Pandas 2.x

## References

### Dependencies

**Must Load First:**
- **200-python-core.md** - Modern Python tooling and practices

**Related:**
- **251a-python-datetime-advanced.md** - Date arithmetic, performance optimization
- **251b-python-datetime-integration.md** - Streamlit, Plotly, SQL integration
- **252-python-pandas-core.md** - Pandas performance and anti-patterns

### External Documentation
- [Python datetime Documentation](https://docs.python.org/3/library/datetime.html)
- [Pandas Time Series / Date Functionality](https://pandas.pydata.org/docs/user_guide/timeseries.html)
- [Python zoneinfo](https://docs.python.org/3/library/zoneinfo.html) - Python 3.9+ timezone support

## Contract

### Inputs and Prerequisites

- Python 3.11+, pandas 2.x+
- Standard library: `datetime`, `zoneinfo` (Python 3.9+)
- Third-party: `python-dateutil` (for relativedelta, rrule, parser) - install with `uv add python-dateutil`
- Optional: `pytz` (legacy; prefer `zoneinfo` for new code)

### Mandatory

- **Always:** Use `datetime.now(UTC)` instead of deprecated `datetime.utcnow()`
- **Always:** Be explicit about timezones (tz_localize, tz_convert)
- **Always:** Convert types explicitly before comparing pd.Timestamp with Python datetime
- **Rule:** Parse dates with format specification when structure is known
- **Rule:** Use consistent datetime types within operations

### Forbidden

- Mixed datetime type comparisons without conversion
- Hardcoded timezone offsets (use named timezones)
- Using deprecated `datetime.utcnow()` or `datetime.utcfromtimestamp()`
- Parsing dates without format specification on large datasets
- Ignoring timezone information in data processing

### Execution Steps

1. Identify datetime types in use (check df.dtypes)
2. Normalize to consistent types before comparisons
3. Be explicit about timezones (localize, convert)
4. Parse dates with format specification when structure is known
5. Test cross-library compatibility (Python, Pandas)

### Output Format

Type-safe datetime operations, explicit timezone handling, Pandas 2.x compatible code.

### Validation

**Pre-Task-Completion Checks:**
- All datetime type conversions handled explicitly
- Timezone operations are explicit
- Date parsing uses format specification when known
- No deprecated datetime APIs used

**Success Criteria:**
- All datetime comparisons use same types (no mixed pd.Timestamp/datetime)
- All timezone operations are explicit (no implicit local time)
- Parsing uses `format=` on datasets >1K rows
- Type conversions documented at integration boundaries

**Negative Tests:**
- Mixed datetime comparison without conversion (should fail)
- timezone-naive comparison with tz-aware (should warn)
- Ambiguous date parsing (should coerce or error)

### Design Principles

- **Type Safety First:** Never mix datetime types without explicit conversion
- **Timezone Explicit:** Always specify timezone handling (UTC default)
- **Pandas 2.x Compatible:** Use patterns that work with strict type checking

### Post-Execution Checklist

- [ ] All datetime type conversions handled explicitly
- [ ] Timezone operations are explicit
- [ ] Date parsing uses format specification when known
- [ ] No deprecated APIs (utcnow, utcfromtimestamp)
- [ ] Pandas 2.x compatibility validated

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Comparing pd.Timestamp with Python datetime

**Problem:** Mixed datetime types cause TypeError in Pandas 2.x; implicit conversions unreliable.

**Correct Pattern:** Explicitly convert to the same type before comparison.

```python
# Wrong: Direct comparison causes TypeError in Pandas 2.x+
pd_ts = pd.Timestamp('2024-10-23 14:30:00', tz='UTC')
py_dt = datetime.now(UTC)
if pd_ts > py_dt:  # TypeError!
    print("Future date")

# Correct: Explicit type conversion before comparison
if pd_ts.to_pydatetime() > py_dt:  # Convert to same type
    print("Future date")
```

### Anti-Pattern 2: Using Deprecated datetime.utcnow()

**Problem:** Deprecated in Python 3.12+; returns naive datetime without timezone.

**Correct Pattern:** Use `datetime.now(UTC)` for timezone-aware UTC timestamps.

```python
# Wrong: Deprecated, returns naive datetime
timestamp = datetime.utcnow()

# Correct: Modern timezone-aware datetime
from datetime import datetime, UTC
timestamp = datetime.now(UTC)
```

### Anti-Pattern 3: Parsing Dates Without Format Specification

**Problem:** 10-100x slower on large datasets; ambiguous dates (MM/DD vs DD/MM).

**Correct Pattern:** Always specify format when the date structure is known.

```python
# Wrong: Slow inference, ambiguous
df['date'] = pd.to_datetime(df['date'])

# Correct: Explicit format (fast, unambiguous)
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
```

### Anti-Pattern 4: Ignoring Timezones

**Problem:** Timezone ambiguity causes bugs with international data; tz-naive vs tz-aware comparisons fail.

**Correct Pattern:** Be explicit about timezone handling; localize and convert explicitly.

```python
# Wrong: No timezone info
df['date'] = pd.to_datetime(df['date'])
df_filtered = df[df['date'] > datetime.now()]  # tz mismatch?

# Correct: Explicit timezone handling
df['date'] = pd.to_datetime(df['date']).dt.tz_localize('UTC')
now_utc = pd.Timestamp.now(tz='UTC')
df_filtered = df[df['date'] > now_utc]
```

### Anti-Pattern 5: Using Python datetime for Vectorized Operations

**Problem:** 100x slower than vectorized Pandas operations.

**Correct Pattern:** Use Pandas vectorized operations for column-level datetime math.

```python
# Wrong: Row-level iteration
for idx, row in df.iterrows():
    row['next_week'] = row['date'] + datetime.timedelta(days=7)

# Correct: Vectorized Pandas operation
df['next_week'] = df['date'] + pd.Timedelta(days=7)
```

### Type Preservation in Arithmetic

Arithmetic operations preserve types — be aware of what you get back:

```python
import pandas as pd
from datetime import datetime, UTC

ts = pd.Timestamp.now(tz='UTC')
result = ts + pd.Timedelta(days=7)
type(result)  # pd.Timestamp — NOT datetime.datetime

# If you need Python datetime:
py_dt = result.to_pydatetime()  # Convert explicitly

# DataFrame column arithmetic also returns Timestamp:
df['next_week'] = df['date'] + pd.Timedelta(days=7)
# df['next_week'].dtype → datetime64[ns, UTC]

# See 251a for full arithmetic details (relativedelta, business days, etc.)
```

> **Investigation Required**
> When applying this rule:
> 1. **Read data files BEFORE datetime operations** - Check existing date formats, timezone awareness
> 2. **Verify Pandas version** - Check if Pandas 2.x compatibility needed
> 3. **Never assume datetime types** - Check df.dtypes to see datetime64 vs object
> 4. **Check existing timezone handling** - Read code to understand if tz-aware or naive
> 5. **Check if `python-dateutil` is installed** (`uv pip list | grep dateutil`) — needed for `relativedelta`, `rrule`, flexible parsing

## DateTime Type System

### Three Main DateTime Representations

**Python datetime.datetime:**
```python
from datetime import datetime, UTC

py_dt = datetime(2024, 10, 23, 14, 30, 0)
py_dt_utc = datetime.now(UTC)  # Timezone-aware
```

**Pandas Timestamp (extends Python datetime):**
```python
import pandas as pd

pd_ts = pd.Timestamp('2024-10-23 14:30:00')
pd_ts_utc = pd.Timestamp.now(tz='UTC')  # Timezone-aware
```

**NumPy datetime64 / Pandas Series dtype:**
```python
# Pandas Series with datetime64[ns] dtype
df['date'] = pd.to_datetime(df['date'])  # Creates datetime64[ns] column
```

**Key Insight:** Pandas Series operations return datetime64[ns] arrays, but individual elements are pd.Timestamp objects.

## Type Conversions and Safety

### Universal DateTime Conversion Helper

```python
import datetime
import pandas as pd

def ensure_python_datetime(dt):
    """Convert any datetime-like object to Python datetime.

    Handles None/NaT, datetime.datetime, pd.Timestamp, and strings.
    Safe for Pandas 2.x+ strict type checking.
    """
    if dt is None or pd.isna(dt):
        return None
    if isinstance(dt, datetime.datetime):
        return dt
    if hasattr(dt, 'to_pydatetime'):
        return dt.to_pydatetime()
    return pd.to_datetime(dt).to_pydatetime()
```

### DataFrame-Level Type Conversions

```python
# String to datetime
df['date'] = pd.to_datetime(df['date'])

# Datetime to string (for display or Plotly performance)
df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')

# To Python datetime objects (for compatibility)
df['date_python'] = df['date'].apply(lambda x: x.to_pydatetime() if pd.notna(x) else None)

# Remove timezone info (make tz-naive)
df['date'] = df['date'].dt.tz_localize(None)
```

### Epoch Timestamp Type Conversion

```python
# Epoch (int/float) → pd.Timestamp:
ts = pd.Timestamp(1709913600, unit='s')
ts = pd.Timestamp(1709913600000, unit='ms')

# pd.Timestamp → epoch:
epoch_s = int(ts.timestamp())  # seconds
epoch_ms = int(ts.timestamp() * 1000)  # milliseconds

# Python datetime → epoch:
from datetime import datetime, UTC
dt = datetime.now(UTC)
epoch = int(dt.timestamp())
```

## Date Parsing Best Practices

### Explicit Format Specification

```python
# GOOD: Explicit format (fast, unambiguous)
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

# GOOD: ISO 8601 format
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%dT%H:%M:%S')

# ACCEPTABLE: Mixed formats (flexible, but slower)
df['date'] = pd.to_datetime(df['date'], format='mixed')

# Handle parsing errors gracefully
df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Invalid becomes NaT
```

### Read CSV with Date Parsing

```python
# BEST: Parse dates during CSV read
df = pd.read_csv('data.csv', parse_dates=['order_date', 'ship_date'], date_format='%Y-%m-%d')
```

### Epoch / Unix Timestamp Conversion

Convert Unix timestamps (seconds or milliseconds since 1970-01-01):

```python
import pandas as pd

# Seconds since epoch (common in APIs, logs):
df['datetime'] = pd.to_datetime(df['epoch_seconds'], unit='s')

# Milliseconds since epoch (common in JavaScript, Java):
df['datetime'] = pd.to_datetime(df['epoch_ms'], unit='ms')

# With timezone — epoch is always UTC:
df['datetime'] = pd.to_datetime(df['epoch_seconds'], unit='s', utc=True)

# Convert datetime back to epoch:
df['epoch'] = df['datetime'].astype('int64') // 10**9  # seconds
df['epoch_ms'] = df['datetime'].astype('int64') // 10**6  # milliseconds

# Python stdlib equivalent:
from datetime import datetime, UTC
dt = datetime.fromtimestamp(1709913600, tz=UTC)  # Always specify tz!
# Never use datetime.fromtimestamp(ts) without tz — returns local time
```

## Timezone Management

### Core Principles

- **Always:** Store data in UTC
- **Always:** Convert to local timezone only for display
- **Always:** Be explicit about timezone operations

### Timezone Operations

```python
# Make timezone-aware (localize)
df['date'] = pd.to_datetime(df['date'])
df['date'] = df['date'].dt.tz_localize('UTC')

# Handle ambiguous times (DST transitions)
df['date'] = df['date'].dt.tz_localize('US/Eastern', ambiguous='infer')

# Convert between timezones
df['date_utc'] = df['date'].dt.tz_convert('UTC')
df['date_eastern'] = df['date'].dt.tz_convert('US/Eastern')

# Remove timezone info (for libraries that don't support tz-aware)
df['date'] = df['date'].dt.tz_localize(None)
```
