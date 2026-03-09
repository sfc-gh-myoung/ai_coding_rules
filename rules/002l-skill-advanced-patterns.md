# Skill Advanced Patterns

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines advanced skill authoring patterns for Claude Code skills.
> Load when building complex skills requiring plan-validate-execute, visual analysis, or orchestrator composition.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** skill advanced patterns, plan-validate-execute, visual analysis, skill composition, orchestrator worker, batch skills, verifiable outputs, intermediate validation
**TokenBudget:** ~1950
**ContextTier:** Low
**Depends:** 002h-claude-code-skills.md
**LoadTrigger:** kw:skill composition, kw:plan-validate-execute, kw:orchestrator skill, kw:batch skill, kw:visual analysis pattern

## Scope

**What This Rule Covers:**
Advanced patterns for Claude Code skill authoring: the plan-validate-execute pattern for verifiable intermediate outputs, visual analysis for image-based inputs, and the orchestrator-worker composition pattern for bulk/batch skills.

**When to Load This Rule:**
- Building skills that need intermediate validation steps
- Creating batch or bulk processing skills
- Designing orchestrator-worker skill compositions
- Working with visual or image-based skill inputs

## References

### Dependencies

**Must Load First:**
- **002h-claude-code-skills.md** - Core skill authoring patterns and structure

**Related:**
- **002d-advanced-rule-patterns.md** - Advanced rule patterns (parallel to skill patterns)

## Contract

### Inputs and Prerequisites

- Familiarity with core skill structure (see 002h-claude-code-skills.md)
- An existing or planned skill requiring advanced patterns

### Mandatory

- Core skill already has SKILL.md with valid YAML frontmatter
- Workflow files exist or are planned in `workflows/` directory

### Forbidden

- Applying plan-validate-execute to trivial single-step operations
- Orchestrator skills reimplementing worker logic instead of referencing worker SKILL.md
- Skipping the validation step in plan-validate-execute workflows

### Execution Steps

1. Identify which advanced pattern applies to your skill
2. Follow the pattern-specific guidance below
3. Integrate the pattern into your skill's workflow files

### Output Format

Skill workflow files updated with the chosen advanced pattern integrated into the appropriate phase.

### Validation

**Success Criteria:**
- Pattern correctly applied to skill workflow
- Intermediate validation scripts exist for plan-validate-execute patterns
- Orchestrator skills reference worker SKILL.md files, not reimplemented logic

### Error Recovery

- **Validation script bugs:** Fix the validation script, then re-run the plan-validate-execute cycle from step 3
- **Batch partial failure (worker fails on item N):** Continue to item N+1, record failure with error details, report all failures at end
- **Worker SKILL.md changes between runs:** Re-read worker documentation before each batch; adapt if interface has changed
- **Plan-validate catches errors:** Fix errors in the plan file and re-validate; maximum 3 retry attempts before escalating to the user

### Post-Execution Checklist

- [ ] Advanced pattern selected matches the skill's complexity requirements
- [ ] Plan-validate-execute: validation script exists and produces clear error messages
- [ ] Orchestrator-worker: orchestrator references worker SKILL.md, does not duplicate logic
- [ ] Pattern integrated into workflow files, not inlined in SKILL.md

## Pattern Selection

Choose the pattern based on the operation type:

- **Plan-Validate-Execute:** Batch/destructive operations, schema migrations, multi-step changes requiring rollback
- **Visual Analysis:** Form/layout-dependent inputs, document structure analysis, spatial relationships are critical
- **Orchestrator-Worker:** N items need the same workflow applied, batch processing with independent items

## Key Principles

### Verifiable Intermediate Outputs (Plan-Validate-Execute)

When Claude performs complex, open-ended tasks, it can make mistakes. The "plan-validate-execute" pattern catches errors early by having Claude first create a plan in a structured format, then validate that plan with a script before executing it.

**Example problem:** Asking Claude to update 50 form fields in a PDF based on a spreadsheet. Without validation, Claude might reference non-existent fields, create conflicting values, miss required fields, or apply updates incorrectly.

**Solution:** Add an intermediate `changes.json` file that gets validated before applying changes.

**Workflow:**
1. **Analyze** - Understand requirements
2. **Create plan file** - Generate `changes.json` with all modifications
3. **Validate plan** - Run validation script on plan file
4. **Execute** - Apply changes if validation passes
5. **Verify** - Confirm results

**Why this pattern works:**
- **Catches errors early**: Validation finds problems before changes are applied
- **Machine-verifiable**: Scripts provide objective verification
- **Reversible planning**: Claude can iterate on the plan without touching originals
- **Clear debugging**: Error messages point to specific problems

**When to use:**
- Batch operations
- Destructive changes
- Complex validation rules
- High-stakes operations

**Implementation tip:** Make validation scripts verbose with specific error messages like "Field 'signature_date' not found. Available fields: customer_name, order_total, signature_date_signed" to help Claude fix issues.

### Visual Analysis Pattern

When inputs can be rendered as images, have Claude analyze them visually instead of relying on text extraction alone.

**When to use:**
- Form/layout-dependent inputs (PDFs, screenshots, diagrams)
- Document structure where spatial relationships matter
- Inputs where text extraction loses critical formatting

**Workflow:**
1. **Identify visual inputs** - Determine which inputs benefit from image-based analysis
2. **Convert to images** - Render PDFs/documents to PNG/JPEG (e.g., `pdf2image`, `Pillow`, or built-in PDF reading)
3. **Analyze visually** - Use Claude's vision capabilities to identify fields, layouts, and relationships
4. **Extract structured data** - Convert visual observations into structured format (JSON, CSV)
5. **Validate extraction** - Compare extracted data against expected schema or field list

**Implementation tip:** For multi-page documents, process one page at a time to keep context focused. Include the page number in extracted data for traceability.

### Skill Composition Pattern (Orchestrator + Worker)

**Problem:** How do you create a "bulk" or "batch" skill that processes multiple items using another skill's workflow?

**Architecture:**

Orchestrator skill loads and follows the worker skill's documented workflow. Skills cannot invoke other skills programmatically - "Use the X skill" is guidance for users, not a callable API.

**Directory layout:**

- **bulk-processor/** (orchestrator)
  - `SKILL.md` - Batch processing logic
  - `workflows/batch-execution.md` - "For each: load processor/SKILL.md, follow workflow"
- **processor/** (worker)
  - `SKILL.md` - Single-item workflow
  - `workflows/` - Step-by-step processing

**What orchestrator does:**
- Loads worker SKILL.md once to understand workflow
- Follows that workflow for each item
- Uses progressive disclosure (loads rubrics/workflows as needed)
- Tracks batch metadata (progress, failures, resume)

**What orchestrator does NOT do:**
- Try to "invoke" worker skill programmatically
- Reimplement worker logic without consulting docs
- Skip progressive disclosure

**When to use:** Bulk operations, periodic audits, batch validation, mass migrations.

**Batch failure handling:** When worker fails on item N: (1) Log error with item identifier and error details, (2) Continue to item N+1, (3) After all items processed, report summary: `{succeeded: X, failed: Y, errors: [...]}`

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Skipping Validation in Plan-Validate-Execute

**Problem:** Executing plans directly without validation step.

```python
# WRONG: No validation
plan = generate_plan(task)
execute(plan)  # May contain errors
```

**Correct Pattern:**
```python
# CORRECT: Validate before execution
plan = generate_plan(task)
errors = validate_plan(plan)
if errors:
    raise ValidationError(errors)
execute(plan)
```

### Anti-Pattern 2: Orchestrator Reimplementing Worker Logic

**Problem:** Orchestrator duplicates worker skill logic instead of loading and following it.

```python
# WRONG: Duplicating worker logic
def orchestrator_process_item(item):
    # Copy-pasted logic from worker skill
    validate(item)
    transform(item)
    save(item)
```

**Correct Pattern:**
```python
# CORRECT: Read worker skill docs, follow documented workflow
def orchestrator_process_item(item):
    # Read worker/SKILL.md to understand the workflow
    # Execute each step from the worker's documented process
    # Do not reimplement — follow the documented steps
    pass
```
