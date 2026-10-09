---
schema_version: v4.0
rule_version: v5.0.0
description: "Professional contribution workflow directives covering commits, pull requests, changelog discipline, and rule authoring standards to ensure consistent project collaboration and quality."
last_updated: 2026-10-06
keywords:
  - kw:pull requests
  - kw:conventional commits
  - kw:CONTRIBUTING.md
  - kw:changelog discipline
  - kw:rule authoring
  - kw:pre-commit validation
token_budget: ~1100
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 801-project-readme.md  # README best practices
    - 803-project-git-workflow.md  # Git workflow management
    - 002-rule-governance.md  # Rule authoring standards
---
# Contribution Workflow

## Scope

**What This Rule Covers:**
Contributor setup, canonical-source edits, validation, review and release documentation with separately authorized Git/publication actions.

**When to Load This Rule:**
When creating/reviewing CONTRIBUTING, preparing contributions or documenting commit, PR and rule-authoring workflows.

## Contract

### Inputs and Prerequisites

- Existing CONTRIBUTING, PR templates, governance and branch/protection conventions.
- Actual project automation/toolchain and validation commands, verified from current files.
- Current staged/unstaged state and user authorization for any branch, commit, push, PR or merge operation.

### Mandatory

- Read current contribution docs/templates before prescribing commands. Detect automation from existing Makefile, Taskfile or package scripts; do not hard-code obsolete make targets or generic Python versions.
- Edit canonical source (`rules/` here), not deployed plugin replicas. Follow numbering, schema and dependency requirements when authoring rules.
- Rule source uses v4 Scope/Contract/References, four required non-empty contract sections, at most 250 lines and three correct examples; preserve discovery metadata and safety semantics.
- Validate modified rules and applicable lint/format/tests before publication; full merge gates remain required even after focused checks pass.
- Use project Conventional Commits/branch naming conventions when authorized. Feature branches and PR review are the collaboration path, not permission to create/publish them automatically.
- Update Unreleased changelog for user-facing code/rule/config/doc changes; README only for changed user setup/behavior, avoiding contributor-detail duplication.
- Preserve staged/unrelated/concurrent work. Never force-push main/master, amend another author's commit, skip hooks or destructively restore files without explicit approval.
- Keep PR scope cohesive and describe concrete problem/result, verification and limitations. Split unrelated features/refactors when appropriate, not tightly coupled fixes solely for ceremony.
- Address review feedback with traceable new commits where project policy requires; do not amend/squash/rebase/merge without authorization. Disclose disagreement or follow-up scope clearly.
- Test invalid metadata/missing sections/commit-policy controls only in safe fixtures; never push deliberately invalid commits or main-branch changes to test branch protection.

### Execution Steps

1. Read current guidelines/templates, inspect branch/status and verify automation/tool availability.
2. Prepare a scoped change in canonical source following language/governance requirements, preserving unrelated edits.
3. Run focused then required full validation and review the diff; record actual failures and infrastructure limitations.
4. Update relevant changelog/user docs and prepare a reviewable PR description with accurate evidence.
5. Only with specific approval, create/stage/commit/push/PR actions per project policy. Do not treat an implementation request as publication permission.
6. For conflicts, inspect both versions and ownership before resolution; validate again. Rebase/fetch/push steps must be authorized, not a mandatory automatic recipe.
7. Address reviewer feedback, rerun affected gates and request re-review only when authorized. Merge follows approved repository strategy and review requirements.

### Validation

- Contribution documentation matches actual toolchain/commands and current v4 governance.
- Canonical-source/deployed-replica boundaries respected; numbering and dependency/discovery metadata verified.
- Required tests/lint/format/schema gates pass or exact blockers disclosed; no fabricated CI evidence.
- Changelog/docs/PR describe final user-visible behavior without secrets or unrelated inventory.
- Git/publication actions reflect explicit approvals; original staged work preserved and no direct-main/force/amend-policy violation.
- CI failures reproduced from actual logs where possible; unrelated failures clearly separated, not hidden or guessed away.

## References

- [GitHub: Contributor guidelines](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub: Pull request reviews](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests)
- `002-rule-governance.md` for rule authoring.
- `803-project-git-workflow.md` for source-control workflow.
