# LoadTrigger Guidelines — DEPRECATED TOMBSTONE

> **TOMBSTONE:** This rule has been deprecated and merged into `002-rule-governance.md`.
> It is retained for one release cycle to preserve inbound `Depends:` links.
> Do NOT load this rule. Load `002-rule-governance.md` instead.

## Metadata

**SchemaVersion:** v3.4
**RuleVersion:** v2.0.0
**LastUpdated:** 2026-07-12
**Keywords:**
**TokenBudget:** ~50
**ContextTier:** Low
**Depends:**

## Scope

**What This Rule Covers:**
DEPRECATED. Active load-trigger guidance has been merged into `002-rule-governance.md`
(§ LoadTrigger Guidelines). This tombstone file will be removed in the next release cycle.

**When to Load This Rule:**
- Never. Use `002-rule-governance.md` for LoadTrigger / keyword-trigger guidance.

## Migration

All LoadTrigger guidance — trigger types (`ext:`, `file:`, `dir:`, `kw:`), best practices,
anti-patterns, and the decision process — is now in **`002-rule-governance.md`**,
§ LoadTrigger Guidelines.

If you have `required:002i-rule-loadtrigger.md` in a rule's `**Depends:**`, update it to
`optional:002-rule-governance.md` (or remove it if the governance rule is already listed).
