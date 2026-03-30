#!/usr/bin/env python3
"""
Timing Data Validation Script

Validates per-dimension timing data in rule review files to detect:
- Fabricated timestamps (suspiciously round durations)
- Impossible durations (sum exceeds total)
- Timestamp plausibility issues

Usage:
    python validate_timing.py reviews/rule-reviews/REVIEW_FILE.md
    python validate_timing.py reviews/rule-reviews/*.md  # Validate all
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TimingValidator:
    """Validates timing data from rule review markdown files."""
    
    def __init__(self, review_file: Path):
        self.review_file = review_file
        self.content = review_file.read_text()
        self.errors = []
        self.warnings = []
        
    def validate(self) -> Dict:
        """Run all validation checks."""
        if "Per-Dimension Timing" not in self.content:
            return {
                "file": str(self.review_file),
                "has_timing": False,
                "errors": [],
                "warnings": [],
                "status": "SKIPPED"
            }
        
        total_seconds = self._extract_total_duration()
        checkpoints = self._extract_checkpoints()
        dimensions = self._extract_dimension_timings()
        
        if total_seconds and dimensions:
            self._validate_sum_plausibility(total_seconds, dimensions)
            self._validate_round_durations(dimensions)
            self._validate_negative_durations(dimensions)
            
            if checkpoints:
                available_window = checkpoints.get("review_complete", 0) - checkpoints.get("skill_loaded", 0)
                if available_window > 0:
                    self._validate_dimension_window(available_window, dimensions)
        
        status = "FAILED" if self.errors else ("WARNING" if self.warnings else "PASSED")
        
        return {
            "file": str(self.review_file),
            "has_timing": True,
            "total_seconds": total_seconds,
            "dimension_count": len(dimensions),
            "dimension_sum": sum(d["duration"] for d in dimensions if d["duration"] > 0),
            "errors": self.errors,
            "warnings": self.warnings,
            "status": status
        }
    
    def _extract_total_duration(self) -> Optional[float]:
        """Extract total review duration in seconds."""
        match = re.search(r"\| Duration \| (\d+)m (\d+)s \((\d+\.\d+)s\)", self.content)
        return float(match.group(3)) if match else None
    
    def _extract_checkpoints(self) -> Dict[str, float]:
        """Extract checkpoint timings."""
        checkpoints = {}
        checkpoint_match = re.search(r"\| Checkpoints \| (.+?) \|", self.content)
        if checkpoint_match:
            checkpoint_str = checkpoint_match.group(1)
            for cp in checkpoint_str.split(", "):
                if ":" in cp:
                    name, duration = cp.split(":")
                    checkpoints[name.strip()] = float(duration.strip().replace("s", ""))
        return checkpoints
    
    def _extract_dimension_timings(self) -> List[Dict]:
        """Extract per-dimension timing data."""
        dimensions = []
        
        # Find the timing table after "Per-Dimension Timing" header
        lines = self.content.split('\n')
        in_timing_section = False
        
        for line in lines:
            if '### Per-Dimension Timing' in line:
                in_timing_section = True
                continue
            
            if in_timing_section:
                # Stop at next header or empty section
                if line.startswith('##') and 'Per-Dimension' not in line:
                    break
                
                # Parse table rows (skip header and separator)
                if '|' in line and 'Dimension' not in line and '---' not in line and 'Total' not in line:
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 3:
                        dim_name = parts[0]
                        duration_str = parts[1]
                        mode = parts[2]
                        
                        if 's' in duration_str:
                            try:
                                duration = float(duration_str.replace('s', '').strip())
                                dimensions.append({
                                    "dimension": dim_name,
                                    "duration": duration,
                                    "mode": mode
                                })
                            except ValueError:
                                pass
        
        return dimensions
    
    def _validate_sum_plausibility(self, total_seconds: float, dimensions: List[Dict]):
        """Validate dimension sum vs total duration."""
        sum_dimensions = sum(d["duration"] for d in dimensions if d["duration"] > 0)
        ratio = sum_dimensions / total_seconds if total_seconds > 0 else 0
        
        # Allow 20% overclaim for overhead/measurement variance
        if ratio > 1.2:
            self.errors.append(
                f"Dimension sum ({sum_dimensions:.2f}s) exceeds total duration "
                f"({total_seconds:.2f}s) by {(ratio-1)*100:.1f}% (>20% threshold)"
            )
        elif ratio > 1.0:
            self.warnings.append(
                f"Dimension sum ({sum_dimensions:.2f}s) exceeds total duration "
                f"({total_seconds:.2f}s) by {(ratio-1)*100:.1f}% (within 20% tolerance)"
            )
        elif ratio < 0.5:
            self.warnings.append(
                f"Dimension sum ({sum_dimensions:.2f}s) is only {ratio*100:.0f}% "
                f"of total duration ({total_seconds:.2f}s) - possible missing dimensions"
            )
    
    def _validate_round_durations(self, dimensions: List[Dict]):
        """Flag suspiciously round durations."""
        round_durations = []
        for d in dimensions:
            if d["duration"] >= 60 and d["duration"] % 60 == 0 and d["mode"] == "self-report":
                round_durations.append(f"{d['dimension']}: {d['duration']:.0f}s")
        
        if len(round_durations) >= 3:
            self.errors.append(
                f"Multiple suspiciously round durations (exact 60s multiples): {', '.join(round_durations)}"
            )
        elif round_durations:
            self.warnings.append(
                f"Round duration detected: {', '.join(round_durations)}"
            )
    
    def _validate_negative_durations(self, dimensions: List[Dict]):
        """Check for failed timing measurements."""
        failed = [d["dimension"] for d in dimensions if d["duration"] < 0]
        if failed:
            self.warnings.append(f"Failed timing measurements: {', '.join(failed)}")
    
    def _validate_dimension_window(self, available_window: float, dimensions: List[Dict]):
        """Validate dimensions fit within available time window."""
        for d in dimensions:
            if d["duration"] > available_window:
                self.errors.append(
                    f"{d['dimension']} duration ({d['duration']:.2f}s) exceeds "
                    f"available window ({available_window:.2f}s)"
                )


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_timing.py REVIEW_FILE.md")
        print("       python validate_timing.py reviews/rule-reviews/*.md")
        sys.exit(1)
    
    review_files = []
    for arg in sys.argv[1:]:
        path = Path(arg)
        if path.is_file():
            review_files.append(path)
        elif "*" in arg:
            # Shell expansion didn't work, try glob
            review_files.extend(Path(".").glob(arg))
    
    if not review_files:
        print(f"No review files found")
        sys.exit(1)
    
    print(f"Validating {len(review_files)} review file(s)...\n")
    
    results = []
    for review_file in review_files:
        validator = TimingValidator(review_file)
        result = validator.validate()
        results.append(result)
    
    # Print results
    passed = 0
    warned = 0
    failed = 0
    skipped = 0
    
    for result in results:
        status = result["status"]
        symbol = {
            "PASSED": "✓",
            "WARNING": "⚠",
            "FAILED": "✗",
            "SKIPPED": "-"
        }.get(status, "?")
        
        print(f"{symbol} {Path(result['file']).name} [{status}]")
        
        if result["has_timing"]:
            print(f"  Total: {result['total_seconds']:.2f}s, "
                  f"Dimensions: {result['dimension_count']}, "
                  f"Sum: {result['dimension_sum']:.2f}s")
        
        for error in result["errors"]:
            print(f"  ERROR: {error}")
        
        for warning in result["warnings"]:
            print(f"  WARN: {warning}")
        
        print()
        
        if status == "PASSED":
            passed += 1
        elif status == "WARNING":
            warned += 1
        elif status == "FAILED":
            failed += 1
        else:
            skipped += 1
    
    # Summary
    print("=" * 60)
    print(f"SUMMARY: {len(results)} files")
    print(f"  Passed: {passed}")
    print(f"  Warnings: {warned}")
    print(f"  Failed: {failed}")
    print(f"  Skipped (no timing): {skipped}")
    print("=" * 60)
    
    # Exit code
    if failed > 0:
        sys.exit(1)
    elif warned > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
