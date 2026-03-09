# Go Patterns: HTTP Servers, Middleware & Production Readiness

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Go, Golang, HTTP server, middleware, graceful shutdown, timeouts, database patterns, production, server configuration
**TokenBudget:** ~1650
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

handler := recoveryMiddleware(loggingMiddleware(mux))
```

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
