**Description:** How to create new `.md` project rule files for AI coding assistants (editor- and model-agnostic).
**AutoAttach:** true
**Version:** 1.0
**LastUpdated:** 2025-09-10

# Rule Governance: Directives for the Agent

## Rule Creation & Naming Constraints
- **Requirement:** Place universal rule files in the canonical `ai_coding_rules/` directory. Optional mirrors may exist in editor-specific folders (e.g., `.cursor/rules/`).
- **Requirement:** Use a snake-case naming convention with a `.md` extension (e.g., `your_rule_name.md`).
- **Requirement:** Include a clear description and, if needed, scope notes at the top of the file. Optional metadata like `id`, `Version`, and `LastUpdated` may also be included in plain text.

## Content & Structure Constraints
- **Requirement:** Every rule file must have a single `#` H1 title.
- **Requirement:** Keep each rule file concise and focused (target 150–300 lines; max 500 lines).
- **Recommended:** Split large topics into multiple composable rules.
- **Requirement:** Avoid duplication across rules; reference other rules or `@path/to/file` instead.
- **Always:** For all agent interactions, follow the core rules in `00-global-core.md`.

## Rule Scoping and Type
- **Requirement:** Only the global core rule should auto-attach universally.
- **Requirement:** Limit scope tightly to avoid auto-attaching rules unnecessarily.
- **Recommended:** Prefer an on-demand (Agent Requested) pattern for specialized topics to control context cost across IDEs and CLI tools.

## Documentation & Validation
- **Always:** Include links to relevant, current product documentation for reference.
- **Requirement:** Before finalizing any rule or code, verify syntax, best practices, and API usage against the linked docs.

## Change Workflow
- **Always:** When creating a new rule, include a purpose, chosen rule type, and a brief 5–7 item checklist of key principles.
- **Always:** When refactoring, split oversized rules and remove content duplication.
- **Always:** Before finalizing a rule, validate it against current, vendor-agnostic documentation and your primary IDE/tooling documentation for compliance (e.g., Visual Studio Code, Cursor, Claude Code, Gemini CLI, Cline).
