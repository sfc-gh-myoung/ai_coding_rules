# Rule Review: `100-snowflake-core.md`

## Scores

- **Actionability**: 3/5
  - **Notes**: Good “do/don’t” directives, but several “Always/Prefer” items
    lack explicit fallback branches when prerequisites are unknown or when
    permissions/tooling prevent the recommended path.

- **Completeness**: 3/5
  - **Notes**: Covers common SQL patterns, but failure modes (unknown
    DB/SCHEMA, insufficient privileges, Streams/Tasks not allowed, performance
    regressions) aren’t paired with explicit recovery steps.

- **Consistency**: 2/5
  - **Notes**: Multiple examples contradict hard mandates (notably `SELECT *`
    and unqualified object names). This can cause literal-following agents to
    generate disallowed SQL.

- **Parsability**: 4/5
  - **Notes**: Metadata is machine-readable; structure is clear; code blocks are
    well delimited. A few duplicated/overlapping sections and mixed placeholder
    vs “real” examples reduce extraction reliability.

- **Token Efficiency**: 2/5
  - **Notes**: File reads materially larger than the declared
    `**TokenBudget:** ~2850` and contains repeated concepts plus explanatory
    prose not needed for agent execution.

- **Staleness**: 3/5
  - **Notes**: Guidance is mostly evergreen; however, link currency/availability
    wasn’t verifiable in this environment, and a few heuristics are stated too
    strongly (risking outdated or incorrect “rules of thumb”).

**Overall:** 17/30

**Reviewing Model:** GPT-5.2 (Cursor agent)

## Critical Issues (Must Fix)

- **Directive-example contradiction (`SELECT *`)**: The rule forbids
  `SELECT *` yet includes an Output Format Example that uses `SELECT *`, which
  can directly induce agent noncompliance.

- **Directive-example contradiction (fully qualified names)**: “Fully qualify
  all objects” is mandatory, but multiple examples use bare identifiers
  (`large_table`, `events`, `orders`, etc.), which can train agents to violate
  the mandate.

- **Over-strong heuristic presented as rule**: “WHERE clauses before JOINs for
  partition pruning” is not universally correct as written and can mislead
  agents into cargo-cult rewrites.

## Improvements (Should Fix)

- **Add explicit fallback branches**: Cover unknown context (DB/SCHEMA/role),
  missing privileges, or when Streams/Tasks are infeasible.

- **Mark placeholders explicitly**: Require replacement, or fully qualify
  placeholder names consistently.

- **Make “documentation reference” actionable**: Specify when to consult docs
  vs proceed with known-safe defaults, and what to do if docs are inaccessible.

## Minor Suggestions (Nice to Have)

- **Remove/condense meta-prose**: The Quick Start TL;DR contains “position
  advantage” style content that doesn’t directly instruct execution.

- **Deduplicate “Related Rules”**: Multiple “Related Rules” blocks reduce
  deterministic parsing.

- **Convert bare URLs to markdown links**: Keeps formatting consistent and
  improves extraction.

## Specific Recommendations

1. **Location:** `## Output Format Examples` (around lines 275–290)
   - **Problem:** Includes `SELECT * FROM agg;` despite “Never use SELECT * in
     production” being a hard prohibition.
   - **Recommendation:** Replace with explicit columns, or add an explicit
     conditional: if the example is teaching-only, label it NON-PRODUCTION and
     still avoid `SELECT *`.
   - **Example fix:** `SELECT customer_id, num_orders, total_amount FROM agg;`

2. **Location:** Quick Start TL;DR “MANDATORY” (around lines 29–37) vs multiple
   SQL examples (around lines 86–242)
   - **Problem:** “Fully qualify all objects” is mandatory, but examples do not
     show fully qualified names, creating inconsistency and reducing
     actionability.
   - **Recommendation:** Either (A) fully qualify all example objects
     (preferred), or (B) add a single explicit rule that all unqualified
     identifiers in examples are placeholders that must be replaced with
     `DATABASE.SCHEMA.OBJECT`.

3. **Location:** Quick Start TL;DR (around line 32), “Push filters early — WHERE
   clauses before JOINs for partition pruning”
   - **Problem:** As phrased, this is not a reliable or universally applicable
     transformation rule and can cause incorrect rewrites or false confidence.
   - **Recommendation:** Rephrase to an explicit decision rule: push selective
     predicates as close to base tables as possible *without changing
     semantics*, and validate with Query Profile. If a predicate references
     columns from the joined table, keep it in the appropriate join condition
     or post-join filter.

4. **Location:** `## 2. Optimization and Performance` (around line 326),
   `## 3. Security and Governance` (around line 333), and
   `## 5. Incremental Patterns` (around line 345)
   - **Problem:** “Always reference documentation” is not an executable step
     unless you define decision points and fallback behavior (if docs or tools
     are inaccessible).
   - **Recommendation:** Add explicit branches, e.g.:
     - If the agent has web access: consult the relevant docs section.
     - Else: proceed with a known-safe default and ask the user to confirm.
     Also convert bare URLs to markdown links.

5. **Location:** `## Contract` → `<inputs_prereqs>` and `<steps>`
   (around lines 41–60)
   - **Problem:** Inputs list DB/SCHEMA/warehouse/roles but don’t specify what
     to do when they are unknown (common for agents receiving partial prompts).
   - **Recommendation:** Add explicit first branches in `<steps>`, e.g.:
     - If DB/SCHEMA not provided: ask the user; else proceed.
     - If role/privileges unknown: run read-only discovery queries; if not
       possible, ask the user to run `SHOW GRANTS` or provide the role.

6. **Location:** `## Post-Execution Checklist` (around lines 244–256)
   - **Problem:** Checklist references specialized rules (e.g.,
     `119-snowflake-warehouse-management.md`) but the file’s own `Depends` does
     not include them; agents may assume they are loaded.
   - **Recommendation:** Keep `Depends` minimal but explicitly label these as
     “load-on-demand,” or introduce an “Optional Dependencies” metadata line if
     allowed by your schema.

7. **Location:** Quick Start TL;DR prose (around lines 22–27)
   - **Problem:** “Token efficiency / Position advantage / Progressive
     disclosure” is rule-authoring rationale, not execution guidance. It costs
     tokens without improving compliance.
   - **Recommendation:** Move to rule-authoring docs or delete; keep Quick Start
     as executable directives plus a short checklist.

## Staleness Indicators Found

- **Tool Versions:** N/A (no pinned versions mentioned).
- **Deprecated Patterns:** None detected (Streams/Tasks, QUALIFY,
  Query Profile).
- **API Changes:** None referenced directly.
- **Industry Shifts:** N/A.
- **External Links:** Present and “stable-looking,” but could not be verified
  for current validity in this environment (also some are bare URLs).

## Dependency Drift Check

- **Depends:** `rules/000-global-core.md`
- **Conflicts Found:** None direct, but internal contradictions (examples vs
  mandates) undermine the dependency’s execution-contract intent.
- **Missing Dependencies:** Not strictly required, but the rule implicitly
  leans on specialized guidance (`119-...`, `105-...`, `107-...`) in
  checklists/references. Label these as “load-on-demand” rather than assuming.
