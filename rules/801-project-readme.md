# README Best Practices: Professional Project Documentation

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**Keywords:** README, project documentation, getting started, setup instructions, badges, Quick Start, Contributing, License, project structure, technical writing, author contact, maintainer
**TokenBudget:** ~5100
**ContextTier:** Medium
**Depends:** 000-global-core.md
**LoadTrigger:** kw:readme, kw:documentation, file:README.md

## Scope

**What This Rule Covers:**
Comprehensive standards for README.md files following widely accepted industry best practices, ensuring consistent, professional, and accessible project documentation that serves both technical and non-technical audiences.

**When to Load This Rule:**
- Creating or updating README.md files
- Reviewing project documentation standards
- Establishing Quick Start sections for users
- Defining project structure and setup instructions
- Implementing professional documentation practices

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules

**Related:**
- **800-project-changelog.md** - Changelog management standards
- **802-project-contributing.md** - Contributing guidelines
- **803-project-git-workflow.md** - Git workflow management

### External Documentation
- [GitHub README Guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) - Official GitHub documentation standards
- [Make a README](https://www.makeareadme.com/) - Interactive README creation guide and best practices
- [Awesome README Examples](https://github.com/matiassingers/awesome-readme) - Curated collection of excellent README examples
- [CommonMark Spec](https://spec.commonmark.org/) - Authoritative Markdown specification (README.md MUST comply)

## Contract

### Inputs and Prerequisites
- Project repository with README.md file
- Understanding of project type (library, application, framework)
- Knowledge of target audience (technical/non-technical)
- Access to project dependencies and tech stack information

### Mandatory
- MUST read existing README.md before modifying
- MUST test Quick Start commands in a clean environment
- MUST include project description under 160 characters
- MUST verify all links are working before completing
- MUST include Author/Contact section in all operator-authored projects with operator identity block

### Forbidden
- Adding Quick Start without testing commands
- Duplicating content from CONTRIBUTING.md in README
- Using hard-coded paths or environment-specific instructions
- Adding badges without verifying they work
- Assuming tech stack without verification
- Non-compliant Markdown (must follow [CommonMark spec](https://spec.commonmark.org/))

### Execution Steps
1. Read existing README.md to understand current structure
2. Identify project type and verify tech stack
3. Test all installation commands in clean environment
4. Create or update Quick Start section with ONE primary path
5. Add post-action explanations after command blocks
6. Verify all links are working and current
7. Update badges to reflect current project status
8. Validate markdown syntax and formatting

### Output Format
Markdown file (README.md) with:
- Project title and description
- Quick Overview section (30-second summary)
- Quick Start with tested installation commands
- Usage examples with code blocks
- Contributing section (minimal pointer to CONTRIBUTING.md)
- License section

### Validation
**Pre-Task-Completion Checks:**
- README update triggers checked (see 000-global-core.md)
- All required sections present and complete
- Installation instructions tested on clean system
- All code examples syntactically correct and tested
- All links working and pointing to current resources
- Badges reflect current project status
- Language passes readability check: Flesch-Kincaid grade level ≤12
- No jargon used without definition on first occurrence
- No gendered pronouns (use "they/them" or rephrase)
- No slang, colloquialisms, or culture-specific idioms

**Success Criteria:**
- README.md validates with markdown linter
- All links accessible and valid
- Quick Start commands work in clean environment
- Code examples tested and functional
- Formatting consistent throughout
- Contact/support information current

### Design Principles
- **Progressive Disclosure** - Users first, contributors second
- **One Primary Path** - Show simplest installation method in Quick Start
- **Immediate Feedback** - Users see results within 60 seconds
- **Clear Success Indicators** - Tell users what they should see
- **Investigation-First** - Read existing README before modifying
- **Directive Hierarchy** - Priority order: Critical > Mandatory > Always > Requirement > Rule > Consider

### Post-Execution Checklist
- [ ] **CRITICAL:** README update triggers checked (see 000-global-core.md)
- [ ] **CRITICAL:** If triggers apply, README.md reviewed and updated
- [ ] Existing README structure checked before modifications
- [ ] Project type and tech stack verified
- [ ] Installation commands tested in clean environment
- [ ] All code examples syntactically correct
- [ ] All links working and current
- [ ] Badges reflect current status
- [ ] Formatting consistent throughout
- [ ] Contributing section links to CONTRIBUTING.md
- [ ] License section present with key points

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Adding Quick Start Without Testing Commands

**Problem:** Creating Quick Start section with installation commands that haven't been tested in a clean environment.

**Why It Fails:** Commands may fail due to missing dependencies, incorrect paths, or environment-specific assumptions. Users get frustrated when the "quick" start doesn't work, eroding trust in the project documentation.

**Correct Pattern:**
````markdown
## Quick Start

**Prerequisites:** Node.js 18+, npm 9+

```bash
# Clone and install
git clone https://github.com/org/repo.git
cd repo
npm install

# Run
npm start
```

**What just happened?**
- Cloned repository to your local machine
- Installed all dependencies from package.json
- Started development server on http://localhost:3000

**Next Steps:** See [Configuration](#configuration) for customization options.
````

#### Platform-Specific Troubleshooting

If commands differ between macOS, Linux, and Windows, show the primary platform first
with a collapsible `<details>` block for alternatives. Always specify which OS was tested.

**Example:**
````markdown
## Quick Start

**Tested on:** macOS 14, Ubuntu 22.04

```bash
# Clone and install
git clone https://github.com/org/repo.git
cd repo
npm install
```

<details>
<summary>Windows instructions</summary>

```powershell
git clone https://github.com/org/repo.git
cd repo
npm install
```

**Note:** Use PowerShell, not Command Prompt. If `npm install` fails, try running
as Administrator or use `npm install --no-optional`.

</details>
````

**Key Principles:**
- State which OS was tested in the Quick Start header
- Use `<details>` for alternative platforms — keeps primary path clean
- Include platform-specific error resolutions
- Never assume a single platform without stating it

### Anti-Pattern 2: Duplicating CONTRIBUTING.md Content in README

**Problem:** Including detailed development workflow, environment setup, and contribution guidelines in README instead of linking to CONTRIBUTING.md.

**Why It Fails:** Creates maintenance burden (two places to update), overwhelms end users with contributor information, violates progressive disclosure principle.

**Correct Pattern:** Use the Contributing boundary pattern from [Content Boundaries](#content-boundaries-readme-vs-contributingmd) — minimal pointer with quick reference commands, full workflow in CONTRIBUTING.md.

### Anti-Pattern 3: Assuming Tech Stack Without Verification

**Problem:** Adding installation instructions or badges based on assumptions rather than checking actual project dependencies.

**Why It Fails:** Incorrect instructions confuse users, invalid badges damage credibility, may recommend wrong tools or versions.

**Correct Pattern:**
```markdown
# Investigation-First Approach

1. Read existing README.md
2. Check package.json / pyproject.toml / go.mod for actual dependencies
3. Verify build tools and test frameworks
4. Test installation commands in clean environment
5. Only then add/update README sections
```

### Anti-Pattern 4: Broken Badge URLs After Deployment

**Problem:** Badge URLs become invalid after service changes, repository moves, or service deprecation.

**Why It Fails:** Broken badges damage credibility, confuse users about project status, and suggest unmaintained project. Users may question reliability if basic documentation elements are broken.

**Correct Pattern:**
- Validate badge URLs in CI: `grep -oP 'https://[^)]+\.svg' README.md | xargs -I{} curl -f -s -o /dev/null {}`
- If broken: check service docs for new URL format, update redirects, or migrate to shields.io
- Use shields.io for custom badges (stable, maintained service)
- Test badges in pull request validation

### Investigation Required

Before modifying any README.md, complete these checks:

1. **Check if README.md exists:** `ls README.md` — if missing, use the Required Sections template (line 249)
2. **Identify project type:** Check `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, or `Gemfile` for actual tech stack
3. **Verify current badges are functional:** `grep -oP 'https://[^)]+\.svg' README.md | xargs -I{} curl -f -s -o /dev/null {}`
4. **Check CONTRIBUTING.md exists:** `ls CONTRIBUTING.md` — if present, verify no content duplication per Content Boundaries pattern
5. **Identify target audience:** Check if project is library (API docs needed), application (setup docs needed), or framework (tutorial needed)

## Implementation Details

### Quick Start TL;DR for README Content

**Essential Patterns:**
- **Required sections** - Title, Description, Quick Start, Usage, Contributing, License
- **Quick Start first** - Get users running ASAP
- **Badge placement** - Build status, version, license at top
- **Code examples** - Show actual usage, not just API docs
- **Prerequisites clear** - List all dependencies upfront
- **Never assume knowledge** - Explain setup steps clearly

## Essential README Structure

### Content Boundaries: README vs CONTRIBUTING.md

**Principle:** Progressive disclosure - users first, contributors second

**README.md Should Contain:**
- Project overview and value proposition
- Quick Overview section (30-second summary)
- Quick Start for end users
- Installation and usage instructions
- Understanding/concepts section
- Troubleshooting for users
- Minimal contributor pointer with quick reference commands
- License and acknowledgments

**CONTRIBUTING.md Should Contain:**
- Complete development workflow
- Environment setup details
- Code quality and linting procedures
- Rule authoring/coding standards
- PR templates and review process
- Configuration safety guidelines
- Testing requirements
- Validation procedures

**Boundary Pattern:**
````markdown

## Contributing (in README.md)

**This section and those following are for developers who want to modify or contribute.**
If you're using the project, setup is complete. See [Troubleshooting](#troubleshooting) for support.

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for complete guidelines.

**Quick Reference:**
```bash
# Essential commands for contributors
```

For detailed workflows, see [CONTRIBUTING.md](CONTRIBUTING.md).
````

### Required Sections (In Order)
- **Requirement:** Every README.md must include these core sections:

```markdown
# Project Title

## Quick Overview (recommended)

## Description

## Quick Start

## Usage

## Contributing (minimal pointer to CONTRIBUTING.md)

## Author / Contact

## License
```

### Recommended Additional Sections
- **For complex projects:** Features, Prerequisites, Configuration, API Documentation, Examples, Testing, Deployment, FAQ, Support, Acknowledgments, Changelog
- **Consider:** Table of Contents with separate "For Users" and "For Contributors" groupings

## Content Guidelines

### Project Title and Description
- **Requirement:** Use a single H1 (`#`) for the project title
- **Requirement:** Include a concise one-line description immediately after the title
- **Always:** Add badges/shields for build status, version, license, test coverage, and download count
- **Requirement:** Description ≤160 characters (validate with `wc -c`)
- **Multi-Platform Projects:** Include badges for hosting platforms

```markdown
# Project Name

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Version](https://img.shields.io/badge/version-1.0.0-orange)]()
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/org/repo)

> One-line description of what this project does and why it matters
```

### Quick Overview Section (Recommended)

**Purpose:** 30-second elevator pitch before full documentation
**Placement:** Immediately after badges, before Table of Contents
**Requirement:** Include Quick Checklist with prerequisite verification link

**Format:**
- **What:** One-line project description
- **Works with:** Compatibility/platform info
- **Deploy:** Installation summary ("2 commands", "3 steps", etc.)
- **Benefit:** Key value proposition
- **Quick Checklist:** 4-5 key decision points with anchor links

```markdown

## Quick Overview

**What:** Brief description of what this project provides
**Works with:** Compatible platforms/tools
**Deploy:** Simple installation summary (e.g., "2 commands")
**Benefit:** Key value proposition

**Quick Checklist:**
- [ ] Prerequisites met? See [Prerequisites](#prerequisites)
- [ ] Ready to deploy? See [Quick Start](#quick-start)
- [ ] Want to understand first? See [Understanding](#understanding)
- [ ] Contributing? See [Contributing](#contributing)
```

**Why This Works:**
- Users can self-assess readiness before diving in
- Reduces support questions about prerequisites
- Provides clear navigation to relevant sections
- Sets expectations for installation complexity

### Quick Start Section
- **Requirement:** Provide immediate value within first 30 seconds of reading
- **Always:** Include the minimal commands to get started
- **Rule:** Test all installation commands on clean systems
- **Multi-Platform:** Show both platform options for dual-hosted repositories
- **Note:** "Quick Start" and "Installation" may be used interchangeably, but prefer "Quick Start" for consistency

```markdown

## Understanding [System Name]

### What Are [Core Concepts]?
[1-2 paragraph explanation of fundamental concepts]

### How [Automatic Feature] Works
1. [Step-by-step walkthrough]
2. [Show progression]
3. [Explain outcomes]

### Why [Design Decision]?
[Brief summary with key benefits]

**For complete architectural details, see [ARCHITECTURE.md](ARCHITECTURE.md) or [Design Decisions](#design-decisions) section.**
```

### Context-Aware Documentation (for AI/LLM Projects)

**For AI projects,** document the following:
- Document token budgets or context limitations
- Explain modular loading strategies
- Include searchable indexes (e.g., RULES_INDEX.md pattern)

**Example:**
```markdown
## Rule Categories

**Rule Domain Overview:**
- **Core:** 7 rules, ~900 tokens - Always load
- **Python:** 15 rules, ~4500 tokens - Load on demand
```

**When to use:**
- Projects with AI coding rules or prompts
- Agent systems with context window management
- Modular documentation systems
- Projects optimizing for LLM consumption

### API Documentation
- **Rule:** For libraries, include core API examples in README
- **Consider:** Link to comprehensive API docs hosted elsewhere
- **Always:** Show input/output examples with expected results

### License Section

**Requirement:** Every README must include a License section
**Always:** Link to LICENSE file
**Consider:** Include key points summary for common licenses
**Rule:** State contribution licensing terms

**Minimal Pattern:**
```markdown
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

**Enhanced Pattern (Recommended):**
```markdown
## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

**Key Points:**

- [PASS] Commercial use permitted
- [PASS] Modification and distribution allowed
- [PASS] Patent grant included
- [WARN] Trademark use NOT granted
- [WARN] No warranty provided

**Contributing:** By submitting a pull request, you agree to license your contribution under Apache 2.0.
```

### Contributing Section
- **Requirement:** Link to CONTRIBUTING.md if it exists
- **Always:** Include minimal pointer with quick reference commands
- **Rule:** Use boundary statement to separate user/contributor content — see [Content Boundaries](#content-boundaries-readme-vs-contributingmd)
- **Avoid:** Duplicating detailed contribution workflows from CONTRIBUTING.md in README

## Quality and Formatting

- **Requirement:** Use consistent heading hierarchy (H1 > H2 > H3), fenced code blocks with language identifiers
- **Requirement:** All code examples must be syntactically correct and tested
- **Rule:** Use descriptive link text — avoid "click here"
- **Always:** Keep line length ≤100 characters
- **Rule:** Include table of contents for long READMEs (>500 lines)
- **Avoid:** Horizontal rule markers (`---`) for content separation — use text-based boundary statements instead

## Lifecycle: README Update Triggers

**Reference:** Pre-Task-Completion Validation Gate in `000-global-core.md` section 6

**CRITICAL:** README.md updates are MANDATORY when these triggers apply:
- Adding, removing, or significantly modifying rule files
- Changes to project structure or file organization
- Updates to development workflows or commands
- Feature completion that moves items from roadmap to implemented
- Adding new IDE/agent support
- Modifying generation scripts or automation tools

**Exception:** Only skip if user explicitly requests override (acknowledge README may be outdated).

## Common Anti-Patterns to Avoid

### Content Issues
- **Avoid:** Wall of text without structure or formatting
- **Avoid:** Outdated installation instructions or broken examples
- **Avoid:** Assuming prior knowledge without providing context
- **Avoid:** Marketing speak without technical substance

### Structure Problems
- **Avoid:** Missing or unclear project title
- **Avoid:** Burying important information deep in the file
- **Avoid:** Inconsistent formatting and style
- **Avoid:** Too many sections for simple projects

### Maintenance Problems
- **Avoid:** Stale badges showing incorrect status
- **Avoid:** Dead links to documentation or resources
- **Avoid:** Version information that doesn't match releases
- **Avoid:** Examples that no longer work with current version

## Integration with Development Workflow

### Code Review Process
- **Rule:** Include README changes in pull request reviews
- **Always:** Verify examples work with proposed changes
- **Consider:** Require README updates for new features
- **Rule:** Check for consistency with existing documentation

### Automation Opportunities
- **Consider:** Auto-generate API documentation sections
- **Rule:** Validate markdown syntax in CI/CD pipeline
- **Consider:** Automated link checking and badge updates
- **Always:** Include README in documentation deployment process

## Accessibility in README Content

- MUST include alt text for all images and badges in README
- SHOULD use text labels alongside color-coded badges so meaning is not color-dependent
- Avoid relying solely on images or screenshots to convey critical setup information
- Use semantic heading hierarchy for screen reader navigation
- Ensure code blocks have language identifiers for syntax highlighting tools

## Author / Contact Section

**Requirement:** Every README for a project authored by the operator MUST include an Author / Contact section.

**Placement:** After Contributing, before License.

**Single Author Template:**
```markdown
## Author

**Your Name** — Organization
- Email: your.email@example.com
- GitHub: [@your-handle](https://github.com/your-handle)
```

**Multiple Authors Template:**
```markdown
## Authors

| Name | Role | Contact |
|------|------|---------|
| Author Name | Lead | author@example.com |
| Contributor Name | Role | contributor@example.com |
```

**Rules:**
- MUST appear in every project the operator creates or is the primary author of
- MUST include at minimum: name, email, and GitHub handle
- MAY include role, team, or Slack channel for internal projects
- Agent SHOULD check AGENTS.md or operator profile for contact details to auto-populate
- For forked or contributed projects, add to existing Authors section rather than replacing

## Internal Project README Considerations

For internal/private project READMEs, also consider:
- Include team/owner contact information and escalation paths (see also [Author / Contact Section](#author--contact-section))
- Reference internal wiki or Confluence for extended documentation
- Include deployment environment details (staging URLs, internal endpoints)
- MAY omit License section for internal-only projects
- Include links to internal CI/CD dashboards and monitoring

## README Anti-Patterns to Avoid

> **Note:** See also [Anti-Patterns and Common Mistakes](#anti-patterns-and-common-mistakes) for detailed patterns with Problem/Correct format.

- **Empty sections with "TODO" placeholders** — Remove sections until content is ready rather than leaving stubs
- **Screenshots without text alternatives** — Always include descriptive text alongside visual content (see also Accessibility, line 475)
- **Installation instructions that skip prerequisites** — List all required tools and versions before commands (see AP1)
- **"Just run `npm install`" without explaining what the project does** — Always lead with project purpose (see AP3)
