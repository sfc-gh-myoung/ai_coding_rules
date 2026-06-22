---
name: plan-creator
description: Produces best-in-class implementation plans with 15 mandatory sections covering architecture, final-state artifacts, dependency deltas, parity tables, test strategy, CI matrix, risk register, phased tasks with time estimates, rollback, acceptance criteria, and open questions. Use when authoring a migration plan, feature design, refactor plan, or any non-trivial implementation document. Triggers on "create a plan", "write a plan", "migration plan", "implementation plan", "design doc", "refactor plan", "propose a design", "feature plan", "architecture plan". Do NOT use for small fixes, one-line changes, or pure research questions.
version: 2.0.1
---

# Plan Creator

## Purpose

Generates architecturally rigorous, tactically concrete, safe-to-execute, and independently auditable implementation plans. Forces structural completeness so plan quality does not vary with the underlying model.

## Use this skill when

- The user asks for a "plan", "design doc", "migration plan", or "refactor plan".
- Work spans multiple files, introduces architectural change, or has real tradeoffs between approaches.
- A pre-existing plan must be reviewed, upgraded, or standardized.
- Comparing multiple plans and producing a synthesized "best of" plan.
- The user wants a planning output they can hand to another engineer without follow-up questions.

**Do not use for:** single-line fixes, typos, obvious one-file changes, or pure "what/where is X?" research queries.

## Inputs

### Required
- `task`: string — the specific implementation task the plan addresses. Must include enough context for the plan author to determine scope, current state, and target state.

### Optional
- `codebase_root`: path (default: current working directory) — directory to inventory before writing the plan.
- `reference_plans`: list of paths (default: none) — prior plans to synthesize from. When present, the `Plan Provenance` section (15) becomes mandatory.
- `runtime_targets`: list (default: inferred) — explicit target runtime / versions that become hard constraints.
- `out_of_scope`: list (default: none) — items the user has already declared non-goals.

## Outputs

### Required
Write plan to: `<plan_dir>/<slug>-<YYYY-MM-DD>.plan.md`

- `plan_dir` default: `.snowflake/cortex/plans/` if it exists, else `docs/plans/`, else `./` with a note.
- `slug`: lowercase-hyphens summary of the task (max 48 chars).
- **No overwrites:** if file exists, append `-01.md`, `-02.md`, etc.
- End file with the literal line `**End of plan.**`.

## Workflow

Execute phases in order. Do not skip any.

### Phase 1 — Research (mandatory before writing)

1. Read the current state of the codebase relevant to `task`. Inventory every file that will be created, modified, or deleted. Record paths.
2. Identify every caller / consumer of the thing being changed (grep for it). Note downstream breakage points.
3. Identify the current runtime, package manager, test framework, CI system, and container base image. **Do not assume — verify by reading config files.**
4. Surface orphan / missing files referenced by config (e.g., `bin` entries pointing at nonexistent files). Flag them for Phase 0 of the plan.
5. If `reference_plans` provided, read each and note distinctive strengths / weaknesses per plan for Section 15.
6. **Cite findings inline in the plan.** Phase 1 discoveries (verified runtime versions, orphan config entries, downstream consumers, current base images) must appear explicitly in Sections 2 (Hard Constraints), 3 (Target Architecture), 9 (Risk Register), or 10 (Phase 0 tasks) — not just inform the plan silently. A reader must be able to trace every non-trivial claim back to a file path or command output.

### Phase 2 — Apply plan constraints

Every plan must satisfy these constraints. Enforce them in the plan content:

- **Zero new runtime or dev dependencies unless justified** in Section 4 with a per-dep reason. Prefer standard-library APIs.
- **Preserve existing behavior** unless the task explicitly requires breaking change. Breaking changes require a `CHANGELOG.md` entry and a version bump note in the plan.
- **Every external dependency call** (CLI, network, subprocess) must define an error type or exit-code contract in Section 3.
- **Every destructive operation** supports a non-interactive `--yes` (or equivalent) flag AND refuses to hang on non-TTY without it.
- **Cross-platform claims** must be proven by a CI matrix in Section 8, not asserted in prose.

### Phase 3 — Write the plan

Use these exact top-level section headings, numbered, in this order:

1. **Recommendation & Rationale** — comparison table of ≥3 alternatives with explicit rejection reasons for each non-chosen option.
2. **Hard Constraints** — numbered list (C1, C2, …) of non-negotiable requirements.
3. **Target Architecture** — directory layout as a code block; key APIs / types / interfaces as signatures (not implementations); error-handling contract (exit codes, error classes).
4. **Dependency Changes** — four tables: Add / Remove / Update / Keep. Each entry has a reason column.
5. **Final-State Artifact(s)** — complete final form of every config file being rewritten (e.g., full `package.json` scripts block). **Excerpts are not acceptable.** If too large, split into subsections but show every line that will exist.
6. **1:1 Parity / Mapping Table** — for migrations, one row per old→new entrypoint. Prove zero coverage regression.
7. **Documentation Updates** — three subsections: New files (path + purpose), Modified files (path + exact sections that change), Deleted files.
8. **Test Strategy** — unit tests (file list + what each covers), integration tests (gating mechanism + opt-in flag), CI matrix (OS × runtime-version grid), mocking / fixture conventions.
9. **Risk Register** — at least 8 rows. Columns: #, Risk, Likelihood (Low/Med/High), Impact, Mitigation.
10. **Phased Task List** — Phase 0 must be a compatibility / discovery gate with no code changes. Each phase has: name, time estimate, numbered checkbox tasks, and a validation step at the end. Include manual smoke tests for workflows that cannot be unit-tested.
11. **Rollback Plan** — concrete steps if the final validation phase fails and cannot be fixed within a bounded time window.
12. **Acceptance Criteria** — checklist of objectively verifiable "done" conditions. Every criterion must be something a third party can check without asking the author.
13. **Open Questions** — decisions that must be made before Phase 1 begins. Mark each `BLOCKING` or `non-blocking`.
14. **Non-Goals / Out of Scope** — explicit list of things this plan does NOT do.
15. **Plan Provenance** — required when `reference_plans` provided. Table mapping each major decision to its source plan. Note any deliberate divergence.

### Phase 4 — Self-audit (mandatory before returning)

Before writing the plan to disk, answer every question below. If any answer is "no", revise before returning.

- [ ] Could a new engineer execute this plan without asking the author a single clarifying question?
- [ ] Does Section 1 contain ≥3 rejected alternatives with explicit rejection reasons?
- [ ] Does Section 5 show complete final-state artifacts (not excerpts)?
- [ ] Does Section 6 prove 1:1 parity (or note explicitly "not a migration — parity table omitted")?
- [ ] Is every dependency change in Section 4 justified?
- [ ] Does Section 8 include a CI matrix (not just unit-test list)?
- [ ] Does Section 9 contain ≥8 risks with concrete mitigations?
- [ ] Does Phase 0 of Section 10 gate the rest of the plan on verifiable compatibility?
- [ ] Does Section 11 specify a time-bounded rollback trigger?
- [ ] Does Section 12 contain only third-party-verifiable criteria (no "looks good" language)?
- [ ] Does Section 13 mark each open question BLOCKING or non-blocking?
- [ ] Are Phase 1 research findings cited inline in the plan (verified runtime versions, orphan files, consumer lists) — not just used silently?
- [ ] Does Section 14 exist even if brief?
- [ ] Does the document end with `**End of plan.**`?

### Output Format

- Markdown.
- Use the exact 15 section headings above, numbered.
- Code blocks for file layouts, signatures, and final-state artifacts.
- Pipe-syntax tables for every list of ≥3 rows with ≥2 attributes.
- No emojis. No marketing language. Engineer-to-engineer tone.
- Do not write code — produce only the plan document.
- Do not modify any project files other than the output plan file.

## Degrees of Freedom

**Low freedom for structure:** The 15 sections are mandatory. Section headings are fixed. The self-audit checklist is non-negotiable.

**High freedom for content:** What goes *inside* each section is judgment-driven. Choice of alternatives to compare, which 8+ risks to surface, which tests to prioritize — all reflect engineering judgment appropriate to the task.

## Anti-Patterns

### Anti-Pattern 1: Excerpted final artifact
Bad: "The `package.json` should look roughly like this: [shows 10 of 40 scripts]"
Good: shows every script entry that will exist in the final file.

### Anti-Pattern 2: Unproven cross-platform claim
Bad: "This is cross-platform" (no evidence).
Good: CI matrix with `[ubuntu-latest, macos-latest, windows-latest]` in Section 8.

### Anti-Pattern 3: Vague risk mitigation
Bad: "Risk: dependency drift. Mitigation: monitor."
Good: "Risk: `snow` CLI JSON output drift. Mitigation: version-tolerant parsing in `run-sql.ts`; fixture-based unit tests capture current output shape; preflight warns on unsupported `snow` versions."

### Anti-Pattern 4: Drive-by dependency additions
Bad: adding `picocolors`, `lodash`, etc. without entry in Section 4.
Good: every new dep listed in Section 4 Add table with a justification column; stdlib alternative considered in rationale.

### Anti-Pattern 5: Acceptance criteria that require author judgment
Bad: "Code is clean and well-organized."
Good: "`npm run validate` passes on ubuntu + macos + windows × Node 24 in CI."

### Anti-Pattern 6: Phase 0 skipped
Bad: jumping straight to "Phase 1 — Toolchain upgrade".
Good: Phase 0 runs a compatibility gate (install, build, smoke test on target runtime) before any rewrite begins.

### Anti-Pattern 7: Missing rollback
Bad: no Section 11.
Good: Section 11 specifies `git revert` procedure, time-bounded fix window, and where to document root cause.

## Invocation Template

When this skill is invoked, structure the user prompt as:

```
TASK: <one-sentence description of what the plan must cover>

SCOPE HINTS (optional):
- Current state: <what exists today>
- Target state: <what should exist after>
- Hard constraints: <non-negotiables, e.g., runtime versions>
- Reference plans: <paths to existing plans to synthesize from, if any>
- Out of scope: <things deliberately excluded>
```

The skill fills in any missing scope hints during Phase 1 research rather than asking the user.

## Examples

**Invocation example:**
> "Write a migration plan for replacing our Makefile and scripts/run-sql.sh with npm scripts and TypeScript. Target Node.js 24 LTS and npm 11. Reference plans are in .snowflake/cortex/plans/. Out of scope: Next.js version changes."

**Expected output path:**
`.snowflake/cortex/plans/makefile-to-npm-migration-2026-04-25.plan.md`

**Expected first section heading:** `## 1. Recommendation & Rationale`
**Expected last line:** `**End of plan.**`

## Version History

See CHANGELOG.md.
