# Snowflake Snowpark Container Services (SPCS)

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:spcs, kw:container
**Keywords:** SPCS, compute pools, OCI images, service spec, container deployment, service logs, platform events
**TokenBudget:** ~2950
**ContextTier:** High
**Depends:** 100-snowflake-core.md

## Scope

**What This Rule Covers:**
Deploying and managing containerized apps on SPCS: compute pools, service specs, monitoring, and troubleshooting.

**When to Load:**
- Deploying containers on Snowflake SPCS
- Creating/configuring compute pools
- Troubleshooting SPCS services
- GPU-enabled ML/AI workloads

## References

### Dependencies
**Must Load First:** 100-snowflake-core.md

**Related:** 105 (cost), 107 (security), 111 (observability), 119 (warehouse mgmt)

### Related Examples

- **examples/120-spcs-service-spec-example.md** - Production SPCS YAML spec with security, logging, RBAC

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
CREATE COMPUTE POOL pool MIN_NODES=1 MAX_NODES=3 INSTANCE_FAMILY=CPU_X64_S AUTO_SUSPEND_SECS=60;
```

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

### Compute Pool Configuration
```sql
CREATE COMPUTE POOL app_pool
  MIN_NODES = 1 MAX_NODES = 5
  INSTANCE_FAMILY = CPU_X64_XS
  AUTO_SUSPEND_SECS = 60;

-- GPU for ML
CREATE COMPUTE POOL ml_pool
  MIN_NODES = 1 MAX_NODES = 3
  INSTANCE_FAMILY = GPU_NV_S;
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
- **GPU only when needed:** CPU_X64_S for most workloads
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
