---
schema_version: v4.0
rule_version: v5.0.0
description: "Bounded Cortex REST clients: endpoint grounding, safe retries, streaming, cost controls, and private observability."
last_updated: 2026-10-07
keywords:
  - kw:cortex rest api
  - kw:exponential backoff retry
  - kw:idempotency keys
  - kw:rest vs aisql decision
  - kw:sse streaming responses
  - kw:token usage monitoring
token_budget: ~1350
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake fundamentals
    - 105-snowflake-cost-governance.md  # Cost monitoring and optimization
  optional:
    - 114-snowflake-cortex-aisql.md  # AISQL for batch processing
---
# Snowflake Cortex REST API Best Practices

## Scope

**What This Rule Covers:**
Endpoint selection, bounded retries, duplicate prevention, client pooling, latency/cost controls, and safe REST observability.

**When to Load This Rule:**
When implementing Cortex REST clients or choosing REST versus AISQL. Read `118a-snowflake-cortex-rest-api-streaming.md` for token authentication and SSE parsing; read `114-snowflake-cortex-aisql.md` for table-oriented AI processing.

## Contract

### Inputs and Prerequisites

- Existing client/configuration, target account URL, documented endpoint revision, supported model, role/region availability, and permitted data boundary.
- Approved authentication mechanism, workload latency/throughput SLOs, input/output budget, retry deadline, and actual installed SDK/client dependencies.
- Explicit authorization for paid canaries, external transmission, deployment, or role/model changes; client implementation alone grants none.

### Mandatory

- Read existing client code before adding calls; preserve established auth, pooling, retries, and error reporting. Verify the operation's request/response schema rather than copying an old endpoint or invented SDK method.
- Current inference docs expose OpenAI-compatible Chat Completions and Anthropic-compatible Messages endpoints; embeddings and Agents have separate contracts. A legacy inference payload is not interchangeable with chat messages or Agent requests. Verify actual account support before deployment.
- Prefer REST for interactive/on-demand applications and evaluate AISQL for governed table/batch processing. Neither choice guarantees a speedup, lower cost, or exemption from rate limits.
- Use documented PAT/OAuth/key-pair JWT authentication and endpoint-specific default-role privileges/model access. Never put credentials in source, URLs, logs, or version control; do not silently change roles or grants.
- Bound input size, output tokens using the endpoint/model's actual option, response bytes, concurrency, connect/read timeouts, total deadline, attempts, and spend. A read timeout is not a total stream deadline. Truncate only with explicit semantics; report missing usage rather than recording zero.
- Reuse a configured session/client for connection pooling and close responses/clients. Streaming requires both the endpoint's streaming option and transport streaming; choose the parser from documented format and actual Content-Type.
- Classify failures before retry: retry documented rate-limit/transient failures with capped exponential backoff and jitter, honoring Retry-After within the total deadline. Do not retry invalid requests, unauthorized access, or every exception. Check application error payloads even when HTTP status is successful.
- Inference POST retries can duplicate billable work; Agent retries can repeat tool effects. A timeout or lost connection does not prove nothing executed. Do not replay uncertain or partially streamed operations unless documented recovery/idempotency and approved effect scope make replay safe.
- Send an idempotency key only when the specific endpoint documents its support and semantics. A client-generated Idempotency-Key header or request hash alone does not provide server deduplication. Use permission-scoped application deduplication/caching where appropriate, without cross-user confidential response reuse.
- Configure circuit-breaker thresholds/cooldowns from the application's failure policy, not universal five-failure/60-second product requirements. Bound recovery probes and distinguish throttling, configuration errors, and service failures.
- Log sanitized request IDs, model, status/error category, attempts, latency, time to first token, completion state, and reported usage. Do not log prompts, completions, tokens, PII, or raw error bodies by default.
- Reconcile token/cost observations against applicable usage views/current pricing with latency caveats. Cortex inference REST requests do not automatically populate AI_OBSERVABILITY_EVENTS; use CORTEX_REST_API_USAGE_HISTORY for their consumption and separate application tracing where needed.

### Execution Steps

1. Inspect client and operation documentation; establish endpoint/model/auth/data scope and compare REST/AISQL workload fit.
2. Implement the smallest compatible client with pooling, format-aware parsing, resource limits, classified retries, and uncertain-outcome handling.
3. Test locally with controlled response/transport fixtures before any separately authorized paid canary.
4. Under canary authorization, check actual authentication, response schema, rate limits, latency distribution, output correctness, usage, and cleanup.
5. Report implementation/configuration, observed metrics, cost assumptions, and unverified account/runtime behavior separately; deploy only within approval.

### Validation

- Authentication/authorization and model/region support are established by actual evidence, or explicitly unverified.
- Fixtures cover 400/auth failures without retries, 429/selected transient backoff, Retry-After, exhausted deadlines, and uncertain POST outcomes without blind replay.
- Token/input/response/concurrency limits work; caches preserve user/data boundaries and usage omissions are not zeros.
- JSON/SSE parsing, timeout/cancellation, pool/response cleanup, and sanitized logs are checked.
- Approved representative canaries meet specified p95/p99/error/cost targets; no claimed SLO or live success comes from static checks alone.

## References

- [Cortex REST API endpoints, authorization, limits, and usage](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-rest-api)
- [REST authentication](https://docs.snowflake.com/en/developer-guide/snowflake-rest-api/authentication)
- [Vector embedding API](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-rest-api/embed-api)
- [Agent run contract](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-run)
- [REST API usage history](https://docs.snowflake.com/en/sql-reference/account-usage/cortex_rest_api_usage_history)
- `118a-snowflake-cortex-rest-api-streaming.md` for auth and stream framing.
