---
schema_version: v4.0
rule_version: v5.0.0
description: "FastAPI architecture, correct async/sync boundaries, typed API models, scoped resource lifecycle, and safe errors."
last_updated: 2026-10-07
keywords:
  - kw:application factory
  - kw:APIRouter modular routing
  - kw:Pydantic request response separation
  - kw:async def route handlers
  - kw:dependency injection database sessions
  - kw:uvicorn ASGI server
  - kw:fastapi
token_budget: ~1400
context_tier: High
depends:
  required:
    - 200-python-core.md  # Python foundation for all Python projects
  optional:
    - 203-python-project-setup.md  # Project structure and uv setup
    - 210b-python-fastapi-testing.md  # FastAPI testing strategies
    - 210d-python-fastapi-monitoring.md  # FastAPI monitoring and observability
---
# FastAPI Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> Essential FastAPI architecture and execution contract.

## Scope

**What This Rule Covers:**
Application/router structure, sync/async execution, dependencies/resources, request/response validation, error contracts, configuration and lifecycle.

**When to Load This Rule:**
When building or modifying FastAPI APIs. Read `210b-python-fastapi-testing.md` for tests, `210d-python-fastapi-monitoring.md` for streaming/metrics, `210a-python-fastapi-security.md` for auth and `210c-python-fastapi-deployment.md` for deployment.

## Contract

### Inputs and Prerequisites

- Existing application/routes/models/services/dependencies, Python/dependency manager/lock and installed FastAPI/Pydantic/server versions.
- API requirements, data/auth boundaries, actual database/client sync or async interfaces, resource budgets and error contract.
- Authorized local execution/dependency/configuration/deployment scope; read current architecture before adding abstractions.

### Mandatory

- Follow the project's established manager/automation and structure. Use uv run where uv is established, not mandatory new uv init or installing another server. Factory construction and APIRouter modules support testable apps; preserve existing equivalent structure and avoid speculative layers for a tiny API.
- Separate configuration/app construction from resource startup. Use supported lifespan context for shared clients/engines and shutdown cleanup; fail clearly on missing required settings, without import-time external connections or secret defaults.
- Choose async def for awaitable I/O; normal def routes/dependencies run in FastAPI's thread pool and can use sync libraries. A directly called sync helper inside async code is not automatically offloaded. Use appropriate bounded thread offload where necessary; don't call blocking requests/sleep/ORM directly on the event loop.
- CPU-heavy work needs measured executor/process/job design, not assuming asyncio.to_thread removes GIL or cancellation instantly stops a worker. Bound concurrency, client timeouts, outstanding work and memory.
- Use dependency injection for services/auth and request-scoped sessions; don't share an AsyncSession between concurrent tasks/requests. Explicitly own transaction commit/rollback semantics and cleanup. A generator dependency's teardown timing can depend on scope/version/streaming; do not defer critical commits blindly until after response success.
- Pool clients/connections when supported; size aggregate capacity across workers/replicas relative to actual database limits. Investigate leaks, slow queries and saturation before increasing pools; no universal pool-size/connection-limit table.
- Define Pydantic input constraints and explicit response projection; separate models when fields/security differ, reuse only when genuinely identical. Never return password/hash/token/internal fields through broad ORM serialization. Validate business authorization independently of shape.
- For updates distinguish omitted fields from explicit NULL with the intended model/exclude_unset behavior; enforce protected-field/mass-assignment rules. Money/precision/date/time and coercion must follow actual domain requirements.
- Handle expected errors with meaningful status and safe details; keep production stack traces, SQL/credential errors and sensitive request inputs out of responses/logs. Pydantic validation error objects may include raw input and non-JSON context; sanitize before returning custom responses.
- Preserve consistent error contracts and useful internal correlation IDs; don't convert all HTTP errors to 500 or swallow cancellation. Add global handlers only for distinct needs not already covered by framework/project behavior.
- Centralize typed settings with explicit required versus optional values, approved secrets and separate environments; no hardcoded credentials or automatic persistent writes. Missing secret fails before serving traffic.
- Configure CORS/trusted-host/proxy/middleware from deployment policy. Middleware wraps in registration order effects; verify actual request/response/error behavior instead of a blanket security-before-compression ordering rule.
- WebSockets require trusted authentication/authorization, bounded messages/rate and disconnect cleanup; client_id in a path is not identity. SSE/cross-thread state must use the captured running event loop and thread-safe scheduling, not asyncio.get_event_loop inside an unrelated thread.
- API docs/OpenAPI access is deployment policy; /docs can intentionally be disabled/protected. Starting a dev --reload server does not prove production readiness and must not bind external interfaces without approval.

### Execution Steps

1. Read current app/toolchain/model/dependency/auth patterns and clarify API/resource requirements.
2. Implement smallest compatible route/service/schema change with correct sync/async boundary and resource lifecycle.
3. Verify response projection/business access, transactions, error behavior and configuration using focused tests.
4. Run project lint/format/typecheck/test automation; use authorized local lifespan/startup smoke only when needed.
5. Report behavior, tests and remaining deployment/concurrency/database gaps without claiming unsupported runtime success.

### Validation

- Routes/routers and typed contracts match existing architecture and intended API, including omitted/NULL and sensitive fields.
- Awaitable/blocking boundaries, session ownership, transactions and shared-client cleanup are correct.
- Error handling/validation/logs preserve safe context and statuses; auth and WebSocket/stream boundaries are tested.
- Settings, middleware and docs visibility match environment policy; database/pool/worker budgets justified.
- Project checks pass and unexecuted server/database/deployment behavior stays unverified; no unauthorized install/start/deploy.

## References

- [FastAPI async/sync execution](https://fastapi.tiangolo.com/async/)
- [Routers and application structure](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Lifespan](https://fastapi.tiangolo.com/advanced/events/)
- [Dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)
- [Response models](https://fastapi.tiangolo.com/tutorial/response-model/)
- [SQLAlchemy async session/engine](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
