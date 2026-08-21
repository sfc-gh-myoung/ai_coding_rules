# Rendered Review Format v1

Canonical layout for `rule-review-result/v1` Markdown output.

The Markdown is generated **deterministically** by `ai-rules review-artifact render`.
Never edit the rendered Markdown directly. On any mismatch, regenerate from the canonical JSON.

## Output Structure

```
# Rule Review: <rule_name>

**Review Date:** YYYY-MM-DD
**Review Mode:** FULL|FOCUSED|STALENESS
**Model:** <model-slug>
**Schema:** rule-review-result/v1
**Renderer:** ai-rules review-artifact render/v1

## Executive Summary

| Dimension | Raw (0-10) | Weight | Points | Max |
|-----------|------------|--------|--------|-----|
| Actionability           | N | 3.0 | N   | 30  |
| Rule Size               | N | 2.5 | N   | 25  |
| Parsability             | N | 1.5 | N   | 15  |
| Completeness            | N | 1.5 | N   | 15  |
| Consistency             | N | 1.0 | N   | 10  |
| Cross-Agent Consistency | N | 0.5 | N   | 5   |
| **TOTAL**               |   |     | **N** | **100** |

**Verdict:** <VERDICT> (<score>/100)
**Blocking Issues:** <N>
**Hard Caps Applied:** <None | description>

<executive_summary[0].text>
<executive_summary[1].text>
...

## Blocking Issues

(present only if blocking_issue_count > 0)

### 1. [CRITICAL|HIGH] <finding_id>

<claim.text>

- **Evidence (source|docs):** `path:line`
  > "<quote>"
**Recommendation:** <recommendation>

...

## Additional Findings

(present only if non-blocking findings exist)

- **[MEDIUM|LOW] <finding_id>:** <claim.text>

---

<!-- integrity footer — do not edit -->
<!-- schema: rule-review-result/v1 -->
<!-- json-path: <repo-relative-path-to-json> -->
<!-- sha256: <sha256-of-canonical-json> -->
<!-- renderer: ai-rules review-artifact render/v1 -->
<!-- review-artifact: end -->
```

## Integrity Footer Fields

| Field | Description |
|-------|-------------|
| `schema` | The schema version: always `rule-review-result/v1`. |
| `json-path` | Repo-relative path to the canonical JSON artifact. |
| `sha256` | SHA-256 of the canonical JSON (keys sorted, 2-space indent, UTF-8). |
| `renderer` | Renderer identity: always `ai-rules review-artifact render/v1`. |
| sentinel | `<!-- review-artifact: end -->` — must be the final line. |

## Verification

`ai-rules review-artifact verify-pair --input <review.json> --markdown <review.md>`

Re-renders the JSON and compares byte-for-byte.
Exits 3 on any mismatch (hand-edited Markdown, changed JSON, or missing sentinel).

## Rules

1. **One semantic authority.** All substantive review content lives in the canonical JSON.
   The Markdown contains no independent semantics.
2. **Never hand-edit rendered Markdown.** Edits are silently overwritten on the next render.
   To change the review, edit the JSON and re-render.
3. **Same-stem naming.** `<rule-id>-<review-id>.json` pairs with `<rule-id>-<review-id>.md`.
   A Markdown file without a same-stem JSON sibling is an orphan diagnostic, not an accepted artifact.
4. **Publish order.** Markdown is published first; canonical JSON last.
   Automation discovers accepted artifacts from `.json` files only.
5. **Rejected artifacts.** Rejected JSON is preserved as `<stem>-rejected-<N>.json`.
   Never overwrite a rejected artifact.
