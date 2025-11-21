<!-- 
BOILERPLATE TEMPLATE: AI Coding Rule Structure
===============================================
This file serves as the canonical reference for rule format, structure, content, and flow.

PURPOSE: All new rules and significant rule updates MUST use this template as the structural foundation.

USAGE:
1. Copy this file to new filename following numbering scheme (e.g., 210-python-fastapi-core.md)
2. Replace ALL placeholder content [in brackets] with domain-specific content
3. Remove or adjust optional sections based on rule complexity
4. Validate using: python scripts/validate_agent_rules.py --directory templates
5. Ensure 100% compliance before submitting

COMPLIANCE: This template conforms to 002-rule-governance.md v5.0 standards.
-->

<!-- ========================================================================
METADATA SECTION (Lines 1-30)
================================================================================
CRITICAL: Metadata fields MUST appear in this exact order per Section 11.1:
1. Description, 2. Type, 3. AppliesTo, 4. AutoAttach, 5. Keywords
6. TokenBudget, 7. ContextTier, 8. Version, 9. LastUpdated, 10. Depends

FORMAT REQUIREMENTS:
- Use **Field:** format for all metadata
- TokenBudget: Use ~NUMBER format (e.g., ~450, ~1200, ~2500) - NO text labels
- ContextTier: Use Critical | High | Medium | Low
- Keywords: Include 15-20 semantic terms for discovery
- Depends: List prerequisite rules in dependency order
======================================================================== -->

**Keywords:** [technology name], [primary feature], [secondary feature], [common use case 1], [common use case 2], [pattern 1], [pattern 2], [problem solved], [framework name], [tool name], [action verb 1], [action verb 2], [related concept 1], [related concept 2], [semantic term]
**TokenBudget:** ~3650
**TokenBudget:** ~[estimated tokens - calculate as: word_count * 1.3]
**ContextTier:** [Critical | High | Medium | Low]
**Depends:** 000-global-core[, other-prerequisite-rules]

<!-- ========================================================================
TITLE AND PURPOSE (Lines 31-50)
================================================================================
REQUIREMENTS:
- H1 title follows naming conventions: [Number]-[technology]-[aspect].md
- Purpose: 1-2 sentences clearly explaining value proposition
- Be concise and specific about what problem this rule solves
======================================================================== -->

# [Rule Title: Technology/Framework Name - Specific Aspect]

## Purpose
[1-2 sentences clearly explaining what this rule accomplishes and why it exists. Focus on the value proposition and problem being solved.]

<!-- ========================================================================
RULE TYPE AND SCOPE (Lines 51-60)
================================================================================
REQUIREMENT: MANDATORY section per 002-rule-governance.md Section 3
PLACEMENT: Immediately after Purpose section

GUIDANCE:
- Type: "Auto-attach" for foundational rules, "Agent Requested" for specialized
- Scope: Describe domain coverage, applicable technologies, and use cases
======================================================================== -->

## Rule Type and Scope

- **Type:** [Auto-attach | Agent Requested]
- **Scope:** [Detailed description of what this rule covers, applies to, and its intended use cases. Include technology versions, applicable patterns, and domain boundaries.]

<!-- ========================================================================
CONTRACT SECTION (Lines 61-95)
================================================================================
CRITICAL: MUST appear before line 100 per Section 11.3

PURPOSE: Establishes clear operational contract between AI agent and rule
SECTIONS: Inputs/Prereqs, Allowed Tools, Forbidden Tools, Required Steps, 
          Output Format, Validation Steps

GUIDANCE:
- Be explicit and exhaustive with Required Steps (Claude 4 needs clear instructions)
- List tools by category, not individual commands
- Validation steps should be specific and measurable
======================================================================== -->

## Contract

- **Inputs/Prereqs:** [Required context, files, environment variables, installed dependencies, prerequisite knowledge]
- **Allowed Tools:** [List tools permitted for this domain - e.g., uv run, uvx ruff, file read tools, specific frameworks]
- **Forbidden Tools:** [List tools NOT allowed - e.g., bare python, direct file system modifications without validation, deprecated patterns]
- **Required Steps:**
  1. [First mandatory step - be explicit and specific]
  2. [Second mandatory step - include verification criteria]
  3. [Third mandatory step - specify expected outcomes]
  4. [Fourth step - include error handling approach]
  5. [Fifth step - specify validation requirements]
  [Add more steps as needed - aim for 5-10 explicit, ordered steps]
- **Output Format:** [Exact expected output format - code snippets, diffs, commands, documentation, etc.]
- **Validation Steps:** [Specific checks the AI must run to confirm success - commands, expected outputs, error conditions to verify]

<!-- ========================================================================
KEY PRINCIPLES (Lines 96-115)
================================================================================
OPTIONAL: Include for foundational rules or complex topics
OMIT: For simple, straightforward rules with clear implementation

PURPOSE: Provide high-level conceptual framework before detailed implementation
FORMAT: Concise bullet points summarizing core concepts

GUIDANCE:
- Keep to 4-6 principles maximum
- Each principle should be one line
- Focus on conceptual understanding, not implementation details
======================================================================== -->

## Key Principles

- **[Principle 1 Name]:** [Brief explanation of foundational concept]
- **[Principle 2 Name]:** [Brief explanation of operational approach]
- **[Principle 3 Name]:** [Brief explanation of quality standard]
- **[Principle 4 Name]:** [Brief explanation of integration pattern]
- **[Principle 5 Name]:** [Brief explanation of maintainability guideline]

<!-- ========================================================================
QUICK START TL;DR (Lines 116-160)
================================================================================
MANDATORY: Required per Section 11.2

PURPOSE: 30-second reference of critical patterns for 80% of use cases
BENEFITS: Token efficiency, attention optimization, progressive disclosure

FORMAT:
- **MANDATORY:** header for critical requirements
- **Essential Patterns:** 6-7 key patterns in priority order
- **Quick Checklist:** 5-7 verification items

GUIDANCE:
- Use **bold** for emphasis on critical terms
- Keep each pattern to one line with brief explanation
- Checklist items should be binary (yes/no) verifications
======================================================================== -->

## Quick Start TL;DR (Read First - 30 Seconds)

**MANDATORY:**
**Essential Patterns:**
- **[Pattern 1 - Most Critical]** - [Brief explanation of why this matters and what to do]
- **[Pattern 2 - Second Priority]** - [Concise guidance on correct implementation]
- **[Pattern 3 - Core Workflow]** - [Essential workflow step or requirement]
- **[Pattern 4 - Common Gotcha]** - [Warning about common mistake to avoid]
- **[Pattern 5 - Validation Gate]** - [Required validation or testing step]
- **[Pattern 6 - Tool Usage]** - [Correct tool invocation or command pattern]
- **[Pattern 7 - Success Criteria]** - [How to verify correct implementation]

**Quick Checklist:**
- [ ] [Verification item 1 - can be checked quickly]
- [ ] [Verification item 2 - binary yes/no check]
- [ ] [Verification item 3 - validation command succeeds]
- [ ] [Verification item 4 - required section present]
- [ ] [Verification item 5 - tests pass or lint succeeds]
- [ ] [Verification item 6 - documentation updated]
- [ ] [Verification item 7 - final success criterion met]

<!-- ========================================================================
DETAILED IMPLEMENTATION SECTIONS (Lines 161-400+)
================================================================================
PURPOSE: Comprehensive guidance organized by topic

STRUCTURE: Numbered sections for clarity (## 1., ## 2., ## 3., etc.)
DIRECTIVE LANGUAGE: Use Requirement, Always, Rule, Consider, Avoid, Never

HIERARCHY:
- **Requirement:** Mandatory behavior, non-negotiable
- **Always:** Best practice to follow consistently in all cases
- **Rule:** Standard operating procedure for this domain
- **Consider:** Context-dependent recommendation, use judgment
- **Avoid:** Anti-pattern to prevent, strong discouragement
- **Never:** Absolute prohibition, forbidden action

SUBSECTIONS: Use ### for subtopics within numbered sections

CODE EXAMPLES: Include working, tested examples with language tags
======================================================================== -->

## 1. [First Major Topic: Foundation Concepts]

### [Subtopic 1.1: Basic Setup]
- **Requirement:** [Mandatory configuration or setup step]
- **Always:** [Best practice that should always be followed]
- **Rule:** [Standard procedure for this specific scenario]
- **Consider:** [Context-dependent recommendation with conditions]
- **Avoid:** [Anti-pattern to watch out for]

```[language]
# Good example showing correct pattern
[working code example demonstrating best practice]
[include relevant imports and context]
```

```[language]
# Bad example (avoid this pattern)
[code showing what NOT to do]
[explain why this is problematic]
```

### [Subtopic 1.2: Configuration]
- **Requirement:** [Required configuration setting]
- **Always:** [Configuration best practice]
- **Rule:** [Standard configuration approach]

```[language]
# Configuration example
[complete, working configuration example]
```

## 2. [Second Major Topic: Core Implementation]

### [Subtopic 2.1: Implementation Patterns]
- **Requirement:** [Mandatory implementation approach]
- **Always:** [Consistent implementation pattern]
- **Rule:** [Standard implementation procedure]
- **Consider:** [Alternative approach with tradeoffs]

```[language]
# Implementation example
[complete, tested implementation showing correct pattern]
[include error handling and edge cases]
```

### [Subtopic 2.2: Common Operations]
- **Requirement:** [Required operational behavior]
- **Always:** [Operational best practice]
- **Rule:** [Standard operating procedure]

## 3. [Third Major Topic: Advanced Patterns]

### [Subtopic 3.1: Optimization]
- **Requirement:** [Performance requirements]
- **Consider:** [Performance optimization strategies]
- **Avoid:** [Performance anti-patterns]

### [Subtopic 3.2: Error Handling]
- **Requirement:** [Error handling requirements]
- **Always:** [Error handling best practices]
- **Rule:** [Standard error handling approach]

```[language]
# Error handling example
[code showing proper error handling pattern]
[include logging, recovery, and user feedback]
```

## 4. [Fourth Major Topic: Integration & Testing]

### [Subtopic 4.1: Integration Patterns]
- **Requirement:** [Integration requirements]
- **Always:** [Integration best practices]

### [Subtopic 4.2: Testing Requirements]
- **Requirement:** [Testing requirements]
- **Always:** [Testing best practices]
- **Rule:** [Standard testing procedure]

```[language]
# Test example
[complete test showing correct testing pattern]
[include setup, execution, and assertions]
```

<!-- ========================================================================
ANTI-PATTERNS SECTION (Lines 401-500)
================================================================================
CRITICAL: Required for rules with complex behavior per Section 5a
IMPORTANCE: Claude 4 pays extreme attention to examples

PURPOSE: Show both incorrect and correct approaches side-by-side
FORMAT: Anti-Pattern → Problem → Correct Pattern → Benefits

REQUIREMENT: Include 2-5 anti-pattern/correct-pattern pairs
REQUIREMENT: Use fenced code blocks with language tags
REQUIREMENT: Explain WHY each anti-pattern is problematic
REQUIREMENT: Explain WHY the correct pattern is better

GUIDANCE:
- Use complete, runnable examples (not fragments)
- Focus on common mistakes developers actually make
- Explain the consequences of the anti-pattern
- Show measurable benefits of the correct pattern
======================================================================== -->

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: [Descriptive Name of Common Mistake]**
```[language]
# Bad example showing what NOT to do
[complete, runnable code showing anti-pattern]
[include context and imports]
```
**Problem:** [Specific issues this causes - performance, maintainability, correctness, security]

**Correct Pattern:**
```[language]
# Good example showing right approach
[complete, runnable code showing correct pattern]
[include context and imports]
```
**Benefits:** [Why this approach is better - specific measurable improvements]

---

**Anti-Pattern 2: [Another Common Mistake]**
```[language]
# Bad: [Description of what's wrong]
[anti-pattern code example]
```
**Problem:** [Consequences and why it's problematic]

**Correct Pattern:**
```[language]
# Good: [Description of correct approach]
[correct code example]
```
**Benefits:** [Advantages and improvements]

---

**Anti-Pattern 3: [Vague or Incomplete Instructions]**
```markdown
"Create a [feature] that works well"
```
**Problem:** Claude 4 won't automatically add extra features unless explicitly requested. Vague instructions lead to minimal implementations.

**Correct Pattern (Explicit Instructions):**
```markdown
"Create a [feature] with the following requirements:
1. [Specific requirement 1]
2. [Specific requirement 2]
3. [Specific requirement 3]
Include error handling, logging, and comprehensive tests.
Go beyond basics to create a production-ready implementation."
```
**Benefits:** Explicit behavior specifications ensure correct scope and quality expectations.

<!-- ========================================================================
INVESTIGATION-FIRST PROTOCOL (Lines 501-540)
================================================================================
MANDATORY: For rules that reference code/files per Section 11.5
OPTIONAL: For rules dealing with abstract concepts only

PURPOSE: Prevent hallucinations by requiring verification before response
ORIGIN: Claude 4 best practices - "Never speculate about code you haven't opened"

FORMAT: Blockquote with investigation requirements and examples

REQUIREMENT: Include if rule involves:
- Reading files, code analysis, codebase exploration
- File system operations, directory structures
- Configuration files, environment setup
- Any scenario where assumptions could lead to errors

SKIP IF: Rule is purely conceptual without file/code references
======================================================================== -->

> **Investigation Required**
> When applying this rule:
> 1. **Read referenced files BEFORE making recommendations** - Never guess file contents
> 2. **Verify assumptions against actual code/data** - Check structure, patterns, dependencies
> 3. **Never speculate about file contents or system state** - If unsure, read the file
> 4. **If uncertain, explicitly state:** "I need to read [file] to provide accurate guidance"
> 5. **Make grounded, hallucination-free recommendations based on investigation** - Use facts, not assumptions
>
> **Anti-Pattern:**
> "Based on typical [technology] patterns, this file probably contains [speculation]..."
> "Usually this would be implemented as [assumption without verification]..."
>
> **Correct Pattern:**
> "Let me read the file first to give you accurate guidance."
> [reads file using appropriate tool]
> "After reviewing [file], I found [specific facts observed]. Here's my recommendation based on what I observed: [grounded advice]"

<!-- ========================================================================
QUICK COMPLIANCE CHECKLIST (Lines 541-560)
================================================================================
MANDATORY: Required per 002-rule-governance.md Section 3

PURPOSE: Practical verification items AI can check before responding
FORMAT: Checkbox list with 5-10 items

GUIDANCE:
- Items should be specific and verifiable
- Focus on practical checks, not vague goals
- Include validation commands where applicable
- Order by importance (critical items first)
======================================================================== -->

## Quick Compliance Checklist
- [ ] Required dependencies and prerequisites verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns from this rule
- [ ] Code examples tested and working
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully (commands run, tests pass)
- [ ] Error handling implemented per guidelines
- [ ] Documentation updated where required
- [ ] Integration points verified
- [ ] Final success criteria met per Contract section

<!-- ========================================================================
VALIDATION SECTION (Lines 561-585)
================================================================================
MANDATORY: Required per 002-rule-governance.md Section 3

PURPOSE: Explicit success criteria and failure modes
SECTIONS: Success checks (what should pass), Negative tests (what should fail)

GUIDANCE:
- Success checks: List specific, measurable verification steps
- Negative tests: Describe failure scenarios and how to detect them
- Include commands to run, expected outputs, error messages to check
- Be concrete and specific, avoid vague criteria
======================================================================== -->

## Validation
- **Success checks:** [Specific verification steps - commands that should succeed, outputs that should appear, files that should exist, tests that should pass, linting that should be clean, specific behaviors that should work correctly]
- **Negative tests:** [What should fail and how to detect it - invalid inputs should be rejected, malformed data should raise errors, edge cases should be handled gracefully, deprecated patterns should trigger warnings]

<!-- ========================================================================
RESPONSE TEMPLATE (Lines 586-650)
================================================================================
MANDATORY: Required per 002-rule-governance.md Section 3

PURPOSE: Provide complete working examples showing correct response format
REQUIREMENT: Template must be comprehensive with working code examples

FORMAT:
- Include MODE declaration (PLAN/ACT)
- Show investigation phase
- Include implementation examples with proper language tags
- Show validation commands
- Demonstrate validation results format

GUIDANCE:
- Use real, working code examples (not placeholders)
- Include all necessary imports and context
- Show complete workflow from investigation to validation
- Demonstrate proper error handling
======================================================================== -->

## Response Template

```markdown
MODE: [PLAN|ACT]

Investigation:
[Description of investigation steps taken]
[Files read, patterns analyzed, dependencies verified]

Implementation:
[Clear explanation of changes being made]
```

```[language]
# Implementation example following rule patterns
[Complete, working code example]
[Include all imports and necessary context]
[Show proper error handling]
[Demonstrate correct usage of tools/frameworks]

# Example function
def example_function(param: str) -> dict:
    """
    Example showing correct implementation pattern.
    
    Args:
        param: Description of parameter
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When invalid input provided
    """
    # Implementation following rule guidelines
    if not param:
        raise ValueError("Parameter cannot be empty")
    
    result = {"status": "success", "data": param}
    return result
```

```bash
# Validation commands
[command to run validation]
[command to run tests]
[command to verify output]

# Example validation commands
uvx ruff check .
uvx ruff format --check .
uv run pytest tests/
```

**Validation Results:**

**Files Checked:**
- [list of files validated]
- [list of tests run]

**Issues Found:** [count or "None"]

**Actions Taken:**
1. [Description of fix or change]
2. [Description of validation performed]

**Validation Passed:** ✓ / ✗
- [x] Ruff linting clean
- [x] Ruff formatting clean
- [x] All tests passing
- [x] Integration verified
- [x] Documentation updated

<!-- ========================================================================
REFERENCES SECTION (Lines 651-680)
================================================================================
MANDATORY: Required per 002-rule-governance.md Section 3

SUBSECTIONS:
1. External Documentation (required)
2. Related Rules (required when logical relationships exist)

REQUIREMENTS:
- External docs must be current, authoritative, official sources
- Use format: - [Link Text](URL) - Description
- Related rules use format: - **Rule Name**: `filename.md`
- Links must be working and relevant

GUIDANCE:
- Prioritize official documentation over blog posts
- Include comprehensive guides and tutorials
- Reference related rules to build rule ecosystem
- Update links during maintenance reviews
======================================================================== -->

## References

### External Documentation
- [Official Documentation](https://example.com/docs) - [Brief description of what this link provides]
- [Best Practices Guide](https://example.com/best-practices) - [Description of content and relevance]
- [API Reference](https://example.com/api) - [Description of technical reference content]
- [Tutorial Series](https://example.com/tutorials) - [Description of learning resources]

### Related Rules
- **Global Core**: `000-global-core.md`
- **[Related Technology]**: `[number]-[technology]-[aspect].md`
- **[Prerequisite Rule]**: `[number]-[technology]-[aspect].md`
- **[Complementary Rule]**: `[number]-[technology]-[aspect].md`

<!-- ========================================================================
END OF BOILERPLATE TEMPLATE
================================================================================

FINAL CHECKLIST BEFORE SUBMISSION:
✓ All [placeholders] replaced with actual content
✓ Metadata in correct order (11 fields)
✓ Contract section before line 100
✓ Quick Start TL;DR section present
✓ Investigation-First Protocol included (if applicable)
✓ Anti-Patterns section with 2-5 pairs
✓ Response Template with working examples
✓ References section complete
✓ Validated with: python scripts/validate_agent_rules.py
✓ Zero critical errors, minimal warnings

NEXT STEPS:
1. Validate this rule: python scripts/validate_agent_rules.py --directory templates
2. Add entry to RULES_INDEX.md
3. Update CHANGELOG.md with conventional commit message
4. Test rule by loading it for relevant task

For questions or clarifications, refer to:
- 002-rule-governance.md (governance standards)
- 000-global-core.md (foundational principles)
- AGENTS.md (discovery and loading guidance)
======================================================================== -->
