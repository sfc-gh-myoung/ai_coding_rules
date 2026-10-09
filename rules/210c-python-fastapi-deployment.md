---
schema_version: v4.0
rule_version: v5.0.0
description: "Reproducible FastAPI deployment, measured worker/resource budgets, secure runtime configuration, health and truthful OpenAPI contracts."
last_updated: 2026-10-07
keywords:
  - kw:gunicorn uvicorn worker
  - kw:multi-stage docker build
  - kw:health check endpoint
  - kw:non-root container user
  - kw:openapi schema customization
  - kw:worker process configuration
token_budget: ~1250
context_tier: High
depends:
  required:
    - 210-python-fastapi-core.md
---
# FastAPI Deployment and Documentation

## Scope

**What This Rule Covers:**
Platform/server choice, reproducible container dependencies, worker/lifecycle/health settings, secrets/network boundaries and API documentation.

**When to Load This Rule:**
When preparing FastAPI runtime/build or OpenAPI documentation changes; review `210a-python-fastapi-security.md` and `210e-python-fastapi-security-hardening.md` when auth/infrastructure security applies.

## Contract

### Inputs and Prerequisites

- Existing Dockerfile/Compose/server/CI configuration, platform/orchestrator, registry, Python/dependency lock, application lifespan and resource profile.
- Worker/replica/memory/connection limits, proxy/TLS policy, health requirements, graceful shutdown/rollback and approved deployment scope.
- Actual API models/status/security schemes, docs visibility, synthetic examples and current ASGI server version capabilities.

### Mandatory

- Extend existing working deployment rather than replacing it with mandatory Docker/Gunicorn. Uvicorn directly, process managers and orchestrator-managed replicas can all fit; one worker per replicated container is valid and async workers are not sequential-only.
- Size workers/replicas from measured concurrency, CPU quota, memory/model size, database pools and failure isolation; no universal 2*CPU+1 or fixed 512MB formula. Global in-process caches/rate limits/session state are not shared across workers.
- Use the actual project's dependency manager and locked compatible Python/platform dependencies. Build/runtime interpreter and copied environment path must align; match tested supported versions, not a blanket ban on newer deployment Python.
- Choose multi-stage builds when they reduce runtime dependencies; pin/review image/tool versions or digests without stale hardcoded patch numbers. Ensure uv sync uses the environment actually copied to runtime and application/package installation is complete.
- Keep credentials/source-private files out of layers/build context and development mounts; use .dockerignore, approved build/runtime secrets and non-root user/readable files. Do not copy a secret-bearing .env into the production image.
- Configure environment settings explicitly with no production secret fallbacks. Compose dependencies do not guarantee readiness; use health/retry orchestration. Development --reload, broad port mappings and weak sample database passwords are not production defaults.
- Use documented current worker class/process-manager interface; inspect installed Uvicorn/Gunicorn compatibility rather than copying obsolete worker imports. Preload must not fork already-open database/event-loop resources; initialize/dispose in worker lifespan appropriately.
- Set connect/request/keepalive/graceful timeouts, payload/resource limits and restart policy from workload, including streaming/WebSockets. Handle SIGTERM/draining and bounded cleanup; don't equate request timeout with safely cancelling all effects.
- Separate liveness (process/event-loop functioning) from readiness (required dependencies/configuration). Use bounded real checks, 503 when unavailable and minimal public information; missing dependency must not claim healthy or force destructive restart loops.
- Configure TLS/proxy/trusted hosts/forwarded headers and external bind explicitly for the target platform. Local test servers bind loopback unless wider exposure is approved; image build/run/push/deploy and registry authentication have distinct authority.
- Document route purpose, inputs, response model/status/errors, authentication scopes and API version. Preserve generated component/security definitions when customizing OpenAPI; do not overwrite every existing security scheme with one Bearer entry or invent global enforcement from schema metadata.
- Examples use synthetic safe data and match real validation/status. Docs/OpenAPI can be public, protected or disabled under policy; disabling /docs alone leaves other schema/UI routes. Docs visibility is not authorization.
- Validate reproducible build/startup/lifespan/resources and approved staging representative requests before production promotion; perform authorized image/dependency scanning and report actual residual findings without claiming zero vulnerabilities from a successful build.
- Capture version/config/consumer/migration changes and rollback scope. Database migrations are separately authorized and must not run once per worker by accident. Preserve existing volumes/data; no blind container teardown to test deployment.

### Execution Steps

1. Read existing deployment/build/app/API contracts and platform constraints; establish exact authorized scope.
2. Prepare minimal locked runtime/server/container changes with secrets, worker/pool budget, probes and graceful lifecycle.
3. Update accurate OpenAPI/docs examples without exposing private configuration or changing enforcement silently.
4. Run project checks and permitted local build/start/health/shutdown tests; use approved staging smoke/scan before deployment.
5. Report actual image/runtime/health/docs evidence, rollback and untested platform/security gaps.

### Validation

- Runtime interpreter/dependencies/image paths reproducible and application starts under intended server/user.
- Worker/replica capacity, pools, lifespan, signal/shutdown and streaming behavior match measured constraints.
- Required dependencies affect readiness truthfully; secrets/ports/TLS/proxy exposure match policy.
- OpenAPI models/status/security examples reflect actual application and approved visibility.
- Approved build/staging/scans are distinguished from static checks; no unapproved registry upload, deployment, migration or data deletion.

## References

- [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/)
- [FastAPI containers and worker replication](https://fastapi.tiangolo.com/deployment/docker/)
- [Uvicorn deployment reference](https://www.uvicorn.org/deployment/)
- [Gunicorn settings](https://docs.gunicorn.org/en/stable/settings.html)
- [OpenAPI customization](https://fastapi.tiangolo.com/how-to/extending-openapi/)
- [Lifespan](https://fastapi.tiangolo.com/advanced/events/)
