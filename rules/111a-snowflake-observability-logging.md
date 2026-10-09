---
schema_version: v4.0
rule_version: v5.0.0
description: Runtime-supported Snowflake handler logging with safe structured attributes, volume controls, and correlated collection verification.
last_updated: 2026-10-07
keywords:
  - kw:handler logging
  - kw:log volume control
  - kw:sampling strategy
  - kw:conditional logging
  - kw:event table routing
  - kw:tight loop logging
  - kw:udf
token_budget: ~1100
context_tier: High
depends:
  required:
    - 100-snowflake-core.md
    - 111-snowflake-observability-core.md
---
# Snowflake Observability: Logging Best Practices

## Scope

**What This Rule Covers:**
Handler logging APIs, effective levels/routing, safe structured context, bounded sampling, truthful operation outcomes and collection checks.

**When to Load This Rule:**
When instrumenting Snowflake Python/Java/JavaScript handlers or investigating missing/expensive logs.

## Contract

### Inputs and Prerequisites

- Actual handler language/runtime, supported logging API, existing logger config, active event destination and effective thresholds.
- Approved emission/query/configuration scope, safe attribute taxonomy, volume budget, retention/access policy and expected correlated events.

### Mandatory

- Use supported language/runtime logging APIs: Python logging, documented Java SLF4J integration, or Snowflake-supported JavaScript logging. Do not assume console or print universally routes to event tables.
- Create appropriately named module/class loggers and preserve framework handlers/configuration. Avoid broad basicConfig/handler replacement in managed runtime; inspect effective Python and SQL levels before overrides.
- INFO milestones, WARN anomalies and ERROR/CRITICAL failures reflect actual severity. Python CRITICAL maps to FATAL in Snowflake; production severity policy depends on operational needs, not a universal WARN-only requirement.
- Approved temporary verbose logging must be scoped, time-bounded, cost/privacy-reviewed and restored. No fixed 10-100x multiplier or universal entries-per-minute threshold; measure actual volume/signal.
- Prefer operation/batch summaries to per-row UDF logs. Apply meaningful conditional/rate/sampling controls when measured workload volume warrants them; record sampling context and counts so consumers do not mistake sampled logs for complete audit evidence.
- Repeated failures can also flood logs; aggregate/rate-limit duplicate failures while retaining critical alerts/counts and required audit events. Do not swallow failed records then claim every record processed successfully.
- Never log credentials/tokens, personal/sensitive rows, unapproved SQL/prompts or arbitrary exception bodies. Short unsalted hashes are not guaranteed anonymization; use approved opaque correlation identifiers instead.
- Use deferred message formatting and guard expensive diagnostics when appropriate. Logging must not cause repeated count/collect actions, convert a Snowpark DataFrame to a local list, or use len(df) as an assumed distributed count.
- Python logger extra key/value attributes are supported and stored in RECORD_ATTRIBUTES; prefer safe structured fields over delimiter-split strings. Span attributes describe tracing and are not a universal substitute for log attributes.
- Query actual event schema: RECORD severity, SCOPE logger name, VALUE message and applicable attribute fields. Do not query invented BODY or flat severity columns or infer log persistence merely from emitted calls.
- Verify correlated handler events after authorized runtime invocation with effective thresholds/destination and realistic ingestion delay. Missing logs remain unverified until diagnosed; no accountwide routing/debug mutation as automatic fallback.
- Logging success means actual completed work, not queued/lazy transformations. Preserve exception propagation and partial-failure semantics; clean sensitive errors before exposed diagnostics.
- External log export/integrations and configuration/grant/lifecycle changes need separate authorization; retain immutable failure evidence and unrelated telemetry.

### Execution Steps

1. Inspect handler and current logger/telemetry destination/threshold, supported API and privacy/volume policy.
2. Add safe structured milestones/errors and appropriate conditional/sampling summaries without costly extra data actions.
3. Test logger messages/attributes/partial failures locally with synthetic inputs and review redaction/volume behavior.
4. Under runtime approval, emit representative events and verify correlated records through actual event schema.
5. Report actual outcomes and missing collection checks; restore approved temporary overrides without deleting unrelated logs.

### Validation

- Supported logging API/logger config preserved, severity/threshold semantics correct and intended events correlated where tested.
- Secrets/PII and arbitrary exception payloads excluded, structured attributes queryable and sampling completeness disclosed.
- No tight-loop flood, repeated distributed diagnostics, blanket hash-anonymization claim or swallowed failure success.
- Actual emission/collection tests distinct from synthetic logger tests; unavailable runtime evidence remains unverified.
- Deliver scoped instrumentation, volume/privacy rationale, exact checks and limitations.

## References

- [Python handler logging and custom attributes](https://docs.snowflake.com/en/developer-guide/logging-tracing/logging-python)
- [Snowflake logging APIs](https://docs.snowflake.com/en/developer-guide/logging-tracing/logging)
- [Python logging](https://docs.python.org/3/library/logging.html)
- [Event-table columns](https://docs.snowflake.com/en/developer-guide/logging-tracing/event-table-columns)
- `111-snowflake-observability-core.md` for destination/levels and cost.
