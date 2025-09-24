**Description:** Universal standards for creating and maintaining AI coding rule files across all models and editors.
**AppliesTo:** `**/*-*.md` rule files, documentation standards
**AutoAttach:** true
**Type:** Auto-attach
**Version:** 2.0
**LastUpdated:** 2025-09-24

# Rule Governance: Universal Standards for AI Coding Rules

## Purpose
Establish comprehensive governance for creating, maintaining, and organizing AI coding rule files to ensure consistency, discoverability, and effectiveness across different editors and AI models.

## Rule Type and Scope

- **Type:** Auto-attach
- **Scope:** Universal rule file creation, maintenance, and governance standards for all AI models and editors

## Contract
- **Inputs/Prereqs:** Rule creation requirements; project context; technology scope
- **Allowed Tools:** Documentation tools; rule templates; validation tools
- **Forbidden Tools:** Rule duplication tools; context-specific rule generators without universal principles
- **Required Steps:**
  1. Define rule purpose and scope clearly
  2. Include required sections (Purpose, Contract, Validation, etc.)
  3. Specify type (Auto-attach vs Agent Requested)
  4. Include compliance checklist and response template
  5. Add external documentation references
- **Output Format:** Markdown files following required section structure
- **Validation Steps:** Section completeness check; cross-reference validation; size budget compliance

## Key Principles

- **Universal Applicability:** Rules work across different AI models and editors
- **Single Responsibility:** Each rule focuses on one specific domain or technology
- **Explicit Contracts:** Clear inputs, outputs, and validation criteria
- **Composable Design:** Rules reference and build upon each other logically
- **Professional Standards:** Consistent tone, structure, and formatting

## 1. Rule Creation & Naming Constraints
- **Requirement:** Place universal rule files in the canonical `ai_coding_rules/` directory. Optional mirrors may exist in editor-specific folders (e.g., `.cursor/rules/`).
- **Requirement:** Use a snake-case naming convention with a `.md` extension (e.g., `your_rule_name.md`).
- **Requirement:** Include a clear description and, if needed, scope notes at the top of the file. Mandatory metadata `Version` and `LastUpdated` must be included in plain text. Optional metadata like `id` may also be included.

## 2. Required Rule Structure

### Mandatory Sections (In Order)
Every rule file must follow this structure:

```markdown
# Rule Title

## Purpose
[1-2 sentences clearly explaining what this rule accomplishes and why it exists]

## Rule Type and Scope
- **Type:** [Auto-attach | Agent Requested]
- **Scope:** [Description of what the rule covers and applies to]

## Contract
- **Inputs/Prereqs:** [Required context, files, env vars]
- **Allowed Tools:** [List tools permitted for this rule]
- **Forbidden Tools:** [List tools not allowed]
- **Required Steps:** [Ordered, explicit steps the AI must follow]
- **Output Format:** [Exact expected output format]
- **Validation Steps:** [Checks the AI must run to confirm success]

## Key Principles (when applicable)
- [Concise bullet points summarizing core concepts]

## 1. Detailed Section
[Comprehensive implementation details]

## Quick Compliance Checklist
- [ ] [5-10 verification items AI can check before acting]

## Validation
- **Success Checks:** [How to verify rule compliance]
- **Negative Tests:** [What should fail and how to detect it]

## Response Template
```<LANG>
<Minimal, copy-pasteable template showing expected output format>
```

## References

### External Documentation
- [Official Documentation](https://example.com/) - Description

### Related Rules
- **Rule Name**: `filename.md`
```

### Section Requirements

**When to include Key Principles:**
- **Required:** Foundational rules (core, language-specific, major frameworks)
- **Consider:** Complex topics with multiple interconnected concepts
- **Optional:** Simple, focused rules with straightforward implementation

**Rule Type and Scope Section Requirements:**
- **Mandatory:** Every rule must include a `## Rule Type and Scope` section immediately after the Purpose section
- **Type:** Must specify either "Auto-attach" (for foundational rules) or "Agent Requested" (for specialized rules)
- **Scope:** Must clearly describe what the rule covers, applies to, and its intended use cases

**References Section Requirements:**
- **Mandatory:** Every rule must include a `## References` section
- **Mandatory:** Include `### External Documentation` with links to official documentation, guides, and authoritative resources
- **Mandatory:** Include `### Related Rules` when logical relationships exist to other rules in the system
- **Format:** Use `- **Rule Name**: \`filename.md\`` format for Related Rules entries
- **Quality:** External documentation links must be current, authoritative, and directly relevant to the rule's purpose

## 3. Rule Types and Scoping

### Auto-attach Rules
- **Criteria:** Universal principles that apply to all interactions
- **Examples:** Core workflow, safety protocols, professional communication
- **Limit:** Keep to essential foundational rules only
- **Scope Control:** Avoid auto-attaching specialized technology rules
- **Requirement:** Only the global core rule should auto-attach universally
- **Requirement:** Limit scope tightly to avoid auto-attaching rules unnecessarily

### Agent Requested Rules
- **Criteria:** Specialized knowledge for specific technologies or domains
- **Examples:** Language-specific practices, framework patterns, tool usage
- **Benefits:** Reduces context overhead; allows targeted expertise
- **Organization:** Group related rules in numbered ranges (e.g., 200-299 for Python)
- **Consider:** Prefer an on-demand (Agent Requested) pattern for specialized topics to control context cost across IDEs and CLI tools

## 4. Content Standards

### Rule Sizing Guidelines
- **Target Length:** 150-300 lines per rule
- **Maximum Length:** 500 lines (split larger topics into multiple rules)
- **Focus Principle:** One rule per major concept or technology area
- **Composition:** Reference other rules rather than duplicating content
- **Requirement:** Keep each rule file concise and focused (target 150–300 lines; max 500 lines)
- **Consider:** Split large topics into multiple composable rules
- **Requirement:** Avoid duplication across rules; reference other rules or `@path/to/file` instead

### Professional Communication Requirements
- **Tone:** Technical, direct, professional
- **Language:** Use directive language (Requirement, Always, Rule, Avoid)
- **Visual Elements:** No emojis, GIFs, or decorative elements unless explicitly requested
- **Examples:** Include practical, runnable examples with proper syntax highlighting
- **Requirement:** Follow professional communication standards from `000-global-core.md`: no emojis or GIF images in rule files unless explicitly requested by the user

### Cross-Reference Standards
- **Format:** Use `@filename.md` or `**Rule Name**: \`filename.md\`` format
- **Validation:** Verify all cross-references point to existing files
- **Relationships:** Document logical dependencies between rules
- **Maintenance:** Update references when files are renamed or reorganized

## 5. Numbering and Organization

### Numbering Scheme
- **000-099:** Core Foundation (global, memory-bank, governance)
- **100-199:** Data Platform (Snowflake, databases)
- **200-299:** Software Engineering - Python
- **300-399:** Software Engineering - Shell Scripts
- **400-499:** [Reserved for future expansion]
- **500-599:** Data Science & Analytics
- **600-699:** Data Governance
- **700-799:** Business Intelligence
- **800-899:** Project Management
- **900-999:** Demo & Synthetic Data

### Subdomain Organization
- **10-number ranges:** Framework-specific rules (e.g., 210-219 for FastAPI)
- **Sequential numbering:** Use next available number within appropriate range
- **Reserved ranges:** Leave space for future related rules

## 6. Quality Assurance

### Content Validation Requirements
- **Accuracy:** All code examples must be syntactically correct and tested
- **Currency:** External documentation links must be current and authoritative
- **Completeness:** Required sections must be present and properly formatted
- **Uniqueness:** Avoid duplicating information across rules

### Review Process
- **Section Check:** Verify all mandatory sections are present
- **Cross-Reference Validation:** Confirm all rule references are accurate
- **External Link Verification:** Test that documentation links work
- **Example Testing:** Validate all code examples and commands

### Maintenance Responsibilities
- **Version Tracking:** Update version number and LastUpdated date for changes
- **Dependency Updates:** Update cross-references when related rules change
- **Content Pruning:** Remove outdated information and broken links
- **Scope Verification:** Ensure rules remain focused and don't overlap

## 7. Documentation & Validation
- **Always:** Include links to relevant, current product documentation for reference
- **Requirement:** Before finalizing any rule or code, verify syntax, best practices, and API usage against the linked docs

## 8. Change Workflow
- **Always:** When creating a new rule, include a clear `## Purpose` section and, when appropriate, a `## Key Principles` section with 3-7 concise bullet points summarizing core concepts
- **Mandatory:** When creating a new rule, include a `## Rule Type and Scope` section immediately after the Purpose section specifying the rule's type and scope
- **Mandatory:** When creating a new rule, include a complete `## References` section with both `### External Documentation` and `### Related Rules` subsections
- **Mandatory:** When creating a new rule, include `Version: 1.0` and `LastUpdated` with current date in YYYY-MM-DD format
- **Mandatory:** When updating any rule file, increment the version number and update `LastUpdated` to the current date in YYYY-MM-DD format
- **Always:** When refactoring, split oversized rules and remove content duplication
- **Always:** When creating or updating rules, verify compliance with professional communication standards (no emojis, GIFs, or visual elements unless requested)
- **Always:** Validate Related Rules cross-references for accuracy and ensure they represent logical relationships
- **Always:** Before finalizing a rule, validate it against current, vendor-agnostic documentation and your primary IDE/tooling documentation for compliance (e.g., Visual Studio Code, Cursor, Claude Code, Gemini CLI, Cline)
- **Always:** For all agent interactions, follow the core rules in `000-global-core.md`

## Quick Compliance Checklist
- [ ] Rule follows mandatory section structure
- [ ] Purpose clearly states what rule accomplishes and why
- [ ] Contract specifies inputs, tools, steps, output format, and validation
- [ ] Compliance checklist has 5-10 actionable items
- [ ] Response template shows expected output format
- [ ] External documentation links are current and authoritative
- [ ] Related rules cross-references are accurate
- [ ] Rule length is within guidelines (≤500 lines)
- [ ] Professional communication standards followed
- [ ] Version and LastUpdated metadata included

## Validation
- **Success Checks:** All required sections present; cross-references work; external links accessible; examples are syntactically correct
- **Negative Tests:** Rules missing required sections fail validation; broken cross-references cause confusion; outdated external links impede learning

## Response Template
```markdown
## Rule Analysis
- **Purpose:** [What the rule accomplishes]
- **Type:** [Auto-attach | Agent Requested]
- **Scope:** [Technology/domain coverage]
- **Dependencies:** [Required prerequisite rules]

## Implementation
[Rule content following required structure]

## Validation
- [ ] [Compliance checklist items]
```

## References

### External Documentation
- [Cursor Documentation](https://docs.cursor.com/) - AI-powered code editor features and capabilities
- [Cursor Rules Guide](https://docs.cursor.com/en/context/rules) - Project rules and context management
- [Visual Studio Code Custom Instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions) - Configure custom instructions for GitHub Copilot in VS Code
- [GitHub Copilot Best Practices](https://docs.github.com/en/copilot/get-started/best-practices) - GitHub Copilot usage guidance and optimization tips
- [GitHub Copilot Personal Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-personal-instructions) - Configure personal custom instructions for GitHub Copilot
- [GitHub Copilot Repository Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions) - Add custom instructions at the repository level
- [Technical Writing Guide](https://developers.google.com/tech-writing) - Google's comprehensive guide for clear technical documentation
- [Markdown Specification](https://spec.commonmark.org/) - Official CommonMark specification for consistent formatting
- [Documentation Best Practices](https://www.writethedocs.org/guide/) - Community guide for effective technical documentation
- [Professional Technical Writing](https://developers.google.com/tech-writing) - Google's technical writing standards and best practices
- [Markdown Guide](https://www.markdownguide.org/) - Complete Markdown syntax and formatting reference

### Related Rules
- **Global Core**: `000-global-core.md`
- **Memory Bank Universal**: `001-memory-bank.md`