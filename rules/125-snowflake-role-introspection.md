---
schema_version: v4.0
rule_version: v5.0.0
description: "Typed and safely quoted account/database role inspection, explicit grant versus hierarchy semantics, and visibility-aware audits."
last_updated: 2026-10-07
keywords:
  - kw:role introspection
  - kw:account roles vs database roles
  - kw:SHOW GRANTS syntax
  - kw:SQL compilation error 000906
  - kw:role type detection
  - kw:RBAC automation
  - kw:rbac
token_budget: ~1300
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Core foundation patterns
    - 100-snowflake-core.md  # Snowflake foundation patterns
  optional:
    - 107-snowflake-security-governance.md  # RBAC and privilege patterns
    - 200-python-core.md  # Python development patterns
---
# Snowflake Role Introspection

## Scope

**What This Rule Covers:**
Account/database role identity, quoted identifiers, safe grant inspection, upward/downward hierarchy traversal, and incomplete audit evidence.

**When to Load This Rule:**
When automating role/grant audits, handling qualifier errors, or evaluating role inheritance. Read `107-snowflake-security-governance.md` for access design and `200-python-core.md` for Python implementation.

## Contract

### Inputs and Prerequisites

- Explicit role type or role inventory metadata, canonical identifier components/database context, current session role and intended inspection direction.
- Authorized read-only connection/client, visibility scope and current command/schema documentation; no implied grants/role switches.
- Expected result shape, deduplication/traversal limits and precise error/query evidence.

### Mandatory

- Prefer explicit type from authoritative inventory/caller contract, not dot heuristics. Account roles have one identifier component; database roles use database.role, not database.schema.role. A database role can be relative under a known database context, so lack of a dot does not prove account type.
- Preserve quoted identifier semantics: one quoted component containing a dot is not two components; separately quoted database/role components are qualified. Escaped double quotes, case and database context must survive structured parsing. Never strip outer quotes and split blindly.
- Validate resolved identity against authorized inventory and safely quote every component. A name returned by SHOW can still contain SQL punctuation; trusted origin does not make raw f-string SQL interpolation safe. Do not concatenate arbitrary user names or switch to another query route after validation fails.
- Choose type-specific supported grant command/API: account-role TO lists explicit privileges/roles granted to it, OF lists grantees. Database-role inspection needs its supported current interface; do not assume generic documentation lists every variant or claim live compilation without a permitted check.
- Current generic SHOW GRANTS reference does not list TO/OF DATABASE ROLE in its syntax, while listing SHOW FUTURE GRANTS TO DATABASE ROLE. Existing database-role variants must be verified against applicable interface/version or clearly marked unverified; a documentation omission alone doesn't prove the feature absent.
- Introspection is read-only; no grant, revoke, ownership transfer, role creation, elevation or production test mutation to make an audit succeed. Missing visibility should produce an incomplete report, not an empty-grants safety conclusion.
- SHOW outputs explicit grants, not a fully expanded effective privilege closure. Future grants differ from current object access; object/role OWNERSHIP is not synonymous with inherited privileges. Primary/secondary roles and policy effects matter for actual authorization.
- For downward traversal follow typed role/database-role membership edges from grants TO; for upward traversal follow OF grantees. Roles granted to a parent convey privileges upward; users/shares/app/service roles are distinct node kinds, not every result is another account role.
- Traverse a bounded work queue with visited keys including type/database/quoted identity. Avoid appending to the list being iterated; deduplicate grants and preserve path provenance/shared ancestors. Detect cycles/malformed edges and report truncation rather than silently dropping coverage.
- Read actual result columns from cursor metadata or a dictionary cursor. SHOW postprocessing columns are lowercase and need quoting in SQL. Do not claim list-of-dictionaries while returning positional tuples.
- Inspect structured exception errno/SQLSTATE/message/query ID, not string-match 000906 and automatically try the opposite role type. Qualifier failure can mean malformed identity or wrong syntax; access/network errors require different diagnosis. Retain original error and verify type before a bounded read-only retry.
- Record inspection time, current identity/role, commands/sources, visibility/latency, unsupported variants and limits. Account Usage can be delayed; grants can change mid-traversal, and a non-atomic audit should disclose that consistency limit.

### Execution Steps

1. Read current inventory/type metadata and caller intent; resolve canonical components, context and permitted visibility.
2. Build safely quoted supported inspection operations and validate expected result/error shape without privilege changes.
3. Fetch permitted explicit grants and bounded typed hierarchy closure, retaining provenance and incompleteness.
4. Test quoted dots/quotes/case, relative database roles, malformed names, inaccessible objects, shared ancestors and cycles in fixtures.
5. Report actual grants/paths and remaining syntax/access/runtime gaps; verify live variants only if separately permitted.

### Validation

- Account/database identity and quote/qualification handling are correct; no three-component database role or injection-prone concatenation.
- TO/OF/future/current/effective semantics and role edge directions are explicit.
- Traversal terminates/deduplicates and reports incomplete visibility, limits and changing state.
- Structured errors retain original evidence without speculative alternate-type retry or self-grants.
- Output includes typed identity, actual grant result shape/provenance and limitations. Uncompiled command variants stay unverified.

## References

- [SHOW GRANTS scope, output, and listed variants](https://docs.snowflake.com/en/sql-reference/sql/show-grants)
- [SHOW DATABASE ROLES](https://docs.snowflake.com/en/sql-reference/sql/show-database-roles)
- [Access control and database-role identity](https://docs.snowflake.com/en/user-guide/security-access-control-overview)
- [Quoted identifiers](https://docs.snowflake.com/en/sql-reference/identifiers-syntax)
