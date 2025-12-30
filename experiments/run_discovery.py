#!/usr/bin/env python3
"""CLI for running hierarchy discovery."""

import argparse
import json
from pathlib import Path

from src.discover import run_discovery

DATA_DIR = Path("data")


def main():
    parser = argparse.ArgumentParser(description="Discover paper hierarchy for a category")
    parser.add_argument("category", help="Category code (e.g., reasoning_models)")
    parser.add_argument("--limit", type=int, default=500, help="Max papers to fetch")
    parser.add_argument("--batch-size", type=int, default=50, help="Papers per LLM batch")
    parser.add_argument("--depth", type=int, default=1, choices=[1, 2], help="Hierarchy depth (1=subcategories, 2=sub-subcategories)")
    parser.add_argument("--output", type=str, help="Output file path")
    args = parser.parse_args()

    result = run_discovery(
        category=args.category,
        limit=args.limit,
        batch_size=args.batch_size,
        depth=args.depth,
    )

    DATA_DIR.mkdir(exist_ok=True)
    output_path = Path(args.output) if args.output else DATA_DIR / f"hierarchy_{args.category}.json"

    with open(output_path, "w") as f:
        json.dump(result.to_dict(), f, indent=2)

    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
