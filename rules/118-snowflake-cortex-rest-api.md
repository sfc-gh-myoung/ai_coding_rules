# Snowflake Cortex REST API Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:cortex-api, kw:rest-api
**Keywords:** idempotency, rate limits, Complete endpoint, Embed endpoint, exponential backoff, REST API, Cortex API, response format, retry logic, cost controls, batch vs interactive
**TokenBudget:** ~4250
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 105-snowflake-cost-governance.md, 111-snowflake-observability-core.md
**Companions:** 118a-snowflake-cortex-rest-api-streaming.md

## Scope

**What This Rule Covers:**
Production patterns for Cortex REST API: retry logic with exponential backoff, idempotency keys, cost controls, observability, and REST vs AISQL decision guidance.

**When to Load This Rule:**
- Building applications using Cortex REST API
- Implementing retry logic and error handling for REST APIs
- Choosing between REST API vs AISQL for workloads
- Optimizing API performance and cost
- For authentication (PAT/OAuth/JWT) and SSE streaming, see **118a-snowflake-cortex-rest-api-streaming.md**

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake fundamentals
- **105-snowflake-cost-governance.md** - Cost monitoring and optimization
- **111-snowflake-observability-core.md** - Logging and performance monitoring

**Related:**
- **114-snowflake-cortex-aisql.md** - AISQL for batch processing
- **115-snowflake-cortex-agents-core.md** - Cortex Agents REST API
- **107-snowflake-security-governance.md** - Authentication and security

### External Documentation

- [Cortex REST API Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-rest-api) - API endpoints and authentication
- [Complete API Reference](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions#complete) - Text generation endpoint
- [Embed API Reference](https://docs.snowflake.com/en/user-guide/snowflake-cortex/vector-embeddings#embed) - Embedding endpoint

## Contract

### Inputs and Prerequisites

- Connectivity and credentials for Snowflake REST API (per account region)
- Model allowlists and RBAC aligned with organizational policy
- Clear latency/throughput SLOs
- Understanding of REST vs AISQL trade-offs

### Mandatory

- REST clients with backoff/retry logic
- Streaming API support (when available)
- Structured logging/tracing
- AI Observability integration
- Token and response size limits

### Forbidden

- Unauthenticated/implicit credential flows
- Infinite retries or unbounded request payloads
- Storing credentials in code or version control
- Ignoring rate limits or retryable errors

### Execution Steps

1. **Choose API:** Prefer REST for interactive latency-sensitive tasks; prefer AISQL for batch throughput
2. **Implement Retry:** Use exponential backoff and jitter on retryable statuses (429, 503, 504)
3. **Enforce Idempotency:** Add idempotency keys for non-idempotent operations
4. **Limit Resources:** Set max_tokens and response size limits; stream outputs when supported
5. **Monitor:** Log request/response metadata (not PII) and integrate distributed tracing
6. **Validate:** Run canary tests, verify SLO latency, respect rate limits, monitor costs

### Output Format

```python
# Python client with retry and streaming
import requests
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(multiplier=1, min=2, max=30), stop=stop_after_attempt(5))
def call_complete(prompt: str, model: str = "mistral-large") -> str:
    response = requests.post(
        f"https://{account}.snowflakecomputing.com/api/v2/cortex/inference:complete",
        headers={"Authorization": f"Bearer {token}"},
        json={"model": model, "prompt": prompt, "max_tokens": 500},
        stream=True
    )
    response.raise_for_status()
    # Parse SSE stream (stream=True requires line-by-line parsing, NOT response.json())
    result = ""
    for line in response.iter_lines(decode_unicode=True):
        if line and line.startswith("data: "):
            data = json.loads(line[6:])
            if "choices" in data:
                result += data["choices"][0].get("delta", {}).get("content", "")
    return result
```

### Validation

**Pre-Task-Completion Checks:**
- Authentication configured correctly (PAT, OAuth, or JWT)
- Retry logic implemented with exponential backoff and jitter
- Idempotency keys used for non-idempotent operations
- Token limits enforced (max_tokens set)
- Streaming enabled where appropriate
- Request/response logging configured (no PII)
- Rate limits respected

**Success Criteria:**
- Canary tests pass with expected latency
- SLO latency requirements met (p95, p99)
- Rate limits respected (no 429 errors under normal load)
- Costs within budget thresholds
- Error rates below acceptable thresholds

**Negative Tests:**
- Transient errors (503, 504) trigger retry with backoff
- Rate limit errors (429) trigger backoff before retry
- Invalid requests (400) do not trigger retry
- Token limits prevent runaway generation costs

### Design Principles

- **Align with SLOs:** Use streaming and timeouts; cap tokens to meet latency requirements
- **Separate Concerns:** Per-request model options (max_tokens) vs global defaults (retry policy)
- **Observability:** Capture metrics (latency, tokens, error rates); build alerting for regressions
- **Cost Control:** Enforce token limits, monitor usage, alert on anomalies

### Post-Execution Checklist

- [ ] Authentication configured (PAT, OAuth, or JWT)
- [ ] Retry logic with exponential backoff and jitter
- [ ] Idempotency keys for non-idempotent operations
- [ ] Token limits enforced (max_tokens set)
- [ ] Streaming enabled where appropriate
- [ ] Request/response logging (no PII)
- [ ] Rate limits respected
- [ ] Canary tests passing
- [ ] SLO latency met
- [ ] Costs within budget

## Anti-Patterns and Common Mistakes

### Circuit Breaker and Connection Pooling

- **Rule:** After 5 consecutive failures, stop retrying for 60 seconds before attempting again (circuit breaker pattern)
- **Rule:** Use `requests.Session()` for connection reuse across multiple API calls — avoids TCP handshake overhead
- **Consider:** Rate limits vary by account tier; check Snowflake documentation for current limits. If you receive HTTP 429 responses, reduce request frequency.

```python
import requests

# Connection pooling with session reuse
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {token}"})

# Circuit breaker state
consecutive_failures = 0
circuit_open_until = None

def call_api_with_circuit_breaker(payload):
    global consecutive_failures, circuit_open_until
    if circuit_open_until and time.time() < circuit_open_until:
        raise Exception("Circuit breaker open — waiting 60s")
    try:
        resp = session.post(url, json=payload)
        resp.raise_for_status()
        consecutive_failures = 0
        return resp.json()
    except Exception:
        consecutive_failures += 1
        if consecutive_failures >= 5:
            circuit_open_until = time.time() + 60
        raise
```

### Anti-Pattern 1: Not Implementing Retry Logic with Exponential Backoff
```python
# Bad: No retry on transient errors
import requests

response = requests.post(
    f"https://{account}.snowflakecomputing.com/api/v2/cortex/inference:complete",
    headers={"Authorization": f"Bearer {token}"},
    json={"model": "mistral-large", "prompt": "Hello"}
)
# Network glitch or rate limit = immediate failure!
```
**Problem:** Transient failures cause user errors; rate limits not handled

**Correct Pattern:**
```python
# Good: Use with_retry utility (see "Retry and Backoff Implementation" section below)
# Retry on 429 (rate limit) and 5xx (server errors) with exponential backoff + jitter
resp = with_retry(lambda: requests.post(
    f"https://{account}.snowflakecomputing.com/api/v2/cortex/inference:complete",
    headers={"Authorization": f"Bearer {token}"},
    json={"model": "mistral-large", "prompt": prompt},
    timeout=30
))
# Key: Honor Retry-After header on 429, use jitter to avoid thundering herd
```
**Benefits:** Handles rate limits and transient errors; production-ready reliability

### Anti-Pattern 2: Not Using Streaming for Long Responses
```python
# Bad: Wait for entire response before showing anything
response = requests.post(
    f"https://{account}.snowflakecomputing.com/api/v2/cortex/inference:complete",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "model": "mistral-large",
        "prompt": "Write a 2000 word essay on AI",
        "stream": False  # Waits for full response!
    }
)
result = response.json()
print(result['choices'][0]['text'])  # User waits 30+ seconds!
```
**Problem:** Long wait times; poor UX; appears frozen to user

**Correct Pattern:**
```python
# Good: Stream responses for immediate feedback
response = requests.post(
    f"https://{account}.snowflakecomputing.com/api/v2/cortex/inference:complete",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "model": "mistral-large",
        "prompt": "Write a 2000 word essay on AI",
        "stream": True  # Enable streaming!
    },
    stream=True
)

print("Response: ", end='', flush=True)
for line in response.iter_lines():
    if line:
        # Parse server-sent events format
        if line.startswith(b'data: '):
            data = json.loads(line[6:])
            if 'choices' in data:
                chunk = data['choices'][0].get('delta', {}).get('content', '')
                print(chunk, end='', flush=True)  # Show immediately!
print()  # New line at end
```
**Benefits:** Immediate feedback; better UX; shows progress; feels responsive; professional; lower perceived latency; user engagement

### Anti-Pattern 3: Not Monitoring Token Usage and Costs
```python
# Bad: No tracking of token usage
for user_query in user_queries:
    response = call_cortex_api(prompt=user_query)
    print(response['choices'][0]['text'])
# No idea: How many tokens used? What's the cost? Any patterns?
```
**Problem:** No cost visibility; budget overruns; can't optimize usage

**Correct Pattern:**
```python
# Good: Track token usage and costs
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    filename='cortex_api_usage.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def call_cortex_api_with_tracking(prompt, model="mistral-large"):
    start_time = datetime.now()

    response = requests.post(
        f"https://{account}.snowflakecomputing.com/api/v2/cortex/inference:complete",
        headers={"Authorization": f"Bearer {token}"},
        json={"model": model, "prompt": prompt}
    )

    end_time = datetime.now()
    latency_ms = (end_time - start_time).total_seconds() * 1000

    result = response.json()
    usage = result.get('usage', {})

    # Log usage metrics
    log_entry = {
        'timestamp': start_time.isoformat(),
        'model': model,
        'prompt_tokens': usage.get('prompt_tokens', 0),
        'completion_tokens': usage.get('completion_tokens', 0),
        'total_tokens': usage.get('total_tokens', 0),
        'latency_ms': latency_ms,
        'status': response.status_code
    }
    logging.info(json.dumps(log_entry))

    return result

# Analyze usage patterns
def analyze_token_usage(log_file='cortex_api_usage.log'):
    import pandas as pd

    logs = []
    with open(log_file) as f:
        for line in f:
            logs.append(json.loads(line.split(' - ')[1]))

    df = pd.DataFrame(logs)

    print(f"Total API calls: {len(df)}")
    print(f"Total tokens used: {df['total_tokens'].sum():,}")
    print(f"Average tokens per call: {df['total_tokens'].mean():.0f}")
    print(f"Average latency: {df['latency_ms'].mean():.0f}ms")
    print(f"95th percentile latency: {df['latency_ms'].quantile(0.95):.0f}ms")

    # Check current pricing at https://www.snowflake.com/pricing/
    # Credit costs vary by model and change with each release
    print(f"Total tokens used: {df['total_tokens'].sum():,} -- check pricing docs for cost estimate")
```
**Benefits:** Cost visibility; usage tracking; optimization insights; budget control; anomaly detection; performance monitoring; professional; financial responsibility

### Anti-Pattern 4: Using REST API for Batch Processing Instead of AISQL
```python
# Bad: REST API for processing 10,000 records
records = load_records()  # 10,000 records

results = []
for record in records:
    response = requests.post(
        f"https://{account}.snowflakecomputing.com/api/v2/cortex/inference:complete",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "model": "mistral-large",
            "prompt": f"Classify sentiment: {record['text']}"
        }
    )
    results.append(response.json())
    time.sleep(0.1)  # Rate limit protection

# Takes hours! 10,000 API calls! Rate limits! Expensive! Fragile!
```
**Problem:** Extremely slow; rate limit issues; expensive API calls; network overhead; fragile; error handling complexity; unprofessional; poor scalability

**Correct Pattern:**
```sql
-- Good: Use AISQL for batch processing
-- Process 10,000 records in parallel, native Snowflake
CREATE OR REPLACE TABLE sentiment_results AS
SELECT
  record_id,
  text,
  SNOWFLAKE.CORTEX.COMPLETE(
    'mistral-large',
    CONCAT('Classify sentiment: ', text)
  ) AS sentiment_classification
FROM records_table;

-- Parallel processing, no rate limits, optimized, reliable!
-- Completes in minutes, not hours
```
```python
# Or use Python connector for batch with AISQL
import snowflake.connector

conn = snowflake.connector.connect(
    connection_name=os.getenv("SNOWFLAKE_CONNECTION_NAME") or "myconn"
)

# Process in batch with SQL
query = """
SELECT
  record_id,
  SNOWFLAKE.CORTEX.COMPLETE('mistral-large',
    CONCAT('Classify sentiment: ', text)
  ) AS sentiment
FROM records_table
"""

cursor = conn.cursor()
cursor.execute(query)
results = cursor.fetchall()

# Fast, reliable, scalable, professional!
```
**Benefits:** 100x+ faster; parallel processing; no rate limits; native Snowflake optimization; reliable; cost-effective; professional; scalable

> **Investigation Required**
> When applying this rule:
> 1. **Read existing REST API client code BEFORE adding new calls** - Check retry logic, auth patterns
> 2. **Verify API endpoint availability** - Check Snowflake account region, feature availability
> 3. **Never assume retry strategy** - Read existing code to understand backoff patterns
> 4. **Check rate limiting** - Review existing usage patterns and limits
> 5. **Test with actual API** - Validate authentication and responses before deployment
>
> **Anti-Pattern:**
> "Calling Cortex REST API... (without checking auth setup)"
> "Adding retry logic... (without checking existing pattern)"
>
> **Correct Pattern:**
> "Let me check your existing API client setup first."
> [reads existing client code, checks auth, reviews retry logic]
> "I see you use exponential backoff with 3 retries. Following this pattern for the new endpoint..."

## Output Format Examples
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

### REST vs AISQL
- Use REST for: user-facing chat/assistants, embeddings on-demand, agentic interactions where latency matters
- Use AISQL for: large table processing, batch embeddings, aggregations across many rows

## Retry and Backoff Implementation

Rate limits vary by endpoint and account tier. If receiving HTTP 429, implement exponential backoff starting at 1 second, doubling up to 60 seconds max. Always honor the `Retry-After` header when present.

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

## Idempotency Keys
```http
POST /cortex/complete HTTP/1.1
Idempotency-Key: 4f2b6c1d-8c0d-4a32-8a2a-98a1aa0b0c77
Content-Type: application/json

{"model":"llama3.1-8b","prompt":"Answer briefly.","max_tokens":64}
```

## Streaming Responses
```python
for chunk in client.complete_stream(model="llama3.1-8b", prompt=prompt, max_tokens=64):
    print(chunk.delta, end="")
```

## Cost Controls
- Cap `max_tokens` and truncate inputs; preflight with token counters when available
- Cache frequent prompts/responses; deduplicate with hashes
- Set sane client timeouts; drop requests exceeding UX thresholds

## Observability
- Log request metadata (model, token counts, latency, status)
- Emit traces and associate with evaluation events in AI Observability

## Authentication, Response Format, and SSE Streaming

> **See companion rule for authentication and streaming implementation details:**
> - **118a-snowflake-cortex-rest-api-streaming.md** — Authentication token types (PAT, OAuth, JWT vs session tokens), response format verification (JSON vs SSE detection), SSE protocol format, parsing approaches (sseclient library and manual), SSE error handling with reconnection, production-ready Cortex Agent SSE example, and SSE best practices
