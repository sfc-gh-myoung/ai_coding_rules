---
schema_version: v4.0
rule_version: v3.0.0
description: "Grounded Podman/Buildah/Quadlet workflow output with real dependency artifacts, scoped lifecycle and honest validation."
last_updated: 2026-10-07
keywords:
  - kw:Buildah multi-stage
  - kw:Quadlet systemd
  - kw:rootless numeric UID
  - kw:SBOM generation script
  - kw:Containerfile healthcheck
  - kw:versioned image tags
  - kw:ini
token_budget: ~850
context_tier: Low
depends:
  required:
    - 351-podman-core.md  # Parent rule with patterns and requirements
---
# Podman Workflow Output Patterns

## Scope

**What This Rule Covers:**
Project-specific Buildah stages, runtime dependency copying, Quadlet configuration and separate build/scan/deploy evidence.

**When to Load This Rule:**
When producing Containerfile/Buildah/Quadlet workflows; parent owns security/rootless/lifecycle contract.

## Contract

### Inputs and Prerequisites

- Read actual source/manifests/image identities/entrypoint and installed Podman/Buildah/systemd capabilities.
- Approved image/registry/volume/port/user/service scope and build/scan/publication authority.

### Mandatory

- Adapt real names/paths/ports/versions and use actual verified digests, not sha256:specific-digest. Prose placeholders are not executable production-ready examples or proof a workflow ran.
- Multi-stage dependencies must reach runtime: pip global site-packages isn't copied by /app-only transfer. Copy compatible venv/artifacts at actual paths, including project source/entrypoint/runtime libraries.
- Buildah handle/mount lifecycle tracks returned builder/runtime containers with cleanup on failure; unmount before removal when required. Do not copy broad passwd/group files as a substitute for explicit intended user/permissions.
- Numeric user/rootless mappings/read-only filesystem and owned volume labeling match actual access. Quadlet PublishPort binds explicitly approved interfaces; bare 8080:8000 can expose all host interfaces.
- Validate Quadlet keys/unit extension/image/search path/[Install] against installed generator and startup policy. UserNS=auto can alter mappings; generated service enable behavior is not ordinary permanent unit enable.
- Healthcheck invokes installed command with bounded timeout and fails on unhealthy status. Synthetic print validation is not entrypoint/dependency/network/probe evidence.
- Build, test, scan, SBOM, sign, push, and systemd start are separate steps/permissions; SBOM creation does not sign. Registry attestations may publish proprietary metadata and need destination approval.
- A script must fail on validation errors, preserve image/attempt IDs and clean only owned disposable resources. No fallback image versions that conceal missing inputs or unreviewed service start/teardown.
- Prefer concise correct distinct examples only if concrete verified inputs make them useful; otherwise provide required workflow/fields in prose rather than broken placeholder code.

### Execution Steps

1. Read target inputs and select actual build/runtime/Quadlet operation with permitted scope.
2. Produce minimal correct project-specific configuration/script and explicit validation/cleanup stages.
3. Run available lint/generator and approved real build/health/scan checks; record outcomes.
4. Report output paths/image identities and unrun sign/push/deploy gates; never claim production-ready from syntax alone.

### Validation

- Artifacts/dependencies/users/ports/volumes complete and correct under real runtime.
- Generator/build/health/scan/SBOM/signature outcomes separately observed or explicitly unverified.
- No unapproved external publication/service activation or broader cleanup; source/volume state preserved.

## References

- [Buildah manuals](https://github.com/containers/buildah/tree/main/docs)
- [Podman build](https://docs.podman.io/en/latest/markdown/podman-build.1.html)
- [Quadlet unit specification](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html)
- [Syft SBOM](https://github.com/anchore/syft)
