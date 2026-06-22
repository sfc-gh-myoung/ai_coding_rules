---
name: stage-changes
description: Stages currently unstaged git changes after presenting a grouped multi-select preview and a resolved file-list confirmation gate. Use before commit-changes, update-changelog, or release-commit when nothing is yet staged. Triggers on "stage changes", "stage files", "git add", "stage all", "stage my work".
version: 1.0.0
---

# Stage Changes

## Purpose

Selects and stages currently unstaged changes (modified, added, deleted, renamed, plus untracked) in the working tree, using a two-gate dry-run pattern: a group-level selection gate followed by a resolved file-list confirmation gate. Operates strictly through `git add` — no `--force`, no hunk splitting.

## Use this skill when

- Preparing to commit but nothing is staged yet.
- Scoping a commit to a subset of working-tree changes.
- Running ahead of [`commit-changes`](../commit-changes/SKILL.md), [`update-changelog`](../update-changelog/SKILL.md), or [`release-commit`](../release-commit/SKILL.md).

Do not use for: partial-file (hunk-level) staging — run `git add -p` directly; staging files matched by `.gitignore`; resolving merge conflicts.

## Inputs

### Required

- None.

### Optional

- `paths`: list of strings (default: none) — explicit files or directories to stage. When provided, the skill skips the group-selection gate and goes directly to the resolved file-list confirmation gate.
- `include_untracked`: boolean (default: `true`).
- `warn_size_mb`: integer (default: `5`) — files larger than this trigger a per-file safety warning in the confirmation gate.
- `mode`: `"interactive"` | `"all"` (default: `"interactive"`). `"all"` skips group selection and prefills "everything unstaged" into the confirmation gate. The confirmation gate still runs.

## Outputs

Side-effects only: a `git add <paths>` for each selected path. No files written by this skill.

After the apply step, the skill prints:

- Count of files staged.
- Grouped list of staged paths (`M skills/stage-changes/SKILL.md`, `A docs/adr/0006-...`, etc.).
- Pointer to the next likely skill (`commit-changes` or `release-commit`).

## Workflow

### Phase 1 — Preflight

1. Verify `git` is available and the working directory is inside a git repository (`git rev-parse --git-dir`).
2. **Refuse to operate** when any of these exist:
   - `.git/MERGE_HEAD`
   - `.git/CHERRY_PICK_HEAD`
   - `.git/REBASE_HEAD`, `.git/rebase-apply/`, or `.git/rebase-merge/`

   Report the in-progress operation and exit with no side effects.
3. Run `git status --porcelain=v1 -z` and parse entries by working-tree status:
   - **Modified (M)** — tracked file modified in working tree.
   - **Added / Untracked (A or `??`)** — new file.
   - **Deleted (D)** — tracked file deleted in working tree.
   - **Renamed (R)** — rendered as `R old → new`.
4. Drop entries whose index status is non-space (those are already staged; outside this skill's scope). Report the count for context.
5. If `include_untracked: false`, drop `??` entries.
6. If nothing remains: exit with `Nothing unstaged. (X files already staged.)`.

### Phase 2 — Grouping

Build the group table keyed by **top-level directory** (the first path segment; `<root>` for files in the repo root). For each group, count by change class:

```
Group                  Files   Classes
─────────────────────────────────────────────────
skills/                3       M:1  A:2
docs/                  2       A:2  [new]
prompts/               1       M:1
<root>                 1       M:1
```

Append `[new]` to any group containing only untracked files; append `[+untracked]` to mixed groups containing at least one untracked file.

### Phase 3 — Gate 1: group selection

- If `paths` was provided, **skip this gate** and pass the explicit list to Phase 4.
- If `mode: "all"`, **skip this gate** with all groups preselected.

Otherwise, call `ask_user_question` with `multiSelect: true`. Each option label is a group row (label + file count + class breakdown). Default selection: all groups preselected.

If the user submits zero selections, treat as Cancel and exit.

### Phase 4 — Gate 2: resolved file list confirmation

1. Resolve the selected groups (or explicit `paths`) to the concrete file list. Expand directories: every unstaged file under each selected directory.
2. **Safety scan** of the resolved list:
   - Compute size per file; flag any > `warn_size_mb`.
   - Detect binary content via `git check-attr` / file inspection; flag binaries.
   - Detect submodule pointer changes. **Exclude** by default; include only if their path was named explicitly in `paths`.
   - Detect `.gitignore` matches (defensive; impossible without `--force`); exclude.
3. Print the framed preview:

```
═════════════════════════════════
FILES TO BE STAGED (N)
─────────────────────────────────
 M  skills/stage-changes/SKILL.md
 A  skills/stage-changes/CHANGELOG.md         [new]
 A  docs/adr/0006-stage-changes-selection-ux.md  [new]
 M  skills/release-commit/SKILL.md
 M  prompts/README.md
═════════════════════════════════


═════════════════════════════════
WARNINGS  (not part of the staging set)
─────────────────────────────────
 ⚠ skills/stage-changes/assets/demo.gif   8.2 MB  [binary, > 5 MB]
═════════════════════════════════


═════════════════════════════════
EXCLUDED  (not part of the staging set)
─────────────────────────────────
 ⤫ vendor/submodule-x   [submodule pointer update — name explicitly to include]
═════════════════════════════════
```

Preview formatting follows [ADR 0007](../../docs/adr/0007-skill-style-guide.md).

4. Call `ask_user_question` with options:
   - **Stage** — execute Phase 5.
   - **Edit** — re-prompt with `type: "text"`, `defaultValue` set to the newline-separated resolved path list. After edit, re-run the safety scan and return to step 3.
   - **Cancel** — exit with no side effects.

If preview length would exceed 200 lines, truncate the per-file list to the first 200 entries and print `… and N more files (full list will be staged).` The full list is still staged on approval.

### Phase 5 — Apply

1. For deletes: `git add -u -- <path>` (preserves removal semantics).
2. For modifications and additions: `git add -- <path>`.
3. Prefer one batched `git add` invocation per class to keep apply atomic from the user's view.
4. **On failure mid-batch:** run `git reset HEAD -- <paths-attempted>` to unstage everything this skill staged in this invocation, then report the failure.
5. Re-run `git status --porcelain` to verify the post-state.

### Phase 6 — Closeout

Print:

- `Staged N files.`
- Grouped post-state list.
- `Next: invoke commit-changes or release-commit.`

## Safety

- Refuses during merge / cherry-pick / rebase.
- Never uses `git add --force`; `.gitignore`d files cannot be staged.
- Never runs `git commit` or `git push`.
- Never modifies the working tree's content (only the index).
- Submodule pointers excluded unless explicitly named.
- Binary or large files trigger warnings, not refusals.

## Anti-patterns

- **Silent untracked sweep.** Untracked files are always labeled `[new]` in both gates.
- **Wholesale `git add .` without preview.** The two-gate flow is mandatory; `mode: "all"` still confirms the resolved list.
- **Operating during a merge.** Merge resolution is the user's responsibility.
- **Re-staging already-staged files.** Phase 1 drops them from consideration and reports the count.

## Examples

**Invocation:** "Stage my work."

**Gate 1 prompt:**

```
Question: Select groups to stage (multi-select).
Options:
  [✓] skills/   (3 files: M:1  A:2)
  [✓] docs/     (2 files: A:2  [new])
  [✓] prompts/  (1 file:  M:1)
  [✓] <root>    (1 file:  M:1)
```

**Gate 2 preview:** see Phase 4.

**Closeout:**

```
Staged 7 files.
Next: invoke commit-changes or release-commit.
```

## Related Skills

- [`commit-changes`](../commit-changes/SKILL.md) — drafts and applies a Conventional Commits message on the staged set.
- [`update-changelog`](../update-changelog/SKILL.md) — drafts a Keep-a-Changelog entry from the staged set.
- [`release-commit`](../release-commit/SKILL.md) — orchestrator; auto-invokes `stage-changes` when nothing is staged.

## References

- Pro Git §2.2 (`git add`, `git reset HEAD`).
- `git-status(1)` porcelain v1 format.

## Version History

See [CHANGELOG.md](CHANGELOG.md).
