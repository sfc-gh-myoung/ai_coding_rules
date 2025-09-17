**Description:** Industry-standard README.md structure, content guidelines, and quality assurance patterns for professional project documentation.
**AppliesTo:** `**/README.md`, `**/readme.md`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-09-10

# README Best Practices: Professional Project Documentation

## Purpose
This rule establishes comprehensive standards for README.md files following widely accepted industry best practices. It ensures consistent, professional, and accessible project documentation that serves both technical and non-technical audiences.

## Essential README Structure

### Required Sections (In Order)
- **Requirement:** Every README.md must include these core sections:

```markdown
# Project Title
## Description  
## Quick Start / Installation
## Usage
## Contributing
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

```markdown
# Project Name

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Version](https://img.shields.io/badge/version-1.0.0-orange)]()

> One-line description of what this project does and why it matters
```

### Quick Start Section
- **Requirement:** Provide immediate value within first 30 seconds of reading
- **Always:** Include the minimal commands to get started
- **Rule:** Test all installation commands on clean systems

```markdown
## Quick Start

```bash
# Install
npm install project-name

# Run
npm start
```

### Installation Section  
- **Requirement:** List all prerequisites and system requirements
- **Always:** Provide step-by-step installation instructions
- **Rule:** Include troubleshooting for common installation issues
- **Consider:** Separate installation methods (npm, Docker, manual)

### Usage Section
- **Requirement:** Include practical, runnable examples
- **Always:** Show the most common use cases first
- **Rule:** Use code blocks with proper syntax highlighting
- **Consider:** Include screenshots for UI-heavy projects

### API Documentation
- **Rule:** For libraries, include core API examples in README
- **Consider:** Link to comprehensive API docs hosted elsewhere
- **Always:** Show input/output examples with expected results

### Contributing Section
- **Requirement:** Link to CONTRIBUTING.md if it exists
- **Always:** Include basic contribution workflow
- **Rule:** Specify code style and testing requirements

```markdown
## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `npm test`
5. Submit a pull request
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

### Maintenance Practices
- **Requirement:** Review README quarterly for accuracy
- **Always:** Update links, dependencies, and examples
- **Rule:** Archive or redirect outdated information
- **Consider:** Set up automated link checking

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
- [ ] All required sections present and complete
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

## References

### External Documentation
- [GitHub README Guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) - Official GitHub documentation standards
- [Make a README](https://www.makeareadme.com/) - Interactive README creation guide and best practices
- [Awesome README Examples](https://github.com/matiassingers/awesome-readme) - Curated collection of excellent README examples
- [Markdown Guide](https://www.markdownguide.org/) - Complete Markdown syntax reference and formatting guide
- [Conventional Commits](https://www.conventionalcommits.org/) (for changelog integration)

## Rule Type and Scope

- **Type:** Agent Requested (see header metadata - use `@801-project-readme-rules.md` to apply)
- **Scope:** Project documentation, technical writing, developer experience
- **Applies to:** All README.md files, project documentation
- **Validation:** Manual review and automated markdown checking
