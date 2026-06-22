---
name: commit-changes
description: Composes a Conventional Commits 1.0.0 message from currently staged git changes and commits after dry-run user approval. Use when committing reviewed staged changes with a well-formed conventional commit message. Triggers on "commit", "commit changes", "commit staged", "conventional commit", "git commit".
version: 1.1.1
---

# Commit Changes

## Purpose

Drafts a [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) message from the currently staged set, prints it for review, and commits only after explicit user approval. Operates strictly on what is already staged — never stages files on the user's behalf.

## Use this skill when

- Committing changes the user has already reviewed and staged.
- Producing well-formed Conventional Commits messages without hand-authoring them.
- Pairing with `update-changelog` (manually or via the `release-commit` orchestrator).

Do not use for: staging files, force-pushing, amending arbitrary commits, or committing across multiple repositories in one shot.

## Inputs

### Required

- None — the skill operates on `git diff --cached`.

### Optional

- `type`: enum (default: inferred) — Conventional Commits type. One of `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- `scope`: string (default: inferred from common path prefix of staged files).
- `description`: string (default: drafted from diff summary).
- `body`: string (default: a single short paragraph describing the feature or fix — never a list of changed files; file inventory is discoverable via `git show --stat`).
- `breaking`: boolean (default: `false`) — when true, appends `!` to type/scope and adds `BREAKING CHANGE:` footer.
- `signoff`: boolean (default: `false`) — when true, passes `--signoff` to `git commit`.

## Outputs

A single `git commit` on the current branch using `git commit -m "<subject>" -m "<body>"`. No other side effects. No files written by this skill.

## Workflow

### Phase 1 — Preflight

1. Run `git diff --cached --name-status`. If empty: stop, report `Nothing staged to commit. Stage changes first.`
2. Detect repository root, current branch, and whether the working tree has unstaged changes (warn — not error — if so).
3. Refuse to operate if `.git/MERGE_HEAD` or `.git/CHERRY_PICK_HEAD` exists; report and exit.

### Phase 2 — Draft

1. Infer `type` from staged paths and diff signals:
   - New files in `tests/`, `__tests__/`, `spec/`, or matching `*_test.*` → `test`
   - Only files under `docs/`, `*.md`, or `README*` → `docs`
   - Only files under `.github/workflows/`, `ci/` → `ci`
   - Dependency manifest changes only (`package.json`, `pyproject.toml`, `Cargo.toml`) → `chore` or `build`
   - Default heuristic: presence of new exported functions/classes → `feat`; otherwise `fix` if diff is small, `refactor` if diff is large with no behavior keywords.
2. Infer `scope` from the longest common directory prefix of staged files, trimmed to a single segment (e.g., `skills/commit-changes/SKILL.md` → `commit-changes`; if mixed roots → empty scope).
3. Compose subject: `<type>(<scope>): <description>` (≤72 chars; truncate description and append `…` if longer). Subject must be feature- or behavior-focused — describe *what changed for the user or system*, not which files moved.
4. Compose body (optional — omit entirely if the subject is self-explanatory):
   - One short paragraph (1–3 sentences) explaining the *why* or the user-visible behavior change.
   - **Do not list changed files.** The file inventory is recoverable from `git show --stat` / `git log --stat` and adds noise to the message.
   - **Do not restate the subject.** If there is nothing to add beyond the subject, leave the body empty.
5. If `breaking: true`: append `!` after type/scope and add a `BREAKING CHANGE: <description>` footer.

### Phase 3 — Dry-run gate

Print the draft using the canonical preview pattern (per [ADR 0007](../../docs/adr/0007-skill-style-guide.md)):

```
═════════════════════════════════
PROPOSED COMMIT MESSAGE
─────────────────────────────────
<subject>

<body>

<footer (if any)>
═════════════════════════════════


═════════════════════════════════
FILES TO BE COMMITTED (N)  (not part of the commit message)
─────────────────────────────────
 M  path/one
 A  path/two
 D  path/three
═════════════════════════════════
```

Call `ask_user_question` with options:

- **Commit** — proceed to Phase 4.
- **Edit** — re-prompt with a `type: "text"` question whose `defaultValue` is the full current draft (subject + body + footer). After edit, return to the framed preview.
- **Cancel** — exit without committing.

### Phase 4 — Commit

1. Build `git commit` command:
   - `git commit -m "<subject>"` for the subject.
   - Additional `-m "<paragraph>"` for body paragraphs and footers.
   - Append `--signoff` if `signoff: true`.
2. Execute.
3. Report the new commit hash (short) and the final subject line.

## Safety

- Never runs `--no-verify` unless the user explicitly passes that input.
- Never runs `git add`.
- Never runs `git push`.
- Refuses to commit if no changes are staged.
- Refuses to commit during a merge or cherry-pick.

## Anti-patterns

- **Bypassing hooks.** `--no-verify` is opt-in only.
- **Auto-staging.** Users stage; this skill commits.
- **Multi-purpose subjects.** If staged changes span unrelated concerns, recommend splitting into multiple commits during the dry-run gate (informational only — do not split automatically).
- **Type guessing without signal.** If type cannot be inferred, ask via `ask_user_question` rather than defaulting to `chore`.
- **File lists in the body.** Never enumerate changed files in the commit message — that information lives in `git show --stat` and clutters the message. Keep bodies feature-focused and concise.

## Examples

**Staged diff:**

```
A  skills/commit-changes/SKILL.md
A  skills/commit-changes/CHANGELOG.md
```

**Drafted message:**

```
feat(skills): add commit-changes skill

Converts the prior prompt into a self-contained skill that drafts
Conventional Commits messages and commits after explicit user approval.
```

Note: no file list in the body — `git show --stat <hash>` recovers it on demand.

## References

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)

## Version History

See [CHANGELOG.md](CHANGELOG.md).
