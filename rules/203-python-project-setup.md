---
schema_version: v4.0
rule_version: v5.0.0
description: "Essential Python project setup and packaging guidance covering package structure, pyproject.toml configuration, dependency management, and build error prevention. Includes __init__.py requirements,"
last_updated: 2026-10-06
keywords:
  - kw:pyproject.toml
  - kw:hatchling build backend
  - kw:uv dependency manager
  - kw:__init__.py package recognition
  - kw:flat layout src layout
  - kw:editable install
token_budget: ~1100
context_tier: High
depends:
  required:
    - 200-python-core.md  # Python foundation patterns
  optional:
    - 201-python-lint-format.md  # Code quality configuration in pyproject.toml
    - 206-python-pytest.md  # Testing configuration
    - 210-python-fastapi-core.md  # FastAPI application patterns
---
# Python Project Setup and Packaging

## Scope

**What This Rule Covers:**
Package/layout/build configuration, project metadata, dependencies, entry points and testing installed artifacts without environment destruction.

**When to Load This Rule:**
When initializing/packaging Python projects or diagnosing build/import/distribution issues.

## Contract

### Inputs and Prerequisites

- Existing pyproject/build backend, package layout, import/distribution names and supported Python/platforms.
- Current manager/lock/environment/test configuration and authorized setup/install scope.

### Mandatory

- Inspect current layout/backend before changing it. Keep flat/src/workspace organization unless a layout migration is requested; module/contributor counts do not dictate architecture.
- Use pyproject metadata/build-system standards and the actual backend's package discovery rules. Hatchling is a choice, not universal dependency or mandatory backend override.
- Regular packages use __init__.py; intentional namespace packages can omit it. Test directories need not be packages. Do not diagnose every missing import as missing __init__.
- Ensure intended package source exists before build/install; configure explicit package paths when discovery needs them. Distribution name and import name can differ; document actual names.
- Keep project/runtime dependencies separate from dev/test/docs groups or user-facing optional extras as appropriate. Use established manager operations/lock policy; manual edits are not categorically forbidden when reviewed/locked correctly.
- Library version ranges and application locks serve different purposes; lock exact deploy/test resolution without forcing every reusable library requirement to one version.
- Use approved isolated editable installs for development and test real wheels/sdists in clean environments for release. No global installs or unrequested package publishing.
- Never clear .venv, replace managers, upgrade dependencies, use alternate mirrors or change proxy settings as a blind setup fix.
- Console scripts point to actual callable imports; __main__ supports module execution only when implemented. Keep parsing separate from business logic, match existing CLI/framework choice.
- Configure actual lint/type/test tools/Python target; do not insert obsolete ty keys or hard-coded py311 support. Build artifact tests verify inclusion of resources and installed imports, not just repository imports.

### Execution Steps

1. Read manifests/locks/backend and inspect package/test/source layout, imports and console entry points.
2. Choose minimal metadata/discovery/dependency changes, preserving supported platforms and existing manager.
3. If initializing, create actual source/regular-package markers or intentional namespace structure before installation.
4. Under setup authorization, resolve/sync intended groups and editable install using the manager; preserve lock consistency and avoid clear/rebuild defaults.
5. Build wheel/sdist, inspect packaged modules/data and run imports/CLI help/tests against installed artifacts in an approved clean environment.
6. Diagnose failures from exact build/import evidence, not guessed package names; update setup docs and report tested versus unverified platforms.

### Validation

- pyproject parses and backend discovery matches real source/layout; regular/namespace package choice intentional.
- Editable development imports and clean installed artifact imports/console scripts tested where authorized.
- Wheel/sdist includes required resources and excludes secrets/scratch assets.
- Dependencies/groups/lock/build versions coherent, no unrequested upgrades/mirror changes/destructive environment clear.
- Tests/lint/types and package support match actual configuration; publishing not performed without explicit approval.

## References

- [Python packaging: pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Python packaging: src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Namespace packages](https://packaging.python.org/en/latest/guides/packaging-namespace-packages/)
- [Hatch build configuration](https://hatch.pypa.io/latest/config/build/)
- [uv projects](https://docs.astral.sh/uv/guides/projects/)
