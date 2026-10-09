---
schema_version: v4.0
rule_version: v3.0.0
description: "Podman/Buildah rootless identity, safe volume/network authority, reproducible images and tested Quadlet lifecycle."
last_updated: 2026-10-07
keywords:
  - kw:rootless containers
  - kw:Containerfile authoring
  - kw:Quadlet systemd
  - kw:daemonless architecture
  - kw:pod orchestration
  - kw:Buildah image building
  - kw:SELinux volume labeling
token_budget: ~1250
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
    - 202-markup-config-validation.md  # Configuration validation patterns
  optional:
    - 351a-podman-examples.md  # Complete output format examples
    - 350-docker-core.md  # Docker-specific patterns (Podman is largely compatible)
    - 200-python-core.md  # Python-specific container patterns
---
# Podman Core

## Scope

**What This Rule Covers:**
Existing Podman/Buildah/Compose/machine context, rootless namespace/access, Containerfile artifacts, pods and systemd Quadlet.

**When to Load This Rule:**
When building/running Podman containers or systemd integration; read `351a-podman-examples.md` for workflow details and Docker companion only for shared image patterns.

## Contract

### Inputs and Prerequisites

- Installed Podman/Buildah/Quadlet version/platform/machine/runtime context and existing images/Containerfiles/ignore/units/volumes.
- Target UID/GID/sub-ID/cgroups/network/SELinux requirements, registry/data authority and approved build/run/start/cleanup scope.

### Mandatory

- Inspect actual runtime/version/rootless state, not assume daemonless means no VM/server/socket on macOS/Windows/remote. Docker compatibility needs verified provider/API/DOCKER_HOST; enabling sockets/machines/services is a mutation with authority.
- Rootless host execution and non-root image USER are distinct. Verify user namespace mappings, file access and process UID; numeric USER useful but not required for all hosts. sudo changes ownership/image store and needs explicit necessity; a ROOT/PRIVILEGED comment isn't approval.
- Never prescribe host sysctl/subuid/subgid/usermod/linger/cgroup/SELinux changes or privileged containers for generic recovery. Diagnose first and choose least-privileged approved alternative; keep-id isn't a universal cure for all rootless limitations.
- Build reproducible compatible images with actual base identities/locks, minimal runtime artifacts and correct dependency paths. Read registry/Containerfile before changes; no invented hashes or installed dependencies omitted from final image.
- .containerignore/.dockerignore semantics depend on builder; keep secrets/private source out of context/layers and use approved mounts/injection. No arbitrary remote installer or missing-scanner installation by implication.
- Buildah operations reference the working-container handle returned by from, not an image tag as if it were the handle. Track mounts/containers and clean only owned ones in finally; mount/unshare behavior depends on rootless/platform.
- SELinux :Z private versus :z shared relabel affects host files and other consumers; inspect ownership/labels/volume scope and obtain approval. Never relabel broad system/shared directories automatically or disable labeling for convenience.
- Pods share actual configured namespaces and port mappings; inspect collisions/security and workload ownership. Creating a pod, exposing services or generating/publishing Kubernetes data are separate authorized operations.
- Prefer current Quadlet for systemd-managed services when supported. Validate actual unit keys/search paths/generated names; generated services use [Install] behavior from Quadlet, not blindly systemctl enable ephemeral units. User daemon-reload/start/linger are explicit lifecycle mutations.
- Read-only/capability/resource/probe/signal configuration matches application needs and actual cgroup/platform enforcement. Healthchecks use available tooling and real status; no fake print smoke or universal image size target.
- Compose provider/runtime and supported schema differ; depends_on isn't automatic readiness. Verify external binds/secrets/volumes and no production debug tools exposed unasked.
- Use approved scan/SBOM/provenance/signature/consumer verification policy and private registry boundary. Actual podman build SBOM flags/options differ from BuildKit; inspect help instead of assuming --sbom=true parity.
- Never run global prune --all/--volumes/--force as default CI/weekly cleanup or uncertain recovery. Preserve persistent/unrelated resources and beforeimages; identify owned disposable IDs and approval before deletion.
- Test actual rootless build/run/application/probes/Quadlet generator within permitted scope. No claimed compatibility, security scan or live service success from static syntax alone.

### Execution Steps

1. Read existing container/runtime/units/volume context and establish actual support/authority.
2. Implement minimal reproducible image and rootless-compatible access/network/lifecycle configuration.
3. Validate available syntax and approved build/runtime/Quadlet/scan gates, observing ownership/cleanup.
4. Report exact handles/image/config/rootless evidence and remaining platform/systemd/security gaps.

### Validation

- Actual image dependencies, rootless/UID namespace and volume/network access correct.
- Quadlet/provider/probe/resource/signal behavior supported and tested or marked unverified.
- Secrets/registry/privileged/host changes authorized; SBOM/signature/scan evidence real.
- No broad prune/relabel/teardown or unexpected systemd startup; original resources preserved.

## References

- [Podman build](https://docs.podman.io/en/latest/markdown/podman-build.1.html)
- [Podman run](https://docs.podman.io/en/latest/markdown/podman-run.1.html)
- [Quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html)
- [Rootless tutorial](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md)
- [Buildah](https://buildah.io/)
