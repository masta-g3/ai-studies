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
│   ├── STRUCTURE.md               # This file
│   └── VISUAL_GUIDE.md            # D3.js visualization standards
├── features.json                  # Feature backlog
├── pyproject.toml
└── README.md
```

## Workflow

Research develops iteratively: question → explore → build → visualize → publish.

### Study Lifecycle

Studies emerge through conversation, not upfront scaffolding. The user drives direction; structure follows discovery.

1. **Question** — User defines what we're investigating
2. **Explore** — Query database, read papers, gather context (iterative, user-guided)
3. **Build** — Scripts in `experiments/{date}_{topic}/`, outputs to `data/{date}_{topic}/`
4. **Visualize** — D3.js in `viz/` subdirectory, following [VISUAL_GUIDE.md](VISUAL_GUIDE.md)
5. **Publish** — Synthesize findings for blog (separate repo)

Steps 2-4 often interleave. Don't pre-scaffold—build what's needed when it's needed.

### Conventions

**Naming**: Studies use `YYYYMMDD_topic` prefix for chronological grouping.

**Code location**:
- `src/` — Shared utilities (reusable across studies)
- `experiments/` — Study-specific scripts (not meant for reuse)

**Data**: Generated outputs live in `data/` (gitignored). Raw JSON for traceability.

**Features**: Tracked in `features.json` with epic prefixes (e.g., `gran-001`, `gran-002`). Plans start in `docs/plans/`, archived to `docs/history/` on completion.

### Assistant Collaboration

The repository is human-guided, assistant-implemented:
- User drives research direction and decisions
- Assistant handles implementation, code, and visualization
- Conversation history provides context; code provides ground truth
