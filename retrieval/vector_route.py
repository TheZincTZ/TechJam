"""
Dense/vector retrieval route.

Runs entirely in-memory (per the hackathon's "no heavy vector DB" scope
rule). Uses TF-IDF + cosine similarity as a *lightweight stand-in* for
real dense embeddings so the prototype has zero external dependencies
and no API key requirement. This is the "diverse cross-category" track
for open-ended Browsing.

Swap-out point: replace `_vectorize` with a real embedding model
(sentence-transformers, or an API embedding call) and swap the cosine
search for the same in-memory np.dot approach — the rest of the
pipeline doesn't need to change.
"""
from __future__ import annotations
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from models import Product, RetrievalCandidate


class VectorRoute:
    def __init__(self, catalog: List[Product]):
        self.catalog = catalog
        texts = [p.searchable_text() for p in catalog]
        self.vectorizer = TfidfVectorizer(max_features=20000, ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(texts)

    def retrieve(self, query: str, top_k: int = 50) -> List[RetrievalCandidate]:
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.matrix).flatten()
        top_idx = np.argsort(sims)[::-1][:top_k]
        return [
            RetrievalCandidate(asin=self.catalog[i].asin, score=float(sims[i]), route="vector")
            for i in top_idx
            if sims[i] > 0
        ]
