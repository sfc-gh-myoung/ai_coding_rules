# Changelog

All notable changes to the `analyze-plan` skill are documented in this file.
Format: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-06-21

### Added

- Initial conversion from `prompts/analyze-plan.md`.
- Plan discovery via `ask_user_question` with prefilled most-recent `*.plan.md`.
- Output filename `<plan-stem>_<YYYYMMDD_HHMMSS>_ANALYSIS.md` with no-overwrite guarantee.
- Self-contained external-source selection (MADR 4.0, Twelve-Factor, Diátaxis) by detected plan domain.
