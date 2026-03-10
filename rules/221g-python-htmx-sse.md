# HTMX SSE Patterns (Python)

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-03-09
**Keywords:** sse, server-sent events, htmx, alpine.js, eventsource, real-time, streaming, live updates, push notifications, event types, sse-manager
**TokenBudget:** ~4150
**ContextTier:** High
**Depends:** 221-python-htmx-core.md, 221f-python-htmx-integrations.md

## Scope

**What This Rule Covers:**
Patterns for implementing Server-Sent Events (SSE) in HTMX applications, covering the decision between HTMX SSE extension and Alpine.js SSE manager, event type matching, thread-safe publishing, and common anti-patterns that lead to broken real-time updates.

**When to Load This Rule:**
- Implementing Server-Sent Events with HTMX
- Choosing between HTMX SSE extension and Alpine.js SSE manager
- Setting up real-time updates in HTMX applications
- Implementing thread-safe SSE publishing from background tasks
- Debugging SSE event type mismatches

## References

### Dependencies

**Must Load First:**
- **221-python-htmx-core.md** - HTMX foundation patterns
- **221f-python-htmx-integrations.md** - Alpine.js patterns

**Related:**
- **207-python-logging.md** - Web logging with SSE

### Project Documentation

- **SSE Events Reference**: `docs/SSE_EVENTS.md` - Channel and event type documentation

## Contract

### Inputs and Prerequisites

- HTMX installed and configured
- SSE endpoints returning `text/event-stream` content type
- For Alpine.js approach: SSE manager module loaded
- Understanding of async Python patterns

### Mandatory

- sse-starlette or equivalent SSE library
- asyncio for thread-safe publishing
- Browser with EventSource support
- SSE channel documentation file (docs/SSE_EVENTS.md)

### Forbidden

- Mixing HTMX SSE extension with Alpine.js SSE manager on same element
- Using `sse:` prefix in HTMX triggers when events come from Alpine.js
- Calling `asyncio.get_event_loop()` from background threads
- Hardcoding event types without documentation

### Execution Steps

1. Choose SSE approach based on decision matrix (HTMX extension vs Alpine.js manager)
2. Create SSE endpoint with proper `text/event-stream` content type
3. Define event types and document in `docs/SSE_EVENTS.md`
4. Implement backend event generator with named event types
5. Configure frontend listeners matching exact backend event types
6. For Alpine.js: use camelCase triggers with `htmx.trigger()`
7. For background tasks: capture event loop before `asyncio.to_thread()`
8. Implement heartbeat/ping for connection health monitoring
9. Test reconnection behavior on connection drops
10. Verify event type consistency between frontend and backend

### Output Format

- SSE endpoint returning EventSourceResponse
- Events in format: `event: event_type\ndata: json_payload\n\n`

### Validation

**Pre-Task-Completion Checks:**
- SSE approach chosen (HTMX extension vs Alpine.js manager)
- Event types documented and consistent between frontend/backend
- Thread-safe publishing pattern implemented for background tasks
- SSE channel documentation created/updated

**Success Criteria:**
- SSE connection established (browser DevTools Network tab shows EventSource)
- Events received match documented event types exactly
- HTMX elements update when SSE events arrive
- No duplicate connections when using Alpine.js manager
- Background thread publishing works without RuntimeError

### Design Principles

- **Choose ONE SSE approach** - Either HTMX SSE extension OR Alpine.js SSE manager, never both on same element
- **Match event types exactly** - Frontend event listeners must match backend `event_type` values exactly
- **Use camelCase for HTMX triggers** - When using Alpine.js to trigger HTMX, use camelCase (not `sse:` prefix)
- **Capture event loop before threads** - Use `asyncio.get_running_loop()` before `asyncio.to_thread()`
- **Document SSE channels** - Maintain `docs/SSE_EVENTS.md` with all channels, event types, and payloads

### Post-Execution Checklist

- [ ] SSE approach chosen and consistent across page
- [ ] Event types match exactly between backend and frontend
- [ ] HTMX triggers use camelCase (not `sse:` prefix) when using Alpine.js
- [ ] Thread-safe publishing pattern used for background tasks
- [ ] SSE channel documentation updated
- [ ] Heartbeat/ping handling implemented
- [ ] Reconnection logic tested

> **Investigation Required**
> Before adding SSE patterns, the agent MUST:
> 1. Check existing SSE connections in the project — avoid creating duplicate streams for the same data
> 2. Determine which SSE approach (HTMX extension vs Alpine.js) is already in use — **never mix both**
> 3. Read existing `docs/SSE_EVENTS.md` for documented channels and event types
> 4. Verify `sse-starlette` is installed if using FastAPI: `uv pip list | grep sse-starlette`
> 5. Count existing SSE connections — browsers limit to ~6 per domain; consolidate if approaching limit

## SSE Approach Decision Matrix

**When to use HTMX SSE extension:**
- Simple element updates (minimal JavaScript, declarative)

**When to use Alpine.js SSE manager:**
- Multiple elements from one channel (single connection, multiple targets)
- Complex event handling logic (full JavaScript control)
- Toast notifications on events (requires JavaScript for toasts)

**When to use Dedicated SSE endpoint:**
- Streaming progress updates (per-operation stream)

### Browser SSE Connection Limits

**Critical:** Browsers limit concurrent SSE connections to **~6 per domain** (HTTP/1.1). HTTP/2 raises this limit but is not guaranteed.

- **1-3 SSE connections (Safe):** No action needed
- **4-5 SSE connections (Caution):** Consider consolidating channels
- **6+ SSE connections (Broken):** MUST consolidate into multiplexed channel

**Multiplexed channel pattern** (single SSE endpoint, multiple event types):
```python
async def multiplexed_events(request: Request):
    """Single SSE endpoint that emits multiple event types."""
    async def generate():
        while True:
            # Check all event sources and emit with different event types
            if status := await get_system_status():
                yield {"event": "system_status", "data": json.dumps(status)}
            if notifications := await get_user_notifications(request.user):
                for n in notifications:
                    yield {"event": "notification", "data": json.dumps(n)}
            if progress := await get_task_progress():
                yield {"event": "task_progress", "data": json.dumps(progress)}
            await asyncio.sleep(1)
    return EventSourceResponse(generate())
```

Frontend listens to specific event types from the single connection:
```html
<div sse-connect="/api/sse/all" hx-ext="sse">
    <div sse-swap="system_status" hx-target="#status-panel">...</div>
    <div sse-swap="notification" hx-target="#notification-area">...</div>
    <div sse-swap="task_progress" hx-target="#progress-bar">...</div>
</div>
```

## Pattern 1: HTMX SSE Extension

Use when: Simple, single-element updates from SSE events.

### Backend (FastAPI)

```python
from sse_starlette.sse import EventSourceResponse

@router.get("/api/sse/status")
async def sse_status():
    async def event_generator():
        while True:
            status = await get_current_status()
            yield {
                "event": "system_status",  # Named event type
                "data": json.dumps(status)
            }
            await asyncio.sleep(5)

    return EventSourceResponse(event_generator())
```

### Frontend (HTML)

```html
<!-- HTMX SSE Extension Pattern -->
<div
    id="status-display"
    hx-ext="sse"
    sse-connect="/api/sse/status"
    hx-get="/status/content"
    hx-trigger="sse:system_status"
    hx-swap="innerHTML"
>
    Loading...
</div>
```

**Critical:** The `hx-trigger="sse:system_status"` MUST match the backend `event: system_status` exactly.

## Pattern 2: Alpine.js SSE Manager

Use when: Multiple elements need updates, or complex event handling required.

### SSE Manager Setup

```javascript
// sse-manager.js
const CHANNEL_EVENTS = {
    logs: ['log'],
    operations: ['operation_status'],
    demos: ['installed', 'uninstalled', 'operation_started', 'operation_completed'],
    status: ['system_status'],
    validation: ['check_result', 'validation_complete', 'validation_error']
};

export class SSEConnectionManager {
    connect(channel, onMessage, onError = null) {
        const eventSource = new EventSource(`/api/sse/${channel}`);

        // Register listeners for named event types
        const eventTypes = CHANNEL_EVENTS[channel] || [];
        eventTypes.forEach(eventType => {
            eventSource.addEventListener(eventType, (event) => {
                const data = JSON.parse(event.data);
                onMessage(data, event);
            });
        });

        return eventSource;
    }
}
```

### Frontend (HTML with Alpine.js)

```html
<!-- Alpine.js SSE Manager Pattern -->
<div x-data="statusPage()" x-init="init()">
    <div
        id="status-display"
        hx-get="/status/content"
        hx-trigger="load, systemStatus"
        hx-swap="innerHTML"
    >
        Loading...
    </div>
</div>

<script>
function statusPage() {
    return {
        init() {
            window.waitForSSEManager(() => {
                window.sseManager.connect('status', (data, event) => {
                    const eventType = event.type;

                    if (eventType === 'system_status') {
                        // Trigger HTMX refresh with camelCase event
                        htmx.trigger('#status-display', 'systemStatus');
                    }
                });
            });
        }
    };
}
</script>
```

**Critical:** Use camelCase `systemStatus` in `htmx.trigger()`, NOT `sse:system_status`.

## Pattern 3: Thread-Safe SSE Publishing

Use when: Publishing SSE events from background threads (e.g., `asyncio.to_thread()`).

### Correct Pattern

```python
@router.get("/demos/{demo_id}/status/stream")
async def demo_status_stream(demo_id: str):
    async def status_generator():
        progress_queue: asyncio.Queue = asyncio.Queue()

        # CRITICAL: Capture event loop BEFORE entering thread pool
        main_loop = asyncio.get_running_loop()

        def progress_callback(step: str, message: str) -> None:
            """Thread-safe callback from background thread."""
            # Use call_soon_threadsafe to interact with main loop
            main_loop.call_soon_threadsafe(
                progress_queue.put_nowait,
                (step, message)
            )

        async def run_in_thread():
            await asyncio.to_thread(
                long_running_operation,
                callback=progress_callback
            )
            await progress_queue.put(("done", ""))

        task = asyncio.create_task(run_in_thread())

        while True:
            step, message = await progress_queue.get()
            if step == "done":
                yield {"event": "complete", "data": "{}"}
                break
            yield {"event": "progress", "data": json.dumps({"step": step})}

    return EventSourceResponse(status_generator())
```

### Heartbeat and Reconnection

Keep SSE connections alive and handle drops gracefully:

```python
async def event_generator_with_heartbeat():
    while True:
        event = await get_next_event(timeout=15)
        if event:
            yield {"event": event.type, "data": json.dumps(event.data)}
        else:
            # Send heartbeat to keep connection alive
            yield {"event": "ping", "data": ""}
        await asyncio.sleep(0)
```

EventSource auto-reconnects by default. Control the retry interval from the server by including a `retry:` field in the SSE stream (value in milliseconds):

```text
retry: 5000
event: status
data: {"connected": true}
```

### Error Recovery in SSE Generators

Exceptions in the async generator will kill the SSE stream silently. Wrap with error handling:

```python
async def resilient_event_generator(task_id: str):
    """SSE generator with error recovery."""
    try:
        async for event_type, data in progress_stream(task_id):
            yield {"event": event_type, "data": data}
    except asyncio.CancelledError:
        # Client disconnected — clean up
        await cleanup_task(task_id)
        return
    except Exception as exc:
        # Send error event to client, then terminate gracefully
        yield {
            "event": "error",
            "data": json.dumps({"message": str(exc), "task_id": task_id}),
        }
        return
    finally:
        # Always clean up resources
        await cleanup_task(task_id)
```

Frontend error handling:
```javascript
// HTMX SSE extension doesn't handle custom error events by default
// Use htmx:sseError event instead:
document.body.addEventListener('htmx:sseError', function(event) {
    console.error('SSE error:', event.detail);
    // Optionally show error toast
});
```

### SSE with Authentication

`EventSource` does NOT support custom headers. For authenticated SSE endpoints, pass tokens via query parameters or cookies:

**Option 1: Token in query parameter (recommended for JWT):**
```javascript
// Frontend — pass JWT token in URL
const token = localStorage.getItem('auth_token');
const source = new EventSource(`/api/sse/status?token=${token}`);
```

```python
# Backend — validate token from query param
@app.get("/api/sse/status")
async def sse_status(token: str = Query(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    async def generate():
        while True:
            data = await get_user_status(payload["sub"])
            yield {"event": "status", "data": json.dumps(data)}
            await asyncio.sleep(5)

    return EventSourceResponse(generate())
```

**Option 2: Cookie-based (recommended for session auth):**
```python
# Backend — validate session cookie (automatic with Flask/FastAPI session middleware)
@app.get("/api/sse/notifications")
async def sse_notifications(request: Request):
    user = await get_current_user(request)  # From session cookie
    if not user:
        raise HTTPException(status_code=401)
    # ... generate events for user ...
```

```html
<!-- Frontend — cookies sent automatically, no code needed -->
<div sse-connect="/api/sse/notifications" hx-ext="sse">
    <div sse-swap="notification">Waiting for notifications...</div>
</div>
```

**Key rules:**
- JWT tokens in query params are visible in server logs — use short-lived tokens
- Cookie-based auth is simpler but requires same-origin SSE endpoints
- Never pass long-lived secrets in query parameters
- For HTMX SSE extension: cookies are sent automatically; for `new EventSource()`: use `withCredentials: true` for cross-origin cookies

### Anti-Pattern (Will Crash)

```python
# ❌ BAD: Calling get_event_loop() from background thread
def progress_callback(step: str, message: str) -> None:
    loop = asyncio.get_event_loop()  # RuntimeError: no current event loop
    loop.call_soon_threadsafe(...)
```

## Anti-Patterns and Common Mistakes

### Pitfall 1: Mixing SSE Approaches

**Problem:** Using both HTMX SSE extension and Alpine.js SSE manager on the same element creates duplicate connections and event conflicts.

```html
<!-- BAD: Both HTMX SSE and Alpine.js SSE on same element -->
<div
    hx-ext="sse"
    sse-connect="/api/sse/demos"
    hx-trigger="sse:installed"
    x-data="{ init() { sseManager.connect('demos', ...) } }"
>
```

**Correct Pattern:** Choose ONE SSE approach per element.

```html
<!-- GOOD: Choose ONE approach -->
<div
    x-data="libraryPage()"
    x-init="init()"
>
    <div
        id="demo-grid"
        hx-get="/demos/grid"
        hx-trigger="load, demoInstalled"
    >
    </div>
</div>
```

### Pitfall 2: Event Type Mismatch

**Problem:** Frontend event listeners don't match backend event types, causing events to never trigger updates.

```javascript
// BAD: Frontend expects 'started', backend sends 'operation_started'
const CHANNEL_EVENTS = {
    operations: ['started', 'completed', 'failed'],
};

// Backend sends: event: operation_started
// Frontend never receives it!
```

**Correct Pattern:** Match backend event types exactly in frontend listeners.

```javascript
// GOOD: Match backend event types exactly
const CHANNEL_EVENTS = {
    operations: ['operation_status'],
};
```

### Pitfall 3: Wrong HTMX Trigger Syntax

**Problem:** Using `sse:` prefix with `htmx.trigger()` when events come from Alpine.js causes HTMX to ignore the events.

```javascript
// BAD: Using sse: prefix with htmx.trigger()
window.sseManager.connect('demos', (data, event) => {
    htmx.trigger('#demo-grid', 'sse:installed');  // Won't work!
});
```

**Correct Pattern:** Use camelCase custom events with `htmx.trigger()`.

```javascript
// GOOD: Use camelCase custom events
window.sseManager.connect('demos', (data, event) => {
    htmx.trigger('#demo-grid', 'demoInstalled');
});
```

## SSE Channel Documentation Template

Maintain `docs/SSE_EVENTS.md` with this structure:

```markdown
# SSE Events Reference

## Channel: /api/sse/demos

**Event Types:**
- **`installed`** - Demo was installed (payload: `{demo_id, name}`)
- **`uninstalled`** - Demo was uninstalled (payload: `{demo_id}`)
- **`operation_started`** - Operation began (payload: `{demo_id, operation}`)
- **`operation_completed`** - Operation finished (payload: `{demo_id, status}`)
```

## Output Format Examples

### SSE Event Wire Format

```text
event: system_status
data: {"status": "healthy", "uptime": 3600}

event: operation_started
data: {"demo_id": "demo-123", "operation": "install"}

event: progress
data: {"step": "downloading", "percent": 45}

event: complete
data: {}
```

### Flask SSE Note

This rule focuses on FastAPI (async) SSE patterns with `sse-starlette`. For Flask:

- **flask-sse**: Uses Redis for pub/sub — `uv add flask-sse`. Requires `gunicorn` with `gevent` worker
 - **Polling fallback**: For simple Flask apps without async support, use `hx-trigger="every 5s"` polling instead of SSE (see 221i for polling patterns)
- **Quart**: If Flask-compatible async is needed, consider Quart (`uv add quart`) which supports native async SSE generators

For most Flask applications, **polling is simpler and more reliable** than Flask SSE.
