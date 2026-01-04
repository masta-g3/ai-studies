#!/usr/bin/env python3
"""Render hierarchy JSON as tree view or markdown."""

import argparse
import json
from pathlib import Path


def render_tree(data: dict, show_papers: bool = False) -> str:
    """Render hierarchy as ASCII tree."""
    lines = []
    category = data["category"]
    depth = data.get("depth", 1)

    lines.append(f"{category} (depth={depth})")
    lines.append("=" * 60)

    subcategories = data.get("subcategories", [])
    for i, subcat in enumerate(subcategories):
        is_last_subcat = i == len(subcategories) - 1
        prefix = "└── " if is_last_subcat else "├── "
        lines.append(f"{prefix}{subcat['name']} ({subcat['paper_count']} papers)")

        if subcat.get("description"):
            child_prefix = "    " if is_last_subcat else "│   "
            lines.append(f"{child_prefix}  {subcat['description']}")

        children = subcat.get("children", [])
        for j, child in enumerate(children):
            is_last_child = j == len(children) - 1
            child_prefix = "    " if is_last_subcat else "│   "
            child_branch = "└── " if is_last_child else "├── "
            lines.append(f"{child_prefix}{child_branch}{child['name']} ({child['paper_count']} papers)")

            if show_papers:
                paper_prefix = child_prefix + ("    " if is_last_child else "│   ")
                for paper in child.get("papers", [])[:5]:
                    lines.append(f"{paper_prefix}• {paper['arxiv_code']}: {paper['title'][:50]}...")
                if len(child.get("papers", [])) > 5:
                    lines.append(f"{paper_prefix}  ... and {len(child['papers']) - 5} more")

        if show_papers and not children:
            paper_prefix = "    " if is_last_subcat else "│   "
            for paper in subcat.get("papers", [])[:5]:
                lines.append(f"{paper_prefix}  • {paper['arxiv_code']}: {paper['title'][:50]}...")
            if len(subcat.get("papers", [])) > 5:
                lines.append(f"{paper_prefix}    ... and {len(subcat['papers']) - 5} more")

    unassigned = data.get("unassigned", [])
    if unassigned:
        lines.append(f"\nUnassigned: {len(unassigned)} papers")

    return "\n".join(lines)


def render_markdown(data: dict, show_papers: bool = False) -> str:
    """Render hierarchy as markdown."""
    lines = []
    category = data["category"]
    depth = data.get("depth", 1)

    lines.append(f"# {category}")
    lines.append(f"\n*Discovered: {data.get('discovered_at', 'unknown')} | Depth: {depth}*\n")

    for subcat in data.get("subcategories", []):
        lines.append(f"## {subcat['name']} ({subcat['paper_count']} papers)")
        if subcat.get("description"):
            lines.append(f"\n*{subcat['description']}*\n")

        children = subcat.get("children", [])
        if children:
            for child in children:
                lines.append(f"### {child['name']} ({child['paper_count']} papers)")
                if show_papers:
                    lines.append("")
                    for paper in child.get("papers", []):
                        lines.append(f"- **{paper['arxiv_code']}**: {paper['title']}")
                    lines.append("")
        elif show_papers:
            lines.append("")
            for paper in subcat.get("papers", []):
                lines.append(f"- **{paper['arxiv_code']}**: {paper['title']}")
            lines.append("")

    unassigned = data.get("unassigned", [])
    if unassigned:
        lines.append(f"\n## Unassigned ({len(unassigned)} papers)\n")
        if show_papers:
            for paper in unassigned:
                lines.append(f"- **{paper['arxiv_code']}**: {paper['title']}")

    return "\n".join(lines)


def render_json_summary(data: dict) -> str:
    """Render hierarchy as compact JSON summary (no papers, just structure)."""
    summary = {
        "category": data["category"],
        "depth": data.get("depth", 1),
        "subcategories": []
    }

    for subcat in data.get("subcategories", []):
        subcat_summary = {
            "name": subcat["name"],
            "paper_count": subcat["paper_count"],
        }
        if subcat.get("children"):
            subcat_summary["children"] = [
                {"name": c["name"], "paper_count": c["paper_count"]}
                for c in subcat["children"]
            ]
        summary["subcategories"].append(subcat_summary)

    summary["unassigned_count"] = len(data.get("unassigned", []))
    return json.dumps(summary, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Render hierarchy JSON as tree or markdown")
    parser.add_argument("input", help="Path to hierarchy JSON file")
    parser.add_argument("--format", choices=["tree", "markdown", "summary"], default="tree", help="Output format")
    parser.add_argument("--papers", action="store_true", help="Include paper titles in output")
    parser.add_argument("--output", type=str, help="Output file (default: stdout)")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    if args.format == "tree":
        output = render_tree(data, show_papers=args.papers)
    elif args.format == "markdown":
        output = render_markdown(data, show_papers=args.papers)
    else:
        output = render_json_summary(data)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
