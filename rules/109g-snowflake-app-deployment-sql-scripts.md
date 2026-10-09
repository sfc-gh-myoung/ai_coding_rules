---
schema_version: v4.0
rule_version: v3.0.0
description: Scoped application transfer and lifecycle scripts with verified paths, compression, renderer binding, and publication.
last_updated: 2026-10-07
keywords:
  - kw:PUT AUTO_COMPRESS
  - kw:REMOVE before PUT
  - kw:CREATE STREAMLIT FROM
  - kw:stage path matching
  - kw:snow stage copy recursive
  - kw:embedded versioned stage
  - kw:snowpark
token_budget: ~1150
context_tier: Low
depends:
  required:
    - 109b-snowflake-app-deployment-core.md
---
# Snowflake App Deployment SQL Script Patterns

## Scope

**What This Rule Covers:**
Application asset PUT/CLI transfers, stage paths, runtime-aware CREATE/update/publication, and separately authorized cleanup scripts.

**When to Load This Rule:**
When authoring or reviewing Snowflake app deployment SQL and recursive transfer wrappers.

## Contract

### Inputs and Prerequisites

- Core deployment rule loaded, actual app/runtime/CLI version, source manifest/relative layout, approved target and current lifecycle state.
- Verified account/role/warehouse/stage permissions, renderer configuration, ownership, and mutation/deletion approvals.

### Mandatory

- Follow project SQL naming/layout and keep operations inspectable; modularity does not require DROP/REMOVE scripts for every app or unconditional teardown.
- Bind identifiers, stage prefixes, and local file URIs through supported template/parameter mechanisms. Snowflake CLI STANDARD placeholders differ from shell/Task rendering; inspect installed mode and quote each layer correctly.
- PUT requires supported client-side file transfer and an internal stage; do not attempt server-side access to a workstation path or execute uploads as read-only SQL validation.
- Explicitly disable automatic compression for application assets requiring plain source. Use AUTO_COMPRESS=FALSE or verified CLI equivalent; wrapper defaults and emitted flags must agree. Check actual transfer status/content, not only command authorization/history success.
- Preserve manifest relative directories; SQL PUT globs do not automatically traverse/preserve divergent paths. Verify actual recursive CLI option/path semantics rather than pin an arbitrary minimum version or assume all hidden files should upload.
- Do not upload secrets, caches, virtual environments, tests or unrelated repo data with a broad recursive directory. Include only reviewed app assets and required dependency/media files.
- Use an app-owned versioned stage directory where practical. FROM may point to a valid subdirectory; its contents define the source root. Warehouse MAIN_FILE is a filename within that root; container MAIN_FILE can be a supported relative subpath.
- Match dependency files to runtime (warehouse environment.yml, container supported pyproject/requirements). Verify package availability/API compatibility; no universal Streamlit version pin or global prohibition on nested source directories.
- FROM copies files at CREATE time; later source-stage edits do not automatically update the app. Inspect supported current version/update workflow and actual live source identity before publication.
- CREATE IF NOT EXISTS does not update an existing app. Prefer supported preserving lifecycle changes; replacement/drop needs explicit scope, ownership, grant/consumer review and recovery. Use appropriate publication/initialization for the actual Streamlit/notebook surface.
- ADD LIVE VERSION FROM LAST initializes/publishes applicable Streamlit versions; it is not an arbitrary stage-to-app synchronization command. Verify committed/live state and intended consumer access after approved publication.
- REMOVE is optional owned stale-file reconciliation, not mandatory before PUT and never blanket shared-stage clearing. Derive deletions from manifest differences and retain recovery assets until validated.
- Do not construct @snow:// paths or copy to an embedded URI solely from a guessed field. Verify documented file/lifecycle API support and grants before in-place updates; unverified methods remain proposals.
- Treat DROP/REMOVE/PUT/CREATE/ALTER and stage copying as mutations. Record exact resolved scope, per-file/object outcomes, failures and partial state; no unconditional upload/pass SELECT replacing real evidence.

### Execution Steps

1. Inspect current scripts/app/version and manifest, resolving source root, runtime, target and supported CLI/renderer.
2. Prepare scoped upload/update/publication scripts with explicit plain-source flags and preconditions; cleanup only when independently approved.
3. Validate script/template/config locally without transfers or account mutation; review fully resolved target/path policy.
4. With deployment authorization, transfer and verify manifest files, update/create using supported lifecycle, and publish the intended version.
5. Verify effective source/runtime/grants and authorized functionality; inspect uncertain state before scoped replay/recovery.

### Validation

- Exact paths/manifest and compression match source/runtime; no broad upload or shared-prefix delete.
- Renderer/version and privilege bindings verified; source-copy versus live-version behavior understood.
- Effective artifact matches reviewed files, entrypoint/dependencies present, app publication/access validated where authorized.
- No destructive default or guessed embedded-stage syntax; failures retained and unexecuted cloud checks disclosed.
- Deliver scripts/manifest, prerequisites, recovery scope, and actual verification outcomes.

## References

- [PUT](https://docs.snowflake.com/en/sql-reference/sql/put)
- [CREATE STREAMLIT](https://docs.snowflake.com/en/sql-reference/sql/create-streamlit)
- [ALTER STREAMLIT](https://docs.snowflake.com/en/sql-reference/sql/alter-streamlit)
- [Snowflake CLI stage operations](https://docs.snowflake.com/en/developer-guide/snowflake-cli/command-reference/stage-commands/overview)
- `109b-snowflake-app-deployment-core.md` for safe lifecycle boundaries.
- `102a-snowflake-sql-automation.md` for rendering and data-preserving SQL automation.
