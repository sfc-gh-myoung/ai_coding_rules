---
schema_version: v4.0
rule_version: v5.0.0
description: "Explicit datetime/date/epoch/zone semantics, precise Python-pandas boundaries and accountable parsing."
last_updated: 2026-10-07
keywords:
  - kw:datetime type conversion
  - kw:timezone localize convert
  - kw:datetime now utc
  - kw:pd.Timestamp compatibility
  - kw:date parsing format specification
  - kw:epoch timestamp unit conversion
  - kw:pandas
token_budget: ~1000
context_tier: High
depends:
  required:
    - 200-python-core.md  # Modern Python tooling and practices
  optional:
    - 251a-python-datetime-advanced.md  # Date arithmetic, performance optimization
    - 251b-python-datetime-integration.md  # Streamlit, Plotly, SQL integration
    - 252-python-pandas-core.md  # Pandas performance and anti-patterns
---
# Python DateTime Core Patterns

## Scope

**What This Rule Covers:**
Date versus instant/wall-time types, parsing, epoch units, named zones/DST and loss-aware conversions.

**When to Load This Rule:**
When manipulating Python/pandas dates/timestamps; read arithmetic/integration/pandas companions for those tasks.

## Contract

### Inputs and Prerequisites

- Actual schema/dtypes/samples, installed Python/pandas, source format/epoch unit/timezone and intended precision/calendar meaning.
- Missing/invalid/DST policy, reference clock and authorized parsing/test scope.

### Mandatory

- Inspect actual types/source meaning before converting. date, naive wall-time, aware instant, Timestamp and numpy datetime64 differ; UTC storage suits instants, not all local dates/business calendar schedules.
- Use datetime.now(UTC)/fromtimestamp(value,tz=UTC) under supported Python instead of deprecated naive UTC APIs. Naive .timestamp assumes host local zone; timezone replacement assigns interpretation, not instant conversion.
- Timestamp often compares correctly with Python datetime when awareness/type semantics align; don't claim pandas2 always rejects it. Date versus datetime and aware versus naive comparisons need explicit contract; avoid unnecessary to_pydatetime that discards nanoseconds.
- Parse known format explicitly and use installed ISO8601/mixed handling deliberately. No universal thousand-row threshold/speedup. errors=coerce produces NaT; count/retain rejects and never silently hide invalid required timestamps.
- Localize naive values in their actual source zone with explicit ambiguous/nonexistent DST policy; utc=True on naive input assumes UTC, not local source conversion. Convert already-aware values with tz_convert/astimezone; don't localize twice or blindly ambiguous=infer unordered data.
- Named zones preserve DST rules; fixed offsets are valid when source specifies a fixed offset, not substitute for a region calendar. Unknown source timezone remains unknown rather than guessed.
- Distinguish tz_localize(None) preserving wall time from UTC conversion then zone removal preserving intended UTC representation. Removing timezone for speed alone changes semantics and needs approved boundary contract.
- Epoch parsing uses explicit unit/origin and UTC semantics; guard range/precision/NaT. Integer timestamp dtype unit isn't universally ns across pandas versions; don't blindly divide astype(int64) by 1e9 or turn NaT sentinel into a real epoch.
- Scalar conversion checks missing/type safely; pd.isna on arrays isn't a scalar Boolean and Timestamp subclasses datetime, so check desired precision conversion deliberately. .dt accessor requires correct datetime dtype, not assumed object strings.
- Vectorize column operations when useful and preserve index/type/timezone; scalar paths are valid where appropriate. Record precision/zone loss at library/JSON/database boundaries.
- Test UTC/non-UTC, offset/mixed awareness, invalid/empty/NaT, fractional/epoch units, DST/leap and out-of-range values with frozen clock. No new dateutil/pytz dependency for operations standard tools already support.

### Execution Steps

1. Inspect source/dtypes/version and define instant/date/zone/precision/reject contract.
2. Implement minimal explicit parse/localize/convert and boundary adaptation.
3. Verify independent expected instants/types and rejected values at temporal boundaries.
4. Run project checks and report precision/zone/parser gaps.

### Validation

- Types/awareness/source zone/epoch unit correct; no accidental host-local interpretation.
- Invalid/NaT/DST ambiguity explicitly handled and no silent precision/date loss.
- Round-trip expected values and scalar/vectorized behavior tested; claims match installed versions.

## References

- [Python datetime](https://docs.python.org/3/library/datetime.html)
- [zoneinfo](https://docs.python.org/3/library/zoneinfo.html)
- [Pandas time series](https://pandas.pydata.org/docs/user_guide/timeseries.html)
- [Pandas to_datetime](https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html)
