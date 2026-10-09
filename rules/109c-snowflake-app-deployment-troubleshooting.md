---
schema_version: v4.0
rule_version: v5.0.0
description: Evidence-based Snowflake application deployment diagnostics and minimal ownership-scoped remediation.
last_updated: 2026-10-07
keywords:
  - kw:streamlit deployment troubleshooting
  - kw:sis typeerror
  - kw:auto_compress debugging
  - kw:stage file diagnostics
  - kw:live_version_location_uri
  - kw:notebook cache clearing
  - kw:deployment permission debugging
token_budget: ~1150
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns and validation gates
    - 100-snowflake-core.md  # Snowflake SQL, stage operations, and diagnostic commands
    - 101-snowflake-streamlit-core.md  # Core Streamlit patterns for deployment context
---
# Snowflake Application Deployment: Troubleshooting

## Scope

**What This Rule Covers:**
App source/version, compression, paths, packages, permissions and notebook-state diagnostics with minimal reproducible repairs.

**When to Load This Rule:**
When troubleshooting Snowflake app deployment errors, stale source, import/API failures, or stage/object mismatch.

## Contract

### Inputs and Prerequisites

- Exact redacted error/stack and deployment step, app/runtime type, automation/client version, source manifest and expected behavior.
- Authorized read scope for stage/object/live-version/config/grants and separate repair/deployment approval.

### Mandatory

- Inspect existing scripts and available LIST/SHOW/DESCRIBE/live notebook/source evidence before claiming root cause. If account tools are unavailable, provide diagnostics as proposals and keep conclusions provisional.
- TypeError is a symptom, not proof of compression or one of three fixed causes. Inspect full stack, file bytes/extensions, entrypoint path, package/API compatibility and current version state.
- Verify application assets remain uncompressed where required, PUT AUTO_COMPRESS=FALSE/CLI equivalent emitted, transfer results and manifest identity correct. An extension/timestamp alone does not prove readable current content.
- Compare FROM source, MAIN_FILE and effective committed/live source separately; FROM is a one-time copy. For legacy ROOT_LOCATION inspect actual prefix and relative main-file path; subdirectories are not inherently invalid.
- Inspect DESCRIBE fields actually returned, including live_version_location_uri where supported. Do not infer lifecycle solely from one absent field or assume stage updates propagate to copied apps.
- For stale notebook code, compare live source with intended artifact and actual import/version workflow. Preserve unsaved edits before refresh/restart; browser cache clearing is not a substitute for server-side identity verification.
- Diagnose AttributeError/import failures against actual installed runtime and supported dependencies. Warehouse environment.yml and container dependency mechanisms differ; no universal Streamlit >=1.50 fix.
- Permission failures require current primary/secondary role, stage READ/WRITE, schema creation, warehouse/compute and object ownership evidence. Report missing privilege to the authorized owner; do not self-grant, revoke broad access, or invent generic DROP privilege.
- Use the smallest supported update/repair. Successful overwrite/version publication need not include REMOVE/DROP. Destructive cleanup and recreate require verified ownership, explicit approval, grants/consumer review, and recovery.
- Existing-object errors do not authorize DROP. Missing-file REMOVE outcomes and client exit codes must be checked as observed; do not silently ignore all cleanup errors under an idempotency label.
- Inspect final state after interrupted transfer/create/publish before replay. Retain failed command/query evidence, preserve known-good versions and unrelated stage files, and avoid arbitrary GET/download of confidential assets.
- Reproduce fixes through approved project tooling when practical; manual supported UI actions are not categorically prohibited but must be recorded and reconciled. Never run a full mutating deploy merely to diagnose.

### Execution Steps

1. Read actual failure and deployment/runtime configuration, source manifest, and available object/stage state.
2. Separate transfer/compression/path, copied/live-version, dependency/code, permission, and browser/kernel hypotheses using evidence.
3. Propose scoped repair with exact prerequisites, ownership/deletion boundaries, expected state, and recovery.
4. Under repair approval, apply only the demonstrated fix through supported lifecycle tooling; inspect effective artifact/version and permissions.
5. Test app/notebook behavior in authorized scope and document actual results, remaining uncertainty and reproducible prevention.

### Validation

- Root-cause statement ties to actual stack/state evidence; unavailable diagnostics not asserted executed.
- Effective source/runtime/entrypoint/dependencies correct and approved viewer/session behavior verified.
- No blanket DROP/REMOVE, broad revoke/grant, unapproved restart, or stale-file assumptions.
- Compression/path flags and transfer outcomes checked without claiming a universal TypeError mapping.
- Output includes redacted evidence, minimal repair, command outcomes and limits; unrun browser/cloud tests remain unverified.

## References

- [CREATE STREAMLIT](https://docs.snowflake.com/en/sql-reference/sql/create-streamlit)
- [ALTER STREAMLIT](https://docs.snowflake.com/en/sql-reference/sql/alter-streamlit)
- [PUT](https://docs.snowflake.com/en/sql-reference/sql/put)
- [Streamlit troubleshooting](https://docs.snowflake.com/en/developer-guide/streamlit/troubleshooting)
- [Notebook surfaces](https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks-in-workspaces/notebooks-in-workspaces-overview)
- `109b-snowflake-app-deployment-core.md` for safe deployment lifecycle.
- `109j-snowflake-sis-typeerror-debugging.md` for focused symptom diagnosis.
