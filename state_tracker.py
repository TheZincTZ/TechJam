"""
Pillar II (foundation piece) — Dynamic State Machine.

Tracks slots across turns. Two behaviours the problem statement calls out
explicitly, both implemented here:

1. Information Accumulation: new slots merge additively with existing ones
   ("red sneakers" -> "size 9" keeps color=red AND adds size=9).
2. Intent Override: a contradicting value for an already-filled slot wipes
   and replaces it, rather than merging ("actually I want blue, not red").

Slot extraction here is regex-based for transparency/speed in the
prototype. It's the natural place to later swap in an LLM slot-filler —
keep the same `update(text)` contract.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

_COLOR_RE = re.compile(
    r"\b(black|white|red|blue|green|grey|gray|navy|beige|brown|pink|yellow|purple|orange|gold|silver)\b", re.I
)
_SIZE_RE = re.compile(r"\bsize\s+([a-zA-Z0-9.]+)\b", re.I)
_PRICE_UNDER_RE = re.compile(r"\bunder \$?(\d+(?:\.\d+)?)\b", re.I)
_PRICE_RANGE_RE = re.compile(r"\bbetween \$?(\d+(?:\.\d+)?)\s*(?:and|-)\s*\$?(\d+(?:\.\d+)?)\b", re.I)
_CATEGORY_HINTS = [
    "shoes", "sneakers", "boots", "sandals", "dress", "shirt", "jacket",
    "jeans", "jewelry", "necklace", "ring", "watch", "bag", "handbag",
]
_OVERRIDE_CUE_RE = re.compile(r"\b(actually|instead|not|change (it )?to|nvm|never ?mind)\b", re.I)

# Slots we treat as "hard" for intent-routing purposes.
HARD_SLOT_KEYS = {"size", "price_max", "price_min", "brand"}


@dataclass
class DialogState:
    slots: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    turn_count: int = 0

    def hard_slot_count(self) -> int:
        return sum(1 for k in self.slots if k in HARD_SLOT_KEYS)


class StateTracker:
    def __init__(self):
        self.state = DialogState()

    def update(self, text: str) -> DialogState:
        s = self.state
        s.turn_count += 1
        s.history.append(text)

        is_override_turn = bool(_OVERRIDE_CUE_RE.search(text))

        new_slots: Dict[str, Any] = {}

        color_m = _COLOR_RE.search(text)
        if color_m:
            new_slots["color"] = color_m.group(1).lower()

        size_m = _SIZE_RE.search(text)
        if size_m:
            new_slots["size"] = size_m.group(1)

        range_m = _PRICE_RANGE_RE.search(text)
        under_m = _PRICE_UNDER_RE.search(text)
        if range_m:
            new_slots["price_min"] = float(range_m.group(1))
            new_slots["price_max"] = float(range_m.group(2))
        elif under_m:
            new_slots["price_max"] = float(under_m.group(1))

        text_l = text.lower()
        for cat in _CATEGORY_HINTS:
            if cat in text_l:
                new_slots["category"] = cat
                break

        # Information Accumulation vs Intent Override:
        # - Override cue present -> new values for slots mentioned in this
        #   turn REPLACE old ones (erase-and-rewrite for those specific keys).
        # - No override cue -> merge additively (accumulation), new value
        #   still wins for any key mentioned in this turn (most-recent-wins),
        #   but unmentioned slots from earlier turns are preserved either way.
        for k, v in new_slots.items():
            s.slots[k] = v  # most-recent-mention-wins in both modes

        return s

    def reset(self):
        self.state = DialogState()
