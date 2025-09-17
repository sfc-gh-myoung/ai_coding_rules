**Description:** How to create new `.md` project rule files for AI coding assistants (editor- and model-agnostic).
**AutoAttach:** true
**Type:** Auto-attach
**Version:** 1.0
**LastUpdated:** 2025-09-10

# Rule Governance: Directives for the Agent

## Purpose
Establish comprehensive governance for creating, maintaining, and organizing AI coding rule files to ensure consistency, discoverability, and effectiveness across different editors and AI models.

## Rule Creation & Naming Constraints
- **Requirement:** Place universal rule files in the canonical `ai_coding_rules/` directory. Optional mirrors may exist in editor-specific folders (e.g., `.cursor/rules/`).
- **Requirement:** Use a snake-case naming convention with a `.md` extension (e.g., `your_rule_name.md`).
- **Requirement:** Include a clear description and, if needed, scope notes at the top of the file. Optional metadata like `id`, `Version`, and `LastUpdated` may also be included in plain text.

## Content & Structure Constraints
- **Requirement:** Every rule file must have a single `#` H1 title.
- **Requirement:** Every rule file must include a `## Purpose` section immediately after the H1 title that clearly explains what the rule accomplishes and why it exists.
- **Requirement:** Rule files should include a `## Key Principles` section after the Purpose section when the rule contains core concepts that benefit from quick reference (recommended for foundational rules, technology-specific rules, and complex topics).
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

## Key Principles (when applicable)
- [Concise bullet point summarizing key concept]
- [Another essential principle or practice]
- [Additional core concepts as needed]

## 1. Detailed Section
[Comprehensive implementation details]
```

**When to include Key Principles:**
- **Required:** Foundational rules (core, language-specific, major frameworks)
- **Consider:** Complex topics with multiple interconnected concepts
- **Optional:** Simple, focused rules with straightforward implementation

## Documentation & Validation
- **Always:** Include links to relevant, current product documentation for reference.
- **Requirement:** Before finalizing any rule or code, verify syntax, best practices, and API usage against the linked docs.

## Change Workflow
- **Always:** When creating a new rule, include a clear `## Purpose` section and, when appropriate, a `## Key Principles` section with 3-7 concise bullet points summarizing core concepts.
- **Always:** When refactoring, split oversized rules and remove content duplication.
- **Always:** Before finalizing a rule, validate it against current, vendor-agnostic documentation and your primary IDE/tooling documentation for compliance (e.g., Visual Studio Code, Cursor, Claude Code, Gemini CLI, Cline).
