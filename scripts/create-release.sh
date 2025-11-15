#!/usr/bin/env bash
# Script: create-release.sh
# Description: Automated release creation following git workflow best practices
# Usage: ./create-release.sh

set -euo pipefail
IFS=$'\n\t'

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}✓${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $*" >&2
}

log_error() {
    echo -e "${RED}✗${NC} $*" >&2
}

# Validation functions
validate_branch_name() {
    local branch_name="$1"
    
    # Check if branch name matches convention: prefix/description
    if ! echo "$branch_name" | grep -qE "^(feature|fix|docs|refactor|chore)/[a-z0-9-]+$"; then
        log_error "Invalid branch name format: $branch_name"
        log_error "Must match: (feature|fix|docs|refactor|chore)/description-in-kebab-case"
        log_error "Examples:"
        log_error "  - feature/add-snowflake-rule"
        log_error "  - fix/changelog-validation"
        log_error "  - chore/update-dependencies"
        return 1
    fi
    
    return 0
}

validate_tag_name() {
    local tag_name="$1"
    
    # Check if tag follows semantic versioning: vX.Y.Z
    if ! echo "$tag_name" | grep -qE "^v[0-9]+\.[0-9]+\.[0-9]+$"; then
        log_error "Invalid tag format: $tag_name"
        log_error "Must follow semantic versioning: vX.Y.Z (e.g., v2.4.0, v1.0.1)"
        return 1
    fi
    
    return 0
}

validate_commit_message() {
    local commit_msg="$1"
    
    # Check basic length (at least 10 characters)
    if [[ ${#commit_msg} -lt 10 ]]; then
        log_error "Commit message too short (minimum 10 characters)"
        return 1
    fi
    
    # Check if follows Conventional Commits pattern (type: description or type(scope): description)
    if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|chore|refactor|perf|test|build|ci|style)(\([a-z-]+\))?:" ; then
        log_warning "Commit message doesn't follow Conventional Commits format"
        log_warning "Recommended format: type(scope): description"
        log_warning "Example: feat(rules): add git workflow management"
        log_warning ""
        read -r -p "Continue anyway? (y/N): " confirm
        if [[ "$confirm" != [yY] ]]; then
            return 1
        fi
    fi
    
    return 0
}

check_git_state() {
    log_info "Checking git repository state..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository"
        exit 1
    fi
    
    # Check if we're on main branch
    local current_branch
    current_branch="$(git branch --show-current)"
    
    if [[ "$current_branch" != "main" ]]; then
        log_error "Must start on 'main' branch (currently on: $current_branch)"
        log_error "Run: git checkout main"
        exit 1
    fi
    
    log_success "Git state validated (on main branch)"
}

check_staged_files() {
    log_info "Checking for staged files..."
    
    local staged_count
    staged_count=$(git diff --cached --name-only | wc -l | tr -d ' ')
    
    if [[ "$staged_count" -eq 0 ]]; then
        log_error "No files staged for commit"
        log_error "Please stage your changes first:"
        log_error "  git add <files>"
        log_error "  or"
        log_error "  git add ."
        exit 1
    fi
    
    log_success "Found $staged_count staged file(s)"
    log_info "Staged files:"
    git diff --cached --name-only | sed 's/^/  - /'
    echo ""
}

prompt_branch_name() {
    local branch_name
    
    log_info "Enter branch name following convention: (feature|fix|docs|refactor|chore)/description"
    echo "Examples:" >&2
    echo "  - feature/add-semantic-views" >&2
    echo "  - fix/changelog-validation" >&2
    echo "  - chore/update-dependencies" >&2
    echo "" >&2
    
    while true; do
        read -r -p "Branch name: " branch_name
        
        if [[ -z "$branch_name" ]]; then
            log_error "Branch name cannot be empty"
            continue
        fi
        
        if validate_branch_name "$branch_name"; then
            log_success "Branch name validated: $branch_name"
            # Return the branch name via stdout without any formatting
            printf "%s" "$branch_name"
            return 0
        fi
    done
}

prompt_commit_message() {
    local commit_msg
    
    log_info "Enter commit message (Conventional Commits format recommended)"
    echo "Format: type(scope): description" >&2
    echo "Example: feat(rules): enhance Snowflake Semantic Views documentation" >&2
    echo "" >&2
    
    while true; do
        read -r -p "Commit message: " commit_msg
        
        if [[ -z "$commit_msg" ]]; then
            log_error "Commit message cannot be empty"
            continue
        fi
        
        if validate_commit_message "$commit_msg"; then
            log_success "Commit message accepted"
            # Return the commit message via stdout without any formatting
            printf "%s" "$commit_msg"
            return 0
        fi
    done
}

prompt_tag_name() {
    local tag_name
    
    log_info "Enter git tag following semantic versioning: vX.Y.Z"
    echo "Examples: v2.4.0, v1.0.1, v3.2.5" >&2
    echo "" >&2
    
    # Show recent tags for reference
    if git tag --list | head -n 5 | grep -q .; then
        log_info "Recent tags:"
        git tag --list --sort=-version:refname | head -n 5 | sed 's/^/  - /' >&2
        echo "" >&2
    fi
    
    while true; do
        read -r -p "Tag name: " tag_name
        
        if [[ -z "$tag_name" ]]; then
            log_error "Tag name cannot be empty"
            continue
        fi
        
        if validate_tag_name "$tag_name"; then
            # Check if tag already exists
            if git rev-parse "$tag_name" >/dev/null 2>&1; then
                log_error "Tag '$tag_name' already exists"
                log_warning "To recreate an existing tag, delete it first:"
                log_warning "  git tag -d $tag_name"
                log_warning "  git push origin :refs/tags/$tag_name"
                continue
            fi
            
            log_success "Tag name validated: $tag_name"
            # Return the tag name via stdout without any formatting
            printf "%s" "$tag_name"
            return 0
        fi
    done
}

confirm_operation() {
    local branch_name="$1"
    local commit_msg="$2"
    local tag_name="$3"
    
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "                    RELEASE SUMMARY"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Branch:         $branch_name"
    echo "Commit Message: $commit_msg"
    echo "Tag:            $tag_name"
    echo ""
    echo "Operations to perform:"
    echo "  1. Create and checkout branch: $branch_name"
    echo "  2. Commit staged files with message"
    echo "  3. Checkout main branch"
    echo "  4. Merge $branch_name into main"
    echo "  5. Create tag: $tag_name"
    echo "  6. Push main and tags to origin"
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo ""
    
    read -r -p "Proceed with release? (y/N): " confirm
    if [[ "$confirm" != [yY] ]]; then
        log_warning "Release cancelled by user"
        exit 0
    fi
}

create_release() {
    local branch_name="$1"
    local commit_msg="$2"
    local tag_name="$3"
    
    log_info "Starting release process..."
    echo ""
    
    # Step 1: Create and checkout branch
    log_info "Step 1/6: Creating and checking out branch: $branch_name"
    if git checkout -b "$branch_name"; then
        log_success "Branch created and checked out: $branch_name"
    else
        log_error "Failed to create branch: $branch_name"
        exit 1
    fi
    echo ""
    
    # Step 2: Commit staged files
    log_info "Step 2/6: Committing staged files"
    if git commit -m "$commit_msg"; then
        log_success "Changes committed successfully"
    else
        log_error "Failed to commit changes"
        log_error "Cleaning up: deleting branch $branch_name"
        git checkout main
        git branch -D "$branch_name"
        exit 1
    fi
    echo ""
    
    # Step 3: Checkout main branch
    log_info "Step 3/6: Checking out main branch"
    if git checkout main; then
        log_success "Switched to main branch"
    else
        log_error "Failed to checkout main branch"
        exit 1
    fi
    echo ""
    
    # Step 4: Merge feature branch
    log_info "Step 4/6: Merging $branch_name into main"
    if git merge "$branch_name"; then
        log_success "Branch merged successfully"
    else
        log_error "Failed to merge branch: $branch_name"
        log_error "Resolve conflicts manually and run:"
        log_error "  git merge --continue"
        log_error "  git tag -a $tag_name -m \"$commit_msg\""
        log_error "  git push origin main --tags"
        exit 1
    fi
    echo ""
    
    # Step 5: Create annotated tag
    log_info "Step 5/6: Creating annotated tag: $tag_name"
    if git tag -a "$tag_name" -m "$commit_msg"; then
        log_success "Tag created: $tag_name"
    else
        log_error "Failed to create tag: $tag_name"
        exit 1
    fi
    echo ""
    
    # Step 6: Push main and tags
    log_info "Step 6/6: Pushing main branch and tags to origin"
    if git push origin main --tags; then
        log_success "Changes and tags pushed to origin"
    else
        log_error "Failed to push changes to origin"
        log_error "You may need to push manually:"
        log_error "  git push origin main --tags"
        exit 1
    fi
    echo ""
    
    # Final success message
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "               RELEASE COMPLETED SUCCESSFULLY"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Branch:  $branch_name"
    echo "Tag:     $tag_name"
    echo "Status:  Pushed to origin"
    echo ""
    log_success "Release $tag_name created successfully!"
    echo ""
    
    # Optional cleanup
    read -r -p "Delete local branch $branch_name? (y/N): " cleanup
    if [[ "$cleanup" == [yY] ]]; then
        git branch -d "$branch_name"
        log_success "Branch $branch_name deleted"
    else
        log_info "Branch $branch_name retained locally"
    fi
}

# Main execution
main() {
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "              GIT RELEASE AUTOMATION SCRIPT"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    
    cd "$PROJECT_ROOT" || exit 1
    
    # Pre-flight checks
    check_git_state
    check_staged_files
    echo ""
    
    # Gather user inputs
    local branch_name commit_msg tag_name
    branch_name=$(prompt_branch_name)
    echo ""
    commit_msg=$(prompt_commit_message)
    echo ""
    tag_name=$(prompt_tag_name)
    
    # Confirm before executing
    confirm_operation "$branch_name" "$commit_msg" "$tag_name"
    
    # Execute release
    create_release "$branch_name" "$commit_msg" "$tag_name"
}

# Execute main function
main "$@"

