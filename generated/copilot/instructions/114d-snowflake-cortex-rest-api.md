---
appliesTo:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.sh"
---
<!-- Generated for GitHub Copilot repository instructions. See https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions -->

**Keywords:** Cortex REST API, API authentication, streaming responses, API retries, idempotency, rate limits
**Depends:** 100-snowflake-core, 105-snowflake-cost-governance, 111-snowflake-observability

**TokenBudget:** ~350
**ContextTier:** Medium

# Snowflake Cortex REST API Best Practices

## Purpose
Provide production patterns for Cortex REST API usage for interactive/low-latency workloads: authentication, Complete/Embed/Agents endpoints, retries, idempotency, streaming, cost controls, and observability.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** REST API usage for Complete, Embed, Agents; client patterns; when to use REST vs AISQL

## Contract
- **Inputs/Prereqs:**
  - Connectivity and credentials for Snowflake REST API (per account region)
  - Model allowlists and RBAC aligned with organizational policy
  - Clear latency/throughput SLOs
- **Allowed Tools:** REST clients with backoff/retry; streaming APIs; structured logging/tracing; AI Observability
- **Forbidden Tools:**
  - Unauthenticated/implicit credential flows
  - Infinite retries; unbounded request payloads
- **Required Steps:**
  1. Prefer REST for interactive latency-sensitive tasks; prefer AISQL for batch throughput
  2. Implement retry with exponential backoff and jitter on retryable statuses
  3. Enforce idempotency keys for non-idempotent operations
  4. Limit tokens and response size; stream outputs when supported
  5. Log request/response metadata (not PII) and integrate tracing
- **Output Format:** Minimal client snippets with safe defaults
- **Validation Steps:** Canary tests pass; SLO latency met; rate limits respected; costs within budget

## Key Principles
- Align client design with SLOs: use streaming and timeouts; cap tokens
- Separate per-request model options (e.g., max_tokens) from global defaults
- Capture metrics (latency, tokens, error rates); build alerting for regressions

## 1. Usage Guidance: REST vs AISQL
- Use REST for: user-facing chat/assistants, embeddings on-demand, agentic interactions where latency matters
- Use AISQL for: large table processing, batch embeddings, aggregations across many rows

## 2. Retry & Backoff (Python sketch)
```python
import time, random

def with_retry(call, max_attempts=5, base=0.5, cap=8.0):
    attempt = 0
    while True:
        try:
            return call()
        except RetryableError as e:
            attempt += 1
            if attempt >= max_attempts:
                raise
            sleep = min(cap, base * (2 ** (attempt - 1)))
            time.sleep(sleep + random.random() * 0.2)
```

## 3. Idempotency Key (HTTP sketch)
```http
POST /cortex/complete HTTP/1.1
Idempotency-Key: 4f2b6c1d-8c0d-4a32-8a2a-98a1aa0b0c77
Content-Type: application/json

{"model":"llama3.1-8b","prompt":"Answer briefly.","max_tokens":64}
```

## 4. Streaming (pseudo)
```python
for chunk in client.complete_stream(model="llama3.1-8b", prompt=prompt, max_tokens=64):
    print(chunk.delta, end="")
```

## 5. Cost Controls
- Cap `max_tokens` and truncate inputs; preflight with token counters when available
- Cache frequent prompts/responses; deduplicate with hashes
- Set sane client timeouts; drop requests exceeding UX thresholds

## 6. Observability
- Log request metadata (model, token counts, latency, status)
- Emit traces and associate with evaluation events in AI Observability

## Quick Compliance Checklist
- [ ] REST used for interactive use cases; AISQL for batch
- [ ] Retry with exponential backoff and jitter implemented
- [ ] Idempotency keys used for non-idempotent operations
- [ ] Token limits and streaming enabled where applicable
- [ ] Logging/tracing integrated; costs and latency monitored

## Validation
- **Success checks:** SLO latency met; low error rates; duplicate request safety via idempotency
- **Negative tests:** Simulated timeouts and 429/5xx retried successfully; oversized prompts rejected

## Response Template
```bash
# Minimal client invocation (idempotency + timeouts)
curl -sS -X POST "$CORTEX_URL/complete" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: $(uuidgen)" \
  -H 'Content-Type: application/json' \
  --max-time 15 \
  -d '{"model":"llama3.1-8b","prompt":"Hello","max_tokens":64}'
```

```python
# Retry with backoff (sketch)
def call_complete(client, payload):
    return client.complete(**payload)

resp = with_retry(lambda: call_complete(client, {
    "model": "llama3.1-8b", "prompt": prompt, "max_tokens": 64
}))
```

## References

### External Documentation
- [Cortex REST API](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-rest-api)
- [Snowflake Cortex AISQL](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql)
- [AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability)

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **AISQL**: `114-snowflake-cortex-aisql.md`
- **Cost Governance**: `105-snowflake-cost-governance.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
- **Observability**: `111-snowflake-observability.md`


