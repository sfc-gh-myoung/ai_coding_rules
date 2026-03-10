# Go Patterns: HTTP Servers, Middleware & Production Readiness

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Go, Golang, HTTP server, middleware, graceful shutdown, timeouts, database patterns, production, server configuration
**TokenBudget:** ~2250
**ContextTier:** Low
**Depends:** 600-golang-core.md
**LoadTrigger:** kw:go-http, kw:go-server, kw:go-middleware

## Scope

**What This Rule Covers:**
Advanced Go patterns for production services including HTTP server configuration, middleware chains, graceful shutdown, database access patterns, and server hardening.

**When to Load This Rule:**
- Building HTTP servers or REST APIs in Go
- Implementing middleware chains
- Configuring production-ready server settings (timeouts, graceful shutdown)
- Setting up database access patterns in Go

**For core Go patterns (error handling, interfaces, testing, concurrency), see `600-golang-core.md`.**

## References

### Dependencies

**Must Load First:**
- **600-golang-core.md** - Core Go patterns and conventions

**Related:**
- **820-taskfile-automation.md** - Build automation for Go projects
- **821-makefile-automation.md** - Makefile automation for Go projects

### External Documentation
- [net/http Package](https://pkg.go.dev/net/http) - Standard library HTTP server
- [chi Router](https://github.com/go-chi/chi) - Lightweight HTTP router
- [database/sql Package](https://pkg.go.dev/database/sql) - Database access

## Contract

### Inputs and Prerequisites
- Go 1.22+ installed
- Core Go patterns understood (600-golang-core.md)
- HTTP service requirements identified

### Mandatory
- MUST set explicit timeouts on `http.Server` (ReadTimeout, WriteTimeout, IdleTimeout)
- MUST implement graceful shutdown with signal handling
- MUST use `context.Context` for request-scoped values and cancellation
- MUST close database connections with `defer db.Close()`

### Forbidden
- HTTP servers without timeouts (leads to resource exhaustion)
- Bare `log.Fatal` in goroutines (kills entire process without cleanup)
- Database connections without connection pool limits

### Execution Steps
1. Configure `http.Server` with explicit timeouts
2. Set up signal handling for graceful shutdown
3. Implement middleware chain (logging, recovery, auth)
4. Configure database connection pooling
5. Test with race detector and load testing

### Output Format
Production-ready Go HTTP server with timeouts, graceful shutdown, and middleware.

### Pre-Task Checks
- [ ] Check existing `http.Server` configuration: `grep -r "http.Server" --include="*.go" .`
- [ ] Check for existing signal handling: `grep -r "signal.Notify" --include="*.go" .`
- [ ] Verify Go version supports required features: `go version` (requires 1.22+)
- [ ] Check database driver import: `grep -r "database/sql" --include="*.go" .`

### Success Criteria
```bash
# Health check responds
curl -sf http://localhost:8080/health && echo "PASS" || echo "FAIL"

# Graceful shutdown: start server, send SIGTERM, verify in-flight requests complete
kill -SIGTERM $(pgrep myserver) && echo "Shutdown signal sent"

# Race detector passes
go test -race ./...
```

### Validation
- Server starts and responds to health checks
- Graceful shutdown completes in-flight requests
- Timeouts prevent resource exhaustion under load
- Race detector passes with concurrent requests

### Post-Execution Checklist
- [ ] HTTP server has ReadTimeout, WriteTimeout, IdleTimeout set
- [ ] Graceful shutdown handles SIGINT and SIGTERM
- [ ] Middleware chain includes recovery and logging
- [ ] Database connection pool configured (MaxOpenConns, MaxIdleConns)
- [ ] All tests pass with `-race` flag

> **Investigation Required**
> When applying this rule:
> 1. Check existing `http.Server` configuration for timeout values — avoid overwriting intentional settings
> 2. Identify signal handling patterns already in use (`os.Signal`, `signal.Notify`) — don't duplicate handlers
> 3. Review current database connection configuration (`sql.Open`, connection pool settings)
> 4. Check if a middleware chain already exists and what order it uses — recovery must be outermost

## HTTP Server with Timeouts

MUST always set explicit timeouts to prevent resource exhaustion:

```go
srv := &http.Server{
    Addr:         ":8080",
    Handler:      mux,
    ReadTimeout:  5 * time.Second,
    WriteTimeout: 10 * time.Second,
    IdleTimeout:  120 * time.Second,
}
```

**Why:** Without timeouts, slow clients can hold connections indefinitely, exhausting server resources.

**TLS/HTTPS Configuration:**
```go
// For production: use TLS with explicit certificate paths
srv := &http.Server{
    Addr:         ":8443",
    Handler:      mux,
    ReadTimeout:  5 * time.Second,
    WriteTimeout: 10 * time.Second,
    IdleTimeout:  120 * time.Second,
    TLSConfig: &tls.Config{
        MinVersion: tls.VersionTLS12,
    },
}

if err := srv.ListenAndServeTLS("cert.pem", "key.pem"); err != nil && err != http.ErrServerClosed {
    log.Fatalf("TLS server failed: %v", err)
}
```

> **Certificate errors:** If `ListenAndServeTLS` fails with "no such file" or "failed to find certificate", verify paths are absolute or relative to the working directory. Use `crypto/x509` to validate certificates programmatically in tests.

## Graceful Shutdown

MUST implement graceful shutdown for production services:

```go
srv := &http.Server{Addr: ":8080", Handler: mux}

go func() {
    sigCh := make(chan os.Signal, 1)
    signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
    <-sigCh

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()
    if err := srv.Shutdown(ctx); err != nil {
        log.Printf("HTTP server shutdown error: %v", err)
    }
}()

if err := srv.ListenAndServe(); err != http.ErrServerClosed {
    log.Fatalf("HTTP server error: %v", err)
}
```

**Why:** Abrupt termination drops in-flight requests, causing client errors and data loss.

## Middleware Patterns

### Recovery Middleware

```go
func recoveryMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                log.Printf("panic recovered: %v\n%s", err, debug.Stack())
                http.Error(w, "Internal Server Error", http.StatusInternalServerError)
            }
        }()
        next.ServeHTTP(w, r)
    })
}
```

### Logging Middleware

```go
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}
```

### Composing Middleware

```go
mux := http.NewServeMux()
mux.HandleFunc("GET /health", healthHandler)
mux.HandleFunc("GET /api/users", usersHandler)

// Recovery MUST be outermost — wraps everything including logging
handler := recoveryMiddleware(loggingMiddleware(authMiddleware(mux)))
```

> **Middleware ordering matters:** Recovery middleware MUST be the outermost wrapper. If logging is outermost instead, a panic bypasses the logger's duration measurement and may leave partial log entries. If auth is outermost, a panic in auth logic crashes the server.
>
> Correct order (outermost to innermost): `recovery` then `logging` then `auth` then `handler`

## Database Access Patterns

### Connection Pool Configuration

```go
db, err := sql.Open("postgres", connStr)
if err != nil {
    return fmt.Errorf("opening database: %w", err)
}
defer db.Close()

db.SetMaxOpenConns(25)
db.SetMaxIdleConns(5)
db.SetConnMaxLifetime(5 * time.Minute)

if err := db.PingContext(ctx); err != nil {
    return fmt.Errorf("pinging database: %w", err)
}
```

### Context-Aware Queries

```go
func getUser(ctx context.Context, db *sql.DB, id int) (*User, error) {
    var user User
    err := db.QueryRowContext(ctx,
        "SELECT id, name, email FROM users WHERE id = $1", id,
    ).Scan(&user.ID, &user.Name, &user.Email)
    if errors.Is(err, sql.ErrNoRows) {
        return nil, ErrNotFound
    }
    if err != nil {
        return nil, fmt.Errorf("querying user %d: %w", id, err)
    }
    return &user, nil
}
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: HTTP Server Without Timeouts

```go
// Bad: No timeouts — vulnerable to slowloris attacks
http.ListenAndServe(":8080", mux)
```
**Problem:** Slow or malicious clients hold connections open indefinitely.

**Correct Pattern:** Use `http.Server` struct with explicit timeout fields (see HTTP Server with Timeouts section above).

### Anti-Pattern 2: No Graceful Shutdown

```go
// Bad: Abrupt termination on signal
log.Fatal(http.ListenAndServe(":8080", mux))
```
**Problem:** In-flight requests are dropped, database transactions may be left incomplete.

**Correct Pattern:** Use signal-based graceful shutdown (see Graceful Shutdown section above).

### Anti-Pattern 3: Unbounded Database Connections

```go
// Bad: No connection pool limits
db, _ := sql.Open("postgres", connStr)
// Uses unlimited connections, exhausts database under load
```
**Problem:** Under high load, opens unlimited connections, exhausting database server resources.

**Correct Pattern:** Always set `SetMaxOpenConns`, `SetMaxIdleConns`, and `SetConnMaxLifetime` (see Database Access Patterns above).
