# Actionability Rubric (25 points)

## Scoring Criteria

### 5/5 (25 points): Excellent
- Zero undefined thresholds
- All conditionals have explicit branches (if X then Y; else Z)
- All actions use imperative voice
- Quantified examples for all ambiguous terms
- No subjective language without quantification

**Example:**
- ✅ "Large table: >10M rows OR >5GB OR >1000 updates/hour"
- ✅ "If timeout occurs: retry 3 times; else report error"
- ✅ "Run: `uvx ruff check .` (no optional flags)"

### 4/5 (20 points): Good
- 1-3 undefined thresholds
- Most conditionals have explicit branches (1-2 missing else clauses)
- Mostly imperative voice (90%+)
- Some quantification present but incomplete

### 3/5 (15 points): Acceptable
- 4-6 undefined thresholds
- Some conditionals incomplete (3-5 missing branches)
- Mixed imperative/passive voice (60-90% imperative)
- Minimal quantification

### 2/5 (10 points): Needs Work
- 7-10 undefined thresholds
- Many conditionals incomplete (>5 missing branches)
- Frequent passive or conditional voice
- Subjective language common

### 1/5 (5 points): Poor
- >10 undefined thresholds
- Most conditionals incomplete
- Mostly subjective, vague language
- Agent cannot execute without judgment calls

## Common Undefined Thresholds

Search for these patterns:

**Size/Volume:**
- "large", "small", "big", "huge", "tiny"
- "many", "few", "several", "multiple"
- "high volume", "low volume"

**Complexity:**
- "complex", "simple", "complicated", "straightforward"
- "difficult", "easy", "trivial"

**Quality:**
- "significant", "minor", "major"
- "important", "critical", "essential"
- "appropriate", "suitable", "reasonable"

**Performance:**
- "fast", "slow", "quick"
- "efficient", "inefficient"
- "responsive", "laggy"

## Quantification Examples

| Vague Term | Quantified Replacement |
|------------|------------------------|
| "large file" | ">10MB OR >10000 lines" |
| "significant changes" | ">100 lines modified OR >10 files changed" |
| "complex function" | ">50 lines OR >5 branches OR cyclomatic complexity >10" |
| "many requests" | ">1000 requests/minute" |
| "high error rate" | ">5% of requests fail OR >100 errors/hour" |
| "slow query" | ">5 seconds execution time" |
| "frequent updates" | ">10 updates/day OR >100 updates/month" |

## Conditional Branch Completeness

**Incomplete (BAD):**
```python
if error_occurs:
    retry()
# What if error doesn't occur? Missing else branch!
```

**Complete (GOOD):**
```python
if error_occurs:
    retry()
else:
    continue_processing()
```

**Complete with explicit no-op (GOOD):**
```python
if error_occurs:
    retry()
# If no error: continue with next step (explicit no-op documented)
```

## Imperative Voice Check

**Passive/Conditional (BAD):**
- "The file should be validated"
- "It would be good to check permissions"
- "Consider running tests"

**Imperative (GOOD):**
- "Validate the file"
- "Check permissions"
- "Run tests"

## Scoring Formula

```
Base score = 5/5 (25 points)

For each undefined threshold: -0.5 points (up to -10)
For each missing conditional branch: -0.5 points (up to -5)
For passive voice >10%: -1 point
For ambiguous actions: -0.5 points each (up to -5)

Minimum score: 1/5 (5 points)
```

## Agent Execution Test Integration

If Agent Execution Test finds ≥10 blocking issues:
- Cap Actionability at 2/5 maximum
- Document each blocking issue
- Prioritize undefined thresholds in recommendations
