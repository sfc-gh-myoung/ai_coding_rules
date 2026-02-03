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

### Risk Category Taxonomy

**Purpose:** Eliminate variance in risk classification (resolves 10/10 vs 7/10 gap).

#### Four Risk Categories (Mandatory Classification)

**1. Technical Risks** - Tool/system failures, technical limitations
- Build/compilation failures
- Test failures
- Performance degradation
- Memory leaks
- Resource exhaustion
- Configuration errors
- Dependency conflicts

**2. Operational Risks** - Process/timing/coordination issues
- Deployment outside business hours
- Wrong environment deployment
- Missing approvals
- Insufficient monitoring
- Documentation gaps
- Team coordination failures
- Scheduling conflicts

**3. Data Risks** - Content loss, corruption, integrity issues
- Data loss during migration
- Data corruption
- Privacy/security exposure
- Backup failures
- Inconsistent state
- **Concurrent modifications** → Data risk (file corruption) ✓
- Schema migration failures

**4. Integration Risks** - External service/API dependencies
- Third-party API downtime
- API rate limiting
- Authentication failures
- Network connectivity
- Version incompatibilities
- External service changes

#### Classification Protocol

For each risk identified in plan, apply this decision tree:

```
Is it a tool/system failure? 
  → YES: Technical risk
  → NO: Continue

Is it timing/coordination/process issue?
  → YES: Operational risk
  → NO: Continue

Is it data integrity/loss/corruption?
  → YES: Data risk
  → NO: Continue

Is it external dependency/API?
  → YES: Integration risk
  → NO: Re-classify (may be compound risk)
```

#### Classification Examples

**"Concurrent modifications during rule optimization"**
- INCORRECT (CLI review): Operational risk (coordination)
- **CORRECT (Desktop review): Data risk (file corruption) ✓**
- **Rationale:** The PRIMARY concern is data loss/corruption from concurrent writes, not coordination timing

**"Database migration fails"**
- Category: Technical risk (system failure)

**"API rate limit exceeded"**
- Category: Integration risk (external dependency)

**"Deploy scheduled during peak hours"**
- Category: Operational risk (timing/coordination)

**"Backup corruption discovered"**
- Category: Data risk (data integrity)

#### Scoring Rubric with Taxonomy

| Score | Categories Covered | Risks Identified | Requirements |
|-------|-------------------|------------------|--------------|
| 10/10 | 4/4 | 3+ total | All categories, complete assessment, full rollback |
| 8/10 | 3/4 | 2+ total | Most categories, mitigation for 95%+ |
| 6/10 | 2/4 | 2+ total | Limited categories, mitigation for 80%+ |
| 4/10 | 1/4 | 1+ total | Single category, partial mitigation |
| 2/10 | 0-1/4 | 0-1 | Minimal risk awareness |

#### Mandatory Risk Worksheet

**Complete this worksheet during review:**

| Risk Statement | Technical | Operational | Data | Integration | Probability | Impact | Mitigation? |
|----------------|-----------|-------------|------|-------------|-------------|--------|-------------|
| [Risk 1] | | ✓ | | | High/Med/Low | Critical/High/Med/Low | Y/N |
| [Risk 2] | ✓ | | | | High/Med/Low | Critical/High/Med/Low | Y/N |
| [Risk 3] | | | ✓ | | High/Med/Low | Critical/High/Med/Low | Y/N |
| **TOTALS** | X | Y | Z | W | | | |
| **Categories Covered** | | | | | | | **N/4** |

**Minimum for 10/10:** ≥1 risk identified in 3+ categories

#### Category Coverage Verification

**After filling worksheet, verify:**
- [ ] Technical risks section present in plan?
- [ ] Operational risks section present in plan?
- [ ] Data risks section present in plan?
- [ ] Integration risks section present in plan?

**Categories covered:** ___/4

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

## Score Decision Matrix (ENHANCED)

**Purpose:** Convert risk identification and mitigation metrics into dimension score. No interpretation needed - just look up the tier.

### Input Values

From completed worksheet:
- **Risk Categories:** Count of 4 types addressed (Technical/Operational/Data/Integration)
- **Risk Assessment:** Probability + impact documented per risk
- **Mitigation Coverage %:** Risks with mitigation / Total risks × 100
- **Rollback Elements:** Count of 4 types (Trigger/Steps/Verification/Timeframe)

### Scoring Table

| Categories | Assessment | Mitigation % | Rollback | Tier | Raw Score | × Weight | Points |
|------------|------------|--------------|----------|------|-----------|----------|--------|
| 4/4 | Complete | 100% | 4/4 | Perfect | 10/10 | × 0.5 | 5 |
| 4/4 | Complete | 100% | 4/4 | Near-Perfect | 9/10 | × 0.5 | 4.5 |
| 4/4 | Mostly | 95%+ | 3-4/4 | Excellent | 8/10 | × 0.5 | 4 |
| 3-4/4 | Mostly | 90%+ | 3/4 | Good | 7/10 | × 0.5 | 3.5 |
| 3/4 | Most | 80%+ | 2-3/4 | Acceptable | 6/10 | × 0.5 | 3 |
| 2-3/4 | Some | 60-79% | 2/4 | Borderline | 5/10 | × 0.5 | 2.5 |
| 2/4 | Some | 50-69% | 1-2/4 | Below Standard | 4/10 | × 0.5 | 2 |
| 1-2/4 | Few | 40-59% | 1/4 | Poor | 3/10 | × 0.5 | 1.5 |
| 1/4 | Few | 30-49% | 0-1/4 | Very Poor | 2/10 | × 0.5 | 1 |
| 0-1/4 | None | <30% | 0/4 | Critical | 1/10 | × 0.5 | 0.5 |
| 0/4 | None | 0% | 0/4 | No Risk Awareness | 0/10 | × 0.5 | 0 |

**Critical Gate:** If rollback missing for high-impact changes, cap at 4/10

### Tie-Breaking Algorithm (Deterministic)

**When category count falls exactly on tier boundary:**

1. **Check Mitigation Coverage:** If mitigation > tier requirement → HIGHER tier
2. **Check Rollback Elements:** If rollback > tier requirement → HIGHER tier
3. **Check Risk Severity:** If identified risks are low-severity → HIGHER tier
4. **Default:** LOWER tier (conservative - missing risk awareness is dangerous)

### Edge Cases

**Edge Case 1: Low-risk / read-only operations**
- **Example:** Plan only generates reports, no modifications
- **Rule:** Don't penalize minimal risk documentation for low-risk plans
- **Rationale:** Risk awareness scales with actual risk

**Edge Case 2: Version control as implicit rollback**
- **Example:** "All changes via git commits" (no explicit rollback)
- **Rule:** Count version control as valid rollback mechanism
- **Rationale:** Git provides rollback capability

**Edge Case 3: Error handling in completeness dimension**
- **Example:** Comprehensive error recovery but no "risk" section
- **Rule:** Check if risks are addressed in error handling section
- **Rationale:** Risk mitigation may exist under different label

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

## Non-Issues (Do NOT Count)

**Purpose:** Eliminate false positives by explicitly defining what is NOT a risk awareness issue.

### Pattern 1: Low-Risk/Read-Only Operations

**Example:**
```markdown
Task: "Analyze log files and generate report"
(No risk section)
```
**Why NOT an issue:** Read-only operations have minimal inherent risk  
**Overlap check:** Not Completeness - it's risk scope appropriateness  
**Correct action:** Do not penalize missing risks for read-only plans

### Pattern 2: Version Control as Built-In Rollback

**Example:**
```markdown
"All changes tracked in git"
(No explicit rollback procedure)
```
**Why NOT an issue:** Git provides implicit rollback capability  
**Overlap check:** N/A - git is standard rollback mechanism  
**Correct action:** Count git tracking as rollback element (1/4)

### Pattern 3: Error Handling in Completeness Dimension

**Example:**
```markdown
"Error handling" section under Completeness
```
**Why NOT an issue:** Error handling counted in Completeness, not Risk  
**Overlap check:** See _overlap-resolution.md Rule 2 (Completeness primary for error handling)  
**Correct action:** Do not double-count error handling as risk mitigation

### Pattern 4: Mitigation Counted in Another Dimension

**Example:**
```markdown
Plan has validation commands throughout (Success Criteria)
```
**Why NOT an issue:** Validation is a form of risk mitigation, already counted  
**Overlap check:** See _overlap-resolution.md (Success Criteria primary for verification)  
**Correct action:** Do not require separate risk section for validation

## Complete Pattern Inventory

**Purpose:** Eliminate interpretation variance by providing exhaustive lists. If it's not in this list, don't invent it. Match case-insensitive.

### Category 1: Technical Risk Indicators (20 Patterns)

**Build/Compilation:**
- "build fail"
- "compilation error"
- "syntax error"
- "import error"
- "dependency conflict"

**Runtime:**
- "crash"
- "exception"
- "out of memory"
- "OOM"
- "memory leak"
- "stack overflow"
- "segfault"

**Performance:**
- "slow"
- "latency"
- "timeout"
- "bottleneck"
- "resource exhaustion"
- "CPU spike"
- "degradation"

**Configuration:**
- "misconfiguration"
- "config error"
- "wrong setting"

**Regex Patterns:**
```regex
\b(build|compilation|syntax|import)\s*(fail|error)\b
\b(crash|exception|OOM|out\s+of\s+memory|memory\s+leak|stack\s+overflow)\b
\b(slow|latency|timeout|bottleneck|degradation)\b
\b(misconfigur|config\s*error|wrong\s+setting)\b
```

### Category 2: Operational Risk Indicators (15 Patterns)

**Timing:**
- "off-hours"
- "peak hours"
- "maintenance window"
- "business hours"
- "deployment timing"

**Coordination:**
- "missing approval"
- "wrong environment"
- "wrong branch"
- "merge conflict"
- "communication failure"

**Process:**
- "skip step"
- "out of order"
- "manual error"
- "human error"
- "documentation gap"

**Regex Patterns:**
```regex
\b(off-hours|peak\s+hours|maintenance\s+window|business\s+hours)\b
\b(missing|wrong)\s+(approval|environment|branch)\b
\b(merge\s+conflict|communication\s+failure)\b
\b(skip|missed)\s+step\b
\b(manual|human)\s+error\b
```

### Category 3: Data Risk Indicators (20 Patterns)

**Loss:**
- "data loss"
- "lost data"
- "deleted accidentally"
- "overwritten"
- "truncated"

**Corruption:**
- "corrupted"
- "inconsistent"
- "invalid data"
- "malformed"
- "integrity violation"

**Security:**
- "exposed"
- "leaked"
- "unauthorized access"
- "PII exposure"
- "security breach"

**State:**
- "stale data"
- "race condition"
- "concurrent write"
- "dirty read"
- "phantom read"

**Regex Patterns:**
```regex
\b(data\s+loss|lost\s+data|deleted\s+accidentally|overwritten|truncated)\b
\b(corrupted?|inconsistent|invalid\s+data|malformed|integrity)\b
\b(exposed?|leaked?|unauthorized|PII|breach)\b
\b(stale|race\s+condition|concurrent\s+write|dirty\s+read)\b
```

### Category 4: Integration Risk Indicators (15 Patterns)

**API:**
- "API down"
- "API error"
- "rate limit"
- "throttled"
- "quota exceeded"

**Network:**
- "connection refused"
- "network failure"
- "DNS failure"
- "timeout"
- "unreachable"

**Version:**
- "version mismatch"
- "incompatible"
- "breaking change"
- "deprecated"
- "unsupported"

**Regex Patterns:**
```regex
\b(API|service)\s+(down|error|failure|unavailable)\b
\b(rate\s+limit|throttle|quota\s+exceeded)\b
\b(connection\s+refused|network\s+failure|DNS\s+failure|unreachable)\b
\b(version\s+mismatch|incompatible|breaking\s+change|deprecated|unsupported)\b
```

### Category 5: Probability Indicators (3 Levels)

**High (>50%):**
- "likely"
- "probable"
- "expected"
- "common"
- "frequent"
- "often"

**Medium (10-50%):**
- "possible"
- "may occur"
- "sometimes"
- "occasional"
- "moderate chance"

**Low (<10%):**
- "unlikely"
- "rare"
- "improbable"
- "edge case"
- "exceptional"
- "seldom"

**Regex Patterns:**
```regex
# High
\b(likely|probable|expected|common|frequent|often)\b
# Medium
\b(possible|may\s+occur|sometimes|occasional|moderate)\b
# Low
\b(unlikely|rare|improbable|edge\s+case|exceptional|seldom)\b
```

### Category 6: Impact Indicators (4 Levels)

**Critical:**
- "system down"
- "complete outage"
- "data loss"
- "irrecoverable"
- "production down"

**High:**
- "major feature broken"
- "significant impact"
- "widespread"
- "many users affected"

**Medium:**
- "degraded"
- "slow"
- "partial"
- "some users"
- "workaround available"

**Low:**
- "minor"
- "cosmetic"
- "inconvenience"
- "few users"
- "low priority"

**Regex Patterns:**
```regex
# Critical
\b(system\s+down|complete\s+outage|data\s+loss|irrecoverable|production\s+down)\b
# High
\b(major|significant|widespread|many\s+users)\b
# Medium
\b(degraded|partial|some\s+users|workaround)\b
# Low
\b(minor|cosmetic|inconvenience|few\s+users|low\s+priority)\b
```

### Category 7: Mitigation Indicators (20 Phrases)

**Prevention:**
- "to prevent"
- "to avoid"
- "safeguard"
- "protect against"
- "guard against"

**Detection:**
- "monitor for"
- "alert on"
- "detect"
- "watch for"
- "check for"

**Recovery:**
- "rollback"
- "restore"
- "recover"
- "fallback"
- "retry"
- "circuit breaker"
- "failover"
- "backup"

**Containment:**
- "isolate"
- "quarantine"
- "limit impact"

**Regex Patterns:**
```regex
\b(to\s+)?(prevent|avoid|safeguard|protect|guard)\s+(against)?\b
\b(monitor|alert|detect|watch|check)\s+(for|on)\b
\b(rollback|restore|recover|fallback|retry|failover|backup)\b
\b(circuit\s+breaker|rate\s+limit)\b
\b(isolate|quarantine|limit\s+impact)\b
```

### Category 8: Rollback Element Patterns (4 Types)

**Trigger:**
- "if X fails"
- "when Y exceeds"
- "trigger rollback"
- "rollback criteria"
- "abort condition"

**Steps:**
- "rollback steps"
- "to rollback"
- "revert to"
- "restore from"
- "undo changes"

**Verification:**
- "verify rollback"
- "confirm reverted"
- "check restored"
- "validate rollback"

**Timeframe:**
- "rollback time"
- "ETA"
- "within X minutes"
- "time to recover"
- "RTO"

**Regex Patterns:**
```regex
# Trigger
\b(if|when)\s+.*(fail|exceed|error).*rollback\b
\b(trigger|criteria|condition)\s+(for\s+)?rollback\b

# Steps
\b(rollback\s+steps|to\s+rollback|revert\s+to|restore\s+from|undo)\b

# Verification
\b(verify|confirm|check|validate)\s+(rollback|revert|restore)\b

# Timeframe
\b(rollback|recovery|restore)\s+(time|ETA|within)\b
\b(RTO|time\s+to\s+recover)\b
```

### Ambiguous Cases Resolution

**Case 1: Risk classification uncertainty**

**Pattern:** "Concurrent file modifications may cause issues"

**Ambiguity:** Technical (system) or Data (corruption) risk?

**Resolution Rule:**
- Apply Risk Category Taxonomy decision tree
- Primary concern is data integrity → Data risk
- System/tool failure → Technical risk
- Pick ONE category (no double-counting)

**Case 2: Error handling vs risk mitigation**

**Pattern:** Comprehensive error recovery in Completeness section

**Ambiguity:** Does error handling count as risk mitigation?

**Resolution Rule:**
- Error handling = Completeness dimension (primary)
- Risk mitigation = separate risk-focused section
- Don't double-count between dimensions
- Check _overlap-resolution.md for guidance

**Case 3: Version control as implicit rollback**

**Pattern:** "All changes via git commits" (no explicit rollback)

**Ambiguity:** Is git implicit rollback?

**Resolution Rule:**
- Git provides valid rollback mechanism
- Count as 1/4 rollback elements (steps via git revert)
- Still need: trigger, verification, timeframe for full credit

**Case 4: Low-risk plan without risk section**

**Pattern:** Read-only analysis plan, no risks documented

**Ambiguity:** Is missing risk section a gap?

**Resolution Rule:**
- Low-risk operations (read-only, no state changes) = minimal risk
- Don't penalize missing risk documentation for inherently safe plans
- Note: "Low-risk plan - minimal documentation acceptable"

**Case 5: Risk mentioned without assessment**

**Pattern:** "Be careful of rate limits" (no probability/impact)

**Ambiguity:** Is mention without assessment a risk?

**Resolution Rule:**
- Mention without probability/impact = incomplete assessment
- Count risk as identified but assessment as incomplete
- Full credit needs: probability + impact + mitigation

**Case 6: Single risk covering multiple categories**

**Pattern:** "Database failure could cause data loss and service outage"

**Ambiguity:** Count in multiple categories?

**Resolution Rule:**
- Single event = single risk = single category
- Classify by ROOT CAUSE (Technical - database failure)
- Consequences inform impact rating, not category

**Case 7: Mitigation via framework/library**

**Pattern:** "Use retry decorator with exponential backoff"

**Ambiguity:** Is delegated mitigation valid?

**Resolution Rule:**
- Framework/library mitigation = valid
- Count as mitigation present
- More specific is better but delegation acceptable

**Case 8: Rollback for stateless operations**

**Pattern:** Plan involves only API calls, no persistent changes

**Ambiguity:** Is rollback needed for stateless operations?

**Resolution Rule:**
- Stateless operations have no state to rollback
- Don't penalize missing rollback for idempotent/stateless plans
- Note: "Stateless operation - rollback N/A"

## Anti-Pattern Examples (Common Mistakes)

**❌ WRONG (False Positive):**
- Flagged: "No rollback procedure documented"
- Rationale given: "Missing rollback elements"
- Problem: Plan uses git and explicitly mentions "revert commit if needed"
- Impact: Incorrect rollback score reduction

**✅ CORRECT:**
- Git-based rollback counts
- Rationale: Version control is valid rollback mechanism
- Condition: Would be flagged IF plan involves non-versioned state changes

**❌ WRONG (False Positive):**
- Flagged: "Missing operational risks"
- Rationale given: "No operational risks documented"
- Problem: Plan is purely technical code change, no operations involved
- Impact: Incorrect category coverage reduction

**✅ CORRECT:**
- Not all 4 categories required for every plan
- Rationale: Risk categories should match plan scope
- Condition: Would be flagged IF plan involves deployment/operations

## Ambiguous Case Resolution Rules (REQUIRED)

**Purpose:** Provide deterministic scoring when risk classification/assessment is borderline.

### Rule 1: Same-File Context
**Count risk category as covered if:** At least one risk in that category explicitly identified  
**Count risk category as NOT covered if:** Zero risks in that category

### Rule 2: Adjectives Without Quantifiers
**Count mitigation as complete if:** Specific steps to prevent or recover from risk  
**Count mitigation as incomplete if:** Vague mention ("handle appropriately", "mitigate risk")

### Rule 3: Pattern Variations
**Classify risk using Risk Category Taxonomy decision tree (Technical → Operational → Data → Integration)**  
**Assign to first matching category only (no double-counting)**

### Rule 4: Default Resolution
**Still uncertain after Rules 1-3?** → Count risk in most conservative category (highest impact), count mitigation as incomplete

### Borderline Cases Template

Document borderline decisions in your worksheet:

```markdown
### Risk: "[Risk Description]"
- **Decision:** Category [Technical/Operational/Data/Integration], Mitigation [Complete/Incomplete/Missing]
- **Rule Applied:** [1/2/3/4]
- **Reasoning:** [Explain why this classification]
- **Alternative:** [Other interpretation and why rejected]
- **Confidence:** [HIGH/MEDIUM/LOW]
```

## Mandatory Counting Worksheet (REQUIRED)

**CRITICAL:** You MUST create and fill this worksheet BEFORE calculating score.

### Why This Is Required
- **Eliminates counting variance:** Same plan → same worksheet → same score
- **Prevents false negatives:** Category-by-category check catches all gaps
- **Provides evidence:** Worksheet shows exactly what was counted

### Worksheet Template (Enhanced from Risk Category Taxonomy)

| Risk Statement | Technical | Operational | Data | Integration | Probability | Impact | Mitigation? |
|----------------|-----------|-------------|------|-------------|-------------|--------|-------------|
| [Risk 1] | | ✓ | | | H/M/L | C/H/M/L | Y/N |
| [Risk 2] | ✓ | | | | H/M/L | C/H/M/L | Y/N |
| [Risk 3] | | | ✓ | | H/M/L | C/H/M/L | Y/N |
| **TOTALS** | X | Y | Z | W | | | |
| **CATEGORIES COVERED** | | | | | | | **___/4** |

**Rollback Element Checklist:**
| Element | Present? | Description |
|---------|----------|-------------|
| Rollback trigger defined | Y/N | |
| Rollback steps documented | Y/N | |
| Rollback verification | Y/N | |
| Time estimate | Y/N | |
| **TOTAL** | **___/4** | |

**Mitigation Coverage:**
```
Mitigation coverage % = (risks with mitigation / total risks) × 100 = ___%
```

### Counting Protocol (6 Steps)

**Step 1: Create Empty Worksheet**
- Copy template above into working document

**Step 2: Identify All Risks in Plan**
- Read plan from line 1 to END
- For each risk mentioned: Add row to worksheet
- Classify into ONE category (use Risk Category Taxonomy decision tree)

**Step 3: Assess Risk Documentation**
- For each risk: Check probability (H/M/L)
- For each risk: Check impact (Critical/High/Medium/Low)
- For each risk: Check if mitigation strategy present

**Step 4: Calculate Category Coverage**
- Count unique categories with ≥1 risk identified
- Minimum for 10/10: ≥1 risk in 3+ categories

**Step 5: Check Rollback Elements**
- Fill rollback checklist (4 elements)
- Complete = 4/4, Partial = 2-3/4, Minimal = 1/4, Missing = 0/4

**Step 6: Include in Review Output**
- Copy completed worksheet into review document
- Calculate score using Score Decision Matrix

### Common Mistakes to Avoid

**❌ Mistake 1: Classifying same risk into multiple categories**
- Problem: Risk counted multiple times
- Solution: Use Risk Category Taxonomy decision tree, pick ONE primary category

**❌ Mistake 2: Accepting vague mitigation as complete**
- Problem: "Handle errors" counted as mitigation
- Solution: Only Y if specific recovery steps provided

## Inter-Run Consistency Target

**Expected variance:** ±1 category

**Verification:**
- Use 4-category checklist
- Count risks with complete assessment
- Use rollback element checklist

**If variance exceeds threshold:**
- Re-verify using category definitions
- Apply assessment completeness strictly
