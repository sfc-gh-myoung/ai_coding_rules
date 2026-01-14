# Snowflake Observability: Logging Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** DEBUG, INFO, WARN, ERROR, FATAL, conditional logging, sampling, tight loop logging, standard logging libraries, log volume control, cost management, log configuration, log handlers
**TokenBudget:** ~4350
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 111-snowflake-observability-core.md

## Scope

**What This Rule Covers:**
Comprehensive logging best practices for Snowflake handler code, covering standard library integration, strategic log level usage, conditional logging patterns, and volume control strategies to optimize observability while managing costs.

**When to Load This Rule:**
- Implementing logging in Snowflake handlers (Python, Java, JavaScript)
- Managing log volumes and costs
- Using conditional logging patterns
- Integrating with standard logging libraries
- Optimizing logging for production environments

### Quantification Standards

**Frequency Thresholds:**
- **High-frequency operation:** >1000 log calls per minute OR >100 iterations per second in a loop (context: requires sampling strategy)
- **Sampling rate for tight loops:** Log every 100th-1000th iteration (e.g., log every 100th row processed in batch of 10K+ rows)
- **Acceptable log volume:** <10MB per handler execution OR <1000 log entries per minute (context: cost management)
- **Production log level:** WARN or ERROR only (DEBUG generates 10-100x more volume, see 111-snowflake-observability-core.md)

## References

### External Documentation
- [Snowflake Logging Overview](https://docs.snowflake.com/en/developer-guide/logging-tracing/logging) - Official logging documentation for Snowflake handlers
- [Python Logging Library](https://docs.python.org/3/library/logging.html) - Standard Python logging library documentation
- [SLF4J (Java)](https://www.slf4j.org/) - Standard Java logging facade

### Related Rules
- **Observability Core**: `111-snowflake-observability-core.md` - Foundation observability patterns and telemetry configuration
- **Observability Tracing**: `111b-snowflake-observability-tracing.md` - Distributed tracing patterns
- **Observability Monitoring**: `111c-snowflake-observability-monitoring.md` - Monitoring and analysis patterns
- **Snowflake Core**: `100-snowflake-core.md` - Foundation Snowflake practices

## Contract

### Inputs and Prerequisites
- Active event table configured (see `111-snowflake-observability-core.md`)
- Telemetry levels configured appropriately for environment
- Standard logging library available (Python `logging`, Java `slf4j`)

### Mandatory
- Standard logging libraries (Python `logging`, Java `slf4j`, JavaScript `console`)
- Conditional logging with if-statements for volume control
- Sampling strategies for high-frequency operations (>1000 log calls/min OR >100 iterations/sec)

### Forbidden
- `print` statements instead of logging (do NOT route to event tables)
- DEBUG logging in production environments without cost analysis
- Logging in tight loops without sampling
- Logging sensitive data (PII, credentials, tokens)

### Execution Steps
1. **Import:** Use standard logging library at module level
2. **Configure:** Set appropriate log levels for environment (see `111-snowflake-observability-core.md`)
3. **Implement:** Add strategic log statements at key decision points
4. **Sample:** Use conditional logging or sampling (every 100th-1000th iteration) for high-frequency operations (>1000 calls/min OR >100 iter/sec)
5. **Validate:** Verify logs appear in event tables after deployment

### Output Format
- Python/Java/JavaScript code with proper logging import statements
- Log messages with meaningful context (include relevant variables)
- Conditional logging for volume control
- Comments explaining sampling strategy

### Validation
- Verify standard logging library is imported
- Confirm log levels match environment (no DEBUG in prod)
- Check tight loops use sampling or conditional logging
- Validate logs appear in event tables

### Design Principles
- Use standard logging libraries that automatically route to event tables (Python `logging`, Java `slf4j`)
- Set log levels based on environment: WARN+ for production, DEBUG for development only
- Implement conditional logging to capture only meaningful scenarios and control data volume
- **CRITICAL:** Use sampling strategies for high-frequency operations (>1000 log calls/min OR >100 iter/sec: log every Nth iteration in tight loops)
- Include relevant context in log messages (variable values, record counts, error details)
- **CRITICAL:** Never log sensitive data (PII, credentials, API tokens) - security and compliance violation

### Post-Execution Checklist
- [ ] Standard logging library imported (not print statements)
- [ ] Log levels appropriate (WARN+ for prod, DEBUG for dev)
- [ ] Tight loops use sampling (every Nth iteration, typically 1000)
- [ ] Sensitive data excluded from logs (PII, credentials, tokens)
- [ ] Meaningful context included in log messages
- [ ] Conditional logging used for volume control

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using print() Instead of Standard Logging Library**
```python
# Bad: print() statements don't route to event tables
def process_data(records):
    print(f"Processing {len(records)} records")  # Lost in stdout!
    for record in records:
        print(f"Processing record {record['id']}")  # No persistence
    print("Processing complete")
```
**Problem:** Logs not captured in event tables; no persistence; can't query historical logs; debugging impossible in production; no log levels; no structured data

**Correct Pattern:**
```python
# Good: Use standard logging library
import logging
logger = logging.getLogger(__name__)

def process_data(records):
    logger.info(f"Processing {len(records)} records")
    # [process records with sampling - see anti-pattern 2]
    logger.info("Processing complete")
# Logs automatically routed to event table for querying
```
**Benefits:** Logs persisted in event tables; queryable history; production debugging; proper log levels; structured data; automatic routing

**Anti-Pattern 2: Logging Every Iteration in Tight Loops**
```python
# Bad: Log every record in large dataset
for i, record in enumerate(large_dataset):  # 1 million records
    logger.info(f"Processing record {i}: {record['id']}")
# Generates 1 million log entries! Massive costs!
```
**Problem:** Massive log volume; 1000x normal costs; event table bloat; performance degradation; signal-to-noise ratio destroyed; unusable logs

**Correct Pattern:**
```python
# Good: Sample logging - every 1000th iteration
for i, record in enumerate(large_dataset):
    if i % 1000 == 0:  # Log every 1000th record
        logger.info(f"Processing batch: record {i} of {len(large_dataset)}")
# Final summary
logger.info(f"Completed processing {len(large_dataset)} records")
```
**Benefits:** 1000x fewer logs; manageable costs; performance maintained; signal preserved; actionable logs; production-scalable

**Anti-Pattern 3: Logging Sensitive Data (PII, Credentials)**
```python
# Bad: Log sensitive information
def authenticate_user(username, password, ssn):
    logger.info(f"Authenticating user: {username}, SSN: {ssn}, password: {password}")
    # SECURITY VIOLATION: PII and credentials in logs!
```
**Problem:** Security breach; PII exposure; compliance violations (GDPR, HIPAA); credential leakage; audit failures; regulatory fines; data breach liability

**Correct Pattern:**
```python
# Good: Exclude sensitive data, log safe identifiers only
def authenticate_user(username, password, ssn):
    # Hash or mask sensitive fields
    user_hash = hashlib.sha256(username.encode()).hexdigest()[:8]
    logger.info(f"Authenticating user_hash: {user_hash}")
    # Never log: password, ssn, credit cards, tokens, API keys
```
**Benefits:** Security maintained; compliance-ready; no PII exposure; safe debugging; audit-friendly; regulatory compliance; zero breach liability

**Anti-Pattern 4: Using DEBUG Log Level in Production**
```python
# Bad: DEBUG level in production
import logging
logging.basicConfig(level=logging.DEBUG)  # In production!
logger = logging.getLogger(__name__)

def process_order(order):
    logger.debug(f"Order details: {order}")  # 100x more data volume
    logger.debug(f"Validating order {order['id']}")
    logger.debug(f"Processing payment {order['payment']}")
    # Generates massive log volume, high costs
```
**Problem:** 10-100x log volume increase; massive serverless costs; event table bloat; performance impact; signal-to-noise destroyed; production noise

**Correct Pattern:**
```python
# Good: Environment-appropriate log levels
import logging
import os

# Production: WARN or ERROR only
if os.getenv('ENV') == 'production':
    logging.basicConfig(level=logging.WARN)
else:  # Development
    logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

def process_order(order):
    logger.info(f"Processing order {order['id']}")  # Key milestone only
    # Errors logged automatically at WARN+ level
    if validation_error:
        logger.error(f"Order validation failed: {error_code}")
```
**Benefits:** Cost-effective production logging; manageable volume; performance maintained; actionable signal; development flexibility; production scalability

## Output Format Examples
```python
# Logging Best Practices Template

import logging

# Configure logger at module level
logger = logging.getLogger(__name__)

def my_handler(session, input_data):
    """Handler with logging best practices."""

    # Log entry point with context
    logger.info(f"Starting processing for {len(input_data)} records")

    try:
        # Validate inputs with conditional logging
        if not input_data:
            logger.error("Input data is empty")
            return None

        # Warn about large datasets
        if len(input_data) > 100000:
            logger.warn(f"Large dataset: {len(input_data)} records (may take time)")

        # Process with sampling for progress
        results = []
        for i, record in enumerate(input_data):
            # Sample progress logging (every 10,000 records)
            if i % 10000 == 0 and i > 0:
                logger.info(f"Progress: {i}/{len(input_data)} ({i/len(input_data)*100:.1f}%)")

            try:
                result = process_record(record)
                results.append(result)
            except Exception as e:
                # Always log individual failures
                logger.error(f"Failed processing record {record.id}: {e}")

        # Log completion with summary
        logger.info(f"Processing complete: {len(results)}/{len(input_data)} successful")
        return results

    except Exception as e:
        # Log fatal errors
        logger.error(f"Handler failed: {str(e)}")
        raise
```

### Logging Documentation
- [Snowflake Logging Guide](https://docs.snowflake.com/en/developer-guide/logging-tracing/logging) - Comprehensive guide to logging messages from functions and procedures
- [Python logging module](https://docs.python.org/3/library/logging.html) - Official Python logging documentation
- [SLF4J documentation](https://www.slf4j.org/manual.html) - Java/Scala logging framework

## Standard Library Integration

### Python Logging
- **Always:** Use Python's built-in `logging` module which automatically routes to event tables.
- **Rule:** Configure logger at module level, not inside functions.

```python
import logging

# Configure logging at module level
logger = logging.getLogger(__name__)

def process_data(session, df):
    """Process DataFrame with comprehensive logging."""
    logger.info(f"Starting data processing for {len(df)} rows")

    try:
        # Processing logic
        result = df.filter(df.amount > 0)
        logger.info(f"Filtered to {len(result)} valid records")

        if len(result) == 0:
            logger.warn("No valid records found after filtering")
            return None

        # Additional processing
        transformed = result.withColumn("processed_at", current_timestamp())
        logger.info("Data transformation completed successfully")

        return transformed

    except Exception as e:
        logger.error(f"Data processing failed: {str(e)}")
        raise
```

### Java/Scala Logging (SLF4J)
- **Always:** Use SLF4J logging framework for Java and Scala handlers.
- **Rule:** Follow same patterns as Python (strategic placement, appropriate levels).

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DataProcessor {
    private static final Logger logger = LoggerFactory.getLogger(DataProcessor.class);

    public DataFrame processData(Session session, DataFrame df) {
        logger.info("Starting data processing for {} rows", df.count());

        try {
            DataFrame result = df.filter(col("amount").gt(0));
            logger.info("Filtered to {} valid records", result.count());

            if (result.count() == 0) {
                logger.warn("No valid records found after filtering");
                return null;
            }

            DataFrame transformed = result.withColumn("processed_at", current_timestamp());
            logger.info("Data transformation completed successfully");

            return transformed;

        } catch (Exception e) {
            logger.error("Data processing failed: {}", e.getMessage());
            throw e;
        }
    }
}
```

## Log Level Strategy

### Environment-Based Log Levels
- **Production:** Use WARN or ERROR to capture significant events without excessive verbosity.
- **Development:** Use INFO or DEBUG for detailed troubleshooting.
- **Critical Systems:** Use ERROR or FATAL for mission-critical components.

**Configuration (see `111-snowflake-observability-core.md` for SQL commands):**
```sql
-- Production environment logging
ALTER DATABASE prod_db SET LOG_LEVEL = WARN;

-- Development environment logging
ALTER DATABASE dev_db SET LOG_LEVEL = INFO;

-- Critical UDF debugging
ALTER FUNCTION critical_calculation(number, number) SET LOG_LEVEL = DEBUG;
```

### When to Use Each Log Level

**DEBUG:** Development/troubleshooting only
```python
logger.debug(f"Variable state: x={x}, y={y}, computed_value={computed_value}")
```

**INFO:** Normal operation milestones
```python
logger.info(f"Processing completed: {len(results)} records processed in {elapsed_time}s")
```

**WARN:** Potential issues or unexpected states
```python
logger.warn(f"Large dataset detected: {len(data)} records (may impact performance)")
```

**ERROR:** Operation failures that are caught
```python
logger.error(f"Failed to process record {record.id}: {str(e)}")
```

**FATAL:** Critical system failures
```python
logger.fatal(f"Database connection lost: {str(e)}")
```

## Conditional Logging

### Logging Only Meaningful Scenarios
- **Rule:** Use conditional statements to log only when there's meaningful information to capture.
- **Benefit:** Reduces log volume and focuses on actionable insights.

```python
def validate_input(data):
    """Validate input with conditional logging."""
    if not data:
        logger.error("Input data is empty or null")
        return False

    if len(data) > 10000:
        logger.warn(f"Large dataset detected: {len(data)} records")

    # Only log validation details for problematic cases
    invalid_count = sum(1 for row in data if not is_valid(row))
    if invalid_count > 0:
        logger.warn(f"Found {invalid_count} invalid records out of {len(data)}")

    return invalid_count == 0
```

### Progress Logging for Long Operations
```python
def process_large_dataset(records):
    """Process with intelligent logging."""
    total = len(records)
    logger.info(f"Starting processing of {total} records")

    for i, record in enumerate(records):
        # Log progress at intervals (not every record)
        if i % 10000 == 0:
            logger.info(f"Progress: {i}/{total} records ({i/total*100:.1f}%)")

        try:
            process_record(record)
        except Exception as e:
            # Always log failures
            logger.error(f"Failed processing record {record.id}: {e}")

    logger.info(f"Processing complete: {total} records processed")
```

## Sampling Strategies

### Anti-Pattern: Logging in Tight Loops
**Anti-Pattern: Excessive logging without sampling**
```python
def process_large_dataset(records):
    """Process with excessive logging."""
    for record in records:  # Could be millions of records
        logger.debug(f"Processing record {record.id}")  # Generates huge log volume
        process_record(record)
```
**Problem:** Generates millions of log entries, overwhelming event tables and increasing storage costs.

### Correct Pattern: Use Sampling or Conditional Logging
```python
def process_large_dataset(records):
    """Process with intelligent logging."""
    total = len(records)
    for i, record in enumerate(records):
        # Log progress at intervals
        if i % 10000 == 0:
            logger.info(f"Progress: {i}/{total} records ({i/total*100:.1f}%)")

        try:
            process_record(record)
        except Exception as e:
            # Always log failures
            logger.error(f"Failed processing record {record.id}: {e}")
```

### Sampling with Configurable Rate
```python
import random

# Volume-conscious logging strategy
def log_with_sampling(logger, level, message, sample_rate=0.1):
    """Log messages with sampling to control volume."""
    if random.random() < sample_rate:
        logger.log(level, f"[SAMPLED {sample_rate*100}%] {message}")

# Use for high-frequency operations
for record in large_dataset:
    result = process_record(record)

    # Only log a sample of successful operations
    if result.success:
        log_with_sampling(logger, logging.INFO, f"Processed record {record.id}", sample_rate=0.01)
    else:
        # Always log failures
        logger.warn(f"Failed to process record {record.id}: {result.error}")
```

## Common Logging Anti-Patterns

### Anti-Pattern 1: Using DEBUG level in production
```sql
-- Setting DEBUG for all production workloads
ALTER DATABASE prod_db SET LOG_LEVEL = DEBUG;
```
**Problem:** Generates excessive log volume, increases costs, and may expose sensitive information.

**Correct Pattern: Environment-appropriate log levels**
```sql
-- Production: Conservative logging
ALTER DATABASE prod_db SET LOG_LEVEL = WARN;

-- Development: Verbose logging for debugging
ALTER DATABASE dev_db SET LOG_LEVEL = DEBUG;

-- Critical functions: Targeted debugging
ALTER FUNCTION prod_db.schema.critical_udf(varchar) SET LOG_LEVEL = INFO;
```

### Anti-Pattern 2: Not using standard logging libraries
```python
def my_function():
    # Using print statements instead of logging
    print("Starting processing")  # Does NOT route to event tables
    print(f"Error occurred: {error}")  # Not captured in telemetry
```

**Correct Pattern: Use standard logging libraries**
```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    # Automatically routes to event tables
    logger.info("Starting processing")
    try:
        # Processing logic
        pass
    except Exception as e:
        logger.error(f"Error occurred: {e}")  # Captured in telemetry
```

### Anti-Pattern 3: Logging sensitive data
```python
def authenticate_user(username, password):
    # NEVER LOG PASSWORDS OR TOKENS
    logger.debug(f"Authenticating user {username} with password {password}")  # FORBIDDEN
```

**Correct Pattern: Exclude sensitive data**
```python
def authenticate_user(username, password):
    # Log non-sensitive information only
    logger.info(f"Authentication attempt for user {username}")

    result = perform_authentication(username, password)

    if result.success:
        logger.info(f"User {username} authenticated successfully")
    else:
        logger.warn(f"Authentication failed for user {username}: {result.error_code}")
```
