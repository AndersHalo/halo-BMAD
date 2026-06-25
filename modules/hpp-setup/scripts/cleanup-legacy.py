#!/usr/bin/env python3
"""
cleanup-legacy.py — Remove legacy _bmad/{module-code}/ directories after migration.

Verifies skills exist at the new .claude/skills/ location before removing anything.
Safe to run multiple times — idempotent.

Usage:
    python3 cleanup-legacy.py \
        --module <module-code> \
        --bmad-dir <path/to/_bmad> \
        --skills-dir <path/to/.claude/skills>
"""
import argparse
import os
import shutil
import sys


def main():
    parser = argparse.ArgumentParser(description="Remove legacy BMAD module directories.")
    parser.add_argument("--module", required=True, help="Module code (e.g. hpp)")
    parser.add_argument("--bmad-dir", required=True, dest="bmad_dir", help="Path to _bmad/ directory")
    parser.add_argument("--skills-dir", required=True, dest="skills_dir", help="Path to .claude/skills/ directory")
    args = parser.parse_args()

    module = args.module
    legacy_path = os.path.join(args.bmad_dir, module)

    # Nothing to remove
    if not os.path.exists(legacy_path):
        print(f"✓ No legacy directory found at {legacy_path} — nothing to clean up")
        return

    # Verify skills are present at the new location before removing legacy
    skills_dir = args.skills_dir
    if not os.path.isdir(skills_dir):
        print(f"WARNING: Skills directory not found at {skills_dir} — skipping cleanup to avoid data loss")
        return

    # Count skills in the new location that belong to this module
    new_skills = [
        d for d in os.listdir(skills_dir)
        if os.path.isdir(os.path.join(skills_dir, d)) and d.startswith(module + "-")
    ]

    if not new_skills:
        print(
            f"WARNING: No skills found under {skills_dir} matching prefix '{module}-'. "
            f"Skipping cleanup to avoid data loss. Migrate skills first."
        )
        return

    # Safe to remove
    shutil.rmtree(legacy_path)
    print(f"✓ Removed legacy directory: {legacy_path}")
    print(f"  ({len(new_skills)} skill(s) confirmed at new location: {', '.join(new_skills)})")


if __name__ == "__main__":
    main()
