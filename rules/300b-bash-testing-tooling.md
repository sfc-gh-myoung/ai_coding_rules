# Bash Testing and Tooling Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:bash-testing, kw:bats
**Keywords:** Bash, testing, ShellCheck, bats, shell script testing, CI/CD, debugging, static analysis, linting, test automation
**TokenBudget:** ~3200
**ContextTier:** Medium
**Depends:** 300-bash-scripting-core.md

## Scope

**What This Rule Covers:**
Comprehensive bash testing, debugging, and modern tooling integration including ShellCheck, CI/CD workflows, and development practices to ensure script quality and reliability.

**When to Load This Rule:**
- Setting up testing infrastructure for bash scripts
- Integrating ShellCheck static analysis
- Writing automated tests with Bats or similar frameworks
- Implementing CI/CD pipelines for shell scripts
- Debugging complex bash script issues

## References

### Dependencies

**Must Load First:**
- **300-bash-scripting-core.md** - Foundation bash scripting patterns

**Related:**
- **300a-bash-security.md** - Security testing considerations

### External Documentation

- [ShellCheck Documentation](https://github.com/koalaman/shellcheck/wiki) - Static analysis tool for shell scripts and best practices
- [BATS Testing Framework](https://github.com/bats-core/bats-core) - Bash Automated Testing System for unit testing
- [Google Shell Testing Guide](https://google.github.io/styleguide/shellguide.html#s7-tests) - Professional shell script testing standards

## Contract

### Inputs and Prerequisites

- Bash scripts requiring testing and quality assurance
- Development environment with shell access
- Understanding of testing methodologies
- Access to CI/CD pipeline configuration (if applicable)

### Mandatory

- ShellCheck static analysis on all scripts
- Automated test suite (Bats or equivalent framework)
- CI/CD integration for automated testing
- Debug mode implementation for troubleshooting
- Pre-commit hooks for quality checks
- Test coverage for critical functions

### Forbidden

- Deploying scripts without ShellCheck validation
- Relying solely on manual testing
- Disabling ShellCheck warnings without mandatory inline justification
- Skipping error path testing
- Testing only happy path scenarios

### Execution Steps

1. Install ShellCheck and configure for project (via package manager or Docker)
2. Run ShellCheck on all existing scripts and document issues
3. Set up testing framework (Bats recommended) with test directory structure
4. Write unit tests for critical functions with positive and negative cases
5. Implement debug mode with trace logging and error reporting
6. Configure CI/CD pipeline to run ShellCheck and tests automatically
7. Add pre-commit hooks to validate scripts before commit
8. Document test coverage and testing procedures

### Output Format

Testing infrastructure with:
- ShellCheck configuration file (`.shellcheckrc`)
- Test directory with Bats test files (`test_*.bats`)
- CI/CD pipeline configuration (`.github/workflows/shell.yml` or equivalent)
- Pre-commit hooks (`.git/hooks/pre-commit`)
- Debug mode implementation in scripts
- Test documentation and coverage reports

### Validation

**Pre-Task-Completion Checks:**
- ShellCheck installed and accessible
- All scripts pass ShellCheck with 0 warnings (or documented exceptions)
- Test framework installed and configured
- Tests written for critical functions
- CI/CD pipeline runs successfully
- Pre-commit hooks functional

**Success Criteria:**
- `shellcheck scripts/*.sh` returns 0 exit code
- `bats tests/` passes all tests
- CI/CD pipeline green on latest commit
- Debug mode produces useful trace output
- Error paths tested and verified
- Test coverage documented (>80% for critical functions)

### Design Principles

- **Automate Everything:** Testing, linting, and validation in CI/CD
- **Fail Fast:** Catch issues early with pre-commit hooks and static analysis
- **Test Error Paths:** Verify failures are handled correctly
- **Debug-Friendly:** Comprehensive logging and trace modes
- **Continuous Quality:** Maintain high standards through automation

### Post-Execution Checklist

- [ ] ShellCheck installed and configured
- [ ] All scripts pass ShellCheck validation
- [ ] Test framework (Bats) installed
- [ ] Unit tests written and passing
- [ ] CI/CD pipeline configured and green
- [ ] Pre-commit hooks installed
- [ ] Debug mode implemented
- [ ] Error paths tested
- [ ] Test coverage documented
- [ ] Development environment setup documented

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Skipping ShellCheck Static Analysis

**Problem:** Not running ShellCheck on bash scripts before deployment, missing common bugs, security issues, and portability problems.

**Correct Pattern:**
```bash
# BAD: No static analysis
#!/bin/bash
# Script deployed without ShellCheck review
for f in $(ls *.txt); do  # SC2045: Iterating over ls output
    cat $f  # SC2086: Double quote to prevent globbing
done

# GOOD: ShellCheck in CI/CD pipeline
# .github/workflows/lint.yml
- name: ShellCheck
  run: shellcheck scripts/*.sh

# Or pre-commit hook
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.9.0.6
    hooks:
      - id: shellcheck
```

### Anti-Pattern 2: Testing Scripts Only Manually

**Problem:** Relying on manual testing of shell scripts instead of automated unit tests with frameworks like Bats or shunit2.

**Correct Pattern:**
```bash
# BAD: No automated tests
# "I ran it once and it worked"

# GOOD: Bats test file (test_deploy.bats)
#!/usr/bin/env bats

setup() {
    source ./deploy.sh
}

@test "validate_environment returns 0 for valid env" {
    export DEPLOY_ENV="production"
    run validate_environment
    [ "$status" -eq 0 ]
}

@test "validate_environment fails for missing env" {
    unset DEPLOY_ENV
    run validate_environment
    [ "$status" -eq 1 ]
    [[ "$output" =~ "DEPLOY_ENV required" ]]
}

# Run: bats test_deploy.bats
```

## Static Analysis with ShellCheck

### ShellCheck Integration
- **Requirement:** Use ShellCheck for static analysis of all bash scripts
- **Always:** Address ShellCheck warnings before deployment
- **Rule:** Include ShellCheck in CI/CD pipelines

```bash
# Install ShellCheck (various methods)
# Ubuntu/Debian: apt-get install shellcheck
# macOS: brew install shellcheck
# Or use Docker: docker run --rm -v "$PWD:/mnt" koalaman/shellcheck:stable

# Basic usage
shellcheck script.sh

# Check multiple files
find . -name "*.sh" -exec shellcheck {} +

# Output formats
shellcheck --format=gcc script.sh     # GCC-style output for IDEs
shellcheck --format=json script.sh    # JSON output for parsing
shellcheck --format=diff script.sh    # Show suggested fixes
```

### ShellCheck Configuration
- **Rule:** Use `.shellcheckrc` for project-wide settings (only for confirmed false positives, not style preferences):
```bash
# .shellcheckrc -- project-wide disables for false positives only
disable=SC2034,SC1091
shell=bash
```

### ShellCheck Directives
- **Rule:** Use inline directives for intentional exceptions:
```bash
#!/usr/bin/env bash

# Disable specific checks with justification
# shellcheck disable=SC2034  # Variable appears unused
readonly CONFIG_VERSION="1.0"  # Used by sourced configuration files

# Disable for external file sourcing
# shellcheck source=/dev/null
source "$EXTERNAL_CONFIG_FILE"

# Disable for specific lines
# shellcheck disable=SC2086  # Intentional word splitting
set -- $OPTIONS

# Enable specific checks
# shellcheck enable=check-unassigned-uppercase
MY_VAR="value"
```

### Common ShellCheck Fixes
```bash
# Quote variables: cp "$file" "$dest"
# Use $(): result="$(command)"
# Quote arrays: cmd "${array[@]}"
```

## Testing Frameworks and Strategies

### Simple Testing Framework
- **Rule:** Basic test framework:
```bash
# test_framework.sh
declare -g TESTS_RUN=0 TESTS_PASSED=0

assert_equals() {
    local expected="$1" actual="$2" name="${3:-test}"
    ((TESTS_RUN++))
    if [[ "$expected" == "$actual" ]]; then
        echo "PASS: $name"
        ((TESTS_PASSED++))
    else
        echo "FAIL: $name (expected '$expected', got '$actual')"
    fi
}

run_tests() {
    echo "Running tests..."
    for test_func in "$@"; do "$test_func"; done
    echo "Results: $TESTS_PASSED/$TESTS_RUN passed"
}
```

### Unit Testing Example
- **Rule:** Test functions separately:
```bash
# calculator.sh
add() { echo $(($1 + $2)); }

# test_calculator.sh
source test_framework.sh
source calculator.sh

test_add() {
    local result
    result="$(add 2 3)"
    assert_equals "5" "$result" "add function"
}

run_tests "test_add"
```

### Integration Testing
- **Rule:** Test system integration:
```bash
test_file_ops() {
    local temp_dir
    temp_dir="$(mktemp -d)"
    echo "test" > "$temp_dir/file"
    [[ -f "$temp_dir/file" ]] && echo "PASS: file creation"
    rm -rf "$temp_dir"
}
```

## Debugging Techniques

### Debug Mode Implementation
- **Rule:** Implement comprehensive debug modes:
```bash
#!/usr/bin/env bash

# Debug configuration
DEBUG="${DEBUG:-false}"
TRACE="${TRACE:-false}"
VERBOSE="${VERBOSE:-false}"

# Enable debug modes based on environment
if [[ "$DEBUG" == "true" ]]; then
    set -x  # Print commands as they execute
fi

if [[ "$TRACE" == "true" ]]; then
    PS4='+ ${BASH_SOURCE[0]}:${LINENO}: ${FUNCNAME[0]:+${FUNCNAME[0]}(): }'
    set -x
fi

# Debug logging functions
debug_log() {
    if [[ "$DEBUG" == "true" ]]; then
        echo "[DEBUG] $*" >&2
    fi
}

verbose_log() {
    if [[ "$VERBOSE" == "true" || "$DEBUG" == "true" ]]; then
        echo "[VERBOSE] $*" >&2
    fi
}

trace_log() {
    if [[ "$TRACE" == "true" ]]; then
        echo "[TRACE] ${BASH_SOURCE[1]}:${BASH_LINENO[0]} ${FUNCNAME[1]}() - $*" >&2
    fi
}

# Function entry/exit tracing
trace_function_entry() {
    trace_log "ENTER: $1 with args: ${*:2}"
}

trace_function_exit() {
    trace_log "EXIT: $1 with return code: $2"
}

# Example usage
process_file() {
    trace_function_entry "${FUNCNAME[0]}" "$@"
    local file="$1"
    local exit_code=0

    debug_log "Processing file: $file"

    if [[ ! -f "$file" ]]; then
        echo "Error: File not found: $file" >&2
        exit_code=1
    else
        verbose_log "File exists, processing..."
        # Process file here
        debug_log "File processed successfully"
    fi

    trace_function_exit "${FUNCNAME[0]}" "$exit_code"
    return $exit_code
}
```

### Error Debugging
- **Rule:** Implement detailed error reporting:
```bash
# Enhanced error handling with debugging info
debug_error() {
    local exit_code="$1"
    local line_number="$2"
    local command="$3"

    echo "ERROR: Command failed with exit code $exit_code" >&2
    echo "  Line: $line_number" >&2
    echo "  Command: $command" >&2
    echo "  Function: ${FUNCNAME[2]:-main}" >&2
    echo "  Script: ${BASH_SOURCE[1]}" >&2

    # Print call stack
    echo "Call stack:" >&2
    local i=1
    while [[ ${FUNCNAME[$i]} ]]; do
        echo "  $i: ${FUNCNAME[$i]} (${BASH_SOURCE[$i+1]}:${BASH_LINENO[$i]})" >&2
        ((i++))
    done
}

# Set up error trap
set -eE
trap 'debug_error $? $LINENO "$BASH_COMMAND"' ERR
```

### Performance Profiling
- **Rule:** Implement basic profiling for performance-sensitive functions:
```bash
profile() {
    local start end
    start="$(date +%s)"
    "$@"
    end="$(date +%s)"
    echo "Duration: $((end - start))s" >&2
}
```

## CI/CD Integration

### CI/CD Integration
- **Rule:** Automate testing:
```yaml
# .github/workflows/shell.yml
name: Shell Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: sudo apt-get install shellcheck
      - run: find . -name "*.sh" -exec shellcheck {} +
      - run: chmod +x tests/*.sh && tests/test_*.sh
```

### Pre-commit Hooks
- **Rule:** Validate before commit. See `dev-setup.sh` `setup_git_hooks()` function below for the canonical pre-commit hook installation pattern.

## Code Coverage and Quality Metrics

### Coverage Tracking
- **Rule:** Track test coverage for critical functions:
```bash
# Track function calls
declare -A CALLS=()
track_call() { CALLS["$1"]=$((${CALLS["$1"]:-0} + 1)); }
show_coverage() {
    for func in "${!CALLS[@]}"; do
        echo "$func: ${CALLS[$func]} calls"
    done
}
```

## Development Environment Setup

### Setup Checklist
- Install ShellCheck via package manager (`apt-get install shellcheck`, `brew install shellcheck`, or Docker)
- Install Bats: `npm install -g bats` or `brew install bats-core`
- Configure IDE ShellCheck extension (VS Code: `shellcheck.enable: true`, `shellcheck.run: "onType"`)
- Create project structure: `mkdir -p {src,tests,scripts,docs}`
- Set up pre-commit hook for ShellCheck (see CI/CD Integration section above)
- Create test template in `tests/` directory using framework from Testing Frameworks section
