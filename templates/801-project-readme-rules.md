**Description:** Industry-standard README.md structure, content guidelines, and quality assurance patterns for professional project documentation.
**Type:** Agent Requested
**AppliesTo:** `**/README.md`, `**/readme.md`
**AutoAttach:** false
**Keywords:** README, project documentation, getting started, setup instructions, badges, Quick Start, Contributing, License, project structure, technical writing
**TokenBudget:** ~3500
**ContextTier:** Medium
**Version:** 1.4
**LastUpdated:** 2025-11-21
**Depends:** 000-global-core

# README Best Practices: Professional Project Documentation

## Purpose
This rule establishes comprehensive standards for README.md files following widely accepted industry best practices. It ensures consistent, professional, and accessible project documentation that serves both technical and non-technical audiences.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Project documentation, technical writing, developer experience


## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Start TL;DR (Read First - 30 Seconds)

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
```markdown
## Contributing (in README.md)

**This section and those following are for developers who want to modify or contribute.**  
If you're using the project, setup is complete. See [Troubleshooting](#troubleshooting) for support.

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for complete guidelines.

**Quick Reference:**
```bash
# Essential commands for contributors
```

For detailed workflows, see [CONTRIBUTING.md](CONTRIBUTING.md).
```

### Required Sections (In Order)
- **Requirement:** Every README.md must include these core sections:

```markdown
# Project Title
## Quick Overview (recommended)
## Description  
## Quick Start / Installation
## Usage
## Contributing (minimal pointer to CONTRIBUTING.md)
## License
```

### Recommended Additional Sections
- **Consider:** Include these sections based on project complexity:

```markdown
## Table of Contents
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
- **Always:** Add badges/shields for build status, version, license, and key metrics
- **Rule:** Keep description under 160 characters for social media compatibility
- **Multi-Platform Projects:** Include badges for all hosting platforms (GitHub, GitLab, etc.)

```markdown
# Project Name

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Version](https://img.shields.io/badge/version-1.0.0-orange)]()
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/org/repo)
[![GitLab](https://img.shields.io/badge/GitLab-Repository-orange?logo=gitlab)](https://gitlab.com/org/repo)

> One-line description of what this project does and why it matters
```

### Quick Overview Section (Recommended)

**Purpose:** 30-second elevator pitch before full documentation
**Placement:** Immediately after badges, before Table of Contents

**Format:**
- **What:** One-line project description
- **Works with:** Compatibility/platform info
- **Deploy:** Installation summary
- **Benefit:** Value proposition
- **Quick Checklist:** 4-5 key decision points with anchor links

```markdown
## Quick Overview

**What:** Brief description of what this project provides  
**Works with:** Compatible platforms/tools  
**Deploy:** Simple installation summary  
**Benefit:** Key value proposition

**Quick Checklist:**
- [ ] Prerequisites met? → See [Prerequisites](#prerequisites)
- [ ] Ready to deploy? → See [Quick Start](#quick-start)
- [ ] Want to understand first? → See [Understanding](#understanding)
- [ ] Contributing? → See [Contributing](#contributing)
```

### Quick Start Section
- **Requirement:** Provide immediate value within first 30 seconds of reading
- **Always:** Include the minimal commands to get started
- **Rule:** Test all installation commands on clean systems
- **Multi-Platform:** Show both platform options for dual-hosted repositories

```markdown
## Quick Start

```bash
# Clone the repository (choose one)
# GitHub:
git clone https://github.com/org/repo.git
# GitLab:
git clone https://gitlab.com/org/repo.git

cd repo

# Install
npm install

# Run
npm start
```

**What just happened?**
- Cloned the repository to your local machine
- Installed all dependencies
- Started the development server

**Next Steps:**
- [x] Installation complete → [Configure](#configuration)
- Want to understand how it works → [Understanding](#understanding)
- Need different setup → Continue reading options below
```

### Installation Section  
- **Requirement:** List all prerequisites and system requirements
- **Always:** Provide step-by-step installation instructions
- **Rule:** Include troubleshooting for common installation issues
- **Consider:** Separate installation methods (npm, Docker, manual)
- **Multi-Platform:** Show all repository platform options with "(choose one)" guidance

### Usage Section
- **Requirement:** Include practical, runnable examples
- **Always:** Show the most common use cases first
- **Rule:** Use code blocks with proper syntax highlighting
- **Consider:** Include screenshots for UI-heavy projects

### Understanding/Concepts Section (Recommended)

**Purpose:** Consolidate conceptual explanations between Quick Start and advanced topics
**Placement:** After Quick Start, before detailed configuration/usage

**Include:**
- High-level architecture or system design
- Key concepts and terminology
- How automatic features work (discovery, loading, etc.)
- "Why" rationale for architectural decisions (brief summary, link to detailed docs)

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

### API Documentation
- **Rule:** For libraries, include core API examples in README
- **Consider:** Link to comprehensive API docs hosted elsewhere
- **Always:** Show input/output examples with expected results

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

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for complete guidelines.

**Quick Reference:**
```bash
# Fork and clone
git clone https://github.com/org/repo.git
cd repo

# Set up development environment
npm install

# Make changes, then validate
npm test
npm run lint

# Submit pull request
```

For detailed workflows and examples, see [CONTRIBUTING.md](CONTRIBUTING.md).
```

### License Section
- **Requirement:** Clearly state the project license
- **Always:** Link to full license text
- **Rule:** Use standard license identifiers (MIT, Apache-2.0, GPL-3.0)

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
---
## For Contributors
[content]
```

**Correct Pattern:**
```markdown
## Contributing

**This section and those following are for developers who want to modify or contribute.**  
If you're using the project, setup is complete. See [Troubleshooting](#troubleshooting) for support.
```

**Alternative:** Use Table of Contents grouping:
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

## Accessibility Best Practices

### Inclusive Language
- **Requirement:** Use inclusive, welcoming language
- **Avoid:** Assumptions about user knowledge or background
- **Rule:** Provide context for cultural references or idioms
- **Always:** Use clear, direct language over clever wordplay

### Screen Reader Compatibility
- **Rule:** Use descriptive alt text for images
- **Always:** Structure content with proper heading hierarchy
- **Consider:** Avoid ASCII art or complex visual formatting
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

## Validation Checklist

### Pre-Publication Review
- [ ] **CRITICAL:** README update triggers checked (see 000-global-core.md section 6)
- [ ] **CRITICAL:** If triggers apply, README.md updated before task completion
- [ ] All required sections present and complete

> **Investigation Required**
> When applying this rule:
> 1. **Read existing README BEFORE modifying** - Check current structure
> 2. **Verify project type** - Different projects need different sections
> 3. **Never assume tech stack** - Check actual dependencies
> 4. **Check for existing badges** - Don't duplicate or remove valid ones
> 5. **Test installation steps** - Verify Quick Start actually works
>
> **Anti-Pattern:**
> "Adding Quick Start... (without checking if it works)"
> "Adding badges... (without verifying they're valid)"
>
> **Correct Pattern:**
> "Let me check your existing README structure first."
> [reads README, identifies missing sections, verifies tech stack]
> "I see you're missing Quick Start. Adding installation steps for [tech]..."
- [ ] Installation instructions tested on clean system
- [ ] All code examples are syntactically correct and tested
- [ ] All links are working and point to current resources
- [ ] Badges reflect current project status
- [ ] Language is clear, inclusive, and professional
- [ ] Formatting is consistent throughout
- [ ] Contact/support information is current

### Ongoing Maintenance
- [ ] README updated with significant feature changes
- [ ] Version compatibility information current
- [ ] Dependencies and prerequisites accurate
- [ ] Examples work with current version
- [ ] Links checked and updated quarterly

> **Investigation Required**
> When applying this rule:
> 1. **Read existing README BEFORE modifying** - Check current structure, badges, sections
> 2. **Verify project type** - Different projects need different sections (library vs app vs framework)
> 3. **Never assume tech stack** - Check actual dependencies, build tools, test frameworks
> 4. **Check for existing badges** - Don't duplicate or remove valid badges without reason
> 5. **Test installation steps** - Verify Quick Start commands actually work in clean environment
>
> **Anti-Pattern:**
> "Adding Quick Start section... (without checking if commands work)"
> "Adding badges... (without verifying they're valid for this project)"
>
> **Correct Pattern:**
> "Let me read your existing README first to understand current structure."
> [reads README, package.json, identifies tech stack]
> "I see you're using [tech]. Let me verify the installation commands work..."

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

## Quick Compliance Checklist
- [ ] **CRITICAL:** README update triggers checked (see 000-global-core.md section 6)
- [ ] **CRITICAL:** If triggers apply, README.md reviewed and updated before task completion
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Response Template

```markdown
Project Documentation Changes:

**File Modified:** [README.md|CHANGELOG.md|CONTRIBUTING.md]
**Section Updated:** [specific section]
**Validation:** [documentation standards checklist]

Changes Made:
1. **[Section Name]**
   - Added: [specific content]
   - Updated: [what changed and why]
   - Format: [Markdown standards followed]

2. **[Another Section]**
   - Clarified: [ambiguous content]
   - Examples: [added working examples]

Validation Checklist:
- [x] Markdown lint passes
- [x] Links are valid and accessible
- [x] Code examples are tested
- [x] Formatting is consistent
- [x] Table of contents updated (if applicable)

Preview:
[Show relevant excerpt of updated documentation]
```

## References

### External Documentation
- [GitHub README Guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) - Official GitHub documentation standards                    
- [Make a README](https://www.makeareadme.com/) - Interactive README creation guide and best practices
- [Awesome README Examples](https://github.com/matiassingers/awesome-readme) - Curated collection of excellent README examples

### Related Rules
- **Global Core**: `000-global-core.md`
- **Changelog Rules**: `800-project-changelog-rules.md`
- **Contributing Guidelines**: `805-project-contributing-rules.md`
