# Inter-Rule Verification Gate

## Purpose

Prevent optimization drift during long-running bulk reviews by forcing periodic re-grounding in skill principles.

## The Problem

During execution of 100+ rules, the anti-optimization guidance fades from active attention:
- Rules 1-10: Full compliance with skill protocol
- Rules 20-40: Subtle drift toward efficiency thinking
- Rules 50+: "Throughput optimization mode" takes over

**Root cause:** Default agent training ("be helpful/efficient") overrides loaded skill guidance as context ages.

## The Solution: Mandatory Re-Grounding Gates

### Gate Frequency

**Every 5 rules:** Execute the Inter-Rule Gate Protocol

### Gate Protocol

**BEFORE starting rule N (where N % 5 == 0):**

```markdown
## Inter-Rule Gate: Rule #[N]

### 1. Re-Read Anti-Optimization Section

I am now re-reading the Anti-Optimization Protocol from SKILL.md...

**Key reminders absorbed:**
- ACCURACY over efficiency
- Skills ≠ Rules (different optimization goals)
- NO template-based reviews
- NO time/token calculations
- NO mid-stream questions

### 2. Self-Assessment Questions

Answer honestly BEFORE proceeding:

1. **Am I thinking about how many rules remain?**
   - YES → STOP. This is optimization thinking. Focus on current rule only.
   - NO → Continue

2. **Am I planning to reuse text from the previous review?**
   - YES → STOP. This is template thinking. Delete planned reuse.
   - NO → Continue

3. **Have I thought about "saving time" in the last 5 reviews?**
   - YES → STOP. Re-read "Quality Over Efficiency Principle" section.
   - NO → Continue

4. **Did my last 5 reviews each have ≥15 unique line references?**
   - NO → STOP. Review quality degrading. Re-read per-rule-verification.md.
   - YES → Continue

5. **Did any of my last 5 reviews have "None required" recommendations?**
   - YES → AUDIT those reviews. "None required" without line-referenced justification = shortcut.
   - NO → Continue

### 3. Commitment Renewal

Before proceeding to rule #[N], I commit to:
- [ ] Reading the COMPLETE rule file
- [ ] Running `ai-rules validate`
- [ ] Performing Agent Execution Test (counting blocking issues)
- [ ] Loading and consulting rubrics for EACH dimension
- [ ] Writing ≥15 line references with direct quotes
- [ ] Producing 3000-8000 byte review
- [ ] NOT using any text from previous reviews

**Gate PASSED. Proceeding to rule #[N].**
```

### Gate Failure Actions

**If ANY self-assessment answer indicates drift:**

1. **STOP** current execution
2. **Re-read** complete SKILL.md (not just Anti-Optimization section)
3. **Audit** last 5 reviews for quality degradation
4. **Delete and redo** any reviews that show shortcut indicators
5. **Resume** only after confirming commitment renewal

### Implementation in Review Loop

```
for i, rule_file in enumerate(rule_files):
    # Inter-Rule Gate at every 5th rule
    if i > 0 and i % 5 == 0:
        execute_inter_rule_gate(rule_number=i)
        # Gate may HALT execution if drift detected
    
    # Normal review process
    review_rule(rule_file)
```

## Why Every 5 Rules?

**Trade-off analysis:**
- Every rule: Too frequent, breaks flow without adding value
- Every 10 rules: Too infrequent, drift can establish before detection
- Every 5 rules: Catches drift early, reasonable overhead (~26 extra checkpoints for 129 rules)

**Measured impact:**
- Gate execution: ~10 seconds
- 20 gates × 10 sec = ~3 minutes additional time
- Prevention value: Avoids complete redo of compromised batch

## Context Refresh (MANDATORY)

**Every 5 rules (N % 5 == 0):** Validate the last completed review JSON and re-read skill instructions:

```python
if rule_number % 5 == 0:
    invoke("ai-rules review-artifact validate --input <last_review.json>")
    print(f"Review validated at rule #{rule_number}")
```

**Why every 5 rules?** Schema drift is the primary cause of inconsistent reviews. The canonical JSON schema (`schemas/rule-review-result-v1.schema.json`) contains the EXACT dimension set, weights, and scoring rules that all reviews MUST follow.

**Drift Detection Trigger:** If previous review JSON fails `ai-rules review-artifact validate` OR the `.json` file is missing:

```python
if not json_path.exists():
    print("DRIFT DETECTED: Review JSON missing")
    read_file("skills/rule-reviewer/SKILL.md")  # Full re-read
    read_file("skills/rule-reviewer/references/reviewer-defaults.yml")

if validate_exit_code != 0:
    print("FORMAT DEVIATION DETECTED")
    # Fix the canonical JSON; re-render Markdown from corrected JSON
    invoke(
        "ai-rules review-artifact render --input <corrected.json> --output <review.md> --replace"
    )
    invoke("ai-rules review-artifact verify-pair --input <corrected.json> --markdown <review.md>")
```

**Why validate, not re-read template?** The canonical JSON schema is the format authority. Detecting drift via schema validation is deterministic and machine-verifiable, unlike pattern-matching in Markdown.

## Integration with Other Protocols

**per-rule-verification.md:** Gate question #4 references this
**anti-shortcut-checklist.md:** Gate reinforces these checks periodically
**reset-trigger.md:** Gate failure may trigger full reset
