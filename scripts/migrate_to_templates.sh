#!/usr/bin/env bash
set -euo pipefail

# Migration helper script for Option 1 structure
# This script automates the complete migration process

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting migration to Option 1 structure..."
echo ""

# Check if already migrated
if [ -d "$PROJECT_ROOT/templates" ] && [ "$(ls -A "$PROJECT_ROOT/templates"/*.md 2>/dev/null | wc -l)" -gt 0 ]; then
    echo "✓ templates/ directory already exists with files"
else
    echo "❌ templates/ directory not found or empty"
    echo "   Run Phase 1 manually first"
    exit 1
fi

# Check if discovery/ exists
if [ -d "$PROJECT_ROOT/discovery" ]; then
    echo "✓ discovery/ directory exists"
else
    echo "❌ discovery/ directory not found"
    echo "   Run Phase 1 manually first"
    exit 1
fi

# Generate all rule formats
echo ""
echo "🔨 Generating all rule formats..."
cd "$PROJECT_ROOT"

if command -v task &> /dev/null; then
    echo "   Using task automation..."
    task rule:all
else
    echo "   Using direct script invocation..."
    uv run scripts/generate_agent_rules.py --agent universal
    uv run scripts/generate_agent_rules.py --agent cursor
    uv run scripts/generate_agent_rules.py --agent copilot
    uv run scripts/generate_agent_rules.py --agent cline
fi

# Create symlinks if they don't exist
echo ""
echo "🔗 Creating compatibility symlinks..."

create_symlink() {
    local target="$1"
    local link="$2"
    
    if [ -L "$link" ]; then
        echo "   ✓ Symlink already exists: $link"
    elif [ -e "$link" ]; then
        echo "   ⚠️  Path exists but is not a symlink: $link"
        echo "      Remove it manually if you want to create a symlink"
    else
        ln -s "$target" "$link"
        echo "   ✓ Created symlink: $link -> $target"
    fi
}

create_symlink "generated/cursor/rules" ".cursor/rules"
create_symlink "generated/copilot/instructions" ".github/instructions"
create_symlink "generated/cline" ".clinerules"
create_symlink "generated/universal" "rules"

echo ""
echo "✅ Migration complete!"
echo ""
echo "📊 Structure summary:"
echo "   Templates: $(ls -1 templates/*.md 2>/dev/null | wc -l) files"
echo "   Generated universal: $(ls -1 generated/universal/*.md 2>/dev/null | wc -l) files"
echo "   Generated cursor: $(ls -1 generated/cursor/rules/*.mdc 2>/dev/null | wc -l) files"
echo "   Generated copilot: $(ls -1 generated/copilot/instructions/*.md 2>/dev/null | wc -l) files"
echo "   Generated cline: $(ls -1 generated/cline/*.md 2>/dev/null | wc -l) files"
echo ""
echo "Next steps:"
echo "  1. Review generated files in generated/ directories"
echo "  2. Test with your IDE (Cursor, Copilot, Cline)"
echo "  3. Commit changes: git add . && git commit -m 'feat: migrate to Option 1 structure'"
echo ""
echo "📖 For more information, see:"
echo "   - project-structure-plan.md"
echo "   - project-structure-recommendations.md"

