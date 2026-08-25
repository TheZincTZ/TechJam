"""
Core data models shared across the pipeline.

These are intentionally plain dataclasses so they're easy to serialize
to/from JSON and easy to swap out once you wire up the real participant
kit's Product / Session schema (Amazon Reviews 2023, Clothing_Shoes_and_Jewelry).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class Product:
    """A single catalog item.

    Field names are chosen to be a reasonable superset of what the Amazon
    Reviews 2023 metadata typically exposes. Adjust once you see the real
    participant-kit schema.
    """
    asin: str
    title: str
    category: str
    price: Optional[float] = None
    brand: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)  # e.g. {"color": "black", "size": "M"}
    description: str = ""

    def searchable_text(self) -> str:
        """Flat text blob used by keyword / vector retrieval."""
        parts = [self.title, self.category, self.brand or "", self.description]
        parts += [f"{k} {v}" for k, v in self.attributes.items()]
        return " ".join(str(p) for p in parts if p)


@dataclass
class Turn:
    """A single user utterance in a session."""
    turn_id: int
    text: str


@dataclass
class RetrievalCandidate:
    """A candidate product surfaced by one retrieval route, with per-route score."""
    asin: str
    score: float
    route: str  # "keyword" | "category" | "vector"


@dataclass
class RankedResult:
    asin: str
    final_score: float
    explanation: str = ""
