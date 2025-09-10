**Description:** Directives for a professional contribution workflow: commits, pull requests, and changelog discipline.
**Applies to:** `CONTRIBUTING.md`, `README.md`, `.github/**/*`
**Auto-attach:** false

# Contribution Workflow

## 1. Commit & Changelog Discipline
- **Requirement:** Follow Conventional Commits: `<type>(<scope>): <imperative summary>`.
- **Requirement:** Valid types: `feat`, `fix`, `perf`, `refactor`, `style`, `docs`, `chore`, `build`, `ci`, `test`.
- **Requirement:** Use a short, descriptive scope (e.g., `generator`, `ui`, `snowflake`).
- **Always:** After user-facing changes, update `CHANGELOG.md` under `## [Unreleased]`.
- **Requirement:** Each changelog entry is a single concise line; collapse micro-fixes.
- **Requirement:** Avoid anti-patterns: "WIP" subjects, unscoped types for multi-domain changes, mixing features and fixes.

## 2. General Code Standards
- **Requirement:** SQL must use uppercase keywords and explicit identifiers (avoid `SELECT *`).
- **Always:** New behavior should include at least one happy-path test and one negative/edge case test.
- **Requirement:** Test function names follow `test_<function>_when_<condition>_should_<result>`.
- **Always:** Reference specialized rules as needed (e.g., `20-python-core.md`).

## 3. Pull Requests & Branching
- **Requirement:** PR titles must follow Conventional Commits.
- **Requirement:** PRs must contain delta-only edits; avoid unrelated formatting.
- **Always:** For multi-user projects, submit PRs to a protected `main` branch.

## 4. Documentation
- **Always:** Reference Conventional Commits: https://www.conventionalcommits.org/en/v1.0.0/#specification