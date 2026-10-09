---
schema_version: v4.0
rule_version: v5.0.0
description: Stack- and runtime-grounded Streamlit TypeError/AttributeError diagnosis with safe source and dependency repair.
last_updated: 2026-10-07
keywords:
  - kw:SiS TypeError
  - kw:AUTO_COMPRESS FALSE
  - kw:AttributeError streamlit module
  - kw:FROM source path
  - kw:live_version_location_uri
  - kw:environment.yml streamlit pin
token_budget: ~1050
context_tier: Medium
depends:
  optional:
    - 109c-snowflake-app-deployment-troubleshooting.md  # Parent troubleshooting rule
---
# Snowflake SiS TypeError and AttributeError Debugging

## Scope

**What This Rule Covers:**
Streamlit deployment/import/API symptoms, source compression/path/version checks, dependency compatibility, and scoped verification.

**When to Load This Rule:**
When investigating SiS TypeError, missing Streamlit attributes, source-stage path issues, or runtime dependency mismatches.

## Contract

### Inputs and Prerequisites

- Exact redacted stack/error, affected page/step, runtime, app/source identifiers, actual package versions, and deployment helper configuration.
- Authorized inspection scope and separate permission for transfer/object/package changes or app execution.

### Mandatory

- Read stack and actual source/runtime evidence before assigning cause. Compression, missing/misaligned files, publication, incompatible API, module shadowing or application code are hypotheses, not an exhaustive universal TypeError mapping.
- Inspect permitted LIST/DESCRIBE/source/version evidence and transfer results. If unavailable, propose checks and label diagnosis provisional; do not claim commands executed.
- Verify all required application assets are readable/uncompressed where needed and wrappers emit AUTO_COMPRESS=FALSE or actual CLI disabling flags. Check manifest/content, not only .py extension or timestamp.
- Compare actual FROM source root, runtime MAIN_FILE constraints, committed/live version, and legacy ROOT_LOCATION. Valid stage subdirectories are allowed; warehouse main file is a filename within the chosen root, container paths can differ.
- FROM copies files at creation; re-uploading source alone does not update copied app state. Use supported version/source lifecycle; no guessed embedded @snow:// path or mandatory DROP/CREATE for every fix.
- Check whether live initialization/publication is missing using actual state. ADD LIVE VERSION FROM LAST is a mutation requiring approval; an absent field or blank page alone does not prove it is the fix.
- Diagnose AttributeError against actual st.__version__, module path/name, runtime support and dependency resolution. No universal default 1.22.0 or blanket latest-version fix; documented package availability varies by runtime.
- Warehouse dependencies use environment.yml/package picker; containers use supported pyproject/requirements mechanisms. Verify compatible version/operator syntax and runtime API support, rather than assuming an environment.yml applies everywhere.
- Temporary diagnostic source edits/output must be approved, avoid secrets, and be removed only if owned and no longer needed. Do not broadly download confidential stage files to arbitrary locations.
- Scope remediation to the demonstrated cause, preserving grants, consumers, prior versions and unrelated assets. Cleanup/replacement need independently verified ownership and explicit deletion authority.
- Missing objects/files or transfer failures require real structured evidence; do not use nonexistent SYSTEM$CHECK_FILE_EXISTS or grep fragments as runtime/import proof.
- After approved repair, verify effective source/dependencies and app behavior for the affected pages and intended viewers. Browser/app calls may execute SQL and need authorization.

### Execution Steps

1. Inspect exact failure and actual runtime/deployment source without mutating app/account state.
2. Test hypotheses with authorized source/path/compression/version/dependency evidence and distinguish missing checks.
3. Propose minimal supported fix with ownership, deployment and recovery boundaries.
4. Apply only approved repair, inspect effective source/version/package state, and test authorized affected behavior.
5. Record remaining failures/unverified checks and preventive helper/manifest checks without guaranteed resolution claims.

### Validation

- Root cause corroborated by actual stack/source/runtime evidence, not symptom-only assertions.
- Plain assets, source root/main file and active version match reviewed artifact.
- Actual API/dependency support confirmed for chosen runtime, no fixed default/latest-version assumption.
- No broad teardown, unsupported file-check function, implicit grant or unapproved app execution.
- Deliver evidence, scoped repair, actual results and limitations; unavailable browser/runtime checks remain unverified.

## References

- [Streamlit dependency management](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/dependency-management)
- [CREATE STREAMLIT](https://docs.snowflake.com/en/sql-reference/sql/create-streamlit)
- [ALTER STREAMLIT](https://docs.snowflake.com/en/sql-reference/sql/alter-streamlit)
- [PUT](https://docs.snowflake.com/en/sql-reference/sql/put)
- `109c-snowflake-app-deployment-troubleshooting.md` for broader diagnostics.
- `109b-snowflake-app-deployment-core.md` for preserving lifecycle.
