# Go Core: Modern Standards & Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Golang patterns. Load for Go tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** Go, Golang, go.mod, modules, error handling, interfaces, goroutines, channels, testing, go fmt, golangci-lint, concurrency, context, defer
**TokenBudget:** ~4500
**ContextTier:** High
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Foundational Go development practices using idiomatic patterns, modern tooling (Go 1.21+), and industry-standard conventions to ensure reliable, maintainable, and performant Go codebases.

**When to Load This Rule:**
- Writing or modifying Go code
- Setting up new Go projects with modules
- Implementing error handling and concurrency patterns
- Establishing Go project structure and organization
- Configuring Go tooling (go fmt, vet, golangci-lint)
- Writing Go tests with race detection
- Implementing interfaces and goroutines

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates

**Related:**
- None currently - this is the core Go rule

### External Documentation

**Official Documentation:**
- [Go Documentation](https://go.dev/doc/) - Official Go language documentation
- [Effective Go](https://go.dev/doc/effective_go) - Essential reading for idiomatic Go
- [Go Modules Reference](https://go.dev/ref/mod) - Module system documentation

**Best Practices Guides:**
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments) - Common code review feedback
- [Standard Go Project Layout](https://github.com/golang-standards/project-layout) - Project structure conventions
- [golangci-lint](https://golangci-lint.run/) - Fast linters runner for Go

## Contract

### Inputs and Prerequisites

- Go 1.21+ installed (check with `go version`)
- `go.mod` file present (or create with `go mod init`)
- golangci-lint installed for comprehensive linting
- Project requirements and existing codebase identified

### Mandatory

- **Always use `go fmt`** - Format all code before committing
- **Run `go vet`** - Static analysis catches common mistakes
- **Use `golangci-lint run`** - Comprehensive linting with multiple analyzers
- **Run `go test -race ./...`** - Race detector catches concurrency bugs
- **Handle all errors** - Never use `_` to ignore errors without explicit justification
- **Use `context.Context`** - First parameter for functions that do I/O or may be cancelled
- **Document exports** - All exported identifiers must have doc comments

### Forbidden

- Ignoring errors with blank identifier `_` without explanatory comment
- Bare `panic` in library code (libraries should return errors)
- Global mutable state (use dependency injection)
- `init()` functions with side effects (network calls, file I/O)
- Missing error handling
- Unexported error types (errors should be values, not types)

### Execution Steps

1. Initialize module with `go mod init <module-path>`
2. Structure code following standard layout (`cmd/`, `internal/`, `pkg/`)
3. Write idiomatic Go following Effective Go guidelines
4. Handle all errors explicitly with wrapping context (`fmt.Errorf` with `%w`)
5. Write table-driven tests with race detection
6. Run formatters and linters before committing

### Output Format

```go
// Package myservice provides user management functionality.
package myservice

import (
    "context"
    "fmt"
)

// User represents a user in the system.
type User struct {
    ID   int
    Name string
}

// GetUser retrieves a user by ID.
// Returns an error if the user is not found or if the database query fails.
func GetUser(ctx context.Context, id int) (*User, error) {
    if id <= 0 {
        return nil, fmt.Errorf("invalid user ID: %d", id)
    }
    
    // Simulate database query
    user := &User{ID: id, Name: "John Doe"}
    return user, nil
}
```

```go
// myservice_test.go
package myservice_test

import (
    "context"
    "testing"
    
    "example.com/myservice"
)

func TestGetUser(t *testing.T) {
    tests := []struct {
        name    string
        id      int
        wantErr bool
    }{
        {name: "valid user", id: 1, wantErr: false},
        {name: "invalid ID", id: -1, wantErr: true},
        {name: "zero ID", id: 0, wantErr: true},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            ctx := context.Background()
            user, err := myservice.GetUser(ctx, tt.id)
            
            if (err != nil) != tt.wantErr {
                t.Errorf("GetUser() error = %v, wantErr %v", err, tt.wantErr)
                return
            }
            
            if !tt.wantErr && user == nil {
                t.Error("GetUser() returned nil user without error")
            }
        })
    }
}
```

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

Reference: Complete validation protocol in `000-global-core.md` and `AGENTS.md`

**Code Quality:**
- **CRITICAL:** `go fmt ./...` produces no changes
- **CRITICAL:** `go vet ./...` passes with no issues
- **CRITICAL:** `golangci-lint run` passes with no errors
- **CRITICAL:** All errors handled explicitly (no ignored errors with `_`)
- **Format Check:** All exported identifiers have godoc comments
- **Format Check:** Imports grouped (stdlib, external, internal)

**Testing:**
- **CRITICAL:** `go test ./...` passes all tests
- **CRITICAL:** `go test -race ./...` passes with no race conditions
- **Coverage:** Use `go test -cover ./...` for coverage metrics
- **Benchmarks:** Use `go test -bench=. ./...` for performance tests

**Module Management:**
- **CRITICAL:** `go mod tidy` leaves no changes
- **CRITICAL:** `go mod verify` confirms dependencies are unmodified
- **Format Check:** `go.mod` has proper module path and Go version

**Success Criteria:**
- All Go tooling passes (fmt, vet, lint, test)
- No race conditions detected
- All errors handled with context
- Exported APIs documented
- Tests use table-driven pattern

**Investigation Required:**
1. **Check Go version** (`go version`) to ensure compatibility with modern features
2. **Read existing code** to understand patterns before adding new code
3. **Verify module path** in `go.mod` matches repository structure
4. **Check for existing tests** to understand testing patterns
5. **Review golangci-lint config** (`.golangci.yml`) for project-specific rules

**Anti-Pattern Examples:**
- Ignoring errors: `result, _ := doSomething()`
- Using `panic` in library code
- Global mutable state without synchronization
- Missing context parameter for I/O operations
- Unexported error types

**Correct Pattern:**
- "Let me check your go.mod and Go version first."
- [checks go.mod, verifies Go 1.21+, reads existing code]
- "I see you're using standard project layout. Here's the implementation with proper error handling..."
- [implements with godoc, runs go fmt, go vet, golangci-lint, tests]

### Design Principles

- **Accept interfaces, return structs** - Functions should be flexible on input, concrete on output
- **Make the zero value useful** - Types should work without explicit initialization
- **Errors are values** - Handle them explicitly, don't ignore or panic
- **Don't communicate by sharing memory** - Share memory by communicating (channels)
- **A little copying is better than a little dependency** - Avoid unnecessary abstractions
- **Clear is better than clever** - Write code that's easy to understand

### Post-Execution Checklist

**Before Starting:**
- [ ] Rule dependencies loaded (000-global-core.md)
- [ ] Go 1.21+ available
- [ ] golangci-lint installed
- [ ] Existing Go codebase reviewed (if modifying)

**After Completion:**
- [ ] **CRITICAL:** `go fmt ./...` produces no changes
- [ ] **CRITICAL:** `go vet ./...` passes with no issues
- [ ] **CRITICAL:** `golangci-lint run` passes with no errors
- [ ] **CRITICAL:** `go test -race ./...` passes with no race conditions
- [ ] **CRITICAL:** `go mod tidy` leaves no changes
- [ ] All exported identifiers have godoc comments
- [ ] All errors handled explicitly
- [ ] Context.Context used for I/O operations
- [ ] Tests use table-driven pattern
- [ ] No global mutable state
- [ ] No `init()` functions with side effects
- [ ] CHANGELOG.md and README.md updated as required

## Key Principles

### Project Structure

Follow the standard Go project layout:

Directory structure for `project/`:
- **cmd/** - Main applications
  - **myapp/** - `main.go`
- **internal/** - Private packages (not importable)
  - **config/**, **service/**
- **pkg/** - Public packages (importable)
  - **api/**
- `go.mod`, `go.sum`
- `Makefile` (or `Taskfile.yml`)
- `README.md`

**Rules:**
- Use `internal/` for packages that should not be imported by other modules
- Use `cmd/` for application entry points (one `main.go` per application)
- Keep `main.go` minimal - delegate to internal packages
- Use `pkg/` sparingly - only for truly reusable public APIs

### Naming Conventions

**Package Names:**
- Short, lowercase, single-word names
- No underscores or mixedCaps
- Avoid generic names like `util`, `common`, `misc`

**Identifiers:**
- MixedCaps for exported, mixedCaps for unexported
- Acronyms should be consistent case: `HTTPServer`, `xmlParser`
- Interface names: single-method interfaces use method name + "er" (`Reader`, `Writer`)

**File Names:**
- Lowercase with underscores: `user_service.go`, `http_handler.go`
- Test files: `*_test.go`

### Error Handling

**Always handle errors explicitly:**

```go
// Good: Wrap errors with context
result, err := doSomething()
if err != nil {
    return fmt.Errorf("failed to do something: %w", err)
}

// Good: Check specific errors
if errors.Is(err, sql.ErrNoRows) {
    return nil, ErrNotFound
}

// Good: Extract error details
var pathErr *os.PathError
if errors.As(err, &pathErr) {
    log.Printf("path error on %s: %v", pathErr.Path, pathErr.Err)
}
```

**Error wrapping rules:**
- Use `%w` verb to wrap errors (enables `errors.Is` and `errors.As`)
- Add context that helps debugging: what operation failed, what input caused it
- Define sentinel errors for expected conditions: `var ErrNotFound = errors.New("not found")`

### Interfaces

**Accept interfaces, return structs:**

```go
// Good: Accept interface
func ProcessData(r io.Reader) error {
    // Can accept *os.File, *bytes.Buffer, *http.Response.Body, etc.
}

// Good: Return concrete type
func NewService(db *sql.DB) *Service {
    return &Service{db: db}
}
```

**Interface design:**
- Keep interfaces small (1-3 methods)
- Define interfaces where they are used, not where they are implemented
- Don't export interfaces for mocking - use internal test doubles

### Concurrency Patterns

**Use context for cancellation:**

```go
func FetchData(ctx context.Context, url string) ([]byte, error) {
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, fmt.Errorf("creating request: %w", err)
    }
    // ...
}
```

**Goroutine patterns:**

```go
// Good: Use errgroup for coordinated goroutines
g, ctx := errgroup.WithContext(ctx)
for _, item := range items {
    item := item // capture loop variable (not needed in Go 1.22+)
    g.Go(func() error {
        return process(ctx, item)
    })
}
if err := g.Wait(); err != nil {
    return err
}
```

**Channel patterns:**
- Sender closes the channel, never the receiver
- Use `select` with `context.Done()` for cancellation
- Prefer unbuffered channels unless you have a specific reason for buffering

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Ignoring Errors**
```go
// Bad: Silently ignoring error
result, _ := doSomething()

// Bad: Empty error check
if err != nil {
    // do nothing
}
```
**Problem:** Bugs become invisible; failures propagate silently; debugging becomes impossible.

**Correct Pattern:**
```go
// Good: Handle or propagate
result, err := doSomething()
if err != nil {
    return fmt.Errorf("doing something: %w", err)
}

// Good: If truly ignorable, document why
_ = writer.Close() // Best-effort cleanup; main data already flushed
```

**Anti-Pattern 2: Naked Returns in Long Functions**
```go
// Bad: Hard to track what's being returned
func process(data []byte) (result string, err error) {
    // 50 lines of code...
    return // What are we returning?
}
```
**Problem:** Reduces readability; makes refactoring error-prone; hides return values.

**Correct Pattern:**
```go
// Good: Explicit returns
func process(data []byte) (string, error) {
    // ...
    return result, nil
}

// Acceptable: Named returns for defer error handling
func writeFile(path string, data []byte) (err error) {
    f, err := os.Create(path)
    if err != nil {
        return err
    }
    defer func() {
        if cerr := f.Close(); err == nil {
            err = cerr
        }
    }()
    _, err = f.Write(data)
    return err
}
```

**Anti-Pattern 3: Overusing `interface{}`/`any`**
```go
// Bad: Loses type safety
func Process(data any) any {
    // Type assertions everywhere
}
```
**Problem:** Runtime panics instead of compile-time errors; code becomes hard to understand.

**Correct Pattern:**
```go
// Good: Use generics for type-safe polymorphism
func Process[T Processable](data T) Result[T] {
    // Type-safe operations
}

// Good: Use specific interfaces
func Process(data io.Reader) ([]byte, error) {
    return io.ReadAll(data)
}
```

**Anti-Pattern 4: Goroutine Leaks**
```go
// Bad: Goroutine never terminates
func watch(ch chan Event) {
    go func() {
        for event := range ch { // Blocks forever if ch never closes
            handle(event)
        }
    }()
}
```
**Problem:** Memory leaks; resource exhaustion; unpredictable behavior.

**Correct Pattern:**
```go
// Good: Use context for cancellation
func watch(ctx context.Context, ch chan Event) {
    go func() {
        for {
            select {
            case <-ctx.Done():
                return
            case event, ok := <-ch:
                if !ok {
                    return
                }
                handle(event)
            }
        }
    }()
}
```

**Anti-Pattern 5: Package-Level `init()` with Side Effects**
```go
// Bad: Hidden initialization, hard to test
func init() {
    db, _ = sql.Open("postgres", os.Getenv("DATABASE_URL"))
    http.HandleFunc("/", handler)
}
```
**Problem:** Makes testing difficult; hidden dependencies; unpredictable initialization order.

**Correct Pattern:**
```go
// Good: Explicit initialization in main or constructors
func main() {
    db, err := sql.Open("postgres", os.Getenv("DATABASE_URL"))
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    svc := NewService(db)
    http.Handle("/", svc.Handler())
}
```

## Tooling and Environment

### Required Tools

- **Go 1.21+** - Use latest stable version; pin in `go.mod`
- **gofmt/goimports** - Code formatting (use `goimports` for import organization)
- **go vet** - Built-in static analysis
- **golangci-lint** - Meta-linter aggregating multiple tools
- **staticcheck** - Advanced static analysis (included in golangci-lint)

### Golangci-lint Configuration

```yaml
# .golangci.yml
linters:
  enable:
    - errcheck      # Check for unchecked errors
    - gosimple      # Simplify code
    - govet         # Vet examines Go source code
    - ineffassign   # Detect ineffectual assignments
    - staticcheck   # Advanced static analysis
    - unused        # Check for unused code
    - gocritic      # Opinionated linter
    - gofmt         # Check formatting
    - goimports     # Check import formatting
    - misspell      # Check for misspellings
    - prealloc      # Find slice preallocation opportunities

linters-settings:
  errcheck:
    check-type-assertions: true
  gocritic:
    enabled-tags:
      - diagnostic
      - style
      - performance

run:
  timeout: 5m
```

### Automation with Taskfiles

```makefile
# Makefile
.PHONY: fmt vet lint test build

fmt:
    go fmt ./...
    goimports -w .

vet:
    go vet ./...

lint:
    golangci-lint run

test:
    go test -race -cover ./...

build:
    go build -o bin/ ./cmd/...

all: fmt vet lint test build
```

## Testing Patterns

### Table-Driven Tests

Standard pattern for testing multiple cases:

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name string
        a, b int
        want int
    }{
        {"positive", 2, 3, 5},
        {"negative", -1, -1, -2},
        {"zero", 0, 0, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.want {
                t.Errorf("Add(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}
```

### Test Helpers

```go
// testutil/helpers.go
package testutil

import "testing"

// AssertEqual fails the test if got != want.
func AssertEqual[T comparable](t testing.TB, got, want T) {
    t.Helper()
    if got != want {
        t.Errorf("got %v, want %v", got, want)
    }
}

// RequireNoError fails the test immediately if err != nil.
func RequireNoError(t testing.TB, err error) {
    t.Helper()
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}
```

### Race Detection

Always run tests with race detector in CI:

```bash
go test -race ./...
```

## Dependencies and Modules

### Module Management

```bash
# Initialize new module
go mod init github.com/org/project

# Add dependency
go get github.com/pkg/errors@v0.9.1

# Update all dependencies
go get -u ./...

# Clean up unused dependencies
go mod tidy

# Vendor dependencies (optional, for reproducibility)
go mod vendor
```

### Dependency Guidelines

- Pin major versions explicitly in `go.mod`
- Run `go mod tidy` before committing
- Review `go.sum` changes in code review
- Prefer stdlib over external dependencies when reasonable
- Evaluate dependencies for maintenance status and security
