# Completeness Rubric (20 points)

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 4
**Points:** Raw × (4/2) = Raw × 2.0

## Scoring Criteria

### 10/10 (20 points): Perfect
- Setup: 5/5 required elements present
- Validation: 3/3 phases documented
- Error recovery: 5+ scenarios with steps
- Cleanup: Complete with verification
- Edge cases: 90%+ coverage

### 9/10 (18 points): Near-Perfect
- Setup: 5/5 elements present
- Validation: 3/3 phases documented
- Error recovery: 4+ scenarios with steps
- Cleanup: Complete with verification
- Edge cases: 85-89% coverage

### 8/10 (16 points): Excellent
- Setup: 5/5 elements present
- Validation: 3/3 phases documented
- Error recovery: 4 scenarios with steps
- Cleanup: Complete
- Edge cases: 80-84% coverage

### 7/10 (14 points): Good
- Setup: 4/5 elements present
- Validation: 2-3/3 phases documented
- Error recovery: 3 scenarios with steps
- Cleanup: Present but partial
- Edge cases: 70-79% coverage

### 6/10 (12 points): Acceptable
- Setup: 4/5 elements present
- Validation: 2-3/3 phases documented
- Error recovery: 2-3 scenarios
- Cleanup: Present but partial
- Edge cases: 60-69% coverage

### 5/10 (10 points): Borderline
- Setup: 3/5 elements present
- Validation: 2/3 phases documented
- Error recovery: 2 scenarios
- Cleanup: Minimal
- Edge cases: 50-59% coverage

### 4/10 (8 points): Needs Work
- Setup: 3/5 elements present
- Validation: 1-2/3 phases documented
- Error recovery: 1 scenario
- Cleanup: Minimal
- Edge cases: 40-49% coverage

### 3/10 (6 points): Poor
- Setup: 2/5 elements present
- Validation: 1/3 phase documented
- Error recovery: 0-1 scenarios
- Cleanup: Missing
- Edge cases: 30-39% coverage

### 2/10 (4 points): Very Poor
- Setup: 2/5 elements present
- Validation: 0-1/3 phases documented
- Error recovery: 0 scenarios
- Cleanup: Missing
- Edge cases: 20-29% coverage

### 1/10 (2 points): Inadequate
- Setup: 1/5 elements present
- Validation: Not documented
- Error recovery: Not documented
- Cleanup: Not documented
- Edge cases: 10-19% coverage

### 0/10 (0 points): Not Complete
- Setup: 0/5 elements present
- Validation: Not documented
- Error recovery: Not documented
- Cleanup: Not documented
- Edge cases: <10% coverage

## Counting Definitions

### Setup Phase Elements

**Required elements (count 0-5):**

**Setup Element Checklist:**
- Prerequisites verification: Present? Commands provided?
- Environment preparation: Present? Steps specified?
- Dependency installation: Present? Commands provided?
- Configuration setup: Present? Values/files specified?
- Initial state verification: Present? Verification command?

**Scoring by count:**
- 5/5 elements: Full credit
- 4/5 elements: -1 point
- 3/5 elements: -3 points
- 2/5 elements: -5 points
- 0-1/5 elements: -8 points

### Validation Phases

**Required phases (count 0-3):**

**Validation Phase Checklist:**
- Pre-execution: Present? Commands? Expected output?
- During execution: Present? Commands? Expected output?
- Post-execution: Present? Commands? Expected output?

**Scoring by count:**
- 3/3 phases: Full credit
- 2/3 phases: -1 point
- 1/3 phases: -3 points
- 0/3 phases: -5 points

### Error Recovery Scenarios

**Count documented scenarios with recovery steps:**

**Error Recovery Checklist:**
- Input validation failures: Documented? Has recovery steps?
- Execution errors (timeout, crash): Documented? Has recovery steps?
- External dependency failures: Documented? Has recovery steps?
- Permission/access errors: Documented? Has recovery steps?
- Resource exhaustion: Documented? Has recovery steps?
- State corruption: Documented? Has recovery steps?

**Count only scenarios WITH recovery steps.**

**Scoring by count:**
- 4+ scenarios with recovery: Full credit
- 2-3 scenarios with recovery: -2 points
- 1 scenario with recovery: -4 points
- 0 scenarios with recovery: -6 points (CRITICAL)

### Cleanup Phase

**Required elements:**

**Cleanup Checklist:**
- Temporary files removal: Present?
- Resources released: Present?
- State reset (if needed): Present?
- Verification of cleanup: Present?

**Scoring:**
- Complete (4/4): Full credit
- Partial (2-3/4): -1 point
- Minimal (1/4): -2 points
- Missing (0/4): -3 points

### Edge Case Coverage

**Categories to check:**

**Edge Case Checklist:**
- Empty states (Empty DB, no users, cold cache): Count addressed out of 3
- Concurrent execution (Dual runs, locks, races): Count addressed out of 3
- Partial completion (Interrupted, resume, idempotency): Count addressed out of 3
- Resource constraints (Disk full, memory, network): Count addressed out of 3

**Coverage calculation:**
```
Coverage % = (items addressed / 12 total) × 100
```

**Scoring by coverage:**
- 80%+ (10-12/12): Full credit
- 60-79% (7-9/12): -1 point
- 40-59% (5-6/12): -2 points
- 20-39% (3-4/12): -3 points
- <20% (0-2/12): -4 points

## Score Decision Matrix (ENHANCED)

**Purpose:** Convert completeness metrics into dimension score. No interpretation needed - just look up the tier.

### Input Values

From completed worksheet:
- **Setup Elements:** Count of 5 types (Prerequisites/Environment/Dependencies/Config/Initial state)
- **Validation Phases:** Count of 3 types (Pre/During/Post execution)
- **Error Recovery Scenarios:** Count with recovery steps documented
- **Cleanup:** Complete with verification / Present / Minimal / Missing
- **Edge Case Coverage %:** Edge cases addressed / Total identified × 100

### Scoring Table

| Setup | Validation | Error Recovery | Cleanup | Edge Cases | Tier | Raw Score | × Weight | Points |
|-------|------------|----------------|---------|------------|------|-----------|----------|--------|
| 5/5 | 3/3 | 5+ | Complete+verify | 90%+ | Perfect | 10/10 | × 2 | 20 |
| 5/5 | 3/3 | 4+ | Complete+verify | 85-89% | Near-Perfect | 9/10 | × 2 | 18 |
| 5/5 | 3/3 | 4 | Complete | 80-84% | Excellent | 8/10 | × 2 | 16 |
| 4/5 | 2-3/3 | 3 | Partial | 70-79% | Good | 7/10 | × 2 | 14 |
| 4/5 | 2-3/3 | 2-3 | Partial | 60-69% | Acceptable | 6/10 | × 2 | 12 |
| 3/5 | 2/3 | 2 | Minimal | 50-59% | Borderline | 5/10 | × 2 | 10 |
| 3/5 | 1-2/3 | 1 | Minimal | 40-49% | Below Standard | 4/10 | × 2 | 8 |
| 2/5 | 1/3 | 0-1 | Missing | 30-39% | Poor | 3/10 | × 2 | 6 |
| 2/5 | 0-1/3 | 0 | Missing | 20-29% | Very Poor | 2/10 | × 2 | 4 |
| 1/5 | 0/3 | 0 | Missing | 10-19% | Critical | 1/10 | × 2 | 2 |
| 0/5 | 0/3 | 0 | Missing | <10% | Incomplete | 0/10 | × 2 | 0 |

**Critical Gate:** If error recovery = 0, cap at 4/10 (8 points)

### Tie-Breaking Algorithm (Deterministic)

**When setup count falls exactly on tier boundary:**

1. **Check Validation Phases:** If validation > tier requirement → HIGHER tier
2. **Check Error Recovery:** If error scenarios > tier requirement → HIGHER tier
3. **Check Cleanup Quality:** If cleanup has verification → HIGHER tier
4. **Default:** LOWER tier (conservative - missing completeness causes failures)

### Edge Cases

**Edge Case 1: Implicit setup from standard tools**
- **Example:** "Run pytest" (no explicit environment setup)
- **Rule:** Don't penalize if standard tooling handles setup
- **Rationale:** pytest handles its own setup

**Edge Case 2: Error recovery delegated to framework**
- **Example:** "Use retry decorator with 3 attempts"
- **Rule:** Count framework-level recovery as valid
- **Rationale:** Framework handles error scenarios

**Edge Case 3: Cleanup not needed (read-only operations)**
- **Example:** Plan only reads data, no modifications
- **Rule:** Don't penalize missing cleanup for read-only plans
- **Rationale:** Nothing to clean up

## Required Components Checklist

### Setup Phase

```markdown
## Setup (Example - Complete)

1. Verify prerequisites:
   - Python 3.11+: python --version ≥ 3.11
   - PostgreSQL: pg_isready returns 0

2. Create environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```
   Verify: uv pip list shows flask==3.0.0

4. Configure:
   ```bash
   cp .env.example .env
   ```
   Edit: Set DATABASE_URL=postgresql://localhost/myapp

5. Verify setup:
   ```bash
   pytest tests/smoke/test_connection.py
   ```
   Expected: 1 passed
```

### Validation Checks

```markdown
## Validation (Example - Complete)

### Pre-execution
- [ ] Prerequisites met: all checks pass
- [ ] Input files exist: ls data/*.csv returns files
- [ ] Permissions valid: test -w output/ returns 0

### During execution
- [ ] Progress logged: tail -f logs/process.log shows activity
- [ ] No errors: grep ERROR logs/process.log returns empty
- [ ] Resources stable: memory usage <2GB

### Post-execution
- [ ] Output exists: ls output/results.json returns file
- [ ] Output valid: jq . output/results.json parses successfully
- [ ] State consistent: pytest tests/integration/ passes
```

### Error Recovery

```markdown
## Error Recovery (Example - Complete)

### Input Validation Failure
Detection: Exit code 1, "ValidationError" in output
Recovery:
1. Check error message for specific field
2. Fix input file: vim data/input.csv
3. Re-run: python process.py
4. If still fails: Contact data team

### Timeout (>30 minutes)
Detection: Process killed, "Timeout" in logs
Recovery:
1. Check resource usage: htop
2. Reduce batch size: --batch-size 100
3. Re-run from checkpoint: --resume
4. If still times out: Scale up resources

### Database Connection Failed
Detection: "Connection refused" in logs
Recovery:
1. Check DB status: pg_isready
2. If down: docker-compose up -d postgres
3. Wait 30 seconds
4. Retry: python process.py
5. If still fails: Check credentials in .env
```

### Cleanup Phase

```markdown
## Cleanup (Example - Complete)

1. Remove temp files:
   ```bash
   rm -rf /tmp/process-*
   ```

2. Stop services:
   ```bash
   docker-compose down
   ```

3. Clear cache:
   ```bash
   rm -rf .cache/
   ```

4. Verify cleanup:
   ```bash
   ls /tmp/process-* 2>&1 | grep -q "No such file"
   docker ps | grep -q myapp && echo "FAIL" || echo "OK"
   ```
```

## Worked Example

**Target:** Data migration plan

### Step 1: Assess Setup

**Setup Assessment:**
- Prerequisites: Yes (Python version, DB)
- Environment: Yes (venv creation)
- Dependencies: Yes (pip install)
- Configuration: No - Missing
- Initial verification: Yes (Smoke test)

**Count:** 4/5 elements

### Step 2: Assess Validation

**Validation Assessment:**
- Pre-execution: Yes, commands provided
- During execution: No
- Post-execution: Yes, commands provided

**Count:** 2/3 phases

### Step 3: Assess Error Recovery

**Error Recovery Assessment:**
- Input validation: Yes, has recovery steps
- Timeout: No
- DB failure: Yes, has recovery steps
- Permission error: No

**Count:** 2 scenarios with recovery

### Step 4: Assess Cleanup

**Cleanup Assessment:**
- Temp files: Yes
- Resources: No
- State reset: No
- Verification: Yes

**Count:** 2/4 (Partial)

### Step 5: Assess Edge Cases

**Edge Case Coverage:**
- Empty states: 1/3
- Concurrent: 0/3
- Partial completion: 2/3
- Resources: 1/3

**Coverage:** 4/12 = 33%

### Step 6: Calculate Score

**Component Assessment:**
- Setup: 4/5 = -1 point
- Validation: 2/3 = -1 point
- Error recovery: 2 = -2 points
- Cleanup: 2/4 = -1 point
- Edge cases: 33% = -3 points

**Total deductions:** -8 points
**Final:** 12 points = 6/10 (Acceptable)

### Step 7: Document in Review

```markdown
## Completeness: 6/10 (12 points)

**Setup:** 4/5 elements
- [YES] Prerequisites, environment, dependencies, verification
- [NO] Configuration setup missing

**Validation:** 2/3 phases
- [YES] Pre-execution, post-execution
- [NO] During-execution monitoring missing

**Error recovery:** 2 scenarios
- [YES] Input validation, DB failure
- [NO] Timeout, permission errors missing

**Cleanup:** Partial (2/4)
- [YES] Temp files, verification
- [NO] Resource release, state reset missing

**Edge cases:** 33% (4/12)
- Concurrent execution: Not addressed
- Resource constraints: Partially addressed

**Priority fixes:**
1. Add configuration setup step
2. Add during-execution monitoring
3. Add timeout and permission error handling
4. Complete cleanup section
```

## Completeness Checklist

During review, verify Setup, Validation, Error Recovery, Cleanup, Edge Cases coverage.

## Non-Issues (Do NOT Count)

**Purpose:** Eliminate false positives by explicitly defining what is NOT a completeness issue.

### Pattern 1: Setup Implicitly Complete from Context

**Example:**
```markdown
Prerequisites: "Python 3.11+ (per system requirements)"
```
**Why NOT an issue:** System requirements referenced, not missing  
**Overlap check:** Not Context issue - reference provided  
**Correct action:** Count as present if reference is valid

### Pattern 2: Error Recovery Covered Elsewhere

**Example:**
```markdown
Error handling: "See Error Recovery section below"
(Error Recovery section exists with 4+ scenarios)
```
**Why NOT an issue:** Error recovery exists, just in separate section  
**Overlap check:** See _overlap-resolution.md Rule 2 (Completeness primary)  
**Correct action:** Count if referenced section exists and is complete

### Pattern 3: Cleanup Not Needed for Read-Only Operations

**Example:**
```markdown
Task: "Analyze log files and generate report"
(No cleanup section)
```
**Why NOT an issue:** Read-only analysis creates no artifacts needing cleanup  
**Overlap check:** Not a Risk issue (no state changes)  
**Correct action:** Do not penalize missing cleanup for read-only plans

### Pattern 4: Edge Cases Handled by Design

**Example:**
```markdown
"Process uses idempotent operations - safe for reruns"
```
**Why NOT an issue:** Idempotency handles partial completion by design  
**Overlap check:** N/A - architectural choice  
**Correct action:** Count idempotency as covering partial completion edge cases

## Complete Pattern Inventory

**Purpose:** Eliminate interpretation variance by providing exhaustive lists. If it's not in this list, don't invent it. Match case-insensitive.

### Category 1: Setup Element Indicators (5 Types)

**Type 1 - Prerequisites Verification:**
- "verify prerequisites"
- "check requirements"
- "prerequisite check"
- "system requirements"
- Version check commands (`python --version`, `node --version`)
- Availability checks (`which python`, `command -v`)

**Type 2 - Environment Preparation:**
- "create environment"
- "setup environment"
- "venv", "virtualenv"
- "conda env"
- "nvm use"
- "source activate"
- ".venv", ".env"

**Type 3 - Dependency Installation:**
- "pip install"
- "npm install"
- "yarn install"
- "poetry install"
- "uv pip install"
- "cargo build"
- "go mod download"
- "bundle install"
- "requirements.txt"
- "package.json"

**Type 4 - Configuration Setup:**
- "configure", "configuration"
- "cp .env.example .env"
- "edit config"
- "set environment variables"
- "config.yaml", "settings.json"
- "DATABASE_URL", "API_KEY"

**Type 5 - Initial State Verification:**
- "verify setup"
- "smoke test"
- "sanity check"
- "test connection"
- "health check"
- "ping", "curl localhost"

**Regex Patterns:**
```regex
\b(verify|check)\s+(prerequisites?|requirements?|setup)\b
\b(create|setup|activate)\s+(environment|venv|virtualenv)\b
\b(pip|npm|yarn|poetry|uv|cargo|go\s+mod)\s+(install|sync|build|download)\b
\b(configure|configuration|config)\b
\bcp\s+\.env
\b(smoke|sanity)\s+(test|check)\b
\bhealth\s*check\b
```

### Category 2: Validation Phase Indicators (3 Types)

**Type 1 - Pre-execution Validation:**
- "before starting"
- "pre-flight check"
- "prerequisites met"
- "verify inputs"
- "check input files"
- "validate configuration"
- "ensure ready"

**Type 2 - During-execution Validation:**
- "progress check"
- "monitor progress"
- "watch logs"
- "tail -f"
- "check status"
- "no errors during"
- "resource usage"
- "htop", "top"

**Type 3 - Post-execution Validation:**
- "after completion"
- "verify output"
- "check results"
- "validate output"
- "integration test"
- "end-to-end test"
- "final verification"

**Regex Patterns:**
```regex
\b(before|pre[-\s]?(flight|execution|start)|prerequisites?\s+met)\b
\b(progress|monitor|watch|during|status)\s+(check|logs?|execution)\b
\btail\s+-f\b
\b(after|post[-\s]?(execution|completion)|final)\s+(verification|check|validation)\b
\b(verify|validate|check)\s+(output|results?)\b
```

### Category 3: Error Recovery Indicators (6 Scenarios)

**Scenario 1 - Input Validation Failure:**
- "invalid input"
- "validation error"
- "ValidationError"
- "malformed data"
- "parse error"
- "schema violation"

**Scenario 2 - Execution Errors:**
- "timeout"
- "crash"
- "exception"
- "exit code non-zero"
- "process killed"
- "OOM" (out of memory)
- "stack trace"

**Scenario 3 - External Dependency Failure:**
- "connection refused"
- "network error"
- "API error"
- "service unavailable"
- "503", "504"
- "timeout connecting"
- "DNS failure"

**Scenario 4 - Permission/Access Errors:**
- "permission denied"
- "access denied"
- "unauthorized"
- "403", "401"
- "authentication failed"
- "insufficient privileges"

**Scenario 5 - Resource Exhaustion:**
- "disk full"
- "out of memory"
- "resource exhausted"
- "quota exceeded"
- "rate limited"
- "too many connections"

**Scenario 6 - State Corruption:**
- "corrupted"
- "inconsistent state"
- "data integrity"
- "rollback required"
- "transaction failed"
- "deadlock"

**Regex Patterns:**
```regex
\b(invalid|validation|parse)\s*(input|error|failed)\b
\b(timeout|crash|exception|killed|OOM)\b
\b(connection|network|API|service)\s*(refused|error|unavailable|failed)\b
\b(permission|access|authentication)\s*(denied|failed|error)\b
\b(disk|memory|resource|quota)\s*(full|exhausted|exceeded)\b
\b(corrupted|inconsistent|integrity|rollback|deadlock)\b
```

### Category 4: Cleanup Indicators (4 Elements)

**Element 1 - Temporary Files:**
- "rm -rf /tmp/"
- "remove temp"
- "delete temporary"
- "cleanup temp"
- "*.tmp"
- "/tmp/process-*"

**Element 2 - Resources Released:**
- "stop service"
- "docker-compose down"
- "kill process"
- "close connection"
- "release lock"
- "shutdown"

**Element 3 - State Reset:**
- "reset state"
- "restore original"
- "revert changes"
- "rollback"
- "undo"
- "reset to baseline"

**Element 4 - Cleanup Verification:**
- "verify cleanup"
- "confirm removed"
- "check no leftover"
- "verify stopped"
- "ensure clean"

**Regex Patterns:**
```regex
\brm\s+(-rf?\s+)?(/tmp/|temp|temporary)\b
\b(stop|down|kill|close|release|shutdown)\s+(service|process|connection|lock)\b
\b(reset|restore|revert|rollback|undo)\s+(state|original|changes|baseline)\b
\b(verify|confirm|check|ensure)\s+(cleanup|removed|stopped|clean)\b
```

### Category 5: Edge Case Indicators (12 Types)

**Empty States (3):**
1. "empty database" / "no records"
2. "no users" / "first user"
3. "cold cache" / "cache miss"

**Concurrent Execution (3):**
4. "concurrent" / "parallel execution"
5. "race condition" / "lock"
6. "multiple instances" / "dual runs"

**Partial Completion (3):**
7. "interrupted" / "partial"
8. "resume" / "checkpoint"
9. "idempotent" / "rerun safe"

**Resource Constraints (3):**
10. "disk full" / "low disk"
11. "memory limit" / "low memory"
12. "network failure" / "offline"

**Regex Patterns:**
```regex
\b(empty|no)\s+(database|records?|users?|data)\b
\b(cold|clear|miss)\s*cache\b
\b(concurrent|parallel|simultaneous)\s+(execution|runs?|instances?)\b
\b(race\s+condition|lock|mutex|semaphore)\b
\b(interrupted|partial|incomplete)\s*(completion|execution|run)?\b
\b(resume|checkpoint|idempotent|rerun)\b
\b(disk|memory|network)\s+(full|limit|failure|offline)\b
```

### Ambiguous Cases Resolution

**Case 1: Setup via standard tool**

**Pattern:** "Run pytest" (no explicit environment setup)

**Ambiguity:** Is setup implicitly handled?

**Resolution Rule:**
- Standard tools (pytest, npm) handle their own setup
- Don't penalize if tool manages setup
- Still prefer explicit setup documentation

**Case 2: Error recovery in framework**

**Pattern:** "Use retry decorator with 3 attempts"

**Ambiguity:** Does framework recovery count?

**Resolution Rule:**
- Framework-level recovery = valid error handling
- Count as covered for that error type
- Document: "Error recovery via [framework]"

**Case 3: Cleanup not needed**

**Pattern:** Plan only reads data, creates no artifacts

**Ambiguity:** Is missing cleanup a gap?

**Resolution Rule:**
- Read-only operations don't need cleanup
- Don't penalize missing cleanup for read-only plans
- Flag: "Cleanup N/A (read-only)"

**Case 4: Edge cases by design**

**Pattern:** "Idempotent operations - safe for reruns"

**Ambiguity:** Does idempotency cover partial completion?

**Resolution Rule:**
- Idempotency addresses interrupted/partial completion
- Count as 3/3 partial completion edge cases covered
- Document: "Partial completion via idempotency"

**Case 5: Validation at phase level only**

**Pattern:** Each phase has verification, but tasks don't

**Ambiguity:** Is phase-level validation sufficient?

**Resolution Rule:**
- Phase-level validation = acceptable
- Covers all tasks within phase
- Count as 3/3 validation phases if each phase has pre/during/post

**Case 6: Error recovery referenced elsewhere**

**Pattern:** "Error handling: See Troubleshooting Guide"

**Ambiguity:** Does external reference count?

**Resolution Rule:**
- External reference to existing doc = partial credit
- Full credit requires inline recovery steps
- Count as 1 scenario (generic reference)

**Case 7: Implicit pre-execution validation**

**Pattern:** "Verify prerequisites in Phase 0"

**Ambiguity:** Is prerequisite check = pre-execution validation?

**Resolution Rule:**
- Prerequisites verification = pre-execution validation
- Count as present if Phase 0 has verification commands
- Same function, different label

**Case 8: Resource constraints out of scope**

**Pattern:** "Assuming adequate resources available"

**Ambiguity:** Is assumption = addressing edge case?

**Resolution Rule:**
- Assumption ≠ addressing edge case
- Need: what to do IF resources insufficient
- Don't count assumptions as coverage

## Anti-Pattern Examples (Common Mistakes)

**❌ WRONG (False Positive):**
- Flagged: "Missing cleanup section"
- Rationale given: "No cleanup documented"
- Problem: Plan is read-only analysis (no artifacts created)
- Impact: Incorrect -3 point deduction

**✅ CORRECT:**
- Not flagged for missing cleanup
- Rationale: Read-only operations don't require cleanup
- Condition: Would be flagged IF plan creates temp files or changes state

**❌ WRONG (False Positive):**
- Flagged: "Only 2 error scenarios documented"
- Rationale given: "Missing timeout, permission errors"
- Problem: Plan scope doesn't involve network or permissions
- Impact: Incorrect -2 point deduction for irrelevant scenarios

**✅ CORRECT:**
- Count scenarios relevant to plan scope
- Rationale: File-only plan doesn't need network error handling
- Condition: Would be flagged IF plan involves network/permissions

## Ambiguous Case Resolution Rules (REQUIRED)

**Purpose:** Provide deterministic scoring when completeness elements are borderline.

### Rule 1: Same-File Context
**Count element as present if:** Element explicitly documented in plan (may be in different section)  
**Count element as missing if:** No mention of element type anywhere in plan

### Rule 2: Adjectives Without Quantifiers
**Count as addressed if:** Specific steps, commands, or checks provided  
**Count as NOT addressed if:** Only vague mention ("handle errors", "clean up")

### Rule 3: Pattern Variations
**Count error recovery as complete if:** Detection AND recovery steps AND verification provided  
**Count error recovery as incomplete if:** Missing detection OR recovery OR verification

### Rule 4: Default Resolution
**Still uncertain after Rules 1-3?** → Count as missing/incomplete (conservative scoring)

### Borderline Cases Template

Document borderline decisions in your worksheet:

```markdown
### Element: "[Element Name]"
- **Decision:** Present [Y/N], Complete [Y/N]
- **Rule Applied:** [1/2/3/4]
- **Reasoning:** [Explain why this classification]
- **Alternative:** [Other interpretation and why rejected]
- **Confidence:** [HIGH/MEDIUM/LOW]
```

## Mandatory Counting Worksheet (REQUIRED)

**CRITICAL:** You MUST create and fill this worksheet BEFORE calculating score.

### Why This Is Required
- **Eliminates counting variance:** Same plan → same worksheet → same score
- **Prevents false negatives:** Checklist-based enumeration catches all gaps
- **Provides evidence:** Worksheet shows exactly what was counted

### Worksheet Template

**Setup Elements (0-5):**
| Element | Present? | Lines | Notes |
|---------|----------|-------|-------|
| Prerequisites verification | Y/N | | |
| Environment preparation | Y/N | | |
| Dependency installation | Y/N | | |
| Configuration setup | Y/N | | |
| Initial state verification | Y/N | | |
| **TOTAL** | | | **___/5** |

**Validation Phases (0-3):**
| Phase | Present? | Commands? | Expected Output? |
|-------|----------|-----------|------------------|
| Pre-execution | Y/N | Y/N | Y/N |
| During execution | Y/N | Y/N | Y/N |
| Post-execution | Y/N | Y/N | Y/N |
| **TOTAL** | | | **___/3** |

**Error Recovery Scenarios:**
| Scenario | Documented? | Has Recovery Steps? |
|----------|-------------|---------------------|
| Input validation failures | Y/N | Y/N |
| Execution errors (timeout, crash) | Y/N | Y/N |
| External dependency failures | Y/N | Y/N |
| Permission/access errors | Y/N | Y/N |
| Resource exhaustion | Y/N | Y/N |
| State corruption | Y/N | Y/N |
| **TOTAL WITH RECOVERY** | | **___** |

**Cleanup Elements (0-4):**
| Element | Present? |
|---------|----------|
| Temporary files removal | Y/N |
| Resources released | Y/N |
| State reset | Y/N |
| Verification of cleanup | Y/N |
| **TOTAL** | **___/4** |

**Edge Case Coverage (0-12):**
| Category | Item | Addressed? |
|----------|------|------------|
| Empty states | Empty DB | Y/N |
| Empty states | No users | Y/N |
| Empty states | Cold cache | Y/N |
| Concurrent | Dual runs | Y/N |
| Concurrent | Locks | Y/N |
| Concurrent | Races | Y/N |
| Partial completion | Interrupted | Y/N |
| Partial completion | Resume | Y/N |
| Partial completion | Idempotency | Y/N |
| Resources | Disk full | Y/N |
| Resources | Memory | Y/N |
| Resources | Network | Y/N |
| **TOTAL** | | **___/12** |

### Counting Protocol

1. Fill each section systematically
2. Calculate totals for each category
3. Use Score Decision Matrix to determine raw score
4. Include completed worksheet in review output

## Inter-Run Consistency Target

**Expected variance:** ±1 point per component

**Verification:**
- Use checklists with Y/N for each item
- Count only items explicitly documented
- Edge case coverage: use category table

**If variance exceeds threshold:**
- Re-verify using checklist tables
- Document borderline items
