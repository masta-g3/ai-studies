# Epic: Concept Granularity (`gran`)

> **Tracking**: See `features.json` for individual feature status (`gran-001` through `gran-006`)

## Goal

Investigate: **What level of semantic granularity can embeddings capture?**

We want to understand whether pre-computed Gemini embeddings can distinguish papers at multiple hierarchical levels — from broad categories down to narrow sub-sub-topics.

## Data Context

**Source**: PostgreSQL MCP with ~12,700 papers, each with:
- Gemini embeddings (3072-dim)
- 1+ category labels from 42 predefined categories
- Title + abstract text

**Target**: ~500 papers organized into 3-level hierarchy:
```
Category (DB-provided) → Subcategory (AI-derived) → Sub-subcategory (AI-derived)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PHASE 1: Data Curation                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │   Select     │───▶│   Sample     │───▶│   LLM        │           │
│  │   Categories │    │   Papers     │    │   Classify   │           │
│  │   (4-5)      │    │   (~2000)    │    │   (Gemini)   │           │
│  └──────────────┘    └──────────────┘    └──────────────┘           │
│                                                 │                    │
│                                                 ▼                    │
│                                    ┌──────────────────────┐          │
│                                    │  Curated Dataset     │          │
│                                    │  ~500 papers         │          │
│                                    │  3-level hierarchy   │          │
│                                    └──────────────────────┘          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      PHASE 2: Analysis Pipeline                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │   Fetch      │───▶│   Compute    │───▶│   Evaluate   │           │
│  │   Embeddings │    │   Distances  │    │   Metrics    │           │
│  └──────────────┘    └──────────────┘    └──────────────┘           │
│         │                   │                   │                    │
│         ▼                   ▼                   ▼                    │
│    PostgreSQL          Cosine/L2         Silhouette, ARI,           │
│    (pgvector)          Pairwise          Intra/Inter cluster        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      PHASE 3: Reporting                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Exploratory (matplotlib)  ──▶  Notebook Report                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

> **Note**: D3.js visualization is out of scope — separate follow-up epic.

## Category Selection

Based on DB analysis, selecting **4 categories** with rich internal structure:

| Category | Count | Rationale |
|----------|-------|-----------|
| `reasoning_models` | 1,030 | Clear subtopics: CoT, math reasoning, verification, RL-based |
| `agentic_systems` | 993 | Rich hierarchy: tool-use, multi-agent, memory, planning |
| `model_compression` | 783 | Distinct methods: quantization, pruning, distillation, LoRA |
| `multimodal_integration` | 906 | Cross-modal subtopics: vision-language, audio, document |

**Target**: ~125 papers per category × 4 = 500 papers

## Hierarchy Discovery Approach

The 3-level hierarchy (category → subcategory → sub-subcategory) will be **discovered from data**, not prescribed upfront.

### Process

1. **Large sample**: Fetch ~500 papers per category from DB (2000 total)

2. **LLM-assisted discovery**: For each category, prompt LLM to identify natural clusters:
   - Input: batch of paper titles + abstracts
   - Output: proposed subcategory groupings with rationale
   - Iterate to identify sub-subcategories within each subcategory

3. **Manual curation**: Review LLM proposals, refine into coherent hierarchy:
   - Ensure each level has 3+ groups (statistical validity)
   - Ensure groups are semantically distinct
   - Aim for balanced distribution across groups

4. **Classification script**: Once hierarchy is validated, build classifier:
   - Fetch papers from DB by category
   - Use LLM to assign subcategory/sub-subcategory labels
   - Apply quotas to ensure balanced final dataset (~125 per category)

5. **Output**: `data/curated_papers.json` with ~500 papers, each labeled with:
   - `arxiv_code`, `title`, `abstract`
   - `category`, `subcategory`, `subsubcategory`

### Balancing Strategy

```
Per category:     ~125 papers
Per subcategory:  ~40 papers  (assuming 3 subcategories)
Per sub-subcat:   ~13 papers  (assuming 3 sub-subcategories)
```

Iterate over papers, applying quotas at each level to prevent imbalance.

## Analysis Approach

**To be defined during feature planning.** Key considerations:

- What does "capture granularity" mean operationally?
- What's the downstream use case? (retrieval, clustering, understanding geometry)
- Metrics should be derived from research question, not defaulted

### Core Question

> At what hierarchy level do embeddings stop providing useful semantic signal?

## File Structure

```
embeddings/
├── src/
│   ├── db.py              # PostgreSQL connection utilities
│   ├── classify.py        # LLM classification logic
│   └── metrics.py         # Embedding analysis metrics
├── experiments/
│   ├── curate_dataset.py  # Data curation script
│   ├── analyze.py         # Exploratory analysis
│   └── granularity.ipynb  # Final notebook report
├── data/
│   └── curated_papers.json
└── .env
```

## Dependencies

```toml
[project]
dependencies = [
    "psycopg2-binary",
    "litellm",
    "numpy",
    "scikit-learn",
    "matplotlib",
    "seaborn",
    "python-dotenv",
]
```

## Open Questions

1. **Hierarchy depth**: 3 levels may not be achievable for all categories. Some may only support 2 meaningful levels.

2. **Sample size**: 500 papers (~13 per sub-subcategory) may be tight for statistical significance. Can scale up if needed.

3. **Embedding comparison**: Starting with Gemini embeddings. Framework should allow future comparison with other models.
