---
schema_version: v4.0
rule_version: v3.0.0
description: "Where short-life, in-progress, or scratch project assets live in the repository. Establishes .workbench/ at the repo root as the single canonical home for workbench artifacts so long-lived"
last_updated: 2026-10-06
keywords:
  - kw:.workbench/ folder
  - kw:short-life assets
  - kw:promotion protocol
  - kw:filesystem hygiene
  - kw:workbench mirroring
  - kw:gitignore workbench
token_budget: ~800
context_tier: Low
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns
  optional:
    - 800-project-changelog.md  # Changelog format for landed workbench work
    - 803-project-git-workflow.md  # Commit conventions when promoting assets out of `.workbench/`
    - 804-project-documentation.md  # `docs/` folder organization (long-lived docs)
---
# Workbench Folder Policy: Short-Life Project Assets

## Scope

**What This Rule Covers:**
Repository-local scratch/evidence assets, canonical workbench location and deliberate promotion to maintained deliverables.

**When to Load This Rule:**
When placing diagnostic scripts, measurement snapshots, exploratory reports, temporary plans or promoting evidence into project documentation. Preserve explicitly established plan/evidence locations rather than relocating an approved workflow.

## Contract

### Inputs and Prerequisites

- Verified repository root, existing ignore policy, asset lifetime and current consumers.
- User/project scope for persistence, immutable evidence and authorized promotion/publication.

### Mandatory

- Put new short-life assets in root `.workbench/`, using analysis/benchmarks/plans/scripts subfolders as needed. Keep maintained source/docs/test directories focused on deliverables.
- Workbench is ignored by default; do not force-add it or promote assets without deliberate approval. Canonical maintained scripts and approved committed plans belong in their established long-lived homes.
- Identify each asset's eventual promotion criterion or disposal policy. Immutable run/baseline evidence must never be deleted/rewritten merely because it is temporary.
- Keep one canonical identity per asset; intentional immutable versions/epochs are distinct identities, not duplicate drift.
- Promotion updates consumers/references together in the authorized landing change. Preserve evidence integrity and avoid replacing existing target content.
- Production runtime/tests must not require ignored ephemeral paths. Cite transient evidence by title in permanent source or promote the needed artifact before using a stable path.
- Do not create ignored workbench-like subdirectories inside maintained docs as a substitute, or symlink a maintained doc to an ephemeral workbench asset.
- Existing approved plan locations and user preservation constraints take precedence over generic cleanup advice; do not move or delete them unasked.

### Execution Steps

1. Inspect asset purpose, repository root, current ignore policy and established plan/evidence homes.
2. Create scratch assets under the appropriate workbench folder, with scoped references between workbench siblings.
3. Validate contents and note promotion/disposal criterion; retain unsuccessful/interrupted immutable records where required.
4. When approved as a deliverable, promote to the canonical maintained home, update references and document rationale in the authorized change.
5. Remove superseded scratch duplicates only when deletion is authorized and no immutable evidence/consumer depends on them.

### Validation

- Scratch placement/ignore policy verified, no unrelated long-lived directory pollution.
- Maintained runtime/tests have no dependency on ignored workbench paths.
- Promotion preserves evidence, updates consumers and leaves one canonical deliverable identity.
- Immutable versions/failed runs retained; no automatic force-add, commit, move or deletion.
- Existing approved plan/evidence location and user instructions respected.

## References

- [Git ignore documentation](https://git-scm.com/docs/gitignore)
- `804-project-documentation.md` for maintained documentation organization.
- `803-project-git-workflow.md` for separately authorized landing changes.
