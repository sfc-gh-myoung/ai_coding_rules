---
name: release-commit
description: Orchestrates update-changelog and commit-changes into a single atomic release-commit workflow with one combined approval gate. Use when shipping staged work that needs both a CHANGELOG entry and a Conventional Commits commit in one shot. Triggers on "release commit", "ship changes", "changelog and commit", "commit with changelog".
version: 1.1.1
---

# Release Commit

## Purpose

Composes a combined release-commit workflow that drafts a Keep-a-Changelog entry and a Conventional Commits message from the same staged set, presents a single combined preview, and on approval applies the changelog edit, stages it, and commits — atomically. If the commit step fails, the changelog edit is reverted.

## Use this skill when

- Shipping staged work that needs both a CHANGELOG entry and a commit.
- Reducing two approval gates (one per child skill) to a single combined gate.

Do not use for: pushing to a remote, cutting a versioned release (moving `[Unreleased]` to a versioned section), or staging files.

## Inputs

### Required

- None — operates on `git diff --cached`.

### Optional

- All optional inputs from [`update-changelog`](../update-changelog/SKILL.md) (e.g., `changelog_path`, `category`, `entry`).
- All optional inputs from [`commit-changes`](../commit-changes/SKILL.md) (e.g., `type`, `scope`, `description`, `body`, `breaking`, `signoff`).
- All optional inputs from [`stage-changes`](../stage-changes/SKILL.md) (e.g., `paths`, `include_untracked`, `warn_size_mb`, `mode`) — forwarded only when `stage-changes` is auto-invoked.
- `skip_changelog`: boolean (default: `false`) — when true, behave exactly like `commit-changes` alone.
- `skip_stage`: boolean (default: `false`) — when true, preserve the prior fail-fast behavior (`Nothing staged. Stage changes before running release-commit.`). When false (default), auto-invoke `stage-changes` if nothing is staged.

## Outputs

- `CHANGELOG.md` modified in place and staged.
- A single `git commit` containing both the staged changes and the changelog update.

## Workflow

### Phase 1 — Preflight

1. Run `git diff --cached --name-status`.
2. **If nothing is staged:**
   - If `skip_stage: true`: stop, report `Nothing staged. Stage changes before running release-commit.`
   - Otherwise (default): invoke [`stage-changes`](../stage-changes/SKILL.md) end-to-end (its Phase 1–6). If the user cancels `stage-changes`, exit this skill with no side effects. On success, re-run `git diff --cached --name-status` and continue. Files staged in this step are tracked separately for the combined preview in Phase 3.
3. Refuse to operate during a merge or cherry-pick (same rule as `commit-changes`).
4. Take an in-memory backup of `CHANGELOG.md` (the entire current file contents) before any mutation.

### Phase 2 — Draft both

1. Invoke the `update-changelog` drafting logic (Phase 1–2 of that skill) **without** triggering its dry-run gate. Capture the proposed changelog entry as `changelog_draft`.
2. Invoke the `commit-changes` drafting logic (Phase 1–2 of that skill) **without** triggering its dry-run gate. Capture the proposed commit message as `commit_draft`.
3. If `skip_changelog: true`, set `changelog_draft` to none and skip its application.

### Phase 3 — Combined dry-run gate

Print a single combined preview:

```
═════════════════════════════════
PROPOSED CHANGELOG ENTRY  (./CHANGELOG.md, under ## [Unreleased])
─────────────────────────────────
### Added
- Add commit-changes skill for Conventional Commits drafting

### Changed
- Point prompts/README.md at new skill locations
═════════════════════════════════


═════════════════════════════════
PROPOSED COMMIT MESSAGE
─────────────────────────────────
feat(skills): add commit-changes skill

Converts prompts/commit-changes.md into a self-contained skill that
drafts Conventional Commits messages and commits after approval.

- skills/commit-changes/SKILL.md
- skills/commit-changes/CHANGELOG.md
═════════════════════════════════


═════════════════════════════════
FILES TO BE STAGED ON APPROVAL  (not part of message or changelog)
─────────────────────────────────
+ CHANGELOG.md  (will be staged by this skill)
  (already staged before this invocation):
  A  skills/commit-changes/SKILL.md
  A  skills/commit-changes/CHANGELOG.md
  M  prompts/README.md
  (staged via stage-changes this invocation):
  A  skills/stage-changes/SKILL.md
  A  skills/stage-changes/CHANGELOG.md
═════════════════════════════════
```

Preview formatting follows [ADR 0007](../../docs/adr/0007-skill-style-guide.md): two-blank-line gap between each labeled block; metadata-hint suffix on non-artifact blocks.

Call `ask_user_question` with options:

- **Commit** — proceed to Phase 4.
- **Edit changelog** — re-prompt the changelog draft (`type: "text"`, `defaultValue: changelog_draft`); return to combined preview.
- **Edit commit message** — re-prompt the commit draft (`type: "text"`, `defaultValue: commit_draft`); return to combined preview.
- **Cancel** — exit without changes.

### Phase 4 — Apply atomically

1. Apply `changelog_draft` to `CHANGELOG.md` using the `update-changelog` Phase 4 logic.
2. `git add <changelog_path>`.
3. Run `git commit` using the `commit-changes` Phase 4 logic and `commit_draft`.
4. **On commit failure:**
   - Restore `CHANGELOG.md` from the in-memory backup.
   - `git reset HEAD <changelog_path>` to unstage it.
   - **Files staged via `stage-changes` during this invocation are left in the index** so the user can fix and retry without re-running staging.
   - Report the failure with the original commit error message.
5. **On success:** report the new commit hash (short) and the categories added to the changelog.

## Safety

- Atomic: either both edits land or neither does.
- Never runs `git push`.
- Never runs `--no-verify` unless explicitly passed via `commit-changes` inputs.
- Refuses to operate during a merge or cherry-pick.
- Refuses to operate when nothing is staged.

## Anti-patterns

- **Reimplementing child logic.** This skill delegates drafting and application to `update-changelog` and `commit-changes`. Drift between this skill and either child is a bug.
- **Skipping the combined preview.** Even when both children would have skipped their previews (e.g., user supplied complete inputs), the combined gate runs.
- **Partial apply on commit failure.** The atomicity rule is non-negotiable.

## Examples

**Invocation:**

> "Release-commit the staged work."

**Resulting flow:** combined preview as shown in Phase 3, single approval, atomic apply.

## Related Skills

- [`stage-changes`](../stage-changes/SKILL.md) — select and stage unstaged changes; auto-invoked when nothing is staged.
- [`update-changelog`](../update-changelog/SKILL.md) — draft and prepend changelog entry.
- [`commit-changes`](../commit-changes/SKILL.md) — draft and execute commit.

## References

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)

## Version History

See [CHANGELOG.md](CHANGELOG.md).
