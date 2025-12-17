# Snowflake Cortex REST API Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** idempotency, rate limits, Complete endpoint, Embed endpoint, exponential backoff, REST API, Cortex API, authentication tokens, PAT, OAuth, JWT, SSE, token verification, response format
**TokenBudget:** ~3950
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md, rules/105-snowflake-cost-governance.md, rules/111-snowflake-observability-core.md

## Purpose
Provide production patterns for Cortex REST API usage for interactive/low-latency workloads: authentication, Complete/Embed/Agents endpoints, retries, idempotency, streaming, cost controls, and observability.

## Rule Scope

REST API usage for Complete, Embed, Agents; client patterns; when to use REST vs AISQL

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Use REST for low-latency** - Interactive, latency-sensitive tasks
- **Use AISQL for batch** - High-throughput batch processing
- **Implement retry with backoff** - Exponential backoff + jitter on retryable errors
- **Enforce idempotency keys** - For non-idempotent operations
- **Stream responses** - When supported, for better UX
- **Limit tokens** - Set max_tokens and response size limits
- **Never use infinite retries** - Always set retry limits

**Quick Checklist:**
- [ ] Proper authentication configured
- [ ] Retry logic with exponential backoff
- [ ] Idempotency keys for writes
- [ ] Token limits enforced
- [ ] Streaming enabled where appropriate
- [ ] Request/response logging (no PII)
- [ ] Rate limits respected

## Contract

<contract>
<inputs_prereqs>
- Connectivity and credentials for Snowflake REST API (per account region)
- Model allowlists and RBAC aligned with organizational policy
- Clear latency/throughput SLOs
</inputs_prereqs>

<mandatory>
REST clients with backoff/retry; streaming APIs; structured logging/tracing; AI Observability
</mandatory>

<forbidden>
- Unauthenticated/implicit credential flows
- Infinite retries; unbounded request payloads
</forbidden>

<steps>
1. Prefer REST for interactive latency-sensitive tasks; prefer AISQL for batch throughput
2. Implement retry with exponential backoff and jitter on retryable statuses
3. Enforce idempotency keys for non-idempotent operations
4. Limit tokens and response size; stream outputs when supported
5. Log request/response metadata (not PII) and integrate tracing
</steps>

<output_format>
Minimal client snippets with safe defaults
</output_format>

<validation>
Canary tests pass; SLO latency met; rate limits respected; costs within budget
</validation>

<design_principles>
- Align client design with SLOs: use streaming and timeouts; cap tokens
- Separate per-request model options (e.g., max_tokens) from global defaults
- Capture metrics (latency, tokens, error rates); build alerting for regressions
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Not Implementing Retry Logic with Exponential Backoff**
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
**Problem:** Transient failures cause user errors; rate limits not handled; poor reliability; bad user experience; unnecessary failures; unprofessional

**Correct Pattern:**
```python
# Good: Exponential backoff with jitter
import requests
import time
import random

def call_cortex_api_with_retry(prompt, model="mistral-large", max_retries=3):
    base_delay = 1  # seconds
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"https://{account}.snowflakecomputing.com/api/v2/cortex/inference:complete",
                headers={"Authorization": f"Bearer {token}"},
                json={"model": model, "prompt": prompt},
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limit
                retry_after = int(response.headers.get('Retry-After', base_delay * (2 ** attempt)))
                jitter = random.uniform(0, 1)
                wait_time = retry_after + jitter
                print(f"Rate limited, waiting {wait_time:.2f}s")
                time.sleep(wait_time)
            elif response.status_code >= 500:  # Server error
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Server error, retrying in {delay:.2f}s")
                time.sleep(delay)
            else:
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"Request failed: {e}, retrying in {delay:.2f}s")
            time.sleep(delay)

    raise Exception(f"Failed after {max_retries} retries")
```
**Benefits:** Handles rate limits; retries transient errors; better reliability; professional API client; good user experience; production-ready


**Anti-Pattern 2: Not Using Streaming for Long Responses**
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
**Problem:** Long wait times; poor UX; appears frozen; user abandons; no progress indication; unprofessional; high latency perception

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


**Anti-Pattern 3: Not Monitoring Token Usage and Costs**
```python
# Bad: No tracking of token usage
for user_query in user_queries:
    response = call_cortex_api(prompt=user_query)
    print(response['choices'][0]['text'])
# No idea: How many tokens used? What's the cost? Any patterns?
```
**Problem:** No cost visibility; budget overruns; can't optimize; no usage patterns; billing surprises; no anomaly detection; unprofessional; financial risk

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

    # Estimate costs (example: $0.002 per 1K tokens)
    total_cost = (df['total_tokens'].sum() / 1000) * 0.002
    print(f"Estimated cost: ${total_cost:.2f}")
```
**Benefits:** Cost visibility; usage tracking; optimization insights; budget control; anomaly detection; performance monitoring; professional; financial responsibility


**Anti-Pattern 4: Using REST API for Batch Processing Instead of AISQL**
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

## Post-Execution Checklist
- [ ] REST used for interactive use cases; AISQL for batch
- [ ] Retry with exponential backoff and jitter implemented
- [ ] Idempotency keys used for non-idempotent operations
- [ ] Token limits and streaming enabled where applicable
- [ ] Logging/tracing integrated; costs and latency monitored

## Validation
- **Success checks:** SLO latency met; low error rates; duplicate request safety via idempotency
- **Negative tests:** Simulated timeouts and 429/5xx retried successfully; oversized prompts rejected

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

## References

### External Documentation
- [Cortex REST API](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-rest-api)
- [Snowflake Cortex AISQL](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql)
- [AI Observability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-observability)

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **AISQL**: `rules/114-snowflake-cortex-aisql.md`
- **Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`
- **Observability**: `rules/111-snowflake-observability-core.md`

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

## 7. Authentication Token Types

**Rule:** Session tokens from `snowflake-connector-python` are INTERNAL ONLY and cannot be used with Snowflake REST APIs.

**Before using ANY token for Snowflake REST API authentication:**
1. Verify token type is explicitly supported by the target API documentation
2. For Cortex Agent REST API: Use PAT (Personal Access Token), OAuth, or JWT
3. Never assume session tokens from Python connector work with REST APIs
4. Check API docs for required header: `X-Snowflake-Authorization-Token-Type`

**Common Token Types:**
- Session tokens (from snowflake-connector-python): Internal only, not for REST APIs
- PAT (Personal Access Token): For REST API authentication
- OAuth tokens: For REST API authentication
- JWT tokens: For REST API authentication

**Anti-Pattern:**
```python
# Bad: Using session token from connector for REST API
conn = snowflake.connector.connect(...)
token = conn._rest._token  # Internal session token
headers = {"Authorization": f"Bearer {token}"}  # Will fail with 390303 error
```

**Correct Pattern:**
```python
# Good: Use PAT for REST API
import os
pat = os.getenv("SNOWFLAKE_PAT")
headers = {
    "Authorization": f"Bearer {pat}",
    "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN"
}
```

## 8. Response Format Verification

**Rule:** Never assume REST API endpoints return JSON. Verify response format from documentation before implementing.

**Before implementing ANY REST API client:**
1. Search docs for endpoint operation (not just authentication)
   - Example: "cortex agent run", "agent response format"
2. Explicitly identify response format: JSON, SSE stream, binary, multipart
3. Verify Content-Type header expectations
4. Block implementation until you can state: "Endpoint X returns [format] requiring [parsing method]"

**Common Response Formats:**
- JSON: `response.json()`
- Server-Sent Events (SSE): Parse event stream with SSE client
- Binary: Handle raw bytes
- Streaming: Iterate chunks

**Anti-Pattern:**
```python
# Bad: Assuming JSON without verification
response = requests.post(url, json=payload)
data = response.json()  # May fail with JSONDecodeError if SSE stream
```

**Validation Gate:**
- Before REST API implementation, add TODO: "Verified response format from docs: [JSON/SSE/binary]"
- Search docs for endpoint name + "response" or "returns"

### 8.1 Server-Sent Events (SSE) in Snowflake

**What is SSE?**
Server-Sent Events is a standard HTTP protocol for streaming data from server to client. The server keeps the connection open and sends events as they occur, allowing real-time updates without polling.

**When Snowflake Uses SSE:**
- Cortex Agent `/run` endpoint (streaming agent responses)
- Long-running inference operations requiring incremental feedback
- Any endpoint documented with `text/event-stream` Content-Type

**SSE Protocol Format:**
```
data: {"message": "chunk 1"}\n\n
data: {"message": "chunk 2"}\n\n
event: error\n
data: {"error": "something failed"}\n\n
```

Key characteristics:
- Each event starts with `data:` prefix
- Events separated by double newline `\n\n`
- Optional `event:` field specifies event type (default: "message")
- Optional `id:` field for event tracking
- Optional `retry:` field for reconnection timing

### 8.2 Detecting SSE Responses

Always check `Content-Type` header before parsing:

```python
response = requests.post(url, json=payload, stream=True)

content_type = response.headers.get('Content-Type', '')

if 'text/event-stream' in content_type:
    # SSE format - parse as event stream
    parse_sse_stream(response)
elif 'application/json' in content_type:
    # JSON format - parse as JSON
    data = response.json()
else:
    # Unknown format - log and handle gracefully
    raise ValueError(f"Unexpected Content-Type: {content_type}")
```

### 8.3 Parsing SSE: Two Approaches

**Approach 1: Using sseclient library (Recommended)**
```python
# Install: pip install sseclient-py
import sseclient
import json

response = requests.post(
    url,
    json=payload,
    stream=True,
    headers=headers
)

client = sseclient.SSEClient(response)

for event in client.events():
    # event.event: event type (default: "message")
    # event.data: event data (string)
    # event.id: event id (if provided)

    if event.data:
        try:
            data = json.loads(event.data)
            print(f"Received: {data}")
        except json.JSONDecodeError:
            print(f"Non-JSON data: {event.data}")
```

**Approach 2: Manual parsing (No dependencies)**
```python
import json

def parse_sse_stream(response):
    """
    Parse SSE stream manually without external dependencies.

    SSE format:
    - Lines starting with 'data:' contain the payload
    - Events separated by blank lines (\\n\\n)
    - Comments start with ':'
    """
    buffer = ""

    for line in response.iter_lines(decode_unicode=True):
        if line is None:
            continue

        # Skip comments
        if line.startswith(':'):
            continue

        # Empty line marks end of event
        if not line.strip():
            if buffer:
                yield buffer
                buffer = ""
            continue

        # Parse data field
        if line.startswith('data:'):
            data = line[5:].strip()  # Remove 'data:' prefix
            buffer = data

        # Parse event field (optional)
        elif line.startswith('event:'):
            event_type = line[6:].strip()
            # Handle different event types if needed
            pass

# Usage:
response = requests.post(url, json=payload, stream=True)

for event_data in parse_sse_stream(response):
    try:
        data = json.loads(event_data)
        print(f"Event: {data}")
    except json.JSONDecodeError:
        print(f"Non-JSON event: {event_data}")
```

### 8.4 SSE Error Handling

**Handle connection errors and malformed events:**

```python
import sseclient
import json
import requests
from requests.exceptions import RequestException

def consume_sse_with_error_handling(url, payload, headers, max_retries=3):
    """
    Robust SSE consumption with error handling.
    """
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                stream=True,
                timeout=60  # Connection timeout
            )

            # Check for error status codes
            if response.status_code != 200:
                error_body = response.text
                raise Exception(f"HTTP {response.status_code}: {error_body}")

            # Verify Content-Type
            content_type = response.headers.get('Content-Type', '')
            if 'text/event-stream' not in content_type:
                raise ValueError(f"Expected SSE, got Content-Type: {content_type}")

            # Parse SSE stream
            client = sseclient.SSEClient(response)

            for event in client.events():
                if not event.data:
                    continue

                try:
                    # Parse event data
                    data = json.loads(event.data)

                    # Check for error events
                    if 'error' in data:
                        print(f"Error event: {data['error']}")
                        return None

                    yield data

                except json.JSONDecodeError as e:
                    print(f"Malformed JSON in event: {event.data}")
                    # Continue processing other events
                    continue

            # Stream completed successfully
            return

        except RequestException as e:
            print(f"Connection error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise

        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

# Usage:
try:
    for chunk in consume_sse_with_error_handling(url, payload, headers):
        if chunk:
            print(f"Received chunk: {chunk}")
except Exception as e:
    print(f"SSE stream failed: {e}")
```

### 8.5 Complete Cortex Agent SSE Example

**Production-ready pattern for Cortex Agent API:**

```python
import requests
import sseclient
import json
import os

def call_cortex_agent_sse(
    account_url: str,
    agent_name: str,
    question: str,
    pat_token: str,
    max_tokens: int = 1024
):
    """
    Call Cortex Agent with SSE streaming response.

    Args:
        account_url: Snowflake account URL (e.g., 'https://myaccount.snowflakecomputing.com')
        agent_name: Fully qualified agent name (e.g., 'DB.SCHEMA.AGENT_NAME')
        question: User question
        pat_token: Personal Access Token (PAT)
        max_tokens: Maximum response tokens

    Returns:
        Complete agent response text
    """
    url = f"{account_url}/api/v2/cortex/agents/{agent_name}:run"

    headers = {
        "Authorization": f"Bearer {pat_token}",
        "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
        "Content-Type": "application/json"
    }

    payload = {
        "question": question,
        "max_tokens": max_tokens
    }

    print(f"Calling Cortex Agent: {agent_name}")
    print(f"Question: {question}")
    print("-" * 60)

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            stream=True,  # CRITICAL: Enable streaming
            timeout=60
        )

        # Check status
        if response.status_code != 200:
            error_msg = response.text
            raise Exception(f"Agent API error {response.status_code}: {error_msg}")

        # Verify SSE format
        content_type = response.headers.get('Content-Type', '')
        if 'text/event-stream' not in content_type:
            raise ValueError(f"Expected text/event-stream, got: {content_type}")

        # Parse SSE stream
        client = sseclient.SSEClient(response)

        full_response = ""

        for event in client.events():
            if not event.data:
                continue

            try:
                data = json.loads(event.data)

                # Check for completion
                if data.get('done'):
                    print("\n[Stream complete]")
                    break

                # Extract content chunk
                if 'content' in data:
                    chunk = data['content']
                    print(chunk, end='', flush=True)
                    full_response += chunk

                # Check for errors
                if 'error' in data:
                    raise Exception(f"Agent error: {data['error']}")

            except json.JSONDecodeError:
                print(f"\n[Warning: Malformed event data: {event.data}]")
                continue

        print("\n" + "-" * 60)
        return full_response

    except requests.exceptions.Timeout:
        raise Exception("Agent request timed out after 60 seconds")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")

# Example usage:
if __name__ == "__main__":
    account_url = os.getenv("SNOWFLAKE_ACCOUNT_URL")
    pat_token = os.getenv("SNOWFLAKE_PAT")

    response = call_cortex_agent_sse(
        account_url=account_url,
        agent_name="ANALYTICS.AI.PORTFOLIO_AGENT",
        question="What are the top 5 holdings by weight?",
        pat_token=pat_token
    )

    print(f"\nFinal response length: {len(response)} characters")
```

### 8.6 SSE Best Practices

**DO:**
- Always set `stream=True` in requests
- Verify `Content-Type: text/event-stream` before parsing
- Handle connection timeouts (SSE can be long-lived)
- Parse JSON within event data (not the event itself)
- Handle malformed events gracefully (continue stream)
- Implement reconnection logic for critical streams
- Close connections properly when done

**DON'T:**
- Assume all APIs return JSON
- Call `response.json()` on SSE streams
- Forget to set `stream=True` (response may hang)
- Parse entire response as single JSON object
- Ignore Content-Type header
- Skip error handling for malformed events
- Leave connections open indefinitely
