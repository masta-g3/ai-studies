# Feature: gran-002 — Hierarchy Discovery Script

> **Epic**: Concept Granularity
> **Status**: Done
> **Completed**: 2025-12-30

## Summary

LLM-powered hierarchy discovery for paper categories. Uses Gemini 3 Flash via LiteLLM to discover subcategories and sub-subcategories from paper abstracts, with embedding-aware prompting.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM Provider | LiteLLM + Gemini 3 Flash | Unified interface, latest model |
| Workflow | Batch then review | Run all batches, output JSON for offline validation |
| Output | JSON per category | `data/hierarchy_{category}.json` with structure + paper assignments |
| Batching | ~50 papers/batch | Balance context window vs. coherent grouping |
| Prompts | Embedding-aware | Framed around semantic clustering for validation |

## API

```
src/llm.py
├── call_gemini(prompt, json_mode) → LLMResponse
└── parse_json_response(response) → dict

src/discover.py
├── run_discovery(category, limit, batch_size, depth) → HierarchyResult
├── discover_subcategories(category, papers, batch_size) → list[Subcategory]
├── merge_proposals(proposals, category) → list[Subcategory]
└── assign_papers(papers, subcategories, batch_size) → (list[Subcategory], list[PaperInfo])

experiments/run_discovery.py
└── CLI: category [--limit] [--batch-size] [--depth] [--output]

experiments/render_hierarchy.py
└── CLI: input [--format tree|markdown|summary] [--papers] [--output]
```

## Output Format

```json
{
  "category": "reasoning_models",
  "depth": 2,
  "subcategories": [{
    "name": "Chain-of-Thought Prompting",
    "description": "...",
    "paper_count": 156,
    "papers": [{"arxiv_code": "2401.00123", "title": "..."}],
    "children": [{ /* same structure */ }]
  }],
  "unassigned": [{"arxiv_code": "...", "title": "..."}]
}
```

## Usage

```bash
# Discover hierarchy (depth=2 for sub-subcategories)
uv run python experiments/run_discovery.py reasoning_models --depth 2

# Render results
uv run python experiments/render_hierarchy.py data/hierarchy_reasoning_models.json
uv run python experiments/render_hierarchy.py data/hierarchy_reasoning_models.json --papers
uv run python experiments/render_hierarchy.py data/hierarchy_reasoning_models.json --format markdown
```

## Completed

- [x] Add litellm dependency to pyproject.toml
- [x] Create src/llm.py with Gemini wrapper
- [x] Create src/discover.py with two-phase discovery logic
- [x] Create experiments/run_discovery.py CLI
- [x] Create experiments/render_hierarchy.py for tree/markdown output
- [x] Add --depth flag for sub-subcategory discovery
- [x] Include paper titles in output (not just arxiv_codes)
- [x] Embedding-aware prompts for semantic clustering validation
