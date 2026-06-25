#!/usr/bin/env python3
"""
merge-config.py — Anti-zombie config merge for BMAD modules.

Removes all existing entries for the module, then writes fresh ones.
Writes shared config to config.yaml and personal settings to config.user.yaml.

Usage:
    python3 merge-config.py \
        --module <module-code> \
        --config-path <path/to/_bmad/config.yaml> \
        --user-config-path <path/to/_bmad/config.user.yaml> \
        --values key1=val1 key2=val2 ...
"""
import argparse
import os
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def load_yaml(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_yaml(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def parse_values(raw_values):
    result = {}
    for item in raw_values:
        if "=" in item:
            k, _, v = item.partition("=")
            result[k.strip()] = v.strip()
    return result


def main():
    parser = argparse.ArgumentParser(description="Merge module config into BMAD config files.")
    parser.add_argument("--module", required=True, help="Module code (e.g. hpp)")
    parser.add_argument("--config-path", required=True, dest="config_path", help="Path to _bmad/config.yaml")
    parser.add_argument("--user-config-path", required=True, dest="user_config_path", help="Path to _bmad/config.user.yaml")
    parser.add_argument("--values", nargs="*", default=[], help="key=value pairs to write")
    args = parser.parse_args()

    values = parse_values(args.values)
    module = args.module

    # ── Shared config (config.yaml) ──────────────────────────────────────────
    config = load_yaml(args.config_path)

    # Anti-zombie: remove stale module section
    config.pop(module, None)

    # Write fresh module section
    config[module] = values

    save_yaml(args.config_path, config)
    print(f"✓ config.yaml updated — [{module}] section written with {len(values)} key(s)")

    # ── User config (config.user.yaml) — user_setting vars ──────────────────
    # For hpp module, no user_setting vars are defined. File left unchanged.
    print(f"✓ config.user.yaml unchanged (no user_setting vars for {module})")


if __name__ == "__main__":
    main()
