---
appliesTo:
  - "**/*.py"
  - "**/*.scl"
  - "**/*.js"
---
<!-- Generated for GitHub Copilot repository instructions. See https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions -->

**Keywords:** Logging, Python logging, logger, log levels, DEBUG, INFO, WARN, ERROR, FATAL, conditional logging, sampling, tight loop logging, standard logging libraries, log volume control, cost management, setup logging, log configuration, logging best practices, log handlers
**TokenBudget:** ~2700
**ContextTier:** High
**Depends:** 100-snowflake-core, 111-snowflake-observability-core

# Snowflake Observability: Logging Best Practices

## Purpose
Provide comprehensive logging best practices for Snowflake handler code, covering standard library integration, strategic log level usage, conditional logging patterns, and volume control strategies to optimize observability while managing costs.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Logging patterns for Python, Java/Scala, and JavaScript handlers in Snowflake environments

## Contract

**MANDATORY:**
- **Inputs/Prereqs:** 
  - Active event table configured (see `111-snowflake-observability-core.md`)
  - Telemetry levels configured appropriately for environment
  - Standard logging library available (Python `logging`, Java `slf4j`)

- **Allowed Tools:** 
  - Standard logging libraries (Python `logging`, Java `slf4j`, JavaScript `console`)
  - Conditional logging with if-statements for volume control
  - Sampling strategies for high-frequency operations

**FORBIDDEN:**
- **Forbidden Tools:** 
  - `print` statements instead of logging (do NOT route to event tables)
  - DEBUG logging in production environments without cost analysis
  - Logging in tight loops without sampling
  - Logging sensitive data (PII, credentials, tokens)

**MANDATORY:**
- **Required Steps:**
  1. **Import:** Use standard logging library at module level
  2. **Configure:** Set appropriate log levels for environment (see `111-snowflake-observability-core.md`)
  3. **Implement:** Add strategic log statements at key decision points
  4. **Sample:** Use conditional logging or sampling for high-frequency operations
  5. **Validate:** Verify logs appear in event tables after deployment

- **Output Format:** 
  - Python/Java/JavaScript code with proper logging import statements
  - Log messages with meaningful context (include relevant variables)
  - Conditional logging for volume control
  - Comments explaining sampling strategy

- **Validation Steps:** 
  - Verify standard logging library is imported
  - Confirm log levels match environment (no DEBUG in prod)
  - Check tight loops use sampling or conditional logging
  - Validate logs appear in event tables

## Quick Start TL;DR (Essential Patterns Reference)

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Use standard logging libraries** - Python `logging`, Java `slf4j` (NOT print statements)
- **WARN+ for production** - DEBUG generates 10-100x more data
- **Conditional logging** - Only log meaningful scenarios
- **Sample tight loops** - Log every Nth iteration, not every record
- **Include context** - Log relevant variables for troubleshooting
- **Never log sensitive data** - PII, credentials, tokens must be excluded

**Quick Checklist:**
- [ ] Standard logging library imported (not print)
- [ ] Log levels appropriate (WARN+ for prod, DEBUG for dev)
- [ ] Tight loops use sampling (every Nth iteration)
- [ ] Sensitive data excluded from logs

## Key Principles
- Use standard logging libraries that automatically route to event tables (Python `logging`, Java `slf4j`).
- Set log levels based on environment: WARN+ for production, DEBUG for development only.
- Implement conditional logging to capture only meaningful scenarios and control data volume.
- Use sampling strategies for high-frequency operations (log every Nth iteration in tight loops).
- Include relevant context in log messages (variable values, record counts, error details).
- Never log sensitive data (PII, credentials, API tokens) - security and compliance violation.

## 1. Standard Library Integration

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

## 2. Log Level Strategy

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

## 3. Conditional Logging

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

## 4. Sampling Strategies

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

## 5. Common Logging Anti-Patterns

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

## Quick Compliance Checklist
- [ ] Logging uses standard libraries (Python `logging`, Java `slf4j`, NOT print)
- [ ] Log levels appropriate for environment (WARN+ for prod, DEBUG for dev only)
- [ ] Tight loops use sampling (every Nth iteration, NOT every record)
- [ ] Sensitive data excluded (no passwords, tokens, PII in logs)
- [ ] Meaningful context included (variable values, record counts, error details)
- [ ] Cost implications considered (DEBUG generates 10-100x more data)
- [ ] Conditional logging implemented (only log meaningful scenarios)

## Validation
- **Success Checks:** 
  - Logging from handler code appears in event table within minutes
  - Log messages include relevant context for troubleshooting
  - Log volume is reasonable for environment (< 10MB/day for typical prod workload)
  - Sensitive data NOT present in log messages

- **Negative Tests:** 
  - Using `print` statements should NOT appear in event tables
  - DEBUG level in production should trigger cost review
  - Tight loop logging without sampling should be flagged
  - Sensitive data in logs should be rejected in code review

> **Investigation Required**  
> When applying this rule:
> 1. **Check existing logging patterns** - Review current handler code for logging usage
> 2. **Verify log levels** - Ensure environment-appropriate levels (WARN+ for prod)
> 3. **Identify tight loops** - Look for high-frequency operations that need sampling
> 4. **Review log volume** - Query event tables to understand current volume
> 5. **Scan for sensitive data** - Check logs don't contain PII, credentials, tokens
>
> **Anti-Pattern:**
> "Adding DEBUG logging everywhere... (without cost analysis)"
> "Using print statements for logging... (won't route to event tables)"
>
> **Correct Pattern:**
> "Let me review your current logging patterns first."
> [checks event table volume, reviews log levels, scans for anti-patterns]
> "I see you're using INFO level with 5MB/day volume. Adding WARN-level logging for errors following this pattern..."

## Response Template
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

## References

### Logging Documentation
- [Snowflake Logging Guide](https://docs.snowflake.com/en/developer-guide/logging-tracing/logging) - Comprehensive guide to logging messages from functions and procedures
- [Python logging module](https://docs.python.org/3/library/logging.html) - Official Python logging documentation
- [SLF4J documentation](https://www.slf4j.org/manual.html) - Java/Scala logging framework

### Related Rules
- **Observability Core**: `111-snowflake-observability-core.md` - Telemetry configuration and event tables
- **Observability Tracing**: `111b-snowflake-observability-tracing.md` - Distributed tracing patterns
- **Observability Monitoring**: `111c-snowflake-observability-monitoring.md` - Monitoring and analysis
- **Cost Governance**: `105-snowflake-cost-governance.md` - Cost optimization strategies for telemetry data
