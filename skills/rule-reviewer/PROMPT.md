# Agent-Centric Rule Review Prompt (Template)

```markdown
## Rule Review Request

**Target File:** [path/to/rule.md]
**Review Date:** [YYYY-MM-DD]
**Review Mode:** [FULL | FOCUSED | STALENESS]

**Review Objective:** Evaluate this rule file for use by
**non-human AI agents** as an **instruction set**, not a reference document.

### Design Priority Hierarchy (Governing Principle)

All rules target **autonomous AI agents**, not human developers. Scoring must reflect this priority order:

**Priority 1: Agent Understanding and Execution Reliability (CRITICAL)**
- Instructions must be unambiguous and deterministic
- All conditionals must have explicit branches (if X, then Y; else Z)
- All undefined thresholds must be quantified (e.g., "large table" becomes ">1M rows")
- No visual formatting agents cannot interpret (ASCII tables, diagrams, arrow characters)
- Use imperative voice for all instructions

**Priority 2: Token and Context Window Efficiency (HIGH)**
- Minimize tokens without sacrificing Priority 1 clarity
- Use structured lists over prose paragraphs
- Front-load critical information in each section
- Reference other rules instead of duplicating content

**Priority 3: Human Readability (TERTIARY)**
- Maintain logical organization for human reviewers
- Does NOT affect scoring; noted in recommendations only

**Trade-off Rule:** When priorities conflict, Priority 1 wins. More tokens for explicit error handling is acceptable. Repeated key terms for clarity is acceptable.

### Dimension Point Allocation

Points are allocated based on criticality for autonomous agent execution:

**Critical Dimensions (50 points total):**
- **Actionability:** 25 points - Agent must follow instructions without judgment
- **Completeness:** 25 points - Missing paths cause agent failure

**Important Dimensions (30 points total):**
- **Consistency:** 15 points - Conflicting guidance causes errors
- **Parsability:** 15 points - Agent must extract structured data

**Standard Dimensions (20 points total):**
- **Token Efficiency:** 10 points - Affects context budget, not correctness
- **Staleness:** 10 points - Affects accuracy over time

**Scoring formula:**
- Actionability: X/5 × 5 = Y/25
- Completeness: X/5 × 5 = Y/25
- Consistency: X/5 × 3 = Y/15
- Parsability: X/5 × 3 = Y/15
- Token Efficiency: X/5 × 2 = Y/10
- Staleness: X/5 × 2 = Y/10
- **Total: Z/100**

---

### Agent Execution Test (REQUIRED - First Gate)

Before scoring any dimension, answer this question:

**"Can an autonomous agent execute this rule end-to-end without asking for clarification or making judgment calls?"**

- If YES: Proceed with dimension scoring
- If NO: Document blocking issues, then proceed with scoring (issues will reduce scores)

**Blocking Issue Categories (count each):**
1. **Undefined thresholds** - Terms requiring agent judgment (e.g., "large", "critical", "appropriate")
2. **Missing branches** - Conditionals without explicit else/default
3. **Ambiguous actions** - Instructions that could be interpreted multiple ways
4. **Visual formatting** - ASCII tables, arrow characters (`→`), decision trees, Mermaid diagrams

**Gate Impact:**
- If blocking issues ≥10: Maximum score = 60/100 (automatic NEEDS_REFINEMENT)
- If blocking issues ≥20: Maximum score = 40/100 (automatic NOT_EXECUTABLE)

---

### Priority Compliance Check (Required - Before Scoring)

Before scoring dimensions, verify the rule follows the design priority hierarchy:

**Priority 1 Compliance (Agent Understanding) - CRITICAL:**
- [ ] No ASCII tables in content (use structured lists)
- [ ] No arrow characters (`→`) outside code blocks
- [ ] No ASCII decision trees (`├─`, `└─`, `│`)
- [ ] No Mermaid diagrams or ASCII art
- [ ] All undefined thresholds quantified (see Threshold Audit below)
- [ ] All conditionals have explicit branches (if X, then Y; else Z)
- [ ] Instructions use imperative voice (commands, not passive)

**Priority 2 Compliance (Token Efficiency) - HIGH:**
- [ ] TokenBudget within ±15% of actual
- [ ] No duplicate content (references used where appropriate)
- [ ] Critical information front-loaded in sections
- [ ] Lists preferred over prose paragraphs

**Scoring Impact:**
- Priority 1 violations: Reduce Actionability and Parsability scores
- 3-5 Priority 1 violations: Maximum Actionability = 3/5 (15/25)
- 6+ Priority 1 violations: Maximum overall score = 60/100 (NEEDS_REFINEMENT cap)
- Priority 2 violations: Reduce Token Efficiency score only (do NOT reduce Priority 1 scores)

---

### Review Criteria

Analyze the rule against these criteria, scoring each 1-5 (5 = excellent):

#### 1. Actionability (Can an agent follow this?) — 25 points

**Priority 1 Alignment:** This dimension directly measures Priority 1 compliance.
Rules must pass the Priority Compliance Check above to score ≥4/5.
- Are instructions unambiguous with no room for interpretation?
- Does every conditional have explicit branches (if X, then Y; else Z)?
- Are there edge cases that would leave an agent uncertain what to do?
- **Are all thresholds quantified?** (e.g., "large table" must specify ">1M rows",
  "high change rate" must specify ">30%")
- **Are undefined thresholds eliminated?** Use the **Threshold Audit table** (mandatory)
  to systematically identify and count undefined thresholds.

**Scoring Scale:**
- **5/5:** 0-1 undefined thresholds; all conditionals have explicit branches; agent executes without judgment.
- **4/5:** 2-3 undefined thresholds; 95%+ instructions explicit; minor inference needed.
- **3/5:** 4-5 undefined thresholds; major instructions clear but some require judgment.
- **2/5:** 6-10 undefined thresholds; significant interpretation required.
- **1/5:** >10 undefined thresholds; rule reads as guidance, not instructions.

**Quantifiable Metrics (Critical Dimension):**
- Count undefined thresholds (via Threshold Audit table)
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

```markdown
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
```

### Agent Perspective Checklist (REQUIRED)

Answer each question explicitly in your assessment:

- [ ] **Agent execution test:** Can an autonomous agent execute this rule end-to-end
  without asking for clarification? (Yes/No with explanation)
- [ ] **Undefined threshold count:** Count all terms requiring agent judgment (e.g., "prefer,"
  "consider," "when appropriate," "as needed", "large", "critical")
- [ ] **Missing branch count:** Count conditionals without explicit else/default
- [ ] **Example-mandate alignment:** Do all code examples comply with the rule's
  own requirements? (Yes/No, list violations)
- [ ] **Failure coverage:** What percentage of examples show success patterns vs.
  failure/recovery paths? (e.g., "4 success, 0 failure")
- [ ] **Threshold audit:** List all undefined thresholds found in the Threshold Audit table

### Priority Compliance Summary (REQUIRED)

Include this summary in every review to track priority violations:

```markdown
**Priority Compliance Summary:**

**Priority 1 (Agent Understanding) - CRITICAL:**
- Undefined thresholds found: [N]
- Missing conditional branches: [N]
- Ambiguous phrases: [N]
- Visual formatting issues: [N] (ASCII tables, arrows, diagrams)
- Passive voice instructions: [N]
- **Total Priority 1 violations:** [N]
- **Score cap applied:** [Yes/No - state cap if ≥6 violations]

**Priority 2 (Token Efficiency) - HIGH:**
- TokenBudget variance: [N%] (target: ±15%)
- Duplicate content sections: [N]
- Buried critical information: [N]
- **Total Priority 2 violations:** [N]

**Priority 3 (Human Readability) - TERTIARY:**
- [Notes for maintainers - does NOT affect scoring]
```

**Scoring adjustments:**
- 3-5 Priority 1 violations: Cap Actionability at 15/25 (3/5)
- 6+ Priority 1 violations: Cap overall score at 60/100 (NEEDS_REFINEMENT)
- Priority 2 violations: Reduce Token Efficiency only; do NOT reduce Priority 1 scores

### Mandatory Verification Tables (Required for Scoring Justification)

Include these tables in your assessment to support your scores. These ensure systematic
analysis and enable cross-model comparison:

#### Threshold Audit (Required for Actionability scoring)

Scan the rule for undefined thresholds (terms requiring agent judgment). Create this list:

```markdown
**Undefined Thresholds Found:**

- **"critical query"** (line 269) - Undefined. Proposed fix: ">30s execution OR >100GB scan OR >100 calls/day"
- **"large table"** (line 340) - Undefined. Proposed fix: ">10M rows OR >1GB"
- **"high change rate"** (line 412) - Undefined. Proposed fix: ">30% delta between runs"

**Total undefined thresholds:** [N]
```

**Terms to scan for (non-exhaustive):**

- Size/scale: "large", "small", "significant", "excessive", "deep"
- Importance: "critical", "important", "high", "low"
- Judgment: "prefer", "consider", "when appropriate", "as needed", "if necessary"
- Quality: "complex", "simple", "reasonable", "sufficient", "advanced"
- Domain-specific: Any term requiring context to evaluate (e.g., "mutable", "production-ready")

**Scoring impact:**
- 0-1 undefined thresholds: 5/5 eligible
- 2-3 undefined thresholds: 4/5 maximum
- 4-5 undefined thresholds: 3/5 maximum
- 6-10 undefined thresholds: 2/5 maximum
- >10 undefined thresholds: 1/5 maximum

#### Token Budget Verification (Required for Token Efficiency scoring)

Calculate actual token count and compare to declared budget:

```markdown
**TokenBudget Verification:**
- Declared TokenBudget: ~[X] tokens
- Word count: [Y] words (if available)
- Calculated tokens: [Y × 1.3 = Z] (rough estimate)
- Variance: [(Z-X)/X × 100 = N%]
- Within ±15%? [Yes/No]
- Assessment: [Accurate / Underestimated / Overestimated]
```

If verification tools unavailable, note limitation but review for obvious redundancy
(repeated sections, excessive prose, duplicated examples).

**Scoring impact:** Variance >15% OR significant redundancy = score ≤3/5.

#### Example-Mandate Alignment (Required for Consistency scoring)

For each code example in the rule, verify compliance with the rule's own requirements:

```markdown
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
```

**Scoring impact:** Each example-mandate violation reduces Consistency score. Major
violations (contradicting core mandates) = score ≤2/5.

---

## Scoring Impact Rules (Algorithmic Overrides)

These rules override subjective assessment:

### Actionability (25 points)

**Undefined Threshold Impact:**
- >10 undefined thresholds: Maximum 1/5 (5/25 points)
- 6-10 undefined thresholds: Maximum 2/5 (10/25 points)
- 4-5 undefined thresholds: Maximum 3/5 (15/25 points)
- 2-3 undefined thresholds: Maximum 4/5 (20/25 points)
- 0-1 undefined thresholds: Eligible for 5/5 (25/25 points)

### Completeness (25 points)

**Error Handling Coverage Impact:**
- No error handling: Maximum 1/5 (5/25 points)
- Happy path only: Maximum 2/5 (10/25 points)
- Partial error handling: Maximum 3/5 (15/25 points)
- Most paths covered: Maximum 4/5 (20/25 points)
- All paths + recovery: Eligible for 5/5 (25/25 points)

### Consistency (15 points)

**Example-Mandate Violation Impact:**
- Major example-mandate violations: Maximum 1/5 (3/15 points)
- 3+ example violations: Maximum 2/5 (6/15 points)
- 2 example violations: Maximum 3/5 (9/15 points)
- 1 example violation: Maximum 4/5 (12/15 points)
- No violations: Eligible for 5/5 (15/15 points)

### Parsability (15 points)

**Structure and Metadata Impact:**
- Unstructured, no metadata: Maximum 1/5 (3/15 points)
- Missing required metadata: Maximum 2/5 (6/15 points)
- Partial metadata, some format issues: Maximum 3/5 (9/15 points)
- Minor format issues: Maximum 4/5 (12/15 points)
- Complete and well-formatted: Eligible for 5/5 (15/15 points)

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
```
