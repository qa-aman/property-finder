"""Domain entities and ports. No framework or vendor imports allowed here."""
from __future__ import annotations

from enum import Enum
from typing import Any, Protocol

from pydantic import BaseModel, field_validator


class TransportMode(str, Enum):
    own_car = "own_car"
    auto = "auto"
    public = "public"


class UserBrief(BaseModel):
    """What the user knows: which city, office location, how they move, budget, preferences."""
    city: str
    office_location: str
    transport_mode: TransportMode
    monthly_budget_inr: int
    preferences: list[str] = []
    # Optional apartment-level criteria used to filter listings (R2). None = unconstrained.
    bhk: str | None = None              # e.g. "1 BHK"
    min_sqft: int | None = None         # e.g. 500
    needs_car_parking: bool = False     # four-wheeler parking required
    furnishing: str | None = None       # e.g. "semi-furnished"

    @field_validator("city", "office_location")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must not be blank")
        return value.strip()

    @field_validator("monthly_budget_inr")
    @classmethod
    def _positive_budget(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("monthly_budget_inr must be greater than 0")
        return value


class CommuteEstimate(BaseModel):
    minutes_morning_peak: int
    minutes_evening_peak: int
    feasible_for_mode: bool
    notes: str = ""
    reliable: bool = True  # False when the maps result looks anomalous


class Listing(BaseModel):
    """A candidate flat. From grounded best-effort search, so verified is False:
    attributes are indicative and must be confirmed on the listing/at visit."""
    title: str
    rent_inr: int | None = None
    bhk: str | None = None
    sqft: int | None = None
    car_parking: bool | None = None
    furnishing: str | None = None
    source_url: str | None = None
    verified: bool = False


class AreaRecommendation(BaseModel):
    area_name: str
    society_names: list[str]
    commute: CommuteEstimate
    sentiment_summary: str
    why_recommended: str
    confidence: float  # 0..1
    monsoon_note: str = ""  # seasonal flood/waterlogging risk, empty if none/unknown
    listings: list[Listing] = []  # candidate flats matching the brief's criteria (unverified)


class Shortlist(BaseModel):
    """The POC's output: a ranked, visit-worthy shortlist."""
    city: str
    brief: UserBrief
    recommendations: list[AreaRecommendation]


# Ports (implemented in infrastructure / tools)

class MapsProvider(Protocol):
    def commute_estimate(self, origin: str, area: str, mode: TransportMode) -> CommuteEstimate: ...


class ReviewsProvider(Protocol):
    def neighbourhood_sentiment(self, area: str, city: str) -> str: ...


class SocietiesProvider(Protocol):
    def find_societies(self, area: str, city: str) -> list[str]: ...


class HazardProvider(Protocol):
    def seasonal_risk(self, area: str, city: str) -> str:
        """Return a seasonal-hazard note (e.g. monsoon flooding) for the area,
        or an empty string if none is known for this city."""
        ...


class ListingsProvider(Protocol):
    def find_listings(self, area: str, brief: "UserBrief") -> list["Listing"]:
        """Return candidate flats in the area matching the brief's criteria.
        Implementations may return unverified, best-effort results."""
        ...


class LLMPort(Protocol):
    def chat(self, system: str, user: str, response_schema: Any | None = None) -> str:
        """Return the model's text. If response_schema is given, the text is JSON
        conforming to that schema (provider-side structured output)."""
        ...
