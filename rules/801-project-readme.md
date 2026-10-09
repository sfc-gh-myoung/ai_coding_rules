---
schema_version: v4.0
rule_version: v5.0.0
description: "Comprehensive standards for README.md files following widely accepted industry best practices, ensuring consistent, professional, and accessible project documentation that serves both technical and"
last_updated: 2026-10-06
keywords:
  - kw:README.md structure
  - kw:quick start commands
  - kw:progressive disclosure
  - kw:badge validation
  - kw:clean environment testing
  - kw:author contact section
  - file:README.md
token_budget: ~1200
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 802-project-contributing.md  # Contributing guidelines
    - 805-technical-writing-style.md  # Writing standards (voice, tone, sentence case, inclusive language, accessibility) that apply to README prose
---
# README Best Practices

## Scope

**What This Rule Covers:**
User-first project overview, prerequisites, a primary Quick Start, verified usage, accessible navigation and clear contributor/support boundaries.

**When to Load This Rule:**
When creating, updating or reviewing README content, setup instructions, badges, usage examples or user-facing documentation changes.

## Contract

### Inputs and Prerequisites

- Existing README, actual dependency/build manifests, target audience and supported platforms.
- Verified project capabilities, package/version/license information and authorized test environment.
- Existing contributor/architecture documentation and appropriate public/internal support contacts.

### Mandatory

- Read the README and actual tech-stack manifests before editing. Never infer dependency versions, capabilities, badges or installed tools from a generic template.
- Lead with one H1/title and a concise description of purpose/value (target 160 characters). Use progressive disclosure: overview/prerequisites, Quick Start, usage, contributor pointer, support/contact and licensing as appropriate.
- Show one primary installation path with prerequisites before commands and expected observable results afterward. Put platform alternatives/troubleshooting in clearly labeled sections; state which platforms were tested.
- Test Quick Start and executable examples in a clean environment when authorized. Installation/network/cloud side effects need permission; if unavailable, explicitly label instructions untested, not verified.
- Keep user setup/usage in README, full development/review/validation workflow in CONTRIBUTING. Link rather than duplicate architecture/API detail.
- Include real core API/usage examples with input/output and relevant configuration. Do not leave empty TODO sections or copy fictitious commands.
- Verify links/anchors and current badges; a hardcoded passing badge is not build evidence. Add only relevant status badges with meaningful alt text and actual destinations.
- Preserve license identity from the project's actual LICENSE; do not invent legal terms or claim an open-source license for a private project. Internal READMEs may describe internal access/support instead.
- Operator-authored projects should include approved Author/Contact information. Confirm public name/email/GitHub details from authorized project data; never autofill private identity/contact information from account data without permission. Preserve existing authors in contributed projects.
- Follow writing/accessibility guidance: semantic heading order, sentence case, descriptive links, language-tagged examples, alt text and text alternatives to screenshots. Prefer readable lines near 100 characters, not forced wrapping of URLs/code.
- Update when user behavior, commands, features, support platforms, project structure or workflow changes. Explain AI context/rule loading and measured versus estimated budgets where relevant, without unsupported efficiency claims.

### Execution Steps

1. Read existing README and related docs; verify audience, project type, stack and actual user workflow.
2. Identify changed behavior and required sections; keep scope minimal and avoid contributor-detail duplication.
3. Write the primary Quick Start with prerequisite/expected-result context; add relevant usage/configuration/troubleshooting and approved contacts.
4. Test safe examples and clean setup under authorization, validate links/badges/anchors and platform assumptions.
5. Run Markdown/project documentation checks and compare README claims with actual code/tests/releases.
6. Report tested platforms and any unverified installation/runtime/link checks; do not claim all users can complete setup in an arbitrary time limit.

### Validation

- Purpose, prerequisites, installation, usage and support/license/contribution boundaries are clear and complete for the project.
- Commands/capabilities/versions match current source; one primary path, alternatives explicitly scoped.
- No fabricated badge/build status, license/contact data, untested-success claim or unsafe admin workaround.
- Markdown/anchors/links and accessibility checks pass; examples tested or limitations disclosed.
- README and CONTRIBUTING/architecture docs remain consistent without duplicated maintenance content.

## References

- [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [CommonMark](https://spec.commonmark.org/)
- [Make a README](https://www.makeareadme.com/)
- `805-technical-writing-style.md` for prose and accessibility.
