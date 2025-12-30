"""Database utilities for fetching papers and embeddings."""

import os
from dataclasses import dataclass

import numpy as np
import psycopg2
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Paper:
    arxiv_code: str
    title: str
    summary: str


@dataclass
class Category:
    code: str
    full_name: str
    description: str
    category_group: str


def get_connection():
    """Create PostgreSQL connection from .env credentials."""
    return psycopg2.connect(
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
    )


def fetch_papers(category: str, limit: int = 500, offset: int = 0) -> list[Paper]:
    """Fetch papers by category with pagination.

    Args:
        category: Category code (e.g., 'reasoning_models')
        limit: Max papers to return
        offset: Skip first N papers

    Returns:
        List of Paper objects with arxiv_code, title, summary
    """
    query = """
        SELECT ad.arxiv_code, ad.title, ad.summary
        FROM paper_categories pc
        JOIN arxiv_details ad ON pc.arxiv_code = ad.arxiv_code
        WHERE %s = ANY(pc.categories)
        ORDER BY ad.arxiv_code
        LIMIT %s OFFSET %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (category, limit, offset))
            return [Paper(arxiv_code=r[0], title=r[1], summary=r[2]) for r in cur.fetchall()]


def fetch_embeddings(arxiv_codes: list[str]) -> dict[str, np.ndarray]:
    """Batch fetch embeddings for given arxiv codes.

    Args:
        arxiv_codes: List of arxiv codes to fetch

    Returns:
        Dict mapping arxiv_code to 3072-dim numpy array
    """
    if not arxiv_codes:
        return {}

    query = """
        SELECT arxiv_code, embedding
        FROM arxiv_embeddings_3072
        WHERE arxiv_code = ANY(%s)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (arxiv_codes,))
            results = {}
            for arxiv_code, embedding in cur.fetchall():
                if isinstance(embedding, str):
                    vec = np.fromstring(embedding.strip("[]"), sep=",")
                else:
                    vec = np.array(embedding)
                results[arxiv_code] = vec
            return results


def list_categories() -> list[Category]:
    """Fetch all category definitions."""
    query = """
        SELECT code, full_name, description, category_group
        FROM paper_category_definitions
        ORDER BY display_order
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return [
                Category(code=r[0], full_name=r[1], description=r[2], category_group=r[3])
                for r in cur.fetchall()
            ]


def count_papers(category: str) -> int:
    """Count papers in a category."""
    query = """
        SELECT COUNT(*)
        FROM paper_categories
        WHERE %s = ANY(categories)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (category,))
            return cur.fetchone()[0]


if __name__ == "__main__":
    print("Testing db.py...")

    # Test 1: Fetch papers
    papers = fetch_papers("reasoning_models", limit=5)
    print(f"\nfetch_papers('reasoning_models', limit=5):")
    for p in papers:
        print(f"  {p.arxiv_code}: {p.title[:60]}...")

    # Test 2: Fetch embeddings
    codes = [p.arxiv_code for p in papers]
    embeddings = fetch_embeddings(codes)
    print(f"\nfetch_embeddings({codes}):")
    for code, vec in embeddings.items():
        print(f"  {code}: shape={vec.shape}, dtype={vec.dtype}")

    # Test 3: Count
    count = count_papers("reasoning_models")
    print(f"\ncount_papers('reasoning_models'): {count}")

    # Test 4: Categories
    cats = list_categories()
    print(f"\nlist_categories(): {len(cats)} categories")
    for c in cats[:3]:
        print(f"  {c.code}: {c.full_name}")
