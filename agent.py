"""
ShoppingCopilotAgent — wires together the Pillar I + II foundation:

  Turn -> StateTracker.update -> IntentRouter.classify
       -> [KeywordRoute, CategoryRoute, VectorRoute] -> merge_routes
       -> over-generality check -> (clarify | LLMRanker.rank) -> response

This is deliberately the "foundation" slice only: Pillar III (long-term
profile distillation / runtime re-orchestration) is stubbed as a TODO
hook (`_update_long_term_profile`) so the state machine already has the
right seam to grow into it without a rewrite.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from models import Product, RankedResult
from state_tracker import StateTracker
from intent_router import IntentRouter, Intent
from retrieval.keyword_route import KeywordRoute
from retrieval.category_route import CategoryRoute
from retrieval.vector_route import VectorRoute
from retrieval.hybrid import merge_routes
from ranking import LLMRanker

# Candidate-pool size above which we treat the query as "Over-Generic" and
# cut retrieval short to ask a clarifying question instead of ranking blind.
OVER_GENERALITY_THRESHOLD = 30
MAX_TURNS = 10  # hard limit from problem statement 4.3


@dataclass
class AgentResponse:
    turn: int
    intent: Intent
    slots: Dict[str, Any]
    action: str  # "clarify" | "results" | "session_terminated"
    clarification_prompt: Optional[str] = None
    results: List[RankedResult] = field(default_factory=list)


class ShoppingCopilotAgent:
    def __init__(self, catalog: List[Product], llm_client: Optional[Any] = None):
        self.catalog = catalog
        self.catalog_by_asin = {p.asin: p for p in catalog}

        self.state_tracker = StateTracker()
        self.intent_router = IntentRouter()
        self.keyword_route = KeywordRoute(catalog)
        self.category_route = CategoryRoute(catalog)
        self.vector_route = VectorRoute(catalog)
        self.ranker = LLMRanker(client=llm_client)

        self.long_term_profile: Dict[str, Any] = {}  # Pillar III seam

    def handle_turn(self, text: str) -> AgentResponse:
        state = self.state_tracker.update(text)

        if state.turn_count > MAX_TURNS:
            return AgentResponse(
                turn=state.turn_count, intent=Intent.BROWSING, slots=state.slots,
                action="session_terminated",
            )

        decision = self.intent_router.classify(text, accumulated_hard_slots=state.hard_slot_count())
        strict_filter = decision.intent == Intent.BUYING

        kw = self.keyword_route.retrieve(text)
        cat = self.category_route.retrieve(state.slots, strict=strict_filter)
        vec = self.vector_route.retrieve(text)

        merged = merge_routes(kw, cat, vec, decision.intent)

        if len(merged) > OVER_GENERALITY_THRESHOLD:
            prompt = self._build_clarification(state.slots, merged)
            return AgentResponse(
                turn=state.turn_count, intent=decision.intent, slots=state.slots,
                action="clarify", clarification_prompt=prompt,
            )

        ranked = self.ranker.rank(query_context=self._build_context(state), candidates=merged,
                                   catalog_by_asin=self.catalog_by_asin, top_k=10)

        self._update_long_term_profile(state, decision)

        return AgentResponse(
            turn=state.turn_count, intent=decision.intent, slots=state.slots,
            action="results", results=ranked,
        )

    def _build_context(self, state) -> str:
        return " | ".join(state.history[-3:])  # short-term session window

    def _build_clarification(self, slots: Dict[str, Any], merged) -> str:
        # Ask about whichever high-value slot is still missing, in priority order.
        for key, question in [
            ("category", "What type of item are you looking for (e.g. shoes, jewelry, jacket)?"),
            ("price_max", "What's your budget range?"),
            ("color", "Any color preference?"),
            ("size", "What size do you need?"),
        ]:
            if key not in slots:
                return f"I found {len(merged)} possible matches — {question}"
        return f"I found {len(merged)} possible matches — can you narrow it down further (brand, style, occasion)?"

    def _update_long_term_profile(self, state, decision) -> None:
        # TODO (Pillar III): Personalized Context Distillation.
        # Fold state.slots / decision history into a persisted long-term
        # profile here, and use it to bias future sessions' retrieval
        # weights / clarification ordering.
        pass
