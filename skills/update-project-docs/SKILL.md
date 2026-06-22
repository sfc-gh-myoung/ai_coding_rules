---
name: update-project-docs
description: Audits project documentation for duplicate, overlapping, and contradicting content across discovered markdown files and emits a remediation report with prioritized recommendations. Use when reviewing README, CONTRIBUTING, ARCHITECTURE, DEPLOYMENT, or docs directory for quality, consistency, and freshness. Triggers on "audit docs", "review project docs", "update project documentation", "docs remediation", "doc overlap".
version: 1.0.1
---

# Update Project Docs

## Purpose

Audits the project's markdown documentation for duplicate content, overlapping sections, internal contradictions, and stale references; produces a prioritized remediation report. Read-only by default — remediation edits are gated behind an explicit `apply_remediation` opt-in plus per-file dry-run approval.

## Use this skill when

- Auditing project documentation (README, CONTRIBUTING, ARCHITECTURE, DEPLOYMENT, `docs/`).
- Identifying duplicate or contradicting content across files.
- Producing a remediation backlog before a docs refactor.
- Establishing whether documentation matches industry conventions (Diátaxis, GitHub community standards).

Do not use for: writing new documentation, generating API reference, or fixing a single typo (use direct edits).

## Inputs

### Required

- None.

### Optional

- `target_files`: list of paths (default: discovery — see [Discovery Algorithm](#discovery-algorithm)).
- `apply_remediation`: boolean (default: `false`) — when true, the skill produces per-file diffs and offers to apply them with per-file approval.
- `report_path`: path (default: `docs/doc-audit-<YYYYMMDD>.md`; if `docs/` does not exist, falls back to `./doc-audit-<YYYYMMDD>.md`).
- `link_check`: boolean (default: `true`) — when true, performs HEAD requests on external URLs and existence checks on relative paths.

## Outputs

- A markdown report at `report_path` (no-overwrite — append `-01`, `-02` if exists).
- If `apply_remediation: true`: per-file edits applied after individual approval gates.

## Discovery Algorithm

When `target_files` is not provided:

1. Collect `*.md` at the repo root: `./*.md`.
2. Collect `**/*.md` under `docs/` if it exists.
3. Exclude:
   - `LICENSE*`
   - `CHANGELOG.md` (audited by `update-changelog` workflows)
   - `node_modules/**`, `.git/**`, `dist/**`, `build/**`, `target/**`, `vendor/**`
   - Files inside `prompts/archive/` or `skills/**/CHANGELOG.md`
4. Present the discovered list via `ask_user_question` with `type: "text"`, `defaultValue: <newline-separated list>`. The user can add or remove paths before the audit runs.

## Workflow

### Phase 1 — Discovery and confirmation

1. Run the discovery algorithm.
2. Confirm the file list with the user. If the user clears the list, exit.

### Phase 2 — Per-file profile

For each file, extract:

- Title (first H1).
- Heading tree (H1 → H6).
- First paragraph under each H2 (used for overlap detection).
- All link targets (relative paths and external URLs).
- Diátaxis classification heuristic: tutorial / how-to / reference / explanation / mixed (a single file in mixed mode is a finding).

### Phase 3 — Overlap and contradiction analysis

1. **Overlap matrix.** Build a section-level matrix: for each pair of `(file, H2)` and `(file', H2')`, compute a similarity score on heading text + first paragraph. Mark pairs at ≥0.7 similarity as **overlap**.
2. **Contradictions.** For each fact pattern that appears in multiple files (install commands, version numbers, default ports, env-var names), flag pairs that differ.
3. **Staleness.**
   - Relative path link → file existence check.
   - External URL → HEAD request when `link_check: true`; flag any non-2xx.
   - Tool version mentions → flag if multiple files state different versions.
4. **Diátaxis fit.** Flag any file that mixes Diátaxis modes (e.g., a README that interleaves tutorial steps and reference tables).
5. **GitHub community standards.** For the README, check presence of: project description, install, usage, contributing pointer, license pointer. For CONTRIBUTING, check: how to file issues, how to submit PRs, code of conduct pointer, dev setup.

### Phase 4 — Report

Write to `report_path`:

```markdown
# Documentation Audit — <YYYY-MM-DD>

## 1. Summary

- Files audited (N)
- Duplicate-content findings (N)
- Contradicting-content findings (N)
- Stale-reference findings (N)
- Structure findings (N)
- Overall recommendation: refactor / targeted-fix / no-action

## 2. Per-File Findings

For each file: title, heading tree summary, Diátaxis classification, issues
found, recommended action.

## 3. Overlap Matrix

Pipe table of overlapping sections with similarity score and recommendation
(merge / cross-reference / leave-as-is).

## 4. Contradictions

For each contradiction: fact, files that disagree, evidence lines, recommended
resolution.

## 5. Staleness

- Broken relative paths
- Broken external URLs
- Version mismatches across files

## 6. Remediation Backlog

Prioritized P0–P3 with: task, target files, rationale, dependencies, pros, cons,
alignment, source.

**End of audit.**
```

### Phase 5 — Conditional remediation

When `apply_remediation: true`:

1. For each P0 and P1 finding, produce a concrete per-file diff.
2. Print the diff using the canonical preview pattern (per [ADR 0007](../../docs/adr/0007-skill-style-guide.md)):

   ```
   ═════════════════════════════════
   PROPOSED FILE EDIT (path/to/file.md)
   ─────────────────────────────────
   - <removed line(s)>
   + <added line(s)>
   ═════════════════════════════════


   ═════════════════════════════════
   RATIONALE  (not part of the file edit)
   ─────────────────────────────────
   <one or two sentences citing the audit finding ID>
   ═════════════════════════════════
   ```

3. `ask_user_question`: `Apply / Skip / Stop` per file.
4. On `Apply`: edit the file using surgical `Edit` operations (no whole-file rewrites). Re-verify the file profile after edit.
5. On `Stop`: end the remediation phase; audit report remains the artifact.

## Safety

- Read-only when `apply_remediation: false` (the report file is the only write).
- Edits, when applied, are per-file and per-finding — never bulk.
- No file is modified without dry-run approval.
- External link checks have a per-URL timeout of 10s; failures are reported, not retried indefinitely.

## Anti-patterns

- **Auto-merging files without approval.** Even with `apply_remediation: true`, every file edit is gated.
- **Surface-level dedup.** A duplicate heading is not a finding by itself; content similarity must support it.
- **Ignoring Diátaxis when a project follows a different convention.** If the project documents its own framework (e.g., in CONTRIBUTING.md), treat that as authoritative and demote Diátaxis findings.
- **Conflating CHANGELOG.md with project docs.** `CHANGELOG.md` is excluded from discovery.

## Examples

**Invocation:**

> "Audit our project docs."

**Discovered file list (prefilled in prompt):**

```
README.md
CONTRIBUTING.md
ARCHITECTURE.md
docs/deployment.md
docs/style-guide.md
```

**Report path:** `docs/doc-audit-20260621.md`

## References

- [Diátaxis](https://diataxis.fr/)
- [GitHub community standards](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions)

## Version History

See [CHANGELOG.md](CHANGELOG.md).
