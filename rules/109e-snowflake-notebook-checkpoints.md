# Snowflake Notebook Checkpoints and Teaching Points

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:notebook-checkpoint, kw:teaching-point
**Keywords:** checkpoint validation, teaching point callouts, notebook validation gates, progress verification, learning checkpoints, NOTE prefix, tutorial checkpoints
**TokenBudget:** ~2650
**ContextTier:** Low
**Depends:** 109a-snowflake-notebooks-tutorials.md

## Scope

**What This Rule Covers:**
Patterns for implementing checkpoint validation cells and teaching point callouts in educational Snowflake notebooks, including validation gate structure, actionable error messages, and inline explanations of design decisions.

**When to Load This Rule:**
- Adding checkpoint validations between notebook sections
- Creating teaching point callouts explaining "why" decisions were made
- Implementing progress verification in tutorial notebooks
- Designing validation gates that prevent learners from proceeding with errors

## References

### Related Rules
**Closely Related** (consider loading together):
- **109a-snowflake-notebooks-tutorials.md** - Parent rule for tutorial design patterns
- **109-snowflake-notebooks.md** - Core notebook best practices

## Contract

### Inputs and Prerequisites

- Tutorial notebook with major sections defined
- Learning objectives established (see 109a)

### Mandatory

- Checkpoint validation cells between major sections (3-7 checks per checkpoint)
- Teaching point callouts with [NOTE] prefix placed before implementations
- Actionable error messages referencing which step to re-run

### Forbidden

- Checkpoints without actionable error messages
- Teaching points placed after implementation instead of before

### Execution Steps

1. Identify major section transitions in notebook
2. Add checkpoint validation cells between sections
3. Add teaching point callouts before complex implementations
4. Test checkpoint validations catch expected errors

### Output Format

Checkpoint validation cells (Python) and teaching point callouts (Markdown).

### Validation

Verify checkpoints catch common errors and provide actionable fixes. Verify teaching points explain business context.

### Design Principles

- Validate progress before allowing advancement.
- Context before code: explain "why" before showing "how."
- Actionable errors: tell the learner exactly which step to re-run.

### Post-Execution Checklist

- [ ] Checkpoint validation cells between major sections (3-7 checks each)
- [ ] Teaching point callouts ([NOTE] prefix) explaining "why" before implementations
- [ ] Actionable error messages reference specific steps to re-run
- [ ] Progress summary shows what is complete and what is next

**Testing checkpoints:** After creating checkpoints, test with intentionally incorrect state (e.g., empty DataFrame, wrong column names) to verify they catch errors and produce actionable messages. A checkpoint that always passes provides no value.

## Implementation Details

### Checkpoint Validations

**Purpose:** Automated validation gates that verify learner progress and prevent proceeding with errors.

**Structure:**
```markdown

## Checkpoint N - [Name] Complete

Before proceeding to [next section], verify all [previous section] steps succeeded.
```

```python
# Checkpoint [N] Validation
print("=" * 80)
print("[PASS] CHECKPOINT [N]: [NAME]")
print("=" * 80)

checks_passed = []
checks_failed = []

# Check 1: [Description]
if [condition]:
    checks_passed.append("[PASS] [Success message]")
else:
    checks_failed.append("[Failure message] - run Step X.Y")

# Check 2: [Description]
if [condition]:
    checks_passed.append("[PASS] [Success message]")
else:
    checks_failed.append("[Failure message] - run Step X.Y")

# Display results
print("\nValidation Results:")
print("-" * 80)
for check in checks_passed:
    print(check)

if checks_failed:
    print("\nIssues Detected:")
    for check in checks_failed:
        print(check)
    print("\nFix issues above before proceeding to [next section]")
    print("=" * 80)
else:
    print("\nALL CHECKS PASSED - Ready for [next section]!")
    print("=" * 80)
    print("\nNext Steps:")
    print("  - [Description of what comes next]")
```

**SQL-only checkpoint pattern** (for SQL-focused tutorials):
```sql
-- SQL Checkpoint: Verify data loaded correctly
SELECT
  CASE WHEN COUNT(*) > 0 THEN '[PASS] Data loaded'
       ELSE '[FAIL] No data found - rerun Step 2' END AS check_1,
  CASE WHEN COUNT(DISTINCT region) >= 3 THEN '[PASS] All regions present'
       ELSE '[FAIL] Missing regions - check source data' END AS check_2
FROM target_table;
```

**Best Practices:**
- **Requirement:** Place checkpoints between major sections (not every cell)
- **Requirement:** 3-7 validation checks per checkpoint
- **Always:** Check for critical state (data loaded, models trained, features present)
- **Always:** Provide actionable error messages (which step to re-run)
- **Always:** Show progress summary (what's complete, what's next)
- **Consider:** Include diagnostic information (row counts, feature counts, time elapsed)

**Checkpoint frequency:** For short tutorials (10-20 cells): 2-3 checkpoints. For medium tutorials (20-40 cells): 3-5 checkpoints. For long tutorials (40+ cells): 5-7 checkpoints. Place at natural section boundaries, not arbitrarily.

### Teaching Point Callouts

**Purpose:** Inline explanations of WHY decisions were made, providing context and rationale.

**Structure:**
```markdown
### [NOTE] Teaching Point: [Topic]

**[Key Concept/Question]:**
- [Explanation point 1]
- [Explanation point 2]
- [Explanation point 3]

**Why This Matters:**
- [Business or technical impact]
- [Cost/performance/reliability consideration]

**[Comparison/Strategy]:**
1. **Approach A:** [Description and tradeoffs]
2. **Approach B:** [Description and tradeoffs]

**Demo Strategy:** [How this notebook demonstrates the concept]
```

**Best Practices:**
- **Requirement:** Use [NOTE] callout prefix for visual scanning
- **Always:** Place BEFORE the implementation (context before code)
- **Always:** Explain business rationale, not just technical details
- **Consider:** Use tables for comparing approaches
- **Consider:** Reference external documentation for deeper learning

**Example - Good:**
```markdown
### [NOTE] Teaching Point: Why Class Imbalance Matters

**The Real-World Problem:**
- In production datasets, failures are rare (often <5% of samples)
- Standard ML algorithms optimize for overall accuracy
- Result: Model predicts "healthy" for everything, achieving 95% accuracy but 0% recall!

**Why This Fails in Practice:**
- **Business Cost Asymmetry:** Missed failure = $100,000+ in emergency repairs
- **False alarm cost:** $1,000 for planned inspection
- **Cost ratio:** 100:1 (some utilities report 10-50x)

**Two Solutions to Explore:**
1. **Path A (SMOTE):** Create synthetic failure samples to balance training data
2. **Path B (Algorithm-Level):** Use algorithms that internally handle imbalance

**Demo Strategy:** We'll train 4 models (2 from each path) and compare results.
```

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Checkpoint That Only Prints Success**

**Problem:** Developers add checkpoint cells that only print a success message without actually validating state. The cell runs `print("[PASS] Data loaded successfully")` unconditionally, giving learners false confidence. When they hit errors in later sections, they have no idea which earlier step failed because the checkpoint never checked anything.

**Correct Pattern:** Every checkpoint must contain actual validation logic -- query row counts, verify columns exist, check that variables are defined and non-empty. Use `if/else` with `checks_passed` and `checks_failed` lists. A checkpoint with zero conditional checks is not a checkpoint, it's decoration.

```python
# Wrong: Unconditional success message with no actual validation
print("=" * 80)
print("[PASS] CHECKPOINT 1: Data Loading Complete")
print("=" * 80)
print("[PASS] Training data loaded successfully")
print("[PASS] Feature columns created")
print("Ready for model training!")

# Correct: Actual validation logic with actionable failure messages
checks_passed = []
checks_failed = []

if training_df.count() > 0:
    checks_passed.append(f"[PASS] Training data has {training_df.count()} rows")
else:
    checks_failed.append("[FAIL] Training table has 0 rows - re-run Step 2.1 (Data Loading)")

expected_cols = ["FEATURE_1", "FEATURE_2", "LABEL"]
missing = [c for c in expected_cols if c not in training_df.columns]
if not missing:
    checks_passed.append("[PASS] All required feature columns present")
else:
    checks_failed.append(f"[FAIL] Missing columns: {missing} - re-run Step 2.3 (Feature Engineering)")

for msg in checks_passed:
    print(msg)
if checks_failed:
    for msg in checks_failed:
        print(msg)
    print("\nFix issues above before proceeding to Model Training!")
```

**Anti-Pattern 2: Teaching Points Placed After the Code**

**Problem:** A teaching point explaining WHY a design decision was made is placed in a markdown cell after the code cell that implements it. Learners execute the code first, see results they don't understand, then scroll down to find the explanation. This breaks the "context before code" principle and reduces learning retention because learners form incorrect mental models before seeing the rationale.

**Correct Pattern:** Always place teaching point callouts (markdown cells with `[NOTE]` prefix) immediately before the implementation cell they explain. The learner should read the "why" before seeing the "how". Structure notebooks as: Teaching Point (markdown) -> Implementation (code) -> Checkpoint (code).

```markdown
<!-- Wrong: Teaching point AFTER code — learner sees code before context -->
<!-- Cell 5 (code): -->
model = RandomForestClassifier(class_weight="balanced")
model.fit(X_train, y_train)

<!-- Cell 6 (markdown): -->
### [NOTE] Why we use class_weight="balanced"
In imbalanced datasets, the minority class gets overwhelmed...

<!-- Correct: Teaching point BEFORE code — context then implementation -->
<!-- Cell 5 (markdown): -->
### [NOTE] Teaching Point: Why class_weight="balanced"
In imbalanced datasets (e.g., 95% healthy, 5% failure), standard
algorithms optimize for accuracy and ignore the minority class.
`class_weight="balanced"` tells the algorithm to penalize mistakes
on rare classes proportionally to their scarcity.

<!-- Cell 6 (code): -->
model = RandomForestClassifier(class_weight="balanced")
model.fit(X_train, y_train)
```

**Anti-Pattern 3: Non-Actionable Error Messages in Checkpoints**

**Problem:** Checkpoint failure messages say things like `"[FAIL] Data issue detected"` or `"[FAIL] Something went wrong"` without telling the learner which specific step to re-run or what corrective action to take. Learners waste time re-running the entire notebook from scratch instead of fixing the specific failing step.

**Correct Pattern:** Every failure message must reference the specific step to re-run: `"[FAIL] Training table has 0 rows - re-run Step 3.2 (Data Loading)"`. Include the step number, step name, and what the expected state should be. This lets learners surgically fix issues without restarting.

```python
# Wrong: Vague error messages with no guidance
if training_df.count() == 0:
    print("[FAIL] Data issue detected")
if "LABEL" not in training_df.columns:
    print("[FAIL] Something went wrong with features")

# Correct: Actionable messages with step references and expected state
if training_df.count() == 0:
    print("[FAIL] Training table has 0 rows - re-run Step 3.2 (Data Loading)")
    print("       Expected: >1000 rows after joining asset and weather data")
if "LABEL" not in training_df.columns:
    print("[FAIL] LABEL column missing - re-run Step 3.4 (Label Generation)")
    print("       Expected: binary LABEL column (0=healthy, 1=failure)")
```
