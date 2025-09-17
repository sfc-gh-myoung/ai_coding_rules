**Description:** Bash testing, debugging, and modern tooling integration including ShellCheck, CI/CD, and development workflows.
**AppliesTo:** `**/*.sh`, `**/*.bash`, `scripts/**/*`, `bin/**/*`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-09-13

# Bash Testing and Tooling Best Practices

## Purpose
Provide comprehensive bash testing, debugging, and modern tooling integration including ShellCheck, CI/CD workflows, and development practices to ensure script quality and reliability.

## 1. Static Analysis with ShellCheck

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
- **Rule:** Use `.shellcheckrc`:
```bash
# .shellcheckrc
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

## 2. Testing Frameworks and Strategies

### Simple Testing Framework
- **Rule:** Basic test framework:
```bash
# test_framework.sh
declare -g TESTS_RUN=0 TESTS_PASSED=0

assert_equals() {
    local expected="$1" actual="$2" name="${3:-test}"
    ((TESTS_RUN++))
    if [[ "$expected" == "$actual" ]]; then
        echo "✓ PASS: $name"
        ((TESTS_PASSED++))
    else
        echo "✗ FAIL: $name (expected '$expected', got '$actual')"
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

## 3. Debugging Techniques

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
- **Consider:** Basic profiling:
```bash
profile() {
    local start end
    start="$(date +%s)"
    "$@"
    end="$(date +%s)"
    echo "Duration: $((end - start))s" >&2
}
```

## 4. CI/CD Integration

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
      - uses: actions/checkout@v3
      - run: sudo apt-get install shellcheck
      - run: find . -name "*.sh" -exec shellcheck {} +
      - run: chmod +x tests/*.sh && tests/test_*.sh
```

### Pre-commit Hooks
- **Rule:** Validate before commit:
```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit
set -e

# Check staged shell scripts
mapfile -t scripts < <(git diff --cached --name-only | grep '\.sh$' || true)
for script in "${scripts[@]}"; do
    [[ -f "$script" ]] && shellcheck "$script"
done
```

## 5. Code Coverage and Quality Metrics

### Coverage Tracking
- **Consider:** Simple coverage:
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

## 6. Development Environment Setup

### IDE Integration
- **Rule:** Configure development environment for bash scripting:
```bash
# VS Code settings.json for bash development
{
    "shellcheck.enable": true,
    "shellcheck.executablePath": "/usr/bin/shellcheck",
    "shellcheck.run": "onType",
    "files.associations": {
        "*.sh": "shellscript",
        "*.bash": "shellscript"
    },
    "editor.formatOnSave": true,
    "[shellscript]": {
        "editor.defaultFormatter": "foxundermoon.shell-format"
    }
}
```

### Development Scripts
- **Rule:** Create development helper scripts:
```bash
#!/usr/bin/env bash
# dev-setup.sh - Development environment setup

setup_git_hooks() {
    echo "Setting up git hooks..."
    
    # Create pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

# Run ShellCheck on staged files
mapfile -t staged_scripts < <(git diff --cached --name-only | grep '\.sh$' || true)
for script in "${staged_scripts[@]}"; do
    [[ -f "$script" ]] && shellcheck "$script"
done
EOF
    
    chmod +x .git/hooks/pre-commit
    echo "Pre-commit hook installed"
}

install_dependencies() {
    echo "Installing development dependencies..."
    
    # Install ShellCheck based on OS
    if command -v apt-get >/dev/null; then
        sudo apt-get update && sudo apt-get install -y shellcheck
    elif command -v brew >/dev/null; then
        brew install shellcheck
    elif command -v dnf >/dev/null; then
        sudo dnf install -y ShellCheck
    else
        echo "Please install ShellCheck manually"
        exit 1
    fi
}

create_project_structure() {
    echo "Creating project structure..."
    
    mkdir -p {src,tests,scripts,docs}
    
    # Create basic test template
    cat > tests/test_template.sh << 'EOF'
#!/usr/bin/env bash
# Test template

source "$(dirname "${BASH_SOURCE[0]}")/../test_framework.sh"

test_example() {
    assert_equals "expected" "expected" "example test"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_test_suite "Template Tests" "test_example"
fi
EOF
    
    chmod +x tests/test_template.sh
}

# Main setup
main() {
    echo "Setting up bash development environment..."
    
    install_dependencies
    setup_git_hooks
    create_project_structure
    
    echo "Development environment setup complete!"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

## 7. Documentation and Maintenance

### Automated Documentation Generation
- **Consider:** Generate documentation from code:
```bash
#!/usr/bin/env bash
# generate-docs.sh - Extract documentation from shell scripts

generate_function_docs() {
    local script_file="$1"
    local output_file="$2"
    
    echo "# Functions in $(basename "$script_file")" > "$output_file"
    echo >> "$output_file"
    
    # Extract function definitions and comments
    awk '
        /^[[:space:]]*#/ { 
            comment = comment $0 "\n"
        }
        /^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*\(\)/ {
            if (comment) {
                print "## " $1
                print comment
                print "```bash"
            }
            print $0
            in_function = 1
            brace_count = 0
            comment = ""
        }
        in_function && /{/ { brace_count++ }
        in_function && /}/ { 
            brace_count--
            if (brace_count == 0) {
                print "```"
                print ""
                in_function = 0
            }
        }
        in_function { print }
        !/^[[:space:]]*#/ && !/^[[:space:]]*[a-zA-Z_]/ { comment = "" }
    ' "$script_file" >> "$output_file"
}
```

## References and Resources

- [ShellCheck Documentation](https://github.com/koalaman/shellcheck/wiki)
- [Bash Automated Testing System (BATS)](https://github.com/bats-core/bats-core)
- [Google Shell Style Guide - Testing](https://google.github.io/styleguide/shellguide.html#s7-tests)
- [Advanced Bash-Scripting Guide - Testing](https://tldp.org/LDP/abs/html/debugging.html)

## Rule Type and Scope

- **Type:** Agent Requested (use `@302-bash-testing-tooling.md` to apply)
- **Scope:** Bash testing, debugging, development workflows, CI/CD
- **Applies to:** Development environments, testing frameworks, automation pipelines
- **Validation:** Automated testing, ShellCheck integration, CI/CD validation
