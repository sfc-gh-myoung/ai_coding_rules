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

## Score Decision Matrix (ENHANCED)

**Purpose:** Convert dependency category coverage and specification quality into dimension score. No interpretation needed - just look up the tier.

### Input Values

From completed worksheet:
- **Categories Addressed:** Count of 5 types (Tool/Access/Ordering/Environment/Data)
- **Tool Version Coverage %:** Tools with versions / Total tools × 100
- **Ordering Clarity:** Explicit with rationale / Explicit without / Some implicit / Unclear
- **Access Requirements:** Complete with verification / Listed only / Missing
- **Environment Assumptions:** Count of 6 elements documented

### Scoring Table

| Categories | Versions % | Ordering | Access | Environment | Tier | Raw Score | × Weight | Points |
|------------|------------|----------|--------|-------------|------|-----------|----------|--------|
| 5/5 | 100% | Explicit+rationale | Complete+verify | 6/6 | Perfect | 10/10 | × 1 | 10 |
| 5/5 | 95-99% | Explicit | Complete+verify | 5-6/6 | Near-Perfect | 9/10 | × 1 | 9 |
| 5/5 | 90-94% | Explicit | Stated | 5/6 | Excellent | 8/10 | × 1 | 8 |
| 4/5 | 85-89% | Mostly explicit | Stated | 4/6 | Good | 7/10 | × 1 | 7 |
| 4/5 | 80-84% | Mostly explicit | Stated | 3-4/6 | Acceptable | 6/10 | × 1 | 6 |
| 3/5 | 70-79% | Some | Partial | 2-3/6 | Borderline | 5/10 | × 1 | 5 |
| 3/5 | 60-69% | Some | Partial | 2/6 | Below Standard | 4/10 | × 1 | 4 |
| 2/5 | 50-59% | Unclear | Missing | 1/6 | Poor | 3/10 | × 1 | 3 |
| 2/5 | 40-49% | Unclear | Missing | 0-1/6 | Very Poor | 2/10 | × 1 | 2 |
| 1/5 | 30-39% | None | Missing | 0/6 | Critical | 1/10 | × 1 | 1 |
| 0/5 | <30% | None | Missing | 0/6 | No Dependencies | 0/10 | × 1 | 0 |

### Tie-Breaking Algorithm (Deterministic)

**When category count falls exactly on tier boundary:**

1. **Check Version Coverage:** If versions > tier requirement → HIGHER tier
2. **Check Ordering Clarity:** If ordering is explicit with rationale → HIGHER tier
3. **Check Access Verification:** If access includes verification commands → HIGHER tier
4. **Default:** LOWER tier (conservative - missing dependencies cause failures)

### Edge Cases

**Edge Case 1: Standard system tools (no version needed)**
- **Example:** "git, curl, bash" without versions
- **Rule:** Standard system tools don't penalize version coverage
- **Rationale:** These are available on all systems at compatible versions

**Edge Case 2: Implicit ordering from phase structure**
- **Example:** "Phase 1 before Phase 2" without explicit statement
- **Rule:** Count phase ordering as implicit but acceptable
- **Rationale:** Phase structure provides ordering

**Edge Case 3: Minimum versions vs exact versions**
- **Example:** "Python 3.11+" vs "Python 3.11.4"
- **Rule:** Both count as versioned
- **Rationale:** Minimum version is often more appropriate

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

## Non-Issues (Do NOT Count)

**Purpose:** Eliminate false positives by explicitly defining what is NOT a dependencies issue.

### Pattern 1: Minimum Version Specified

**Example:**
```markdown
"Python 3.11+" (with + suffix)
```
**Why NOT an issue:** "+" indicates minimum version, acceptable specification  
**Overlap check:** N/A - version constraint provided  
**Correct action:** Count as versioned (meets "version specified" requirement)

### Pattern 2: Standard System Tools (No Version Needed)

**Example:**
```markdown
"Uses: bash, curl, grep, sed"
```
**Why NOT an issue:** System utilities are standard, version rarely matters  
**Overlap check:** N/A - ubiquitous tools  
**Correct action:** Do not penalize missing versions for standard *nix utilities

### Pattern 3: Ordering Implied by Phase Structure

**Example:**
```markdown
Phase 1: Setup
Phase 2: Implementation (implicitly depends on Phase 1)
Phase 3: Validation
```
**Why NOT an issue:** Phase numbering implies sequential ordering  
**Overlap check:** Not Executability - execution order is clear  
**Correct action:** Count phase structure as explicit ordering

### Pattern 4: Data Dependencies Implied by Task Type

**Example:**
```markdown
Task: "Migrate users table"
```
**Why NOT an issue:** Migration implies users table must exist  
**Overlap check:** May be Completeness if setup section missing, but not Dependencies  
**Correct action:** Implied dependencies acceptable for domain-standard operations

## Complete Pattern Inventory

**Purpose:** Eliminate interpretation variance by providing exhaustive lists. If it's not in this list, don't invent it. Match case-insensitive.

### Category 1: Tool Dependency Indicators (25 Patterns)

**Explicit Tool References (count as present):**
1. "Python X.Y+"
2. "Node.js X+"
3. "npm X+"
4. "Docker X+"
5. "PostgreSQL X+"
6. "MySQL X+"
7. "Redis X+"
8. "MongoDB X+"
9. "git"
10. "curl"
11. "wget"
12. "make"
13. "cargo"
14. "go"
15. "java"
16. "pip"
17. "poetry"
18. "uv"
19. "yarn"
20. "pnpm"
21. "brew"
22. "apt"
23. "yum"
24. "dnf"
25. "pacman"

**Regex Patterns:**
```regex
\b(python|node|npm|docker|postgres|mysql|redis|mongo|git|curl|make|cargo|go|java|pip|poetry|uv|yarn)\s*(\d+\.?\d*\.?\d*\+?)?\b
\b(brew|apt|yum|dnf|pacman)\s+(install|update)\b
```

**Context Rules:**
- Tool name + version → Count as versioned
- Tool name only (no version) → Count as unversioned
- Exception: Standard system tools (git, curl, grep, sed) don't need versions

### Category 2: Access Requirement Indicators (20 Patterns)

**Credential/Permission Patterns:**
1. "API key"
2. "access token"
3. "personal access token"
4. "PAT"
5. "secret key"
6. "AWS credentials"
7. "AWS_ACCESS_KEY"
8. "AWS_SECRET_KEY"
9. "service account"
10. "SSH key"
11. "database password"
12. "DB_PASSWORD"
13. "authentication"
14. "authorization"
15. "permission"
16. "role"
17. "IAM"
18. "RBAC"
19. "OAuth"
20. "credentials"

**Regex Patterns:**
```regex
\b(api|access|secret|auth)\s*(key|token)\b
\b(AWS|GCP|Azure|GitHub|GitLab)\s*(credentials?|token|key)\b
\bservice\s+account\b
\bSSH\s*key\b
\b(DB|DATABASE)_(PASSWORD|USER|HOST|URL)\b
\b(IAM|RBAC|OAuth)\b
```

**Context Rules:**
- Credential mentioned → Check for verification command
- With verification command → Complete access requirement
- Without verification command → Incomplete (flag)

### Category 3: Ordering Dependency Indicators (15 Patterns)

**Explicit Ordering Patterns:**
1. "depends on"
2. "requires"
3. "after"
4. "before"
5. "must complete first"
6. "prerequisite"
7. "blocked by"
8. "blocks"
9. "can run in parallel"
10. "parallelizable"
11. "sequential"
12. "in order"
13. "step X then step Y"
14. "Phase 1, Phase 2"
15. "→" (arrow notation)

**Regex Patterns:**
```regex
\b(depends?\s+on|requires?|after|before|blocked\s+by|blocks)\b
\bstep\s+\d+\s+(then|before|after)\s+step\s+\d+\b
\b(sequential|parallel|in\s+order)\b
\bphase\s+\d+\b
```

**Context Rules:**
- Explicit "depends on" → Clear ordering
- Phase numbering → Implicit sequential ordering
- No ordering language + numbered list → Weak implicit ordering

### Category 4: Environment Assumption Patterns (6 Categories)

**Operating System:**
- "macOS", "Darwin", "Mac OS X"
- "Ubuntu", "Debian", "Linux"
- "Windows", "Win10", "Win11"
- "Unix-like", "POSIX"

**Shell Type:**
- "bash", "zsh", "sh"
- "PowerShell", "cmd"
- "fish", "tcsh"

**Network Access:**
- "internet access", "network access"
- "offline", "air-gapped"
- "VPN required", "proxy"

**Disk Space:**
- "X GB free", "disk space"
- "storage requirement"

**Memory:**
- "X GB RAM", "memory"
- "minimum memory"

**Ports:**
- "port X available", "ports"
- "8080", "3000", "5432", "6379"

**Regex Patterns:**
```regex
\b(macOS|Ubuntu|Linux|Windows|POSIX)\b
\b(bash|zsh|sh|PowerShell)\b
\b(internet|network)\s+access\b
\b\d+\s*(GB|MB|TB)\s+(free|available|disk|RAM|memory)\b
\bport\s+\d+\b
```

### Category 5: Standard System Tools (No Version Needed)

**Tools that don't require version specification:**
1. git
2. curl
3. wget
4. grep
5. sed
6. awk
7. cat
8. ls
9. mv
10. cp
11. rm
12. mkdir
13. chmod
14. chown
15. tar
16. gzip
17. unzip
18. ssh
19. scp
20. rsync

**Context Rules:**
- These tools are ubiquitous and backward-compatible
- Don't penalize missing versions for standard *nix utilities
- DO penalize if exotic flags used that require specific version

### Ambiguous Cases Resolution

**Case 1: Minimum version vs exact version**

**Pattern:** "Python 3.11+" vs "Python 3.11.4"

**Ambiguity:** Is minimum version sufficient specification?

**Resolution Rule:**
- Both count as versioned
- Minimum version (X+) is often more appropriate for dependencies
- Exact version needed only for reproducibility requirements

**Case 2: Version in package file vs plan**

**Pattern:** Version in requirements.txt but not in plan text

**Ambiguity:** Does external file count?

**Resolution Rule:**
- If plan references "see requirements.txt" → Count as versioned
- If plan doesn't reference file → Count as unversioned in plan
- Flag: "Versions in requirements.txt, not in plan prerequisites"

**Case 3: Implicit tool from command**

**Pattern:** "Run: pytest tests/" (pytest not listed in prerequisites)

**Ambiguity:** Is tool implicitly a dependency?

**Resolution Rule:**
- Tools used in commands ARE dependencies
- If not in prerequisites section → Flag as missing dependency
- Add to inventory: "pytest used at line X, not in prerequisites"

**Case 4: Ordering from document structure**

**Pattern:** Phase 1, Phase 2, Phase 3 (no explicit "depends on")

**Ambiguity:** Is phase structure explicit ordering?

**Resolution Rule:**
- Phase numbering = implicit but acceptable ordering
- Count as "ordering present" (implicit)
- Would be "explicit" if "Phase 2 depends on Phase 1" stated

**Case 5: Access verification in different section**

**Pattern:** Access requirements in Prerequisites, verification in Validation

**Ambiguity:** Is separated verification acceptable?

**Resolution Rule:**
- Verification in same plan = acceptable
- Search entire plan before flagging missing verification
- Flag only if NO verification anywhere

**Case 6: Environment assumptions implied**

**Pattern:** "Run on local development machine"

**Ambiguity:** Does this count as environment documentation?

**Resolution Rule:**
- Vague reference = NOT documented
- Need specific: OS, shell, disk, memory, ports, network
- "Local machine" ≠ environment specification

**Case 7: Data dependency from task description**

**Pattern:** "Migrate users table" (implies users table exists)

**Ambiguity:** Is implied data dependency documented?

**Resolution Rule:**
- Implied dependencies acceptable for domain-standard operations
- Explicit verification preferred ("Verify users table has ≥1000 rows")
- Don't penalize obvious implications

**Case 8: Credential placeholder vs actual requirement**

**Pattern:** "$DB_PASSWORD" in example code

**Ambiguity:** Is this a documented access requirement?

**Resolution Rule:**
- Env var placeholder = access requirement identified
- Still need: how to obtain, verification command
- Partial credit: requirement identified, verification missing

## Anti-Pattern Examples (Common Mistakes)

**❌ WRONG (False Positive):**
- Flagged: "Node.js 20+" as "version not specified"
- Rationale given: "Exact version needed"
- Problem: Minimum version constraint is valid specification
- Impact: Tool version coverage % incorrectly reduced

**✅ CORRECT:**
- "20+" counted as versioned
- Rationale: Minimum version is valid constraint
- Condition: Would be flagged IF just "Node.js" without any version

**❌ WRONG (False Positive):**
- Flagged: "Missing ordering dependencies"
- Rationale given: "No explicit 'depends on' statements"
- Problem: Plan uses Phase 1/2/3 structure (implicit ordering)
- Impact: Ordering marked as "unclear" incorrectly

**✅ CORRECT:**
- Phase structure counts as explicit ordering
- Rationale: Sequential phases = sequential dependencies
- Condition: Would be flagged IF tasks out of order or no structure

## Ambiguous Case Resolution Rules (REQUIRED)

**Purpose:** Provide deterministic scoring when dependency documentation is borderline.

### Rule 1: Same-File Context
**Count category as present if:** At least one item in that category documented  
**Count category as missing if:** Zero items in that category

### Rule 2: Adjectives Without Quantifiers
**Count version as specified if:** Any version constraint (exact, minimum with +, range)  
**Count version as NOT specified if:** Tool listed without any version information

### Rule 3: Pattern Variations
**Count ordering as explicit if:** "depends on", phase numbers, or "after X" stated  
**Count ordering as implicit if:** Only sequential listing without dependency notation

### Rule 4: Default Resolution
**Still uncertain after Rules 1-3?** → Count as missing/unspecified (conservative scoring)

### Borderline Cases Template

Document borderline decisions in your worksheet:

```markdown
### Category/Tool: "[Name]"
- **Decision:** Present [Y/N], Version specified [Y/N], Complete [Y/N]
- **Rule Applied:** [1/2/3/4]
- **Reasoning:** [Explain why this classification]
- **Alternative:** [Other interpretation and why rejected]
- **Confidence:** [HIGH/MEDIUM/LOW]
```

## Mandatory Counting Worksheet (REQUIRED)

**CRITICAL:** You MUST create and fill this worksheet BEFORE calculating score.

### Worksheet Template

**Dependency Categories (0-5):**
| Category | Present? | Complete? | Missing Items |
|----------|----------|-----------|---------------|
| Tool dependencies | Y/N | Y/N | |
| Access requirements | Y/N | Y/N | |
| Ordering dependencies | Y/N | Y/N | |
| Environment assumptions | Y/N | Y/N | |
| Data dependencies | Y/N | Y/N | |
| **TOTAL** | | | **___/5** |

**Tool Version Coverage:**
| Tool | Listed? | Version Specified? |
|------|---------|-------------------|
| [Tool 1] | Y/N | Y/N |
| [Tool 2] | Y/N | Y/N |
| **COVERAGE** | | **___% versioned** |

**Environment Elements (0-6):**
| Element | Documented? |
|---------|-------------|
| Operating system | Y/N |
| Shell type | Y/N |
| Network access | Y/N |
| Disk space | Y/N |
| Memory | Y/N |
| Available ports | Y/N |
| **TOTAL** | **___/6** |

### Counting Protocol

1. Fill each section systematically
2. Calculate coverage percentages
3. Use Score Decision Matrix to determine raw score
4. Include completed worksheet in review output

## Inter-Run Consistency Target

**Expected variance:** ±1 category

**Verification:**
- Use 5-category checklist
- Count versioned tools explicitly
- Use environment element checklist

**If variance exceeds threshold:**
- Re-verify using category table
- Apply completeness criteria strictly
