# Dependencies Rubric (10 points)

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 2
**Points:** Raw × (2/2) = Raw × 1.0

## Scoring Criteria

### 10/10 (10 points): Perfect
- 5/5 dependency categories addressed
- 100% tools have versions specified
- Task ordering dependencies explicit
- Access requirements with verification
- Environment assumptions complete (6/6)

### 9/10 (9 points): Near-Perfect
- 5/5 dependency categories addressed
- 95-99% tools have versions
- Ordering explicit
- Access requirements with verification
- Environment assumptions 5-6/6

### 8/10 (8 points): Excellent
- 5/5 dependency categories addressed
- 90-94% tools have versions
- Ordering explicit
- Access requirements stated
- Environment assumptions 5/6

### 7/10 (7 points): Good
- 4/5 dependency categories addressed
- 85-89% tools have versions
- Most ordering clear
- Access requirements stated
- Environment assumptions 4/6

### 6/10 (6 points): Acceptable
- 4/5 dependency categories addressed
- 80-84% tools have versions
- Most ordering clear
- Access requirements stated
- Environment assumptions 3-4/6

### 5/10 (5 points): Borderline
- 3/5 dependency categories addressed
- 70-79% tools have versions
- Some ordering clear
- Partial access requirements
- Environment assumptions 2-3/6

### 4/10 (4 points): Needs Work
- 3/5 dependency categories addressed
- 60-69% tools have versions
- Some ordering clear
- Partial access requirements
- Environment assumptions 2/6

### 3/10 (3 points): Poor
- 2/5 dependency categories addressed
- 50-59% tools have versions
- Ordering unclear
- Access requirements missing
- Environment assumptions 1/6

### 2/10 (2 points): Very Poor
- 2/5 dependency categories addressed
- 40-49% tools have versions
- Ordering unclear
- Access requirements missing
- Environment assumptions 0-1/6

### 1/10 (1 point): Inadequate
- 1/5 dependency categories addressed
- 30-39% tools have versions
- No ordering
- No access requirements
- Environment assumptions 0/6

### 0/10 (0 points): No Dependencies
- 0/5 dependency categories addressed
- <30% tools have versions
- No ordering
- No access requirements
- No environment assumptions

## Counting Definitions

### Dependency Categories

**Five categories (count 0-5):**

**Dependency Category Checklist:**
- 1. Tool dependencies: Present? Versions specified?
- 2. Access requirements: Present? Verification commands?
- 3. Ordering dependencies: Present? Explicit sequence?
- 4. Environment assumptions: Present? Complete?
- 5. Data dependencies: Present? Verification commands?

**Scoring by categories:**
- 5/5 categories: Full credit
- 4/5 categories: 4/5 maximum
- 3/5 categories: 3/5 maximum
- 2/5 categories: 2/5 maximum
- 0-1/5 categories: 1/5 maximum

### Tool Version Coverage

**Count tools with explicit versions:**

**Tool Version Checklist (example):**
- Python: Listed? Version specified (e.g., 3.11+)?
- Node.js: Listed? Version specified (e.g., 20+)?
- PostgreSQL: Listed? Version specified (e.g., 15+)?
- Docker: Listed? Version specified (e.g., 24+)?

**Coverage calculation:**
```
Version coverage % = (tools with versions / tools listed) × 100
```

### Ordering Clarity

**Check for each task dependency:**
- Is dependency stated explicitly?
- Is order unambiguous?
- Can agent determine sequence?

**Scoring:**
- All explicit with rationale: Full credit
- All explicit, no rationale: -0.5 points
- Some implicit: -1 point
- Mostly unclear: -2 points

### Access Requirements

**Required elements:**
- Credential types needed
- Permission levels
- Verification commands

**Scoring:**
- Complete with verification: Full credit
- Listed without verification: -1 point
- Missing: -2 points

### Environment Assumptions

**Required elements:**

**Environment Element Checklist:**
- Operating system: Documented?
- Shell type: Documented?
- Network access: Documented?
- Disk space: Documented?
- Memory: Documented?
- Available ports: Documented?

**Scoring by coverage:**
- 5-6/6 elements: Full credit
- 3-4/6 elements: -1 point
- 1-2/6 elements: -2 points
- 0/6 elements: -3 points

## Score Decision Matrix

**Score Tier Criteria:**
- **10/10 (10 pts):** 5/5 categories, 100% tool versions, explicit ordering, complete access, 6/6 environment
- **9/10 (9 pts):** 5/5 categories, 95-99% tool versions, explicit ordering, access with verification, 5-6/6 environment
- **8/10 (8 pts):** 5/5 categories, 90-94% tool versions, explicit ordering, access stated, 5/6 environment
- **7/10 (7 pts):** 4/5 categories, 85-89% tool versions, mostly explicit ordering, access stated, 4/6 environment
- **6/10 (6 pts):** 4/5 categories, 80-84% tool versions, mostly explicit ordering, access stated, 3-4/6 environment
- **5/10 (5 pts):** 3/5 categories, 70-79% tool versions, some ordering, partial access, 2-3/6 environment
- **4/10 (4 pts):** 3/5 categories, 60-69% tool versions, some ordering, partial access, 2/6 environment
- **3/10 (3 pts):** 2/5 categories, 50-59% tool versions, unclear ordering, missing access, 1/6 environment
- **2/10 (2 pts):** 2/5 categories, 40-49% tool versions, unclear ordering, missing access, 0-1/6 environment
- **1/10 (1 pt):** 1/5 categories, 30-39% tool versions, no ordering, missing access, 0/6 environment
- **0/10 (0 pts):** 0/5 categories, <30% tool versions, no ordering, no access, no environment

## Dependency Category Details

### 1. Tool Dependencies

```markdown
## Prerequisites (Example - Complete)

**Required tools:**
- Python 3.11+ (check: python --version ≥ 3.11)
- Node.js 20+ (check: node --version ≥ 20)
- PostgreSQL 15+ (check: psql --version ≥ 15)
- Docker 24+ (check: docker --version ≥ 24)
- uv 0.1.0+ (check: uv --version ≥ 0.1)

**Installation (if missing):**
```bash
brew install python@3.11 node@20 postgresql@15 docker
curl -LsSf https://astral.sh/uv/install.sh | sh
```
```

### 2. Access Requirements

```markdown
## Required Access (Example - Complete)

- AWS account with S3 write permissions
- GitHub personal access token (repo scope)
- Production database read access
- Slack bot token for notifications

**Verification:**
```bash
aws s3 ls  # Should list buckets
gh auth status  # Should show logged in
psql $PROD_DB_URL -c "SELECT 1"  # Should return 1
```
```

### 3. Ordering Dependencies

```markdown
## Task Dependencies (Example - Complete)

**Execution order:**
1. Install deps (no dependencies)
2. Run tests (depends: step 1)
3. Build app (depends: step 1)
4. Deploy staging (depends: steps 2 AND 3)
5. Deploy prod (depends: step 4)

**Parallelization:**
- Steps 2 and 3 can run simultaneously
- Step 4 requires BOTH 2 and 3 complete

**Dependency graph:**
```
1 -> 2 --+
         +-> 4 -> 5
1 -> 3 --+
```
```

### 4. Environment Assumptions

```markdown
## Environment (Example - Complete)

- Operating system: macOS 12+ or Ubuntu 22.04+
- Shell: Bash 5+ or Zsh 5.8+
- Network: Internet access required (for package downloads)
- Disk space: ≥5GB free
- Memory: ≥8GB RAM
- Ports: 8000, 5432, 6379 available

**Verification:**
```bash
uname -s  # Darwin or Linux
echo $0   # bash or zsh
ping -c1 google.com  # Network works
df -h .   # Check disk space
```
```

### 5. Data Dependencies

```markdown
## Required Data (Example - Complete)

- Database: users table with ≥1000 rows
- Storage: S3 bucket 'myapp-uploads' exists
- Config: config/production.yml present
- Certs: /etc/ssl/certs/myapp.crt valid (not expired)

**Verification:**
```bash
psql -c "SELECT COUNT(*) FROM users" | grep -q "1000"
aws s3 ls s3://myapp-uploads/
test -f config/production.yml && echo "OK"
openssl x509 -in /etc/ssl/certs/myapp.crt -noout -checkend 0
```
```

## Dependency Tracking Table

Use during review:

**Dependency Tracking Checklist:**
- Tools: Present? Complete? Missing items?
- Access: Present? Complete? Missing items?
- Ordering: Present? Complete? Issues?
- Environment: Present? Complete? Missing items?
- Data: Present? Complete? Missing items?

## Worked Example

**Target:** Deployment plan

### Step 1: Check Categories

**Category Assessment:**
- Tools: Yes, partial (80% versions)
- Access: Yes, no verification
- Ordering: Yes, explicit
- Environment: Partial (2/6)
- Data: No - Not mentioned

**Count:** 3/5 categories complete

### Step 2: Tool Version Coverage

**Tool Version Assessment:**
- Python: Yes (3.11+)
- Node.js: Yes (20+)
- PostgreSQL: No - None specified
- Docker: Yes (24+)
- uv: No - None specified

**Coverage:** 3/5 = 60%

### Step 3: Ordering Assessment

```markdown
Tasks listed with "depends on" statements
Sequence is unambiguous
Parallelization noted
```

**Quality:** Explicit (Full credit)

### Step 4: Access Assessment

```markdown
Listed: AWS, GitHub, Database
No verification commands provided
```

**Quality:** Listed without verification (-1 point)

### Step 5: Environment Assessment

**Environment Inventory:**
- OS: Yes
- Shell: No
- Network: Yes
- Disk: No
- Memory: No
- Ports: No

**Coverage:** 2/6 (-2 points)

### Step 6: Calculate Score

**Component Assessment:**
- Categories: 3/5 = 3/5 baseline
- Tool versions: 60% = Within range
- Ordering: Explicit = Full credit
- Access: No verification = -1 point
- Environment: 2/6 = -2 points

**Total deductions:** -3 points from 3/5 baseline
**Final:** 5/10 (5 points)

### Step 7: Document in Review

```markdown
## Dependencies: 5/10 (5 points)

**Categories addressed:** 3/5
- [YES] Tool dependencies (60% versioned)
- [PARTIAL] Access requirements (no verification)
- [YES] Ordering dependencies (explicit)
- [PARTIAL] Environment assumptions (2/6 elements)
- [NO] Data dependencies (missing)

**Tool version coverage:** 60%
- Missing: PostgreSQL version, uv version

**Access verification:** Missing
- AWS, GitHub, DB listed but no verification commands

**Environment:** Partial
- Missing: Shell, disk, memory, ports

**Priority fixes:**
1. Add data dependencies section
2. Add version for PostgreSQL, uv
3. Add access verification commands
4. Complete environment assumptions
```

## Dependencies Checklist

During review, verify:

- [ ] All tools listed with versions
- [ ] Installation commands for tools
- [ ] Access requirements stated
- [ ] Credentials verification commands
- [ ] Task ordering dependencies clear
- [ ] Parallel execution opportunities identified
- [ ] Environment assumptions explicit (OS, shell, network, disk, memory, ports)
- [ ] Data dependencies listed
- [ ] Data verification commands provided

## Inter-Run Consistency Target

**Expected variance:** ±1 category

**Verification:**
- Use 5-category checklist
- Count versioned tools explicitly
- Use environment element checklist

**If variance exceeds threshold:**
- Re-verify using category table
- Apply completeness criteria strictly
