"""CLI for running paper selection experiment."""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from sample import sample_papers, get_sample_distribution, PaperSample
from selector import select_papers, run_multi_selection, DEFAULT_MODEL


def model_to_id(model: str, reasoning_effort: str | None = None) -> str:
    """Convert model string to filesystem-safe ID."""
    # Remove provider prefix (e.g., "gemini/" -> "")
    name = model.split("/")[-1] if "/" in model else model
    # Replace unsafe chars with hyphens
    base_id = re.sub(r"[^a-zA-Z0-9-]", "-", name).strip("-")
    if reasoning_effort:
        return f"{base_id}-{reasoning_effort}"
    return base_id


def save_json(data: dict | list, path: Path):
    """Save data as formatted JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_pool(path: Path) -> list[PaperSample]:
    """Load paper pool from JSON."""
    with open(path) as f:
        data = json.load(f)
    return [
        PaperSample(
            arxiv_code=p["arxiv_code"],
            title=p["title"],
            abstract=p["abstract"],
            published=datetime.fromisoformat(p["published"]),
            categories=p["categories"],
        )
        for p in data
    ]


def main():
    parser = argparse.ArgumentParser(description="Run paper selection experiment")
    parser.add_argument("--sample", action="store_true", help="Sample papers (Phase 1)")
    parser.add_argument("--select", action="store_true", help="Run selection (Phase 2)")
    parser.add_argument("--n", type=int, default=200, help="Papers to sample")
    parser.add_argument("--x", type=int, default=5, help="Papers to select per run")
    parser.add_argument("--z", type=int, default=30, help="Number of multi-run iterations")
    parser.add_argument("--recency-days", type=int, default=60)
    parser.add_argument("--categories", nargs="+", help="Filter to specific category codes")
    parser.add_argument("--category-groups", nargs="+", help="Filter to specific category groups")
    parser.add_argument(
        "--stratify-by",
        choices=["category", "group"],
        default="group",
        help="How to distribute samples across strata (default: group)",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between API calls")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="LLM model to use")
    parser.add_argument(
        "--reasoning-effort",
        type=str,
        choices=["minimal", "low", "medium", "high"],
        default="medium",
        help="Reasoning/thinking effort level (default: medium)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data",
    )

    args = parser.parse_args()

    if args.sample:
        print(f"Sampling {args.n} papers (last {args.recency_days} days, stratify by {args.stratify_by})...")

        papers = sample_papers(
            n=args.n,
            recency_days=args.recency_days,
            categories=args.categories,
            category_groups=args.category_groups,
            stratify_by=args.stratify_by,
            seed=args.seed,
        )

        if not papers:
            print("No papers found matching criteria.")
            return

        pool_data = [
            {
                "arxiv_code": p.arxiv_code,
                "title": p.title,
                "abstract": p.abstract,
                "published": p.published.isoformat(),
                "categories": p.categories,
            }
            for p in papers
        ]
        save_json(pool_data, args.output_dir / "papers_pool.json")
        print(f"Saved {len(papers)} papers to {args.output_dir / 'papers_pool.json'}")

        # Show distribution by stratify level
        dist = get_sample_distribution(papers, by=args.stratify_by)
        sorted_dist = sorted(dist.items(), key=lambda x: -x[1])
        label = "groups" if args.stratify_by == "group" else "categories"
        print(f"\nTop 10 {label} (of {len(dist)} total):")
        for name, count in sorted_dist[:10]:
            print(f"  {name}: {count}")
        if len(sorted_dist) > 10:
            others = sum(c for _, c in sorted_dist[10:])
            print(f"  ... {len(sorted_dist) - 10} more: {others}")

    if args.select:
        pool_path = args.output_dir / "papers_pool.json"
        if not pool_path.exists():
            print("Error: Run --sample first to create paper pool")
            return

        papers = load_pool(pool_path)
        model_id = model_to_id(args.model, args.reasoning_effort)
        run_dir = args.output_dir / "runs" / model_id
        print(f"Loaded {len(papers)} papers from pool")
        print(f"Model: {args.model} (id: {model_id})")
        print(f"Reasoning effort: {args.reasoning_effort}")

        # Single-shot baseline
        print("\n=== Single-shot selection ===")
        single = select_papers(papers, top_k=args.x, model=args.model, reasoning_effort=args.reasoning_effort)
        single_data = {
            "timestamp": datetime.now().isoformat(),
            "model": args.model,
            "reasoning_effort": args.reasoning_effort,
            "params": {"n": len(papers), "x": args.x},
            "selections": [
                {"arxiv_code": s.arxiv_code, "reasoning": s.reasoning}
                for s in single.selections
            ],
            "usage": single.usage,
        }
        save_json(single_data, run_dir / "single_shot.json")
        print(f"Selected: {[s.arxiv_code for s in single.selections]}")

        # Multi-run
        print(f"\n=== Multi-run selection ({args.z} runs) ===")
        multi = run_multi_selection(
            papers, top_k=args.x, runs=args.z, delay=args.delay, model=args.model, reasoning_effort=args.reasoning_effort
        )
        multi_data = {
            "timestamp": datetime.now().isoformat(),
            "model": args.model,
            "reasoning_effort": args.reasoning_effort,
            "params": {"n": len(papers), "x": args.x, "z": args.z},
            "runs": [
                {
                    "run_id": i + 1,
                    "selections": [
                        {"arxiv_code": s.arxiv_code, "reasoning": s.reasoning}
                        for s in r.selections
                    ],
                    "usage": r.usage,
                }
                for i, r in enumerate(multi)
            ],
        }
        save_json(multi_data, run_dir / "multi_run_results.json")
        print(f"Completed {args.z} runs")
        print(f"Results saved to {run_dir}")

        # Quick summary
        total_tokens = sum(r.usage["prompt_tokens"] + r.usage["completion_tokens"] for r in multi)
        total_tokens += single.usage["prompt_tokens"] + single.usage["completion_tokens"]
        print(f"\nTotal tokens used: {total_tokens:,}")


if __name__ == "__main__":
    main()
