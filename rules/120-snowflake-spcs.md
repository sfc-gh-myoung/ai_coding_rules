# Snowflake Snowpark Container Services (SPCS) Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** service deployment, compute pools, OCI images, image registry, health checks, GPU workloads, create service, compute pool, container deployment, service spec, container troubleshooting, SPCS error, service logs
**TokenBudget:** ~5150
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md

## Purpose
Provide comprehensive guidance for deploying, managing, and optimizing containerized applications using Snowflake Snowpark Container Services, covering architecture patterns, security, performance optimization, and operational best practices.

## Rule Scope

Snowflake Snowpark Container Services, containerized applications, microservices

**Progressive Disclosure - Token Budget:**
- Quick Start + Contract: ~400 tokens (always load for SPCS tasks)
- + Service Creation (sections 1-2): ~1000 tokens (load for setup)
- + Networking & Security (sections 3-4): ~1800 tokens (load for configuration)
- + Complete Reference: ~2400 tokens (full SPCS guide)

**Recommended Loading Strategy:**
- **Understanding SPCS**: Quick Start only
- **Creating services**: + Service Creation
- **Network/security config**: + Networking & Security
- **Production deployment**: Full reference

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Use OCI-compliant images** - Build with multi-stage for minimal size
- **Snowflake managed registry** - Semantic versioning (v1.2.3, not latest)
- **Include health checks** - Implement health endpoints in applications
- **Optimize compute pools** - Choose correct size, use GPUs for ML/AI
- **Implement service security** - Proper endpoint security, authentication
- **Monitor and scale** - Track usage, scale based on metrics
- **Never use 'latest' tag** - Always use semantic versioning

**Quick Checklist:**
- [ ] OCI-compliant image built
- [ ] Image in Snowflake registry with version
- [ ] Health check endpoint implemented
- [ ] Compute pool configured
- [ ] Resource limits set
- [ ] Service security configured
- [ ] Monitoring enabled

## Contract

<contract>
<inputs_prereqs>
[Context, files, dependencies needed]
</inputs_prereqs>

<mandatory>
[Tools permitted for this domain]
</mandatory>

<forbidden>
[Tools not allowed for this domain]
</forbidden>

<steps>
[Ordered steps the agent must follow]
</steps>

<output_format>
[Expected output format]
</output_format>

<validation>
[Checks to confirm success]
</validation>

<design_principles>
- Use OCI-compliant images; leverage Snowflake's managed image registry for secure storage.
- Design services for high availability with proper health checks and resource limits.
- Optimize compute pools for workload patterns; use GPUs for ML/AI workloads.
- Implement proper service-to-service communication and external endpoint security.
- Follow cost optimization patterns; monitor usage and scale appropriately.
> **Investigation Required**
> When working with Snowpark Container Services:
> 1. Verify SPCS availability in account: `SHOW PARAMETERS LIKE 'ENABLE_SNOWPARK_CONTAINER_SERVICES' IN ACCOUNT;`
> 2. Check compute pool exists: `SHOW COMPUTE POOLS;`
> 3. Verify image repository access: `SHOW IMAGE REPOSITORIES IN SCHEMA <db>.<schema>;`
> 4. Check service exists before operations: `SHOW SERVICES IN SCHEMA <db>.<schema>;`
> 5. Never assume image availability - verify image exists: `SHOW IMAGES IN IMAGE REPOSITORY <repo>;`
> 6. Test service health endpoint before declaring deployment successful
>
> **Anti-Pattern:**
> "Let me deploy this service - SPCS should be available."
>
> **Correct Pattern:**
> "Let me verify SPCS is enabled and check compute pool availability first."
> [checks parameters, verifies compute pool, lists images]
> "SPCS enabled, compute pool ready, image available. Deploying service..."
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Creating Oversized Compute Pools for Simple Workloads**
```sql
-- Bad: Huge pool for simple inference API
CREATE COMPUTE POOL inference_pool
MIN_NODES = 5        -- Always 5 nodes running!
MAX_NODES = 10
INSTANCE_FAMILY = GPU_NV_M  -- Expensive GPU instances!
AUTO_SUSPEND_SECS = 3600;   -- Stays up 1 hour after last use

-- For API that gets 10 requests per day!
-- Burns thousands of dollars per month!
```
**Problem:** Massive cost overrun; wasted resources; poor utilization; budget disaster; unprofessional; financial irresponsibility

**Correct Pattern:**
```sql
-- Good: Right-sized pool matching workload
CREATE COMPUTE POOL inference_pool
MIN_NODES = 1        -- Start small, scale if needed
MAX_NODES = 3        -- Reasonable upper bound
INSTANCE_FAMILY = CPU_X64_S  -- Start with CPU, upgrade if GPU needed
AUTO_SUSPEND_SECS = 60;      -- Suspend after 1 minute idle

-- Monitor usage and scale up only if needed
-- Check metrics:
SELECT
  pool_name,
  active_nodes,
  idle_nodes,
  AVG(cpu_usage_percent) as avg_cpu,
  MAX(cpu_usage_percent) as max_cpu
FROM SNOWFLAKE.ACCOUNT_USAGE.COMPUTE_POOL_METRICS
WHERE pool_name = 'INFERENCE_POOL'
  AND start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP())
GROUP BY pool_name, active_nodes, idle_nodes;

-- Scale up only if consistently hitting max capacity
```
**Benefits:** Cost-effective; right-sized; scalable; monitored; data-driven scaling; professional; financially responsible


**Anti-Pattern 2: Exposing Internal Services Publicly**
```yaml
# Bad: spec.yaml exposes internal service to internet
spec:
  containers:
  - name: internal-api
    image: /my-repo/internal-api:latest
    env:
      DATABASE_PASSWORD: PLACEHOLDER_PASSWORD  # Secrets in plain text!
    endpoints:
    - name: api
      port: 8080
      public: true  # Exposed to internet!

# Anyone on internet can access internal API!
# Credentials exposed in plain text!
```
**Problem:** Security breach; exposed credentials; unauthorized access; data leak; compliance violation; reputation damage; potential data theft

**Correct Pattern:**
```yaml
# Good: Internal endpoints, externalize secrets
spec:
  containers:
  - name: internal-api
    image: /my-repo/internal-api:latest
    env:
      DATABASE_PASSWORD:
        secretKeyRef: db-credentials  # Reference secret, not plain text
    endpoints:
    - name: api
      port: 8080
      public: false  # Internal only!

# Create secret separately
# SNOW SQL> CREATE SECRET db_credentials TYPE = GENERIC_STRING SECRET_STRING = 'PLACEHOLDER_PASSWORD';

# If external access needed, use Snowflake authentication:
spec:
  containers:
  - name: public-api
    image: /my-repo/public-api:latest
    endpoints:
    - name: api
      port: 8080
      public: true
      authentication:
        type: SNOWFLAKE_JWT  # Require Snowflake auth!
```
**Benefits:** Security hardened; credentials protected; authentication required; internal services isolated; compliance-friendly; no unauthorized access


**Anti-Pattern 3: Creating New Database Connections Per Request**
```python
# Bad: New connection per API request
from fastapi import FastAPI
import snowflake.connector

app = FastAPI()

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    # New connection every request!
    conn = snowflake.connector.connect(
        connection_name="myconn"
    )
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM customers WHERE id = {customer_id}")
    result = cursor.fetchone()
    conn.close()  # Close immediately

    return result

# 1000 requests = 1000 connections = slow, resource exhaustion!
```
**Problem:** Connection overhead; slow responses; resource exhaustion; connection pool limits; poor scalability; unprofessional; bad performance

**Correct Pattern:**
```python
# Good: Connection pooling and reuse
from fastapi import FastAPI
import snowflake.connector
from snowflake.connector import pooling

app = FastAPI()

# Create connection pool at startup
connection_pool = pooling.SnowflakeConnectionPool(
    pool_size=10,
    connection_name="myconn"
)

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    # Borrow connection from pool
    conn = connection_pool.getconn()

    try:
        cursor = conn.cursor()
        # Use parameterized query (prevents SQL injection)
        cursor.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
        result = cursor.fetchone()
        return result
    finally:
        # Return connection to pool (don't close)
        connection_pool.putconn(conn)

# Reuses connections, fast, scalable, professional!

@app.on_event("shutdown")
def shutdown():
    connection_pool.close()  # Clean up pool on shutdown
```
**Benefits:** Fast responses; connection reuse; scalable; resource-efficient; professional; better performance; SQL injection prevention


**Anti-Pattern 4: Not Setting Resource Limits, Causing OOM**
```yaml
# Bad: No resource limits specified
spec:
  containers:
  - name: data-processor
    image: /my-repo/processor:latest
    # No resources specified!

# Python code processes large datasets in memory:
import pandas as pd

def process_data():
    df = pd.read_sql("SELECT * FROM huge_table", conn)  # Loads 10GB into memory!
    df_transformed = df.apply(expensive_function)
    return df_transformed

# Container OOM killed, service crashes, users see errors!
```
**Problem:** OOM crashes; service unavailability; user errors; unpredictable behavior; debugging nightmare; unprofessional; poor reliability

**Correct Pattern:**
```yaml
# Good: Explicit resource limits and streaming processing
spec:
  containers:
  - name: data-processor
    image: /my-repo/processor:latest
    resources:
      requests:
        memory: 2Gi
        cpu: 1000m
      limits:
        memory: 4Gi
        cpu: 2000m
```

```python
# Python: Stream data in chunks, don't load all into memory
import pandas as pd

def process_data_streaming():
    chunk_size = 10000  # Process 10K rows at a time

    # Stream results in chunks
    for chunk in pd.read_sql(
        "SELECT * FROM huge_table",
        conn,
        chunksize=chunk_size
    ):
        # Process chunk
        chunk_transformed = chunk.apply(expensive_function)

        # Write chunk to output (don't accumulate in memory)
        chunk_transformed.to_sql(
            'output_table',
            conn,
            if_exists='append',
            index=False
        )

    return "Processing complete"

# Memory usage stays constant, no OOM, reliable!
```
**Benefits:** No OOM crashes; predictable resource usage; reliable service; professional; scalable; memory-efficient; good performance

## Post-Execution Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

> **Investigation Required**
> When applying this rule:
> 1. **Read existing SPCS configurations BEFORE deploying services** - Check compute pools, service specs, image registries
> 2. **Verify SPCS availability** - Check if SPCS is enabled in account
> 3. **Never assume compute pool size** - Review existing pools and workload patterns
> 4. **Check image registry** - Verify Snowflake image repository setup and access
> 5. **Test service deployment** - Validate in dev environment before production
>
> **Anti-Pattern:**
> "Deploying SPCS service... (without checking existing patterns)"
> "Using 'latest' image tag... (breaks reproducibility)"
>
> **Correct Pattern:**
> "Let me check your SPCS setup first."
> [reads compute pools, checks service specs, reviews image registry]
> "I see you use GPU_NV_S compute pools with versioned images. Deploying new service following this pattern..."

## Output Format Examples

```sql
-- Analysis Query: Investigate current state
SELECT column_pattern, COUNT(*) as usage_count
FROM information_schema.columns
WHERE table_schema = 'TARGET_SCHEMA'
GROUP BY column_pattern;

-- Implementation: Apply Snowflake best practices
CREATE OR REPLACE VIEW schema.view_name
COMMENT = 'Business purpose following semantic model standards'
AS
SELECT
    -- Explicit column list with business context
    id COMMENT 'Surrogate key',
    name COMMENT 'Business entity name',
    created_at COMMENT 'Record creation timestamp'
FROM schema.source_table
WHERE is_active = TRUE;

-- Validation: Confirm implementation
SELECT * FROM schema.view_name LIMIT 5;
SHOW VIEWS LIKE '%view_name%';
```

## References

### External Documentation
- [Snowpark Container Services Overview](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/overview) - Architecture, concepts, and getting started guide
- [SPCS Tutorials](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/tutorials) - Step-by-step implementation examples
- [Service Specification Reference](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/specification-reference) - YAML service definition schema and options
- [SPCS SQL Commands](https://docs.snowflake.com/en/sql-reference/sql/create-service) - CREATE SERVICE and related SQL command reference
- [SPCS Cost Management](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/costs) - Pricing model and cost optimization strategies
- [SPCS Platform Events Monitoring](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/platform-events) - Guide for monitoring and troubleshooting SPCS platform events

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **Security Governance**: `rules/107-snowflake-security-governance.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`

## 1. Architecture, Images, and Service Types

### Container and Image Management
- **Rule:** Build OCI-compliant images optimized for Snowflake; use multi-stage builds to minimize size.
- **Always:** Use Snowflake's managed image registry with semantic versioning (e.g., `v1.2.3`, not `latest`).
- **Rule:** Include health check endpoints in applications; implement vulnerability scanning and automated builds.
- **Always:** Design stateless services with graceful shutdown handling and explicit resource limits.

```sql
-- Create and configure image repository
CREATE IMAGE REPOSITORY my_app_repo;
GRANT USAGE ON IMAGE REPOSITORY my_app_repo TO ROLE app_developer_role;
```

```bash
# Upload image with proper tagging
docker tag my-app:v1.0.0 <account>.registry.snowflakecomputing.com/my_db/my_schema/my_app_repo/my-app:v1.0.0
docker push <account>.registry.snowflakecomputing.com/my_db/my_schema/my_app_repo/my-app:v1.0.0
```

### Service Types and Patterns
- **Rule:** Use long-running services for web applications, APIs, and persistent workloads.
- **Rule:** Use job services for batch processing, ML training, and finite-duration tasks.
- **Always:** Choose service type based on workload characteristics and implement proper lifecycle management.

## 2. Compute Pools and Resource Management

### Pool Configuration and Scaling
- **Rule:** Right-size compute pools based on workload requirements; set appropriate min/max nodes for auto-scaling.
- **Rule:** Use GPU-enabled machine types only for ML/AI workloads requiring GPU acceleration.
- **Always:** Configure auto-suspend for variable workloads; use dedicated pools for production guarantees.
- **Always:** Monitor utilization, costs, and implement account-level quotas and limits.

```sql
-- Compute pool examples
CREATE COMPUTE POOL my_app_pool MIN_NODES = 1 MAX_NODES = 5 INSTANCE_FAMILY = CPU_X64_XS;
CREATE COMPUTE POOL ml_training_pool MIN_NODES = 1 MAX_NODES = 3 INSTANCE_FAMILY = GPU_NV_S;
```

## 3. Service Specifications and Security

### YAML Configuration and Security Standards
- **Rule:** Use explicit resource requests/limits; implement structured logging with `logExporters`.
- **Always:** Build health endpoints into applications; use environment variables for configuration.
- **Rule:** Never include secrets in specifications; use Snowflake's secret management instead.
- **Always:** Follow official SPCS specification syntax; implement least-privilege access controls.

```yaml
# Complete service specification with security
spec:
  containers:
  - name: my-app
    image: /my_db/my_schema/my_app_repo/my-app:v1.0.0
    resources:
      requests: { memory: 1Gi, cpu: 0.5 }
      limits: { memory: 2Gi, cpu: 1.0 }
    env:
      SNOWFLAKE_WAREHOUSE: MY_WAREHOUSE
      LOG_LEVEL: INFO
    secrets:
    - snowflakeSecret: { objectName: db-credentials }
      envVarName: DATABASE_PASSWORD
      secretKeyRef: password
  logExporters:
    eventTableConfig: { logLevel: INFO }
  endpoints:
  - name: web-endpoint
    port: 8080
    public: true
    protocol: HTTP
capabilities:
  securityContext: { executeAsCaller: false }
serviceRoles:
- name: api_user_role
  endpoints: [web-endpoint]
```

## 4. Networking and Data Integration

### Service Communication and Endpoints
- **Rule:** Use service DNS names for internal communication; configure public endpoints only when required.
- **Always:** Implement connection pooling, circuit breakers, and proper authentication for external endpoints.
- **Rule:** Use HTTPS/TLS for external communications; monitor and log endpoint access.
- **Always:** Use Snowflake connectors with connection pooling for optimal data access performance.

### Data Access and Stage Integration
- **Rule:** Leverage Snowflake stages for file-based data exchange; use appropriate warehouse sizes.
- **Always:** Clean up temporary stage files; implement proper error handling and use efficient formats (Parquet, JSON).

```python
# Snowflake connectivity with connection pooling
import snowflake.connector
def get_connection():
    return snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'), warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'), schema=os.getenv('SNOWFLAKE_SCHEMA'),
        authenticator='snowflake_jwt', private_key=get_private_key()
    )
```

```yaml
# Service with stage volumes and endpoints
spec:
  containers:
  - name: data-processor
    image: /my_db/my_schema/my_app_repo/processor:v1.0.0
    volumeMounts:
    - { name: data-stage, mountPath: /data }
    - { name: temp-storage, mountPath: /tmp }
  volumes:
  - { name: data-stage, source: "@my_data_stage", uid: 1000, gid: 1000 }
  - { name: temp-storage, source: local }
  endpoints:
  - { name: api, port: 8080, public: true, protocol: HTTP }
```

## 5. Monitoring, Logging, and Troubleshooting

### Service Monitoring and Health Checks
- **Always:** Build health endpoints into applications; use structured JSON logging with correlation IDs.
- **Rule:** Monitor metrics using `platformMonitor`; set up alerting based on logs and external monitoring.
- **Always:** Since SPCS has no built-in health probes, implement application-level health checks.

### Logging and Observability
- **Rule:** Use Snowflake's logging functions for analysis; implement appropriate log retention policies.
- **Always:** Include request IDs and user context; log health status for monitoring via log analysis.

```yaml
# Monitoring configuration
spec:
  containers:
  - name: my-app
    env: { HEALTH_CHECK_PORT: "8080", HEALTH_CHECK_PATH: "/health" }
  logExporters: { eventTableConfig: { logLevel: INFO } }
  platformMonitor: { metricConfig: { groups: [basic] } }
```

```python
# Health check implementation
from flask import Flask, jsonify
import logging
app = Flask(__name__)
@app.route('/health')
def health_check():
    try:
        health_status = {"status": "healthy", "checks": {"database": "ok", "memory": "ok"}}
        logging.info(f"Health check passed: {health_status}")
        return jsonify(health_status), 200
    except Exception as e:
        error_status = {"status": "unhealthy", "error": str(e)}
        logging.error(f"Health check failed: {error_status}")
        return jsonify(error_status), 503
```

### Platform Events: Container Status Monitoring

SPCS platform events provide visibility into container lifecycle and failures. These events are automatically recorded to the event table when LOG_LEVEL is configured.

**Supported Container Status Events:**

**INFO Severity Events:**
- **READY / Running** - Container is healthy and operational
- **PENDING / Waiting to start** - Container initialization in progress
- **PENDING / Compute pool node(s) are being provisioned** - Awaiting node resources
- **PENDING / Readiness probe is failing** - Health check endpoint not responding (check path/port)

**ERROR Severity Events:**
- **PENDING / Failed to pull image** - Image registry authentication or availability issue
- **FAILED / Provided image name uses an invalid format** - Image reference malformed (check path syntax)
- **FAILED / Encountered fatal error, retrying** - Application crashed; automatic restart in progress
- **FAILED / Encountered fatal error** - Application crashed; maximum retries reached
- **FAILED / Encountered fatal error while running** - Application error detected; see logs for details
- **FAILED / Container was OOMKilled** - Memory limit exceeded; increase resource limits
- **FAILED / User application error** - Application threw exception; review logs
- **FAILED / Encountered fatal error while starting container** - Startup failure; check configuration and logs

**INFO Severity Events:**
- **DONE / Completed successfully** - Job service task completed (job services only)

**Enable Platform Event Logging:**

```sql
-- Enable platform events at service creation
CREATE SERVICE my_service
  IN COMPUTE POOL my_pool
  FROM @my_stage
  SPECIFICATION = '...'
  LOG_LEVEL = INFO;  -- Enables both INFO and ERROR platform events

-- Or enable on existing service
ALTER SERVICE my_service SET LOG_LEVEL = INFO;

-- Set LOG_LEVEL to ERROR for production to reduce event volume
ALTER SERVICE my_service SET LOG_LEVEL = ERROR;

-- Disable platform event logging
ALTER SERVICE my_service SET LOG_LEVEL = OFF;
```

**Query Platform Events for Container Troubleshooting:**

```sql
-- Option 1: Use service helper function (recommended - scoped access)
SELECT
    TIMESTAMP,
    RECORD:"name" AS event_name,
    RECORD:"severity_text" AS severity,
    VALUE:"status" AS container_status,
    VALUE:"message" AS status_message
FROM TABLE(my_service!SPCS_GET_EVENTS(
    START_TIME => DATEADD('hour', -1, CURRENT_TIMESTAMP())
))
WHERE RECORD:"name" = 'CONTAINER.STATUS_CHANGE'
ORDER BY TIMESTAMP DESC
LIMIT 20;

-- Option 2: Query event table directly (requires event table access)
SELECT
    TIMESTAMP,
    RESOURCE_ATTRIBUTES:"snow.service.name"::string AS service_name,
    RESOURCE_ATTRIBUTES:"snow.service.container.name"::string AS container_name,
    RECORD:"name"::string AS event_name,
    RECORD:"severity_text"::string AS severity,
    VALUE:"status"::string AS container_status,
    VALUE:"message"::string AS status_message
FROM snowflake.account_usage.event_table
WHERE TIMESTAMP > DATEADD('hour', -1, CURRENT_TIMESTAMP())
    AND RESOURCE_ATTRIBUTES:"snow.service.name" = 'my_service'
    AND RECORD_TYPE = 'EVENT'
    AND SCOPE:"name" = 'snow.spcs.platform'
ORDER BY TIMESTAMP DESC
LIMIT 20;
```

**Troubleshooting Decision Tree:**

```sql
-- Find most recent status for each service
WITH latest_statuses AS (
  SELECT
      RESOURCE_ATTRIBUTES:"snow.service.name"::string AS service_name,
      RESOURCE_ATTRIBUTES:"snow.service.container.name"::string AS container_name,
      VALUE:"status"::string AS current_status,
      VALUE:"message"::string AS message,
      RECORD:"severity_text"::string AS severity,
      TIMESTAMP,
      ROW_NUMBER() OVER (
        PARTITION BY RESOURCE_ATTRIBUTES:"snow.service.name",
                     RESOURCE_ATTRIBUTES:"snow.service.container.name"
        ORDER BY TIMESTAMP DESC
      ) AS rn
  FROM snowflake.account_usage.event_table
  WHERE RECORD_TYPE = 'EVENT'
      AND SCOPE:"name" = 'snow.spcs.platform'
      AND TIMESTAMP > DATEADD('day', -7, CURRENT_TIMESTAMP())
)
SELECT
    service_name,
    container_name,
    current_status,
    message,
    severity,
    TIMESTAMP,
    CASE
      WHEN current_status = 'READY' THEN 'OK - Service is operational'
      WHEN current_status = 'PENDING' AND message LIKE '%node%' THEN 'ACTION: Wait for compute pool provisioning or check pool capacity'
      WHEN current_status = 'PENDING' AND message LIKE '%Failed to pull%' THEN 'ACTION: Verify image path, registry credentials, and network access'
      WHEN current_status = 'FAILED' AND message LIKE '%OOMKilled%' THEN 'ACTION: Increase memory limit in service spec or optimize app memory usage'
      WHEN current_status = 'FAILED' AND message LIKE '%image name%' THEN 'ACTION: Correct image path format; should be /DATABASE/SCHEMA/REPOSITORY/IMAGE:TAG'
      WHEN current_status = 'FAILED' THEN 'ACTION: Check SYSTEM$GET_SERVICE_LOGS(); review application logs and startup configuration'
      ELSE 'CHECK: Review full message for specific guidance'
    END AS recommended_action
FROM latest_statuses
WHERE rn = 1
ORDER BY severity DESC, service_name;
```

**Anti-Patterns in SPCS Troubleshooting:**

```sql
-- ANTI-PATTERN: Querying only recent seconds (missing context)
SELECT * FROM event_table
WHERE TIMESTAMP > DATEADD('minute', -1, CURRENT_TIMESTAMP());

-- CORRECT: Query sufficient time window to capture failure progression
SELECT * FROM event_table
WHERE TIMESTAMP > DATEADD('hour', -2, CURRENT_TIMESTAMP())
ORDER BY TIMESTAMP DESC;

-- ANTI-PATTERN: Checking only FAILED status (missing transitional states)
SELECT * FROM event_table
WHERE VALUE:"status" = 'FAILED';

-- CORRECT: Review full status sequence including PENDING states
SELECT TIMESTAMP, VALUE:"status", VALUE:"message", RECORD:"severity_text"
FROM event_table
WHERE RESOURCE_ATTRIBUTES:"snow.service.name" = 'my_service'
  AND RECORD_TYPE = 'EVENT'
ORDER BY TIMESTAMP DESC;

-- ANTI-PATTERN: Assuming ERROR severity without checking status
-- (Some INFO events indicate actual problems like PENDING with readiness failures)

-- CORRECT: Analyze message content and status together
SELECT VALUE:"status", RECORD:"severity_text", COUNT(*)
FROM event_table
WHERE RECORD_TYPE = 'EVENT'
  AND SCOPE:"name" = 'snow.spcs.platform'
GROUP BY VALUE:"status", RECORD:"severity_text"
ORDER BY RECORD:"severity_text" DESC;
```

### Accessing Container Logs

- **Rule:** Use `SYSTEM$GET_SERVICE_LOGS()` for direct log retrieval during development; use event table for persistent analysis.
- **Always:** Check container logs in conjunction with platform events for complete troubleshooting context.

```sql
-- Retrieve recent container logs
SELECT * FROM TABLE(SYSTEM$GET_SERVICE_LOGS('my_service', 'container_name', 100));

-- Query logs for specific time range (requires application to log to stdout/stderr)
SELECT
    TIMESTAMP,
    VALUE
FROM snowflake.account_usage.event_table
WHERE RESOURCE_ATTRIBUTES:"snow.service.name" = 'my_service'
  AND RECORD_TYPE = 'LOG'
  AND TIMESTAMP >= DATEADD('minute', -30, CURRENT_TIMESTAMP())
ORDER BY TIMESTAMP DESC;
```

### Troubleshooting and Debugging
- **Always:** Check service logs first; verify compute pool capacity and network connectivity.
- **Rule:** Validate YAML syntax; use Snowflake's built-in monitoring functions for operational visibility.
- **Rule:** Enable LOG_LEVEL = INFO to capture all events; scale back to ERROR in production after validation.

```sql
-- Essential troubleshooting queries
SELECT * FROM TABLE(SYSTEM$GET_SERVICE_LOGS('my_service', 'web-app', 100));
SELECT * FROM TABLE(my_service!SPCS_GET_EVENTS(START_TIME => DATEADD('hour', -2, CURRENT_TIMESTAMP())));
SELECT SYSTEM$GET_SERVICE_STATUS('my_service');
SHOW SERVICES;
SHOW COMPUTE POOLS;
DESCRIBE SERVICE my_service;
```

## 6. Performance Optimization and Cost Management

### Container and Resource Optimization
- **Rule:** Use optimized base images (Alpine, distroless); minimize startup time through image optimization.
- **Always:** Profile applications for optimal resource allocations; implement proper caching and connection pooling.
- **Rule:** Use multi-stage builds; implement horizontal scaling for variable workloads.

### Cost Optimization and Efficiency
- **Rule:** Use auto-suspend for dev/test; share compute pools across similar workloads for better utilization.
- **Always:** Monitor costs and right-size pools; implement cost budgets and alerts for SPCS usage.
- **Rule:** Clean up unused services regularly; use appropriate instance families for workload characteristics.

```sql
-- Cost monitoring and optimization
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.COMPUTE_POOL_HISTORY
WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP());
```

## 7. Development, Testing, and Deployment

### CI/CD and Testing Strategies
- **Rule:** Implement automated testing for images and specifications; use infrastructure as code.
- **Always:** Test services in isolated compute pools; implement integration and synthetic monitoring tests.
- **Rule:** Use proper environment promotion workflows (dev then test then prod) with approval gates.
- **Always:** Test disaster recovery scenarios; maintain deployment runbooks.

## 8. ML/AI Workloads and Advanced Patterns

### Machine Learning and GPU Workloads
- **Rule:** Use GPU-enabled compute pools for ML training; integrate with Snowflake ML features.
- **Always:** Use job services for model training/inference; implement proper model versioning.
- **Rule:** Integrate with Streams and Tasks for event-driven processing; leverage data sharing capabilities.

```yaml
# GPU-enabled ML training specification
spec:
  containers:
  - name: ml-trainer
    image: /my_db/my_schema/ml_repo/trainer:v2.0.0
    resources:
      requests: { memory: 8Gi, cpu: 2.0, nvidia.com/gpu: 1 }
      limits: { memory: 16Gi, cpu: 4.0, nvidia.com/gpu: 1 }
    env: { CUDA_VISIBLE_DEVICES: "0", MODEL_OUTPUT_PATH: "/models" }
    volumeMounts: [{ name: model-storage, mountPath: /models }]
  volumes: [{ name: model-storage, source: "@model_artifacts_stage" }]
```

### Compliance and Governance
- **Always:** Maintain audit logs; implement data lineage tracking and use Snowflake's governance features.
- **Rule:** Implement data masking/encryption; follow data residency requirements and retention policies.

## 9. Anti-Patterns and Common Pitfalls

### Critical Anti-Patterns to Avoid
- **Avoid:** Using `latest` tags in production; hardcoding secrets in images; running unnecessary root containers.
- **Avoid:** Creating oversized pools for simple workloads; exposing internal services publicly.
- **Avoid:** New connections per request (use pooling); processing large datasets in memory without streaming.
- **Avoid:** Ignoring resource limits; using synchronous processing for long-running operations.

## Related Rules

**Closely Related** (consider loading together):
- `119-snowflake-warehouse-management` - For compute pool sizing and resource management patterns
- `111-snowflake-observability-core` - For container logging, tracing, and monitoring in SPCS

**Sometimes Related** (load if specific scenario):
- `115-snowflake-cortex-agents-core` - When deploying agent services on SPCS
- `116-snowflake-cortex-search` - When running custom search services on SPCS
- `109-snowflake-notebooks` - When running notebook workloads on SPCS compute

**Complementary** (different aspects of same domain):
- `107-snowflake-security-governance` - For secrets, network rules, and RBAC on SPCS services
- `105-snowflake-cost-governance` - For monitoring compute pool and service costs
