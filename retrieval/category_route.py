"""
Category / hard-constraint filter route.

This is the other half of the "high-precision filter track": it applies
the DialogState's hard slots (category, price range, color, size, brand)
as literal filters over the catalog. Used heavily on the Buying track;
used as a soft boost (not a hard filter) on the Browsing track so we don't
kill diversity.
"""
from __future__ import annotations
from typing import List, Dict, Any

from models import Product, RetrievalCandidate


class CategoryRoute:
    def __init__(self, catalog: List[Product]):
        self.catalog = catalog

    def retrieve(self, slots: Dict[str, Any], top_k: int = 50, strict: bool = True) -> List[RetrievalCandidate]:
        candidates = []
        for p in self.catalog:
            score = 0
            hard_fail = False

            if "category" in slots:
                if slots["category"].lower() in p.category.lower():
                    score += 2
                elif strict:
                    hard_fail = True

            if "price_max" in slots and p.price is not None:
                if p.price <= slots["price_max"]:
                    score += 1
                elif strict:
                    hard_fail = True

            if "price_min" in slots and p.price is not None:
                if p.price >= slots["price_min"]:
                    score += 1
                elif strict:
                    hard_fail = True

            if "color" in slots:
                if str(p.attributes.get("color", "")).lower() == slots["color"].lower():
                    score += 1
                elif strict and "color" in p.attributes:
                    hard_fail = True

            if "brand" in slots:
                if p.brand and slots["brand"].lower() == p.brand.lower():
                    score += 2
                elif strict and p.brand:
                    hard_fail = True

            if hard_fail:
                continue
            if score > 0:
                candidates.append(RetrievalCandidate(asin=p.asin, score=float(score), route="category"))

        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates[:top_k]
