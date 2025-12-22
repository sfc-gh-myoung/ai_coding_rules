# Claude Code Skills Best Practices

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential patterns for creating Claude Code skills.
> Load when authoring, reviewing, or maintaining skills in the `skills/` directory.

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Claude Code, skills, SKILL.md, agent skills, skill structure, progressive disclosure, workflows, trigger keywords, skill authoring, skill testing, skill validation, input contracts, output contracts, skill examples
**TokenBudget:** ~2400
**ContextTier:** High
**Depends:** 000-global-core.md, 002-rule-governance.md

## Purpose

Defines best practices for authoring Claude Code skills, covering SKILL.md structure, directory organization, progressive disclosure patterns, input/output contracts, workflow phases, and testing strategies for reproducible, production-ready agent skills.

## Rule Scope

All skill files in the `skills/` directory, including SKILL.md entrypoints, workflow guides, examples, and test files.

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **YAML frontmatter required:** Every SKILL.md must start with `---` delimited frontmatter containing name, description, version, author, tags, dependencies
- **Progressive disclosure:** Keep SKILL.md focused on core workflow; move detailed guides to `workflows/`, examples to `examples/`, tests to `tests/`
- **Trigger keywords in description:** Include activation phrases (e.g., "create rule", "review docs") in the description field for semantic discovery
- **Input/output contracts:** Define required and optional inputs, specify exact output locations and formats
- **Workflow phase references:** List phases in order with pointers to detailed workflow files
- **No inline implementation:** SKILL.md orchestrates; workflow files contain step-by-step instructions

**Pre-Execution Checklist:**
- [ ] Skill purpose clearly defined (what problem does it solve?)
- [ ] YAML frontmatter complete (name, description, version, author, tags)
- [ ] Directory structure created (SKILL.md, README.md, workflows/, examples/, tests/)
- [ ] Trigger keywords identified and included in description
- [ ] Input contract defined (required vs optional, formats, defaults)
- [ ] Output contract defined (file paths, formats, no-overwrite rules)
- [ ] At least one example workflow documented

## Contract

<inputs_prereqs>
Skill authoring task; understanding of Claude Code skill format; access to skills/ directory; knowledge of target workflow domain
</inputs_prereqs>

<mandatory>
Text editor; skills/ directory write access; understanding of progressive disclosure; familiarity with YAML frontmatter
</mandatory>

<forbidden>
Putting detailed implementation in SKILL.md; omitting YAML frontmatter; using undocumented trigger patterns; skipping input validation; hardcoding paths without defaults
</forbidden>

<steps>
1. Create skill directory: `skills/<skill-name>/`
2. Create SKILL.md with YAML frontmatter (name, description, version, author, tags, dependencies)
3. Write Purpose section (1-2 sentences defining the problem solved)
4. Write "Use this skill when" section with activation scenarios
5. Define Inputs section (required and optional with defaults)
6. Define Outputs section (file paths, formats, no-overwrite behavior)
7. Create workflow files in `workflows/` for each phase
8. Create example files in `examples/` showing complete walkthroughs
9. Create test files in `tests/` with input validation and workflow tests
10. Create README.md with usage documentation and quick start
</steps>

<output_format>
Skill directory with SKILL.md entrypoint, README.md documentation, workflows/ phase guides, examples/ walkthroughs, tests/ validation files
</output_format>

<validation>
- SKILL.md has valid YAML frontmatter (parseable, all required fields present)
- All workflow files referenced in SKILL.md exist
- All example files demonstrate complete workflows
- Input validation covers required fields and format constraints
- Output paths follow no-overwrite conventions
</validation>

## Key Principles

### 1. SKILL.md Structure

**YAML Frontmatter (Required):**

```yaml
---
name: skill-name
description: Brief description with trigger keywords like "create", "review", "validate"
version: 1.0.0
author: Author or Project Name
tags: [tag1, tag2, tag3]
dependencies: []
---
```

**Required Sections:**
- **Purpose:** 1-2 sentences defining what the skill does
- **Use this skill when:** Bullet list of activation scenarios
- **Inputs:** Required and optional parameters with defaults
- **Outputs:** File paths and formats produced
- **Workflow:** Ordered list of phases with file references
- **Examples:** Links to example walkthroughs

### 2. Directory Organization

```
skills/<skill-name>/
├── SKILL.md           # Entrypoint with frontmatter and workflow overview
├── README.md          # Usage documentation, quick start, troubleshooting
├── PROMPT.md          # Optional: detailed prompt templates
├── VALIDATION.md      # Optional: skill self-validation procedures
├── workflows/         # Phase-specific detailed guides
│   ├── phase-1.md
│   ├── phase-2.md
│   └── ...
├── examples/          # Complete workflow walkthroughs
│   ├── basic-example.md
│   ├── advanced-example.md
│   └── edge-cases.md
└── tests/             # Test cases and validation
    ├── README.md
    ├── test-inputs.md
    └── test-workflows.md
```

### 3. Progressive Disclosure

**SKILL.md (High-Level):**
- Core workflow overview
- Quick validation snippets
- Phase references to workflow files

**workflows/ (Detailed):**
- Step-by-step instructions per phase
- Decision trees and conditionals
- Error handling procedures

**examples/ (Concrete):**
- Complete end-to-end walkthroughs
- Real inputs and outputs
- Edge case handling

### 4. Input/Output Contracts

**Input Contract Pattern:**

```markdown
## Inputs

### Required
- `param_name`: `format` - Description

### Optional
- `param_name`: `format` (default: `value`) - Description
```

**Output Contract Pattern:**

```markdown
## Output (required)

Write to: `path/to/<name>-<date>.md`

**No overwrites:** If file exists, append `-01.md`, `-02.md`, etc.
```

### 5. Trigger Keywords

Include activation phrases in the description field:

```yaml
description: Review project documentation. Triggers on "review docs", "audit documentation", "check README", "documentation quality".
```

**Effective trigger patterns:**
- Action verbs: "create", "review", "validate", "generate", "check"
- Domain nouns: "rule", "documentation", "code", "tests"
- Combinations: "create rule", "review docs", "validate schema"

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Monolithic SKILL.md

**Problem:** Putting all implementation details, examples, and edge cases directly in SKILL.md instead of using progressive disclosure.

```text
# Bad: Everything in SKILL.md (500+ lines)
# Purpose section
...
# Detailed Step 1 section
[50 lines of instructions]
# Detailed Step 2 section
[100 lines of instructions]
# Example 1 section
[Complete walkthrough]
# Example 2 section
[Another complete walkthrough]
# Edge Cases section
[All edge cases inline]
```

**Why It Fails:**
- Consumes excessive context tokens on every skill activation
- Makes skill updates difficult (changes buried in large file)
- Overwhelms agent with details before understanding workflow

**Correct Pattern:**

```text
# Good: SKILL.md as orchestrator
# Purpose section
Brief description.

# Workflow section (progressive disclosure)
1. Phase 1: see workflows/phase-1.md
2. Phase 2: see workflows/phase-2.md

# Examples section
- Basic: see examples/basic.md
- Advanced: see examples/advanced.md
```

**Benefits:**
- Minimal token cost for skill activation
- Easy to update individual phases
- Agent loads detail only when needed

### Anti-Pattern 2: Missing Input Validation

**Problem:** Accepting inputs without validation, leading to failures deep in workflow execution.

```markdown
# Bad: No validation
## Inputs
- target_file: The file to process
- mode: Processing mode

[Proceeds directly to workflow without checking inputs]
```

**Why It Fails:**
- Invalid inputs cause cryptic errors mid-workflow
- Agent wastes tokens on doomed execution paths
- User experience degraded by late failures

**Correct Pattern:**

```python
# Good: Explicit validation with quick snippets in SKILL.md
# Inputs section defines: target_file (path, must exist, must be .md)
#                         mode (FULL | FOCUSED | STALENESS)

def check_inputs(target_file: str, mode: str) -> tuple[bool, list[str]]:
    errors = []
    if not Path(target_file).exists():
        errors.append(f"File not found: {target_file}")
    if mode.upper() not in {'FULL', 'FOCUSED', 'STALENESS'}:
        errors.append(f"Invalid mode: {mode}")
    return (len(errors) == 0, errors)
```

**Benefits:**
- Fails fast with clear error messages
- Reduces wasted computation on invalid inputs
- Improves user experience with actionable feedback

### Anti-Pattern 3: Vague Trigger Keywords

**Problem:** Using generic or ambiguous keywords that cause false activations or missed activations.

```yaml
# Bad: Too generic
description: A skill for working with files and doing things.
```

**Why It Fails:**
- "files" and "things" match too many unrelated requests
- Skill activates when it shouldn't, or fails to activate when it should
- User confusion about when to use the skill

**Correct Pattern:**

```yaml
# Good: Specific action + domain combinations
description: Create production-ready rule files. Triggers on "create rule", "add rule", "new rule", "generate rule for [technology]".
```

**Benefits:**
- Precise activation on intended requests
- Clear user understanding of skill purpose
- Reduced false positives and negatives

## Post-Execution Checklist

- [ ] SKILL.md has valid YAML frontmatter (name, description, version, author, tags)
- [ ] Description includes specific trigger keywords
- [ ] Inputs section defines required vs optional with formats
- [ ] Outputs section specifies paths and no-overwrite behavior
- [ ] Workflow phases reference existing files in workflows/
- [ ] At least one complete example exists in examples/
- [ ] Quick validation snippets provided for input checking
- [ ] README.md documents usage and troubleshooting
- [ ] All referenced files exist and are accessible
- [ ] Skill tested with representative inputs

## Validation

**Success Checks:**
- YAML frontmatter parses without errors
- All workflow file references resolve to existing files
- Input validation snippets execute without syntax errors
- Example files demonstrate complete workflows
- Trigger keywords appear in description field

**Negative Tests:**
- Missing frontmatter field triggers clear error
- Invalid input format caught by validation snippets
- Non-existent workflow file reference flagged
- Skill without examples marked incomplete

## Output Format Examples

### SKILL.md Frontmatter Template

```yaml
name: my-skill
description: Brief purpose. Triggers on "keyword1", "keyword2", "action noun".
version: 1.0.0
author: Project Name
tags: [domain, action, output-type]
dependencies: []
```

### SKILL.md Section Structure

The SKILL.md file should contain these sections in order:

1. **Purpose** - 1-2 sentences describing the problem solved
2. **Use this skill when** - Bullet list of activation scenarios
3. **Inputs** - Required and optional parameters with defaults
4. **Output (required)** - File paths and no-overwrite behavior
5. **Workflow (progressive disclosure)** - Ordered phase list with file references
6. **Examples** - Links to example walkthroughs
7. **Quick Validation Snippets** - Inline validation code

### Directory Creation Commands

```bash
# Create skill directory structure
mkdir -p skills/my-skill/{workflows,examples,tests}

# Create required files
touch skills/my-skill/SKILL.md
touch skills/my-skill/README.md
touch skills/my-skill/workflows/{input-validation,processing,output}.md
touch skills/my-skill/examples/{basic,edge-cases}.md
touch skills/my-skill/tests/{README,test-inputs,test-workflows}.md
```

### Input Validation Snippet Example

```python
from pathlib import Path

def check_inputs(target_file: str, mode: str) -> tuple[bool, list[str]]:
    """Validate skill inputs before workflow execution."""
    errors = []
    if not Path(target_file).exists():
        errors.append(f"File not found: {target_file}")
    if mode.upper() not in {'FULL', 'FOCUSED', 'STALENESS'}:
        errors.append(f"Invalid mode: {mode}")
    return (len(errors) == 0, errors)
```

## References

### Related Rules
- `rules/000-global-core.md` - Foundation patterns for all agents
- `rules/002-rule-governance.md` - Schema standards (skills follow similar patterns)
- `rules/002a-rule-creation-guide.md` - Rule creation workflow (parallel to skill creation)
- `rules/003-context-engineering.md` - Context management for progressive disclosure

### External Documentation
- [Claude Code Skills Guide](https://docs.anthropic.com) - Official Anthropic documentation
- [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) - Community patterns

### Example Skills in Repository
- `skills/rule-creator/` - Rule creation skill with full workflow structure
- `skills/rule-reviewer/` - Rule review skill with quality dimensions
- `skills/doc-reviewer/` - Documentation review skill with cross-reference validation
