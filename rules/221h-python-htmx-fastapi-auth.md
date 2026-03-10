# 221h: FastAPI + HTMX Authentication, SSE & CSRF

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** fastapi, htmx, jwt, authentication, sse, csrf, starlette-wtf, oauth2, server-sent-events
**TokenBudget:** ~2400
**ContextTier:** Medium
**Depends:** 221c-python-htmx-fastapi.md, 221-python-htmx-core.md
**LoadTrigger:** kw:htmx-fastapi-auth, kw:htmx-jwt, kw:htmx-sse-fastapi, kw:htmx-csrf-fastapi

## Scope

**What This Rule Covers:**
Authentication, Server-Sent Events (SSE), and CSRF protection patterns for FastAPI+HTMX applications. Split from 221c to keep rule sizes manageable.

**When to Load This Rule:**
- Implementing JWT authentication for HTMX endpoints in FastAPI
- Setting up SSE streaming with HTMX
- Configuring CSRF protection with Starlette-WTF
- Handling 401/403 redirects for HTMX requests

## References

### Dependencies

**Must Load First:**
- **221c-python-htmx-fastapi.md** - Core FastAPI+HTMX patterns (Jinja2Templates, DI, async routes)
- **221-python-htmx-core.md** - HTMX foundation patterns

**Related:**
- **210a-python-fastapi-security.md** - FastAPI security patterns
- **221g-python-htmx-sse.md** - General SSE patterns
- **221d-python-htmx-testing.md** - Testing auth+HTMX

### External Documentation

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/) - Official security guide
- [Starlette-WTF](https://github.com/muicss/starlette-wtf) - CSRF protection for Starlette/FastAPI
- [HTMX SSE Extension](https://htmx.org/extensions/server-sent-events/) - SSE with HTMX

## Contract

### Inputs and Prerequisites

- FastAPI+HTMX application configured (see 221c)
- Jinja2Templates and HTMX detection dependency set up
- Understanding of FastAPI dependency injection

### Mandatory

- JWT via `python-jose` or `PyJWT` for token auth
- `python-multipart` for form-based login
- Starlette-WTF or custom middleware for CSRF
- Async-compatible patterns throughout

### Forbidden

- Storing JWT secrets in code — use environment variables
- Skipping CSRF protection on state-changing HTMX routes
- Using synchronous I/O in SSE generators

### Execution Steps

1. Implement JWT authentication dependency
2. Add HTMX-aware exception handler for 401/403
3. Configure SSE streaming endpoints (if needed)
4. Install and configure CSRF middleware

### Output Format

```python
# Example: JWT authentication dependency
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def require_auth(token: str = Depends(security)) -> dict:
    """Validate JWT and return payload."""
    try:
        payload = decode_jwt(token.credentials)
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
```

### Validation

**Success Criteria:**
- JWT auth dependency rejects invalid tokens with 401
- HTMX 401 responses include `HX-Redirect` to login
- SSE streams deliver real-time updates to HTMX clients
- CSRF tokens validated on all POST/PUT/DELETE requests

### Post-Execution Checklist

- [ ] JWT authentication dependency implemented
- [ ] Exception handler redirects HTMX 401s to login
- [ ] SSE streaming uses `asyncio.to_thread()` for blocking work
- [ ] Cross-thread communication uses `loop.call_soon_threadsafe()`
- [ ] CSRF middleware configured with secret from environment
- [ ] Templates include `{{ csrf_token() }}`

> **Investigation Required**
> Before modifying FastAPI+HTMX auth/SSE/CSRF, the agent MUST:
> 1. Check existing authentication dependencies — never create a duplicate `get_current_user`
> 2. Verify existing CSRF middleware setup (Starlette-WTF may already be configured)
> 3. Check if SSE endpoints already exist — extend rather than duplicate
> 4. Read existing exception handlers for 401/403 before adding new ones
> 5. Verify `python-jose` or `PyJWT` is installed: `uv pip list | grep -i jose`

## Key Principles

### 1. Authentication with Dependency Injection

**JWT Authentication:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401)
        return username
    except JWTError:
        raise HTTPException(status_code=401)

@app.get("/dashboard")
async def dashboard(
    request: Request,
    current_user: str = Depends(get_current_user),
    htmx: bool = Depends(is_htmx)
):
    if htmx:
        return templates.TemplateResponse(
            "partials/_dashboard.html",
            {"request": request, "user": current_user}
        )

    return templates.TemplateResponse(
        "pages/dashboard.html",
        {"request": request, "user": current_user}
    )
```

**Exception Handler for HTMX:**
```python
from fastapi import Request
from fastapi.responses import HTMLResponse

@app.exception_handler(HTTPException)
async def htmx_exception_handler(request: Request, exc: HTTPException):
    is_htmx_request = request.headers.get('HX-Request') == 'true'

    if exc.status_code == 401 and is_htmx_request:
        # Redirect to login for HTMX requests
        response = HTMLResponse(content="", status_code=401)
        response.headers['HX-Redirect'] = '/login'
        return response

    # Default handling for non-HTMX
    return HTMLResponse(content=str(exc.detail), status_code=exc.status_code)
```

### 2. Server-Sent Events (SSE) with HTMX

**SSE Streaming for Long-Running Operations:**
```python
from fastapi.responses import StreamingResponse
import asyncio
import json

@app.get("/operations/{op_id}/stream")
async def stream_operation_progress(op_id: str):
    """Stream progress updates via SSE for HTMX consumption."""
    # Capture event loop BEFORE any thread work
    loop = asyncio.get_running_loop()
    progress_queue: asyncio.Queue[dict] = asyncio.Queue()

    def progress_callback(step: str, message: str) -> None:
        """Thread-safe callback - uses captured loop reference."""
        loop.call_soon_threadsafe(
            progress_queue.put_nowait,
            {"step": step, "message": message, "timestamp": datetime.now().isoformat()}
        )

    async def event_generator():
        # Run blocking work with asyncio.to_thread()
        task = asyncio.create_task(
            asyncio.to_thread(run_operation, op_id, progress_callback)
        )

        while True:
            if task.done():
                # Drain remaining messages
                while not progress_queue.empty():
                    msg = await progress_queue.get()
                    yield f"data: {json.dumps(msg)}\n\n"

                try:
                    result = task.result()
                    yield f"data: {json.dumps({'step': 'done', 'success': True})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'step': 'error', 'message': str(e)})}\n\n"
                break

            try:
                msg = await asyncio.wait_for(progress_queue.get(), timeout=0.5)
                yield f"data: {json.dumps(msg)}\n\n"
            except TimeoutError:
                # Keepalive ping
                yield f"data: {json.dumps({'step': 'ping'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
```

**HTMX SSE Extension Usage:**
```html
<!-- Include SSE extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/sse.js"></script>

<!-- Connect to SSE stream -->
<div hx-ext="sse" sse-connect="/operations/123/stream">
    <div sse-swap="message" hx-swap="beforeend">
        <!-- Progress messages will be appended here -->
    </div>
</div>
```

**Critical Pattern - Cross-Thread Communication:**
```python
# CORRECT: Capture loop before thread starts
loop = asyncio.get_running_loop()  # In async context
loop.call_soon_threadsafe(queue.put_nowait, data)  # From thread

# WRONG: Accessing event loop from thread
asyncio.get_event_loop()  # Raises "no current event loop in thread"
```

### 3. CSRF Protection

**Using Starlette-WTF:**
```bash
uv add starlette-wtf
```

```python
import os
from starlette_wtf import CSRFProtectMiddleware

app.add_middleware(
    CSRFProtectMiddleware,
    csrf_secret=os.environ['CSRF_SECRET']
)

# Template usage
@app.get("/form")
async def form_page(request: Request):
    return templates.TemplateResponse(
        "partials/_form.html",
        {"request": request}
    )

# In template: {{ csrf_token() }}
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Hardcoded JWT Secret

**Problem:** Storing `SECRET_KEY` directly in source code.

**Correct Pattern:**
```python
import os
SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"
```

### Anti-Pattern 2: Missing HTMX Exception Handler

**Problem:** Default FastAPI exception handler returns JSON for 401/403, breaking HTMX flows.

**Correct Pattern:**
```python
# BAD: Default JSON response breaks HTMX
@app.exception_handler(HTTPException)
async def default_handler(request, exc):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
# HTMX receives JSON instead of redirect, page doesn't update

# GOOD: Return HX-Redirect for HTMX requests
@app.exception_handler(HTTPException)
async def htmx_exception_handler(request: Request, exc: HTTPException):
    if request.headers.get("HX-Request"):
        if exc.status_code in (401, 403):
            response = Response(status_code=exc.status_code)
            response.headers["HX-Redirect"] = "/login"
            return response
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
```

Use the `htmx_exception_handler` from Section 1 to return `HX-Redirect` headers for HTMX requests.

## Output Format

See Section 1 for JWT auth + exception handler, Section 2 for SSE streaming, Section 3 for CSRF setup.
