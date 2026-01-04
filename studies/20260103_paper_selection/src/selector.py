"""LLM-based paper selection."""

import time
from dataclasses import dataclass

from src.llm import call_gemini, parse_json_response, DEFAULT_MODEL


SELECTION_PROMPT = '''You are evaluating AI/LLM research papers for interestingness.

## Evaluation Criteria

**Upweight (+) papers that have:**
- Surprising or counter-intuitive findings about LLM behavior, capabilities, or limitations
- Novel conceptual frameworks, philosophical perspectives, or psychological insights
- Actionable agentic insights: specific patterns, failure modes, or best practices
- Creative, artistic, or highly unconventional LLM applications
- Research connecting LLMs to seemingly unrelated fields unexpectedly
- Discoveries of emergent properties that challenge existing understanding
- Controversial or counterintuitive claims backed by evidence

**Downweight (-) papers that are:**
- Focused on incremental improvements to models, architectures, or benchmarks
- Purely technical optimizations lacking conceptual shifts
- Jargon-heavy writing that obscures rather than clarifies
- Claims lacking clear evidence or conceptual grounding
- Overly mathematical without practical or conceptual implications

## Task

From the papers below, select the TOP {top_k} most interesting papers.
Use the exact arxiv_code values shown in brackets (e.g., [1] 2501.12345).

Return JSON:
```json
{{
  "selections": [
    {{
      "arxiv_code": "...",
      "reasoning": "One sentence explaining why this paper is interesting"
    }}
  ]
}}
```

## Papers

{papers_text}
'''


@dataclass
class Selection:
    arxiv_code: str
    reasoning: str


@dataclass
class SelectionResult:
    selections: list[Selection]
    usage: dict
    model: str
    reasoning_effort: str | None = None


def format_papers_for_prompt(papers: list) -> str:
    """Format papers as numbered list for prompt."""
    lines = []
    for i, p in enumerate(papers, 1):
        lines.append(f"[{i}] {p.arxiv_code}")
        lines.append(f"Title: {p.title}")
        abstract = p.abstract[:800] + "..." if len(p.abstract) > 800 else p.abstract
        lines.append(f"Abstract: {abstract}")
        lines.append("")
    return "\n".join(lines)


def select_papers(
    papers: list,
    top_k: int = 5,
    model: str = DEFAULT_MODEL,
    reasoning_effort: str | None = None,
) -> SelectionResult:
    """Have LLM select top-k interesting papers.

    Args:
        papers: List of PaperSample objects
        top_k: Number of papers to select
        model: Model identifier
        reasoning_effort: Thinking level - "minimal", "low", "medium", "high", or None

    Returns:
        SelectionResult with selections and token usage
    """
    papers_text = format_papers_for_prompt(papers)
    prompt = SELECTION_PROMPT.format(top_k=top_k, papers_text=papers_text)

    response = call_gemini(prompt, model=model, json_mode=True, reasoning_effort=reasoning_effort)
    data = parse_json_response(response)

    selections = [
        Selection(arxiv_code=s["arxiv_code"], reasoning=s["reasoning"])
        for s in data["selections"]
    ]

    return SelectionResult(
        selections=selections,
        usage=response.usage,
        model=response.model,
        reasoning_effort=response.reasoning_effort,
    )


def run_multi_selection(
    papers: list,
    top_k: int = 5,
    runs: int = 30,
    delay: float = 0.5,
    model: str = DEFAULT_MODEL,
    reasoning_effort: str | None = None,
) -> list[SelectionResult]:
    """Run selection multiple times to build distribution.

    Args:
        papers: List of PaperSample objects
        top_k: Number of papers to select per run
        runs: Number of runs
        delay: Seconds between API calls (rate limiting)
        model: Model identifier
        reasoning_effort: Thinking level - "minimal", "low", "medium", "high", or None

    Returns:
        List of SelectionResult objects
    """
    results = []
    for i in range(runs):
        result = select_papers(papers, top_k, model=model, reasoning_effort=reasoning_effort)
        results.append(result)
        if i < runs - 1:
            time.sleep(delay)
    return results


if __name__ == "__main__":
    from sample import sample_papers

    print("Testing select.py...")

    papers = sample_papers(n=20, recency_days=30, seed=42)
    print(f"Sampled {len(papers)} papers for testing\n")

    print("Running single selection (top 3)...")
    result = select_papers(papers, top_k=3)

    print(f"\nSelected {len(result.selections)} papers:")
    for s in result.selections:
        print(f"  {s.arxiv_code}: {s.reasoning[:60]}...")

    print(f"\nToken usage: {result.usage}")
