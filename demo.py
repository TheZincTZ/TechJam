"""
End-to-end smoke test / demo for the foundation pipeline.

Run: python demo.py

Simulates a session that starts browsing, narrows down, then hits a
hard-constraint buying turn, to exercise:
  - Browsing -> vector-dominant routing
  - Over-generality -> clarification prompt
  - Slot accumulation -> Buying -> keyword+category-dominant routing
  - Intent override ("actually, blue not black")
"""
from data.sample_catalog import load_sample_catalog
from agent import ShoppingCopilotAgent

TURNS = [
    "I'm looking for something for a gift",
    "gift ideas for jewelry",
    "under $30 in gold",
    "actually make it silver",
]


def main():
    catalog = load_sample_catalog()
    agent = ShoppingCopilotAgent(catalog)  # no llm_client -> ranking falls back to hybrid score order

    for text in TURNS:
        resp = agent.handle_turn(text)
        print(f"\n--- Turn {resp.turn} ---")
        print(f"User: {text}")
        print(f"Intent: {resp.intent.value} | Slots: {resp.slots}")
        print(f"Action: {resp.action}")
        if resp.action == "clarify":
            print(f"Agent asks: {resp.clarification_prompt}")
        elif resp.action == "results":
            for r in resp.results[:5]:
                p = agent.catalog_by_asin[r.asin]
                print(f"  {r.asin} | {p.title} | ${p.price} | score={r.final_score:.3f} | {r.explanation}")


if __name__ == "__main__":
    main()
