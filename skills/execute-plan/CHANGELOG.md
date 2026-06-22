# Changelog

All notable changes to the `execute-plan` skill are documented in this file.
Format: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-06-21

### Added

- Initial conversion from `prompts/execute-plan.md`.
- Progress-marker convention (`- [ ] / [~] / [x] (date)`) for cross-session resumability.
- Per-task, per-phase, and auto confirmation modes.
- Mutation safety: only `^- \[[ x~]\]` lines are touched; surrounding markdown preserved.
