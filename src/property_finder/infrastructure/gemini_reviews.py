"""Neighbourhood-sentiment source backed by Gemini + Google Search grounding.

Implements ReviewsProvider. Instead of calling the Reddit API directly, this asks
Gemini to run a live Google Search and ground its answer in current web results
(resident discussion, reviews, news). That keeps sentiment current and sourced
(mitigating the hallucination risk of ungrounded model knowledge) while needing
only the Gemini key. The SentimentAgent then compresses the grounded text.
"""
from __future__ import annotations

from google import genai
from google.genai import types

_PROMPT = (
    "Search the web for what residents and visitors say about living in {area}, {city}. "
    "In 3-4 sentences, summarize real sentiment on commute/traffic, safety, amenities "
    "(markets, schools, hospitals), and overall quality of life. If there is little "
    "information, say so plainly."
)


class GeminiGroundedReviews:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def neighbourhood_sentiment(self, area: str, city: str) -> str:
        try:
            resp = self._client.models.generate_content(
                model=self._model,
                contents=_PROMPT.format(area=area, city=city),
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                ),
            )
        except Exception:
            return ""  # let the SentimentAgent fall back to its "no data" message
        return (resp.text or "").strip()
