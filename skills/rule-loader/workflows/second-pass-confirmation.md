# Second-Pass Confirmation (Phase 3.5)

**Manifest schema:** `rule-loader-manifest/v2`
**SKILL.md version:** ≥ 2.0.0
**Position in pipeline:** after activity matching (Phase 3), before dependency resolution (Phase 4).

## Purpose

Reduce false-positive SOFT (activity-keyword) matches by opening each candidate
rule's `## Scope` block and checking for semantic overlap with the user's
request. HARD candidates (ext / file / dir / high-risk / dependency-closure)
are **never** filtered here — they remain exempt.

## Input Contract

- `candidate_rules[]` — the union of HARD and SOFT matched rules from
  Phases 1–3 (`domain-matching`, `activity-matching`). Each entry carries
  `path`, `layer` (`hard` | `soft`), and `keyword_matches`.
- `request_text` — the user's query verbatim, passed through unmodified from
  the main agent.

The stage MUST NOT mutate `candidate_rules[]` in place; a new post-filter
list plus `second_pass_evidence` is returned.

## Output Contract

- `candidate_rules[]` structure is unchanged (schema-compatible with v1).
- Each **SOFT** candidate gains a `second_pass` annotation:

  ```yaml
  second_pass:
    evaluated: bool          # true if Scope was read and scored
    confirmed: bool          # false → moved to deferred_rules[]
    confirmation_reason: string
    scope_excerpt_hash: string   # sha256 of the extracted Scope excerpt
  ```

- **HARD** candidates get a stub annotation, un-evaluated:

  ```yaml
  second_pass:
    evaluated: false
    confirmed: true
    confirmation_reason: "hard-candidate-exempt"
  ```

- **Rejected SOFT** candidates are **moved** to `deferred_rules[]` with
  `reason_type: "second_pass_rejected"` and a short `reason` string quoting
  the mismatch. They MUST NOT remain in `candidate_rules[]`.
- **Cap overflow** SOFT candidates (position > 8) receive
  `second_pass: {evaluated: false, confirmed: true, degraded: true}` and pass
  through unfiltered.
- **Completeness invariant:** every input candidate appears in exactly one of
  `load_sequence` or `deferred_rules` after this stage — nothing is dropped
  silently.
- `second_pass_evidence: [{rule_path, confirmed, reason}]` is appended at
  manifest root for Gate-2 attestation.

## Filter Algorithm

1. **Partition.** Split `candidate_rules[]` into `hard[]` (skip) and `soft[]`
   (evaluate). Preserve keyword-match count ordering inside `soft[]`.
2. **Read Scope.** For each `soft[i]` up to i < 8:
   - `read_file` the rule.
   - Extract the `## Scope` block — specifically the
     `When to Load This Rule` and `What This Rule Covers` prose. Cap the
     extracted excerpt at ≤500 tokens (truncate on paragraph boundary).
   - Compute `scope_excerpt_hash = sha256(excerpt)`.
3. **Score.** Tokenize `request_text` into three buckets: verb tokens,
   technology tokens, domain-noun tokens (stemmed, lowercased).
   - **≥1 direct match** on a verb OR technology token against the Scope
     excerpt → `confirmed: true`, reason `"scope-overlap: <matched-token>"`.
   - **Zero matches** → `confirmed: false`, reason
     `"no-scope-overlap: request tokens absent from Scope"` → move to
     `deferred_rules[]`.
4. **Ambiguous passthrough.** If the Scope excerpt is short (<80 tokens after
   stopwords) or reads as a broad-domain rule (e.g., contains
   `"ALWAYS"` / `"foundation"` / `"every response"`), set
   `confirmed: true`, reason `"ambiguous-passthrough"`. Prefer a false-positive
   pass-through over a false-negative filter.

## HARD Candidate Exemption

HARD candidates (`layer == "hard"`) — matched via `ext:`, `file:`, `dir:`,
high-risk action map, or `depends.required:` closure — are never opened,
never scored, and never moved to `deferred_rules[]` by this stage. Their
`second_pass.confirmation_reason` is fixed to `"hard-candidate-exempt"`.

Rationale: HARD triggers are typed, precise, and already justified by
`domain-matching`; running a semantic filter over them adds latency without
precision gain and risks dropping mandatory rules.

## Cap and Degraded-Mode

- **Cap:** Evaluate at most the **top-8 SOFT candidates** by keyword-match
  count.
- **Overflow (position ≥ 8):** annotate
  `second_pass: {evaluated: false, confirmed: true, degraded: true}` and
  pass through into `load_sequence`. Do not read Scope; do not defer.
- **Rationale:** the cap bounds worst-case latency and cost. Degraded
  passthrough preserves the completeness invariant (nothing dropped) and
  favors recall over precision for tail candidates.
- **Signal:** if any candidate is annotated `degraded: true`, add
  `second_pass_evidence` entry with `reason: "cap-degraded-passthrough"` so
  Gate-2 attestation surfaces the degradation.

## Latency Budget

- Per-candidate Scope read: **≤500 tokens extracted**.
- Total second-pass budget inside the discovery sub-agent: **≤4,000 tokens**
  (8 candidates × ~500 tokens = 4,000).
- Reading only the `## Scope` block (not the whole rule) is what keeps
  per-candidate cost bounded. Any implementation that reads the full file
  violates this workflow.

## Cache Invariants

- Scope excerpts and their scores are **never cached** across requests.
- Every invocation reads fresh via `read_file` — Scope prose is edited over
  time (rules are living documents), and stale cache entries would resurrect
  filtered candidates or drop newly-in-scope ones.
- `scope_excerpt_hash` is emitted for auditability only; it is not a cache
  key.
- The main agent must not persist `candidate_rules[*].second_pass` across
  sessions.

## Manifest Impact (`rule-loader-manifest/v2`)

- Per-candidate fields added (SOFT + HARD):
  `second_pass: {evaluated, confirmed, confirmation_reason, scope_excerpt_hash}`.
- `deferred_rules[*].reason_type` enum gains value
  `"second_pass_rejected"`.
- Root-level field added:
  `second_pass_evidence: [{rule_path, confirmed, reason}]`.
- `schema_version` bumps to `"rule-loader-manifest/v2"`.
- **Backward compatibility:** v1 manifests remain accepted by the main agent
  during the rollout window. v2 is emitted only when the skill advertises
  version ≥ `2.0.0`.

## Example

**Request:** `"Add pytest fixtures for the FastAPI auth router"`

**Candidate rules (post-Phase-3):**

| Rule | Layer | kw matches |
|---|---|---|
| `206-python-pytest.md` | soft | 3 |
| `210c-python-fastapi-deployment.md` | soft | 2 |
| `950-dbt-core.md` | soft | 1 |
| `200-python-core.md` | hard (ext: `.py`) | n/a |

**Second-pass execution:**

- `200-python-core.md` — HARD, skipped. `confirmation_reason: "hard-candidate-exempt"`.
- `206-python-pytest.md` — SOFT. Scope mentions `"pytest fixtures"`,
  `"test authoring"`. Direct match on `pytest` → **accepted**.
  `confirmation_reason: "scope-overlap: pytest"`.
- `210c-python-fastapi-deployment.md` — SOFT. Scope mentions
  `"gunicorn / uvicorn worker deployment"`, `"multi-stage docker build"`.
  No overlap with `pytest` / `fixtures` / `auth-router` → **rejected**.
  Moves to `deferred_rules[]` with
  `reason_type: "second_pass_rejected"`,
  `reason: "no-scope-overlap: request tokens absent from Scope"`.
- `950-dbt-core.md` — SOFT. Scope mentions `"dbt-project-object"`,
  `"snow-dbt-deploy"`. No overlap → **rejected**, moved to `deferred_rules[]`.

**Resulting `second_pass_evidence` (root):**

```yaml
second_pass_evidence:
  - rule_path: rules/206-python-pytest.md
    confirmed: true
    reason: "scope-overlap: pytest"
  - rule_path: rules/210c-python-fastapi-deployment.md
    confirmed: false
    reason: "no-scope-overlap: request tokens absent from Scope"
  - rule_path: rules/950-dbt-core.md
    confirmed: false
    reason: "no-scope-overlap: request tokens absent from Scope"
```

## Failure Modes

- **Scope block missing.** If the candidate rule has no `## Scope` heading,
  treat as ambiguous passthrough (`confirmed: true`,
  `confirmation_reason: "scope-block-missing"`). Do not defer. Log a
  `second_pass_evidence` entry so the omission is visible.
- **`read_file` error.** On any I/O failure, treat as ambiguous passthrough
  (`confirmed: true`, `confirmation_reason: "read-error-passthrough"`). Never
  defer a candidate on read failure — favor recall.
- **Budget exhaustion.** If the cumulative token budget reaches 4,000 before
  all top-8 candidates are scored, remaining unscored SOFT candidates are
  passed through with `degraded: true`.

## Related Workflows

- [`activity-matching.md`](activity-matching.md) — produces the SOFT
  candidate list this stage consumes.
- [`domain-matching.md`](domain-matching.md) — produces the HARD candidate
  list (never filtered here).
- [`dependency-resolution.md`](dependency-resolution.md) — runs after this
  stage on the confirmed candidates.
- [`token-budget.md`](token-budget.md) — the R4 token ceiling still applies;
  second-pass budget is a sub-budget inside the discovery sub-agent.
