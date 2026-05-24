"""Composition root: wires adapters into agents and the orchestrator.

This is the only place outer layers (infrastructure) are bound to inner ones,
and the only place we choose stub vs real adapters. Fail-fast lives here: a real
adapter with a missing key raises immediately.
"""
from __future__ import annotations

from property_finder.agents.area_agent import AreaAgent
from property_finder.agents.commute_agent import CommuteAgent
from property_finder.agents.orchestrator import Orchestrator
from property_finder.agents.sentiment_agent import SentimentAgent
from property_finder.config import Settings


def build_orchestrator(settings: Settings) -> Orchestrator:
    if settings.use_stub_adapters:
        from property_finder.infrastructure.stubs import (
            StubLLM,
            StubListings,
            StubMaps,
            StubReviews,
            StubSocieties,
        )

        area_llm: object = StubLLM()
        sentiment_llm: object = StubLLM()
        societies: object = StubSocieties()
        maps: object = StubMaps()
        reviews: object = StubReviews()
        listings: object = StubListings()
    else:
        from property_finder.infrastructure.gemini_listings import GeminiGroundedListings
        from property_finder.infrastructure.gemini_llm import GeminiLLMAdapter
        from property_finder.infrastructure.gemini_reviews import GeminiGroundedReviews
        from property_finder.infrastructure.google_maps import GoogleMapsProvider
        from property_finder.infrastructure.places import GooglePlacesAdapter

        _require(settings.gemini_api_key, "GEMINI_API_KEY")
        _require(settings.google_maps_api_key, "GOOGLE_MAPS_API_KEY")

        area_llm = GeminiLLMAdapter(settings.gemini_api_key, model="gemini-2.5-flash")
        sentiment_llm = GeminiLLMAdapter(settings.gemini_api_key, model="gemini-2.5-flash-lite")
        societies = GooglePlacesAdapter(settings.google_maps_api_key)
        maps = GoogleMapsProvider(settings.google_maps_api_key)
        # Sentiment + listings via Gemini + Google Search grounding (no extra key).
        reviews = GeminiGroundedReviews(settings.gemini_api_key, model="gemini-2.5-flash")
        listings = GeminiGroundedListings(settings.gemini_api_key, model="gemini-2.5-flash")

    # Seasonal-hazard lookup is static data (no key), same for stub and real.
    from property_finder.infrastructure.hazards import MumbaiFloodHazards

    return Orchestrator(
        area_agent=AreaAgent(llm=area_llm, societies=societies),
        commute_agent=CommuteAgent(maps),
        sentiment_agent=SentimentAgent(reviews=reviews, llm=sentiment_llm),
        hazards=MumbaiFloodHazards(),
        listings=listings,
    )


def _require(value: str | None, name: str) -> None:
    if not value:
        raise RuntimeError(
            f"{name} is required for real adapters. Set it, or set USE_STUB_ADAPTERS=true."
        )
