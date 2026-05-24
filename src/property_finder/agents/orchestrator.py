"""Coordinates the sub-agents to turn a UserBrief into a Shortlist.

Flow:
  1. area_agent proposes candidate areas + societies for the brief.
  2. commute_agent scores each candidate's commute feasibility (by mode, time of day).
  3. sentiment_agent pulls neighbourhood sentiment.
  4. orchestrator ranks and returns the visit-worthy shortlist.

This is the human-in-the-loop boundary: output is a shortlist to validate
in person, never a final decision.
"""
from __future__ import annotations

from property_finder.agents.area_agent import AreaAgent
from property_finder.agents.commute_agent import CommuteAgent
from property_finder.agents.sentiment_agent import SentimentAgent
from property_finder.domain.models import (
    AreaRecommendation,
    CommuteEstimate,
    HazardProvider,
    Listing,
    ListingsProvider,
    Shortlist,
    UserBrief,
)

# Words in a sentiment summary that drag an area's score down.
_BAD_SIGNALS = (
    "unsafe", "avoid", "crime", "flood", "waterlog", "dirty", "noisy", "poor", "bad",
)
# Confidence penalty applied when an area is in a known seasonal-hazard zone.
_HAZARD_PENALTY = 0.1


def _matches(listing: Listing, brief: UserBrief) -> bool:
    """Keep a listing unless a KNOWN attribute violates a criterion. Unknown
    (None) attributes are not grounds to exclude - the data is best-effort, so
    we surface incomplete candidates rather than silently dropping everything."""
    if listing.rent_inr is not None and listing.rent_inr > brief.monthly_budget_inr:
        return False
    if brief.min_sqft and listing.sqft is not None and listing.sqft < brief.min_sqft:
        return False
    if brief.needs_car_parking and listing.car_parking is False:
        return False
    if brief.bhk and listing.bhk and brief.bhk.lower().replace(" ", "") not in \
            listing.bhk.lower().replace(" ", ""):
        return False
    if brief.furnishing and listing.furnishing and \
            brief.furnishing.lower().split()[0] not in listing.furnishing.lower():
        return False
    return True


class Orchestrator:
    def __init__(
        self,
        area_agent: AreaAgent,
        commute_agent: CommuteAgent,
        sentiment_agent: SentimentAgent,
        hazards: HazardProvider | None = None,
        listings: ListingsProvider | None = None,
    ) -> None:
        self._area = area_agent
        self._commute = commute_agent
        self._sentiment = sentiment_agent
        self._hazards = hazards
        self._listings = listings

    def run(self, brief: UserBrief, top_n: int = 5) -> Shortlist:
        # The target city comes from the brief (brief.city), so the same flow
        # works for any city without code changes.
        candidates: list[AreaRecommendation] = []
        for area, societies in self._area.propose_areas(brief):
            commute = self._commute.estimate(brief.office_location, area, brief.transport_mode)
            sentiment = self._sentiment.summarize(area, brief.city)
            monsoon = self._hazards.seasonal_risk(area, brief.city) if self._hazards else ""
            listings = self._matched_listings(area, brief)
            confidence = self._confidence(commute, sentiment, societies)
            if monsoon:
                confidence = round(max(0.0, confidence - _HAZARD_PENALTY), 2)
            candidates.append(
                AreaRecommendation(
                    area_name=area,
                    society_names=societies,
                    commute=commute,
                    sentiment_summary=sentiment,
                    why_recommended=self._why(commute, sentiment, societies, monsoon),
                    confidence=confidence,
                    monsoon_note=monsoon,
                    listings=listings,
                )
            )

        ranked = sorted(candidates, key=lambda r: r.confidence, reverse=True)[:top_n]
        return Shortlist(city=brief.city, brief=brief, recommendations=ranked)

    def _matched_listings(self, area: str, brief: UserBrief) -> list[Listing]:
        if self._listings is None:
            return []
        return [lst for lst in self._listings.find_listings(area, brief)
                if _matches(lst, brief)][:5]

    @staticmethod
    def _confidence(
        commute: CommuteEstimate, sentiment: str, societies: list[str]
    ) -> float:
        worst = max(commute.minutes_morning_peak, commute.minutes_evening_peak)
        commute_score = max(0.0, 1.0 - worst / 90.0)
        if not commute.feasible_for_mode:
            commute_score = min(commute_score, 0.3)

        sentiment_score = 0.5
        if any(word in sentiment.lower() for word in _BAD_SIGNALS):
            sentiment_score = 0.2

        coverage_score = min(1.0, len(societies) / 5.0)

        confidence = 0.5 * commute_score + 0.3 * sentiment_score + 0.2 * coverage_score
        return round(confidence, 2)

    @staticmethod
    def _why(
        commute: CommuteEstimate, sentiment: str, societies: list[str], monsoon: str = ""
    ) -> str:
        society_note = (
            f"{len(societies)} societies found" if societies else "limited society data"
        )
        if commute.reliable:
            worst = max(commute.minutes_morning_peak, commute.minutes_evening_peak)
            commute_note = (
                f"Commute up to ~{worst} min at peak "
                f"({'feasible' if commute.feasible_for_mode else 'tight'})."
            )
        else:
            commute_note = "Commute estimate unreliable (verify manually)."
        why = f"{commute_note} {society_note}. Sentiment: {sentiment[:100]}"
        if monsoon:
            why += " | MONSOON RISK"
        return why
