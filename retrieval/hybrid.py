"""
Multi-Route Retrieval combiner.

"Pipeline Base: Multi-Route Retrieval -> LLM Semantic Ranking (combining
keyword, category, and vector similarity)."

Route weights differ by detected intent:
- BUYING: keyword + category dominate (precision, hard constraints).
- BROWSING: vector dominates, category is a soft boost only (diversity).

Scores are min-max normalized per-route before weighting so no single
route's raw scale (BM25 vs TF-IDF cosine vs filter-match-count) dominates
by accident.
"""
from __future__ import annotations
from typing import List, Dict
from collections import defaultdict

from models import RetrievalCandidate
from intent_router import Intent

WEIGHTS = {
    Intent.BUYING: {"keyword": 0.4, "category": 0.4, "vector": 0.2},
    Intent.BROWSING: {"keyword": 0.2, "category": 0.2, "vector": 0.6},
}


def _normalize(cands: List[RetrievalCandidate]) -> Dict[str, float]:
    if not cands:
        return {}
    scores = [c.score for c in cands]
    lo, hi = min(scores), max(scores)
    rng = (hi - lo) or 1.0
    return {c.asin: (c.score - lo) / rng for c in cands}


def merge_routes(
    keyword_cands: List[RetrievalCandidate],
    category_cands: List[RetrievalCandidate],
    vector_cands: List[RetrievalCandidate],
    intent: Intent,
) -> List[RetrievalCandidate]:
    weights = WEIGHTS[intent]
    norm_kw = _normalize(keyword_cands)
    norm_cat = _normalize(category_cands)
    norm_vec = _normalize(vector_cands)

    combined: Dict[str, float] = defaultdict(float)
    for asin, sc in norm_kw.items():
        combined[asin] += sc * weights["keyword"]
    for asin, sc in norm_cat.items():
        combined[asin] += sc * weights["category"]
    for asin, sc in norm_vec.items():
        combined[asin] += sc * weights["vector"]

    merged = [RetrievalCandidate(asin=a, score=s, route="hybrid") for a, s in combined.items()]
    merged.sort(key=lambda c: c.score, reverse=True)
    return merged
