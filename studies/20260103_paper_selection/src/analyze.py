"""Analysis of paper selection experiment results."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path


def model_id_to_display_name(model_id: str) -> str:
    """Convert model ID to human-readable display name."""
    # gemini-3-flash-preview -> Gemini 3 Flash Preview
    words = model_id.replace("-", " ").split()
    return " ".join(w.capitalize() for w in words)


def compute_run_similarity(runs: list) -> list[dict]:
    """Compute Jaccard similarity between consecutive runs."""
    similarities = []
    for i in range(len(runs) - 1):
        set_a = {s["arxiv_code"] for s in runs[i]["selections"]}
        set_b = {s["arxiv_code"] for s in runs[i + 1]["selections"]}
        union = set_a | set_b
        jaccard = len(set_a & set_b) / len(union) if union else 0
        similarities.append({
            "run_pair": f"{i+1}-{i+2}",
            "jaccard": round(jaccard, 3),
            "overlap_count": len(set_a & set_b),
        })
    return similarities


def analyze_results(run_dir: Path, pool: dict) -> dict:
    """Analyze results and prepare visualization data.

    Args:
        run_dir: Directory containing single_shot.json and multi_run_results.json
        pool: Paper pool dict keyed by arxiv_code
    """
    with open(run_dir / "single_shot.json") as f:
        single = json.load(f)

    with open(run_dir / "multi_run_results.json") as f:
        multi = json.load(f)

    z = multi["params"]["z"]
    x = multi["params"]["x"]

    # Selection frequency across runs (filter hallucinated codes)
    selection_counts = Counter()
    reasoning_by_paper = {}
    hallucinated = set()

    for run in multi["runs"]:
        for sel in run["selections"]:
            code = sel["arxiv_code"]
            if code not in pool:
                hallucinated.add(code)
                continue
            selection_counts[code] += 1
            reasoning_by_paper.setdefault(code, []).append(sel["reasoning"])

    if hallucinated:
        print(f"Warning: {len(hallucinated)} hallucinated arxiv codes skipped: {hallucinated}")

    # Build paper data with frequency
    papers_with_freq = []
    for code, count in selection_counts.most_common():
        paper = pool[code]
        papers_with_freq.append({
            "arxiv_code": code,
            "title": paper["title"],
            "abstract": paper["abstract"],
            "categories": paper["categories"],
            "frequency": count,
            "percentage": round(count / z * 100, 1),
            "reasonings": reasoning_by_paper[code],
        })

    # Single-shot papers (with flag for comparison)
    single_codes = {s["arxiv_code"] for s in single["selections"] if s["arxiv_code"] in pool}
    single_shot_papers = []
    freq_by_code = {p["arxiv_code"]: p for p in papers_with_freq}
    for sel in single["selections"]:
        code = sel["arxiv_code"]
        if code not in pool:
            continue
        paper = pool[code]
        freq_entry = freq_by_code.get(code)
        single_shot_papers.append({
            "arxiv_code": code,
            "title": paper["title"],
            "abstract": paper["abstract"],
            "categories": paper["categories"],
            "reasoning": sel["reasoning"],
            "multi_run_frequency": freq_entry["frequency"] if freq_entry else 0,
            "multi_run_percentage": freq_entry["percentage"] if freq_entry else 0,
        })

    # Consensus papers (>50% selection rate)
    consensus_papers = [p for p in papers_with_freq if p["percentage"] > 50]

    # Top 5 by frequency (for comparison with single-shot)
    top_5_papers = []
    for p in papers_with_freq[:5]:
        top_5_papers.append({
            **p,
            "above_threshold": p["percentage"] > 50,
        })

    # Run-to-run stability
    run_similarities = compute_run_similarity(multi["runs"])
    avg_similarity = (
        sum(s["jaccard"] for s in run_similarities) / len(run_similarities)
        if run_similarities
        else 0
    )

    # Summary stats
    summary = {
        "total_runs": z,
        "papers_per_run": x,
        "pool_size": len(pool),
        "unique_papers_selected": len(selection_counts),
        "consensus_count": len(consensus_papers),
        "avg_run_similarity": round(avg_similarity, 3),
        "single_in_consensus": len(
            single_codes & {p["arxiv_code"] for p in consensus_papers}
        ),
    }

    return {
        "summary": summary,
        "single_shot": single_shot_papers,
        "consensus": consensus_papers,
        "top_5": top_5_papers,
        "frequency_distribution": papers_with_freq,
        "run_similarities": run_similarities,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data",
        help="Directory containing papers_pool.json and runs/ subdirectory",
    )
    parser.add_argument(
        "--publish-dir",
        type=Path,
        default=Path(__file__).parent.parent / "publish" / "viz",
        help="Output directory for viz data files",
    )
    args = parser.parse_args()

    # Load paper pool
    with open(args.data_dir / "papers_pool.json") as f:
        pool = {p["arxiv_code"]: p for p in json.load(f)}

    # Find all model runs
    runs_dir = args.data_dir / "runs"
    if not runs_dir.exists():
        print(f"Error: No runs directory found at {runs_dir}")
        return

    model_dirs = [d for d in runs_dir.iterdir() if d.is_dir()]
    if not model_dirs:
        print(f"Error: No model runs found in {runs_dir}")
        return

    # Create output directories
    viz_data_dir = args.publish_dir / "data"
    viz_data_dir.mkdir(parents=True, exist_ok=True)

    # Process each model
    models_index = {"default": None, "models": []}
    for model_dir in sorted(model_dirs):
        model_id = model_dir.name
        print(f"\n=== Analyzing {model_id} ===")

        results = analyze_results(model_dir, pool)

        # Save per-model viz data
        output_path = viz_data_dir / f"{model_id}.json"
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        # Add to models index
        models_index["models"].append({
            "id": model_id,
            "name": model_id_to_display_name(model_id),
            "file": f"data/{model_id}.json",
        })

        # Console summary
        s = results["summary"]
        print(f"Pool: {s['pool_size']} papers | Runs: {s['total_runs']} × {s['papers_per_run']} selections")
        print(f"Unique selected: {s['unique_papers_selected']} | Consensus (>50%): {s['consensus_count']}")
        print(f"Avg run similarity: {s['avg_run_similarity']:.1%}")
        print(f"Single-shot in consensus: {s['single_in_consensus']}/{s['papers_per_run']}")
        print(f"Saved: {output_path}")

    # Set default to first model
    if models_index["models"]:
        models_index["default"] = models_index["models"][0]["id"]

    # Write models index
    models_path = args.publish_dir / "models.json"
    with open(models_path, "w") as f:
        json.dump(models_index, f, indent=2)
    print(f"\nModels index: {models_path} ({len(models_index['models'])} models)")


if __name__ == "__main__":
    main()
