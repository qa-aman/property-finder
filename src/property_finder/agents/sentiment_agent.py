"""Summarizes neighbourhood sentiment from reviews and resident discussion.

Feeds the level-1 filter (P4): gives an outsider enough signal to decide
whether an area is worth an in-person visit.
"""
from __future__ import annotations

from property_finder.domain.models import LLMPort, ReviewsProvider

_SYSTEM = (
    "You summarize neighbourhood sentiment for someone considering renting there. Given raw "
    "text from Reddit posts or map reviews about a specific area, write a neutral 1 to 2 "
    "sentence summary covering commute/traffic, safety, amenities, and quality of life. "
    "Only summarize what is in the source text. Do not invent facts."
)

_NO_DATA = "Limited public data available for this area."


class SentimentAgent:
    def __init__(self, reviews: ReviewsProvider, llm: LLMPort) -> None:
        self._reviews = reviews
        self._llm = llm

    def summarize(self, area: str, city: str) -> str:
        raw = self._reviews.neighbourhood_sentiment(area, city)
        if not raw or not raw.strip():
            return _NO_DATA
        user = f"Area: {area}, {city}\n\nSource text:\n{raw[:2000]}"
        summary = self._llm.chat(_SYSTEM, user)
        return summary.strip() or _NO_DATA
