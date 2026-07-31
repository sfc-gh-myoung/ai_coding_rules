---
schema_version: v3.5
rule_version: v2.1.0
description: "Where short-life, in-progress, or scratch project assets live in the repository. Establishes .workbench/ at the repo root as the single canonical home for workbench artifacts so long-lived"
last_updated: 2026-07-15
keywords:
  - kw:.workbench/ folder
  - kw:short-life assets
  - kw:promotion protocol
  - kw:filesystem hygiene
  - kw:workbench mirroring
  - kw:gitignore workbench
token_budget: ~1950
context_tier: Low
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns
  optional:
    - 800-project-changelog.md  # Changelog format for landed workbench work
    - 803-project-git-workflow.md  # Commit conventions when promoting assets out of `.workbench/`
    - 804-project-documentation.md  # `docs/` folder organization (long-lived docs)
---
# Workbench Folder Policy — Short-Life Project Assets

## Scope

**What This Rule Covers:**
Where short-life, in-progress, or scratch project assets live in the repository. Establishes `.workbench/` at the repo root as the single canonical home for workbench artifacts so long-lived directories (`docs/`, `scripts/`, `rules/`, `skills/`, `src/`, `tests/`, `templates/`) stay a pure signal of committed deliverables.

**Applies To:**

- Baseline scripts scoped to a specific plan (e.g. token-count snapshotters, one-off measurement runners)
- Plan-analyzer, plan-reviewer, or research outputs whose findings have already been folded into a plan or ADR
- In-flight plan files that are not yet ready to land
- Spike-branch measurements and other exploratory artifacts
- Any file whose lifetime is bounded by a single plan or investigation

**Does NOT Apply To:**

- Canonical project scripts (migration runners kept for reproducibility, security-scan pre-commit hooks, CI helpers)
- Committed plans that represent a project deliverable (once a plan lands, it is promoted out of `.workbench/plans/` to `docs/plans/`)
- Frozen baselines that ship as canonical references alongside a batch commit — those are promoted out of `.workbench/benchmarks/` to `docs/benchmarks/` at landing time

**When to Load This Rule:**

- Creating a new baseline script, analyzer output, or in-flight plan
- Considering where to put a diagnostic dump or measurement snapshot
- Auditing the repository for filesystem hygiene
- Promoting a workbench asset into a project deliverable

## References

### External Documentation

_None._

## Contract

### Inputs and Prerequisites

- Repo root writable
- `.gitignore` contains `.workbench/`
- Consumer scripts and skills refer to workbench assets by their `.workbench/…` path, not `docs/…` or `scripts/…`

### Mandatory

- **Location:** All short-life assets live under `.workbench/` at the repo root, mirroring the shape of the long-lived dir they would otherwise pollute (`.workbench/analysis/`, `.workbench/plans/`, `.workbench/benchmarks/`, `.workbench/scripts/`, etc.).
- **Ignored by default:** `.workbench/` is listed in `.gitignore`. Contents are opt-in via `git add -f` only when a deliberate exception is required.
- **Promotion protocol:** When a workbench asset matures into a project deliverable, it is `mv`'d out of `.workbench/` into its long-lived home in the same commit that promotes it. The promotion commit is a `docs(...)`, `feat(...)`, or `chore(...)` Conventional Commit that names the promoted asset.
- **Single-name assets:** Only one canonical name per asset. When a plan is promoted from `.workbench/plans/foo.plan.md` to `docs/plans/foo.plan.md`, the workbench copy is removed — no drift.

### Forbidden

- **Mixed homes:** Do not gitignore workbench-shaped subdirectories inside long-lived dirs (e.g. `docs/analysis/`, `docs/plans/`, `docs/benchmarks/`) as a substitute for `.workbench/`. Long-lived dirs must read as long-lived at the filesystem level, not only at the git-tracking level.
- **Cross-references from tracked code to `.workbench/` paths in production runtime paths.** Documentation citations from tracked code (docstrings, comments) MAY reference a workbench artifact by title, but MUST NOT hardcode a `.workbench/...` path since that path is ephemeral until the asset is promoted.
- **Silent promotion:** Do not move an asset out of `.workbench/` without a matching Conventional Commit entry naming it.

### Execution Steps

1. When creating a short-life asset, choose its `.workbench/<subdir>/` location based on where it *would have* lived if it were long-lived.
2. Reference the asset from other workbench siblings by relative `.workbench/…` paths.
3. When the asset matures (plan lands, baseline ships with a batch, analyzer findings become an ADR), promote it out of `.workbench/` in the landing commit and update cross-references.
4. Delete or archive the workbench copy after promotion — never leave two copies.

### Output Format

Workbench layout mirror:

```
.workbench/
  analysis/        # analyzer outputs, exploratory findings
  benchmarks/      # baseline snapshots pre-landing
  plans/           # in-flight plans + plan-analyzer output
  scripts/         # baseline scripts, one-off measurement runners
  # additional subdirs mirroring long-lived directories as needed
```

### Validation

- `grep -rEn "docs/(analysis|plans|benchmarks)/" src/ rules/ skills/ tests/ templates/ docs/` returns zero matches (workbench-shaped subdirs must not exist under `docs/`).
- `.gitignore` contains `.workbench/` and does NOT contain per-`docs/` workbench-ignore lines.
- Every asset under `.workbench/` has a clear promotion candidate (the long-lived dir it belongs in when it matures) OR is genuinely disposable.

### Post-Execution Checklist

- [ ] Asset is placed under the appropriate `.workbench/<subdir>/`
- [ ] Cross-references from other workbench siblings use `.workbench/…` paths
- [ ] Tracked code refers to the asset by title, not by path
- [ ] Promotion candidate is identified when the asset is created

## Key Principles

### Filesystem shape as signal

The filesystem tree is a first-class communication channel. When `docs/` contains only committed content, contributors know at a glance that anything under it is a project deliverable. When workbench artifacts are sprinkled into long-lived dirs — even if gitignored — the visual signal is polluted and the ignore rules become a hidden second contract that must be memorised.

### Promotion is intentional

Moving a plan from `.workbench/plans/` to `docs/plans/` is an editorial act, not a filesystem accident. The promotion commit makes the transition auditable and lets a reviewer verify the asset is ready for its long-lived home.

### One canonical path per asset

Never leave two copies of the same file across `.workbench/` and its long-lived home. The workbench copy is a work-in-progress; the long-lived copy is the deliverable. They must not coexist.

## Anti-Patterns and Common Mistakes

### Critical Violations

- **Per-`docs/` ignore lines:** Adding `docs/analysis/`, `docs/plans/`, or similar workbench-shaped ignore lines to `.gitignore`. Fix: relocate contents to `.workbench/` and remove the per-`docs/` lines.
- **Path-hardcoded citations in tracked code:** Docstrings or comments in `src/`, `rules/`, or `skills/` that name a `.workbench/…` path. Fix: cite the asset by title, not by ephemeral path.

### Common Anti-Patterns

**Anti-Pattern 1: Treating `.workbench/` as a graveyard**

**Problem:** Assets accumulate in `.workbench/` indefinitely because promotion is never scheduled.

**Correct Pattern:** Every workbench asset has a promotion trigger — a plan landing, a batch commit, an ADR being cut. If no trigger exists, the asset is disposable; delete it rather than leaving it in the workbench.

**Anti-Pattern 2: Symlinking `.workbench/foo` from `docs/foo`**

**Problem:** Attempting to keep the old location "working" via a symlink while the real content lives in `.workbench/`. Creates two paths to the same asset and undermines the filesystem-shape-as-signal principle.

**Correct Pattern:** Move the file; update the references. Symlinks are a policy violation.
