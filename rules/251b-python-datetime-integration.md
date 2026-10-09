---
schema_version: v4.0
rule_version: v3.0.0
description: "Typed bound temporal database parameters, timezone-correct UI ranges and precise JSON/chart/display boundaries."
last_updated: 2026-10-07
keywords:
  - kw:parameterized queries datetime
  - kw:streamlit date input
  - kw:SQL injection datetime
  - kw:plotly datetime axis
  - kw:datetime display formatting
  - kw:allowlist validation SQL keywords
token_budget: ~950
context_tier: Medium
depends:
  required:
    - 251-python-datetime-core.md  # Core datetime types and timezone handling
  optional:
    - 251a-python-datetime-advanced.md  # Date arithmetic and performance
    - 101a-snowflake-streamlit-visualization.md  # Plotly visualization patterns
---
# Python DateTime Integration Patterns

## Scope

**What This Rule Covers:**
Database adapter/binding/type boundaries, UI date/time filters, JSON/display and Plotly temporal aggregation.

**When to Load This Rule:**
When timestamps cross database/UI/JSON/visual boundaries; load actual Streamlit/Snowflake rules for those implementation tasks.

## Contract

### Inputs and Prerequisites

- Actual adapter/schema/placeholder types and source/consumer timezone/precision, installed UI/chart version and selected range meaning.
- Validated temporal data, query/report scope and explicit display/freshness contract.

### Mandatory

- Bind datetime/date values with actual adapter semantics, not f-string SQL. sqlite qmark, connector/SQLAlchemy placeholders and Snowpark params aren't interchangeable. Keywords/identifiers use validated syntax/builders; date-part arguments may be bindable on some engines, not universally prohibited.
- Prefer native temporal database columns where designing schema; don't migrate an existing string source unasked. Parse legacy strings explicitly with reject evidence and assess session/column TIMESTAMP/date timezone coercion before writes/comparison.
- Preserve appropriate aware/naive/date representation per database type and source contract; PostgreSQL/Snowflake type semantics differ. Decimal epoch/precision conversions tested, no guessed timezone from server defaults.
- UI date inputs return dates/ranges with possible incomplete selection; convert explicitly at filtering boundary. Validate start<=end and use half-open next-day bound for inclusive date ranges in the intended local zone then UTC; <=end midnight excludes most of final day.
- Combine dates/times with actual source/user zone and DST ambiguity policy. Cross-midnight time windows require explicit logic; applying .dt.time can lose zone/date and mishandle overnight data.
- Use formatting only for display, retain typed timestamps for sorting/filtering/chart axis. strftime + Z requires UTC conversion; preserve fractions/timezone where interoperability needs them. ISO JSON with explicit offsets and tested consumer parsing, not assumed lossless nanoseconds through Python datetime.
- Streamlit/chart API supported width/date types depend on actual installed release; don't prescribe use_container_width from a guessed version. Caching keys include authorized user/time/query boundaries and actual freshness.
- Plotly date axes need valid sorted typed dates and stated zone/granularity/gaps. Aggregate large datasets according to business sum/count/weighted mean/extrema, not blindly mean; ranges/ticks don't prove correct data.
- Test database binding, same-day/end-date/DST/overnight, missing range/NaT, JSON round-trip and display/chart sorting independently. Query execution/loads/UI server mutations need actual approval.

### Execution Steps

1. Inspect adapter/schema/UI/data and define type/zone/range/output contracts.
2. Implement safe binding and explicit UI/JSON/chart boundary adaptation.
3. Test temporal/security edge cases and independent aggregation totals with synthetic inputs.
4. Run project checks and approved integration tests; report unexecuted database/UI gaps.

### Validation

- Parameters/identifiers safe and actual database type/timezone semantics preserved.
- UI ranges include intended days/overnight/DST with incomplete/invalid inputs handled.
- Display/JSON/chart preserve explicit precision/zone/grain or report loss; no runtime claim from static format.

## References

- [Python datetime](https://docs.python.org/3/library/datetime.html)
- [Pandas time series](https://pandas.pydata.org/docs/user_guide/timeseries.html)
- [Streamlit date_input](https://docs.streamlit.io/develop/api-reference/widgets/st.date_input)
- [Plotly time-series axes](https://plotly.com/python/time-series/)
- [SQLAlchemy bound expressions](https://docs.sqlalchemy.org/en/20/core/sqlelement.html)
