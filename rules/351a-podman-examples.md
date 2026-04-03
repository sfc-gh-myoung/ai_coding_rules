# Podman Output Format Examples

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-25
**Keywords:** Podman examples, Containerfile example, buildah example, quadlet example, podman build script
**TokenBudget:** ~1750
**ContextTier:** Low
**Depends:** 351-podman-core.md

## Scope

**What This Rule Covers:**
Complete, production-ready output examples for Podman container workflows including Buildah multi-stage builds, Containerfile patterns, Quadlet unit files, and build/validate/deploy scripts.

**When to Load This Rule:**
- Generating complete Containerfile or Buildah script output
- Creating Quadlet unit files for systemd integration
- Building deploy scripts with security validation
- Reference implementations for 351-podman-core.md patterns

## References

### Dependencies

**Must Load First:**
- **351-podman-core.md** - Parent rule with patterns and requirements

## Contract

### Inputs and Prerequisites

- Parent rule 351-podman-core.md loaded for patterns and requirements
- Target project with source code and dependency files

### Mandatory

- Adapt all placeholder values (image names, ports, paths) to project requirements
- Validate output against 351-podman-core.md checklist
- All images use versioned tags (no `:latest`)

### Post-Execution Checklist

- [ ] Examples adapted to project requirements
- [ ] Build script tested successfully
- [ ] Quadlet unit generates valid systemd service
- [ ] SBOM generated for production images

### Forbidden

- Using `:latest` tags in any example output
- Copying examples without adapting project-specific values

### Execution Steps

1. Select appropriate example based on target workflow
2. Adapt example values (image names, ports, paths) to project requirements
3. Validate output against 351-podman-core.md checklist

### Validation

**Pre-Task-Completion Checks:**
- [ ] All placeholder values adapted to project
- [ ] No `:latest` tags in output
- [ ] SBOM generation included in build scripts
- [ ] Quadlet units have correct file extension (`.container`)

**Success Criteria:**
- Examples pass Hadolint linting
- Build scripts execute without errors
- Quadlet units generate valid systemd services
- All images use versioned tags (no `:latest`)

### Output Format

### Buildah Multi-Stage Workflow (Podman-Specific)

```bash
#!/bin/bash
# build.sh - Buildah multi-stage build with fine-grained control
set -euo pipefail

# Stage 1: Build in a working container
builder=$(buildah from python:3.12-slim@sha256:specific-digest)
buildah run "$builder" -- groupadd -r appuser --gid=1000
buildah run "$builder" -- useradd -r -g appuser --uid=1000 --home=/app appuser
buildah config --workingdir /app "$builder"
buildah copy "$builder" requirements.txt /app/requirements.txt
buildah run "$builder" -- pip install --no-cache-dir -r /app/requirements.txt
builder_mount=$(buildah mount "$builder")

# Stage 2: Minimal runtime container
runtime=$(buildah from python:3.12-slim@sha256:specific-digest)
buildah copy "$runtime" "$builder_mount/etc/passwd" /etc/passwd
buildah copy "$runtime" "$builder_mount/etc/group" /etc/group
buildah copy --chown 1000:1000 "$runtime" "$builder_mount/app" /app
buildah copy --chown 1000:1000 "$runtime" ./src /app/src

# Configure runtime (numeric UID for rootless compatibility)
buildah config --user 1000:1000 "$runtime"
buildah config --workingdir /app "$runtime"
buildah config --port 8000 "$runtime"
buildah config --cmd '["python", "app.py"]' "$runtime"
buildah config --healthcheck-command 'CMD python -c "import urllib.request; urllib.request.urlopen(\"http://localhost:8000/health\")"' "$runtime"
buildah config --healthcheck-interval 30s --healthcheck-timeout 3s --healthcheck-start-period 5s "$runtime"

# Commit and clean up
buildah commit "$runtime" "myapp:v${VERSION:-1.0.0}"
buildah rm "$builder" "$runtime"

# Generate SBOM and sign
syft packages myapp:v${VERSION:-1.0.0} -o spdx-json > myapp-sbom.json
```

### Containerfile with Podman-Specific Features

```dockerfile
# Containerfile - Podman rootless build with Quadlet integration
FROM python:3.12-slim@sha256:specific-digest AS builder

RUN groupadd -r appuser --gid=1000 && \
    useradd -r -g appuser --uid=1000 --home=/app appuser
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim@sha256:specific-digest
COPY --from=builder /etc/passwd /etc/group /etc/
WORKDIR /app
COPY --from=builder --chown=1000:1000 /app /app
COPY --chown=1000:1000 . .

# Numeric UID/GID required for rootless compatibility across hosts
USER 1000:1000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

EXPOSE 8000
CMD ["python", "app.py"]
```

### Quadlet Unit File (Production)

```ini
# ~/.config/containers/systemd/myapp.container (Quadlet unit for production)
[Unit]
Description=My Application Container

[Container]
Image=myapp:v1.2.3
PublishPort=8080:8000
Volume=/data:/app/data:Z
Environment=APP_ENV=production
ReadOnly=true
DropCapability=ALL
UserNS=auto

[Service]
Restart=always

[Install]
WantedBy=default.target
```

### Build, Validate, and Deploy Script

```bash
# Build, validate, and deploy with Podman
podman build --layers -t myapp:v1.0.0 .
podman run --rm myapp:v1.0.0 id  # Verify non-root UID
podman run --rm --cap-drop=ALL --read-only --tmpfs /tmp myapp:v1.0.0 python -c "print('Validation passed')"

# Deploy via Quadlet
systemctl --user daemon-reload
systemctl --user start myapp.service
```

## Anti-Patterns and Common Mistakes

### Pattern 1: Using Examples Without Adapting Values

**Problem:** Copy-pasting example values (port 8000, image name `myapp`) without adapting to project.

**Why It Fails:** Port conflicts, image name collisions, incorrect paths.

**Correct Pattern:**
```bash
podman build --layers -t myproject:v2.1.0 .
podman run -d --name myproject -p 9090:8080 myproject:v2.1.0
```

### Pattern 2: Missing SBOM Generation in Build Scripts

**Problem:** Omitting SBOM generation step from build workflows.

**Why It Fails:** Violates supply chain integrity requirements in 351-podman-core.md; production images lack provenance.

**Correct Pattern:**
```bash
buildah commit "$runtime" "myapp:v${VERSION:-1.0.0}"
syft packages myapp:v${VERSION:-1.0.0} -o spdx-json > myapp-sbom.json
cosign sign myapp:v${VERSION:-1.0.0}
```
