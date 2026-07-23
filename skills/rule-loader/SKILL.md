---
name: rule-loader
description: Determines which rule files to load for a given user request by matching file extensions, directory paths, and keywords against RULES_INDEX.md. Handles foundation loading, domain matching (HARD layer), activity matching (SOFT layer), dependency resolution, and token budget management. Runs as the single source of truth for rule discovery — typically inside a discovery sub-agent that returns a metadata-only JSON manifest (never rule file contents). Use when loading rules, selecting rules for a task, resolving rule dependencies, or managing token budgets during rule loading.
version: 2.1.0
---

# Rule Loader

Selects and loads the correct set of rule files for any user request, ensuring consistent rule discovery across agents and sessions.

## Purpose

Given a user request, determine which rules to load, in what order, respecting dependencies and token budgets. This skill formalizes the rule-loading algorithm defined in AGENTS.md Steps 1-3 into a reusable, progressively-disclosed workflow.

## Use this skill when

- Loading rules for a new user request (first response or task switch)
- Resolving which domain rules match a file extension
- Determining activity rules from request keywords
- Managing token budgets when multiple rules are candidates
- Debugging why a rule was or was not loaded
- Building rule-loading logic into new agent configurations

## Inputs

### Required
- `user_request`: `string` - The user's message text to analyze for keywords, extensions, and technologies

### Optional
- `token_budget_limit`: `number` (default: `20000`) - Hard maximum token budget for loaded rules. A soft warning triggers at 75% of this value (default: 15,000) to begin evaluating Low-tier deferrals.
- `context_tier_filter`: `string` (default: `all`) - Filter by ContextTier: `all`, `critical`, `critical+high`, `critical+high+medium`

### Preconditions

- Working directory must be the **project root** (the directory that contains the `rules/` folder).
  All rule paths in this skill are resolved relative to `rules/` from the working directory.
  The skill does not perform root discovery; if the working directory is incorrect, foundation
  loading will fail with a "file not found" CRITICAL error.

### Input Validation

Before executing Phase 1:

1. `user_request` must be a non-empty string. If empty or whitespace-only: STOP with "No user request provided."
2. `token_budget_limit` must be a positive integer >= 5000. If below 5000: WARN "Token budget too low for foundation + any domain rule. Minimum recommended: 5000."
3. `context_tier_filter` must be one of: `all`, `critical`, `critical+high`, `critical+high+medium`. If invalid: WARN and default to `all`.

## Outputs

A `## Rules Loaded` section listing all selected rules with loading reasons, formatted per AGENTS.md Step 4.

**Example output:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/100-snowflake-core.md (dependency of 101)
- rules/101-snowflake-streamlit-core.md (keyword: Streamlit)
- rules/206-python-pytest.md (keyword: test)
- [Deferred: 204-python-docs.md - Low tier, not required for task]
```

## Manifest Output

When this skill runs inside a **discovery sub-agent**, its authoritative return
value is the fenced JSON manifest below (`rule-loader-manifest/v2` — default
emission since Phase 4 cutover; skill version ≥ `2.0.0`). It contains
**PATHS + METADATA ONLY — never rule file contents**. The `## Rules Loaded` prose
above is retained only for the inline-render (Step 2B) case; any Markdown table is
display-only and cannot satisfy Gate 2.

```json
{
  "schema_version": "rule-loader-manifest/v2",
  "request_fingerprint": "sha256:<hex of normalized user request>",
  "runtime": {
    "primitive": "Task|runtime-specific-direct-worker",
    "spawn_evidence": "<tool_call_id or runtime-visible spawn record>",
    "agent_id": "<worker agent id from the runtime result>"
  },
  "keywords_searched": ["<keyword-or-extension>"],
  "index_evidence": [
    {
      "kind": "grep|read_file_fallback",
      "target": "rules/RULES_INDEX.md",
      "query": "<exact grep/read expression>",
      "result_summary": "<matched filenames or none>"
    }
  ],
  "candidate_rules": [
    {
      "rule_path": "rules/202a-markdown-linting.md",
      "rule_name": "202a-markdown-linting.md",
      "reason_type": "extension|file|directory|activity_keyword|high_risk|dependency|optional_dependency",
      "reason": "candidate discovered before token-budget / ContextTier capping",
      "context_tier": "Low",
      "token_estimate": 2800,
      "layer": "SOFT",
      "required": false
    }
  ],
  "candidate_count": 1,
  "degraded": false,
  "failures": [
    {
      "stage": "domain_matching|activity_matching|dependency_resolution|token_budget",
      "message": "<failure text>",
      "fallback_used": "<fallback name or null>"
    }
  ],
  "load_sequence": [
    {
      "order": 1,
      "rule_path": "rules/000-global-core.md",
      "rule_name": "000-global-core.md",
      "reason_type": "foundation|extension|file|directory|activity_keyword|high_risk|dependency|project_context",
      "reason": "foundation",
      "context_tier": "Critical|High|Medium|Low",
      "token_estimate": 2550,
      "layer": "FOUNDATION|HARD|SOFT",
      "required": true,
      "read_required": true,
      "description": "One-sentence summary sourced from the rule's desc= field in RULES_INDEX.md. Optional; populated when desc= is present."
    }
  ],
  "deferred_rules": [
    {
      "rule_path": "rules/202a-markdown-linting.md",
      "rule_name": "202a-markdown-linting.md",
      "reason_type": "token_budget|context_tier_cap|duplicate|superseded|optional_dependency",
      "reason": "Deferred by token-budget management after dependency resolution",
      "context_tier": "Low",
      "token_estimate": 2800,
      "layer": "SOFT",
      "deferred_because": "ContextTier Low and total estimated context exceeded the configured token-budget cap"
    }
  ],
  "execution_hints": {
    "expected_turns_per_fixture": 3,
    "max_output_tokens": 1000,
    "note": "Advisory only. Calibrated from opus-4-6 baseline (91 turns / 35 fixtures ≈ 2.6 turns/fixture; 19k output tokens / 35 fixtures ≈ 543 tokens/fixture)."
  }
}
```

Schema rules:

- The fenced JSON block is the only authoritative manifest format. Markdown tables are display-only and cannot satisfy Gate 2.
- `load_sequence[*].rule_path` is repository-relative and must start with `rules/`; absolute paths are rendered by the main agent.
- `candidate_rules` is required, even when empty — the complete candidate universe after domain/activity/dependency discovery and before token-budget / ContextTier capping.
- `candidate_count` must equal `len(candidate_rules)`.
- `load_sequence` is dependency-resolved first, then token-budget-capped; duplicate `rule_path` entries are removed before ordering.
- `deferred_rules` is required, even when empty — every candidate removed by token-budget / ContextTier-cap, optional-dependency deferral, duplicate suppression, or supersession.
- **Completeness invariant:** every unique `candidate_rules[*].rule_path` must appear in exactly one of `load_sequence[*].rule_path` or `deferred_rules[*].rule_path`.
- `deferred_rules[*]` `reason`, `reason_type`, and `deferred_because` must be specific enough for the main agent to preserve the deferral reason in Gate 3 output.
- The manifest contains PATHS + METADATA ONLY. Rule file bodies never cross back.
- A malformed manifest, missing `runtime.agent_id` / `runtime.spawn_evidence` / `index_evidence` / `candidate_rules` / `candidate_count` / `deferred_rules`, invalid JSON, failed candidate-completeness validation, or any rule body content triggers Step 2B fallback.

See `examples/manifest-output.md` for a minimal valid example.

## Manifest v2 (`rule-loader-manifest/v2`)

Starting at skill version `2.0.0` and defaulted since Phase 4 cutover, the
authoritative manifest schema is `rule-loader-manifest/v2`. The v2 schema is
**additive** relative to v1 — no fields are removed. `rule-loader-manifest/v1`
manifests remain **accepted by the main agent** for legacy consumers that have
not yet been updated; the skill itself emits v2 by default.

**Added fields (all additive):**

```json
{
  "schema_version": "rule-loader-manifest/v2",
  "candidate_rules": [
    {
      "rule_path": "rules/206-python-pytest.md",
      "rule_name": "206-python-pytest.md",
      "reason_type": "activity_keyword",
      "reason": "kw:pytest matched user request",
      "context_tier": "High",
      "token_estimate": 1800,
      "layer": "SOFT",
      "required": false,
      "second_pass": {
        "evaluated": true,
        "confirmed": true,
        "confirmation_reason": "scope-overlap: pytest",
        "scope_excerpt_hash": "sha256:<hex>"
      }
    }
  ],
  "deferred_rules": [
    {
      "rule_path": "rules/210c-python-fastapi-deployment.md",
      "rule_name": "210c-python-fastapi-deployment.md",
      "reason_type": "second_pass_rejected",
      "reason": "no-scope-overlap: request tokens absent from Scope",
      "context_tier": "High",
      "token_estimate": 2200,
      "layer": "SOFT",
      "deferred_because": "Phase 3.5 second-pass rejected: Scope excludes user request"
    }
  ],
  "second_pass_evidence": [
    {
      "rule_path": "rules/206-python-pytest.md",
      "confirmed": true,
      "reason": "scope-overlap: pytest"
    },
    {
      "rule_path": "rules/210c-python-fastapi-deployment.md",
      "confirmed": false,
      "reason": "no-scope-overlap: request tokens absent from Scope"
    }
  ]
}
```

**v2 schema rules (additive to v1):**

- `schema_version` MUST equal `"rule-loader-manifest/v2"` when emitted by
  skill version ≥ `2.0.0`.
- Every entry in `candidate_rules[]` MUST carry a `second_pass` object.
  - For HARD candidates (`layer == "HARD"`): `{evaluated: false, confirmed: true, confirmation_reason: "hard-candidate-exempt"}`.
  - For SOFT candidates evaluated in Phase 3.5 (top-8 by keyword-match count):
    `{evaluated: true, confirmed: bool, confirmation_reason: string, scope_excerpt_hash: string}`.
  - For SOFT candidates beyond the top-8 cap:
    `{evaluated: false, confirmed: true, confirmation_reason: "cap-degraded-passthrough", degraded: true}`.
- `deferred_rules[*].reason_type` enum gains value `"second_pass_rejected"`
  (all v1 values remain valid).
- Root-level `second_pass_evidence: [{rule_path, confirmed, reason}]` MUST be
  present when v2 is emitted, even if empty (`[]` when no SOFT candidates were
  evaluated).
- **Completeness invariant is unchanged:** every unique
  `candidate_rules[*].rule_path` must appear in exactly one of
  `load_sequence[*].rule_path` or `deferred_rules[*].rule_path`.
- **HARD-never-filtered invariant:** a HARD candidate MUST NOT appear in
  `deferred_rules[]` with `reason_type: "second_pass_rejected"`. Second-pass
  rejection applies only to SOFT candidates.

**Backward compatibility:**

- The main agent accepts both `rule-loader-manifest/v1` and
  `rule-loader-manifest/v2` during the rollout window (schema-version
  detection on `schema_version` field). Phase 4 flips the default emission to
  v2 in this skill.
- A v2-emitting skill invoked by a v1-only consumer degrades gracefully: the
  consumer ignores the additive fields and reads `candidate_rules` +
  `load_sequence` + `deferred_rules` as before.
- Producing manifests without `schema_version`, or with an unrecognized
  value, triggers Step 2B fallback.

**Second-pass workflow:** see `workflows/second-pass-confirmation.md` for the
Phase 3.5 filter algorithm, cap, latency budget, and cache invariants that
produce the `second_pass` annotations and `second_pass_evidence` root list.

## Python Script Invocation (Primary Path)

Starting with skill version `2.1.0`, rule discovery is delegated to the
deterministic Python matcher (`src/ai_rules/rule_matcher/`).  The sub-agent
or skill executor invokes it as:

```bash
python -m ai_rules.rule_matcher \
  --keywords "streamlit,deploy" \
  --extensions ".py" \
  --paths "src/app.py" \
  --rules-dir ./rules \
  --format manifest-v2
```

**Exit codes:**
- `0` — success, at least one rule matched; stdout contains `rule-loader-manifest/v2` JSON.
- `1` — no rules matched; stdout contains valid JSON with `load_sequence: []`.
- `2` — fatal error (e.g. `--rules-dir` not found); stdout is empty, error on stderr.

**Fallback path (script unavailable or exits 2):** Return the empty-manifest
sentinel to the main agent:

```json
{
  "schema_version": "rule-loader-manifest/v2",
  "error": "matcher_unavailable",
  "load_sequence": [],
  "deferred_rules": [],
  "candidate_rules": [],
  "warnings": []
}
```

The main agent treats this as a Gate 2 failure and automatically falls through
to the Step 2B grep fallback (RULES_INDEX.md grep / read_file).  No manual
intervention is required.

**RULES_INDEX.md status:** Retained for the Step 2B fallback path. Deprecated
as the primary discovery mechanism.  Do not remove until all three model eval
suites pass their targets and AC-11 (round-trip parity) is verified.

## Workflow

Detailed phase content is loaded on demand from `workflows/` (progressive disclosure). Execute phases in order. Load workflow files only as needed.

### Phase 1: Foundation Loading
Always load `000-global-core.md`. Non-negotiable.

**Details:** `workflows/foundation-loading.md`

### Phase 2: Domain Matching
Match file extensions and directory paths to domain rules using RULES_INDEX.md.

**Details:** `workflows/domain-matching.md`

### Phase 3: Activity Matching
Search RULES_INDEX.md for keyword matches from the user request.

**Details:** `workflows/activity-matching.md`

### Phase 4: Dependency Resolution
For each selected rule, check `Depends` metadata and load prerequisites first.
**Closure loading is MANDATORY — recurse to fixpoint; do not return until all `required:` parents are included.**

**Details:** `workflows/dependency-resolution.md`

### Phase 5: Token Budget Management
Sum TokenBudget values, defer low-priority rules if over budget. `required:` dependency closure is loaded in addition to — and does not count against — the 3 domain/activity-selection cap, and a `required:` parent is never deferred for token pressure. If loading a mandatory closure would exceed the 20,000-token R4 ceiling, defer LEAF/optional selections first; a still-over-budget mandatory closure is escalated (see `workflows/token-budget.md` Q3-resolution), never silently trimmed. The budget ceiling applies to TOTAL per-response context (fixed floor + index match + selected rules), not just the selected rules — verify with `ai-rules tokens --context-estimate`.

**Details:** `workflows/token-budget.md`

## Matching Layers (HARD vs SOFT)

**HARD layer (mechanical, reproducible):** file extension (`ext=`), explicit file
(`file=`), directory (`dir=`), and the high-risk-action map. Resolved by
exact-string lookup against `rules/RULES_INDEX.md`. Same request → same
HARD rule set on every run. Covers safety-critical loads (.py, .sql, git, deploy, …).

**SOFT layer (best-effort, non-deterministic):** activity keywords extracted via
the fixed procedure in `workflows/activity-matching.md`, matched against per-rule
`kw:` frontmatter tokens. Results MAY vary run-to-run. Explicitly best-effort.

## Quick Validation

After rule selection, verify:

1. Foundation (000-global-core.md) is always present
2. Every loaded rule was actually read via `read_file` (not assumed)
3. Dependencies loaded before dependents
4. Total per-response context (fixed floor + index match + selected rules) does not exceed limit (default 20,000)
5. `required:` dependency closure is loaded in addition to — and does not count against — the 3 domain/activity-selection cap (cap counts LEAF/domain selections only); a `required:` parent is never deferred
6. Deferred rules are declared with reason

## Error Handling

**RULES_INDEX.md not found:**
- Warn, fall back to foundation + file-extension matching only
- Proceed in degraded mode

**Rule file not found:**
- If only matched rule: Report with options (A) correct path, (B) proceed without, (C) cancel
- If other rules loaded: Note failure, mark Gate 3 as PASSED, continue

**Dependency not found:**
- Skip the dependent rule, log warning
- Continue with remaining rules

**Token budget exceeded:**
- Defer Low tier rules first, then Medium tier
- Never defer Critical tier rules
- Declare deferrals in Rules Loaded section

## Examples

See `examples/` for complete walkthroughs:
- `streamlit-dashboard.md` - "Write tests for my Streamlit dashboard"
- `python-api.md` - "Add a FastAPI endpoint"
- `multi-domain.md` - Cross-domain request (Snowflake SQL + Python)
- `token-budget-deferral.md` - Token budget deferral with Low-tier rule deferred

## Related

- **AGENTS.md** - Bootstrap protocol that invokes this loading logic (Steps 1-3)
- **RULES_INDEX.md** - The agent discovery index (grep target). Generated from rule frontmatter.
- **002h-claude-code-skills.md** - Skill authoring standards this skill follows
- **003-context-engineering.md** - Token budget and attention management principles

## Version History

See `CHANGELOG.md`.
