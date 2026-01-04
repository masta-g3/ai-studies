"""Paper sampling for selection experiment."""

import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.db import get_connection


@dataclass
class PaperSample:
    arxiv_code: str
    title: str
    abstract: str
    published: datetime
    categories: list[str]


def get_category_mappings() -> tuple[dict[str, str], set[str], set[str]]:
    """Fetch category code -> group mappings from DB.

    Returns:
        (cat_to_group dict, valid_categories set, valid_groups set)
    """
    query = "SELECT code, category_group FROM paper_category_definitions"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    cat_to_group = {r[0]: r[1] for r in rows}
    valid_categories = set(cat_to_group.keys())
    valid_groups = set(cat_to_group.values())
    return cat_to_group, valid_categories, valid_groups


def sample_papers(
    n: int = 200,
    recency_days: int = 60,
    categories: list[str] | None = None,
    category_groups: list[str] | None = None,
    stratify_by: str = "group",
    seed: int | None = None,
) -> list[PaperSample]:
    """Sample N papers from database.

    Args:
        n: Number of papers to sample
        recency_days: Only include papers from last N days
        categories: Filter to these category codes (mutually exclusive with category_groups)
        category_groups: Filter to categories in these groups (mutually exclusive with categories)
        stratify_by: How to distribute samples - 'category' or 'group'
        seed: Random seed for reproducibility

    Returns:
        List of PaperSample objects

    Raises:
        ValueError: If invalid parameters provided
    """
    # Validate mutually exclusive filters
    if categories and category_groups:
        raise ValueError(
            "Cannot use both 'categories' and 'category_groups'. Pick one filter type."
        )

    # Validate stratify_by
    if stratify_by not in ("category", "group"):
        raise ValueError(
            f"stratify_by must be 'category' or 'group', got '{stratify_by}'"
        )

    if seed is not None:
        random.seed(seed)

    # Get category mappings for validation and grouping
    cat_to_group, valid_categories, valid_groups = get_category_mappings()

    # Validate category codes
    if categories:
        invalid = set(categories) - valid_categories
        if invalid:
            raise ValueError(
                f"Invalid category codes: {invalid}. "
                f"Valid codes: {sorted(valid_categories)}"
            )

    # Validate and expand category groups to category codes
    filter_categories = None
    if category_groups:
        invalid = set(category_groups) - valid_groups
        if invalid:
            raise ValueError(
                f"Invalid category groups: {invalid}. "
                f"Valid groups: {sorted(valid_groups)}"
            )
        # Expand groups to their category codes
        filter_categories = [
            cat for cat, group in cat_to_group.items() if group in category_groups
        ]
    elif categories:
        filter_categories = categories

    # Query papers
    cutoff = datetime.now() - timedelta(days=recency_days)

    if filter_categories:
        query = """
            SELECT DISTINCT ad.arxiv_code, ad.title, ad.summary,
                   ad.published, pc.categories
            FROM arxiv_details ad
            JOIN paper_categories pc ON ad.arxiv_code = pc.arxiv_code
            WHERE ad.published >= %s
              AND pc.categories && %s
            ORDER BY ad.published DESC
        """
        params = (cutoff, filter_categories)
    else:
        query = """
            SELECT DISTINCT ad.arxiv_code, ad.title, ad.summary,
                   ad.published, pc.categories
            FROM arxiv_details ad
            JOIN paper_categories pc ON ad.arxiv_code = pc.arxiv_code
            WHERE ad.published >= %s
            ORDER BY ad.published DESC
        """
        params = (cutoff,)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

    papers = [
        PaperSample(
            arxiv_code=r[0],
            title=r[1],
            abstract=r[2],
            published=r[3],
            categories=r[4],
        )
        for r in rows
    ]

    if not papers:
        return []

    # Stratified sampling
    if stratify_by == "category":
        by_stratum = {}
        for p in papers:
            key = p.categories[0] if p.categories else "unknown"
            by_stratum.setdefault(key, []).append(p)
    else:  # stratify_by == "group"
        by_stratum = {}
        for p in papers:
            cat = p.categories[0] if p.categories else "unknown"
            key = cat_to_group.get(cat, "Other")
            by_stratum.setdefault(key, []).append(p)

    per_stratum = max(1, n // len(by_stratum))
    sampled = []
    for stratum_papers in by_stratum.values():
        sampled.extend(random.sample(stratum_papers, min(per_stratum, len(stratum_papers))))

    if len(sampled) < n:
        remaining = [p for p in papers if p not in sampled]
        sampled.extend(random.sample(remaining, min(n - len(sampled), len(remaining))))

    random.shuffle(sampled)
    return sampled[:n]


def get_sample_distribution(
    papers: list[PaperSample], by: str = "category"
) -> dict[str, int]:
    """Get distribution of papers by category or group.

    Args:
        papers: List of sampled papers
        by: 'category' or 'group'

    Returns:
        Dict mapping category/group name to count
    """
    if by == "group":
        cat_to_group, _, _ = get_category_mappings()

    counts = {}
    for p in papers:
        cat = p.categories[0] if p.categories else "unknown"
        if by == "group":
            key = cat_to_group.get(cat, "Other")
        else:
            key = cat
        counts[key] = counts.get(key, 0) + 1

    return counts


if __name__ == "__main__":
    print("Testing sample.py...")

    # Test 1: Stratify by category (default)
    papers = sample_papers(n=10, recency_days=30, seed=42)
    print(f"\nSampled {len(papers)} papers (stratify by category):")
    for p in papers[:3]:
        print(f"  {p.arxiv_code}: {p.title[:40]}... [{p.categories[0]}]")

    # Test 2: Stratify by group
    papers = sample_papers(n=10, recency_days=30, stratify_by="group", seed=42)
    print(f"\nSampled {len(papers)} papers (stratify by group):")
    dist = get_sample_distribution(papers, by="group")
    for group, count in sorted(dist.items(), key=lambda x: -x[1]):
        print(f"  {group}: {count}")

    # Test 3: Filter by category group
    papers = sample_papers(
        n=10, recency_days=60, category_groups=["Reasoning and Knowledge"], seed=42
    )
    print(f"\nSampled {len(papers)} papers (filtered to Reasoning and Knowledge):")
    for p in papers[:3]:
        print(f"  {p.arxiv_code}: {p.title[:40]}... [{p.categories[0]}]")

    # Test 4: Error - both filters
    try:
        sample_papers(categories=["reasoning_models"], category_groups=["Other"])
    except ValueError as e:
        print(f"\nExpected error: {e}")

    # Test 5: Error - invalid category
    try:
        sample_papers(categories=["not_a_real_category"])
    except ValueError as e:
        print(f"\nExpected error (invalid category): {e}")
