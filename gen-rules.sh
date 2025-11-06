#!/usr/bin/env bash
# Script: gen-rules
# Description: System-wide wrapper for AI coding rules generation from anywhere
# Author: AI Coding Rules Project
# Version: 2.2
# Last Updated: 2025-11-05
# Usage: gen-rules [OPTIONS] <task> [task-args]

set -euo pipefail

# ============================================================================
# Constants and Configuration
# ============================================================================

readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly SCRIPT_VERSION="2.2"

# Allow PROJECT_DIR override via environment variable
# Default assumes script is in project root; override with GEN_RULES_PROJECT_DIR if installed elsewhere
readonly DEFAULT_PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIR="${GEN_RULES_PROJECT_DIR:-${DEFAULT_PROJECT_DIR}}"

# Exit codes
readonly EXIT_SUCCESS=0
readonly EXIT_ERROR=1
readonly EXIT_INVALID_ARGS=2
readonly EXIT_MISSING_DEPENDENCY=3
readonly EXIT_INVALID_PROJECT=4

# Debug and verbose modes
DEBUG="${DEBUG:-false}"
VERBOSE="${VERBOSE:-false}"

# ============================================================================
# Logging Functions
# ============================================================================

log_error() {
    echo "[$SCRIPT_NAME ERROR] $*" >&2
}

log_warning() {
    echo "[$SCRIPT_NAME WARNING] $*" >&2
}

log_info() {
    if [[ "$VERBOSE" == "true" || "$DEBUG" == "true" ]]; then
        echo "[$SCRIPT_NAME INFO] $*" >&2
    fi
}

log_debug() {
    if [[ "$DEBUG" == "true" ]]; then
        echo "[$SCRIPT_NAME DEBUG] $*" >&2
    fi
}

# ============================================================================
# Help and Usage
# ============================================================================

show_usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS] <task> [task-args]

Generate AI coding rules for various IDEs/agents from anywhere on your system.
By default, rules are generated into the current working directory.

OPTIONS:
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output
    -d, --debug         Enable debug mode
    -V, --version       Show version information
    -p, --project DIR   Override project directory (default: \$GEN_RULES_PROJECT_DIR or script directory)

GENERATION TASKS:
    rule:cursor         Generate Cursor .mdc files
    rule:copilot        Generate GitHub Copilot instructions
    rule:cline          Generate Cline rules
    rule:universal      Generate Universal rules (IDE-agnostic)
    rule:all            Generate all IDE-specific rules (including universal)
    rule:cursor:dry     Dry run preview for Cursor
    rule:cursor:check   Check if Cursor rules are current
    
DEPLOYMENT TASKS:
    deploy:cursor       Deploy Cursor rules to target project (.cursor/rules/)
    deploy:copilot      Deploy Copilot rules to target project (.github/copilot/instructions/)
    deploy:cline        Deploy Cline rules to target project (.clinerules/)
    deploy:universal    Deploy Universal rules to target project (rules/)

OTHER TASKS:
    validate            Run all validation checks
    status              Show project status

GENERATION EXAMPLES:
    # Generate Cursor rules into current directory
    $SCRIPT_NAME rule:cursor

    # Generate Universal rules (works with any IDE/LLM) - recommended
    $SCRIPT_NAME rule:universal

    # Generate all formats (cursor, copilot, cline, universal)
    $SCRIPT_NAME rule:all

    # Generate with verbose output
    $SCRIPT_NAME --verbose rule:universal

    # Generate to specific directory
    $SCRIPT_NAME rule:cursor DEST=/path/to/project

    # Dry run preview (no files written)
    $SCRIPT_NAME rule:cursor:dry

    # Check if rules need regeneration
    $SCRIPT_NAME rule:universal:check

DEPLOYMENT EXAMPLES:
    # Deploy Cursor rules to current directory
    $SCRIPT_NAME deploy:cursor
    
    # Deploy Universal rules to specific project
    $SCRIPT_NAME deploy:universal DEST=~/my-project
    
    # Deploy Cline rules to sibling project
    cd ~/dev/ai_coding_rules_gitlab
    $SCRIPT_NAME deploy:cline DEST=../my-streamlit-app
    
    # Deploy Copilot rules with verbose output
    $SCRIPT_NAME --verbose deploy:copilot DEST=/path/to/project

PROJECT DIRECTORY EXAMPLES:
    # Override project directory if script installed elsewhere
    $SCRIPT_NAME --project ~/my-ai-rules rule:cursor

    # Use environment variable for project directory
    export GEN_RULES_PROJECT_DIR=~/my-ai-rules
    $SCRIPT_NAME rule:universal

ENVIRONMENT VARIABLES:
    GEN_RULES_PROJECT_DIR   Override default project directory
    DEBUG                   Enable debug mode (true/false)
    VERBOSE                 Enable verbose mode (true/false)

EXIT CODES:
    0   Success
    1   General error
    2   Invalid arguments
    3   Missing dependency
    4   Invalid project directory

For more information, see: $PROJECT_DIR/README.md
EOF
}

show_version() {
    echo "$SCRIPT_NAME version $SCRIPT_VERSION"
}

# ============================================================================
# Validation Functions
# ============================================================================

check_dependency() {
    local cmd="$1"
    local description="$2"
    
    if ! command -v "$cmd" >/dev/null 2>&1; then
        log_error "Required dependency not found: $cmd ($description)"
        log_error "Please install $cmd and ensure it's in your PATH"
        return 1
    fi
    
    log_debug "Dependency check passed: $cmd"
    return 0
}

validate_project_directory() {
    local dir="$1"
    
    log_debug "Validating project directory: $dir"
    
    # Check directory exists
    if [[ ! -d "$dir" ]]; then
        log_error "Project directory not found: $dir"
        log_error "Set GEN_RULES_PROJECT_DIR environment variable or use --project flag"
        return 1
    fi
    
    # Check directory is readable
    if [[ ! -r "$dir" ]]; then
        log_error "Project directory not readable: $dir"
        log_error "Check directory permissions"
        return 1
    fi
    
    # Verify Taskfile.yml exists
    if [[ ! -f "$dir/Taskfile.yml" ]]; then
        log_error "Taskfile.yml not found in project directory: $dir"
        log_error "This does not appear to be a valid ai_coding_rules project"
        return 1
    fi
    
    # Verify scripts/generate_agent_rules.py exists
    if [[ ! -f "$dir/scripts/generate_agent_rules.py" ]]; then
        log_warning "scripts/generate_agent_rules.py not found in project directory"
        log_warning "Some tasks may not work correctly"
    fi
    
    # Verify templates directory exists (v2.1+ structure)
    if [[ ! -d "$dir/templates" ]]; then
        log_warning "templates/ directory not found in project directory"
        log_warning "This may be an older version of the project structure"
    fi
    
    log_debug "Project directory validation passed"
    return 0
}

validate_current_directory() {
    local current_dir="$PWD"
    
    log_debug "Current directory: $current_dir"
    
    # Check current directory is writable
    if [[ ! -w "$current_dir" ]]; then
        log_error "Current directory is not writable: $current_dir"
        log_error "Change to a writable directory or specify DEST"
        return 1
    fi
    
    return 0
}

# ============================================================================
# Argument Parsing
# ============================================================================

parse_arguments() {
    local custom_project_dir=""
    local -a remaining_args=()
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                show_usage
                exit "$EXIT_SUCCESS"
                ;;
            -V|--version)
                show_version
                exit "$EXIT_SUCCESS"
                ;;
            -v|--verbose)
                VERBOSE="true"
                log_info "Verbose mode enabled"
                shift
                ;;
            -d|--debug)
                DEBUG="true"
                VERBOSE="true"
                log_debug "Debug mode enabled"
                shift
                ;;
            -p|--project)
                if [[ $# -lt 2 ]]; then
                    log_error "Option $1 requires an argument"
                    return "$EXIT_INVALID_ARGS"
                fi
                custom_project_dir="$2"
                shift 2
                ;;
            -*)
                log_error "Unknown option: $1"
                log_error "Use --help for usage information"
                return "$EXIT_INVALID_ARGS"
                ;;
            *)
                remaining_args+=("$1")
                shift
                ;;
        esac
    done
    
    # Export custom project dir if provided
    if [[ -n "$custom_project_dir" ]]; then
        log_debug "Using custom project directory: $custom_project_dir"
        # shellcheck disable=SC2034  # Used by caller
        PROJECT_DIR="$custom_project_dir"
    fi
    
    # Check if any task was provided
    if [[ ${#remaining_args[@]} -eq 0 ]]; then
        log_error "No task specified"
        log_error "Use --help for usage information"
        return "$EXIT_INVALID_ARGS"
    fi
    
    # Store remaining args for task execution
    # shellcheck disable=SC2034  # Used by caller
    TASK_ARGS=("${remaining_args[@]}")
    
    return 0
}

# ============================================================================
# Main Execution
# ============================================================================

execute_task() {
    local project_dir="$1"
    shift
    local -a task_args=("$@")
    
    log_info "Executing task with project directory: $project_dir"
    log_debug "Task arguments: ${task_args[*]}"
    
    # Check if user provided DEST argument
    local has_dest=false
    for arg in "${task_args[@]}"; do
        if [[ "$arg" == DEST=* ]]; then
            has_dest=true
            log_debug "DEST argument provided by user: $arg"
            break
        fi
    done
    
    # Build task command
    local -a task_cmd=(task -d "$project_dir")
    task_cmd+=("${task_args[@]}")
    
    # Add DEST if not provided
    if [[ "$has_dest" == "false" ]]; then
        task_cmd+=(DEST="${PWD}")
        log_info "Defaulting DEST to current directory: $PWD"
    fi
    
    log_debug "Full task command: ${task_cmd[*]}"
    
    # Execute task
    exec "${task_cmd[@]}"
}

main() {
    log_debug "Starting $SCRIPT_NAME v$SCRIPT_VERSION"
    log_debug "Project directory (default): $PROJECT_DIR"
    log_debug "Current working directory: $PWD"
    
    # Parse command line arguments
    local -a task_args=()
    if ! parse_arguments "$@"; then
        exit "$?"
    fi
    
    # Use custom project dir if set
    local effective_project_dir="${PROJECT_DIR}"
    
    # Validate dependencies
    if ! check_dependency "task" "Task runner (https://taskfile.dev)"; then
        exit "$EXIT_MISSING_DEPENDENCY"
    fi
    
    # Validate project directory
    if ! validate_project_directory "$effective_project_dir"; then
        exit "$EXIT_INVALID_PROJECT"
    fi
    
    # Validate current directory (for DEST default)
    if ! validate_current_directory; then
        exit "$EXIT_ERROR"
    fi
    
    log_info "All validation checks passed"
    
    # Execute task
    execute_task "$effective_project_dir" "${TASK_ARGS[@]}"
}

# Only run main if script is executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
