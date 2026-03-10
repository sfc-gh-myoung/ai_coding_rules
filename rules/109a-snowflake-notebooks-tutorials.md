# Snowflake Notebook Tutorial Design Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.1
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:notebook-tutorial
**Keywords:** checkpoints, learning objectives, pedagogical design, educational content, progressive learning, Snowflake notebooks, teaching point callouts, validation gates, tutorial structure, learning design, educational notebooks, teaching methodology, notebook education
**TokenBudget:** ~3600
**ContextTier:** High
**Depends:** 109-snowflake-notebooks.md, 920-data-science-analytics.md

## Scope

**What This Rule Covers:**
Comprehensive patterns for designing educational Snowflake notebooks that effectively teach concepts through clear learning objectives, structured content, anti-pattern examples, validation checkpoints, and progressive complexity management.

**When to Load This Rule:**
- Creating tutorial notebooks for Snowflake
- Designing educational content and learning materials
- Building self-paced learning experiences
- Structuring notebook-based training
- Implementing learning checkpoints and validation

## References

### External Documentation
- [Snowflake Notebooks Getting Started](https://docs.snowflake.com/en/user-guide/ui-snowsight-notebooks-gs) - Official quickstart guide
- [Snowpark for Python Tutorials](https://quickstarts.snowflake.com/guide/getting_started_with_snowpark_python/index.html) - Hands-on learning
- [Jupyter Best Practices](https://jupyter-notebook.readthedocs.io/en/stable/notebook.html) - General notebook guidelines

### Related Rules
- **Notebook Core**: `109-snowflake-notebooks.md` - Core notebook patterns
- **App Deployment**: `109b-snowflake-app-deployment-core.md` - Production deployment
- **Snowflake Core**: `100-snowflake-core.md` - Foundational practices

## Contract

### Inputs and Prerequisites
- Technical notebook content from `109-snowflake-notebooks.md`
- Target audience definition (beginner/intermediate/advanced)
- Learning outcomes to achieve
- Time budget for tutorial completion

### Mandatory
- Learning objectives section at cell #2 with 3-6 measurable outcomes using action verbs
- Tutorial structure overview with time estimates for different modes (quick demo, full tutorial)
- Anti-pattern sections pairing wrong and correct examples with "why wrong" explanations
- Checkpoint validation cells between major sections (3-7 checks per checkpoint)
- Teaching point callouts with [NOTE] prefix placed before implementations
- All technical jargon defined on first use

### Forbidden
- Overly technical jargon without definitions for beginner content
- Copy-paste code without explanation
- Examples without context or business rationale

### Execution Steps
1. Define clear learning objectives (3-6 outcomes)
2. Structure content into logical parts with time estimates
3. Add anti-pattern sections showing what NOT to do
4. Insert checkpoint validations between major sections
5. Include teaching point callouts explaining "why"
6. Provide progressive complexity (simple, then advanced)
7. Add self-assessment opportunities

### Post-Execution Checklist

See detailed Post-Execution Checklist below for comprehensive tutorial validation steps.

### Output Format
- Learning objectives section (markdown cell #2 after main header)
- Tutorial structure overview with time estimates
- Anti-pattern sections with incorrect and correct examples
- Checkpoint validation cells (code cells with assertions)
- Teaching point callouts ([NOTE] prefix in markdown)

### Validation
1. Verify learning objectives are measurable and clear
2. Confirm all major sections have checkpoint validations
3. Check anti-patterns have both incorrect and correct examples
4. Validate time estimates are realistic
5. Test self-paced learning flow (can skip ahead)

### Design Principles
- **Clear Learning Path:** Objectives, then Structure, then Checkpoints, then Assessment
- **Show Don't Tell:** Anti-patterns teach as effectively as best practices
- **Validate Progress:** Checkpoints prevent learners from proceeding with errors
- **Progressive Disclosure:** Simple concepts first, complexity builds gradually
- **Self-Paced Friendly:** Can skip sections, clear prerequisites stated
- **Context First:** Business rationale before technical implementation

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Vague Learning Objectives**
```markdown
## Learning Objectives
1. Learn about ML
2. Understand data
3. Build models
```
**Problem:** Not measurable, no clear outcomes, too broad - learners won't know what specific skills they'll gain.

**Correct Pattern:** See Learning Objectives section below for the correct pattern with detailed examples and best practices.

**Anti-Pattern 2: No Anti-Pattern Teaching**

**Problem:** Listing best practices without showing what to avoid or why — learners may still make common mistakes.

```markdown
## Best Practices
1. Use parameterized queries
2. Validate inputs
3. Handle errors
```

**Correct Pattern:** Show both incorrect and correct approaches with explanations.

```markdown
## Common Mistakes and Solutions

### Anti-Pattern: String Concatenation in Queries
**Wrong:**
sql = f"SELECT * FROM users WHERE id = {user_id}"

**Correct:**
sql = "SELECT * FROM users WHERE id = ?"
cursor.execute(sql, (user_id,))

**Why:** String concatenation enables SQL injection attacks.
```

## Post-Execution Checklist

- [ ] Learning objectives section present (3-6 outcomes, measurable, placed at cell #2)
- [ ] Tutorial structure overview with time estimates provided
- [ ] Anti-pattern sections with incorrect and correct examples (3-5 per topic)
- [ ] Checkpoint validation cells between major sections (3-7 checks each)
- [ ] Teaching point callouts ([NOTE] prefix) explaining "why" before implementations
- [ ] Progressive complexity (simple, then real-world, then advanced pattern)
- [ ] Self-paced friendly (can skip sections, prerequisites stated clearly)
- [ ] Two-approach clarifications when demonstrating but not fully using features
- [ ] Time estimates realistic and tested
- [ ] All technical jargon defined on first use

### Tutorial Validation Script

Validate tutorial structure programmatically by checking:
- Learning objectives cell exists at position 2 (after main header)
- Checkpoint cells exist between major sections
- `[NOTE]` callouts precede code cells that implement key concepts
- Time estimates are present in Tutorial Structure section

## Validation

- **Success Checks:**
  - Learning objectives are specific and measurable
  - Checkpoints catch common errors and provide actionable fixes
  - Anti-patterns include both wrong and correct approaches with explanations
  - Time estimates match actual execution (tested)
  - Teaching points explain business context, not just technical details
  - Progressive complexity builds logically
  - Notebook works for self-paced learning (can skip ahead with prerequisites met)

- **Negative Tests:**
  - Vague objectives ("learn about ML") should be flagged
  - Missing checkpoints should be added between major sections
  - Anti-patterns without correct alternatives should be enhanced
  - Technical jargon without definitions should trigger warnings
  - Overly complex introductory sections should be simplified

> **Investigation Required**
> When applying this rule:
> 1. **Read existing notebook cells BEFORE creating learning objectives** - Extract actual content taught (algorithms, techniques, data patterns)
> 2. **Count major sections for structure calculation** - Use for "Parts" organization (aim for 5-7 parts max, group related steps)
> 3. **Analyze code complexity to validate audience level** - Beginner: basic operations; Intermediate: algorithms + optimization; Advanced: custom implementations
> 4. **Estimate time based on cell count and complexity** - Formula: ~30 seconds per markdown cell (reading), ~60 seconds per code cell (reading + execution)
> 5. **Check for existing checkpoint patterns** - Identify validation gates present vs needed (add between major transitions)
> 6. **Verify technical prerequisites mentioned** - List required knowledge explicitly (e.g., "assumes familiarity with pandas DataFrames")
> 7. **Never create generic learning objectives** - Base on specific features/concepts actually demonstrated in notebook
>
> **Anti-Pattern:**
> "Based on typical ML notebooks, you probably want to teach feature engineering and model training..."
> "Most tutorials include these standard learning objectives..."
> [Creates generic objectives without reading notebook]
>
> **Correct Pattern:**
> "Let me read your notebook structure first."
> [reads notebook cells, counts sections, analyzes code complexity]
> "I found 8 major sections across 42 cells (18 markdown, 24 code). Code complexity: intermediate (uses scikit-learn pipeline, SMOTE, threshold tuning).
>
> Based on actual content:
> 1. **Feature Engineering** - Organizes 16 ML features using Snowflake Feature Store (cells 5-12)
> 2. **Imbalanced Data Strategies** - Compares SMOTE vs class_weight parameter (cells 15-24, demonstrates 4 models)
> 3. **Threshold Optimization** - Tunes decision thresholds using ROC curves to minimize missed failures (cells 28-35)
>
> Estimated time: 12-15 minutes full tutorial (5-7 minutes quick demo with n_estimators=50)"

## Output Format Examples

```markdown
## [GOAL] Learning Objectives
By the end of this notebook, you will understand:
1. **[Concept]** - [Specific measurable outcome]
2. **[Concept]** - [Specific measurable outcome]

## Tutorial Structure
**Part 1: [Name]** (Steps 1-3, ~5 min)
**Part 2: [Name]** (Steps 4-6, ~8 min)

## Common Anti-Patterns in [Topic]
**Anti-Pattern 1: [Name]**
- Why wrong: [Explanation]
- Correct: [What to do instead]
```

```python
# Checkpoint validation cell
checks_passed, checks_failed = [], []
if condition:
    checks_passed.append("[PASS] Data loaded correctly")
else:
    checks_failed.append("[FAIL] Missing data - rerun Step 2")
print("ALL CHECKS PASSED" if not checks_failed else "Fix issues above")
```

### SQL-Only Tutorial Guidance

For SQL-focused tutorials without Python:
- Use SQL cells exclusively with Markdown narrative between them
- Checkpoint validations use SQL assertions: `SELECT CASE WHEN COUNT(*) > 0 THEN 'PASS' ELSE 'FAIL' END`
- Anti-patterns show wrong SQL alongside correct SQL
- Time estimates may be shorter (SQL cells execute faster than Python)

## Learning Objectives Section

> Sections below expand on Contract Mandatory requirements. See Contract for the authoritative list.

**Purpose:** Set clear expectations for what learners will achieve by completing the notebook.

**Structure:**
```markdown

## [GOAL] Learning Objectives

By the end of this notebook, you will understand:

1. **[Concept 1]** - [Specific skill or knowledge]
2. **[Concept 2]** - [Specific skill or knowledge]
3. **[Concept 3]** - [Specific skill or knowledge]
4. **[Concept 4]** - [Specific skill or knowledge]
5. **[Concept 5]** - [Specific skill or knowledge]
6. **[Concept 6]** - [Specific skill or knowledge]
```

**Best Practices:**
- **Requirement:** Place immediately after main header (cell #2)
- **Requirement:** 3-6 objectives maximum (cognitive load management)
- **Requirement:** Use action verbs (understand, implement, compare, optimize, analyze)
- **Requirement:** Each objective should be measurable and achievable
- **Always:** Bold the concept, explain the specific outcome
- **Consider:** Order from foundational to advanced concepts

**Example - Good:**
```markdown
1. **Feature Engineering** - How to organize 16 ML features using Snowflake Feature Store
2. **Imbalanced Data Strategies** - Compare SMOTE vs Algorithm-level balancing approaches
3. **Threshold Optimization** - Tune decision thresholds to align with business objectives
```

**Example - Bad:**
```markdown
1. Learn about features
2. Understand data
3. Build models
```
Too vague, not measurable, no clear outcome

## Tutorial Structure Overview

**Purpose:** Provide roadmap of tutorial organization with time estimates for self-paced learning.

**Structure:**
```markdown

## 📚 Tutorial Structure

This notebook is organized into [N] parts:

**Part 1: [Name]** (Steps X-Y)
- [Brief description of what's covered]
- [Key concepts introduced]

**Part 2: [Name]** (Steps X-Y)
- [Brief description]
- [Key concepts]

...

## Estimated Time

- **Quick Demo Mode:** X-Y minutes ([configuration])
- **Full Tutorial Mode:** X-Y minutes ([configuration])
- **Production Mode:** X-Y minutes ([configuration])

*Configure scenario in Step [reference]*
```

**Best Practices:**
- **Requirement:** Place after Learning Objectives (cell #3)
- **Requirement:** Provide time estimates for different modes
- **Always:** Group related steps into logical parts (5-7 parts maximum)
- **Always:** Indicate what each part teaches
- **Consider:** Show dependencies between parts (can skip if prerequisites known)

## Anti-Pattern Sections

**Purpose:** Teach what NOT to do by showing common mistakes alongside correct approaches. Use "Anti-Pattern" terminology in rule files and "Common Pitfalls" in user-facing tutorial content.

**Structure:**
```markdown

## Common Anti-Patterns in [Topic]

Understanding what NOT to do is as important as knowing best practices:

**Anti-Pattern 1: [Descriptive Name]**
- Why wrong: [Explanation of the problem]
- Correct: [What to do instead]

**Anti-Pattern 2: [Descriptive Name]**
- Why wrong: [Explanation]
- Correct: [Correct approach]

**Anti-Pattern 3: [Descriptive Name]**
- Why wrong: [Explanation]
- Correct: [Correct approach]

This notebook avoids all these pitfalls through careful design!
```

**Best Practices:**
- **Requirement:** 3-5 pitfalls per major topic
- **Requirement:** Always pair wrong with correct
- **Always:** Explain WHY it's wrong, not just WHAT is wrong
- **Always:** Show concrete impact (performance, cost, accuracy)
- **Consider:** Reference where in notebook the correct pattern is demonstrated

**Example:** See Anti-Pattern 2 above for a complete pitfall teaching example with SMOTE/accuracy contrast.

## Checkpoint Validations

> For the full checkpoint validation pattern with code templates, best practices, and actionable error message patterns, see **109e-snowflake-notebook-checkpoints.md**.

**Key requirements:** Place checkpoints between major sections (3-7 checks per checkpoint). Always provide actionable error messages referencing which step to re-run.

## Teaching Point Callouts

> For the full teaching point callout pattern with structure templates, best practices, and examples, see **109e-snowflake-notebook-checkpoints.md**.

**Key requirements:** Use [NOTE] callout prefix. Place BEFORE the implementation (context before code). Explain business rationale, not just technical details.

## Progressive Complexity Management

**Purpose:** Gradually increase complexity, building on foundational concepts before introducing advanced topics.

**Pattern:**
1. **Simple Example:** Minimal viable implementation
2. **Real-World Context:** Why simple example isn't sufficient
3. **Production Pattern:** Complete implementation with error handling
4. **Advanced Optimization:** Performance/cost improvements

**Best Practices:**
- **Requirement:** Start with simplest working example
- **Always:** Explain what each layer of complexity adds
- **Always:** Mark optional advanced sections clearly
- **Consider:** Provide "skip to advanced" shortcuts for experienced learners
- **Consider:** Use configuration variables to toggle complexity (quick_demo vs production)

**Example Structure:**
```markdown

## Step 1 - Basic Implementation (Simple)
[Minimal code that works]

## Step 2 - Production Considerations (Real-World)
[Add error handling, validation, logging]

## Step 3 - Performance Optimization (Advanced - Optional)
[Caching, parallelization, cost optimization]
```

## Tutorial Versioning

When Snowflake APIs or features change, update tutorials promptly:
- Add a version stamp cell at the top: `Last verified: YYYY-MM-DD, Snowflake version: X.Y`
- Use a changelog markdown cell to document significant updates
- Mark deprecated patterns with `[DEPRECATED]` prefix and link to the replacement approach
- Re-run all checkpoint validation cells after updates to confirm tutorials still pass

## Two-Approach Clarification Pattern

> For the full two-approach clarification pattern with templates, best practices, and a real-world Feature Store example, see **109f-snowflake-notebook-two-approach-pattern.md**.

**When to use:** When a tutorial demonstrates a feature (e.g., Feature Store) but uses a simplified approach for learning purposes. Always explain BOTH approaches as valid, clarify which the notebook uses, and provide production migration guidance.
