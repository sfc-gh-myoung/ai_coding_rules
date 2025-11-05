---
appliesTo:
  - "CONTRIBUTING.md"
  - "README.md"
  - ".github/**/*"
  - "**/*-*.md"
---
<!-- Generated for GitHub Copilot repository instructions. See https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions -->

**Keywords:** CONTRIBUTING, pull requests, code review, contribution guidelines, branching strategy
**Depends:** 000-global-core

**TokenBudget:** ~400
**ContextTier:** Medium

# Contribution Workflow

## Purpose
Establish directives for a professional contribution workflow covering commits, pull requests, changelog discipline, and rule authoring standards to ensure consistent project collaboration and quality.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Professional contribution workflows for commits, pull requests, and rule authoring standards


## 1. Commit & Changelog Discipline
- **Requirement:** Follow Conventional Commits: `<type>(<scope>): <imperative summary>`.
- **Requirement:** Valid types: `feat`, `fix`, `perf`, `refactor`, `style`, `docs`, `chore`, `build`, `ci`, `test`.
- **Requirement:** Use descriptive scopes aligned with rule categories:
  - Core: `core`, `governance`, `memory-bank`
  - Snowflake: `snowflake`, `sql`, `streamlit`, `spcs`
  - Python: `python`, `fastapi`, `lint`, `setup`
  - Shell: `bash`, `zsh`, `shell`
  - Project: `changelog`, `readme`, `contributing`, `taskfile`
  - Analytics: `data-science`, `governance`, `business`
- **Always:** After user-facing changes, update `CHANGELOG.md` under `## [Unreleased]`.
- **Requirement:** Each changelog entry is a single concise line; collapse micro-fixes.
- **Requirement:** Avoid anti-patterns: "WIP" subjects, unscoped types for multi-domain changes, mixing features and fixes.

## 2. Rule Authoring Standards

### Rule File Structure
- **Requirement:** Follow 3-digit numbering scheme with clear domain separation:
  - `000-099`: Core Foundation (global, memory-bank, governance)
  - `100-199`: Data Platform - Snowflake
  - `200-299`: Software Engineering - Python
  - `300-399`: Software Engineering - Shell Scripts
  - `500-599`: Data Science & Analytics
  - `600-699`: Data Governance
  - `700-799`: Business Intelligence
  - `800-899`: Project Management
  - `900-999`: Demo & Synthetic Data

### Rule Content Guidelines
- **Requirement:** Keep rules focused and concise (target 150-300 lines; max 500 lines).
- **Requirement:** Split large topics into multiple composable rules within the same range.
- **Requirement:** Use explicit directive language: `Requirement`, `Always`, `Avoid`, `Rule`, `Consider`.
- **Always:** Include metadata header with Description, AppliesTo, AutoAttach, Type, Version, LastUpdated.
- **Always:** Reference related rules using `@rule-name.md` syntax.

### Subdomain Organization
- **Rule:** Use 10-number ranges for framework-specific rules:
  - Python FastAPI: `210-219`
  - Bash Scripting: `300-309`
  - Zsh Scripting: `310-319`
- **Rule:** Use 20-number jumps for major feature areas (e.g., `120` for Snowflake SPCS).

## 3. General Code Standards
- **Requirement:** SQL must use uppercase keywords and explicit identifiers (avoid `SELECT *`).
- **Requirement:** Shell scripts must include proper shebang and error handling (`set -euo pipefail`).
- **Always:** New behavior should include at least one happy-path test and one negative/edge case test.
- **Requirement:** Test function names follow `test_<function>_when_<condition>_should_<result>`.
- **Always:** Reference specialized rules as needed (e.g., `@200-python-core.md`, `@300-bash-scripting-core.md`).

## 4. Pull Requests & Branching
- **Requirement:** PR titles must follow Conventional Commits.
- **Requirement:** PRs must contain delta-only edits; avoid unrelated formatting.
- **Always:** For multi-user projects, submit PRs to a protected `main` branch.
- **Rule:** When adding new rules, update README.md to reflect the new structure.
- **Rule:** When modifying rule numbering, ensure all cross-references are updated.

## 5. Rule Categories and Examples

### Current Rule Structure
```
Core Foundation (000-099)
├── 000-global-core.md
├── 001-memory-bank.md
└── 002-rule-governance.md

Snowflake (100-199)
├── 100-109: Core Snowflake
├── 110-119: [Reserved]
└── 120-129: Snowpark Container Services

Python (200-299)
├── 200-209: Core Python
└── 210-219: FastAPI Framework

Shell Scripts (300-399)
├── 300-309: Bash Scripting
└── 310-319: Zsh Scripting

Analytics & Data (500-699)
├── 500-599: Data Science
└── 600-699: Data Governance

Business & Project (700-899)
├── 700-799: Business Intelligence
└── 800-899: Project Management

Demo & Templates (900-999)
└── 900-999: Demo Creation
```

### Adding New Rules
- **Rule:** Choose appropriate number range based on domain
- **Rule:** Use next available number in sequence within the range
- **Rule:** For new frameworks, reserve 10-number subrange (e.g., 220-229 for Django)
- **Always:** Update README.md rule categories section
- **Always:** Validate rule follows governance standards in `@002-rule-governance.md`

## 6. Documentation References
- **Always:** Reference Conventional Commits: https://www.conventionalcommits.org/en/v1.0.0/#specification
- **Always:** Follow rule governance: `@002-rule-governance.md`
- **Always:** Use README standards: `@801-project-readme-rules.md`
- **Always:** Follow changelog discipline: `@800-project-changelog-rules.md`

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Response Template
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [GitHub Contributing Guidelines](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors) - GitHub's guide for contribution workflows 
- [Open Source Guides](https://opensource.guide/) - Best practices for open source project management
- [Conventional Commits](https://www.conventionalcommits.org/) - Standardized commit message format

### Related Rules
- **Global Core**: `000-global-core.md`
- **Changelog Rules**: `800-project-changelog-rules.md`
- **README Rules**: `801-project-readme-rules.md`
- **Rules Governance**: `002-rule-governance.md`
