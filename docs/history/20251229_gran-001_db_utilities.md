# Feature: gran-001 — Database Utilities

> **Epic**: Concept Granularity
> **Status**: Done
> **Completed**: 2025-12-29

## Summary

PostgreSQL utilities for fetching papers and embeddings by category. Foundational data layer for granularity analysis.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| DB Connection | psycopg2 direct | Need numpy array conversion for embeddings |
| Paper fields | title + summary | Sufficient for LLM classification |
| Embedding format | numpy.ndarray | Ready for sklearn/scipy |
| Multi-category | Include overlapping | Fetch by single category, allow duplicates |
| Credentials | .env file | `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT` |
| Pagination | limit + offset | Clean, efficient for large fetches |
| Caching | None | Fresh queries, no complexity |

## Database Schema

```
arxiv_details
├── arxiv_code (PK), title, summary

arxiv_embeddings_3072
├── arxiv_code, embedding (vector 3072-dim)

paper_categories
├── arxiv_code, categories (array)

paper_category_definitions
├── code (PK), full_name, description, category_group
```

## API

```
src/db.py
├── get_connection() → psycopg2.connection
├── fetch_papers(category, limit, offset) → list[Paper]
├── fetch_embeddings(arxiv_codes) → dict[str, np.ndarray]
├── list_categories() → list[Category]
└── count_papers(category) → int
```

## Completed

- [x] Add psycopg2-binary, python-dotenv to pyproject.toml
- [x] Create src/db.py with all functions
- [x] Verify fetch_papers returns papers with arxiv_code, title, summary
- [x] Verify fetch_embeddings returns 3072-dim numpy arrays
- [x] Verify count_papers returns ~1030 for reasoning_models
