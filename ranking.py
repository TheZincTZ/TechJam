"""
LLM Semantic Ranking stage — second half of "Multi-Route Retrieval ->
LLM Semantic Ranking".

Takes the hybrid-merged candidate pool (already narrowed from 50k down to
~top_k) and asks an LLM to re-rank by genuine semantic fit to the dialog
state, since this is where MRR / Top-K Hit Rate is won or lost.

No API key required to run the prototype: if `client` is None, falls back
to passing through the hybrid score order untouched, so the rest of the
pipeline (state tracking, routing, clarification) is fully demoable
without external credentials. Plug in a real client (Anthropic, OpenAI,
local model) by implementing `LLMRanker.rank()`'s TODO.
"""
from __future__ import annotations
from typing import List, Optional, Dict, Any

from models import Product, RetrievalCandidate, RankedResult


class LLMRanker:
    def __init__(self, client: Optional[Any] = None, model: str = "claude-sonnet-4-6"):
        self.client = client
        self.model = model

    def rank(
        self,
        query_context: str,
        candidates: List[RetrievalCandidate],
        catalog_by_asin: Dict[str, Product],
        top_k: int = 10,
    ) -> List[RankedResult]:
        pool = candidates[: max(top_k * 3, top_k)]  # rerank a modestly wider pool than we return

        if self.client is None:
            # Fallback: no LLM wired up yet -> pass through hybrid ranking.
            return [
                RankedResult(asin=c.asin, final_score=c.score, explanation="hybrid score (no LLM configured)")
                for c in pool[:top_k]
            ]

        # TODO: real LLM call. Sketch:
        #   1. Build a compact prompt: dialog context + numbered candidate
        #      list (title/category/price/attrs only, no full descriptions,
        #      to keep tokens down over a 50-item pool).
        #   2. Ask for strict JSON: [{"asin": ..., "rank": ..., "why": ...}]
        #   3. Parse and map back to RankedResult, falling back to hybrid
        #      order for any asin the model fails to return.
        raise NotImplementedError("Wire up your LLM client here.")
