#!/usr/bin/env python3
"""
Script to fix LastUpdated dates with today's actual date
"""

import re
from datetime import datetime
from pathlib import Path

def fix_date_in_file(file_path: Path):
    """Fix the LastUpdated date in a single file"""
    content = file_path.read_text(encoding='utf-8')
    
    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Replace the hardcoded date with today's date
    updated_content = re.sub(
        r'\*\*LastUpdated:\*\* 2025-01-15',
        f'**LastUpdated:** {today}',
        content
    )
    
    # Also handle any other incorrect dates that might exist
    updated_content = re.sub(
        r'\*\*LastUpdated:\*\* \d{4}-\d{2}-\d{2}',
        f'**LastUpdated:** {today}',
        updated_content
    )
    
    if updated_content != content:
        file_path.write_text(updated_content, encoding='utf-8')
        print(f"Updated date in {file_path.name} to {today}")
        return True
    return False

def main():
    # Update all *.md files except documentation files
    skip_files = {'README.md', 'CHANGELOG.md', 'CONTRIBUTING.md'}
    
    updated_count = 0
    for md_file in Path('.').glob('*.md'):
        if md_file.name not in skip_files:
            if fix_date_in_file(md_file):
                updated_count += 1
    
    print(f"\nFixed dates in {updated_count} files")
    print(f"Today's date: {datetime.now().strftime('%Y-%m-%d')}")

if __name__ == '__main__':
    main()
