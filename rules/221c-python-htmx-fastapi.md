# FastAPI + HTMX Integration

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-03-09
**Keywords:** fastapi, async, dependency injection, background tasks, fastapi templates, starlette, pydantic, async routes
**TokenBudget:** ~3450
**ContextTier:** Medium
**Depends:** 221-python-htmx-core.md, 221a-python-htmx-templates.md
**LoadTrigger:** kw:htmx-fastapi

## Scope

**What This Rule Covers:**
FastAPI-specific integration patterns for HTMX applications, covering async route handlers, Jinja2 template configuration, dependency injection for HTMX detection, background task patterns with polling, and response header management. For authentication, SSE, and CSRF, see 221h.

**When to Load This Rule:**
- Building FastAPI applications with HTMX
- Implementing async route handlers for HTMX
- Using dependency injection for HTMX detection
- Configuring Jinja2 templates with FastAPI
- Implementing background tasks with HTMX polling

## References

### Dependencies

**Must Load First:**
- **221-python-htmx-core.md** - HTMX foundation patterns
- **221a-python-htmx-templates.md** - Jinja2 patterns

**Related:**
- **221h-python-htmx-fastapi-auth.md** - Auth, SSE, CSRF for FastAPI+HTMX
- **221d-python-htmx-testing.md** - Testing FastAPI+HTMX
- **221e-python-htmx-patterns.md** - CRUD, forms, etc.
- **200-python-core.md** - Python standards

### External Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Official FastAPI guide
- [FastAPI Templates](https://fastapi.tiangolo.com/advanced/templates/) - Jinja2 with FastAPI
- [Starlette-WTF](https://github.com/muicss/starlette-wtf) - CSRF protection for Starlette/FastAPI
- [HTMX Examples](https://htmx.org/examples/) - HTMX patterns

## Contract

### Inputs and Prerequisites

- FastAPI installed
- Jinja2 templates configured
- HTMX library in frontend
- Understanding of async/await
- HTMX core patterns (221-python-htmx-core.md)
- Template strategies (221a-python-htmx-templates.md)

### Mandatory

- FastAPI framework
- python-multipart for form data
- Jinja2
- HTMX library
- Async route handlers
- Dependency injection system
- Pydantic for validation

### Forbidden

- Blocking I/O in async routes
- Returning JSON for HTMX requests
- Using synchronous I/O libraries (`requests`, `urllib3`, `psycopg2`, `pymysql`) inside `async def` routes — use async alternatives (`httpx`, `asyncpg`, `aiomysql`) or wrap with `asyncio.to_thread()`
- Accepting form data without Pydantic model validation or FastAPI parameter constraints (`Field(min_length=1, max_length=255)`, `Query(ge=1, le=100)`, `Path(gt=0)`) — every user input must have type + constraint validation
- Bypassing CSRF protection
- Using unmanaged global state for request data — use dependency injection, Redis, or database instead. Module-level registries for lifecycle management (e.g., background task tracking) are acceptable when clearly labeled for production replacement.

### Execution Steps

1. Install FastAPI, Jinja2, python-multipart
2. Configure Jinja2Templates with template directory
3. Create dependency for HTMX request detection
4. Define async routes with proper dependency injection
5. Implement Pydantic models for form validation
6. Configure CSRF protection (Starlette-WTF or custom)
7. Test async routes with HTMX requests

### Output Format

- FastAPI application with async routes
- Jinja2 templates
- Dependency injection
- Pydantic validation
- HTMX integration

### Validation

**Pre-Task-Completion Checks:**
- Jinja2Templates configured with template directory
- HTMX detection dependency created
- Async route handlers defined for I/O operations
- Pydantic models created for form validation
- CSRF protection middleware installed (if needed)
- Authentication dependency implemented (if needed)

**Success Criteria:**
- Jinja2Templates renders partials and full pages correctly
- HTMX detection dependency works in routes
- Async routes handle I/O without blocking
- Form validation returns HTML error responses
- CSRF protection active for state-changing routes
- Tests validate async behavior and HTMX responses

### Design Principles

- **Configure Jinja2Templates** - Set up FastAPI template rendering with Jinja2
- **Use async route handlers** - Leverage `async def` for I/O-bound operations
- **Implement dependency injection** - Create dependencies for HTMX detection and auth
- **Handle background tasks** - Use FastAPI BackgroundTasks with HTMX polling
- **Validate with Pydantic** - Use Pydantic models for form validation, return HTML on errors
- **Configure CSRF protection** - Use middleware or Starlette-WTF

### Post-Execution Checklist

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
- [ ] Background task + polling pattern tested

> **Investigation Required**
> Before modifying FastAPI+HTMX integration, the agent MUST:
> 1. Check if `Jinja2Templates` is already configured — never create a duplicate `templates` instance
> 2. Verify existing dependency injection patterns for HTMX detection (`is_htmx()` or `HTMXContext`)
> 3. Check current CSRF middleware setup (Starlette-WTF may already be configured)
> 4. Read existing `Depends()` patterns to match the project's DI style
> 5. Check if `python-multipart` is installed (required for form data): `uv pip list | grep multipart`
> 6. Verify existing authentication dependencies before adding JWT patterns

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
from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., gt=0, lt=150)

    @field_validator('email', mode='before')
    @classmethod
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

# NOTE: Module-level dict for demo only. In production, replace with:
# - Redis: `await redis.hset(f"task:{task_id}", mapping=task_data)`
# - Database: `await db.execute(insert(Task).values(...))`
tasks: dict[str, dict] = {}

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
    request: Request,
    background_tasks: BackgroundTasks,
    data: dict
):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(process_data, task_id, data)

    # Return polling element
    return templates.TemplateResponse(
        "partials/_task_progress.html",
        {"request": request, "task_id": task_id, "progress": 0}
    )

@app.get("/tasks/{task_id}/status")
async def task_status(task_id: str, request: Request):
    task = tasks.get(task_id, {"status": "unknown"})

    if task["status"] == "processing":
        return templates.TemplateResponse(
            "partials/_task_progress.html",
            {"request": request, "task_id": task_id, "progress": task["progress"]}
        )

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

## Output Format

See sections 1-4 for complete examples of Jinja2Templates setup, HTMX detection, async routes, and form handling with Pydantic.
