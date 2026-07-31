---
schema_version: v3.5
rule_version: v4.0.0
description: 'Deploying and managing containerized apps on SPCS: compute pools, service
  specs, monitoring, and troubleshooting.'
last_updated: 2026-07-15
keywords:
- kw:Snowpark Container Services
- kw:compute pool instance families
- kw:OCI image deployment
- kw:service specification YAML
- kw:platform events monitoring
- kw:GPU workload configuration
- kw:SPCS
token_budget: ~3550
context_tier: High
depends:
  required:
  - 100-snowflake-core.md
  optional:
  - 105-snowflake-cost-governance.md
  - 111-snowflake-observability-core.md
  - 119-snowflake-warehouse-management.md
---
# Snowflake Snowpark Container Services (SPCS)

## Scope

**What This Rule Covers:**
Deploying and managing containerized apps on SPCS: compute pools, service specs, monitoring, and troubleshooting.

**When to Load This Rule:**
- Deploying containers on Snowflake SPCS
- Creating/configuring compute pools
- Troubleshooting SPCS services
- GPU-enabled ML/AI workloads

## References

### External Documentation
- [SPCS Overview](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/overview)
- [Service Specification](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/specification-reference)
- [Platform Events](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/platform-events)

## Contract

### Inputs and Prerequisites
- SPCS-enabled account with compute pool
- Image repository access
- Service spec YAML file

### Mandatory
- OCI-compliant images
- Semantic versioning (v1.2.3)
- Health check endpoints
- Resource limits in specs
- Structured logging to stdout/stderr
- Snowflake secret management

### Forbidden
- `latest` tag in production
- Hardcoded secrets in images/specs
- Exposing internal services publicly without auth
- New DB connections per request
- Processing large datasets entirely in memory
- Omitting resource limits

### Execution Steps

> **Investigation Required:** Run `SHOW COMPUTE POOLS` and `DESCRIBE COMPUTE POOL <name>` to verify available GPU types and node limits before creating services.

1. Verify SPCS: `SHOW PARAMETERS LIKE 'ENABLE_SNOWPARK_CONTAINER_SERVICES' IN ACCOUNT;`
2. Check pool: `SHOW COMPUTE POOLS;`
3. Verify image: `SHOW IMAGES IN IMAGE REPOSITORY <repo>;`
4. Deploy: `CREATE SERVICE ... FROM @stage SPECIFICATION = '...'`
5. Monitor: Check platform events for READY
6. Test health endpoint
7. Verify logs: `SYSTEM$GET_SERVICE_LOGS()`

### Output Format
Service spec YAML, CREATE SERVICE SQL, health check implementation

### Validation
**Pre-Task Checks:**
- SPCS enabled, compute pool exists
- Image with semantic version tag
- Spec includes resource limits
- Secrets via Snowflake objects

**Success Criteria:**
- Status READY in platform events
- Health endpoint returns 200 OK
- No OOMKilled events

### Post-Execution Checklist
- [ ] Compute pool sized appropriately
- [ ] Image tagged with version (not `latest`)
- [ ] Resource limits specified
- [ ] Health check responding
- [ ] LOG_LEVEL configured
- [ ] Service status READY

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Oversized Compute Pools
```sql
-- WRONG: 5 GPU nodes for 10 requests/day
CREATE COMPUTE POOL pool MIN_NODES=5 MAX_NODES=10 INSTANCE_FAMILY=GPU_NV_M;
```
**Problem:** Massive cost overrun, wasted resources, poor utilization.

**Correct Pattern:**
```sql
-- AWS/Azure (current-gen general compute)
CREATE COMPUTE POOL pool MIN_NODES=1 MAX_NODES=3 INSTANCE_FAMILY=GEN_X64_G2_4 AUTO_SUSPEND_SECS=60;
-- GCP (current-gen on GCP retains CPU_X64_* naming)
-- CREATE COMPUTE POOL pool MIN_NODES=1 MAX_NODES=3 INSTANCE_FAMILY=CPU_X64_S AUTO_SUSPEND_SECS=60;
```

### Anti-Pattern 1b: Using Previous-Generation Instance Families on AWS/Azure
```sql
-- WRONG on AWS/Azure: CPU_X64_*/HIGHMEM_X64_* are previous-generation
CREATE COMPUTE POOL pool MIN_NODES=1 MAX_NODES=3 INSTANCE_FAMILY=CPU_X64_S;
```
**Problem:** Worse price/performance than current-gen `GEN_X64_G2_*`/`MEM_X64_G2_*`. Snowflake docs recommend current-gen for all new workloads on AWS/Azure.

**Correct Pattern:** See "Instance Family Selection" below.

### Anti-Pattern 2: Exposing Internal Services Without Auth
```yaml
endpoints:
- name: api
  port: 8080
  public: true  # Exposed without auth!
```
**Problem:** Security breach, unauthorized access, data leak risk.

**Correct Pattern:**
```yaml
endpoints:
- name: api
  port: 8080
  public: true
  authentication:
    type: SNOWFLAKE_JWT
```

## Implementation Details

### Instance Family Selection

> **Investigation Required (MANDATORY before pool creation):** Always run `SHOW COMPUTE POOL INSTANCE FAMILIES;` and `SELECT CURRENT_REGION();` to confirm availability — region availability differs per cloud and changes over time. See [Snowflake docs](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/instance-families).

**Cloud-aware Current-Generation Families (prefer for new workloads):**

- **General Compute (small):** AWS `GEN_X64_G2_2` | Azure `GEN_X64_G2_2` | GCP `CPU_X64_XS`
- **General Compute (medium):** AWS `GEN_X64_G2_4`/`GEN_X64_G2_8` | Azure `GEN_X64_G2_4`/`GEN_X64_G2_8`/`GEN_X64_G2_16` | GCP `CPU_X64_S`/`CPU_X64_M`
- **General Compute (large):** AWS `GEN_X64_G2_32` | Azure `GEN_X64_G2_32` | GCP `CPU_X64_SL`/`CPU_X64_L`
- **High Memory:** AWS `MEM_X64_G2_8/32/64/192` | Azure `MEM_X64_G2_8/32/64/96` | GCP `HIGHMEM_X64_S/M/SL`
- **GPU (inference, light):** AWS `GPU_NV_S` (A10G) or `GPU_L40S_G1_8` (L40S) | Azure `GPU_NV_XS` (T4) | GCP `GPU_GCP_NV_L4_1_24G` (L4)
- **GPU (training, heavy):** AWS `GPU_NV_L` (A100 8x), `GPU_L40S_G1_192`, or `GPU_R6K_G1_*` (RTX PRO 6000 Blackwell) | Azure `GPU_NV_3M`/`GPU_NV_SL` (A100) | GCP `GPU_GCP_NV_A100_8_40G`

**Note (GCP):** On Google Cloud, `CPU_X64_*` and `HIGHMEM_X64_*` ARE the current generation — there are no previous-generation families on GCP. On AWS and Azure, those names are previous-generation; use `GEN_X64_G2_*`/`MEM_X64_G2_*` instead.

**Previous-Generation Migration (AWS/Azure only):**

- `CPU_X64_XS` becomes `GEN_X64_G2_2`
- `CPU_X64_S` becomes `GEN_X64_G2_4`
- `CPU_X64_M` becomes `GEN_X64_G2_8`
- `CPU_X64_SL` becomes `GEN_X64_G2_16` (Azure)
- `CPU_X64_L` becomes `GEN_X64_G2_32`
- `HIGHMEM_X64_S` becomes `MEM_X64_G2_8`
- `HIGHMEM_X64_M` becomes `MEM_X64_G2_32`
- `HIGHMEM_X64_L`/`HIGHMEM_X64_SL` become `MEM_X64_G2_64`/`MEM_X64_G2_96`/`MEM_X64_G2_192` (cloud-specific)

### Compute Pool Configuration
```sql
-- Verify availability first (MANDATORY)
SHOW COMPUTE POOL INSTANCE FAMILIES;
SELECT CURRENT_REGION();

-- General-purpose pool (AWS/Azure current-gen)
CREATE COMPUTE POOL app_pool
  MIN_NODES = 1 MAX_NODES = 5
  INSTANCE_FAMILY = GEN_X64_G2_2  -- AWS/Azure; on GCP use CPU_X64_XS
  AUTO_SUSPEND_SECS = 60;

-- GPU pool for ML (current-gen, AWS example with NVIDIA L40S for GenAI inference)
CREATE COMPUTE POOL ml_pool
  MIN_NODES = 1 MAX_NODES = 3
  INSTANCE_FAMILY = GPU_L40S_G1_8;  -- AWS only (us-east-1/2, us-west-2, eu-central-1, etc.)
  -- Azure alternative: INSTANCE_FAMILY = GPU_NV_XS (T4)
  -- GCP alternative:   INSTANCE_FAMILY = GPU_GCP_NV_L4_1_24G (L4)
```

### Complete Service Spec
```yaml
spec:
  containers:
  - name: my-app
    image: /db/schema/repo/app:v1.0.0
    resources:
      requests: { memory: 1Gi, cpu: 0.5 }
      limits: { memory: 2Gi, cpu: 1.0 }
    env:
      SNOWFLAKE_WAREHOUSE: MY_WH
      LOG_LEVEL: INFO
    secrets:
    - snowflakeSecret: { objectName: db-creds }
      envVarName: DB_PASSWORD
      secretKeyRef: password
  logExporters:
    eventTableConfig: { logLevel: INFO }
  endpoints:
  - name: web
    port: 8080
    public: true
    protocol: HTTP
    authentication:
      type: SNOWFLAKE_JWT
capabilities:
  securityContext: { executeAsCaller: false }
```

### Image Management
```bash
docker tag app:v1.0.0 <account>.registry.snowflakecomputing.com/db/schema/repo/app:v1.0.0
docker push <account>.registry.snowflakecomputing.com/db/schema/repo/app:v1.0.0
```

### Health Check Implementation
```python
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "checks": {"database": "ok"}}), 200
```

## Platform Events Monitoring

**Container Status Events:**

- **INFO/READY:** Running - service operational
- **INFO/PENDING:** Waiting/Provisioning - wait for resources
- **ERROR/PENDING:** Failed to pull image - check image path/auth
- **ERROR/FAILED:** OOMKilled - increase memory limit
- **ERROR/FAILED:** Fatal error - check SYSTEM$GET_SERVICE_LOGS()

**Enable Logging:**
```sql
CREATE SERVICE my_svc IN COMPUTE POOL pool FROM @stage SPECIFICATION='...' LOG_LEVEL=INFO;
ALTER SERVICE my_svc SET LOG_LEVEL = INFO;
```

**Query Platform Events:**
```sql
SELECT TIMESTAMP, VALUE:"status" AS status, VALUE:"message" AS msg
FROM TABLE(my_service!SPCS_GET_EVENTS(START_TIME => DATEADD('hour', -1, CURRENT_TIMESTAMP())))
WHERE RECORD:"name" = 'CONTAINER.STATUS_CHANGE'
ORDER BY TIMESTAMP DESC LIMIT 20;
```

**Troubleshooting Decision Tree:**
```sql
SELECT service_name, current_status, message,
  CASE
    WHEN current_status = 'READY' THEN 'OK'
    WHEN message LIKE '%Failed to pull%' THEN 'Check image path/auth'
    WHEN message LIKE '%OOMKilled%' THEN 'Increase memory limit'
    ELSE 'Check SYSTEM$GET_SERVICE_LOGS()'
  END AS action
FROM latest_events;
```

### Essential Troubleshooting Commands
```sql
SELECT * FROM TABLE(SYSTEM$GET_SERVICE_LOGS('my_svc', 'container', 100));
SELECT SYSTEM$GET_SERVICE_STATUS('my_svc');
SHOW SERVICES; SHOW COMPUTE POOLS;
DESCRIBE SERVICE my_svc;
```

## Data Access and Networking

### Stage Volumes
```yaml
spec:
  containers:
  - name: processor
    volumeMounts:
    - { name: data-stage, mountPath: /data }
  volumes:
  - { name: data-stage, source: "@my_stage" }
```

### Connection Pooling
```python
from snowflake.connector import pooling
pool = pooling.SnowflakeConnectionPool(pool_size=10, connection_name="myconn")

@app.get("/data")
def get():
    conn = pool.getconn()
    try:
        return conn.cursor().execute("SELECT ...").fetchone()
    finally:
        pool.putconn(conn)
```

## Cost Optimization

- **Right-size pools:** Start MIN_NODES=1, scale based on metrics
- **Auto-suspend:** Use 60-300 seconds for variable workloads
- **GPU only when needed:** `GEN_X64_G2_4` (AWS/Azure) or `CPU_X64_S` (GCP) covers most workloads
- **Prefer current-gen:** On AWS/Azure use `GEN_X64_G2_*`/`MEM_X64_G2_*`; on GCP use `CPU_X64_*`/`HIGHMEM_X64_*` (these ARE current-gen on GCP)
- **Monitor usage:**
```sql
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.COMPUTE_POOL_HISTORY WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP());
```

## RBAC and Permissions

**Required Privileges:**

- **CREATE COMPUTE POOL:** Granted at account level to pool admins
- **CREATE SERVICE:** Granted on schema where services are deployed
- **USAGE on COMPUTE POOL:** Required for any role deploying services
- **BIND SERVICE ENDPOINT:** Required for roles accessing public endpoints
- **READ on IMAGE REPOSITORY:** Required to pull images

```sql
-- Grant compute pool creation
GRANT CREATE COMPUTE POOL ON ACCOUNT TO ROLE spcs_admin;

-- Grant service deployment
GRANT CREATE SERVICE ON SCHEMA my_db.my_schema TO ROLE spcs_deployer;
GRANT USAGE ON COMPUTE POOL app_pool TO ROLE spcs_deployer;

-- Grant image repository access
GRANT READ ON IMAGE REPOSITORY my_db.my_schema.my_repo TO ROLE spcs_deployer;

-- Grant endpoint access to consuming roles
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE app_user;
```

## Service Lifecycle Management

```sql
-- Suspend a running service (stops containers, retains config)
ALTER SERVICE my_svc SUSPEND;

-- Resume a suspended service
ALTER SERVICE my_svc RESUME;

-- Update service spec (triggers rolling restart)
ALTER SERVICE my_svc FROM @stage SPECIFICATION = 'spec.yaml';

-- Change compute pool assignment
ALTER SERVICE my_svc SET COMPUTE_POOL = new_pool;

-- Change min/max instances for scaling
ALTER SERVICE my_svc SET MIN_INSTANCES = 2 MAX_INSTANCES = 5;

-- Drop a service permanently
DROP SERVICE IF EXISTS my_svc;

-- Drop a compute pool (must drop all services first)
DROP COMPUTE POOL IF EXISTS app_pool;
```

**Upgrade Strategies:**

- **Rolling update:** Use `ALTER SERVICE ... FROM @stage` with updated spec. Snowflake handles container replacement.
- **Blue-green:** Deploy new service with different name, validate, then switch DNS/references and drop old service.
