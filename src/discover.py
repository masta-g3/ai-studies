"""Hierarchy discovery via LLM batching."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.db import Paper, count_papers, fetch_papers
from src.llm import call_gemini, parse_json_response


@dataclass
class PaperInfo:
    arxiv_code: str
    title: str


@dataclass
class Subcategory:
    name: str
    description: str
    papers: list[PaperInfo] = field(default_factory=list)
    children: list["Subcategory"] = field(default_factory=list)

    @property
    def paper_count(self) -> int:
        return len(self.papers)

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "description": self.description,
            "paper_count": self.paper_count,
            "papers": [{"arxiv_code": p.arxiv_code, "title": p.title} for p in self.papers],
        }
        if self.children:
            result["children"] = [c.to_dict() for c in self.children]
        return result


@dataclass
class HierarchyResult:
    category: str
    discovered_at: str
    depth: int
    subcategories: list[Subcategory]
    unassigned: list[PaperInfo]

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "discovered_at": self.discovered_at,
            "depth": self.depth,
            "subcategories": [s.to_dict() for s in self.subcategories],
            "unassigned": [{"arxiv_code": p.arxiv_code, "title": p.title} for p in self.unassigned],
        }


DISCOVERY_PROMPT = """
You are analyzing {paper_count} academic papers from the "{category}" category.

Your task: Identify natural subcategories that group these papers by conceptually distinct themes.

Context: These groupings will be validated using embedding similarity analysis. Papers in the same subcategory should be semantically similar in embedding space.

Guidelines:
- Focus on conceptually distinct groups that would cluster together in embedding space
- Each subcategory should represent a coherent research theme
- Use clear, descriptive names (2-5 words)
- If some papers don't fit any clear group, create an "Other/Miscellaneous" category for them
- Don't force papers into categories - it's okay to have outliers

Papers (title + first 200 chars of abstract):
{papers_text}

Respond with valid JSON only:
{{
  "subcategories": [
    {{"name": "Subcategory Name", "description": "Brief description of focus area"}}
  ]
}}
"""

ASSIGNMENT_PROMPT = """
Classify each paper into the most appropriate subcategory based on its title and abstract.

Available subcategories:
{subcategories_json}

Papers to classify (format: arxiv_code | title | abstract_snippet):
{papers_text}

Guidelines:
- Assign each paper to the single best-fitting subcategory
- If a paper doesn't clearly fit any subcategory, use "Unassigned"
- Consider which papers would cluster together in embedding space

Respond with valid JSON only:
{{
  "assignments": [
    {{"arxiv_code": "2401.00123", "subcategory": "Exact Subcategory Name or Unassigned"}}
  ]
}}
"""


def format_papers_for_prompt(papers: list[Paper], max_abstract_chars: int = 200) -> str:
    """Format papers for LLM prompt."""
    lines = []
    for p in papers:
        abstract = p.summary[:max_abstract_chars].replace("\n", " ")
        lines.append(f"- {p.arxiv_code} | {p.title} | {abstract}...")
    return "\n".join(lines)


def batch_papers(papers: list[Paper], batch_size: int = 50) -> list[list[Paper]]:
    """Split papers into batches."""
    return [papers[i : i + batch_size] for i in range(0, len(papers), batch_size)]


def discover_subcategories(
    category: str,
    papers: list[Paper],
    batch_size: int = 50,
) -> list[Subcategory]:
    """Phase 1: Discover subcategories from paper batches."""
    batches = batch_papers(papers, batch_size)
    all_proposals = []

    print(f"  Discovering subcategories from {len(batches)} batches...")

    for i, batch in enumerate(batches):
        prompt = DISCOVERY_PROMPT.format(
            paper_count=len(batch),
            category=category,
            papers_text=format_papers_for_prompt(batch),
        )
        response = call_gemini(prompt)
        result = parse_json_response(response)
        all_proposals.extend(result.get("subcategories", []))
        print(f"    Batch {i + 1}/{len(batches)}: {len(result.get('subcategories', []))} proposals")

    return merge_proposals(all_proposals, category)


def merge_proposals(proposals: list[dict], category: str) -> list[Subcategory]:
    """Merge similar subcategory proposals into unified list."""
    if len(proposals) <= 8:
        return [Subcategory(name=p["name"], description=p["description"]) for p in proposals]

    merge_prompt = f"""
You have {len(proposals)} subcategory proposals for the "{category}" category.
Many are duplicates or overlapping. Consolidate them into distinct, non-overlapping subcategories.

Guidelines:
- Merge truly duplicate or highly overlapping proposals
- Keep conceptually distinct topics separate, even if they only have a few proposals
- If some proposals don't fit any major theme, group them as "Other/Miscellaneous"
- Aim for clarity over forced consolidation - it's okay to have more categories if they're genuinely distinct
- The result will be validated with embedding analysis, so semantic distinctness matters

Proposals:
{json.dumps(proposals, indent=2)}

Respond with valid JSON only:
{{
  "subcategories": [
    {{"name": "Merged Name", "description": "Combined description"}}
  ]
}}
"""
    response = call_gemini(merge_prompt)
    result = parse_json_response(response)
    return [
        Subcategory(name=s["name"], description=s["description"])
        for s in result.get("subcategories", [])
    ]


def assign_papers(
    papers: list[Paper],
    subcategories: list[Subcategory],
    batch_size: int = 50,
) -> tuple[list[Subcategory], list[PaperInfo]]:
    """Phase 2: Assign papers to discovered subcategories."""
    batches = batch_papers(papers, batch_size)
    subcats_json = json.dumps(
        [{"name": s.name, "description": s.description} for s in subcategories]
    )

    subcat_map = {s.name: s for s in subcategories}
    paper_map = {p.arxiv_code: p for p in papers}
    unassigned = []

    print(f"  Assigning {len(papers)} papers to {len(subcategories)} subcategories...")

    for i, batch in enumerate(batches):
        prompt = ASSIGNMENT_PROMPT.format(
            subcategories_json=subcats_json,
            papers_text=format_papers_for_prompt(batch),
        )
        response = call_gemini(prompt)
        result = parse_json_response(response)

        for assignment in result.get("assignments", []):
            arxiv_code = assignment.get("arxiv_code")
            subcat_name = assignment.get("subcategory")

            if not arxiv_code or not subcat_name:
                continue

            if arxiv_code not in paper_map:
                continue

            paper = paper_map[arxiv_code]
            paper_info = PaperInfo(arxiv_code=arxiv_code, title=paper.title)

            if subcat_name.lower() == "unassigned":
                unassigned.append(paper_info)
            elif subcat_name in subcat_map:
                subcat_map[subcat_name].papers.append(paper_info)
            else:
                unassigned.append(paper_info)

        print(f"    Batch {i + 1}/{len(batches)}: assigned {len(result.get('assignments', []))} papers")

    return list(subcat_map.values()), unassigned


def run_discovery(
    category: str,
    limit: int = 500,
    batch_size: int = 50,
    depth: int = 1,
) -> HierarchyResult:
    """Run full hierarchy discovery pipeline for a category.

    Args:
        category: Category code (e.g., 'reasoning_models')
        limit: Max papers to fetch
        batch_size: Papers per LLM batch
        depth: 1 for subcategories only, 2 for sub-subcategories

    Returns:
        HierarchyResult with discovered hierarchy and paper assignments
    """
    print(f"\n{'='*60}")
    print(f"Hierarchy Discovery: {category} (depth={depth})")
    print(f"{'='*60}")

    total = count_papers(category)
    papers = fetch_papers(category, limit=limit)
    paper_map = {p.arxiv_code: p for p in papers}
    print(f"Fetched {len(papers)} papers (of {total} total)")

    # Level 1: Discover subcategories
    print(f"\n[Level 1] Discovering subcategories...")
    subcategories = discover_subcategories(category, papers, batch_size)
    subcategories, unassigned = assign_papers(papers, subcategories, batch_size)

    print(f"\n  Found {len(subcategories)} subcategories:")
    for s in subcategories:
        print(f"    - {s.name}: {s.paper_count} papers")

    # Level 2: Discover sub-subcategories (if depth=2)
    if depth >= 2:
        print(f"\n[Level 2] Discovering sub-subcategories...")
        for subcat in subcategories:
            if subcat.paper_count < 6:
                print(f"  Skipping '{subcat.name}' (only {subcat.paper_count} papers)")
                continue

            print(f"\n  Processing '{subcat.name}' ({subcat.paper_count} papers)...")
            subcat_papers = [paper_map[p.arxiv_code] for p in subcat.papers if p.arxiv_code in paper_map]

            children = discover_subcategories(subcat.name, subcat_papers, batch_size)
            children, child_unassigned = assign_papers(subcat_papers, children, batch_size)

            subcat.children = children
            print(f"    Found {len(children)} sub-subcategories:")
            for c in children:
                print(f"      - {c.name}: {c.paper_count} papers")

    result = HierarchyResult(
        category=category,
        discovered_at=datetime.now(timezone.utc).isoformat(),
        depth=depth,
        subcategories=subcategories,
        unassigned=unassigned,
    )

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for s in subcategories:
        print(f"{s.name}: {s.paper_count} papers")
        for c in s.children:
            print(f"  └── {c.name}: {c.paper_count} papers")
    print(f"Unassigned: {len(unassigned)} papers")

    return result
