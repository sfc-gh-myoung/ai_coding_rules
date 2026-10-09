---
schema_version: v4.0
rule_version: v3.0.0
description: Controlled environment promotion, artifact validation, concurrency safeguards, and ownership-scoped deployment recovery.
last_updated: 2026-10-07
keywords:
  - kw:multi-environment promotion
  - kw:deployment validation gates
  - kw:rollback recovery procedures
  - kw:stage backup snapshot
  - kw:deployment audit trail
  - kw:environment-aware automation
token_budget: ~1000
context_tier: Low
depends: {}
---
# Snowflake App Deployment Advanced Patterns

## Scope

**What This Rule Covers:**
Environment promotion, artifact/configuration gates, known-good preservation, concurrency control, audit evidence and safe failure recovery.

**When to Load This Rule:**
When designing multi-environment app deployment, production validation gates, or interrupted-deployment recovery.

## Contract

### Inputs and Prerequisites

- Existing deployment/automation workflow, reviewed artifact/manifest, explicit environment map and approved promotion policy.
- Current target/grants/consumers/live versions, known-good assets, ownership boundaries, recovery objectives and operation approvals.

### Mandatory

- Bind environment/account/role/database/schema/stage/compute explicitly; reject unknown or missing names instead of a default catch-all. Do not route production through an environment variable alone without approval.
- Validate reviewed artifacts in the project's required lower environments before production. Preserve identical artifact identity across promotion; handle any approved emergency exception explicitly rather than invent a mandatory QA environment.
- Gate source availability before mutation, staged manifest/content after transfer, effective definition/live-version/grants after update, and functionality under authorized consumer contexts. Object existence and substring grep are insufficient health checks.
- Use structured command outputs with exact object/path matching, counts/checksums where supported, and proper exit handling; do not hide verification failures with || true or infer success from unrelated rows.
- Preserve known-good source manifests/config/grants and live-version recovery options before risky updates. A COPY FILES stage snapshot does not capture the entire app definition, permissions, state or copied runtime version.
- Backup/restoration transfers require approved owned source/destination and retention policy. No whole shared-stage copy/clear or arbitrary external backup upload; inspect supported file/version APIs before relying on recovery.
- Document recovery by failure stage and inspect actual state/query outcomes before replay. Restore only affected owned changes under approval; no blanket DROP/REMOVE or assumed seconds-long rollback guarantee.
- Use a reviewed historical artifact in a separate safe location for recovery; never overwrite unrelated local edits with git checkout HEAD~1/HEAD or assume the preceding commit is the deployed known-good version.
- Define real mutual exclusion for overlapping deployment scopes through existing CI/lock facilities. SELECT-then-INSERT into an unconstrained table is not an atomic lock; acquisition/release need owner token, expiry, failure handling and scoped release.
- Record artifact/config/query/deployment IDs, environment, actor, time, actual outcome, failures and recovery events in approved evidence. Do not log success before verification or disclose secrets/sensitive account data.
- Notifications use authorized existing channels/endpoints and scoped content. Never post deployment/account data to an arbitrary webhook merely because a template contains a URL.
- Test applicable recovery in approved isolated scope before production dependence; define downtime/data compatibility and missing evidence, not a claim that one command restores all state.

### Execution Steps

1. Inspect lifecycle/environment/known-good state and define artifact identity, scope, promotion and recovery constraints.
2. Add exact structured pre/post gates and existing concurrency controls, preserving source/object/grant state.
3. Validate local scripts and isolated lower-environment behavior only within execution approval; retain failures.
4. Promote the approved artifact through protected gates; separately verify effective publication and consumer health.
5. On failure inspect uncertain state, perform approved scoped recovery, and report actual restored/unresolved outcomes.

### Validation

- Environment binding and production authorization explicit; same reviewed artifact tested/promoted.
- Gates verify content/config/live state and actual health with fail-closed exit handling.
- Known-good recovery includes needed source/object/grant state, concurrency lock genuinely exclusive and owner-scoped.
- No destructive shared cleanup, local Git restore, broad lock release, fabricated audit success, or unapproved webhook.
- Deliver environment-aware configuration, tested recovery/runbook and actual validation limits; unexecuted production/rollback checks remain unverified.

## References

- [CREATE STREAMLIT source/runtime semantics](https://docs.snowflake.com/en/sql-reference/sql/create-streamlit)
- [ALTER STREAMLIT version lifecycle](https://docs.snowflake.com/en/sql-reference/sql/alter-streamlit)
- [COPY FILES](https://docs.snowflake.com/en/sql-reference/sql/copy-files)
- `109b-snowflake-app-deployment-core.md` for preserving lifecycle.
- `109h-snowflake-app-deployment-taskfile.md` for ordered automation.
- `803-project-git-workflow.md` for local/source-control preservation.
