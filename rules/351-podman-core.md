# Podman Core

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2026-03-25
**Keywords:** Podman, Containerfile, containers, rootless containers, buildah, podman-compose, pods, daemonless, systemd, quadlet, image optimization, non-root, healthcheck, security scanning, SBOM
**TokenBudget:** ~4350
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
- **351a-podman-examples.md** - Complete output format examples
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

- Podman 4.0+ required (4.5+ recommended for improved rootless; 5.0+ for manifest improvements). Check: `podman --version`
- Buildah for advanced image building (optional)
- Access to base images/registries
- Project source with `.containerignore` (or `.dockerignore`)
- **Tools:** Podman CLI, Buildah, Podman Compose (or docker-compose with podman socket), Hadolint (Containerfile linter), Trivy/Grype (security scanning), syft (SBOM generation), cosign (image signing)

### Mandatory

- MUST run containers rootless by default; root mode requires `# ROOT: <specific-technical-reason>` comment in Containerfile. Acceptable: host network access, kernel module loading, cgroup/systemd manipulation. Not acceptable: "needed for app," "legacy," "easier."
- MUST use Quadlet for systemd-managed containers in production
- MUST scan images with Trivy/Grype before deployment; fail on critical or high CVEs
- MUST NOT embed secrets in images or image layers
- MUST NOT use `--privileged` without `# PRIVILEGED: <specific-technical-reason>` comment. Acceptable: host network namespace, kernel module loading, cgroup manipulation.
- MUST NOT use `latest` floating tags in production
- MUST NOT run as root user when rootless is possible
- MUST NOT assume Docker daemon is available

### Forbidden

See MUST NOT items in Mandatory above. Additionally:
- Exposing SSH or adding debug tools in production images

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
- Image size optimized (<200MB for Python, <50MB for Go/distroless, <100MB for Node.js)
- Hadolint passes with no errors
- Vulnerability scan clean (no critical or high CVEs; medium CVEs documented with justification)
- Container runs rootless as non-root
- Healthcheck defined and working
- Digest pinning verified
- SBOM generated

### Design Principles

- **MUST:** Use multi-stage builds; choose slim, LTS base images
- **MUST:** Add a `.containerignore` to keep contexts tiny; avoid copying VCS/venv/node_modules
- **MUST:** Run rootless by default; add non-root USER; drop Linux capabilities
- **MUST:** Pin base images and packages; avoid `latest`; prefer digest pinning for production
- **MUST:** Structure layers to maximize caching; separate dependency installation from source copy
- **MUST:** Generate SBOM and sign images; store attestations in registry
- **MUST:** Provide a `HEALTHCHECK`; avoid long `CMD` shell strings; use JSON exec form
- **SHOULD:** Base image selection decision tree: (1) Static binary with no runtime deps (Go, Rust): use `distroless/static`; (2) JVM app: use `distroless/java`; (3) Needs shell or `apt`/`apk` at runtime: use Alpine or `-slim` variant; (4) Dev container or build stage: use full base image. Always verify glibc vs musl compatibility before choosing Alpine.
- **MUST NOT:** COPY secrets into images; bake envs into image layers; use `--privileged` without `# PRIVILEGED: <reason>` comment

### Post-Execution Checklist

All items from Pre-Task-Completion Checks above, plus:
- [ ] Image signed with cosign
- [ ] Podman Compose configured for development
- [ ] Quadlet unit files created for production (if using systemd)
- [ ] Resource limits defined

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

### Pattern 3: Common Error Recovery

**Rootless Permission Issues:**
```bash
# Check subuid/subgid configuration
grep $(whoami) /etc/subuid /etc/subgid

# If missing, add mappings (requires root)
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $(whoami)

# Reset user namespace after config change
podman system migrate

# Debug namespace mapping
podman unshare cat /proc/self/uid_map
podman unshare cat /proc/self/gid_map
```

**SELinux Label Failures:**
```bash
# BAD: Volume mount fails with "Permission denied" on SELinux systems
podman run -v /data:/app/data myapp

# GOOD: Use :Z (private relabel) for single-container volumes
podman run -v /data:/app/data:Z myapp

# GOOD: Use :z (shared relabel) for volumes shared across containers
podman run -v /shared:/app/shared:z myapp
```

**Registry Authentication Failures:**
```bash
# Diagnose auth issues
podman login --get-login registry.example.com
# Auth config location (rootless): ${XDG_RUNTIME_DIR}/containers/auth.json
# Re-authenticate if needed
podman logout registry.example.com && podman login registry.example.com
```

> **Investigation Required**
> Before applying: (1) read existing Containerfile, (2) verify rootless compatibility, (3) check for Docker-specific syntax, (4) verify pod requirements, (5) test build and run.
>
> **Anti-Pattern:** "Adding rootless config... (without checking if workload supports it)"
> **Correct:** "Let me check your Containerfile first." [reads file, checks base image, reviews layers]

### Output Format Examples

See `351a-podman-examples.md` for complete, production-ready examples including:
- Buildah multi-stage build script with SBOM generation
- Containerfile with rootless, Quadlet, and HEALTHCHECK patterns
- Build, validate, and deploy script with security checks

## Podman-Specific Patterns

### Rootless Container Execution

```bash
# Default: Run rootless (no sudo needed)
podman run -d --name myapp -p 8080:8000 myapp:v1.0.0

# Check rootless status
podman info --format '{{.Host.Security.Rootless}}'  # Should be true

# User namespace mapping (automatic in rootless)
podman unshare cat /proc/self/uid_map
```

**If `Rootless: false` unexpectedly:** Check that Podman is not running as root or via `sudo`. Verify `/etc/subuid` and `/etc/subgid` contain entries for your user. Run `podman system migrate` after modifying sub-ID ranges. If using `machinectl` or `loginctl`, ensure lingering is enabled: `loginctl enable-linger $USER`. For WSL2, ensure the user namespace kernel parameter is set: `sysctl -w kernel.unprivileged_userns_clone=1`.

### Pod-Based Deployments (Kubernetes-Style)

```bash
# Create a pod (groups containers sharing network/IPC)
podman pod create --name mypod -p 8080:80

# Add containers to pod
podman run -d --pod mypod --name web nginx:1.27-alpine
podman run -d --pod mypod --name api myapp:v1.0.0

# Containers in pod share localhost
# web can reach api at localhost:8000

# Generate Kubernetes YAML from pod
podman generate kube mypod > mypod.yaml
```

### Building with Buildah (Advanced)

```bash
# Buildah for fine-grained control
buildah from python:3.12-slim@sha256:a1b2c3...
buildah run python:3.12-slim@sha256:a1b2c3... -- pip install flask
buildah config --user 1000:1000 python:3.12-slim@sha256:a1b2c3...
buildah commit python:3.12-slim@sha256:a1b2c3... myapp:v1.0.0

# Build from Containerfile
buildah bud -t myapp:v1.0.0 .

# Build without cache
buildah bud --no-cache -t myapp:v1.0.0 .
```

### Quadlet: Systemd Integration (Production)

See complete Quadlet unit example in Output Format Examples above. Key commands:

```bash
# Reload and start
systemctl --user daemon-reload
systemctl --user start myapp.service
systemctl --user enable myapp.service

# Check status
systemctl --user status myapp.service
```

#### Quadlet Failure Recovery
- **Unit fails to generate:** Run `/usr/lib/systemd/system-generators/podman-system-generator --dryrun` (system) or `podman-system-generator --user --dryrun` to see parsing errors. Check file syntax, ensure `[Container]` section header is present, and verify file extension is `.container`.
- **Service fails to start:** Run `journalctl --user -u webapp --no-pager -n 50` to check logs. Common causes: image pull failure (check registry auth), volume mount SELinux denial (use `:Z` suffix), port already in use. Fix and re-run `systemctl --user daemon-reload && systemctl --user restart webapp`.
- **Health check failures after start:** Verify health endpoint responds: `podman exec <id> curl -f http://localhost:8080/health`. Check `--start-period` if the application needs warmup time. Increase `HealthInterval` or `HealthRetries` if health checks fail after `start-period` elapses (check with `podman inspect --format '{{.State.Health.Status}}'`).

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
.git
.gitignore
.github/
__pycache__/
*.py[cod]
.venv/
venv/
node_modules/
dist/
.env
.env.*
*.pem
*.key
```

See `350-docker-core.md` for extended `.dockerignore` patterns.

## Build Performance and Caching

- **MUST:** Order layers: dependencies first, app code last.
- **MUST:** Use cache mounts for pip/npm: `--mount=type=cache,target=/root/.cache/pip`
- **SHOULD:** Use `--layers` flag for layer caching in CI.
- **MUST:** Pin versions; rely on lock files (`uv.lock`, `poetry.lock`, `package-lock.json`).
- **MUST:** Generate SBOM for production images using syft (`podman build --sbom=true` or `syft packages`).

### Build Cache Cleanup

Build caches accumulate over time. Clean after each CI pipeline run, or weekly on development machines:

```bash
# View cache usage
podman system df

# Remove dangling (unused) images and build cache
podman system prune --force

# Remove all unused images (not just dangling) and build cache
podman system prune --all --force

# Remove build cache only (Podman ≥ 4.1)
podman buildx prune --force

# In CI: always clean cache after pushing final image
# to avoid disk exhaustion on ephemeral runners
podman system prune --all --force --volumes
```

**Caution:** `--volumes` also removes unused named volumes. Do not use in environments with persistent data volumes.

## Security and Least Privilege

- **MUST:** Run rootless by default; root only for: port binding <1024 without CAP_NET_BIND_SERVICE, system file modification during build. Use `--userns=keep-id` when rootless is insufficient. All other workloads MUST use rootless.
- **MUST:** Set `USER` to non-root UID/GID (use numeric for portability).
- **MUST:** Drop capabilities and use read-only FS unless the application requires runtime file writes (logs, uploads, SQLite). Use `--tmpfs` for temporary write paths:
  - `--cap-drop=ALL --read-only --tmpfs /tmp --tmpfs /var/log` at runtime.
- **MUST:** Keep base images up-to-date; rebuild weekly in CI or within 48 hours of base image CVE advisories.
- **MUST:** Scan images in CI (Trivy, Grype); fail on critical CVEs.
- **MUST:** SELinux: Use `:Z` or `:z` volume suffixes for proper labeling on SELinux-enabled hosts.
- **MUST NOT:** Expose SSH or add debug tools in production images.

## Supply Chain Integrity

- **MUST:** Pin images by digest in production deployments.
- **MUST:** Generate SBOM and attach provenance.
- **MUST:** Sign images with cosign; enforce signature verification in deployment.
- **MUST:** Use private registries for images containing proprietary code; public registries acceptable for open-source base images.

## Podman vs Docker Differences

- **Architecture:** Docker uses daemon (dockerd); Podman is daemonless (user process)
- **Default User:** Docker runs as root; Podman runs rootless
- **Build Tool:** Docker uses `docker build`; Podman uses `podman build` or `buildah`
- **Compose:** Docker uses `docker-compose`; Podman uses `podman-compose`
- **Systemd:** Docker has limited support; Podman has native Quadlet integration
- **Pods:** Docker has no native support; Podman supports Kubernetes-style pods
- **Socket:** Docker at `/var/run/docker.sock`; Podman at `$XDG_RUNTIME_DIR/podman/podman.sock`

## Runtime and Orchestration

- **MUST:** Provide `HEALTHCHECK` in image or orchestrator.
- **MUST:** Configure resource limits (`--memory`, `--cpus`), ulimits, and log drivers.
- **MUST:** Externalize configuration via env and mounted secrets; never bake secrets.
- **SHOULD:** Add readiness/liveness probes when deploying to Kubernetes or Podman pods with health monitoring. Include graceful shutdown handling and PID 1 signal forwarding (use `tini` or exec form CMD).
- **SHOULD:** Use Quadlet for systemd-managed containers in production over manual `podman run`.

## CI/CD and Testing

- **MUST:** Lint Containerfile with Hadolint; scan image on each build.
- **MUST:** Cache layers in CI with `--layers` flag.
- **SHOULD:** Run smoke tests using Testcontainers or `podman run` in CI to validate container starts and responds.
- **Note:** Most Docker CI patterns work with Podman; set `DOCKER_HOST` to Podman socket if needed.
