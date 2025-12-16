# FastAPI + HTMX Integration

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** fastapi, async, dependency injection, background tasks, oauth2, jwt, fastapi templates, starlette, pydantic, async routes
**TokenBudget:** ~2300
**ContextTier:** Medium
**Depends:** rules/221-python-htmx-core.md, rules/221a-python-htmx-templates.md

## Purpose

Defines FastAPI-specific integration patterns for HTMX applications, covering async route handlers, Jinja2 template configuration, dependency injection for HTMX detection, background task patterns with polling, and authentication strategies.

## Rule Scope

FastAPI web applications integrating HTMX for hypermedia-driven interfaces with async/await patterns

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Configure Jinja2Templates** - Set up FastAPI template rendering with Jinja2
- **Use async route handlers** - Leverage `async def` for I/O-bound operations
- **Implement dependency injection** - Create dependencies for HTMX detection and auth
- **Handle background tasks** - Use FastAPI BackgroundTasks with HTMX polling
- **Validate with Pydantic** - Use Pydantic models for form validation, return HTML on errors
- **Configure CSRF protection** - Use middleware or Starlette-WTF

**Pre-Execution Checklist:**
- [ ] Jinja2Templates configured with template directory
- [ ] HTMX detection dependency created
- [ ] Async route handlers defined for I/O operations
- [ ] Pydantic models created for form validation
- [ ] CSRF protection middleware installed (if needed)
- [ ] Authentication dependency implemented (if needed)
- [ ] Background task + polling pattern tested

## Contract

<inputs_prereqs>
FastAPI installed; Jinja2 templates configured; HTMX library in frontend; understanding of async/await; HTMX core patterns (221-python-htmx-core.md); template strategies (221a-python-htmx-templates.md)
</inputs_prereqs>

<mandatory>
FastAPI framework; python-multipart for form data; Jinja2; HTMX library; async route handlers; dependency injection system; Pydantic for validation
</mandatory>

<forbidden>
Blocking I/O in async routes; returning JSON for HTMX requests; mixing sync/async inappropriately; skipping input validation; bypassing CSRF protection; using global state
</forbidden>

<steps>
1. Install FastAPI, Jinja2, python-multipart
2. Configure Jinja2Templates with template directory
3. Create dependency for HTMX request detection
4. Define async routes with proper dependency injection
5. Implement Pydantic models for form validation
6. Configure CSRF protection (Starlette-WTF or custom)
7. Test async routes with HTMX requests
</steps>

<output_format>
FastAPI application with async routes, Jinja2 templates, dependency injection, Pydantic validation, HTMX integration
</output_format>

<validation>
- Jinja2Templates renders partials and full pages correctly
- HTMX detection dependency works in routes
- Async routes handle I/O without blocking
- Form validation returns HTML error responses
- CSRF protection active for state-changing routes
- Tests validate async behavior and HTMX responses
</validation>

## Key Principles

### 1. Jinja2Templates Configuration

**Setup:**
```python
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI()

# Configure templates
templates = Jinja2Templates(directory="templates")

# Or with multiple directories
templates = Jinja2Templates(directory=["templates", "app/templates"])

# Add custom filters (optional)
def format_date(value):
    return value.strftime('%Y-%m-%d')

templates.env.filters['format_date'] = format_date
```

**Basic Template Rendering:**
```python
from fastapi import Request
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "pages/home.html",
        {"request": request}  # Required by Jinja2Templates
    )
```

### 2. HTMX Detection Dependency

**Dependency Function:**
```python
from fastapi import Request

def is_htmx(request: Request) -> bool:
    """Dependency to detect HTMX requests"""
    return request.headers.get('HX-Request') == 'true'

# Usage in route
@app.get("/users")
async def users_list(
    request: Request,
    htmx: bool = Depends(is_htmx)
):
    users = await get_users()

    if htmx:
        return templates.TemplateResponse(
            "partials/_users_table.html",
            {"request": request, "users": users}
        )

    return templates.TemplateResponse(
        "pages/users.html",
        {"request": request, "users": users}
    )
```

**Enhanced HTMX Context Dependency:**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class HTMXContext:
    is_htmx: bool
    trigger: Optional[str] = None
    target: Optional[str] = None
    current_url: Optional[str] = None

def get_htmx_context(request: Request) -> HTMXContext:
    """Extract all HTMX-related request headers"""
    return HTMXContext(
        is_htmx=request.headers.get('HX-Request') == 'true',
        trigger=request.headers.get('HX-Trigger'),
        target=request.headers.get('HX-Target'),
        current_url=request.headers.get('HX-Current-URL')
    )

# Usage
@app.get("/data")
async def get_data(
    request: Request,
    htmx_ctx: HTMXContext = Depends(get_htmx_context)
):
    if htmx_ctx.is_htmx:
        # Handle based on trigger, target, etc.
        pass
```

### 3. Async Route Patterns

**Async Route with Database I/O:**
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

@app.get("/users/{user_id}")
async def user_detail(
    user_id: int,
    request: Request,
    htmx: bool = Depends(is_htmx),
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    template = "partials/_user_detail.html" if htmx else "pages/user.html"
    return templates.TemplateResponse(
        template,
        {"request": request, "user": user}
    )
```

**Async Route with External API:**
```python
import httpx

@app.get("/weather/{city}")
async def weather(
    city: str,
    request: Request,
    htmx: bool = Depends(is_htmx)
):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.com/{city}")
        data = response.json()

    if htmx:
        return templates.TemplateResponse(
            "partials/_weather.html",
            {"request": request, "weather": data}
        )

    return templates.TemplateResponse(
        "pages/weather.html",
        {"request": request, "weather": data}
    )
```

### 4. Form Handling with Pydantic

**Pydantic Model:**
```python
from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., gt=0, lt=150)

    @validator('email')
    def email_must_be_lowercase(cls, v):
        return v.lower()
```

**Form Route with Validation:**
```python
from fastapi import Form, Response
from pydantic import ValidationError

@app.post("/users")
async def create_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    age: int = Form(...)
):
    try:
        user_data = UserCreate(name=name, email=email, age=age)
        user = await create_user_in_db(user_data)

        # Success: Return new user row
        return templates.TemplateResponse(
            "partials/_user_row.html",
            {"request": request, "user": user}
        )

    except ValidationError as e:
        # Error: Return form with errors
        errors = {err['loc'][0]: err['msg'] for err in e.errors()}
        response = templates.TemplateResponse(
            "partials/_user_form.html",
            {"request": request, "errors": errors, "name": name, "email": email, "age": age}
        )
        response.status_code = 400
        response.headers['HX-Retarget'] = '#user-form'
        return response
```

### 5. Background Tasks with Polling

**Background Task Pattern:**
```python
from fastapi import BackgroundTasks
import asyncio
import uuid

# In-memory task storage (use Redis in production)
tasks = {}

async def process_data(task_id: str, data: dict):
    """Long-running background task"""
    tasks[task_id] = {"status": "processing", "progress": 0}

    for i in range(10):
        await asyncio.sleep(1)  # Simulate work
        tasks[task_id]["progress"] = (i + 1) * 10

    tasks[task_id]["status"] = "completed"
    tasks[task_id]["result"] = "Data processed successfully"

@app.post("/process")
async def start_processing(
    background_tasks: BackgroundTasks,
    data: dict
):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(process_data, task_id, data)

    # Return polling element
    return f'''
    <div hx-get="/tasks/{task_id}/status"
         hx-trigger="every 1s"
         hx-swap="outerHTML">
        Processing started...
    </div>
    '''

@app.get("/tasks/{task_id}/status")
async def task_status(task_id: str, request: Request):
    task = tasks.get(task_id, {"status": "unknown"})

    if task["status"] == "processing":
        return f'''
        <div hx-get="/tasks/{task_id}/status"
             hx-trigger="every 1s"
             hx-swap="outerHTML">
            Progress: {task['progress']}%
        </div>
        '''

    elif task["status"] == "completed":
        return f'<div class="success">{task["result"]}</div>'

    else:
        return '<div class="error">Task not found</div>'
```

### 6. Response Headers

**Setting HTMX Response Headers:**
```python
from fastapi.responses import HTMLResponse

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    await delete_user_from_db(user_id)

    response = HTMLResponse(content="", status_code=200)
    response.headers['HX-Trigger'] = 'userDeleted'
    return response

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = authenticate(username, password)
    if not user:
        return HTMLResponse(
            '<div class="error">Invalid credentials</div>',
            status_code=401
        )

    # Successful login: redirect
    response = HTMLResponse(content="", status_code=200)
    response.headers['HX-Redirect'] = '/dashboard'
    return response
```

### 7. Authentication with Dependency Injection

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

### 8. Server-Sent Events (SSE) with HTMX

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
# ✓ CORRECT: Capture loop before thread starts
loop = asyncio.get_running_loop()  # In async context
loop.call_soon_threadsafe(queue.put_nowait, data)  # From thread

# ✗ WRONG: Accessing event loop from thread
asyncio.get_event_loop()  # Raises "no current event loop in thread"
```

### 9. CSRF Protection

**Using Starlette-WTF:**
```bash
pip install starlette-wtf
```

```python
from starlette_wtf import CSRFProtectMiddleware

app.add_middleware(
    CSRFProtectMiddleware,
    csrf_secret="your-csrf-secret"
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

### Anti-Pattern 1: Blocking I/O in Async Routes

**Problem:** Using synchronous HTTP libraries (requests) in async FastAPI routes.

**Why It Fails:** Blocks the event loop; degrades performance; defeats async benefits.

**Correct Pattern:**
```python
@app.get("/data")
async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        data = response.json()
    return data
```

### Anti-Pattern 2: Missing Request in TemplateResponse

**Problem:** Omitting the `request` object from Jinja2 template context.

**Why It Fails:** Jinja2Templates requires request; causes runtime errors.

**Correct Pattern:**
```python
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
```

## Post-Execution Checklist

- [ ] Jinja2Templates configured with template directory
- [ ] HTMX detection dependency created and used
- [ ] Async routes use async I/O libraries
- [ ] Pydantic models validate form inputs
- [ ] Form validation errors return HTML (not JSON)
- [ ] Background tasks use FastAPI BackgroundTasks
- [ ] CSRF protection middleware configured
- [ ] Authentication dependency implemented
- [ ] Exception handlers check for HTMX requests
- [ ] Tests cover async routes and HTMX behavior

## Validation

**Success Checks:**
- HTMX detection dependency works correctly
- Async routes complete without blocking
- Form validation returns HTML error responses
- Background tasks execute and polling works
- CSRF tokens validated for state-changing routes
- Authentication redirects HTMX requests appropriately

**Negative Tests:**
- Blocking I/O causes performance issues (detected via profiling)
- Missing request context raises template error
- Invalid form data returns 400 with error HTML
- Unauthenticated HTMX request returns HX-Redirect

## Output Format Examples

### Complete FastAPI App
```python
from fastapi import FastAPI, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def is_htmx(request: Request) -> bool:
    return request.headers.get('HX-Request') == 'true'

@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    htmx: bool = Depends(is_htmx)
):
    template = "partials/_home.html" if htmx else "pages/home.html"
    return templates.TemplateResponse(template, {"request": request})

@app.post("/users")
async def create_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...)
):
    user = await create_user_in_db(name, email)
    return templates.TemplateResponse(
        "partials/_user_row.html",
        {"request": request, "user": user}
    )
```

## References

### External Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Official FastAPI guide
- [FastAPI Templates](https://fastapi.tiangolo.com/advanced/templates/) - Jinja2 with FastAPI
- [Starlette-WTF](https://github.com/muicss/starlette-wtf) - CSRF protection for Starlette/FastAPI
- [HTMX Examples](https://htmx.org/examples/) - HTMX patterns

### Related Rules
- **HTMX Foundation**: `rules/221-python-htmx-core.md` - HTMX core patterns
- **Template Strategies**: `rules/221a-python-htmx-templates.md` - Jinja2 patterns
- **Testing Patterns**: `rules/221d-python-htmx-testing.md` - Testing FastAPI+HTMX
- **Common Patterns**: `rules/221e-python-htmx-patterns.md` - CRUD, forms, etc.
- **Python Core**: `rules/200-python-core.md` - Python standards
