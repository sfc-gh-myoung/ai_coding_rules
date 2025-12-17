# Snowflake Connection Error Classification

## Metadata

**SchemaVersion:** v3.0
**RuleVersion:** v1.0.0
**Keywords:** connection errors, error classification, network policy, authentication, VPN, error codes, 08001, 390114, error handling, snowflake.connector, DatabaseError, message analysis, error detection
**TokenBudget:** ~2400
**ContextTier:** High
**Depends:** rules/100-snowflake-core.md
**LastUpdated:** 2025-12-09

## Purpose

Provide systematic error classification for Snowflake connection errors to prevent misdiagnosis of network policy violations as authentication failures, enabling accurate troubleshooting guidance across all Python-based Snowflake applications.

## Rule Scope

Connection error handling for `snowflake-connector-python` across Python scripts, CLI tools, REST APIs, Streamlit apps, and Snowpark applications.

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Message-first classification**: Never map Snowflake error codes 1:1 to problem types. Error codes are categories; message content contains diagnosis.
- **Specific-to-generic order**: Check for network policy indicators before auth checks, before transient checks, before generic connection fallbacks.
- **Actionable guidance output**: Each classification must yield a concrete next action (VPN reconnect vs auth refresh vs retry/backoff vs request privileges).

**Detection Order (Most Specific First):**
1. **Network Policy Violations** - Check for "not allowed to access", "IP/Token" patterns
2. **Authentication Errors** - Check specific auth codes (390114, 390318, 390144)
3. **Generic Connection Errors** - Fallback for 08001, 08003

**Anti-Pattern:** `if error_code == "08001": return "Auth expired"` [FAIL]
**Correct:** Check message content first, then code [PASS]

## Contract

<contract>
<inputs_prereqs>
Exception object from snowflake.connector.errors; error message string; error code
</inputs_prereqs>

<mandatory>
Message content analysis before error code matching; detection order from specific to generic
</mandatory>

<forbidden>
1:1 error code to problem type mapping; skipping message content analysis; generic-first detection order
</forbidden>

<steps>
1. Extract error message and code from exception
2. Check for network policy indicators in message (highest priority)
3. Check for authentication-specific error codes
4. Check for transient/permission errors
5. Fall back to generic connection error
6. Return error classification with appropriate guidance
</steps>

<output_format>
Error classification enum/constant with user-facing guidance string
</output_format>

<validation>
- Network policy errors NOT classified as auth errors
- Error classification includes specific guidance (VPN reconnect vs auth refresh)
- Detection order is specific to generic
- Message content checked before code matching
</validation>

<design_principles>
- **Specificity First:** Check most specific patterns before generic codes
- **Message Analysis:** Error codes are categories; messages contain diagnosis
- **Actionable Guidance:** Each error type maps to specific user actions
- **VPN Awareness:** Network policy violations are common in enterprise environments
</design_principles>

</contract>

## Error Classification Hierarchy

### Critical Pattern: Detection Order Matters

Snowflake error code `08001` appears in multiple scenarios:
- VPN disconnection (network policy violation)
- Authentication token expiration
- Network timeout
- Wrong account URL

**WRONG Approach:**
```python
# [FAIL] This misclassifies VPN issues as auth problems
AUTH_ERROR_CODES = {
    "08001": "Authentication expired"
}

if error_code in AUTH_ERROR_CODES:
    return "Run snow connection test to refresh auth"
```

**CORRECT Approach:**
```python
# [PASS] Check message content, specific -> generic
def classify_snowflake_error(error_msg: str, error_code: str) -> ErrorType:
    # 1. Network Policy (HIGHEST PRIORITY)
    if _is_network_policy_error(error_msg):
        return ErrorType.NETWORK_POLICY
    
    # 2. Authentication (specific codes)
    if _is_auth_error(error_code):
        return ErrorType.AUTH_EXPIRED
    
    # 3. Transient
    if _is_transient_error(error_msg):
        return ErrorType.TRANSIENT
    
    # 4. Permissions
    if _is_permission_error(error_msg):
        return ErrorType.PERMISSION
    
    # 5. Generic Connection (fallback)
    return ErrorType.CONNECTION_FAILED
```

### 1. Network Policy Violations (Check First)

**Detection Pattern:**
```python
def _is_network_policy_error(error_msg: str) -> bool:
    """
    Detect network policy violations (VPN disconnect, IP not allowlisted).
    
    MUST check BEFORE generic auth/connection checks.
    Often appears with error code 08001 or 250001.
    """
    indicators = [
        "not allowed to access",
        "ip/token",
        "network policy",
        "allowlist",
        "whitelist",
        "incoming request with ip"
    ]
    msg_lower = error_msg.lower()
    return any(indicator in msg_lower for indicator in indicators)
```

**Example Error:**
```
250001 (08001): Failed to connect to DB: account.snowflakecomputing.com:443.
Incoming request with IP/Token 73.15.210.19 is not allowed to access Snowflake.
Contact your local security administrator.
```

**User Guidance:**
```
NETWORK POLICY VIOLATION
Your IP address is not allowed to access Snowflake.

Actions:
1. Reconnect to your VPN
2. Wait 5 seconds
3. Refresh/retry connection

If still failing: Contact your Snowflake administrator to add your IP to the network policy allowlist.
```

### 2. Authentication Errors (Specific Codes)

**Detection Pattern:**
```python
def _is_auth_error(error_code: str) -> bool:
    """
    Detect authentication failures using specific error codes.
    
    Only check AFTER network policy check.
    """
    AUTH_ERROR_CODES = {
        "390114": "Authentication token has expired",
        "390318": "Session token has expired", 
        "390144": "Invalid authentication token",
        "390195": "JWT token has expired"
    }
    return error_code in AUTH_ERROR_CODES
```

**User Guidance:**
```
AUTHENTICATION EXPIRED
Your Snowflake authentication token has expired.

Actions:
1. Run: snow connection test
2. Re-authenticate if prompted
3. Refresh/retry connection
```

### 3. Transient Network Errors

**Detection Pattern:**
```python
def _is_transient_error(error_msg: str) -> bool:
    """
    Detect temporary network issues that may self-resolve.
    """
    indicators = [
        "timeout",
        "connection reset",
        "temporarily unavailable",
        "network unreachable"
    ]
    msg_lower = error_msg.lower()
    return any(indicator in msg_lower for indicator in indicators)
```

**User Guidance:**
```
NETWORK TIMEOUT
Temporary network issue - retrying automatically.

Auto-retry with exponential backoff (3 attempts).
```

### 4. Permission Errors

**Detection Pattern:**
```python
def _is_permission_error(error_msg: str) -> bool:
    """
    Detect insufficient privileges for database operations.
    """
    indicators = [
        "insufficient privileges",
        "permission denied",
        "access denied",
        "not authorized"
    ]
    msg_lower = error_msg.lower()
    # Exclude network policy messages (already handled)
    if "not allowed to access snowflake" in msg_lower:
        return False
    return any(indicator in msg_lower for indicator in indicators)
```

**User Guidance:**
```
PERMISSION DENIED
You don't have privileges for this operation.

Actions:
1. Contact your Snowflake administrator
2. Request necessary role/privileges
3. Check current role: SELECT CURRENT_ROLE();
```

### 5. Generic Connection Errors (Fallback)

**Detection Pattern:**
```python
def _is_connection_error(error_code: str) -> bool:
    """
    Generic connection failures (only after specific checks).
    """
    CONNECTION_ERROR_CODES = {
        "08001": "Unable to establish connection",
        "08003": "Connection does not exist",
        "08004": "Connection rejected"
    }
    return error_code in CONNECTION_ERROR_CODES
```

**User Guidance:**
```
CONNECTION FAILED
Unable to connect to Snowflake.

Actions:
1. Verify account URL: account.snowflakecomputing.com
2. Check network connectivity
3. Verify warehouse/database exist
4. Try: snow connection test
```

## Common Error Code Patterns

**Error Code Reference:**
- **08001** - VPN disconnect, auth expired, wrong URL - Check message content (network policy vs auth)
- **250001** - Network policy violation - Look for "not allowed to access" in message
- **390114** - Token expired - Auth-specific code
- **390318** - Session expired - Auth-specific code
- **390144** - Invalid token - Auth-specific code
- **002003** - SQL compilation error - Not connection-related
- **000606** - Object not found - Permission or object existence

## Implementation Example

### Complete Classification Function

```python
from enum import Enum
from typing import Tuple

class SnowflakeErrorType(Enum):
    NETWORK_POLICY = "network_policy"
    AUTH_EXPIRED = "auth_expired"
    TRANSIENT = "transient"
    PERMISSION = "permission"
    CONNECTION = "connection"
    UNKNOWN = "unknown"

def classify_snowflake_connection_error(
    error_msg: str,
    error_code: str
) -> Tuple[SnowflakeErrorType, str]:
    """
    Classify Snowflake connection error and return user guidance.
    
    Args:
        error_msg: Full error message string
        error_code: Snowflake error code (e.g., "08001")
    
    Returns:
        (ErrorType, user_guidance_string)
    """
    # Order matters: Most specific first!
    
    # 1. Network Policy (VPN disconnect)
    if _is_network_policy_error(error_msg):
        guidance = (
            "NETWORK POLICY VIOLATION\n\n"
            "1. Reconnect to your VPN\n"
            "2. Wait 5 seconds\n"
            "3. Retry connection"
        )
        return (SnowflakeErrorType.NETWORK_POLICY, guidance)
    
    # 2. Authentication
    if _is_auth_error(error_code):
        guidance = (
            "AUTHENTICATION EXPIRED\n\n"
            "Run: snow connection test"
        )
        return (SnowflakeErrorType.AUTH_EXPIRED, guidance)
    
    # 3. Transient
    if _is_transient_error(error_msg):
        guidance = "NETWORK TIMEOUT - Retrying automatically"
        return (SnowflakeErrorType.TRANSIENT, guidance)
    
    # 4. Permission
    if _is_permission_error(error_msg):
        guidance = (
            "PERMISSION DENIED\n\n"
            "Contact administrator for privileges"
        )
        return (SnowflakeErrorType.PERMISSION, guidance)
    
    # 5. Generic Connection
    if _is_connection_error(error_code):
        guidance = (
            "CONNECTION FAILED\n\n"
            "1. Verify account URL\n"
            "2. Check network\n"
            "3. Run: snow connection test"
        )
        return (SnowflakeErrorType.CONNECTION, guidance)
    
    # 6. Unknown
    guidance = f"Error {error_code}: {error_msg}"
    return (SnowflakeErrorType.UNKNOWN, guidance)
```

### Usage in Python Scripts

```python
from snowflake.connector import connect
from snowflake.connector.errors import DatabaseError

try:
    conn = connect(
        account="myaccount",
        user="myuser",
        authenticator="externalbrowser"
    )
except DatabaseError as e:
    error_type, guidance = classify_snowflake_connection_error(
        str(e),
        e.errno if hasattr(e, 'errno') else ""
    )
    
    if error_type == SnowflakeErrorType.NETWORK_POLICY:
        print(guidance)
        print("\nWaiting for VPN reconnection...")
        time.sleep(5)
        # Retry logic here
    elif error_type == SnowflakeErrorType.AUTH_EXPIRED:
        print(guidance)
        subprocess.run(["snow", "connection", "test"])
    else:
        print(guidance)
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: 1:1 Code Mapping
```python
# [FAIL] Assumes 08001 always means auth failure
if error_code == "08001":
    return "Authentication expired - refresh token"

# Problem: 08001 can be VPN, auth, or network timeout
```
**Problem:** Misclassifies network policy failures (VPN/IP allowlist) as authentication expiry, leading to incorrect remediation.

**Correct Pattern:** Check message text for network policy indicators first, then auth-specific codes, then generic fallbacks.

### Anti-Pattern 2: Generic-First Detection
```python
# [FAIL] Checks generic connection before specific network policy
if "08001" in str(error_code):
    return ErrorType.CONNECTION  # Catches VPN issues incorrectly!

if "not allowed to access" in error_msg:
    return ErrorType.NETWORK_POLICY  # Never reached!
```
**Problem:** The first match wins; VPN/network policy signals are never reached.

**Correct Pattern:** Order checks from most specific to most generic (network policy -> auth -> transient -> permission -> connection fallback).

### Anti-Pattern 3: Ignoring Message Content
```python
# [FAIL] Only checks error codes
def classify_error(error_code: str):
    if error_code in AUTH_CODES:
        return "Auth problem"
    return "Connection problem"

# Problem: Misses network policy violations in message text
```
**Problem:** Network policy failures often reuse generic connection codes; skipping message analysis causes repeated misdiagnosis.

**Correct Pattern:** Parse message content first (network policy strings), then use codes only as supporting signal.

## Post-Execution Checklist

Before deploying connection error handling:

- [ ] Network policy detection runs FIRST (before auth/connection)
- [ ] Error message content analyzed (not just codes)
- [ ] Each error type has specific user guidance (VPN vs auth vs network)
- [ ] Detection order: specific to generic
- [ ] VPN disconnection NOT classified as auth error
- [ ] Auto-retry implemented for transient errors
- [ ] Logging includes error type classification for debugging

## Validation

**Success Checks:**
- Network policy errors (message includes "not allowed to access") are classified as NETWORK_POLICY even if error code is 08001/250001
- Auth errors (e.g., 390114/390318/390144) are classified as AUTH_EXPIRED only after network policy check fails
- Transient messages (timeout/reset) are classified as TRANSIENT and trigger retry/backoff
- Permission messages ("insufficient privileges") are classified as PERMISSION
- Generic connection codes (08001/08003/08004) only classify as CONNECTION when no more-specific match exists

**Negative Tests:**
- A network policy message must not be classified as AUTH_EXPIRED
- A generic 08001 without network policy indicators must not automatically map to auth expiry
- Reordering checks to generic-first should be caught in review (it breaks the hierarchy)

## Output Format Examples

```python
# Example usage (pseudo-log output)
error_type, guidance = classify_snowflake_connection_error(
    "250001 (08001): Incoming request with IP/Token ... is not allowed to access Snowflake.",
    "08001",
)
print(error_type.value)  # network_policy
print(guidance)          # NETWORK POLICY VIOLATION ... Reconnect to VPN ...
```

## References

### Related Rules
- `rules/100-snowflake-core.md` - Foundational Snowflake practices
- `rules/101e-snowflake-streamlit-sql-errors.md` - Streamlit error presentation
- `rules/109c-snowflake-app-deployment-troubleshooting.md` - Production deployment errors
- `rules/200-python-core.md` - Python exception handling patterns

### External Documentation
- [Snowflake CLI](https://docs.snowflake.com/developer-guide/snowflake-cli/index) - Connection testing and CLI usage
- [Network policies](https://docs.snowflake.com/en/user-guide/network-policies) - IP allowlist enforcement and troubleshooting context
- [`snowflake-connector-python` docs](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector) - Connector behaviors and error surfaces

## Related Rules

- **100-snowflake-core.md**: Foundational Snowflake practices
- **101e-snowflake-streamlit-sql-errors.md**: Streamlit error presentation
- **109c-snowflake-app-deployment-troubleshooting.md**: Production deployment errors
- **200-python-core.md**: Python exception handling patterns
