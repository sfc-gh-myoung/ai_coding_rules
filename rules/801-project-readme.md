# README Best Practices: Professional Project Documentation

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** README, project documentation, getting started, setup instructions, badges, Quick Start, Contributing, License, project structure, technical writing
**TokenBudget:** ~4500
**ContextTier:** Medium
**Depends:** rules/000-global-core.md

## Purpose
This rule establishes comprehensive standards for README.md files following widely accepted industry best practices. It ensures consistent, professional, and accessible project documentation that serves both technical and non-technical audiences.

## Rule Scope
Project documentation, technical writing, developer experience

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **One primary path** - Show the simplest, most common installation method first
- **2-4 commands maximum** - Clone, install, run - that's it
- **Immediate feedback** - User sees something working within 60 seconds
- **Clear success indicator** - Tell users what they should see when it works
- **Next steps signposted** - Point to configuration, deployment, or docs

**Pre-Execution Checklist:**
- [ ] Identified the most common/simplest installation path
- [ ] Verified commands work on fresh environment
- [ ] Prepared clear success indicators for users
- [ ] Planned where to direct users after Quick Start
- [ ] Separated alternative methods to dedicated sections

**Example:**
```bash
# Clone the repository
git clone https://github.com/org/repo.git

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
- [PASS] Installation complete - See [Configure](#configuration)
- [?] Want to understand how it works - See [Understanding](#understanding)
- [!] Need different setup - Continue reading options below

### Quick Start Complexity Management

**Rule:** Limit Quick Start to ONE primary path for immediate success
**Always:** Move alternative installation methods to separate "Deployment Options" section
**Consider:** Use "Need different setup?" link to alternatives section
**Avoid:** Presenting multiple options (A, B, C, D) in Quick Start - creates decision fatigue

**Anti-Pattern:**
```markdown
## Quick Start
Choose option A, B, C, or D...
[Four different installation paths]
```

**Correct Pattern:**
```markdown
## Quick Start

**Get started in 2 commands:**

    # 1. Simple path
    # 2. Primary installation

**That's it!** Installation complete.

**Need different setup?** See [Deployment Options](#deployment-options)
```

### Installation Section
- **Requirement:** List all prerequisites and system requirements
- **Always:** Provide step-by-step installation instructions
- **Rule:** Include troubleshooting for common installation issues
- **Consider:** Separate installation methods (npm, Docker, manual)
- **Multi-Platform:** Show all repository platform options with "(choose one)" guidance

### Post-Action Explanations ("What just happened?")

**Requirement:** After EVERY command block in Quick Start, include "What just happened?" section
**Always:** Explain in user-friendly terms (avoid jargon)
**Rule:** List 2-4 bullet points describing state changes
**Format:** Use checkmarks and past tense ("[PASS] Cloned", "[PASS] Installed", "[PASS] Started")

**Pattern:**
```markdown
    npm install
    npm start
```

**What just happened?**

- [PASS] Installed all dependencies from package.json
- [PASS] Started development server on http://localhost:3000
- [PASS] Enabled hot-reload for code changes

**Next Steps:** [link to next section]
```

**Anti-Pattern:**
```bash
npm install && npm start
# Good to go!
```
[FAIL] No explanation of state change or what was accomplished

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
## Contract

<contract>
<inputs_prereqs>
[Context, files, dependencies needed]
</inputs_prereqs>

<mandatory>
[Tools permitted for this domain]
</mandatory>

<forbidden>
[Tools not allowed for this domain]
</forbidden>

<steps>
[Ordered steps the agent must follow]
</steps>

<output_format>
[Expected output format]
</output_format>

<validation>
[Checks to confirm success]
</validation>

</contract>

## Anti-Patterns and Common Mistakes

### Pattern 1: [Common Mistake Title]

**Problem:**
[Describe what developers commonly do wrong]

**Why It Fails:**
[Explain why this approach causes issues]

**Correct Pattern:**
```python
# Correct approach with explanation
```

### Pattern 2: [Another Common Mistake]

**Problem:**
[Description of the anti-pattern]

**Why It Fails:**
[Technical explanation of the problem]

**Correct Pattern:**
```python
# Proper implementation
```

## Post-Execution Checklist
- [ ] **CRITICAL:** README update triggers checked (see 000-global-core.md section 6)
- [ ] **CRITICAL:** If triggers apply, README.md reviewed and updated before task completion
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation

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

## Output Format Examples

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
- **Global Core**: `rules/000-global-core.md`
- **Changelog Rules**: `rules/800-project-changelog.md`
- **Contributing Guidelines**: `rules/802-project-contributing.md`

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

**For Users:**
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

**For Contributors:**
- [Contributing](#contributing)
- [Development](#development)
- [Testing](#testing)
```

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

**Consider:** For projects involving AI, LLMs, or context windows:
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

**Validation:** Test with screen reader (NVDA, JAWS, VoiceOver)

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
