# Snowflake Cortex REST API: Authentication & Streaming

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:cortex-api-streaming, kw:cortex-auth
**Keywords:** SSE, server-sent events, streaming response, event stream, PAT, OAuth, JWT, authentication token, token type, response format, sseclient, cortex agent SSE, streaming parsing
**TokenBudget:** ~4650
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 118-snowflake-cortex-rest-api.md

## Scope

**What This Rule Covers:**
Authentication token types for Cortex REST API (PAT, OAuth, JWT vs session tokens), response format verification (JSON vs SSE detection), and complete Server-Sent Events (SSE) implementation: protocol format, detection, parsing (library and manual), error handling, reconnection logic, and production-ready Cortex Agent SSE example.

**When to Load This Rule:**
- Authenticating with Cortex REST API (choosing PAT vs OAuth vs JWT)
- Implementing SSE streaming for Cortex Agent responses
- Parsing server-sent event streams from Snowflake endpoints
- Handling SSE connection errors and reconnection
- Verifying response format before parsing (JSON vs SSE)

**For core REST API patterns (retry, idempotency, cost controls), see `118-snowflake-cortex-rest-api.md`**

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns
- **118-snowflake-cortex-rest-api.md** - Core REST API patterns (retry, idempotency, cost controls)

**Related:**
- **107-snowflake-security-governance.md** - Authentication and security
- **115-snowflake-cortex-agents-core.md** - Cortex Agents REST API

### External Documentation

- [Cortex REST API Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-rest-api) - API endpoints and authentication
- [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents) - Agent concepts and API

## Contract

### Inputs and Prerequisites

Cortex REST API endpoint identified, authentication credentials available, response format verified from documentation

### Mandatory

Token type selection (PAT/OAuth/JWT), response format verification, SSE parsing for streaming endpoints

### Forbidden

Using session tokens from snowflake-connector-python for REST APIs, assuming JSON response format without verification, calling response.json() on SSE streams

### Execution Steps

1. Select authentication token type (PAT, OAuth, or JWT)
2. Configure authorization headers with correct token type header
3. Verify response format from API documentation (JSON vs SSE)
4. Implement appropriate parser (JSON or SSE)
5. Add SSE error handling and reconnection logic for streaming endpoints
6. Test with actual API endpoint

### Output Format

Authentication configuration, SSE parsing code, error handling patterns

### Validation

**Pre-Task-Completion Checks:**
- Token type explicitly verified against API documentation
- Authorization headers include X-Snowflake-Authorization-Token-Type where required
- Response format verified before parser implementation
- SSE parser handles malformed events gracefully
- Connection timeouts configured for streaming endpoints

**Success Criteria:**
- Authentication succeeds with chosen token type
- SSE stream parsed correctly with incremental output
- Error events detected and handled
- Connection errors trigger retry with backoff
- Stream completes without data loss

**Negative Tests:**
- Session tokens rejected by REST API (expected: 390303 error)
- Malformed SSE events skipped without crashing
- Connection timeout triggers retry
- Non-SSE response detected and handled differently

### Design Principles

- Always verify token type against API documentation before use
- Check Content-Type header before choosing parser (JSON vs SSE)
- Handle SSE events incrementally for responsive UX
- Implement reconnection logic for production streaming

### Post-Execution Checklist

- [ ] Token type selected and verified (PAT, OAuth, or JWT)
- [ ] Authorization headers configured correctly
- [ ] Response format verified from documentation
- [ ] SSE parser implemented (library or manual)
- [ ] Error handling covers malformed events
- [ ] Connection timeout and retry configured
- [ ] Stream cleanup (connection close) implemented

## Authentication Token Types

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

## Response Format Verification

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

## Server-Sent Events (SSE) in Snowflake

### What is SSE?

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

### Detecting SSE Responses

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

### Parsing SSE: Two Approaches

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

### SSE Error Handling

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
                time.sleep(2 ** attempt)  # See 118 core rule for full retry pattern
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

### Complete Cortex Agent SSE Example

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
# response = call_cortex_agent_sse(
#     account_url=os.getenv("SNOWFLAKE_ACCOUNT_URL"),
#     agent_name="ANALYTICS.AI.PORTFOLIO_AGENT",
#     question="What are the top 5 holdings by weight?",
#     pat_token=os.getenv("SNOWFLAKE_PAT")
# )
```

### SSE Best Practices

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
- Leave connections open

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Forgetting `stream=True` and Buffering the Entire SSE Response**

**Problem:** Calling `requests.post(url, json=payload)` without `stream=True`. The requests library buffers the entire response body in memory before returning. For SSE streams, this means the client blocks until the server closes the connection (which may never happen for long-lived streams), the user sees no incremental output, and memory usage grows unbounded. The call may eventually timeout or OOM.

**Correct Pattern:** Always pass `stream=True` to `requests.post()` for SSE endpoints. Then iterate over events incrementally using `sseclient.SSEClient(response)` or `response.iter_lines()`. This enables real-time streaming output and constant memory usage regardless of response length.

```python
import requests, sseclient, json

# Wrong: Missing stream=True — blocks until server closes connection
response = requests.post(url, json=payload, headers=headers)
# Client hangs here waiting for the full response body...
for line in response.text.splitlines():  # Only runs after entire stream is buffered
    print(line)

# Correct: stream=True enables incremental event processing
response = requests.post(url, json=payload, headers=headers, stream=True)
client = sseclient.SSEClient(response)
for event in client.events():  # Processes each event as it arrives
    if event.data:
        data = json.loads(event.data)
        print(data.get("content", ""), end="", flush=True)
```

**Anti-Pattern 2: Using Session Tokens from snowflake-connector-python for REST APIs**

**Problem:** Extracting the internal session token from `conn._rest._token` and using it as a Bearer token for Cortex REST API calls. Session tokens are internal to the connector's protocol and are not valid for Snowflake REST APIs. The API returns a `390303` authentication error, but developers waste time debugging because they assume the token "should work" since it came from an authenticated connection.

**Correct Pattern:** Use a Personal Access Token (PAT), OAuth token, or JWT for REST API authentication. Set the `Authorization: Bearer <token>` header along with `X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN` (for PAT). Never access private attributes of the connector object for authentication tokens.

```python
import snowflake.connector, os, requests

# Wrong: Extracting internal session token for REST API use
conn = snowflake.connector.connect(user="me", password="...", account="myaccount")
token = conn._rest._token  # Private internal attribute — NOT for REST APIs
headers = {"Authorization": f"Bearer {token}"}
resp = requests.post(cortex_url, json=payload, headers=headers)
# Result: HTTP 390303 authentication error

# Correct: Use a PAT (Personal Access Token) for REST API calls
pat = os.getenv("SNOWFLAKE_PAT")
headers = {
    "Authorization": f"Bearer {pat}",
    "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
    "Content-Type": "application/json",
}
resp = requests.post(cortex_url, json=payload, headers=headers, stream=True)
# Result: HTTP 200 with valid SSE stream
```

**Anti-Pattern 3: Calling `response.json()` on an SSE Stream**

**Problem:** Assuming the Cortex Agent API returns a JSON response and calling `response.json()` directly. SSE streams have `Content-Type: text/event-stream` and contain multiple `data:` prefixed lines, not a single JSON object. This raises a `JSONDecodeError` and developers incorrectly conclude the API is broken or returning malformed data.

**Correct Pattern:** Always check the `Content-Type` header before choosing a parser. If the header contains `text/event-stream`, parse as an SSE stream (using `sseclient` or manual line parsing). If it contains `application/json`, then use `response.json()`. Each individual SSE event's `data:` field may contain JSON that should be parsed separately with `json.loads(event.data)`.

```python
import requests, sseclient, json

# Wrong: Assuming JSON response from a streaming endpoint
response = requests.post(agent_url, json=payload, headers=headers, stream=True)
data = response.json()  # Raises JSONDecodeError — response is SSE, not JSON!

# Correct: Check Content-Type and parse accordingly
response = requests.post(agent_url, json=payload, headers=headers, stream=True)
content_type = response.headers.get("Content-Type", "")

if "text/event-stream" in content_type:
    # SSE stream — parse each event's data field individually
    client = sseclient.SSEClient(response)
    for event in client.events():
        if event.data:
            chunk = json.loads(event.data)  # Parse EACH event as JSON
            print(chunk.get("content", ""), end="", flush=True)
elif "application/json" in content_type:
    # Standard JSON response
    data = response.json()
    print(data)
else:
    raise ValueError(f"Unexpected Content-Type: {content_type}")
```
