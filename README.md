# Shopping Copilot — Foundation Prototype

This is **Pillar I + the foundation of Pillar II** from the problem statement:
Dual-Track Intent Routing, Multi-Route Retrieval → Ranking, and a slot-based
dialog state tracker with over-generality clarification. It runs entirely
in-memory with **no API key required** (LLM ranking gracefully falls back to
hybrid-score order until you wire one up).

## Why it's structured this way

| Problem statement requirement | File |
|---|---|
| Dual-Track Routing (Buying vs Browsing) | `intent_router.py` |
| Multi-Route Retrieval (keyword, category, vector) | `retrieval/keyword_route.py`, `retrieval/category_route.py`, `retrieval/vector_route.py` |
| Combine routes with intent-aware weighting | `retrieval/hybrid.py` |
| LLM Semantic Ranking | `ranking.py` (stubbed fallback — see TODO inside) |
| Information Accumulation / Intent Override | `state_tracker.py` |
| Over-Generality → clarification prompts | `agent.py::_build_clarification` |
| Max 10 turns hard limit | `agent.py::MAX_TURNS` |
| Personalized Context Distillation (Pillar III) | `agent.py::_update_long_term_profile` — seam only, not implemented yet |

## Quickstart

```bash
pip install -r requirements.txt
python demo.py
```

`demo.py` runs a 4-turn synthetic session (browse → narrow → buy → override)
against a 15-item synthetic catalog in `data/sample_catalog.py`, so you can
see intent switching, slot accumulation, and override-on-contradiction working
before you touch the real dataset.

## Wiring in the real dataset

1. Download the participant kit's frozen 50k-item catalog.
2. Write a loader that returns `List[Product]` (see `models.py`) — swap out
   `load_sample_catalog()` for it in `demo.py` / wherever you build the agent.
3. Check the real field names against `Product` and adjust `searchable_text()`
   / `CategoryRoute` filter logic if the schema differs from the assumed one.

## Wiring in a real LLM for ranking

`ranking.py::LLMRanker.rank()` has the fallback in place; the `TODO` block
sketches the prompt shape (numbered candidate list + dialog context → strict
JSON rank list). Anthropic/OpenAI/local model all fit the same interface —
nothing else in the pipeline needs to change.

## Known simplifications (call these out in your Devpost writeup)

- **Vector route uses TF-IDF cosine, not real embeddings** — zero-dependency
  stand-in so the prototype needs no API key. Swapping to sentence-transformers
  or an embedding API is a one-file change (`retrieval/vector_route.py`).
- **Slot extraction is regex-based**, not an LLM slot-filler. Transparent and
  fast for the prototype; an LLM-based extractor would generalize much better
  and is the natural place to spend more engineering effort next.
- **Intent routing is rule-based.** Good enough to demo the dual-track
  architecture; an LLM or a small trained classifier would improve accuracy
  on ambiguous phrasing.
- **No persisted long-term user profile yet** (Pillar III seam only) — this
  is the next thing to build once the foundation is solid.

## Evaluation hookup

Once you have the official local evaluator from the participant kit, the
integration point is `ShoppingCopilotAgent.handle_turn(text) -> AgentResponse`
— check `AgentResponse.results` (list of `RankedResult`, each with `.asin`)
against whatever interface the evaluator expects (likely a `respond(session)`
style call per the "published Python Agent interface"). You may need a thin
adapter class around `ShoppingCopilotAgent` to match the exact method
signature once you see the kit's API contract.
