**Description:** How to create new `.md` project rule files for AI coding assistants (editor- and model-agnostic).
**AutoAttach:** true
**Type:** Auto-attach
**Version:** 1.4
**LastUpdated:** 2025-09-17

# Rule Governance: Directives for the Agent

## Purpose
Establish comprehensive governance for creating, maintaining, and organizing AI coding rule files to ensure consistency, discoverability, and effectiveness across different editors and AI models.

## Rule Type and Scope

- **Type:** Auto-attach
- **Scope:** AI coding rule file creation, maintenance, and governance standards for all editors and AI models

## Rule Creation & Naming Constraints
- **Requirement:** Place universal rule files in the canonical `ai_coding_rules/` directory. Optional mirrors may exist in editor-specific folders (e.g., `.cursor/rules/`).
- **Requirement:** Use a snake-case naming convention with a `.md` extension (e.g., `your_rule_name.md`).
- **Requirement:** Include a clear description and, if needed, scope notes at the top of the file. Mandatory metadata `Version` and `LastUpdated` must be included in plain text. Optional metadata like `id` may also be included.

## Content & Structure Constraints
- **Requirement:** Every rule file must have a single `#` H1 title.
- **Requirement:** Every rule file must include a `## Purpose` section immediately after the H1 title that clearly explains what the rule accomplishes and why it exists.
- **Requirement:** Every rule file must include a `## Rule Type and Scope` section immediately after the Purpose section that specifies the rule's type and scope.
- **Requirement:** Rule files should include a `## Key Principles` section after the Rule Type and Scope section when the rule contains core concepts that benefit from quick reference (recommended for foundational rules, technology-specific rules, and complex topics).
- **Requirement:** Every rule file must include a `## References` section with required subsections (see Required Section Structure below).
- **Requirement:** Keep each rule file concise and focused (target 150–300 lines; max 500 lines).
- **Consider:** Split large topics into multiple composable rules.
- **Requirement:** Avoid duplication across rules; reference other rules or `@path/to/file` instead.
- **Always:** For all agent interactions, follow the core rules in `000-global-core.md`.

## Rule Scoping and Type
- **Requirement:** Only the global core rule should auto-attach universally.
- **Requirement:** Limit scope tightly to avoid auto-attaching rules unnecessarily.
- **Consider:** Prefer an on-demand (Agent Requested) pattern for specialized topics to control context cost across IDEs and CLI tools.

## Required Section Structure
Every rule file must follow this structure:

```markdown
# Rule Title

## Purpose
[1-2 sentences clearly explaining what this rule accomplishes and why it exists]

## Rule Type and Scope

- **Type:** [Auto-attach | Agent Requested]
- **Scope:** [Description of what the rule covers and applies to]

## Key Principles (when applicable)
- [Concise bullet point summarizing key concept]
- [Another essential principle or practice]
- [Additional core concepts as needed]

## 1. Detailed Section
[Comprehensive implementation details]

## References

### External Documentation
- [Official Documentation](https://example.com/) - Description of the resource
- [Additional Resource](https://example.com/) - Another relevant external link

### Related Rules
- **Core Rule Name**: `filename.md`
- **Related Rule**: `another-filename.md`
```

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

## Documentation & Validation
- **Always:** Include links to relevant, current product documentation for reference.
- **Requirement:** Before finalizing any rule or code, verify syntax, best practices, and API usage against the linked docs.

## Change Workflow
- **Always:** When creating a new rule, include a clear `## Purpose` section and, when appropriate, a `## Key Principles` section with 3-7 concise bullet points summarizing core concepts.
- **Mandatory:** When creating a new rule, include a `## Rule Type and Scope` section immediately after the Purpose section specifying the rule's type and scope.
- **Mandatory:** When creating a new rule, include a complete `## References` section with both `### External Documentation` and `### Related Rules` subsections.
- **Mandatory:** When creating a new rule, include `Version: 1.0` and `LastUpdated` with current date in YYYY-MM-DD format.
- **Mandatory:** When updating any rule file, increment the version number and update `LastUpdated` to the current date in YYYY-MM-DD format.
- **Always:** When refactoring, split oversized rules and remove content duplication.
- **Always:** Validate Related Rules cross-references for accuracy and ensure they represent logical relationships.
- **Always:** Before finalizing a rule, validate it against current, vendor-agnostic documentation and your primary IDE/tooling documentation for compliance (e.g., Visual Studio Code, Cursor, Claude Code, Gemini CLI, Cline).

## References

### External Documentation
- [Cursor Documentation](https://docs.cursor.com/) - AI-powered code editor features and capabilities
- [Cursor Rules Guide](https://docs.cursor.com/en/context/rules) - Project rules and context management
- [Professional Technical Writing](https://developers.google.com/tech-writing) - Google's technical writing standards and best practices
- [Markdown Guide](https://www.markdownguide.org/) - Complete Markdown syntax and formatting reference

### Related Rules
- **Global Core**: `000-global-core.md`
- **Memory Bank System**: `001-cursor-memory-bank.md`
