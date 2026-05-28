# Using the Plan Creator Skill

**Last Updated:** 2026-05-14

The Plan Creator Skill produces architecturally rigorous, tactically concrete,
safe-to-execute, and independently auditable implementation plans. Use it to
author migration plans, feature designs, refactor plans, or any non-trivial
implementation document. The skill enforces a fixed 15-section structure so plan
quality does not vary with the underlying model.

## Examples

### Minimal Required Example

```text
Use the plan-creator skill.

task: Migrate the warehouse runtime configuration from environment.yml to pyproject.toml across all Streamlit apps.
```

### With All Optional Settings

```text
Use the plan-creator skill.

task: Replace the Makefile and scripts/run-sql.sh with npm scripts and TypeScript.
codebase_root: /Users/me/projects/sql-runner    # Optional (default: cwd): directory to inventory before writing
runtime_targets: Node.js 24 LTS, npm 11         # Optional (default: inferred): hard runtime constraints
reference_plans: .snowflake/cortex/plans/old-plan-A.md, .snowflake/cortex/plans/old-plan-B.md  # Optional: synthesize from prior plans
out_of_scope: Next.js version changes, CI provider migration  # Optional: pre-declared non-goals
```

### Synthesizing From Prior Plans

```text
Use the plan-creator skill.

task: Consolidate three competing migration proposals into one executable plan for the dbt-on-Snowflake rollout.
reference_plans: plans/migration-claude.md, plans/migration-gpt.md, plans/migration-gemini.md
```

When `reference_plans` is provided, Section 15 (Plan Provenance) becomes
mandatory and maps each major decision back to its source plan, including
deliberate divergences.

## When to Use This Skill

| Scenario | Use plan-creator? |
|----------|------------------|
| Multi-file refactor with real tradeoffs | Yes |
| Migration between runtimes, tools, or syntaxes | Yes |
| Feature design that touches architecture | Yes |
| Synthesizing or upgrading existing plan documents | Yes |
| Comparing competing plans into one "best of" plan | Yes |
| Single-line bug fixes or typos | No |
| Pure research questions ("what is X?") | No |
| Obvious one-file changes | No |

## Inputs

### Required

| Input | Type | Purpose |
|-------|------|---------|
| `task` | string | The implementation task the plan addresses. Must include enough context for the plan author to determine scope, current state, and target state. |

### Optional

| Input | Type | Default | Purpose |
|-------|------|---------|---------|
| `codebase_root` | path | current working directory | Directory inventoried before writing the plan |
| `reference_plans` | list of paths | none | Prior plans to synthesize from. When present, Section 15 becomes mandatory |
| `runtime_targets` | list | inferred from config files | Explicit target runtime/versions that become hard constraints |
| `out_of_scope` | list | none | Items the user has already declared non-goals |

## Understanding Your Results

### Output Location

The skill writes the plan to a deterministic path:

```text
<plan_dir>/<slug>-<YYYY-MM-DD>.plan.md
```

| Component | Resolution |
|-----------|------------|
| `plan_dir` | `.snowflake/cortex/plans/` if it exists, else `docs/plans/`, else `./` with a note |
| `slug` | lowercase-hyphens summary of the task (max 48 chars) |
| Suffix on collision | `-01.md`, `-02.md`, etc. (no overwrites) |
| Final line | `**End of plan.**` (literal) |

### The 15 Mandatory Sections

Every plan contains these top-level numbered sections in this exact order.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Recommendation & Rationale | Comparison table of ≥3 alternatives with explicit rejection reasons |
| 2 | Hard Constraints | Numbered list (C1, C2, …) of non-negotiable requirements |
| 3 | Target Architecture | Directory layout, key API signatures, error-handling contract |
| 4 | Dependency Changes | Four tables: Add / Remove / Update / Keep with reason column |
| 5 | Final-State Artifact(s) | Complete final form of every config file being rewritten: no excerpts |
| 6 | 1:1 Parity / Mapping Table | One row per old→new entrypoint to prove zero coverage regression |
| 7 | Documentation Updates | New / modified / deleted files with paths and exact sections changed |
| 8 | Test Strategy | Unit tests, integration tests, CI matrix (OS × runtime grid), fixtures |
| 9 | Risk Register | At least 8 rows with Likelihood, Impact, and concrete Mitigation |
| 10 | Phased Task List | Phase 0 = compatibility gate; each phase has time estimate, tasks, validation |
| 11 | Rollback Plan | Concrete steps if final validation fails within a bounded time window |
| 12 | Acceptance Criteria | Objectively verifiable "done" conditions a third party can check |
| 13 | Open Questions | Decisions to be made before Phase 1, marked `BLOCKING` or `non-blocking` |
| 14 | Non-Goals / Out of Scope | Explicit list of things the plan does NOT do |
| 15 | Plan Provenance | Required when `reference_plans` provided; maps decisions to sources |

### Plan Constraints

Every plan satisfies these constraints:

- **Zero new runtime or dev dependencies unless justified** in Section 4 with a per-dep reason. Standard-library APIs preferred.
- **Existing behavior preserved** unless the task explicitly requires breaking change. Breaking changes get a CHANGELOG entry and version bump note.
- **Every external dependency call** (CLI, network, subprocess) defines an error type or exit-code contract in Section 3.
- **Every destructive operation** supports a non-interactive `--yes` (or equivalent) flag and refuses to hang on non-TTY without it.
- **Cross-platform claims** are proven by a CI matrix in Section 8, not asserted in prose.

### Self-Audit Checklist

Before the plan is written to disk, the skill answers every question below. If any answer is "no", it revises before returning.

- [ ] Could a new engineer execute this plan without asking the author a single clarifying question?
- [ ] Does Section 1 contain ≥3 rejected alternatives with explicit rejection reasons?
- [ ] Does Section 5 show complete final-state artifacts (not excerpts)?
- [ ] Does Section 6 prove 1:1 parity (or note explicitly "not a migration: parity table omitted")?
- [ ] Is every dependency change in Section 4 justified?
- [ ] Does Section 8 include a CI matrix (not just unit-test list)?
- [ ] Does Section 9 contain ≥8 risks with concrete mitigations?
- [ ] Does Phase 0 of Section 10 gate the rest of the plan on verifiable compatibility?
- [ ] Does Section 11 specify a time-bounded rollback trigger?
- [ ] Does Section 12 contain only third-party-verifiable criteria (no "looks good" language)?
- [ ] Does Section 13 mark each open question BLOCKING or non-blocking?
- [ ] Are Phase 1 research findings cited inline (verified runtime versions, orphan files, consumer lists)?
- [ ] Does Section 14 exist even if brief?
- [ ] Does the document end with `**End of plan.**`?

## Advanced Usage

### Workflow Phases

The skill executes four phases in order. Phases are not skippable.

| Phase | Activity | Key Output |
|-------|----------|------------|
| Phase 1 | Research the codebase, inventory affected files, identify consumers, verify runtime/config | Findings cited inline in Sections 2, 3, 9, and 10 |
| Phase 2 | Apply plan constraints (deps, behavior preservation, error contracts, non-interactive flags) | Constraints enforced in plan content |
| Phase 3 | Write the 15 sections in order | Markdown plan document |
| Phase 4 | Self-audit against the 14-item checklist | Revisions before disk write |

### Output Path Resolution

The skill picks the first directory that exists:

```text
.snowflake/cortex/plans/  →  docs/plans/  →  ./  (with a note in the plan)
```

Override by ensuring the desired directory exists before invocation, or by
specifying `codebase_root` so the skill discovers your preferred structure.

### No-Overwrite Safety

If the target filename already exists, the skill appends `-01`, `-02`, etc. The
skill never silently overwrites a prior plan.

### Degrees of Freedom

| Aspect | Freedom |
|--------|---------|
| Section count and order | Low: 15 sections are mandatory |
| Section headings | Low: fixed, numbered |
| Self-audit checklist | Low: non-negotiable |
| Choice of alternatives in Section 1 | High: judgment-driven |
| Which 8+ risks to surface | High: judgment-driven |
| Test prioritization | High: judgment-driven |

### Output Format Rules

- Markdown only.
- Numbered top-level sections with the exact 15 headings.
- Code blocks for file layouts, signatures, and final-state artifacts.
- Pipe-syntax tables for any list of ≥3 rows with ≥2 attributes.
- No emojis. No marketing language. Engineer-to-engineer tone.
- The skill produces only the plan document: no code is written, and no project files outside the output plan are modified.

## FAQ

### What makes a plan "executable" by this skill's standard?

A plan is executable when a new engineer can run it end-to-end without asking
the original author a single clarifying question. The 15-section structure and
self-audit exist to enforce that bar.

### What should I pass for `task`?

A specific, scoped sentence: not a topic. Compare:

- Bad: "Improve our deployment process."
- Good: "Replace the Makefile and scripts/run-sql.sh with npm scripts and TypeScript, targeting Node.js 24 LTS."

The skill fills in scope hints during Phase 1 research; clearer `task` input
yields a tighter plan.

### When should I use plan-creator instead of plan-reviewer?

| Need | Skill |
|------|-------|
| Author a new plan from scratch | `plan-creator` |
| Synthesize competing plans into one | `plan-creator` (with `reference_plans`) |
| Score an existing plan's quality | `plan-reviewer` |
| Compare multiple plans side-by-side | `plan-reviewer` (COMPARISON mode) |
| Check whether a revision resolved earlier issues | `plan-reviewer` (DELTA mode) |

### Why is Section 5 required to show *complete* artifacts?

Excerpted artifacts hide the change surface area. A plan that says "the
`package.json` should look roughly like this" cannot be reviewed for
correctness. Every line of every rewritten config file must appear so the diff
can be verified before any code is written.

### Why is Phase 0 separate from the rest of the work?

Phase 0 is a compatibility / discovery gate with no code changes. It catches
runtime mismatches, missing files, and orphan config entries before the
expensive rewrite begins. Skipping Phase 0 is one of the most common ways for
plans to fail late.

### What if my task does not need a parity table?

Section 6 may be marked explicitly: `not a migration: parity table omitted`.
The section header still appears so reviewers can confirm the omission was
deliberate.

### What if my plan does not need a Plan Provenance section?

Section 15 is required only when `reference_plans` is provided. For from-scratch
plans, omit it (the section number runs to 14 in that case).

## Reference

### Architecture Overview

```text
Coordinator
│
├── Phase 1: Research codebase, inventory files, verify runtime/config
├── Phase 2: Apply plan constraints (deps, behavior, error contracts)
├── Phase 3: Write 15 sections in order
└── Phase 4: Self-audit against 14-item checklist before disk write
```

### File Structure

```text
skills/plan-creator/
├── SKILL.md
└── CHANGELOG.md
```

### Anti-Patterns the Skill Avoids

| # | Anti-Pattern | Why It Fails |
|---|--------------|---------------|
| 1 | Excerpted final artifact | Hides change surface; cannot be diff-reviewed |
| 2 | Unproven cross-platform claim | Asserting cross-platform without a CI matrix in Section 8 |
| 3 | Vague risk mitigation | "Monitor" is not a mitigation; concrete actions required |
| 4 | Drive-by dependency additions | Every new dep needs a Section 4 row with justification |
| 5 | Acceptance criteria requiring author judgment | "Looks clean" cannot be verified by a third party |
| 6 | Phase 0 skipped | No compatibility gate means rewrites land on broken assumptions |
| 7 | Missing rollback (Section 11) | No bounded recovery path if final validation fails |

### Related Skills

| Skill | Relationship |
|-------|--------------|
| `plan-reviewer` | Scores plans produced by this skill against an 8-dimension rubric |
| `doc-reviewer` | Reviews user-facing documentation rather than executable plans |
| `rule-creator` | Authors new rule files (a different artifact type) |

### Source of Truth

For behavior details, prefer these files over older examples or copied notes:

- `skills/plan-creator/SKILL.md`
- `skills/plan-creator/CHANGELOG.md`
