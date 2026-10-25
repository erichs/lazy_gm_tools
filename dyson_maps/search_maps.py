#!/usr/bin/env python3
"""Search the Dyson maps YAML index with structured filters."""

import argparse
import json
import os
import sys

import yaml

INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "map-index.yaml")


def load_index():
    with open(INDEX_PATH) as f:
        return yaml.safe_load(f)["maps"]


def csv_list(value):
    """Parse comma-separated CLI argument into a list."""
    return [v.strip() for v in value.split(",") if v.strip()]


def matches(entry, args):
    """Check if a map entry matches all provided filters.

    Each filter is OR within its values, AND across different filters.
    """
    if args.type:
        if entry.get("type") not in args.type:
            return False

    if args.setting:
        if entry.get("setting") not in args.setting:
            return False

    if args.scale:
        scale = entry.get("scale", "")
        if not any(scale.startswith(s) for s in args.scale):
            return False

    if args.features:
        entry_features = set(entry.get("features") or [])
        if not any(f in entry_features for f in args.features):
            return False

    if args.combat_use:
        entry_combat = set(entry.get("combat_use") or [])
        if not any(c in entry_combat for c in args.combat_use):
            return False

    if args.atmosphere:
        # Some entries have comma-separated atmosphere values from Gemini
        raw = entry.get("atmosphere", "")
        entry_atmos = {a.strip() for a in raw.split(",")} if isinstance(raw, str) else {raw}
        if not any(a in entry_atmos for a in args.atmosphere):
            return False

    if args.layout:
        if entry.get("layout") not in args.layout:
            return False

    if args.min_rooms is not None:
        if (entry.get("rooms") or 0) < args.min_rooms:
            return False

    if args.min_chokepoints is not None:
        if (entry.get("chokepoints") or 0) < args.min_chokepoints:
            return False

    if args.gridded is not None:
        if entry.get("gridded") != args.gridded:
            return False

    if args.search:
        text = ((entry.get("description") or "") + " " + (entry.get("name") or "")).lower()
        if args.search.lower() not in text:
            return False

    return True


def build_parser():
    parser = argparse.ArgumentParser(description="Search the Dyson maps YAML index.")
    parser.add_argument("--type", type=csv_list, default=None, help="Map types (comma-separated)")
    parser.add_argument("--setting", type=csv_list, default=None, help="Settings: indoor,outdoor,underground,mixed")
    parser.add_argument("--scale", type=csv_list, default=None, help="Scale: small,medium,large")
    parser.add_argument("--features", type=csv_list, default=None, help="Features (comma-separated, OR match)")
    parser.add_argument("--combat-use", type=csv_list, default=None, dest="combat_use", help="Combat uses (comma-separated)")
    parser.add_argument("--atmosphere", type=csv_list, default=None, help="Atmosphere (comma-separated)")
    parser.add_argument("--layout", type=csv_list, default=None, help="Layout type (comma-separated)")
    parser.add_argument("--min-rooms", type=int, default=None, dest="min_rooms", help="Minimum room count")
    parser.add_argument("--min-chokepoints", type=int, default=None, dest="min_chokepoints", help="Minimum chokepoints")
    parser.add_argument("--gridded", action="store_true", default=None, help="Only gridded maps")
    parser.add_argument("--no-gridded", action="store_false", dest="gridded", help="Only non-gridded maps")
    parser.add_argument("--search", type=str, default=None, help="Substring search in name and description")
    parser.add_argument("--limit", type=int, default=None, help="Max results to return")
    parser.add_argument("--format", choices=["json", "yaml", "names"], default="json", help="Output format")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    maps = load_index()
    results = {}

    for key, entry in maps.items():
        if matches(entry, args):
            results[key] = entry
            if args.limit and len(results) >= args.limit:
                break

    if not results:
        print("No maps matched the given filters.", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        json.dump(results, sys.stdout, indent=2)
        print()
    elif args.format == "yaml":
        yaml.dump(results, sys.stdout, default_flow_style=False, sort_keys=False)
    elif args.format == "names":
        for key in results:
            print(key)


if __name__ == "__main__":
    main()
