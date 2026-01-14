# README Best Practices: Professional Project Documentation

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** README, project documentation, getting started, setup instructions, badges, Quick Start, Contributing, License, project structure, technical writing
**TokenBudget:** ~5350
**ContextTier:** Medium
**Depends:** 000-global-core.md

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
- Text editor for README.md
- Markdown validation tools
- Link checker for external references
- Understanding of project structure and setup

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
- Language is clear, inclusive, and professional

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

### Anti-Pattern 2: Duplicating CONTRIBUTING.md Content in README

**Problem:** Including detailed development workflow, environment setup, and contribution guidelines in README instead of linking to CONTRIBUTING.md.

**Why It Fails:** Creates maintenance burden (two places to update), overwhelms end users with contributor information, violates progressive disclosure principle.

**Correct Pattern:**
```markdown
## Contributing

**This section is for developers who want to modify or contribute.**
If you're using the project, setup is complete. See [Troubleshooting](#troubleshooting) for support.

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for complete guidelines.

**Quick Reference:**
```bash
task quality:fix  # Fix code quality issues
task test         # Run tests
task validate     # Run all checks
```

For detailed workflows, see [CONTRIBUTING.md](CONTRIBUTING.md).
```

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
```markdown
## Automated Badge Validation

Add to Taskfile.yml:

```yaml
validate:badges:
  desc: Verify all README badges are accessible
  cmds:
    - |
      grep -oP 'https://[^)]+\.svg' README.md | while read url; do
        if ! curl -f -s -o /dev/null "$url"; then
          echo "BROKEN: $url"
          exit 1
        fi
      done
    - echo "All badges validated"
```

**Recovery Procedure:**
1. Test all badge URLs: `curl -I [badge_url]` (expect HTTP 200)
2. If 404: Check service documentation for new URL format
3. If 301/302: Update to final redirect destination URL
4. If service deprecated: Remove badge or migrate to alternative service (shields.io)
5. Add badge validation to CI/CD pipeline
6. Document badge service dependencies in CONTRIBUTING.md

**Prevention:**
- Use shields.io for custom badges (stable, maintained service)
- Avoid service-specific badges when alternatives exist
- Test badges in pull request validation
- Monitor badge status monthly
```

## Implementation Details

### Quick Start TL;DR for README Content

**MANDATORY:**
**Essential Patterns:**
- **Required sections** - Title, Description, Quick Start, Usage, Contributing, License
- **Quick Start first** - Get users running ASAP
- **Badge placement** - Build status, version, license at top
- **Code examples** - Show actual usage, not just API docs
- **Prerequisites clear** - List all dependencies upfront
- **Maintainability info** - How to contribute, where to report issues
- **Never assume knowledge** - Explain setup steps clearly

**Quick Checklist:**
- [ ] Title clear and descriptive
- [ ] Description explains purpose
- [ ] Quick Start/Installation section
- [ ] Usage examples with code
- [ ] Contributing guidelines linked
- [ ] License specified
- [ ] Badges (if applicable)

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

## License
```

### Recommended Additional Sections
- **For complex projects,** include these sections based on project complexity:

```markdown

## Table of Contents

**For Users:**
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

**For Contributors:**
- [Contributing](#contributing)
- [Development](#development)
- [Testing](#testing)
```

```markdown
## Features

## Prerequisites

## Configuration

## API Documentation

## Examples

## Testing

## Deployment

## FAQ

## Support

## Acknowledgments

## Changelog
```

## Content Guidelines

### Project Title and Description
- **Requirement:** Use a single H1 (`#`) for the project title
- **Requirement:** Include a concise one-line description immediately after the title
- **Always:** Add badges/shields for build status, version, license, test coverage, and download count
- **Rule:** Keep description under 160 characters for social media compatibility
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

### Directive Language Hierarchy Documentation (Optional)

**Consider:** For rule-based or policy-driven projects, document directive hierarchy

**Pattern:** Show priority levels for behavioral guidance
- Priority order: Critical, then Mandatory, then Always, then Requirement, then Rule, then Consider
- Include visual indicators (colors, symbols, emoji) for priority levels

**When to use:** Projects with:
- Coding standards or style guides
- Compliance requirements
- Multi-agent AI systems
- Quality gates or approval workflows

**Example:**
```markdown
## Directive Language Hierarchy

Priority levels (highest to lowest):
- **Critical** - System Safety [RED] - Must never violate
- **Mandatory** - Non-negotiable [ORANGE] - Must always follow
- **Always** - Universal Practice [YELLOW] - Should be consistent
- **Requirement** - Technical Standard [BLUE] - Should implement
- **Rule** - Best Practice [GREEN] - Recommended pattern
- **Consider** - Optional [WHITE] - Suggestions & alternatives

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

**Why Include Key Points:**
- Saves users time reading full license text
- Clarifies common questions upfront
- Sets expectations for contribution terms
- Highlights important restrictions (trademark, warranty)

### Contributing Section
- **Requirement:** Link to CONTRIBUTING.md if it exists
- **Always:** Include minimal pointer with quick reference commands
- **Rule:** Use boundary statement to separate user/contributor content
- **Avoid:** Duplicating detailed contribution workflows from CONTRIBUTING.md in README
- **Pattern:** Quick reference commands acceptable, full workflow belongs in CONTRIBUTING.md

```markdown

## Contributing

**This section and those following are for developers who want to modify or contribute.**
If you're using the project, setup is complete. See [Troubleshooting](#troubleshooting) for support.
```

**Alternative:** Use Table of Contents grouping:
```markdown

## Formatting Standards

### Markdown Syntax
- **Requirement:** Use consistent heading hierarchy (H1 > H2 > H3)
- **Always:** Use fenced code blocks with language identifiers
- **Rule:** Use `**bold**` for emphasis, `*italics*` for subtle emphasis
- **Avoid:** Mixing heading styles (`#` vs `===`)

### Code Examples
- **Requirement:** All code examples must be syntactically correct
- **Always:** Include language identifiers in fenced blocks
- **Rule:** Test all code examples before publishing
- **Consider:** Use line numbers for longer examples

```bash
# Good: Language identifier included
npm install package-name
```

### Links and References
- **Rule:** Use descriptive link text, avoid "click here"
- **Always:** Verify all links are working and current
- **Consider:** Use reference-style links for cleaner formatting

```markdown
# Good
See the [API documentation](https://example.com/docs) for details.

# Avoid
Click [here](https://example.com/docs) for more info.
```

## Quality Assurance

### Content Validation
- **Requirement:** README must be accurate and up-to-date
- **Always:** Update README when making significant changes
- **Rule:** Review README during code review process
- **Consider:** Automate README validation in CI/CD

### Readability Standards
- **Rule:** Use clear, concise language appropriate for target audience
- **Always:** Define technical terms and acronyms on first use
- **Consider:** Include a glossary for domain-specific terminology
- **Avoid:** Jargon without explanation

### Visual Organization
- **Rule:** Use whitespace effectively to improve readability
- **Always:** Keep line length under 80-100 characters
- **Consider:** Use tables for structured information
- **Rule:** Include table of contents for long READMEs (>500 lines)

### Visual Separation Patterns

**Avoid:** Horizontal rule markers (`---`) for content separation
**Problem:** Overused by LLMs, creates visual noise without semantic meaning
**Correct Pattern:** Use text-based boundary statements in section headers or TOC grouping

**Anti-Pattern:**
```markdown

## For Users
[content]

## For Contributors
[content]
```

### Visual Element Accessibility

**Rule:** For ASCII art, diagrams, or complex visual formatting:
- **Always:** Provide text-based alternative or description
- **Consider:** Use `<details>` tag to collapse visual elements
- **Consider:** Use Mermaid diagrams (more accessible than ASCII art)
- **Requirement:** Include descriptive summary before visual element

**Pattern:**
```markdown
<details>
<summary>[CHART] Visual Decision Tree (expand for diagram)</summary>

```ascii
[ASCII art diagram]
```

</details>

### Text-Based Alternative

**Step 1:** Identify your primary technology
- Python: Load 200-python-core
- Snowflake: Load 100-snowflake-core

**Step 2:** Select your use case
- Python + FastAPI: Load 210-python-fastapi-core
- Snowflake + Streamlit: Load 101-snowflake-streamlit-core
```

**Validation:** Test with screen reader (NVDA, JAWS, VoiceOver, or equivalent accessibility testing tool)

**Why This Matters:**
- Screen readers cannot interpret ASCII art
- Text alternatives serve users with visual impairments
- Collapsible sections keep README clean for all users

**Correct Pattern:**
```markdown

## Accessibility Best Practices

### Inclusive Language
- **Requirement:** Use inclusive, welcoming language
- **Avoid:** Assumptions about user knowledge or background
- **Rule:** Provide context for cultural references or idioms
- **Always:** Use clear, direct language over clever wordplay

### Screen Reader Compatibility
- **Rule:** Use descriptive alt text for images
- **Always:** Structure content with proper heading hierarchy
- **Rule:** Provide text alternatives for ASCII art or complex visual formatting
- **Rule:** Ensure links have descriptive text

### International Considerations
- **Consider:** Provide translations for global projects
- **Rule:** Use universal examples and references
- **Always:** Include timezone information for events/releases
- **Avoid:** Culture-specific assumptions

## Project Lifecycle Management

### Version Control Integration
- **Rule:** Keep README in sync with codebase changes
- **Always:** Update version numbers and compatibility information
- **Consider:** Automate README updates through CI/CD
- **Rule:** Tag README changes in commit messages

### Maintenance Practices (MANDATORY for Trigger Events)

**Reference:** Pre-Task-Completion Validation Gate in `000-global-core.md` section 6 and `AGENTS.md`

**CRITICAL:** README.md updates are MANDATORY when update triggers apply.

- **MANDATORY:** Review README.md after task completion to check if any triggers from `000-global-core.md` section 6 apply
- **CRITICAL:** If triggers apply, update README.md BEFORE marking task complete
- **Requirement:** Review README quarterly for accuracy
- **Always:** Update links, dependencies, and examples
- **Rule:** Archive or redirect outdated information
- **Consider:** Set up automated link checking
- **Exception:** Only skip README updates if user explicitly requests override (acknowledge that README may be outdated)

### README Update Triggers (from 000-global-core.md)
These changes REQUIRE README updates before task completion:
- Adding, removing, or significantly modifying rule files
- Changes to project structure or file organization
- Updates to development workflows or commands
- Feature completion that moves items from roadmap to implemented
- Adding new IDE/agent support
- Modifying generation scripts or automation tools

### Evolution Patterns
- **Rule:** Start simple, add complexity as project grows
- **Always:** Maintain backward compatibility in examples
- **Consider:** Separate detailed docs from README as project matures
- **Rule:** Keep README focused on getting started quickly

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
