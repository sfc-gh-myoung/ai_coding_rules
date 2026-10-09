---
schema_version: v4.0
rule_version: v5.0.0
description: "Reproducible container builds with complete runtime artifacts, scoped secrets/resources and verified supply-chain evidence."
last_updated: 2026-10-07
keywords:
  - kw:multi-stage builds
  - kw:image digest pinning
  - kw:non-root container user
  - kw:layer caching optimization
  - kw:SBOM generation
  - kw:BuildKit mount cache
token_budget: ~1250
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
    - 202-markup-config-validation.md  # Configuration validation patterns
  optional:
    - 200-python-core.md  # Python-specific Docker patterns
    - 203-python-project-setup.md  # Python project structure for containers
---
# Docker Core

## Scope

**What This Rule Covers:**
Existing image/build context, compatibility/layers, complete multi-stage artifacts, runtime privilege/health and approved scan/SBOM/signature evidence.

**When to Load This Rule:**
When authoring/reviewing Dockerfiles/build/Compose/container CI; read language or Podman companions for actual runtime-specific needs.

## Contract

### Inputs and Prerequisites

- Existing Dockerfile/context/ignore/lock/CI/runtime, installed builder/frontend/Compose capabilities and image/platform architecture.
- Approved base/dependency/image identities, registry/data boundary, application health/resource requirements and build/run/push scope.

### Mandatory

- Read current configuration before changing base/build stages. Match established tooling; BuildKit feature/default support varies by release/driver, not presumed from Engine20.10 alone. Missing linter/scanner is an unverified gate, not authority to curl-install tools.
- Pin reviewed base/runtime/dependency versions or actual digests per policy; mutable version tags aren't immutable. Never invent a placeholder hash as executable evidence. Evaluate glibc/musl/architecture/dynamic library/CA compatibility before Alpine/distroless switches.
- Use multi-stage when it isolates build tools/artifacts; don't add it mechanically to an already minimal runtime. Copy actual dependencies/binaries/venv from their installation paths with compatible interpreter/ABI, not only /app when pip installed elsewhere.
- Keep dependency manifest before changing source for useful caching; install required project package/source at the correct stage. Cache mounts are builder/version-specific; don't disable package cache then claim mount benefit. Locked install/build actually reproducible, not a fallback silently dropping lock semantics.
- Bound build context with .dockerignore and check required source isn't omitted. No secrets/private keys/.env/VCS/customer payloads in context/layers; deleting later doesn't remove earlier layers. Build args/env aren't a secret store; approved ephemeral secret mounts/runtime secret injection only.
- Dedicated non-root USER/permissions, least capabilities and read-only filesystem with approved writable volumes/tmpfs. Rootless daemon and non-root container user are distinct. Privileged/device/host/socket access needs concrete necessity, threat review and explicit approval; a comment doesn't grant authority.
- Keep proprietary images/metadata/SBOM within approved private destinations. Builds can contact package registries, scanners can download databases/upload findings, and signing/pushing can publish data; review each boundary before execution.
- Use exec-form command/entrypoint where appropriate for PID1/signal handling, graceful termination and cleanup. Healthchecks must fail on actual unhealthy/error status and use installed tools/timeouts; a requests.get without raise_for_status can falsely pass on HTTP500.
- Configure application liveness/readiness and platform probes deliberately; a Docker HEALTHCHECK isn't automatically consumed by every orchestrator. EXPOSE doesn't publish a port; actual bind/PublishPort and authenticated network scope require approval.
- Size CPU/memory/ulimits/workers/log retention from workload evidence and runtime enforcement; no universal 200MB/50MB image or fixed resource target. Development reload/mounts/ports separate from production; Compose depends_on readiness and restart behavior tested.
- Run actual lint/build/runtime health/start/shutdown and approved vulnerability/SBOM/provenance/signing verification gates. SBOM isn't a signature and signing alone doesn't enforce consumer verification; define acceptance/exceptions/rotation/current base patch cadence under policy.
- Diagnose failed layers/registry/health/resources from logs/config first. Never automatically docker system/builder prune, force volume removal, privileged QEMU registration, sysctl, daemon config or security bypass. Cleanup only verified task-owned disposable objects under approval.
- Capture original image/config/grants/persistent-volume identities and uncertain outcomes before repair. A print('validation passed') inside container isn't application smoke; test real entrypoint/import/dependencies/health behavior.

### Execution Steps

1. Inspect current context/image/runtime/CI and authority; define reproducible artifacts/security/resource targets.
2. Implement minimal compatible layers/artifact copy and non-root secret/probe/signal configuration.
3. Run available local lint and approved build/runtime/scan/SBOM checks with durable outcomes.
4. Review errors/owned recovery and report exact image/config/evidence plus unrun publication/platform gates.

### Validation

- Runtime contains actual compatible dependencies/source and starts correctly; pins/locks/context verified.
- No secrets/layer leaks or unapproved public bind/privilege/registry transfer; resources/probes/signals work.
- Actual scan/SBOM/signature/provenance expectations met or gaps explicit, no fake smoke/hash.
- Original volumes/unrelated images preserved and cleanup restricted to authorized owned scope.

## References

- [Docker build best practices](https://docs.docker.com/build/building/best-practices/)
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Build secrets](https://docs.docker.com/build/building/secrets/)
- [Build attestations](https://docs.docker.com/build/metadata/attestations/)
- [Docker security](https://docs.docker.com/engine/security/)
