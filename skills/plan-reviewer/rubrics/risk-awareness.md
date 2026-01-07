# Risk Awareness Rubric (5 points)

## Scoring Criteria

### 5/5 (5 points): Excellent
- Failure scenarios identified
- Mitigation strategies defined
- Rollback procedures documented
- Risk assessment present
- Contingency plans included

### 4/5 (4 points): Good
- Most failures identified
- Most mitigations defined
- Basic rollback present

### 3/5 (3 points): Acceptable
- Some failures identified
- Some mitigations defined
- Limited rollback

### 2/5 (2 points): Needs Work
- Few failures identified
- Few mitigations
- No rollback

### 1/5 (1 point): Poor
- No risk awareness
- No mitigations
- No rollback

## Risk Categories

### 1. Technical Risks

Identify technical failure points:

**Example:**
```markdown
## Technical Risks

### Risk: Database migration fails
Probability: Medium
Impact: HIGH (production downtime)

Mitigation:
1. Test migration on staging (identical data volume)
2. Create database backup before migration
3. Use transactional DDL (PostgreSQL supports this)
4. Set statement timeout to 30s (prevent locks)

Rollback:
If migration fails:
1. Stop application: kubectl scale deployment app --replicas=0
2. Restore backup: psql myapp_prod < backup-2024-01-06.sql
3. Verify: Run smoke tests
4. Restart application: kubectl scale deployment app --replicas=3

### Risk: Memory leak in new code
Probability: Low
Impact: Medium (gradual performance degradation)

Mitigation:
1. Memory profiling before deploy (py-spy, memory_profiler)
2. Monitor RSS after deploy (alert if >2GB)
3. Canary deployment (10% traffic first)

Rollback:
If memory leak detected:
1. Immediate rollback: kubectl rollout undo deployment/app
2. Monitor memory drops to baseline
3. Investigation in development environment
```

### 2. Operational Risks

Identify operational failure points:

**Example:**
```markdown
## Operational Risks

### Risk: Deployment outside business hours
Probability: Low (prevented by CI checks)
Impact: HIGH (no support staff available)

Mitigation:
1. CI blocks deploys outside 9AM-5PM Pacific
2. Override requires manager approval
3. On-call engineer auto-paged for after-hours deploys

### Risk: Wrong environment deployment
Probability: Low
Impact: CRITICAL (prod data corruption)

Mitigation:
1. Require explicit --env=production flag
2. Confirmation prompt before production
3. Production deploys require 2FA
4. Audit log all deployments
```

### 3. Data Risks

Identify data loss/corruption risks:

**Example:**
```markdown
## Data Risks

### Risk: Data loss during migration
Probability: Low (tested on staging)
Impact: CRITICAL (irrecoverable user data)

Mitigation:
1. Full backup before migration
2. Incremental backups every hour during migration
3. Data validation after migration (row counts, checksums)
4. Keep old system running read-only for 7 days

Rollback:
If data corruption detected:
1. Stop accepting writes immediately
2. Restore from last known good backup
3. Replay write logs if available
4. Data reconciliation (compare old vs new)
```

### 4. Integration Risks

Identify third-party/integration risks:

**Example:**
```markdown
## Integration Risks

### Risk: Payment API downtime
Probability: Low (99.9% SLA)
Impact: HIGH (no purchases possible)

Mitigation:
1. Implement circuit breaker (fail after 3 timeouts)
2. Queue payments for retry (up to 24 hours)
3. Fallback to backup payment provider
4. Monitor API health before peak hours

Contingency:
If payment API down >1 hour:
1. Enable maintenance mode
2. Queue all purchases
3. Process queue when API returns
4. Notify customers via email
```

## Risk Assessment Table

Use during review:

| Risk | Probability | Impact | Mitigation? | Rollback? |
|------|-------------|--------|-------------|-----------|
| DB migration fails | Medium | HIGH | ✅ Yes | ✅ Yes |
| Memory leak | Low | Medium | ✅ Yes | ✅ Yes |
| API timeout | High | Low | ❌ No | ❌ No |
| Data corruption | Low | CRITICAL | ✅ Yes | ✅ Yes |

**Missing mitigations:** API timeout risk (no handling)

## Rollback Requirements

Every high-impact change must have rollback:

**Required elements:**
1. Rollback trigger (when to rollback?)
2. Rollback steps (how to rollback?)
3. Rollback verification (how to confirm success?)
4. Rollback time estimate

**Example:**
```markdown
## Rollback Procedure

**Trigger:** Any of:
- Error rate >1% for 5 minutes
- P95 latency >1000ms for 5 minutes  
- Manual decision (critical bug found)

**Steps:**
1. Execute: kubectl rollout undo deployment/app
2. Wait: 2 minutes for pods to restart
3. Verify: curl https://app.com/health returns 200
4. Verify: Error rate <0.1% for 5 minutes
5. Verify: P95 latency <500ms

**Time estimate:** 5 minutes total

**If rollback fails:**
1. Emergency: Scale to 0, restore from backup (15 min)
2. Escalate to on-call manager
3. Page database team if DB issues
```

## Scoring Formula

```
Base score = 5/5 (5 points)

Risk identification:
  All major risks identified: 5/5
  Most risks identified: 4/5 (-1)
  Some risks identified: 3/5 (-2)
  Few risks identified: 2/5 (-3)
  No risks identified: 1/5 (-4)

Additional deductions:
  No mitigation strategies: -1 point
  No rollback procedures: -1 point (CRITICAL)

Minimum score: 1/5 (1 point)
```

## Common Risk Issues

### Issue 1: No Risk Identification

**Problem:**
```markdown
Deploy new authentication system
(No risks mentioned)
```

**Fix:**
```markdown
## Risks

### Authentication failure locks out users
Impact: CRITICAL
Mitigation:
- Deploy to 10% of users first (canary)
- Keep old auth system running 48 hours
- Emergency bypass code for admin access
- Monitor login success rate (alert if <95%)

### Session migration data loss
Impact: HIGH
Mitigation:
- Backup session store before migration
- Dual-write to old and new stores for 24 hours
- Verify data consistency before cutover
```

### Issue 2: No Rollback Plan

**Problem:**
```markdown
Task: Migrate to new database
(No rollback mentioned)
```

**Fix:**
```markdown
## Rollback Plan

**Trigger:** If any of:
- Migration fails (exit code non-zero)
- Data validation fails (row count mismatch >1%)
- Performance degrades (p95 latency >2x baseline)
- Data corruption detected

**Steps:**
1. Stop application: systemctl stop myapp
2. Restore database: psql -f backup-pre-migration.sql
3. Revert application code: git checkout v1.2.3 && deploy
4. Start application: systemctl start myapp
5. Verify: pytest tests/smoke/ all pass

**Time estimate:** 15 minutes

**Data loss window:** 0 (writes disabled during migration)
```

### Issue 3: Unquantified Impact

**Problem:**
```markdown
Risk: High traffic might cause issues
```

**Fix:**
```markdown
Risk: Traffic spike exceeds capacity

Details:
- Current capacity: 1000 RPS
- Expected peak: 2000 RPS (Black Friday)
- Impact: 503 errors, user frustration, lost revenue

Mitigation:
- Pre-scale to 6 replicas (2x capacity = 2000 RPS)
- Auto-scaling: 4-12 replicas based on CPU (>70%)
- CDN for static assets (reduce origin load by 60%)
- Queue non-critical requests (analytics, logs)

Monitoring:
- Alert if 5xx rate >1%
- Alert if avg response time >1000ms
- Dashboard: requests/sec, error rate, latency
```

### Issue 4: No Mitigation Strategy

**Problem:**
```markdown
Risk: Payment API might be slow
(No mitigation)
```

**Fix:**
```markdown
Risk: Payment API timeout

Probability: Medium (p99 latency=5s, we timeout at 3s)
Impact: High (failed purchases, user frustration)

Mitigation:
1. Implement retry with backoff (3 attempts)
2. Increase timeout to 10s for payment calls
3. Circuit breaker: fail fast after 3 consecutive timeouts
4. Queue failed payments for manual processing
5. Cache payment provider status (reduce calls by 30%)

Monitoring:
- Track payment API latency percentiles
- Alert if p95 >5s or p99 >10s
- Dashboard shows: success rate, timeout rate, circuit breaker state

Fallback:
- Backup payment provider (switch if primary fails)
- Manual payment processing workflow
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
