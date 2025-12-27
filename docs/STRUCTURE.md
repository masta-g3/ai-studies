# Embeddings Research - Project Structure

## Vision

A lightweight, organized research repository for investigating embedding concepts from machine learning. The goal is to:

1. **Collect** resources (papers, blogs, publications) via MCP paper archive + web search
2. **Analyze** embeddings through structured Python experiments
3. **Synthesize** findings into accessible markdown documents
4. **Publish** insights to a blog (separate repo)

This repo prioritizes discoverability and maintainability over complexity.

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| Language | Python 3.11+ | ML ecosystem, pandas, sklearn |
| Package Manager | uv | Fast, reliable |
| Data Storage | CSV/JSON | Simple, git-friendly, no DB overhead |
| Documentation | Markdown | Portable, renders on GitHub |
| Exploratory Viz | matplotlib/seaborn | Quick iteration during analysis |
| Publication Viz | D3.js | Interactive, consistent blog style (TBD) |

## Architecture

```
embeddings/
├── src/                    # Python modules
│   ├── __init__.py
│   ├── fetch.py           # Resource fetching (MCP, web)
│   ├── embed.py           # Embedding generation/loading
│   ├── analyze.py         # Analysis utilities
│   └── utils.py           # Common helpers
│
├── data/
│   ├── raw/               # Unprocessed fetched data
│   ├── processed/         # Cleaned/transformed data
│   └── results/           # Experiment outputs (CSVs)
│
├── research/
│   ├── questions/         # Research question specs (YAML/MD)
│   │   └── q001_granularity.md
│   ├── resources/         # Curated resource lists per topic
│   │   └── granularity/
│   └── findings/          # Synthesized conclusions
│       └── q001_granularity_findings.md
│
├── notebooks/             # Exploratory Jupyter notebooks
│
├── docs/
│   └── STRUCTURE.md       # This file
│
├── features.json          # Feature backlog
├── pyproject.toml         # Dependencies
└── README.md              # Quick start
```

## Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  MCP Archive    │────▶│   data/raw/     │────▶│ data/processed/ │
│  Web Search     │     │  (papers, urls) │     │ (cleaned CSVs)  │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ research/       │◀────│  data/results/  │◀────│   src/analyze   │
│ findings/*.md   │     │  (experiments)  │     │  (analysis)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Research Question Format

Each question in `research/questions/` follows:

```markdown
# Q001: [Title]

## Question
What specific question are we answering?

## Hypothesis
What do we expect to find?

## Method
- Data sources
- Analysis approach
- Success criteria

## Status
- [ ] Resources collected
- [ ] Data processed
- [ ] Analysis complete
- [ ] Findings written
```

## Key Patterns

### Resource Metadata
Resources are tracked in CSVs with consistent schema:

```csv
id,title,url,source_type,date_added,tags,question_id
r001,Attention Is All You Need,https://arxiv.org/...,paper,2024-01-15,"transformers,attention",q001
```

### Experiment Results
Results CSVs include experiment context:

```csv
experiment_id,question_id,timestamp,metric,value,params
exp001,q001,2024-01-15T10:30:00,cosine_similarity,0.85,"{""model"":""text-embedding-3-small""}"
```

### Findings Structure
Each finding links back to resources and experiments:

```markdown
# Q001 Findings: Concept Granularity

## Summary
[Key takeaways]

## Evidence
- Experiment exp001: [result interpretation]
- Resource r001: [relevant insight]

## Implications
[What this means for practitioners]

## Open Questions
[What we still don't know]
```

## Visualization Workflow

Two-stage approach:

1. **Exploratory** (Python): matplotlib/seaborn for quick iteration
   - Used during analysis to validate hypotheses
   - Output to `notebooks/` or inline in scripts

2. **Publication** (D3.js): Interactive visualizations for blog
   - Ported from exploratory findings once analysis is complete
   - Consistent visual style across all posts (style guide TBD)
   - Sophisticated, interactive, accessible
   - Stored in separate blog repo, data exported from here as JSON/CSV

## Commands

```bash
# Setup
uv sync
source .venv/bin/activate

# Run analysis script
python src/analyze.py --question q001

# Generate findings template
python src/utils.py init-finding q001
```

## File Naming Conventions

- Questions: `q{NNN}_{slug}.md`
- Resources: `{question_slug}/resources.csv`
- Results: `{experiment_id}_{question_id}.csv`
- Findings: `q{NNN}_{slug}_findings.md`
