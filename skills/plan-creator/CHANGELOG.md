# Changelog

All notable changes to the `plan-creator` skill are documented here.
Format: reverse-chronological order (newest version first).

## 2.0.0 — 2026-05-14

- **Breaking:** Renamed skill from `create-plan` to `plan-creator` to align with
  the `<noun>-<agent-noun>` naming convention used across this skill collection.
  Any caller pinning `name: create-plan` must update to `name: plan-creator`.

## 1.0.1 — 2026-04-25

- Add Phase 1.6 requiring research findings to be cited inline in the plan,
  not just used silently to inform it.
- Add matching self-audit checkbox in Phase 4.

## 1.0.0 — 2026-04-25

- Initial release.
- 15-section mandatory plan structure: Recommendation, Hard Constraints,
  Target Architecture, Dependency Changes, Final-State Artifacts, Parity Table,
  Documentation Updates, Test Strategy, Risk Register, Phased Task List,
  Rollback Plan, Acceptance Criteria, Open Questions, Non-Goals,
  Plan Provenance.
- Four-phase workflow: Research, Apply Constraints, Write Plan, Self-Audit.
- Self-audit checklist with 13 verification items.
- Invocation template with optional scope hints.
- Anti-pattern catalog (7 anti-patterns).
