# Rule Loader — Changelog

All notable changes to the `rule-loader` skill. Current version is tracked in `SKILL.md` frontmatter.

## [1.6.0] - 2026-07-12

### Changed

- **Dependency co-loading (behavioral fix):** `required:` dependency closure is now explicitly exempt from the R3 domain-rule cap (cap counts only LEAF/domain selections) and from the R4 `total > ceiling` deferral path. A `required:` parent is never silently deferred or trimmed.
- `SKILL.md` Phase 4: added mandatory-closure one-liner ("Closure loading is MANDATORY — recurse to fixpoint").
- `SKILL.md` Phase 5: replaced old cap wording with canonical cap-exemption sentence covering both R3 (count) and R4 (token) exemptions.
- `SKILL.md` Quick-Validation #5: replaced "No more than 3 domain/activity rules loaded" with canonical cap-exemption statement clarifying LEAF-only counting.
- `workflows/dependency-resolution.md`: added explicit rule that `required:` closure does not count against the cap; added worked closure example (119→{100,103,105}).
- `workflows/token-budget.md`: R3 section clarified — cap counts LEAF/domain selections only; R4 section adds canonical exemption sentence; line-82 deferral path adds explicit `required:` closure exemption; added Q3-resolution section for UNSATISFIABLE mandatory closures.

## [1.5.1] - 2026-07-11

### Changed

- Dual rule index collapsed into a single generated `rules/RULES_INDEX.md` (compact F4 format). All skill references to `RULES_INDEX_COMPACT.md` (SKILL.md `## Manifest Output` `index_evidence.target`, `## Related` bullets, and the `workflows/` grep targets) now point at `rules/RULES_INDEX.md`. Removed the obsolete "human-only RULES_INDEX.md" framing introduced in 1.5.0 — `RULES_INDEX.md` is once again the single agent discovery index.

## [1.5.0] - 2026-07-11

### Added

- `## Matching Layers (HARD vs SOFT)` section: HARD layer (ext/file/dir + high-risk map) is mechanical and reproducible against `RULES_INDEX_COMPACT.md`; SOFT layer (activity keywords) is explicitly best-effort / non-deterministic.
- `## Manifest Output` section defining the authoritative `rule-loader-manifest/v1` fenced JSON schema returned when the skill runs inside a discovery sub-agent. Metadata only — rule bodies never cross back. Requires `candidate_rules`, `candidate_count`, and `deferred_rules` with a candidate-completeness invariant.
- `examples/manifest-output.md` with a minimal valid manifest and a token-budget deferral example.

### Changed

- `description` frontmatter now states the skill is the single source of truth for rule discovery, runs in a discovery sub-agent, matches against `RULES_INDEX_COMPACT.md`, and returns a metadata-only manifest.
- Agent-facing `RULES_INDEX.md` references in `workflows/activity-matching.md` and `workflows/dependency-resolution.md` repointed to `RULES_INDEX_COMPACT.md`; `RULES_INDEX.md` labeled human-only in `## Related`.
- `workflows/domain-matching.md` and `workflows/activity-matching.md` gained HARD / SOFT layer header notes (with the high-risk-action check marked HARD).

## [1.3.0] - 2026-07-03

### Fixed

- `{rules_path}` placeholder in workflow files is now resolved to the literal `rules/` prefix. Removes the runtime substitution ambiguity that could cause foundation loading to fail silently when the placeholder was never expanded.

### Changed

- `rules_path` optional input removed from `SKILL.md` `## Inputs`. Callers no longer configure the rules directory — the skill resolves paths relative to `rules/` from the working directory.
- Added a `### Preconditions` block to `## Inputs` declaring that the working directory must be the project root (the directory containing `rules/`). Foundation loading fails with a CRITICAL "file not found" error otherwise.

## v1.2.0 (2026-06-21)

### Changed

- docs: remove decorative heading suffixes — `## Output (required)` → `## Outputs`; `## Workflow (progressive disclosure)` → `## Workflow`. The progressive-disclosure note moved into the section body.

### Added

- **Multi-phase loading algorithm** — foundation (000-global-core.md) always loaded first,
  then domain rules matched by file extension, then activity rules matched by request keywords
- **Token budget management** — respects context window limits; lower-priority rules deferred
  when budget exceeded
- **Dependency resolution** — loads rule dependencies declared in `Depends:` metadata field
- **Directory-based rule override** — requests targeting `rules/` load 002-rule-governance.md;
  requests targeting `skills/` load 002h-claude-code-skills.md
- **RULES_INDEX.md grep fallback** — when grep is unavailable, falls back to read_file +
  manual scan rather than failing the gate
- **Periodic refresh** — forces full Step 1-4 reload on every 5th response or after errors
