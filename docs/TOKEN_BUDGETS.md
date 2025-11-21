# Token Budget Update Script

## Quick Reference

### Purpose
Automatically update token budgets in AI coding rule files to ensure accuracy.

### Location
`scripts/update_token_budgets.py`

### Quick Start
```bash
# Preview what would be updated
python scripts/update_token_budgets.py --dry-run

# Show detailed analysis
python scripts/update_token_budgets.py --detailed

# Apply updates
python scripts/update_token_budgets.py
```

### Common Commands
```bash
# Dry run with details
python scripts/update_token_budgets.py -n --detailed

# Update with custom threshold (20%)
python scripts/update_token_budgets.py --threshold 20

# Verbose output
python scripts/update_token_budgets.py -v --detailed

# Update specific directory
python scripts/update_token_budgets.py -d rules/
```

### How It Works
1. **Estimates tokens** using word count × 1.3 multiplier
2. **Compares** estimate against declared TokenBudget
3. **Updates** if difference exceeds threshold (default ±15%)
4. **Rounds** to nearest 50 for clean numbers
5. **Updates** TokenBudget, LastUpdated, Version fields

### Integration Workflow
```bash
# After making content changes
python scripts/update_token_budgets.py --dry-run --detailed

# Review and apply
python scripts/update_token_budgets.py

# Validate
python scripts/validate_agent_rules.py

# Regenerate
task generate:tokens
```

### Options
- `--directory, -d`: Target directory (default: templates/)
- `--threshold, -t`: Update threshold % (default: 15.0)
- `--dry-run, -n`: Preview without modifying
- `--detailed`: Show analysis for all files
- `--verbose, -v`: Show verbose output
- `--help, -h`: Show help message

### Status Codes
- `OK`: Within threshold
- `UPDATE`: Needs updating
- `MISSING`: No budget declared
- `ERROR`: Read/write error

### Exit Codes
- `0`: Success
- `1`: Errors encountered

### Examples

#### Preview Changes
```bash
$ python scripts/update_token_budgets.py --dry-run

TOKEN BUDGET UPDATE SUMMARY
Total files analyzed: 72
  [OK]      Within ±15.0%: 70
  [UPDATE]  Need updating: 2
  
[DRY RUN] Would update 2 files
```

#### Detailed Analysis
```bash
$ python scripts/update_token_budgets.py --detailed

File                           Current    Estimated  Diff %     Suggested  Status
002-rule-governance.md         ~14300     9646       -32.5%     ~9650      UPDATE
101a-streamlit-vis.md          ~6100      3625       -40.6%     ~3600      UPDATE
```

#### Apply Updates
```bash
$ python scripts/update_token_budgets.py

TOKEN BUDGET UPDATE SUMMARY
Total files analyzed: 72
  [OK]      Within ±15.0%: 72
  [UPDATE]  Need updating: 0
  
Successfully updated 0 files
```

### Notes
- Always run with `--dry-run` first to preview changes
- Token estimates are based on word count, not actual tokenization
- Threshold of ±15% ensures high accuracy for token budgets
- Script preserves file structure and formatting
- Updates are safe and reversible via git

### Related Scripts
- `validate_agent_rules.py`: Validate rule compliance
- `remove_emojis.py`: Remove emojis from files
- `generate_rules.py`: Generate rules for deployment

### Troubleshooting

**Issue**: "No files found"
- Check directory path with `-d` option

**Issue**: "Permission denied"
- Ensure script is executable: `chmod +x scripts/update_token_budgets.py`

**Issue**: "Unexpected token count"
- Check if file has unusual formatting
- Review with `--detailed` flag

### Version
Script version: 1.0.0
Compatible with: Rule governance v4.0
Last updated: 2025-11-07
