# Token Budget Update Script

## Quick Reference

### Purpose
Automatically update token budgets in AI coding rule files to ensure accuracy.

### Location
`scripts/token_validator.py`

### Quick Start
```bash
# Preview what would be updated
python scripts/token_validator.py --dry-run

# Show detailed analysis
python scripts/token_validator.py --detailed

# Apply updates
python scripts/token_validator.py
```

### Common Commands
```bash
# Dry run with details
python scripts/token_validator.py -n --detailed

# Update with custom threshold (20%)
python scripts/token_validator.py --threshold 20

# Verbose output
python scripts/token_validator.py -v --detailed

# Update specific directory
python scripts/token_validator.py -d rules/
```

### How It Works
1. **Estimates tokens** using word count × 1.3 multiplier
2. **Compares** estimate against declared TokenBudget
3. **Updates** if difference exceeds threshold (default ±5%)
4. **Rounds** to nearest 50 for clean numbers
5. **Updates** TokenBudget, LastUpdated, Version fields

### Integration Workflow
```bash
# After making content changes
python scripts/token_validator.py --dry-run --detailed

# Review and apply
python scripts/token_validator.py

# Validate
python scripts/schema_validator.py rules/

# Regenerate
task generate:tokens
```

### Options
- `--directory, -d`: Target directory (default: templates/)
- `--threshold, -t`: Update threshold % (default: 5.0)
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
$ python scripts/token_validator.py --dry-run

TOKEN BUDGET UPDATE SUMMARY
Total files analyzed: 72
  [OK]      Within ±5.0%: 70
  [UPDATE]  Need updating: 2
  
[DRY RUN] Would update 2 files
```

#### Detailed Analysis
```bash
$ python scripts/token_validator.py --detailed

File                           Current    Estimated  Diff %     Suggested  Status
002-rule-governance.md         ~14300     9646       -32.5%     ~9650      UPDATE
101a-streamlit-vis.md          ~6100      3625       -40.6%     ~3600      UPDATE
```

#### Apply Updates
```bash
$ python scripts/token_validator.py

TOKEN BUDGET UPDATE SUMMARY
Total files analyzed: 72
  [OK]      Within ±5.0%: 72
  [UPDATE]  Need updating: 0
  
Successfully updated 0 files
```

### Notes
- Always run with `--dry-run` first to preview changes
- Token estimates are based on word count, not actual tokenization
- Threshold of ±5% ensures high accuracy for token budgets
- Script preserves file structure and formatting
- Updates are safe and reversible via git

### Related Scripts
- `schema_validator.py`: Validate rule structure and compliance
- `index_generator.py`: Generate RULES_INDEX.md catalog
- `rule_deployer.py`: Deploy rules to projects

### Troubleshooting

**Issue**: "No files found"
- Check directory path with `-d` option

**Issue**: "Permission denied"
- Ensure script is executable: `chmod +x scripts/token_validator.py`

**Issue**: "Unexpected token count"
- Check if file has unusual formatting
- Review with `--detailed` flag

### Version
Script version: 1.0.0
Compatible with: Rule governance v4.0
Last updated: 2025-11-07
