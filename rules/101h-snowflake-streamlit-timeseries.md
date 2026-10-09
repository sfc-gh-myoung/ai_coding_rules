---
schema_version: v4.0
rule_version: v3.0.0
description: "Time series aggregation for Streamlit charts: purpose-driven methods, SQL-side bucketing, current pandas frequency aliases, timezone and gap handling and transparent reduction."
last_updated: 2026-10-07
keywords:
  - kw:time series smoothing
  - kw:pandas resample
  - kw:SCADA visualization
  - kw:aggregation method selection
  - kw:high-frequency sensor data
  - kw:Streamlit chart performance
token_budget: ~900
context_tier: Low
depends:
  optional:
    - 101a-snowflake-streamlit-visualization.md  # Core visualization patterns
---
# Streamlit Time Series Aggregation

## Scope

**What This Rule Covers:**
Reducing and smoothing high-frequency time series (sensor, SCADA, PMU, IoT, metrics) for Streamlit charts: bucket size and method selection, Snowflake TIME_SLICE/DATE_TRUNC aggregation, pandas resample and EWMA, timezones, gaps and disclosure.

**When to Load This Rule:**
When time series charts are noisy, slow or misleading at native granularity; load `101a-snowflake-streamlit-visualization.md` for chart library selection.

## Contract

### Inputs and Prerequisites

- Timestamp type (TIMESTAMP_NTZ, LTZ or TZ), sampling interval, value semantics (levels, rates, counts, limits) and data volume.
- The question the chart answers (trend, peaks, compliance, anomalies) and any regulatory or safety interpretation.

### Mandatory

- Choose aggregation by purpose: mean or median for trends, max/min (or min/max bands) when peaks and sags matter, sum for counts, last for state; never hide safety-relevant extremes behind averages.
- Aggregate large data in Snowflake (`TIME_SLICE` or `DATE_TRUNC` with AVG/MIN/MAX/COUNT) before transfer, then use pandas only for modest local reshaping.
- Use frequency aliases supported by the installed pandas version (pandas 2.2+ uses lowercase `h`, `min`, `s`; uppercase `H` is deprecated).
- Handle timezones explicitly: NTZ values carry no zone, LTZ values follow the session timezone and TZ values carry offsets; convert to one zone before resampling and label the zone on charts.
- Include per-bucket counts and detect gaps or missing readings; do not interpolate or forward-fill across gaps without disclosing it.
- Document NaN handling: pandas resample aggregations skip NaN by default, so empty buckets appear as NaN; decide whether to show gaps or fill them.
- Disclose reduction to viewers (original vs displayed granularity or points and the method) and offer granularity or method controls when users need to explore.
- EWMA and rolling smoothing parameters (span, window) are chosen and labeled per use case and do not imply original resolution was retained.
- Validate aggregated results against raw data for sample windows (counts, extremes) and confirm rendering performance with real volumes.

### Execution Steps

1. Read timestamp types, interval, volume and chart purpose.
2. Implement SQL-side bucketing and any local smoothing with purpose-appropriate methods, timezone handling and gap detection.
3. Reconcile aggregated windows to raw data and test rendering and controls.
4. Report method, granularity, disclosure and verification evidence.

### Validation

- Method matches the question; extremes preserved where they matter.
- Aggregation pushed to Snowflake; pandas aliases current.
- Timezone, gaps and NaN handling explicit and disclosed.
- Aggregates reconcile to raw samples; chart performance verified.

## References

- [TIME_SLICE](https://docs.snowflake.com/en/sql-reference/functions/time_slice)
- [DATE_TRUNC](https://docs.snowflake.com/en/sql-reference/functions/date_trunc)
- [pandas resample](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html)
- [pandas offset aliases](https://pandas.pydata.org/docs/user_guide/timeseries.html#offset-aliases)
- [Snowflake timestamp types](https://docs.snowflake.com/en/sql-reference/data-types-datetime)
