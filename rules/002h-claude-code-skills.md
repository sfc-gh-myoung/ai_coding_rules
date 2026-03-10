# Claude Code Skills Best Practices

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential patterns for creating Claude Code skills.
> Load when authoring, reviewing, or maintaining skills in the `skills/` directory.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.4.0
**LastUpdated:** 2026-03-09
**Keywords:** Claude Code, skills, SKILL.md, skill structure, progressive disclosure, workflows, trigger keywords, skill authoring, skill testing, skill validation, input contracts, output contracts, skill examples, YAML frontmatter, description writing, MCP tools, degrees of freedom, context window, third person, naming conventions
**TokenBudget:** ~4500
**ContextTier:** High
**Depends:** 000-global-core.md, 002-rule-governance.md
**LoadTrigger:** dir:skills/, kw:skill

## Scope

**What This Rule Covers:**
Best practices for authoring Claude Code skills in the `skills/` directory. Covers SKILL.md structure, YAML frontmatter, directory organization, progressive disclosure patterns, input/output contracts, workflow phases, trigger keywords, and testing strategies for reproducible, production-ready agent skills.

**Important:** Skills in `skills/` use YAML frontmatter format. This is DIFFERENT from rules in `rules/` which use inline `**Field:** value` format per `002-rule-governance.md`. Do not confuse skill format with rule format.

**When to Load This Rule:**
- Authoring new Claude Code skills
- Reviewing or maintaining skills in `skills/` directory
- Understanding skill structure and organization
- Creating workflow guides and examples
- Testing and validating skills

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules
- **002-rule-governance.md** - Schema requirements and v3.2 standards

**Related:**
- **002a-rule-creation.md** - Rule authoring principles apply to skills
- **002d-advanced-rule-patterns.md** - Progressive disclosure and workflows

### External Documentation

- **[Claude Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)** - Official Anthropic guidance on skill authoring
- **[Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)** - Claude Code skill format and usage
- **YAML Specification** - YAML frontmatter formatting reference

## Contract

### Inputs and Prerequisites

- Skill authoring task
- Understanding of Claude Code skill format
- Access to `skills/` directory
- Knowledge of target workflow domain

### Mandatory

- Text editor
- `skills/` directory write access
- Understanding of progressive disclosure
- Familiarity with YAML frontmatter

### Forbidden

- Putting detailed implementation in SKILL.md (use workflow files; **see Size Limit below**)
- Omitting required YAML frontmatter fields (`name`, `description`)
- Writing description in first person ("I can help") or second person ("you can use")
- Using vague or generic trigger keywords (see specificity criteria below)
- Skipping input validation
- Hardcoding paths without defaults
- Using bare tool names instead of fully qualified MCP tool names (ServerName:tool_name)
- Assuming packages are installed without explicit installation instructions

### Execution Steps

1. Create skill directory: `skills/<skill-name>/`
2. Create SKILL.md with YAML frontmatter:
   - Required: `name` (lowercase-hyphens, max 64 chars), `description` (third person, max 1024 chars)
   - Project standard: `version` (semantic versioning)
   - Optional: `author`, `tags`, `dependencies`
3. Write Purpose section (1-2 sentences defining the problem solved)
4. Write "Use this skill when" section with activation scenarios
5. Define Inputs section (required and optional with defaults)
6. Define Outputs section (file paths, formats, no-overwrite behavior)
7. Create workflow files in `workflows/` for each phase (see Size Limit below)
8. Create example files in `examples/` showing complete walkthroughs
9. Create test files in `tests/` with input validation and workflow tests
10. Create README.md with usage documentation and quick start

### Output Format

Skill directory structure with:
- SKILL.md entrypoint with YAML frontmatter
- README.md documentation
- workflows/ phase guides
- examples/ walkthroughs
- tests/ validation files

### Error Recovery

- **SKILL.md exceeds 500 lines:** Extract detailed content into `workflows/` or `reference/` files using progressive disclosure. Keep SKILL.md as an overview with cross-references.
- **YAML frontmatter fails to parse:** Validate YAML syntax separately. Check for unescaped colons in description text, missing closing `---`, or tab characters (use spaces only).
- **Skill not discovered by Claude:** Verify the `description` field contains specific trigger keywords. Test with exact phrases users would say. Ensure the description is non-empty and under 1024 characters.
- **MCP tool not found at runtime:** Confirm fully qualified `ServerName:tool_name` format. Verify the MCP server is available in the execution environment.
- **Package dependency missing:** Add explicit install instructions in the skill workflow. Do not assume packages are pre-installed, especially in API environments with no network access.

### Validation

**Pre-Task-Completion Checks:**
- Skill purpose clearly defined
- YAML frontmatter fields identified
- Directory structure planned
- Trigger keywords identified
- Input/output contracts defined
- Workflow phases planned

**Success Criteria:**
- SKILL.md has valid YAML frontmatter with required fields (`name`, `description`)
- `name` follows format requirements (lowercase-hyphens, max 64 chars, no reserved words)
- `description` written in third person, max 1024 chars, includes trigger keywords
- `description` includes both WHAT skill does and WHEN to use it
- SKILL.md body under 500 lines (see Size Limit in Key Principles)
- All workflow files referenced in SKILL.md exist
- All example files demonstrate complete workflows
- Input validation covers required fields and format constraints
- Output paths follow no-overwrite conventions
- MCP tool references use fully qualified names
- Package dependencies explicitly listed
- Skill tested with target models (Haiku/Sonnet/Opus as applicable)

**Negative Tests:**
- Missing frontmatter field triggers clear error
- Invalid input format caught by validation snippets
- Non-existent workflow file reference flagged
- Skill without examples marked incomplete

### Post-Execution Checklist

**YAML Frontmatter:**
- [ ] `name` field: lowercase-letters-and-hyphens-only, max 64 chars, no reserved words
- [ ] `description` field: written in third person, max 1024 chars, includes trigger keywords
- [ ] `description` includes both WHAT skill does and WHEN to use it
- [ ] `version` field present (project standard)
- [ ] YAML frontmatter is parseable (valid YAML syntax)

**Content Quality:**
- [ ] SKILL.md body under 500 lines (see Size Limit in Key Principles)
- [ ] Description written in third person (no "I" or "you")
- [ ] Appropriate degrees of freedom set for task fragility
- [ ] Assumes Claude's existing knowledge (concise, not verbose)
- [ ] Inputs section defines required vs optional with formats
- [ ] Outputs section specifies paths and no-overwrite behavior
- [ ] MCP tool references use fully qualified names (ServerName:tool_name)
- [ ] Package dependencies explicitly listed and verified

**Progressive Disclosure:**
- [ ] Workflow phases reference existing files in workflows/
- [ ] At least one complete example exists in examples/
- [ ] Quick validation snippets provided for input checking
- [ ] All referenced files exist and are accessible

**Documentation & Testing:**
- [ ] README.md documents usage and troubleshooting
- [ ] Skill tested with representative inputs
- [ ] Tested with all models intended for use (Haiku, Sonnet, Opus if applicable)

**Naming & Organization:**
- [ ] Skill name follows consistent convention (gerund or noun phrase)
- [ ] Files named descriptively (not doc1.md, doc2.md)
- [ ] Directory structure organized by domain/feature

## Key Principles

### 1. SKILL.md Structure

**YAML Frontmatter Requirements:**

**Required fields (Anthropic specification):**
- **name**: Skill identifier
  - Maximum 64 characters
  - Must contain only lowercase letters, numbers, and hyphens
  - Cannot contain XML tags
  - Cannot contain reserved words: "anthropic", "claude"
- **description**: Brief purpose with trigger keywords
  - Must be non-empty
  - Maximum 1024 characters
  - Cannot contain XML tags
  - Should describe what the skill does AND when to use it
  - **Must be written in third person** (critical for skill discovery). The description is injected into the system prompt; inconsistent point-of-view causes skill discovery problems.
    - Good: "Processes Excel files and generates reports"
    - Avoid: "I can help you process Excel files"
    - Avoid: "You can use this to process Excel files"
  - Be specific and include key terms for both WHAT the skill does and WHEN to use it
  - Include trigger keywords directly: `"Review project documentation. Triggers on 'review docs', 'audit documentation'."`
  - A non-vague description must include at least:
    1. One **action verb** (create, review, validate, analyze, generate, deploy)
    2. One **domain noun** (rule, schema, document, database, pipeline)
    3. One **qualifying context** (quality, compliance, format, Snowflake, Python)
  - Examples:
    - PASS: "Reviews rule files for schema compliance and agent executability"
      (verb: reviews, noun: rule files, context: schema compliance + agent executability)
    - PASS: "Generates Snowflake stored procedures from natural language descriptions"
      (verb: generates, noun: stored procedures, context: Snowflake + natural language)
    - FAIL: "Helps with documents" (verb: helps — too generic, no context)
    - FAIL: "Processes data" (verb: processes — too generic, no domain noun specificity)

**Project standard (optional fields):**
- **version**: Semantic version (e.g., 1.0.0, 2.1.0) - Recommended for tracking changes
  - Major: breaking workflow changes (renamed inputs, removed steps)
  - Minor: new features or steps (added inputs, new workflow phases)
  - Patch: bug fixes or wording improvements

**Other optional fields:**
- **author**: Author or project name
- **tags**: Category labels array
- **dependencies**: Prerequisite skills array

**Example:**

```yaml
---
name: rule-reviewer
description: Execute agent-centric rule reviews using 6-dimension rubric. Use when reviewing rule files, auditing quality, checking staleness, or validating compliance.
version: 2.0.0
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

- **skills/\<skill-name\>/** - Skill root directory
  - `SKILL.md` - Entrypoint with frontmatter and workflow overview
  - `README.md` - Usage documentation, quick start, troubleshooting
  - `PROMPT.md` - Optional: detailed prompt templates
  - `VALIDATION.md` - Optional: skill self-validation procedures
  - **workflows/** - Phase-specific detailed guides
    - `phase-1.md`, `phase-2.md`, etc.
  - **examples/** - Complete workflow walkthroughs
    - `basic-example.md`, `advanced-example.md`, `edge-cases.md`
  - **tests/** - Test cases and validation
    - `README.md`, `test-inputs.md`, `test-workflows.md`

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

### 6. Core Principles from Official Best Practices

#### Concise is Key

The context window is shared with system prompt, conversation history, other skills' metadata, and user requests.

**Default assumption:** Claude is already very smart. Only add context Claude doesn't already have.

**Size Limit:** Keep SKILL.md body under 500 lines for optimal performance. If content exceeds this, split into separate files using progressive disclosure patterns.

**Example - concise vs verbose:**

```markdown
# Concise (Good): ~50 tokens - assumes Claude knows what PDFs are
Use pdfplumber for text extraction:
  import pdfplumber
  with pdfplumber.open("file.pdf") as pdf:
      text = pdf.pages[0].extract_text()

# Verbose (Bad): ~150 tokens - explains what PDFs are, compares libraries
PDF (Portable Document Format) files are a common file format...
```

#### Set Appropriate Degrees of Freedom

Match specificity to the task's fragility and variability:

- **High freedom** (text-based): Multiple valid approaches, context-dependent decisions
- **Medium freedom** (pseudocode/templates): Preferred pattern exists, some variation acceptable
- **Low freedom** (exact scripts): Operations fragile/irreversible, consistency critical, error recovery expensive

Use high freedom when tasks are exploratory or creative. Use low freedom when output format is rigidly defined or operations are irreversible.

#### Test with All Models You Plan to Use

Skills act as additions to models, so effectiveness depends on the underlying model. What works for Opus might need more detail for Haiku. Test with all models you intend to support:
- **Claude Haiku** (fast, economical): Does the skill provide enough guidance?
- **Claude Sonnet** (balanced): Is the skill clear and efficient?
- **Claude Opus** (powerful reasoning): Does the skill avoid over-explaining?

#### Naming Conventions

**Recommended:** gerund form (verb + -ing): `processing-pdfs`, `analyzing-spreadsheets`, `managing-databases`

**Acceptable:** noun phrases (`pdf-processing`, `rule-reviewer`) or action-oriented (`process-pdfs`)

**Avoid:** vague names (`helper`, `utils`, `tools`), overly generic (`documents`, `data`). See Forbidden section for reserved word restrictions.

## Technical Details

### MCP Tool References

If your skill uses MCP (Model Context Protocol) tools, always use fully qualified tool names to avoid "tool not found" errors.

**Format:** `ServerName:tool_name`

**Example:**

```markdown
Use the BigQuery:bigquery_schema tool to retrieve table schemas.
Use the GitHub:create_issue tool to create issues.
```

Where:
- `BigQuery` and `GitHub` are MCP server names
- `bigquery_schema` and `create_issue` are the tool names within those servers

Without the server prefix, Claude may fail to locate the tool, especially when multiple MCP servers are available.

### Package Dependencies

Skills run in the code execution environment with platform-specific limitations:

- **claude.ai**: Can install packages from npm and PyPI and pull from GitHub repositories
- **Anthropic API**: Has no network access and no runtime package installation

List required packages in your SKILL.md and verify they're available.

**Don't assume packages are installed:**

````markdown
# Bad: Assumes installation
"Use the pdf library to process the file."

# Good: Explicit about dependencies
"Install required package: `pip install pypdf`

Then use it:
```python
from pypdf import PdfReader
reader = PdfReader("file.pdf")
```"
````

### Runtime Environment and Progressive Disclosure

For runtime environment details, refer to the Anthropic skill documentation.
Key runtime considerations: package availability differs between claude.ai (can install)
and API (no network access). See lines 371-372 for platform-specific guidance.

## Advanced Patterns

**See:** **002l-skill-advanced-patterns.md** for plan-validate-execute, visual analysis, and orchestrator-worker composition patterns.

### Concurrent Skill Modification

When multiple developers may edit the same skill:

1. Use git branches — one branch per skill modification
2. Check `git status skills/<skill-name>/` before editing
3. If conflict on SKILL.md: prefer the version with more specific trigger keywords
4. If conflict on workflow files: merge both changes, re-test the complete workflow

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Monolithic SKILL.md

**Problem:**
```markdown
# BAD: Everything inline (800+ lines)
## Rubric
[200 lines of rubric...]
## Workflow  
[400 lines of workflow...]
```

**Correct Pattern:**
```markdown
# GOOD: Progressive disclosure (~250 lines)
## Quick Reference
See rubrics/quality-rubric.md for full criteria.

## Workflow
1. Read workflows/review-workflow.md
2. Execute review steps
```

### Anti-Pattern 2: Missing Input Validation

**Problem:**
```markdown
# BAD: No validation - fails deep in workflow
1. Read the file at {path}
2. Apply rubric...
```

**Correct Pattern:**
```markdown
# GOOD: Validate first
1. Verify {path} exists and is readable
2. If missing: Report error, stop workflow
3. Read the file at {path}
```

### Anti-Pattern 3: Vague Trigger Keywords

**Problem:**
```yaml
# BAD: Too generic, causes false activations
description: Helps with files and things.
```

**Correct Pattern:**
```yaml
# GOOD: Specific action + domain
description: Reviews rule files for quality. Triggers on "review rule", "audit rules".
```

### Anti-Pattern 4: Description Not in Third Person

**Problem:**
```yaml
# BAD: First/second person causes skill discovery issues
description: I can help you review rules.
```

**Correct Pattern:**
```yaml
# GOOD: Third person, active voice
description: Reviews rule files for quality and compliance.
```

### Anti-Pattern 5: SKILL.md Exceeds Size Limit

**Problem:**
```markdown
# BAD: 600 lines inline, excessive context consumption
[All rubrics, workflows, examples embedded...]
```

**Correct Pattern:**
```markdown
# GOOD: ~250 lines with references
See rubrics/ for evaluation criteria.
See workflows/ for step-by-step guides.
```

### Testing Skill Discovery

To verify a skill triggers correctly:

1. Identify 3-5 natural language prompts that SHOULD trigger the skill
2. Identify 2-3 prompts that should NOT trigger it
3. For each prompt, verify the description's trigger keywords would match
4. Test with the actual agent: "When I say '[prompt]', does this skill appear?"
5. If discovery fails: add more specific keywords to the description field

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
