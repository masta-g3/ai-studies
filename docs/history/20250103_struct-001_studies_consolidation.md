# struct-001: Consolidate Study Directory Structure

Refactored from scattered `experiments/` + `data/` directories to unified `studies/` with self-contained dated subdirectories.

## Structure

```
studies/YYYYMMDD_topic/
├── src/           # Python scripts
├── viz/           # D3.js visualizations
└── data/          # Generated outputs (gitignored)
```

## Design Decisions

- **`studies/` container** over top-level dated directories — cleaner root, easy gitignore pattern
- **Self-contained studies** — each study has its own `src/`, `viz/`, `data/`
- **No import changes needed** — scripts use `from src.db import ...` with `PYTHONPATH=.`

## Completed

- [x] Created `studies/` with `20251230_granularity` and `20250103_paper_selection`
- [x] Moved scripts to `studies/{study}/src/`
- [x] Moved viz to `studies/{study}/viz/`
- [x] Updated hardcoded paths in entry scripts to use `Path(__file__).parent.parent / "data"`
- [x] Updated `.gitignore` to `studies/*/data/`
- [x] Updated `docs/STRUCTURE.md` and `README.md`
