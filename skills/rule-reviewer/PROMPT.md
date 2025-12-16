# Agent-Centric Rule Review Prompt (Template)

~~~~markdown
## Rule Review Request

**Target File:** [path/to/rule.md]
**Review Date:** [YYYY-MM-DD]
**Review Mode:** [FULL | FOCUSED | STALENESS]

**Review Objective:** Evaluate this rule file for use by
**non-human AI agents** as an **instruction set**, not a reference document.

### Dimension Point Allocation

Points are allocated based on criticality for autonomous agent execution:

| Dimension | Points | Rationale |
|-----------|--------|-----------|
| **Actionability** | 25 | Critical - agent must follow instructions without judgment |
| **Completeness** | 25 | Critical - missing paths cause agent failure |
| Consistency | 15 | Important - conflicting guidance causes errors |
| Parsability | 15 | Important - agent must extract structured data |
| Token Efficiency | 10 | Affects context budget but not correctness |
| Staleness | 10 | Affects accuracy over time |

**Scoring formula:**
- Actionability: X/5 × 5 = Y/25
- Completeness: X/5 × 5 = Y/25
- Consistency: X/5 × 3 = Y/15
- Parsability: X/5 × 3 = Y/15
- Token Efficiency: X/5 × 2 = Y/10
- Staleness: X/5 × 2 = Y/10
- **Total: Z/100**

---

### Review Criteria

Analyze the rule against these criteria, scoring each 1-5 (5 = excellent):

#### 1. Actionability (Can an agent follow this?) — 25 points
- Are instructions unambiguous with no room for interpretation?
- Does every conditional have explicit branches (if X, then Y; else Z)?
- Are there edge cases that would leave an agent uncertain what to do?
- **Are all thresholds quantified?** (e.g., "large table" should specify ">1M rows",
  "high change rate" should specify ">30%")
- **Are subjective terms defined?** Use the **Threshold Audit table** (mandatory)
  to systematically identify undefined terms.

**Scoring Scale:**
- **5/5:** 0-1 undefined terms; all conditionals have explicit branches; agent executes without judgment.
- **4/5:** 2-3 undefined terms; 95%+ instructions explicit; minor inference needed.
- **3/5:** 4-5 undefined terms; major instructions clear but some require judgment.
- **2/5:** 6-10 undefined terms; significant interpretation required.
- **1/5:** >10 undefined terms; rule reads as guidance, not instructions.

**Quantifiable Metrics (Critical Dimension):**
- Count undefined subjective terms (via Threshold Audit table)
- Count conditionals without explicit branches
- Count edge cases without defined behavior

**Calibration Examples:**
- **5/5:** "If table has >1M rows, use COPY INTO; else use INSERT"
- **3/5:** "For large tables, prefer COPY INTO" (undefined "large", implicit else)
- **1/5:** "Consider using appropriate loading method" (requires judgment)

#### 2. Completeness (Are all paths covered?) — 25 points
- What happens when the "happy path" fails?
- Are error conditions and recovery steps explicit?
- Are there implicit assumptions that an agent might not share?

**Scoring Scale:**
- **5/5:** All paths covered; error handling explicit; no implicit assumptions; 0-1 gaps.
- **4/5:** Major paths complete; 2-3 minor gaps (e.g., missing edge case handling).
- **3/5:** Happy path clear; error handling partial; some assumptions unstated.
- **2/5:** Significant gaps; agent would need to infer multiple behaviors.
- **1/5:** Only happy path covered; no error handling; many implicit assumptions.

**Quantifiable Metrics (Critical Dimension):**
- Count of error conditions with explicit recovery steps
- Count of implicit assumptions identified
- Percentage of code paths with defined behavior

**Calibration Examples:**
- **5/5:** "If query fails with timeout: retry 3× with exponential backoff. If still fails: log error, skip record, continue. If >10% failures: halt and report."
- **3/5:** "If query fails, retry" (no retry count, no failure handling)
- **1/5:** "Execute query" (no error handling mentioned)

#### 3. Consistency (Does guidance conflict within the file or with dependencies?) — 15 points
- Do different sections give conflicting advice?
- Are numeric thresholds consistent throughout?
- Does the rule conflict with its declared dependencies?
- **Do code examples comply with the rule's own mandates?** Use the
  **Example-Mandate Alignment Check** (mandatory) to systematically verify all examples
- **Do examples demonstrate patterns the rule requires?** Check for both negative
  compliance (avoiding prohibitions) and positive compliance (demonstrating requirements)

#### 4. Parsability (Can an agent extract structured data?) — 15 points
- Are tables, lists, and code blocks properly formatted?
- Is metadata (TokenBudget, ContextTier, Keywords) machine-readable?
- Are examples clearly delineated from prose?

**Scoring Scale:**
- **5/5:** All structured elements properly formatted; metadata complete; examples clearly marked.
- **4/5:** Minor formatting issues; metadata mostly complete; examples identifiable.
- **3/5:** Some malformed tables/lists; metadata partial; examples mixed with prose.
- **2/5:** Significant formatting problems; missing required metadata; hard to extract data.
- **1/5:** Unstructured prose; no metadata; examples indistinguishable from text.

**Quantifiable Metrics:**
- Count of malformed tables/lists/code blocks
- Metadata completeness (TokenBudget, ContextTier, Keywords, Depends present?)
- Count of examples without clear delimiters

**Calibration Examples:**
- **5/5:** Proper markdown tables, fenced code blocks with language tags, complete metadata header
- **3/5:** Some tables render incorrectly, metadata missing ContextTier
- **1/5:** Plain text with no structure, inline code mixed with prose

#### 5. Token Efficiency (Is the rule appropriately sized?) — 10 points
- **Is the TokenBudget accurate (within ±15% of actual)?** Use the
  **Token Budget Verification** (mandatory) to calculate and compare
- Could sections be split without losing coherence?
- Is there redundant content that could be removed or referenced?
- Look for: repeated concepts, duplicate examples, explanatory prose not needed for
  execution, verbose rationale that could be condensed

**Scoring Scale:**
- **5/5:** TokenBudget within ±10%; no redundancy; appropriately sized for scope.
- **4/5:** TokenBudget within ±15%; minor redundancy; mostly efficient.
- **3/5:** TokenBudget variance 15-25%; some redundant sections; could be condensed.
- **2/5:** TokenBudget variance 25-40%; significant redundancy; should be split.
- **1/5:** TokenBudget variance >40%; excessive redundancy; major restructuring needed.

#### 6. Staleness Detection (Is the rule current?) — 10 points
- Are referenced tools/versions still current? (e.g., Python 3.11 vs 3.13, Ruff vs
  older linters)
- Are API patterns or library interfaces still valid?
- Are best practices still industry-standard or have they evolved?
- Are any deprecated features, functions, or approaches mentioned?
- Do external documentation links still work and point to current versions?

**Scoring Scale:**
- **5/5:** All references current; no deprecated patterns; links valid.
- **4/5:** 1-2 minor version differences; no critical staleness.
- **3/5:** Some outdated references; deprecated patterns mentioned but not blocking.
- **2/5:** Multiple outdated references; deprecated patterns as recommendations.
- **1/5:** Significantly outdated; recommends deprecated approaches as primary.

### Output Format

Provide your assessment in this structure:

~~~markdown
## Rule Review: [rule-name.md]

### Scores
| Criterion | Max | Raw | Points | Notes |
|-----------|-----|-----|--------|-------|
| Actionability | 25 | X/5 | Y/25 | [brief justification] |
| Completeness | 25 | X/5 | Y/25 | [brief justification] |
| Consistency | 15 | X/5 | Y/15 | [brief justification] |
| Parsability | 15 | X/5 | Y/15 | [brief justification] |
| Token Efficiency | 10 | X/5 | Y/10 | [brief justification] |
| Staleness | 10 | X/5 | Y/10 | [brief justification] |

**Overall:** X/100

**Reviewing Model:** [Model name and version that performed this review]

### Overall Score Interpretation

| Score Range | Assessment | Verdict |
|-------------|------------|---------|
| 90-100 | Excellent | EXECUTABLE |
| 80-89 | Good | EXECUTABLE_WITH_REFINEMENTS |
| 60-79 | Needs Work | NEEDS_REFINEMENT |
| 40-59 | Poor | NOT_EXECUTABLE |
| <40 | Inadequate | NOT_EXECUTABLE - Rewrite required |

**Critical dimension overrides:**
- If Actionability ≤2/5 → Verdict = "NEEDS_REFINEMENT" minimum
- If Completeness ≤2/5 → Verdict = "NEEDS_REFINEMENT" minimum
- If 2+ critical dimensions ≤2/5 → Verdict = "NOT_EXECUTABLE"

### Agent Executability Verdict
**[EXECUTABLE | NEEDS_REFINEMENT | NOT_EXECUTABLE]**

[1-2 sentence summary of why this verdict was assigned]

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

## Scoring Impact Rules (Algorithmic Overrides)

These rules override subjective assessment:

### Actionability (25 points)
| Finding | Maximum Score | Max Points |
|---------|---------------|------------|
| >10 undefined terms | 1/5 | 5/25 |
| 6-10 undefined terms | 2/5 | 10/25 |
| 4-5 undefined terms | 3/5 | 15/25 |
| 2-3 undefined terms | 4/5 | 20/25 |
| 0-1 undefined terms | 5/5 | 25/25 |

### Completeness (25 points)
| Finding | Maximum Score | Max Points |
|---------|---------------|------------|
| No error handling | 1/5 | 5/25 |
| Happy path only | 2/5 | 10/25 |
| Partial error handling | 3/5 | 15/25 |
| Most paths covered | 4/5 | 20/25 |
| All paths + recovery | 5/5 | 25/25 |

### Consistency (15 points)
| Finding | Maximum Score | Max Points |
|---------|---------------|------------|
| Major example-mandate violations | 1/5 | 3/15 |
| 3+ example violations | 2/5 | 6/15 |
| 2 example violations | 3/5 | 9/15 |
| 1 example violation | 4/5 | 12/15 |
| No violations | 5/5 | 15/15 |

### Parsability (15 points)
| Finding | Maximum Score | Max Points |
|---------|---------------|------------|
| Unstructured, no metadata | 1/5 | 3/15 |
| Missing required metadata | 2/5 | 6/15 |
| Partial metadata, some format issues | 3/5 | 9/15 |
| Minor format issues | 4/5 | 12/15 |
| Complete and well-formatted | 5/5 | 15/15 |

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
