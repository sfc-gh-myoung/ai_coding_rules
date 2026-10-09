---
schema_version: v4.0
rule_version: v3.0.0
description: "Authorized typed pandas IO, permission-scoped Streamlit caches/filters and semantically correct chart/export boundaries."
last_updated: 2026-10-07
keywords:
  - kw:streamlit cache_data
  - kw:plotly aggregation
  - kw:interactive dataframe filtering
  - kw:csv download button
  - kw:dtype optimization caching
  - kw:pandas streamlit plotly
  - kw:pandas
token_budget: ~1000
context_tier: Medium
depends:
  required:
    - 252-python-pandas-core.md  # Core Pandas patterns
  optional:
    - 252a-python-pandas-performance.md  # Memory optimization and groupby
    - 101a-snowflake-streamlit-visualization.md  # Plotly chart patterns
    - 101b-snowflake-streamlit-performance.md  # Caching strategies
---
# Pandas IO and Integration Patterns

## Scope

**What This Rule Covers:**
Load/error/type contracts, selective cache/freshness, UI filters, chart aggregation and safe exact exports.

**When to Load This Rule:**
When pandas crosses file/Streamlit/Plotly boundaries; read actual cache/visualization companions for those implementation tasks.

## Contract

### Inputs and Prerequisites

- Source/path/format/schema/dtypes/encoding/timezone and actual pandas/UI/chart versions.
- Authorized data/tenant/cache/export scope, expected rows/keys/totals and freshness/chart aggregation requirements.

### Mandatory

- Load only approved paths/hosts and required columns with explicit format/schema/NA/time semantics. Parsing failure, inaccessible source and genuinely empty result are different states; don't return a cached empty frame as successful outage recovery.
- Validate required columns/types/row counts before downstream widgets; optimize dtype only after range/precision checks, never blanket status_code.astype(int8). Keep errors safe without leaking local/private paths or data.
- Cache only eligible deterministic authorized computations with key including actual source identity/version/filter/role/user boundary where required and appropriate freshness/TTL. st.cache_data can share across users; don't omit tenant/auth inputs or assume DataFrame copy makes disclosure safe.
- No mandatory cache on every loader or fixed 3600s TTL. Source content can change with same path; explicit invalidation/version is needed. Clear only intended function/entry, not app-wide st.cache_data.clear for routine refresh without impact review.
- Keep loader errors separate from UI messages and verified data; avoid replayed st.error inside cached functions confusing recovery. Cache mutations/dtypes/serialization under actual installed lifecycle API.
- Guard empty data/no options/incomplete date range and NULL categories; widgets provide valid bounded values and actual filtering preserves index/type/security. query expressions must stay trusted/static with safe values; .loc masks are valid, query isn't compulsory.
- Plot raw/detail data when justified and bounded; aggregate/downsample only to intended business/time/entity grain with correct sum/count/weighted mean/extrema. No universal million-row boundary or converting same timestamps into assumed days.
- Keep typed temporal axes/order/zone and explicit units, missing gaps and sample/reduction labels. Rendering width/options follow installed version; static fig construction isn't successful browser render.
- Exports reflect exactly the authorized displayed/defined filtered data with deliberate index/encoding/columns/precision/date/NULL semantics. Bound memory; CSV formula injection and sensitive column/role scope need mitigation for intended spreadsheet consumers.
- Download permission is distinct from on-screen access where policy requires; do not upload/export files externally by implication. Test CSV round-trip and count/key/total reconciliation plus cache role/freshness change.

### Execution Steps

1. Inspect source/schema/cache/widget/chart/export and define exact authorized boundary.
2. Implement minimal typed load, eligible scoped cache and safe bounded filters.
3. Verify chart grain and export round-trip against independent expected values.
4. Run project/browser checks where authorized and report runtime/freshness gaps.

### Validation

- Load errors/empty/schema and dtype precision clearly distinguished; no missing rows hidden.
- Cache/user/source/freshness and filtering boundaries secure, widget states complete.
- Chart/extracted CSV match actual intended grain/data/units, formula and sensitive fields handled.
- Actual browser/download checks separate from static tests; no unauthorized external transfer.

## References

- [Pandas IO](https://pandas.pydata.org/docs/user_guide/io.html)
- [Streamlit cache_data](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data)
- [Streamlit downloads](https://docs.streamlit.io/develop/api-reference/widgets/st.download_button)
- [Plotly charts](https://plotly.com/python/)
- [OWASP CSV injection](https://owasp.org/www-community/attacks/CSV_Injection)
