---
schema_version: v4.0
rule_version: v3.0.0
description: "Markdown linting patterns, tool configuration, and integration for consistent documentation quality. Uses pymarkdownlnt as the primary Python-native linter."
last_updated: 2026-10-06
keywords:
  - kw:pymarkdownlnt
  - kw:markdown linting
  - kw:uvx pymarkdownlnt
  - kw:.pymarkdown.yml
  - kw:MD013 line length
  - kw:markdown automation integration
token_budget: ~800
context_tier: Low
depends:
  required:
    - 202-markup-config-validation.md  # Parent rule for markup and config validation
  optional:
    - 820-taskfile-automation.md
---
# Markdown Linting

## Scope

**What This Rule Covers:**
Markdown lint configuration, check/fix integration and precise reporting of structural versus semantic documentation quality.

**When to Load This Rule:**
When editing/linting Markdown, configuring pymarkdownlnt or integrating documentation checks into automation/CI.

## Contract

### Inputs and Prerequisites

- Existing Markdown, active linter/version/config and project automation.
- Intended document type (agent rule, human guide, generated/include file) and authorized edit scope.

### Mandatory

- Run project Markdown automation first. pymarkdownlnt is this project's Python-native choice; respect an established markdownlint/other tool elsewhere rather than replacing it unasked.
- Pin actual tooling/lock/hook version when reproducibility requires; a >= version range or unversioned uvx command is not an exact pin.
- Use current configuration keys/file formats supported by the installed linter. Inspect help/docs before prescribing fix flags; do not copy obsolete --fix syntax or invalid JSON-with-comments.
- Check every modified Markdown file before task completion. Missing tooling is an unverified gate, not a silent skip or permission to install/download dependencies.
- Keep headings contiguous, blank lines/fences/lists consistent, code blocks language-tagged and links descriptive. Validate frontmatter/first-heading behavior with rule-specific config where applicable.
- Configure line-length/HTML/table policies for actual audience and project needs; do not disable all checks or impose an arbitrary five-file threshold for justified exceptions.
- Document narrow intentional exceptions. Prefer local/context-specific config over blanket suppression that masks heading/trailing-space/structure errors.
- Separate check-only and scoped fix targets. Review fixes to preserve code samples, frontmatter, links and unrelated/staged content.
- Lint does not verify link availability, example correctness, product claims or runtime behavior; those need distinct checks/manual evidence.

### Execution Steps

1. Read modified files, project configs, automation and installed linter help/version.
2. Run check-only configured lint on changed scope, then required project-wide doc/rule targets.
3. Diagnose exact IDs/locations and fix minimal formatting errors; adjust justified config only when within scope.
4. Recheck lint and semantic effects on fences/frontmatter/examples/links.
5. Report real outputs and unavailable semantic/link/runtime checks; do not claim all examples tested from zero lint errors.

### Validation

- Modified Markdown passes actual project lint configuration; exceptions narrow and documented.
- No invalid JSON/comments, malformed nested fences or unexpected frontmatter changes.
- Check/fix commands valid for installed tool; hook/CI/local versions consistent.
- No unauthorized global install, dependency update or broad formatter sweep.
- Semantic/link/example verification separate from syntax/format lint and honestly disclosed.

## References

- [PyMarkdown documentation](https://pymarkdown.readthedocs.io/en/latest/)
- [PyMarkdown source](https://github.com/jackdewinter/pymarkdown)
- [CommonMark](https://spec.commonmark.org/)
- [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2)
