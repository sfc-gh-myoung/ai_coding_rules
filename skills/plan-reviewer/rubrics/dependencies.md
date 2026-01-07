# Dependencies Rubric (10 points)

## Scoring Criteria

### 5/5 (10 points): Excellent
- All prerequisites listed
- Tool versions specified
- Ordering dependencies clear
- Access requirements stated
- Environment assumptions explicit

### 4/5 (8 points): Good
- Most prerequisites listed
- Most versions specified
- Ordering mostly clear

### 3/5 (6 points): Acceptable
- Some prerequisites listed
- Some versions specified
- Some ordering clear

### 2/5 (4 points): Needs Work
- Few prerequisites listed
- Few versions specified
- Ordering unclear

### 1/5 (2 points): Poor
- Prerequisites missing
- No versions
- No ordering

## Dependency Categories

### 1. Tool Dependencies

List all required tools with versions:

**Good example:**
```markdown
## Prerequisites

**Required tools:**
- Python 3.11+ (check: python --version)
- Node.js 20+ (check: node --version)
- PostgreSQL 15+ (check: psql --version)
- Docker 24+ (check: docker --version)
- uv 0.1.0+ (check: uv --version)

**Installation (if missing):**
```bash
brew install python@3.11 node@20 postgresql@15 docker
curl -LsSf https://astral.sh/uv/install.sh | sh
```
```

### 2. Access Requirements

State required permissions/credentials:

**Good example:**
```markdown
## Required Access

- AWS account with S3 write permissions
- GitHub personal access token (repo scope)
- Production database read access
- Slack bot token for notifications

**Verification:**
```bash
aws s3 ls  # Should list buckets
gh auth status  # Should show logged in
psql $PROD_DB_URL -c "SELECT 1"  # Should connect
```
```

### 3. Ordering Dependencies

Specify task execution order:

**Good example:**
```markdown
## Task Dependencies

```
graph TD
  A[Install deps] --> B[Run tests]
  A --> C[Build app]
  B --> D[Deploy staging]
  C --> D
  D --> E[Deploy prod]
```

**Execution order:**
1. Install deps (no dependencies)
2. Run tests (depends: install deps)
3. Build app (depends: install deps)
4. Deploy staging (depends: tests + build)
5. Deploy prod (depends: staging deploy)

**Can parallelize:** Tests and build can run simultaneously
```

### 4. Environment Assumptions

State assumed environment configuration:

**Good example:**
```markdown
## Environment Assumptions

- Operating system: macOS or Linux (not Windows)
- Shell: Bash or Zsh
- Network: Internet access required
- Disk space: ≥5GB free
- Memory: ≥8GB RAM
- Ports: 8000, 5432 available
```

### 5. Data Dependencies

List required data or state:

**Good example:**
```markdown
## Required Data

- Database contains user table (≥1000 rows)
- S3 bucket 'myapp-uploads' exists
- Config file: config/production.yml present
- SSL cert: /etc/ssl/certs/myapp.crt valid

**Verification:**
```bash
psql -c "SELECT COUNT(*) FROM users" | grep -q "1000"
aws s3 ls s3://myapp-uploads/
test -f config/production.yml
openssl x509 -in /etc/ssl/certs/myapp.crt -noout -dates
```
```

## Dependency Tracking Table

Use during review:

| Category | Dependencies Listed | Complete? | Versions? | Notes |
|----------|---------------------|-----------|-----------|-------|
| Tools | Python, Node | ⚠️  Partial | ✅ Yes | Missing: PostgreSQL |
| Access | AWS, GitHub | ✅ Complete | N/A | All listed |
| Ordering | 5 tasks | ✅ Complete | N/A | Dependencies clear |
| Environment | OS, disk | ⚠️  Partial | N/A | Missing: network |
| Data | Database | ✅ Complete | N/A | Verification provided |

## Scoring Formula

```
Base score = 5/5 (10 points)

Dependency categories:
  All 5 categories addressed: 5/5 (10 points)
  4/5 categories: 4/5 (8 points)
  3/5 categories: 3/5 (6 points)
  2/5 categories: 2/5 (4 points)
  ≤1 category: 1/5 (2 points)

Additional deductions:
  Missing tool versions: -0.5 per tool (up to -2)
  Unclear ordering: -1 point
  No access requirements: -1 point

Minimum score: 1/5 (2 points)
```

## Common Dependency Issues

### Issue 1: Missing Tool Versions

**Problem:**
```markdown
Prerequisites: Python, PostgreSQL
```

**Fix:**
```markdown
Prerequisites:
- Python 3.11+ (check: python --version ≥ 3.11.0)
- PostgreSQL 15+ (check: psql --version ≥ 15.0)
```

### Issue 2: No Access Requirements

**Problem:**
```markdown
Task: Deploy to production
(No mention of credentials)
```

**Fix:**
```markdown
## Required Access

Before deploying, verify you have:
- AWS credentials configured: aws sts get-caller-identity
- Production deploy permissions: aws iam get-user
- Slack webhook URL: echo $SLACK_WEBHOOK_URL

If missing, request from ops team (Slack: #ops-requests)
```

### Issue 3: Unclear Ordering

**Problem:**
```markdown
Tasks:
1. Deploy app
2. Run migrations
3. Build Docker image
```
→ Wrong order! (Deploy before build?)

**Fix:**
```markdown
Tasks (in order):
1. Build Docker image
2. Run migrations
3. Deploy app (depends: steps 1+2 complete)

Rationale: Must build before deploy, migrate before deploy to avoid downtime
```

### Issue 4: Missing Environment Assumptions

**Problem:**
```markdown
Run: make install
(Assumes make is installed)
```

**Fix:**
```markdown
## Prerequisites

**Build tools:**
- make (check: make --version)
- gcc/clang (check: gcc --version)

**If missing:**
- macOS: xcode-select --install
- Ubuntu: sudo apt install build-essential
- Fedora: sudo dnf groupinstall "Development Tools"
```

## Dependency Checklist

During review, verify:

- [ ] All tools listed with versions
- [ ] Installation commands for tools
- [ ] Access requirements stated
- [ ] Credentials verification commands
- [ ] Task ordering dependencies clear
- [ ] Parallel execution opportunities identified
- [ ] Environment assumptions explicit
- [ ] OS requirements stated
- [ ] Network requirements stated
- [ ] Data dependencies listed
- [ ] Data verification commands provided
