# Docker and Dockerfile Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** Docker, Dockerfile, containers, multi-stage builds, layer caching, image optimization, docker-compose, BuildKit, distroless, security scanning, SBOM, non-root, healthcheck
**TokenBudget:** ~3150
**ContextTier:** Medium
**Depends:** 000-global-core.md, 202-markup-config-validation.md

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

- Container runtime (Docker/Podman)
- BuildKit enabled
- Access to base images/registries
- Project source with `.dockerignore`

### Mandatory

- Docker/Buildx/BuildKit
- Docker Compose
- Hadolint (Dockerfile linter)
- Docker Scout/Trivy/Grype (security scanning)
- SBOM tools (syft)
- Cosign for signatures
- SLSA provenance

### Forbidden

- Embedding secrets in images
- Running containers with privileged mode without justification
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
- Image size optimized
- Hadolint passes with no errors
- Vulnerability scan clean or acceptable
- Container runs as non-root
- Healthcheck defined and working
- Digest pinning verified
- SBOM generated

### Design Principles

- **Always:** Use multi-stage builds; choose slim, LTS base images
- **Always:** Add a `.dockerignore` to keep contexts tiny; avoid copying VCS/venv/node_modules
- **Always:** Run as a dedicated non-root user; drop Linux capabilities; prefer read-only FS
- **Always:** Pin base images and packages; avoid `latest`; prefer digest pinning for prod
- **Always:** Structure layers to maximize caching; separate dependency installation from source copy
- **Requirement:** Generate SBOM and sign images; store attestations in registry
- **Requirement:** Provide a `HEALTHCHECK`; avoid long `CMD` shell strings; use JSON exec form
- **Rule:** Prefer distroless/alpine only when appropriate; verify glibc/musl compatibility
- **Avoid:** COPY-ing secrets; baking envs into image; using privileged containers

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

### Pattern 1: [Common Mistake Title]

**Problem:**
[Describe what developers commonly do wrong]

**Why It Fails:**
[Explain why this approach causes issues]

**Correct Pattern:**
```python
# Correct approach with explanation
```

### Pattern 2: [Another Common Mistake]

**Problem:**
[Description of the anti-pattern]

**Why It Fails:**
[Technical explanation of the problem]

**Correct Pattern:**
```python
# Proper implementation
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
docker build --no-cache -t myapp:latest .
docker run --rm myapp:latest python -c "print('Container validation passed')"
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
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev || pip install --no-cache-dir -r requirements.txt

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
.gitignore
.gitattributes
.github/
.hg/
.svn/

# OS junk
.DS_Store
Thumbs.db
ehthumbs.db
Icon?
*.swp
*.swo

# Editors/IDE
.vscode/
.idea/
.vs/
*.suo
*.user
*.iml

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.venv/
venv/
.pytype/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.tox/
.coverage
.coverage.*
coverage.xml
htmlcov/
.eggs/
*.egg-info/

# Node/Frontend
node_modules/
npm-debug.log*
yarn-error.log*
.pnpm-store/
.next/
.nuxt/
.svelte-kit/
.vite/
.babel-cache/
.cache/
dist/
build/

# Java/JVM
target/
build/
.gradle/
.mvn/
*.class

# Go
bin/

# .NET / Microsoft
bin/
obj/
.vs/
*.svclog
*.user
*.suo

# Containers & tooling
docker-compose*.yml
.docker/
Dockerfile.*.local

# Secrets & env (never bake into image)
.env
.env.*
*.pem
*.key
*.crt
*.pfx
*.keystore
id_rsa
id_dsa

# Tests, docs, examples (uncomment if not needed during build)
# tests/
# docs/
# examples/
```

## Build Performance and Caching
- **Rule:** Order layers: dependencies first, app code last.
- **Rule:** Use BuildKit features: `--mount=type=cache` for pip/npm caches.
- **Rule:** Use `--platform` for cross-building; prefer `docker buildx bake` for matrix builds.
- **Requirement:** Pin versions; rely on lock files (`uv.lock`, `poetry.lock`, `package-lock.json`).
- **Consider:** Produce SBOM: `docker buildx build --sbom=true` or `syft packages`.

## Security and Least Privilege
- **Mandatory:** Run as non-root; set `USER` to an unprivileged UID/GID.
- **Mandatory:** Drop capabilities and use read-only FS when possible:
  - `--cap-drop=ALL --read-only --tmpfs /tmp` at runtime.
- **Requirement:** Keep base images up-to-date; rebuild regularly.
- **Requirement:** Scan images in CI (Docker Scout, Trivy, Grype); fail on critical CVEs.
- **Rule:** Avoid package managers in runtime stage; copy only built artifacts.
- **Avoid:** Exposing SSH or adding debug tools in prod images.

## Supply Chain Integrity
- **Requirement:** Pin images by digest in prod deployments.
- **Requirement:** Generate SBOM and attach provenance (SLSA/Attestations).
- **Rule:** Sign images with cosign; enforce signature verification in deployment.
- **Consider:** Use private registries; restrict pull from trusted sources only.

## Language-Specific Notes
### Python
- Use `uv` or `pip --no-cache-dir`; separate `requirements.txt` or lockfile from sources.
- For FastAPI/Uvicorn: prefer gunicorn/uvicorn workers and graceful shutdown signals.

### Node.js
- Copy only `package.json`/`package-lock.json` first; run `npm ci` then copy sources.

### Java
- Use multi-stage with Maven/Gradle in builder; run with JRE or distroless Java.

## Runtime and Orchestration
- **Requirement:** Provide `HEALTHCHECK` in image or orchestrator.
- **Rule:** Configure resource limits (CPU/memory), ulimits, and log drivers.
- **Rule:** Externalize configuration via env and mounted secrets; never bake secrets.
- **Consider:** Readiness/liveness probes, graceful shutdown, and PID 1 handling.

## Compose and YAML
- **Always:** Separate `compose.yml` (dev) and `compose.prod.yml` (prod overrides).
- **Rule:** Use `.env` files for local development; do not commit secrets.
- **Requirement:** Follow YAML safety practices (see `202-markup-config-validation.md`).

## CI/CD and Testing
- **Rule:** Lint Dockerfile with Hadolint; scan image on each build.
- **Rule:** Cache layers in CI with BuildKit; enable `--provenance` and `--sbom`.
- **Consider:** Smoke tests using Testcontainers or docker run in CI.

## Docker Changes
- Base image: <name:tag@sha256:...>
- Non-root user: <uid:gid>
- Healthcheck: <command>
- SBOM: <attached|artifact path>
- Signature: <cosign yes/no>
```
