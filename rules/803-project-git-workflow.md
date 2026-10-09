---
schema_version: v4.0
rule_version: v5.0.0
description: "Git workflow: Conventional Commits, feature branching, PR workflows, pre-commit validation, and CHANGELOG updates."
last_updated: 2026-10-06
keywords:
  - kw:conventional commits
  - kw:feature branch workflow
  - kw:conventional branch naming
  - kw:CHANGELOG.md updates
  - kw:pre-commit validation gate
  - kw:pull request workflow
token_budget: ~1000
context_tier: Medium
depends:
  required:
    - 800-project-changelog.md  # Changelog management
    - 802-project-contributing.md  # Contribution workflow
  optional:
    - 000-global-core.md  # Pre-Task-Completion Validation Gate
---
# Git Workflow Management

## Scope

**What This Rule Covers:**
Feature-branch contributions, atomic conventional commits, review, validation and safe recovery with explicit publication authority.

**When to Load This Rule:**
When preparing commits, branches, PRs, merges or contribution workflow changes.

## Contract

### Inputs and Prerequisites

- Current branch, status, index/worktree diff, remote state and project CONTRIBUTING/merge strategy.
- Existing validation/hooks/branch protections and explicit approval for source-control mutations.
- Actual change purpose, user impact and verification evidence.

### Mandatory

- Inspect status/index/diff before staging or changing branches. Preserve pre-existing staged, unstaged and concurrent work; do not require a clean tree by discarding it.
- Create/commit/push/PR/merge only when specifically authorized. Work on an approved feature branch, not directly on protected main/master.
- Follow project branch conventions, normally type/kebab-case description; do not rename an existing user branch merely for style.
- Make commits one cohesive logical change. Use Conventional Commits: type, optional scope, concise feature-focused subject; explain why/impact/validation in a short body when needed, not a file inventory.
- Mark breaking changes with `!` or BREAKING CHANGE and migration guidance. Keep CHANGELOG user-facing and shorter than engineering commit details; do not copy full entries blindly.
- Follow higher-priority attribution instructions and explicitly configured project preferences. A rule file cannot override system/developer authority.
- Run required validation/hooks before publication. Do not use no-verify/no-gpg-sign, force push, hard reset, checkout restore, rebase, amend or branch deletion without specific approval where destructive/history-changing.
- Never amend another author's commit or force-push protected main/master. Inspect authorship, push state and ownership before any approved history operation.
- Recover accidental commits by first inspecting whether pushed and who owns the changes; propose a scoped recovery. Do not automatically reset/revert/push or blindly undo HEAD.
- Use the documented consistent merge strategy and required approvals/status checks; do not merge your own PR without applicable review policy.

### Execution Steps

1. Read contribution/merge conventions and current Git state; identify intended scope and approved operations.
2. Prepare a minimal cohesive diff and changelog update, then run focused/full gates required by risk and project policy.
3. If commit authorized, inspect staged contents and secrets, stage only relevant owned files, write accurate conventional message and run normal hooks.
4. Verify commit outcome and remaining status. Hook failures need diagnosis/fix, not bypass; preserve unrelated staged changes.
5. If publication authorized, verify branch tracking/divergence and full branch diff before push/PR. Describe final behavior, actual validation and limitations.
6. Resolve conflicts locally after comparing both versions/ownership; rerun checks before authorized publication. Coordinate with conflicting authors when necessary.
7. Merge/delete branches only under explicit approval and repository strategy; verify final state rather than assuming success.

### Validation

- Correct approved branch/scope, no unrelated index changes or secrets.
- Atomic conventional commit messages reflect why, behavior and evidence; attribution obeys governing instructions.
- Hooks/project gates actually pass; CI evidence real and relevant, limitations disclosed.
- No unauthorized direct-main/force/destructive/history rewrite or publication.
- PR includes all branch commits since base, not only latest; merge review/protection requirements satisfied.
- Remaining worktree state accurately reported, not silently cleaned.

## References

- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
- [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)
- [Git reference](https://git-scm.com/docs)
- [Conventional Branch](https://conventional-branch.github.io/)
