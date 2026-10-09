---
schema_version: v4.0
rule_version: v5.0.0
description: Supported Snowflake trace-event and OpenTelemetry span APIs, bounded instrumentation, and schema-grounded metrics.
last_updated: 2026-10-07
keywords:
  - kw:snowflake-telemetry-python
  - kw:create_span context manager
  - kw:128 event span limit
  - kw:nested span hierarchy
  - kw:TRACE_LEVEL configuration
  - kw:span attribute enrichment
  - kw:snowsight
token_budget: ~1200
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
    - 111-snowflake-observability-core.md  # Telemetry configuration and event tables
  optional:
    - 111a-snowflake-observability-logging.md  # Logging best practices
    - 111c-snowflake-observability-monitoring.md  # Monitoring, Snowsight interfaces, analysis
    - 103-snowflake-performance-tuning.md  # Performance optimization using trace data
---
# Snowflake Observability: Distributed Tracing and Metrics

## Scope

**What This Rule Covers:**
Trace events/attributes, supported custom spans, hierarchy/correlation, bounded volume, resource metrics and actual collection verification.

**When to Load This Rule:**
When instrumenting or diagnosing Snowflake handler traces, span performance, and metrics.

## Contract

### Inputs and Prerequisites

- Actual handler language/runtime, installed supported telemetry/OpenTelemetry APIs, destination/levels and expected operation boundaries.
- Approved emission/config/query scope, privacy/volume budget, correlation requirements and current record schema.

### Mandatory

- Verify supported APIs rather than trust older examples. Python Snowflake telemetry documents add_event and set_span_attribute; current custom spans use OpenTelemetry trace.get_tracer/start_as_current_span. Do not invent telemetry.create_span/set_attribute/emit_metric as mandatory package APIs.
- Make required packages available through the actual runtime/package policy; defaults and Streamlit/container environment rules differ. No unapproved installation or global environment change.
- Use context-managed supported custom spans and close them before handler completion so events can be captured. Preserve parent/context across asynchronous/external boundaries using supported propagation; no universal automatic cross-system inheritance claim.
- Instrument meaningful operation boundaries with child spans only where diagnostic value warrants overhead. Do not impose a universal 100ms cutoff or claim tracing costs less than 5% without measurements.
- Record safe bounded attributes such as operation, counts, units, stage and actual outcome. Avoid secrets/PII/prompts/raw exception data and unbounded high-cardinality record IDs.
- Current trace guidelines allow up to 128 events and 128 span attributes per span. Aggregate/sample progress to stay within supported limits; repeated attribute keys overwrite values and repeated event names add records. Do not certify completeness when data may be omitted.
- ON_EVENT is not simply errors-only; collection depends on trace instrumentation and documented behavior. Choose effective TRACE_LEVEL/METRIC_LEVEL from workload and cost needs, inspect hierarchy, and scope temporary changes with restoration approval.
- Snowflake can collect system CPU/memory metrics for supported runtimes without custom emission code. Inspect RECORD name/unit/type and VALUE before queries; no assumed universal cpu_usage_percent flat column or unverified custom-metric API.
- Measure elapsed durations with a captured monotonic start locally or documented span timestamps in telemetry. Never subtract two immediate time.time calls or label lazy query construction as completed execution.
- Track successful/failed/partial operations honestly and preserve exception propagation. A batch with rejected records is not total_success merely because the loop returned.
- Query actual event columns: TRACE IDs, RECORD span name, RECORD_ATTRIBUTES and START_TIMESTAMP/TIMESTAMP. Correlate by real trace/span/query identity and appropriate grain; joining every log to every span in a trace can fan out results.
- Logging attributes, trace attributes and system metrics are distinct telemetry types. Verify representative emissions/metrics through destination/effective thresholds with realistic ingestion delay; local mocks do not prove persisted traces.
- SQL text tracing and external propagation/export require privacy review and authorization. Do not enable accountwide tracing or send telemetry to arbitrary collectors by default.

### Execution Steps

1. Inspect runtime APIs, existing instrumentation, effective destination/levels and operation boundaries.
2. Add minimal supported events/attributes/spans with safe correlation, bounded counts and correct lifecycle.
3. Test synthetic lifecycle/failure/sampling/duration behavior without account operations.
4. Under runtime approval, emit representative data and inspect correlated actual traces/metrics using the real event schema.
5. Measure overhead/volume and report gaps; restore approved temporary settings and preserve failures.

### Validation

- APIs/packages and context lifecycle supported; spans close before completion and correlation remains meaningful.
- Limits/privacy/sampling and actual partial outcomes represented honestly, durations/units correct.
- System metrics and trace/log schemas distinguished; no nonexistent flat columns or invented telemetry APIs.
- Persisted collection verified where authorized, no guaranteed overhead/completeness or errors-only ON_EVENT claim.
- Deliver instrumentation/query design and exact synthetic/runtime verification limits.

## References

- [Python trace events and custom spans](https://docs.snowflake.com/en/developer-guide/logging-tracing/tracing-python)
- [Tracing guidelines and limits](https://docs.snowflake.com/en/developer-guide/logging-tracing/tracing)
- [System metrics](https://docs.snowflake.com/en/developer-guide/logging-tracing/metrics)
- [Event columns](https://docs.snowflake.com/en/developer-guide/logging-tracing/event-table-columns)
- `111-snowflake-observability-core.md` for collection/level configuration.
