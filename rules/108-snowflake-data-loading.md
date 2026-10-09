---
schema_version: v4.0
rule_version: v5.0.0
description: Reliable staged bulk loading with explicit parsing, compatible validation, load evidence, and duplicate-safe recovery.
last_updated: 2026-10-07
keywords:
  - kw:COPY INTO
  - kw:stage management
  - kw:file format definition
  - kw:bulk load optimization
  - kw:VALIDATION_MODE
  - kw:ON_ERROR handling
  - kw:COPY_HISTORY monitoring
token_budget: ~1250
context_tier: High
depends:
  required:
    - 100-snowflake-core.md
---
# Snowflake Data Loading

## Scope

**What This Rule Covers:**
Internal/external stages, file preparation and formats, COPY INTO validation/error behavior, reconciliation, and safe recovery.

**When to Load This Rule:**
When designing/reviewing batch file ingestion, staging, load performance, or COPY error handling.

## Contract

### Inputs and Prerequisites

- Approved source files/manifest, encoding/format/compression, expected row/key counts, target schema, ingestion SLA, and error tolerance.
- Existing stage/format/target configuration and authorized roles. Check stage-type-specific READ/WRITE or USAGE, warehouse USAGE, target INSERT, parent access, and creation/integration permissions where needed.

### Mandatory

- Inspect existing stages/formats/targets before creating or altering them. Use approved storage integrations for external cloud access, not embedded cloud keys. Uploads, loads, purge, and external transfers require explicit scope authorization.
- Define parsing explicitly through a reviewed named or inline format: delimiters/quotes/headers, encoding/BOM, compression, timestamp/precision, and NULL/empty semantics. Do not require a new named object when an existing correct format suffices.
- Prepare files with a format-aware parser; CSV quoted multiline records cannot be safely split/concatenated with blanket line/head/tail recipes. Preserve headers and record boundaries, schema consistency, and manifest identity.
- Aim roughly for documented 100-250 MB compressed files where practical, balancing source latency, format, and actual compute parallelism. This is guidance, not a hard minimum or fixed warehouse-file-count/throughput guarantee.
- Use set-based COPY for staged files and INSERT SELECT for appropriate internal data; avoid row-by-row ingestion. Select intended file paths/patterns and columns/mappings; no unrestricted stage wildcard by default.
- Choose ON_ERROR = ABORT_STATEMENT, CONTINUE, or supported SKIP_FILE variants according to approved partial-load semantics. ABORT is not the option name; CONTINUE is not a universal production default. No invented 1% acceptable loss threshold.
- Validate first using a supported method. VALIDATION_MODE does not load rows and is incompatible with MATCH_BY_COLUMN_NAME; transformations also have validation restrictions. Use an authorized isolated alternative when needed, not an invalid combination or an unapproved production load.
- MATCH_BY_COLUMN_NAME suits compatible name-based loads, not every Parquet workflow; verify case handling and missing/mismatched fields. JSON VARIANT parsing/STRIP_OUTER_ARRAY and subcolumn extraction must match actual source semantics; stripping nulls can change meaning.
- Record COPY result status, files, parsed/loaded/rejected rows, errors and query IDs; inspect relevant COPY_HISTORY/load history with retention/latency caveats. Statement success or LIST alone is not complete ingestion.
- Reconcile source-to-target counts, keys, types, precision, timestamps, NULLs, and business totals, accounting for transformations/deduplication. Distinguish malformed/schema data from tolerated rejects and track quarantine/remediation owners.
- Load metadata is bounded, not business-key deduplication. FORCE, changed file content/names, aged history, and target replacement can reload data; inspect actual committed state before replay, especially after interruption or CONTINUE.
- Corrected-file reload must not duplicate previously accepted rows. Use an approved reconciliation/staging/keyed-application plan and retain immutable original manifests/error evidence; no blanket FORCE, TRUNCATE, table replacement, or purge for recovery.
- Compression defaults for data do not apply to application assets. Verify PUT/CLI flags and consumer requirements; keep .py/config assets uncompressed when deployment requires that. No asserted universal exception message.

### Execution Steps

1. Inspect files/manifest and current stage/target/format permissions; establish expected results and partial-load/replay policy.
2. Prepare bounded format-aware batches and explicit parsing/mapping with approved transfer paths.
3. Run only authorized compatible preflight checks; resolve parsing/schema errors before approved target loading.
4. Execute approved COPY, capture per-file/result evidence, and reconcile target integrity and load history.
5. Quarantine rejects, inspect uncertain committed state, and apply only scoped duplicate-safe remediation; remove files only with retention/deletion approval.

### Validation

- Intended files and format/mapping verified; encoding/quotes/multiline/NULL/type/time edge cases correct.
- Compatible preflight performed or gap disclosed; no MATCH_BY_COLUMN_NAME/VALIDATION_MODE misuse.
- Loaded/rejected/skipped outcomes reconciled to manifest and approved tolerance, not inferred from successful return.
- Safe rerun/recovery behavior tested with keys/counts, partial failures, history limits, and FORCE/PURGE disabled unless specifically approved.
- Output includes reviewed stage/format/COPY design, expected counts, query/file evidence, reject report, and unresolved checks. Unexecuted loads remain unverified.

## References

- [COPY INTO table](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table)
- [Preparing files and sizing](https://docs.snowflake.com/en/user-guide/data-load-considerations-prepare)
- [Stages](https://docs.snowflake.com/en/user-guide/data-load-stages-intro)
- [COPY_HISTORY](https://docs.snowflake.com/en/sql-reference/functions/copy_history)
- `121-snowflake-snowpipe.md` for continuous ingestion.
- `109b-snowflake-app-deployment-core.md` for application-asset compression.
