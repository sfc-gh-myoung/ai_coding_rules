# Snowflake Connection Error Classification

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:connection-error, kw:timeout
**Keywords:** connection errors, error classification, network policy, authentication, VPN, error codes, 08001, 390114, error handling, snowflake.connector, DatabaseError, message analysis, error detection
**TokenBudget:** ~3900
**ContextTier:** High
**Depends:** 100-snowflake-core.md

## Scope

**What This Rule Covers:**
Systematic error classification for Snowflake connection errors using message-first analysis (never 1:1 error code mapping) to prevent misdiagnosis of network policy violations as authentication failures. Detection order: network policy indicators -> specific auth codes (390114, 390318, 390144) -> transient errors -> permissions -> generic 08001 fallback. Applies to snowflake-connector-python across Python scripts, CLI tools, REST APIs, Streamlit apps, and Snowpark applications.

**When to Load This Rule:**
- Handling Snowflake connection errors (snowflake.connector.errors.DatabaseError)
- Diagnosing network policy violations vs authentication failures
- Implementing connection error classification logic
- Troubleshooting VPN-related connection issues
- Providing actionable error guidance in Python applications
- Handling error code 08001 ambiguity (VPN/auth/network/URL)

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake fundamentals and connection patterns

**Related:**
- **101e-snowflake-streamlit-sql-errors.md** - SQL error handling patterns for Streamlit
- **101b-snowflake-streamlit-performance.md** - Connection caching with @st.cache_resource

### External Documentation

**Snowflake:**
- [Snowflake Error Codes](https://docs.snowflake.com/en/user-guide/admin-error-codes.html) - Complete error code reference
- [Network Policies](https://docs.snowflake.com/en/user-guide/network-policies.html) - IP allowlist configuration
- [snowflake-connector-python Errors](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-api.html#errors) - Connector exception classes

**Authentication:**
- [OAuth Integration](https://docs.snowflake.com/en/user-guide/oauth-snowflake.html) - OAuth authentication patterns
- [Key Pair Authentication](https://docs.snowflake.com/en/user-guide/key-pair-auth.html) - Certificate-based authentication

## Contract

### Inputs and Prerequisites

Exception object from snowflake.connector.errors; error message string; error code

### Mandatory

Message content analysis before error code matching; detection order from specific to generic

### Forbidden

1:1 error code to problem type mapping; skipping message content analysis; generic-first detection order

### Execution Steps

1. Extract error message and code from exception
2. Check for network policy indicators in message (highest priority)
3. Check for authentication-specific error codes
4. Check for transient/permission errors
5. Fall back to generic connection error
6. Return error classification with appropriate guidance

### Output Format

Error classification enum/constant with user-facing guidance string

### Validation

**Test Requirements:**
- Network policy errors NOT classified as auth errors
- Error classification includes specific guidance (VPN reconnect vs auth refresh)
- Detection order is specific to generic
- Message content checked before code matching

**Success Criteria:**
- Message-first classification implemented
- Specific-to-generic detection order enforced
- Actionable guidance provided for each error type
- VPN/network policy errors correctly identified

### Design Principles

- **Specificity First:** Check most specific patterns before generic codes
- **Message Analysis:** Error codes are categories; messages contain diagnosis
- **Actionable Guidance:** Each error type maps to specific user actions
- **VPN Awareness:** Network policy violations are common in enterprise environments

**Detection Order (Most Specific First):**
1. **Network Policy Violations** - Check for "not allowed to access", "IP/Token" patterns
2. **Authentication Errors** - Check specific auth codes (390114, 390318, 390144)
3. **Generic Connection Errors** - Fallback for 08001, 08003

**Anti-Pattern:** `if error_code == "08001": return "Auth expired"` [FAIL]  
**Correct:** Check message content first, then code [PASS]

### Post-Execution Checklist

- [ ] Message content analyzed before error code matching
- [ ] Detection order: network policy -> auth -> transient -> generic
- [ ] Network policy errors NOT misclassified as auth errors
- [ ] Each error type provides actionable guidance
- [ ] VPN reconnect guidance for network policy violations
- [ ] Auth refresh guidance for authentication errors
- [ ] Retry/backoff guidance for transient errors

## Error Classification Hierarchy

### Critical Pattern: Detection Order Matters

**Language-Agnostic Error Classification:**

1. **NETWORK_POLICY** — Message contains "not allowed to access", "IP/Token", or "network policy". Action: Reconnect VPN, check IP allowlist
2. **AUTH_EXPIRED** — Error code 390114, 390318, 390144, or 390195. Action: Run `snow connection test`
3. **TRANSIENT** — Message contains "timeout", "connection reset", or "temporarily unavailable". Action: Retry with exponential backoff
4. **PERMISSION** — Message contains "insufficient privileges" or "permission denied". Action: Contact admin for role/privileges
5. **CONNECTION** — Error code 08001, 08003, or 08004 (fallback). Action: Verify account URL, check network

**Detection order matters:** Check patterns top-to-bottom. Network policy MUST be checked before auth codes.

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

**Retry Implementation:**
```python
import time

def retry_on_transient(func, max_retries=3, base_delay=1.0):
    """Retry a Snowflake operation on transient errors with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except DatabaseError as e:
            if not _is_transient_error(str(e)):
                raise  # Non-transient errors should not be retried
            if attempt == max_retries - 1:
                raise  # Exhausted retries
            time.sleep(base_delay * 2 ** attempt)  # 1s, 2s, 4s
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

# Guidance messages per error type
_GUIDANCE = {
    SnowflakeErrorType.NETWORK_POLICY: (
        "NETWORK POLICY VIOLATION\n\n"
        "1. Reconnect to your VPN\n"
        "2. Wait 5 seconds\n"
        "3. Retry connection"
    ),
    SnowflakeErrorType.AUTH_EXPIRED: "AUTHENTICATION EXPIRED\n\nRun: snow connection test",
    SnowflakeErrorType.TRANSIENT: "NETWORK TIMEOUT - Retrying automatically",
    SnowflakeErrorType.PERMISSION: "PERMISSION DENIED\n\nContact administrator for privileges",
    SnowflakeErrorType.CONNECTION: (
        "CONNECTION FAILED\n\n"
        "1. Verify account URL\n"
        "2. Check network\n"
        "3. Run: snow connection test"
    ),
}

# Compose detectors: reuses functions defined in sections 1-5 above
_DETECTORS = [
    # (check_func, uses_msg, error_type)
    (_is_network_policy_error, True,  SnowflakeErrorType.NETWORK_POLICY),
    (_is_auth_error,           False, SnowflakeErrorType.AUTH_EXPIRED),
    (_is_transient_error,      True,  SnowflakeErrorType.TRANSIENT),
    (_is_permission_error,     True,  SnowflakeErrorType.PERMISSION),
    (_is_connection_error,     False, SnowflakeErrorType.CONNECTION),
]

def classify_snowflake_connection_error(
    error_msg: str,
    error_code: str
) -> Tuple[SnowflakeErrorType, str]:
    """Classify Snowflake connection error using composition of detectors."""
    error_msg = error_msg or ""
    error_code = error_code or ""
    for detector, uses_msg, error_type in _DETECTORS:
        if detector(error_msg if uses_msg else error_code):
            return (error_type, _GUIDANCE[error_type])
    return (SnowflakeErrorType.UNKNOWN, f"Error {error_code}: {error_msg}")
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
        str(e.errno) if hasattr(e, 'errno') else ""
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

### Usage in Streamlit Apps

```python
import streamlit as st
from snowflake.connector.errors import DatabaseError

def get_connection():
    try:
        return st.connection("snowflake")
    except DatabaseError as e:
        error_type, guidance = classify_snowflake_connection_error(
            str(e), str(getattr(e, 'errno', ''))
        )
        if error_type == SnowflakeErrorType.NETWORK_POLICY:
            st.error("VPN disconnected. Reconnect and click Retry.")
        elif error_type == SnowflakeErrorType.AUTH_EXPIRED:
            st.error("Authentication expired. Run `snow connection test`, then Retry.")
        elif error_type == SnowflakeErrorType.TRANSIENT:
            st.warning("Temporary network issue. Retrying...")
        else:
            st.error(guidance)

        if st.button("Retry Connection"):
            st.rerun()
        return None
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
