# Retry Contract — rule-review-result/v1

Specifies how LLM-authored review JSON is repaired and re-submitted. All
retry logic uses `ai-rules review-artifact verify-repair` to enforce that
only the declared pointers changed.

## Exit-Code Routing

| Exit | Class | Recovery |
|------|-------|----------|
| 0 | Success | Publish the pair (render Markdown, verify pair, publish). |
| 1 | LLM-authored schema or semantic violation | Preserve rejected JSON. Request bounded repair of `repairable_paths`. Retry up to cap. |
| 2 | Missing, unreadable, invalid UTF-8, or invalid JSON | Retry producer if no artifact exists. Otherwise escalate as I/O failure. Do not consume a repair slot. |
| 3 | Deterministic implementation or pair-integrity defect | **Stop immediately. Do not consume any LLM retry.** File a defect report. |
| 4 | Repair-integrity violation | Preserve candidate JSON. Retry within the repair cap. |

## Retry Cap

Maximum **2** repair attempts per artifact. After 2 failures:
- Preserve the final rejected JSON as `<stem>-rejected-<N>.json`.
- Stop and report the unresolved issues to the caller.
- Never fall back to a hand-authored Markdown artifact.

## Allowed Repair Pointers

The LLM may touch only the fields listed in `repairable_paths` from the
`validate` diagnostic output. Typical repairable paths:

| Path | Condition |
|------|-----------|
| `/dimensions` | Wrong dimension set, wrong weights, wrong points arithmetic |
| `/score` | Score does not match sum of dimension points |
| `/verdict` | Verdict does not match canonical threshold for score |
| `/blocking_issue_count` | Count does not match critical/high finding count |
| `/findings/<id>/claim/evidence` | Blocking finding has no source or docs evidence |
| `/findings/<id>/claim/evidence/<n>/locator` | Source locator is not in `path:line` format |

## Rejected Repair Suffixes (Terminal — Exit 3)

These conditions are deterministic defects, not LLM errors. They stop
retry immediately regardless of repair cap:

- Integrity sentinel absent or malformed (`<!-- review-artifact: end -->` missing).
- SHA-256 in footer does not match the canonical JSON encoding.
- Markdown modified independently of JSON (pair-integrity violation).
- `schema_version` field is not exactly `rule-review-result/v1`.
- Renderer or schema implementation raised an exception.

## Rejected Input Handling

When a review artifact fails exit-1 validation:

1. Write the rejected artifact to `<stem>-rejected-<N>.json` (N = 1, 2, …).
2. Invoke `ai-rules review-artifact validate --input <rejected.json>` and
   capture the typed diagnostic (includes `repairable_paths`).
3. Request a field-level repair: only the `repairable_paths` may change.
4. Invoke `ai-rules review-artifact verify-repair --baseline <rejected.json>
   --candidate <candidate.json> --allowed-path <path>...` to confirm drift
   is confined to the declared paths.
5. If verify-repair exits 4 (unauthorized drift), preserve candidate and
   retry within cap.
6. If verify-repair exits 0, re-run `validate` on the candidate.
7. If still failing after the cap, stop. Never publish a Markdown-only fallback.

## Markdown-Only Fallback — Prohibited

Publishing a hand-authored Markdown file when canonical JSON validation
fails is **prohibited**. Markdown without a same-stem JSON sibling is an
orphan diagnostic artifact, not an accepted review. Automation ignores it.
