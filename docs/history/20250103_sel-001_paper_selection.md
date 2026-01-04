# Feature: sel-001 — LLM Paper Selection Experiment

> **Epic**: Paper Selection
> **Status**: Done
> **Completed**: 2025-01-03

## Summary

Experiment comparing single-shot vs multi-run LLM paper selection. Tests whether running selection Z times and analyzing consensus yields more interesting papers than a single selection.

## Design

```
Sample N papers → Single-shot select top X
               → Multi-run select top X × Z times
               → Analyze frequency distribution + consensus
               → D3.js visualization for human evaluation
```

## Evaluation Criteria

**Upweight (+)**: Surprising findings, novel frameworks, agentic insights, unconventional applications, emergent properties, controversial claims with evidence.

**Downweight (-)**: Incremental improvements, pure optimizations, jargon-heavy writing, unsubstantiated claims, overly mathematical.

## API

```
experiments/20250103_paper_selection/
├── sample.py           # Paper sampling with stratification
├── selector.py         # LLM selection logic
├── run_experiment.py   # CLI orchestrator
├── analyze.py          # Prepares viz_data.json
└── viz/                # D3.js interactive dashboard
```

### CLI Usage

```bash
# Sample (stratified by group by default)
python run_experiment.py --sample [--n 200] [--stratify-by group|category]
                         [--categories ...] [--category-groups ...]

# Run selection
python run_experiment.py --select [--x 5] [--z 30]

# Analyze
python analyze.py
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| N | 200 | Papers to sample |
| X | 5 | Papers per selection |
| Z | 30 | Multi-run iterations |
| stratify-by | group | Stratification level |
| recency-days | 60 | Paper recency filter |

## Visualization

D3.js dashboard following Tufte principles:
- Headline stats with run similarity sparkline
- Side-by-side single-shot vs consensus comparison
- Collapsible frequency distribution
- Click-to-expand paper details with abstract and LLM reasoning

## Completed

- [x] Sampling module with category/group stratification
- [x] Selection module with evaluation criteria prompt
- [x] Multi-run execution with rate limiting
- [x] Analysis with frequency, consensus, Jaccard similarity
- [x] Interactive D3.js visualization
