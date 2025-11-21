#!/usr/bin/env bash
# Script: gen-rules.sh
# Description: System-wide wrapper for AI coding rules generation from anywhere (Task-free alternative)
# Author: AI Coding Rules Project
# Version: 3.0
# Last Updated: 2025-11-21
# Location: project root (gen-rules.sh)
# Usage: gen-rules.sh [OPTIONS] <command> [args]

set -euo pipefail

# ============================================================================
# Constants and Configuration
# ============================================================================

readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly SCRIPT_VERSION="3.0"

# Allow PROJECT_DIR override via environment variable
# Script is now in project root, so default to current script directory
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIR="${GEN_RULES_PROJECT_DIR:-${SCRIPT_DIR}}"

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
Usage: $SCRIPT_NAME [OPTIONS] <command> [args]

Generate AI coding rules for various IDEs/agents from anywhere on your system.
Pure shell/Python implementation - no Task dependency required.

OPTIONS:
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output
    -d, --debug         Enable debug mode
    -V, --version       Show version information
    -p, --project DIR   Override project directory (default: \$GEN_RULES_PROJECT_DIR or script directory)

GENERATION COMMANDS:
    generate cursor [DEST]      Generate Cursor .mdc files
    generate copilot [DEST]     Generate GitHub Copilot instructions
    generate cline [DEST]       Generate Cline rules
    generate universal [DEST]   Generate Universal rules (IDE-agnostic, recommended)
    generate all [DEST]         Generate all IDE-specific rules

    Options for generate:
      --dry-run                 Preview changes without writing files
      --check                   Check if outputs are current/valid

DEPLOYMENT COMMANDS:
    deploy cursor [DEST]        Deploy Cursor rules to target (.cursor/rules/)
    deploy copilot [DEST]       Deploy Copilot rules to target (.github/copilot/instructions/)
    deploy cline [DEST]         Deploy Cline rules to target (.clinerules/)
    deploy universal [DEST]     Deploy Universal rules to target (rules/)

VALIDATION COMMANDS:
    validate                    Run all validation checks

STATUS COMMANDS:
    status                      Show project status

GENERATION EXAMPLES:
    # Generate Universal rules (works with any IDE/LLM) - recommended
    $SCRIPT_NAME generate universal

    # Generate Cursor rules into current directory
    $SCRIPT_NAME generate cursor

    # Generate to specific directory
    $SCRIPT_NAME generate universal ~/my-project

    # Generate with verbose output
    $SCRIPT_NAME --verbose generate universal

    # Dry run preview (no files written)
    $SCRIPT_NAME generate cursor --dry-run

    # Check if rules need regeneration
    $SCRIPT_NAME generate universal --check

    # Generate all formats
    $SCRIPT_NAME generate all

DEPLOYMENT EXAMPLES:
    # Deploy Universal rules to current directory
    $SCRIPT_NAME deploy universal
    
    # Deploy to specific project
    $SCRIPT_NAME deploy universal ~/my-project
    
    # Deploy Cursor rules with verbose output
    $SCRIPT_NAME --verbose deploy cursor ~/my-project

PROJECT DIRECTORY EXAMPLES:
    # Override project directory
    $SCRIPT_NAME --project ~/my-ai-rules generate universal

    # Use environment variable for project directory
    export GEN_RULES_PROJECT_DIR=~/my-ai-rules
    $SCRIPT_NAME generate universal

ENVIRONMENT VARIABLES:
    GEN_RULES_PROJECT_DIR   Override default project directory
    DEBUG                   Enable debug mode (true/false)
    VERBOSE                 Enable verbose mode (true/false)

EXIT CODES:
    0   Success
    1   General error
    2   Invalid arguments
    3   Missing dependency (python3)
    4   Invalid project directory

DEPENDENCIES:
    - python3 (no Task required - pure shell/Python implementation)

For more information, see: $PROJECT_DIR/README.md
EOF
}

show_version() {
    echo "$SCRIPT_NAME version $SCRIPT_VERSION"
    echo "Pure shell/Python implementation (Task-free)"
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
    
    # Verify scripts/generate_agent_rules.py exists
    if [[ ! -f "$dir/scripts/generate_agent_rules.py" ]]; then
        log_error "scripts/generate_agent_rules.py not found in project directory: $dir"
        log_error "This does not appear to be a valid ai_coding_rules project"
        return 1
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
        log_error "Change to a writable directory or specify destination"
        return 1
    fi
    
    return 0
}

# ============================================================================
# Command Execution Functions
# ============================================================================

execute_generate() {
    local agent="$1"
    shift
    local -a extra_args=()
    local destination="${PWD}"
    
    # Parse remaining arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run|--check)
                extra_args+=("$1")
                shift
                ;;
            *)
                # Treat as destination
                destination="$1"
                shift
                ;;
        esac
    done
    
    log_info "Generating $agent rules to: $destination"
    
    local -a python_cmd=(
        python3
        "${PROJECT_DIR}/scripts/generate_agent_rules.py"
        --agent "$agent"
        --source "${PROJECT_DIR}/templates"
        --destination "$destination"
    )
    
    # Add extra args (dry-run, check)
    if [[ ${#extra_args[@]} -gt 0 ]]; then
        python_cmd+=("${extra_args[@]}")
    fi
    
    log_debug "Python command: ${python_cmd[*]}"
    
    "${python_cmd[@]}"
}

execute_generate_all() {
    local destination="${1:-${PWD}}"
    
    log_info "Generating all agent formats to: $destination"
    
    local -a agents=(cursor copilot cline universal)
    local failed=false
    
    for agent in "${agents[@]}"; do
        log_info "Generating $agent rules..."
        if ! execute_generate "$agent" "$destination"; then
            log_error "Failed to generate $agent rules"
            failed=true
        fi
    done
    
    if [[ "$failed" == "true" ]]; then
        log_error "One or more agent generations failed"
        return 1
    fi
    
    log_info "Successfully generated all agent formats"
    return 0
}

execute_deploy() {
    local agent="$1"
    local destination="${2:-${PWD}}"
    
    log_info "Deploying $agent rules to: $destination"
    
    # Check if deploy_rules.py exists
    if [[ ! -f "${PROJECT_DIR}/scripts/deploy_rules.py" ]]; then
        log_error "scripts/deploy_rules.py not found"
        log_error "Deploy functionality requires deploy_rules.py script"
        return 1
    fi
    
    local -a python_cmd=(
        python3
        "${PROJECT_DIR}/scripts/deploy_rules.py"
        --agent "$agent"
        --destination "$destination"
    )
    
    log_debug "Python command: ${python_cmd[*]}"
    
    "${python_cmd[@]}"
}

execute_validate() {
    log_info "Running validation checks"
    
    # Check if validate script exists
    if [[ ! -f "${PROJECT_DIR}/scripts/validate_agent_rules.py" ]]; then
        log_error "scripts/validate_agent_rules.py not found"
        log_error "Validation functionality requires validate_agent_rules.py script"
        return 1
    fi
    
    local -a python_cmd=(
        python3
        "${PROJECT_DIR}/scripts/validate_agent_rules.py"
        --directory "${PROJECT_DIR}/templates"
    )
    
    log_debug "Python command: ${python_cmd[*]}"
    
    "${python_cmd[@]}"
}

execute_status() {
    log_info "Project Status"
    echo ""
    echo "Project Directory: $PROJECT_DIR"
    echo "Templates: ${PROJECT_DIR}/templates"
    echo "Scripts: ${PROJECT_DIR}/scripts"
    echo ""
    
    # Count templates
    if [[ -d "${PROJECT_DIR}/templates" ]]; then
        local template_count
        template_count=$(find "${PROJECT_DIR}/templates" -name "*.md" -type f | wc -l | tr -d ' ')
        echo "Template files: $template_count"
    else
        echo "Template files: N/A (directory not found)"
    fi
    
    # Check Python scripts
    echo ""
    echo "Available scripts:"
    if [[ -f "${PROJECT_DIR}/scripts/generate_agent_rules.py" ]]; then
        echo "  ✓ generate_agent_rules.py"
    else
        echo "  ✗ generate_agent_rules.py (missing)"
    fi
    
    if [[ -f "${PROJECT_DIR}/scripts/deploy_rules.py" ]]; then
        echo "  ✓ deploy_rules.py"
    else
        echo "  ✗ deploy_rules.py (missing)"
    fi
    
    if [[ -f "${PROJECT_DIR}/scripts/validate_agent_rules.py" ]]; then
        echo "  ✓ validate_agent_rules.py"
    else
        echo "  ✗ validate_agent_rules.py (missing)"
    fi
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
                export VERBOSE
                log_info "Verbose mode enabled"
                shift
                ;;
            -d|--debug)
                DEBUG="true"
                VERBOSE="true"
                export DEBUG VERBOSE
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
        PROJECT_DIR="$custom_project_dir"
        export PROJECT_DIR
    fi
    
    # Check if any command was provided
    if [[ ${#remaining_args[@]} -eq 0 ]]; then
        log_error "No command specified"
        log_error "Use --help for usage information"
        return "$EXIT_INVALID_ARGS"
    fi
    
    # Store remaining args for command execution
    COMMAND_ARGS=("${remaining_args[@]}")
    export COMMAND_ARGS
    
    return 0
}

# ============================================================================
# Command Dispatcher
# ============================================================================

dispatch_command() {
    local command="$1"
    shift
    
    case "$command" in
        generate)
            if [[ $# -eq 0 ]]; then
                log_error "Missing agent type for generate command"
                log_error "Usage: $SCRIPT_NAME generate {cursor|copilot|cline|universal|all} [destination] [--dry-run|--check]"
                return "$EXIT_INVALID_ARGS"
            fi
            
            local agent="$1"
            shift
            
            case "$agent" in
                all)
                    execute_generate_all "$@"
                    ;;
                cursor|copilot|cline|universal)
                    execute_generate "$agent" "$@"
                    ;;
                *)
                    log_error "Unknown agent type: $agent"
                    log_error "Valid agents: cursor, copilot, cline, universal, all"
                    return "$EXIT_INVALID_ARGS"
                    ;;
            esac
            ;;
            
        deploy)
            if [[ $# -eq 0 ]]; then
                log_error "Missing agent type for deploy command"
                log_error "Usage: $SCRIPT_NAME deploy {cursor|copilot|cline|universal} [destination]"
                return "$EXIT_INVALID_ARGS"
            fi
            
            local agent="$1"
            shift
            
            case "$agent" in
                cursor|copilot|cline|universal)
                    execute_deploy "$agent" "$@"
                    ;;
                *)
                    log_error "Unknown agent type: $agent"
                    log_error "Valid agents: cursor, copilot, cline, universal"
                    return "$EXIT_INVALID_ARGS"
                    ;;
            esac
            ;;
            
        validate)
            execute_validate
            ;;
            
        status)
            execute_status
            ;;
            
        *)
            log_error "Unknown command: $command"
            log_error "Valid commands: generate, deploy, validate, status"
            log_error "Use --help for more information"
            return "$EXIT_INVALID_ARGS"
            ;;
    esac
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    log_debug "Starting $SCRIPT_NAME v$SCRIPT_VERSION"
    log_debug "Project directory (default): $PROJECT_DIR"
    log_debug "Current working directory: $PWD"
    
    # Parse command line arguments
    if ! parse_arguments "$@"; then
        exit "$?"
    fi
    
    # Validate dependencies
    if ! check_dependency "python3" "Python 3 interpreter"; then
        exit "$EXIT_MISSING_DEPENDENCY"
    fi
    
    # Validate project directory
    if ! validate_project_directory "$PROJECT_DIR"; then
        exit "$EXIT_INVALID_PROJECT"
    fi
    
    # Validate current directory (for default destination)
    if ! validate_current_directory; then
        exit "$EXIT_ERROR"
    fi
    
    log_info "All validation checks passed"
    
    # Dispatch command
    dispatch_command "${COMMAND_ARGS[@]}"
}

# Only run main if script is executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
