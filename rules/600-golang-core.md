# Go Core: Modern Standards & Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential Golang patterns. Load for Go tasks.
> Specialized rules depend on this foundation.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Go, Golang, go.mod, modules, error handling, interfaces, goroutines, channels, testing, go fmt, golangci-lint, concurrency, context, defer
**TokenBudget:** ~3500
**ContextTier:** High
**Depends:** rules/000-global-core.md

## Purpose

Establishes foundational Go development practices using idiomatic patterns, modern tooling, and industry-standard conventions to ensure reliable, maintainable, and performant Go codebases.

## Rule Scope

Foundational Go development practices with modern tooling (Go 1.21+), project structure, error handling, testing, and concurrency fundamentals

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Always use `go fmt`** - Format all code before committing (or `gofmt -s` for simplification)
- **Run `go vet`** - Static analysis catches common mistakes
- **Use `golangci-lint run`** - Comprehensive linting with multiple analyzers
- **Run `go test -race ./...`** - Race detector catches concurrency bugs
- **Handle all errors** - Never use `_` to ignore errors without explicit justification
- **Use `context.Context`** - First parameter for functions that do I/O or may be cancelled

**Pre-Execution Checklist:**
- [ ] `go fmt ./...` runs clean
- [ ] `go vet ./...` passes with no issues
- [ ] `golangci-lint run` passes
- [ ] `go test -race ./...` passes
- [ ] `go mod tidy` leaves no changes
- [ ] All exported identifiers have doc comments

## Contract

<contract>
<inputs_prereqs>
Go 1.21+; `go.mod` present; golangci-lint installed
</inputs_prereqs>

<mandatory>
`go fmt`, `go vet`, `go test`, `golangci-lint`; Taskfile or Makefile for automation
</mandatory>

<forbidden>
Ignoring errors with blank identifier without comment; bare `panic` in library code; global mutable state; `init()` with side effects
</forbidden>

<steps>
1. Initialize module with `go mod init`
2. Structure code following standard layout (`cmd/`, `internal/`, `pkg/`)
3. Write idiomatic Go following Effective Go guidelines
4. Handle all errors explicitly with wrapping context
5. Write table-driven tests with race detection
6. Run linters and formatters before committing
</steps>

<output_format>
Go source files (.go) with godoc comments; go.mod/go.sum for dependencies
</output_format>

<validation>
`go fmt` produces no changes; `go vet` passes; `golangci-lint run` passes; `go test -race ./...` passes
</validation>

<design_principles>
- Accept interfaces, return structs
- Make the zero value useful
- Errors are values - handle them explicitly
- Don't communicate by sharing memory; share memory by communicating
- A little copying is better than a little dependency
- Clear is better than clever
</design_principles>

</contract>

## Key Principles

### 1. Project Structure

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

### 2. Naming Conventions

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

### 3. Error Handling

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

### 4. Interfaces

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

### 5. Concurrency

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

## Post-Execution Checklist

- [ ] `go fmt ./...` produces no changes
- [ ] `go vet ./...` passes with no issues
- [ ] `golangci-lint run` passes (or project-specific linter config)
- [ ] `go test -race ./...` passes with all tests green
- [ ] `go mod tidy` leaves no uncommitted changes
- [ ] All exported functions, types, and constants have doc comments
- [ ] Errors are wrapped with context using `fmt.Errorf` and `%w`
- [ ] No ignored errors without explicit justification comment
- [ ] Context is passed as first parameter where applicable
- [ ] No goroutine leaks (all goroutines have termination paths)
- [ ] CHANGELOG.md updated for code changes

## Validation

**Success Checks:**
- `go build ./...` compiles without errors
- `go fmt ./...` produces no diff
- `go vet ./...` reports no issues
- `golangci-lint run` passes
- `go test -race -cover ./...` passes with acceptable coverage
- `go mod tidy` produces no changes

**Negative Tests:**
- Unhandled errors should fail linting
- Missing doc comments on exports should trigger warnings
- Data races should be caught by `-race` flag
- Unused dependencies should be caught by `go mod tidy`

> **Investigation Required**
> When applying this rule:
> 1. **Check go.mod** for Go version and existing dependencies
> 2. **Verify golangci-lint config** - Look for `.golangci.yml` or `.golangci.yaml`
> 3. **Check existing code patterns** - Match project's error handling and naming conventions
> 4. **Review test patterns** - Use existing test helpers and fixtures
> 5. **Check for Makefile/Taskfile** - Use existing automation patterns

## Output Format Examples

```go
// Example: Well-structured Go service

package service

import (
    "context"
    "errors"
    "fmt"
)

// ErrNotFound is returned when a requested resource does not exist.
var ErrNotFound = errors.New("not found")

// UserService handles user-related operations.
type UserService struct {
    repo UserRepository
}

// UserRepository defines the interface for user data access.
type UserRepository interface {
    GetByID(ctx context.Context, id string) (*User, error)
    Save(ctx context.Context, user *User) error
}

// NewUserService creates a new UserService with the given repository.
func NewUserService(repo UserRepository) *UserService {
    return &UserService{repo: repo}
}

// GetUser retrieves a user by ID.
func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
    if id == "" {
        return nil, errors.New("id cannot be empty")
    }

    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("getting user %s: %w", id, err)
    }

    return user, nil
}
```

```go
// Example: Table-driven test

package service_test

import (
    "context"
    "errors"
    "testing"

    "myapp/internal/service"
)

func TestUserService_GetUser(t *testing.T) {
    tests := []struct {
        name    string
        id      string
        want    *service.User
        wantErr error
    }{
        {
            name:    "valid user",
            id:      "user-123",
            want:    &service.User{ID: "user-123", Name: "Alice"},
            wantErr: nil,
        },
        {
            name:    "empty id",
            id:      "",
            want:    nil,
            wantErr: errors.New("id cannot be empty"),
        },
        {
            name:    "not found",
            id:      "nonexistent",
            want:    nil,
            wantErr: service.ErrNotFound,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            repo := &mockRepo{users: map[string]*service.User{
                "user-123": {ID: "user-123", Name: "Alice"},
            }}
            svc := service.NewUserService(repo)

            got, err := svc.GetUser(context.Background(), tt.id)

            if tt.wantErr != nil {
                if err == nil {
                    t.Errorf("expected error %v, got nil", tt.wantErr)
                }
                return
            }
            if err != nil {
                t.Errorf("unexpected error: %v", err)
                return
            }
            if got.ID != tt.want.ID {
                t.Errorf("got ID %s, want %s", got.ID, tt.want.ID)
            }
        })
    }
}
```

```bash
# Validation commands
go fmt ./...
go vet ./...
golangci-lint run
go test -race -cover ./...
go mod tidy
```

## References

### External Documentation
- [Effective Go](https://go.dev/doc/effective_go) - Official Go style and idioms guide
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments) - Common code review feedback
- [Standard Go Project Layout](https://github.com/golang-standards/project-layout) - Community project structure guide
- [Go Proverbs](https://go-proverbs.github.io/) - Rob Pike's guiding principles
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md) - Industry-adopted style guide
- [golangci-lint](https://golangci-lint.run/) - Fast linters runner for Go

### Related Rules
- **Global Core**: `rules/000-global-core.md` - Foundation for all rules
- **Taskfile Automation**: `rules/820-taskfile-automation.md` - Build automation patterns

## 1. Tooling & Environment

### 1.1 Required Tools

- **Go 1.21+** - Use latest stable version; pin in `go.mod`
- **gofmt/goimports** - Code formatting (use `goimports` for import organization)
- **go vet** - Built-in static analysis
- **golangci-lint** - Meta-linter aggregating multiple tools
- **staticcheck** - Advanced static analysis (included in golangci-lint)

### 1.2 Recommended golangci-lint Configuration

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

### 1.3 Makefile/Taskfile Integration

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

## 2. Testing Patterns

### 2.1 Table-Driven Tests

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

### 2.2 Test Helpers

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

### 2.3 Race Detection

Always run tests with race detector in CI:

```bash
go test -race ./...
```

## 3. Dependencies & Modules

### 3.1 Module Management

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

### 3.2 Dependency Guidelines

- Pin major versions explicitly in `go.mod`
- Run `go mod tidy` before committing
- Review `go.sum` changes in code review
- Prefer stdlib over external dependencies when reasonable
- Evaluate dependencies for maintenance status and security
