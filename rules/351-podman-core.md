# Podman Core

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-02-05
**Keywords:** Podman, Containerfile, containers, rootless containers, buildah, podman-compose, pods, daemonless, systemd, quadlet, image optimization, non-root, healthcheck, security scanning, SBOM
**TokenBudget:** ~3650
**ContextTier:** Medium
**Depends:** 000-global-core.md, 202-markup-config-validation.md
**LoadTrigger:** file:Containerfile, file:podman-compose.yml, file:podman-compose.yaml, kw:podman, kw:buildah

## Scope

**What This Rule Covers:**
Provides practical, production-ready guidance for authoring Containerfiles, building images with Podman/Buildah, and running containers securely using Podman's daemonless, rootless-by-default architecture.

**When to Load This Rule:**
- Creating or updating Containerfiles (Podman's preferred naming)
- Implementing multi-stage builds with Buildah
- Running rootless containers with Podman
- Setting up Podman Compose for development
- Deploying containers as systemd services (Quadlet)
- Working with pods (Kubernetes-style grouping)

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules
- **202-markup-config-validation.md** - Configuration validation patterns

**Related:**
- **350-docker-core.md** - Docker-specific patterns (Podman is largely compatible)
- **200-python-core.md** - Python-specific container patterns
- **203-python-project-setup.md** - Python project structure for containers

### External Documentation

- [Podman Documentation](https://docs.podman.io/) - Official Podman guidance
- [Containerfile Reference](https://docs.podman.io/en/latest/markdown/podman-build.1.html) - Build syntax
- [Buildah Documentation](https://buildah.io/) - Image building tool
- [Quadlet Documentation](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) - Systemd integration

## Contract

### Inputs and Prerequisites

- Podman installed (daemonless, no service required)
- Buildah for advanced image building (optional)
- Access to base images/registries
- Project source with `.containerignore` (or `.dockerignore`)

### Mandatory

- Podman CLI
- Buildah (for advanced builds)
- Podman Compose (or docker-compose with podman socket)
- Hadolint (Containerfile linter)
- Trivy/Grype (security scanning)
- SBOM tools (syft)
- Cosign for signatures

### Forbidden

- Embedding secrets in images
- Running containers with `--privileged` without justification
- `latest` floating tags in production
- Copying secrets into image layers
- Running as root user when rootless is possible
- Assuming Docker daemon is available

### Execution Steps

1. Author a minimal, multi-stage Containerfile with deterministic builds
2. Implement `.containerignore` and order layers for cache effectiveness
3. Enforce least-privilege (rootless mode, non-root USER, read-only FS)
4. Pin image digests/versions; scan image; attach SBOM and provenance
5. Define runtime healthchecks and resource limits; externalize secrets
6. Use Podman Compose for dev; use Quadlet/systemd for production services

### Output Format

Deterministic Containerfile(s) and Compose files with:
- Explicit versions
- Comments where non-obvious
- Validated by linters/scanners
- Multi-stage builds
- Rootless-compatible design

### Validation

**Pre-Task-Completion Checks:**
- [ ] Multi-stage Containerfile
- [ ] Base images pinned
- [ ] Non-root USER specified
- [ ] .containerignore configured
- [ ] Layers optimized for caching
- [ ] HEALTHCHECK defined
- [ ] Security scan passing
- [ ] Rootless compatibility verified

**Success Criteria:**
- Build with Podman succeeds
- Image size optimized
- Hadolint passes with no errors
- Vulnerability scan clean or acceptable
- Container runs rootless as non-root
- Healthcheck defined and working
- Digest pinning verified
- SBOM generated

### Design Principles

- **Always:** Use multi-stage builds; choose slim, LTS base images
- **Always:** Add a `.containerignore` to keep contexts tiny; avoid copying VCS/venv/node_modules
- **Always:** Run rootless by default; add non-root USER; drop Linux capabilities
- **Always:** Pin base images and packages; avoid `latest`; prefer digest pinning for prod
- **Always:** Structure layers to maximize caching; separate dependency installation from source copy
- **Requirement:** Generate SBOM and sign images; store attestations in registry
- **Requirement:** Provide a `HEALTHCHECK`; avoid long `CMD` shell strings; use JSON exec form
- **Rule:** Prefer distroless/alpine only when appropriate; verify glibc/musl compatibility
- **Avoid:** COPY-ing secrets; baking envs into image; using `--privileged` containers

### Post-Execution Checklist

- [ ] Multi-stage Containerfile implemented
- [ ] Base images pinned to specific versions/digests
- [ ] Non-root USER specified in Containerfile
- [ ] .containerignore configured and tested
- [ ] Layers optimized for caching
- [ ] HEALTHCHECK defined
- [ ] Security scan passing (hadolint, trivy)
- [ ] SBOM generated
- [ ] Image signed with cosign
- [ ] Podman Compose configured for development
- [ ] Quadlet unit files created for production (if using systemd)
- [ ] Secrets externalized (not in image)
- [ ] Resource limits defined
- [ ] Container runs successfully rootless

## Anti-Patterns and Common Mistakes

### Pattern 1: Assuming Docker Daemon Availability

**Problem:**
Scripts or CI pipelines that assume `docker.sock` or Docker daemon is running.

**Why It Fails:**
Podman is daemonless - there is no background service. Commands run directly as user processes.

**Correct Pattern:**
```bash
# BAD: Assumes Docker daemon
docker info  # May fail if Docker not installed

# GOOD: Use Podman directly (daemonless)
podman info  # Works without any daemon

# GOOD: For Docker-compatible tooling, use podman socket
systemctl --user start podman.socket
export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock
```

### Pattern 2: Running as Root When Rootless Works

**Problem:**
Using `sudo podman` or running as root when the workload supports rootless.

**Why It Fails:**
Loses security benefits of user namespaces; increases attack surface; violates least-privilege.

**Correct Pattern:**
```bash
# BAD: Running as root unnecessarily
sudo podman run -d nginx

# GOOD: Run rootless (default)
podman run -d nginx

# GOOD: If port <1024 needed, use port mapping
podman run -d -p 8080:80 nginx  # Map to unprivileged port

# GOOD: Or configure sysctl for rootless low ports
echo "net.ipv4.ip_unprivileged_port_start=80" | sudo tee /etc/sysctl.d/podman-ports.conf
```

> **Investigation Required**
> When applying this rule:
> 1. **Read existing Containerfile BEFORE suggesting changes** - Check current structure, stages
> 2. **Verify rootless compatibility** - Check if workload requires privileged operations
> 3. **Check for Docker-specific syntax** - Some Dockerfile features may differ
> 4. **Verify pod requirements** - Determine if multi-container pods are needed
> 5. **Test build and run** - Verify changes don't break builds or runtime
>
> **Anti-Pattern:**
> "Adding rootless config... (without checking if workload supports it)"
> "Using podman-compose... (without verifying it's installed)"
>
> **Correct Pattern:**
> "Let me check your current Containerfile first."
> [reads Containerfile, checks base image, reviews layers]
> "I see you're using debian:12. Adding multi-stage build with rootless support..."

## Output Format Examples

```dockerfile
# Containerfile - Multi-stage build following security best practices

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

# Switch to non-root user (UID for rootless compatibility)
USER 1000:1000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port and run
EXPOSE 8000
CMD ["python", "app.py"]
```

```bash
# Validation with Podman
podman build --no-cache -t myapp:latest .
podman run --rm myapp:latest python -c "print('Container validation passed')"

# Verify rootless execution
podman run --rm myapp:latest id  # Should show non-root UID
```

## Podman-Specific Patterns

### Rootless Container Execution

```bash
# Default: Run rootless (no sudo needed)
podman run -d --name myapp -p 8080:8000 myapp:latest

# Check rootless status
podman info --format '{{.Host.Security.Rootless}}'  # Should be true

# User namespace mapping (automatic in rootless)
podman unshare cat /proc/self/uid_map
```

### Pod-Based Deployments (Kubernetes-Style)

```bash
# Create a pod (groups containers sharing network/IPC)
podman pod create --name mypod -p 8080:80

# Add containers to pod
podman run -d --pod mypod --name web nginx:alpine
podman run -d --pod mypod --name api myapp:latest

# Containers in pod share localhost
# web can reach api at localhost:8000

# Generate Kubernetes YAML from pod
podman generate kube mypod > mypod.yaml
```

### Building with Buildah (Advanced)

```bash
# Buildah for fine-grained control
buildah from python:3.12-slim
buildah run python:3.12-slim -- pip install flask
buildah config --user 1000:1000 python:3.12-slim
buildah commit python:3.12-slim myapp:latest

# Build from Containerfile
buildah bud -t myapp:latest .

# Build without cache
buildah bud --no-cache -t myapp:latest .
```

### Quadlet: Systemd Integration (Production)

```ini
# ~/.config/containers/systemd/myapp.container
[Unit]
Description=My Application Container

[Container]
Image=myapp:latest
PublishPort=8080:8000
Volume=/data:/app/data:Z
Environment=APP_ENV=production

[Service]
Restart=always

[Install]
WantedBy=default.target
```

```bash
# Reload and start
systemctl --user daemon-reload
systemctl --user start myapp.service
systemctl --user enable myapp.service

# Check status
systemctl --user status myapp.service
```

### Podman Compose

```yaml
# podman-compose.yml
version: "3"
services:
  web:
    build: .
    ports:
      - "8080:8000"
    volumes:
      - ./data:/app/data:Z  # :Z for SELinux relabeling
    environment:
      - APP_ENV=development
    user: "1000:1000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

```bash
# Using podman-compose
podman-compose up -d
podman-compose logs -f
podman-compose down

# Or use docker-compose with Podman socket
systemctl --user start podman.socket
export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock
docker-compose up -d
```

### Example: .containerignore (Same as .dockerignore)

```
# VCS & metadata
.git
.gitignore
.github/

# Python
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Node/Frontend
node_modules/
dist/
build/

# Secrets & env (never bake into image)
.env
.env.*
*.pem
*.key

# Podman/Container specific
*.container
*.pod
```

## Build Performance and Caching

- **Rule:** Order layers: dependencies first, app code last.
- **Rule:** Use cache mounts for pip/npm: `--mount=type=cache,target=/root/.cache/pip`
- **Rule:** Use `--layers` flag for layer caching in CI.
- **Requirement:** Pin versions; rely on lock files (`uv.lock`, `poetry.lock`, `package-lock.json`).
- **Consider:** Produce SBOM: `podman build --sbom=true` or `syft packages`.

## Security and Least Privilege

- **Mandatory:** Run rootless by default; only use root mode when absolutely required.
- **Mandatory:** Set `USER` to non-root UID/GID (use numeric for portability).
- **Mandatory:** Drop capabilities and use read-only FS when possible:
  - `--cap-drop=ALL --read-only --tmpfs /tmp` at runtime.
- **Requirement:** Keep base images up-to-date; rebuild regularly.
- **Requirement:** Scan images in CI (Trivy, Grype); fail on critical CVEs.
- **Rule:** SELinux: Use `:Z` or `:z` volume suffixes for proper labeling.
- **Avoid:** Exposing SSH or adding debug tools in prod images.

## Supply Chain Integrity

- **Requirement:** Pin images by digest in prod deployments.
- **Requirement:** Generate SBOM and attach provenance.
- **Rule:** Sign images with cosign; enforce signature verification in deployment.
- **Consider:** Use private registries; restrict pull from trusted sources only.

## Podman vs Docker Differences

**Architecture:**
- Docker: Daemon-based (requires dockerd service)
- Podman: Daemonless (runs as user process)

**Default User:**
- Docker: Root
- Podman: Rootless

**Build Tool:**
- Docker: `docker build`
- Podman: `podman build` or `buildah`

**Compose:**
- Docker: `docker-compose`
- Podman: `podman-compose`

**Systemd Integration:**
- Docker: Limited
- Podman: Native (Quadlet)

**Pod Support:**
- Docker: No native support
- Podman: Kubernetes-style pods

**Socket Path:**
- Docker: `/var/run/docker.sock`
- Podman: `$XDG_RUNTIME_DIR/podman/podman.sock`

## Runtime and Orchestration

- **Requirement:** Provide `HEALTHCHECK` in image or orchestrator.
- **Rule:** Configure resource limits (`--memory`, `--cpus`), ulimits, and log drivers.
- **Rule:** Externalize configuration via env and mounted secrets; never bake secrets.
- **Consider:** Readiness/liveness probes, graceful shutdown, and PID 1 handling.
- **Prefer:** Quadlet for systemd-managed containers in production over manual `podman run`.

## CI/CD and Testing

- **Rule:** Lint Containerfile with Hadolint; scan image on each build.
- **Rule:** Cache layers in CI with `--layers` flag.
- **Consider:** Smoke tests using Testcontainers or `podman run` in CI.
- **Note:** Most Docker CI patterns work with Podman; set `DOCKER_HOST` to Podman socket if needed.
