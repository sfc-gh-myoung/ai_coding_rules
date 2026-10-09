---
name: rule-loader
description: Determines which rule files to load for a given user request by matching file extensions, directory paths, and keywords using the deterministic Python matcher. Handles foundation loading, domain matching (HARD layer), activity matching (SOFT layer), dependency resolution, and token budget management. Runs as the single source of truth for rule discovery - typically invoked by the plugin hook, returning a metadata-only JSON manifest (never rule file contents). Use when loading rules, selecting rules for a task, resolving rule dependencies, or managing token budgets during rule loading.
version: 2.2.2
---

# Rule Loader

Selects and loads the correct set of rule files for any user request, ensuring consistent rule discovery across agents and sessions.

## Purpose

Given a user request, determine which rules to load, in what order, respecting dependencies and token budgets. The plugin hook runs the deterministic matcher and returns a manifest; this skill provides override and clarification capability when the hook result needs adjustment.

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

Two invocation modes:

- **Repo/CLI mode** (cwd is the repository root): rule paths resolve relative to `rules/` from the working directory. Foundation loading fails with a "file not found" CRITICAL error if the working directory is not the repo root.
- **Plugin-installed mode** (rules bundled under the plugin install path): the plugin hook passes an absolute `--rules-dir` (the installed plugin's `rules/`) and rewrites matched rule paths to canonical absolute form before injection. The consuming model reads the emitted absolute paths directly.

### Input Validation

Before executing Phase 1:

1. `user_request` must be a non-empty string. If empty or whitespace-only: STOP with "No user request provided."
2. `token_budget_limit` must be a positive integer >= 5000. If below 5000: WARN "Token budget too low for foundation + any domain rule. Minimum recommended: 5000."
3. `context_tier_filter` must be one of: `all`, `critical`, `critical+high`, `critical+high+medium`. If invalid: WARN and default to `all`.

## Outputs

A `## Rules Loaded` section listing all selected rules with loading reasons, formatted per the rule-loading contract in `rules/000-global-core.md`.

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

When this skill runs inside a **discovery sub-agent**, its authoritative return value is the `rule-loader-matcher/v1` fenced JSON block (**PATHS + METADATA ONLY: never rule file contents**). The `## Rules Loaded` prose above is retained only for the inline-render (Step 2B) case; Markdown tables are display-only and cannot satisfy Gate 2.

**Required top-level fields:** `schema_version`, `candidate_rules`, `load_sequence`, `deferred_rules`.

**Completeness invariant:** every unique `candidate_rules[*].rule_path` must appear in exactly one of `load_sequence[*].rule_path` or `deferred_rules[*].rule_path`. A malformed manifest, missing required fields, or any rule body content triggers Step 2B fallback.

**Full field definitions and schema rules:** [`references/manifest-schema.md`](references/manifest-schema.md). Minimal valid examples: [`examples/manifest-output.md`](examples/manifest-output.md).

## Python Script Invocation (Primary Path)

Starting with skill version `2.1.0`, rule discovery is delegated to the
standalone deterministic matcher (`skills/rule-loader/scripts/match_rules.py`).
The hook, sub-agent, or skill executor invokes it with the raw user request:

```bash
python3 skills/rule-loader/scripts/match_rules.py \
  --prompt "$USER_REQUEST" \
  --rules-dir ./rules \
  --max-entries 8 \
  --max-tokens 100000
```

`--keywords` is a low-level interface for callers that already extracted a
comma-delimited list of normalized terms, for example
`--keywords "streamlit,deploy"`. Do not pass raw user prose to `--keywords`.
The matcher defensively extracts a single long prose value, but callers must
use `--prompt` as the primary contract. When a plausible request still returns
an empty manifest, return the empty-manifest sentinel and use the Step 2B
fallback rather than treating it as a successful discovery result.

**Exit codes:**
- `0`: success, at least one rule matched; stdout contains `rule-loader-matcher/v1` JSON.
- `1`: no rules matched; stdout contains valid JSON with `load_sequence: []`.
- `2`: fatal error (e.g. `--rules-dir` not found); stdout is empty, error on stderr.

**Fallback path (script unavailable or exits 2):** Return the empty-manifest
sentinel to the main agent:

```json
{
  "schema_version": "rule-loader-matcher/v1",
  "error": "matcher_unavailable",
  "load_sequence": [],
  "deferred_rules": [],
  "candidate_rules": [],
  "warnings": []
}
```

The main agent treats this as a Gate 2 failure and uses the hook-injected
manifest when available. In repo-only operation, invoke `match_rules.py` against
`rules/`; it scans YAML frontmatter directly. No generated rule index exists.

## Workflow

Detailed phase content is loaded on demand from `workflows/` (progressive disclosure). Execute phases in order. Load workflow files only as needed.

### Phase 1: Foundation Loading
Always load `000-global-core.md`. Non-negotiable.

**Details:** `workflows/foundation-loading.md`

### Phase 2: Domain Matching
Match file extensions and directory paths with the deterministic matcher over `rules/` frontmatter.

**Details:** `workflows/domain-matching.md`

### Phase 3: Activity Matching
Search `rules/` frontmatter for keyword matches through the deterministic matcher.

**Details:** `workflows/activity-matching.md`

### Phase 4: Dependency Resolution
For each selected rule, check `Depends` metadata and load prerequisites first.
**Closure loading is MANDATORY: recurse to fixpoint; do not return until all `required:` parents are included.**

**Details:** `workflows/dependency-resolution.md`

### Phase 5: Token Budget Management
Sum TokenBudget values, defer low-priority rules if over budget. `required:` dependency closure is loaded in addition to: and does not count against: the 3 domain/activity-selection cap, and a `required:` parent is never deferred for token pressure. If loading a mandatory closure would exceed the 20,000-token R4 ceiling, defer LEAF/optional selections first; a still-over-budget mandatory closure is escalated (see `workflows/token-budget.md` Q3-resolution), never silently trimmed. The budget ceiling applies to TOTAL per-response context (fixed floor + index match + selected rules), not just the selected rules: verify with `ai-rules tokens --context-estimate`.

**Details:** `workflows/token-budget.md`

## Matching Layers (HARD vs SOFT)

**HARD layer (mechanical, reproducible):** file extension (`ext=`), explicit file
(`file=`), directory (`dir=`), and the high-risk-action map. Resolved by
exact-string lookup against rule frontmatter. Same request → same
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
5. `required:` dependency closure is loaded in addition to: and does not count against: the 3 domain/activity-selection cap (cap counts LEAF/domain selections only); a `required:` parent is never deferred
6. Deferred rules are declared with reason

## Error Handling

**Matcher unavailable:**
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

- **`hooks/user-prompt-submit`** - Plugin hook that runs this loading logic automatically
- **`scripts/match_rules.py`** - The deterministic discovery boundary used by the hook.
- **002h-claude-code-skills.md** - Skill authoring standards this skill follows
- **003-context-engineering.md** - Token budget and attention management principles

## Version History

See `CHANGELOG.md`.
