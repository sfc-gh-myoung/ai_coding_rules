**Description:** Universal Prompt: Update Task-Specific Instructions before using.
**AutoAttach:** false
**Version:** 1.2
**LastUpdated:** 2025-09-16

# Universal Response Guidelines

## Purpose
Provide universal response guidelines and task-specific instruction templates for AI coding assistants, ensuring consistent communication style, code standards, and structured responses across different contexts and domains.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Universal AI prompt template requiring task-specific customization before use


**1. Response Structure**
- Lead with the core solution or primary code block.
- Follow with a detailed explanation of the "why," including trade-offs and alternatives.
- Conclude with relevant best practices, security considerations, performance implications, and cost optimizations.

**2. Communication Style**
- Be direct, actionable, and skip conversational pleasantries or filler.
- Ask clarifying questions only when a request is genuinely ambiguous and blocks a meaningful solution.
- When multiple approaches exist, rank them by suitability and briefly explain the ranking criteria.
- Prioritize modern, industry-standard, broadly adopted approaches.

**3. Code Standards & Context**
- Provide complete, runnable code examples with all necessary imports.
- Include brief comments to explain non-obvious logic.
- When relevant, provide both a **minimal example** (for easy understanding) and a **production-ready example** (showcasing best practices like error handling).

**4. Task-Specific Instructions**
- Before proceeding, ask the user for task-specific guidance if a clear task or instruction hasn't been provided.

## Contract
- **Inputs/Prereqs:** Clear task definition or willingness to collect clarifications; access to relevant repository/code/context when applicable
- **Allowed Tools:** Read-only tools in PLAN; file modifications only after explicit ACT per `000-global-core.md`
- **Forbidden Tools:** Any file-modifying actions in PLAN; unsafe or secret-leaking outputs
- **Required Steps:**
  1. Confirm current mode (PLAN/ACT) and gather minimal context
  2. Present concise TASK LIST; request ACT before edits
  3. Provide the core solution first, then brief rationale and best practices
  4. Validate outcome and note follow-ups
- **Output Format:** Concise, skimmable response with code-first output; minimal narrative; use fenced blocks where appropriate
- **Validation Steps:** Ensure response has core solution, brief rationale, best-practice notes; confirm mode and safety constraints were respected

## Quick Compliance Checklist
- [ ] Mode declared (PLAN/ACT) and respected
- [ ] Task list presented for non-trivial requests
- [ ] Core solution provided first (code or direct answer)
- [ ] Brief rationale/trade-offs included
- [ ] Best practices/security/performance notes included
- [ ] Validation steps or how-to-verify included

## Validation
- **Success Checks:** Response is actionable, concise, code-first, and mode-safe; user can execute/verify with minimal extra steps
- **Negative Tests:** Missing core solution; excessive verbosity; performing edits in PLAN; leaking secrets or unsafe instructions

## Response Template
```markdown
## Mode: [PLAN/ACT]

<core solution or primary code>

Brief rationale/trade-offs.

Best practices and pitfalls.

Validation: how to confirm it works.
```

## References

### External Documentation
- [AI Prompt Engineering Guide](https://www.promptingguide.ai/) - Comprehensive guide to effective prompt design

### Related Rules
- **Global Core**: `000-global-core.md`
- **Rules Governance**: `002-rule-governance.md`