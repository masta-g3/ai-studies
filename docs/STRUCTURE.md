# Embeddings Research - Project Structure

## Vision

A lightweight research repository for investigating embedding concepts from machine learning. The goal is to:

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
| Data Storage | PostgreSQL + CSV/JSON | MCP paper archive for papers/embeddings, local JSON for curated datasets |
| Documentation | Markdown | Portable, renders on GitHub |
| Exploratory Viz | matplotlib/seaborn | Quick iteration during analysis |
| Publication Viz | D3.js | Interactive, consistent blog style |

## Architecture

```
embeddings/
├── src/                           # Shared Python modules
│   ├── __init__.py
│   ├── db.py                      # PostgreSQL utilities (papers, embeddings)
│   └── llm.py                     # LiteLLM wrapper for Gemini
├── experiments/                   # Study-specific scripts
│   └── 20251230_granularity/      # Concept granularity study
│       ├── discover.py            # Hierarchy discovery logic
│       ├── run_discovery.py       # CLI entry point
│       ├── render_hierarchy.py    # Tree/markdown rendering
│       └── viz/                   # D3.js interactive visualization
│           ├── index.html
│           ├── style.css
│           └── hierarchy-tree.js
├── data/                          # Generated outputs (gitignored)
│   └── 20251230_granularity/      # Study outputs
├── docs/
│   ├── plans/                     # Active feature plans
│   ├── history/                   # Archived completed features
│   └── STRUCTURE.md
├── features.json                  # Feature backlog
├── pyproject.toml
└── README.md
```
