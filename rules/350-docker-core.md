# Docker Core

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-03-09
**Keywords:** Docker, Dockerfile, containers, multi-stage builds, layer caching, image optimization, docker-compose, BuildKit, distroless, security scanning, SBOM, non-root, healthcheck
**TokenBudget:** ~4250
**ContextTier:** Medium
**Depends:** 000-global-core.md, 202-markup-config-validation.md
**LoadTrigger:** file:Dockerfile, file:docker-compose.yml, file:docker-compose.yaml, kw:docker, kw:container

## Scope

**What This Rule Covers:**
Provides practical, production-ready guidance for authoring Dockerfiles, building images, and running containers securely and efficiently, minimizing image size, build time, and supply-chain risk.

**When to Load This Rule:**
- Creating or updating Dockerfiles
- Implementing multi-stage builds
- Optimizing Docker image size and build time
- Securing container images and runtime
- Setting up Docker Compose for development
- Implementing CI/CD with Docker

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules
- **202-markup-config-validation.md** - Configuration validation patterns

**Related:**
- **200-python-core.md** - Python-specific Docker patterns
- **203-python-project-setup.md** - Python project structure for containers

### External Documentation

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/) - Official Docker guidance
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/) - Complete Dockerfile syntax
- [Docker Security](https://docs.docker.com/engine/security/) - Security best practices
- [BuildKit Documentation](https://docs.docker.com/build/buildkit/) - Advanced build features

## Contract

### Inputs and Prerequisites

- Container runtime (Docker Engine 20.10+ with BuildKit default, or Podman)
- Docker Compose v2+ (integrated CLI plugin)
- BuildKit features used: `--mount=type=cache` (18.09+), heredocs (20.10.13+)
- Access to base images/registries
- Project source with `.dockerignore`
- Hadolint (Dockerfile linter)
- Docker Scout, Trivy, or Grype (security scanning)
- SBOM tools (syft)
- Cosign for image signatures
- SLSA provenance tooling

**Toolchain Verification:** Before starting, verify tools are available:
```bash
command -v hadolint && command -v trivy && command -v syft && command -v cosign
```
Install missing tools before proceeding. See each tool's documentation for installation instructions.

### Mandatory

- MUST use multi-stage builds for production images
- MUST run containers as non-root user
- MUST include HEALTHCHECK in Dockerfile or orchestrator
- MUST pin base images to specific versions or digests
- MUST scan images for vulnerabilities in CI pipeline
- MUST generate SBOM for production images

### Forbidden

- Embedding secrets in images
- Running containers with privileged mode without documented justification (MUST include `# PRIVILEGED: <reason>` comment; acceptable reasons: host device access `/dev/*`, kernel parameter modification via sysctl, Docker-in-Docker for CI; NOT acceptable: "app needs it", "debugging", "easier than finding specific capabilities")
- `latest` floating tags in production
- Copying secrets into image layers
- Running as root user

### Execution Steps

1. Author a minimal, multi-stage Dockerfile with deterministic builds
2. Implement `.dockerignore` and order layers for cache effectiveness
3. Enforce least-privilege (non-root, read-only FS, drop capabilities)
4. Pin image digests/versions; scan image; attach SBOM and provenance
5. Define runtime healthchecks and resource limits; externalize secrets
6. Use Compose for dev with overrides; separate prod config

### Output Format

Deterministic Dockerfile(s) and Compose files with:
- Explicit versions
- Comments where non-obvious
- Validated by linters/scanners
- Multi-stage builds
- Security best practices

### Validation

**Pre-Task-Completion Checks:**
- [ ] Multi-stage Dockerfile
- [ ] Base images pinned
- [ ] Non-root USER specified
- [ ] .dockerignore configured
- [ ] Layers optimized for caching
- [ ] HEALTHCHECK defined
- [ ] Security scan passing

**Success Criteria:**
- Build with BuildKit succeeds
- Image size optimized: <200MB for Python apps, <50MB for Go/distroless, <100MB for Node.js
- Hadolint passes with no errors
- Vulnerability scan clean: no critical or high CVEs; medium CVEs documented with justification
- Container runs as non-root
- Healthcheck defined and working
- Digest pinning verified
- SBOM generated

**Error Recovery:**

- **Build failure (cache invalidation):** Run `docker builder prune` to clear stale cache. If layer caching is inconsistent, rebuild with `--no-cache` once, then re-enable caching. Check `.dockerignore` for missing entries that cause unnecessary cache busts.
- **Build failure (BuildKit):** Verify BuildKit is enabled: `DOCKER_BUILDKIT=1` or `docker buildx create --use`. Check `docker buildx ls` for builder health. For multi-platform builds, ensure QEMU is registered: `docker run --rm --privileged multiarch/qemu-user-static --reset -p yes`.
- **Security scan failure (CVEs found):** Update base image to latest patched version. If CVE is in a dependency, pin to a fixed version. For false positives or accepted risks, document with `--ignore` flags and add justification to the security policy. Re-scan after each change.
- **Registry access failure:** Verify authentication: `docker login <registry>`. Check network connectivity and proxy settings. For rate-limited registries (Docker Hub), use authenticated pulls or mirror to a private registry. Fallback: cache base images in CI artifacts.
- **HEALTHCHECK runtime failure:** If HEALTHCHECK fails: verify the health endpoint responds locally (`curl -f http://localhost:<port>/health`), check container logs (`docker logs <id>`), verify the `--start-period` is sufficient for application startup (increase if startup is slow). For orchestrated deployments, configure `restart: unless-stopped` in Compose or appropriate Kubernetes restart policy (`restartPolicy: Always` with `livenessProbe`). Common causes: app not yet listening, wrong port, endpoint returns non-2xx.

### Design Principles

- **MUST:** Use multi-stage builds; choose slim, LTS base images
- **MUST:** Add a `.dockerignore` to keep contexts tiny; avoid copying VCS/venv/node_modules
- **MUST:** Run as a dedicated non-root user; drop Linux capabilities; prefer read-only FS
- **MUST:** Pin base images and packages; avoid `latest`; prefer digest pinning for prod
- **MUST:** Structure layers to maximize caching; separate dependency installation from source copy
- **MUST:** Generate SBOM and sign images; store attestations in registry
- **MUST:** Provide a `HEALTHCHECK`; avoid long `CMD` shell strings; use JSON exec form
- **SHOULD:** Select base image tier based on application needs:
  - **Distroless:** Single static binary (Go, Rust), Java JAR with bundled JRE
  - **Minimal (Alpine/slim):** Apps needing shell for debugging, Python/Node.js apps (verify glibc/musl compatibility before switching to Alpine)
  - **Full base:** Development containers, apps requiring system packages. When unsure, default to Alpine/slim.
- **MUST NOT:** COPY secrets into images; bake environment-specific values into image layers; use privileged containers without documented justification

### Post-Execution Checklist

- [ ] Multi-stage Dockerfile implemented
- [ ] Base images pinned to specific versions/digests
- [ ] Non-root USER specified in Dockerfile
- [ ] .dockerignore configured and tested
- [ ] Layers optimized for caching
- [ ] HEALTHCHECK defined
- [ ] Security scan passing (hadolint, trivy)
- [ ] SBOM generated
- [ ] Image signed with cosign
- [ ] Docker Compose configured for development
- [ ] Secrets externalized (not in image)
- [ ] Resource limits defined
- [ ] Container runs successfully as non-root

## Anti-Patterns and Common Mistakes

### Pattern 1: Using `latest` Tag in Production Dockerfiles

**Problem:**
Developers use `FROM python:latest` or `FROM node:latest` in Dockerfiles, creating non-reproducible builds that break unpredictably when upstream images update.

**Why It Fails:**
The `latest` tag is mutable — it points to different image contents over time. A build that works today may fail tomorrow when the base image updates with breaking changes, new OS packages, or a different Python/Node minor version. This violates deterministic build requirements and makes debugging production incidents nearly impossible.

**Bad:**
```dockerfile
FROM python:latest
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

**Correct Pattern:**
```dockerfile
# Pin to specific version and digest for reproducibility
FROM python:3.12-slim@sha256:abc123...
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

### Pattern 2: COPY . . Before Dependency Installation (Cache Bust)

**Problem:**
Developers copy the entire application source before installing dependencies, causing Docker to re-download and reinstall all dependencies on every source code change.

**Why It Fails:**
Docker layer caching invalidates all subsequent layers when a layer changes. If `COPY . .` comes before `pip install` or `npm ci`, any source file change invalidates the dependency installation layer. This turns a seconds-long rebuild into a minutes-long full reinstall of all dependencies.

**Bad:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]
```

**Correct Pattern:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
# Copy dependency manifest first — this layer is cached until requirements change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy source code last — only this layer rebuilds on code changes
COPY . .
CMD ["python", "app.py"]
```

> **Investigation Required**
> When applying this rule:
> 1. **Read existing Dockerfile BEFORE suggesting changes** - Check current structure, stages
> 2. **Verify base image compatibility** - Check if changing base breaks dependencies
> 3. **Never assume layer order** - Check existing layer organization before optimizing
> 4. **Check for secrets** - Review if secrets are hardcoded or properly externalized
> 5. **Test build and run** - Verify changes don't break builds or runtime
>
> **Anti-Pattern:**
> "Adding multi-stage build... (without checking if dependencies are compatible)"
> "Changing to alpine... (without testing glibc compatibility)"
>
> **Correct Pattern:**
> "Let me check your current Dockerfile first."
> [reads Dockerfile, checks base image, reviews layers]
> "I see you're using debian:12. Adding multi-stage build with compatible base..."

## Output Format Examples

```dockerfile
# Multi-stage build following security best practices

# Stage 1: Build stage
FROM python:3.12-slim@sha256:specific-digest AS builder

# Create non-root user
RUN groupadd -r appuser --gid=1000 && \
    useradd -r -g appuser --uid=1000 --home=/app appuser

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage (minimal attack surface)
FROM python:3.12-slim@sha256:specific-digest

# Copy non-root user from builder
COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/group /etc/group

# Set up application
WORKDIR /app
COPY --from=builder --chown=appuser:appuser /app /app
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port and run
EXPOSE 8000
CMD ["python", "app.py"]
```

```bash
# Validation
docker build --no-cache -t myapp:test .
docker run --rm myapp:test python -c "print('Container validation passed')"
```

## Image Authoring Patterns
### Multi-Stage Builds (Generic)
```Dockerfile
# Filename: Dockerfile
# Stage 1: builder
FROM --platform=$BUILDPLATFORM golang:1.22-bookworm AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=$TARGETARCH go build -o app ./cmd/app

# Stage 2: runtime (distroless/static as appropriate)
FROM gcr.io/distroless/static:nonroot
WORKDIR /app
COPY --from=builder /src/app /app/app
USER nonroot:nonroot
ENTRYPOINT ["/app/app"]
```

### Python (uv/pip) Example
```Dockerfile
# Filename: Dockerfile
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

FROM base AS deps
WORKDIR /app
COPY pyproject.toml uv.lock* ./
# Prefer uv for speed & determinism; fallback to pip if needed
RUN if command -v uv >/dev/null 2>&1 || pip install --no-cache-dir uv; then \
        uv sync --frozen --no-dev; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

FROM base AS runtime
WORKDIR /app
# Create non-root user
RUN useradd -u 10001 -m appuser
COPY --from=deps /usr/local /usr/local
COPY . .
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://localhost:8000/health || exit 1
CMD ["uv", "run", "python", "-m", "myapp"]
```

### Example: .dockerignore (Industry-standard)
```
# VCS & metadata
.git
.github/

# IDE/Editor
.vscode/
.idea/

# Python
__pycache__/
*.py[cod]
.venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Node/Frontend
node_modules/
dist/
build/
.next/

# Secrets & env (never bake into image)
.env
.env.*
*.pem
*.key
```
See [Docker .dockerignore reference](https://docs.docker.com/build/concepts/context/#dockerignore-files) for comprehensive patterns.

## Build Performance and Caching
- **MUST:** Order layers: dependencies first, app code last.
- **MUST:** Use BuildKit features: `--mount=type=cache` for pip/npm caches.
- **SHOULD:** Use `--platform` for cross-building; prefer `docker buildx bake` for matrix builds.
- **MUST:** Pin versions; rely on lock files (`uv.lock`, `poetry.lock`, `package-lock.json`).
- **MUST:** Produce SBOM for production images: `docker buildx build --sbom=true` or `syft packages`.

## Security and Least Privilege
- **MUST:** Run as non-root; set `USER` to an unprivileged UID/GID.
- **MUST:** Drop capabilities and use read-only FS when possible:
  - `--cap-drop=ALL --read-only --tmpfs /tmp` at runtime.
- **MUST:** Keep base images up-to-date; rebuild regularly.
- **MUST:** Scan images in CI (Docker Scout, Trivy, Grype); fail on critical CVEs.
- **SHOULD:** Avoid package managers in runtime stage; copy only built artifacts.
- **MUST NOT:** Expose SSH or add debug tools in production images.

## Supply Chain Integrity
- **MUST:** Pin images by digest in production deployments.
- **MUST:** Generate SBOM and attach provenance (SLSA/Attestations).
- **MUST:** Sign images with cosign; enforce signature verification in deployment.
- **SHOULD:** Use private registries for proprietary images; **MUST** for images containing internal code or credentials.

## Language-Specific Notes
### Python
- Use `uv` or `pip --no-cache-dir`; separate `requirements.txt` or lockfile from sources.
- For FastAPI/Uvicorn: prefer gunicorn/uvicorn workers and graceful shutdown signals.
- For data science: use `--mount=type=cache,target=/root/.cache/pip` to speed up large dependency installs.

### Node.js
- Copy only `package.json`/`package-lock.json` first; run `npm ci` then copy sources.
- Use `node:20-slim` or `node:20-alpine` for production; full `node:20` only for build stages.

### Java
- Use multi-stage with Maven/Gradle in builder; run with JRE or distroless Java.
- Pin JRE version explicitly: `eclipse-temurin:21-jre-alpine@sha256:...`.

## Runtime and Orchestration
- **MUST:** Provide `HEALTHCHECK` in image or orchestrator.
- **MUST:** Configure resource limits (CPU/memory), ulimits, and log drivers.
- **MUST:** Externalize configuration via env and mounted secrets; never bake secrets.
- **MUST:** Add readiness/liveness probes for orchestrated deployments (Kubernetes, Swarm); **SHOULD** implement graceful shutdown and PID 1 handling (use `tini` or `dumb-init` if entrypoint is not PID 1 aware).

## Compose and YAML
- **MUST:** Separate `compose.yml` (dev) and `compose.prod.yml` (prod overrides).
- **SHOULD:** Use `.env` files for local development; MUST NOT commit secrets to version control.
- **MUST:** Follow YAML safety practices (see `202-markup-config-validation.md`).

## CI/CD and Testing
- **MUST:** Lint Dockerfile with Hadolint; scan image on each build.
- **MUST:** Cache layers in CI with BuildKit; enable `--provenance` and `--sbom`.
- **SHOULD:** Run smoke tests using Testcontainers or `docker run` in CI; **MUST** for services with health endpoints.

## Docker Changes Checklist

When modifying Docker configuration, document each change:

- **Base image:** `<name:tag@sha256:...>`
- **Non-root user:** `<uid:gid>`
- **Healthcheck:** `<command>`
- **SBOM:** `<attached|artifact path>`
- **Signature:** `<cosign yes/no>`
