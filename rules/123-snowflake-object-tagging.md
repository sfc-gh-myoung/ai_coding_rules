---
schema_version: v4.0
rule_version: v5.0.0
description: "Governed tag taxonomy, assignment/inheritance, supported masking bindings, coverage, attribution, and lifecycle impact."
last_updated: 2026-10-07
keywords:
  - kw:object tagging
  - kw:tag inheritance
  - kw:tag-based masking
  - kw:ALLOWED_VALUES
  - kw:TAG_REFERENCES
  - kw:cost attribution tags
token_budget: ~1450
context_tier: High
depends:
  required:
    - 105-snowflake-cost-governance.md  # Resource monitors and cost optimization
    - 107-snowflake-security-governance.md  # Access control and security policies
---
# Snowflake Object Tagging Best Practices

## Scope

**What This Rule Covers:**
Reusable classification/attribution taxonomy, tag privileges and effective values, inheritance versus propagation, masking, audits, and safe removal.

**When to Load This Rule:**
When designing/applying tags, assessing coverage or lineage, configuring tag-based masking, or reconciling cost/access evidence.

## Contract

### Inputs and Prerequisites

- Approved taxonomy/values, steward/ownership model, exact tag/object identities, current assignments/inheritance/propagation, and policy consumers.
- Creation/APPLY/object ownership or supported global privileges and parent access; actual edition support for propagation/masking.
- Explicit assignment/policy/classification/lifecycle mutation scope and authorized metadata/audit reads.

### Mandatory

- Reuse a documented concept/owner rather than proliferating synonymous team tags. Choose centralized/decentralized/hybrid stewardship from actual responsibilities; naming/schema examples are organization policy, not mandatory GOVERNANCE.TAGS creation.
- Tags are schema-level metadata objects; values are strings. Define ALLOWED_VALUES for bounded categories where appropriate, not every free-form identifier. Current documented bounds are 5000 allowed values and 256 characters per value; inspect actual list with SYSTEM$GET_TAG_ALLOWED_VALUES.
- Changing allowed values does not rewrite existing assignments. Audit/remediate now-disallowed values deliberately. Allowed-value order can affect supported propagation conflict handling; review before reordering.
- Respect documented 50-tag per-object and 50-different-tag combined-column limits, plus 100 tag/entity associations per table/view statement. Count applicable entities and current assignments rather than assuming fifty per individual column or silently consolidating protection tags.
- Distinguish CREATE TAG, tag OWNERSHIP, specific APPLY plus target ownership, and supported global APPLY TAG. Future grants on tags are not supported. No automatic role/grant escalation or broad APPLY privilege merely to make assignment succeed.
- Hierarchical inheritance follows securable containment; table columns can inherit table/schema/database/account tags. A derived view does not inherit a source-table tag solely from its SQL dependency; dependency/data-movement propagation is a separate configured feature.
- For automatic propagation inspect supported objects/operations, edition, PROPAGATE mode, conflicts and manual/inherited/classified overrides. Check effective values and apply_method/lineage after changes instead of promising every derived/replicated object is protected.
- Metadata tags alone do not authorize or restrict data access. Tag-based masking requires an actual supported masking-policy binding with matching column type. Existing direct masking takes precedence under documented rules; test all consumer identities and type cases.
- A tag can hold distinct masking policies by data type, not an automatic policy selection per tag value. One STRING policy on a semantic-category tag can affect all tagged STRING categories; branch using documented tag lookup or use separate approved tags where needed. Preserve compatible output types and explicit entitlements.
- Do not invent ALTER TAG SET ROW ACCESS POLICY. Row-access policies attach to supported tables/views and may inspect trusted entitlements/tag values where appropriate; the tag assignment itself is not automatic row isolation.
- Sensitive-data classification must use current documented procedure/profile interfaces and approved sampling/tag application. Do not blindly call SYSTEM$CLASSIFY as a SELECT or assume system tags accept arbitrary custom masking attachments. Classification labels need review and policy enforcement evidence.
- Audit direct/effective inherited/propagated tags using appropriate TAG_REFERENCES, TAG_REFERENCES_WITH_LINEAGE or SYSTEM$GET_TAG; inspect function/view scope/access/latency. Tag references are not exhaustive data lineage or proof of policy effectiveness.
- Coverage checks join full database/schema/object/domain/column and tag identities, exclude dropped objects where applicable, and distinguish direct from effective assignments. Define critical-object denominator/coverage goal from policy; no fabricated universal 90% success threshold.
- Chargeback and access-history joins need stable identities, matching time grain and deduplication. Current tags/object names cannot establish historical classification or allocations at time of usage; reconcile sums and direct/base object/column access separately.
- Clone/LIKE/replication behavior is operation/scope dependent. Inspect copied/remapped tag/policy references and target permissions; inherited defaults can change under the destination hierarchy. Do not assume policy attachments and cross-database definitions replicate identically.
- Unset/drop/replacement can remove protection triggers and attribution. Inspect dependents and effective attachments, obtain approval, retain beforeimages and verify consumers. Documented DROP TAG grace/UNDROP is recovery assistance, not permission to remove controls.

### Execution Steps

1. Inventory existing taxonomy, assignments/lineage, effective policies, ownership and consumer requirements through approved reads.
2. Design minimal reuse/allowed-value/assignment scope with explicit inheritance/propagation and masking/row-policy boundaries.
3. Prepare authorized versioned changes and recovery, including quota/conflict and clone/replication effects.
4. Apply only approved changes; inspect effective values/attachments and test allowed/denied consumers independently.
5. Reconcile coverage/cost/access evidence and report unresolved historical attribution or policy gaps.

### Validation

- Taxonomy/values/owners and actual privileges match policy; supported limits and allowed-value history are respected.
- Effective inheritance/propagation and direct overrides are observed on actual targets, not inferred from a tag definition.
- Masking types/entitlements and row isolation function through consumer paths; no tag-only security claim.
- Coverage, historical cost/access joins and clone/replication behavior are scoped and reconciled without fanout.
- Output includes definitions/assignments, impact/ownership, tests and gaps; no unapproved classification, grant, or protection removal.

## References

- [Tag fundamentals and quotas](https://docs.snowflake.com/en/user-guide/object-tagging/introduction)
- [Tag DDL, allowed values, access, and lifecycle](https://docs.snowflake.com/en/user-guide/object-tagging/work)
- [Inheritance](https://docs.snowflake.com/en/user-guide/object-tagging/inheritance)
- [Automatic propagation](https://docs.snowflake.com/en/user-guide/object-tagging/propagation)
- [Tag-based masking](https://docs.snowflake.com/en/user-guide/tag-based-masking-policies)
- [Row access policies](https://docs.snowflake.com/en/user-guide/security-row-intro)
- [Monitoring tags](https://docs.snowflake.com/en/user-guide/object-tagging/monitor)
