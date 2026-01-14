# Risk Awareness Rubric (5 points)

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 1
**Points:** Raw × (1/2) = Raw × 0.5

## Scoring Criteria

### 10/10 (5 points): Perfect
- 4/4 risk categories addressed
- All risks have probability + impact
- Mitigation strategies for all risks
- Rollback procedures documented (4/4 elements)
- Contingency plans for critical risks

### 9/10 (4.5 points): Near-Perfect
- 4/4 risk categories addressed
- All risks have probability + impact
- Mitigation for all risks
- Rollback documented (4/4 elements)

### 8/10 (4 points): Excellent
- 4/4 risk categories addressed
- Most risks have probability + impact
- Mitigation for 95%+ risks
- Rollback documented (3-4/4 elements)

### 7/10 (3.5 points): Good
- 3-4/4 risk categories addressed
- Most risks have probability + impact
- Mitigation for 90%+ risks
- Basic rollback present (3/4 elements)

### 6/10 (3 points): Acceptable
- 3/4 risk categories addressed
- Most risks have probability + impact
- Mitigation for most risks (80%+)
- Basic rollback present (2-3/4 elements)

### 5/10 (2.5 points): Borderline
- 2-3/4 risk categories addressed
- Some risks assessed
- Some mitigations defined (60-79%)
- Limited rollback (2/4 elements)

### 4/10 (2 points): Needs Work
- 2/4 risk categories addressed
- Some risks assessed
- Some mitigations defined (50-69%)
- Limited rollback (1-2/4 elements)

### 3/10 (1.5 points): Poor
- 1-2/4 risk categories addressed
- Few risks assessed
- Few mitigations (40-59%)
- No rollback (1/4 elements)

### 2/10 (1 point): Very Poor
- 1/4 risk categories addressed
- Few risks assessed
- Few mitigations (30-49%)
- No rollback (0-1/4 elements)

### 1/10 (0.5 points): Inadequate
- 0-1/4 risk categories addressed
- No risk assessment
- No mitigations (<30%)
- No rollback

### 0/10 (0 points): No Risk Awareness
- 0/4 risk categories addressed
- No risk assessment
- No mitigations
- No rollback

## Counting Definitions

### Risk Categories

**Four categories (count 0-4):**

**Risk Category Checklist:**
- 1. Technical risks: Present? Risk count?
- 2. Operational risks: Present? Risk count?
- 3. Data risks: Present? Risk count?
- 4. Integration risks: Present? Risk count?

**Scoring by categories:**
- 4/4 categories: Full credit
- 3/4 categories: 4/5 maximum
- 2/4 categories: 3/5 maximum
- 1/4 categories: 2/5 maximum
- 0/4 categories: 1/5 maximum

### Risk Assessment Completeness

**For each risk, check:**

**Risk Assessment Checklist:**
- Probability rating: Present?
- Impact rating: Present?
- Mitigation strategy: Present?

**Probability levels:**
- High: >50% likelihood
- Medium: 10-50% likelihood
- Low: <10% likelihood

**Impact levels:**
- CRITICAL: System down, data loss
- HIGH: Major feature broken
- MEDIUM: Degraded performance
- LOW: Minor inconvenience

### Mitigation Coverage

**Count risks with explicit mitigation steps:**

```
Mitigation coverage % = (risks with mitigation / total risks) × 100
```

**Scoring:**
- 90-100% coverage: Full credit
- 70-89% coverage: -0.5 points
- 50-69% coverage: -1 point
- <50% coverage: -2 points

### Rollback Procedures

**Required elements:**

**Rollback Element Checklist:**
- Rollback trigger defined: Present?
- Rollback steps documented: Present?
- Rollback verification: Present?
- Time estimate: Present?

**Scoring:**
- Complete (4/4): Full credit
- Partial (2-3/4): -0.5 points
- Minimal (1/4): -1 point
- Missing (0/4): -2 points (CRITICAL)

## Score Decision Matrix

**Score Tier Criteria:**
- **10/10 (5 pts):** 4/4 categories, complete assessment, 100% mitigation, complete rollback (4/4)
- **9/10 (4.5 pts):** 4/4 categories, complete assessment, 100% mitigation, complete rollback (4/4)
- **8/10 (4 pts):** 4/4 categories, mostly assessed, 95%+ mitigation, rollback (3-4/4)
- **7/10 (3.5 pts):** 3-4/4 categories, mostly assessed, 90%+ mitigation, rollback (3/4)
- **6/10 (3 pts):** 3/4 categories, most assessed, 80%+ mitigation, rollback (2-3/4)
- **5/10 (2.5 pts):** 2-3/4 categories, some assessed, 60-79% mitigation, limited rollback (2/4)
- **4/10 (2 pts):** 2/4 categories, some assessed, 50-69% mitigation, limited rollback (1-2/4)
- **3/10 (1.5 pts):** 1-2/4 categories, few assessed, 40-59% mitigation, no rollback (1/4)
- **2/10 (1 pt):** 1/4 categories, few assessed, 30-49% mitigation, no rollback (0-1/4)
- **1/10 (0.5 pts):** 0-1/4 categories, none assessed, <30% mitigation, no rollback
- **0/10 (0 pts):** 0/4 categories, none assessed, no mitigation, no rollback

**Critical gate:** If rollback missing for high-impact changes, cap at 4/10

## Risk Categories Detail

### 1. Technical Risks

**Common technical risks:**
- Build/compilation failures
- Test failures
- Performance degradation
- Memory leaks
- Resource exhaustion
- Configuration errors

**Example:**
```markdown
### Risk: Database migration fails
Probability: Medium (10-50%)
Impact: HIGH (production downtime)

Mitigation:
1. Test on staging with identical data
2. Create backup before migration
3. Use transactional DDL
4. Set statement timeout to 30s

Rollback:
If migration fails:
1. Stop application
2. Restore from backup
3. Verify data integrity
4. Restart application
```

### 2. Operational Risks

**Common operational risks:**
- Deployment outside business hours
- Wrong environment deployment
- Missing approvals
- Insufficient monitoring
- Documentation gaps

**Example:**
```markdown
### Risk: Deployment outside business hours
Probability: Low (<10%)
Impact: HIGH (no support available)

Mitigation:
1. CI blocks deploys outside 9AM-5PM
2. Override requires manager approval
3. On-call auto-paged for after-hours
```

### 3. Data Risks

**Common data risks:**
- Data loss during migration
- Data corruption
- Privacy/security exposure
- Backup failures
- Inconsistent state

**Example:**
```markdown
### Risk: Data loss during migration
Probability: Low (<10%)
Impact: CRITICAL (irrecoverable)

Mitigation:
1. Full backup before migration
2. Incremental backups hourly during migration
3. Data validation after (row counts, checksums)
4. Keep old system read-only for 7 days

Rollback:
1. Stop accepting writes
2. Restore from backup
3. Replay write logs if available
```

### 4. Integration Risks

**Common integration risks:**
- Third-party API downtime
- API rate limiting
- Authentication failures
- Network connectivity
- Version incompatibilities

**Example:**
```markdown
### Risk: Payment API downtime
Probability: Low (99.9% SLA)
Impact: HIGH (no purchases)

Mitigation:
1. Circuit breaker after 3 timeouts
2. Queue payments for retry (24h max)
3. Fallback to backup provider
4. Monitor API health before peak

Contingency:
If down >1 hour:
1. Enable maintenance mode
2. Queue all purchases
3. Process when API returns
4. Notify customers via email
```

## Risk Assessment Table

Use during review:

**Risk Assessment Inventory (example):**
- DB migration (Technical): Probability Medium, Impact HIGH, Mitigation Yes, Rollback Yes
- Memory leak (Technical): Probability Low, Impact Medium, Mitigation Yes, Rollback Yes
- API timeout (Integration): Probability High, Impact LOW, Mitigation No, Rollback No
- Data loss (Data): Probability Low, Impact CRITICAL, Mitigation Yes, Rollback Yes

**Missing:** API timeout mitigation

## Rollback Requirements

### Complete Rollback (Good)

```markdown
## Rollback Procedure

**Trigger:** Any of:
- Error rate >1% for 5 minutes
- P95 latency >1000ms for 5 minutes
- Manual decision (critical bug)

**Steps:**
1. Execute: kubectl rollout undo deployment/app
2. Wait: 2 minutes for pods
3. Verify: curl /health returns 200
4. Verify: Error rate <0.1%
5. Verify: P95 latency <500ms

**Time estimate:** 5 minutes

**If rollback fails:**
1. Scale to 0, restore backup (15 min)
2. Escalate to on-call manager
3. Page database team if DB issues
```

### Missing Rollback (Bad)

```markdown
## Deployment

1. Run deploy script
2. Verify health check
(No rollback mentioned)
```

## Worked Example

**Target:** Feature release plan

### Step 1: Identify Risk Categories

**Category Assessment:**
- Technical: Yes (2 risks)
- Operational: No (0 risks)
- Data: Yes (1 risk)
- Integration: No (0 risks)

**Count:** 2/4 categories

### Step 2: Assess Risk Documentation

**Risk Documentation Assessment:**
- Build failure: Probability Yes (Medium), Impact Yes (HIGH), Mitigation Yes
- Perf regression: Probability No, Impact No, Mitigation Partial
- Data corruption: Probability Yes (Low), Impact Yes (CRITICAL), Mitigation Yes

**Assessment coverage:** 2/3 complete

### Step 3: Calculate Mitigation Coverage

- Risks with mitigation: 2
- Risks with partial: 1
- Total risks: 3

**Coverage:** 2.5/3 = 83%

### Step 4: Check Rollback

**Rollback Element Assessment:**
- Trigger: Yes
- Steps: Yes
- Verification: No
- Time estimate: No

**Quality:** Partial (2/4)

### Step 5: Calculate Score

**Component Assessment:**
- Categories: 2/4 = 3/5 baseline
- Assessment: Incomplete = -0.5 points
- Mitigation: 83% = OK
- Rollback: 2/4 = -0.5 points

**Total deductions:** -1 point
**Final:** 5/10 - 1 = 4/10 (2 points)

### Step 6: Document in Review

```markdown
## Risk Awareness: 4/10 (2 points)

**Categories addressed:** 2/4
- [YES] Technical risks (build, performance)
- [NO] Operational risks (missing)
- [YES] Data risks (corruption)
- [NO] Integration risks (missing)

**Risk assessment:** Incomplete
- Build failure: Complete (prob, impact, mitigation)
- Perf regression: Missing probability/impact
- Data corruption: Complete

**Mitigation coverage:** 83%

**Rollback:** Partial (2/4 elements)
- [YES] Trigger, steps
- [NO] Verification, time estimate

**Priority fixes:**
1. Add operational risks (deployment timing, approvals)
2. Add integration risks (external APIs)
3. Complete performance regression assessment
4. Add rollback verification and time estimate
```

## Risk Awareness Checklist

During review, verify:

- [ ] Technical risks identified
- [ ] Operational risks identified
- [ ] Data risks identified
- [ ] Integration risks identified
- [ ] Each risk has probability assessment
- [ ] Each risk has impact assessment
- [ ] Mitigation strategies defined
- [ ] Rollback procedures documented
- [ ] Rollback triggers specified
- [ ] Time estimates for rollback
- [ ] Monitoring/alerting for risks
- [ ] Contingency plans for critical risks

## Inter-Run Consistency Target

**Expected variance:** ±1 category

**Verification:**
- Use 4-category checklist
- Count risks with complete assessment
- Use rollback element checklist

**If variance exceeds threshold:**
- Re-verify using category definitions
- Apply assessment completeness strictly
