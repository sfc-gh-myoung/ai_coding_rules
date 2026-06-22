# Rule Loader — Changelog

All notable changes to the `rule-loader` skill. Current version is tracked in `SKILL.md` frontmatter.

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
