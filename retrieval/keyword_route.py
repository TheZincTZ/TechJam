"""
Keyword retrieval route (BM25).

This is the "high-precision filter track" workhorse for Buying intent:
sparse lexical matching is good at nailing exact terms (brand names,
model numbers) that dense retrieval can blur over.
"""
from __future__ import annotations
from typing import List
from rank_bm25 import BM25Okapi

from models import Product, RetrievalCandidate


def _tokenize(text: str) -> List[str]:
    return text.lower().split()


class KeywordRoute:
    def __init__(self, catalog: List[Product]):
        self.catalog = catalog
        self._corpus_tokens = [_tokenize(p.searchable_text()) for p in catalog]
        self.bm25 = BM25Okapi(self._corpus_tokens)

    def retrieve(self, query: str, top_k: int = 50) -> List[RetrievalCandidate]:
        scores = self.bm25.get_scores(_tokenize(query))
        ranked = sorted(zip(self.catalog, scores), key=lambda x: x[1], reverse=True)[:top_k]
        return [
            RetrievalCandidate(asin=p.asin, score=float(sc), route="keyword")
            for p, sc in ranked
            if sc > 0
        ]
