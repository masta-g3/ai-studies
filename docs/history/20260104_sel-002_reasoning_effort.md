# Reasoning Effort Parameter Support

Add `reasoning_effort` parameter to the LLM interface, enabling experiments with different thinking levels across providers.

## Summary

Added support for controlling LLM reasoning/thinking effort via the `--reasoning-effort` CLI flag. LiteLLM handles provider-specific translation (e.g., maps to `thinking_level` for Gemini models).

## Provider Support

| Provider | Parameter | Valid Values | Default |
|----------|-----------|--------------|---------|
| Gemini 3 | `reasoning_effort` → `thinking_level` | `minimal`, `low`, `medium`, `high` | `high` |
| OpenAI o1/o3 | `reasoning_effort` | `low`, `medium`, `high` | varies |
| Anthropic | (not yet supported) | — | — |

## Changes

- [x] `src/llm.py`: Added `reasoning_effort` param to `call_llm()` and `LLMResponse` dataclass
- [x] `studies/.../src/selector.py`: Added `reasoning_effort` to `SelectionResult`, `select_papers()`, `run_multi_selection()`
- [x] `studies/.../src/run_experiment.py`: Added `--reasoning-effort` CLI flag (default: medium), updated `model_to_id()` to include suffix

## Usage

```bash
# Default (medium reasoning)
uv run python run_experiment.py --select

# High reasoning effort
uv run python run_experiment.py --select --reasoning-effort high

# Low reasoning effort
uv run python run_experiment.py --select --reasoning-effort low
```

Output directories include reasoning effort in ID:
- `data/runs/gemini-3-flash-preview-medium/`
- `data/runs/gemini-3-flash-preview-high/`
- `data/runs/gemini-3-flash-preview-low/`
