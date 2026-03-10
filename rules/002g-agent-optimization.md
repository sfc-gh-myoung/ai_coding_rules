# 002g: Agent Optimization Principles

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-03-09
**Keywords:** agent, LLM, optimization, format, token, efficiency, understanding, execution, comprehension, design, patterns, priority, agent-first
**TokenBudget:** ~3000
**ContextTier:** High
**Depends:** 000-global-core.md, 002-rule-governance.md

## Scope

**What This Rule Covers:**
The PRIMARY design priority for all rules: **agent understanding and execution reliability**. All rules are instruction sets for autonomous agents, not reference documents for humans.

**Design Priorities (Strictly Enforced):**

See `002-rule-governance.md` "Key Principles" for canonical definitions.

1. **Priority 1 (CRITICAL):** Agent understanding and execution reliability - All wording must be unambiguous for autonomous non-human agents
2. **Priority 2 (HIGH):** Rule discovery efficacy and determinism
3. **Priority 3 (HIGH):** Context window and token utilization efficiency
4. **Priority 4 (LOW):** Human developer maintainability

**When to Load This Rule:**
- Creating or updating any rule in the `rules/` directory
- Reviewing rule formatting and structure decisions
- Understanding agent-first design principles
- Resolving conflicts between human-friendly vs agent-parseable formats

**Rule:** When human-friendly formatting conflicts with agent parsing, **agent parsing wins**.

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules
- **002-rule-governance.md** - Schema requirements and v3.2 standards

**Related:**
- **002a-rule-creation.md** - Step-by-step rule creation with agent optimization
- **002c-rule-optimization.md** - Token budgets and performance
- **002d-advanced-rule-patterns.md** - System prompt altitude and investigation-first

### External Documentation

- **Schema Definition:** `schemas/rule-schema.yml` - Authoritative v3.2 schema optimized for agent parsing

## Contract

### Inputs and Prerequisites

- Rule file being created or modified
- Understanding of target agent/LLM capabilities
- Knowledge of existing rule terminology conventions

### Mandatory

- Replace all ASCII tables with structured lists
- Replace arrow characters (`→`) with text alternatives
- Replace ASCII decision trees (`├─`, `└─`, `│`) with nested lists
- Use consistent terminology across all rules
- Write instructions in imperative voice (commands)
- Place critical information at start of sections
- Follow schema-required structures exactly

### Forbidden

- ASCII tables in rule content
- Arrow characters (`→`) outside code blocks
- ASCII decision tree characters (`├─`, `└─`, `│`) outside code blocks
- Mermaid diagrams or ASCII art (visual content for humans)
- Horizontal rule separators (`---`) as visual dividers

**Code Block Exception:** Code blocks documenting external systems (SQL output, API responses,
terminal output) may contain tables, arrows, and ASCII trees as part of the documented content.
The prohibition on these characters applies to rule prose only, not to code examples showing
external format output.

- Passive voice in instructions
- Inconsistent terminology across rules

### Execution Steps

1. Identify ASCII tables, arrows, and decision trees in content
2. Replace tables with structured lists
3. Replace arrows with text alternatives (then, to, Instead)
4. Replace decision trees with nested conditional lists
5. Review instructions for passive voice and rewrite
6. Verify terminology matches standard terms
7. Run `ai-rules validate` to confirm compliance

### Output Format

Rule files with optimized formatting for agent comprehension

### Validation

**Pre-Task-Completion Checks:**
- Rule file identified for optimization
- ASCII tables, arrows, decision trees detected
- Terminology conventions reviewed
- Schema requirements understood

**Success Criteria:**
- `ai-rules validate` passes
- No ASCII tables in content
- No arrow characters (`→`) in content
- No ASCII decision tree characters in content
- Terminology matches glossary
- Instructions use imperative voice
- Critical information front-loaded

**Negative Tests:**
- Rule with ASCII table should trigger refactoring
- Rule with arrow characters should use text alternatives
- Rule with ASCII decision trees should use nested lists
- Passive voice instructions should be rewritten
- Inconsistent terminology should be standardized

### Error Recovery

- If ASCII tables cannot be fully converted to lists, add a **TODO:** Convert table to structured list — and flag for manual review
- If terminology conflicts exist between rules, defer to the term defined in 002-rule-governance.md
- If validation fails after optimization, revert the failing change and re-run `ai-rules validate` before retrying

### Post-Execution Checklist

- [ ] All ASCII tables replaced with structured lists
- [ ] All arrow characters (`→`) replaced with text alternatives
- [ ] All ASCII decision trees replaced with nested lists
- [ ] All Mermaid diagrams and ASCII art removed (replaced with structured text)
- [ ] All horizontal rule separators (`---`) removed
- [ ] Instructions use imperative voice (commands)
- [ ] Critical information front-loaded in sections
- [ ] Terminology matches standard terms
- [ ] Schema-critical sections use required structure
- [ ] `ai-rules validate` passes
- [ ] Token budget within target range

## Priority Enforcement

### Priority 1 Violations (CRITICAL - Must Fix)

These patterns prevent reliable agent execution:

- **ASCII tables** - Agents parse cell-by-cell without grid context
- **Arrow characters (`→`)** outside code blocks - Ambiguous for sequential parsing
- **ASCII decision trees (`├─`, `└─`, `│`)** - Confuse sequential processing
- **Mermaid diagrams or ASCII art** - Visual content agents cannot interpret
- **Undefined subjective terms** - "large", "critical", "appropriate" without quantified thresholds
- **Conditionals without explicit branches** - Missing else/default cases
- **Passive voice instructions** - Ambiguous about who acts

### Priority 2 Violations (HIGH - Should Fix)

These patterns waste context budget:

- **Redundant content** that could be referenced from other rules
- **Verbose prose** where structured lists suffice
- **TokenBudget variance >5%** from actual count
- **Duplicate examples** across rules or within same rule
- **Buried critical information** in middle of paragraphs

### Acceptable Trade-offs (Priority 1 > Priority 2/3 > Priority 4)

When priorities conflict, higher priority wins:

- **More tokens for explicit error handling** - Acceptable (Priority 1 over Priority 3)
- **Repeated key terms for clarity** - Acceptable (Priority 1 over Priority 3)
- **Complete examples over terse references** - Acceptable (Priority 1 over Priority 3)
- **Explicit branches for all conditionals** - Required even if verbose (Priority 1)
- **Verbose discovery metadata over compact** - Acceptable (Priority 2 over Priority 3)

## Key Principles

### 1. Sequential Processing Model

LLMs read text linearly without visual layout interpretation. Design implications:

**Do:**
- Structure information as ordered lists
- Use bold prefixes for categorization (`**Category:** content`)
- Place related items in consecutive lines

**Don't:**
- Use ASCII tables (agents parse cell-by-cell without grid context)
- Rely on column alignment for meaning
- Assume visual proximity conveys relationship

### 2. Explicit Over Implicit

Agents follow explicit instructions reliably; they struggle with implied requirements.

**Do:**
- State requirements directly: "Always validate input before processing"
- Use action verbs: "Create", "Validate", "Return", "Check"
- Specify conditions: "When X, do Y"

**Don't:**
- Assume context: "Handle errors appropriately"
- Use passive voice: "Errors should be handled"
- Leave conditions ambiguous: "Consider error handling"

### 3. Schema-Critical Sections

Some sections require specific structures for deterministic agent behavior:

**Contract Section:**
- Must use Markdown subsections (###), NOT XML tags
- Refer to 002-rule-governance.md §Contract Structure for canonical format
- All subsections required in order
- Enables consistent extraction by any agent

**Anti-Patterns Section:**
- Must use code blocks for examples
- Must include "Problem:" and "Correct Pattern:" keywords
- Enables pattern matching for violation detection

### 4. Token Efficiency Without Information Loss

Optimize tokens while preserving meaning:

**Effective Compression:**
- "Use `uvx ruff check .` for linting" (7 tokens)
- Not: "The recommended approach for linting is to use the uvx command with ruff" (14 tokens)

**Ineffective Compression (Loses Information):**
- "Lint code" (2 tokens) - Missing tool, command, context
- Better: "Lint with `uvx ruff check .`" (6 tokens) - Preserves actionable detail

### 5. Terminology Consistency

Use identical terms for identical concepts across all rules:

**Standard Terms (use the first term; avoid alternatives):**
- "agent" — not "AI", "LLM", "bot", "assistant"
- "rule" — not "prompt", "instruction set", "system prompt", "guideline"
- "rule file" — not "rule document", "rule spec", "rule page"
- "validation" — not "checking", "verification"
- "execution" — not "running", "performing", "processing"
- "execution steps" — not "workflow", "procedure", "instructions"
- "anti-pattern" — not "bad practice", "mistake", "pitfall"
- "schema" — not "definition", "spec", "format"
- "metadata" — not "frontmatter", "header fields", "properties"
- "dependency" — not "prerequisite rule", "required rule"
- "context window" — not "context limit", "token limit", "memory"
- "token budget" — not "token count", "token allocation", "size"
- "cross-reference" — not "link", "pointer", "see also"
- "surgical edit" — not "targeted change", "minimal fix", "patch"
- "blocking issue" — not "critical bug", "showstopper", "dealbreaker"

## Anti-Patterns and Common Mistakes

For the complete set of 9 formatting anti-patterns with Problem/Correct Pattern examples,
see `002m-agent-format-antipatterns.md`. Key violations to avoid:

1. ASCII tables in rule content (use structured lists)
2. Arrow characters outside code blocks (use text alternatives — see Arrow Replacement Guide)
3. ASCII decision trees (use nested lists — see Tree Replacement Guide)
4. Passive voice in instructions (use imperative voice)
5. Buried critical information (front-load priorities)

### Anti-Pattern 1: Using ASCII Tables for Options

**Problem:** Tables waste tokens and confuse sequential parsing.

```markdown
| Flag | Description |
|------|-------------|
| --dry-run | Preview changes |
| --force | Skip confirmations |
```

**Correct Pattern:** Use structured lists instead.

```markdown
**Flags:**
- **`--dry-run`** - Preview changes without applying
- **`--force`** - Skip confirmation prompts
```

### Anti-Pattern 2: Arrow Characters in Rule Content

**Problem:** Arrow characters cause encoding issues and validation failures.

```markdown
Input -> Process -> Output
Bad state -> Good state
```

**Correct Pattern:** Use text alternatives based on context.

```markdown
Input to Process to Output
Bad state becomes Good state
```

The Arrow Replacement Guide and Tree Replacement Guide below remain in this rule for
quick reference during agent optimization work.

**Arrow Replacement Guide:**
- **Sequences:** "then" - `Step 1, then Step 2`
- **Data flow:** "to" - `Input to Output`
- **Corrections:** "Instead, use" - `Bad. Instead, use good.`
- **UI navigation:** ">" - `Menu > Submenu > Item`
- **Mappings:** "maps to" or "becomes" - `Input becomes Output`
- **Causes:** "causes" or "results in" - `Error causes failure`

**Tree Replacement Guide:**

For simple yes/no decisions:
```markdown
**Question?**
- If YES: Action
- If NO: Alternative action
```

For multi-branch decisions:
```markdown
**What is the condition?**
- If CONDITION_A: Action A
- If CONDITION_B: Action B
- If CONDITION_C: Action C
```

For directory structures:
```markdown
Directory structure for `project/`:
- **folder/** - Description
  - `file.ext` - Purpose
  - **subfolder/** - More files
```

### Binary and Image Content

Rules must contain text-only content. Do not embed images or binary content. If visual reference is needed, describe the concept textually or reference an external file path.

## Format Guidelines Reference

### List Formatting (Preferred)

**Simple key-value:**
```markdown
- **Key:** Value
- **Key:** Value
```

**Multi-attribute items:**
```markdown
**Item Name:**
- Attribute 1: Value
- Attribute 2: Value
- Attribute 3: Value
```

**Decision guidance:**
```markdown
**When to use X:**
- Condition 1 (reason)
- Condition 2 (reason)

**When to use Y:**
- Condition 1 (reason)
- Condition 2 (reason)
```

### When Tables May Be Acceptable

Tables are acceptable only when:
1. Data has 4+ columns with genuine grid relationships
2. Row/column intersection creates unique meaning
3. No simpler list structure preserves the information

If in doubt, use structured lists instead.
