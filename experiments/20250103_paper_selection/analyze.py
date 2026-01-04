"""Analysis of paper selection experiment results."""

import argparse
import json
from collections import Counter
from pathlib import Path


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


def analyze_results(data_dir: Path) -> dict:
    """Analyze results and prepare visualization data."""
    with open(data_dir / "papers_pool.json") as f:
        pool = {p["arxiv_code"]: p for p in json.load(f)}

    with open(data_dir / "single_shot.json") as f:
        single = json.load(f)

    with open(data_dir / "multi_run_results.json") as f:
        multi = json.load(f)

    z = multi["params"]["z"]
    x = multi["params"]["x"]

    # Selection frequency across runs
    selection_counts = Counter()
    reasoning_by_paper = {}

    for run in multi["runs"]:
        for sel in run["selections"]:
            code = sel["arxiv_code"]
            selection_counts[code] += 1
            reasoning_by_paper.setdefault(code, []).append(sel["reasoning"])

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
    single_codes = {s["arxiv_code"] for s in single["selections"]}
    single_shot_papers = []
    freq_by_code = {p["arxiv_code"]: p for p in papers_with_freq}
    for sel in single["selections"]:
        code = sel["arxiv_code"]
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
        "frequency_distribution": papers_with_freq,
        "run_similarities": run_similarities,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/20250103_paper_selection"),
    )
    args = parser.parse_args()

    results = analyze_results(args.data_dir)

    output_path = args.data_dir / "viz_data.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    # Console summary
    s = results["summary"]
    print(f"\n=== Summary ===")
    print(
        f"Pool: {s['pool_size']} papers | Runs: {s['total_runs']} × {s['papers_per_run']} selections"
    )
    print(
        f"Unique selected: {s['unique_papers_selected']} | Consensus (>50%): {s['consensus_count']}"
    )
    print(f"Avg run similarity: {s['avg_run_similarity']:.1%}")
    print(f"Single-shot in consensus: {s['single_in_consensus']}/{s['papers_per_run']}")
    print(f"\nViz data: {output_path}")


if __name__ == "__main__":
    main()
