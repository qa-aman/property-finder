"""In-memory fake adapters for the four ports.

Used when USE_STUB_ADAPTERS is true so the full flow runs (and tests pass)
without Anthropic/Gemini/Google/Reddit keys. Deterministic, no network.
"""
from __future__ import annotations

import json
from typing import Any

from property_finder.domain.models import CommuteEstimate, Listing, TransportMode, UserBrief


class StubLLM:
    """Returns canned output. For area proposal (schema given) returns a JSON
    array; otherwise returns a short fake sentiment summary."""

    def chat(self, system: str, user: str, response_schema: Any | None = None) -> str:
        if response_schema is not None:
            return json.dumps(
                ["North Quarter", "Riverside", "Tech Park East", "Old Town", "Green Meadows"]
            )
        return "Residents call it well-connected and green, with the usual peak-hour traffic."


class StubSocieties:
    def find_societies(self, area: str, city: str) -> list[str]:
        return [f"{area} Heights", f"{area} Residency", f"{area} Greens"]


class StubMaps:
    def commute_estimate(self, origin: str, area: str, mode: TransportMode) -> CommuteEstimate:
        # Vary by area length so feasibility and ranking have something to sort on.
        base = 12 + (len(area) % 5) * 7
        return CommuteEstimate(
            minutes_morning_peak=base + 6,
            minutes_evening_peak=base + 12,
            feasible_for_mode=True,  # the CommuteAgent decides real feasibility
            notes="",
        )


class StubReviews:
    def neighbourhood_sentiment(self, area: str, city: str) -> str:
        return (
            f"Discussion about {area} in {city}: good markets and metro access, "
            "but parking is tight and mornings are busy."
        )


class StubListings:
    def find_listings(self, area: str, brief: UserBrief) -> list[Listing]:
        rent = min(brief.monthly_budget_inr, 45000)
        return [
            Listing(title=f"{area} Heights - Flat A", rent_inr=rent, bhk=brief.bhk or "1 BHK",
                    sqft=max(brief.min_sqft or 0, 550), car_parking=True,
                    furnishing=brief.furnishing or "semi-furnished",
                    source_url="https://example.com/listing/a", verified=False),
            Listing(title=f"{area} Residency - Flat B", rent_inr=rent - 3000,
                    bhk=brief.bhk or "1 BHK", sqft=max(brief.min_sqft or 0, 520),
                    car_parking=True, furnishing=brief.furnishing or "semi-furnished",
                    source_url="https://example.com/listing/b", verified=False),
        ]
