# Agent-Centric Rule Review Prompt (Template)

~~~~markdown
## Rule Review Request

**Target File:** [path/to/rule.md]
**Review Date:** [YYYY-MM-DD]
**Review Mode:** [FULL | FOCUSED | STALENESS]

**Review Objective:** Evaluate this rule file for use by
**non-human AI agents** as an **instruction set**, not a reference document.

### Review Criteria

Analyze the rule against these criteria, scoring each 1-5 (5 = excellent):

#### 1. Actionability (Can an agent follow this?)
- Are instructions unambiguous with no room for interpretation?
- Does every conditional have explicit branches (if X, then Y; else Z)?
- Are there edge cases that would leave an agent uncertain what to do?
- **Are all thresholds quantified?** (e.g., "large table" should specify ">1M rows",
  "high change rate" should specify ">30%")
- **Are subjective terms defined?** Use the **Threshold Audit table** (mandatory)
  to systematically identify undefined terms.

#### 2. Completeness (Are all paths covered?)
- What happens when the "happy path" fails?
- Are error conditions and recovery steps explicit?
- Are there implicit assumptions that an agent might not share?

#### 3. Consistency (Does guidance conflict within the file or with dependencies?)
- Do different sections give conflicting advice?
- Are numeric thresholds consistent throughout?
- Does the rule conflict with its declared dependencies?
- **Do code examples comply with the rule's own mandates?** Use the
  **Example-Mandate Alignment Check** (mandatory) to systematically verify all examples
- **Do examples demonstrate patterns the rule requires?** Check for both negative
  compliance (avoiding prohibitions) and positive compliance (demonstrating requirements)

#### 4. Parsability (Can an agent extract structured data?)
- Are tables, lists, and code blocks properly formatted?
- Is metadata (TokenBudget, ContextTier, Keywords) machine-readable?
- Are examples clearly delineated from prose?

#### 5. Token Efficiency (Is the rule appropriately sized?)
- **Is the TokenBudget accurate (within ±15% of actual)?** Use the
  **Token Budget Verification** (mandatory) to calculate and compare
- Could sections be split without losing coherence?
- Is there redundant content that could be removed or referenced?
- Look for: repeated concepts, duplicate examples, explanatory prose not needed for
  execution, verbose rationale that could be condensed

#### 6. Staleness Detection (Is the rule current?)
- Are referenced tools/versions still current? (e.g., Python 3.11 vs 3.13, Ruff vs
  older linters)
- Are API patterns or library interfaces still valid?
- Are best practices still industry-standard or have they evolved?
- Are any deprecated features, functions, or approaches mentioned?
- Do external documentation links still work and point to current versions?

### Output Format

Provide your assessment in this structure:

~~~markdown
## Rule Review: [rule-name.md]

### Scores
| Criterion | Score | Notes |
|-----------|-------|-------|
| Actionability | X/5 | [brief justification] |
| Completeness | X/5 | [brief justification] |
| Consistency | X/5 | [brief justification] |
| Parsability | X/5 | [brief justification] |
| Token Efficiency | X/5 | [brief justification] |
| Staleness | X/5 | [brief justification] |

**Overall:** X/30

**Reviewing Model:** [Model name and version that performed this review]

### Critical Issues (Must Fix)
[List issues that would cause agent failure or incorrect behavior]

### Improvements (Should Fix)
[List issues that would improve agent performance]

### Minor Suggestions (Nice to Have)
[List stylistic or optimization suggestions]

### Specific Recommendations
For each issue, provide:
1. **Location:** Line number or section name
2. **Problem:** What's wrong and why it matters for agents
3. **Recommendation:** Specific fix with example if helpful

### Staleness Indicators Found
List any outdated elements detected:
- **Tool Versions:** [e.g., "References Python 3.9, current is 3.13"]
- **Deprecated Patterns:** [e.g., "Uses setup.py, pyproject.toml is now standard"]
- **API Changes:** [e.g., "Snowflake connector API changed in v3.0"]
- **Industry Shifts:** [e.g., "Recommends unittest, pytest is now dominant"]

### Dependency Drift Check
If rule declares dependencies, verify alignment:
- **Depends:** [list from rule metadata]
- **Conflicts Found:** [any guidance that contradicts dependencies]
- **Missing Dependencies:** [rules that should be listed but aren't]
~~~

### Agent Perspective Checklist (REQUIRED)

Answer each question explicitly in your assessment:

- [ ] **Literal execution test:** If an agent followed every instruction literally,
  would it produce correct output? (Yes/No with explanation)
- [ ] **Judgment detection:** List any phrases requiring human judgment (e.g., "prefer,"
  "consider," "when appropriate," "as needed")
- [ ] **Example-mandate alignment:** Do all code examples comply with the rule's
  own requirements? (Yes/No, list violations)
- [ ] **Failure coverage:** What percentage of examples show success patterns vs.
  failure/recovery paths? (e.g., "4 success, 0 failure")
- [ ] **Threshold audit:** List all undefined thresholds found
  (subjective terms without numeric criteria)

### Mandatory Verification Tables (Required for Scoring Justification)

Include these tables in your assessment to support your scores. These ensure systematic
analysis and enable cross-model comparison:

#### Threshold Audit (Required for Actionability scoring)

Scan the rule for subjective terms without quantified criteria. Create this table:

~~~markdown
| Term | Line(s) | Defined? | Issue | Proposed Fix |
|------|---------|----------|-------|--------------|
| critical query | 269 | ❌ | Undefined term | >30s OR >100GB OR >100/day |
| large table | 340 | ❌ | Undefined size | >10M rows OR >1GB |
~~~

**Terms to scan for:**

- "critical," "large," "high," "low," "important,"
- "prefer," "consider," "when appropriate," "significant,"
- "deep," "complex," "reasonable," "sufficient,"
- "excessive," "simple," "advanced"

**Note:** This list is illustrative, not exhaustive.
Include any term that would require agent judgment to evaluate (e.g., domain-specific
terms like "mutable," "incremental," and "production-ready").

**Scoring impact:** Each undefined threshold reduces Actionability score.
More than 5 undefined = score ≤3/5.

#### Token Budget Verification (Required for Token Efficiency scoring)

Calculate actual token count and compare to declared budget:

~~~markdown
**TokenBudget Verification:**
- Declared TokenBudget: ~[X] tokens
- Word count: [Y] words (if available)
- Calculated tokens: [Y × 1.3 = Z] (rough estimate)
- Variance: [(Z-X)/X × 100 = N%]
- Within ±15%? [Yes/No]
- Assessment: [Accurate / Underestimated / Overestimated]
~~~

If verification tools unavailable, note limitation but review for obvious redundancy
(repeated sections, excessive prose, duplicated examples).

**Scoring impact:** Variance >15% OR significant redundancy = score ≤3/5.

#### Example-Mandate Alignment (Required for Consistency scoring)

For each code example in the rule, verify compliance with the rule's own requirements:

~~~markdown
**Example-Mandate Alignment Check:**

Verification steps:
1. ✅/❌ All examples avoid stated prohibitions (e.g., `SELECT *`, `DISTINCT` for
   deduplication)
2. ✅/❌ All examples demonstrate stated requirements (e.g., fully-qualified
   `DB.SCHEMA.TABLE`)
3. ✅/❌ All examples use prescribed patterns (e.g., CTEs, explicit columns)
4. ✅/❌ No examples use documented anti-patterns

**Violations found:**
- Line [X]: [Example uses Y despite rule prohibiting it]
- Line [Z]: [Example doesn't demonstrate required pattern Q]

OR

- None found - all examples comply with rule mandates
~~~

**Scoring impact:** Each example-mandate violation reduces Consistency score. Major
violations (contradicting core mandates) = score ≤2/5.

---

### Output Guidelines

- **Target length (flexible based on rule criticality):**
  - **Concise:** 150-200 lines (specialized rules, focused reviews)
  - **Standard:** 200-350 lines (domain cores, typical FULL mode)
  - **Comprehensive:** 400+ lines (foundation rules - include executive summary,
    priority levels, detailed code fixes)
- **Code examples:** Include fix examples for Critical issues; optional for Minor
  suggestions
- **Effort estimates:** Recommended for Critical and Should Fix items
  (e.g., "~30 min to fix")
- **Line references:** Always include line numbers or section names for issues
- **Prioritization:** If >10 issues found, group by implementation priority

## Review Modes

### FULL Mode (Comprehensive)
Use for new rules or major revisions. Evaluates all 6 criteria with detailed
recommendations.

### FOCUSED Mode (Targeted)
Use when you know specific areas need attention. Specify which criteria to evaluate.

### STALENESS Mode (Periodic Maintenance)
Use for quarterly/annual rule audits. Focuses on criteria 5-6 (Token Efficiency,
Staleness) plus dependency drift.

**For FOCUSED/STALENESS modes:** Skip Mandatory Verification Tables unless specifically
reviewing:
- Actionability (Threshold Audit)
- Consistency (Example-Mandate Alignment)
- Token Efficiency (Token Budget Verification)

### Output File (REQUIRED)

Save your full review output as a Markdown file under `reviews/` using this filename
format:

`reviews/<rule-name>-<model>-<YYYY-MM-DD>.md`

Rules:
- `<rule-name>`: base name of **Target File** with no extension
  (example: `rules/810-project-readme.md` → `810-project-readme`)
- `<model>`: lowercase, hyphenated model identifier
  (example: `claude-sonnet45`, `gpt-52`)
- `<YYYY-MM-DD>`: **Review Date**

Example:
- Target File: `rules/810-project-readme.md`
- Reviewing Model: `Claude Sonnet 4.5`
- Review Date: `2025-12-12`
- Output file: `reviews/810-project-readme-claude-sonnet45-2025-12-12.md`

If you cannot write files in this environment, output the full Markdown content and
include the intended path on the first line exactly as:

`OUTPUT_FILE: reviews/<rule-name>-<model>-<YYYY-MM-DD>.md`
<!-- End of prompt template -->
<!-- EOF -->
~~~~
