---
schema_version: v4.0
rule_version: v3.0.0
description: "Calendar versus elapsed arithmetic, business/DST boundaries and correctness-preserving time-series aggregation."
last_updated: 2026-10-07
keywords:
  - kw:timedelta vs dateoffset
  - kw:calendar-aware arithmetic
  - kw:vectorized datetime operations
  - kw:business day calculations
  - kw:time series downsampling
  - kw:relativedelta age calculation
token_budget: ~900
context_tier: Medium
depends:
  required:
    - 251-python-datetime-core.md  # Core datetime types and timezone handling
  optional:
    - 251b-python-datetime-integration.md  # Streamlit, Plotly, SQL integration
    - 252-python-pandas-core.md  # Pandas performance patterns
---
# Python DateTime Advanced Patterns

## Scope

**What This Rule Covers:**
Elapsed/calendar/business arithmetic, exact age/duration, date ranges, missing data and measured downsampling.

**When to Load This Rule:**
When arithmetic/calendar/aggregation behavior matters; read integration companion for UI/database/display boundaries.

## Contract

### Inputs and Prerequisites

- Actual datetime types/zones/precision and installed pandas/dateutil, business calendar/holidays and period/fiscal definition.
- Exact elapsed versus local-calendar requirement, reference clock and aggregation/missing policy.

### Mandatory

- Use Timedelta for fixed elapsed durations and DateOffset/appropriate calendar offset or relativedelta for calendar periods. A month isn't thirty days; a local calendar day across DST isn't always 24 elapsed hours. Python aware arithmetic semantics also need explicit expected checks.
- Verify MonthEnd/BDay/CustomBusinessDay behavior on already-boundary dates, weekends/holidays and local zones; default business days do not know the organization's holidays. No blanket US federal calendar substitution.
- Duration .days floors whole days; total_seconds preserves fractional elapsed duration. Negative intervals, missing dates and business rounding have defined policy.
- Calculate exact age from calendar birthday/year rules and fixed reference date. days//365 isn't a ±one-day-accurate age and can be wrong near leap/birthday boundaries; don't replace correct arithmetic merely above a dataset-size threshold.
- Prefer vectorized operations where semantics/performance fit, with .loc assigned to intended frame/index. Scalar/apply can be valid for unsupported calendars; measure rather than guarantee 100x or arbitrary size quotas.
- Period conversions can discard timezone; fiscal quarter/month boundaries must match contract. date_range frequency/version/inclusivity/zone must be explicit, not stale aliases assumed universal.
- Reindex only with appropriate unique sorted key/group. Forward-fill changes meaning and can leak future/other-entity state; bound fill by domain/gap policy and never automatically fill missing counts or observations.
- Resample/Grouper needs datetime-compatible index or explicit on/key/level; DatetimeIndex isn't the only supported path. Define origin/closed/label/timezone and aggregation per column; no mean on every measure or averaging averages without weights.
- Downsample for display only when preserving business totals/extrema/gaps and label the reduction. Converting date axis to categorical strings can lose spacing/sorting/time navigation; removing zones isn't an automatic performance fix.
- Benchmark approved representative data with matched versions/dtypes and verify numeric/temporal equivalence. No caching TTL or new dateutil install unless needed/authorized.

### Execution Steps

1. Inspect temporal/calendar and aggregate contract plus existing operations.
2. Implement minimal correct offset/duration/group/resample with explicit boundaries/missing policy.
3. Test DST/month/leap/birthday/negative/gap and entity separation against independent expected values.
4. Run project checks and measured performance where approved; report reduction/precision gaps.

### Validation

- Elapsed/calendar/holiday/age computations meet exact semantics at boundaries.
- Assignments/periods/resample/fill preserve entity/time grain and stated missing values.
- Downsample/performance claims measured and reduced chart semantics disclosed.

## References

- [Pandas time series/calendar offsets](https://pandas.pydata.org/docs/user_guide/timeseries.html)
- [Dateutil relativedelta](https://dateutil.readthedocs.io/en/stable/relativedelta.html)
- [Pandas resample](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html)
