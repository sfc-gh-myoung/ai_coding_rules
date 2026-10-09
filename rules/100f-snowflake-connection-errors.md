---
schema_version: v4.0
rule_version: v5.0.0
description: Evidence-based Snowflake connection error classification, safe remediation, and bounded replay-aware retry.
last_updated: 2026-10-07
keywords:
  - kw:connection error classification
  - kw:network policy violation detection
  - kw:message-first error analysis
  - kw:VPN disconnect diagnosis
  - kw:snowflake.connector.errors.DatabaseError
  - kw:error code 08001 ambiguity
  - kw:snowpark
token_budget: ~1100
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake fundamentals and connection patterns
  optional:
    - 101e-snowflake-streamlit-sql-errors.md  # SQL error handling patterns for Streamlit
    - 101b-snowflake-streamlit-performance.md  # Connection caching with @st.cache_resource
---
# Snowflake Connection Error Classification

## Scope

**What This Rule Covers:**
Message-first classification of connection failures, network policy versus authentication diagnosis, uncertainty, user guidance, and safe retry.

**When to Load This Rule:**
When handling Snowflake connector/Snowpark connection exceptions or implementing actionable connection-error reporting.

## Contract

### Inputs and Prerequisites

- Exception type/message, connector version, errno and sqlstate separately, operation phase, auth method, approved endpoint, and relevant query ID.
- Current application error handling and retry policy; authorized diagnostic scope and redaction requirements.

### Mandatory

- Inspect specific message evidence before generic code fallback. Connector errno is not SQLSTATE: 08001/08003/08004 are connection SQLSTATE categories, not universal expired-auth mappings.
- Prioritize explicit network-policy evidence before auth/connection fallback; then distinguish specific authentication, permission, transient transport, generic connection, and unknown failures using corroborating context. Conflicting evidence remains uncertain.
- Do not infer VPN loss from every policy block or classify broad words such as access denied as network policy. IP/Token denial may involve configured network rules or auth context; verify observed message and environment.
- Do not label every 390xxx code expired authentication or every 250001 network policy. Check current driver/product documentation and actual message; invalid credentials, expired tokens, wrong account, and policy rejection require different remediation.
- Return a stable category, bounded confidence/evidence, safe user guidance, and retry eligibility. Preserve original exception chaining and query/request IDs while redacting credentials, tokens, private endpoints/IPs, and sensitive SQL from exposed logs.
- Network-policy guidance checks approved network/VPN/private connectivity and escalates to the owner; never automatically loosen allowlists, disable TLS/certificate validation, or recommend blanket public access.
- Auth guidance follows configured OAuth/key-pair/browser/service identity flow. A connection-test command is diagnostic, not a universal token refresh; verify command availability and approval before invocation.
- Permission guidance checks role/object scope without self-granting or escalating. Missing-object and not-authorized errors can be deliberately ambiguous; do not assert object absence solely from the message.
- Retry only confirmed retryable connection/read operations within approved bounds. Use timeout, capped exponential backoff with jitter, cancellation, and observable attempts; avoid retrying persistent auth/policy/permission failures.
- A transport timeout during DDL/DML can leave the server outcome unknown. Inspect query/transaction state before replay; do not wrap arbitrary database mutations in a generic retry decorator.
- Unknown errors stay unknown with redacted diagnostic escalation, not a fabricated cause. User-facing text must not claim an automatic retry happened when none was performed.

### Execution Steps

1. Read existing connection/error paths and extract structured exception fields without logging secrets.
2. Apply tested specific-to-generic message/context rules; retain code/SQLSTATE as supporting evidence.
3. Provide category-specific approved remediation and decide retryability from operation phase and replay safety.
4. Implement scoped handling/backoff and state inspection; preserve original failures and avoid automatic security changes.
5. Test overlapping/unknown messages and simulated transport outcomes; run live connection checks only when authorized.

### Validation

- Network-policy evidence is not swallowed by generic auth/08001 fallback; errno/SQLSTATE remain distinct.
- Expired/invalid auth, permissions, transient transport, generic connection, and unknown cases give truthful bounded guidance.
- Mixed-case, missing fields, overlapping messages, and unfamiliar driver errors covered without overly broad substring matches.
- Retry limits/cancellation and uncertain-mutation outcomes verified; no credential exposure, implicit token refresh, TLS bypass, or privilege escalation.
- Report classifier behavior/tests and diagnostic limitations; simulated fixtures are not proof of live account connectivity.

## References

- [Python connector errors](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-api#errors)
- [Connectivity troubleshooting](https://docs.snowflake.com/en/user-guide/client-connectivity-troubleshooting/error-messages)
- [Network policies](https://docs.snowflake.com/en/user-guide/network-policies)
- [Key-pair authentication](https://docs.snowflake.com/en/user-guide/key-pair-auth)
- [OAuth](https://docs.snowflake.com/en/user-guide/oauth-snowflake)
- `101e-snowflake-streamlit-sql-errors.md` for Streamlit presentation.
