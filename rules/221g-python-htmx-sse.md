# HTMX SSE Patterns (Python)

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** sse, server-sent events, htmx, alpine.js, eventsource, real-time, streaming, live updates, push notifications, event types, sse-manager
**TokenBudget:** ~2000
**ContextTier:** High
**Depends:** rules/221-python-htmx-core.md, rules/221f-python-htmx-integrations.md

## Purpose

Defines patterns for implementing Server-Sent Events (SSE) in HTMX applications, covering the decision between HTMX SSE extension and Alpine.js SSE manager, event type matching, thread-safe publishing, and common anti-patterns that lead to broken real-time updates.

## Rule Scope

Python web applications using HTMX with SSE for real-time updates (FastAPI, Flask, or other Python web frameworks)

## Quick Start TL;DR

**MANDATORY:**

- **Choose ONE SSE approach** - Either HTMX SSE extension OR Alpine.js SSE manager, never both on same element
- **Match event types exactly** - Frontend event listeners must match backend `event_type` values exactly
- **Use camelCase for HTMX triggers** - When using Alpine.js to trigger HTMX, use camelCase (not `sse:` prefix)
- **Capture event loop before threads** - Use `asyncio.get_running_loop()` before `asyncio.to_thread()`
- **Document SSE channels** - Maintain `docs/SSE_EVENTS.md` with all channels, event types, and payloads

**Pre-Execution Checklist:**

- [ ] SSE approach chosen (HTMX extension vs Alpine.js manager)
- [ ] Event types documented and consistent between frontend/backend
- [ ] Thread-safe publishing pattern implemented for background tasks
- [ ] SSE channel documentation created/updated

## Contract

<inputs_prereqs>
HTMX installed and configured; SSE endpoints returning `text/event-stream` content type; For Alpine.js approach: SSE manager module loaded; Understanding of async Python patterns
</inputs_prereqs>

<mandatory>
sse-starlette or equivalent SSE library; asyncio for thread-safe publishing; Browser with EventSource support; SSE channel documentation file (docs/SSE_EVENTS.md)
</mandatory>

<forbidden>
Mixing HTMX SSE extension with Alpine.js SSE manager on same element; Using `sse:` prefix in HTMX triggers when events come from Alpine.js; Calling `asyncio.get_event_loop()` from background threads; Hardcoding event types without documentation
</forbidden>

<steps>
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
</steps>

<output_format>
SSE endpoint returning EventSourceResponse with events in format: `event: event_type\ndata: json_payload\n\n`
</output_format>

<validation>
- SSE connection established (browser DevTools Network tab shows EventSource)
- Events received match documented event types exactly
- HTMX elements update when SSE events arrive
- No duplicate connections when using Alpine.js manager
- Background thread publishing works without RuntimeError
</validation>

## SSE Approach Decision Matrix

**When to use HTMX SSE extension:**
- Simple element updates (minimal JavaScript, declarative)

**When to use Alpine.js SSE manager:**
- Multiple elements from one channel (single connection, multiple targets)
- Complex event handling logic (full JavaScript control)
- Toast notifications on events (requires JavaScript for toasts)

**When to use Dedicated SSE endpoint:**
- Streaming progress updates (per-operation stream)

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

## Post-Execution Checklist

- [ ] SSE approach chosen and consistent across page
- [ ] Event types match exactly between backend and frontend
- [ ] HTMX triggers use camelCase (not `sse:` prefix) when using Alpine.js
- [ ] Thread-safe publishing pattern used for background tasks
- [ ] SSE channel documentation updated
- [ ] Heartbeat/ping handling implemented
- [ ] Reconnection logic tested

## Validation

**Success Checks:**
- SSE endpoint returns `Content-Type: text/event-stream` header
- Browser DevTools Network tab shows EventSource connection (type: eventsource)
- Events arrive with correct `event:` field matching documented types
- HTMX elements swap content when SSE events trigger updates
- Alpine.js SSE manager receives events and triggers HTMX refreshes
- Background thread publishing completes without `RuntimeError: no running event loop`
- Connection automatically reconnects after network interruption

**Negative Tests:**
- Mismatched event type: frontend listener does not fire (verify no silent failures)
- Missing `sse:` prefix with HTMX extension: element does not update
- Using `sse:` prefix with Alpine.js `htmx.trigger()`: element does not update
- Calling `asyncio.get_event_loop()` in thread: raises RuntimeError
- Duplicate SSE connections: only one EventSource per channel in Network tab

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

### Backend Response Pattern (FastAPI)

```python
from sse_starlette.sse import EventSourceResponse

async def sse_endpoint():
    async def generator():
        yield {"event": "status", "data": json.dumps({"ready": True})}
        yield {"event": "update", "data": json.dumps({"count": 42})}
    return EventSourceResponse(generator())
```

### Frontend Listener Pattern (Alpine.js + HTMX)

```html
<div x-data="page()" x-init="init()">
    <div id="target" hx-get="/content" hx-trigger="load, contentUpdated"></div>
</div>
<script>
function page() {
    return {
        init() {
            window.sseManager.connect('channel', (data, event) => {
                htmx.trigger('#target', 'contentUpdated');
            });
        }
    };
}
</script>
```

## References

### Related Rules

- **HTMX Core**: `rules/221-python-htmx-core.md` - Foundation patterns
- **Alpine.js Integration**: `rules/221f-python-htmx-integrations.md` - Alpine.js patterns
- **Logging Patterns**: `rules/207-python-logging.md` - Web logging with SSE

### Project Documentation

- **SSE Events Reference**: `docs/SSE_EVENTS.md` - Channel and event type documentation
