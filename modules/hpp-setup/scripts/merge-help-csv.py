#!/usr/bin/env python3
"""
merge-help-csv.py — Anti-zombie module-help.csv merge for BMAD modules.

Removes all rows for the module from the target CSV, then appends fresh rows
from the module's source CSV.

Usage:
    python3 merge-help-csv.py \
        --module <module-code> \
        --source <path/to/assets/module-help.csv> \
        --target <path/to/_bmad/module-help.csv>
"""
import argparse
import csv
import os
import sys


EXPECTED_COLUMNS = [
    "module", "skill", "display-name", "menu-code", "description",
    "action", "args", "phase", "preceded-by", "followed-by",
    "required", "output-location", "outputs"
]


def read_csv(path):
    if not os.path.exists(path):
        return [], []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return rows, fieldnames


def write_csv(path, fieldnames, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Merge module-help.csv into BMAD target CSV.")
    parser.add_argument("--module", required=True, help="Module code (e.g. hpp)")
    parser.add_argument("--source", required=True, help="Path to module's assets/module-help.csv")
    parser.add_argument("--target", required=True, help="Path to _bmad/module-help.csv")
    args = parser.parse_args()

    module = args.module

    # Read source rows
    source_rows, _ = read_csv(args.source)
    if not source_rows:
        print(f"ERROR: Source CSV not found or empty: {args.source}", file=sys.stderr)
        sys.exit(1)

    # Read target rows
    target_rows, target_fieldnames = read_csv(args.target)

    # Determine fieldnames: use EXPECTED_COLUMNS; fall back to target's existing columns
    fieldnames = target_fieldnames if target_fieldnames else EXPECTED_COLUMNS

    # Anti-zombie: remove all rows for this module
    kept_rows = [r for r in target_rows if r.get("module", "").strip() != module]
    removed = len(target_rows) - len(kept_rows)

    # Append fresh source rows
    merged = kept_rows + source_rows

    write_csv(args.target, fieldnames, merged)

    print(f"✓ module-help.csv updated — removed {removed} stale row(s), added {len(source_rows)} row(s) for [{module}]")


if __name__ == "__main__":
    main()
