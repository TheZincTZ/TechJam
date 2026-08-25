"""
Pillar I — Dual-Track Routing.

Detects whether a turn (in the context of the accumulated dialog state)
reflects high-intent "Buying" behaviour (hard constraints present: brand,
size, exact price ceiling, "buy now" language) vs open-ended "Browsing"
(vague scenario language: "something for", "gift ideas", "casual look").

This starts as a transparent, debuggable rule-based classifier (regex +
slot-count heuristic) so you can demo it without any external API key.
Swap `classify()` for an LLM call later without touching the rest of the
pipeline — the interface (IntentRouter.classify) stays the same.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from enum import Enum


class Intent(str, Enum):
    BUYING = "buying"
    BROWSING = "browsing"


# Signals that suggest a hard-constraint, ready-to-purchase query.
_BUYING_PATTERNS = [
    r"\bunder \$?\d+\b",
    r"\bbetween \$?\d+\s*(and|-)\s*\$?\d+\b",
    r"\bsize\s+\w+\b",
    r"\b(buy|purchase|order|checkout|add to cart)\b",
    r"\bin (black|white|red|blue|green|grey|gray|navy|beige|brown)\b",
    r"\b(exactly|specifically|only)\b",
]

# Signals that suggest open-ended scenario / vibe browsing.
_BROWSING_PATTERNS = [
    r"\b(something|anything) for\b",
    r"\bgift ideas?\b",
    r"\blooking for\b(?! .*(size|under \$))",
    r"\bcasual (look|style|outfit)\b",
    r"\bnot sure (what|which)\b",
    r"\brecommend(ations)?\b",
    r"\bwhat goes with\b",
]


@dataclass
class IntentDecision:
    intent: Intent
    confidence: float
    matched_signals: list[str]


class IntentRouter:
    def __init__(self, hard_slot_threshold: int = 2):
        # If the accumulated state already has >= this many hard slots
        # (brand/size/exact price), lean BUYING even on a soft utterance.
        self.hard_slot_threshold = hard_slot_threshold
        self._buy_re = [re.compile(p, re.I) for p in _BUYING_PATTERNS]
        self._browse_re = [re.compile(p, re.I) for p in _BROWSING_PATTERNS]

    def classify(self, text: str, accumulated_hard_slots: int = 0) -> IntentDecision:
        buy_hits = [p.pattern for p in self._buy_re if p.search(text)]
        browse_hits = [p.pattern for p in self._browse_re if p.search(text)]

        buy_score = len(buy_hits) + (1 if accumulated_hard_slots >= self.hard_slot_threshold else 0)
        browse_score = len(browse_hits)

        if buy_score == 0 and browse_score == 0:
            # No strong signal either way: default to BROWSING (safer — wide
            # net retrieval) but with low confidence so downstream can react.
            return IntentDecision(Intent.BROWSING, confidence=0.5, matched_signals=[])

        if buy_score >= browse_score:
            total = buy_score + browse_score
            return IntentDecision(Intent.BUYING, confidence=buy_score / total, matched_signals=buy_hits)
        else:
            total = buy_score + browse_score
            return IntentDecision(Intent.BROWSING, confidence=browse_score / total, matched_signals=browse_hits)
